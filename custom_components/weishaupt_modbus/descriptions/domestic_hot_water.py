"""Weishaupt domestic hot water entity descriptions."""

from .description import (
    EntityDescription,
    NumberDescription,
    SelectDescription,
    SensorDescription,
)
from .params import (
    ENUM,
    NUMBER_EMPTY,
    SGR_RAISE,
    TEMPERATURE,
    WW_TEMP,
)


DOMESTIC_HOT_WATER_ENTITIES: tuple[EntityDescription, ...] = (
    SensorDescription(
        key="target_temperature",
        params=TEMPERATURE,
        report_name="domestic_hot_water",
        value_fn=lambda device: device.domestic_hot_water_input.target_temperature,
    ),
    SensorDescription(
        key="temperature",
        params=TEMPERATURE,
        report_name="domestic_hot_water",
        value_fn=lambda device: device.domestic_hot_water_input.temperature,
    ),
    SelectDescription(
        key="configuration",
        enum=None,
        report_name="domestic_hot_water",
        value_fn=lambda device: device.domestic_hot_water_config.configuration,
        set_value_fn=lambda device, value: device.domestic_hot_water_config.write(
            "configuration",
            value,
        ),
    ),
    NumberDescription(
        key="push",
        params=NUMBER_EMPTY,
        report_name="domestic_hot_water",
        value_fn=lambda device: device.domestic_hot_water_config.push,
        set_value_fn=lambda device, value: device.domestic_hot_water_config.write(
            "push",
            value,
        ),
    ),
    NumberDescription(
        key="normal_temperature",
        params=WW_TEMP,
        report_name="domestic_hot_water",
        value_fn=lambda device: device.domestic_hot_water_config.normal_temperature,
        set_value_fn=lambda device, value: device.domestic_hot_water_config.write(
            "normal_temperature",
            value,
        ),
    ),
    NumberDescription(
        key="lowering_temperature",
        params=WW_TEMP,
        report_name="domestic_hot_water",
        value_fn=lambda device: device.domestic_hot_water_config.lowering_temperature,
        set_value_fn=lambda device, value: device.domestic_hot_water_config.write(
            "lowering_temperature",
            value,
        ),
    ),
    NumberDescription(
        key="sg_ready_raise",
        params=SGR_RAISE,
        report_name="domestic_hot_water",
        value_fn=lambda device: device.domestic_hot_water_config.sg_ready_raise,
        set_value_fn=lambda device, value: device.domestic_hot_water_config.write(
            "sg_ready_raise",
            value,
        ),
    ),
)
