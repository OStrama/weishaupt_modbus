"""Weishaupt heating circuit entity descriptions."""

from .description import (
    EntityDescription,
    NumberDescription,
    SelectDescription,
    SensorDescription,
)
from .params import (
    ENUM,
    HUMIDITY,
    ROOM_TEMP_COMFORT,
    ROOM_TEMP_LOW,
    ROOM_TEMP_NORMAL,
    TEMPERATURE,
)


HEATING_CIRCUIT_ENTITIES: tuple[EntityDescription, ...] = (
    SensorDescription(
        key="room_target_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit_input.room_target_temperature,
    ),
    SensorDescription(
        key="room_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit_input.room_temperature,
    ),
    SensorDescription(
        key="room_humidity",
        params=HUMIDITY,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit_input.room_humidity,
    ),
    SensorDescription(
        key="flow_target_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit_input.flow_target_temperature,
    ),
    SensorDescription(
        key="flow_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit_input.flow_temperature,
    ),
    SelectDescription(
        key="configuration",
        enum=None,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit_config.configuration,
        set_value_fn=lambda device, value: device.heating_circuit_config.write(
            "configuration",
            value,
        ),
    ),
    SelectDescription(
        key="demand",
        enum=None,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit_config.demand,
        set_value_fn=lambda device, value: device.heating_circuit_config.write(
            "demand",
            value,
        ),
    ),
    SelectDescription(
        key="operation_mode",
        enum=None,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit_config.operation_mode,
        set_value_fn=lambda device, value: device.heating_circuit_config.write(
            "operation_mode",
            value,
        ),
    ),
    SelectDescription(
        key="party_pause",
        enum=None,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit_config.party_pause,
        set_value_fn=lambda device, value: device.heating_circuit_config.write(
            "party_pause",
            value,
        ),
    ),
    NumberDescription(
        key="comfort_room_target_temperature",
        params=ROOM_TEMP_COMFORT,
        report_name="heating_circuit",
        value_fn=lambda device: (
            device.heating_circuit_config.comfort_room_target_temperature
        ),
        set_value_fn=lambda device, value: device.heating_circuit_config.write(
            "comfort_room_target_temperature",
            value,
        ),
    ),
    NumberDescription(
        key="normal_room_target_temperature",
        params=ROOM_TEMP_NORMAL,
        report_name="heating_circuit",
        value_fn=lambda device: (
            device.heating_circuit_config.normal_room_target_temperature
        ),
        set_value_fn=lambda device, value: device.heating_circuit_config.write(
            "normal_room_target_temperature",
            value,
        ),
    ),
    NumberDescription(
        key="lowering_room_target_temperature",
        params=ROOM_TEMP_LOW,
        report_name="heating_circuit",
        value_fn=lambda device: (
            device.heating_circuit_config.lowering_room_target_temperature
        ),
        set_value_fn=lambda device, value: device.heating_circuit_config.write(
            "lowering_room_target_temperature",
            value,
        ),
    ),
)
