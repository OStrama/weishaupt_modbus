"""Provide pytest fixtures for the in-memory Modbus implementation."""

from __future__ import annotations

import pytest

from .mock import MockModbusConnection, MockModbusUnit

DEFAULT_UNIT_ID = 1


@pytest.fixture
def mock_modbus_connection() -> MockModbusConnection:
    """A fresh in-memory ``MockModbusConnection``."""
    return MockModbusConnection()


@pytest.fixture
def mock_modbus_unit(mock_modbus_connection: MockModbusConnection) -> MockModbusUnit:
    """The unit-1 handle on ``mock_modbus_connection``, ready to configure."""
    return mock_modbus_connection.for_unit(DEFAULT_UNIT_ID)
