"""The ``Component`` base class: a device sub-system of typed register fields."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from functools import cached_property
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, overload

from ._component_base import _ComponentBase
from ._const import _MAX_GAP, _MAX_SPAN, Range, RegisterSpace, Space
from ._planning import ReadItem, ReadPlan, ResolvedField, _plan_blocks
from ._ranges import DeviceRanges, SpaceMap, _ranges_excluding
from ._writing import write_bit_field, write_register_field
from .fields import CoilField, DiscreteInputField, RegisterField, _BitField

if TYPE_CHECKING:
    from .._protocol import ModbusUnit

#: Resolves a ``repeating_group``'s ``stride`` from the component that owns the
#: outermost block, once its fixed block has been read.
type Placement = Callable[[Any], int]


def _partition[F](
    fields: dict[str, F], keep: set[str]
) -> tuple[dict[str, F], dict[str, F]]:
    """Split ``fields`` into ``(kept, dropped)`` by name membership in ``keep``."""
    kept: dict[str, F] = {}
    dropped: dict[str, F] = {}
    for name, field in fields.items():
        (kept if name in keep else dropped)[name] = field
    return kept, dropped


class Component(_ComponentBase):
    """Map a device subsystem to typed register and bit attributes."""

    _register_fields: dict[str, RegisterField[Any]] = {}
    _bit_fields: dict[str, CoilField | DiscreteInputField] = {}

    declared_fields: Mapping[
        str, RegisterField[Any] | CoilField | DiscreteInputField
    ] = MappingProxyType({})
    # repeating_group fields, split by when they can be placed: a static group
    # (fixed ``int`` count and stride) folds into the normal read
    # like ordinary fields; any other is placed at poll time (the two-phase
    # repeating path).
    _static_groups: dict[str, RepeatingGroupField[Any]] = {}
    _repeating_fields: dict[str, RepeatingGroupField[Any]] = {}

    # The device's readable address ranges; None falls back to gap-based planning.
    # Override on a subclass (or set per instance) to constrain reads to the
    # addresses the device answers. Each applies within its own address space:
    # ``register_ranges`` to this component's register space, ``coil_ranges`` to
    # coils (FC01) and ``discrete_ranges`` to discrete inputs (FC02), which are
    # distinct spaces with their own readable maps. They are part of the declared
    # layout, so they are stated in the same coordinates as the field addresses and
    # move with the component (see ``_resolved_ranges``).
    register_ranges: tuple[Range, ...] | None = None
    coil_ranges: tuple[Range, ...] | None = None
    discrete_ranges: tuple[Range, ...] | None = None

    # Block-planning limits, overridable per device. ``max_gap`` only applies to
    # gap-based planning (no ranges): spans within this many addresses merge into
    # one read. Higher means fewer reads but more over-reading. ``max_span`` caps
    # a single block's width (125 is the Modbus per-request ceiling; lower it for
    # a gateway that caps reads shorter).
    max_gap: int = _MAX_GAP
    max_span: int = _MAX_SPAN

    # The register space this component's fields are read from (FC03 / FC04).
    register_space: RegisterSpace = "holding"

    # Set on a repeating sub-unit whose scale factors live inside its own block:
    # its ``scale_register`` addresses then shift with the instance instead of
    # naming a shared scale factor in the parent's fixed block (the default). No
    # effect on a non-repeating component, whose instance offset is 0.
    scale_in_block: bool = False

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        registers: dict[str, RegisterField[Any]] = {}
        bits: dict[str, CoilField | DiscreteInputField] = {}
        static_groups: dict[str, RepeatingGroupField[Any]] = {}
        repeating: dict[str, RepeatingGroupField[Any]] = {}
        declared: dict[str, RegisterField[Any] | CoilField | DiscreteInputField] = {}
        for klass in reversed(cls.__mro__):
            for name, value in vars(klass).items():
                if isinstance(value, RegisterField):
                    registers[name] = value
                    declared[name] = value
                elif isinstance(value, (CoilField, DiscreteInputField)):
                    bits[name] = value
                    declared[name] = value
                elif isinstance(value, RepeatingGroupField):
                    target = static_groups if value.is_static else repeating
                    target[name] = value
        cls._register_fields = registers
        cls._bit_fields = bits
        cls._static_groups = static_groups
        cls._repeating_fields = repeating
        cls.declared_fields = MappingProxyType(declared)

    def __init__(
        self,
        unit: ModbusUnit,
        index: int = 1,
        *,
        base_offset: int = 0,
        _instance_offset: int = 0,
    ) -> None:
        self._unit = unit
        self._index = index
        self._base_offset = base_offset
        # Internal, set by repeating_group when building instances: the
        # per-instance shift within the parent's block, applied to fields and
        # bits but not to scale registers (those follow the block itself),
        # unless the sub-unit sets ``scale_in_block``.
        self._instance_offset = _instance_offset
        self._values: dict[str, Any] = {}
        self._bits: dict[str, bool | None] = {}
        # Spaces whose ranges restrict_fields synthesised: a claim over what
        # the kept fields read rather than a declaration of what the device serves.
        self._claimed_spaces: set[Space] = set()
        # Set up listener and repeating_group state; fixed-count groups'
        # instances are built now so they fold into the normal read plan like
        # ordinary fields.
        self._build_groups()

    @property
    def _count_space(self) -> RegisterSpace:
        # a count register is read from this component's own register space
        return self.register_space

    def _scale_address(self, field: RegisterField[Any]) -> int:
        """Where a field's scale register is read, shifted with the layout."""
        assert field.scale_register is not None
        address = (
            field.scale_register
            + field.scale_register_stride * (self._index - 1)
            + self._base_offset
        )
        if self.scale_in_block:
            address += self._instance_offset
        return address

    def _address(self, field: RegisterField[Any] | _BitField) -> int:
        return self._declared_address(field) + self._base_offset + self._instance_offset

    def _declared_address(self, field: RegisterField[Any] | _BitField) -> int:
        """A field's address in declared coordinates (before ``base_offset``).

        This is the coordinate system readable ranges are stated in; ``_address``
        adds ``base_offset`` and the instance shift on top.
        """
        return field.address + field.stride * (self._index - 1)

    @property
    def modbus_unit(self) -> ModbusUnit:
        """The unit this component reads from and writes to."""
        return self._unit

    @cached_property
    def resolved_fields(self) -> Mapping[str, ResolvedField]:
        """Every field this component reads, with where it sits on the device.

        In declaration order, like ``declared_fields``, but narrowed by
        ``restrict_fields`` and resolved per instance: a sub-instance built by
        a ``repeating_group`` carries its own shift in the addresses.
        """
        resolved_map: dict[str, ResolvedField] = {}
        for name in self.declared_fields:
            if (register := self._register_fields.get(name)) is not None:
                resolved_map[name] = self._resolve(register, self.register_space)
            elif (bit := self._bit_fields.get(name)) is not None:
                resolved_map[name] = self._resolve(bit, bit.space)
        return MappingProxyType(resolved_map)

    # -- update --------------------------------------------------------------

    @cached_property
    def _own_items(self) -> list[ReadItem]:
        """This component's own read targets, fixed-count instances excluded."""
        items = [
            ReadItem(
                resolved,
                self._values
                if isinstance(resolved.field, RegisterField)
                else self._bits,
            )
            for resolved in self.resolved_fields.values()
        ]
        return items + self._count_items

    def _invalidate_caches(self) -> None:
        self.__dict__.pop("resolved_fields", None)
        super()._invalidate_caches()

    def _resolved_ranges(self) -> DeviceRanges:
        """This component's readable ranges at the addresses it reads.

        The declared ranges share the coordinate system of the declared field
        addresses, so they take the same shift ``_address`` applies: everything
        that moves the whole block. A per-field ``stride`` is not part of that
        shift, so a layout addressed by ``index`` states its ranges absolutely.

        A ``repeating_group``'s instances are read from this component's
        plan, so their maps are merged in (see ``_with_instance_ranges``).

        Raises ``ValueError`` if this component's map conflicts with an instance's.
        """
        stated: dict[Space, tuple[Range, ...] | None] = {
            self.register_space: self.register_ranges,
            "coil": self.coil_ranges,
            "discrete": self.discrete_ranges,
        }
        declared = DeviceRanges(
            {
                space: (
                    None
                    if ranges is None
                    else SpaceMap(ranges, declared=space not in self._claimed_spaces)
                )
                for space, ranges in stated.items()
            }
        )
        return self._with_instance_ranges(
            declared.shift(self._base_offset + self._instance_offset)
        )

    def _build_plan(self) -> ReadPlan:
        return ReadPlan.build(
            self._read_items,
            self._resolved_ranges(),
            max_gap=self.max_gap,
            max_span=self.max_span,
        )

    def restrict_fields(self, names: Iterable[str]) -> None:
        """Narrow this component to ``names`` and reshape its read plan.

        Only the fields in ``names`` are kept; excluded fields read as ``None``
        and can no longer be written.
        """
        if self._static_groups or self._repeating_fields:
            raise ValueError(
                "restrict_fields is not supported on a component with "
                "repeating_group fields"
            )
        keep = set(names)
        unknown = keep - set(self._register_fields) - set(self._bit_fields)
        if unknown:
            raise ValueError(f"unknown field(s): {', '.join(sorted(unknown))}")

        kept_registers, dropped_registers = _partition(self._register_fields, keep)
        kept_bits, dropped_bits = _partition(self._bit_fields, keep)

        spaces: tuple[tuple[Space, str, Any, Any], ...] = (
            (
                self.register_space,
                "register_ranges",
                kept_registers.values(),
                dropped_registers.values(),
            ),
            *(
                (
                    space,
                    f"{space}_ranges",
                    [f for f in kept_bits.values() if f.space == space],
                    [f for f in dropped_bits.values() if f.space == space],
                )
                for space in ("coil", "discrete")
            ),
        )
        for space, attr, kept, dropped in spaces:
            declared = getattr(self, attr)
            reshaped = self._reshaped_ranges(declared, kept, dropped)
            setattr(self, attr, reshaped)
            if declared is None and reshaped is not None:
                # synthesised from the kept fields: a claim rather than a declaration
                self._claimed_spaces.add(space)

        self._register_fields = kept_registers
        self._bit_fields = kept_bits
        # Drop any already-read value for a removed field so it reads as None,
        # whether restrict_fields runs before or after the first update.
        for name in [*dropped_registers]:
            self._values.pop(name, None)
        for name in [*dropped_bits]:
            self._bits.pop(name, None)
        self._invalidate_caches()

    def _reshaped_ranges(
        self,
        declared: tuple[Range, ...] | None,
        kept_fields: Iterable[RegisterField[Any] | _BitField],
        dropped_fields: Iterable[RegisterField[Any] | _BitField],
    ) -> tuple[Range, ...] | None:
        """Reshape one space's ranges to exclude the dropped fields' addresses.

        Everything works in declared coordinates (see ``_declared_address``),
        the same system the stored ranges live in, so ``_resolved_ranges`` shifts
        them by ``base_offset`` exactly once when the plan is built.
        """
        excluded: set[int] = set()
        for field in dropped_fields:
            address = self._declared_address(field)
            excluded.update(range(address, address + field.count))
        if not excluded:
            return declared  # nothing dropped from this space, so leave it as declared
        spans: list[tuple[int, int]] = []
        for f in kept_fields:
            spans.append((self._declared_address(f), f.count))
            if isinstance(f, RegisterField) and f.scale_register is not None:
                scale = f.scale_register + f.scale_register_stride * (self._index - 1)
                spans.append((scale, 1))
        # A kept field reading an address is proof the device serves it.
        for start, count in spans:
            excluded.difference_update(range(start, start + count))
        if not excluded:
            return declared
        if declared is not None:
            return _ranges_excluding(declared, excluded)
        if not spans:
            return declared  # every field in this space dropped, so ranges are unused
        blocks = _plan_blocks(spans, max_gap=self.max_gap, max_span=self.max_span)
        return _ranges_excluding(
            [(start, start + count - 1) for start, count in blocks], excluded
        )

    async def async_update(self, *, notify: bool = True) -> None:
        """Read this component and notify its listeners.

        Pass ``notify=False`` to skip the listeners, for a caller that
        notifies them itself.

        Raises ``ModbusExceptionError`` if the device rejects a block.
        """
        await self._refresh(collect_raw=False, notify=notify)

    # -- writes --------------------------------------------------------------

    async def write(self, field: str, value: Any) -> None:
        """Write a writable register or coil by attribute name.

        Raises ``AttributeError`` for an unknown or read-only field and
        ``ValueError`` if the value cannot be scaled.
        """
        resolved = self.resolved_fields.get(field)
        if resolved is None:
            raise AttributeError(f"unknown field {field!r}")
        if isinstance(resolved.field, RegisterField):
            await write_register_field(
                self._unit,
                resolved.field,
                resolved.address,
                self.register_space,
                value,
                label=field,
                scale_address=resolved.scale_address,
            )
        else:
            await write_bit_field(
                self._unit, resolved.field, resolved.address, value, label=field
            )


class RepeatingGroupField[C: Component]:
    """Describe repeated subcomponents."""

    name: str = ""  # set by __set_name__ when used as a class descriptor

    def __init__(
        self,
        count: RegisterField[int] | RegisterField[float] | int,
        component_class: type[C],
        *,
        stride: int | Placement,
        count_in_block: bool = True,
    ) -> None:
        self.count = count
        self.component_class = component_class
        self.stride = stride
        self.count_in_block = count_in_block

    @property
    def is_static(self) -> bool:
        """Whether the instances can be placed before the device is read."""
        return isinstance(self.count, int) and not callable(self.stride)

    def resolved_stride(self, root: Any) -> int:
        """Resolve ``stride`` against the outermost component.

        Raises ``ValueError`` if it is not positive.
        """
        stride = self.stride(root) if callable(self.stride) else self.stride
        if stride <= 0:
            raise ValueError(
                f"repeating_group {self.name!r} stride resolved to {stride};"
                " it must be > 0"
            )
        return stride

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name
        if isinstance(self.count, RegisterField):
            self.count.name = name  # the decoded count lands in ``_counts[name]``

    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: Any = ...) -> RepeatingGroupField[C]: ...

        @overload
        def __get__(self, obj: object, objtype: Any = ...) -> list[C]: ...

    def __get__(self, obj: Any, objtype: Any = None) -> Any:
        if obj is None:
            return self
        return obj._groups.get(self.name, [])


def repeating_group[C: Component](
    count: RegisterField[int] | RegisterField[float] | int,
    component_class: type[C],
    *,
    stride: int | Placement,
    count_in_block: bool = True,
) -> RepeatingGroupField[C]:
    """Create a repeated subcomponent field.

    A float-typed count field (e.g. a SunSpec ``uint16`` ``N`` point) is
    accepted: the decoded count is truncated to an ``int``, and an
    unimplemented (``None``) count yields no instances.

    ``count_in_block`` says where a register count nested inside another
    ``repeating_group`` is read. By default it is part of the repeated block, so
    it shifts with each enclosing instance. Pass ``False`` when it is a point of
    the layout that owns the outermost block, as a SunSpec ``NPt`` point is:
    every instance then reads it at the same address.

    ``stride`` may be a callable taking the component that owns the outermost
    block, for a block whose width is only known once the device has been read
    (a SunSpec curve is ``header + 2 * NPt`` wide). Such a group is placed in
    the second pass that sizes register-read counts, even with a fixed ``int``
    count. The callable is not called while the count is 0.

    On readable ranges: a fixed-count group's instances are read from the
    parent's own plan, so their maps merge into it and must not describe the
    same addresses differently. The common case is to let the parent's
    ``register_ranges`` cover the instance addresses and leave the
    sub-component's unset, which keeps the repeated area in the parent's
    block. For a sub-unit whose own map has holes the parent cannot express,
    give the sub-component ranges disjoint from the parent's. Declaring the same
    addresses in both raises ``ValueError``.

    Raises ``ValueError`` for a non-positive stride or negative fixed count. A
    callable stride is checked when it resolves instead.
    """
    if not callable(stride) and stride <= 0:
        raise ValueError(f"repeating_group stride must be > 0, got {stride}")
    if isinstance(count, int) and count < 0:
        raise ValueError(f"a fixed count must be >= 0, got {count}")
    return RepeatingGroupField(
        count,
        component_class,
        stride=stride,
        count_in_block=count_in_block,
    )
