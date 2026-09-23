"""All entities from the different modules."""

from .heat_pump import HEAT_PUMP_ENTITIES
from .system import SYSTEM_ENTITIES
from .heating_circuit import HEATING_CIRCUIT_ENTITIES

ENTITIES = SYSTEM_ENTITIES + HEAT_PUMP_ENTITIES + HEATING_CIRCUIT_ENTITIES
