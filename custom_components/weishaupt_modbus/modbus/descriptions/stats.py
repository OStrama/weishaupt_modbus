"""Weishaupt statistics entity descriptions."""

from .description import EntityDescription, SensorDescription
from .params import ENERGY, EMPTY

STATISTICS_ENTITIES: tuple[EntityDescription, ...] = (
    SensorDescription(
        key="total_energy_today",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.total_energy_today,
    ),
    SensorDescription(
        key="total_energy_yesterday",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.total_energy_yesterday,
    ),
    SensorDescription(
        key="total_energy_month",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.total_energy_month,
    ),
    SensorDescription(
        key="total_energy_year",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.total_energy_year,
    ),
    SensorDescription(
        key="heating_energy_today",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.heating_energy_today,
    ),
    SensorDescription(
        key="heating_energy_yesterday",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.heating_energy_yesterday,
    ),
    SensorDescription(
        key="heating_energy_month",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.heating_energy_month,
    ),
    SensorDescription(
        key="heating_energy_year",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.heating_energy_year,
    ),
    SensorDescription(
        key="hot_water_energy_today",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.hot_water_energy_today,
    ),
    SensorDescription(
        key="hot_water_energy_yesterday",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.hot_water_energy_yesterday,
    ),
    SensorDescription(
        key="hot_water_energy_month",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.hot_water_energy_month,
    ),
    SensorDescription(
        key="hot_water_energy_year",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.hot_water_energy_year,
    ),
    SensorDescription(
        key="cooling_energy_today",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.cooling_energy_today,
    ),
    SensorDescription(
        key="cooling_energy_yesterday",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.cooling_energy_yesterday,
    ),
    SensorDescription(
        key="cooling_energy_month",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.cooling_energy_month,
    ),
    SensorDescription(
        key="cooling_energy_year",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.cooling_energy_year,
    ),
    SensorDescription(
        key="defrost_energy_today",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.defrost_energy_today,
    ),
    SensorDescription(
        key="defrost_energy_yesterday",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.defrost_energy_yesterday,
    ),
    SensorDescription(
        key="defrost_energy_month",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.defrost_energy_month,
    ),
    SensorDescription(
        key="defrost_energy_year",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.defrost_energy_year,
    ),
    SensorDescription(
        key="total_energy_2_today",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.total_energy_2_today,
    ),
    SensorDescription(
        key="total_energy_2_yesterday",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.total_energy_2_yesterday,
    ),
    SensorDescription(
        key="total_energy_2_month",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.total_energy_2_month,
    ),
    SensorDescription(
        key="total_energy_2_year",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.total_energy_2_year,
    ),
    SensorDescription(
        key="electric_energy_today",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.electric_energy_today,
    ),
    SensorDescription(
        key="electric_energy_yesterday",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.electric_energy_yesterday,
    ),
    SensorDescription(
        key="electric_energy_month",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.electric_energy_month,
    ),
    SensorDescription(
        key="electric_energy_year",
        params=ENERGY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.electric_energy_year,
    ),
    SensorDescription(
        key="adr36801",
        params=EMPTY,
        report_name="statistics",
        value_fn=lambda device: device.statistics_input.register_36801,
    ),
)
