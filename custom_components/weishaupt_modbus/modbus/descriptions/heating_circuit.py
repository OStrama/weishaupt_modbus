"""Weishaupt heating circuit entity descriptions."""

from .description import (
    EntityDescription,
    NumberDescription,
    SelectDescription,
    SensorDescription,
)
from .myenums import (
    HeatingCircuitDemand,
    HeatingCircuitOperation,
    HeatingCircuitPartyPause,
    HeatingCircuitWaterConfiguration,
)
from .params import (
    CONST_TEMP_HEATING,
    EMPTY,
    HEATING_CURVE,
    HUMIDITY,
    ROOM_TEMP_COMFORT,
    ROOM_TEMP_LOW,
    ROOM_TEMP_NORMAL,
    ROOM_TEMPERATURE,
    SUMMER_WINTER_SWITCH_TEMPERATURE,
    TEMPERATURE,
)


def _heating_circuit_entities(
    circuit: int,
    report_name: str,
) -> tuple[EntityDescription, ...]:
    """Return entity descriptions for a heating circuit."""

    return (
        SensorDescription(
            key="room_target_temperature",
            params=TEMPERATURE,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_inputs.heating_circuits[
                    circuit
                ].room_target_temperature
            ),
        ),
        SensorDescription(
            key="room_temperature",
            params=TEMPERATURE,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_inputs.heating_circuits[circuit].room_temperature
            ),
        ),
        SensorDescription(
            key="room_humidity",
            params=HUMIDITY,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_inputs.heating_circuits[circuit].room_humidity
            ),
        ),
        SensorDescription(
            key="flow_target_temperature",
            params=TEMPERATURE,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_inputs.heating_circuits[
                    circuit
                ].flow_target_temperature
            ),
        ),
        SensorDescription(
            key="flow_temperature",
            params=TEMPERATURE,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_inputs.heating_circuits[circuit].flow_temperature
            ),
        ),
        SensorDescription(
            key="adr31106",
            params=EMPTY,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_inputs.heating_circuits[circuit].register_31106
            ),
        ),
        SelectDescription(
            key="water_configuration",
            enum=HeatingCircuitWaterConfiguration,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[circuit].configuration
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "configuration",
                    value,
                )
            ),
        ),
        SelectDescription(
            key="demand",
            enum=HeatingCircuitDemand,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[circuit].demand
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "demand",
                    value,
                )
            ),
        ),
        SelectDescription(
            key="operation_mode",
            enum=HeatingCircuitOperation,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[circuit].operation_mode
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "operation_mode",
                    value,
                )
            ),
        ),
        SelectDescription(
            key="party_pause",
            enum=HeatingCircuitPartyPause,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[circuit].party_pause
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "party_pause",
                    value,
                )
            ),
        ),
        NumberDescription(
            key="comfort_room_target_temperature",
            params=ROOM_TEMP_COMFORT,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[
                    circuit
                ].comfort_room_target_temperature
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "comfort_room_target_temperature",
                    value,
                )
            ),
        ),
        NumberDescription(
            key="normal_room_target_temperature",
            params=ROOM_TEMP_NORMAL,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[
                    circuit
                ].normal_room_target_temperature
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "normal_room_target_temperature",
                    value,
                )
            ),
        ),
        NumberDescription(
            key="lowering_room_target_temperature",
            params=ROOM_TEMP_LOW,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[
                    circuit
                ].lowering_room_target_temperature
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "lowering_room_target_temperature",
                    value,
                )
            ),
        ),
        NumberDescription(
            key="heating_curve",
            params=HEATING_CURVE,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[circuit].heating_curve
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "heating_curve",
                    value,
                )
            ),
        ),
        NumberDescription(
            key="summer_winter_switch_temperature",
            params=SUMMER_WINTER_SWITCH_TEMPERATURE,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[
                    circuit
                ].summer_winter_switch_temperature
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "summer_winter_switch_temperature",
                    value,
                )
            ),
        ),
        NumberDescription(
            key="constant_heating_temperature",
            params=CONST_TEMP_HEATING,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[
                    circuit
                ].constant_heating_temperature
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "constant_heating_temperature",
                    value,
                )
            ),
        ),
        NumberDescription(
            key="constant_heating_lowering_temperature",
            params=ROOM_TEMPERATURE,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[
                    circuit
                ].constant_heating_lowering_temperature
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "constant_heating_lowering_temperature",
                    value,
                )
            ),
        ),
        NumberDescription(
            key="constant_cooling_temperature",
            params=ROOM_TEMPERATURE,
            report_name=report_name,
            value_fn=lambda device: (
                device.heating_circuit_configs.heating_circuits[
                    circuit
                ].constant_cooling_temperature
            ),
            set_value_fn=lambda device, value: (
                device.heating_circuit_configs.heating_circuits[circuit].write(
                    "constant_cooling_temperature",
                    value,
                )
            ),
        ),
    )


HEATING_CIRCUIT_ENTITIES: tuple[EntityDescription, ...] = _heating_circuit_entities(
    0,
    "heating_circuit",
)

HEATING_CIRCUIT_ENTITIES2: tuple[EntityDescription, ...] = _heating_circuit_entities(
    1,
    "heating_circuit2",
)

HEATING_CIRCUIT_ENTITIES3: tuple[EntityDescription, ...] = _heating_circuit_entities(
    2,
    "heating_circuit3",
)

HEATING_CIRCUIT_ENTITIES4: tuple[EntityDescription, ...] = _heating_circuit_entities(
    3,
    "heating_circuit4",
)

HEATING_CIRCUIT_ENTITIES5: tuple[EntityDescription, ...] = _heating_circuit_entities(
    4,
    "heating_circuit5",
)
