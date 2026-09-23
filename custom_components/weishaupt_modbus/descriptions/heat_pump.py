"""Weishaupt heat pump entity descriptions."""

from .description import (
    EntityDescription,
    NumberDescription,
    SelectDescription,
    SensorDescription,
)
from .params import EMPTY, SENSOR_PERCENTAGE, TEMPERATURE, ENUM

HEAT_PUMP_ENTITIES: tuple[EntityDescription, ...] = (
    # Heat pump input
    SensorDescription(
        key="operation",
        report_name="heat_pump",
        params=ENUM,
        value_fn=lambda device: device.heat_pump_input.operation,
    ),
    SensorDescription(
        key="fault",
        report_name="heat_pump",
        params=ENUM,
        value_fn=lambda device: device.heat_pump_input.fault,
    ),
    SensorDescription(
        key="power_request",
        report_name="heat_pump",
        params=SENSOR_PERCENTAGE,
        value_fn=lambda device: device.heat_pump_input.power_request,
    ),
    SensorDescription(
        key="flow_temperature",
        report_name="heat_pump",
        params=TEMPERATURE,
        value_fn=lambda device: device.heat_pump_input.flow_temperature,
    ),
    SensorDescription(
        key="return_temperature",
        report_name="heat_pump",
        params=TEMPERATURE,
        value_fn=lambda device: device.heat_pump_input.return_temperature,
    ),
    SensorDescription(
        key="evaporation_temperature",
        report_name="heat_pump",
        params=TEMPERATURE,
        value_fn=lambda device: device.heat_pump_input.evaporation_temperature,
    ),
    SensorDescription(
        key="compressor_suction_temperature",
        report_name="heat_pump",
        params=TEMPERATURE,
        value_fn=lambda device: device.heat_pump_input.compressor_suction_temperature,
    ),
    SensorDescription(
        key="diverter_temperature",
        report_name="heat_pump",
        params=TEMPERATURE,
        value_fn=lambda device: device.heat_pump_input.diverter_temperature,
    ),
    SensorDescription(
        key="regenerative_flow_temperature",
        report_name="heat_pump",
        params=TEMPERATURE,
        value_fn=lambda device: device.heat_pump_input.regenerative_flow_temperature,
    ),
    SensorDescription(
        key="buffer_temperature",
        report_name="heat_pump",
        params=TEMPERATURE,
        value_fn=lambda device: device.heat_pump_input.buffer_temperature,
    ),
    SensorDescription(
        key="precise_flow_temperature",
        report_name="heat_pump",
        params=TEMPERATURE,
        value_fn=lambda device: device.heat_pump_input.precise_flow_temperature,
    ),
    SensorDescription(
        key="temperature_spread",
        report_name="heat_pump",
        params=TEMPERATURE,
        value_fn=lambda device: device.heat_pump_input.temperature_spread,
    ),
    # Heat pump configuration
    SelectDescription(
        key="configuration",
        report_name="heat_pump",
        params=EMPTY,
        value_fn=lambda device: device.heat_pump_config.configuration,
        set_value_fn=lambda device, value: device.heat_pump_config.set_configuration(
            value
        ),
    ),
    SelectDescription(
        key="rest_mode",
        report_name="heat_pump",
        params=EMPTY,
        value_fn=lambda device: device.heat_pump_config.rest_mode,
        set_value_fn=lambda device, value: device.heat_pump_config.set_rest_mode(value),
    ),
    NumberDescription(
        key="pump_start_type",
        report_name="heat_pump",
        params=EMPTY,
        value_fn=lambda device: device.heat_pump_config.pump_start_type,
        set_value_fn=lambda device, value: device.heat_pump_config.set_pump_start_type(
            value
        ),
    ),
    NumberDescription(
        key="heating_pump_power_setpoint",
        report_name="heat_pump",
        params=SENSOR_PERCENTAGE,
        value_fn=lambda device: device.heat_pump_config.heating_pump_power_setpoint,
        set_value_fn=lambda device, value: (
            device.heat_pump_config.set_heating_pump_power_setpoint(value)
        ),
    ),
    NumberDescription(
        key="cooling_pump_power_setpoint",
        report_name="heat_pump",
        params=SENSOR_PERCENTAGE,
        value_fn=lambda device: device.heat_pump_config.cooling_pump_power_setpoint,
        set_value_fn=lambda device, value: (
            device.heat_pump_config.set_cooling_pump_power_setpoint(value)
        ),
    ),
    NumberDescription(
        key="hot_water_pump_power_setpoint",
        report_name="heat_pump",
        params=SENSOR_PERCENTAGE,
        value_fn=lambda device: device.heat_pump_config.hot_water_pump_power_setpoint,
        set_value_fn=lambda device, value: (
            device.heat_pump_config.set_hot_water_pump_power_setpoint(value)
        ),
    ),
    NumberDescription(
        key="defrost_pump_power_setpoint",
        report_name="heat_pump",
        params=SENSOR_PERCENTAGE,
        value_fn=lambda device: device.heat_pump_config.defrost_pump_power_setpoint,
        set_value_fn=lambda device, value: (
            device.heat_pump_config.set_defrost_pump_power_setpoint(value)
        ),
    ),
    NumberDescription(
        key="heating_flow_rate_setpoint",
        report_name="heat_pump",
        params=EMPTY,
        value_fn=lambda device: device.heat_pump_config.heating_flow_rate_setpoint,
        set_value_fn=lambda device, value: (
            device.heat_pump_config.set_heating_flow_rate_setpoint(value)
        ),
    ),
    NumberDescription(
        key="cooling_flow_rate_setpoint",
        report_name="heat_pump",
        params=EMPTY,
        value_fn=lambda device: device.heat_pump_config.cooling_flow_rate_setpoint,
        set_value_fn=lambda device, value: (
            device.heat_pump_config.cooling_flow_rate_setpoint(value)
        ),
    ),
    NumberDescription(
        key="hot_water_flow_rate_setpoint",
        report_name="heat_pump",
        params=EMPTY,
        value_fn=lambda device: device.heat_pump_config.hot_water_flow_rate_setpoint,
        set_value_fn=lambda device, value: (
            device.heat_pump_config.hot_water_flow_rate_setpoint(value)
        ),
    ),
)
