"""Plan and execute pooled component reads."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, NamedTuple

from .._types import BitSpace
from ..decode import decode_int16
from ..exceptions import ModbusExceptionError, ReadBlock
from ._const import _MAX_GAP, _MAX_SPAN, Range, Raw, RegisterSpace, Space
from ._ranges import DeviceRanges, _range_of, _validate_ranges
from .fields import CoilField, DiscreteInputField, RegisterField

if TYPE_CHECKING:
    from .._protocol import ModbusUnit


@dataclass(frozen=True)
class ResolvedField:
    """Where a component's field sits on the device.

    The addresses are absolute: the declared address plus everything that
    places the layout, which is ``base_offset``, a repeated instance's shift,
    and a per-field ``stride``.
    """

    field: RegisterField[Any] | CoilField | DiscreteInputField
    address: int
    """Absolute address of the field's first register or bit."""

    count: int
    """Registers the field spans (always 1 for a bit)."""

    scale_address: int | None
    """Absolute address of the field's scale register, if it has one."""

    space: RegisterSpace | BitSpace
    """The address space the field is read from and written to."""


class ReadItem(NamedTuple):
    """One read target: a resolved field, and where its value is stored."""

    resolved: ResolvedField
    store: dict[str, Any]  # the component store decoded values land in


def _plan_blocks(
    spans: Iterable[tuple[int, int]],
    ranges: tuple[Range, ...] | None = None,
    *,
    max_gap: int = _MAX_GAP,
    max_span: int = _MAX_SPAN,
) -> list[tuple[int, int]]:
    """Group address spans into read blocks.

    Raises ``ValueError`` for invalid ranges, a span wider than ``max_span``,
    or a span that does not fit inside one readable range.
    """
    if ranges is not None:
        _validate_ranges(ranges)
    ordered = sorted(set(spans))
    if not ordered:
        return []
    for address, width in ordered:
        if width > max_span:
            raise ValueError(
                f"a field spanning {width} registers exceeds the "
                f"{max_span}-register read limit"
            )
        end = address + width - 1
        if ranges is None:
            continue
        # A field the map does not contain cannot be read: it crosses a range
        # boundary, or sits at addresses the device does not answer at all.
        span_range = _range_of(address, ranges)
        if span_range is None or span_range != _range_of(end, ranges):
            raise ValueError(
                f"a field at address {address} spanning {width} registers "
                f"({address}-{end}) does not fit inside a readable range"
            )
    blocks: list[tuple[int, int]] = []
    block_start, width = ordered[0]
    block_end = block_start + width - 1  # last (inclusive) address covered so far
    block_range = _range_of(block_start, ranges)
    for address, width in ordered[1:]:
        end = address + width - 1
        if ranges is None:
            mergeable = address - block_end <= max_gap
        else:
            mergeable = _range_of(address, ranges) == block_range
        if mergeable and end - block_start + 1 <= max_span:
            block_end = max(block_end, end)
        else:
            blocks.append((block_start, block_end - block_start + 1))
            block_start, block_end = address, end
            block_range = _range_of(address, ranges)
    blocks.append((block_start, block_end - block_start + 1))
    return blocks


def _spans(items: Iterable[ReadItem]) -> dict[Space, list[tuple[int, int]]]:
    """The addresses these items cover, per space, scale registers included."""
    spans: dict[Space, list[tuple[int, int]]] = {}
    for resolved in (item.resolved for item in items):
        spans.setdefault(resolved.space, []).append((resolved.address, resolved.count))
        if resolved.scale_address is not None:
            spans[resolved.space].append((resolved.scale_address, 1))
    return spans


def unmapped_items(ranges: DeviceRanges, items: Iterable[ReadItem]) -> list[ReadItem]:
    """The items read from a space ``ranges`` leaves unconstrained."""
    return [item for item in items if ranges.for_space(item.resolved.space) is None]


def claimed_ranges(
    items: Iterable[ReadItem], *, max_gap: int, max_span: int
) -> DeviceRanges:
    """Claim the addresses these items cover when read on their own.

    This stands in for a readable map a component did not declare: it claims
    exactly what the component reads by itself, so pooling it with others
    cannot bridge into addresses no component claims.
    """
    return DeviceRanges.claims(
        {
            space: tuple(
                (start, start + count - 1)
                for start, count in _plan_blocks(
                    space_spans, None, max_gap=max_gap, max_span=max_span
                )
            )
            for space, space_spans in _spans(items).items()
        }
    )


def _reader(
    unit: ModbusUnit, space: Space
) -> Callable[[int, int], Awaitable[Sequence[int | bool]]]:
    """The unit's read call for one address space (FC03/FC04/FC01/FC02)."""
    match space:
        case "holding":
            return unit.read_holding_registers
        case "input":
            return unit.read_input_registers
        case "coil":
            return unit.read_coils
        case "discrete":
            return unit.read_discrete_inputs


class ReadPlan(NamedTuple):
    """Store the targets and blocks for one component read."""

    items: list[ReadItem]
    blocks: dict[Space, list[tuple[int, int]]]

    @classmethod
    def build(
        cls,
        items: Iterable[ReadItem],
        ranges: DeviceRanges,
        *,
        max_gap: int = _MAX_GAP,
        max_span: int = _MAX_SPAN,
    ) -> ReadPlan:
        """Plan block reads covering ``items``."""
        items = list(items)
        return cls(
            items,
            {
                space: _plan_blocks(
                    space_spans,
                    ranges.for_space(space),
                    max_gap=max_gap,
                    max_span=max_span,
                )
                for space, space_spans in _spans(items).items()
            },
        )

    async def execute(self, unit: ModbusUnit, *, collect_raw: bool = False) -> Raw:
        """Read and decode every block.

        Raises ``ModbusExceptionError`` if the device rejects a block.
        """
        if not self.items:
            return {}
        values: dict[tuple[Space, int], int | bool] = {}
        for space, space_blocks in self.blocks.items():
            read = _reader(unit, space)
            for start, count in space_blocks:
                try:
                    got = await read(start, count)
                except ModbusExceptionError as err:
                    raise ModbusExceptionError.from_code(
                        err.exception_code,
                        f"{space} block read at address {start} (count {count}) "
                        f"returned Modbus exception code {err.exception_code}",
                        block=ReadBlock(space, start, count),
                    ) from err
                for offset in range(count):
                    values[(space, start + offset)] = got[offset]
        for item in self.items:
            resolved = item.resolved
            words = [
                values[(resolved.space, resolved.address + offset)]
                for offset in range(resolved.count)
            ]
            scale_exponent: int | None = None
            if resolved.scale_address is not None:
                scale_exponent = decode_int16(
                    [values[(resolved.space, resolved.scale_address)]]
                )
            field = resolved.field
            item.store[field.name] = field.decode(words, scale_exponent)
        if not collect_raw:
            return {}
        raw: Raw = {}
        for (space, address), value in values.items():
            raw.setdefault(space, {})[address] = value
        return raw


def _merge_raw(
    into: dict[str, dict[int, int | bool]],
    more: Mapping[str, Mapping[int, int | bool]],
) -> None:
    """Merge a raw ``{space: {address: value}}`` map into an accumulator in place."""
    for space, values in more.items():
        into.setdefault(space, {}).update(values)


def _sorted_raw(raw: Raw) -> Raw:
    """The same raw map with every space's addresses ascending."""
    return {space: dict(sorted(values.items())) for space, values in raw.items()}


class _Readable:
    """Share read-plan execution between component types."""

    _unit: ModbusUnit
    _plan: ReadPlan | None = None
    _parent: _Readable | None = None

    def _build_plan(self) -> ReadPlan:
        """This object's read plan; built lazily and cached by :meth:`_refresh`."""
        raise NotImplementedError

    def notify(self) -> None:
        """Fire update listeners; provided by the subclass."""
        raise NotImplementedError

    async def _refresh_repeating_groups(self, *, collect_raw: bool) -> Raw:
        """The register-count ``repeating_group`` second pass; subclass-provided."""
        raise NotImplementedError

    def _invalidate_caches(self) -> None:
        """Drop the caches this object owns; subclasses add theirs via ``super()``."""
        self._plan = None
        if self._parent is not None:
            self._parent._invalidate_caches()

    def _verify_read(self) -> None:
        """Check the values just read, before any listener sees them.

        Runs on every refresh, whether or not it notifies. Subclasses raise to
        fail the update.
        """

    async def _refresh(self, *, collect_raw: bool, notify: bool = True) -> Raw:
        """Read all targets and optionally return raw values."""
        if self._plan is None:
            self._plan = self._build_plan()
        raw = await self._plan.execute(self._unit, collect_raw=collect_raw)
        _merge_raw(raw, await self._refresh_repeating_groups(collect_raw=collect_raw))
        self._verify_read()
        if notify:
            self.notify()
        return raw

    async def async_read_raw(
        self, *, notify: bool = True
    ) -> dict[str, dict[int, int | bool]]:
        """Read and return every target keyed by address space and address.

        Raises ``ModbusExceptionError`` if the device rejects a block.
        """
        raw = await self._refresh(collect_raw=True, notify=notify)
        return _sorted_raw(raw)
