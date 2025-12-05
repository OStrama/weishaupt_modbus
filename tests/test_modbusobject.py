"""Unit tests for modbusobject module."""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from pymodbus import ModbusException

from custom_components.weishaupt_modbus.const import CONF, FORMATS, TYPES
from custom_components.weishaupt_modbus.items import ModbusItem
from custom_components.weishaupt_modbus.modbusobject import (
    BACKOFF_BASE_SECONDS,
    BACKOFF_MAX_SECONDS,
    BACKOFF_THRESHOLD_FAILURES,
    ModbusAPI,
    ModbusObject,
)


@pytest.fixture
def mock_config_entry():
    """Create a mock config entry."""
    config_entry = MagicMock()
    config_entry.data = {
        CONF.HOST: "192.168.1.100",
        CONF.PORT: 502,
    }
    return config_entry


@pytest.fixture
def modbus_api(mock_config_entry):
    """Create a ModbusAPI instance."""
    with patch("custom_components.weishaupt_modbus.modbusobject.AsyncModbusTcpClient"):
        return ModbusAPI(mock_config_entry)


@pytest.fixture
def mock_modbus_item():
    """Create a mock ModbusItem."""
    item = MagicMock(spec=ModbusItem)
    item.address = 1000
    item.name = "test_sensor"
    item.translation_key = "test_sensor"
    item.format = FORMATS.TEMPERATURE
    item.type = TYPES.SENSOR
    item.is_invalid = False
    return item


class TestModbusAPI:
    """Test ModbusAPI class."""

    def test_init(self, modbus_api, mock_config_entry):
        """Test ModbusAPI initialization."""
        assert modbus_api._ip == mock_config_entry.data[CONF.HOST]
        assert modbus_api._port == mock_config_entry.data[CONF.PORT]
        assert modbus_api._connect_pending is False
        assert modbus_api._failed_reconnect_counter == 0

    @pytest.mark.asyncio
    async def test_connect_success(self, modbus_api):
        """Test successful connection."""
        modbus_api._modbus_client.connect = AsyncMock()
        modbus_api._modbus_client.connected = True

        result = await modbus_api.connect()

        assert result is True
        assert modbus_api._failed_reconnect_counter == 0
        modbus_api._modbus_client.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, modbus_api):
        """Test failed connection."""
        modbus_api._modbus_client.connect = AsyncMock()
        modbus_api._modbus_client.connected = False
        modbus_api._modbus_client.close = MagicMock()

        result = await modbus_api.connect()

        assert result is False
        assert modbus_api._failed_reconnect_counter == 1

    @pytest.mark.asyncio
    async def test_connect_modbus_exception(self, modbus_api):
        """Test connection with ModbusException."""
        modbus_api._modbus_client.connect = AsyncMock(
            side_effect=ModbusException("Connection failed")
        )
        modbus_api._modbus_client.close = MagicMock()

        result = await modbus_api.connect()

        assert result is False
        assert modbus_api._failed_reconnect_counter == 1

    @pytest.mark.asyncio
    async def test_connect_pending(self, modbus_api):
        """Test connection when already pending."""
        modbus_api._connect_pending = True
        modbus_api._modbus_client.connected = True

        result = await modbus_api.connect()

        assert result is True

    @pytest.mark.asyncio
    async def test_exponential_backoff(self, modbus_api):
        """Test exponential backoff after multiple failures."""
        modbus_api._modbus_client.connect = AsyncMock()
        modbus_api._modbus_client.connected = False
        modbus_api._modbus_client.close = MagicMock()

        # Fail 3 times to trigger backoff
        for _ in range(BACKOFF_THRESHOLD_FAILURES):
            result = await modbus_api.connect()
            assert result is False

        assert modbus_api._failed_reconnect_counter == BACKOFF_THRESHOLD_FAILURES

        # Next attempt should be blocked by backoff
        with patch("asyncio.get_running_loop") as mock_loop:
            mock_loop.return_value.time.return_value = 0
            modbus_api._last_connection_try = 0
            result = await modbus_api.connect()
            # Should return False due to backoff
            assert result is False

    def test_close(self, modbus_api):
        """Test closing connection."""
        modbus_api._modbus_client.close = MagicMock()

        modbus_api.close()

        modbus_api._modbus_client.close.assert_called_once()

    def test_get_device(self, modbus_api):
        """Test get_device returns client."""
        device = modbus_api.get_device()
        assert device == modbus_api._modbus_client


class TestModbusObject:
    """Test ModbusObject class."""

    def test_init(self, modbus_api, mock_modbus_item):
        """Test ModbusObject initialization."""
        obj = ModbusObject(modbus_api, mock_modbus_item)

        assert obj._modbus_item == mock_modbus_item
        assert obj._modbus_client == modbus_api.get_device()
        assert obj._no_connect_warn is False

    def test_check_temperature_valid(self, modbus_api, mock_modbus_item):
        """Test temperature validation with valid value."""
        obj = ModbusObject(modbus_api, mock_modbus_item)

        result = obj.check_temperature(250)  # 25.0°C

        assert result == 250
        assert mock_modbus_item.is_invalid is False

    def test_check_temperature_no_sensor(self, modbus_api, mock_modbus_item):
        """Test temperature validation with no sensor."""
        obj = ModbusObject(modbus_api, mock_modbus_item)

        result = obj.check_temperature(-32768)

        assert result is None
        assert mock_modbus_item.is_invalid is True

    def test_check_temperature_broken_sensor(self, modbus_api, mock_modbus_item):
        """Test temperature validation with broken sensor."""
        obj = ModbusObject(modbus_api, mock_modbus_item)

        result = obj.check_temperature(-32767)

        assert result == -999
        assert mock_modbus_item.is_invalid is False

    def test_check_temperature_negative(self, modbus_api, mock_modbus_item):
        """Test temperature validation with negative value."""
        obj = ModbusObject(modbus_api, mock_modbus_item)

        # Test two's complement conversion
        result = obj.check_temperature(65436)  # -10.0°C in two's complement

        assert result == -100
        assert mock_modbus_item.is_invalid is False

    def test_check_percentage_valid(self, modbus_api, mock_modbus_item):
        """Test percentage validation with valid value."""
        mock_modbus_item.format = FORMATS.PERCENTAGE
        obj = ModbusObject(modbus_api, mock_modbus_item)

        result = obj.check_percentage(50)

        assert result == 50
        assert mock_modbus_item.is_invalid is False

    def test_check_percentage_invalid(self, modbus_api, mock_modbus_item):
        """Test percentage validation with invalid value."""
        mock_modbus_item.format = FORMATS.PERCENTAGE
        obj = ModbusObject(modbus_api, mock_modbus_item)

        result = obj.check_percentage(65535)

        assert result is None
        assert mock_modbus_item.is_invalid is True

    def test_check_status(self, modbus_api, mock_modbus_item):
        """Test status validation."""
        mock_modbus_item.format = FORMATS.STATUS
        obj = ModbusObject(modbus_api, mock_modbus_item)

        result = obj.check_status(1)

        assert result == 1
        assert mock_modbus_item.is_invalid is False

    @pytest.mark.asyncio
    async def test_get_value_success(self, modbus_api, mock_modbus_item):
        """Test getting value successfully."""
        obj = ModbusObject(modbus_api, mock_modbus_item)
        obj._modbus_client.connected = True

        mock_response = MagicMock()
        mock_response.isError.return_value = False
        mock_response.registers = [250]

        obj._modbus_client.read_input_registers = AsyncMock(return_value=mock_response)

        result = await obj.get_value()

        assert result == 250

    @pytest.mark.asyncio
    async def test_get_value_not_connected(self, modbus_api, mock_modbus_item):
        """Test getting value when not connected."""
        obj = ModbusObject(modbus_api, mock_modbus_item)
        obj._modbus_client.connected = False

        result = await obj.get_value()

        assert result is None

    @pytest.mark.asyncio
    async def test_get_value_holding_register(self, modbus_api, mock_modbus_item):
        """Test getting value from holding register."""
        mock_modbus_item.type = TYPES.NUMBER
        obj = ModbusObject(modbus_api, mock_modbus_item)
        obj._modbus_client.connected = True

        mock_response = MagicMock()
        mock_response.isError.return_value = False
        mock_response.registers = [100]

        obj._modbus_client.read_holding_registers = AsyncMock(
            return_value=mock_response
        )

        result = await obj.get_value()

        assert result == 100

    @pytest.mark.asyncio
    async def test_set_value_success(self, modbus_api, mock_modbus_item):
        """Test setting value successfully."""
        mock_modbus_item.type = TYPES.NUMBER
        obj = ModbusObject(modbus_api, mock_modbus_item)
        obj._modbus_client.connected = True
        obj._modbus_client.write_register = AsyncMock()

        await obj.set_value(100)

        obj._modbus_client.write_register.assert_called_once_with(
            mock_modbus_item.address, 100, device_id=1
        )

    @pytest.mark.asyncio
    async def test_set_value_readonly(self, modbus_api, mock_modbus_item):
        """Test setting value on read-only sensor."""
        mock_modbus_item.type = TYPES.SENSOR
        obj = ModbusObject(modbus_api, mock_modbus_item)
        obj._modbus_client.connected = True
        obj._modbus_client.write_register = AsyncMock()

        await obj.set_value(100)

        # Should not write to read-only sensor
        obj._modbus_client.write_register.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_value_not_connected(self, modbus_api, mock_modbus_item):
        """Test setting value when not connected."""
        mock_modbus_item.type = TYPES.NUMBER
        obj = ModbusObject(modbus_api, mock_modbus_item)
        obj._modbus_client.connected = False
        obj._modbus_client.write_register = AsyncMock()

        await obj.set_value(100)

        # Should not attempt write when not connected
        obj._modbus_client.write_register.assert_not_called()

    def test_check_valid_response_temperature(self, modbus_api, mock_modbus_item):
        """Test response validation for temperature."""
        obj = ModbusObject(modbus_api, mock_modbus_item)

        # Negative temperature should be converted to two's complement
        result = obj.check_valid_response(-100)

        assert result == 65436

    def test_check_valid_response_other(self, modbus_api, mock_modbus_item):
        """Test response validation for non-temperature."""
        mock_modbus_item.format = FORMATS.STATUS
        obj = ModbusObject(modbus_api, mock_modbus_item)

        result = obj.check_valid_response(100)

        assert result == 100


class TestConstants:
    """Test module constants."""

    def test_backoff_constants(self):
        """Test backoff constants are defined correctly."""
        assert BACKOFF_BASE_SECONDS == 300  # 5 minutes
        assert BACKOFF_MAX_SECONDS == 3600  # 60 minutes
        assert BACKOFF_THRESHOLD_FAILURES == 3
