"""Exercise WebIF construction and declared long-term-statistics metadata."""

from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from custom_components.weishaupt_modbus import entities
from custom_components.weishaupt_modbus.const import CONF, DEVICES, FORMATS, TYPES
from custom_components.weishaupt_modbus.hpconst import (
    DEVICELISTS_WEBIF,
    PARAMS_ENERGY_WEBIF,
    PARAMS_HOUR,
    PARAMS_POWER,
    PARAMS_PRESSURE,
    PARAMS_RPM,
    WEBIF_INFO_2WEZ,
)
from custom_components.weishaupt_modbus.items import WebItem
from homeassistant.components.sensor import SensorStateClass


def make_entity(item):
    """Use the actual constructor, not __new__ with prefilled attributes."""
    entry = SimpleNamespace(
        data={
            CONF.DEVICE_POSTFIX: "",
            CONF.PREFIX: "test",
            CONF.NAME_DEVICE_PREFIX: False,
            CONF.NAME_TOPIC_PREFIX: False,
        }
    )
    return entities.MyWebifSensorEntity(entry, item, MagicMock(), 0)


def make_item(fmt=FORMATS.NUMBER, params=None):
    """Build one scraped item without modifying the shared metadata."""
    return WebItem(
        name="test",
        mformat=fmt,
        mtype=TYPES.SENSOR,
        device=DEVICES.WI2W,
        webif_group="WI2W",
        translation_key="webif_statistics_test",
        params=params,
    )


@pytest.mark.parametrize(
    ("params", "state_class"),
    [
        (PARAMS_HOUR, SensorStateClass.MEASUREMENT),
        (PARAMS_ENERGY_WEBIF, SensorStateClass.TOTAL_INCREASING),
        (PARAMS_POWER, SensorStateClass.MEASUREMENT),
        (PARAMS_PRESSURE, SensorStateClass.MEASUREMENT),
        (PARAMS_RPM, SensorStateClass.MEASUREMENT),
    ],
)
def test_number_sensor_honours_declared_state_class(params, state_class):
    """Duration, energy and other numeric items retain their declared semantics."""
    before = deepcopy(params)
    entity = make_entity(make_item(params=params))
    assert entity.state_class == state_class
    assert entity.native_unit_of_measurement == params["unit"]
    assert entity.unique_id == "webif_statistics_test"
    assert params == before


@pytest.mark.parametrize("name", ["Betriebsstunden E1", "Betriebsstunden E2"])
def test_real_heater_runtime_item_is_numeric_and_statistics_eligible(name):
    """Actual E1/E2 WebIF definitions expose numeric hours and a state class."""
    item = next(item for item in WEBIF_INFO_2WEZ if item.name == name)
    entity = make_entity(item)
    entity.coordinator.data = {item.name: "36 h"}
    entity.async_write_ha_state = MagicMock()
    entity._handle_coordinator_update()
    assert entity.native_value == 36.0
    assert entity.state_class == SensorStateClass.MEASUREMENT
    entity.async_write_ha_state.assert_called_once()


def test_energy_counter_retains_total_increasing_after_update():
    """Energy is cumulative, not a measurement with hourly averages."""
    item = make_item(params=PARAMS_ENERGY_WEBIF)
    entity = make_entity(item)
    entity.coordinator.data = {item.name: "12.375 kWh"}
    entity.async_write_ha_state = MagicMock()
    entity._handle_coordinator_update()
    assert entity.native_value == 12.375
    assert entity.state_class == SensorStateClass.TOTAL_INCREASING


@pytest.mark.parametrize(("value", "expected"), [("750 rpm", 750.0), ("---", None)])
def test_state_class_only_number_is_coerced(value, expected):
    """RPM has no device class; its state class must still trigger conversion."""
    item = make_item(params=PARAMS_RPM)
    entity = make_entity(item)
    entity.coordinator.data = {item.name: value}
    entity.async_write_ha_state = MagicMock()
    entity._handle_coordinator_update()
    assert entity.native_value == expected


@pytest.mark.parametrize("params", [None, {}, {"stateclass": None}])
def test_undeclared_statistics_are_not_invented(params):
    """Unclassified numeric fields do not gain an arbitrary state class."""
    assert make_entity(make_item(params=params)).state_class is None


def test_text_status_cannot_inherit_numeric_statistics():
    """Text remains ineligible even if its metadata accidentally has a class."""
    item = make_item(FORMATS.TEXT, PARAMS_HOUR)
    entity = make_entity(item)
    entity.coordinator.data = {item.name: "Ein"}
    entity.async_write_ha_state = MagicMock()
    entity._handle_coordinator_update()
    assert entity.state_class is None
    assert entity.device_class is None
    assert entity.native_value == "Ein"


@pytest.mark.parametrize("fmt", [FORMATS.TEMPERATURE, FORMATS.PERCENTAGE])
def test_scalar_format_defaults_remain_statistics_eligible(fmt):
    """Existing temperature/percentage defaults still work without params."""
    assert make_entity(make_item(fmt)).state_class == SensorStateClass.MEASUREMENT


def test_all_existing_webif_definitions_construct():
    """All real WebIF item shapes can pass the actual sensor constructor."""
    items = [item for group in DEVICELISTS_WEBIF for item in group]
    assert items
    for item in items:
        entity = make_entity(item)
        assert entity.unique_id == item.translation_key
