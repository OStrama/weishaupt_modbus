"""Weishaupt system register models."""


from modbus_connection.model import enum, integer

from .component import WeishauptComponent
from .enums import SysError, SysOperatingDisplay, SysOperatingMode
from .register_values import sensor_temperature


class SystemStatus(WeishauptComponent):
    """Weishaupt system input registers (Input Registers - 3xxxx)."""

    register_space = "input"

    outside_temperature = sensor_temperature(30001)
    """Outside temperature."""

    intake_temperature = sensor_temperature(30002)
    """Air intake temperature."""

    error = enum(30003, SysError)
    """System error status."""

    warning = enum(30004, SysError)
    """System warning status."""

    error_free = integer(30005)
    """System error-free status."""

    operating_display = enum(30006, SysOperatingDisplay)
    """Operating display status."""


class SystemConfig(WeishauptComponent):
    """Weishaupt system configuration registers (Holding Registers - 4xxxx)."""

    register_space = "holding"

    operating_mode = enum(40001, SysOperatingMode, writable=True)
    """System operating mode."""

    pv_setpoint = integer(40002, unit="W", writable=True)
    """PV setpoint in watts."""
