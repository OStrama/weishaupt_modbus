"""Unit tests for WebIF sensor value handling (issue #159)."""

from unittest.mock import MagicMock

import pytest

from custom_components.weishaupt_modbus import entities
from custom_components.weishaupt_modbus.const import DEVICES, FORMATS, TYPES
from custom_components.weishaupt_modbus.items import WebItem


def make_webitem(
    fmt: str, name: str = "Soll Leistung", params: dict | None = None
) -> WebItem:
    """Create a WebItem with the given format and optional params."""
    return WebItem(
        name=name,
        mformat=fmt,
        mtype=TYPES.SENSOR,
        device=DEVICES.WIW,
        webif_group="WIW",
        translation_key="webif_test",
        params=params,
    )


class TestWebItemGetValue:
    """WebItem.get_value must strip units for numeric formats and tolerate None."""

    def test_number_strips_unit(self):
        """A NUMBER value keeps only the numeric part ('1234 kWh' -> '1234')."""
        assert make_webitem(FORMATS.NUMBER).get_value("1234 kWh") == "1234"

    def test_number_non_numeric_kept(self):
        """A non-numeric NUMBER value is returned unchanged."""
        assert make_webitem(FORMATS.NUMBER).get_value("Aus") == "Aus"

    def test_temperature_strips_unit(self):
        """A TEMPERATURE value keeps only the numeric part."""
        assert make_webitem(FORMATS.TEMPERATURE).get_value("26.0 °C") == "26.0"

    def test_text_kept_unchanged(self):
        """A TEXT value is returned unchanged."""
        assert make_webitem(FORMATS.TEXT).get_value("Betrieb aktiv") == "Betrieb aktiv"

    def test_none_is_tolerated(self):
        """A None value must not raise AttributeError on None.split(...)."""
        assert make_webitem(FORMATS.TEMPERATURE).get_value(None) is None
        assert make_webitem(FORMATS.NUMBER).get_value(None) is None


class TestWebifSensorCoercion:
    """MyWebifSensorEntity must never expose a non-numeric string on a numeric sensor.

    Regression test for issue #159: a numeric WebIF sensor (e.g. "Soll Leistung",
    FORMATS.NUMBER + power device_class) received the scraped string "Aus", which
    Home Assistant then tried to int()/float() -> ValueError, crashing the
    coordinator listener.
    """

    POWER_PARAMS = {"non_numeric_value": 0}

    @staticmethod
    def _run(fmt, device_class, state_class, value, params=None):
        """Drive _handle_coordinator_update on a bare entity and return native_value."""
        ent = entities.MyWebifSensorEntity.__new__(entities.MyWebifSensorEntity)
        item = make_webitem(fmt, params=params)
        ent._api_item = item
        ent._attr_device_class = device_class
        ent._attr_state_class = state_class
        ent._attr_native_value = None
        ent.coordinator = MagicMock()
        ent.coordinator.data = {item.name: value}
        ent.async_write_ha_state = MagicMock()

        ent._handle_coordinator_update()

        # The state was written exactly once.
        ent.async_write_ha_state.assert_called_once()
        return ent._attr_native_value

    def test_non_numeric_on_numeric_sensor_becomes_none(self):
        """Default: NUMBER + numeric device_class + 'Aus' -> None (no crash)."""
        assert self._run(FORMATS.NUMBER, "power", None, "Aus") is None

    def test_numeric_string_with_unit_is_parsed(self):
        """A power/energy value like '1234 kWh' stays usable, not None."""
        assert self._run(FORMATS.NUMBER, "power", None, "1234 kWh") == 1234.0

    def test_plain_number_is_parsed(self):
        """A plain numeric string is coerced to float."""
        assert self._run(FORMATS.NUMBER, "power", None, "42.5") == 42.5

    def test_state_class_only_also_coerces(self):
        """A sensor with only a state_class (no device_class) is also coerced."""
        assert self._run(FORMATS.NUMBER, None, "measurement", "Aus") is None

    def test_non_numeric_sensor_keeps_text(self):
        """A sensor without device_class/state_class keeps its string value."""
        assert self._run(FORMATS.TEXT, None, None, "Betrieb aktiv") == "Betrieb aktiv"

    def test_power_off_falls_back_to_zero(self):
        """A power sensor with non_numeric_value=0 reports 0 W when switched off."""
        assert self._run(FORMATS.NUMBER, "power", None, "Aus", self.POWER_PARAMS) == 0

    @pytest.mark.parametrize("off_text", ["Aus", "Uit", "Off", "Arrêt", "---", ""])
    def test_power_off_is_language_independent(self, off_text):
        """The 0 fallback triggers on any non-numeric text, not just German 'Aus'."""
        assert (
            self._run(FORMATS.NUMBER, "power", None, off_text, self.POWER_PARAMS) == 0
        )

    def test_power_valid_value_still_parsed(self):
        """A real power reading is still parsed, the fallback only applies on failure."""
        assert (
            self._run(FORMATS.NUMBER, "power", None, "1234 W", self.POWER_PARAMS)
            == 1234.0
        )

    @pytest.mark.parametrize("value", ["Aus", "Ein", "---", "", "1234 kWh", "42.5"])
    def test_numeric_sensor_value_is_never_a_non_numeric_string(self, value):
        """Invariant that prevents the HA crash: native value is never a bad string."""
        result = self._run(FORMATS.NUMBER, "power", None, value)
        assert result is None or isinstance(result, (int, float))
