"""Setting up sensor entities."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry
from .modbus.descriptions.all import get_entities
from .modbus.descriptions.description import SensorDescription
from .modbus.entities import WeishauptSensor
from .webif.description.all import get_webif_entities
from .webif.description.description import WebifSensorDescription
from .webif.entity import WebifSensor

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""

    weishaupt_coordinator = config_entry.runtime_data.weishaupt_coordinator

    for description in get_entities(config_entry):
        if isinstance(description, SensorDescription):
            entity = WeishauptSensor(
                weishaupt_coordinator,
                description,
                config_entry,
            )

            async_add_entities([entity])

    webif_coordinator = config_entry.runtime_data.webif_coordinator
    if webif_coordinator is not None:
        webif_entities = get_webif_entities(config_entry)
        for description in webif_entities:
            if isinstance(description, WebifSensorDescription):
                entity = WebifSensor(
                    webif_coordinator,
                    description,
                    config_entry,
                )
                async_add_entities([entity])
