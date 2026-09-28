"""Address-space types and planning defaults shared across the model."""

from __future__ import annotations

from typing import Literal

from .._types import BitSpace

# Defaults for Component.max_gap / Component.max_span (overridable per device).
_MAX_GAP = 16  # gap-based planning: merge spans within this many addresses
# Default block-width cap. 125 is the Modbus per-request ceiling for read-holding
# (FC03) / read-input (FC04); a device whose gateway caps lower can override it.
_MAX_SPAN = 125

Range = tuple[int, int]  # an inclusive (low, high) readable address range

# Which register space a field is read from: input (FC04) or holding (FC03).
# They are separate address spaces (input 507 is a different register from
# holding 507), so blocks from different spaces are never merged into one read.
RegisterSpace = Literal["input", "holding"]

# Any of the four Modbus address spaces a read target can live in.
Space = RegisterSpace | BitSpace

# Raw read results, grouped ``{space: {address: value}}``: words for the
# register spaces, booleans for the bit spaces.
Raw = dict[str, dict[int, int | bool]]

# The attribute a space's readable ranges are declared under, for error messages.
_RANGE_ATTR: dict[Space, str] = {
    "holding": "register_ranges",
    "input": "register_ranges",
    "coil": "coil_ranges",
    "discrete": "discrete_ranges",
}
