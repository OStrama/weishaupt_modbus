"""Entity classes used in this integration."""

from typing import TYPE_CHECKING

from homeassistant.components.number import NumberEntity
from homeassistant.components.select import SelectEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .configentry import MyConfigEntry
from .const import CONF, CONST
from .coordinator import WeishauptCoordinator
from .descriptions.description import (
    EntityDescription,
    NumberDescription,
    SelectDescription,
    SensorDescription,
)

if TYPE_CHECKING:
    import logging

    _LOGGER: logging.Logger = __import__("logging").getLogger(__name__)


class WeishauptEntity(CoordinatorEntity[WeishauptCoordinator]):
    """Base entity for Weishaupt devices."""

    description: EntityDescription

    def __init__(
        self,
        coordinator: WeishauptCoordinator,
        description: EntityDescription,
        config_entry: MyConfigEntry,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

        self.description = description
        self._mac = config_entry.data[CONF.MAC]

        self._attr_has_entity_name = True
        self._attr_unique_id = (
            f"{self._mac}_{description.report_name}_{description.key}"
        )
        self._attr_translation_key = f"{description.report_name}_{description.key}"

    @property
    def available(self) -> bool:
        """Return whether the entity is available."""
        return (
            super().available
            and self.description.report_name in self.coordinator.data.updated
        )

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        report_name = self.description.report_name

        return DeviceInfo(
            identifiers={
                (CONST.DOMAIN, self._mac, report_name),
            },
            translation_key=f"dev_{report_name}",
            sw_version="Device_SW_Version",
            model="Device_model",
            manufacturer="Weishaupt",
        )


class WeishauptSensor(WeishauptEntity, SensorEntity):
    """Representation of a Weishaupt sensor."""

    description: SensorDescription

    def __init__(
        self,
        coordinator: WeishauptCoordinator,
        description: SensorDescription,
        config_entry: MyConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description, config_entry)

        self._attr_device_class = description.params.device_class
        self._attr_state_class = description.params.state_class
        self._attr_native_unit_of_measurement = (
            description.params.native_unit_of_measurement
        )

    @property
    def native_value(self) -> float | str | None:
        """Return the sensor value."""
        value = self.description.value_fn(self.coordinator.device)

        if value is None:
            return None

        if self.description.params.is_enum:
            return f"{self.description.report_name}_{self.description.key}_{value}"

        return value


class WeishauptNumber(WeishauptEntity, NumberEntity):
    """Representation of a Weishaupt number."""

    description: NumberDescription

    def __init__(
        self,
        coordinator: WeishauptCoordinator,
        description: NumberDescription,
        config_entry: MyConfigEntry,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator, description, config_entry)

        self._attr_device_class = description.params.device_class
        self._attr_native_unit_of_measurement = (
            description.params.native_unit_of_measurement
        )
        self._attr_native_min_value = description.params.native_min_value
        self._attr_native_max_value = description.params.native_max_value
        self._attr_native_step = description.params.native_step

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        return self.description.value_fn(self.coordinator.device)

    async def async_set_native_value(self, value: float) -> None:
        """Set the value."""
        await self.description.set_value_fn(
            self.coordinator.device,
            value,
        )
        await self.coordinator.async_request_refresh()


class WeishauptSelect(WeishauptEntity, SelectEntity):
    """Representation of a Weishaupt select."""

    description: SelectDescription

    def __init__(
        self,
        coordinator: WeishauptCoordinator,
        description: SelectDescription,
        config_entry: MyConfigEntry,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, description, config_entry)

        self._enum = description.enum

        self._attr_options = tuple(member.name for member in self._enum)

    @property
    def current_option(self) -> str | None:
        """Return the current option."""
        value = self.description.value_fn(self.coordinator.device)

        if value is None:
            return None

        return self._enum(value).name

    async def async_select_option(self, option: str) -> None:
        """Set the selected option."""
        value = self._enum[option].value

        await self.description.set_value_fn(
            self.coordinator.device,
            value,
        )
        await self.coordinator.async_request_refresh()
