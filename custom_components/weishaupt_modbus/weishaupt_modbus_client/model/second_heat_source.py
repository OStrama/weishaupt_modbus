"""Weishaupt second heat source register models."""

from modbus_connection.model import Component, enum, gauge, integer

from .enums import (
    ElectricHeater1Configuration,
    ElectricHeater2Configuration,
    SecondHeatSourceConfiguration,
    SecondHeatSourceStatus,
)


class SecondHeatSourceInput(Component):
    """Weishaupt second heat source input registers."""

    register_space = "input"

    status = enum(
        34101,
        SecondHeatSourceStatus,
    )

    # This is correct. The modbus documentation is wrong.
    electric_heater_1_switch_cycles = integer(34102)

    # This is always 0. Error of weishaupt on modbus. The modbus documentation is wrong.
    electric_heater_1_operating_hours = gauge(
        34103,
        1,
        unit="h",
    )

    electric_heater_1_status = enum(
        34104,
        SecondHeatSourceStatus,
    )

    electric_heater_2_status = enum(
        34105,
        SecondHeatSourceStatus,
    )

    # This is correct. The modbus documentation is wrong.
    electric_heater_2_switch_cycles = integer(34106)

    # This is always 0. Error of weishaupt on modbus. The modbus documentation is wrong.
    electric_heater_2_operating_hours = gauge(
        34107,
        1,
        unit="h",
    )


class SecondHeatSourceConfig(Component):
    """Weishaupt second heat source configuration registers."""

    configuration = enum(
        44101,
        SecondHeatSourceConfiguration,
        writable=True,
    )

    electric_heater_1_configuration = enum(
        44102,
        ElectricHeater1Configuration,
        writable=True,
    )

    electric_heater_2_configuration = enum(
        44103,
        ElectricHeater2Configuration,
        writable=True,
    )

    limit_temperature = gauge(
        44104,
        0.1,
        unit="°C",
        writable=True,
        nan=32768,
    )

    bivalence_temperature = gauge(
        44105,
        0.1,
        unit="°C",
        writable=True,
        nan=32768,
    )

    bivalence_temperature_hot_water = gauge(
        44106,
        0.1,
        unit="°C",
        writable=True,
        nan=32768,
    )
