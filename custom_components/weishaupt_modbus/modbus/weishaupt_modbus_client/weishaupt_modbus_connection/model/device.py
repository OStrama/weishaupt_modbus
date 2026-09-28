"""The ``Device`` base class: a library's top-level object over its components."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from ..exceptions import (
    IllegalDataAddressError,
    IllegalFunctionError,
    ModbusConnectionError,
    ModbusError,
    ModbusTimeoutError,
)
from ._const import Raw
from ._planning import _merge_raw, _sorted_raw

if TYPE_CHECKING:
    from .._protocol import ModbusUnit
    from .component import Component
    from .component_group import ComponentGroup
    from .manual import ManualComponent


@dataclass
class UpdateReport:
    """What one poll managed to refresh."""

    updated: set[str] = field(default_factory=set)
    failed: dict[str, ModbusError] = field(default_factory=dict)

    @property
    def complete(self) -> bool:
        """Whether every sub-system the poll covered refreshed."""
        return not self.failed


async def read_optional[C: Component | ComponentGroup | ManualComponent](
    component: C,
) -> C | None:
    """Read an optional sub-system; ``None`` if the device does not serve it.

    A device refuses the registers of a sub-system it lacks with an illegal
    data address or an illegal function. Any other ``ModbusError`` propagates.
    """
    try:
        await component.async_update()
    except (IllegalDataAddressError, IllegalFunctionError):
        return None
    return component


class Device:
    """Hold a device's components and poll them by attribute name."""

    def __init__(self, unit: ModbusUnit) -> None:
        self.modbus_unit = unit
        self._setup_done = False

    async def _async_setup(self) -> None:
        """Read what never changes and settle which optional sub-systems exist.

        Override in a subclass. Runs from the first poll, and again on the next
        one if it raised.
        """

    async def async_ensure_setup(self) -> None:
        """Run ``_async_setup()`` once; a failed run is retried on the next call."""
        if self._setup_done:
            return
        await self._async_setup()
        self._setup_done = True

    async def async_poll(
        self, names: Iterable[str], report: UpdateReport | None = None
    ) -> UpdateReport:
        """Read each named sub-system on its own and record what happened.

        A name whose attribute is ``None`` is skipped, so a fixed tuple can
        name an optional sub-system the device lacks. Pass ``report`` to add
        to the outcome of an earlier poll.

        Raises ``ModbusConnectionError`` as soon as one read hits it, since the
        rest would only wait for timeouts. Raises ``ModbusTimeoutError`` only
        while nothing has answered yet, so a caller can tell a dead link from
        one slow sub-system. Every other ``ModbusError`` lands in ``failed``.
        """
        await self.async_ensure_setup()
        if report is None:
            report = UpdateReport()
        updated: list[str] = []
        for name in names:
            component = getattr(self, name)
            if component is None:
                continue
            try:
                await component.async_update(notify=False)
            except ModbusConnectionError:
                raise
            except ModbusTimeoutError as err:
                if not report.updated and not report.failed:
                    raise
                report.failed[name] = err
            except ModbusError as err:
                report.failed[name] = err
            else:
                report.updated.add(name)
                updated.append(name)
        # Listeners fire once every read is in, so they see a consistent poll.
        for name in updated:
            getattr(self, name).notify()
        return report

    async def async_read_raw(self, names: Iterable[str]) -> Raw:
        """Read the named sub-systems and return their raw maps merged into one.

        The result is keyed ``{space: {address: value}}`` like
        ``Component.async_read_raw()``. Listeners do not fire. A name whose
        attribute is ``None`` is skipped. Raises the same ``ModbusError``
        subclasses as an update.
        """
        await self.async_ensure_setup()
        raw: Raw = {}
        for name in names:
            component = getattr(self, name)
            if component is None:
                continue
            _merge_raw(raw, await component.async_read_raw(notify=False))
        return _sorted_raw(raw)
