"""Build entity List and Update Coordinator."""

import logging
from typing import Union

from homeassistant.helpers.entity import Entity

from .configentry import MyConfigEntry
from .const import TypeConstants
from .coordinator import MyCoordinator, check_configured
from .entities import MyCalcSensorEntity, MyNumberEntity, MySelectEntity, MySensorEntity
from .items import ModbusItem, WebItem
from .modbusobject import ModbusObject

logging.basicConfig()
log = logging.getLogger(__name__)


async def check_available(modbus_item: ModbusItem, config_entry: MyConfigEntry) -> bool:
    """Check if item is valid and available.

    :param config_entry: HASS config entry
    :type config_entry: MyConfigEntry
    :param modbus_item: definition of modbus item
    :type modbus_item: ModbusItem
    """
    if await check_configured(modbus_item, config_entry) is False:
        return False

    _modbus_api = config_entry.runtime_data.modbus_api
    if _modbus_api is None:
        log.error("Modbus API is not initialized.")
        return False
    mbo = ModbusObject(_modbus_api, modbus_item, no_connect_warn=True)
    _useless = await mbo.value
    return modbus_item.is_invalid is False


async def build_entity_list(
    entries: list[Entity],
    config_entry: MyConfigEntry,
    api_items: list[Union[ModbusItem, WebItem]],
    item_type: TypeConstants,
    coordinator: MyCoordinator,
) -> list[Entity]:
    """Build entity list.

    function builds a list of entities that can be used as parameter by async_setup_entry()
    type of list is defined by the ModbusItem's type flag
    so the app only holds one list of entities that is build from a list of ModbusItem
    stored in hpconst.py so far, will be provided by an external file in future

    :param config_entry: HASS config entry
    :type config_entry: MyConfigEntry
    :param modbus_item: definition of modbus item
    :type modbus_item: ModbusItem
    :param item_type: type of modbus item
    :type item_type: TypeConstants
    :param coordinator: the update coordinator
    :type coordinator: MyCoordinator
    """

    for index, item in enumerate(api_items):
        if item.type == item_type:
            if isinstance(item, ModbusItem):
                if await check_available(item, config_entry=config_entry) is True:
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
