"""Tests for the Weishaupt coordinator."""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from homeassistant.core import HomeAssistant
from custom_components.weishaupt_modbus.modbus.coordinator import WeishauptCoordinator
from custom_components.weishaupt_modbus.modbus.weishaupt_modbus_client.model.modbus_connection_device import (
    UpdateReport,
)
import pytest


@pytest.mark.asyncio
async def test_partial_update_failure_is_logged(hass: HomeAssistant, caplog):
    """Test that failed reports are logged."""
    device = MagicMock()

    error = RuntimeError("test failure")
    device.async_update = AsyncMock(
        return_value=UpdateReport(
            updated={"system"},
            failed={"heat_pump": error},
        )
    )

    coordinator = WeishauptCoordinator(
        hass=hass,
        device=device,
        mcu_lock=asyncio.Lock(),
    )

    await coordinator._async_update_data()

    assert "Failed to update Weishaupt reports: heat_pump: test failure" in caplog.text
