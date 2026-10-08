"""Tests for migration helpers."""

from unittest.mock import MagicMock, patch

from custom_components.weishaupt_modbus.migrate_helpers import (
    DELETIONS,
    DEVICE_MIGRATIONS,
    HZ_UID_MAPPINGS,
    MIGRATION,
    migrate_entities,
    new_unique_id,
    old_device_identifier,
    old_unique_id,
    remove_heating_circuit_entities,
)

from config.custom_components.weishaupt_modbus.const import CONF, CONST


def test_old_unique_id() -> None:
    """Test legacy unique ID generation."""
    assert old_unique_id(None, None, "Sensor") == "Sensor"
    assert old_unique_id("", "", "Sensor") == "Sensor"
    assert old_unique_id("device", "prefix", "Sensor") == "prefixSensor_device"
    assert old_unique_id(None, "prefix", "Sensor") == "prefixSensor"
    assert old_unique_id("device", None, "Sensor") == "Sensor_device"


def test_new_unique_id() -> None:
    """Test new unique ID generation."""
    assert new_unique_id("system_temperature", "AA:BB:CC:DD:EE:FF") == (
        "AA:BB:CC:DD:EE:FF_system_temperature"
    )


def test_old_device_identifier() -> None:
    """Test legacy device identifier generation."""
    assert old_device_identifier("device", None) == "device"
    assert old_device_identifier("device", "") == "device"
    assert old_device_identifier("device", "suffix") == "device_suffix"


def test_remove_heating_circuit_entities() -> None:
    """Test removal list for inactive heating circuits."""
    config_entry = MagicMock()
    config_entry.data = {
        CONF.HK2: False,
        CONF.HK3: False,
        CONF.HK4: False,
        CONF.HK5: False,
    }

    result = remove_heating_circuit_entities(config_entry, MagicMock())

    assert len(result) == len(HZ_UID_MAPPINGS) * 4

    assert "Raumsolltemperatur2" in result
    assert "Raumsolltemperatur3" in result
    assert "Raumsolltemperatur4" in result
    assert "Raumsolltemperatur5" in result


def test_remove_heating_circuit_entities_active() -> None:
    """Test that active heating circuits are not removed."""
    config_entry = MagicMock()
    config_entry.data = {
        CONF.HK2: True,
        CONF.HK3: True,
        CONF.HK4: True,
        CONF.HK5: True,
    }

    assert remove_heating_circuit_entities(config_entry, MagicMock()) == ()


def test_migrate_entities_with_placeholder_mac() -> None:
    """Test that migration is skipped without a valid MAC."""
    config_entry = MagicMock()
    config_entry.data = {
        CONF.MAC: "CHANGEME",
    }

    hass = MagicMock()

    with (
        patch(
            "custom_components.weishaupt_modbus.migrate_helpers.er.async_get"
        ) as entity_get,
        patch(
            "custom_components.weishaupt_modbus.migrate_helpers.dr.async_get"
        ) as device_get,
    ):
        migrate_entities(config_entry, hass)

    entity_get.assert_not_called()
    device_get.assert_not_called()


def test_migrate_entities() -> None:
    """Test entity migration and deletion."""
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry"
    config_entry.data = {
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
        CONF.PREFIX: "weishaupt_",
        CONF.DEVICE_POSTFIX: "",
        CONF.HK2: True,
        CONF.HK3: True,
        CONF.HK4: True,
        CONF.HK5: True,
    }

    first_migration = MIGRATION[0]

    migrated_entity = MagicMock()
    migrated_entity.entity_id = "sensor.migrated"
    migrated_entity.unique_id = old_unique_id(
        config_entry.data[CONF.DEVICE_POSTFIX],
        config_entry.data[CONF.PREFIX],
        first_migration.name,
    )

    deleted_entity = MagicMock()
    deleted_entity.entity_id = "sensor.deleted"
    deleted_entity.unique_id = old_unique_id(
        config_entry.data[CONF.DEVICE_POSTFIX],
        config_entry.data[CONF.PREFIX],
        DELETIONS[0],
    )

    untouched_entity = MagicMock()
    untouched_entity.entity_id = "sensor.untouched"
    untouched_entity.unique_id = "something_else"

    entity_registry = MagicMock()
    entity_registry.entities.get_entries_for_config_entry_id.return_value = [
        migrated_entity,
        deleted_entity,
        untouched_entity,
    ]

    device_registry = MagicMock()
    device_registry.async_get_device_by_identifier.return_value = None

    hass = MagicMock()

    with (
        patch(
            "custom_components.weishaupt_modbus.migrate_helpers.er.async_get",
            return_value=entity_registry,
        ),
        patch(
            "custom_components.weishaupt_modbus.migrate_helpers.dr.async_get",
            return_value=device_registry,
        ),
    ):
        migrate_entities(config_entry, hass)

    entity_registry.async_update_entity.assert_called_once_with(
        "sensor.migrated",
        new_unique_id=new_unique_id(
            first_migration.new_key,
            "AA:BB:CC:DD:EE:FF",
        ),
    )

    entity_registry.async_remove.assert_called_once_with("sensor.deleted")


def test_migrate_entities_devices() -> None:
    """Test device migration."""
    config_entry = MagicMock()
    config_entry.entry_id = "test_entry"
    config_entry.data = {
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
        CONF.PREFIX: "weishaupt_",
        CONF.DEVICE_POSTFIX: "",
        CONF.HK2: False,
        CONF.HK3: True,
        CONF.HK4: True,
        CONF.HK5: True,
    }

    entity_registry = MagicMock()
    entity_registry.entities.get_entries_for_config_entry_id.return_value = []

    device_registry = MagicMock()

    devices = {
        DEVICE_MIGRATIONS[0].old_device: MagicMock(id="system_device"),
        DEVICE_MIGRATIONS[3].old_device: MagicMock(id="hk1_device"),
        DEVICE_MIGRATIONS[4].old_device: MagicMock(id="hk2_device"),
    }

    def get_device(identifiers, config_entry_id):
        """Return matching test device."""
        _domain, identifier = identifiers

        for migration in DEVICE_MIGRATIONS:
            if identifier == old_device_identifier(
                migration.old_device,
                config_entry.data[CONF.DEVICE_POSTFIX],
            ):
                return devices.get(migration.old_device)

        return None

    device_registry.async_get_device_by_identifier.side_effect = get_device

    hass = MagicMock()

    with (
        patch(
            "custom_components.weishaupt_modbus.migrate_helpers.er.async_get",
            return_value=entity_registry,
        ),
        patch(
            "custom_components.weishaupt_modbus.migrate_helpers.dr.async_get",
            return_value=device_registry,
        ),
    ):
        migrate_entities(config_entry, hass)

    device_registry.async_update_device.assert_any_call(
        "system_device",
        new_identifiers={
            (
                CONST.DOMAIN,
                "AA:BB:CC:DD:EE:FF_system",
            )
        },
    )

    device_registry.async_update_device.assert_any_call(
        "hk1_device",
        new_identifiers={
            (
                CONST.DOMAIN,
                "AA:BB:CC:DD:EE:FF_heating_circuit",
            )
        },
    )

    device_registry.async_remove_device.assert_called_once_with("hk2_device")
