"""Readable address-range maps and the operations on them.

Each address space a component reads has one of three kinds of map. An
unconstrained space has no map and is planned gap-based. A declared map is
what the author stated in ``register_ranges`` and its siblings: the addresses
the device answers. A claimed map is what a component reads on its own,
planned alone. It stands in where the author declared nothing.

Two rules govern a merge. Declarations draw boundaries and conflict where they
overlap without matching, because they describe one device. Claims draw no
boundary and overlap freely, because they only say that something reads those
addresses. A merged map therefore never widens a read past a split a
declaration drew, and never bridges a gap no part reads.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass

from ._const import _RANGE_ATTR, Range, Space


def _range_of(address: int, ranges: tuple[Range, ...] | None) -> Range | None:
    """The readable range containing ``address``, or ``None``."""
    if ranges is None:
        return None
    for low, high in ranges:
        if low <= address <= high:
            return (low, high)
    return None


def _validate_ranges(ranges: tuple[Range, ...]) -> None:
    """Validate readable ranges.

    Raises ``ValueError`` for reversed or overlapping ranges.
    """
    for low, high in ranges:
        if low > high:
            raise ValueError(f"readable range ({low}, {high}) is reversed: low > high")
    ordered = sorted(ranges)
    for (a_low, a_high), (b_low, b_high) in zip(ordered, ordered[1:], strict=False):
        if b_low <= a_high:
            raise ValueError(
                f"readable ranges overlap: ({a_low}, {a_high}) and ({b_low}, {b_high})"
            )


def _coalesce(ranges: tuple[Range, ...]) -> tuple[Range, ...]:
    """Join ranges that touch or overlap.

    Two ranges with nothing between them describe one readable run, so a read
    may span both. Only called on maps whose parts have already been checked
    for conflicts.
    """
    joined: list[Range] = []
    for low, high in sorted(ranges):
        if joined and low <= joined[-1][1] + 1:
            joined[-1] = (joined[-1][0], max(joined[-1][1], high))
        else:
            joined.append((low, high))
    return tuple(joined)


def _ranges_excluding(
    intervals: Iterable[Range], excluded: set[int]
) -> tuple[Range, ...]:
    """Split ``intervals`` around every excluded address, dropping empty runs.

    Each ``(low, high)`` interval is cut at every excluded address it covers.
    The result only splits the input and never merges across an interval
    boundary. Used to narrow a component's readable ranges to the addresses a
    device serves.
    """
    result: list[Range] = []
    for low, high in intervals:
        start = low
        for cut in sorted(address for address in excluded if low <= address <= high):
            if cut > start:
                result.append((start, cut - 1))
            start = cut + 1
        if start <= high:
            result.append((start, high))
    return tuple(result)


@dataclass(frozen=True)
class SpaceMap:
    """The readable ranges of one address space."""

    ranges: tuple[Range, ...]

    declared: bool = True
    """Whether an author declared the ranges. A claim records reads instead."""


@dataclass(frozen=True)
class DeviceRanges:
    """A device's readable ranges per address space.

    A space mapped to ``None``, or absent entirely, is unconstrained and is
    planned gap-based. The maps live in whatever coordinate system their owner
    resolves them in. ``shift`` moves the whole device's map between systems.
    """

    maps: Mapping[Space, SpaceMap | None]

    @classmethod
    def declared(cls, ranges: Mapping[Space, tuple[Range, ...] | None]) -> DeviceRanges:
        """Wrap ranges an author declared; ``None`` leaves a space unconstrained."""
        return cls(
            {
                space: None if space_ranges is None else SpaceMap(space_ranges)
                for space, space_ranges in ranges.items()
            }
        )

    def for_space(self, space: Space) -> tuple[Range, ...] | None:
        """The readable ranges of one space, or ``None`` if unconstrained."""
        space_map = self.maps.get(space)
        return None if space_map is None else space_map.ranges

    def shift(self, offset: int) -> DeviceRanges:
        """Move every space's ranges, like the addresses they constrain."""
        if offset == 0:
            return self
        return DeviceRanges(
            {
                space: (
                    None
                    if space_map is None
                    else SpaceMap(
                        tuple(
                            (low + offset, high + offset)
                            for low, high in space_map.ranges
                        ),
                        space_map.declared,
                    )
                )
                for space, space_map in self.maps.items()
            }
        )

    @classmethod
    def claims(cls, ranges: Mapping[Space, tuple[Range, ...]]) -> DeviceRanges:
        """Wrap the addresses something reads, as a claim per space."""
        return cls(
            {
                space: SpaceMap(space_ranges, declared=False)
                for space, space_ranges in ranges.items()
            }
        )

    @classmethod
    def merged(
        cls,
        maps: Iterable[DeviceRanges],
        *,
        whose: str | Callable[[Space], str],
    ) -> DeviceRanges:
        """Merge several devices' maps into the map they jointly describe.

        Per space, unset maps add no constraint and the rest merge, so parts
        of one device at different offsets fit together. Declarations are
        compared by the addresses they name, so maps of a different shape
        over the same addresses agree. Declarations covering the same
        addresses differently conflict.

        The merged map keeps every boundary a declaration draws, so pooling
        never widens a read past a split a component declared. Claims draw no
        boundary. They overlap freely and their coverage widens the merge, and
        a gap no map covers still separates two runs.

        Raises ``ValueError`` if the declarations conflict. ``whose`` names
        whose maps are being merged in the error. A callable receives the
        conflicting space, so the message can say which one
        (``register_ranges`` alone is ambiguous between holding and input).
        """
        describe = whose if callable(whose) else lambda _space: whose
        declared_by: dict[Space, set[tuple[Range, ...]]] = {}
        claimed_by: dict[Space, set[tuple[Range, ...]]] = {}
        for device in maps:
            for space, space_map in device.maps.items():
                if space_map is None:
                    continue
                kind = declared_by if space_map.declared else claimed_by
                kind.setdefault(space, set()).add(space_map.ranges)
        merged: dict[Space, SpaceMap | None] = {}
        for space in declared_by.keys() | claimed_by.keys():
            declared = declared_by.get(space, set())
            joint = tuple(sorted({r for ranges in declared for r in _coalesce(ranges)}))
            try:
                _validate_ranges(joint)  # overlap is a conflict; touching is not
            except ValueError as err:
                raise ValueError(
                    f"{describe(space)} must agree on {_RANGE_ATTR[space]} "
                    f"where their maps overlap, but got conflicting values: "
                    f"{sorted(declared)}"
                ) from err
            # A declaration that splits a run says a read may not cross the
            # split, so every declared edge cuts the merged runs. A claim cuts
            # nothing: it is covered without being partitioned.
            cuts = sorted(
                {
                    edge
                    for ranges in declared
                    for low, high in ranges
                    for edge in (low, high + 1)
                }
            )
            claimed = (r for ranges in claimed_by.get(space, ()) for r in ranges)
            runs: list[Range] = []
            for low, high in _coalesce((*joint, *claimed)):
                start = low
                for cut in cuts:
                    if start < cut <= high:
                        runs.append((start, cut - 1))
                        start = cut
                runs.append((start, high))
            merged[space] = SpaceMap(tuple(runs), declared=bool(declared))
        return cls(merged)
