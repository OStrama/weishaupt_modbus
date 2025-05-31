"""The Update Coordinator for the ModbusItems."""

import asyncio
from datetime import timedelta
import logging

from pymodbus import ModbusException

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .configentry import MyConfigEntry
from .const import CONF, CONST, DEVICES, TYPES
from .items import ModbusItem
from .modbusobject import ModbusAPI, ModbusObject
from .webif_object import WebifConnection

logging.basicConfig()
log = logging.getLogger(__name__)


async def check_configured(
    modbus_item: ModbusItem, config_entry: MyConfigEntry
) -> bool:
    """Check if item is configured.

    :param modbus_item: definition of modbus item
    :type modbus_item: ModbusItem
    :param config_entry: HASS config entry
    :type config_entry: MyConfigEntry
    """
    if modbus_item.device is DEVICES.HZ2:
        return config_entry.data[CONF.HK2]
    if modbus_item.device is DEVICES.HZ3:
        return config_entry.data[CONF.HK3]
    if modbus_item.device is DEVICES.HZ4:
        return config_entry.data[CONF.HK4]
    if modbus_item.device is DEVICES.HZ5:
        return config_entry.data[CONF.HK5]
    return True


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
        self._device = None
        self._modbusitems = api_items
        self._number_of_items = len(api_items)
        self._config_entry = p_config_entry

    async def get_value(self, modbus_item: ModbusItem):
        """Read a value from the modbus."""
        mbo = ModbusObject(self._modbus_api, modbus_item)
        if mbo is None:
            modbus_item.state = None
        else:
            modbus_item.state = await mbo.value
        return modbus_item.state

    def get_value_from_item(self, translation_key: str) -> int:
        """Read a value from another modbus item."""
        for _useless, item in enumerate(self._modbusitems):
            if item.translation_key == translation_key:
                return item.state
        return None

    async def _async_setup(self):
        """Set up the coordinator.

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        if self._modbus_api._modbus_client is None:
            log.warning(
                "coordinator: async_setup: Modbus client is None. Returning None"
            )
            return None
        await self._modbus_api.connect(startup=True)
        if self._modbus_api._modbus_client.connected is False:
            log.warning("Connection retry in asyunc_update_data failed. Returning None")
            return None
        # await self.fetch_data()

    async def fetch_data(self, idx=None):
        """Fetch all values from the modbus."""

        # if idx is not None:
        if idx is None:
            # first run: Update all entities
            to_update = tuple(range(len(self._modbusitems)))
        elif len(idx) == 0:
            # idx exists but is not yet filled up: Update all entities.
            to_update = tuple(range(len(self._modbusitems)))
        else:
            # idx exists and is filled up: Update only entities requested by the coordinator.
            to_update = idx

        ret = await self.save_connect()
        if ret is False:
            log.warning(
                "coordinator: fetch_data: Could not establish modbus cconnection"
            )
            return

        for index in to_update:
            item = self._modbusitems[index]
            # At setup the coordinator has to be called before buildentitylist.
            # Therefore check if we should add HZ2,3,4,5...
            if await check_configured(item, self._config_entry) is True:
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

    async def save_connect(self) -> bool:
        """Establish modbus connection."""
        if self._modbus_api._modbus_client is None:
            log.warning(
                "coordinator: async_update_data: Modbus client is None. Returning None"
            )
            return False
        if self._modbus_api._modbus_client.connected is False:
            status = await self._modbus_api.connect(startup=False)
            if status is False:
                log.warning(
                    "Connection retry in asyunc_update_data failed. Returning None"
                )
                return False
        return True

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        ret = await self.save_connect()
        if ret is False:
            log.warning(
                "coordinator: async_update_data: Could not establish modbus cconnection"
            )
            return None
        # await self.fetch_data()
        # Note: asyncio.TimeoutError and aiohttp.ClientError are already
        # handled by the data update coordinator.
        async with asyncio.timeout(10):
            # Grab active context variables to limit data required to be fetched from API
            # Note: using context is not required if there is no need or ability to limit
            # data retrieved from API.
            try:
                # listening_idx = set(self.async_contexts())
                return await self.fetch_data()  # !!!!!using listening_idx will result in some entities never updated !!!!!
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
                return await self.my_api.get_info()
        except TimeoutError:
            logging.debug(msg="Timeout while fetching data")
        # except ApiAuthError as err:
        # Raising ConfigEntryAuthFailed will cancel future updates
        # and start a config flow with SOURCE_REAUTH (async_step_reauth)
        #    raise ConfigEntryAuthFailed from err
        # except ApiError as err:
        #    raise UpdateFailed(f"Error communicating with API: {err}")
