#!/usr/bin/env python3

from pathlib import Path


REPLACEMENTS = {
    # System / Basis Sensoren
    "aussentemp": "system_outside_temperature",
    "luftansautgemp": "system_intake_temperature",
    "fehler": "system_error",
    "warnung": "system_warning",
    "fehlerfrei": "system_error_free",
    "betriebsanzeige": "system_operating_display",
    "sys_operationmode": "system_operating_mode",
    "sys_pv": "system_pv_setpoint",
    # Statistik
    "abtau_energie_heute": "statistics_defrost_energy_today",
    "abtau_energie_gester": "statistics_defrost_energie_yesterday",  # Achtung: Tippfehler im Original "gester"
    "abtau_energie_monat": "statistics_defrost_energy_month",
    "abtau_energie_jahr": "statistics_defrost_energy_year",
    "el_energie_heute": "statistics_electric_energy_today",
    "el_energie_gestern": "statistics_electric_energy_yesterday",
    "el_energie_monat": "statistics_electric_energy_month",
    "el_energie_jahr": "statistics_electric_energy_year",
    "ges_energie_heute": "statistics_total_energy_today",
    "ges_energie_yesterday": "statistics_total_energy_yesterday",
    "ges_energie_monat": "statistics_total_energy_month",
    "ges_energie_jahr": "statistics_total_energy_year",
    "heiz_energie_heute": "statistics_heating_energy_today",
    "heiz_energie_getern": "statistics_heating_energy_yesterday",
    "heiz_energie_monat": "statistics_heating_energy_month",
    "heiz_energie_jahr": "statistics_heating_energy_jahr",  # Prüfe ob "year" oder "jahr"
    "kuehl_energie_heute": "statistics_cooling_energy_today",
    "kuehl_energie_gestern": "statistics_cooling_energy_yesterday",
    "kuehl_energie_monat": "statistics_cooling_energy_month",
    "kuehl_energie_jahr": "statistics_cooling_energy_year",
    "ww_energie_heute": "statistics_hot_water_energy_today",
    "ww_energie_gestern": "statistics_hot_water_energy_yesterday",
    "ww_energie_monat": "statistics_hot_water_energy_month",
    "ww_energie_jahr": "statistics_hot_water_energy_year",
    # Wärmepumpe / Heizkreis
    "wp_betrieb": "heat_pump_operation",
    "wp_stoermeldung": "heat_pump_fault",
    "wp_konf": "heat_pump_configuration",
    "anf_typ": "heating_circuit_demand",
    "vl_temp": "heat_pump_flow_temperature",
    "rl_temp": "heat_pump_return_temperature",
    "spreizung": "heat_pump_temperature_spread",
    "weichen_temp": "heat_pump_diverter_temperature",
    "leistungsanforderung": "heat_pump_power_request",
    "puffer_temp": "heat_pump_buffer_temperature",
    "raum_soll_temp": "heating_circuit_room_target_temperature",
    "raum_temp": "heating_circuit_room_temperature",
    "raum_feuchte": "heating_circuit_room_humidity",
    "hz_operationmode": "heating_circuit_operation_mode",
    "party_pause": "heating_circuit_party_pause",
    "ww_temp": "domestic_hot_water_temperature",
    "ww_soll_temp": "domestic_hot_water_target_temperature",
    "ww_push": "domestic_hot_water_push",
    "ww_konf": "domestic_hot_water_configuration",
    # Zweiter Wärmeerzeuger
    "bivalenztemp": "second_heat_source_bivalence_temperature",
    "bivalenztemp_ww": "second_heat_source_bivalence_temperature_hot_water",
    "grenztemp": "second_heat_source_limit_temperature",
    "status_2_wez": "second_heat_source_status",
    "status_e1": "second_heat_source_electric_heater_1_status",
    "status_e2": "second_heat_source_electric_heater_2_status",
    "betriebss_e1": "second_heat_source_electric_heater_1_operating_hours",
    "betriebss_e2": "second_heat_source_electric_heater_2_operating_hours",
    "schaltsp_e1": "second_heat_source_electric_heater_1_switch_cycles",
    "schaltsp_e2": "second_heat_source_electric_heater_2_switch_cycles",
    "w2_konf": "second_heat_source_configuration",
}


def replace_keys(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    replacements = 0

    for old_key, new_key in REPLACEMENTS.items():
        old = f'"{old_key}": {{'
        new = f'"{new_key}": {{'

        count = text.count(old)

        if count:
            text = text.replace(old, new)
            replacements += count
            print(f"{path.name}: {old_key} -> {new_key} ({count})")

    path.write_text(text, encoding="utf-8")

    print(f"{path.name}: {replacements} replacement(s)")


if __name__ == "__main__":
    directory = Path(__file__).resolve().parent

    for filename in ("de.json", "en.json", "nl.json"):
        path = directory / filename

        if not path.exists():
            print(f"{filename}: not found")
            continue

        replace_keys(path)
