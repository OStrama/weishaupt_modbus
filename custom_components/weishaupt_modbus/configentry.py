"""my config entry."""

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# from .coordinator import MyCoordinator


@dataclass
class MyData:
    """My config data."""

    modbus_api: any
    webif_api: any
    config_dir: str
    hass: HomeAssistant
    coordinator: any  # MyCoordinator
    powermap: any


type MyConfigEntry = ConfigEntry[MyData]
