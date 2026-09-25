"""Number."""

from __future__ import annotations

from typing import Any

from config.custom_components.weishaupt_modbus.descriptions.all import (
    get_entities,
)
from config.custom_components.weishaupt_modbus.descriptions.description import (
    NumberDescription,
)
from config.custom_components.weishaupt_modbus.entities import WeishauptNumber
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry
from .const import TYPES


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""

    weishaupt_coordinator = config_entry.runtime_data.weishaupt_coordinator

    for description in get_entities(config_entry):
        if isinstance(description, NumberDescription):
            entity = WeishauptNumber(
                weishaupt_coordinator,
                description,
                config_entry,
            )

            async_add_entities([entity])
