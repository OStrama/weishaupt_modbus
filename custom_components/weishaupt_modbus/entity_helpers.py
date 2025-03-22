"""Build entity List and Update Coordinator."""

import logging

from .configentry import MyConfigEntry
from .const import TYPES
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
    mbo = ModbusObject(_modbus_api, modbus_item)
    _useless = await mbo.value
    return modbus_item.is_invalid is False


async def build_entity_list(
    entries,
    config_entry: MyConfigEntry,
    api_items: ModbusItem | WebItem,
    item_type,
    coordinator: MyCoordinator,
):
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
    :type item_type: TYPES
    :param coordinator: the update coordinator
    :type coordinator: MyCoordinator
    """

    for index, item in enumerate(api_items):
        if item.type == item_type:
            if await check_available(item, config_entry=config_entry) is True:
                match item_type:
                    # here the entities are created with the parameters provided
                    # by the ModbusItem object
                    case TYPES.SENSOR | TYPES.NUMBER_RO:
                        entries.append(
                            MySensorEntity(config_entry, item, coordinator, index)
                        )
                    case TYPES.SENSOR_CALC:
                        entries.append(
                            MyCalcSensorEntity(
                                config_entry,
                                item,
                                coordinator,
                                index,
                            )
                        )
                    case TYPES.SELECT:
                        entries.append(
                            MySelectEntity(config_entry, item, coordinator, index)
                        )
                    case TYPES.NUMBER:
                        entries.append(
                            MyNumberEntity(config_entry, item, coordinator, index)
                        )

    return entries
