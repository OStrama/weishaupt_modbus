"""Select."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .configentry import MyConfigEntry
from .const import TYPES
from .entity_helpers import build_entity_list
from .hpconst import DEVICELISTS


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: MyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Select entry setup."""
    _useless = hass
    # start with an empty list of entries
    entries = []

    # we create one communicator per integration only for better performance and to allow dynamic parameters
    coordinator = config_entry.runtime_data.coordinator

    for device in DEVICELISTS:
        entries = await build_entity_list(
            entries=entries,
            config_entry=config_entry,
            api_items=device,
            item_type=TYPES.SELECT,
            coordinator=coordinator,
        )

    async_add_entities(
        entries,
        update_before_add=True,
    )
