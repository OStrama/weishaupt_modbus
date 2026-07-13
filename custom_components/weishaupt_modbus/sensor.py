"""Setting up sensor entities."""

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry
from .const import TYPES
from .entity_helpers import build_entity_list, build_webif_entity_list

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    # we create one communicator per integration only for better performance and to allow dynamic parameters
    coordinator = config_entry.runtime_data.coordinator
    webif_coordinator = config_entry.runtime_data.webif_coordinator

    # Add the Modbus sensors on their own, before and independently of the
    # optional WebIF sensors, so that a problem while setting up the WebIF
    # sensors can never prevent the Modbus sensors from being registered
    # (issue #172).
    if coordinator is not None:
        modbus_entries: list[Any] = await build_entity_list(
            entries=[],
            config_entry=config_entry,
            api_items=coordinator.modbus_items,
            item_types=(TYPES.NUMBER_RO, TYPES.SENSOR_CALC, TYPES.SENSOR),
            coordinator=coordinator,
        )
        async_add_entities(
            modbus_entries,
            update_before_add=True,
        )

    if webif_coordinator is not None:
        try:
            webif_entries: list[Any] = await build_webif_entity_list(
                entries=[],
                config_entry=config_entry,
                api_items=webif_coordinator.api_items,
                item_type=(TYPES.SENSOR),
                coordinator=webif_coordinator,
            )
            async_add_entities(
                webif_entries,
                update_before_add=False,
            )
        except Exception:
            _LOGGER.exception(
                "Setting up WebIF sensors failed; Modbus sensors are not affected"
            )
