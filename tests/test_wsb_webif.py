"""Replay the WSB WEM Lokal reports without contacting a controller."""

import asyncio
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from custom_components import weishaupt_modbus as integration
from custom_components.weishaupt_modbus.config_flow import ConfigFlow
from custom_components.weishaupt_modbus.const import CONF
from custom_components.weishaupt_modbus.webif.coordinator import (
    WeishauptWebifCoordinator,
)
from custom_components.weishaupt_modbus.webif.description.all import get_webif_entities
from custom_components.weishaupt_modbus.webif.entity import WebifSensor
from custom_components.weishaupt_modbus.webif.wsb import (
    WSB_REQUEST_DELAY_SECONDS,
    WsbWebifCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import frame

_ROOT = "/settings_export.html"
_PUMP_MENU = f"{_ROOT}?stack=A0,11"
_PUMP = f"{_PUMP_MENU},01"
_INFO = f"{_ROOT}?stack=A0,22"
_HEATER = f"{_INFO},01"
_HEAT_PUMP = f"{_INFO},02"
_HEATING_CIRCUIT = f"{_INFO},03"
_WRONG_HEATING_CIRCUIT = f"{_ROOT}?stack=A0,33"


def _link(path: str, label: str) -> str:
    return f'<a href="{path}"><h5>{label}</h5></a>'


def _row(label: str, value: str) -> str:
    return f'<div class="nav-link browseobj"><h5>{label}</h5>{value}</div>'


@pytest.fixture
def reports() -> dict[str, str]:
    """Use fabricated menu stacks with the verified WSB report structure."""
    return {
        _ROOT: (
            "WWP-CPU COM V5.2 Rev. 14"
            + _link(_PUMP_MENU, "Wärmepumpe")
            + _link(_INFO, "Info")
        ),
        _PUMP_MENU: _link(_PUMP, "Pumpe"),
        _PUMP: (
            '<a href="pro.html">Regelungsart Heizen Konstantbetrieb</a>'
            '<a href="pro.html">Freigabe bei EVU-Sperre Aus</a>'
        ),
        _INFO: (
            _link(_HEATER, "2. WEZ")
            + _link(_HEAT_PUMP, "Wärmepumpe")
            + _link(_HEATING_CIRCUIT, "Heizkreis")
            + _link(_WRONG_HEATING_CIRCUIT, "Heizkreis")
            + _link(_PUMP_MENU, "Wärmepumpe")
        ),
        _HEATER: _row("Betriebsstunden E1", "25 h"),
        _HEAT_PUMP: (
            _row("Volumenstrom", "1,1 m³/h")
            + _row("Drehzahl Pumpe M1", "57 %")
            + _row("Schaltspiele Verdichter", "21")
            + _row("Schaltspiele Abtauen", "4")
            + _row("Ist Frequenz Verdichter", "Aus")
            + _row("Wärmetauscher AG Eintrit", "-2,1 °C")
            + _row("Version WWP-CPU", "V5.2 R14")
        ),
        _HEATING_CIRCUIT: _row("Vorlauftemperatur", "34,2 °C"),
    }


@pytest.fixture
def wsb_entry() -> ConfigEntry:
    """Enable the three supported category options for a test entry."""
    return MagicMock(
        spec=ConfigEntry,
        data={
            CONF.CB_WEBIF: True,
            CONF.CB_WEBIF_WSB: True,
            CONF.CB_WEBIF_WP: True,
            CONF.CB_WEBIF_HK1: True,
            CONF.CB_WEBIF_2WEZ: True,
            CONF.UID_MIGRATION: True,
            CONF.MAC: "example-device",
            CONF.HOST: "controller.invalid",
            CONF.PORT: 502,
            CONF.USERNAME: "",
            CONF.PASSWORD: "",
        },
    )


@pytest_asyncio.fixture
async def wsb_coordinator(tmp_path, reports, wsb_entry):
    """Build a real HA coordinator with a fake HTTP transport."""
    hass = HomeAssistant(str(tmp_path))
    frame.async_setup(hass)

    async def request(method, path):
        assert method == "GET"
        return SimpleNamespace(status_code=200, text=reports[path])

    api = MagicMock(_request=AsyncMock(side_effect=request))
    with patch.object(frame, "report_usage"):
        coordinator = WsbWebifCoordinator(hass, api, wsb_entry, asyncio.Lock())
    yield coordinator
    await coordinator.async_shutdown()


def _requested(coordinator):
    return [call.args[1] for call in coordinator.api._request.await_args_list]


def _entity(coordinator, entry, key):
    description = next(row for row in get_webif_entities(entry) if row.key == key)
    return WebifSensor(coordinator, description, entry)


def test_webif_profile_can_be_selected_and_defaults_to_off():
    """Keep existing configuration in standard mode until the user opts in."""
    schema = ConfigFlow()._build_webif_schema()
    assert schema({})[CONF.CB_WEBIF_WSB] is False
    assert schema({CONF.CB_WEBIF_WSB: True})[CONF.CB_WEBIF_WSB] is True


@pytest.mark.asyncio
async def test_uses_scoped_reports_then_reuses_the_validated_routes(
    wsb_coordinator, wsb_entry
):
    """Discover four correct reports with seven GETs, then reuse their URLs."""
    await wsb_coordinator.async_refresh()

    assert wsb_coordinator.update_interval == timedelta(minutes=5)
    assert _requested(wsb_coordinator) == [
        _ROOT,
        _PUMP_MENU,
        _PUMP,
        _INFO,
        _HEATER,
        _HEAT_PUMP,
        _HEATING_CIRCUIT,
    ]
    assert wsb_coordinator.data["heat_pump"] == {
        "pump_regulation_heating": "Konstantbetrieb",
        "pump_utility_lock_release": "Aus",
        "volume_flow": 1.1,
        "pump_m1_speed": 57,
        "compressor_switching_cycles": 21,
        "defrost_switching_cycles": 4,
        "compressor_frequency_actual": 0,
        "outdoor_heat_exchanger_inlet_temperature": -2.1,
        "control_board_version": "V5.2 R14",
    }
    assert _entity(wsb_coordinator, wsb_entry, "flow_temperature").native_value == 34.2
    assert (
        _entity(
            wsb_coordinator, wsb_entry, "electric_heater_1_operating_hours"
        ).native_value
        == 25
    )

    wsb_coordinator.api._request.reset_mock()
    await wsb_coordinator.async_refresh()
    assert _requested(wsb_coordinator) == [
        _ROOT,
        _PUMP,
        _HEATER,
        _HEAT_PUMP,
        _HEATING_CIRCUIT,
    ]


@pytest.mark.asyncio
async def test_does_not_follow_a_main_menu_link_as_an_info_report(
    wsb_coordinator, reports, wsb_entry
):
    """Use the valid pump settings even when the Info section is incomplete."""
    reports[_INFO] = reports[_INFO].replace(_link(_HEAT_PUMP, "Wärmepumpe"), "")
    await wsb_coordinator.async_refresh()

    assert _requested(wsb_coordinator).count(_PUMP_MENU) == 1
    assert _HEAT_PUMP not in _requested(wsb_coordinator)
    assert _entity(wsb_coordinator, wsb_entry, "pump_regulation_heating").available
    assert not _entity(wsb_coordinator, wsb_entry, "volume_flow").available


@pytest.mark.asyncio
async def test_retries_incomplete_pump_report_within_same_cycle(
    wsb_coordinator, reports, wsb_entry
):
    """Replay the verified case where a pump request first returns navigation."""
    await wsb_coordinator.async_refresh()

    calls = 0

    async def request(method, path):
        nonlocal calls
        assert method == "GET"
        if path == _PUMP:
            calls += 1
            if calls == 1:
                return SimpleNamespace(status_code=200, text=reports[_ROOT])
        return SimpleNamespace(status_code=200, text=reports[path])

    wsb_coordinator.api._request.reset_mock(side_effect=True)
    wsb_coordinator.api._request.side_effect = request
    await wsb_coordinator.async_refresh()

    assert _requested(wsb_coordinator) == [
        _ROOT,
        _PUMP,
        _HEATER,
        _HEAT_PUMP,
        _HEATING_CIRCUIT,
        _PUMP,
    ]
    assert (
        _entity(wsb_coordinator, wsb_entry, "pump_regulation_heating").native_value
        == "Konstantbetrieb"
    )


@pytest.mark.asyncio
async def test_missing_values_do_not_stay_available_or_exceed_budget(
    wsb_coordinator, reports, wsb_entry
):
    """Limit retries for partial pages and keep the other reports current."""
    await wsb_coordinator.async_refresh()
    volume = _entity(wsb_coordinator, wsb_entry, "volume_flow")
    heat_flow = _entity(wsb_coordinator, wsb_entry, "flow_temperature")
    assert volume.available and heat_flow.available

    wsb_coordinator.api._request.reset_mock()
    reports[_PUMP] = reports[_ROOT]
    reports[_HEATER] = reports[_ROOT]
    reports[_HEAT_PUMP] = reports[_ROOT]
    reports[_HEATING_CIRCUIT] = _row("Vorlauftemperatur", "35 °C")
    await wsb_coordinator.async_refresh()

    assert len(_requested(wsb_coordinator)) == 7
    assert not volume.available
    assert volume.native_value is None
    assert heat_flow.available and heat_flow.native_value == 35.0


@pytest.mark.asyncio
async def test_leaves_modbus_lock_available_between_export_requests(
    wsb_coordinator, reports
):
    """Let a waiting Modbus cycle run before the second WebIF request."""
    order = []
    root_started = asyncio.Event()
    modbus_waiting = asyncio.Event()

    async def request(method, path):
        assert method == "GET"
        assert wsb_coordinator._mcu_lock.locked()
        order.append(path)
        if path == _ROOT:
            root_started.set()
            await modbus_waiting.wait()
        return SimpleNamespace(status_code=200, text=reports[path])

    async def modbus():
        await root_started.wait()
        modbus_waiting.set()
        async with wsb_coordinator._mcu_lock:
            order.append("Modbus")

    wsb_coordinator.api._request.side_effect = request
    await asyncio.wait_for(
        asyncio.gather(wsb_coordinator.async_refresh(), modbus()), timeout=3
    )

    assert order[:3] == [_ROOT, "Modbus", _PUMP_MENU]


@pytest.mark.asyncio
async def test_report_timeout_preserves_the_other_wem_values(
    wsb_coordinator, reports, wsb_entry
):
    """Separate an unreachable report from the readings fetched that cycle."""
    await wsb_coordinator.async_refresh()

    async def request(method, path):
        assert method == "GET"
        if path == _PUMP:
            raise TimeoutError
        return SimpleNamespace(status_code=200, text=reports[path])

    wsb_coordinator.api._request.reset_mock()
    wsb_coordinator.api._request.side_effect = request
    await wsb_coordinator.async_refresh()

    assert wsb_coordinator.last_update_success
    assert _requested(wsb_coordinator).count(_PUMP) == 1
    assert _entity(wsb_coordinator, wsb_entry, "volume_flow").available
    assert not _entity(wsb_coordinator, wsb_entry, "pump_regulation_heating").available


@pytest.mark.asyncio
async def test_firmware_change_invalidates_learned_routes(wsb_coordinator, reports):
    """Rediscover URLs on an observed controller firmware change."""
    await wsb_coordinator.async_refresh()
    wsb_coordinator.api._request.reset_mock()
    reports[_ROOT] = reports[_ROOT].replace("Rev. 14", "Rev. 15")

    await wsb_coordinator.async_refresh()

    assert _requested(wsb_coordinator) == [
        _ROOT,
        _PUMP_MENU,
        _PUMP,
        _INFO,
        _HEATER,
        _HEAT_PUMP,
        _HEATING_CIRCUIT,
    ]


@pytest.mark.asyncio
async def test_upstream_ids_and_metadata_are_reused(wsb_coordinator, wsb_entry):
    """Keep shared WebIF entities identifiable when opting into the WSB reader."""
    keys = (
        "volume_flow",
        "pump_m1_speed",
        "compressor_switching_cycles",
        "defrost_switching_cycles",
        "outside_temperature_average",
        "electric_heater_1_operating_hours",
    )

    shared = {key: _entity(wsb_coordinator, wsb_entry, key) for key in keys}
    wsb_entry.data[CONF.CB_WEBIF_WSB] = False
    standard = WeishauptWebifCoordinator(
        wsb_coordinator.hass, wsb_coordinator.api, wsb_entry, asyncio.Lock()
    )
    for key, new in shared.items():
        original = _entity(standard, wsb_entry, key)
        assert new.unique_id == original.unique_id
        assert new.device_info["identifiers"] == original.device_info["identifiers"]
        assert new.state_class == original.state_class
        assert new.native_unit_of_measurement == original.native_unit_of_measurement

    standard.api.get_value.return_value = "1.2"
    assert _entity(standard, wsb_entry, "volume_flow").native_value == "1.2"


@pytest.mark.asyncio
async def test_disabled_categories_are_not_polled_or_registered(
    wsb_coordinator, wsb_entry
):
    """Keep WebIF category opt-ins and exclude unverified extra reports."""
    wsb_entry.data.update(
        {CONF.CB_WEBIF_WP: False, CONF.CB_WEBIF_HK1: False, CONF.CB_WEBIF_HK2: True}
    )
    await wsb_coordinator.async_refresh()

    assert _requested(wsb_coordinator) == [_ROOT, _INFO, _HEATER]
    assert {row.report_name for row in get_webif_entities(wsb_entry)} == {
        "electric_heater"
    }


@pytest.mark.asyncio
async def test_failed_first_wsb_poll_still_loads_modbus_platforms(
    wsb_coordinator, wsb_entry, reports
):
    """Set up Modbus even if WebIF returns the login page at startup."""
    reports[_ROOT] = '<html><title>Login</title><input name="pass"></html>'
    hass = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    modbus = MagicMock(async_config_entry_first_refresh=AsyncMock())
    powermap = MagicMock(initialize=AsyncMock())

    with (
        patch.object(
            integration, "WebifConnection", return_value=wsb_coordinator.api
        ) as api,
        patch.object(integration, "WsbWebifCoordinator", return_value=wsb_coordinator),
        patch.object(integration, "async_get_unit"),
        patch.object(integration, "Weishaupt"),
        patch.object(integration, "WeishauptCoordinator", return_value=modbus),
        patch.object(integration, "PowerMap", return_value=powermap),
    ):
        assert await integration.async_setup_entry(hass, wsb_entry)

    assert api.call_args.kwargs["request_delay"] == WSB_REQUEST_DELAY_SECONDS
    modbus.async_config_entry_first_refresh.assert_awaited_once()
    hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        wsb_entry, integration.PLATFORMS
    )
    assert not wsb_coordinator.last_update_success
    assert _requested(wsb_coordinator) == [_ROOT]


@pytest.mark.asyncio
async def test_mock_mode_preserves_upstream_setup_and_avoids_live_wsb(
    wsb_coordinator, wsb_entry
):
    """An entry with mock data selected follows the generic coordinator path."""
    wsb_entry.data[CONF.CB_WEBIF_MOCKUP_DATA] = True
    hass = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    coordinator = MagicMock(async_config_entry_first_refresh=AsyncMock())
    powermap = MagicMock(initialize=AsyncMock())
    with (
        patch.object(
            integration, "WebifConnection", return_value=wsb_coordinator.api
        ) as api,
        patch.object(
            integration, "WeishauptWebifCoordinator", return_value=coordinator
        ),
        patch.object(integration, "WsbWebifCoordinator") as wsb,
        patch.object(integration, "async_get_unit"),
        patch.object(integration, "Weishaupt"),
        patch.object(integration, "WeishauptCoordinator", return_value=coordinator),
        patch.object(integration, "PowerMap", return_value=powermap),
    ):
        assert await integration.async_setup_entry(hass, wsb_entry)

    wsb.assert_not_called()
    assert "request_delay" not in api.call_args.kwargs
    assert not _requested(wsb_coordinator)
    assert "pump_regulation_heating" not in {
        row.key for row in get_webif_entities(wsb_entry)
    }
