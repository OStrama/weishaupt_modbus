"""my config entry."""

from dataclasses import dataclass

# Forward reference to avoid circular imports
from typing import TYPE_CHECKING, Any, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

if TYPE_CHECKING:
    from .coordinator import MyCoordinator


@dataclass
class MyData:
    """My config data."""

    modbus_api: Optional[Any] = None
    webif_api: Optional[Any] = None
    config_dir: str = ""
    hass: Optional[HomeAssistant] = None
    coordinator: Optional["MyCoordinator"] = None
    powermap: Optional[Any] = None


type MyConfigEntry = ConfigEntry[MyData]
