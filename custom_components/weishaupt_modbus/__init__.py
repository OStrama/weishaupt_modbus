"""Home Assistant integration initialization."""

import asyncio
import logging
from typing import TYPE_CHECKING

from homeassistant.components.modbus.connection import ModbusTcpParams, async_get_unit
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .configentry import MyData
from .migrate_helpers import migrate_entities
from .modbus.coordinator import WeishauptCoordinator
from .modbus.weishaupt_modbus_client.model.device import Weishaupt
from .webif.coordinator import WeishauptWebifCoordinator
from .webif.description.description import WebifConnection

if TYPE_CHECKING:
    from .configentry import MyConfigEntry

from .const import CONF, CONST
from .kennfeld.kennfeld import PowerMap

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = [
    "number",
    "select",
    "sensor",
    #    "switch",
]


async def async_setup_entry(hass: HomeAssistant, entry: MyConfigEntry) -> bool:
    """Set up entry."""
    if entry.data.get(CONF.MAC) == "CHANGEME":
        _LOGGER.error("MAC Address not set. Reconfigure integration and set MAC")
        _LOGGER.error(
            "In case you need help: https://github.com/OStrama/weishaupt_modbus"
        )
        return False

    if not entry.data.get(CONF.UID_MIGRATION, False):
        migrate_entities(entry, hass)

        hass.config_entries.async_update_entry(
            entry,
            data={
                **entry.data,
                CONF.UID_MIGRATION: True,
            },
        )

    mcu_lock = asyncio.Lock()

    webif_coordinator = None

    if entry.data.get(CONF.CB_WEBIF):
        webif_api = WebifConnection(
            ip=entry.data[CONF.HOST],
            user=entry.data[CONF.USERNAME],
            password=entry.data[CONF.PASSWORD],
        )

        webif_coordinator = WeishauptWebifCoordinator(
            hass=hass,
            api=webif_api,
            entry=entry,
            mcu_lock=mcu_lock,
        )

        await webif_coordinator.async_config_entry_first_refresh()
    else:
        webif_api = None
    readings = [
        "system",
        "heat_pump",
        "heating_circuit",
        "domestic_hot_water",
        "second_heat_source",
        "statistics",
        "io",
    ]
    if entry.data.get(CONF.HK2, False) is True:
        readings.append("heating_circuit2")
    if entry.data.get(CONF.HK3, False) is True:
        readings.append("heating_circuit3")
    if entry.data.get(CONF.HK4, False) is True:
        readings.append("heating_circuit4")
    if entry.data.get(CONF.HK5, False) is True:
        readings.append("heating_circuit5")

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
    device = Weishaupt(unit, readings)
    weishaupt_coordinator = WeishauptCoordinator(
        hass=hass,
        # entry=entry,
        device=device,
        # interval=timedelta(seconds=30),
        mcu_lock=mcu_lock,
    )
    await weishaupt_coordinator.async_config_entry_first_refresh()

    entry.runtime_data = MyData(
        config_dir=hass.config.config_dir,
        hass=hass,
        powermap=None,
        weishaupt_coordinator=weishaupt_coordinator,
        webif_api=webif_api,
        webif_coordinator=webif_coordinator,
        mcu_lock=mcu_lock,
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
        _LOGGER.warning("Version <5 detected")
        new_data[CONF.CB_WEBIF] = False
        new_data[CONF.USERNAME] = ""
        new_data[CONF.PASSWORD] = ""
        new_data[CONF.WEBIF_TOKEN] = ""
        hass.config_entries.async_update_entry(
            config_entry, data=new_data, minor_version=1, version=5
        )
    if config_entry.version < 7:
        _LOGGER.warning("Version <7 detected")
        new_data[CONF.CB_WEBIF_MOCKUP_DATA] = False
    if config_entry.version < 8:
        _LOGGER.warning("Version <8 detected")
        new_data[CONF.CB_WEBIF_HK1] = False
        new_data[CONF.CB_WEBIF_HK2] = False
        new_data[CONF.CB_WEBIF_HK3] = False
        new_data[CONF.CB_WEBIF_HK4] = False
        new_data[CONF.CB_WEBIF_HK5] = False
        new_data[CONF.CB_WEBIF_WP] = False
        new_data[CONF.CB_WEBIF_2WEZ] = False
        new_data[CONF.CB_WEBIF_SATISTICS] = False

    hass.config_entries.async_update_entry(
        config_entry, data=new_data, minor_version=1, version=8
    )
    _LOGGER.warning("Config entries updated to version 8")

    if config_entry.version < 9:
        _LOGGER.warning("Version <9 detected")
        new_data[CONF.MAC] = "CHANGEME"

    hass.config_entries.async_update_entry(
        config_entry, data=new_data, minor_version=1, version=9
    )
    _LOGGER.warning("Config entries updated to version 9")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload entry."""
    if entry.runtime_data.webif_api is not None:
        await entry.runtime_data.webif_api.close()

    return await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )
