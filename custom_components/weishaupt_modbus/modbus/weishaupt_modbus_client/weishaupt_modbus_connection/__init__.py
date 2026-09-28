"""Provide backend-neutral Modbus connections, units, and shared types."""

from ._client import (
    BaseModbusConnection as ModbusConnection,
)
from ._client import (
    ModbusSerialParams,
    ModbusTcpParams,
    ModbusTlsParams,
    ModbusUdpParams,
)
from ._protocol import ModbusUnit
from ._types import WordOrder
from .exceptions import (
    AcknowledgeError,
    BlockReadError,
    ClientClosedError,
    ExceptionCode,
    GatewayPathUnavailableError,
    GatewayTargetError,
    IllegalDataAddressError,
    IllegalDataValueError,
    IllegalFunctionError,
    MemoryParityError,
    ModbusConnectionError,
    ModbusDesyncError,
    ModbusError,
    ModbusExceptionError,
    ModbusProtocolError,
    ModbusTimeoutError,
    ReadBlock,
    ServerDeviceBusyError,
    ServerDeviceFailureError,
)

__all__ = [
    "ReadBlock",
    "ServerDeviceFailureError",
    "ServerDeviceBusyError",
    "MemoryParityError",
    "IllegalFunctionError",
    "IllegalDataValueError",
    "IllegalDataAddressError",
    "GatewayTargetError",
    "GatewayPathUnavailableError",
    "ExceptionCode",
    "AcknowledgeError",
    "BlockReadError",
    "ClientClosedError",
    "ModbusConnection",
    "ModbusConnectionError",
    "ModbusError",
    "ModbusExceptionError",
    "ModbusDesyncError",
    "ModbusProtocolError",
    "ModbusSerialParams",
    "ModbusTcpParams",
    "ModbusTimeoutError",
    "ModbusTlsParams",
    "ModbusUdpParams",
    "ModbusUnit",
    "WordOrder",
]
