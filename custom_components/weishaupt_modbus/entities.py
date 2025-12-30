"""Entity classes used in this integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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

if TYPE_CHECKING:
    import logging

_LOGGER: logging.Logger = __import__("logging").getLogger(__name__)


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
    _has_dynamic_min = False
    _has_dynamic_max = False
    _dev_device_base: str = ""

    def __init__(
        self,
        config_entry: MyConfigEntry,
        api_item: ModbusItem | WebItem,
        modbus_api: ModbusAPI | MyWebIfCoordinator,
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
            device_key = self._api_item.device
            name_topic_prefix = f"{reverse_device_list.get(device_key, 'UK')}_"
        else:
            name_topic_prefix = ""

        name_prefix = name_topic_prefix + name_device_prefix

        self._dev_device = self._api_item.device + dev_postfix
        self._dev_device_base = self._api_item.device

        self._attr_translation_key = self._api_item.translation_key
        self._attr_translation_placeholders = {"prefix": name_prefix}
        self._dev_translation_placeholders = {"postfix": dev_postfix}

        if isinstance(self._api_item, ModbusItem):
            self._attr_unique_id = create_unique_id(self._config_entry, self._api_item)
        else:
            # For WebItem, create a simple unique ID
            dev_postfix = "_" + self._config_entry.data[CONF.DEVICE_POSTFIX]
            if dev_postfix == "_":
                dev_postfix = ""
            dev_prefix = self._config_entry.data[CONF.PREFIX]
            self._attr_unique_id = (
                f"{dev_prefix}_{self._api_item.name}{dev_postfix}_webif"
            )

        self._modbus_api = modbus_api

        if self._api_item.format == FORMATS.STATUS:
            self._divider = 1
        else:
            # Set attributes for non-status items
            if self._api_item.params is not None:
                self._attr_native_unit_of_measurement = self._api_item.params.get(
                    "unit", ""
                )
                self._attr_native_step = self._api_item.params.get("step", 1)
                self._divider = self._api_item.params.get("divider", 1)
                self._attr_device_class = self._api_item.params.get("deviceclass", None)
                self._attr_suggested_display_precision = self._api_item.params.get(
                    "precision", 2
                )
                self._attr_native_min_value = self._api_item.params.get("min", -999999)
                self._attr_native_max_value = self._api_item.params.get("max", 999999)
                if self._api_item.params.get("dynamic_min", None) is not None:
                    self._has_dynamic_min = True
                if self._api_item.params.get("dynamic_max", None) is not None:
                    self._has_dynamic_max = True
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
            if (self._has_dynamic_min is False) & (self._has_dynamic_max is False):
                return

        if self._has_dynamic_min:
            self._dynamic_min = (
                self._config_entry.runtime_data.coordinator.get_value_from_item(
                    self._api_item.params.get("dynamic_min", None)
                )
            )
            if self._dynamic_min is not None:
                self._attr_native_min_value = self._dynamic_min / self._divider

        if self._has_dynamic_max:
            self._dynamic_max = (
                self._config_entry.runtime_data.coordinator.get_value_from_item(
                    self._api_item.params.get("dynamic_max", None)
                )
            )
            if self._dynamic_max is not None:
                self._attr_native_max_value = self._dynamic_max / self._divider

    def translate_val(self, val: Any) -> float | str | None:
        """Translate modbus value into senseful format."""
        if self._api_item.format == FORMATS.STATUS:
            return self._api_item.get_translation_key_from_number(val)

        if val is None:
            return None
        self.set_min_max(True)
        return float(val) / self._divider

    async def set_translate_val(self, value: str | float) -> int | None:
        """Translate and writes a value to the modbus."""
        if not isinstance(self._api_item, ModbusItem):
            return None

        if self._api_item.format == FORMATS.STATUS:
            val = self._api_item.get_number_from_translation_key(str(value))
        else:
            self.set_min_max(True)
            val = int(float(value) * self._divider)

        if val is None:
            return None

        if not isinstance(self._modbus_api, ModbusAPI):
            return None

        await self._modbus_api.connect()
        mbo = ModbusObject(self._modbus_api, self._api_item)
        await mbo.set_value(val)
        return val

    def my_device_info(self) -> DeviceInfo:
        """Build the device info."""
        return DeviceInfo(
            identifiers={(CONST.DOMAIN, str(self._dev_device))},
            translation_key=str(self._dev_device_base),
            translation_placeholders=self._dev_translation_placeholders,
            sw_version="Device_SW_Version",
            model="Device_model",
            manufacturer="Weishaupt",
        )

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        return self.my_device_info()


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

        # Set sensor-specific state class
        if modbus_item.format != FORMATS.STATUS:
            # default state class to record all entities by default
            self._attr_state_class = SensorStateClass.MEASUREMENT
            if modbus_item.params is not None:
                self._attr_state_class = modbus_item.params.get(
                    "stateclass", SensorStateClass.MEASUREMENT
                )

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
                    self._calculation_source, "calculation", "eval"
                )
            except SyntaxError:
                _LOGGER.warning("Syntax error %s", self._calculation_source)

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
            if self._calculation is not None:
                y = eval(self._calculation)  # pylint: disable=eval-used  # noqa: S307
            else:
                return None
        except ZeroDivisionError:
            return None
        except NameError:
            _LOGGER.warning("Variable not defined %s", self._calculation_source)
            return None
        except TypeError:
            _LOGGER.warning("No valid calculation string")
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
        idx: Any,
    ) -> None:
        """Initialize NyNumberEntity."""
        super().__init__(coordinator, context=idx)
        self._idx = idx
        MyEntity.__init__(self, config_entry, modbus_item, coordinator.modbus_api)

    def translate_val_number(self, val: Any) -> float | None:
        """Translate modbus value for number entity."""
        if val is None:
            return None
        self.set_min_max(True)
        return float(val) / self._divider

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.translate_val_number(self._api_item.state)
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Send value over modbus and refresh HA."""
        result = await self.set_translate_val(value)
        if result is not None:
            self._api_item.state = result
            self._attr_native_value = self.translate_val_number(self._api_item.state)
            self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        return self.my_device_info()


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
        idx: Any,
    ) -> None:
        """Initialize MySelectEntity."""
        super().__init__(coordinator, context=idx)
        self._idx = idx
        MyEntity.__init__(self, config_entry, modbus_item, coordinator.modbus_api)
        self.async_internal_will_remove_from_hass_port = self._config_entry.data[
            CONF.PORT
        ]
        # option list build from the status list of the ModbusItem
        self._attr_options: list[str] = []
        for _useless, item in enumerate(self._api_item._resultlist):  # noqa: SLF001
            self._attr_options.append(item.translation_key)
        self._attr_current_option = "FEHLER"

    def translate_val_select(self, val: Any) -> str | None:
        """Translate modbus value for select entity."""
        if self._api_item.format == FORMATS.STATUS:
            result = self._api_item.get_translation_key_from_number(val)
            return str(result) if result is not None else None
        return None

    async def async_select_option(self, option: str) -> None:
        """Write the selected option to modbus and refresh HA."""
        result = await self.set_translate_val(option)
        if result is not None:
            self._api_item.state = result
            self._attr_current_option = self.translate_val_select(self._api_item.state)
            self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_current_option = self.translate_val_select(self._api_item.state)
        self.async_write_ha_state()

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        return self.my_device_info()


class MyWebifSensorEntity(CoordinatorEntity, SensorEntity, MyEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    _api_item: WebItem

    def __init__(
        self,
        config_entry: MyConfigEntry,
        api_item: WebItem,
        coordinator: MyWebIfCoordinator,
        idx: Any,
    ) -> None:
        """Initialize of MySensorEntity."""
        super().__init__(coordinator, context=idx)
        self.idx = idx
        MyEntity.__init__(self, config_entry, api_item, coordinator)

        # Initialize MyEntity with minimal parameters
        self._config_entry = config_entry
        self._api_item = api_item

        # Set basic attributes without calling MyEntity.__init__
        dev_prefix = self._config_entry.data[CONF.PREFIX]
        if self._config_entry.data[CONF.DEVICE_POSTFIX] == "_":
            dev_postfix = ""
        else:
            dev_postfix = self._config_entry.data[CONF.DEVICE_POSTFIX]

        self._attr_unique_id = f"{dev_prefix}_{self._api_item.name}{dev_postfix}_webif"
        self._attr_name = api_item.name

        # Set sensor-specific attributes
        self._attr_state_class = SensorStateClass.MEASUREMENT

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
                _LOGGER.warning(
                    "Update of %s failed. None response from server",
                    self._api_item.name,
                )
        except KeyError:
            _LOGGER.warning("Key Error: %s", self._api_item.name)

    async def async_turn_on(self, **kwargs):  # pylint: disable=unused-argument
        """Turn the light on.

        Example method how to request data updates.
        """
        # Do the turning on.
        # ...

        # Update the data
        await self.coordinator.async_request_refresh()
