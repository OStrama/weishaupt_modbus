"""Unit tests for the sensor platform setup."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.weishaupt_modbus import sensor


def make_config_entry(with_webif: bool) -> MagicMock:
    """Create a mock config entry with coordinator runtime data."""
    config_entry = MagicMock()
    config_entry.runtime_data.coordinator = MagicMock()
    config_entry.runtime_data.coordinator.modbus_items = []
    if with_webif:
        config_entry.runtime_data.webif_coordinator = MagicMock()
        config_entry.runtime_data.webif_coordinator.api_items = []
    else:
        config_entry.runtime_data.webif_coordinator = None
    return config_entry


def added_entities(async_add_entities: MagicMock) -> list:
    """Collect all entities passed to async_add_entities across all calls."""
    return [
        entity for call in async_add_entities.call_args_list for entity in call.args[0]
    ]


class TestSensorSetup:
    """Test the sensor platform setup."""

    @pytest.mark.asyncio
    async def test_modbus_sensors_added_when_webif_setup_fails(self):
        """Modbus sensors must be added even if the WebIF setup raises.

        Regression test for issue #172: the sensor platform used to build
        Modbus and WebIF entities into one list and call async_add_entities
        only once at the very end, so any error in the WebIF part prevented
        the already built Modbus sensors from being registered.
        """
        config_entry = make_config_entry(with_webif=True)
        async_add_entities = MagicMock()
        modbus_entities = [MagicMock(), MagicMock()]

        with (
            patch.object(
                sensor,
                "build_entity_list",
                AsyncMock(return_value=modbus_entities),
            ),
            patch.object(
                sensor,
                "build_webif_entity_list",
                AsyncMock(side_effect=RuntimeError("WebIF broken")),
            ),
        ):
            await sensor.async_setup_entry(
                MagicMock(), config_entry, async_add_entities
            )

        assert added_entities(async_add_entities) == modbus_entities

    @pytest.mark.asyncio
    async def test_all_sensors_added_when_webif_works(self):
        """Modbus and WebIF sensors are all added when both setups succeed."""
        config_entry = make_config_entry(with_webif=True)
        async_add_entities = MagicMock()
        modbus_entities = [MagicMock(), MagicMock()]
        webif_entities = [MagicMock()]
        expected = [*modbus_entities, *webif_entities]

        async def fake_build_webif_entity_list(entries, **kwargs):
            # Mirror the real contract: extend the passed list and return it.
            entries.extend(webif_entities)
            return entries

        with (
            patch.object(
                sensor,
                "build_entity_list",
                AsyncMock(return_value=modbus_entities),
            ),
            patch.object(
                sensor,
                "build_webif_entity_list",
                AsyncMock(side_effect=fake_build_webif_entity_list),
            ),
        ):
            await sensor.async_setup_entry(
                MagicMock(), config_entry, async_add_entities
            )

        assert added_entities(async_add_entities) == expected

    @pytest.mark.asyncio
    async def test_webif_skipped_without_webif_coordinator(self):
        """Only Modbus sensors are added when no WebIF coordinator exists."""
        config_entry = make_config_entry(with_webif=False)
        async_add_entities = MagicMock()
        modbus_entities = [MagicMock()]
        webif_mock = AsyncMock()

        with (
            patch.object(
                sensor,
                "build_entity_list",
                AsyncMock(return_value=modbus_entities),
            ),
            patch.object(sensor, "build_webif_entity_list", webif_mock),
        ):
            await sensor.async_setup_entry(
                MagicMock(), config_entry, async_add_entities
            )

        assert added_entities(async_add_entities) == modbus_entities
        webif_mock.assert_not_awaited()
