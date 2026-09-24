"""Weishaupt system register models."""

from modbus_connection.model import Component, boolean, enum, gauge, integer

from .enums import SysError, SysOperatingDisplay, SysOperatingMode


class SystemStatus(Component):
    """Weishaupt system input registers (Input Registers - 3xxxx)."""

    register_space = "input"

    outside_temperature = gauge(
        30001,
        scale=0.1,
        unit="°C",
    )
    """Outside temperature."""

    intake_temperature = gauge(
        30002,
        scale=0.1,
        unit="°C",
    )
    """Air intake temperature."""

    error = enum(30003, SysError)
    """System error status."""

    warning = enum(30004, SysError)
    """System warning status."""

    error_free = integer(30005)
    """System error-free status."""

    operating_display = enum(30006, SysOperatingDisplay)
    """Operating display status."""


class SystemConfig(Component):
    """Weishaupt system configuration registers (Holding Registers - 4xxxx)."""

    register_space = "holding"

    operating_mode = enum(40001, SysOperatingMode, writable=True)
    """System operating mode."""

    pv_setpoint = integer(40002, unit="W", writable=True)
    """PV setpoint in watts."""
