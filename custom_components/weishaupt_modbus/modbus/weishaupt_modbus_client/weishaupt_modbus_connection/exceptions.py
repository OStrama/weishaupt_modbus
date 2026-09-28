"""Define the public Modbus exception hierarchy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, ClassVar


class ExceptionCode(IntEnum):
    """The Modbus exception codes a device can answer with."""

    ILLEGAL_FUNCTION = 0x01
    ILLEGAL_DATA_ADDRESS = 0x02
    ILLEGAL_DATA_VALUE = 0x03
    SERVER_DEVICE_FAILURE = 0x04
    ACKNOWLEDGE = 0x05
    SERVER_DEVICE_BUSY = 0x06
    MEMORY_PARITY_ERROR = 0x08
    GATEWAY_PATH_UNAVAILABLE = 0x0A
    GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND = 0x0B


def _describe(name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    """Render a unit operation call, e.g. ``read_holding_registers(9, 2)``."""
    shown = [_short(a) for a in args]
    shown += [f"{key}={_short(value)}" for key, value in kwargs.items()]
    return f"{name}({', '.join(shown)})"


def _short(value: Any) -> str:
    """Render one argument, abbreviating a long sequence of values."""
    if isinstance(value, (list, tuple)) and len(value) > 4:
        return f"[{', '.join(repr(v) for v in value[:4])}, … {len(value)} values]"
    return repr(value)


@dataclass(frozen=True)
class ReadBlock:
    """The planned block read an exception response refused."""

    space: str
    address: int
    count: int


class ModbusError(Exception):
    """Base class for every error raised by a modbus_connection backend."""


class ModbusConnectionError(ModbusError):
    """The link is down: not connected, connection lost, or transport failure."""


class ClientClosedError(ModbusConnectionError):
    """A request was attempted on a closed connection."""


class ModbusTimeoutError(ModbusError, TimeoutError):
    """A Modbus operation timed out."""


class ModbusProtocolError(ModbusError):
    """A response could not be used.

    Either the frame was corrupt, or a well-formed answer belonged to a
    different request than the one sent.
    """


class ModbusDesyncError(ModbusProtocolError):
    """The reply answers a different exchange; the backend dropped the link."""


class ModbusExceptionError(ModbusError):
    """The device returned a Modbus exception response.

    A code with a standard meaning raises the matching subclass, so callers
    branch with ``except`` or ``isinstance`` instead of comparing
    ``exception_code`` against magic numbers.
    """

    def __init__(
        self,
        exception_code: int | None,
        message: str | None = None,
        *,
        block: ReadBlock | None = None,
    ) -> None:
        if (
            exception_code is not None
            and exception_code in ExceptionCode._value2member_map_
        ):
            exception_code = ExceptionCode(exception_code)
        self.exception_code = exception_code
        # The planned block read this response refused; None for a raw request.
        self.block = block
        super().__init__(
            message or f"Device returned Modbus exception code {exception_code}"
        )

    @property
    def space(self) -> str | None:
        """Deprecated: read ``block.space``."""
        return self.block.space if self.block else None

    @property
    def address(self) -> int | None:
        """Deprecated: read ``block.address``."""
        return self.block.address if self.block else None

    @property
    def count(self) -> int | None:
        """Deprecated: read ``block.count``."""
        return self.block.count if self.block else None

    @staticmethod
    def from_code(
        exception_code: int | None,
        message: str | None = None,
        *,
        block: ReadBlock | None = None,
    ) -> ModbusExceptionError:
        """Build the subclass matching ``exception_code``, or the base class."""
        cls: type[ModbusExceptionError] = ModbusExceptionError
        if exception_code is not None:
            cls = _CODED_ERRORS.get(exception_code, cls)
        return cls(exception_code, message, block=block)


class _CodedError(ModbusExceptionError):
    """A Modbus exception response with a fixed, standard code."""

    code: ClassVar[ExceptionCode]

    def __init__(
        self,
        exception_code: int | None = None,
        message: str | None = None,
        *,
        block: ReadBlock | None = None,
    ) -> None:
        super().__init__(
            self.code if exception_code is None else exception_code,
            message,
            block=block,
        )


class IllegalFunctionError(_CodedError):
    """Code 1: the device does not support the requested function."""

    code = ExceptionCode.ILLEGAL_FUNCTION


class IllegalDataAddressError(_CodedError):
    """Code 2: the device does not serve the requested address."""

    code = ExceptionCode.ILLEGAL_DATA_ADDRESS


class IllegalDataValueError(_CodedError):
    """Code 3: the device rejected a value in the request."""

    code = ExceptionCode.ILLEGAL_DATA_VALUE


class ServerDeviceFailureError(_CodedError):
    """Code 4: the device failed while performing the request."""

    code = ExceptionCode.SERVER_DEVICE_FAILURE


class AcknowledgeError(_CodedError):
    """Code 5: the device accepted the request but needs time to process it."""

    code = ExceptionCode.ACKNOWLEDGE


class ServerDeviceBusyError(_CodedError):
    """Code 6: the device is busy; retry the request later."""

    code = ExceptionCode.SERVER_DEVICE_BUSY


class MemoryParityError(_CodedError):
    """Code 8: the device detected a parity error reading its memory."""

    code = ExceptionCode.MEMORY_PARITY_ERROR


class GatewayPathUnavailableError(_CodedError):
    """Code 10: the gateway has no path to the target device."""

    code = ExceptionCode.GATEWAY_PATH_UNAVAILABLE


class GatewayTargetError(_CodedError):
    """Code 11: the gateway's target device did not respond."""

    code = ExceptionCode.GATEWAY_TARGET_DEVICE_FAILED_TO_RESPOND


_CODED_ERRORS: dict[int, type[_CodedError]] = {
    cls.code: cls for cls in _CodedError.__subclasses__()
}

# Deprecated alias: the update-aborting error is the typed exception itself,
# with the refused block on ``block``. Kept so ``except BlockReadError`` and
# ``isinstance`` checks keep working.
BlockReadError = ModbusExceptionError
