"""Entity descriptions for the Weishaupt integration."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import IntEnum

from ...kennfeld.kennfeld import PowerMap
from ..coordinator import WeishauptCoordinator
from ..weishaupt_modbus_client.model.device import Weishaupt
from .params import NumberParams, SensorParams


@dataclass(frozen=True, kw_only=True)
class SensorDescription:
    """Describe a Weishaupt sensor."""

    key: str
    report_name: str
    params: SensorParams
    value_fn: Callable[[Weishaupt], float | str | None]
    calculated_value_fn: (
        Callable[
            [WeishauptCoordinator, PowerMap],
            float | None,
        ]
        | None
    ) = None


@dataclass(frozen=True, kw_only=True)
class NumberDescription:
    """Describe a Weishaupt number entity."""

    key: str
    report_name: str
    params: NumberParams
    value_fn: Callable[[Weishaupt], float | None]
    set_value_fn: Callable[[Weishaupt, float], Awaitable[None]]


@dataclass(frozen=True, kw_only=True)
class SelectDescription:
    """Describe a Weishaupt select entity."""

    key: str
    report_name: str
    enum: type[IntEnum]
    value_fn: Callable[[Weishaupt], int | None]
    set_value_fn: Callable[[Weishaupt, int], Awaitable[None]]


EntityDescription = SensorDescription | NumberDescription | SelectDescription
