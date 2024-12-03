"""Build entitiy List and Update Coordinator."""

import logging
from .configentry import MyConfigEntry
from .items import ModbusItem, WebItem
from .modbusobject import ModbusObject
from .const import DEVICES, CONF, TYPES
from .coordinator import MyCoordinator
from .entities import MySensorEntity, MyCalcSensorEntity, MyNumberEntity, MySelectEntity

logging.basicConfig()
log = logging.getLogger(__name__)


async def check_available(modbus_item: ModbusItem, config_entry: MyConfigEntry) -> bool:
    """function checks if item is valid and available

    :param config_entry: HASS config entry
    :type config_entry: MyConfigEntry
    :param modbus_item: definition of modbus item
    :type modbus_item: ModbusItem
    """
    log.debug("Check if item %s is available ..", modbus_item.translation_key)
    if config_entry.data[CONF.HK2] is False:
        if modbus_item.device is DEVICES.HZ2:
            return False

    if config_entry.data[CONF.HK3] is False:
        if modbus_item.device is DEVICES.HZ3:
            return False

    if config_entry.data[CONF.HK4] is False:
        if modbus_item.device is DEVICES.HZ4:
            return False

    if config_entry.data[CONF.HK5] is False:
        if modbus_item.device is DEVICES.HZ5:
            return False

    _modbus_api = config_entry.runtime_data.modbus_api
    mbo = ModbusObject(_modbus_api, modbus_item)
    _useless = await mbo.value
    if modbus_item.is_invalid is False:
        log.debug("Check availability item %s successful ..", modbus_item.translation_key)
        return True
    return False


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
                log.debug("Add item %s to entity list ..", item.translation_key)
                match item_type:
                    # here the entities are created with the parameters provided
                    # by the ModbusItem object
                    case TYPES.SENSOR | TYPES.NUMBER_RO:
                        log.debug("Add item %s to entity list ..", item.translation_key)
                        entries.append(
                            MySensorEntity(config_entry, item, coordinator, index)
                        )
                    case TYPES.SENSOR_CALC:
                        log.debug("Add item %s to entity list ..", item.translation_key)
                        entries.append(
                            MyCalcSensorEntity(
                                config_entry,
                                item,
                                coordinator,
                                index,
                            )
                        )
                    case TYPES.SELECT:
                        log.debug("Add item %s to entity list ..", item.translation_key)
                        entries.append(
                            MySelectEntity(config_entry, item, coordinator, index)
                        )
                    case TYPES.NUMBER:
                        log.debug("Add item %s to entity list ..", item.translation_key)
                        entries.append(
                            MyNumberEntity(config_entry, item, coordinator, index)
                        )

    return entries
