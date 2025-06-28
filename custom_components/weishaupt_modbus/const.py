"""Constants."""

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
from typing import Final

from homeassistant.const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_PREFIX,
    CONF_USERNAME,
)


@dataclass(frozen=True)
class ConfConstants:
    """Constants used for configuration."""

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
    WEBIF_TOKEN = "Web-IF-Token"


CONF = ConfConstants()


@dataclass(frozen=True)
class MainConstants:
    """Main constants."""

    DOMAIN: Final = "weishaupt_modbus"
    SCAN_INTERVAL = timedelta(seconds=30)
    UNIQUE_ID = "unique_id"
    APPID = 100
    DEF_KENNFELDFILE = "weishaupt_wbb_kennfeld.json"
    DEF_PREFIX = "weishaupt_wbb"


CONST = MainConstants()


class FormatConstants(Enum):
    """Format constants."""

    TEMPERATUR = "temperature"
    PERCENTAGE = "percentage"
    NUMBER = "number"
    STATUS = "status"
    UNKNOWN = "unknown"


class TypeConstants(Enum):
    """Type constants."""

    SENSOR = "Sensor"
    SENSOR_CALC = "Sensor_Calc"
    SELECT = "Select"
    NUMBER = "Number"
    NUMBER_RO = "Number_RO"


class DeviceConstants(Enum):
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


@dataclass(frozen=True)
class DeviceNameConstants:
    """Device constants."""

    SYS: Final = "WH System"
    WP: Final = "WH Wärmepumpe"
    WW: Final = "WH Warmwasser"
    HZ: Final = "WH Heizkreis"
    HZ2: Final = "WH Heizkreis2"
    HZ3: Final = "WH Heizkreis3"
    HZ4: Final = "WH Heizkreis4"
    HZ5: Final = "WH Heizkreis5"
    W2: Final = "WH 2. Wärmeerzeuger"
    ST: Final = "WH Statistik"
    UK: Final = "WH Unknown"
    IO: Final = "WH Eingänge/Ausgänge"


DEVICENAMES = DeviceNameConstants()
