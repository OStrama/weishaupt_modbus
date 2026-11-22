"""Additional WSB reports read by the optional WEM Lokal profile."""

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfFrequency

from .description import WebifSensorDescription
from .params import PARAMS_TEMPERATURE, PARAMS_TEXT, SensorParams

PARAMS_FREQUENCY = SensorParams(
    device_class=SensorDeviceClass.FREQUENCY,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfFrequency.HERTZ,
)

_WSB_HEAT_PUMP_FIELDS = (
    ("pump_regulation_heating", PARAMS_TEXT),
    ("pump_regulation_hot_water", PARAMS_TEXT),
    ("pump_regulation_cooling", PARAMS_TEXT),
    ("pump_function", PARAMS_TEXT),
    ("pump_utility_lock_release", PARAMS_TEXT),
    ("compressor_frequency_target", PARAMS_FREQUENCY),
    ("compressor_frequency_actual", PARAMS_FREQUENCY),
    ("outdoor_heat_exchanger_inlet_temperature", PARAMS_TEMPERATURE),
    ("outdoor_heat_exchanger_middle_temperature", PARAMS_TEMPERATURE),
    ("indoor_heat_exchanger_temperature", PARAMS_TEMPERATURE),
    ("indoor_refrigerant_temperature", PARAMS_TEMPERATURE),
    ("control_board_version", PARAMS_TEXT),
)

WSB_HEAT_PUMP_DESCRIPTIONS = [
    WebifSensorDescription(key=key, report_name="heat_pump", params=params)
    for key, params in _WSB_HEAT_PUMP_FIELDS
]
