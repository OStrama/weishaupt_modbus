"""The backend-neutral ``ModbusUnit`` Protocol."""

from collections.abc import Callable
from typing import Protocol, runtime_checkable


@runtime_checkable
class ModbusUnit(Protocol):
    """Represent one unit on a shared Modbus connection."""

    @property
    def connected(self) -> bool: ...

    # raw register I/O
    async def read_holding_registers(self, address: int, count: int) -> list[int]: ...
    async def read_input_registers(self, address: int, count: int) -> list[int]: ...
    async def write_register(self, address: int, value: int) -> None: ...
    async def write_registers(self, address: int, values: list[int]) -> None: ...

    # raw coil / discrete-input I/O
    async def read_coils(self, address: int, count: int) -> list[bool]: ...
    async def read_discrete_inputs(self, address: int, count: int) -> list[bool]: ...
    async def write_coil(self, address: int, value: bool) -> None: ...
    async def write_coils(self, address: int, values: list[bool]) -> None: ...

    async def read_exception_status(self) -> int: ...  # 0x07
    async def report_server_id(self) -> bytes: ...  # 0x11
    async def mask_write_register(
        self, address: int, and_mask: int, or_mask: int
    ) -> None: ...  # 0x16
    async def read_write_registers(
        self,
        read_address: int,
        read_count: int,
        write_address: int,
        write_values: list[int],
    ) -> list[int]: ...  # 0x17
    async def read_fifo_queue(self, address: int) -> list[int]: ...  # 0x18
    async def read_device_identification(self) -> dict[int, bytes]: ...  # 0x2B / 0x0E
    async def read_file_record(
        self, file: int, record: int, length: int
    ) -> list[int]: ...  # 0x14
    async def write_file_record(
        self, file: int, record: int, values: list[int]
    ) -> None: ...  # 0x15
    async def diagnostics(self, sub_function: int, data: int = 0) -> int: ...  # 0x08
    async def get_comm_event_counter(self) -> tuple[bool, int]: ...  # 0x0B
    async def get_comm_event_log(self) -> bytes: ...  # 0x0C

    def set_message_spacing(self, seconds: float) -> None:
        """Set the minimum interval between requests to this unit."""

    def require_timeout(self, seconds: float | None) -> None:
        """Ask the link for a per-request timeout of at least ``seconds``.

        ``None`` withdraws the requirement.
        """

    def require_connect_delay(self, seconds: float | None) -> None:
        """Ask the link for a pause of at least ``seconds`` after it opens.

        ``None`` withdraws the requirement.
        """

    def on_connection_lost(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Register a callback fired when the link drops; returns an unsubscribe."""

    async def disconnect(self) -> None:
        """Drop the underlying link; the next request establishes a new one."""
