"""Model SunSpec points and discovered models."""

from __future__ import annotations

from enum import IntEnum, IntFlag
from typing import TYPE_CHECKING, Any, overload

from ..component import Component, RepeatingGroupField
from ..fields import (
    Eui48Field,
    FloatField,
    IPv4Field,
    IPv6Field,
    NumberField,
    StringField,
    WriteValidator,
)
from ..fields import boolean as _boolean
from .errors import SunSpecError, SunSpecMapShiftError
from .scan import SunSpecModel, SunSpecModels, scan

if TYPE_CHECKING:
    from collections.abc import Iterable

    from ..._protocol import ModbusUnit

__all__ = [
    "SunSpecComponent",
    "SunSpecError",
    "SunSpecMapShiftError",
    "SunSpecModel",
    "SunSpecModels",
    "acc16",
    "acc32",
    "acc64",
    "bitfield16",
    "bitfield32",
    "bitfield64",
    "boolean",
    "scan",
    "enum16",
    "enum32",
    "eui48",
    "float32",
    "float64",
    "int16",
    "int32",
    "int64",
    "ipaddr",
    "ipv6addr",
    "model_length_group",
    "string",
    "sunssf",
    "uint16",
    "uint32",
    "uint64",
]

# Per-type "unimplemented" / "not accumulated" sentinels (SunSpec spec).
_INT16_NAN = 0x8000
_UINT16_NAN = 0xFFFF
_INT32_NAN = 0x8000_0000
_UINT32_NAN = 0xFFFF_FFFF
_INT64_NAN = 0x8000_0000_0000_0000
_UINT64_NAN = 0xFFFF_FFFF_FFFF_FFFF
_ACC_NAN = 0x0  # acc16/32/64: 0 means "not accumulated"
# The spec constrains a sunssf exponent to -10..10; devices have been seen
# reporting garbage outside it (typically around an inverter's sleep/wake
# transition), which would otherwise scale a sane raw value into an absurd one.
_SUNSSF_RANGE = (-10, 10)


def _scaled(
    address: int,
    *,
    count: int,
    signed: bool,
    nan: int,
    scale: float,
    scale_register: int | None,
    scale_register_stride: int,
    stride: int,
    writable: bool | WriteValidator,
    unit: str | None,
) -> NumberField[float]:
    return NumberField(
        address,
        count=count,
        signed=signed,
        nan=nan,
        scale=scale,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        scale_exponent_range=_SUNSSF_RANGE,
        stride=stride,
        writable=writable,
        unit=unit,
    )


def int16(
    address: int,
    *,
    scale: float = 1.0,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
) -> NumberField[float]:
    """A signed 16-bit point (unimplemented 0x8000)."""
    return _scaled(
        address,
        count=1,
        signed=True,
        nan=_INT16_NAN,
        scale=scale,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        stride=stride,
        writable=writable,
        unit=unit,
    )


def uint16(
    address: int,
    *,
    scale: float = 1.0,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
) -> NumberField[float]:
    """An unsigned 16-bit point (unimplemented 0xFFFF)."""
    return _scaled(
        address,
        count=1,
        signed=False,
        nan=_UINT16_NAN,
        scale=scale,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        stride=stride,
        writable=writable,
        unit=unit,
    )


def int32(
    address: int,
    *,
    scale: float = 1.0,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
) -> NumberField[float]:
    """A signed 32-bit point over two registers (unimplemented 0x80000000)."""
    return _scaled(
        address,
        count=2,
        signed=True,
        nan=_INT32_NAN,
        scale=scale,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        stride=stride,
        writable=writable,
        unit=unit,
    )


def uint32(
    address: int,
    *,
    scale: float = 1.0,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
) -> NumberField[float]:
    """An unsigned 32-bit point over two registers (unimplemented 0xFFFFFFFF)."""
    return _scaled(
        address,
        count=2,
        signed=False,
        nan=_UINT32_NAN,
        scale=scale,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        stride=stride,
        writable=writable,
        unit=unit,
    )


def int64(
    address: int,
    *,
    scale: float = 1.0,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
) -> NumberField[float]:
    """A signed 64-bit point over four registers (unimplemented 0x8000…)."""
    return _scaled(
        address,
        count=4,
        signed=True,
        nan=_INT64_NAN,
        scale=scale,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        stride=stride,
        writable=writable,
        unit=unit,
    )


def uint64(
    address: int,
    *,
    scale: float = 1.0,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
) -> NumberField[float]:
    """An unsigned 64-bit point over four registers (unimplemented 0xFFFF…)."""
    return _scaled(
        address,
        count=4,
        signed=False,
        nan=_UINT64_NAN,
        scale=scale,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        stride=stride,
        writable=writable,
        unit=unit,
    )


def acc16(
    address: int,
    *,
    scale: float = 1.0,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    stride: int = 0,
    unit: str | None = None,
) -> NumberField[int]:
    """A 16-bit accumulator, a monotonic counter (0 means not accumulated)."""
    return NumberField(
        address,
        count=1,
        signed=False,
        nan=_ACC_NAN,
        scale=scale,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        scale_exponent_range=_SUNSSF_RANGE,
        stride=stride,
        unit=unit,
    )


def acc32(
    address: int,
    *,
    scale: float = 1.0,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    stride: int = 0,
    unit: str | None = None,
) -> NumberField[int]:
    """A 32-bit accumulator over two registers (0 means not accumulated)."""
    return NumberField(
        address,
        count=2,
        signed=False,
        nan=_ACC_NAN,
        scale=scale,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        scale_exponent_range=_SUNSSF_RANGE,
        stride=stride,
        unit=unit,
    )


def acc64(
    address: int,
    *,
    scale: float = 1.0,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    stride: int = 0,
    unit: str | None = None,
) -> NumberField[int]:
    """A 64-bit accumulator over four registers (0 means not accumulated)."""
    return NumberField(
        address,
        count=4,
        signed=False,
        nan=_ACC_NAN,
        scale=scale,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        scale_exponent_range=_SUNSSF_RANGE,
        stride=stride,
        unit=unit,
    )


def sunssf(address: int, *, stride: int = 0) -> NumberField[int]:
    """A scale-factor point: a signed int16 power-of-ten exponent."""
    return NumberField(address, count=1, signed=True, nan=_INT16_NAN, stride=stride)


def boolean(
    address: int,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[bool]:
    """A 16-bit 0/1 enable-flag point decoding to ``bool`` (unimplemented 0xFFFF)."""
    return _boolean(address, nan=_UINT16_NAN, stride=stride, writable=writable)


@overload
def enum16(
    address: int, *, stride: int = 0, writable: bool | WriteValidator = False
) -> NumberField[int]: ...
@overload
def enum16[E: IntEnum](
    address: int,
    enum: type[E],
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[E]: ...
def enum16(
    address: int,
    enum: type[IntEnum] | None = None,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[Any]:
    """Create a 16-bit enumeration point."""
    return NumberField(
        address,
        count=1,
        signed=False,
        nan=_UINT16_NAN,
        convert=enum,
        stride=stride,
        writable=writable,
    )


@overload
def enum32(
    address: int, *, stride: int = 0, writable: bool | WriteValidator = False
) -> NumberField[int]: ...
@overload
def enum32[E: IntEnum](
    address: int,
    enum: type[E],
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[E]: ...
def enum32(
    address: int,
    enum: type[IntEnum] | None = None,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[Any]:
    """Create a 32-bit enumeration point."""
    return NumberField(
        address,
        count=2,
        signed=False,
        nan=_UINT32_NAN,
        convert=enum,
        stride=stride,
        writable=writable,
    )


@overload
def bitfield16(
    address: int, *, stride: int = 0, writable: bool | WriteValidator = False
) -> NumberField[int]: ...
@overload
def bitfield16[F: IntFlag](
    address: int,
    flags: type[F],
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[F]: ...
def bitfield16(
    address: int,
    flags: type[IntFlag] | None = None,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[Any]:
    """Create a 16-bit bitfield point."""
    return NumberField(
        address,
        count=1,
        signed=False,
        nan=_UINT16_NAN,
        convert=flags,
        stride=stride,
        writable=writable,
    )


@overload
def bitfield32(
    address: int, *, stride: int = 0, writable: bool | WriteValidator = False
) -> NumberField[int]: ...
@overload
def bitfield32[F: IntFlag](
    address: int,
    flags: type[F],
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[F]: ...
def bitfield32(
    address: int,
    flags: type[IntFlag] | None = None,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[Any]:
    """Create a 32-bit bitfield point."""
    return NumberField(
        address,
        count=2,
        signed=False,
        nan=_UINT32_NAN,
        convert=flags,
        stride=stride,
        writable=writable,
    )


@overload
def bitfield64(
    address: int, *, stride: int = 0, writable: bool | WriteValidator = False
) -> NumberField[int]: ...
@overload
def bitfield64[F: IntFlag](
    address: int,
    flags: type[F],
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[F]: ...
def bitfield64(
    address: int,
    flags: type[IntFlag] | None = None,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> NumberField[Any]:
    """Create a 64-bit bitfield point."""
    return NumberField(
        address,
        count=4,
        signed=False,
        nan=_UINT64_NAN,
        convert=flags,
        stride=stride,
        writable=writable,
    )


def float32(
    address: int,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
) -> FloatField:
    """An IEEE-754 single-precision point (unimplemented NaN)."""
    return FloatField(
        address,
        count=2,
        stride=stride,
        writable=writable,
        unit=unit,
    )


def float64(
    address: int,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
) -> FloatField:
    """An IEEE-754 double-precision point over four registers (unimplemented NaN)."""
    return FloatField(
        address,
        count=4,
        stride=stride,
        writable=writable,
        unit=unit,
    )


def string(
    address: int,
    length: int,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
) -> StringField:
    """A fixed-length null-padded ASCII string over ``length`` registers."""
    return StringField(address, count=length, stride=stride, writable=writable)


def ipaddr(address: int, *, stride: int = 0) -> IPv4Field:
    """An IPv4 address over two registers."""
    return IPv4Field(address, count=2, stride=stride)


def ipv6addr(address: int, *, stride: int = 0) -> IPv6Field:
    """An IPv6 address over eight registers."""
    return IPv6Field(address, count=8, stride=stride)


def eui48(address: int, *, stride: int = 0) -> Eui48Field:
    """An EUI-48 / MAC address over three registers."""
    return Eui48Field(address, count=3, stride=stride)


# -- components at discovered models --------------------------------------------


class _ModelLengthGroup[C: Component](RepeatingGroupField[C]):
    """A group template bound to one discovered model before reads are planned."""

    stride: int

    def __init__(self, component_class: type[C], start: int, stride: int) -> None:
        super().__init__(0, component_class, stride=stride)
        self._start = start

    def __set_name__(self, owner: type, name: str) -> None:
        super().__set_name__(owner, name)
        if not issubclass(owner, SunSpecComponent):
            raise TypeError(
                f"model_length_group {name!r} needs a SunSpecComponent owner,"
                f" got {owner.__name__}"
            )

    def bind(self, model: SunSpecModel) -> RepeatingGroupField[C]:
        count, remainder = divmod(model.span - self._start, self.stride)
        if count < 0 or remainder:
            raise SunSpecError(
                f"model {model.model_id}: length {model.length} does not fit"
                f" group {self.name!r} at offset {self._start}"
                f" with stride {self.stride}"
            )
        bound = RepeatingGroupField(count, self.component_class, stride=self.stride)
        bound.name = self.name
        return bound


def model_length_group[C: Component](
    component_class: type[C], *, start: int, stride: int
) -> RepeatingGroupField[C]:
    """Repeat a fixed-width block to the end of a discovered SunSpec model.

    Declare this on a ``SunSpecComponent``. ``start`` is the first block's
    offset from the model header, including its two registers. ``stride`` is
    the number of registers per block. The component class declares fields at
    instance-0 addresses, as for ``repeating_group``.

    The count is bound from the scanned length when the parent is constructed.
    A model ending at ``start`` has no instances. A shorter model or a partial
    final block raises ``SunSpecError`` before any register reads.

    Raises ``ValueError`` if ``start < 2`` or ``stride <= 0``.
    """
    if start < 2 or stride <= 0:
        raise ValueError("model_length_group requires start >= 2 and stride > 0")
    return _ModelLengthGroup(component_class, start, stride)


class SunSpecComponent(Component):
    """Represent a discovered SunSpec model."""

    model_id = uint16(0)
    model_length = uint16(1)

    def __init__(self, unit: ModbusUnit, model: SunSpecModel) -> None:
        """Initialize the component at the discovered model's address."""
        # A generated class can serve devices with different model lengths.
        # Bind counts on this instance, leaving the class's templates intact.
        self._static_groups = {
            name: field.bind(model) if isinstance(field, _ModelLengthGroup) else field
            for name, field in self._static_groups.items()
        }
        super().__init__(unit, base_offset=model.address)
        self._model = model

    def restrict_fields(self, names: Iterable[str]) -> None:
        """Narrow this component, keeping the model header fields.

        Every update verifies the header, so a restriction that dropped it
        would fail each update instead of narrowing the component.
        """
        super().restrict_fields({*names, "model_id", "model_length"})

    def _verify_read(self) -> None:
        """Verify the read-back model header against the discovered model.

        Raises ``SunSpecMapShiftError`` on a mismatch.
        """
        if (
            self.model_id != self._model.model_id
            or self.model_length != self._model.length
        ):
            raise SunSpecMapShiftError(
                f"{type(self).__name__} header mismatch:"
                f" expected {self._model.model_id}/{self._model.length},"
                f" read {self.model_id}/{self.model_length}"
                " - the register map has changed"
            )
