"""The Update Coordinator for the ModbusItems."""

import asyncio
from datetime import timedelta
import logging
from typing import TYPE_CHECKING, override

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .weishaupt_modbus_client.model.device import Weishaupt

_LOGGER = logging.getLogger(__name__)


if TYPE_CHECKING:
    from modbus_connection.model import UpdateReport
else:
    try:
        from modbus_connection.model import UpdateReport
    except ImportError:  # pragma: no cover
        from .weishaupt_modbus_client.model.modbus_connection_device import UpdateReport

        _LOGGER.debug("Using local Device/UpdateReport compatibility implementation")


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

    @override
    async def _async_update_data(self) -> UpdateReport:
        """Update the Weishaupt device."""
        async with self._mcu_lock:
            report = await self.device.async_update()

        if report.failed:
            _LOGGER.warning(
                "Failed to update Weishaupt reports: %s",
                ", ".join(f"{name}: {error}" for name, error in report.failed.items()),
            )

        return report
