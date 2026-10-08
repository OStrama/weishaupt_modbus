"""WebIF update coordinator."""

import asyncio
from datetime import timedelta
import logging
from typing import Any, override

from weishaupt_webif_api import WebifConnection, WeishauptWebifError

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ...weishaupt_modbus.const import CONF

_LOGGER = logging.getLogger(__name__)


class WeishauptWebifCoordinator(
    DataUpdateCoordinator[dict[str, Any]],
):
    """Coordinator for Weishaupt WebIF."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: WebifConnection,
        entry: config_entries.ConfigEntry,
        mcu_lock: asyncio.Lock,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name="Weishaupt WebIF",
            update_interval=timedelta(seconds=10),
            always_update=True,
        )

        self.api = api
        self.entry = entry
        self._mcu_lock = mcu_lock

        self.data: dict[str, Any] = {}
        self._category_queue: list[str] = []

    @override
    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the WebIF endpoint."""
        active_categories = self._get_categories()

        if not active_categories:
            return self.data

        self._category_queue = [
            category
            for category in self._category_queue
            if category in active_categories
        ]

        if not self._category_queue:
            self._category_queue = list(active_categories)

        category_to_poll = self._category_queue.pop(0)

        delay = self.api._request_delay
        timeout_budget = delay + 15.0

        try:
            async with self._mcu_lock:
                async with asyncio.timeout(timeout_budget):
                    _LOGGER.debug(
                        "Round-robin: polling WebIF category '%s'",
                        category_to_poll,
                    )

                    if self.entry.data.get(
                        CONF.CB_WEBIF_MOCKUP_DATA,
                        False,
                    ):
                        result = await self.api.update_all_mock([category_to_poll])
                    else:
                        result = await self.api.update_all([category_to_poll])

                    category_data = result.get(category_to_poll)

                    if isinstance(category_data, dict):
                        self.data.update(category_data)

                    return self.data

        except TimeoutError as err:
            raise UpdateFailed(
                f"Timeout while fetching WebIF category {category_to_poll}"
            ) from err
        except WeishauptWebifError as err:
            raise UpdateFailed(f"Error fetching WebIF data: {err}") from err

    def _get_categories(self) -> list[str]:
        """Return the configured WebIF categories."""
        categories = []
        if self.entry.data.get(CONF.CB_WEBIF_HK1):
            categories.append("heating_circuit")

        if self.entry.data.get(CONF.CB_WEBIF_HK2):
            categories.append("heating_circuit2")

        if self.entry.data.get(CONF.CB_WEBIF_HK3):
            categories.append("heating_circuit3")

        if self.entry.data.get(CONF.CB_WEBIF_HK4):
            categories.append("heating_circuit4")

        if self.entry.data.get(CONF.CB_WEBIF_HK5):
            categories.append("heating_circuit5")

        if self.entry.data.get(CONF.CB_WEBIF_WP):
            categories.append("heat_pump")
        if self.entry.data.get(CONF.CB_WEBIF_2WEZ):
            categories.append("electric_heater")
        if self.entry.data.get(CONF.CB_WEBIF_SATISTICS):
            categories.append("statistics")
        return categories
