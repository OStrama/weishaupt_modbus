"""Setting uop my sensor entities."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry
from .const import CONF, TypeConstants
from .coordinator import MyWebIfCoordinator
from .entities import MyWebifSensorEntity
from .entity_helpers import build_entity_list
from .hpconst import DEVICELISTS, WEBIF_INFO_HEIZKREIS1

logging.basicConfig()
log: logging.Logger = logging.getLogger(name=__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    # start with an empty list of entries
    entries = []

    # we create one communicator per integration only for better performance and to allow dynamic parameters
    coordinator = config_entry.runtime_data.coordinator

    for device in DEVICELISTS:
        entries = await build_entity_list(
            entries=entries,
            config_entry=config_entry,
            api_items=device,
            item_type=TypeConstants.NUMBER_RO,
            coordinator=coordinator,
        )
        entries = await build_entity_list(
            entries=entries,
            config_entry=config_entry,
            api_items=device,
            item_type=TypeConstants.SENSOR_CALC,
            coordinator=coordinator,
        )

        # Webif Sensors here
        entries = await build_entity_list(
            entries=entries,
            config_entry=config_entry,
            api_items=device,
            item_type=TypeConstants.SENSOR,
            coordinator=coordinator,
        )

    webifentries = []

    if config_entry.data[CONF.CB_WEBIF]:
        webifcoordinator = MyWebIfCoordinator(hass=hass, config_entry=config_entry)
        for webifitem in WEBIF_INFO_HEIZKREIS1:
            webifentries.append(  # noqa: PERF401
                MyWebifSensorEntity(
                    config_entry=config_entry,
                    api_item=webifitem,
                    coordinator=webifcoordinator,
                    idx=1,
                )
            )
        entries = entries + webifentries

    async_add_entities(
        entries,
        update_before_add=True,
    )
