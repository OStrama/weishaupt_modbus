"""Tests for Weishaupt entity platforms."""

from unittest.mock import MagicMock, patch

from custom_components.weishaupt_modbus.modbus.descriptions.description import (
    NumberDescription,
    SelectDescription,
    SensorDescription,
)
from custom_components.weishaupt_modbus.number import async_setup_entry as setup_number
from custom_components.weishaupt_modbus.select import async_setup_entry as setup_select
from custom_components.weishaupt_modbus.sensor import async_setup_entry as setup_sensor
import pytest

from homeassistant.core import HomeAssistant


def make_description(description_type):
    """Create a description instance without requiring constructor arguments."""
    return object.__new__(description_type)


@pytest.mark.asyncio
async def test_number_setup(hass: HomeAssistant):
    """Test number entities are added."""
    config_entry = MagicMock()
    coordinator = MagicMock()
    config_entry.runtime_data.weishaupt_coordinator = coordinator

    number_description = make_description(NumberDescription)
    sensor_description = make_description(SensorDescription)

    add_entities = MagicMock()

    with (
        patch(
            "custom_components.weishaupt_modbus.number.get_entities",
            return_value=[number_description, sensor_description],
        ),
        patch(
            "custom_components.weishaupt_modbus.number.WeishauptNumber",
            return_value="number_entity",
        ) as number_entity,
    ):
        await setup_number(hass, config_entry, add_entities)

    number_entity.assert_called_once_with(
        coordinator,
        number_description,
        config_entry,
    )
    add_entities.assert_called_once_with(["number_entity"])


@pytest.mark.asyncio
async def test_select_setup(hass: HomeAssistant):
    """Test select entities are added."""
    config_entry = MagicMock()
    coordinator = MagicMock()
    config_entry.runtime_data.weishaupt_coordinator = coordinator

    select_description = make_description(SelectDescription)
    sensor_description = make_description(SensorDescription)

    add_entities = MagicMock()

    with (
        patch(
            "custom_components.weishaupt_modbus.select.get_entities",
            return_value=[select_description, sensor_description],
        ),
        patch(
            "custom_components.weishaupt_modbus.select.WeishauptSelect",
            return_value="select_entity",
        ) as select_entity,
    ):
        await setup_select(hass, config_entry, add_entities)

    select_entity.assert_called_once_with(
        coordinator,
        select_description,
        config_entry,
    )
    add_entities.assert_called_once_with(["select_entity"])


@pytest.mark.asyncio
async def test_sensor_setup(hass: HomeAssistant):
    """Test sensor entities are added."""
    config_entry = MagicMock()
    coordinator = MagicMock()
    config_entry.runtime_data.weishaupt_coordinator = coordinator
    config_entry.runtime_data.webif_coordinator = None

    sensor_description = make_description(SensorDescription)
    number_description = make_description(NumberDescription)

    add_entities = MagicMock()

    with (
        patch(
            "custom_components.weishaupt_modbus.sensor.get_entities",
            return_value=[sensor_description, number_description],
        ),
        patch(
            "custom_components.weishaupt_modbus.sensor.WeishauptSensor",
            return_value="sensor_entity",
        ) as sensor_entity,
    ):
        await setup_sensor(hass, config_entry, add_entities)

    sensor_entity.assert_called_once_with(
        coordinator,
        sensor_description,
        config_entry,
    )
    add_entities.assert_called_once_with(["sensor_entity"])


def test_parallel_updates():
    """Test platform parallel update settings."""
    from custom_components.weishaupt_modbus import number, select, sensor

    assert number.PARALLEL_UPDATES == 1
    assert select.PARALLEL_UPDATES == 1
    assert sensor.PARALLEL_UPDATES == 0
