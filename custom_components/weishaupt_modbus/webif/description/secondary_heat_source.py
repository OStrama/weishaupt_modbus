"""Description of Weishaupt WebIf secondary heat source sensors."""

from .description import WebifSensorDescription
from .params import PARAMS_HOURS, PARAMS_INTEGER, PARAMS_TEXT

WEBIF_SECONDARY_HEAT_SOURCE: list[WebifSensorDescription] = [
    WebifSensorDescription(
        key="status",
        report_name="electric_heater",
        params=PARAMS_TEXT,
    ),
    WebifSensorDescription(
        key="electric_heater_1_status",
        report_name="electric_heater",
        params=PARAMS_TEXT,
    ),
    WebifSensorDescription(
        key="electric_heater_2_status",
        report_name="electric_heater",
        params=PARAMS_TEXT,
    ),
    WebifSensorDescription(
        key="electric_heater_1_operating_hours",
        report_name="electric_heater",
        params=PARAMS_HOURS,
    ),
    WebifSensorDescription(
        key="electric_heater_2_operating_hours",
        report_name="electric_heater",
        params=PARAMS_HOURS,
    ),
    WebifSensorDescription(
        key="electric_heater_1_switching_cycles",
        report_name="electric_heater",
        params=PARAMS_INTEGER,
    ),
    WebifSensorDescription(
        key="electric_heater_2_switching_cycles",
        report_name="electric_heater",
        params=PARAMS_INTEGER,
    ),
]
