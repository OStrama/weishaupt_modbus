"""Entity classes used in this integration."""

import logging
from typing import Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .configentry import MyConfigEntry
from .const import CONF, CONST, DEVICENAMES, FormatConstants
from .coordinator import MyCoordinator, MyWebIfCoordinator
from .hpconst import reverse_device_list
from .items import ModbusItem, WebItem
from .migrate_helpers import create_unique_id
from .modbusobject import ModbusAPI, ModbusObject

_LOGGER = logging.getLogger(__name__)


class MyEntity(Entity):
    """Base entity class for Weishaupt modbus integration.

    The base class for entities that hold general parameters.
    """

    _divider: int = 1
    _attr_should_poll: bool = True
    _attr_has_entity_name: bool = True
    _dynamic_min: float | None = None
    _dynamic_max: float | None = None
    _has_dynamic_min: bool = False
    _has_dynamic_max: bool = False

    def __init__(
        self,
        config_entry: MyConfigEntry,
        api_item: ModbusItem | WebItem,
        modbus_api: ModbusAPI,
    ) -> None:
        """Initialize the entity."""
        self._config_entry = config_entry
        self._api_item: ModbusItem | WebItem = api_item
        self._modbus_api = modbus_api

        dev_postfix = f"_{self._config_entry.data[CONF.DEVICE_POSTFIX]}"
        if dev_postfix == "_":
            dev_postfix = ""

        dev_prefix = self._config_entry.data[CONF.PREFIX]

        name_device_prefix = (
            f"{dev_prefix}_" if self._config_entry.data[CONF.NAME_DEVICE_PREFIX] else ""
        )
        name_topic_prefix = (
            f"{reverse_device_list[str(self._api_item.device)]}_"
            if self._config_entry.data[CONF.NAME_TOPIC_PREFIX]
            else ""
        )

        name_prefix = name_topic_prefix + name_device_prefix

        self._dev_device = f"{self._api_item.device!s}{dev_postfix}"

        # Use _attr_ attributes to work with cached properties
        self._attr_translation_key = self._api_item.translation_key
        self._attr_translation_placeholders = {"prefix": name_prefix}
        self._dev_translation_placeholders = {"postfix": dev_postfix}
        self._attr_unique_id = create_unique_id(self._config_entry, self._api_item)

        if self._api_item.format == FormatConstants.STATUS:
            self._divider = 1
        else:
            # Set common numeric entity attributes
            if self._api_item.params is not None:
                self._attr_native_unit_of_measurement = self._api_item.params.get(
                    "unit", ""
                )
                self._attr_native_step = self._api_item.params.get("step", 1)
                self._divider = self._api_item.params.get("divider", 1)
                self._attr_device_class = self._api_item.params.get("deviceclass")
                self._attr_suggested_display_precision = self._api_item.params.get(
                    "precision", 2
                )
                self._attr_native_min_value = self._api_item.params.get("min", -999999)
                self._attr_native_max_value = self._api_item.params.get("max", 999999)
                self._has_dynamic_min = (
                    self._api_item.params.get("dynamic_min") is not None
                )
                self._has_dynamic_max = (
                    self._api_item.params.get("dynamic_max") is not None
                )
            self.set_min_max()

        if self._api_item.params is not None and (
            icon := self._api_item.params.get("icon")
        ):
            self._attr_icon = icon

    def set_min_max(self, onlydynamic: bool = False) -> None:
        """Set min max to fixed or dynamic values."""
        if self._api_item.params is None:
            return

        if onlydynamic and not (self._has_dynamic_min or self._has_dynamic_max):
            return

        coordinator = self._config_entry.runtime_data.coordinator
        if coordinator is None:
            _LOGGER.warning("Coordinator not available for dynamic min/max calculation")
            return

        if self._has_dynamic_min:
            dynamic_min_param = self._api_item.params.get("dynamic_min")
            if isinstance(dynamic_min_param, str):
                self._dynamic_min = coordinator.get_value_from_item(dynamic_min_param)
                if self._dynamic_min is not None:
                    self._attr_native_min_value = self._dynamic_min / self._divider

        if self._has_dynamic_max:
            dynamic_max_param = self._api_item.params.get("dynamic_max")
            if isinstance(dynamic_max_param, str):
                self._dynamic_max = coordinator.get_value_from_item(dynamic_max_param)
                if self._dynamic_max is not None:
                    self._attr_native_max_value = self._dynamic_max / self._divider

    def translate_val(self, val: Any) -> float | str | None:
        """Translate modbus value into senseful format."""
        if self._api_item.format == FormatConstants.STATUS:
            return self._api_item.get_translation_key_from_number(val)

        if val is None:
            return None
        self.set_min_max(True)
        return float(val) / self._divider

    async def set_translate_val(self, value: Any) -> int | None:
        """Translate and write a value to the modbus."""
        val: int | None = None

        if self._api_item.format == FormatConstants.STATUS:
            val = self._api_item.get_number_from_translation_key(value)
        else:
            self.set_min_max(True)
            val = int(float(value) * self._divider)

        # Only write to modbus if we have a ModbusItem and API
        if (
            self._modbus_api is not None
            and isinstance(self._api_item, ModbusItem)
            and val is not None
        ):
            await self._modbus_api.connect()
            mbo = ModbusObject(self._modbus_api, self._api_item)
            await mbo.setvalue(val)
        return val

    def my_device_info(self) -> DeviceInfo:
        """Build the device info."""
        device_name = getattr(DEVICENAMES, str(self._api_item.device), "Unknown Device")
        return DeviceInfo(
            identifiers={(CONST.DOMAIN, self._dev_device)},
            translation_key=self._dev_device,
            translation_placeholders=self._dev_translation_placeholders,
            sw_version="Device_SW_Version",
            model="Device_model",
            manufacturer="Weishaupt",
            name=device_name,
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return self.my_device_info()


class MySensorEntity(CoordinatorEntity[MyCoordinator], SensorEntity, MyEntity):
    """Sensor entity derived from CoordinatorEntity and SensorEntity."""

    def __init__(
        self,
        config_entry: MyConfigEntry,
        modbus_item: ModbusItem,
        coordinator: MyCoordinator,
        idx: int,
    ) -> None:
        """Initialize MySensorEntity."""
        # Use super() for proper MRO handling
        super().__init__(coordinator, context=idx)
        MyEntity.__init__(self, config_entry, modbus_item, coordinator.modbus_api)
        self.idx = idx

        # Set sensor-specific state class after MyEntity initialization
        if self._api_item.format != FormatConstants.STATUS:
            self._attr_state_class = (
                self._api_item.params.get("stateclass", SensorStateClass.MEASUREMENT)
                if self._api_item.params is not None
                else SensorStateClass.MEASUREMENT
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.translate_val(self._api_item.state)
        self.async_write_ha_state()


class MyCalcSensorEntity(MySensorEntity):
    """Calculated sensor entity with custom formulas."""

    def __init__(
        self,
        config_entry: MyConfigEntry,
        modbus_item: ModbusItem,
        coordinator: MyCoordinator,
        idx: int,
    ) -> None:
        """Initialize MyCalcSensorEntity."""
        super().__init__(config_entry, modbus_item, coordinator, idx)

        self._calculation_source: str | None = None
        self._calculation: Any = None

        if self._api_item.params is not None:
            self._calculation_source = self._api_item.params.get("calculation")

        if self._calculation_source is not None:
            try:
                self._calculation = compile(
                    self._calculation_source, "calculation", "eval"
                )
            except SyntaxError:
                _LOGGER.warning(
                    "Syntax error in calculation: %s", self._calculation_source
                )

    def translate_val(self, val: Any) -> float | None:
        """Translate a value using calculation formula."""
        if self._calculation_source is None or self._api_item.params is None:
            return None

        coordinator = self._config_entry.runtime_data.coordinator
        if coordinator is None:
            return None

        # Prepare variables for calculation
        local_vars = {"val_0": val / self._divider if val is not None else 0}

        # Add additional variables dynamically
        for i in range(1, 9):
            var_name = f"val_{i}"
            if var_name in self._calculation_source:
                param_value = self._api_item.params.get(var_name)
                if isinstance(param_value, str):
                    local_vars[var_name] = coordinator.get_value_from_item(param_value)

        if "power" in self._calculation_source:
            local_vars["power"] = self._config_entry.runtime_data.powermap

        try:
            if self._calculation is not None:
                result = eval(self._calculation, {"__builtins__": {}}, local_vars)  # noqa: S307
                return round(float(result), self._attr_suggested_display_precision or 2)
        except (ZeroDivisionError, NameError, TypeError) as err:
            _LOGGER.warning(
                "Calculation error for %s: %s", self._calculation_source, err
            )

        return None


class MyNumberEntity(CoordinatorEntity[MyCoordinator], NumberEntity, MyEntity):
    """Number entity for writable modbus values."""

    def __init__(
        self,
        config_entry: MyConfigEntry,
        modbus_item: ModbusItem,
        coordinator: MyCoordinator,
        idx: int,
    ) -> None:
        """Initialize MyNumberEntity."""
        # Use super() for proper MRO handling
        super().__init__(coordinator, context=idx)
        MyEntity.__init__(self, config_entry, modbus_item, coordinator.modbus_api)
        self._idx = idx

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        translated_val = self.translate_val(self._api_item.state)
        if isinstance(translated_val, (int, float)):
            self._attr_native_value = float(translated_val)
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Send value over modbus and refresh HA."""
        self._api_item.state = await self.set_translate_val(value)
        translated_val = self.translate_val(self._api_item.state)
        if isinstance(translated_val, (int, float)):
            self._attr_native_value = float(translated_val)
        self.async_write_ha_state()


class MySelectEntity(CoordinatorEntity[MyCoordinator], SelectEntity, MyEntity):
    """Select entity for status modbus values."""

    def __init__(
        self,
        config_entry: MyConfigEntry,
        modbus_item: ModbusItem,
        coordinator: MyCoordinator,
        idx: int,
    ) -> None:
        """Initialize MySelectEntity."""
        # Use super() for proper MRO handling
        super().__init__(coordinator, context=idx)
        MyEntity.__init__(self, config_entry, modbus_item, coordinator.modbus_api)
        self._idx = idx

        # Store port reference for cleanup
        self.async_internal_will_remove_from_hass_port = self._config_entry.data[
            CONF.PORT
        ]

        # Build option list from the status list of the ModbusItem
        self._attr_options = []
        if self._api_item.resultlist is not None:
            for item in self._api_item.resultlist:
                self._attr_options.append(item.translation_key)

        # Set default current option
        self._attr_current_option = "FEHLER"

    async def async_select_option(self, option: str) -> None:
        """Write the selected option to modbus and refresh HA."""
        self._api_item.state = await self.set_translate_val(option)
        translated_val = self.translate_val(self._api_item.state)
        if isinstance(translated_val, str):
            self._attr_current_option = translated_val
        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        translated_val = self.translate_val(self._api_item.state)
        if isinstance(translated_val, str):
            self._attr_current_option = translated_val
        self.async_write_ha_state()


class MyWebifSensorEntity(CoordinatorEntity[MyWebIfCoordinator], SensorEntity):
    """WebIF sensor entity for web interface data."""

    def __init__(
        self,
        config_entry: MyConfigEntry,
        api_item: WebItem,
        coordinator: MyWebIfCoordinator,
        idx: int,
    ) -> None:
        """Initialize MyWebifSensorEntity."""
        super().__init__(coordinator, context=idx)
        self._config_entry = config_entry
        self._api_item = api_item
        self.idx = idx

        # Use _attr_ pattern for cached properties
        self._attr_name = api_item.name

        dev_prefix = self._config_entry.data[CONF.PREFIX]
        dev_postfix = (
            ""
            if self._config_entry.data[CONF.DEVICE_POSTFIX] == "_"
            else self._config_entry.data[CONF.DEVICE_POSTFIX]
        )

        self._attr_unique_id = f"{dev_prefix}{api_item.name}{dev_postfix}webif"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        try:
            if (
                self.coordinator.data is not None
                and self._api_item.name in self.coordinator.data
            ):
                val = self._api_item.get_value(
                    self.coordinator.data[self._api_item.name]
                )
                self._attr_native_value = val
                self.async_write_ha_state()
            else:
                _LOGGER.debug(
                    "Update of %s failed - no data from server", self._api_item.name
                )
        except KeyError:
            _LOGGER.debug("Key error for %s", self._api_item.name)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Request data updates."""
        await self.coordinator.async_request_refresh()
