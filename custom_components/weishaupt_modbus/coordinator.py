"""The Update Coordinator for the ModbusItems."""

import asyncio
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, Any

from modbus_connection.model import UpdateReport
from weishaupt_webif_api import WebifConnection, WeishauptWebifError

from config.custom_components.weishaupt_modbus.modbus.weishaupt_modbus_client.model.device import (
    Weishaupt,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

if TYPE_CHECKING:
    from .configentry import MyConfigEntry
from .const import CONF
from .items import WebItem

_LOGGER = logging.getLogger(__name__)


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


class WeishauptCoordinator(DataUpdateCoordinator[UpdateReport]):
    """Coordinate updates for a Weishaupt device."""

    def __init__(self, hass: HomeAssistant, device: Weishaupt) -> None:
        """Initialize the Weishaupt coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Weishaupt",
            update_interval=timedelta(seconds=10),
        )
        self.device = device

    async def _async_update_data(self) -> UpdateReport:

        return await self.device.async_update()
