"""Regression tests for non-destructive register batching and partial support."""

from collections.abc import Iterator
from types import SimpleNamespace
from unittest.mock import AsyncMock, call, patch

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


def error(code: int) -> SimpleNamespace:
    """Create a protocol exception response."""
    return SimpleNamespace(isError=lambda: True, exception_code=code, registers=[])


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


def test_sparse_registers_are_not_moved(client: WeishauptModbusClient) -> None:
    """A gap must not silently substitute an unconfigured register."""
    items = [item(33101, 33101), item(33103, 33101)]
    assert client._process_and_validate_batches([items]) == {33101: 1, 33103: 1}
    assert [(x.address, x.batch) for x in items] == [(33101, 33101), (33103, 33101)]


def test_duplicate_and_calculated_registers_do_not_change_batch_size(
    client: WeishauptModbusClient,
) -> None:
    """A calculated alias must not overwrite its physical source's decoder."""
    physical = item(33103, 33103, FORMATS.PERCENTAGE)
    calculated = item(33103, 33103, FORMATS.NUMBER, TYPES.SENSOR_CALC)
    items = [physical, calculated, physical, item(33104, 33103)]
    assert client._process_and_validate_batches([items]) == {33103: 2}
    assert client._items_dict[33103] is physical


def test_hardware_batch_limit(client: WeishauptModbusClient) -> None:
    """Respect the hardware limit and preserve every requested address."""
    items = [item(address, 30001) for address in range(30001, 30008)]
    batches = client._process_and_validate_batches([items])
    assert all(1 <= count <= 5 for count in batches.values())
    assert [
        address
        for start, count in batches.items()
        for address in range(start, start + count)
    ] == list(range(30001, 30008))


def test_real_registers_preserve_physical_decoders(
    client: WeishauptModbusClient,
) -> None:
    """Keep calculated aliases out of the real register decoder and read plan."""
    physical = {
        register.address: register
        for group in modbus_api.DEVICELISTS
        for register in group
        if register.type != TYPES.SENSOR_CALC and register.batch is not None
    }
    batches = client._process_and_validate_batches(modbus_api.DEVICELISTS)
    assert client._items_dict[33103] is physical[33103]
    assert client._items_dict[33103].format == FORMATS.PERCENTAGE
    assert all(
        client._items_dict[address] is register
        for address, register in physical.items()
    )
    assert {
        address
        for start, count in batches.items()
        for address in range(start, start + count)
    } == set(physical)


def test_function_boundary(client: WeishauptModbusClient) -> None:
    """Never combine input and holding addresses in one read."""
    items = [item(39999, 39999), item(40000, 39999)]
    assert client._process_and_validate_batches([items]) == {39999: 1, 40000: 1}


@pytest.mark.asyncio
@pytest.mark.parametrize("holding", [False, True])
async def test_partial_block_keeps_valid_registers(
    client: WeishauptModbusClient, monkeypatch: pytest.MonkeyPatch, holding: bool
) -> None:
    """A missing neighbor must not hide otherwise readable values."""
    start = 43106 if holding else 33106
    items = [item(address, start) for address in range(start, start + 3)]
    monkeypatch.setattr(modbus_api, "DEVICELISTS", [items])
    reader = (
        client._client.read_holding_registers
        if holding
        else client._client.read_input_registers
    )
    reader.side_effect = [error(2), response([40]), error(2), response([60])]
    client.data.update(dict.fromkeys(range(start, start + 3), 999))

    result = await client.update()

    assert result == {start: 40, start + 1: None, start + 2: 60}
    assert reader.call_args_list == [
        call(address=start, count=3, device_id=1),
        call(address=start, count=1, device_id=1),
        call(address=start + 1, count=1, device_id=1),
        call(address=start + 2, count=1, device_id=1),
    ]
    client._client.write_register.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("failed", [TimeoutError(), response([])])
async def test_individual_failure_keeps_other_values(
    client: WeishauptModbusClient,
    monkeypatch: pytest.MonkeyPatch,
    failed: Exception | SimpleNamespace,
) -> None:
    """An individual timeout or incomplete reply must not erase its siblings."""
    start = 33106
    monkeypatch.setattr(
        modbus_api,
        "DEVICELISTS",
        [[item(address, start) for address in range(start, start + 3)]],
    )
    client._client.read_input_registers.side_effect = [
        error(2),
        response([40]),
        failed,
        response([60]),
    ]
    client.data.update(dict.fromkeys(range(start, start + 3), 999))
    assert await client.update() == {start: 40, start + 1: None, start + 2: 60}
    client._client.write_register.assert_not_called()


@pytest.mark.asyncio
async def test_non_address_error_does_not_retry_individually(
    client: WeishauptModbusClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Do not amplify a server failure into additional requests."""
    monkeypatch.setattr(
        modbus_api, "DEVICELISTS", [[item(33101, 33101), item(33102, 33101)]]
    )
    client._client.read_input_registers.return_value = error(4)
    assert await client.update() == {33101: None, 33102: None}
    client._client.read_input_registers.assert_awaited_once()


@pytest.mark.asyncio
async def test_short_response_does_not_leave_stale_values(
    client: WeishauptModbusClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An incomplete block must not retain data from the preceding poll."""
    monkeypatch.setattr(
        modbus_api, "DEVICELISTS", [[item(33101, 33101), item(33102, 33101)]]
    )
    client.data.update({33101: 99, 33102: 99})
    client._client.read_input_registers.return_value = response([1])
    assert await client.update() == {33101: None, 33102: None}
