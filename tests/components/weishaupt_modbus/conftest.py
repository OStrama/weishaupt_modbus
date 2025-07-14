"""Fixtures for Weishaupt modbus tests."""

from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.weishaupt_modbus.const import CONF


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry with default values."""
    config_entry = Mock()
    config_entry.data = {
        CONF.HOST: "192.168.1.100",
        CONF.PORT: 502,
        CONF.PREFIX: "wh",
        CONF.DEVICE_POSTFIX: "",
        CONF.NAME_DEVICE_PREFIX: True,
        CONF.NAME_TOPIC_PREFIX: True,
    }
    config_entry.entry_id = "test_entry_id"
    return config_entry


@pytest.fixture
def mock_modbus_api():
    """Create a mock modbus API."""
    api = AsyncMock()
    api.connect = AsyncMock()
    return api
