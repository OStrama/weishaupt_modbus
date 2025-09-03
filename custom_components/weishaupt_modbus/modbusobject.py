"""Modbusobject.

A Modbus object that contains a Modbus item and communicates with the Modbus.
It contains a ModbusClient for setting and getting Modbus register values
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pymodbus import ExceptionResponse, ModbusException
from pymodbus.client import AsyncModbusTcpClient

from .configentry import MyConfigEntry
from .const import CONF, FORMATS, TYPES
from .items import ModbusItem

_LOGGER = logging.getLogger(__name__)


class ModbusAPI:
    """ModbusAPI class provides a connection to the modbus, which is used by the ModbusItems."""

    def __init__(self, config_entry: MyConfigEntry) -> None:
        """Construct ModbusAPI.

        Args:
            config_entry: HASS config entry

        """
        self._ip: str = config_entry.data[CONF.HOST]
        self._port: int = config_entry.data[CONF.PORT]
        self._connected: bool = False
        self._connect_pending: bool = False
        self._failed_reconnect_counter: int = 0
        self._last_connection_try: Any = None
        self._modbus_client: AsyncModbusTcpClient = AsyncModbusTcpClient(
            host=self._ip, port=self._port, name="Weishaupt_WBB", retries=1
        )

    async def connect(self, startup: bool = False) -> bool:
        """Open modbus connection."""
        if self._connect_pending:
            _LOGGER.warning("Connection to heatpump already pending")
            return self._modbus_client.connected
        try:
            self._connect_pending = True
            if self._failed_reconnect_counter >= 3 and not startup:
                _LOGGER.warning(
                    "Connection to heatpump failed %s times. Waiting 15 minutes",
                    str(self._failed_reconnect_counter),
                )
                await asyncio.sleep(300)
            await self._modbus_client.connect()
            if self._modbus_client.connected:
                # _LOGGER.warning("Connection to heatpump succeeded")
                self._failed_reconnect_counter = 0
                self._connect_pending = False
                return self._modbus_client.connected
            self._failed_reconnect_counter += 1
            self._connect_pending = False
            self._modbus_client.close()
            return self._modbus_client.connected  # noqa: TRY300

        except ModbusException:
            _LOGGER.warning("Connection to heatpump failed")
            self._failed_reconnect_counter += 1
            self._connect_pending = False
            self._modbus_client.close()
            return self._modbus_client.connected

    def close(self) -> bool:
        """Close modbus connection."""
        try:
            self._modbus_client.close()
        except ModbusException:
            _LOGGER.warning("Closing connection to heat pump failed")
            return False
        _LOGGER.info("Connection to heat pump closed")
        return True

    def get_device(self) -> AsyncModbusTcpClient:
        """Return modbus connection."""
        return self._modbus_client


class ModbusObject:
    """ModbusObject.

    A Modbus object that contains a Modbus item and communicates with the Modbus.
    It contains a ModbusClient for setting and getting Modbus register values
    """

    def __init__(
        self,
        modbus_api: ModbusAPI,
        modbus_item: ModbusItem,
        no_connect_warn: bool = False,
    ) -> None:
        """Construct ModbusObject.

        Args:
            modbus_api: The modbus API
            modbus_item: definition of modbus item
            no_connect_warn: suppress connection warnings

        """
        self._modbus_item: ModbusItem = modbus_item
        self._modbus_client: AsyncModbusTcpClient = modbus_api.get_device()
        self._no_connect_warn: bool = no_connect_warn

    def check_valid_result(self, val: int) -> int | None:
        """Check if item is available and valid."""
        match self._modbus_item.format:
            case FORMATS.TEMPERATURE:
                return self.check_temperature(val)
            case FORMATS.PERCENTAGE:
                return self.check_percentage(val)
            case FORMATS.STATUS:
                return self.check_status(val)
            case _:
                self._modbus_item.is_invalid = False
                return val

    def check_temperature(self, val: int) -> int | None:
        """Check availability of temperature item and translate return value to valid int.

        Args:
            val: The value from the modbus

        Returns:
            Processed temperature value or None if invalid

        """
        match val:
            case -32768:
                # No Sensor installed, remove it from the list
                self._modbus_item.is_invalid = True
                return None
            case 32768:
                # This seems to be zero, should be allowed
                self._modbus_item.is_invalid = True
                return None
            case -32767:
                # Sensor broken set return value to -99.9 to inform user
                self._modbus_item.is_invalid = False
                return -999
            case _:
                # Temperature Sensor seems to be Einerkomplement
                if val > 32768:
                    val = val - 65536
                self._modbus_item.is_invalid = False
                return val

    def check_percentage(self, val) -> int | None:
        """Check availability of percentage item and translate.

        return value to valid int
        :param val: The value from the modbus
        :type val: int
        """
        if val == 65535:
            self._modbus_item.is_invalid = True
            return None
        self._modbus_item.is_invalid = False
        return val

    def check_status(self, val) -> int:
        """Check general availability of item."""
        self._modbus_item.is_invalid = False
        return val

    def check_valid_response(self, val) -> int:
        """Check if item is valid to write."""
        match self._modbus_item.format:
            case FORMATS.TEMPERATURE:
                if val < 0:
                    val = val + 65536
                return val
            case _:
                return val

    def validate_modbus_answer(self, mbr) -> int | None:
        """Check if there's a valid answer from modbus and translate it to a valid int depending from type.

        :param mbr: The modbus response
        :type mbr: modbus response
        """
        val = None
        if mbr.isError():
            myexception_code: ExceptionResponse = mbr
            if myexception_code.exception_code == 2:
                self._modbus_item.is_invalid = True
            else:
                _LOGGER.warning(
                    "Received Modbus library error: %s in item: %s",
                    str(mbr),
                    str(self._modbus_item.name),
                )
            return None
        if isinstance(mbr, ExceptionResponse):
            _LOGGER.warning(
                "Received ModbusException: %s from library in item: %s",
                str(mbr),
                str(self._modbus_item.name),
            )
            return None
            # THIS IS NOT A PYTHON EXCEPTION, but a valid modbus message
        if len(mbr.registers) > 0:
            val = self.check_valid_result(mbr.registers[0])
        return val

    @property
    async def value(self) -> int | None:
        """Returns the value from the modbus register."""
        if self._modbus_client is None:
            return None
        if self._modbus_client.connected is False:
            # on first check_availability call connection still not available, suppress warning
            if self._no_connect_warn is True:
                return None
            _LOGGER.warning(
                "Try to get value for %s without connection",
                self._modbus_item.translation_key,
            )
            return None
        if not self._modbus_item.is_invalid:
            try:
                match self._modbus_item.type:
                    case TYPES.SENSOR | TYPES.SENSOR_CALC:
                        # Sensor entities are read-only
                        mbr = await self._modbus_client.read_input_registers(
                            self._modbus_item.address, device_id=1
                        )
                        return self.validate_modbus_answer(mbr)
                    case TYPES.SELECT | TYPES.NUMBER | TYPES.NUMBER_RO:
                        mbr = await self._modbus_client.read_holding_registers(
                            self._modbus_item.address, device_id=1
                        )
                        return self.validate_modbus_answer(mbr)
                    case _:
                        _LOGGER.warning(
                            "Unknown Sensor type: %s in %s",
                            str(self._modbus_item.type),
                            str(self._modbus_item.name),
                        )
                        return None
            except ModbusException as exc:
                _LOGGER.warning(
                    "ModbusException: Reading %s in item: %s failed",
                    str(exc),
                    str(self._modbus_item.name),
                )
        return None

    # @value.setter
    async def setvalue(self, value) -> None:
        """Set the value of the modbus register, does nothing when not R/W.

        :param val: The value to write to the modbus
        :type val: int
        """
        if self._modbus_client is None:
            return
        if self._modbus_client.connected is False:
            return
        try:
            match self._modbus_item.type:
                case TYPES.SENSOR | TYPES.NUMBER_RO | TYPES.SENSOR_CALC:
                    # Sensor entities are read-only
                    return
                case _:
                    await self._modbus_client.write_register(
                        self._modbus_item.address,
                        self.check_valid_response(value),
                        device_id=1,
                    )
        except ModbusException:
            _LOGGER.warning(
                "ModbusException: Writing %s to %s (%s) failed",
                str(value),
                str(self._modbus_item.name),
                str(self._modbus_item.address),
            )
            return
