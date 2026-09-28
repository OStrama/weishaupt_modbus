"""The ``ManualComponent``: a register/coil read+write group built at runtime."""

from __future__ import annotations

from functools import cached_property
from typing import TYPE_CHECKING, Any, cast

from ._component_base import _ComponentBase
from ._const import _MAX_GAP, _MAX_SPAN, Range, RegisterSpace
from ._planning import ReadItem, ReadPlan
from ._ranges import DeviceRanges
from ._writing import write_bit_field, write_register_field
from .component import RepeatingGroupField
from .fields import CoilField, DiscreteInputField, RegisterField

if TYPE_CHECKING:
    from .._protocol import ModbusUnit


class ManualComponent(_ComponentBase):
    """Build a component from runtime-defined fields."""

    def __init__(
        self,
        unit: ModbusUnit,
        *,
        max_gap: int = _MAX_GAP,
        max_span: int = _MAX_SPAN,
        holding_ranges: tuple[Range, ...] | None = None,
        input_ranges: tuple[Range, ...] | None = None,
        coil_ranges: tuple[Range, ...] | None = None,
        discrete_ranges: tuple[Range, ...] | None = None,
    ) -> None:
        self._unit = unit
        self.max_gap = max_gap
        self.max_span = max_span
        # Readable address ranges per table; a table left None falls back to
        # gap-based planning, like Component does.
        self._ranges = DeviceRanges.declared(
            {
                "holding": holding_ranges,
                "input": input_ranges,
                "coil": coil_ranges,
                "discrete": discrete_ranges,
            }
        )
        self._registers: dict[str, tuple[RegisterField[Any], RegisterSpace]] = {}
        self._bits: dict[str, CoilField | DiscreteInputField] = {}
        self._values: dict[str, Any] = {}
        # repeating_group support (counts read from holding); groups are added by
        # key like any other target. base_offset stays 0 because addresses are absolute.
        self._static_groups: dict[str, RepeatingGroupField[Any]] = {}
        self._repeating_fields: dict[str, RepeatingGroupField[Any]] = {}
        self._build_groups()

    # -- membership ----------------------------------------------------------

    def add(
        self,
        key: str,
        target: (
            RegisterField[Any]
            | CoilField
            | DiscreteInputField
            | RepeatingGroupField[Any]
        ),
        *,
        space: RegisterSpace | None = None,
    ) -> None:
        """Add a read target under ``key``, replacing any existing one.

        Raises ``TypeError`` for an unsupported target and ``ValueError`` for an
        incompatible address space.
        """
        self.remove(key)  # replace any existing target, and invalidate the plan
        if isinstance(target, RepeatingGroupField):
            if space is not None:
                raise ValueError("space does not apply to a repeating_group")
            if target.is_static:
                self._static_groups[key] = target
                self._groups[key] = self._build_instances(
                    target, 0, cast("int", target.count), cast("int", target.stride)
                )
            else:
                if isinstance(target.count, RegisterField):
                    target.count.name = key  # the decoded count lands in _counts[key]
                self._repeating_fields[key] = target
        elif isinstance(target, (CoilField, DiscreteInputField)):
            if space is not None:
                raise ValueError(
                    "space is fixed by the field type for bits; "
                    "use coil() or discrete_input()"
                )
            target.name = key  # the read pass scatters into store[field.name]
            self._bits[key] = target
        elif isinstance(target, RegisterField):
            register_space = space or "holding"
            if register_space not in ("holding", "input"):
                raise ValueError(
                    f"register space must be 'holding' or 'input', got {space!r}"
                )
            target.name = key  # the read pass scatters into store[field.name]
            self._registers[key] = (target, register_space)
        else:
            raise TypeError(
                f"target must be a RegisterField, a bit field or a repeating_group, "
                f"got {type(target).__name__}"
            )
        self._invalidate_caches()

    def remove(self, key: str) -> None:
        """Remove the target under ``key``; invalidates the cached plan."""
        self._registers.pop(key, None)
        self._bits.pop(key, None)
        self._values.pop(key, None)
        self._static_groups.pop(key, None)
        self._repeating_fields.pop(key, None)
        self._counts.pop(key, None)
        self._strides.pop(key, None)
        self._groups.pop(key, None)
        self._invalidate_caches()

    # -- values --------------------------------------------------------------

    def get(self, key: str) -> Any:
        """The value decoded for ``key`` on the last update (None if not yet read)."""
        if key in self._static_groups or key in self._repeating_fields:
            return self._groups.get(key, [])
        return self._values.get(key)

    @property
    def values(self) -> dict[str, Any]:
        """A copy of all decoded values from the last update."""
        return dict(self._values)

    # -- update --------------------------------------------------------------

    @cached_property
    def _own_items(self) -> list[ReadItem]:
        """This component's own read targets, fixed-count instances excluded."""
        items = [
            ReadItem(self._resolve(field, space), self._values)
            for field, space in self._registers.values()
        ]
        items += [
            ReadItem(self._resolve(field, field.space), self._values)
            for field in self._bits.values()
        ]
        return items + self._count_items

    def _resolved_ranges(self) -> DeviceRanges:
        """The declared per-table ranges, with any fixed-count instances' merged.

        Raises ``ValueError`` if a table's map conflicts with an instance's.
        """
        return self._with_instance_ranges(self._ranges)

    def _build_plan(self) -> ReadPlan:
        return ReadPlan.build(
            self._read_items,
            self._resolved_ranges(),
            max_gap=self.max_gap,
            max_span=self.max_span,
        )

    async def async_update(self, *, notify: bool = True) -> dict[str, Any]:
        """Read every target and return the decoded values.

        Pass ``notify=False`` to skip the listeners, for a caller that
        notifies them itself.

        Raises ``ModbusExceptionError`` if the device rejects a block.
        """
        await self._refresh(collect_raw=False, notify=notify)
        return dict(self._values)

    # -- writes --------------------------------------------------------------

    async def write(self, key: str, value: Any) -> None:
        """Write a writable register or coil by key.

        Raises ``AttributeError`` for an unknown or read-only key and
        ``ValueError`` if the value cannot be scaled.
        """
        if key in self._registers:
            field, register_space = self._registers[key]
            await write_register_field(
                self._unit,
                field,
                field.address,
                register_space,
                value,
                label=key,
                scale_address=field.scale_register,
            )
        elif key in self._bits:
            await write_bit_field(
                self._unit, self._bits[key], self._bits[key].address, value, label=key
            )
        else:
            raise AttributeError(f"unknown key {key!r}")
