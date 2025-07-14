"""Tests for device and entity naming in Weishaupt modbus integration."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock

import pytest

from custom_components.weishaupt_modbus.const import CONF, CONST, DEVICENAMES, DEVICES
from custom_components.weishaupt_modbus.entities import MyEntity
from custom_components.weishaupt_modbus.items import ModbusItem

if TYPE_CHECKING:
    from custom_components.weishaupt_modbus.configentry import MyConfigEntry

# Test data for each device type
DEVICE_TEST_DATA = {
    DEVICES.SYS: {
        "device_key": DEVICES.SYS,
        "expected_device_name": "WH System",
        "expected_entity_prefix": "SYS_",
        "sample_entity": "sample_sensor",
        "expected_entity_id": "sensor.sys_wh_sample_sensor",
    },
    DEVICES.WP: {
        "device_key": DEVICES.WP,
        "expected_device_name": "WH Wärmepumpe",
        "expected_entity_prefix": "WP_",
        "sample_entity": "temperature_sensor",
        "expected_entity_id": "sensor.wp_wh_temperature_sensor",
    },
    DEVICES.WW: {
        "device_key": DEVICES.WW,
        "expected_device_name": "WH Warmwasser",
        "expected_entity_prefix": "WW_",
        "sample_entity": "water_temp",
        "expected_entity_id": "sensor.ww_wh_water_temp",
    },
    DEVICES.HZ: {
        "device_key": DEVICES.HZ,
        "expected_device_name": "WH Heizkreis",
        "expected_entity_prefix": "HZ_",
        "sample_entity": "room_temperature",
        "expected_entity_id": "sensor.hz_wh_room_temperature",
    },
    DEVICES.HZ2: {
        "device_key": DEVICES.HZ2,
        "expected_device_name": "WH Heizkreis2",
        "expected_entity_prefix": "HZ2_",
        "sample_entity": "room_temperature",
        "expected_entity_id": "sensor.hz2_wh_room_temperature",
    },
    DEVICES.HZ3: {
        "device_key": DEVICES.HZ3,
        "expected_device_name": "WH Heizkreis3",
        "expected_entity_prefix": "HZ3_",
        "sample_entity": "room_temperature",
        "expected_entity_id": "sensor.hz3_wh_room_temperature",
    },
    DEVICES.HZ4: {
        "device_key": DEVICES.HZ4,
        "expected_device_name": "WH Heizkreis4",
        "expected_entity_prefix": "HZ4_",
        "sample_entity": "room_temperature",
        "expected_entity_id": "sensor.hz4_wh_room_temperature",
    },
    DEVICES.HZ5: {
        "device_key": DEVICES.HZ5,
        "expected_device_name": "WH Heizkreis5",
        "expected_entity_prefix": "HZ5_",
        "sample_entity": "room_temperature",
        "expected_entity_id": "sensor.hz5_wh_room_temperature",
    },
    DEVICES.W2: {
        "device_key": DEVICES.W2,
        "expected_device_name": "WH 2. Wärmeerzeuger",
        "expected_entity_prefix": "W2_",
        "sample_entity": "grenztemperatur",
        "expected_entity_id": "number.w2_wh_grenztemperatur",
    },
    DEVICES.ST: {
        "device_key": DEVICES.ST,
        "expected_device_name": "WH Statistik",
        "expected_entity_prefix": "ST_",
        "sample_entity": "energy_consumption",
        "expected_entity_id": "sensor.st_wh_energy_consumption",
    },
    DEVICES.UK: {
        "device_key": DEVICES.UK,
        "expected_device_name": "WH Unknown",
        "expected_entity_prefix": "UK_",
        "sample_entity": "unknown_sensor",
        "expected_entity_id": "sensor.uk_wh_unknown_sensor",
    },
    DEVICES.IO: {
        "device_key": DEVICES.IO,
        "expected_device_name": "WH Eingänge/Ausgänge",
        "expected_entity_prefix": "IO_",
        "sample_entity": "input_state",
        "expected_entity_id": "sensor.io_wh_input_state",
    },
}


@pytest.fixture
def mock_config_entry() -> MyConfigEntry:
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


def create_test_modbus_item(device: str, name: str, translation_key: str) -> ModbusItem:
    """Create a test ModbusItem for testing."""
    return ModbusItem(
        address=1000,
        name=name,
        mformat="number",
        mtype="Sensor",
        device=device,
        translation_key=translation_key,
        params={"unit": "°C", "step": 1, "divider": 1},
    )


class TestDeviceNaming:
    """Test device naming for all device types."""

    @pytest.mark.parametrize(
        "device_data", DEVICE_TEST_DATA.values(), ids=DEVICE_TEST_DATA.keys()
    )
    def test_device_names_constant_mapping(self, device_data):
        """Test that device constants map to correct device names."""
        device_key = device_data["device_key"]
        expected_name = device_data["expected_device_name"]

        # Get the device name from DEVICENAMES constant
        device_name_attr = device_key.replace("dev_", "").upper()
        if device_name_attr == "WAERMEERZEUGER2":
            device_name_attr = "W2"
        elif device_name_attr == "WAERMEPUMPE":
            device_name_attr = "WP"
        elif device_name_attr == "WARMWASSER":
            device_name_attr = "WW"
        elif device_name_attr == "HEIZKREIS":
            device_name_attr = "HZ"
        elif device_name_attr == "HEIZKREIS2":
            device_name_attr = "HZ2"
        elif device_name_attr == "HEIZKREIS3":
            device_name_attr = "HZ3"
        elif device_name_attr == "HEIZKREIS4":
            device_name_attr = "HZ4"
        elif device_name_attr == "HEIZKREIS5":
            device_name_attr = "HZ5"
        elif device_name_attr == "EIN_AUS":
            device_name_attr = "IO"
        elif device_name_attr == "SYSTEM":
            device_name_attr = "SYS"
        elif device_name_attr == "STATISTIK":
            device_name_attr = "ST"
        elif device_name_attr == "UNKNOWN":
            device_name_attr = "UK"

        actual_name = getattr(DEVICENAMES, device_name_attr, None)
        assert actual_name == expected_name, (
            f"Device {device_key} should map to '{expected_name}', got '{actual_name}'"
        )

    @pytest.mark.parametrize(
        "device_data", DEVICE_TEST_DATA.values(), ids=DEVICE_TEST_DATA.keys()
    )
    def test_device_info_generation(
        self, device_data, mock_config_entry, mock_modbus_api
    ):
        """Test device info generation for each device type."""
        device_key = device_data["device_key"]
        sample_entity = device_data["sample_entity"]

        # Create a test ModbusItem
        modbus_item = create_test_modbus_item(
            device=device_key, name=sample_entity, translation_key=sample_entity
        )

        # Create entity
        entity = MyEntity(mock_config_entry, modbus_item, mock_modbus_api)

        # Get device info
        device_info = entity.device_info

        # Verify device info structure
        assert device_info is not None
        assert "identifiers" in device_info
        identifiers = list(device_info["identifiers"])
        assert len(identifiers) > 0
        assert CONST.DOMAIN in identifiers[0]
        assert device_key in identifiers[0][1]
        assert device_info.get("translation_key") == device_key
        assert device_info.get("manufacturer") == "Weishaupt"


class TestEntityNaming:
    """Test entity naming for all device types."""

    @pytest.mark.parametrize(
        "device_data", DEVICE_TEST_DATA.values(), ids=DEVICE_TEST_DATA.keys()
    )
    def test_entity_unique_id_generation(
        self, device_data, mock_config_entry, mock_modbus_api
    ):
        """Test unique ID generation for entities."""
        device_key = device_data["device_key"]
        sample_entity = device_data["sample_entity"]

        # Create a test ModbusItem
        modbus_item = create_test_modbus_item(
            device=device_key, name=sample_entity, translation_key=sample_entity
        )

        # Create entity
        entity = MyEntity(mock_config_entry, modbus_item, mock_modbus_api)

        # Verify unique ID is generated
        assert entity.unique_id is not None
        assert len(entity.unique_id) > 0

        # Unique ID should contain prefix and entity name
        expected_prefix = mock_config_entry.data[CONF.PREFIX]
        assert expected_prefix in entity.unique_id
        assert sample_entity in entity.unique_id

    @pytest.mark.parametrize(
        "device_data", DEVICE_TEST_DATA.values(), ids=DEVICE_TEST_DATA.keys()
    )
    def test_entity_translation_attributes(
        self, device_data, mock_config_entry, mock_modbus_api
    ):
        """Test entity translation key and placeholders."""
        device_key = device_data["device_key"]
        sample_entity = device_data["sample_entity"]
        expected_prefix = device_data["expected_entity_prefix"]

        # Create a test ModbusItem
        modbus_item = create_test_modbus_item(
            device=device_key, name=sample_entity, translation_key=sample_entity
        )

        # Create entity
        entity = MyEntity(mock_config_entry, modbus_item, mock_modbus_api)

        # Verify translation attributes
        assert entity.translation_key == sample_entity
        assert entity.translation_placeholders is not None
        assert "prefix" in entity.translation_placeholders

        # Verify prefix contains expected device prefix and device prefix setting
        prefix_value = entity.translation_placeholders["prefix"]
        assert expected_prefix in prefix_value
        if mock_config_entry.data[CONF.NAME_DEVICE_PREFIX]:
            assert mock_config_entry.data[CONF.PREFIX] in prefix_value


class TestEntityNamingWithPostfix:
    """Test entity naming with device postfix."""

    def test_entity_naming_with_postfix(self, mock_modbus_api):
        """Test entity naming when device postfix is configured."""
        # Config with postfix
        config_entry = Mock()
        config_entry.data = {
            CONF.HOST: "192.168.1.100",
            CONF.PORT: 502,
            CONF.PREFIX: "wh",
            CONF.DEVICE_POSTFIX: "test",
            CONF.NAME_DEVICE_PREFIX: True,
            CONF.NAME_TOPIC_PREFIX: True,
        }
        config_entry.entry_id = "test_entry_id"

        # Create a test ModbusItem for W2 device (as per example)
        modbus_item = create_test_modbus_item(
            device=DEVICES.W2, name="grenztemperatur", translation_key="grenztemperatur"
        )

        # Create entity
        entity = MyEntity(config_entry, modbus_item, mock_modbus_api)

        # Verify device info includes postfix
        device_info = entity.device_info
        assert device_info is not None
        assert "identifiers" in device_info
        identifiers = list(device_info["identifiers"])
        assert len(identifiers) > 0
        # The device identifier should contain the device key with postfix
        device_identifier = identifiers[0][1]
        assert device_identifier == f"{DEVICES.W2}_test"

    def test_entity_naming_without_prefixes(self, mock_modbus_api):
        """Test entity naming when prefixes are disabled."""
        # Config without prefixes
        config_entry = Mock()
        config_entry.data = {
            CONF.HOST: "192.168.1.100",
            CONF.PORT: 502,
            CONF.PREFIX: "wh",
            CONF.DEVICE_POSTFIX: "",
            CONF.NAME_DEVICE_PREFIX: False,
            CONF.NAME_TOPIC_PREFIX: False,
        }
        config_entry.entry_id = "test_entry_id"

        # Create a test ModbusItem
        modbus_item = create_test_modbus_item(
            device=DEVICES.W2, name="grenztemperatur", translation_key="grenztemperatur"
        )

        # Create entity
        entity = MyEntity(config_entry, modbus_item, mock_modbus_api)

        # Verify translation placeholders
        prefix_value = entity.translation_placeholders["prefix"]
        # Should be empty when both prefixes are disabled
        assert prefix_value == ""


class TestSpecificEntityExample:
    """Test the specific example from the user request."""

    def test_w2_grenztemperatur_entity(self, mock_modbus_api):
        """Test the specific example: number.wh_2_warmeerzeuger_grenztemperatur."""
        # Config that would generate the expected entity ID
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

        # Create ModbusItem for grenztemperatur on W2 device
        modbus_item = create_test_modbus_item(
            device=DEVICES.W2, name="grenztemperatur", translation_key="grenztemp"
        )

        # Create entity
        entity = MyEntity(config_entry, modbus_item, mock_modbus_api)

        # Verify device info
        device_info = entity.device_info
        assert device_info is not None
        assert device_info.get("translation_key") == DEVICES.W2

        # Verify entity translation attributes
        assert entity.translation_key == "grenztemp"
        prefix_value = entity.translation_placeholders["prefix"]
        # Should contain W2_ (topic prefix) + wh_ (device prefix)
        assert "W2_" in prefix_value
        assert "wh_" in prefix_value

        # Verify unique ID contains expected elements
        assert entity.unique_id is not None
        assert "wh" in entity.unique_id
        assert "grenztemperatur" in entity.unique_id

    def test_device_name_constants_completeness(self):
        """Test that all device constants have corresponding device names."""
        device_attrs = [attr for attr in dir(DEVICES) if not attr.startswith("_")]

        for device_attr in device_attrs:
            device_key = getattr(DEVICES, device_attr)

            # Map device key to device name attribute
            if device_key == DEVICES.SYS:
                name_attr = "SYS"
            elif device_key == DEVICES.WP:
                name_attr = "WP"
            elif device_key == DEVICES.WW:
                name_attr = "WW"
            elif device_key == DEVICES.HZ:
                name_attr = "HZ"
            elif device_key == DEVICES.HZ2:
                name_attr = "HZ2"
            elif device_key == DEVICES.HZ3:
                name_attr = "HZ3"
            elif device_key == DEVICES.HZ4:
                name_attr = "HZ4"
            elif device_key == DEVICES.HZ5:
                name_attr = "HZ5"
            elif device_key == DEVICES.W2:
                name_attr = "W2"
            elif device_key == DEVICES.ST:
                name_attr = "ST"
            elif device_key == DEVICES.UK:
                name_attr = "UK"
            elif device_key == DEVICES.IO:
                name_attr = "IO"
            elif device_key == DEVICES.WIH:
                # Special case - this might not have a corresponding device name
                continue
            else:
                pytest.fail(f"Unknown device key: {device_key}")

            # Verify the device name exists
            assert hasattr(DEVICENAMES, name_attr), (
                f"Missing device name for {device_key}"
            )
            device_name = getattr(DEVICENAMES, name_attr)
            assert device_name is not None and device_name != "", (
                f"Empty device name for {device_key}"
            )
