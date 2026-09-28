"""Provide in-memory Modbus test doubles."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Literal

from ._client import BaseModbusConnection, ModbusTcpParams
from .model._const import Space

__all__ = [
    "CoilSpec",
    "MockModbusConnection",
    "MockModbusUnit",
    "ReadEvent",
    "RegisterSpec",
    "WriteEvent",
]

RegisterSpec = int | list[int] | Callable[[], "int | list[int]"]
"""Value accepted by a mock register store."""

CoilSpec = bool | list[bool] | Callable[[], "bool | list[bool]"]
"""Value accepted by a mock bit store."""

RegisterType = Literal["holding", "coil"]
"""Selects one of the two writable address spaces."""


@dataclass(frozen=True)
class WriteEvent:
    """Describe a write to a mock unit."""

    register_type: RegisterType
    address: int
    values: list[int] | list[bool]
    function_code: int


@dataclass(frozen=True)
class ReadEvent:
    """Describe a block read from a mock unit."""

    register_type: Space
    address: int
    count: int


def _materialize(
    space: dict[int, Any], convert: Callable[[Any], Any]
) -> dict[int, Any]:
    """Materialize a mock store by address."""
    out: dict[int, Any] = {}
    for base, spec in space.items():
        value = spec() if callable(spec) else spec
        if isinstance(value, (list, tuple)):
            for offset, item in enumerate(value):
                out[base + offset] = convert(item)
        else:
            out[base] = convert(value)
    return out


def _read_registers(space: dict[int, Any], address: int, count: int) -> list[int]:
    materialized = _materialize(space, int)
    return [int(materialized.get(address + i, 0)) for i in range(count)]


def _read_bits(space: dict[int, Any], address: int, count: int) -> list[bool]:
    materialized = _materialize(space, bool)
    return [bool(materialized.get(address + i, False)) for i in range(count)]


def _warn_store_name(old: str, new: str) -> None:
    warnings.warn(
        f"MockModbusUnit.{old} is deprecated. Use {new}, the name "
        "async_read_raw() and ReadEvent use for that space.",
        DeprecationWarning,
        stacklevel=3,
    )


def _space(register_type: Space | Literal["discrete_input"]) -> Space:
    """Resolve a ``register_type`` argument to the address space it names."""
    if register_type == "discrete_input":
        warnings.warn(
            'register_type="discrete_input" is deprecated. Use "discrete", the '
            "name async_read_raw() and ReadEvent use for that space.",
            DeprecationWarning,
            stacklevel=3,
        )
        return "discrete"
    return register_type


class MockModbusConnection(BaseModbusConnection):
    """Implement ``ModbusConnection`` in memory."""

    def __init__(self) -> None:
        super().__init__(ModbusTcpParams(host="mock"))
        self._units: dict[int, MockModbusUnit] = {}

    async def _connect_client(self) -> object:
        return object()

    async def _close_client(self, client: object) -> None:
        pass

    def for_unit(self, unit_id: int) -> MockModbusUnit:
        if unit_id not in self._units:
            self._units[unit_id] = MockModbusUnit(self, unit_id)
        return self._units[unit_id]

    def simulate_connection_lost(self) -> None:
        """Drop the link and fire every ``on_connection_lost`` callback.

        The drop is transient, as on a real connection. The next request
        establishes the link again.
        """
        self._client = None
        self._lost_callbacks.fire()


def _address(address: int | str) -> int:
    """One address of a raw snapshot, as a number whether or not it is one."""
    try:
        return int(address)
    except ValueError:
        raise ValueError(
            f"address {address!r} in raw snapshot is not a number"
        ) from None


class MockModbusUnit:
    """Implement ``ModbusUnit`` with in-memory stores."""

    def __init__(self, connection: MockModbusConnection, unit_id: int) -> None:
        self._conn = connection
        self._unit_id = unit_id
        self.holding: dict[int, RegisterSpec] = {}
        self.input: dict[int, RegisterSpec] = {}
        self.coil: dict[int, CoilSpec] = {}
        self.discrete: dict[int, CoilSpec] = {}
        self._write_callbacks: list[Callable[[WriteEvent], None]] = []
        self._write_failures: dict[tuple[RegisterType, int], Exception] = {}
        self._read_failures: dict[tuple[Space, int], Exception] = {}
        self._request_failure: Exception | None = None
        self._responses: dict[str, object] = {}
        self.message_spacing = 0.0
        self.required_timeout: float | None = None
        self.required_connect_delay: float | None = None
        self.read_events: list[ReadEvent] = []

    @property
    def connected(self) -> bool:
        return self._conn.connected

    @property
    def coils(self) -> dict[int, CoilSpec]:
        """Deprecated name of the ``coil`` store."""
        _warn_store_name("coils", "coil")
        return self.coil

    @property
    def discrete_inputs(self) -> dict[int, CoilSpec]:
        """Deprecated name of the ``discrete`` store."""
        _warn_store_name("discrete_inputs", "discrete")
        return self.discrete

    def set_message_spacing(self, seconds: float) -> None:
        """Record the per-unit request interval.

        Raises ``ValueError`` if ``seconds`` is negative.
        """
        if seconds < 0:
            raise ValueError("message_spacing must be non-negative")
        self.message_spacing = seconds

    def require_timeout(self, seconds: float | None) -> None:
        """Record the required per-request timeout, or ``None`` to withdraw it.

        Raises ``ValueError`` if ``seconds`` is negative.
        """
        if seconds is not None and seconds < 0:
            raise ValueError("timeout must be non-negative")
        self.required_timeout = seconds

    def require_connect_delay(self, seconds: float | None) -> None:
        """Record the required pause after the link opens, or ``None`` to withdraw it.

        Raises ``ValueError`` if ``seconds`` is negative.
        """
        if seconds is not None and seconds < 0:
            raise ValueError("connect_delay must be non-negative")
        self.required_connect_delay = seconds

    async def _ensure_connected(self) -> None:
        await self._conn.connect()

    # -- test configuration helpers -------------------------------------------

    def on_write(self, callback: Callable[[WriteEvent], None]) -> Callable[[], None]:
        """Register a callback for register and coil writes."""
        self._write_callbacks.append(callback)

        def unsubscribe() -> None:
            try:
                self._write_callbacks.remove(callback)
            except ValueError:
                pass

        return unsubscribe

    def fail_write(
        self,
        address: int,
        error: Exception | None,
        *,
        register_type: RegisterType = "holding",
    ) -> None:
        """Set the exception raised by matching writes."""
        key = (register_type, address)
        if error is None:
            self._write_failures.pop(key, None)
        else:
            self._write_failures[key] = error

    def fail_read(
        self,
        address: int,
        error: Exception | None,
        *,
        register_type: Space | Literal["discrete_input"] = "holding",
    ) -> None:
        """Set the exception raised by matching reads.

        ``register_type`` names the address space with the same words as an
        ``async_read_raw()`` snapshot. ``"discrete_input"`` is accepted for
        ``"discrete"`` and raises a ``DeprecationWarning``.
        """
        key = (_space(register_type), address)
        if error is None:
            self._read_failures.pop(key, None)
        else:
            self._read_failures[key] = error

    def fail_requests(self, error: Exception | None) -> None:
        """Set the exception raised by every read and write on this unit.

        Models a device that is not answering at all (powered down, unplugged,
        behind a dead gateway), where no address is special and a test need
        not know which one its caller reaches first. Pass ``None`` to let the
        unit answer again.

        This models the device rather than the link. ``connected`` still
        follows the connection, and reads are still recorded in
        ``read_events`` before they raise, so a test can assert what was
        attempted. Per-address ``fail_read`` and ``fail_write`` continue to
        apply on top.
        """
        self._request_failure = error

    def set_response(self, method: str, value: object) -> None:
        """Set a canned response for an operation."""
        self._responses[method] = value

    def load_raw(self, raw: Mapping[str, Mapping[int | str, int | bool]]) -> None:
        """Load an ``async_read_raw`` snapshot into the stores.

        Raises ``ValueError`` for an unknown address space, and for an
        address that is not a number.
        """
        registers = {"holding": self.holding, "input": self.input}
        bits = {"coil": self.coil, "discrete": self.discrete}
        for space, values in raw.items():
            if space in registers:
                registers[space].update({_address(a): v for a, v in values.items()})
            elif space in bits:
                bits[space].update({_address(a): bool(v) for a, v in values.items()})
            else:
                raise ValueError(f"unknown space {space!r} in raw snapshot")

    def _raise_if_write_fails(
        self, register_type: RegisterType, address: int, count: int = 1
    ) -> None:
        if self._request_failure is not None:
            raise self._request_failure
        for offset in range(count):
            error = self._write_failures.get((register_type, address + offset))
            if error is not None:
                raise error

    def _raise_if_read_fails(
        self, register_type: Space, address: int, count: int
    ) -> None:
        if self._request_failure is not None:
            raise self._request_failure
        for offset in range(count):
            error = self._read_failures.get((register_type, address + offset))
            if error is not None:
                raise error

    async def _dispatch_read(
        self, register_type: Space, address: int, count: int
    ) -> None:
        """Connect, record the block, then apply any configured read failure."""
        await self._ensure_connected()
        self.read_events.append(ReadEvent(register_type, address, count))
        self._raise_if_read_fails(register_type, address, count)

    def _fire_write(self, event: WriteEvent) -> None:
        for callback in list(self._write_callbacks):
            callback(event)

    def _canned(self, method: str) -> Any:
        if method not in self._responses:
            raise NotImplementedError(
                f"mock has no response configured for {method}(); "
                f"call unit.set_response({method!r}, ...)"
            )
        value = self._responses[method]
        return value() if callable(value) else value

    # -- raw register I/O -----------------------------------------------------

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        await self._dispatch_read("holding", address, count)
        return _read_registers(self.holding, address, count)

    async def read_input_registers(self, address: int, count: int) -> list[int]:
        await self._dispatch_read("input", address, count)
        return _read_registers(self.input, address, count)

    async def write_register(self, address: int, value: int) -> None:
        await self._ensure_connected()
        self._raise_if_write_fails("holding", address)
        self.holding[address] = int(value)
        self._fire_write(WriteEvent("holding", address, [int(value)], 0x06))

    async def write_registers(self, address: int, values: list[int]) -> None:
        await self._ensure_connected()
        ints = [int(v) for v in values]
        self._raise_if_write_fails("holding", address, len(ints))
        for offset, value in enumerate(ints):
            self.holding[address + offset] = value
        self._fire_write(WriteEvent("holding", address, ints, 0x10))

    # -- raw coil / discrete-input I/O ----------------------------------------

    async def read_coils(self, address: int, count: int) -> list[bool]:
        await self._dispatch_read("coil", address, count)
        return _read_bits(self.coil, address, count)

    async def read_discrete_inputs(self, address: int, count: int) -> list[bool]:
        await self._dispatch_read("discrete", address, count)
        return _read_bits(self.discrete, address, count)

    async def write_coil(self, address: int, value: bool) -> None:
        await self._ensure_connected()
        self._raise_if_write_fails("coil", address)
        self.coil[address] = bool(value)
        self._fire_write(WriteEvent("coil", address, [bool(value)], 0x05))

    async def write_coils(self, address: int, values: list[bool]) -> None:
        await self._ensure_connected()
        bools = [bool(v) for v in values]
        self._raise_if_write_fails("coil", address, len(bools))
        for offset, value in enumerate(bools):
            self.coil[address + offset] = value
        self._fire_write(WriteEvent("coil", address, bools, 0x0F))

    # -- full function-code surface -------------------------------------------

    async def mask_write_register(
        self, address: int, and_mask: int, or_mask: int
    ) -> None:  # 0x16
        await self._ensure_connected()
        self._raise_if_write_fails("holding", address)
        current = _read_registers(self.holding, address, 1)[0]
        new = (current & and_mask) | (or_mask & ~and_mask)
        self.holding[address] = new
        self._fire_write(WriteEvent("holding", address, [new], 0x16))

    async def read_write_registers(
        self,
        read_address: int,
        read_count: int,
        write_address: int,
        write_values: list[int],
    ) -> list[int]:  # 0x17
        await self.write_registers(write_address, write_values)
        return await self.read_holding_registers(read_address, read_count)

    async def read_exception_status(self) -> int:  # 0x07
        await self._ensure_connected()
        return int(self._canned("read_exception_status"))

    async def report_server_id(self) -> bytes:  # 0x11
        await self._ensure_connected()
        return bytes(self._canned("report_server_id"))

    async def read_fifo_queue(self, address: int) -> list[int]:  # 0x18
        await self._ensure_connected()
        return list(self._canned("read_fifo_queue"))

    async def read_device_identification(self) -> dict[int, bytes]:  # 0x2B / 0x0E
        await self._ensure_connected()
        return dict(self._canned("read_device_identification"))

    async def read_file_record(
        self, file: int, record: int, length: int
    ) -> list[int]:  # 0x14
        await self._ensure_connected()
        return list(self._canned("read_file_record"))

    async def write_file_record(
        self, file: int, record: int, values: list[int]
    ) -> None:  # 0x15
        await self._ensure_connected()

    async def diagnostics(self, sub_function: int, data: int = 0) -> int:  # 0x08
        await self._ensure_connected()
        return int(self._canned("diagnostics"))

    async def get_comm_event_counter(self) -> tuple[bool, int]:  # 0x0B
        await self._ensure_connected()
        status, count = self._canned("get_comm_event_counter")
        return bool(status), int(count)

    async def get_comm_event_log(self) -> bytes:  # 0x0C
        await self._ensure_connected()
        return bytes(self._canned("get_comm_event_log"))

    def on_connection_lost(self, callback: Callable[[], None]) -> Callable[[], None]:
        return self._conn.on_connection_lost(callback)

    async def disconnect(self) -> None:
        await self._conn.disconnect()
