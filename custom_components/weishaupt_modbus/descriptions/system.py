"""Weishaupt system entity descriptions."""

from .description import (
    EntityDescription,
    NumberDescription,
    SelectDescription,
    SensorDescription,
)
from .myenums import SystemOperationMode
from .params import ENUM, NUMBER_POWER, TEMPERATURE

SYSTEM_ENTITIES: tuple[EntityDescription, ...] = (
    SensorDescription(
        key="outside_temperature",
        params=TEMPERATURE,
        report_name="system",
        value_fn=lambda device: device.system_input.outside_temperature,
    ),
    SensorDescription(
        key="intake_temperature",
        params=TEMPERATURE,
        report_name="system",
        value_fn=lambda device: device.system_input.intake_temperature,
    ),
    SensorDescription(
        key="error",
        params=ENUM,
        report_name="system",
        value_fn=lambda device: device.system_input.error,
    ),
    SensorDescription(
        key="warning",
        params=ENUM,
        report_name="system",
        value_fn=lambda device: device.system_input.warning,
    ),
    SensorDescription(
        key="error_free",
        params=ENUM,
        report_name="system",
        value_fn=lambda device: device.system_input.error_free,
    ),
    SensorDescription(
        key="operating_display",
        params=ENUM,
        report_name="system",
        value_fn=lambda device: device.system_input.operating_display,
    ),
    SelectDescription(
        key="operating_mode",
        enum=SystemOperationMode,
        report_name="system",
        value_fn=lambda device: device.system_config.operating_mode,
        set_value_fn=lambda device, value: device.system_config.write(
            "operating_mode",
            value,
        ),
    ),
    NumberDescription(
        key="pv_setpoint",
        params=NUMBER_POWER,
        report_name="system",
        value_fn=lambda device: device.system_config.pv_setpoint,
        set_value_fn=lambda device, value: device.system_config.write(
            "pv_setpoint",
            value,
        ),
    ),
)
