"""Weishaupt heating circuit entity descriptions."""

# from ..kennfeld import power
from homeassistant.core import _LOGGER

from .description import EntityDescription, SensorDescription
from ...kennfeld.kennfeld import PowerMap
from .params import (
    POWER,
    COP,
    TEMPERATURE,
)

from ...coordinator import WeishauptCoordinator


def calculate_thermal_power(
    coordinator: WeishauptCoordinator,
    powermap: PowerMap,
) -> float | None:
    """Calculate thermal power."""
    device = coordinator.device

    power_request = device.heat_pump_input.power_request
    intake_temperature = device.system_input.intake_temperature
    flow_temperature = device.heat_pump_input.flow_temperature

    if power_request is None or intake_temperature is None or flow_temperature is None:
        return None

    power = powermap.map(
        intake_temperature,
        flow_temperature,
    )

    if power is None:
        return None

    return power_request / 100 * power


CALCULATERD_ENTITIES: tuple[EntityDescription, ...] = (
    SensorDescription(
        key="thermal_power",
        params=POWER,
        report_name="heat_pump",
        value_fn=lambda device: None,
        calculated_value_fn=calculate_thermal_power,
    ),
    SensorDescription(
        key="daily_cop",
        params=COP,
        report_name="statistics",
        value_fn=lambda device: round(device.statistics_input.daily_cop, 2),
    ),
    SensorDescription(
        key="yesterday_cop",
        params=COP,
        report_name="statistics",
        value_fn=lambda device: round(device.statistics_input.yesterday_cop, 2),
    ),
    SensorDescription(
        key="monthly_cop",
        params=COP,
        report_name="statistics",
        value_fn=lambda device: round(device.statistics_input.monthly_cop, 2),
    ),
    SensorDescription(
        key="yearly_cop",
        params=COP,
        report_name="statistics",
        value_fn=lambda device: round(device.statistics_input.yearly_cop, 2),
    ),
    SensorDescription(
        key="temperature_spread",
        report_name="heat_pump",
        params=TEMPERATURE,
        value_fn=lambda device: device.heat_pump_input.temperature_spread,
    ),
)
