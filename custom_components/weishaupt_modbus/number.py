"""Number."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry
from .modbus.descriptions.all import get_entities
from .modbus.descriptions.description import NumberDescription
from .modbus.entities import WeishauptNumber

PARALLEL_UPDATES = 1


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
