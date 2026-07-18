"""Translation helper utilities for Weishaupt Modbus integration."""

import json
import logging
from pathlib import Path
from typing import Any

from .const import FORMATS, TYPES
from .hpconst import DEVICELISTS
from .items import ModbusItem

_LOGGER = logging.getLogger(__name__)


def _sync_dict(
    master: dict[str, Any], locale: dict[str, Any]
) -> tuple[dict[str, Any], bool]:
    """Recursively sync a locale dictionary with a master dictionary.

    Preserves existing translated strings, appends new keys using master values
    as placeholders, and prunes removed keys. Returns the synced dictionary
    and a boolean indicating if any changes occurred.
    """
    synced: dict[str, Any] = {}
    changed = False

    # 1. Add/Update keys from master to locale
    for key, value in master.items():
        if key in locale:
            if isinstance(value, dict) and isinstance(locale[key], dict):
                # Recursively sync nested dictionaries
                sub_synced, sub_changed = _sync_dict(value, locale[key])
                synced[key] = sub_synced
                if sub_changed:
                    changed = True
            else:
                # Preserve the existing translated value
                synced[key] = locale[key]
        else:
            # Append missing key using master value as a placeholder
            synced[key] = value
            changed = True

    # 2. Prune old keys from locale that are no longer in master
    for key in list(locale.keys()):
        if key not in master:
            changed = True

    return synced, changed


def update_translation(config_dir: str = "config") -> None:
    """Synchronize strings.json, en.json, de.json, and nl.json without losing translations.

    This function reads ModbusItem definitions from hpconst.py, preserves all
    existing English, German, and Dutch translations, and automatically appends
    new keys (using German placeholders) only if they are missing from disk.
    """
    integration_dir = Path(config_dir) / "custom_components" / "weishaupt_modbus"
    strings_path = integration_dir / "strings.json"
    en_path = integration_dir / "translations" / "en.json"

    # 1. Load the existing translation data from strings.json as our master base
    if strings_path.exists():
        try:
            with strings_path.open(encoding="utf-8") as file:
                master_data = json.load(file)
        except json.JSONDecodeError, OSError:
            master_data = {}
    else:
        master_data = {}

    master_entity = master_data.setdefault("entity", {})
    master_sensors = master_entity.setdefault("sensor", {})
    master_numbers = master_entity.setdefault("number", {})
    master_selects = master_entity.setdefault("select", {})

    # 2. Build flat list of all ModbusItems currently in hpconst.py
    all_items: list[ModbusItem] = []
    for devicelist in DEVICELISTS:
        all_items.extend(devicelist)

    # 3. Rebuild category dictionaries, preserving existing translations
    new_sensors: dict[str, Any] = {}
    new_numbers: dict[str, Any] = {}
    new_selects: dict[str, Any] = {}

    for item in all_items:
        key = item.translation_key

        match item.type:
            case TYPES.SENSOR | TYPES.NUMBER_RO | TYPES.SENSOR_CALC:
                if key in master_sensors:
                    new_sensors[key] = master_sensors[key]
                else:
                    sensor_data = {"name": f"{{prefix}}{item.name}"}
                    if item.resultlist and item.format is FORMATS.STATUS:
                        sensor_data["state"] = {
                            status.translation_key: status.text
                            for status in item.resultlist
                        }
                    new_sensors[key] = sensor_data

            case TYPES.NUMBER:
                if key in master_numbers:
                    new_numbers[key] = master_numbers[key]
                else:
                    number_data = {"name": f"{{prefix}}{item.name}"}
                    if item.resultlist and item.format is FORMATS.STATUS:
                        number_data["value"] = {
                            status.translation_key: status.text
                            for status in item.resultlist
                        }
                    new_numbers[key] = number_data

            case TYPES.SELECT:
                if key in master_selects:
                    new_selects[key] = master_selects[key]
                else:
                    select_data = {"name": f"{{prefix}}{item.name}"}
                    if item.resultlist and item.format is FORMATS.STATUS:
                        select_data["state"] = {
                            status.translation_key: status.text
                            for status in item.resultlist
                        }
                    new_selects[key] = select_data

    new_entity_structure = {
        "sensor": new_sensors,
        "number": new_numbers,
        "select": new_selects,
    }

    # 4. Check if the master entity key structure has changed
    if master_entity != new_entity_structure:
        _LOGGER.info("Key synchronization detected changes. Syncing strings.json...")
        master_data["entity"] = new_entity_structure

        # Ensure parent directories exist
        strings_path.parent.mkdir(parents=True, exist_ok=True)

        with strings_path.open(mode="w", encoding="utf-8") as file:
            json.dump(master_data, file, indent=4, sort_keys=True, ensure_ascii=False)
    else:
        _LOGGER.debug("No key changes detected. Skipping strings.json write.")

    # 5. Ensure translations/en.json matches master_data exactly
    if en_path.exists():
        try:
            with en_path.open(encoding="utf-8") as file:
                en_data = json.load(file)
        except json.JSONDecodeError, OSError:
            en_data = {}
    else:
        en_data = {}

    if en_data != master_data:
        _LOGGER.info("Syncing changes to translations/en.json...")
        en_path.parent.mkdir(parents=True, exist_ok=True)
        with en_path.open(mode="w", encoding="utf-8") as file:
            json.dump(master_data, file, indent=4, sort_keys=True, ensure_ascii=False)
    else:
        _LOGGER.debug("translations/en.json is already in sync. Skipping write.")

    # 6. Recursively sync de.json and nl.json with the updated master_data
    for locale_code in ["de", "nl"]:
        locale_path = integration_dir / "translations" / f"{locale_code}.json"

        if locale_path.exists():
            try:
                with locale_path.open(encoding="utf-8") as file:
                    locale_data = json.load(file)
            except json.JSONDecodeError, OSError:
                locale_data = {}
        else:
            locale_data = {}

        # Sync the locale dictionary recursively with the master strings data
        synced_data, changed = _sync_dict(master_data, locale_data)

        if changed:
            _LOGGER.info("Syncing key changes to translations/%s.json...", locale_code)
            locale_path.parent.mkdir(parents=True, exist_ok=True)
            with locale_path.open(mode="w", encoding="utf-8") as file:
                json.dump(
                    synced_data, file, indent=4, sort_keys=True, ensure_ascii=False
                )
        else:
            _LOGGER.debug(
                "translations/%s.json is already in sync. Skipping write.", locale_code
            )
