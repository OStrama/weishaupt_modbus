"""Entity classes used in this integration."""

from typing import TYPE_CHECKING, Any

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .configentry import MyConfigEntry
from .const import CONF, CONST, FORMATS
from .coordinator import MyWebIfCoordinator, WeishauptModbusCoordinator
from .hpconst import reverse_device_list
from .items import ModbusItem, WebItem
from .migrate_helpers import create_unique_id

if TYPE_CHECKING:
    import logging

_LOGGER: logging.Logger = __import__("logging").getLogger(__name__)


class MyEntity(Entity):
    """An entity using CoordinatorEntity."""

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
            dev_postfix = "_" + self._config_entry.data[CONF.DEVICE_POSTFIX]
            if dev_postfix == "_":
                dev_postfix = ""
            dev_prefix = self._config_entry.data[CONF.PREFIX]
            self._attr_unique_id = (
                f"{dev_prefix}_{self._api_item.name}{dev_postfix}_webif"
            )

        if self._api_item.format == FORMATS.STATUS:
            self._divider = 1
        elif self._api_item.format == FORMATS.TEXT:
            self._attr_suggested_display_precision = None
        else:
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
        if self._api_item is None or self._api_item.params is None:
            return

        if onlydynamic is True:
            if (self._has_dynamic_min is False) & (self._has_dynamic_max is False):
                return

        if self._has_dynamic_min:
            min_key = self._api_item.params.get("dynamic_min") or ""
            # Safely fetch the dynamic min from the coordinator
            self._dynamic_min = self.coordinator.get_value_from_item(min_key)
            if self._dynamic_min is not None:
                self._attr_native_min_value = self._dynamic_min / self._divider

        if self._has_dynamic_max:
            max_key = self._api_item.params.get("dynamic_max") or ""
            # Safely fetch the dynamic max from the coordinator
            self._dynamic_max = self.coordinator.get_value_from_item(max_key)
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
        """Translate and write a value directly to the Modbus client."""
        if not isinstance(self._api_item, ModbusItem):
            return None

        if self._api_item.format == FORMATS.STATUS:
            val = self._api_item.get_number_from_translation_key(str(value))
        else:
            self.set_min_max(True)
            val = int(float(value) * self._divider)

        if val is None:
            return None

        address = getattr(self._api_item, "_address", None) or getattr(
            self._api_item, "address", None
        )
        if address is None:
            _LOGGER.error(
                "Cannot write value: No register address found for %s",
                self._api_item.translation_key,
            )
            return None

        try:
            client = getattr(self.coordinator, "client", None)
            if client is None:
                _LOGGER.error(
                    "Cannot write value: Coordinator does not contain a Modbus client"
                )
                return None

            await client.write_register(address=address, value=val)
            return val
        except Exception as err:
            _LOGGER.error("Failed to write to register %s: %s", address, err)
            return None

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
        coordinator: WeishauptModbusCoordinator,
        idx,
    ) -> None:
        """Initialize of MySensorEntity."""

        super().__init__(coordinator, context=idx)
        self.idx = idx
        MyEntity.__init__(self, config_entry, modbus_item)

        # Set sensor-specific state class
        if modbus_item.format in [
            FORMATS.TEMPERATURE,
            FORMATS.PERCENTAGE,
            FORMATS.NUMBER,
            FORMATS.UNKNOWN,
        ]:
            # default state class to record all entities by default
            self._attr_state_class = SensorStateClass.MEASUREMENT
            if modbus_item.params is not None:
                self._attr_state_class = modbus_item.params.get(
                    "stateclass", SensorStateClass.MEASUREMENT
                )
        if modbus_item.format == FORMATS.TEXT:
            # self._attr_state_class = SensorStateClass.NONE
            self._attr_suggested_display_precision = None

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
    """Class that represents a calculated sensor entity."""

    _calculation_source = None
    _calculation = None

    def __init__(
        self,
        config_entry: MyConfigEntry,
        modbus_item: ModbusItem,
        coordinator: WeishauptModbusCoordinator,
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
                _LOGGER.warning(
                    "Syntax error in calculation formula: %s", self._calculation_source
                )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_native_value = self.translate_val(self._api_item.state)
        self.async_write_ha_state()

    async def async_added_to_hass(self) -> None:
        """When entity is added to Hass, perform immediate initial calculation."""
        await super().async_added_to_hass()
        # Force a calculation using the standard sensors' freshly loaded boot states
        self._attr_native_value = self.translate_val(self._api_item.state)
        self.async_write_ha_state()

    def translate_val(self, val: Any) -> float | None:
        """Translate a value from the modbus in-memory with custom console logging."""

        if self._calculation_source is None or self._api_item.params is None:
            return None

        # Build the local namespace dictionary dynamically
        eval_locals: dict[str, Any] = {}

        # 1. Get this calculated sensor's own Modbus register address
        address = getattr(self._api_item, "_address", None) or getattr(
            self._api_item, "address", None
        )
        # 2. Fetch its raw polled value directly from the batch cache
        fetched_raw = (
            self.coordinator.client.get_value(address) if address is not None else None
        )

        # Pull val_0 to val_8 dynamically if they are referenced in the formula
        for i in range(9):
            var_name = f"val_{i}"
            if var_name in self._calculation_source:
                # Fetch key from params (e.g. "vl_temp", "ges_volumenstrom", etc.)
                key_map = self._api_item.params.get(var_name, None)

                if key_map is not None:
                    # Fetch from the standalone standard sensor in memory
                    fetched_val = self.coordinator.get_value_from_item(key_map)

                    if var_name == "val_0":
                        eval_locals[var_name] = (
                            (fetched_val / self._divider)
                            if fetched_val is not None
                            else 0.0
                        )
                    else:
                        eval_locals[var_name] = fetched_val
                # Fallback if no mapping exists in params (retrieve val_0 from our own cached register)
                elif var_name == "val_0":
                    eval_locals[var_name] = (
                        (fetched_raw / self._divider)
                        if fetched_raw is not None
                        else 0.0
                    )
                else:
                    eval_locals[var_name] = None

        # Include powermap if referenced
        if "power" in self._calculation_source:
            eval_locals["power"] = self._config_entry.runtime_data.powermap

        # Perform the evaluation
        try:
            if self._calculation is not None:
                y = eval(self._calculation, {}, eval_locals)  # pylint: disable=eval-used  # noqa: S307
            else:
                return None
        except ZeroDivisionError:
            return 0.0

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
        coordinator: WeishauptModbusCoordinator,
        idx: Any,
    ) -> None:
        """Initialize NyNumberEntity."""
        super().__init__(coordinator, context=idx)
        self._idx = idx
        MyEntity.__init__(self, config_entry, modbus_item)  # , coordinator.modbus_api)

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
        coordinator: WeishauptModbusCoordinator,
        idx: Any,
    ) -> None:
        """Initialize MySelectEntity."""
        super().__init__(coordinator, context=idx)
        self._idx = idx
        MyEntity.__init__(self, config_entry, modbus_item)
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

        # Set unique id with translation key as it is a good choice for the webif items
        self._attr_unique_id = self._api_item.translation_key
        self._attr_translation_key = self._api_item.translation_key
        self._attr_has_entity_name = True

        if self._api_item.format == FORMATS.TEXT:
            self._attr_suggested_display_precision = None
            self._attr_device_class = None
            self._attr_state_class = None
        # WebItem.get_value() strips the unit text ("26.0 °C" -> "26.0"), so set
        # unit + device class explicitly for the well-known scalar formats. Items
        # that carry params get their device_class from MyEntity.__init__ as well.
        elif self._api_item.format == FORMATS.TEMPERATURE:
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_suggested_display_precision = 1
        elif self._api_item.format == FORMATS.PERCENTAGE:
            self._attr_native_unit_of_measurement = PERCENTAGE
            self._attr_state_class = SensorStateClass.MEASUREMENT

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # print(self.coordinator.data)
        try:
            if self.coordinator.data is not None:
                raw = self._api_item.get_value(
                    self.coordinator.data[self._api_item.name]
                )
                # get_value() returns a scraped string. Any sensor that carries a
                # numeric device_class / state_class must expose a numeric (or None)
                # native value, otherwise Home Assistant crashes converting a value
                # like "Aus" via int()/float() (issue #159). Coerce for every numeric
                # sensor, not just TEMPERATURE/PERCENTAGE. A non-numeric reading falls
                # back to the item's "non_numeric_value" param (None by default, e.g.
                # 0 for power sensors that report "off" as text in various languages).
                value: float | str | None = raw
                if (
                    getattr(self, "_attr_device_class", None) is not None
                    or getattr(self, "_attr_state_class", None) is not None
                ):
                    try:
                        value = None if raw is None else float(raw)
                    except ValueError:
                        fallback = self._api_item.params.get("non_numeric_value")
                        _LOGGER.debug(
                            "WebIF sensor %s: non-numeric value %r, using %r",
                            self._api_item.name,
                            raw,
                            fallback,
                        )
                        value = fallback
                self._attr_native_value = value
                self.async_write_ha_state()
            else:
                _LOGGER.warning(
                    "Update of %s failed. None response from server",
                    self._api_item.name,
                )
        except KeyError:
            _LOGGER.warning("Key Error: %s", self._api_item.name)

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        return self.my_device_info()
