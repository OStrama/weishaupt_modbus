"""Regression tests for API value validation and recovery on later polls."""

from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from custom_components.weishaupt_modbus.const import DEVICES, FORMATS, TYPES
from custom_components.weishaupt_modbus.items import ModbusItem
from custom_components.weishaupt_modbus.weishaupt_modbus_api import modbus_api
from custom_components.weishaupt_modbus.weishaupt_modbus_api.modbus_api import (
    WeishauptModbusClient,
)


def item(
    address: int,
    hint: int,
    mformat: str = FORMATS.NUMBER,
    mtype: str = TYPES.SENSOR,
) -> ModbusItem:
    """Create a synthetic register definition without device data."""
    return ModbusItem(address, "Test", mformat, mtype, DEVICES.WP, "test", batch=hint)


def response(values: list[int]) -> SimpleNamespace:
    """Create a successful read response."""
    return SimpleNamespace(isError=lambda: False, registers=values)


@pytest.fixture
def client() -> Iterator[WeishauptModbusClient]:
    """Mock transport creation so the tests never contact a device."""
    with patch.object(modbus_api, "AsyncModbusTcpClient"):
        result = WeishauptModbusClient("example.invalid")
        result._client.connected = True
        result._client.read_holding_registers = AsyncMock()
        result._client.read_input_registers = AsyncMock()
        result._client.write_register = AsyncMock()
        yield result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("mformat", "bad", "good"),
    [(FORMATS.TEMPERATURE, 32769, 180), (FORMATS.PERCENTAGE, 150, 60)],
)
async def test_invalid_reading_recovers_on_next_poll(
    client: WeishauptModbusClient,
    monkeypatch: pytest.MonkeyPatch,
    mformat: str,
    bad: int,
    good: int,
) -> None:
    """A temporary fault or invalid percentage must not disable future updates."""
    register = item(33103, 33103, mformat)
    monkeypatch.setattr(modbus_api, "DEVICELISTS", [[register]])
    client._client.read_input_registers.side_effect = [
        response([bad]),
        response([good]),
    ]
    assert (await client.update())[33103] is None
    assert register.is_invalid is False
    assert (await client.update())[33103] == good
    client._client.write_register.assert_not_called()
