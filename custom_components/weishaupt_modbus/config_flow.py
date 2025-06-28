"""Config flow for Weishaupt modbus integration."""

from typing import Any

from aiofiles.os import scandir
import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import CONF, CONST
from .kennfeld import get_filepath


async def build_kennfeld_list(hass: HomeAssistant) -> list[str]:
    """Browse integration directory for heat pump operation map files."""
    filepath = get_filepath(hass)

    try:
        dir_iterator = await scandir(filepath)
        kennfeld_files = [
            item.name for item in dir_iterator if "kennfeld.json" in item.name
        ]
    except OSError:
        kennfeld_files = []

    # Ensure at least one default file is available
    if not kennfeld_files:
        kennfeld_files.append("weishaupt_wbb_kennfeld.json")

    return kennfeld_files


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Validate hostname length
    if len(data[CONF_HOST]) < 3:
        raise InvalidHost("Hostname too short")

    # Additional validation could be added here:
    # - Test modbus connection
    # - Validate kennfeld file exists
    # - Test WebIF credentials if provided

    return {"title": data[CONF_HOST]}


class WeishauptModbusConfigFlow(config_entries.ConfigFlow, domain=CONST.DOMAIN):
    """Handle a config flow for Weishaupt modbus."""

    VERSION = 6
    MINOR_VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                # Check if already configured
                await self.async_set_unique_id(
                    f"{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)

            except InvalidHost:
                errors["base"] = "invalid_host"
            except ConnectionFailed:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=502): cv.port,
                vol.Optional(CONF.PREFIX, default=CONST.DEF_PREFIX): str,
                vol.Optional(CONF.DEVICE_POSTFIX, default=""): str,
                vol.Optional(
                    CONF.KENNFELD_FILE, default="weishaupt_wbb_kennfeld.json"
                ): vol.In(await build_kennfeld_list(self.hass)),
                vol.Optional(CONF.HK2, default=False): bool,
                vol.Optional(CONF.HK3, default=False): bool,
                vol.Optional(CONF.HK4, default=False): bool,
                vol.Optional(CONF.HK5, default=False): bool,
                vol.Optional(CONF.NAME_DEVICE_PREFIX, default=False): bool,
                vol.Optional(CONF.NAME_TOPIC_PREFIX, default=False): bool,
                vol.Optional(CONF.CB_WEBIF, default=False): bool,
                vol.Optional(CONF_USERNAME, default=""): str,
                vol.Optional(CONF_PASSWORD, default=""): str,
                vol.Optional(CONF.WEBIF_TOKEN, default=""): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle reconfiguration flow."""
        errors: dict[str, str] = {}
        reconfigure_entry = self._get_reconfigure_entry()

        if user_input is not None:
            try:
                await validate_input(self.hass, user_input)
                return self.async_update_reload_and_abort(
                    entry=reconfigure_entry, data_updates=user_input
                )
            except InvalidHost:
                errors["base"] = "invalid_host"
            except ConnectionFailed:
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"

        current_data = reconfigure_entry.data
        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current_data[CONF_HOST]): str,
                vol.Optional(CONF_PORT, default=current_data[CONF_PORT]): cv.port,
                vol.Optional(CONF.PREFIX, default=current_data[CONF.PREFIX]): str,
                vol.Optional(
                    CONF.DEVICE_POSTFIX, default=current_data[CONF.DEVICE_POSTFIX]
                ): str,
                vol.Optional(
                    CONF.KENNFELD_FILE,
                    default=current_data[CONF.KENNFELD_FILE],
                ): vol.In(await build_kennfeld_list(self.hass)),
                vol.Optional(CONF.HK2, default=current_data[CONF.HK2]): bool,
                vol.Optional(CONF.HK3, default=current_data[CONF.HK3]): bool,
                vol.Optional(CONF.HK4, default=current_data[CONF.HK4]): bool,
                vol.Optional(CONF.HK5, default=current_data[CONF.HK5]): bool,
                vol.Optional(
                    CONF.NAME_DEVICE_PREFIX,
                    default=current_data[CONF.NAME_DEVICE_PREFIX],
                ): bool,
                vol.Optional(
                    CONF.NAME_TOPIC_PREFIX,
                    default=current_data[CONF.NAME_TOPIC_PREFIX],
                ): bool,
                vol.Optional(CONF.CB_WEBIF, default=current_data[CONF.CB_WEBIF]): bool,
                vol.Optional(CONF_USERNAME, default=current_data[CONF_USERNAME]): str,
                vol.Optional(CONF_PASSWORD, default=current_data[CONF_PASSWORD]): str,
                vol.Optional(
                    CONF.WEBIF_TOKEN, default=current_data[CONF.WEBIF_TOKEN]
                ): str,
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""


class ConnectionFailed(exceptions.HomeAssistantError):
    """Error to indicate connection failed."""
