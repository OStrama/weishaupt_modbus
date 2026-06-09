"""Setting up sensor entities."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry
from .const import CONF, TYPES
from .coordinator import MyWebIfCoordinator
from .entities import MyWebifSensorEntity
from .entity_helpers import build_entity_list, build_webif_entity_list
from .hpconst import WEBIF_INFO_HEIZKREIS1

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    # start with an empty list of entries
    entries: list[Any] = []

    # we create one communicator per integration only for better performance and to allow dynamic parameters
    coordinator = config_entry.runtime_data.coordinator
    webif_coordinator = config_entry.runtime_data.webif_coordinator

    entries = await build_entity_list(
        entries=entries,
        config_entry=config_entry,
        api_items=coordinator.modbus_items,
        item_types=(TYPES.NUMBER_RO, TYPES.SENSOR_CALC, TYPES.SENSOR),
        coordinator=coordinator,
    )

    webifentries = []

    # if config_entry.data[CONF.CB_WEBIF]:
    #    webifcoordinator = MyWebIfCoordinator(hass=hass, config_entry=config_entry)
    #    for webifitem in WEBIF_INFO_HEIZKREIS1:
    #        webifentries.append(  # noqa: PERF401
    #            MyWebifSensorEntity(
    #                config_entry=config_entry,
    #                api_item=webifitem,
    #                coordinator=webifcoordinator,
    #                idx=1,
    #            )
    #        )
    #    entries.extend(webifentries)

    webif_entries = await build_webif_entity_list(
        entries=entries,
        config_entry=config_entry,
        api_items=webif_coordinator.api_items,
        item_type=(TYPES.SENSOR),
        coordinator=webif_coordinator,
    )

    # entries.extend(webifentries)

    async_add_entities(
        entries,
        update_before_add=True,
    )
