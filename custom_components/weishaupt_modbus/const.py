"""Constants."""

from dataclasses import dataclass
from datetime import timedelta

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_PREFIX,
    CONF_USERNAME,
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)


@dataclass(frozen=True)
class ConfConstants:
    """Constants used for configurastion"""

    HOST = CONF_HOST
    PORT = CONF_PORT
    PREFIX = CONF_PREFIX
    DEVICE_POSTFIX = "Device-Postfix"
    KENNFELD_FILE = "Kennfeld-File"
    HK2 = "Heizkreis 2"
    HK3 = "Heizkreis 3"
    HK4 = "Heizkreis 4"
    HK5 = "Heizkreis 5"
    NAME_DEVICE_PREFIX = "Name-Device-Prefix"
    NAME_TOPIC_PREFIX = "Name-Topic-Prefix"
    CB_WEBIF = "enable-webif"
    PASSWORD = CONF_PASSWORD
    USERNAME = CONF_USERNAME


CONF = ConfConstants()


@dataclass(frozen=True)
class MainConstants:
    """Main constants."""

    DOMAIN = "weishaupt_modbus"
    SCAN_INTERVAL = timedelta(seconds=30)
    UNIQUE_ID = "unique_id"
    APPID = 100
    DEF_KENNFELDFILE = "weishaupt_wbb_kennfeld.json"
    DEF_PREFIX = "weishaupt_wbb"


CONST = MainConstants()


@dataclass(frozen=True)
class FormatConstants:
    """Format constants."""

    TEMPERATUR = UnitOfTemperature.CELSIUS
    TEMPERATUR_DELTA = UnitOfTemperature.KELVIN
    ENERGY = UnitOfEnergy.KILO_WATT_HOUR
    POWER = UnitOfPower.WATT
    POWER_KW = UnitOfPower.KILO_WATT
    PERCENTAGE = PERCENTAGE
    NUMBER = ""
    STATUS = "Status"
    VOLUMENSTROM = UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR
    KENNLINIE = " "  # has to be different from NUMBER we'd have to separate unit strings and format...
    TIME_MIN = UnitOfTime.MINUTES
    TIME_H = UnitOfTime.HOURS
    RPM = REVOLUTIONS_PER_MINUTE
    PRESSURE = UnitOfPressure.BAR
    UNKNOWN = "?"
    ANZAHL = None


FORMATS = FormatConstants()


@dataclass(frozen=True)
class TypeConstants:
    """Type constants."""

    SENSOR = "Sensor"
    SENSOR_CALC = "Sensor_Calc"
    SELECT = "Select"
    NUMBER = "Number"
    NUMBER_RO = "Number_RO"


TYPES = TypeConstants()


@dataclass(frozen=True)
class DeviceConstants:
    """Device constants."""

    SYS = "dev_system"
    WP = "dev_waermepumpe"
    WW = "dev_warmwasser"
    HZ = "dev_heizkreis"
    HZ2 = "dev_heizkreis2"
    HZ3 = "dev_heizkreis3"
    HZ4 = "dev_heizkreis4"
    HZ5 = "dev_heizkreis5"
    W2 = "dev_waermeerzeuger2"
    ST = "dev_statistik"
    UK = "dev_unknown"
    IO = "dev_ein_aus"

    WIH = "Webif Info Heizkreis"
    WIW = "Webif Info Wärmepumpe"
    WI2 = "Webif Info 2. Wärmeerzeuger"
    WIS = "Webif Info Statistik"


DEVICES = DeviceConstants()


@dataclass(frozen=True)
class DeviceNameConstants:
    """Device constants."""

    SYS = "WH System"
    WP = "WH Wärmepumpe"
    WW = "WH Warmwasser"
    HZ = "WH Heizkreis"
    HZ2 = "WH Heizkreis2"
    HZ3 = "WH Heizkreis3"
    HZ4 = "WH Heizkreis4"
    HZ5 = "WH Heizkreis5"
    W2 = "WH 2. Wärmeerzeuger"
    ST = "WH Statistik"
    UK = "WH Unknown"
    IO = "WH Eingänge/Ausgänge"


DEVICENAMES = DeviceNameConstants()


@dataclass(frozen=True)
class CalcConstants:
    """Main constants."""

    POWER = "power"
    QUOTIENT = "quotient"
    DIFFERENCE = "difference"


CALCTYPES = CalcConstants()
