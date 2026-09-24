"""All entities from the different modules."""

from .domestic_hot_water import DOMESTIC_HOT_WATER_ENTITIES
from .heat_pump import HEAT_PUMP_ENTITIES
from .heating_circuit import HEATING_CIRCUIT_ENTITIES
from .second_heat_source import SECOND_HEAT_SOURCE_ENTITIES
from .stats import STATISTICS_ENTITIES
from .system import SYSTEM_ENTITIES

ENTITIES = (
    SYSTEM_ENTITIES
    + HEAT_PUMP_ENTITIES
    + HEATING_CIRCUIT_ENTITIES
    + STATISTICS_ENTITIES
    + DOMESTIC_HOT_WATER_ENTITIES
    + SECOND_HEAT_SOURCE_ENTITIES
)
