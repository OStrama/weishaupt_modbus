import json
import os

print("🚀 Skript wurde gestartet! Lade Konfiguration...")

# --- MAPPINGS ---
REVERSE_DEVICE_MAP = {
    "dev_heat_pump": "dev_waermepumpe",
    "dev_domestic_hot_water": "dev_warmwasser",
    "dev_second_heat_source": "dev_waermeerzeuger2",
    "dev_statistics": "dev_statistik",
}

REVERSE_ENTITY_MAP = {
    # SELECT
    "heating_circuit_operation_mode": ["hz_operationmode"],
    "heating_circuit_party_pause": ["party_pause"],
    "system_config_operating_mode": ["sys_operationmode"],
    "domestic_hot_water_push": ["ww_push"],
    "heating_circuit_demand": ["anf_typ"],
    "heat_pump_rest_mode": ["ruhemodus"],
    "heat_pump_configuration": ["wp_konf"],
    "heating_circuit_water_configuration": ["hz_konf"],
    "second_heat_source_electric_heater_1_configuration": ["adr44102"],
    "second_heat_source_electric_heater_2_configuration": ["adr44103"],
    "second_heat_source_configuration": ["w2_konf"],
    "domestic_hot_water_configuration": ["ww_konf"],
    # NUMBER
    "second_heat_source_bivalence_temperature": ["bivalenztemp"],
    "second_heat_source_bivalence_temperature_hot_water": ["bivalenztemp_ww"],
    "second_heat_source_limit_temperature": ["grenztemp"],
    "heating_circuit_lowering_room_target_temperature": ["raum_soll_temp_absenk"],
    "heating_circuit_comfort_room_target_temperature": ["raum_soll_temp_komf"],
    "heating_circuit_normal_room_target_temperature": ["raum_soll_temp_normal"],
    "domestic_hot_water_sg_ready_raise": ["sgr_anhebung"],
    "domestic_hot_water_lowering_temperature": ["ww_absenk"],
    "domestic_hot_water_normal_temperature": ["ww_normal"],
    "heat_pump_heating_flow_rate_setpoint": ["soll_volumenstrom_heizen"],
    "heat_pump_cooling_flow_rate_setpoint": ["soll_volumenstrom_kuehlen"],
    "heat_pump_hot_water_flow_rate_setpoint": ["soll_volumenstrom_ww"],
    "heat_pump_defrost_pump_power_setpoint": ["sollwert_pumpe_leistung_abtau"],
    "heat_pump_heating_pump_power_setpoint": ["sollwert_pumpe_leistung_heizen"],
    "heat_pump_cooling_pump_power_setpoint": ["sollwert_pumpe_leistung_kuehlen"],
    "heat_pump_hot_water_pump_power_setpoint": ["sollwert_pumpe_leitung_ww"],
    "system_pv_setpoint": ["sys_pv"],
    # SENSOR
    "system_outside_temperature": ["aussentemp"],
    "system_intake_temperature": ["luftansautgemp"],
    "system_error": ["fehler"],
    "system_warning": ["warnung"],
    "system_error_free": ["fehlerfrei"],
    "system_operating_display": ["betriebsanzeige"],
    "statistics_defrost_energy_today": ["abtau_energie_heute"],
    "statistics_defrost_energy_yesterday": [
        "abtau_energie_gester",
        "abtau_energie_yesterday",
        "statistics_defrost_energie_yesterday",
    ],
    "statistics_defrost_energy_month": ["abtau_energie_monat"],
    "statistics_defrost_energy_year": ["abtau_energie_jahr"],
    "statistics_electric_energy_today": ["el_energie_heute"],
    "statistics_electric_energy_yesterday": [
        "el_energie_gestern",
        "el_energie_yesterday",
    ],
    "statistics_electric_energy_month": ["el_energie_monat"],
    "statistics_electric_energy_year": ["el_energie_jahr"],
    "statistics_total_energy_today": ["ges_energie_heute"],
    "statistics_total_energy_yesterday": [
        "ges_energie_yesterday",
        "ges_energie_gestern",
    ],
    "statistics_total_energy_month": ["ges_energie_monat"],
    "statistics_total_energy_year": ["ges_energie_jahr"],
    "statistics_total_energy_2_today": ["ges_energie_2_today", "ges_energie_2_heute"],
    "statistics_total_energy_2_yesterday": [
        "ges_energie_2_yesterday",
        "ges_energie_2_gestern",
    ],
    "statistics_total_energy_2_month": ["ges_energie_2_monat"],
    "statistics_total_energy_2_year": ["ges_energie_2_year", "ges_energie_2_jahr"],
    "statistics_heating_energy_today": ["heiz_energie_heute"],
    "statistics_heating_energy_yesterday": [
        "heiz_energie_getern",
        "heiz_energie_gestern",
    ],
    "statistics_heating_energy_month": ["heiz_energie_monat"],
    "statistics_heating_energy_year": [
        "heiz_energie_jahr",
        "statistics_heating_energy_jahr",
    ],
    "statistics_cooling_energy_today": ["kuehl_energie_heute"],
    "statistics_cooling_energy_yesterday": [
        "kuehl_energie_gestern",
        "kuehl_energie_yesterday",
    ],
    "statistics_cooling_energy_month": ["kuehl_energie_monat"],
    "statistics_cooling_energy_year": ["kuehl_energie_jahr"],
    "statistics_hot_water_energy_today": ["ww_energie_heute"],
    "statistics_hot_water_energy_yesterday": [
        "ww_energie_gestern",
        "ww_energie_yesterday",
    ],
    "statistics_hot_water_energy_month": ["ww_energie_monat"],
    "statistics_hot_water_energy_year": ["ww_energie_jahr"],
    "heat_pump_operation": ["wp_betrieb"],
    "heat_pump_fault": ["wp_stoermeldung"],
    "heat_pump_flow_temperature": ["vl_temp"],
    "heat_pump_return_temperature": ["rl_temp"],
    "heat_pump_temperature_spread": ["spreizung"],
    "heat_pump_diverter_temperature": ["weichen_temp"],
    "heat_pump_power_request": ["leistungsanforderung"],
    "heat_pump_buffer_temperature": ["puffer_temp"],
    "heating_circuit_room_target_temperature": ["raum_soll_temp"],
    "heating_circuit_room_temperature": ["raum_temp"],
    "heating_circuit_room_humidity": ["raum_feuchte"],
    "domestic_hot_water_temperature": ["ww_temp"],
    "domestic_hot_water_target_temperature": ["ww_soll_temp"],
    "second_heat_source_status": ["status_2_wez"],
    "second_heat_source_electric_heater_1_status": ["status_e1"],
    "second_heat_source_electric_heater_2_status": ["status_e2"],
    "second_heat_source_electric_heater_1_operating_hours": ["betriebss_e1"],
    "second_heat_source_electric_heater_2_operating_hours": ["betriebss_e2"],
    "second_heat_source_electric_heater_1_switch_cycles": ["schaltsp_e1"],
    "second_heat_source_electric_heater_2_switch_cycles": ["schaltsp_e2"],
    "heat_pump_regenerative_flow_temperature": ["anforderung_vl_regenerativ"],
    "heat_pump_evaporation_temperature": ["verdampfungs_temp"],
    "heat_pump_compressor_suction_temperature": ["verdichter_ansaug_gas_temp"],
    "heat_pump_precise_flow_temperature": ["vl_praeziese_summenvorlauf_b7"],
    "heat_pump_pump_start_type": ["pumpe_einschaltart"],
}

OPERATING_DISPLAY_MAP = {
    "system_operating_display_0": "system_operationmode_pvmode",
    "system_operating_display_1": "system_operationmode_relaistest",
    "system_operating_display_2": "system_operationmode_emergencystop",
    "system_operating_display_3": "system_operationmode_diagnosis",
    "system_operating_display_4": "system_operationmode_manual",
    "system_operating_display_5": "system_operationmode_manualheating",
    "system_operating_display_6": "system_operationmode_manualcooling",
    "system_operating_display_7": "system_operationmode_manualdefrost",
    "system_operating_display_8": "system_operationmode_defrost",
    "system_operating_display_9": "system_operationmode_manual2ndheatsource",
    "system_operating_display_10": "system_operationmode_evu",
    "system_operating_display_11": "system_operationmode_sgtariff",
    "system_operating_display_12": "system_operationmode_sgmax",
    "system_operating_display_13": "system_operationmode_tariffload",
    "system_operating_display_14": "system_operationmode_elevatedoperation",
    "system_operating_display_15": "system_operationmode_standbytime",
    "system_operating_display_16": "system_operationmode_standby",
    "system_operating_display_17": "system_operationmode_rinse",
    "system_operating_display_18": "system_operationmode_frosprotection",
    "system_operating_display_19": "system_operationmode_heating",
    "system_operating_display_20": "system_operationmode_hotwater",
    "system_operating_display_21": "system_operationmode_legionellaprotection",
    "system_operating_display_22": "system_operationmode_switchheatingcooling",
    "system_operating_display_23": "system_operationmode_cooling",
    "system_operating_display_24": "system_operationmode_passivecooling",
    "system_operating_display_25": "system_operationmode_summer",
    "system_operating_display_26": "system_operationmode_swimmingpool",
    "system_operating_display_27": "system_operationmode_vacation",
    "system_operating_display_28": "system_operationmode_screedprogram",
    "system_operating_display_29": "system_operationmode_locked",
    "system_operating_display_30": "system_operationmode_lockedat",
    "system_operating_display_31": "system_operationmode_lockedsummer",
    "system_operating_display_32": "system_operationmode_lockedwinter",
    "system_operating_display_33": "system_operationmode_applicationlimit",
    "system_operating_display_34": "system_operationmode_lockedcv",
    "system_operating_display_35": "system_operationmode_lowering",
    "system_operating_display_36": "system_operationmode_regenerativeflow",
    "system_operating_display_37": "system_operationmode_heating_sgr",
    "system_operating_display_39": "system_operationmode_hotwater_sgr",
    "system_operating_display_43": "system_operationmode_oilrecirculation",
}


def clean_string(val):
    if isinstance(val, str):
        return val.replace("{prefix}", "").replace("{postfix}", "").strip()
    return val


def get_old_entity(source_json, possible_keys):
    if "entity" in source_json:
        for domain in ["number", "select", "sensor"]:
            if domain in source_json["entity"]:
                for k in possible_keys:
                    if k in source_json["entity"][domain]:
                        return source_json["entity"][domain][k]
    return None


def migrate_translation(master_file, source_file, output_file):
    print(
        f"🔄 Starte Migration von {source_file} basierend auf Struktur von {master_file}..."
    )

    with open(master_file, "r", encoding="utf-8") as f:
        master = json.load(f)
    with open(source_file, "r", encoding="utf-8") as f:
        source = json.load(f)

    target = {}

    if "config" in master:
        target["config"] = source.get("config", master["config"])

    if "device" in master:
        target["device"] = {}
        for new_dev_key, dev_val in master["device"].items():
            old_dev_key = REVERSE_DEVICE_MAP.get(new_dev_key, new_dev_key)
            if "device" in source and old_dev_key in source["device"]:
                name = source["device"][old_dev_key]["name"]
                target["device"][new_dev_key] = {"name": clean_string(name)}
            elif "device" in source and new_dev_key in source["device"]:
                name = source["device"][new_dev_key]["name"]
                target["device"][new_dev_key] = {"name": clean_string(name)}
            else:
                target["device"][new_dev_key] = {"name": clean_string(dev_val["name"])}

    if "entity" in master:
        target["entity"] = {}
        for domain, entities in master["entity"].items():
            target["entity"][domain] = {}
            for new_key, new_val in entities.items():
                possible_keys = [new_key]
                if new_key in REVERSE_ENTITY_MAP:
                    possible_keys.extend(REVERSE_ENTITY_MAP[new_key])

                old_data = get_old_entity(source, possible_keys)

                if old_data:
                    target_entity = {"name": clean_string(old_data["name"])}

                    if "state" in new_val:
                        target_entity["state"] = {}
                        for new_state_key, new_state_val in new_val["state"].items():
                            old_state_key = new_state_key

                            if new_state_key in OPERATING_DISPLAY_MAP:
                                old_state_key = OPERATING_DISPLAY_MAP[new_state_key]
                            elif new_state_key.startswith("system_error_"):
                                old_state_key = new_state_key.replace(
                                    "system_error_", "sys_fehler_"
                                )
                            elif new_state_key.startswith("system_warning_"):
                                old_state_key = new_state_key.replace(
                                    "system_warning_", "sys_fehler_"
                                )

                            if (
                                "state" in old_data
                                and old_state_key in old_data["state"]
                            ):
                                target_entity["state"][new_state_key] = clean_string(
                                    old_data["state"][old_state_key]
                                )
                            elif (
                                "state" in old_data
                                and new_state_key in old_data["state"]
                            ):
                                target_entity["state"][new_state_key] = clean_string(
                                    old_data["state"][new_state_key]
                                )
                            else:
                                target_entity["state"][new_state_key] = clean_string(
                                    new_state_val
                                )

                    target["entity"][domain][new_key] = target_entity
                else:
                    cleaned_val = {"name": clean_string(new_val["name"])}
                    if "state" in new_val:
                        cleaned_state = {
                            k: clean_string(v) for k, v in new_val["state"].items()
                        }
                        cleaned_val["state"] = cleaned_state
                    target["entity"][domain][new_key] = cleaned_val

    if "title" in master:
        target["title"] = source.get("title", master["title"])

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(target, f, indent=4, ensure_ascii=False)

    print(f"✅ Datei '{output_file}' wurde erfolgreich generiert!")


# ==========================================
# AUSFÜHRUNG
# ==========================================
if __name__ == "__main__":
    MASTER_FILE = "de.json"
    SOURCE_FILE = "en.json"
    OUTPUT_FILE = "en_neu.json"

    print(f"🔍 Suche nach {MASTER_FILE} und {SOURCE_FILE}...")

    if os.path.exists(MASTER_FILE) and os.path.exists(SOURCE_FILE):
        migrate_translation(MASTER_FILE, SOURCE_FILE, OUTPUT_FILE)
    else:
        print(
            f"❌ Fehler: Ich finde die Dateien nicht! Stelle sicher, dass '{MASTER_FILE}' und '{SOURCE_FILE}' in diesem Ordner liegen:\n{os.getcwd()}"
        )
