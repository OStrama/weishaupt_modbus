from unittest.mock import AsyncMock, patch

from custom_components.weishaupt_modbus.config_flow import (
    ConfigFlow,
    ConnectionFailed,
    build_kennfeld_list,
    test_modbus,
)
from custom_components.weishaupt_modbus.const import CONF, CONST
import probatio
import pytest

from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData


async def test_form_invalid_mac(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test invalid MAC address."""
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={"source": SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with pytest.raises(InvalidData):
        await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "not-a-mac",
                CONF.PORT: 502,
            },
        )


async def test_form_invalid_host(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test invalid host."""
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={"source": SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF.HOST: "",
            CONF.MAC: "AA:BB:CC:DD:EE:FF",
            CONF.PORT: 502,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {
        "base": "invalid_host",
    }


async def test_form_cannot_connect(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test connection failure."""
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={"source": SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with patch(
        "custom_components.weishaupt_modbus.config_flow.test_modbus",
        new=AsyncMock(side_effect=ConnectionFailed),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {
        "base": "cannot_connect",
    }


async def test_form_success(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test successful configuration."""
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={"source": SOURCE_USER},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    with (
        patch(
            "custom_components.weishaupt_modbus.config_flow.test_modbus",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.async_setup_entry",
            new=AsyncMock(return_value=True),
        ),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF.HOST] == "10.10.1.225"
    assert result["data"][CONF.MAC] == "aa:bb:cc:dd:ee:ff"
    assert result["data"][CONF.PORT] == 502


async def test_form_duplicate_mac(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test that a duplicate MAC address is rejected."""
    with (
        patch(
            "custom_components.weishaupt_modbus.config_flow.test_modbus",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.async_setup_entry",
            new=AsyncMock(return_value=True),
        ),
    ):
        # Create the first entry.
        result = await hass.config_entries.flow.async_init(
            CONST.DOMAIN,
            context={"source": SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY

    # Start a second configuration flow with the same MAC.
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={"source": SOURCE_USER},
    )

    with patch(
        "custom_components.weishaupt_modbus.config_flow.test_modbus",
        new=AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.226",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test reconfiguring an existing entry."""
    with (
        patch(
            "custom_components.weishaupt_modbus.config_flow.test_modbus",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.async_setup_entry",
            new=AsyncMock(return_value=True),
        ),
    ):
        # Create the initial entry.
        result = await hass.config_entries.flow.async_init(
            CONST.DOMAIN,
            context={"source": SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY

    entry = hass.config_entries.async_entries(CONST.DOMAIN)[0]

    # Start reconfigure flow.
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={
            "source": "reconfigure",
            "entry_id": entry.entry_id,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    with patch(
        "custom_components.weishaupt_modbus.config_flow.test_modbus",
        new=AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.226",
                CONF.PORT: 503,
            },
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"

    assert entry.data[CONF.HOST] == "10.10.1.226"
    assert entry.data[CONF.PORT] == 503
    assert entry.data[CONF.MAC] == "aa:bb:cc:dd:ee:ff"


async def test_reconfigure_cannot_connect(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test reconfigure when the connection fails."""
    with (
        patch(
            "custom_components.weishaupt_modbus.config_flow.test_modbus",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.async_setup_entry",
            new=AsyncMock(return_value=True),
        ),
    ):
        # Create the initial entry.
        result = await hass.config_entries.flow.async_init(
            CONST.DOMAIN,
            context={"source": SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY

    entry = hass.config_entries.async_entries(CONST.DOMAIN)[0]

    with patch(
        "custom_components.weishaupt_modbus.config_flow.test_modbus",
        new=AsyncMock(side_effect=ConnectionFailed),
    ):
        result = await hass.config_entries.flow.async_init(
            CONST.DOMAIN,
            context={
                "source": "reconfigure",
                "entry_id": entry.entry_id,
            },
        )

        assert result["type"] is FlowResultType.FORM

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.226",
                CONF.PORT: 503,
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"
    assert result["errors"] == {
        "base": "cannot_connect",
    }

    # The existing entry must remain unchanged.
    assert entry.data[CONF.HOST] == "10.10.1.225"
    assert entry.data[CONF.PORT] == 502
    assert entry.data[CONF.MAC] == "aa:bb:cc:dd:ee:ff"


async def test_reconfigure_mac_immutable(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test that the MAC address cannot be changed during reconfigure."""
    with (
        patch(
            "custom_components.weishaupt_modbus.config_flow.test_modbus",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.async_setup_entry",
            new=AsyncMock(return_value=True),
        ),
    ):
        # Create the initial entry.
        result = await hass.config_entries.flow.async_init(
            CONST.DOMAIN,
            context={"source": SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY

    entry = hass.config_entries.async_entries(CONST.DOMAIN)[0]

    # Start reconfigure flow.
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={
            "source": "reconfigure",
            "entry_id": entry.entry_id,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    # MAC is not part of the reconfigure schema.
    with pytest.raises(InvalidData):
        await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.226",
                CONF.PORT: 503,
                CONF.MAC: "11:22:33:44:55:66",
            },
        )


async def test_form_webif(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test configuration with WebIF enabled."""
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={"source": SOURCE_USER},
    )

    with patch(
        "custom_components.weishaupt_modbus.config_flow.test_modbus",
        new=AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
                CONF.CB_WEBIF: True,
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "webif"

    with patch(
        "custom_components.weishaupt_modbus.async_setup_entry",
        new=AsyncMock(return_value=True),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.USERNAME: "admin",
                CONF.PASSWORD: "password",
            },
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF.HOST] == "10.10.1.225"
    assert result["data"][CONF.MAC] == "aa:bb:cc:dd:ee:ff"
    assert result["data"][CONF.CB_WEBIF] is True
    assert result["data"][CONF.USERNAME] == "admin"
    assert result["data"][CONF.PASSWORD] == "password"


async def test_reconfigure_webif(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test reconfiguring with WebIF enabled."""
    with (
        patch(
            "custom_components.weishaupt_modbus.config_flow.test_modbus",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.async_setup_entry",
            new=AsyncMock(return_value=True),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            CONST.DOMAIN,
            context={"source": SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    entry = hass.config_entries.async_entries(CONST.DOMAIN)[0]

    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={
            "source": "reconfigure",
            "entry_id": entry.entry_id,
        },
    )

    with patch(
        "custom_components.weishaupt_modbus.config_flow.test_modbus",
        new=AsyncMock(),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.226",
                CONF.PORT: 503,
                CONF.CB_WEBIF: True,
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "webif"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF.USERNAME: "admin",
            CONF.PASSWORD: "password",
        },
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"

    assert entry.data[CONF.HOST] == "10.10.1.226"
    assert entry.data[CONF.PORT] == 503
    assert entry.data[CONF.CB_WEBIF] is True
    assert entry.data[CONF.USERNAME] == "admin"
    assert entry.data[CONF.PASSWORD] == "password"


async def test_build_kennfeld_list_scandir_error(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test fallback when the integration directory cannot be read."""
    with patch(
        "custom_components.weishaupt_modbus.config_flow.scandir",
        side_effect=OSError,
    ):
        result = await build_kennfeld_list(hass)

    assert result == ["weishaupt_wbb_kennfeld.json"]


async def test_build_kennfeld_list_empty(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test fallback when no kennfeld files are found."""
    with patch(
        "custom_components.weishaupt_modbus.config_flow.scandir",
        new=AsyncMock(return_value=[]),
    ):
        result = await build_kennfeld_list(hass)

    assert result == ["weishaupt_wbb_kennfeld.json"]


async def test_reconfigure_invalid_host(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test invalid host during reconfiguration."""
    # Create an existing entry first.
    with (
        patch(
            "custom_components.weishaupt_modbus.config_flow.test_modbus",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.async_setup_entry",
            new=AsyncMock(return_value=True),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            CONST.DOMAIN,
            context={"source": SOURCE_USER},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    entry = hass.config_entries.async_entries(CONST.DOMAIN)[0]

    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={
            "source": "reconfigure",
            "entry_id": entry.entry_id,
        },
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF.HOST: "",
            CONF.PORT: 502,
        },
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_host"}


async def test_test_modbus_success() -> None:
    """Test successful Modbus connection."""
    connection = AsyncMock()

    with patch(
        "custom_components.weishaupt_modbus.config_flow.ModbusConnection",
        return_value=connection,
    ):
        assert await test_modbus("10.10.1.225", 502) is True

    connection.connect.assert_awaited_once()
    connection.close.assert_awaited_once()


async def test_test_modbus_connection_failed() -> None:
    """Test Modbus connection errors are converted to ConnectionFailed."""
    connection = AsyncMock()
    connection.connect.side_effect = OSError("connection refused")

    with patch(
        "custom_components.weishaupt_modbus.config_flow.ModbusConnection",
        return_value=connection,
    ):
        with pytest.raises(ConnectionFailed):
            await test_modbus("10.10.1.225", 502)

    connection.close.assert_awaited_once()


async def test_form_invalid_mac_validation(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test invalid MAC handling in the config flow."""
    flow = ConfigFlow()
    flow.hass = hass

    with patch(
        "custom_components.weishaupt_modbus.config_flow.validate_input",
        side_effect=probatio.MacAddressInvalid,
    ):
        result = await flow.async_step_user(
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "invalid",
            }
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF.MAC: "invalid_mac"}


async def test_form_unexpected_error(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test unexpected errors during configuration."""
    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={"source": SOURCE_USER},
    )

    with patch(
        "custom_components.weishaupt_modbus.config_flow.test_modbus",
        new=AsyncMock(side_effect=RuntimeError("boom")),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


async def test_reconfigure_unexpected_error(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test unexpected errors during reconfiguration."""
    with (
        patch(
            "custom_components.weishaupt_modbus.config_flow.test_modbus",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.async_setup_entry",
            new=AsyncMock(return_value=True),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            CONST.DOMAIN,
            context={"source": SOURCE_USER},
        )
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    entry = hass.config_entries.async_entries(CONST.DOMAIN)[0]

    result = await hass.config_entries.flow.async_init(
        CONST.DOMAIN,
        context={
            "source": "reconfigure",
            "entry_id": entry.entry_id,
        },
    )

    with patch(
        "custom_components.weishaupt_modbus.config_flow.test_modbus",
        new=AsyncMock(side_effect=RuntimeError("boom")),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.226",
                CONF.PORT: 502,
            },
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


async def test_reconfigure_invalid_mac_validation(
    hass: HomeAssistant,
    enable_custom_integrations: None,
) -> None:
    """Test invalid MAC handling during reconfiguration."""
    with (
        patch(
            "custom_components.weishaupt_modbus.config_flow.test_modbus",
            new=AsyncMock(),
        ),
        patch(
            "custom_components.weishaupt_modbus.async_setup_entry",
            new=AsyncMock(return_value=True),
        ),
    ):
        result = await hass.config_entries.flow.async_init(
            CONST.DOMAIN,
            context={"source": SOURCE_USER},
        )

        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF.HOST: "10.10.1.225",
                CONF.MAC: "AA:BB:CC:DD:EE:FF",
                CONF.PORT: 502,
            },
        )

    entry = hass.config_entries.async_entries(CONST.DOMAIN)[0]

    flow = ConfigFlow()
    flow.hass = hass
    flow.context = {
        "source": SOURCE_RECONFIGURE,
        "entry_id": entry.entry_id,
    }

    with patch(
        "custom_components.weishaupt_modbus.config_flow.validate_input",
        side_effect=probatio.MacAddressInvalid,
    ):
        result = await flow.async_step_reconfigure(
            {
                CONF.HOST: "10.10.1.226",
                CONF.PORT: 502,
            }
        )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF.MAC: "invalid_mac"}
