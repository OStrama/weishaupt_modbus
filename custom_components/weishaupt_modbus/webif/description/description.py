"""Description of a Weishaupt WebIf sensor."""

from dataclasses import dataclass

from weishaupt_webif_api import WebifConnection

from .params import SensorParams


@dataclass(frozen=True, kw_only=True)
class WebifSensorDescription:
    """Description of a Weishaupt WebIf sensor."""

    key: str
    report_name: str
    params: SensorParams

    def value(self, api: WebifConnection) -> str | None:
        return api.get_value(self.report_name, self.key)
