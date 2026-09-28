"""Implement Modbus connections with pymodbus."""

from __future__ import annotations

import functools
import ssl
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Concatenate, cast

from pymodbus import FramerType
from pymodbus.client import (
    AsyncModbusSerialClient,
    AsyncModbusTcpClient,
    AsyncModbusTlsClient,
    AsyncModbusUdpClient,
)
from pymodbus.client.base import ModbusBaseClient
from pymodbus.exceptions import (
    ConnectionException,
    ModbusException,
    ModbusIOException,
    ParameterException,
)
from pymodbus.pdu import ExceptionResponse, ModbusPDU
from pymodbus.pdu.diag_message import DiagnosticBase
from pymodbus.pdu.file_message import (
    FileRecord,
    ReadFifoQueueResponse,
    ReadFileRecordResponse,
)
from pymodbus.pdu.mei_message import ReadDeviceInformationResponse
from pymodbus.pdu.other_message import GetCommEventLogResponse, ReportDeviceIdResponse

from .._client import (
    BaseModbusConnection,
    ModbusSerialParams,
    ModbusTcpParams,
    ModbusTlsParams,
    ModbusUdpParams,
)
from .._types import SerialFraming, SocketFraming
from ..exceptions import (
    ModbusConnectionError,
    ModbusError,
    ModbusExceptionError,
    ModbusTimeoutError,
    _describe,
)

__all__ = [
    "ModbusConnection",
    "PymodbusConnection",
    "PymodbusUnit",
    "connect_serial",
    "connect_tcp",
    "connect_tls",
    "connect_udp",
]


def _map_errors[**P, R](
    func: Callable[Concatenate[PymodbusUnit, P], Awaitable[R]],
) -> Callable[Concatenate[PymodbusUnit, P], Coroutine[Any, Any, R]]:
    """Connect, pace, and map errors around a unit operation."""

    @functools.wraps(func)
    async def wrapper(self: PymodbusUnit, *args: P.args, **kwargs: P.kwargs) -> R:
        await self._conn.connect()
        prefix = _describe(func.__name__, args, kwargs)
        try:
            async with self._conn._pacer.paced(self._unit_id):
                return await func(self, *args, **kwargs)
        except ModbusError as err:
            # Raised by _check inside the operation; edit the message in place
            # so the typed subclass the caller branches on survives.
            err.args = (f"{prefix}: {err}",)
            raise
        except ConnectionException as err:
            raise ModbusConnectionError(f"{prefix}: {err}") from err
        except ModbusIOException as err:
            raise ModbusTimeoutError(f"{prefix}: {err}") from err
        except ModbusException as err:
            raise ModbusError(f"{prefix}: {err}") from err

    return wrapper


def _check(response: ModbusPDU) -> ModbusPDU:
    """Raise a neutral exception for an error response."""
    if response.isError():
        if isinstance(response, ExceptionResponse):
            raise ModbusExceptionError.from_code(response.exception_code)
        raise ModbusError(f"Modbus request failed: {response}")
    return response


def _safe_close(client: ModbusBaseClient) -> None:
    """Close a client without raising."""
    try:
        client.close()
    except (ModbusException, OSError):
        pass


def _connect_error(
    err: Exception | None,
    params: ModbusTcpParams | ModbusUdpParams | ModbusTlsParams | ModbusSerialParams,
    target: str,
) -> Exception:
    """Translate a pymodbus construct/connect failure to the neutral type."""
    if isinstance(err, ParameterException):
        return ValueError(str(err))
    message = (
        f"could not open serial port {target}"
        if isinstance(params, ModbusSerialParams)
        else f"could not connect to {target}"
    )
    if isinstance(err, TimeoutError):
        return ModbusTimeoutError(message)
    return ModbusConnectionError(message)


class _GenericDiagnostic(DiagnosticBase):
    """Represent a diagnostics request with a custom sub-function."""

    sub_function_code = 0


def _build_diagnostic(sub_function: int, data: int) -> DiagnosticBase:
    request = _GenericDiagnostic(message=data)
    request.sub_function_code = sub_function
    return request


class ModbusConnection(BaseModbusConnection):
    """A Modbus connection backed by pymodbus."""

    # -- spec surface ---------------------------------------------------------

    def for_unit(self, unit_id: int) -> PymodbusUnit:
        return PymodbusUnit(self, unit_id)

    async def _close_client(self, client: ModbusBaseClient) -> None:
        try:
            client.close()
        except (ModbusException, OSError) as err:
            raise ModbusConnectionError(str(err)) from err

    # -- internals ------------------------------------------------------------

    async def _connect_client(self) -> ModbusBaseClient:
        # Unlike tmodbus's create_* functions, pymodbus client constructors can
        # raise; map those failures like any other connect failure.
        try:
            client = await self._create_client()
        except (ModbusException, OSError) as err:
            raise _connect_error(err, self._params, self._target) from err
        try:
            connected = await client.connect()
        except (ModbusException, OSError) as err:
            _safe_close(client)
            raise _connect_error(err, self._params, self._target) from err
        if not connected or not client.connected:
            _safe_close(client)
            raise _connect_error(None, self._params, self._target)
        return client

    async def _create_client(self) -> ModbusBaseClient:
        params = self._params
        if isinstance(params, ModbusTcpParams):
            return AsyncModbusTcpClient(
                params.host,
                port=params.port,
                timeout=self._timeout,
                name="modbus_connection",
                reconnect_delay=0,
                retries=0,
                framer=FramerType(params.framer),
                trace_connect=self._on_trace_connect,
            )
        if isinstance(params, ModbusUdpParams):
            return AsyncModbusUdpClient(
                params.host,
                port=params.port,
                timeout=self._timeout,
                name="modbus_connection",
                reconnect_delay=0,
                retries=0,
                framer=FramerType(params.framer),
                trace_connect=self._on_trace_connect,
            )
        if isinstance(params, ModbusTlsParams):
            return AsyncModbusTlsClient(
                params.host,
                sslctx=await params.create_ssl_context(),
                port=params.port,
                timeout=self._timeout,
                name="modbus_connection",
                reconnect_delay=0,
                retries=0,
                framer=FramerType.TLS,
                trace_connect=self._on_trace_connect,
            )
        return AsyncModbusSerialClient(
            params.device,
            framer=FramerType(params.framer),
            baudrate=params.baudrate,
            bytesize=params.bytesize,
            parity=params.parity,
            stopbits=params.stopbits,
            timeout=self._timeout,
            name="modbus_connection",
            reconnect_delay=0,
            retries=0,
            trace_connect=self._on_trace_connect,
        )

    def _on_trace_connect(self, connecting: bool) -> None:
        """pymodbus trace hook: called True on connect, False on disconnect."""
        # A connection is lost when the transport takes it from us; close() and
        # disconnect() are us tearing it down, and also trigger this hook. Both
        # unpublish the client before tearing down, so a hook that finds no
        # published client is observing our own teardown.
        if connecting or self._closed or self._client is None:
            return
        self._client = None
        self._lost_callbacks.fire()


PymodbusConnection = ModbusConnection


class PymodbusUnit:
    """Represent a unit using pymodbus."""

    def __init__(self, connection: ModbusConnection, unit_id: int) -> None:
        self._conn = connection
        self._unit_id = unit_id

    @property
    def _client(self) -> ModbusBaseClient:
        client = self._conn._client
        if client is None:
            raise ModbusConnectionError("connection is not established")
        return client

    @property
    def connected(self) -> bool:
        return self._conn.connected

    def set_message_spacing(self, seconds: float) -> None:
        self._conn._pacer.set_unit_spacing(self._unit_id, seconds)

    def require_timeout(self, seconds: float | None) -> None:
        self._conn._require_timeout(self._unit_id, seconds)

    def require_connect_delay(self, seconds: float | None) -> None:
        self._conn._require_connect_delay(self._unit_id, seconds)

    # -- raw register I/O -----------------------------------------------------

    @_map_errors
    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        response = _check(
            await self._client.read_holding_registers(
                address, count=count, device_id=self._unit_id
            )
        )
        return response.registers

    @_map_errors
    async def read_input_registers(self, address: int, count: int) -> list[int]:
        response = _check(
            await self._client.read_input_registers(
                address, count=count, device_id=self._unit_id
            )
        )
        return response.registers

    @_map_errors
    async def write_register(self, address: int, value: int) -> None:
        _check(
            await self._client.write_register(address, value, device_id=self._unit_id)
        )

    @_map_errors
    async def write_registers(self, address: int, values: list[int]) -> None:
        _check(
            await self._client.write_registers(address, values, device_id=self._unit_id)
        )

    # -- raw coil / discrete-input I/O ----------------------------------------

    @_map_errors
    async def read_coils(self, address: int, count: int) -> list[bool]:
        response = _check(
            await self._client.read_coils(address, count=count, device_id=self._unit_id)
        )
        return response.bits[:count]

    @_map_errors
    async def read_discrete_inputs(self, address: int, count: int) -> list[bool]:
        response = _check(
            await self._client.read_discrete_inputs(
                address, count=count, device_id=self._unit_id
            )
        )
        return response.bits[:count]

    @_map_errors
    async def write_coil(self, address: int, value: bool) -> None:
        _check(await self._client.write_coil(address, value, device_id=self._unit_id))

    @_map_errors
    async def write_coils(self, address: int, values: list[bool]) -> None:
        _check(await self._client.write_coils(address, values, device_id=self._unit_id))

    # -- full function-code surface -------------------------------------------

    @_map_errors
    async def read_exception_status(self) -> int:  # 0x07
        response = _check(
            await self._client.read_exception_status(device_id=self._unit_id)
        )
        return int(response.status)

    @_map_errors
    async def report_server_id(self) -> bytes:  # 0x11
        # pymodbus types every response as the base ModbusPDU; the cast names
        # the concrete subclass that carries the function-code-specific attribute.
        response = cast(
            ReportDeviceIdResponse,
            _check(await self._client.report_device_id(device_id=self._unit_id)),
        )
        return bytes(response.identifier)

    @_map_errors
    async def mask_write_register(
        self, address: int, and_mask: int, or_mask: int
    ) -> None:  # 0x16
        _check(
            await self._client.mask_write_register(
                address=address,
                and_mask=and_mask,
                or_mask=or_mask,
                device_id=self._unit_id,
            )
        )

    @_map_errors
    async def read_write_registers(
        self,
        read_address: int,
        read_count: int,
        write_address: int,
        write_values: list[int],
    ) -> list[int]:  # 0x17
        response = _check(
            await self._client.readwrite_registers(
                read_address=read_address,
                read_count=read_count,
                write_address=write_address,
                values=write_values,
                device_id=self._unit_id,
            )
        )
        return response.registers

    @_map_errors
    async def read_fifo_queue(self, address: int) -> list[int]:  # 0x18
        response = cast(
            ReadFifoQueueResponse,
            _check(
                await self._client.read_fifo_queue(
                    address=address, device_id=self._unit_id
                )
            ),
        )
        return response.values

    @_map_errors
    async def read_device_identification(self) -> dict[int, bytes]:  # 0x2B / 0x0E
        response = cast(
            ReadDeviceInformationResponse,
            _check(await self._client.read_device_information(device_id=self._unit_id)),
        )
        return response.information

    @_map_errors
    async def read_file_record(
        self, file: int, record: int, length: int
    ) -> list[int]:  # 0x14
        request_record = FileRecord(
            file_number=file, record_number=record, record_length=length
        )
        response = cast(
            ReadFileRecordResponse,
            _check(
                await self._client.read_file_record(
                    records=[request_record], device_id=self._unit_id
                )
            ),
        )
        data = response.records[0].record_data
        return [int.from_bytes(data[i : i + 2], "big") for i in range(0, len(data), 2)]

    @_map_errors
    async def write_file_record(
        self, file: int, record: int, values: list[int]
    ) -> None:  # 0x15
        payload = b"".join(value.to_bytes(2, "big") for value in values)
        request_record = FileRecord(
            file_number=file,
            record_number=record,
            record_length=len(values),
            record_data=payload,
        )
        _check(
            await self._client.write_file_record(
                records=[request_record], device_id=self._unit_id
            )
        )

    @_map_errors
    async def diagnostics(self, sub_function: int, data: int = 0) -> int:  # 0x08
        request = _build_diagnostic(sub_function, data)
        request.dev_id = self._unit_id
        response = _check(await self._client.execute(False, request))
        message = response.message  # type: ignore[attr-defined]  # concrete response attr
        if isinstance(message, (bytes, bytearray)):
            return int.from_bytes(message, "big")
        if isinstance(message, (list, tuple)):
            return int(message[0]) if message else 0
        return int(message)

    @_map_errors
    async def get_comm_event_counter(self) -> tuple[bool, int]:  # 0x0B
        response = _check(
            await self._client.diag_get_comm_event_counter(device_id=self._unit_id)
        )
        # pymodbus already decodes the status word to "ready".
        return bool(response.status), int(response.count)

    @_map_errors
    async def get_comm_event_log(self) -> bytes:  # 0x0C
        response = cast(
            GetCommEventLogResponse,
            _check(await self._client.diag_get_comm_event_log(device_id=self._unit_id)),
        )
        return b"".join(int(event).to_bytes(1, "big") for event in response.events)

    def on_connection_lost(self, callback: Callable[[], None]) -> Callable[[], None]:
        return self._conn.on_connection_lost(callback)

    async def disconnect(self) -> None:
        await self._conn.disconnect()


async def connect_tcp(
    host: str,
    *,
    port: int = 502,
    timeout: float | None = None,
    framer: SocketFraming | None = None,
    message_spacing: float | None = None,
    connect_delay: float | None = None,
) -> ModbusConnection:
    """Open a Modbus TCP connection.

    Raises ``ModbusConnectionError`` if the connection cannot be established.
    """
    connection = ModbusConnection(
        ModbusTcpParams(host=host, port=port, framer=framer),
        timeout=timeout,
        message_spacing=message_spacing,
        connect_delay=connect_delay,
    )
    await connection.connect()
    return connection


async def connect_udp(
    host: str,
    *,
    port: int = 502,
    timeout: float | None = None,
    framer: SocketFraming = "socket",
    message_spacing: float | None = None,
    connect_delay: float | None = None,
) -> ModbusConnection:
    """Open a Modbus UDP connection.

    Raises ``ModbusConnectionError`` if the endpoint cannot be set up.
    """
    connection = ModbusConnection(
        ModbusUdpParams(host=host, port=port, framer=framer),
        timeout=timeout,
        message_spacing=message_spacing,
        connect_delay=connect_delay,
    )
    await connection.connect()
    return connection


async def connect_tls(
    host: str,
    *,
    port: int = 802,
    verify: bool | str = True,
    check_hostname: bool = True,
    client_cert: str | None = None,
    client_key: str | None = None,
    client_key_password: str | None = None,
    sslctx: ssl.SSLContext | None = None,
    timeout: float | None = None,
    message_spacing: float | None = None,
    connect_delay: float | None = None,
) -> ModbusConnection:
    """Open a Modbus/TLS connection.

    Raises ``ModbusConnectionError`` if the connection cannot be established.
    """
    connection = ModbusConnection(
        ModbusTlsParams(
            host=host,
            port=port,
            verify=verify,
            check_hostname=check_hostname,
            client_cert=client_cert,
            client_key=client_key,
            client_key_password=client_key_password,
            sslctx=sslctx,
        ),
        timeout=timeout,
        message_spacing=message_spacing,
        connect_delay=connect_delay,
    )
    await connection.connect()
    return connection


async def connect_serial(
    port: str,
    *,
    baudrate: int = 9600,
    bytesize: int = 8,
    parity: str = "N",
    stopbits: int = 1,
    timeout: float | None = None,
    framer: SerialFraming = "rtu",
    message_spacing: float | None = None,
    connect_delay: float | None = None,
) -> ModbusConnection:
    """Open a Modbus serial connection.

    Raises ``ModbusConnectionError`` if the port cannot be opened.
    """
    connection = ModbusConnection(
        ModbusSerialParams(
            device=port,
            baudrate=baudrate,
            bytesize=bytesize,  # type: ignore[arg-type]
            parity=parity,  # type: ignore[arg-type]
            stopbits=stopbits,  # type: ignore[arg-type]
            framer=framer,
        ),
        timeout=timeout,
        message_spacing=message_spacing,
        connect_delay=connect_delay,
    )
    await connection.connect()
    return connection
