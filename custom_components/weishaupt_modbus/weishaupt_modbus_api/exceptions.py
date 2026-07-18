"""Custom exceptions for the Weishaupt Modbus API."""


class WeishauptModbusError(Exception):
    """Base exception for Weishaupt Modbus communication."""


class ConnectionFailedError(WeishauptModbusError):
    """Exception raised when the Modbus connection fails."""


class ReadError(WeishauptModbusError):
    """Exception raised when a Modbus read operation fails."""


class WriteError(WeishauptModbusError):
    """Exception raised when a Modbus write operation fails."""
