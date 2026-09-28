"""Map Modbus values to typed device components."""

from __future__ import annotations

from .._types import BitSpace
from ._component_base import UpdateListener
from ._const import Range, Raw, RegisterSpace
from ._planning import ResolvedField
from .component import (
    Component,
    Placement,
    RepeatingGroupField,
    repeating_group,
)
from .component_group import ComponentGroup
from .device import Device, UpdateReport, read_optional
from .fields import (
    CoilField,
    Converter,
    DiscreteInputField,
    FloatField,
    NumberField,
    PackedBitField,
    PackedBitsField,
    RawField,
    RegisterField,
    StringField,
    WriteValidator,
    bit,
    bits,
    boolean,
    coil,
    discrete_input,
    enum,
    flags,
    float32,
    float64,
    gauge,
    int32,
    int64,
    integer,
    raw_register,
    string,
    uint32,
    uint64,
)
from .manual import ManualComponent

__all__ = [
    "BitSpace",
    "CoilField",
    "Component",
    "ComponentGroup",
    "Converter",
    "Device",
    "DiscreteInputField",
    "FloatField",
    "ManualComponent",
    "NumberField",
    "PackedBitField",
    "PackedBitsField",
    "Placement",
    "Range",
    "Raw",
    "RawField",
    "RegisterField",
    "RegisterSpace",
    "RepeatingGroupField",
    "ResolvedField",
    "StringField",
    "UpdateListener",
    "UpdateReport",
    "WriteValidator",
    "bit",
    "bits",
    "boolean",
    "coil",
    "discrete_input",
    "enum",
    "flags",
    "float32",
    "float64",
    "gauge",
    "int32",
    "int64",
    "integer",
    "raw_register",
    "read_optional",
    "repeating_group",
    "string",
    "uint32",
    "uint64",
]
