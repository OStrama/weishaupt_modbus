"""Home Assistant integration initialization."""

from __future__ import annotations

import copy
import json
import logging
from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .configentry import MyConfigEntry, MyData
from .const import CONF, CONST, DEVICENAMES, FORMATS, TYPES
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
    #    "switch",
]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up entry."""
    mbapi = ModbusAPI(config_entry=entry)

    if entry.data[CONF.CB_WEBIF]:
        # print
        webapi = WebifConnection(config_entry=entry)
        await webapi.login()
    else:
        webapi = None

    # Create independent copies of ModbusItems for each config entry
    itemlist = []

    for device in DEVICELISTS:
        itemlist.extend(copy.deepcopy(item) for item in device)

    coordinator = MyCoordinator(
        hass=hass, my_api=mbapi, api_items=itemlist, p_config_entry=entry
    )
    # await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = MyData(
        modbus_api=mbapi,
        webif_api=webapi,
        config_dir=hass.config.config_dir,
        hass=hass,
        coordinator=coordinator,
        powermap=None,
    )

    powermap = PowerMap(entry, hass)
    await powermap.initialize()
    entry.runtime_data.powermap = powermap

    # myWebifCon = WebifConnection()
    # data = await myWebifCon.return_test_data()
    # print(data)
    # print(myWebifCon._session.closed)
    # await myWebifCon.login()
    # print(myWebifCon._session.closed)
    # data = await myWebifCon.get_info()
    # await myWebifCon.close()
    # print(myWebifCon._session.closed)

    hass.add_job(migrate_entities, entry, MODBUS_SYS_ITEMS, DEVICENAMES.SYS)
    hass.add_job(migrate_entities, entry, MODBUS_HZ_ITEMS, DEVICENAMES.HZ)
    hass.add_job(migrate_entities, entry, MODBUS_HZ2_ITEMS, DEVICENAMES.HZ2)
    hass.add_job(migrate_entities, entry, MODBUS_HZ3_ITEMS, DEVICENAMES.HZ3)
    hass.add_job(migrate_entities, entry, MODBUS_HZ4_ITEMS, DEVICENAMES.HZ4)
    hass.add_job(migrate_entities, entry, MODBUS_HZ5_ITEMS, DEVICENAMES.HZ5)
    hass.add_job(migrate_entities, entry, MODBUS_WP_ITEMS, DEVICENAMES.WP)
    hass.add_job(migrate_entities, entry, MODBUS_WW_ITEMS, DEVICENAMES.WW)
    hass.add_job(migrate_entities, entry, MODBUS_W2_ITEMS, DEVICENAMES.W2)
    hass.add_job(migrate_entities, entry, MODBUS_IO_ITEMS, DEVICENAMES.IO)
    hass.add_job(migrate_entities, entry, MODBUS_ST_ITEMS, DEVICENAMES.ST)

    # see https://community.home-assistant.io/t/config-flow-how-to-update-an-existing-entity/522442/8
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # This is used to generate a strings.json file from hpconst.py
    # create_string_json()

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("Init done")

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(
        entry.entry_id
    )  # list of entry_ids created for file


async def async_migrate_entry(hass: HomeAssistant, config_entry: MyConfigEntry):
    """Migrate old entry."""

    new_data = {**config_entry.data}

    if config_entry.version > 4:
        # This means the user has downgraded from a future version
        return True

    # to ensure all update paths we have to check every version to not overwrite existing entries
    if config_entry.version < 4:
        _LOGGER.warning("Old Version detected")

    if config_entry.version < 2:
        _LOGGER.warning("Version <2 detected")
        new_data[CONF.PREFIX] = CONST.DEF_PREFIX
        new_data[CONF.DEVICE_POSTFIX] = ""
        new_data[CONF.KENNFELD_FILE] = CONST.DEF_KENNFELDFILE
    if config_entry.version < 3:
        _LOGGER.warning("Version <3 detected")
        new_data[CONF.HK2] = False
        new_data[CONF.HK3] = False
        new_data[CONF.HK4] = False
        new_data[CONF.HK5] = False
    if config_entry.version < 4:
        _LOGGER.warning("Version <4 detected")
        new_data[CONF.NAME_DEVICE_PREFIX] = False
        new_data[CONF.NAME_TOPIC_PREFIX] = False

    if config_entry.version < 5:
        new_data[CONF.CB_WEBIF] = False
        new_data[CONF.USERNAME] = ""
        new_data[CONF.PASSWORD] = ""
        new_data[CONF.WEBIF_TOKEN] = ""
        hass.config_entries.async_update_entry(
            config_entry, data=new_data, minor_version=1, version=5
        )
        _LOGGER.warning("Config entries updated to version 5")

    hass.config_entries.async_update_entry(
        config_entry, data=new_data, minor_version=1, version=6
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    entry.runtime_data.modbus_api.close()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        try:
            hass.data[entry.data[CONF.PREFIX]].pop(entry.entry_id)
        except KeyError:
            _LOGGER.warning("KeyError: %s", str(entry.data[CONF.PREFIX]))

    return unload_ok


def create_string_json() -> None:
    """Create strings.json from hpconst.py."""
    myEntity: dict[str, dict[str, dict[str, Any]]] = {}
    myJson: dict[str, Any] = {}
    mySensors: dict[str, dict[str, Any]] = {}
    myNumbers: dict[str, dict[str, Any]] = {}
    mySelects: dict[str, dict[str, Any]] = {}

    # generate list of all mbitems
    DEVICELIST: list[ModbusItem] = []
    for devicelist in DEVICELISTS:
        DEVICELIST = DEVICELIST + devicelist

    for item in DEVICELIST:
        match item.type:
            case (
                TYPES.SENSOR
                | TYPES.NUMBER_RO
                | TYPES.SENSOR_CALC
            ):
                mySensor: dict[str, Any] = {}
                mySensor["name"] = "{prefix}" + item.name
                if item.resultlist is not None:
                    if item.format is FORMATS.STATUS:
                        myValues: dict[str, str] = {}
                        for myStatusItem in item.resultlist:
                            myValues[myStatusItem.translation_key] = myStatusItem.text
                        mySensor["state"] = myValues
                mySensors[item.translation_key] = mySensor.copy()
            case TYPES.NUMBER:
                myNumber: dict[str, Any] = {}
                myNumber["name"] = "{prefix}" + item.name
                if item.resultlist is not None:
                    if item.format is FORMATS.STATUS:
                        myNumberValues: dict[str, str] = {}
                        for myStatusItem in item.resultlist:
                            myNumberValues[myStatusItem.translation_key] = (
                                myStatusItem.text
                            )
                        myNumber["value"] = myNumberValues
                myNumbers[item.translation_key] = myNumber.copy()
            case TYPES.SELECT:
                mySelect: dict[str, Any] = {}
                mySelect["name"] = "{prefix}" + item.name
                if item.resultlist is not None:
                    if item.format is FORMATS.STATUS:
                        mySelectValues: dict[str, str] = {}
                        for myStatusItem in item.resultlist:
                            mySelectValues[myStatusItem.translation_key] = (
                                myStatusItem.text
                            )
                        mySelect["state"] = mySelectValues
                mySelects[item.translation_key] = mySelect.copy()
    myEntity["sensor"] = mySensors
    myEntity["number"] = myNumbers
    myEntity["select"] = mySelects
    myJson["entity"] = myEntity

    # iterate over all devices in order to create a translation. TODO
    # for key, value in asdict(DeviceConstants).items():
    #    ...

    # load strings.json into string
    # replaced Path.open by open
    with Path("config/custom_components/weishaupt_modbus/strings.json").open(
        encoding="utf-8"
    ) as file:
        data = file.read()
    # create dict from json
    data_dict = json.loads(data)
    # overwrite entity dict
    data_dict["entity"] = myEntity
    # write whole json to file again
    # replaced Path.open by open
    with Path("config/custom_components/weishaupt_modbus/strings.json").open(
        mode="w",
        encoding="utf-8",
    ) as file:
        file.write(json.dumps(data_dict, indent=4, sort_keys=True, ensure_ascii=False))
