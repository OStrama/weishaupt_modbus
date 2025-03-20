"""Entity classes used in this integration."""

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .configentry import MyConfigEntry
from .const import CONF, CONST, FORMATS
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

        if self._api_item.format == FORMATS.STATUS:
            self._divider = 1
        else:
            # default state class to record all entities by default
            self._attr_state_class = SensorStateClass.MEASUREMENT
            if self._api_item.params is not None:
                self._attr_state_class = self._api_item.params.get(
                    "stateclass", SensorStateClass.MEASUREMENT
                )
                self._attr_native_unit_of_measurement = self._api_item.params.get(
                    "unit", ""
                )
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
        """Set min max to fixed or dynamic values."""
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
        """Translate modbus value into senseful format."""
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
    _calculation_source = None
    _calculation = None

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
            self._calculation_source = self._api_item.params.get("calculation", None)

        if self._calculation_source is not None:
            try:
                self._calculation = compile(
                    self._calculation_source, "calulation", "eval"
                )
            except SyntaxError:
                log.warning("Syntax error %s", self._calculation_source)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.translate_val(self._api_item.state)
        self.async_write_ha_state()

    def translate_val(self, val):
        """Translate a value from the modbus."""
        if self._calculation_source is None:
            return None
        if self._api_item.params is None:
            return None
        if "val_1" in self._calculation_source:
            val_1 = self._config_entry.runtime_data.coordinator.get_value_from_item(  # noqa: F841 pylint: disable=unused-variable
                self._api_item.params.get("val_1", 1)
            )
        if "val_2" in self._calculation_source:
            val_2 = self._config_entry.runtime_data.coordinator.get_value_from_item(  # noqa: F841 pylint: disable=unused-variable
                self._api_item.params.get("val_2", 1)
            )
        if "val_3" in self._calculation_source:
            val_3 = self._config_entry.runtime_data.coordinator.get_value_from_item(  # noqa: F841 pylint: disable=unused-variable
                self._api_item.params.get("val_3", 1)
            )
        if "val_4" in self._calculation_source:
            val_4 = self._config_entry.runtime_data.coordinator.get_value_from_item(  # noqa: F841 pylint: disable=unused-variable
                self._api_item.params.get("val_4", 1)
            )
        if "val_5" in self._calculation_source:
            val_5 = self._config_entry.runtime_data.coordinator.get_value_from_item(  # noqa: F841 pylint: disable=unused-variable
                self._api_item.params.get("val_5", 1)
            )
        if "val_6" in self._calculation_source:
            val_6 = self._config_entry.runtime_data.coordinator.get_value_from_item(  # noqa: F841 pylint: disable=unused-variable
                self._api_item.params.get("val_6", 1)
            )
        if "val_7" in self._calculation_source:
            val_7 = self._config_entry.runtime_data.coordinator.get_value_from_item(  # noqa: F841 pylint: disable=unused-variable
                self._api_item.params.get("val_7", 1)
            )
        if "val_8" in self._calculation_source:
            val_8 = self._config_entry.runtime_data.coordinator.get_value_from_item(  # noqa: F841 pylint: disable=unused-variable
                self._api_item.params.get("val_8", 1)
            )
        if "power" in self._calculation_source:
            power = self._config_entry.runtime_data.powermap  # noqa: F841 pylint: disable=unused-variable

        try:
            val_0 = val / self._divider  # noqa: F841 pylint: disable=unused-variable
            y = eval(self._calculation)  # pylint: disable=eval-used  # noqa: S307
        except ZeroDivisionError:
            return None
        except NameError:
            log.warning("Variable not defined %s", self._calculation_source)
            return None
        except TypeError:
            log.warning("No valid calculation string")
            return None
        return round(y, self._attr_suggested_display_precision)


class MyNumberEntity(CoordinatorEntity, NumberEntity, MyEntity):  # pylint: disable=abstract-method
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


class MySelectEntity(CoordinatorEntity, SelectEntity, MyEntity):  # pylint: disable=abstract-method
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
        """Initialize MySelectEntity."""
        super().__init__(coordinator, context=idx)
        self._idx = idx
        MyEntity.__init__(self, config_entry, modbus_item, coordinator.modbus_api)
        self.async_internal_will_remove_from_hass_port = self._config_entry.data[
            CONF.PORT
        ]
        # option list build from the status list of the ModbusItem
        self.options = []
        for _useless, item in enumerate(self._api_item._resultlist):  # noqa: SLF001
            self.options.append(item.translation_key)
        self._attr_current_option = "FEHLER"

    async def async_select_option(self, option: str) -> None:
        """Write the selected option to modbus and refresh HA."""
        self._api_item.state = await self.set_translate_val(option)
        self._attr_current_option = self.translate_val(self._api_item.state)
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
        try:
            if self.coordinator.data is not None:
                val = self._api_item.get_value(
                    self.coordinator.data[self._api_item.name]
                )
                self._attr_native_value = val
                self.async_write_ha_state()
            else:
                log.warning(
                    "Update of %s failed. None response from server",
                    self._api_item.name,
                )
        except KeyError:
            log.warning("Key Error: %s", self._api_item.name)

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()
