"""The Update Coordinator for the ModbusItems."""

import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .weishaupt_modbus_client.model.device import UpdateReport, Weishaupt

_LOGGER = logging.getLogger(__name__)


class WeishauptCoordinator(DataUpdateCoordinator[UpdateReport]):
    """Coordinate updates for a Weishaupt device."""

    def __init__(
        self,
        hass: HomeAssistant,
        device: Weishaupt,
        mcu_lock: asyncio.Lock,
    ) -> None:
        """Initialize the Weishaupt coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Weishaupt",
            update_interval=timedelta(seconds=10),
        )
        self.device = device
        self._mcu_lock = mcu_lock

    async def _async_update_data(self) -> UpdateReport:
        """Update the Weishaupt device."""
        async with self._mcu_lock:
            return await self.device.async_update()
