"""Weishaupt domestic hot water register models."""

from modbus_connection.model import Component, gauge, integer


class DomesticHotWaterInput(Component):
    """Weishaupt domestic hot water input registers."""

    register_space = "input"

    target_temperature = gauge(
        32101,
        0.1,
        unit="°C",
        nan=32768,
    )

    temperature = gauge(
        32102,
        0.1,
        unit="°C",
        nan=32768,
    )


class DomesticHotWaterConfig(Component):
    """Weishaupt domestic hot water configuration registers."""

    configuration = integer(42101)

    push = integer(42102)

    normal_temperature = gauge(
        42103,
        0.1,
        unit="°C",
        nan=32768,
    )

    lowering_temperature = gauge(
        42104,
        0.1,
        unit="°C",
        nan=32768,
    )

    sg_ready_raise = gauge(
        42105,
        0.1,
        unit="°C",
        nan=32768,
    )
