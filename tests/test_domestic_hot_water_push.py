"""Tests for the maximum duration of the hot water boost selector."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from custom_components.weishaupt_modbus.const import CONF
from custom_components.weishaupt_modbus.modbus.weishaupt_modbus_client.model.device import (
    Weishaupt,
)
from custom_components.weishaupt_modbus.select import async_setup_entry

_REGISTER = 42102
_OFF = "domestic_hot_water_push_off"
_MAXIMUM = "domestic_hot_water_push_240"


@pytest.mark.asyncio
async def test_hot_water_push_maximum_through_select_platform() -> None:
    """Expose 240 minutes and round-trip it using the existing holding register."""
    words = {_REGISTER: 0}

    def read_holding(address: int, count: int) -> list[int]:
        return [words.get(register, 0) for register in range(address, address + count)]

    def write_register(address: int, value: int) -> None:
        words[address] = value

    unit = MagicMock(
        read_holding_registers=AsyncMock(side_effect=read_holding),
        read_input_registers=AsyncMock(side_effect=lambda _address, count: [0] * count),
        write_register=AsyncMock(side_effect=write_register),
    )
    device = Weishaupt(unit, ("domestic_hot_water",))
    coordinator = MagicMock(
        device=device,
        async_request_refresh=AsyncMock(side_effect=device.async_update),
    )
    entry = MagicMock(data={CONF.MAC: "test-controller"})
    entry.runtime_data.weishaupt_coordinator = coordinator
    entities = []

    await async_setup_entry(MagicMock(), entry, entities.extend)
    select = next(
        entity
        for entity in entities
        if entity.translation_key == "domestic_hot_water_push"
    )
    await device.async_update()
    assert select.current_option == _OFF
    assert select.options == [
        _OFF,
        *(f"domestic_hot_water_push_{minutes}" for minutes in range(5, 241, 5)),
    ]

    await select.async_select_option(_MAXIMUM)
    assert words[_REGISTER] == 240
    assert select.current_option == _MAXIMUM
    unit.write_register.assert_awaited_once_with(_REGISTER, 240)

    await select.async_select_option(_OFF)
    assert select.current_option == _OFF
    assert unit.write_register.await_args_list == [
        call(_REGISTER, 240),
        call(_REGISTER, 0),
    ]
    assert coordinator.async_request_refresh.await_count == 2
    reads = [request.args for request in unit.read_holding_registers.await_args_list]
    assert sum(address <= _REGISTER < address + count for address, count in reads) == 3


@pytest.mark.parametrize("language", ["de", "en", "nl"])
def test_hot_water_push_maximum_is_translated(language: str) -> None:
    """Each supported locale displays the duration in minutes."""
    translation = (
        Path(__file__).resolve().parents[1]
        / "custom_components/weishaupt_modbus/translations"
        / f"{language}.json"
    )
    strings = json.loads(translation.read_text(encoding="utf-8"))
    options = strings["entity"]["select"]["domestic_hot_water_push"]["state"]
    assert options[_MAXIMUM] == "240 min"
