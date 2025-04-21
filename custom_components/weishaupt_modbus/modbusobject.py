"""Modbusobject.

A Modbus object that contains a Modbus item and communicates with the Modbus.
It contains a ModbusClient for setting and getting Modbus register values
"""

import asyncio
import logging

from pymodbus import ExceptionResponse, ModbusException
from pymodbus.client import AsyncModbusTcpClient

from .configentry import MyConfigEntry
from .const import CONF, FORMATS, TYPES
from .items import ModbusItem

logging.basicConfig()
log = logging.getLogger(__name__)


class ModbusAPI:
    """ModbusAPI class provides a connection to the modbus, which is used by the ModbusItems."""

    def __init__(self, config_entry: MyConfigEntry) -> None:
        """Construct ModbusAPI.

        :param config_entry: HASS config entry
        :type config_entry: MyConfigEntry
        """
        self._ip = config_entry.data[CONF.HOST]
        self._port = config_entry.data[CONF.PORT]
        self._modbus_client = None
        self._conneted = False
        self._connect_pending = False
        self._failed_reconnect_counter = 0
        self._modbus_client = AsyncModbusTcpClient(
            host=self._ip, port=self._port, name="Weishaupt_WBB"
        )

    async def connect(self, startup: bool = False):
        """Open modbus connection."""
        if self._connect_pending:
            log.debug("Connection to heatpump already pending")
            return self._modbus_client.connected
        try:
            self._connect_pending = True

            if self._failed_reconnect_counter >= 3 and not startup:
                log.warning(
                    "Connection to heatpump failed "
                    + str(self._failed_reconnect_counter)
                    + "times. Waiting 15 minutes"
                )
                await asyncio.sleep(120)
            for _useless in range(2):
                await self._modbus_client.connect()
                if self._modbus_client.connected:
                    log.info("Connection to heatpump succeeded")
                    self.conneted = True
                    self._failed_reconnect_counter = 0
                    self._connect_pending = False
                    return self._modbus_client.connected
                else:
                    self.conneted = False
                self._failed_reconnect_counter += 1
                await asyncio.sleep(1)
            self._connect_pending = False
        except ModbusException:
            log.warning("Connection to heatpump failed")
            self._failed_reconnect_counter += 1
            self._connect_pending = False
            return None
        self._connect_pending = False
        return self._modbus_client.connected

    def close(self):
        """Close modbus connection."""
        try:
            self._modbus_client.close()
        except ModbusException:
            log.warning("Closing connection to heat pump failed")
            return False
        log.info("Connection to heat pump closed")
        return True

    def get_device(self):
        """Return modbus connection."""
        return self._modbus_client


class ModbusObject:
    """ModbusObject.

    A Modbus object that contains a Modbus item and communicates with the Modbus.
    It contains a ModbusClient for setting and getting Modbus register values
    """

    def __init__(self, modbus_api: ModbusAPI, modbus_item: ModbusItem) -> None:
        """Construct ModbusObject.

        :param modbus_api: The modbus API
        :type modbus_api: ModbusAPI
        :param modbus_item: definition of modbus item
        :type modbus_item: ModbusItem
        """
        self._modbus_item = modbus_item
        self._modbus_client = modbus_api.get_device()

    def check_valid_result(self, val) -> int:
        """Check if item is available and valid."""
        match self._modbus_item.format:
            case FORMATS.TEMPERATUR:
                return self.check_temperature(val)
            case FORMATS.PERCENTAGE:
                return self.check_percentage(val)
            case FORMATS.STATUS:
                return self.check_status(val)
            case _:
                self._modbus_item.is_invalid = False
                return val

    def check_temperature(self, val) -> int:
        """Check availability of temperature item and translate return value to valid int.

        :param val: The value from the modbus
        :type val: int
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

    def check_percentage(self, val) -> int:
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
            case FORMATS.TEMPERATUR:
                if val < 0:
                    val = val + 65536
                return val
            case _:
                return val

    def validate_modbus_answer(self, mbr) -> int:
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
                log.warning(
                    "Received Modbus library error: %s in item: %s",
                    str(mbr),
                    str(self._modbus_item.name),
                )
            return None
        if isinstance(mbr, ExceptionResponse):
            log.warning(
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
    async def value(self):
        """Returns the value from the modbus register."""
        if self._modbus_client is None:
            return None
        if not self._modbus_item.is_invalid:
            try:
                match self._modbus_item.type:
                    case TYPES.SENSOR | TYPES.SENSOR_CALC:
                        # Sensor entities are read-only
                        mbr = await self._modbus_client.read_input_registers(
                            self._modbus_item.address, slave=1
                        )
                        return self.validate_modbus_answer(mbr)
                    case TYPES.SELECT | TYPES.NUMBER | TYPES.NUMBER_RO:
                        mbr = await self._modbus_client.read_holding_registers(
                            self._modbus_item.address, slave=1
                        )
                        return self.validate_modbus_answer(mbr)
                    case _:
                        log.warning(
                            "Unknown Sensor type: %s in %s",
                            str(self._modbus_item.type),
                            str(self._modbus_item.name),
                        )
                        return None
            except ModbusException as exc:
                log.warning(
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
                        slave=1,
                    )
        except ModbusException:
            log.warning(
                "ModbusException: Writing %s to %s (%s) failed",
                str(value),
                str(self._modbus_item.name),
                str(self._modbus_item.address),
            )
            return
