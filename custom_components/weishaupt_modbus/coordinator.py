"""The Update Coordinator for the ModbusItems."""

import asyncio
from datetime import timedelta
import logging
from typing import Any

from pymodbus import ModbusException
from weishaupt_webif_api import WebifConnection

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .configentry import MyConfigEntry
from .const import CONF, CONST, TYPES, DeviceConstants
from .items import ModbusItem, WebItem
from .modbusobject import ModbusAPI, ModbusObject

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

    @property
    def modbus_items(self) -> list[ModbusItem]:
        """Return the list of modbus items for this coordinator."""
        return self._modbusitems

    async def get_value(self, modbus_item: ModbusItem) -> Any:
        """Read a value from the modbus."""
        mbo = ModbusObject(self._modbus_api, modbus_item)
        if mbo is None:
            modbus_item.state = None
        else:
            modbus_item.state = await mbo.get_value()
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
                # listening_idx = set(self.async_contexts())
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
    ) -> None:
        """Initialize WebIF coordinator."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name="weishaupt-webif",
            update_interval=timedelta(seconds=30),
            always_update=True,
        )

        self.my_api: WebifConnection | None = my_api
        self.api_items = api_items

    async def _async_setup(self) -> None:
        """Set up the coordinator."""

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from WebIF endpoint."""
        # try:
        async with asyncio.timeout(30):
            _LOGGER.debug("Trying to fetch complete WebIF data")
            result: dict[str, Any] | None = None

            what_to_poll = []
            if self.config_entry.data.get(CONF.CB_WEBIF_HK1, False) is True:
                what_to_poll.append("Heizkreis1")

            if self.config_entry.data.get(CONF.CB_WEBIF_HK2, False) is True:
                what_to_poll.append("Heizkreis2")

            if self.config_entry.data.get(CONF.CB_WEBIF_HK3, False) is True:
                what_to_poll.append("Heizkreis3")

            if self.config_entry.data.get(CONF.CB_WEBIF_HK4, False) is True:
                what_to_poll.append("Heizkreis4")

            if self.config_entry.data.get(CONF.CB_WEBIF_HK5, False) is True:
                what_to_poll.append("Heizkreis5")

            if self.config_entry.data.get(CONF.CB_WEBIF_WP, False) is True:
                what_to_poll.append("Waermepumpe")

            if self.config_entry.data.get(CONF.CB_WEBIF_2WEZ, False) is True:
                what_to_poll.append("2WEZ")

            if self.config_entry.data.get(CONF.CB_WEBIF_SATISTICS, False) is True:
                what_to_poll.append("Statistik")

            if self.my_api is not None:
                if self.config_entry is not None:
                    if self.config_entry.data.get(CONF.CB_WEBIF_MOCKUP_DATA, False):
                        result = await self.my_api.update_all_mock(what_to_poll)
                    else:
                        result = await self.my_api.update_all(what_to_poll)
            if result is not None:
                hk = result.get("Heizkreis")
                hk1 = result.get("Heizkreis1")
                hk2 = result.get("Heizkreis2")
                hk3 = result.get("Heizkreis3")
                hk4 = result.get("Heizkreis4")
                hk5 = result.get("Heizkreis5")
                wp = result.get("Waermepumpe")
                wez2 = result.get("2WEZ")
                wes = result.get("Statistik")
                if hk is not None:
                    result = result | hk
                if hk1 is not None:
                    result = result | hk1
                if hk2 is not None:
                    result = result | hk2
                if hk3 is not None:
                    result = result | hk3
                if hk4 is not None:
                    result = result | hk4
                if hk5 is not None:
                    result = result | hk5
                if wp is not None:
                    result = result | wp
                if wez2 is not None:
                    result = result | wez2
                if wes is not None:
                    result = result | wes

            return result if result is not None else {}
        # except TimeoutError:
        #    _LOGGER.debug("Timeout while fetching WebIF data")
        #    return {}
        # except Exception as err:
        #    _LOGGER.debug("Error fetching WebIF data: %s", err)
        #    return {}
