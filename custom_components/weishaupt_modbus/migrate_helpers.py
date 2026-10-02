"""Helpers for entity migration."""

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import CONF

if TYPE_CHECKING:
    from .configentry import MyConfigEntry


_LOGGER = logging.getLogger(__name__)


def old_unique_id(postfix: str, prefix: str, old_name: str) -> str:
    """Create an UID according to old style."""

    if postfix is None:
        postfix = ""
    else:
        postfix = f"_{postfix}"

    if prefix is None:
        prefix = ""
    else:
        prefix = f"{prefix}"

    return f"{prefix}{old_name}{postfix}"


def new_unique_id(base_id: str, mac: str) -> str:
    """Create an UID according to new style."""
    return f"{mac}_{base_id}"


def migrate_entities(config_entry: MyConfigEntry, hass: HomeAssistant) -> None:
    """Migrate entities from old unique_id to new unique_id."""

    _LOGGER.warning("Starting entity migration!")

    postfix = config_entry.data.get(CONF.DEVICE_POSTFIX)
    prefix = config_entry.data.get(CONF.PREFIX)

    mac = config_entry.data.get(CONF.MAC)
    if mac == "CHANGEME":
        return

    entity_registry = er.async_get(hass)
    unique_id_migrations: dict[str, str] = {}
    for item in MIGRATION:
        old_uid = old_unique_id(postfix, prefix, item.name)
        new_uid = new_unique_id(item.new_key, mac)
        unique_id_migrations[old_uid] = new_uid
    _LOGGER.warning("Migration map: %s", unique_id_migrations)

    entities = entity_registry.entities.get_entries_for_config_entry_id(
        config_entry.entry_id
    )
    _LOGGER.warning(
        "Entity migration: config_entry_id=%s, entity_count=%d",
        config_entry.entry_id,
        len(entities),
    )

    for entity in entities:
        new_uid = unique_id_migrations.get(entity.unique_id)
        old_uid = entity.unique_id
        _LOGGER.warning("Old id: %s; new id: %s", old_uid, new_uid)
        if new_uid is None:
            continue

        entity_registry.async_update_entity(
            entity.entity_id,
            new_unique_id=new_uid,
        )

        _LOGGER.warning(
            "Changed old UID: %s to new UID: %s",
            old_uid,
            new_uid,
        )


@dataclass(frozen=True)
class OldModbusItem:
    """Legacy Modbus item for entity migration."""

    name: str
    new_key: str


OLD_MODBUS_SYS_ITEMS: tuple[OldModbusItem, ...] = (
    OldModbusItem(
        name="Aussentemperatur",
        new_key="system_outside_temperature",
    ),
    OldModbusItem(
        name="Luftansaugtemperatur",
        new_key="system_intake_temperature",
    ),
    OldModbusItem(
        name="Fehler",
        new_key="system_error",
    ),
    OldModbusItem(
        name="Warnung",
        new_key="system_warning",
    ),
    OldModbusItem(
        name="Fehlerfrei",
        new_key="system_error_free",
    ),
    OldModbusItem(
        name="Betriebsanzeige",
        new_key="system_operating_display",
    ),
    OldModbusItem(
        name="Systembetriebsart",
        new_key="system_operating_mode",
    ),
    OldModbusItem(
        name="SollwertPV",
        new_key="system_pv_setpoint",
    ),
)


HEAT_PUMP_UID_MIGRATIONS: tuple[OldModbusItem, ...] = (
    OldModbusItem(
        name="Betrieb",
        new_key="heat_pump_operation",
    ),
    OldModbusItem(
        name="Störmeldung",
        new_key="heat_pump_fault",
    ),
    OldModbusItem(
        name="Leistungsanforderung",
        new_key="heat_pump_power_request",
    ),
    OldModbusItem(
        name="Vorlauftemperatur",
        new_key="heat_pump_flow_temperature",
    ),
    OldModbusItem(
        name="Rücklauftemperatur",
        new_key="heat_pump_return_temperature",
    ),
    OldModbusItem(
        name="Verdampfungstemperatur",
        new_key="heat_pump_evaporation_temperature",
    ),
    OldModbusItem(
        name="Verdichtersauggastemp",
        new_key="heat_pump_compressor_suction_temperature",
    ),
    OldModbusItem(
        name="Weichentemperatur",
        new_key="heat_pump_diverter_temperature",
    ),
    OldModbusItem(
        name="Anforderung(Vorlauf regenerativ)",
        new_key="heat_pump_regenerative_flow_temperature",
    ),
    OldModbusItem(
        name="Puffertemperatur?",
        new_key="heat_pump_buffer_temperature",
    ),
    OldModbusItem(
        name="Vorlauftemperatur präzise(Summenvorlauf(B7))",
        new_key="heat_pump_precise_flow_temperature",
    ),
    OldModbusItem(
        name="Konfiguration",
        new_key="heat_pump_configuration",
    ),
    OldModbusItem(
        name="Ruhemodus",
        new_key="heat_pump_rest_mode",
    ),
    OldModbusItem(
        name="Pumpe Einschaltart",
        new_key="heat_pump_pump_start_type",
    ),
    OldModbusItem(
        name="Sollwert Pumpe Leistung Heizen",
        new_key="heat_pump_heating_pump_power_setpoint",
    ),
    OldModbusItem(
        name="Sollwert Pumpe Leistung Kühlen",
        new_key="heat_pump_cooling_pump_power_setpoint",
    ),
    OldModbusItem(
        name="Sollwert Pumpe Leistung Warmwasser",
        new_key="heat_pump_hot_water_pump_power_setpoint",
    ),
    OldModbusItem(
        name="Sollwert Pumpe Leistung Abtaubetrieb",
        new_key="heat_pump_defrost_pump_power_setpoint",
    ),
    OldModbusItem(
        name="Sollwert Volumenstrom Heizen",
        new_key="heat_pump_heating_flow_rate_setpoint",
    ),
    OldModbusItem(
        name="Sollwert Volumenstrom Kühlen",
        new_key="heat_pump_cooling_flow_rate_setpoint",
    ),
    OldModbusItem(
        name="Sollwert Volumenstrom Warmwasser",
        new_key="heat_pump_hot_water_flow_rate_setpoint",
    ),
)

HZ_UID_MAPPINGS: tuple[tuple[str, str], ...] = (
    ("Raumsolltemperatur", "room_target_temperature"),
    ("Raumtemperatur", "room_temperature"),
    ("Raumfeuchte", "room_humidity"),
    ("Vorlaufsolltemperatur", "flow_target_temperature"),
    ("HZ_Vorlauftemperatur", "flow_temperature"),
    ("Adr. 31106", "adr31106"),
    ("HZ_Konfiguration", "water_configuration"),
    ("Anforderung Typ", "demand"),
    ("Betriebsart", "operation_mode"),
    ("Pause / Party", "party_pause"),
    ("Raumsolltemperatur Komfort", "comfort_room_target_temperature"),
    ("Raumsolltemperatur Normal", "normal_room_target_temperature"),
    ("Raumsolltemperatur Absenk", "lowering_room_target_temperature"),
    ("Heizkennlinie", "heating_curve"),
    ("Sommer Winter Umschaltung", "summer_winter_switch_temperature"),
    ("Heizen Konstanttemperatur", "constant_heating_temperature"),
    ("Heizen Konstanttemp Absenk", "constant_heating_lowering_temperature"),
    ("Kühlen Konstanttemperatur", "constant_cooling_temperature"),
)

HEATING_CIRCUIT_UID_MIGRATIONS: tuple[OldModbusItem, ...] = tuple(
    OldModbusItem(
        name=f"{old_name}",
        new_key=f"{report_name}_{new_key}",
    )
    for circuit, (report_name, suffix) in enumerate(
        (
            ("heating_circuit", ""),
            ("heating_circuit2", "2"),
            ("heating_circuit3", "3"),
            ("heating_circuit4", "4"),
            ("heating_circuit5", "5"),
        )
    )
    for old_name, new_key in HZ_UID_MAPPINGS
)

DOMESTIC_HOT_WATER_UID_MIGRATIONS: tuple[OldModbusItem, ...] = (
    OldModbusItem(
        name="Warmwassersolltemperatur",
        new_key="domestic_hot_water_target_temperature",
    ),
    OldModbusItem(
        name="Warmwassertemperatur",
        new_key="domestic_hot_water_temperature",
    ),
    OldModbusItem(
        name="WW_Konfiguration",
        new_key="domestic_hot_water_configuration",
    ),
    OldModbusItem(
        name="Warmwasser Push",
        new_key="domestic_hot_water_push",
    ),
    OldModbusItem(
        name="Warmwasser Normal",
        new_key="domestic_hot_water_normal_temperature",
    ),
    OldModbusItem(
        name="Warmwasser Absenk",
        new_key="domestic_hot_water_lowering_temperature",
    ),
    OldModbusItem(
        name="SG Ready Anhebung",
        new_key="domestic_hot_water_sg_ready_raise",
    ),
)

SECOND_HEAT_SOURCE_UID_MIGRATIONS: tuple[OldModbusItem, ...] = (
    OldModbusItem(
        name="Status 2. WEZ",
        new_key="second_heat_source_status",
    ),
    OldModbusItem(
        name="Schaltspiele E-Heizung 1",
        new_key="second_heat_source_electric_heater_1_switch_cycles",
    ),
    OldModbusItem(
        name="Betriebsstunden E1",
        new_key="second_heat_source_electric_heater_1_operating_hours",
    ),
    OldModbusItem(
        name="Status E-Heizung 1",
        new_key="second_heat_source_electric_heater_1_status",
    ),
    OldModbusItem(
        name="Status E-Heizung 2",
        new_key="second_heat_source_electric_heater_2_status",
    ),
    OldModbusItem(
        name="Schaltspiele E-Heizung 2",
        new_key="second_heat_source_electric_heater_2_switch_cycles",
    ),
    OldModbusItem(
        name="Betriebsstunden E2",
        new_key="second_heat_source_electric_heater_2_operating_hours",
    ),
    OldModbusItem(
        name="W2_Konfiguration",
        new_key="second_heat_source_configuration",
    ),
    OldModbusItem(
        name="Konfiguration EP1",
        new_key="second_heat_source_electric_heater_1_configuration",
    ),
    OldModbusItem(
        name="Konfiguration EP2",
        new_key="second_heat_source_electric_heater_2_configuration",
    ),
    OldModbusItem(
        name="Grenztemperatur",
        new_key="second_heat_source_limit_temperature",
    ),
    OldModbusItem(
        name="Bivalenztemperatur",
        new_key="second_heat_source_bivalence_temperature",
    ),
    OldModbusItem(
        name="Bivalenztemperatur WW",
        new_key="second_heat_source_bivalence_temperature_hot_water",
    ),
)

STATISTICS_UID_MIGRATIONS: tuple[OldModbusItem, ...] = (
    OldModbusItem(
        name="Gesamt Energie heute",
        new_key="statistics_total_energy_today",
    ),
    OldModbusItem(
        name="Gesamt Energie gestern",
        new_key="statistics_total_energy_yesterday",
    ),
    OldModbusItem(
        name="Gesamt Energie Monat",
        new_key="statistics_total_energy_month",
    ),
    OldModbusItem(
        name="Gesamt Energie Jahr",
        new_key="statistics_total_energy_year",
    ),
    OldModbusItem(
        name="Heizen Energie heute",
        new_key="statistics_heating_energy_today",
    ),
    OldModbusItem(
        name="Heizen Energie gestern",
        new_key="statistics_heating_energy_yesterday",
    ),
    OldModbusItem(
        name="Heizen Energie Monat",
        new_key="statistics_heating_energy_month",
    ),
    OldModbusItem(
        name="Heizen Energie Jahr",
        new_key="statistics_heating_energy_year",
    ),
    OldModbusItem(
        name="Warmwasser Energie heute",
        new_key="statistics_hot_water_energy_today",
    ),
    OldModbusItem(
        name="Warmwasser Energie gestern",
        new_key="statistics_hot_water_energy_yesterday",
    ),
    OldModbusItem(
        name="Warmwasser Energie Monat",
        new_key="statistics_hot_water_energy_month",
    ),
    OldModbusItem(
        name="Warmwasser Energie Jahr",
        new_key="statistics_hot_water_energy_year",
    ),
    OldModbusItem(
        name="Kühlen Energie heute",
        new_key="statistics_cooling_energy_today",
    ),
    OldModbusItem(
        name="Kühlen Energie gestern",
        new_key="statistics_cooling_energy_yesterday",
    ),
    OldModbusItem(
        name="Kühlen Energie Monat",
        new_key="statistics_cooling_energy_month",
    ),
    OldModbusItem(
        name="Kühlen Energie Jahr",
        new_key="statistics_cooling_energy_year",
    ),
    OldModbusItem(
        name="Abtauen Energie heute",
        new_key="statistics_defrost_energy_today",
    ),
    OldModbusItem(
        name="Abtauen Energie gestern",
        new_key="statistics_defrost_energy_yesterday",
    ),
    OldModbusItem(
        name="Abtauen Energie Monat",
        new_key="statistics_defrost_energy_month",
    ),
    OldModbusItem(
        name="Abtauen Energie Jahr",
        new_key="statistics_defrost_energy_year",
    ),
    OldModbusItem(
        name="Gesamt Energie II heute",
        new_key="statistics_total_energy_2_today",
    ),
    OldModbusItem(
        name="Gesamt Energie II gestern",
        new_key="statistics_total_energy_2_yesterday",
    ),
    OldModbusItem(
        name="Gesamt Energie II Monat",
        new_key="statistics_total_energy_2_month",
    ),
    OldModbusItem(
        name="Gesamt Energie II Jahr",
        new_key="statistics_total_energy_2_year",
    ),
    OldModbusItem(
        name="Elektr. Energie heute",
        new_key="statistics_electric_energy_today",
    ),
    OldModbusItem(
        name="Elektr. Energie gestern",
        new_key="statistics_electric_energy_yesterday",
    ),
    OldModbusItem(
        name="Elektr. Energie Monat",
        new_key="statistics_electric_energy_month",
    ),
    OldModbusItem(
        name="Elektr. Energie Jahr",
        new_key="statistics_electric_energy_year",
    ),
    OldModbusItem(
        name="Adr. 36801",
        new_key="statistics_adr36801",
    ),
)


IO_UID_MIGRATIONS: tuple[OldModbusItem, ...] = (
    OldModbusItem(
        name="SG-Ready 1",
        new_key="io_sensor_sg_ready_1",
    ),
    OldModbusItem(
        name="SG-Ready 2",
        new_key="io_sensor_sg_ready_2",
    ),
    OldModbusItem(
        name="Ausgang H1.2",
        new_key="io_sensor_input_output_h1_2",
    ),
    OldModbusItem(
        name="Ausgang H1.3",
        new_key="io_sensor_output_h1_3",
    ),
    OldModbusItem(
        name="Ausgang H1.4",
        new_key="io_sensor_output_h1_4",
    ),
    OldModbusItem(
        name="Ausgang H1.5",
        new_key="io_sensor_output_h1_5",
    ),
    OldModbusItem(
        name="Eingang DE1",
        new_key="io_sensor_input_de1",
    ),
    OldModbusItem(
        name="Eingang DE2",
        new_key="io_sensor_input_de2",
    ),
    OldModbusItem(
        name="Konf. Eingang SGR1",
        new_key="io_select_sg_ready_1",
    ),
    OldModbusItem(
        name="Konf. Eingang SGR2",
        new_key="io_select_sg_ready_2",
    ),
    OldModbusItem(
        name="Konf. Ausgang H1.2",
        new_key="io_select_output_h1_2",
    ),
    OldModbusItem(
        name="Konf. Ausgang  H1.3",
        new_key="io_select_output_h1_3",
    ),
    OldModbusItem(
        name="Konf. Ausgang  H1.4",
        new_key="io_select_output_h1_4",
    ),
    OldModbusItem(
        name="Konf. Ausgang  H1.5",
        new_key="io_select_output_h1_5",
    ),
    OldModbusItem(
        name="Konf. Eingang DE1",
        new_key="io_select_input_de1",
    ),
    OldModbusItem(
        name="Konf. Eingang DE2",
        new_key="io_select_input_de2",
    ),
)

MIGRATION = (
    OLD_MODBUS_SYS_ITEMS
    + HEAT_PUMP_UID_MIGRATIONS
    + HEATING_CIRCUIT_UID_MIGRATIONS
    + DOMESTIC_HOT_WATER_UID_MIGRATIONS
    + SECOND_HEAT_SOURCE_UID_MIGRATIONS
    + STATISTICS_UID_MIGRATIONS
    + IO_UID_MIGRATIONS
)
