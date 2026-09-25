"""Weishaupt second heat source entity descriptions."""

from .description import (
    EntityDescription,
    NumberDescription,
    SelectDescription,
    SensorDescription,
)
from .myenums import (
    ElectricHeater1Configuration,
    ElectricHeater2Configuration,
    SecondHeatSourceConfiguration,
    SecondHeatSourceStatus,
)
from .params import (
    BIVALENCE_TEMPERATURE,
    EMPTY,
    ENUM,
    NUMBER_EMPTY,
    TEMPERATURE,
    TIME_HOURS,
)

SECOND_HEAT_SOURCE_ENTITIES: tuple[EntityDescription, ...] = (
    SensorDescription(
        key="status",
        params=ENUM,
        report_name="second_heat_source",
        value_fn=lambda device: device.second_heat_source_input.status,
    ),
    SensorDescription(
        key="electric_heater_1_switch_cycles",
        params=EMPTY,
        report_name="second_heat_source",
        value_fn=lambda device: (
            device.second_heat_source_input.electric_heater_1_switch_cycles
        ),
    ),
    SensorDescription(
        key="electric_heater_1_operating_hours",
        params=TIME_HOURS,
        report_name="second_heat_source",
        value_fn=lambda device: (
            device.second_heat_source_input.electric_heater_1_operating_hours
        ),
    ),
    SensorDescription(
        key="electric_heater_1_status",
        params=ENUM,
        report_name="second_heat_source",
        value_fn=lambda device: (
            device.second_heat_source_input.electric_heater_1_status
        ),
    ),
    SensorDescription(
        key="electric_heater_2_status",
        params=ENUM,
        report_name="second_heat_source",
        value_fn=lambda device: (
            device.second_heat_source_input.electric_heater_2_status
        ),
    ),
    SensorDescription(
        key="electric_heater_2_switch_cycles",
        params=EMPTY,
        report_name="second_heat_source",
        value_fn=lambda device: (
            device.second_heat_source_input.electric_heater_2_switch_cycles
        ),
    ),
    SensorDescription(
        key="electric_heater_2_operating_hours",
        params=TIME_HOURS,
        report_name="second_heat_source",
        value_fn=lambda device: (
            device.second_heat_source_input.electric_heater_2_operating_hours
        ),
    ),
    SelectDescription(
        key="configuration",
        enum=SecondHeatSourceConfiguration,
        report_name="second_heat_source",
        value_fn=lambda device: device.second_heat_source_config.configuration,
        set_value_fn=lambda device, value: device.second_heat_source_config.write(
            "configuration",
            value,
        ),
    ),
    SelectDescription(
        key="electric_heater_1_configuration",
        enum=ElectricHeater1Configuration,
        report_name="second_heat_source",
        value_fn=lambda device: (
            device.second_heat_source_config.electric_heater_1_configuration
        ),
        set_value_fn=lambda device, value: device.second_heat_source_config.write(
            "electric_heater_1_configuration",
            value,
        ),
    ),
    SelectDescription(
        key="electric_heater_2_configuration",
        enum=ElectricHeater2Configuration,
        report_name="second_heat_source",
        value_fn=lambda device: (
            device.second_heat_source_config.electric_heater_2_configuration
        ),
        set_value_fn=lambda device, value: device.second_heat_source_config.write(
            "electric_heater_2_configuration",
            value,
        ),
    ),
    NumberDescription(
        key="limit_temperature",
        params=BIVALENCE_TEMPERATURE,
        report_name="second_heat_source",
        value_fn=lambda device: device.second_heat_source_config.limit_temperature,
        set_value_fn=lambda device, value: device.second_heat_source_config.write(
            "limit_temperature",
            value,
        ),
    ),
    NumberDescription(
        key="bivalence_temperature",
        params=BIVALENCE_TEMPERATURE,
        report_name="second_heat_source",
        value_fn=lambda device: device.second_heat_source_config.bivalence_temperature,
        set_value_fn=lambda device, value: device.second_heat_source_config.write(
            "bivalence_temperature",
            value,
        ),
    ),
    NumberDescription(
        key="bivalence_temperature_hot_water",
        params=BIVALENCE_TEMPERATURE,
        report_name="second_heat_source",
        value_fn=lambda device: (
            device.second_heat_source_config.bivalence_temperature_hot_water
        ),
        set_value_fn=lambda device, value: device.second_heat_source_config.write(
            "bivalence_temperature_hot_water",
            value,
        ),
    ),
)
