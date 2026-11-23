"""Read reports from the WSB variant of WEM Lokal."""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import timedelta
import logging
import math
import re
from typing import Any, override

from bs4 import BeautifulSoup
from weishaupt_webif_api import WebifConnection, WeishauptWebifError

from custom_components.weishaupt_modbus.const import CONF
from homeassistant import config_entries
from homeassistant.const import (
    PERCENTAGE,
    UnitOfFrequency,
    UnitOfTemperature,
    UnitOfTime,
    UnitOfVolumeFlowRate,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from .coordinator import WeishauptWebifCoordinator
from .description.description import WebifSensorDescription

type Value = int | float | str
type ReportParser = Callable[[BeautifulSoup], dict[str, Value]]


def use_wsb_webif(entry: config_entries.ConfigEntry) -> bool:
    """Select WSB for live WebIF; respect the existing mock mode."""
    return bool(
        entry.data.get(CONF.CB_WEBIF)
        and entry.data.get(CONF.CB_WEBIF_WSB)
        and not entry.data.get(CONF.CB_WEBIF_MOCKUP_DATA)
    )


_LOGGER = logging.getLogger(__name__)
_ROOT = "/settings_export.html"
WSB_REQUEST_DELAY_SECONDS = 1.0
_REQUEST_TIMEOUT = 10
_MAX_EXPORT_REQUESTS = 7
_EXPORT_LINK = re.compile(r"/settings_export\.html\?stack=[0-9a-fA-F,]+")
_CONTROLLER_FIRMWARE = re.compile(r"\bWWP-CPU COM V(\d+\.\d+) Rev\.\s*(\d+)\b")
_FLOW_VALUE = re.compile(r"(\d+(?:[.,]\d+)?)\s*m\s*[3³]\s*/\s*h")
_TEMPERATURE_VALUE = re.compile(r"([+−-]?\d+(?:[.,]\d+)?)\s*°\s*C")
_FREQUENCY_VALUE = re.compile(r"(\d+(?:[.,]\d+)?)\s*Hz")
_UNSIGNED_VALUE = re.compile(r"[0-9]{1,12}")
_WEM_ERRORS = (OSError, ValueError, WeishauptWebifError)


@dataclass(frozen=True)
class WsbField:
    """One WSB report field with its upstream key and value format."""

    report: str
    key: str
    label: str
    unit: str | None = None
    choices: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    text_pattern: str | None = None


def _temperature(report: str, key: str, label: str, *aliases: str) -> WsbField:
    return WsbField(
        report,
        key,
        label,
        UnitOfTemperature.CELSIUS,
        aliases=aliases,
    )


_PUMP_REGULATION = ("Konstantbetrieb", "Volumenstrom")
_PUMP_SETTINGS = (
    WsbField(
        "heat_pump",
        "pump_regulation_heating",
        "Regelungsart Heizen",
        choices=_PUMP_REGULATION,
    ),
    WsbField(
        "heat_pump",
        "pump_regulation_hot_water",
        "Regelungsart WW",
        choices=_PUMP_REGULATION,
    ),
    WsbField(
        "heat_pump",
        "pump_regulation_cooling",
        "Regelungsart Kühlen",
        choices=_PUMP_REGULATION,
    ),
    WsbField(
        "heat_pump",
        "pump_function",
        "Funktion",
        choices=("Zubringerpumpe", "HK-Pumpe"),
    ),
    WsbField(
        "heat_pump",
        "pump_utility_lock_release",
        "Freigabe bei EVU-Sperre",
        choices=("Aus", "Ein"),
    ),
)
_HEATER_COUNTERS = (
    WsbField(
        "electric_heater",
        "electric_heater_1_operating_hours",
        "Betriebsstunden E1",
        UnitOfTime.HOURS,
    ),
    WsbField(
        "electric_heater",
        "electric_heater_2_operating_hours",
        "Betriebsstunden E2",
        UnitOfTime.HOURS,
    ),
)
_HEAT_PUMP_INFO = (
    WsbField(
        "heat_pump",
        "volume_flow",
        "Volumenstrom",
        UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR,
    ),
    WsbField("heat_pump", "pump_m1_speed", "Drehzahl Pumpe M1", PERCENTAGE),
    WsbField(
        "heat_pump",
        "compressor_switching_cycles",
        "Schaltspiele Verdichter",
    ),
    WsbField(
        "heat_pump",
        "defrost_switching_cycles",
        "Schaltspiele Abtauen",
    ),
    WsbField(
        "heat_pump",
        "diverter_valve_position",
        "Stellung Umschaltventil",
        choices=("Heizkreis", "Warmwasser"),
    ),
    WsbField(
        "heat_pump",
        "compressor_frequency_target",
        "Soll Frequenz Verdichter",
        UnitOfFrequency.HERTZ,
    ),
    WsbField(
        "heat_pump",
        "compressor_frequency_actual",
        "Ist Frequenz Verdichter",
        UnitOfFrequency.HERTZ,
    ),
    WsbField(
        "heat_pump",
        "compressor_operating_hours",
        "Betriebsstd. Verdichter",
        UnitOfTime.HOURS,
    ),
    _temperature("heat_pump", "target_temperature", "Solltemperatur"),
    _temperature(
        "heat_pump",
        "outdoor_heat_exchanger_inlet_temperature",
        "Wärmetauscher AG Eintritt",
        "Wärmetauscher AG Eintrit",
    ),
    _temperature(
        "heat_pump",
        "outdoor_heat_exchanger_middle_temperature",
        "Wärmetauscher AG Mitte",
    ),
    _temperature(
        "heat_pump", "discharge_gas_temperature", "Druckgas", "Druckgastemperatur"
    ),
    _temperature(
        "heat_pump", "indoor_heat_exchanger_temperature", "Wärmetauscher Innen"
    ),
    _temperature("heat_pump", "indoor_refrigerant_temperature", "Kältemittel Innen"),
    WsbField(
        "heat_pump",
        "wwp_sg_version",
        "Version WWP-SG",
        text_pattern=r"V\d+(?:\.\d+)+(?:\s+(?:R|Rev\.\s*)\d+)?",
    ),
    WsbField(
        "heat_pump",
        "control_board_version",
        "Version WWP-CPU",
        text_pattern=r"V\d+(?:\.\d+)+(?:\s+(?:R|Rev\.\s*)\d+)?",
    ),
    WsbField(
        "heat_pump",
        "outdoor_unit_variant",
        "Außengerät Variante",
        aliases=("Aussengerät Variante",),
        text_pattern=r"WSB \d{1,2}(?:[- ][A-Za-z0-9]+)*",
    ),
)
_HEATING_CIRCUIT_INFO = (
    _temperature("heating_circuit", "outside_temperature_average", "AT Mittelwert"),
    _temperature("heating_circuit", "outside_temperature_long_term", "AT Langzeitwert"),
    _temperature("heating_circuit", "flow_temperature", "Vorlauftemperatur"),
)
WSB_FIELDS = _PUMP_SETTINGS + _HEATER_COUNTERS + _HEAT_PUMP_INFO + _HEATING_CIRCUIT_INFO


def _menu(page: BeautifulSoup, label: str, *, parent: str | None = None) -> str:
    links = [
        str(link["href"])
        for link in page.find_all("a", href=_EXPORT_LINK)
        if _EXPORT_LINK.fullmatch(str(link["href"]))
        and " ".join(link.stripped_strings) == label
        and (parent is None or str(link["href"]).startswith(parent + ","))
    ]
    if not links:
        raise ValueError(f"Missing WEM menu {label}")
    # The navigation repeats top-level labels on child pages. Scope a child
    # lookup to its own stack before preferring the last matching link.
    return links[-1]


def _pump_values(page: BeautifulSoup) -> dict[str, Value]:
    labels = [" ".join(anchor.stripped_strings) for anchor in page.find_all("a")]
    values: dict[str, Value] = {}
    for field in _PUMP_SETTINGS:
        prefix = field.label + " "
        matches = [
            label.removeprefix(prefix) for label in labels if label.startswith(prefix)
        ]
        if len(matches) == 1 and matches[0] in field.choices:
            values[field.key] = matches[0]
    return values


def _info_values(page: BeautifulSoup, fields: tuple[WsbField, ...]) -> dict[str, Value]:
    rows: dict[str, list[str]] = {}
    for row in page.select("div.nav-link.browseobj"):
        if heading := row.find("h5"):
            label = heading.get_text(" ", strip=True)
            raw = row.get_text(" ", strip=True).removeprefix(label).strip()
            rows.setdefault(label, []).append(raw)

    values: dict[str, Value] = {}
    for field in fields:
        matches = [
            value
            for label in (field.label, *field.aliases)
            for value in rows.get(label, ())
        ]
        if (
            len(matches) == 1
            and (value := _parse_info_value(field, matches[0])) is not None
        ):
            values[field.key] = value
    return values


def _parse_info_value(field: WsbField, raw: str) -> Value | None:
    if field.choices:
        return raw if raw in field.choices else None
    if field.text_pattern is not None:
        return raw if re.fullmatch(field.text_pattern, raw) else None
    if field.unit == PERCENTAGE:
        if (match := re.fullmatch(r"(\d{1,3})\s*%", raw)) and int(match[1]) <= 100:
            return int(match[1])
        return None
    if field.unit == UnitOfTime.HOURS:
        match = re.fullmatch(r"([0-9]{1,12})\s*h", raw)
        return int(match[1]) if match else None
    if field.unit is None:
        return int(raw) if _UNSIGNED_VALUE.fullmatch(raw) else None

    if field.unit == UnitOfFrequency.HERTZ and raw == "Aus":
        return 0
    pattern = {
        UnitOfTemperature.CELSIUS: _TEMPERATURE_VALUE,
        UnitOfFrequency.HERTZ: _FREQUENCY_VALUE,
        UnitOfVolumeFlowRate.CUBIC_METERS_PER_HOUR: _FLOW_VALUE,
    }[field.unit]
    if match := pattern.fullmatch(raw):
        value = float(match[1].replace(",", ".").replace("−", "-"))
        if math.isfinite(value) and (
            field.unit != UnitOfTemperature.CELSIUS or -50 <= value <= 200
        ):
            return value
    return None


def _hour_values(page: BeautifulSoup) -> dict[str, Value]:
    return _info_values(page, _HEATER_COUNTERS)


def _heat_pump_values(page: BeautifulSoup) -> dict[str, Value]:
    return _info_values(page, _HEAT_PUMP_INFO)


def _heating_circuit_values(page: BeautifulSoup) -> dict[str, Value]:
    return _info_values(page, _HEATING_CIRCUIT_INFO)


@dataclass(frozen=True)
class _Report:
    """A report category, menu label and value parser."""

    category: str
    label: str
    parse: ReportParser


_REPORTS = (
    ("Wärmepumpe", (_Report("heat_pump", "Pumpe", _pump_values),)),
    (
        "Info",
        (
            _Report("electric_heater", "2. WEZ", _hour_values),
            _Report("heat_pump", "Wärmepumpe", _heat_pump_values),
            _Report("heating_circuit", "Heizkreis", _heating_circuit_values),
        ),
    ),
)


@dataclass(frozen=True)
class _Route:
    """An export URL that returned recognised fields in an earlier poll."""

    path: str
    fields: frozenset[str]


class WsbWebifCoordinator(WeishauptWebifCoordinator):
    """Poll confirmed WSB reports within a fixed request budget."""

    def __init__(
        self,
        hass: HomeAssistant,
        api: WebifConnection,
        entry: config_entries.ConfigEntry,
        mcu_lock: asyncio.Lock,
    ) -> None:
        """Initialize the WSB coordinator."""
        super().__init__(hass, api, entry, mcu_lock)
        self.update_interval = timedelta(minutes=5)
        self._routes: dict[_Report, _Route] = {}
        self._firmware: str | None = None

    @override
    def value_for(self, description: WebifSensorDescription) -> Value | None:
        """Return a value from this cycle, through the existing entity identity."""
        return (self.data or {}).get(description.report_name, {}).get(description.key)

    @override
    def field_available(self, description: WebifSensorDescription) -> bool:
        """Mark missing fields unavailable rather than reuse earlier results."""
        return self.value_for(description) is not None

    async def _get_page(self, path: str) -> BeautifulSoup:
        # Let Modbus take the lock between pages. The pinned transport handles
        # pacing, authentication and retrying an expired session.
        async with self._mcu_lock, asyncio.timeout(_REQUEST_TIMEOUT):
            response = await self.api._request("GET", path)  # noqa: SLF001
        if response.status_code != 200:
            raise ValueError("WEM export unavailable")
        page = BeautifulSoup(response.text, "html.parser")
        if page.select_one('input[name="pass"]') or (
            page.title and page.title.get_text(strip=True).casefold() == "login"
        ):
            raise ValueError("WEM export returned a login page")
        return page

    @override
    async def _async_update_data(self) -> dict[str, Any]:
        """Discover, read and retry selected reports, within seven export calls."""
        categories = self._get_categories()
        if not any(
            report.category in categories
            for _, reports in _REPORTS
            for report in reports
        ):
            return {}

        requests = 0

        async def get_page(path: str) -> BeautifulSoup:
            nonlocal requests
            if requests >= _MAX_EXPORT_REQUESTS:
                raise ValueError("WEM export request budget exhausted")
            requests += 1
            return await self._get_page(path)

        try:
            root = await get_page(_ROOT)
        except _WEM_ERRORS as err:
            raise UpdateFailed(
                f"WSB WEM export unavailable ({type(err).__name__})"
            ) from None
        if match := _CONTROLLER_FIRMWARE.search(root.get_text(" ", strip=True)):
            firmware = match[0]
            if self._firmware is not None and firmware != self._firmware:
                self._routes.clear()
            self._firmware = firmware

        values: dict[str, dict[str, Value]] = {}
        retry: list[tuple[_Report, _Route]] = []
        for parent_label, reports in _REPORTS:
            selected = [report for report in reports if report.category in categories]
            section = None
            if any(report not in self._routes for report in selected):
                try:
                    parent = _menu(root, parent_label)
                    section = await get_page(parent), parent
                except _WEM_ERRORS as err:
                    _LOGGER.debug(
                        "WSB WEM menu %s unavailable (%s)",
                        parent_label,
                        type(err).__name__,
                    )

            for report in selected:
                cached = self._routes.get(report)
                try:
                    if cached is not None:
                        path = cached.path
                    elif section is not None:
                        page, parent = section
                        path = _menu(page, report.label, parent=parent)
                    else:
                        continue
                    current = report.parse(await get_page(path))
                except _WEM_ERRORS as err:
                    if isinstance(err, ValueError):
                        self._routes.pop(report, None)
                    _LOGGER.debug(
                        "WSB WEM report %s unavailable (%s)",
                        report.label,
                        type(err).__name__,
                    )
                    continue
                if current:
                    fields = frozenset(current)
                    self._routes[report] = _Route(
                        path, cached.fields | fields if cached else fields
                    )
                    values.setdefault(report.category, {}).update(current)
                if cached is not None and not cached.fields <= current.keys():
                    _LOGGER.debug(
                        "WSB WEM report %s omitted %d previously read fields",
                        report.label,
                        len(cached.fields - current.keys()),
                    )
                    if not current:
                        self._routes.pop(report, None)
                    retry.append((report, cached))

        # Use spare calls for incomplete reports only after the regular reads.
        for report, cached in retry:
            if requests >= _MAX_EXPORT_REQUESTS:
                break
            try:
                current = report.parse(await get_page(cached.path))
            except _WEM_ERRORS as err:
                _LOGGER.debug(
                    "WSB WEM retry %s failed (%s)", report.label, type(err).__name__
                )
                continue
            if current:
                values.setdefault(report.category, {}).update(current)
                self._routes[report] = _Route(
                    cached.path, cached.fields | current.keys()
                )
        if not values:
            raise UpdateFailed("No supported WSB fields in WEM export")
        return values
