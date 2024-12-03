"""Entity classes used in this integration"""

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .configentry import MyConfigEntry
from .const import CONF, CONST, FORMATS, CALCTYPES
from .coordinator import MyCoordinator, MyWebIfCoordinator
from .hpconst import reverse_device_list
from .items import ModbusItem, WebItem
from .migrate_helpers import create_unique_id
from .modbusobject import ModbusAPI, ModbusObject

logging.basicConfig()
log = logging.getLogger(__name__)


class MyEntity(Entity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
    should_poll
    async_update
    async_added_to_hass
    available

    The base class for entities that hold general parameters
    """

    _divider = 1
    _attr_should_poll = True
    _attr_has_entity_name = True
    _dynamic_min = None
    _dynamic_max = None

    def __init__(
        self,
        config_entry: MyConfigEntry,
        api_item: ModbusItem | WebItem,
        modbus_api: ModbusAPI,
    ) -> None:
        """Initialize the entity."""
        self._config_entry = config_entry
        self._api_item: ModbusItem | WebItem = api_item

        dev_postfix = "_" + self._config_entry.data[CONF.DEVICE_POSTFIX]

        if dev_postfix == "_":
            dev_postfix = ""

        dev_prefix = self._config_entry.data[CONF.PREFIX]

        if self._config_entry.data[CONF.NAME_DEVICE_PREFIX]:
            name_device_prefix = dev_prefix + "_"
        else:
            name_device_prefix = ""

        if self._config_entry.data[CONF.NAME_TOPIC_PREFIX]:
            name_topic_prefix = reverse_device_list[self._api_item.device] + "_"
        else:
            name_topic_prefix = ""

        name_prefix = name_topic_prefix + name_device_prefix

        self._dev_device = self._api_item.device + dev_postfix

        self._attr_translation_key = self._api_item.translation_key
        self._attr_translation_placeholders = {"prefix": name_prefix}
        self._dev_translation_placeholders = {"postfix": dev_postfix}

        self._attr_unique_id = create_unique_id(self._config_entry, self._api_item)
        self._dev_device = self._api_item.device

        self._modbus_api = modbus_api

        if self._api_item.format != FORMATS.STATUS:
            self._attr_native_unit_of_measurement = self._api_item.format

            match self._api_item.format:
                case FORMATS.ENERGY:
                    self._attr_state_class = SensorStateClass.TOTAL_INCREASING
                case (
                    FORMATS.TEMPERATUR
                    | FORMATS.POWER
                    | FORMATS.PERCENTAGE
                    | FORMATS.TIME_H
                    | FORMATS.TIME_MIN
                    | FORMATS.UNKNOWN
                ):
                    self._attr_state_class = SensorStateClass.MEASUREMENT

            if self._api_item.params is not None:
                self._attr_native_step = self._api_item.params.get("step", 1)
                self._divider = self._api_item.params.get("divider", 1)
                self._attr_device_class = self._api_item.params.get("deviceclass", None)
                self._attr_suggested_display_precision = self._api_item.params.get(
                    "precision", 2
                )
            self.set_min_max()

        if self._api_item.params is not None:
            icon = self._api_item.params.get("icon", None)
            if icon is not None:
                self._attr_icon = icon

    def set_min_max(self, onlydynamic: bool = False):
        """sets min max to fixed or dynamic values"""
        if self._api_item.params is None:
            return

        if onlydynamic is True:
            if (self._dynamic_min is None) & (self._dynamic_max is None):
                return

        self._dynamic_min = (
            self._config_entry.runtime_data.coordinator.get_value_from_item(
                self._api_item.params.get("dynamic_min", None)
            )
        )

        self._dynamic_max = (
            self._config_entry.runtime_data.coordinator.get_value_from_item(
                self._api_item.params.get("dynamic_max", None)
            )
        )

        if self._dynamic_min is not None:
            self._attr_native_min_value = self._dynamic_min / self._divider
        else:
            self._attr_native_min_value = self._api_item.params.get("min", -999999)

        if self._dynamic_max is not None:
            self._attr_native_max_value = self._dynamic_max / self._divider
        else:
            self._attr_native_max_value = self._api_item.params.get("max", 999999)

    def translate_val(self, val) -> float:
        """Translate modbus value into sensful format."""
        if self._api_item.format == FORMATS.STATUS:
            return self._api_item.get_translation_key_from_number(val)

        if val is None:
            return None
        self.set_min_max(True)
        return val / self._divider

    async def set_translate_val(self, value) -> int:
        """Translate and writes a value to the modbus."""
        if self._api_item.format == FORMATS.STATUS:
            val = self._api_item.get_number_from_translation_key(value)
        else:
            self.set_min_max(True)
            val = int(value * self._divider)

        await self._modbus_api.connect()
        mbo = ModbusObject(self._modbus_api, self._api_item)
        await mbo.setvalue(val)
        return val

    def my_device_info(self) -> DeviceInfo:
        """Build the device info."""
        return {
            "identifiers": {(CONST.DOMAIN, self._dev_device)},
            "translation_key": self._dev_device,
            "translation_placeholders": self._dev_translation_placeholders,
            "sw_version": "Device_SW_Version",
            "model": "Device_model",
            "manufacturer": "Weishaupt",
        }

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return MySensorEntity.my_device_info(self)


class MySensorEntity(CoordinatorEntity, SensorEntity, MyEntity):
    """Class that represents a sensor entity.

    Derived from Sensorentity
    and decorated with general parameters from MyEntity
    """

    def __init__(
        self,
        config_entry: MyConfigEntry,
        modbus_item: ModbusItem,
        coordinator: MyCoordinator,
        idx,
    ) -> None:
        """Initialize of MySensorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx = idx
        MyEntity.__init__(self, config_entry, modbus_item, coordinator.modbus_api)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.translate_val(self._api_item.state)
        log.debug("Entity update val:%s item:%s",str(self._attr_native_value), self._api_item.translation_key)
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return MyEntity.my_device_info(self)


class MyCalcSensorEntity(MySensorEntity):
    """class that represents a sensor entity.

    Derived from Sensorentity
    and decorated with general parameters from MyEntity
    """

    # calculates output from map
    my_map = None
    _calculation_type = None

    def __init__(
        self,
        config_entry: MyConfigEntry,
        modbus_item: ModbusItem,
        coordinator: MyCoordinator,
        idx,
    ) -> None:
        """Initialize MyCalcSensorEntity."""
        MySensorEntity.__init__(self, config_entry, modbus_item, coordinator, idx)
        if self._api_item.params is not None:
            self._calculation_type = self._api_item.params.get("calculation_type", None)

        if self._calculation_type == CALCTYPES.POWER:
            self.my_map = config_entry.runtime_data.powermap

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.translate_val(self._api_item.state)
        log.debug("Entity update val:%s item:%s",str(self._attr_native_value), self._api_item.translation_key)
        self.async_write_ha_state()

    def translate_val(self, val):
        if val is None:
            return None
        match self._calculation_type:
            case CALCTYPES.POWER:
                return self.power_val(val)
            case CALCTYPES.QUOTIENT:
                return self.quotient_val(val)
            case CALCTYPES.DIFFERENCE:
                return self.diff_val(val)

    def power_val(self, val):
        """Translate a value from the modbus."""
        val_0 = val / self._divider
        val_x = self._config_entry.runtime_data.coordinator.get_value_from_item(
            self._api_item.params.get("x", 1)
        )
        if val_x is None:
            return None
        val_y = self._config_entry.runtime_data.coordinator.get_value_from_item(
            self._api_item.params.get("y", 1)
        )
        if val_y is None:
            return None

        match self._api_item.format:
            case FORMATS.POWER:
                return round(
                    (val_0 / 100) * self.my_map.map(val_x, val_y),
                    self._attr_suggested_display_precision,
                )
            case _:
                if val_0 is None:
                    return None
                return val_0

    def quotient_val(self, val):
        """Translate a value from the modbus."""
        val_0 = val / self._divider
        val_x = self._config_entry.runtime_data.coordinator.get_value_from_item(
            self._api_item.params["denominator"]
        )
        if val_x is None:
            return None
        if val_0 is None:
            return None
        if val_x == 0:
            return None
        return round(val_0 / val_x, self._attr_suggested_display_precision)

    def diff_val(self, val):
        """Translate a value from the modbus."""
        val_0 = val / self._divider
        val_x = self._config_entry.runtime_data.coordinator.get_value_from_item(
            self._api_item.params["diff_val"]
        )
        if val_x is None:
            return None
        if val_0 is None:
            return None
        return round(
            val_0 - val_x / self._divider, self._attr_suggested_display_precision
        )


class MyNumberEntity(CoordinatorEntity, NumberEntity, MyEntity):
    """Represent a Number Entity.

    Class that represents a sensor entity derived from Sensorentity
    and decorated with general parameters from MyEntity
    """

    def __init__(
        self,
        config_entry: MyConfigEntry,
        modbus_item: ModbusItem,
        coordinator: MyCoordinator,
        idx,
    ) -> None:
        """Initialize NyNumberEntity."""
        super().__init__(coordinator, context=idx)
        self._idx = idx
        MyEntity.__init__(self, config_entry, modbus_item, coordinator.modbus_api)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.translate_val(self._api_item.state)
        log.debug("Entity update val:%s item:%s",str(self._attr_native_value), self._api_item.translation_key)
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Send value over modbus and refresh HA."""
        self._api_item.state = await self.set_translate_val(value)
        self._attr_native_value = self.translate_val(self._api_item.state)
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return MyEntity.my_device_info(self)


class MySelectEntity(CoordinatorEntity, SelectEntity, MyEntity):
    """Class that represents a sensor entity.

    Class that represents a sensor entity derived from Sensorentity
    and decorated with general parameters from MyEntity
    """

    def __init__(
        self,
        config_entry: MyConfigEntry,
        modbus_item: ModbusItem,
        coordinator: MyCoordinator,
        idx,
    ) -> None:
        """Initialze MySelectEntity."""
        super().__init__(coordinator, context=idx)
        self._idx = idx
        MyEntity.__init__(self, config_entry, modbus_item, coordinator.modbus_api)
        self.async_internal_will_remove_from_hass_port = self._config_entry.data[
            CONF.PORT
        ]
        # option list build from the status list of the ModbusItem
        self.options = []
        for _useless, item in enumerate(self._api_item._resultlist):
            self.options.append(item.translation_key)
        self._attr_current_option = "FEHLER"

    async def async_select_option(self, option: str) -> None:
        """Write the selected option to modbus and refresh HA."""
        self._api_item.state = await self.set_translate_val(option)
        self._attr_current_option = self.translate_val(self._api_item.state)
        log.debug("Entity update opt:%s item:%s",str(self._attr_current_option), self._api_item.translation_key)
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_current_option = self.translate_val(self._api_item.state)
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return MyEntity.my_device_info(self)


class MyWebifSensorEntity(CoordinatorEntity, SensorEntity, MyEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    _api_item = None
    _attr_name = None

    _attr_native_unit_of_measurement = None
    _attr_device_class = None
    _attr_state_class = None

    def __init__(
        self,
        config_entry: MyConfigEntry,
        api_item: WebItem,
        coordinator: MyWebIfCoordinator,
        idx,
    ) -> None:
        """Initialize of MySensorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx = idx
        MyEntity.__init__(
            self=self, config_entry=config_entry, api_item=api_item, modbus_api=None
        )
        self.idx = idx
        self._api_item = api_item
        self._attr_name = api_item.name

        dev_prefix = CONST.DEF_PREFIX
        dev_prefix = self._config_entry.data[CONF.PREFIX]
        if self._config_entry.data[CONF.DEVICE_POSTFIX] == "_":
            dev_postfix = ""
        else:
            dev_postfix = self._config_entry.data[CONF.DEVICE_POSTFIX]

        self._attr_unique_id = dev_prefix + self._api_item.name + dev_postfix + "webif"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # print(self.coordinator.data)
        if self.coordinator.data is not None:
            val = self._api_item.get_value(self.coordinator.data[self._api_item.name])
            self._attr_native_value = val
            self.async_write_ha_state()
        else:
            logging.warning(
                "Update of %s failed. None response from server", self._api_item.name
            )

    async def async_turn_on(self, **kwargs):
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()
