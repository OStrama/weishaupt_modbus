"""Constants for Weishaupt modbus integration."""

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

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

    HOST: str = CONF_HOST
    PORT: str = CONF_PORT
    PREFIX: str = CONF_PREFIX
    DEVICE_POSTFIX: str = "Device-Postfix"
    KENNFELD_FILE: str = "Kennfeld-File"
    HK2: str = "Heizkreis 2"
    HK3: str = "Heizkreis 3"
    HK4: str = "Heizkreis 4"
    HK5: str = "Heizkreis 5"
    NAME_DEVICE_PREFIX: str = "Name-Device-Prefix"
    NAME_TOPIC_PREFIX: str = "Name-Topic-Prefix"
    CB_WEBIF: str = "enable-webif"
    PASSWORD: str = CONF_PASSWORD
    USERNAME: str = CONF_USERNAME
    WEBIF_TOKEN: str = "Web-IF-Token"


CONF = ConfConstants()


@dataclass(frozen=True)
class MainConstants:
    """Main constants."""

    DOMAIN: str = "weishaupt_modbus"
    SCAN_INTERVAL: timedelta = timedelta(seconds=30)
    UNIQUE_ID: str = "unique_id"
    APPID: int = 100
    DEF_KENNFELDFILE: str = "weishaupt_wbb_kennfeld.json"
    DEF_PREFIX: str = "weishaupt_wbb"


CONST = MainConstants()


@dataclass(frozen=True)
class FormatConstants(Enum):
    """Format constants."""

    TEMPERATURE = "temperature"
    PERCENTAGE = "percentage"
    NUMBER = "number"
    STATUS = "status"
    UNKNOWN = "unknown"

FORMATS = FormatConstants()


@dataclass(frozen=True)
class TypeConstants(Enum):
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

    SYS: str = "dev_system"
    WP: str = "dev_waermepumpe"
    WW: str = "dev_warmwasser"
    HZ: str = "dev_heizkreis"
    HZ2: str = "dev_heizkreis2"
    HZ3: str = "dev_heizkreis3"
    HZ4: str = "dev_heizkreis4"
    HZ5: str = "dev_heizkreis5"
    W2: str = "dev_waermeerzeuger2"
    ST: str = "dev_statistik"
    UK: str = "dev_unknown"
    IO: str = "dev_ein_aus"
    WIH: str = "Webif Info Heizkreis"


DEVICES = DeviceConstants()


@dataclass(frozen=True)
class DeviceNameConstants:
    """Device name constants."""

    SYS: str = "WH System"
    WP: str = "WH Wärmepumpe"
    WW: str = "WH Warmwasser"
    HZ: str = "WH Heizkreis"
    HZ2: str = "WH Heizkreis2"
    HZ3: str = "WH Heizkreis3"
    HZ4: str = "WH Heizkreis4"
    HZ5: str = "WH Heizkreis5"
    W2: str = "WH 2. Wärmeerzeuger"
    ST: str = "WH Statistik"
    UK: str = "WH Unknown"
    IO: str = "WH Eingänge/Ausgänge"


DEVICENAMES = DeviceNameConstants()
