"""Config flow."""

from typing import Any

from aiofiles.os import scandir
import voluptuous as vol

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv

from .const import CONF, CONST
from .kennfeld import get_filepath


async def build_kennfeld_list(hass: HomeAssistant) -> list[str]:
    """Browse integration directory for heat pump operation map ("kennfeld") files."""
    kennfelder = []
    try:
        dir_iterator = await scandir(get_filepath(hass))
        for item in dir_iterator:
            if "kennfeld.json" in item.name:
                kennfelder.append(item.name)
    except OSError:
        pass

    if len(kennfelder) < 1:
        kennfelder.append("weishaupt_wbb_kennfeld.json")

    return kennfelder


async def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the input."""
    if len(data.get(CONF.HOST, "")) < 3:
        raise InvalidHost
    return {"title": data[CONF.HOST]}


class ConfigFlow(config_entries.ConfigFlow, domain=CONST.DOMAIN):  # pylint: disable=abstract-method
    """Class config flow."""

    VERSION = 8
    MINOR_VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self) -> None:
        """Initialize the flow."""
        self._stored_data: dict[str, Any] = {}
        self._reconfigure_entry: config_entries.ConfigEntry | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 1: Core configuration setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                await validate_input(user_input)
                self._stored_data.update(user_input)

                # Check if we need to progress to Page 2 (Web Interface)
                if user_input.get(CONF.CB_WEBIF):
                    return await self.async_step_webif()

                # Otherwise, complete configuration immediately
                return self.async_create_entry(
                    title=self._stored_data[CONF.HOST], data=self._stored_data
                )

            except InvalidHost:
                errors["base"] = "invalid_host"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"

        # Define Schema for Page 1
        schema_page1 = vol.Schema(
            schema={
                vol.Required(
                    schema=CONF.HOST,
                    default=self._stored_data.get(CONF.HOST, ""),
                ): str,
                vol.Optional(
                    schema=CONF.PORT,
                    default=self._stored_data.get(CONF.PORT, "502"),
                ): cv.port,
                vol.Optional(
                    schema=CONF.PREFIX,
                    default=self._stored_data.get(CONF.PREFIX, CONST.DEF_PREFIX),
                ): str,
                vol.Optional(
                    schema=CONF.DEVICE_POSTFIX,
                    default=self._stored_data.get(CONF.DEVICE_POSTFIX, ""),
                ): str,
                vol.Optional(
                    schema=CONF.KENNFELD_FILE,
                    default=self._stored_data.get(
                        CONF.KENNFELD_FILE, "weishaupt_wbb_kennfeld.json"
                    ),
                ): vol.In(container=await build_kennfeld_list(self.hass)),
                vol.Optional(
                    schema=CONF.HK2,
                    default=self._stored_data.get(CONF.HK2, False),
                ): bool,
                vol.Optional(
                    schema=CONF.HK3,
                    default=self._stored_data.get(CONF.HK3, False),
                ): bool,
                vol.Optional(
                    schema=CONF.HK4,
                    default=self._stored_data.get(CONF.HK4, False),
                ): bool,
                vol.Optional(
                    schema=CONF.HK5,
                    default=self._stored_data.get(CONF.HK5, False),
                ): bool,
                vol.Optional(
                    schema=CONF.NAME_DEVICE_PREFIX,
                    default=self._stored_data.get(CONF.NAME_DEVICE_PREFIX, False),
                ): bool,
                vol.Optional(
                    schema=CONF.NAME_TOPIC_PREFIX,
                    default=self._stored_data.get(CONF.NAME_TOPIC_PREFIX, False),
                ): bool,
                vol.Optional(
                    schema=CONF.CB_WEBIF,
                    default=self._stored_data.get(CONF.CB_WEBIF, False),
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema_page1, errors=errors
        )

    async def async_step_webif(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2: Experimental Web Interface setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._stored_data.update(user_input)

            # If we are in a reconfigure flow, finalize the updates
            if self._reconfigure_entry:
                return self.async_update_and_abort(
                    entry=self._reconfigure_entry, data_updates=self._stored_data
                )

            # Standard creation path
            return self.async_create_entry(
                title=self._stored_data[CONF.HOST], data=self._stored_data
            )

        # Define Schema for Page 2
        schema_page2 = vol.Schema(
            schema={
                vol.Optional(
                    schema=CONF.CB_WEBIF_MOCKUP_DATA,
                    default=self._stored_data.get(CONF.CB_WEBIF_MOCKUP_DATA, False),
                ): bool,
                vol.Optional(
                    schema=CONF.USERNAME,
                    default=self._stored_data.get(CONF.USERNAME, ""),
                ): str,
                vol.Optional(
                    schema=CONF.PASSWORD,
                    default=self._stored_data.get(CONF.PASSWORD, ""),
                ): str,
                vol.Optional(
                    schema=CONF.WEBIF_TOKEN,
                    default=self._stored_data.get(CONF.WEBIF_TOKEN, ""),
                ): str,
                vol.Optional(
                    schema=CONF.CB_WEBIF_HK1,
                    default=self._stored_data.get(CONF.CB_WEBIF_HK1, False),
                ): bool,
                vol.Optional(
                    schema=CONF.CB_WEBIF_HK2,
                    default=self._stored_data.get(CONF.CB_WEBIF_HK2, False),
                ): bool,
                vol.Optional(
                    schema=CONF.CB_WEBIF_HK3,
                    default=self._stored_data.get(CONF.CB_WEBIF_HK3, False),
                ): bool,
                vol.Optional(
                    schema=CONF.CB_WEBIF_HK4,
                    default=self._stored_data.get(CONF.CB_WEBIF_HK4, False),
                ): bool,
                vol.Optional(
                    schema=CONF.CB_WEBIF_HK5,
                    default=self._stored_data.get(CONF.CB_WEBIF_HK5, False),
                ): bool,
                vol.Optional(
                    schema=CONF.CB_WEBIF_WP,
                    default=self._stored_data.get(CONF.CB_WEBIF_WP, False),
                ): bool,
                vol.Optional(
                    schema=CONF.CB_WEBIF_2WEZ,
                    default=self._stored_data.get(CONF.CB_WEBIF_2WEZ, False),
                ): bool,
                vol.Optional(
                    schema=CONF.CB_WEBIF_SATISTICS,
                    default=self._stored_data.get(CONF.CB_WEBIF_SATISTICS, False),
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="webif", data_schema=schema_page2, errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Trigger a reconfiguration flow."""
        errors: dict[str, str] = {}
        self._reconfigure_entry = self._get_reconfigure_entry()

        # Pre-seed internal state dictionary with the current saved entry data
        if not self._stored_data:
            self._stored_data.update(self._reconfigure_entry.data)

        if user_input is not None:
            try:
                await validate_input(user_input)
                self._stored_data.update(user_input)

                # Route to WebIF step if it was activated (or kept active)
                if user_input.get(CONF.CB_WEBIF):
                    return await self.async_step_webif()

                # If CB_WEBIF is false, clear any stale webif settings from stored data
                for key in [
                    CONF.CB_WEBIF_MOCKUP_DATA,
                    CONF.USERNAME,
                    CONF.PASSWORD,
                    CONF.WEBIF_TOKEN,
                    CONF.CB_WEBIF_HK1,
                    CONF.CB_WEBIF_HK2,
                    CONF.CB_WEBIF_HK3,
                    CONF.CB_WEBIF_HK4,
                    CONF.CB_WEBIF_HK5,
                    CONF.CB_WEBIF_WP,
                    CONF.CB_WEBIF_2WEZ,
                    CONF.CB_WEBIF_SATISTICS,
                ]:
                    self._stored_data.pop(key, None)

                return self.async_update_and_abort(
                    entry=self._reconfigure_entry, data_updates=self._stored_data
                )
            except InvalidHost:
                errors["base"] = "invalid_host"
            except Exception:  # noqa: BLE001
                errors["base"] = "unknown"

        # We display the same schema as user step 1 for consistency
        schema_reconfigure = vol.Schema(
            schema={
                vol.Required(
                    schema=CONF.HOST,
                    default=self._stored_data.get(CONF.HOST),
                ): str,
                vol.Optional(
                    schema=CONF.PORT,
                    default=self._stored_data.get(CONF.PORT, "502"),
                ): cv.port,
                vol.Optional(
                    schema=CONF.PREFIX,
                    default=self._stored_data.get(CONF.PREFIX, CONST.DEF_PREFIX),
                ): str,
                vol.Optional(
                    schema=CONF.DEVICE_POSTFIX,
                    default=self._stored_data.get(CONF.DEVICE_POSTFIX, ""),
                ): str,
                vol.Optional(
                    schema=CONF.KENNFELD_FILE,
                    default=self._stored_data.get(CONF.KENNFELD_FILE),
                ): vol.In(container=await build_kennfeld_list(hass=self.hass)),
                vol.Optional(
                    schema=CONF.HK2,
                    default=self._stored_data.get(CONF.HK2, False),
                ): bool,
                vol.Optional(
                    schema=CONF.HK3,
                    default=self._stored_data.get(CONF.HK3, False),
                ): bool,
                vol.Optional(
                    schema=CONF.HK4,
                    default=self._stored_data.get(CONF.HK4, False),
                ): bool,
                vol.Optional(
                    schema=CONF.HK5,
                    default=self._stored_data.get(CONF.HK5, False),
                ): bool,
                vol.Optional(
                    schema=CONF.NAME_DEVICE_PREFIX,
                    default=self._stored_data.get(CONF.NAME_DEVICE_PREFIX, False),
                ): bool,
                vol.Optional(
                    schema=CONF.NAME_TOPIC_PREFIX,
                    default=self._stored_data.get(CONF.NAME_TOPIC_PREFIX, False),
                ): bool,
                vol.Optional(
                    schema=CONF.CB_WEBIF,
                    default=self._stored_data.get(CONF.CB_WEBIF, False),
                ): bool,
            }
        )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema_reconfigure,
            errors=errors,
            description_placeholders={
                CONF.HOST: "myhostname",
            },
        )


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""


class ConnectionFailed(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
