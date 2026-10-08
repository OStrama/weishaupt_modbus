"""Tests for Weishaupt entities."""

from enum import Enum
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.weishaupt_modbus.modbus.descriptions.calculated import (
    calculate_thermal_power,
)
from custom_components.weishaupt_modbus.const import CONF, CONST
from custom_components.weishaupt_modbus.modbus.descriptions.description import (
    NumberDescription,
    SelectDescription,
    SensorDescription,
)
from custom_components.weishaupt_modbus.modbus.descriptions.params import (
    EMPTY,
    NUMBER_EMPTY,
)
from custom_components.weishaupt_modbus.modbus.descriptions.second_heat_source import (
    SECOND_HEAT_SOURCE_ENTITIES,
)
from custom_components.weishaupt_modbus.modbus.entities import (
    WeishauptNumber,
    WeishauptSelect,
    WeishauptSensor,
)


def create_entity(updated: set[str], coordinator_available: bool = True):
    """Create a Weishaupt sensor with mocked coordinator data."""
    coordinator = MagicMock()
    coordinator.data.updated = updated
    coordinator.device = MagicMock()

    # CoordinatorEntity.available reads coordinator.last_update_success.
    coordinator.last_update_success = coordinator_available

    config_entry = MagicMock()
    config_entry.data = {
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
    }

    description = SECOND_HEAT_SOURCE_ENTITIES[0]

    return WeishauptSensor(
        coordinator,
        description,
        config_entry,
    )


def test_entity_available_when_report_was_updated():
    """Test that an entity is available when its report was updated."""
    entity = create_entity({"second_heat_source"})

    assert entity.available is True


def test_entity_unavailable_when_report_was_not_updated():
    """Test that an entity is unavailable when its report was not updated."""
    entity = create_entity({"system"})

    assert entity.available is False


def test_entity_unavailable_when_coordinator_update_failed():
    """Test that an entity is unavailable when the coordinator update failed."""
    entity = create_entity(
        {"second_heat_source"},
        coordinator_available=False,
    )

    assert entity.available is False


def test_entity_device_info():
    """Test device information."""
    entity = create_entity({"second_heat_source"})

    device_info = entity.device_info

    assert device_info["identifiers"] == {
        (CONST.DOMAIN, "AA:BB:CC:DD:EE:FF_second_heat_source")
    }
    assert device_info["translation_key"] == "dev_second_heat_source"
    assert device_info["sw_version"] == "Device_SW_Version"
    assert device_info["model"] == "Device_model"
    assert device_info["manufacturer"] == "Weishaupt"


def create_sensor_entity(
    value,
    *,
    is_enum: bool = False,
    calculated_value_fn=None,
):
    """Create a sensor with a controlled value function."""
    coordinator = MagicMock()
    coordinator.device = MagicMock()

    config_entry = MagicMock()
    config_entry.data = {
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
    }
    coordinator.config_entry = config_entry

    value_fn = MagicMock(return_value=value)

    description = SensorDescription(
        key="test_value",
        report_name="heat_pump",
        params=EMPTY if not is_enum else EMPTY,
        value_fn=value_fn,
        calculated_value_fn=calculated_value_fn,
    )

    # The entity uses params.is_enum to decide whether to format the value.
    if is_enum:
        from custom_components.weishaupt_modbus.modbus.descriptions.params import ENUM

        description = SensorDescription(
            key="test_value",
            report_name="heat_pump",
            params=ENUM,
            value_fn=value_fn,
            calculated_value_fn=calculated_value_fn,
        )

    return WeishauptSensor(coordinator, description, config_entry)


def test_sensor_native_value():
    """Test a normal sensor value."""
    entity = create_sensor_entity(12.5)

    assert entity.native_value == 12.5
    entity.description.value_fn.assert_called_once_with(entity.coordinator.device)


def test_sensor_native_value_none():
    """Test a sensor without a value."""
    entity = create_sensor_entity(None)

    assert entity.native_value is None
    entity.description.value_fn.assert_called_once_with(entity.coordinator.device)


def test_sensor_native_value_enum():
    """Test an enum sensor value."""
    entity = create_sensor_entity(3, is_enum=True)

    assert entity.native_value == "heat_pump_test_value_3"
    entity.description.value_fn.assert_called_once_with(entity.coordinator.device)


def test_sensor_native_value_calculated():
    """Test a calculated sensor value."""
    calculated_value_fn = MagicMock(return_value=42.5)

    entity = create_sensor_entity(
        12.5,
        calculated_value_fn=calculated_value_fn,
    )

    assert entity.native_value == 42.5
    calculated_value_fn.assert_called_once_with(
        entity.coordinator,
        entity._weishaupt_config_entry.runtime_data.powermap,
    )


def create_calculated_sensor():
    """Create a sensor using the real thermal power calculation."""
    coordinator = MagicMock()
    coordinator.device = MagicMock()

    config_entry = MagicMock()
    config_entry.data = {
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
    }
    config_entry.runtime_data.powermap = MagicMock()
    coordinator.config_entry = config_entry

    description = SensorDescription(
        key="thermal_power",
        report_name="heat_pump",
        params=EMPTY,
        value_fn=MagicMock(return_value=None),
        calculated_value_fn=calculate_thermal_power,
    )

    entity = WeishauptSensor(
        coordinator,
        description,
        config_entry,
    )

    return entity


def test_sensor_calculated_value_missing_power_request():
    """Test calculated value when power request is unavailable."""
    entity = create_calculated_sensor()

    entity.coordinator.device.heat_pump_input.power_request = None
    entity.coordinator.device.system_input.intake_temperature = 10.0
    entity.coordinator.device.heat_pump_input.flow_temperature = 35.0

    assert entity.native_value is None
    entity.coordinator.config_entry.runtime_data.powermap.map.assert_not_called()


def test_sensor_calculated_value_missing_intake_temperature():
    """Test calculated value when intake temperature is unavailable."""
    entity = create_calculated_sensor()

    entity.coordinator.device.heat_pump_input.power_request = 50.0
    entity.coordinator.device.system_input.intake_temperature = None
    entity.coordinator.device.heat_pump_input.flow_temperature = 35.0

    assert entity.native_value is None
    entity.coordinator.config_entry.runtime_data.powermap.map.assert_not_called()


def test_sensor_calculated_value_missing_flow_temperature():
    """Test calculated value when flow temperature is unavailable."""
    entity = create_calculated_sensor()

    entity.coordinator.device.heat_pump_input.power_request = 50.0
    entity.coordinator.device.system_input.intake_temperature = 10.0
    entity.coordinator.device.heat_pump_input.flow_temperature = None

    assert entity.native_value is None
    entity.coordinator.config_entry.runtime_data.powermap.map.assert_not_called()


def test_sensor_calculated_value_no_power_map_result():
    """Test calculated value when the power map has no result."""
    entity = create_calculated_sensor()

    entity.coordinator.device.heat_pump_input.power_request = 50.0
    entity.coordinator.device.system_input.intake_temperature = 10.0
    entity.coordinator.device.heat_pump_input.flow_temperature = 35.0
    entity.coordinator.config_entry.runtime_data.powermap.map.return_value = None

    assert entity.native_value is None

    entity.coordinator.config_entry.runtime_data.powermap.map.assert_called_once_with(
        10.0,
        35.0,
    )


def test_sensor_calculated_value():
    """Test calculated thermal power."""
    entity = create_calculated_sensor()

    entity.coordinator.device.heat_pump_input.power_request = 50.0
    entity.coordinator.device.system_input.intake_temperature = 10.0
    entity.coordinator.device.heat_pump_input.flow_temperature = 35.0
    entity.coordinator.config_entry.runtime_data.powermap.map.return_value = 8.0

    assert entity.native_value == 4.0

    entity.coordinator.config_entry.runtime_data.powermap.map.assert_called_once_with(
        10.0,
        35.0,
    )


def create_number_entity():
    """Create a number with mocked callbacks."""
    coordinator = MagicMock()
    coordinator.device = MagicMock()
    coordinator.async_request_refresh = AsyncMock()

    config_entry = MagicMock()
    config_entry.data = {
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
    }

    value_fn = MagicMock(return_value=20.5)
    set_value_fn = AsyncMock()

    description = NumberDescription(
        key="test_value",
        report_name="heat_pump",
        params=NUMBER_EMPTY,
        value_fn=value_fn,
        set_value_fn=set_value_fn,
    )

    return WeishauptNumber(coordinator, description, config_entry)


def test_number_native_value():
    """Test the current number value."""
    entity = create_number_entity()

    assert entity.native_value == 20.5
    entity.description.value_fn.assert_called_once_with(entity.coordinator.device)


@pytest.mark.asyncio
async def test_number_set_native_value():
    """Test setting a number value."""
    entity = create_number_entity()

    await entity.async_set_native_value(23.5)

    entity.description.set_value_fn.assert_awaited_once_with(
        entity.coordinator.device,
        23.5,
    )
    entity.coordinator.async_request_refresh.assert_awaited_once()


class SelectTestEnum(Enum):
    """Test select enum."""

    OFF = 0
    ON = 1
    AUTO = 2


def create_select_entity(value):
    """Create a select with a controlled value."""
    coordinator = MagicMock()
    coordinator.device = MagicMock()
    coordinator.async_request_refresh = AsyncMock()

    config_entry = MagicMock()
    config_entry.data = {
        CONF.MAC: "AA:BB:CC:DD:EE:FF",
    }

    value_fn = MagicMock(return_value=value)
    set_value_fn = AsyncMock()

    description = SelectDescription(
        key="test_mode",
        report_name="heat_pump",
        enum=SelectTestEnum,
        value_fn=value_fn,
        set_value_fn=set_value_fn,
    )

    return WeishauptSelect(coordinator, description, config_entry)


def test_select_options():
    """Test select options."""
    entity = create_select_entity(SelectTestEnum.ON.value)

    assert entity.options == ["OFF", "ON", "AUTO"]


def test_select_current_option():
    """Test the current select option."""
    entity = create_select_entity(SelectTestEnum.ON.value)

    assert entity.current_option == "ON"
    entity.description.value_fn.assert_called_once_with(entity.coordinator.device)


def test_select_current_option_none():
    """Test a select without a value."""
    entity = create_select_entity(None)

    assert entity.current_option is None
    entity.description.value_fn.assert_called_once_with(entity.coordinator.device)


@pytest.mark.asyncio
async def test_select_option():
    """Test setting a select option."""
    entity = create_select_entity(SelectTestEnum.OFF.value)

    await entity.async_select_option("AUTO")

    entity.description.set_value_fn.assert_awaited_once_with(
        entity.coordinator.device,
        SelectTestEnum.AUTO.value,
    )
    entity.coordinator.async_request_refresh.assert_awaited_once()
