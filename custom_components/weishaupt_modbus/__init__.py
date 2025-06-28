"""Integration for Weishaupt modbus heat pumps."""

import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .configentry import MyConfigEntry, MyData
from .const import CONF, CONST, DEVICENAMES, FormatConstants, TypeConstants
from .coordinator import MyCoordinator
from .hpconst import (
    DEVICELISTS,
    MODBUS_HZ2_ITEMS,
    MODBUS_HZ3_ITEMS,
    MODBUS_HZ4_ITEMS,
    MODBUS_HZ5_ITEMS,
    MODBUS_HZ_ITEMS,
    MODBUS_IO_ITEMS,
    MODBUS_ST_ITEMS,
    MODBUS_SYS_ITEMS,
    MODBUS_W2_ITEMS,
    MODBUS_WP_ITEMS,
    MODBUS_WW_ITEMS,
)
from .items import ModbusItem
from .kennfeld import PowerMap
from .migrate_helpers import migrate_entities
from .modbusobject import ModbusAPI
from .webif_object import WebifConnection

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = [
    "number",
    "select",
    "sensor",
]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up entry."""
    try:
        # Initialize modbus API
        mbapi = ModbusAPI(config_entry=entry)

        # Initialize WebIF API if enabled
        webapi = None
        if entry.data[CONF.CB_WEBIF]:
            webapi = WebifConnection(config_entry=entry)
            await webapi.login()

        # Collect all items from device lists
        itemlist = [item for device in DEVICELISTS for item in device]

        # Initialize coordinator
        coordinator = MyCoordinator(
            hass=hass, my_api=mbapi, api_items=itemlist, config_entry=entry
        )

        # Initialize power map
        pwrmap = PowerMap(entry, hass)
        await pwrmap.initialize()

        # Store runtime data
        entry.runtime_data = MyData(
            modbus_api=mbapi,
            webif_api=webapi,
            config_dir=hass.config.config_dir,
            hass=hass,
            coordinator=coordinator,
            powermap=pwrmap,
        )

        # Schedule entity migrations
        _schedule_migrations(hass, entry)

        # Set up update listener
        entry.async_on_unload(entry.add_update_listener(update_listener))

        # Forward setup to platforms
        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

        _LOGGER.info("Setup completed successfully")
        return True

    except Exception as err:
        _LOGGER.exception("Failed to set up integration: %s", err)
        raise ConfigEntryNotReady from err


def _schedule_migrations(hass: HomeAssistant, entry: MyConfigEntry) -> None:
    """Schedule entity migrations for all device types."""
    migrations = [
        (MODBUS_SYS_ITEMS, DEVICENAMES.SYS),
        (MODBUS_HZ_ITEMS, DEVICENAMES.HZ),
        (MODBUS_HZ2_ITEMS, DEVICENAMES.HZ2),
        (MODBUS_HZ3_ITEMS, DEVICENAMES.HZ3),
        (MODBUS_HZ4_ITEMS, DEVICENAMES.HZ4),
        (MODBUS_HZ5_ITEMS, DEVICENAMES.HZ5),
        (MODBUS_WP_ITEMS, DEVICENAMES.WP),
        (MODBUS_WW_ITEMS, DEVICENAMES.WW),
        (MODBUS_W2_ITEMS, DEVICENAMES.W2),
        (MODBUS_IO_ITEMS, DEVICENAMES.IO),
        (MODBUS_ST_ITEMS, DEVICENAMES.ST),
    ]

    for items, device_name in migrations:
        hass.add_job(migrate_entities, entry, items, device_name)


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass: HomeAssistant, config_entry: MyConfigEntry) -> bool:
    """Migrate old entry."""
    new_data = {**config_entry.data}

    if config_entry.version > 6:
        # User has downgraded from a future version
        return True

    # Migrate from version 1 to 2
    if config_entry.version < 2:
        _LOGGER.warning("Migrating from version %d", config_entry.version)
        new_data.update(
            {
                CONF.PREFIX: CONST.DEF_PREFIX,
                CONF.DEVICE_POSTFIX: "",
                CONF.KENNFELD_FILE: CONST.DEF_KENNFELDFILE,
            }
        )

    # Migrate from version 2 to 3
    if config_entry.version < 3:
        _LOGGER.warning("Migrating from version %d", config_entry.version)
        new_data.update(
            {
                CONF.HK2: False,
                CONF.HK3: False,
                CONF.HK4: False,
                CONF.HK5: False,
            }
        )

    # Migrate from version 3 to 4
    if config_entry.version < 4:
        _LOGGER.warning("Migrating from version %d", config_entry.version)
        new_data.update(
            {
                CONF.NAME_DEVICE_PREFIX: False,
                CONF.NAME_TOPIC_PREFIX: False,
            }
        )

    # Migrate from version 4 to 5
    if config_entry.version < 5:
        _LOGGER.warning("Migrating from version %d", config_entry.version)
        new_data.update(
            {
                CONF.CB_WEBIF: False,
                CONF.USERNAME: "",
                CONF.PASSWORD: "",
                CONF.WEBIF_TOKEN: "",
            }
        )

    # Update to latest version
    hass.config_entries.async_update_entry(
        config_entry, data=new_data, minor_version=1, version=6
    )
    _LOGGER.info("Migration completed to version 6")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    # Close modbus API connection
    if hasattr(entry.runtime_data, "modbus_api"):
        entry.runtime_data.modbus_api.close()

    # Close WebIF connection if it exists
    if hasattr(entry.runtime_data, "webif_api") and entry.runtime_data.webif_api:
        await entry.runtime_data.webif_api.close()

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        try:
            hass.data[entry.data[CONF.PREFIX]].pop(entry.entry_id)
        except KeyError:
            _LOGGER.debug("KeyError removing entry data: %s", entry.data[CONF.PREFIX])

    return unload_ok


def create_string_json() -> None:
    """Create strings.json from hpconst.py."""
    # Collect all items from device lists
    device_list = [item for device in DEVICELISTS for item in device]

    my_sensors: dict[str, Any] = {}
    my_numbers: dict[str, Any] = {}
    my_selects: dict[str, Any] = {}

    for item in device_list:
        match item.type:
            case (
                TypeConstants.SENSOR
                | TypeConstants.NUMBER_RO
                | TypeConstants.SENSOR_CALC
            ):
                sensor_data = _create_sensor_data(item)
                my_sensors[item.translation_key] = sensor_data
            case TypeConstants.NUMBER:
                number_data = _create_number_data(item)
                my_numbers[item.translation_key] = number_data
            case TypeConstants.SELECT:
                select_data = _create_select_data(item)
                my_selects[item.translation_key] = select_data

    # Create final JSON structure
    my_json = {
        "entity": {
            "sensor": my_sensors,
            "number": my_numbers,
            "select": my_selects,
        }
    }

    # Update strings.json file
    _update_strings_json(my_json["entity"])


def _create_sensor_data(item: ModbusItem) -> dict[str, Any]:
    """Create sensor data for strings.json."""
    sensor_data = {"name": f"{{prefix}}{item.name}"}

    if item.resultlist and item.format is FormatConstants.STATUS:
        values = {
            status_item.translation_key: str(status_item.text)
            if status_item.text
            else ""
            for status_item in item.resultlist
            if status_item is not None
        }
        sensor_data["state"] = json.dumps(values)

    return sensor_data


def _create_number_data(item: ModbusItem) -> dict[str, Any]:
    """Create number data for strings.json."""
    number_data = {"name": f"{{prefix}}{item.name}"}

    if item.resultlist and item.format is FormatConstants.STATUS:
        # Create a flat dictionary of translation keys to display text
        values = {}
        for status_item in item.resultlist:
            if status_item is not None and status_item.translation_key:
                values[status_item.translation_key] = (
                    str(status_item.text) if status_item.text else ""
                )

        # Only add values if we have any
        if values:
            number_data["value"] = json.dumps(values)

    return number_data


def _create_select_data(item: ModbusItem) -> dict[str, Any]:
    """Create select data for strings.json."""
    select_data = {"name": f"{{prefix}}{item.name}"}

    if item.resultlist and item.format is FormatConstants.STATUS:
        # Create a flat dictionary of translation keys to display text
        options = {}
        for status_item in item.resultlist:
            if status_item is not None and status_item.translation_key:
                options[status_item.translation_key] = (
                    str(status_item.text) if status_item.text else ""
                )

        # Only add options if we have any
        if options:
            select_data["options"] = json.dumps(options)

    return select_data


def _update_strings_json(entity_data: dict[str, Any]) -> None:
    """Update the strings.json file with new entity data."""
    strings_path = Path("config/custom_components/weishaupt_modbus/strings.json")

    try:
        # Read existing strings.json or create empty structure
        if strings_path.exists():
            with strings_path.open(encoding="utf-8") as file:
                data_dict = json.load(file)
        else:
            data_dict = {}

        # Ensure entity section exists
        if "entity" not in data_dict:
            data_dict["entity"] = {}

        # Update each platform's entity data
        for platform, entities in entity_data.items():
            if platform not in data_dict["entity"]:
                data_dict["entity"][platform] = {}

            # Merge new entities with existing ones
            data_dict["entity"][platform].update(entities)

        # Ensure parent directory exists
        strings_path.parent.mkdir(parents=True, exist_ok=True)

        # Write updated data back to file
        with strings_path.open(mode="w", encoding="utf-8") as file:
            json.dump(data_dict, file, indent=2, sort_keys=True, ensure_ascii=False)

        _LOGGER.debug(
            "Successfully updated strings.json with %d platforms", len(entity_data)
        )

    except (OSError, json.JSONDecodeError) as err:
        _LOGGER.error("Failed to update strings.json: %s", err)
