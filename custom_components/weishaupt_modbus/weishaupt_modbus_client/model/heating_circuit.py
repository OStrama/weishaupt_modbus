"""Weishaupt heating circuit register models."""

from modbus_connection.model import Component, enum, gauge, integer, repeating_group

from .enums import (
    HeatingCircuitConfiguration,
    HeatingCircuitDemand,
    HeatingCircuitOperation,
)


class HeatingCircuitInput(Component):
    """Weishaupt heating circuit input registers."""

    register_space = "input"

    room_target_temperature = gauge(
        31101,
        0.1,
        unit="°C",
        nan=32768,
    )

    room_temperature = gauge(
        31102,
        0.1,
        unit="°C",
        nan=32768,
    )

    room_humidity = integer(
        31103,
        unit="%",
        nan=65535,
    )

    flow_target_temperature = gauge(
        31104,
        0.1,
        unit="°C",
        nan=32768,
    )

    flow_temperature = gauge(
        31105,
        0.1,
        unit="°C",
        nan=32768,
    )

    register_31106 = integer(31106)


class HeatingCircuitConfig(Component):
    """Weishaupt heating circuit configuration registers."""

    configuration = enum(
        41101,
        HeatingCircuitConfiguration,
        writable=True,
    )

    demand = enum(
        41102,
        HeatingCircuitDemand,
        writable=True,
    )

    operation_mode = enum(
        41103,
        HeatingCircuitOperation,
        writable=True,
    )

    party_pause = integer(
        41104,
        writable=True,
    )

    comfort_room_target_temperature = gauge(
        41105,
        0.1,
        unit="°C",
        nan=32768,
        writable=True,
    )

    normal_room_target_temperature = gauge(
        41106,
        0.1,
        unit="°C",
        nan=32768,
        writable=True,
    )

    lowering_room_target_temperature = gauge(
        41107,
        0.1,
        unit="°C",
        nan=32768,
        writable=True,
    )

    heating_curve = gauge(
        41108,
        0.01,
        writable=True,
    )

    summer_winter_switch_temperature = gauge(
        41109,
        0.1,
        unit="°C",
        nan=32768,
        writable=True,
    )

    constant_heating_temperature = gauge(
        41110,
        0.1,
        unit="°C",
        nan=32768,
        writable=True,
    )

    constant_heating_lowering_temperature = gauge(
        41111,
        0.1,
        unit="°C",
        nan=32768,
        writable=True,
    )

    constant_cooling_temperature = gauge(
        41112,
        0.1,
        unit="°C",
        nan=32768,
        writable=True,
    )


class HeatingCircuitInputs(Component):
    """Repeated Weishaupt heating circuit input registers."""

    heating_circuits = repeating_group(
        4,
        HeatingCircuitInput,
        stride=100,
    )


class HeatingCircuitConfigs(Component):
    """Repeated Weishaupt heating circuit configuration registers."""

    heating_circuits = repeating_group(
        4,
        HeatingCircuitConfig,
        stride=100,
    )
