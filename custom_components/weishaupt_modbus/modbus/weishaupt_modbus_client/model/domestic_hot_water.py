"""Weishaupt domestic hot water register models."""

from modbus_connection.model import Component, gauge, integer

from .register_values import sensor_temperature


class DomesticHotWaterInput(Component):
    """Weishaupt domestic hot water input registers."""

    register_space = "input"

    target_temperature = gauge(
        32101,
        0.1,
        unit="°C",
        nan=32768,
    )

    temperature = sensor_temperature(32102)


class DomesticHotWaterConfig(Component):
    """Weishaupt domestic hot water configuration registers."""

    configuration = integer(
        42101,
        writable=True,
    )

    push = integer(
        42102,
        writable=True,
    )

    normal_temperature = gauge(
        42103,
        0.1,
        unit="°C",
        nan=32768,
        writable=True,
    )

    lowering_temperature = gauge(
        42104,
        0.1,
        unit="°C",
        nan=32768,
        writable=True,
    )

    sg_ready_raise = gauge(
        42105,
        0.1,
        unit="°C",
        nan=32768,
        writable=True,
    )
