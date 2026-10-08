"""Tests for integration initialization."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.weishaupt_modbus import (
    PLATFORMS,
    async_migrate_entry,
    async_unload_entry,
    update_listener,
)
from custom_components.weishaupt_modbus.const import CONF, CONST
import pytest

from custom_components.weishaupt_modbus import (
    PLATFORMS,
    async_migrate_entry,
    async_setup_entry,
    async_unload_entry,
    update_listener,
)


@pytest.mark.asyncio
async def test_update_listener():
    """Test that the config entry is reloaded."""
    hass = MagicMock()
    hass.config_entries.async_reload = AsyncMock()

    entry = MagicMock()
    entry.entry_id = "test_entry"

    await update_listener(hass, entry)

    hass.config_entries.async_reload.assert_awaited_once_with("test_entry")


@pytest.mark.asyncio
async def test_async_unload_entry_without_webif():
    """Test unloading without WebIF."""
    hass = MagicMock()
    entry = MagicMock()
    entry.runtime_data.webif_api = None
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    result = await async_unload_entry(hass, entry)

    assert result is True
    hass.config_entries.async_unload_platforms.assert_awaited_once_with(
        entry,
        PLATFORMS,
    )


@pytest.mark.asyncio
async def test_async_unload_entry_with_webif():
    """Test unloading with WebIF."""
    hass = MagicMock()
    entry = MagicMock()

    webif_api = MagicMock()
    webif_api.close = AsyncMock()
    entry.runtime_data.webif_api = webif_api

    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

    result = await async_unload_entry(hass, entry)

    assert result is True
    webif_api.close.assert_awaited_once()
    hass.config_entries.async_unload_platforms.assert_awaited_once_with(
        entry,
        PLATFORMS,
    )


@pytest.mark.asyncio
async def test_async_migrate_entry_from_version_1():
    """Test migration of an old version 1 entry."""
    legacy_const = SimpleNamespace(
        DEF_KENNFELDFILE="weishaupt_wbb_kennfeld.json",
        DEF_PREFIX="weishaupt_wbb",
    )

    hass = MagicMock()
    config_entry = MagicMock()
    config_entry.version = 1
    config_entry.data = {
        CONF.HOST: "192.168.1.100",
    }

    with patch(
        "custom_components.weishaupt_modbus.CONST",
        legacy_const,
    ):
        result = await async_migrate_entry(hass, config_entry)

    assert result is True

    final_call = hass.config_entries.async_update_entry.call_args_list[-1]
    data = final_call.kwargs["data"]

    # Version 1 -> 2
    assert data[CONF.PREFIX] == "weishaupt_wbb"
    assert data[CONF.DEVICE_POSTFIX] == ""
    assert data[CONF.KENNFELD_FILE] == "weishaupt_wbb_kennfeld.json"

    # Version 2 -> 3
    assert data[CONF.HK2] is False
    assert data[CONF.HK3] is False
    assert data[CONF.HK4] is False
    assert data[CONF.HK5] is False

    # Version 3 -> 4
    assert data[CONF.NAME_DEVICE_PREFIX] is False
    assert data[CONF.NAME_TOPIC_PREFIX] is False

    # Version 4 -> 5
    assert data[CONF.CB_WEBIF] is False
    assert data[CONF.USERNAME] == ""
    assert data[CONF.PASSWORD] == ""
    assert data[CONF.WEBIF_TOKEN] == ""

    # Version 7 -> 8
    assert data[CONF.CB_WEBIF_MOCKUP_DATA] is False
    assert data[CONF.CB_WEBIF_HK1] is False
    assert data[CONF.CB_WEBIF_HK2] is False
    assert data[CONF.CB_WEBIF_HK3] is False
    assert data[CONF.CB_WEBIF_HK4] is False
    assert data[CONF.CB_WEBIF_HK5] is False
    assert data[CONF.CB_WEBIF_WP] is False
    assert data[CONF.CB_WEBIF_2WEZ] is False
    assert data[CONF.CB_WEBIF_SATISTICS] is False

    # Version 8 -> 9
    assert data[CONF.MAC] == "CHANGEME"

    # Final migration version
    assert final_call.kwargs["version"] == 9
    assert final_call.kwargs["minor_version"] == 1


@pytest.mark.asyncio
async def test_async_migrate_entry_to_version_9():
    """Test migration of an entry at version 8."""
    hass = MagicMock()
    config_entry = MagicMock()
    config_entry.version = 8
    config_entry.data = {
        CONF.HOST: "192.168.1.100",
    }

    result = await async_migrate_entry(hass, config_entry)

    assert result is True

    update_calls = hass.config_entries.async_update_entry.call_args_list

    assert len(update_calls) == 2

    assert update_calls[0].kwargs["version"] == 8
    assert update_calls[0].kwargs["minor_version"] == 1

    assert update_calls[1].kwargs["version"] == 9
    assert update_calls[1].kwargs["minor_version"] == 1
    assert update_calls[1].kwargs["data"][CONF.MAC] == "CHANGEME"


@pytest.mark.asyncio
async def test_async_setup_entry_without_webif() -> None:
    """Test setting up the integration without WebIF."""
    hass = MagicMock()
    hass.config.config_dir = "/config"
    hass.states.async_all.return_value = []

    entry = MagicMock()
    entry.data = {
        CONF.HOST: "192.168.1.100",
        CONF.PORT: 502,
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
        CONF.UID_MIGRATION: True,
        CONF.CB_WEBIF: False,
        CONF.HK2: True,
        CONF.HK3: True,
        CONF.HK4: True,
        CONF.HK5: True,
    }

    entry.runtime_data = None
    entry.add_update_listener = MagicMock()
    entry.async_on_unload = MagicMock()

    coordinator = MagicMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()

    powermap = MagicMock()
    powermap.initialize = AsyncMock()

    with (
        patch(
            "custom_components.weishaupt_modbus.async_get_unit",
            return_value=MagicMock(),
        ) as mock_get_unit,
        patch(
            "custom_components.weishaupt_modbus.Weishaupt",
            return_value=MagicMock(),
        ) as mock_weishaupt,
        patch(
            "custom_components.weishaupt_modbus.WeishauptCoordinator",
            return_value=coordinator,
        ) as mock_coordinator,
        patch(
            "custom_components.weishaupt_modbus.PowerMap",
            return_value=powermap,
        ) as mock_powermap,
        patch(
            "custom_components.weishaupt_modbus.asyncio.Lock",
            return_value=MagicMock(),
        ),
    ):
        hass.config_entries.async_forward_entry_setups = AsyncMock()

        result = await async_setup_entry(hass, entry)

    assert result is True

    mock_get_unit.assert_called_once()
    mock_weishaupt.assert_called_once()
    mock_coordinator.assert_called_once()
    coordinator.async_config_entry_first_refresh.assert_awaited_once()

    mock_powermap.assert_called_once_with(entry, hass)
    powermap.initialize.assert_awaited_once()

    assert entry.runtime_data.powermap is powermap

    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        entry,
        PLATFORMS,
    )

    assert mock_weishaupt.call_args.args[1] == [
        "system",
        "heat_pump",
        "heating_circuit",
        "domestic_hot_water",
        "second_heat_source",
        "statistics",
        "io",
        "heating_circuit2",
        "heating_circuit3",
        "heating_circuit4",
        "heating_circuit5",
    ]


@pytest.mark.asyncio
async def test_async_setup_entry_runs_uid_migration() -> None:
    """Test entity UID migration during setup."""
    hass = MagicMock()
    hass.config.config_dir = "/config"
    hass.states.async_all.return_value = []

    entry = MagicMock()
    entry.data = {
        CONF.HOST: "192.168.1.100",
        CONF.PORT: 502,
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
        CONF.UID_MIGRATION: False,
        CONF.CB_WEBIF: False,
    }

    entry.runtime_data = None
    entry.add_update_listener = MagicMock()
    entry.async_on_unload = MagicMock()

    coordinator = MagicMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()

    powermap = MagicMock()
    powermap.initialize = AsyncMock()

    with (
        patch(
            "custom_components.weishaupt_modbus.migrate_entities",
        ) as mock_migrate,
        patch(
            "custom_components.weishaupt_modbus.async_get_unit",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.Weishaupt",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.WeishauptCoordinator",
            return_value=coordinator,
        ),
        patch(
            "custom_components.weishaupt_modbus.PowerMap",
            return_value=powermap,
        ),
    ):
        hass.config_entries.async_forward_entry_setups = AsyncMock()

        result = await async_setup_entry(hass, entry)

    assert result is True

    mock_migrate.assert_called_once_with(entry, hass)

    update_call = hass.config_entries.async_update_entry.call_args
    assert update_call.kwargs["data"][CONF.UID_MIGRATION] is True


@pytest.mark.asyncio
async def test_async_setup_entry_with_webif() -> None:
    """Test setting up the integration with WebIF enabled."""
    hass = MagicMock()
    hass.config.config_dir = "/config"
    hass.states.async_all.return_value = []

    entry = MagicMock()
    entry.data = {
        CONF.HOST: "192.168.1.100",
        CONF.PORT: 502,
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
        CONF.UID_MIGRATION: True,
        CONF.CB_WEBIF: True,
        CONF.USERNAME: "admin",
        CONF.PASSWORD: "secret",
    }

    entry.runtime_data = None
    entry.add_update_listener = MagicMock()
    entry.async_on_unload = MagicMock()

    webif_api = MagicMock()

    webif_coordinator = MagicMock()
    webif_coordinator.async_config_entry_first_refresh = AsyncMock()

    modbus_coordinator = MagicMock()
    modbus_coordinator.async_config_entry_first_refresh = AsyncMock()

    powermap = MagicMock()
    powermap.initialize = AsyncMock()

    with (
        patch(
            "custom_components.weishaupt_modbus.WebifConnection",
            return_value=webif_api,
        ) as mock_webif,
        patch(
            "custom_components.weishaupt_modbus.WeishauptWebifCoordinator",
            return_value=webif_coordinator,
        ) as mock_webif_coordinator,
        patch(
            "custom_components.weishaupt_modbus.async_get_unit",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.Weishaupt",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.WeishauptCoordinator",
            return_value=modbus_coordinator,
        ),
        patch(
            "custom_components.weishaupt_modbus.PowerMap",
            return_value=powermap,
        ),
    ):
        hass.config_entries.async_forward_entry_setups = AsyncMock()

        result = await async_setup_entry(hass, entry)

    assert result is True

    mock_webif.assert_called_once_with(
        ip="192.168.1.100",
        user="admin",
        password="secret",
    )

    mock_webif_coordinator.assert_called_once()

    webif_coordinator.async_config_entry_first_refresh.assert_awaited_once()
    modbus_coordinator.async_config_entry_first_refresh.assert_awaited_once()

    assert entry.runtime_data.webif_api is webif_api
    assert entry.runtime_data.webif_coordinator is webif_coordinator


@pytest.mark.asyncio
async def test_async_setup_entry_with_placeholder_mac(caplog) -> None:
    """Test that setup fails when the MAC address was not migrated/configured."""
    hass = MagicMock()

    entry = MagicMock()
    entry.data = {
        CONF.MAC: "CHANGEME",
    }

    result = await async_setup_entry(hass, entry)

    assert result is False
    assert "MAC Address not set" in caplog.text


@pytest.mark.asyncio
async def test_async_setup_entry_logs_invalid_sensor_unit(caplog) -> None:
    """Test that invalid global sensor units are logged."""
    hass = MagicMock()
    hass.config.config_dir = "/config"

    invalid_state = MagicMock()
    invalid_state.entity_id = "sensor.invalid"
    invalid_state.attributes = {
        "unit_of_measurement": 123,
    }
    hass.states.async_all.return_value = [invalid_state]

    entry = MagicMock()
    entry.data = {
        CONF.HOST: "192.168.1.100",
        CONF.PORT: 502,
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
        CONF.UID_MIGRATION: True,
        CONF.CB_WEBIF: False,
    }

    coordinator = MagicMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()

    powermap = MagicMock()
    powermap.initialize = AsyncMock()

    with (
        patch(
            "custom_components.weishaupt_modbus.async_get_unit",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.Weishaupt",
            return_value=MagicMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.WeishauptCoordinator",
            return_value=coordinator,
        ),
        patch(
            "custom_components.weishaupt_modbus.PowerMap",
            return_value=powermap,
        ),
    ):
        hass.config_entries.async_forward_entry_setups = AsyncMock()

        result = await async_setup_entry(hass, entry)

    assert result is True
    assert "INVALID GLOBAL SENSOR UNIT" in caplog.text
