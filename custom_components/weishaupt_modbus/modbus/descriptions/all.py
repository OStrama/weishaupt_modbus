"""All entities from the different modules."""

from config.custom_components.weishaupt_modbus.const import CONF

from .calculated import CALCULATERD_ENTITIES
from .domestic_hot_water import DOMESTIC_HOT_WATER_ENTITIES
from .heat_pump import HEAT_PUMP_ENTITIES
from .heating_circuit import (
    HEATING_CIRCUIT_ENTITIES,
    HEATING_CIRCUIT_ENTITIES2,
    HEATING_CIRCUIT_ENTITIES3,
    HEATING_CIRCUIT_ENTITIES4,
    HEATING_CIRCUIT_ENTITIES5,
)
from .second_heat_source import SECOND_HEAT_SOURCE_ENTITIES
from .stats import STATISTICS_ENTITIES
from .system import SYSTEM_ENTITIES

ENTITIES = (
    SYSTEM_ENTITIES
    + HEAT_PUMP_ENTITIES
    + HEATING_CIRCUIT_ENTITIES
    + HEATING_CIRCUIT_ENTITIES2
    + HEATING_CIRCUIT_ENTITIES3
    + HEATING_CIRCUIT_ENTITIES4
    # + HEATING_CIRCUIT_ENTITIES5
    + STATISTICS_ENTITIES
    + DOMESTIC_HOT_WATER_ENTITIES
    + SECOND_HEAT_SOURCE_ENTITIES
    + CALCULATERD_ENTITIES
)


def get_entities(entry) -> list:
    """Get all entities for the given config entry."""

    readings = (
        SYSTEM_ENTITIES
        + HEAT_PUMP_ENTITIES
        + HEATING_CIRCUIT_ENTITIES
        + DOMESTIC_HOT_WATER_ENTITIES
        + SECOND_HEAT_SOURCE_ENTITIES
        + STATISTICS_ENTITIES
        + CALCULATERD_ENTITIES
    )
    if entry.data.get(CONF.HK2, False) is True:
        readings += HEATING_CIRCUIT_ENTITIES2
    if entry.data.get(CONF.HK3, False) is True:
        readings += HEATING_CIRCUIT_ENTITIES3
    if entry.data.get(CONF.HK4, False) is True:
        readings += HEATING_CIRCUIT_ENTITIES4
    if entry.data.get(CONF.HK5, False) is True:
        readings += HEATING_CIRCUIT_ENTITIES5
    return readings
