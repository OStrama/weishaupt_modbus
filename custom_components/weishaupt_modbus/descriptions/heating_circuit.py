"""Weishaupt heating circuit entity descriptions."""

from .description import (
    EntityDescription,
    NumberDescription,
    SelectDescription,
    SensorDescription,
)
from .params import EMPTY, SENSOR_PERCENTAGE, TEMPERATURE, ENUM, HUMIDITY


HEATING_CIRCUIT_ENTITIES: tuple[SensorDescription, ...] = (
    SensorDescription(
        key="room_target_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.room_target_temperature,
    ),
    SensorDescription(
        key="room_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.room_temperature,
    ),
    SensorDescription(
        key="room_humidity",
        params=HUMIDITY,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.room_humidity,
    ),
    SensorDescription(
        key="flow_target_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.flow_target_temperature,
    ),
    SensorDescription(
        key="flow_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.flow_temperature,
    ),
    SensorDescription(
        key="configuration",
        params=EMPTY,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.configuration,
    ),
    SensorDescription(
        key="demand",
        params=EMPTY,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.demand,
    ),
    SensorDescription(
        key="operation_mode",
        params=EMPTY,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.operation_mode,
    ),
    SensorDescription(
        key="party_pause",
        params=EMPTY,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.party_pause,
    ),
    SensorDescription(
        key="comfort_room_target_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.comfort_room_target_temperature,
    ),
    SensorDescription(
        key="normal_room_target_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.normal_room_target_temperature,
    ),
    SensorDescription(
        key="lowering_room_target_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.lowering_room_target_temperature,
    ),
    SensorDescription(
        key="heating_curve",
        params=EMPTY,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.heating_curve,
    ),
    SensorDescription(
        key="summer_winter_switch_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.summer_winter_switch_temperature,
    ),
    SensorDescription(
        key="constant_heating_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.constant_heating_temperature,
    ),
    SensorDescription(
        key="constant_heating_lowering_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: (
            device.heating_circuit.constant_heating_lowering_temperature
        ),
    ),
    SensorDescription(
        key="constant_cooling_temperature",
        params=TEMPERATURE,
        report_name="heating_circuit",
        value_fn=lambda device: device.heating_circuit.constant_cooling_temperature,
    ),
)
