from dataclasses import dataclass

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor.const import SensorStateClass
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


PARAMS_TEXT = SensorParams()

PARAMS_TEMPERATURE = SensorParams(
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    suggested_display_precision=1,
)

PARAMS_PERCENTAGE = SensorParams(
    native_unit_of_measurement=PERCENTAGE,
    suggested_display_precision=0,
)

PARAMS_ENERGY = SensorParams(
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    suggested_display_precision=0,
)

PARAMS_KELVIN = SensorParams(
    device_class=SensorDeviceClass.TEMPERATURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTemperature.KELVIN,
    suggested_display_precision=0,
)

PARAMS_POWER = SensorParams(
    device_class=SensorDeviceClass.POWER,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfPower.WATT,
    suggested_display_precision=0,
)

PARAMS_PRESSURE = SensorParams(
    device_class=SensorDeviceClass.PRESSURE,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfPressure.BAR,
    suggested_display_precision=0,
)

PARAMS_FLOW_RATE = SensorParams(
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
    suggested_display_precision=2,
)

PARAMS_HOURS = SensorParams(
    device_class=SensorDeviceClass.DURATION,
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=UnitOfTime.HOURS,
    suggested_display_precision=0,
)

PARAMS_RPM = SensorParams(
    state_class=SensorStateClass.MEASUREMENT,
    native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
    suggested_display_precision=0,
)

PARAMS_INTEGER = SensorParams(
    state_class=SensorStateClass.MEASUREMENT,
    suggested_display_precision=0,
)

PARAMS_ENERGY_WEBIF = SensorParams(
    device_class=SensorDeviceClass.ENERGY,
    state_class=SensorStateClass.TOTAL_INCREASING,
    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
    suggested_display_precision=3,
)
