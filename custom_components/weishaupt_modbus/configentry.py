"""my config entry."""

from dataclasses import dataclass
from typing import Any

from config.custom_components.weishaupt_modbus.coordinator import WeishauptCoordinator
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


@dataclass
class MyData:
    """My config data."""

    config_dir: str
    hass: HomeAssistant
    powermap: Any
    weishaupt_coordinator: WeishauptCoordinator


type MyConfigEntry = ConfigEntry[MyData]
