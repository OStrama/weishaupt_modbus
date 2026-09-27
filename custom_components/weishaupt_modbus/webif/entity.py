from config.custom_components.weishaupt_modbus.configentry import MyConfigEntry
from config.custom_components.weishaupt_modbus.const import CONF, CONST
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .coordinator import WeishauptWebifCoordinator
from .description.description import WebifSensorDescription


class WebifSensor(CoordinatorEntity[WeishauptWebifCoordinator], SensorEntity):
    """Representation of a Weishaupt WebIF sensor."""

    description: WebifSensorDescription

    def __init__(
        self,
        coordinator: WeishauptWebifCoordinator,
        description: WebifSensorDescription,
        config_entry: MyConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self.description = description
        self._mac = config_entry.data[CONF.MAC]

        self._attr_has_entity_name = True
        self._attr_unique_id = (
            f"{self._mac}_webif_{description.report_name}_{description.key}"
        )
        self._attr_translation_key = (
            f"webif_{description.report_name}_{description.key}"
        )

        self._attr_device_class = description.params.device_class
        self._attr_state_class = description.params.state_class
        self._attr_native_unit_of_measurement = (
            description.params.native_unit_of_measurement
        )
        self._attr_suggested_display_precision = (
            description.params.suggested_display_precision
        )

    @property
    def native_value(self) -> float | str | None:
        """Return the sensor value."""
        value = self.description.value(self.coordinator.api)

        if value is None:
            return None

        if self.description.params.is_enum:
            return f"{self.description.report_name}_{self.description.key}_{value}"

        return value

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        report_name = self.description.report_name

        return DeviceInfo(
            identifiers={
                (CONST.DOMAIN, "webif", self._mac, report_name),
            },
            translation_key=f"dev_webif_{report_name}",
            sw_version="Device_SW_Version",
            model="Device_model",
            manufacturer="Weishaupt",
        )
