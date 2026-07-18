"""The Update Coordinator for the ModbusItems."""

import asyncio
from datetime import timedelta
import logging
from typing import Any

from pymodbus import ModbusException

from config.custom_components.weishaupt_modbus.weishaupt_modbus_api.exceptions import (
    ConnectionFailedError,
)
from config.custom_components.weishaupt_modbus.weishaupt_modbus_api.modbus_api import (
    WeishauptModbusClient,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from weishaupt_webif_api import WebifConnection, WeishauptWebifError

from .configentry import MyConfigEntry
from .const import CONF, CONST, TYPES, DeviceConstants
from .items import ModbusItem, WebItem
from .modbusobject import ModbusAPI

_LOGGER = logging.getLogger(__name__)


async def check_configured(
    modbus_item: ModbusItem, config_entry: MyConfigEntry
) -> bool:
    """Check if item is configured."""
    match modbus_item.device:
        case DeviceConstants.HZ2:
            return config_entry.data[CONF.HK2]
        case DeviceConstants.HZ3:
            return config_entry.data[CONF.HK3]
        case DeviceConstants.HZ4:
            return config_entry.data[CONF.HK4]
        case DeviceConstants.HZ5:
            return config_entry.data[CONF.HK5]
        case _:
            return True


class MyWebIfCoordinator(
    DataUpdateCoordinator[dict[str, Any]],
):
    """WebIF coordinator for Weishaupt heat pump."""

    def __init__(
        self,
        hass: HomeAssistant,
        my_api: WebifConnection | None,
        api_items: list[WebItem],
        config_entry: MyConfigEntry,
        mcu_lock: asyncio.Lock,
    ) -> None:
        """Initialize WebIF coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name="weishaupt-webif",
            update_interval=timedelta(seconds=10),
            always_update=True,
        )

        self.my_api: WebifConnection | None = my_api
        self.api_items = api_items
        self._mcu_lock = mcu_lock  # <-- Store lock
        self.data: dict[str, Any] = {item.name: None for item in api_items}
        self._category_queue: list[str] = []  # Queue to track our round-robin rotation

    async def _async_setup(self) -> None:
        """Set up the coordinator."""

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from WebIF endpoint."""
        # try:
        active_categories = []

        if self.config_entry.data.get(CONF.CB_WEBIF_HK1, False) is True:
            active_categories.append("Heizkreis1")

        if self.config_entry.data.get(CONF.CB_WEBIF_HK2, False) is True:
            active_categories.append("Heizkreis2")

        if self.config_entry.data.get(CONF.CB_WEBIF_HK3, False) is True:
            active_categories.append("Heizkreis3")

        if self.config_entry.data.get(CONF.CB_WEBIF_HK4, False) is True:
            active_categories.append("Heizkreis4")

        if self.config_entry.data.get(CONF.CB_WEBIF_HK5, False) is True:
            active_categories.append("Heizkreis5")

        if self.config_entry.data.get(CONF.CB_WEBIF_WP, False) is True:
            active_categories.append("Waermepumpe")

        if self.config_entry.data.get(CONF.CB_WEBIF_2WEZ, False) is True:
            active_categories.append("2WEZ")

        if self.config_entry.data.get(CONF.CB_WEBIF_SATISTICS, False) is True:
            active_categories.append("Statistik")

        if not active_categories:
            return self.data

        # 2. Refill or sanitize the queue
        self._category_queue = [
            cat for cat in self._category_queue if cat in active_categories
        ]
        if not self._category_queue:
            self._category_queue = list(active_categories)

        # 3. Pull exactly ONE category for this run
        category_to_poll = self._category_queue.pop(0)

        # Since we are fetching exactly 1 page, we can set a safe, relaxed timeout budget
        delay = self.my_api._request_delay if self.my_api else 10
        timeout_budget = delay + 15.0

        try:
            # Acquire lock to ensure we do not collide with Modbus polling
            async with self._mcu_lock:
                async with asyncio.timeout(timeout_budget):
                    _LOGGER.debug(
                        "Round-robin: polling single WebIF category '%s'",
                        category_to_poll,
                    )
                    result: dict[str, Any] | None = None

                    if self.my_api is not None:
                        if self.config_entry is not None:
                            if self.config_entry.data.get(
                                CONF.CB_WEBIF_MOCKUP_DATA, False
                            ):
                                result = await self.my_api.update_all_mock(
                                    [category_to_poll]
                                )
                            else:
                                result = await self.my_api.update_all(
                                    [category_to_poll]
                                )

                    if result is not None:
                        # Extract the data for the category we successfully polled
                        category_data = result.get(category_to_poll)
                        if isinstance(category_data, dict):
                            # Update our persistent cache in-place
                            self.data.update(category_data)

                    return self.data
        except TimeoutError as err:
            raise UpdateFailed("Timeout while fetching WebIF data") from err
        except WeishauptWebifError as err:
            raise UpdateFailed(f"Error fetching WebIF data: {err}") from err


class WeishauptModbusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Clean, lock-free DataUpdateCoordinator for batch Modbus register polling."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: WeishauptModbusClient,
        api_items: list[ModbusItem],
        p_config_entry: MyConfigEntry,
    ) -> None:
        """Initialize the coordinator without synchronization overhead."""
        super().__init__(
            hass,
            _LOGGER,
            name="weishaupt-modbus-coordinator",
            update_interval=CONST.SCAN_INTERVAL,
            always_update=True,
        )
        self.client = client
        self._modbusitems = api_items
        self.modbus_items = api_items
        self._config_entry = p_config_entry

    def get_value_from_item(self, translation_key: str) -> Any:
        """Read a value from another modbus item by its translation key."""
        for item in self._modbusitems:
            if item.translation_key == translation_key:
                return item.state
        return None

    async def _async_setup(self) -> None:
        """Verify client connection during integration startup."""
        if not self.client.connected:
            _LOGGER.debug("Establishing initial connection to heat pump...")
            connected = await self.client.connect()
            if not connected:
                raise ConfigEntryNotReady(
                    "Could not establish initial Modbus connection"
                )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch all configured registers using high-efficiency batch reads."""
        try:
            # The locking context is shifted down. The coordinator simply triggers the update.
            async with asyncio.timeout(15):
                await self.client.update()

            return await self._process_cached_data()

        except (TimeoutError, ConnectionFailedError, ModbusException) as err:
            raise UpdateFailed(f"Modbus communication failure: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected coordinator update error: {err}") from err

    async def _process_cached_data(self) -> dict[str, Any]:
        """Map the raw/sanitized cache to the expected translation keys."""
        results: dict[str, Any] = {}

        for item in self._modbusitems:
            # Skip items belonging to unconfigured heating circuits
            if not await check_configured(item, self._config_entry):
                continue

            # 1. Catch purely virtual calculated sensors immediately.
            # They never poll Modbus directly and evaluate entirely in-memory.
            if getattr(item, "type", None) == TYPES.SENSOR_CALC:
                item.state = None
                results[item.translation_key] = None
                continue

            address = getattr(item, "_address", None) or getattr(item, "address", None)

            # 2. Process standard Modbus-polled items
            if address is not None:
                # Instantly retrieve the pre-processed register value from client cache
                val = self.client.get_value(address)
                item.state = val
                results[item.translation_key] = val
            else:
                results[item.translation_key] = None

        return results
