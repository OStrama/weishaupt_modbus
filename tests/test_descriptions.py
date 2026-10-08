"""Tests for entity descriptions."""

from unittest.mock import MagicMock

from custom_components.weishaupt_modbus.const import CONF
from custom_components.weishaupt_modbus.modbus.descriptions.all import get_entities
from custom_components.weishaupt_modbus.modbus.descriptions.heating_circuit import (
    HEATING_CIRCUIT_ENTITIES2,
    HEATING_CIRCUIT_ENTITIES3,
    HEATING_CIRCUIT_ENTITIES4,
    HEATING_CIRCUIT_ENTITIES5,
)


def create_entry(**data):
    """Create a mock config entry."""
    entry = MagicMock()
    entry.data = data
    return entry


def test_get_entities_without_optional_heating_circuits():
    """Test that optional heating circuit entities are not added."""
    entities = get_entities(create_entry())

    assert not any(entity in entities for entity in HEATING_CIRCUIT_ENTITIES2)
    assert not any(entity in entities for entity in HEATING_CIRCUIT_ENTITIES3)
    assert not any(entity in entities for entity in HEATING_CIRCUIT_ENTITIES4)
    assert not any(entity in entities for entity in HEATING_CIRCUIT_ENTITIES5)


def test_get_entities_with_all_optional_heating_circuits():
    """Test that all optional heating circuit entities are added."""
    entities = get_entities(
        create_entry(
            **{
                CONF.HK2: True,
                CONF.HK3: True,
                CONF.HK4: True,
                CONF.HK5: True,
            }
        )
    )

    for heating_circuit_entities in (
        HEATING_CIRCUIT_ENTITIES2,
        HEATING_CIRCUIT_ENTITIES3,
        HEATING_CIRCUIT_ENTITIES4,
        HEATING_CIRCUIT_ENTITIES5,
    ):
        for entity in heating_circuit_entities:
            assert entity in entities
