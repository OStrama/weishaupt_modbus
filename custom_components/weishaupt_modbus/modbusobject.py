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

# Connection backoff constants
BACKOFF_BASE_SECONDS = 5 * 60  # 5 minutes
BACKOFF_MAX_SECONDS = 60 * 60  # 60 minutes
BACKOFF_THRESHOLD_FAILURES = 3


class ModbusAPI:
    """ModbusAPI class provides a connection to the modbus, which is used by the ModbusItems."""

    def __init__(self, config_entry: MyConfigEntry) -> None:
        """Construct ModbusAPI.

        Args:
            config_entry: HASS config entry

        """
        self._ip: str = config_entry.data[CONF.HOST]
        self._port: int = config_entry.data[CONF.PORT]
        self._connect_pending: bool = False
        self._failed_reconnect_counter: int = 0
        self._last_connection_try: Any = None
        self._modbus_client: AsyncModbusTcpClient = AsyncModbusTcpClient(
            host=self._ip, port=self._port, name="Weishaupt_WBB", retries=1
        )

    def _log_backoff_start(self) -> None:
        """Log when exponential backoff starts."""
        _LOGGER.warning(
            "Connection to heatpump failed %s times. "
            "Starting exponential backoff (min %s seconds)",
            self._failed_reconnect_counter,
            BACKOFF_BASE_SECONDS,
        )

    async def connect(self, startup: bool = False) -> bool:
        """Open modbus connection."""
        if self._connect_pending:
            _LOGGER.warning("Connection to heatpump already pending")
            return self._modbus_client.connected

        self._connect_pending = True
        try:
            loop = asyncio.get_running_loop()
            now = loop.time()

            # ----- Exponential backoff calculation -----
            # We only back off after BACKOFF_THRESHOLD_FAILURES failed attempts (and not during startup).
            backoff = 0.0
            if (
                self._failed_reconnect_counter >= BACKOFF_THRESHOLD_FAILURES
                and not startup
            ):
                # fail_count = 3 → 1x base
                # fail_count = 4 → 2x base
                # fail_count = 5 → 4x base
                # etc, capped at max_backoff
                exp = self._failed_reconnect_counter - BACKOFF_THRESHOLD_FAILURES
                backoff = BACKOFF_BASE_SECONDS * (2**exp)
                backoff = min(backoff, BACKOFF_MAX_SECONDS)

            if backoff > 0 and self._last_connection_try is not None and not startup:
                elapsed = now - self._last_connection_try
                if elapsed < backoff:
                    remaining = backoff - elapsed
                    _LOGGER.debug(
                        "Skipping connect attempt: still in backoff window "
                        "(%.0f s remaining, backoff %.0f s for %s failures)",
                        remaining,
                        backoff,
                        self._failed_reconnect_counter,
                    )
                    return False
                # We've waited long enough, log that we are trying again
                _LOGGER.info(
                    "Backoff period (%.0f s) expired after %s failures. "
                    "Retrying connection to heatpump now",
                    backoff,
                    self._failed_reconnect_counter,
                )

            # Record this attempt time
            self._last_connection_try = now

            # ----- Actual connect attempt -----
            await self._modbus_client.connect()

            if self._modbus_client.connected:
                # SUCCESS
                if self._failed_reconnect_counter > 0:
                    _LOGGER.info(
                        "Successfully reconnected to heatpump after %s failed attempts",
                        self._failed_reconnect_counter,
                    )
                else:
                    _LOGGER.info("Successfully connected to heatpump")
                self._failed_reconnect_counter = 0
                return True

            # Connect() returned but not connected → count as failure
            self._failed_reconnect_counter += 1
            if (
                self._failed_reconnect_counter == BACKOFF_THRESHOLD_FAILURES
                and not startup
            ):
                self._log_backoff_start()
            else:
                self._modbus_client.close()
                return False

        except ModbusException as exc:
            _LOGGER.warning(
                "Connection to heatpump failed (modbus): %s",
                str(exc),
            )
            self._failed_reconnect_counter += 1
            if (
                self._failed_reconnect_counter == BACKOFF_THRESHOLD_FAILURES
                and not startup
            ):
                self._log_backoff_start()
            self._modbus_client.close()
            return False

        except (TimeoutError, OSError, ConnectionError) as exc:
            # Catch expected connection errors so state stays clean
            _LOGGER.warning(
                "Connection to heatpump failed (network): %s",
                str(exc),
            )
            self._failed_reconnect_counter += 1
            if (
                self._failed_reconnect_counter == BACKOFF_THRESHOLD_FAILURES
                and not startup
            ):
                self._log_backoff_start()
            try:  # noqa: SIM105
                self._modbus_client.close()
            except Exception:  # noqa: BLE001
                pass
            return False

        except Exception as exc:  # noqa: BLE001
            # Catch any other unexpected errors as last resort
            _LOGGER.warning(
                "Connection to heatpump failed (unexpected): %s",
                str(exc),
            )
            self._failed_reconnect_counter += 1
            if (
                self._failed_reconnect_counter == BACKOFF_THRESHOLD_FAILURES
                and not startup
            ):
                self._log_backoff_start()
            try:  # noqa: SIM105
                self._modbus_client.close()
            except Exception:  # noqa: BLE001
                pass
            return False

        finally:
            # Always clear pending flag, even if we were cancelled
            self._connect_pending = False

    def close(self) -> None:
        """Close modbus connection."""
        try:
            self._modbus_client.close()
            _LOGGER.info("Connection to heatpump closed")
        except ModbusException as exc:
            _LOGGER.warning("Closing connection to heatpump failed: %s", str(exc))

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

    def check_percentage(self, val: int) -> int | None:
        """Check availability of percentage item and translate return value to valid int.

        Args:
            val: The value from the modbus

        Returns:
            Processed percentage value or None if invalid

        """
        if val == 65535:
            self._modbus_item.is_invalid = True
            return None
        self._modbus_item.is_invalid = False
        return val

    def check_status(self, val: int) -> int:
        """Check general availability of item.

        Args:
            val: The value from the modbus

        Returns:
            The status value

        """
        self._modbus_item.is_invalid = False
        return val

    def check_valid_response(self, val: int) -> int:
        """Check if item is valid to write.

        Args:
            val: The value to validate

        Returns:
            Validated value ready for writing to modbus

        """
        match self._modbus_item.format:
            case FORMATS.TEMPERATURE:
                if val < 0:
                    val = val + 65536
                return val
            case _:
                return val

    def validate_modbus_answer(self, mbr: Any) -> int | None:
        """Check if there's a valid answer from modbus and translate it to a valid int depending from type.

        Args:
            mbr: The modbus response

        Returns:
            Validated integer value or None if invalid

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

    async def get_value(self) -> int | None:
        """Return the value from the modbus register."""
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

    async def set_value(self, value: int) -> None:
        """Set the value of the modbus register, does nothing when not R/W.

        Args:
            value: The value to write to the modbus

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
