"""Setting up sensor entities."""

import logging

from config.custom_components.weishaupt_modbus.descriptions.all import ENTITIES
from config.custom_components.weishaupt_modbus.descriptions.description import (
    SensorDescription,
)
from config.custom_components.weishaupt_modbus.entities import WeishauptSensor
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    weishaupt_coordinator = config_entry.runtime_data.weishaupt_coordinator

    for description in ENTITIES:
        if isinstance(description, SensorDescription):
            entity = WeishauptSensor(
                weishaupt_coordinator,
                description,
                config_entry,
            )

            async_add_entities([entity])
