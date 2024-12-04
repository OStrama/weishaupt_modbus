"""The Update Coordinator for the ModbusItems."""

import asyncio
from datetime import timedelta
import logging

from pymodbus import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .configentry import MyConfigEntry
from .const import CONF, CONST, FORMATS, TYPES
from .hpconst import DEVICES, PARAMS_STDTEMP
from .items import ModbusItem
from .modbusobject import ModbusAPI, ModbusObject
from .webif_object import WebifConnection

logging.basicConfig()
log = logging.getLogger(__name__)


class MyCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        my_api: ModbusAPI,
        api_items: ModbusItem,
        p_config_entry: MyConfigEntry,
    ) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            log,
            # Name of the data. For logging purposes.
            name="weishaupt-coordinator",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=CONST.SCAN_INTERVAL,
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=True,
        )
        self._modbus_api = my_api
        self._device = None  #: MyDevice | None = None
        self._modbusitems = api_items
        self._number_of_items = len(api_items)
        self._config_entry = p_config_entry

    async def get_value(self, modbus_item: ModbusItem):
        """Read a value from the modbus."""
        mbo = ModbusObject(self._modbus_api, modbus_item)
        if mbo is None:
            modbus_item.state = None
        modbus_item.state = await mbo.value
        log.debug(
            "Get value:%s from item:%s",
            str(modbus_item.state),
            modbus_item.translation_key,
        )
        return modbus_item.state

    def get_value_from_item(self, translation_key: str) -> int:
        """Read a value from another modbus item"""
        for _useless, item in enumerate(self._modbusitems):
            if item.translation_key == translation_key:
                log.debug(
                    "Get calc value:%s from item:%s",
                    str(item.state),
                    item.translation_key,
                )
                return item.state
        return None

    async def check_configured(self, modbus_item: ModbusItem) -> bool:
        """Check if item is configured."""
        if self._config_entry.data[CONF.HK2] is False:
            if modbus_item.device is DEVICES.HZ2:
                return False

        if self._config_entry.data[CONF.HK3] is False:
            if modbus_item.device is DEVICES.HZ3:
                return False

        if self._config_entry.data[CONF.HK4] is False:
            if modbus_item.device is DEVICES.HZ4:
                return False

        if self._config_entry.data[CONF.HK5] is False:
            if modbus_item.device is DEVICES.HZ5:
                return False
        return True

    async def _async_setup(self):
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        await self.fetch_data()

    async def fetch_data(self, idx=None):
        """Fetch all values from the modbus."""
        # if idx is not None:
        if idx is None:
            # first run: Update all entitiies
            to_update = tuple(range(len(self._modbusitems)))
        elif len(idx) == 0:
            # idx exists but is not yet filled up: Update all entitiys.
            to_update = tuple(range(len(self._modbusitems)))
        else:
            # idx exists and is filled up: Update only entitys requested by the coordinator.
            to_update = idx

        # await self._modbus_api.connect()
        for index in to_update:
            item = self._modbusitems[index]
            # At setup the coordinator has to be called before buildentitylist. Therefore check if we should add HZ2,3,4,5...
            if await self.check_configured(item) is True:
                match item.type:
                    # here the entities are created with the parameters provided
                    # by the ModbusItem object
                    case (
                        TYPES.SENSOR
                        | TYPES.NUMBER_RO
                        | TYPES.NUMBER
                        | TYPES.SELECT
                        | TYPES.SENSOR_CALC
                    ):
                        await self.get_value(item)

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        async with asyncio.timeout(10):
            # Grab active context variables to limit data required to be fetched from API
            # Note: using context is not required if there is no need or ability to limit
            # data retrieved from API.
            try:
                listening_idx = set(self.async_contexts())
                return await self.fetch_data()  # listening_idx)
            except ModbusException:
                log.warning("connection to the heatpump failed")

    @property
    def modbus_api(self) -> str:
        """Return modbus_api."""
        return self._modbus_api


class MyWebIfCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass: HomeAssistant, config_entry: MyConfigEntry) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass=hass,
            logger=log,
            # Name of the data. For logging purposes.
            name="My sensor",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=60),
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=True,
        )
        self.my_api: WebifConnection = config_entry.runtime_data.webif_api
        # self._device: MyDevice | None = None

    async def _async_setup(self):
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        # self._device = await self.my_api.get_device()

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with asyncio.timeout(30):
                # Grab active context variables to limit data required to be fetched from API
                # Note: using context is not required if there is no need or ability to limit
                # data retrieved from API.
                # listening_idx = set(self.async_contexts())
                # return await self.my_api.return_test_data()
                # print("Fetching Data")
                items = {}
                info_hk1 = await self.my_api.fake_info_hk1()
                info_waermepumpe = await self.my_api.fake_info_wp()
                info_2wez = await self.my_api.fake_info_2wez()
                info_statistik = await self.my_api.fake_info_statistik()
                items.update(info_hk1)
                items.update(info_waermepumpe)
                items.update(info_2wez)
                items.update(info_statistik)
                # print(items)
                return items
        except TimeoutError:
            logging.debug(msg="Timeout while fetching data")
        # except ApiAuthError as err:
        # Raising ConfigEntryAuthFailed will cancel future updates
        # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        #    raise ConfigEntryAuthFailed from err
        # except ApiError as err:
        #    raise UpdateFailed(f"Error communicating with API: {err}")
