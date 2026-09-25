"""Select."""

from config.custom_components.weishaupt_modbus.descriptions.all import (
    get_entities,
)
from config.custom_components.weishaupt_modbus.descriptions.description import (
    SelectDescription,
)
from config.custom_components.weishaupt_modbus.entities import WeishauptSelect
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""

    weishaupt_coordinator = config_entry.runtime_data.weishaupt_coordinator

    for description in get_entities(config_entry):
        if isinstance(description, SelectDescription):
            entity = WeishauptSelect(
                weishaupt_coordinator,
                description,
                config_entry,
            )

            async_add_entities([entity])
