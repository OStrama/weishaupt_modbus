"""Helpers for entity migration."""

from dataclasses import dataclass
import logging
from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from .const import CONF

if TYPE_CHECKING:
    from .configentry import MyConfigEntry


_LOGGER = logging.getLogger(__name__)


def old_unique_id(postfix: str, prefix: str, old_name: str) -> str:
    """Create an UID according to old style."""
    dev_postfix = f"_{postfix}"

    if dev_postfix == "_":
        dev_postfix = ""

    return f"{prefix}{old_name}{dev_postfix}"


def new_unique_id(base_id: str, mac: str) -> str:
    """Create an UID according to new style."""
    return f"{mac}_{base_id}"


def migrate_entities(config_entry: MyConfigEntry, hass: HomeAssistant) -> None:

    _LOGGER.info("Starting entity migration!")

    postfix = config_entry.data.get(CONF.DEVICE_POSTFIX)
    prefix = config_entry.data.get(CONF.NAME_DEVICE_PREFIX)

    mac = config_entry.data.get(CONF.MAC)
    if mac == "CHANGEME":
        return

    entity_registry = er.async_get(hass)
    unique_id_migrations: dict[str, str] = {}
    for item in OLD_MODBUS_SYS_ITEMS:
        old_uid = old_unique_id(postfix, prefix, item.name)
        new_uid = new_unique_id(item.new_key, mac)
        unique_id_migrations[old_uid] = new_uid

    entities = entity_registry.entities.get_entries_for_config_entry_id(
        config_entry.entry_id
    )

    for entity in entities:
        new_uid = unique_id_migrations.get(entity.unique_id)
        if new_uid is None:
            continue

        old_uid = entity.unique_id

        entity_registry.async_update_entity(
            entity.entity_id,
            new_unique_id=new_uid,
        )

        _LOGGER.info(
            "Changed old UID: %s to new UID: %s",
            old_uid,
            new_uid,
        )


@dataclass(frozen=True)
class OldModbusItem:
    """Legacy Modbus item for entity migration."""

    name: str
    new_key: str


OLD_MODBUS_SYS_ITEMS: tuple[OldModbusItem, ...] = (
    OldModbusItem(
        name="Aussentemperatur",
        new_key="system_outside_temperature",
    ),
    OldModbusItem(
        name="Luftansaugtemperatur",
        new_key="system_intake_temperature",
    ),
    OldModbusItem(
        name="Fehler",
        new_key="system_error",
    ),
    OldModbusItem(
        name="Warnung",
        new_key="system_warning",
    ),
    OldModbusItem(
        name="Fehlerfrei",
        new_key="system_error_free",
    ),
    OldModbusItem(
        name="Betriebsanzeige",
        new_key="system_operating_display",
    ),
    OldModbusItem(
        name="Systembetriebsart",
        new_key="system_operating_mode",
    ),
    OldModbusItem(
        name="SollwertPV",
        new_key="system_pv_setpoint",
    ),
)
