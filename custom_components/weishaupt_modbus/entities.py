"""Entity classes used in this integration."""

from typing import TYPE_CHECKING, Any

from config.custom_components.weishaupt_modbus.descriptions.description import (
    SensorDescription,
)
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
from .coordinator import WeishauptCoordinator


if TYPE_CHECKING:
    import logging

_LOGGER: logging.Logger = __import__("logging").getLogger(__name__)


class WeishauptSensor(
    CoordinatorEntity[WeishauptCoordinator],
    SensorEntity,
):
    """Representation of a Weishaupt sensor."""

    entity_description: SensorDescription

    def __init__(
        self,
        coordinator: WeishauptCoordinator,
        description: SensorDescription,
        config_entry: MyConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entity_description = description
        self._mac = config_entry.data[CONF.MAC]
        self._attr_has_entity_name = True
        self._attr_unique_id = (
            f"{self._mac}_{description.report_name}_{description.key}"
        )
        self._attr_translation_key = f"{description.report_name}_{description.key}"
        self._attr_device_class = description.params.device_class
        self._attr_state_class = description.params.state_class
        self._attr_native_unit_of_measurement = (
            description.params.native_unit_of_measurement
        )

    @property
    def available(self) -> bool:
        """Return whether the sensor is available."""
        return (
            super().available
            and self._entity_description.report_name in self.coordinator.data.updated
        )

    @property
    def native_value(self) -> float | None:
        """Return the sensor value."""

        value = self._entity_description.value_fn(self.coordinator.device)

        if self._entity_description.params.is_enum:
            return f"{self._entity_description.report_name}_{self._entity_description.key}_{value}"

        return value

    def my_device_info(self) -> DeviceInfo:
        """Build the device info."""
        return DeviceInfo(
            identifiers={self._entity_description.report_name},
            translation_key=f"dev_{self._entity_description.report_name}",
            # translation_placeholders=self._dev_translation_placeholders,
            sw_version="Device_SW_Version",
            model="Device_model",
            manufacturer="Weishaupt",
        )

    @property
    def device_info(self) -> DeviceInfo | None:
        """Return device info."""
        return self.my_device_info()
