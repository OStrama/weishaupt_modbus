"""Modbus_API."""

import asyncio
import contextlib
import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

# Import only configuration constants from the local const file
from .const import (
    BACKOFF_BASE_SECONDS,
    BACKOFF_MAX_SECONDS,
    BACKOFF_THRESHOLD_FAILURES,
    DEFAULT_PORT,
    MAX_BLOCK_READ_COUNT,
)
from .exceptions import ConnectionFailedError, WriteError

# Import Modbus formatting models from local hpconst file
from .hpconst import DEVICELISTS, FORMATS, TYPES, ModbusItem

_LOGGER = logging.getLogger(__name__)


class WeishauptModbusClient:
    """Thread-safe, batch-reading Modbus TCP client with exponential backoff stability."""

    def __init__(
        self,
        host: str,
        port: int = DEFAULT_PORT,
        mcu_lock: asyncio.Lock | None = None,
    ) -> None:
        """Initialize the client with exact legacy parameters."""
        self._host = host
        self._port = port
        self._client = AsyncModbusTcpClient(
            host=self._host,
            port=self._port,
            name="Weishaupt_WBB",  # Legacy device name
            retries=1,  # Legacy retry setting
        )
        self._lock = mcu_lock if mcu_lock is not None else asyncio.Lock()

        # Raw register data cache used by entities to read their state
        self.data: dict[int, int | None] = {}
        self._items_dict: dict[int, ModbusItem] = {}

        # Connection and backoff tracking from ModbusAPI
        self._connect_pending: bool = False
        self._failed_reconnect_counter: int = 0
        self._last_connection_try: float | None = None

    @property
    def connected(self) -> bool:
        """Return True if currently connected."""
        return self._client.connected

    def get_value(self, address: int) -> int | None:
        """Get the cached raw integer value of a register by its address."""
        return self.data.get(address)

    def _log_backoff_start(self) -> None:
        """Log when exponential backoff starts."""
        _LOGGER.warning(
            "Connection to heatpump failed %s times. "
            "Starting exponential backoff (min %s seconds)",
            self._failed_reconnect_counter,
            BACKOFF_BASE_SECONDS,
        )

    async def connect(self, startup: bool = False) -> bool:
        """Establish connection to the heat pump with legacy backoff handling."""
        if self._client.connected:
            return True

        if self._connect_pending:
            _LOGGER.warning("Connection to heatpump already pending")
            return self._client.connected

        self._connect_pending = True
        try:
            loop = asyncio.get_running_loop()
            now = loop.time()

            # ----- Exponential backoff calculation -----
            backoff = 0.0
            if (
                self._failed_reconnect_counter >= BACKOFF_THRESHOLD_FAILURES
                and not startup
            ):
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
                _LOGGER.info(
                    "Backoff period (%.0f s) expired after %s failures. "
                    "Retrying connection to heatpump now",
                    backoff,
                    self._failed_reconnect_counter,
                )

            # Record this attempt time
            self._last_connection_try = now

            # ----- Actual connect attempt -----
            await self._client.connect()

            if self._client.connected:
                if self._failed_reconnect_counter > 0:
                    _LOGGER.info(
                        "Successfully reconnected to heatpump after %s failed attempts",
                        self._failed_reconnect_counter,
                    )
                else:
                    _LOGGER.info("Successfully connected to heatpump")
                self._failed_reconnect_counter = 0
                return True

            # Connect returned but connection failed
            self._failed_reconnect_counter += 1
            if (
                self._failed_reconnect_counter == BACKOFF_THRESHOLD_FAILURES
                and not startup
            ):
                self._log_backoff_start()
            self._client.close()
            return False

        except ModbusException as err:
            _LOGGER.warning("Connection to heatpump failed (modbus): %s", err)
            self._failed_reconnect_counter += 1
            if (
                self._failed_reconnect_counter == BACKOFF_THRESHOLD_FAILURES
                and not startup
            ):
                self._log_backoff_start()
            self._client.close()
            return False
        except (TimeoutError, OSError, ConnectionError) as err:
            _LOGGER.warning("Connection to heatpump failed (network): %s", err)
            self._failed_reconnect_counter += 1
            if (
                self._failed_reconnect_counter == BACKOFF_THRESHOLD_FAILURES
                and not startup
            ):
                self._log_backoff_start()
            with contextlib.suppress(Exception):
                self._client.close()
            return False
        except Exception as err:
            _LOGGER.warning("Connection to heatpump failed (unexpected): %s", err)
            self._failed_reconnect_counter += 1
            if (
                self._failed_reconnect_counter == BACKOFF_THRESHOLD_FAILURES
                and not startup
            ):
                self._log_backoff_start()
            with contextlib.suppress(Exception):
                self._client.close()
            return False
        finally:
            self._connect_pending = False

    async def disconnect(self) -> None:
        """Close connection cleanly."""
        async with self._lock:
            if self._client.connected:
                self._client.close()

    async def _read_individual_registers(
        self, start: int, count: int, is_holding: bool
    ) -> dict[int, int]:
        """Read a partially supported block individually while the caller holds the lock."""
        reader = (
            self._client.read_holding_registers
            if is_holding
            else self._client.read_input_registers
        )
        values: dict[int, int] = {}
        for address in range(start, start + count):
            try:
                response = await reader(address=address, count=1, device_id=1)
                if not response.isError() and len(response.registers) == 1:
                    values[address] = response.registers[0]
            except (TimeoutError, ModbusException, OSError) as err:
                _LOGGER.debug("Cannot read individual register %d: %s", address, err)
        return values

    async def update(self) -> dict[int, int | None]:
        """Coordinator polls this method to batch-update the entire internal register cache."""
        batches = self._process_and_validate_batches(DEVICELISTS)

        def process_raw_value(addr: int, raw_val: int) -> int | None:
            item = self._items_dict.get(addr)
            if not item:
                return raw_val

            mformat = getattr(
                item,
                "format",
                getattr(item, "mformat", getattr(item, "_mformat", None)),
            )

            if mformat == FORMATS.TEMPERATURE:
                match raw_val:
                    case -32768 | 32768:
                        item.is_invalid = True
                        return None
                    case -32767:
                        item.is_invalid = False
                        return -999
                    case _:
                        if raw_val > 32768:
                            raw_val -= 65536
                        item.is_invalid = False
                        return raw_val

            if mformat == FORMATS.PERCENTAGE:
                if raw_val == 65535:
                    item.is_invalid = True
                    return None
                item.is_invalid = False
                return raw_val

            if mformat == FORMATS.STATUS:
                item.is_invalid = False
                return raw_val

            item.is_invalid = False
            return raw_val

        def nullify_batch(start_addr: int, reg_count: int) -> None:
            for i in range(reg_count):
                addr = start_addr + i
                self.data[addr] = None
                item = self._items_dict.get(addr)
                if item:
                    item.is_invalid = True

        async with self._lock:
            if not self._client.connected:
                # Regular polling uses startup=False
                if not await self.connect(startup=False):
                    raise ConnectionFailedError("Modbus client is not connected")

            for start, count in batches.items():
                is_holding = 40000 <= start < 50000

                try:
                    if is_holding:
                        response = await self._client.read_holding_registers(
                            address=start,
                            count=count,
                            device_id=1,
                        )
                    else:
                        response = await self._client.read_input_registers(
                            address=start,
                            count=count,
                            device_id=1,
                        )

                    # Handle Modbus/Library protocol error packets
                    if response.isError():
                        if hasattr(
                            response, "exception_code"
                        ) and response.exception_code in (2, 4, 10):
                            _LOGGER.debug(
                                "Skipping %s block %d: Hardware module not active (Exception %d)",
                                "holding" if is_holding else "input",
                                start,
                                response.exception_code,
                            )
                            # Exception 2 (illegal data address) flags item as invalid
                            if response.exception_code == 2:
                                nullify_batch(start, count)
                                if count > 1:
                                    values = await self._read_individual_registers(
                                        start, count, is_holding
                                    )
                                    for address, raw in values.items():
                                        self.data[address] = process_raw_value(
                                            address, raw
                                        )
                                continue
                        else:
                            _LOGGER.warning(
                                "Modbus error reading %s block %d (count %d): %s",
                                "holding" if is_holding else "input",
                                start,
                                count,
                                response,
                            )
                        nullify_batch(start, count)
                        continue

                    if len(response.registers) != count:
                        _LOGGER.warning(
                            "Unexpected register count for block %d: expected %d, received %d",
                            start,
                            count,
                            len(response.registers),
                        )
                        nullify_batch(start, count)
                        continue

                    # Process and cache register registers
                    for idx, val in enumerate(response.registers):
                        reg_addr = start + idx
                        self.data[reg_addr] = process_raw_value(reg_addr, val)

                except (TimeoutError, ModbusException, OSError) as err:
                    _LOGGER.error(
                        "Exception reading block %d (count %d): %s",
                        start,
                        count,
                        err,
                    )
                    nullify_batch(start, count)

        return self.data

    async def write_register(self, address: int, value: int) -> bool:
        """Write a value to a Modbus holding register safely behind the lock."""
        if not (40000 <= address < 50000):
            raise ValueError(
                f"Invalid write address {address}. Only holding registers (4xxxx) are writable."
            )

        async with self._lock:
            if not self._client.connected:
                if not await self.connect(startup=False):
                    return False
            try:
                cached_val = self.get_value(address)
                if cached_val is not None and cached_val == value:
                    _LOGGER.debug(
                        "Schreiben auf Register %d übersprungen: Wert %d ist bereits aktiv (EEPROM geschont).",
                        address,
                        value,
                    )
                    return True
                item = self._items_dict.get(address)
                if item:
                    mformat = getattr(
                        item,
                        "format",
                        getattr(item, "mformat", getattr(item, "_mformat", None)),
                    )
                    if mformat == FORMATS.TEMPERATURE and value < 0:
                        value += 65536

                response = await self._client.write_register(
                    address=address, value=value, device_id=1
                )
                if response.isError():
                    raise WriteError(
                        f"Modbus error writing to register {address}: {response}"
                    )

                self.data[address] = value
                return True
            except (TimeoutError, ModbusException, OSError) as err:
                raise WriteError(
                    f"Failed to write to register {address}: {err}"
                ) from err

    def _process_and_validate_batches(
        self, items: list[list[ModbusItem]]
    ) -> dict[int, int]:
        """Build contiguous, unique batches without changing register metadata."""
        by_address: dict[int, ModbusItem] = {}
        for group in items:
            for item in group:
                if item.type == TYPES.SENSOR_CALC or item.batch is None:
                    continue
                by_address.setdefault(item.address, item)

        self._items_dict = by_address
        batches: dict[int, int] = {}
        start: int | None = None
        previous: int | None = None
        hint: int | None = None
        for address, item in sorted(by_address.items()):
            if (
                start is None
                or previous is None
                or address != previous + 1
                or item.batch != hint
                or (address >= 40000) != (start >= 40000)
                or batches[start] >= MAX_BLOCK_READ_COUNT
            ):
                start = address
                batches[start] = 0
            batches[start] += 1
            previous = address
            hint = item.batch
        return batches
