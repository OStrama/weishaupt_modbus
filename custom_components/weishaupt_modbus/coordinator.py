"""The Update Coordinator for the ModbusItems."""

import asyncio
from datetime import timedelta
import logging
from typing import Any

from pymodbus import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .configentry import MyConfigEntry
from .const import CONF, CONST, TYPES, DeviceConstants
from .items import ModbusItem
from .modbusobject import ModbusAPI, ModbusObject
from .webif_object import WebifConnection

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


class MyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Modbus coordinator for Weishaupt heat pump."""

    def __init__(
        self,
        hass: HomeAssistant,
        my_api: ModbusAPI,
        api_items: list[ModbusItem],
        p_config_entry: MyConfigEntry,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="weishaupt-coordinator",
            update_interval=CONST.SCAN_INTERVAL,
            always_update=True,
        )
        self._modbus_api = my_api
        self._device: Any = None
        self._modbusitems = api_items
        self._number_of_items = len(api_items)
        self._config_entry = p_config_entry

    async def get_value(self, modbus_item: ModbusItem) -> Any:
        """Read a value from the modbus."""
        mbo = ModbusObject(self._modbus_api, modbus_item)
        if mbo is None:
            modbus_item.state = None
        else:
            modbus_item.state = await mbo.value
        return modbus_item.state

    def get_value_from_item(self, translation_key: str) -> Any:
        """Read a value from another modbus item."""
        for item in self._modbusitems:
            if item.translation_key == translation_key:
                return item.state
        return None

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        if self._modbus_api._modbus_client is None:  # noqa: SLF001
            _LOGGER.warning("Modbus client is None")
            raise ConfigEntryNotReady("Modbus client not initialized")

        await self._modbus_api.connect(startup=True)
        if not self._modbus_api._modbus_client.connected:  # noqa: SLF001
            _LOGGER.warning("Connection failed during setup")
            raise ConfigEntryNotReady("Could not connect to modbus")

    async def fetch_data(self, idx: set[int] | None = None) -> dict[str, Any]:
        """Fetch all values from the modbus."""
        if idx is None or len(idx) == 0:
            to_update = tuple(range(len(self._modbusitems)))
        else:
            to_update = tuple(idx)

        if not await self._ensure_connection():
            return {}

        results: dict[str, Any] = {}

        for index in to_update:
            if index >= len(self._modbusitems):
                continue

            item = self._modbusitems[index]

            if not await check_configured(item, self._config_entry):
                continue

            match item.type:
                case (
                    TYPES.SENSOR
                    | TYPES.NUMBER_RO
                    | TYPES.NUMBER
                    | TYPES.SELECT
                    | TYPES.SENSOR_CALC
                ):
                    value = await self.get_value(item)
                    results[item.translation_key] = value

        return results

    async def _ensure_connection(self) -> bool:
        """Establish modbus connection."""
        if self._modbus_api._modbus_client is None:  # noqa: SLF001
            _LOGGER.debug("Modbus client is None")
            return False

        if not self._modbus_api._modbus_client.connected:  # noqa: SLF001
            status = await self._modbus_api.connect(startup=False)
            if not status:
                _LOGGER.debug("Connection retry failed")
                return False
        return True

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            async with asyncio.timeout(10):
                listening_idx = set(self.async_contexts())  # noqa: F841
                return await self.fetch_data()  # listening_idx)
        except ModbusException as err:
            _LOGGER.debug("Modbus connection failed: %s", err)
            return {}
        except TimeoutError as err:
            _LOGGER.debug("Timeout while fetching data: %s", err)
            return {}

    @property
    def modbus_api(self) -> ModbusAPI:
        """Return modbus API."""
        return self._modbus_api


class MyWebIfCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """WebIF coordinator for Weishaupt heat pump."""

    def __init__(self, hass: HomeAssistant, config_entry: MyConfigEntry) -> None:
        """Initialize WebIF coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name="weishaupt-webif",
            update_interval=timedelta(seconds=60),
            always_update=True,
        )
        self.my_api: WebifConnection = config_entry.runtime_data.webif_api

    async def _async_setup(self) -> None:
        """Set up the coordinator."""

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from WebIF endpoint."""
        try:
            async with asyncio.timeout(30):
                result = await self.my_api.get_info()
                return result if result is not None else {}
        except TimeoutError:
            _LOGGER.debug("Timeout while fetching WebIF data")
            return {}
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Error fetching WebIF data: %s", err)
            return {}
