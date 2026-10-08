"""Config flow."""

from typing import Any, override

from aiofiles.os import scandir
from modbus_connection import ModbusConnectionError
import probatio
from probatio.validators import MacAddress

from homeassistant import config_entries, exceptions
from homeassistant.components.modbus.connection import ModbusConnection, ModbusTcpParams
from homeassistant.core import _LOGGER, HomeAssistant
from homeassistant.helpers.device_registry import format_mac
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .const import CONF, CONST
from .kennfeld.kennfeld import get_filepath


async def build_kennfeld_list(hass: HomeAssistant) -> list[str]:
    """Browse integration directory for heat pump operation map ("kennfeld") files."""
    kennfelder: list[str] = []

    try:
        dir_iterator = await scandir(get_filepath(hass))
        kennfelder.extend(
            item.name for item in dir_iterator if "kennfeld.json" in item.name
        )
    except OSError:
        pass

    if not kennfelder:
        kennfelder.append("weishaupt_wbb_kennfeld.json")

    return kennfelder


def validate_input(
    data: dict[str, Any],
    *,
    validate_mac: bool = True,
) -> dict[str, Any]:
    """Validate and normalize configuration input."""
    host = str(data.get(CONF.HOST, "")).strip()

    if not host:
        raise InvalidHost

    validated_data = {
        CONF.HOST: host,
    }

    if validate_mac:
        mac = str(data.get(CONF.MAC, "")).strip()
        MacAddress()(mac)
        validated_data[CONF.MAC] = format_mac(mac)

    return validated_data


class ConfigFlow(
    config_entries.ConfigFlow,
    domain=CONST.DOMAIN,
):  # pylint: disable=abstract-method
    """Class config flow."""

    VERSION = 9
    MINOR_VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    def __init__(self) -> None:
        """Initialize the flow."""
        self._stored_data: dict[str, Any] = {}
        self._reconfigure_entry: config_entries.ConfigEntry | None = None

    async def _build_core_schema(
        self,
        *,
        include_mac: bool = True,
    ) -> probatio.Schema:
        """Build the core configuration schema."""
        return probatio.Schema(
            schema={
                probatio.Required(
                    schema=CONF.HOST,
                    default=self._stored_data.get(CONF.HOST, ""),
                ): TextSelector(),
                **(
                    {
                        probatio.Required(
                            schema=CONF.MAC,
                            default=self._stored_data.get(CONF.MAC, ""),
                        ): MacAddress()
                    }
                    if include_mac
                    else {}
                ),
                probatio.Optional(
                    schema=CONF.PORT,
                    default=self._stored_data.get(CONF.PORT, 502),
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=1,
                        max=65535,
                        mode=NumberSelectorMode.BOX,
                    )
                ),
                probatio.Optional(
                    schema=CONF.KENNFELD_FILE,
                    default=self._stored_data.get(
                        CONF.KENNFELD_FILE,
                        "weishaupt_wbb_kennfeld.json",
                    ),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=await build_kennfeld_list(self.hass),
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                probatio.Optional(
                    schema=CONF.HK2,
                    default=self._stored_data.get(CONF.HK2, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.HK3,
                    default=self._stored_data.get(CONF.HK3, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.HK4,
                    default=self._stored_data.get(CONF.HK4, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.HK5,
                    default=self._stored_data.get(CONF.HK5, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.CB_WEBIF,
                    default=self._stored_data.get(CONF.CB_WEBIF, False),
                ): BooleanSelector(),
            }
        )

    def _build_webif_schema(self) -> probatio.Schema:
        """Build the WebIF configuration schema."""
        return probatio.Schema(
            schema={
                probatio.Optional(
                    schema=CONF.CB_WEBIF_MOCKUP_DATA,
                    default=self._stored_data.get(CONF.CB_WEBIF_MOCKUP_DATA, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.USERNAME,
                    default=self._stored_data.get(CONF.USERNAME, ""),
                ): TextSelector(),
                probatio.Optional(
                    schema=CONF.PASSWORD,
                    default=self._stored_data.get(CONF.PASSWORD, ""),
                ): TextSelector(),
                probatio.Optional(
                    schema=CONF.WEBIF_TOKEN,
                    default=self._stored_data.get(CONF.WEBIF_TOKEN, ""),
                ): TextSelector(),
                probatio.Optional(
                    schema=CONF.CB_WEBIF_HK1,
                    default=self._stored_data.get(CONF.CB_WEBIF_HK1, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.CB_WEBIF_HK2,
                    default=self._stored_data.get(CONF.CB_WEBIF_HK2, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.CB_WEBIF_HK3,
                    default=self._stored_data.get(CONF.CB_WEBIF_HK3, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.CB_WEBIF_HK4,
                    default=self._stored_data.get(CONF.CB_WEBIF_HK4, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.CB_WEBIF_HK5,
                    default=self._stored_data.get(CONF.CB_WEBIF_HK5, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.CB_WEBIF_WP,
                    default=self._stored_data.get(CONF.CB_WEBIF_WP, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.CB_WEBIF_2WEZ,
                    default=self._stored_data.get(CONF.CB_WEBIF_2WEZ, False),
                ): BooleanSelector(),
                probatio.Optional(
                    schema=CONF.CB_WEBIF_SATISTICS,
                    default=self._stored_data.get(CONF.CB_WEBIF_SATISTICS, False),
                ): BooleanSelector(),
            }
        )

    @override
    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Step 1: Core configuration setup."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                validated_data = validate_input(user_input)

                self._stored_data.update(user_input)
                self._stored_data.update(validated_data)

            except InvalidHost:
                errors["base"] = "invalid_host"
            except probatio.MacAddressInvalid:
                errors[CONF.MAC] = "invalid_mac"
            else:
                await self.async_set_unique_id(validated_data[CONF.MAC])
                self._abort_if_unique_id_configured()

                try:
                    await test_modbus(
                        validated_data[CONF.HOST],
                        validated_data.get(CONF.PORT, 502),
                    )

                    if user_input.get(CONF.CB_WEBIF):
                        return await self.async_step_webif()

                    return self.async_create_entry(
                        title=self._stored_data[CONF.HOST],
                        data=self._stored_data,
                    )

                except ConnectionFailed:
                    errors["base"] = "cannot_connect"
                except Exception:  # noqa: BLE001
                    _LOGGER.exception("Unexpected error during configuration")
                    errors["base"] = "unknown"
        schema_page1 = await self._build_core_schema()

        return self.async_show_form(
            step_id="user",
            data_schema=schema_page1,
            errors=errors,
        )

    async def async_step_webif(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Step 2: Experimental Web Interface setup."""
        if user_input is not None:
            self._stored_data.update(user_input)

            # If we are in a reconfigure flow, finalize the updates
            if self._reconfigure_entry:
                return self.async_update_and_abort(
                    entry=self._reconfigure_entry,
                    data_updates=self._stored_data,
                )

            # Standard creation path
            return self.async_create_entry(
                title=self._stored_data[CONF.HOST],
                data=self._stored_data,
            )

        schema_page2 = self._build_webif_schema()

        return self.async_show_form(
            step_id="webif",
            data_schema=schema_page2,
            errors={},
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Trigger a reconfiguration flow."""
        errors: dict[str, str] = {}
        self._reconfigure_entry = self._get_reconfigure_entry()

        # Pre-seed internal state dictionary with the current saved entry data.
        if not self._stored_data:
            self._stored_data.update(self._reconfigure_entry.data)

        if user_input is not None:
            try:
                validated_data = validate_input(
                    user_input,
                    validate_mac=False,
                )

                # Build the prospective configuration without modifying the
                # current stored data until the connection test succeeds.
                test_data = {
                    **self._stored_data,
                    **user_input,
                    **validated_data,
                }

                await test_modbus(
                    test_data[CONF.HOST],
                    test_data.get(CONF.PORT, 502),
                )

                self._stored_data.update(test_data)

                # Route to WebIF step if it was activated (or kept active).
                if self._stored_data.get(CONF.CB_WEBIF):
                    return await self.async_step_webif()

                # If CB_WEBIF is false, clear any stale WebIF settings
                # from stored data.
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
                    entry=self._reconfigure_entry,
                    data_updates=self._stored_data,
                )

            except InvalidHost:
                errors["base"] = "invalid_host"
            except ConnectionFailed:
                errors["base"] = "cannot_connect"
            except probatio.MacAddressInvalid:
                errors[CONF.MAC] = "invalid_mac"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error during reconfiguration")
                errors["base"] = "unknown"

        schema_reconfigure = await self._build_core_schema(include_mac=False)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema_reconfigure,
            errors=errors,
            description_placeholders={
                CONF.HOST: "myhostname",
            },
        )


async def test_modbus(host: str, port: int) -> bool:
    """Test the connection to the Weishaupt heat pump."""
    params = ModbusTcpParams(
        host=host,
        port=port,
    )

    connection = ModbusConnection(params)

    try:
        await connection.connect()
    except (OSError, TimeoutError, ModbusConnectionError) as err:
        raise ConnectionFailed from err
    finally:
        await connection.close()

    return True


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""


class ConnectionFailed(exceptions.HomeAssistantError):
    """Error to indicate there is a connection failure."""
