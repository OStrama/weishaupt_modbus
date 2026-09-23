"""Entity descriptions for the Weishaupt integration."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...weishaupt_modbus_client.model.device import Weishaupt

from .params import NumberParams, SelectParams, SensorParams


@dataclass(frozen=True, kw_only=True)
class SensorDescription:
    """Describe a Weishaupt sensor."""

    key: str
    report_name: str
    params: SensorParams
    value_fn: Callable[[Weishaupt], float | None]


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
    params: SelectParams
    value_fn: Callable[[Weishaupt], str | None]
    set_value_fn: Callable[[Weishaupt, str], Awaitable[None]]


EntityDescription = SensorDescription | NumberDescription | SelectDescription
