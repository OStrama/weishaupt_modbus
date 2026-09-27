"""This is where all WebIf entieties come together."""

from config.custom_components.weishaupt_modbus.const import CONF
from config.custom_components.weishaupt_modbus.webif.description.heating_circuits import (
    WEBIF_HEATING_CIRCUIT,
    WEBIF_HEATING_CIRCUIT2,
    WEBIF_HEATING_CIRCUIT3,
    WEBIF_HEATING_CIRCUIT4,
    WEBIF_HEATING_CIRCUIT5,
)
from config.custom_components.weishaupt_modbus.webif.description.secondary_heat_source import (
    WEBIF_SECONDARY_HEAT_SOURCE,
)
from config.custom_components.weishaupt_modbus.webif.description.statistics import (
    WEBIF_STATISTICS,
)

from .waermepumpe import WEBIF_HEAT_PUMP


def get_webif_entities(entry) -> list:
    """Get the WebIF entities selected in the config entry."""
    entities = []

    if entry.data.get(CONF.CB_WEBIF_HK1):
        entities.extend(WEBIF_HEATING_CIRCUIT)

    if entry.data.get(CONF.CB_WEBIF_HK2):
        entities.extend(WEBIF_HEATING_CIRCUIT2)

    if entry.data.get(CONF.CB_WEBIF_HK3):
        entities.extend(WEBIF_HEATING_CIRCUIT3)

    if entry.data.get(CONF.CB_WEBIF_HK4):
        entities.extend(WEBIF_HEATING_CIRCUIT4)

    if entry.data.get(CONF.CB_WEBIF_HK5):
        entities.extend(WEBIF_HEATING_CIRCUIT5)

    if entry.data.get(CONF.CB_WEBIF_WP):
        entities.extend(WEBIF_HEAT_PUMP)

    if entry.data.get(CONF.CB_WEBIF_2WEZ):
        entities.extend(WEBIF_SECONDARY_HEAT_SOURCE)

    if entry.data.get(CONF.CB_WEBIF_SATISTICS):
        entities.extend(WEBIF_STATISTICS)

    return entities
