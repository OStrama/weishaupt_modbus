"""Weishaupt heat pump entity descriptions."""

from .description import (
    EntityDescription,
    NumberDescription,
    SelectDescription,
    SensorDescription,
)
from .params import (
    ENUM,
    NUMBER_FLOWRATE,
    NUMBER_PERCENTAGE,
    SENSOR_PERCENTAGE,
    TEMPERATURE,
)


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
        enum=None,
        value_fn=lambda device: device.heat_pump_config.configuration,
        set_value_fn=lambda device, value: device.heat_pump_config.write(
            "configuration",
            value,
        ),
    ),
    SelectDescription(
        key="rest_mode",
        report_name="heat_pump",
        enum=None,
        value_fn=lambda device: device.heat_pump_config.rest_mode,
        set_value_fn=lambda device, value: device.heat_pump_config.write(
            "rest_mode",
            value,
        ),
    ),
    SelectDescription(
        key="pump_start_type",
        report_name="heat_pump",
        enum=None,
        value_fn=lambda device: device.heat_pump_config.pump_start_type,
        set_value_fn=lambda device, value: device.heat_pump_config.write(
            "pump_start_type",
            value,
        ),
    ),
    NumberDescription(
        key="heating_pump_power_setpoint",
        report_name="heat_pump",
        params=NUMBER_PERCENTAGE,
        value_fn=lambda device: device.heat_pump_config.heating_pump_power_setpoint,
        set_value_fn=lambda device, value: device.heat_pump_config.write(
            "heating_pump_power_setpoint",
            value,
        ),
    ),
    NumberDescription(
        key="cooling_pump_power_setpoint",
        report_name="heat_pump",
        params=NUMBER_PERCENTAGE,
        value_fn=lambda device: device.heat_pump_config.cooling_pump_power_setpoint,
        set_value_fn=lambda device, value: device.heat_pump_config.write(
            "cooling_pump_power_setpoint",
            value,
        ),
    ),
    NumberDescription(
        key="hot_water_pump_power_setpoint",
        report_name="heat_pump",
        params=NUMBER_PERCENTAGE,
        value_fn=lambda device: device.heat_pump_config.hot_water_pump_power_setpoint,
        set_value_fn=lambda device, value: device.heat_pump_config.write(
            "hot_water_pump_power_setpoint",
            value,
        ),
    ),
    NumberDescription(
        key="defrost_pump_power_setpoint",
        report_name="heat_pump",
        params=NUMBER_PERCENTAGE,
        value_fn=lambda device: device.heat_pump_config.defrost_pump_power_setpoint,
        set_value_fn=lambda device, value: device.heat_pump_config.write(
            "defrost_pump_power_setpoint",
            value,
        ),
    ),
    NumberDescription(
        key="heating_flow_rate_setpoint",
        report_name="heat_pump",
        params=NUMBER_FLOWRATE,
        value_fn=lambda device: device.heat_pump_config.heating_flow_rate_setpoint,
        set_value_fn=lambda device, value: device.heat_pump_config.write(
            "heating_flow_rate_setpoint",
            value,
        ),
    ),
    NumberDescription(
        key="cooling_flow_rate_setpoint",
        report_name="heat_pump",
        params=NUMBER_FLOWRATE,
        value_fn=lambda device: device.heat_pump_config.cooling_flow_rate_setpoint,
        set_value_fn=lambda device, value: device.heat_pump_config.write(
            "cooling_flow_rate_setpoint",
            value,
        ),
    ),
    NumberDescription(
        key="hot_water_flow_rate_setpoint",
        report_name="heat_pump",
        params=NUMBER_FLOWRATE,
        value_fn=lambda device: device.heat_pump_config.hot_water_flow_rate_setpoint,
        set_value_fn=lambda device, value: device.heat_pump_config.write(
            "hot_water_flow_rate_setpoint",
            value,
        ),
    ),
)
