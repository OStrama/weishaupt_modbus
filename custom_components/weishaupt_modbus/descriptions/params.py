"""Parameters for descriptions."""

from dataclasses import dataclass

from homeassistant.components.number import NumberDeviceClass
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)


@dataclass(frozen=True, kw_only=True)
class SensorParams:
    """Parameters for a sensor description."""

    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = None
    native_unit_of_measurement: str | None = None
    suggested_display_precision: int | None = None
    is_enum: bool = False
    icon: str | None = None


@dataclass(frozen=True, kw_only=True)
class NumberParams:
    """Parameters for a number description."""

    device_class: NumberDeviceClass | None = None
    native_unit_of_measurement: str | None = None
    native_min_value: float = 0
    native_max_value: float = 100
    native_step: float = 1
    icon: str | None = None


@dataclass(frozen=True, kw_only=True)
class SelectParams:
    """Parameters for a select description."""

    options: tuple[str, ...]
    icon: str | None = None


type DescriptionParam = SensorParams | NumberParams | SelectParams


TEMPERATURE = SensorParams(
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    suggested_display_precision=1,
)

ROOM_TEMPERATURE = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=16,
    native_max_value=28,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)

SUMMER_WINTER_SWITCH_TEMPERATURE = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=3,
    native_max_value=30,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)

WATER_TEMPERATURE = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=5.5,
    native_max_value=60,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)

SG_READY_TEMPERATURE = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=0,
    native_max_value=30,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)

BIVALENT_TEMPERATURE = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=-20,
    native_max_value=40,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)

STANDARD_TEMPERATURE = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=-60,
    native_max_value=100,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)

NUMBER_PERCENTAGE = NumberParams(
    native_min_value=0,
    native_max_value=100,
    native_step=1,
    native_unit_of_measurement=PERCENTAGE,
)

HEATING_CURVE = NumberParams(
    native_min_value=0.05,
    native_max_value=1.5,
    native_step=0.05,
)

FLOW_RATE = NumberParams(
    native_min_value=0,
    native_max_value=5,
    native_step=0.1,
    native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
)

ENERGY = SensorParams(
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    suggested_display_precision=0,
)

ENERGY_WEBIF = SensorParams(
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    suggested_display_precision=3,
)

POWER = SensorParams(
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfPower.WATT,
    suggested_display_precision=0,
)

PRESSURE = SensorParams(
    device_class=SensorDeviceClass.PRESSURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfPressure.BAR,
    suggested_display_precision=0,
)

HOURS = SensorParams(
    device_class=SensorDeviceClass.DURATION,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTime.HOURS,
    suggested_display_precision=0,
)

RPM = SensorParams(
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
    suggested_display_precision=0,
)

KELVIN = SensorParams(
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTemperature.KELVIN,
    suggested_display_precision=0,
)

PV_POWER = SensorParams(
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfPower.WATT,
    suggested_display_precision=0,
)


EMPTY = SensorParams(
    device_class=None,
    state_class=None,
    native_unit_of_measurement=None,
    suggested_display_precision=None,
)


SENSOR_PERCENTAGE = SensorParams(
    device_class=None,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=PERCENTAGE,
    suggested_display_precision=None,
)


ENUM = SensorParams(
    device_class=None,
    state_class=None,
    native_unit_of_measurement=None,
    suggested_display_precision=None,
    is_enum=True,
)


HUMIDITY = SensorParams(
    device_class=SensorDeviceClass.HUMIDITY,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=PERCENTAGE,
    suggested_display_precision=0,
)


NUMBER_POWER = NumberParams(
    device_class=SensorDeviceClass.POWER,
    native_unit_of_measurement=UnitOfPower.WATT,
    native_min_value=0.0,
    native_max_value=10000,
    native_step=500,
)


NUMBER_EMPTY = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=-60,
    native_max_value=100,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)


NUMBER_FLOWRATE = NumberParams(
    native_min_value=0,
    native_max_value=5,
    native_step=0.1,
    native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
)


ROOM_TEMP_LOW = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=10,
    native_max_value=20,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)

ROOM_TEMP_NORMAL = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=18,
    native_max_value=25,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)

ROOM_TEMP_COMFORT = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=20,
    native_max_value=28,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)

SGR_RAISE = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=0,
    native_max_value=10,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)

WW_TEMP = NumberParams(
    device_class=NumberDeviceClass.TEMPERATURE,
    native_min_value=40,
    native_max_value=60,
    native_step=0.5,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)


TIME_HOURS = SensorParams(
    device_class=SensorDeviceClass.DURATION,
    state_class=SensorStateClass.TOTAL_INCREASING,
    native_unit_of_measurement=UnitOfTime.HOURS,
)


BIVALENCE_TEMPERATURE = NumberParams(
    native_min_value=-20,
    native_max_value=40,
    native_step=0.5,
    device_class=SensorDeviceClass.TEMPERATURE,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
)
