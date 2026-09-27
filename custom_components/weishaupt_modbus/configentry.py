"""my config entry."""

import asyncio
from dataclasses import dataclass
from typing import Any

from weishaupt_webif_api import WebifConnection

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .modbus.coordinator import WeishauptCoordinator
from .webif.coordinator import WeishauptWebifCoordinator


@dataclass
class MyData:
    """My config data."""

    config_dir: str
    hass: HomeAssistant
    powermap: Any
    mcu_lock: asyncio.Lock
    weishaupt_coordinator: WeishauptCoordinator
    webif_api: WebifConnection | None = None
    webif_coordinator: WeishauptWebifCoordinator | None = None


type MyConfigEntry = ConfigEntry[MyData]
