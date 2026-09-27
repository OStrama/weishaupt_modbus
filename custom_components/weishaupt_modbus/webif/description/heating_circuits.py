from config.custom_components.weishaupt_modbus.webif.description.description import (
    WebifSensorDescription,
)
from config.custom_components.weishaupt_modbus.webif.description.params import (
    PARAMS_TEMPERATURE,
)


_HEATING_CIRCUIT_TEMPLATE = [
    ("outside_temperature", PARAMS_TEMPERATURE),
    ("outside_temperature_average", PARAMS_TEMPERATURE),
    ("outside_temperature_long_term", PARAMS_TEMPERATURE),
    ("room_target_temperature", PARAMS_TEMPERATURE),
    ("flow_target_temperature", PARAMS_TEMPERATURE),
    ("flow_temperature", PARAMS_TEMPERATURE),
]


def _generate_heating_circuit_descriptions(
    circuit_num: int,
) -> list[WebifSensorDescription]:
    """Generate WebIF sensor descriptions for a heating circuit."""
    report_name = (
        "heating_circuit" if circuit_num == 1 else f"heating_circuit{circuit_num}"
    )

    return [
        WebifSensorDescription(
            key=key,
            report_name=report_name,
            params=params,
        )
        for key, params in _HEATING_CIRCUIT_TEMPLATE
    ]


WEBIF_HEATING_CIRCUIT = _generate_heating_circuit_descriptions(1)
WEBIF_HEATING_CIRCUIT2 = _generate_heating_circuit_descriptions(2)
WEBIF_HEATING_CIRCUIT3 = _generate_heating_circuit_descriptions(3)
WEBIF_HEATING_CIRCUIT4 = _generate_heating_circuit_descriptions(4)
WEBIF_HEATING_CIRCUIT5 = _generate_heating_circuit_descriptions(5)
