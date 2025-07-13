"""my config entry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

# from .coordinator import MyCoordinator


@dataclass
class MyData:
    """My config data."""

    modbus_api: Any
    webif_api: Any
    config_dir: str
    hass: HomeAssistant
    coordinator: Any  # MyCoordinator
    powermap: Any


type MyConfigEntry = ConfigEntry[MyData]
