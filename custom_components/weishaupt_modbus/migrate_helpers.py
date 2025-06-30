"""Helpers for entity migration."""

import logging

from homeassistant.core import callback
from homeassistant.helpers import entity_registry as er
from homeassistant.util import slugify

from .configentry import MyConfigEntry
from .const import CONF, CONST, TypeConstants
from .hpconst import reverse_device_list
from .items import ModbusItem

logging.basicConfig()
log = logging.getLogger(__name__)


def create_new_entity_id(
    config_entry: MyConfigEntry, modbus_item: ModbusItem, platform: str, device: str
):
    """Create an entity ID according to new style."""
    dev_postfix = "_" + config_entry.data[CONF.DEVICE_POSTFIX]
    if dev_postfix == "_":
        dev_postfix = ""

    device_name = device + dev_postfix

    if config_entry.data[CONF.NAME_DEVICE_PREFIX]:
        name_device_prefix = CONST.DEF_PREFIX + "_"
    else:
        name_device_prefix = ""

    if config_entry.data[CONF.NAME_TOPIC_PREFIX]:
        name_topic_prefix = reverse_device_list[modbus_item.device] + "_"
    else:
        name_topic_prefix = ""

    entity_name = name_topic_prefix + name_device_prefix + modbus_item.name

    return str(platform + "." + slugify(device_name + "_" + entity_name))


def create_unique_id(config_entry: MyConfigEntry, modbus_item: ModbusItem):
    """Create an UID according to old style."""
    dev_postfix = "_" + config_entry.data[CONF.DEVICE_POSTFIX]

    if dev_postfix == "_":
        dev_postfix = ""

    return str(config_entry.data[CONF.PREFIX] + modbus_item.name + dev_postfix)


@callback
def migrate_entities(
    config_entry: MyConfigEntry,
    modbusitems: ModbusItem,
    device: str,
):
    """Build entity list.

    function builds a list of entities that can be used as parameter by async_setup_entry()
    type of list is defined by the ModbusItem's type flag
    so the app only holds one list of entities that is build from a list of ModbusItem
    stored in hpconst.py so far, will be provided by an external file in future
    """
    # return

    entity_registry = er.async_get(config_entry.runtime_data.hass)

    for _useless, item in enumerate(modbusitems):
        platform = ""
        match item.type:
            case TypeConstants.SENSOR | TypeConstants.NUMBER_RO | TypeConstants.SENSOR_CALC:
                platform = "sensor"
            case TypeConstants.SELECT:
                platform = "select"
            case TypeConstants.NUMBER:
                platform = "number"

        old_uid = create_unique_id(config_entry, item)
        new_entity_id = create_new_entity_id(config_entry, item, platform, device)
        old_entity_id = entity_registry.async_get_entity_id(
            platform, CONST.DOMAIN, old_uid
        )

        if new_entity_id == old_entity_id:
            log.info("already migrated %s", old_entity_id)
            return

        if old_entity_id is not None:
            try:
                entity_registry.async_update_entity(
                    old_entity_id,
                    new_entity_id=new_entity_id,
                )

                log.info(
                    "Init UID:%s, platform:%s old ID:%s new ID:%s",
                    old_uid,
                    platform,
                    old_entity_id,
                    new_entity_id,
                )
            except KeyError as key:
                log.warning(
                    "Exception %s old UID:%s, platform:%s old ID:%s new ID:%s",
                    str(key),
                    old_uid,
                    platform,
                    old_entity_id,
                    new_entity_id,
                )
