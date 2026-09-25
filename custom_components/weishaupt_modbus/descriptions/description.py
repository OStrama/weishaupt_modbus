"""Entity descriptions for the Weishaupt integration."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

from config.custom_components.weishaupt_modbus.coordinator import WeishauptCoordinator

if TYPE_CHECKING:
    from ...weishaupt_modbus_client.model.device import Weishaupt

from .params import NumberParams, SensorParams


@dataclass(frozen=True, kw_only=True)
class SensorDescription:
    """Describe a Weishaupt sensor."""

    key: str
    report_name: str
    params: SensorParams
    value_fn: Callable[[Weishaupt], float | str | None]
    calculated_value_fn: Callable[[WeishauptCoordinator], float | None] | None = None


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
    value_fn: Callable[[Weishaupt], str | None]
    set_value_fn: Callable[[Weishaupt, str], Awaitable[None]]


EntityDescription = SensorDescription | NumberDescription | SelectDescription
