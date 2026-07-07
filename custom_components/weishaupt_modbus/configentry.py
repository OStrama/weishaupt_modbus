"""my config entry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

if TYPE_CHECKING:
    from .coordinator import MyCoordinator, MyWebIfCoordinator


@dataclass
class MyData:
    """My config data."""

    modbus_api: Any
    webif_api: Any
    config_dir: str
    hass: HomeAssistant
    coordinator: MyCoordinator
    webif_coordinator: MyWebIfCoordinator | None
    powermap: Any


type MyConfigEntry = ConfigEntry[MyData]
