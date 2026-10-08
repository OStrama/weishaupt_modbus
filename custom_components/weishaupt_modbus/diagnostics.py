"""Diagnostics support for Weishaupt Modbus."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from .configentry import MyData
from .const import CONF

TO_REDACT = {
    CONF.HOST,
    CONF.MAC,
    CONF.PASSWORD,
    CONF.USERNAME,
    CONF.WEBIF_TOKEN,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry[MyData],
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    runtime_data = entry.runtime_data
    coordinator = runtime_data.weishaupt_coordinator

    return {
        "config_entry": async_redact_data(entry.data, TO_REDACT),
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "data": {
                "updated": sorted(coordinator.data.updated),
                "failed": {
                    name: str(error) for name, error in coordinator.data.failed.items()
                },
            },
        },
        "webif": {
            "enabled": runtime_data.webif_api is not None,
            "coordinator_available": runtime_data.webif_coordinator is not None,
        },
    }
