"""Heat pump constants and definitions."""

from typing import Any

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

from .const import DEVICES, FORMATS, TYPES
from .items import WebItem

PARAMS_PERCENTAGE: dict[str, Any] = {
    "min": 0,
    "max": 100,
    "precision": 0,
    "unit": PERCENTAGE,
}


PARAMS_STDTEMP: dict = {
    "min": -60,
    "max": 100,
    "step": 0.5,
    "divider": 10,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "precision": 1,
    "unit": UnitOfTemperature.CELSIUS,
    "stateclass": SensorStateClass.MEASUREMENT,
}


PARAMS_FLOWRATE: dict = {
    "min": 0,
    "max": 5,
    "step": 0.1,
    "divider": 100,
    "precision": 2,
    "unit": UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_ENERGY: dict[str, Any] = {
    "min": 0,
    "max": 999999999999,
    "deviceclass": SensorDeviceClass.ENERGY,
    "precision": 0,
    "unit": UnitOfEnergy.KILO_WATT_HOUR,
    "stateclass": SensorStateClass.TOTAL_INCREASING,
}

PARAMS_ENERGY_WEBIF: dict[str, Any] = {
    "min": 0,
    "max": 999999999999,
    "deviceclass": SensorDeviceClass.ENERGY,
    "precision": 3,
    "unit": UnitOfEnergy.KILO_WATT_HOUR,
    "stateclass": SensorStateClass.TOTAL_INCREASING,
}

PARAMS_POWER: dict = {
    "min": 0,
    "max": 50000,
    "deviceclass": SensorDeviceClass.POWER,
    "precision": 0,
    "unit": UnitOfPower.WATT,
    "stateclass": SensorStateClass.MEASUREMENT,
    # The web interface reports a switched-off pump as a localized text ("Aus",
    # "Uit", "Off", ...) instead of a number. For a power reading that means 0 W,
    # so fall back to 0 (language-independent) instead of "unknown".
    "non_numeric_value": 0,
}

PARAMS_PRESSURE: dict = {
    "min": 0,
    "max": 100,
    "deviceclass": SensorDeviceClass.PRESSURE,
    "precision": 0,
    "unit": UnitOfPressure.BAR,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_HOUR: dict = {
    "min": 0,
    "max": 100,
    "deviceclass": SensorDeviceClass.DURATION,
    "precision": 0,
    "unit": UnitOfTime.HOURS,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_RPM: dict = {
    "min": 0,
    "max": 100,
    # "deviceclass": SensorDeviceClass.SPEED,
    "precision": 0,
    "unit": REVOLUTIONS_PER_MINUTE,
    "stateclass": SensorStateClass.MEASUREMENT,
}

PARAMS_K: dict = {
    "min": 0,
    "max": 100,
    "deviceclass": SensorDeviceClass.TEMPERATURE,
    "precision": 0,
    "unit": UnitOfTemperature.KELVIN,
    "stateclass": SensorStateClass.MEASUREMENT,
}


# fmt: off
# The template containing only the variable parts
_HEIZKREIS_TEMPLATE = [
    ("Außentemperatur", "aussentemperatur"),
    ("AT Mittelwert", "at_mittelwert"),
    ("AT Langzeitwert", "at_langzeitwert"),
    ("Raumsolltemperatur", "raumsolltemperatur"),
    ("Vorlaufsolltemperatur", "vorlaufsolltemperatur"),
    ("Vorlauftemperatur", "vorlauftemperatur"),
]


def _generate_hk_items(hk_num: int) -> list[WebItem]:
    """Helper to generate standard WebItems for a specific heating circuit."""
    return [
        WebItem(
            name=f"{name}",
            mformat=FORMATS.TEMPERATURE,
            mtype=TYPES.SENSOR,
            device=DEVICES.WIH,
            params=PARAMS_STDTEMP,
            webif_group="WIH",
            translation_key=f"webif_info_heizkreis{hk_num}_{suffix}"
        )
        for name, suffix in _HEIZKREIS_TEMPLATE
    ]


# Dynamically generate lists for HK1 to HK5
WEBIF_INFO_HEIZKREIS1 = _generate_hk_items(1)
WEBIF_INFO_HEIZKREIS2 = _generate_hk_items(2)
WEBIF_INFO_HEIZKREIS3 = _generate_hk_items(3)
WEBIF_INFO_HEIZKREIS4 = _generate_hk_items(4)
WEBIF_INFO_HEIZKREIS5 = _generate_hk_items(5)

WEBIF_INFO_WAERMEPUMPE: list[WebItem] = [
    WebItem(name="Betrieb", mformat=FORMATS.TEXT, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_betrieb"),
    WebItem(name="Störmeldung", mformat=FORMATS.TEXT, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_stoermeldung"),
    WebItem(name="Warmwassertemperatur", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_warmwassertemperatur"),
    WebItem(name="Leistungsanforderung", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PERCENTAGE, webif_group="WIW", translation_key="webif_info_waermepumpe_leistungsanforderung"),
    WebItem(name="Solltemperatur", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_solltemperatur"),
    WebItem(name="Anforderung", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_ENERGY, webif_group="WIW", translation_key="webif_info_waermepumpe_anforderung"),
    WebItem(name="Schaltdifferenz dynamisch", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_K, webif_group="WIW", translation_key="webif_info_waermepumpe_schaltdifferenz_dynamisch"),
    WebItem(name="Vorlauftemperatur", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_vorlauftemperatur"),
    WebItem(name="Rücklauftemperatur", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_ruecklauftemperatur"),
    WebItem(name="Drehzahl Pumpe M1", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PERCENTAGE, webif_group="WIW", translation_key="webif_info_waermepumpe_drehzahl_pumpe_m1"),
    WebItem(name="Volumenstrom", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW,params=PARAMS_FLOWRATE, webif_group="WIW", translation_key="webif_info_waermepumpe_volumenstrom"),
    WebItem(name="Stellung Umschaltventil", mformat=FORMATS.TEXT, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_stellung_umschaltventil"),
    WebItem(name="Version WWP-SG", mformat=FORMATS.TEXT, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_version_wwp_sg"),
    WebItem(name="Version WWP-EC WBB", mformat=FORMATS.TEXT, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_version_wwp_ec_wbb"),
    WebItem(name="Soll Leistung", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_POWER, webif_group="WIW", translation_key="webif_info_waermepumpe_soll_leistung"),
    WebItem(name="Ist Leistung", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_POWER, webif_group="WIW", translation_key="webif_info_waermepumpe_ist_leistung"),
    WebItem(name="Expansionsventil AG Eintr", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_expansionsventil_ag_eintr"),
    WebItem(name="Luftansaugtemperatur", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_luftansaugtemperatur"),
    WebItem(name="Wärmetauscher AG Austrit", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_waermetauscher_ag_austrit"),
    WebItem(name="Verdichtersauggastemp.", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_verdichtersauggastemp"),
    WebItem(name="EVI Sauggastemperatur", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_evi_sauggastemperatur"),
    WebItem(name="Kältemittel IG Austritt", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_kaeltemittel_ig_austritt"),
    WebItem(name="Ölsumpftemperatur", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_oelsumpftemperatur"),
    WebItem(name="Druckgastemperatur", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_druckgastemperatur"),
    WebItem(name="Niederdruck", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PRESSURE, webif_group="WIW", translation_key="webif_info_waermepumpe_niederdruck"),
    WebItem(name="Verdampfungstemperatur", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_verdampfungstemperatur"),
    WebItem(name="Hochdruck", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PRESSURE, webif_group="WIW", translation_key="webif_info_waermepumpe_hochdruck"),
    WebItem(name="Kondensationstemperatur", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_kondensationstemperatur"),
    WebItem(name="Mitteldruck", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PRESSURE, webif_group="WIW", translation_key="webif_info_waermepumpe_mitteldruck"),
    WebItem(name="Sättigungstemperatur EVI", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_STDTEMP, webif_group="WIW", translation_key="webif_info_waermepumpe_saettigungstemperatur_evi"),
    WebItem(name="Überhitzung Heizen", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_K, webif_group="WIW", translation_key="webif_info_waermepumpe_ueberhitzung_heizen"),
    WebItem(name="Öffnungsgrad EXV Heizen", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PERCENTAGE, webif_group="WIW", translation_key="webif_info_waermepumpe_oeffnungsgrad_exv_heizen"),
    WebItem(name="Überhitzung Verdichter", mformat=FORMATS.TEMPERATURE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_K, webif_group="WIW", translation_key="webif_info_waermepumpe_ueberhitzung_verdichter"),
    WebItem(name="Öffnungsgrad EXV Kühlen", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PERCENTAGE, webif_group="WIW", translation_key="webif_info_waermepumpe_oeffnungsgrad_exv_kuehlen"),
    WebItem(name="Überhitzung EVI", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_K, webif_group="WIW", translation_key="webif_info_waermepumpe_ueberhitzung_evi"),
    WebItem(name="Öffnungsgrad EVI", mformat=FORMATS.PERCENTAGE, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_PERCENTAGE, webif_group="WIW", translation_key="webif_info_waermepumpe_oeffnungsgrad_evi"),
    WebItem(name="Betriebsstd. Verdichter", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_HOUR, webif_group="WIW", translation_key="webif_info_waermepumpe_betriebsstd_verdichter"),
    WebItem(name="Schaltspiele Verdichter", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_schaltspiele_verdichter"),
    WebItem(name="Schaltspiele Abtauen", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_schaltspiele_abtauen"),
    WebItem(name="Verdichter", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIW, params=PARAMS_RPM, webif_group="WIW", translation_key="webif_info_waermepumpe_verdichter"),
    WebItem(name="Außengerät Variante", mformat=FORMATS.TEXT, mtype=TYPES.SENSOR, device=DEVICES.WIW, webif_group="WIW", translation_key="webif_info_waermepumpe_aussengeraet_variante"),
]

WEBIF_INFO_2WEZ: list[WebItem] = [
    WebItem(name="Status", mformat=FORMATS.TEXT, mtype=TYPES.SENSOR, device=DEVICES.WI2W, webif_group="WI2W", translation_key="webif_info_2wez_status"),
    WebItem(name="Status E-Heizung 1", mformat=FORMATS.TEXT, mtype=TYPES.SENSOR, device=DEVICES.WI2W, webif_group="WI2W", translation_key="webif_info_2wez_status_e_heizung_1"),
    WebItem(name="Status E-Heizung 2", mformat=FORMATS.TEXT, mtype=TYPES.SENSOR, device=DEVICES.WI2W, webif_group="WI2W", translation_key="webif_info_2wez_status_e_heizung_2"),
    WebItem(name="Betriebsstunden E1", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WI2W, params=PARAMS_HOUR, webif_group="WIH", translation_key="webif_info_2wez_betriebsstunden_e1"),
    WebItem(name="Betriebsstunden E2", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WI2W, params=PARAMS_HOUR, webif_group="WIH", translation_key="webif_info_2wez_betriebsstunden_e2"),
    WebItem(name="Schaltspiele E1", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WI2W, webif_group="WIH", translation_key="webif_info_2wez_schaltspiele_e1"),
    WebItem(name="Schaltspiele E2", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WI2W, webif_group="WI2W", translation_key="webif_info_2wez_schaltspiele_e2"),
]

WEBIF_INFO_STATISTIK: list[WebItem] = [
    WebItem(name="th. Energie Heizen Tag", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_heizen_tag"),
    WebItem(name="th. Energie WW Tag", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_ww_tag"),
    WebItem(name="th. Energie gesamt Tag", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_gesamt_tag"),
    WebItem(name="elektrische Energie Tag", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_elektrische_energie_tag"),
    WebItem(name="th. Energie Heizen Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_heizen_monat"),
    WebItem(name="th. Energie WW Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_ww_monat"),
    WebItem(name="th. Energie gesamt Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_gesamt_monat"),
    WebItem(name="elektrische Energie Monat", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_elektrische_energie_monat"),
    WebItem(name="th. Energie Heizen Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_heizen_jahr"),
    WebItem(name="th. Energie WW Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_ww_jahr"),
    WebItem(name="th. Energie gesamt Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_th_energie_gesamt_jahr"),
    WebItem(name="elektrische Energie Jahr", mformat=FORMATS.NUMBER, mtype=TYPES.SENSOR, device=DEVICES.WIS, params=PARAMS_ENERGY_WEBIF, webif_group="WIS", translation_key="webif_info_statistik_elektrische_energie_jahr"),
]


DEVICELISTS_WEBIF: list = [WEBIF_INFO_HEIZKREIS1, WEBIF_INFO_WAERMEPUMPE, WEBIF_INFO_2WEZ, WEBIF_INFO_STATISTIK]
# fmt: on
