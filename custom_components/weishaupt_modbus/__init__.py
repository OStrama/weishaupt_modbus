"""Home Assistant integration initialization."""

import asyncio
import copy
from datetime import timedelta
import logging
from typing import TYPE_CHECKING

from weishaupt_webif_api import WebifConnection

from config.custom_components.weishaupt_modbus.weishaupt_modbus_api.modbus_api import (
    WeishauptModbusClient,
)
from homeassistant.components.modbus.connection import ModbusTcpParams, async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .configentry import MyData
from .coordinator import WeishauptCoordinator
from .translations import update_translation
from .weishaupt_modbus_client.model.device import Weishaupt

if TYPE_CHECKING:
    from .configentry import MyConfigEntry

from .const import CONF, CONST, DEVICENAMES
from .coordinator import MyWebIfCoordinator, WeishauptModbusCoordinator
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
    WEBIF_INFO_2WEZ,
    WEBIF_INFO_HEIZKREIS1,
    WEBIF_INFO_STATISTIK,
    WEBIF_INFO_WAERMEPUMPE,
)
from .items import ModbusItem, WebItem
from .kennfeld import PowerMap

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = [
    "number",
    "select",
    "sensor",
    #    "switch",
]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up entry."""
    # Create independent copies of ModbusItems for each config entry

    params = ModbusTcpParams(
        host=entry.data[CONF.HOST],
        port=entry.data[CONF.PORT],
    )
    # New modbus-connection based device/coordinator.
    unit = async_get_unit(
        hass,
        entry,
        params,
        1,
    )
    device = Weishaupt(unit)
    weishaupt_coordinator = WeishauptCoordinator(
        hass=hass,
        # entry=entry,
        device=device,
        # interval=timedelta(seconds=30),
    )
    await weishaupt_coordinator.async_config_entry_first_refresh()

    entry.runtime_data = MyData(
        config_dir=hass.config.config_dir,
        hass=hass,
        powermap=None,
        weishaupt_coordinator=weishaupt_coordinator,
    )

    powermap = PowerMap(entry, hass)
    await powermap.initialize()
    entry.runtime_data.powermap = powermap

    # see https://community.home-assistant.io/t/config-flow-how-to-update-an-existing-entity/522442/8
    entry.async_on_unload(entry.add_update_listener(update_listener))

    # This is used to generate a strings.json file from hpconst.py

    # update_translation()

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("Init done")
    for state in hass.states.async_all("sensor"):
        unit = state.attributes.get("unit_of_measurement")

        if not isinstance(unit, (str, type(None))):
            _LOGGER.error(
                "INVALID GLOBAL SENSOR UNIT: %s -> %r (%s), attributes=%r",
                state.entity_id,
                unit,
                type(unit).__name__,
                state.attributes,
            )

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(
        entry.entry_id
    )  # list of entry_ids created for file


async def async_migrate_entry(hass: HomeAssistant, config_entry: MyConfigEntry) -> bool:
    """Migrate old entry."""

    new_data = {**config_entry.data}
    _LOGGER.warning(
        "Starting config migration process. Current version: %s", config_entry.version
    )

    if config_entry.version < 1:
        _LOGGER.warning("Version <1 detected")

    hass.config_entries.async_update_entry(
        config_entry, data=new_data, minor_version=1, version=2
    )
    _LOGGER.warning("Config entries updated to version 2")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    entry.runtime_data.modbus_api.close()
    if entry.runtime_data.webif_api is not None:
        await entry.runtime_data.webif_api.close()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        try:
            hass.data[entry.data[CONF.PREFIX]].pop(entry.entry_id)
        except KeyError:
            _LOGGER.warning("KeyError: %s", str(entry.data[CONF.PREFIX]))

    return unload_ok
