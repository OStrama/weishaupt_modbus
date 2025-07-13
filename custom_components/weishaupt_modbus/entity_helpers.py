"""Build entity List and Update Coordinator."""

from __future__ import annotations

import logging

from .configentry import MyConfigEntry
from .const import TypeConstants
from .coordinator import MyCoordinator, MyWebIfCoordinator, check_configured
from .entities import (
    MyCalcSensorEntity,
    MyNumberEntity,
    MySelectEntity,
    MySensorEntity,
    MyWebifSensorEntity,
)
from .items import ModbusItem, WebItem
from .modbusobject import ModbusObject

_LOGGER = logging.getLogger(__name__)

# Type alias for entity types
EntityType = (
    MySensorEntity
    | MyCalcSensorEntity
    | MySelectEntity
    | MyNumberEntity
    | MyWebifSensorEntity
)


async def check_available(
    api_item: ModbusItem | WebItem, config_entry: MyConfigEntry
) -> bool:
    """Check if item is valid and available.

    Args:
        api_item: definition of modbus or web item
        config_entry: HASS config entry

    Returns:
        True if item is available, False otherwise

    """
    # WebItem doesn't need configuration check
    if isinstance(api_item, WebItem):
        return True

    # For ModbusItem, check configuration
    if await check_configured(api_item, config_entry) is False:
        return False

    modbus_api = config_entry.runtime_data.modbus_api
    mbo = ModbusObject(modbus_api, api_item, no_connect_warn=True)
    _ = await mbo.value
    return api_item.is_invalid is False


async def build_entity_list(
    entries: list[EntityType],
    config_entry: MyConfigEntry,
    api_items: list[ModbusItem | WebItem],
    item_type: TypeConstants,
    coordinator: MyCoordinator,
) -> list[EntityType]:
    """Build entity list.

    Function builds a list of entities that can be used as parameter by async_setup_entry().
    Type of list is defined by the ModbusItem's type flag.
    So the app only holds one list of entities that is built from a list of ModbusItem
    stored in hpconst.py so far, will be provided by an external file in future.

    Args:
        entries: list of entities to append to
        config_entry: HASS config entry
        api_items: list of modbus/web items
        item_type: type of modbus item
        coordinator: the update coordinator

    Returns:
        Updated list of entities

    """
    for index, item in enumerate(api_items):
        if item.type == item_type:
            if await check_available(item, config_entry=config_entry) is True:
                # Only process ModbusItem with the regular entities
                # WebItem should be handled separately with MyWebifSensorEntity
                if isinstance(item, ModbusItem):
                    match item_type:
                        # here the entities are created with the parameters provided
                        # by the ModbusItem object
                        case TypeConstants.SENSOR | TypeConstants.NUMBER_RO:
                            entries.append(
                                MySensorEntity(config_entry, item, coordinator, index)
                            )
                        case TypeConstants.SENSOR_CALC:
                            entries.append(
                                MyCalcSensorEntity(
                                    config_entry,
                                    item,
                                    coordinator,
                                    index,
                                )
                            )
                        case TypeConstants.SELECT:
                            entries.append(
                                MySelectEntity(config_entry, item, coordinator, index)
                            )
                        case TypeConstants.NUMBER:
                            entries.append(
                                MyNumberEntity(config_entry, item, coordinator, index)
                            )

    return entries


async def build_webif_entity_list(
    entries: list[MyWebifSensorEntity],
    config_entry: MyConfigEntry,
    api_items: list[WebItem],
    item_type: TypeConstants,
    coordinator: MyWebIfCoordinator,
) -> list[MyWebifSensorEntity]:
    """Build WebIF entity list.

    Function builds a list of WebIF entities that can be used as parameter by async_setup_entry().
    Type of list is defined by the WebItem's type flag.

    Args:
        entries: list of entities to append to
        config_entry: HASS config entry
        api_items: list of web items
        item_type: type of web item
        coordinator: the WebIF update coordinator

    Returns:
        Updated list of WebIF entities

    """
    for index, item in enumerate(api_items):
        if item.type == item_type:
            if await check_available(item, config_entry=config_entry) is True:
                match item_type:
                    case TypeConstants.SENSOR | TypeConstants.NUMBER_RO:
                        entries.append(
                            MyWebifSensorEntity(config_entry, item, coordinator, index)
                        )
                    # Add other WebIF entity types as needed

    return entries
