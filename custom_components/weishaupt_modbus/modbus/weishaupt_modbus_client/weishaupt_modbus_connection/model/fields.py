"""Define typed register and bit fields."""

from __future__ import annotations

import logging
import math
import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Mapping
from enum import Enum, IntEnum, IntFlag
from ipaddress import IPv4Address, IPv6Address
from typing import TYPE_CHECKING, Any, ClassVar, Self, overload

from .._types import BitSpace, WordOrder
from ..decode import (
    _signed,
    combine_words,
    decode_eui48,
    decode_float32,
    decode_float64,
    decode_ipaddr,
    decode_ipv6addr,
    decode_string,
)
from ..encode import encode_float32, encode_float64, encode_int, encode_string

__all__ = [
    "CoilField",
    "Converter",
    "DiscreteInputField",
    "Eui48Field",
    "FloatField",
    "IPv4Field",
    "IPv6Field",
    "NumberField",
    "RawField",
    "RegisterField",
    "StringField",
    "WriteValidator",
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
    "string",
    "uint32",
    "uint64",
]

_LOGGER = logging.getLogger(__name__)

# A ``writable`` value may be a validator: a callable invoked with the requested
# value before it is encoded, returning the value to write. Passing one
# marks the field writable (a callable is truthy) and lets the validator vet or
# coerce the value. It raises to reject a value. ``writable=True`` writes the
# value as-is with no validation.
WriteValidator = Callable[[Any], Any]

# A ``convert`` value maps the decoded integer to the field's Python value. It
# is a callable taking the raw (sign-decoded) int, such as an ``IntEnum`` /
# ``IntFlag`` class or a plain function, or a mapping looked up by that int. A
# callable raising ``ValueError``, or a mapping missing the key, decodes the
# value to ``None`` (warned once per distinct value). Any other exception
# propagates.
Converter = Callable[[int], Any] | Mapping[int, Any]


def _decimals(scale: float) -> int:
    """Return the decimal precision implied by a scale."""
    return max(0, len(f"{scale:.10f}".rstrip("0").split(".")[1]))


class RegisterField[T](ABC):
    """Expose a register value as a typed component attribute."""

    # Set to the attribute name by __set_name__ when used as a class descriptor;
    # the default keeps decode()/logging working on an unbound field.
    name: str = ""

    def __init__(
        self,
        address: int,
        *,
        count: int = 1,
        writable: bool | WriteValidator = False,
        stride: int = 0,
        unit: str | None = None,
        scale_register: int | None = None,
        scale_register_stride: int = 0,
        force_fc16: bool = False,
    ) -> None:
        """Initialize a register field.

        Raises ``ValueError`` if ``force_fc16`` is set on a read-only field.
        """
        if force_fc16 and not writable:
            raise ValueError("force_fc16 requires writable")
        self.address = address
        self.count = count
        self.writable = writable
        self.stride = stride
        self.unit = unit
        # Address of a scale-factor register whose 10**sf scales this field;
        # None for a static scale. Read by the planner for every field.
        self.scale_register = scale_register
        self.scale_register_stride = scale_register_stride
        self.force_fc16 = force_fc16

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: Any = ...) -> RegisterField[T]: ...

        @overload
        def __get__(self, obj: object, objtype: Any = ...) -> T | None: ...

    def __get__(self, obj: Any, objtype: Any = None) -> Any:
        if obj is None:
            return self
        return obj._values.get(self.name)

    @abstractmethod
    def decode(self, words: list[int], scale_exponent: int | None = None) -> Any:
        """Decode register words into this field's value."""

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        """Encode this field's value into register words.

        Raises ``NotImplementedError`` for a read-only field.
        """
        raise NotImplementedError(f"{type(self).__name__} is read-only")


def _nan_values(nan: int | Iterable[int] | None) -> frozenset[int] | None:
    """Normalize a field's sentinel raw value(s); None means the field has none."""
    if nan is None:
        return None
    values = frozenset((nan,)) if isinstance(nan, int) else frozenset(nan)
    return values or None


_UNSET = object()


def _warn_deprecated_float_nan(nan: object) -> None:
    """Warn about ``nan=`` on a float helper; a NaN always decodes to None."""
    if nan is _UNSET:
        return
    warnings.warn(
        "nan= is deprecated for float fields and does nothing: a NaN reading "
        "always decodes to None. Remove the argument.",
        DeprecationWarning,
        stacklevel=3,
    )


class _ScaledField[T](RegisterField[T]):
    """Apply affine and dynamic scaling to a field."""

    def __init__(
        self,
        address: int,
        *,
        scale: float = 1.0,
        offset: float = 0.0,
        nan: int | Iterable[int] | None = None,
        scale_exponent_range: tuple[int, int] | None = None,
        **kwargs: Any,
    ) -> None:
        """Initialize scaling options."""
        super().__init__(address, **kwargs)
        self.scale = scale
        self.offset = offset
        self.nan = _nan_values(nan)
        self.scale_exponent_range = scale_exponent_range
        # Rounding precision: the finer of what scale and offset each imply, so an
        # integer offset on a 0.1 scale still keeps the scale's decimal.
        self._decimals = max(_decimals(scale), _decimals(offset))

    def _exponent_in_range(self, scale_exponent: int) -> bool:
        """Whether a register-sourced exponent is within the declared spec range."""
        if self.scale_exponent_range is None:
            return True
        low, high = self.scale_exponent_range
        return low <= scale_exponent <= high

    def _scale(self, value: float, scale_exponent: int | None) -> Any:
        """Scale and round a decoded value.

        Returns ``None`` when the dynamic scale cannot produce a finite value.
        """
        try:
            factor = self._factor(scale_exponent)
        except ValueError:
            return None  # exponent outside the spec range, or unusable
        if factor == 1.0 and self.offset == 0.0:
            return value  # keep ints integral when there is nothing to scale
        scaled = value * factor + self.offset
        if not math.isfinite(scaled):
            return None  # scaled beyond the representable range
        if scale_exponent is None:
            decimals = self._decimals
        else:
            decimals = max(_decimals(factor), _decimals(self.offset))
        return int(scaled) if decimals == 0 else round(scaled, decimals)

    def _factor(self, scale_exponent: int | None) -> float:
        """Return the effective scale factor.

        Raises ``ValueError`` if the dynamic scale is missing or unusable.
        """
        if self.scale_register is not None and scale_exponent is None:
            raise ValueError(
                f"field {self.name!r} is dynamically scaled; write it through"
                " its component so the scale factor is read alongside"
            )
        factor = self.scale
        if scale_exponent is not None:
            if not self._exponent_in_range(scale_exponent):
                raise ValueError(
                    f"field {self.name!r}: scale factor {scale_exponent} is"
                    f" outside the spec range {self.scale_exponent_range}"
                )
            try:
                dynamic = 10.0**scale_exponent
            except OverflowError:
                dynamic = 0.0
            if dynamic == 0.0:
                raise ValueError(
                    f"field {self.name!r}: unusable scale factor {scale_exponent}"
                )
            factor *= dynamic
        return factor


class NumberField[T](_ScaledField[T]):
    """Decode a scaled or mapped integer field."""

    _warned_unknown: set[int] | None = None

    def __init__(
        self,
        address: int,
        *,
        signed: bool = True,
        convert: Converter | None = None,
        enum_type: type[Enum] | None = None,
        word_order: WordOrder = "big",
        **kwargs: Any,
    ) -> None:
        super().__init__(address, **kwargs)
        self.signed = signed
        if enum_type is not None:
            if convert is not None:
                raise ValueError("pass either convert or enum_type, not both")
            convert = enum_type  # an enum class is a converter
        # Callable or mapping applied to the raw value (an IntEnum / IntFlag
        # class, a plain function, or a dict); None returns the raw int.
        self.convert = convert
        self.word_order = word_order

    def decode(self, words: list[int], scale_exponent: int | None = None) -> Any:
        raw = combine_words(words, word_order=self.word_order)
        if self.nan is not None and raw in self.nan:
            return None
        # Sign-fold the raw pattern per the field's `signed` flag; the nan check
        # above still matches the raw (unsigned) sentinel pattern.
        value = _signed(raw, 16 * len(words)) if self.signed else raw
        if self.convert is not None:
            return self._convert(value)
        return self._scale(value, scale_exponent)

    def _convert(self, raw: int) -> Any:
        """Map a raw value through ``convert``; unknown values warn once -> None."""
        convert = self.convert
        assert convert is not None
        if isinstance(convert, Mapping):
            if raw in convert:
                return convert[raw]
        else:
            try:
                return convert(raw)  # IntFlag keeps unknown bits; IntEnum may raise
            except ValueError:
                pass
        if self._warned_unknown is None:
            self._warned_unknown = set()
        if raw not in self._warned_unknown:
            self._warned_unknown.add(raw)
            _LOGGER.warning(
                "Field %r: %s has no mapping for value %d; decoding as None",
                self.name,
                getattr(convert, "__name__", type(convert).__name__),
                raw,
            )
        return None

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        factor = self._factor(scale_exponent)
        if factor == 1.0 and self.offset == 0.0:
            raw = int(value)  # no transform: keep the value exact
        else:
            # snap to the precision the factor grants first, so float noise
            # in the division cannot move the result off the nearest step
            decimals = max(_decimals(factor), _decimals(self.offset))
            stepped = round(float(value), decimals)
            raw = round((stepped - self.offset) / factor)
        return encode_int(raw, count=self.count, word_order=self.word_order)


class RawField(RegisterField[int]):
    """A raw register word (no scaling, sign handling or sentinel)."""

    def __init__(
        self,
        address: int,
        *,
        word_order: WordOrder = "big",
        **kwargs: Any,
    ) -> None:
        super().__init__(address, **kwargs)
        self.word_order = word_order

    def decode(self, words: list[int], scale_exponent: int | None = None) -> int:
        return combine_words(words, word_order=self.word_order)

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        return encode_int(int(value), count=self.count, word_order=self.word_order)


class FloatField(_ScaledField[float]):
    """An IEEE-754 float over two (``float32``) or four (``float64``) registers.

    A NaN reading always decodes to ``None``.
    """

    def __init__(
        self,
        address: int,
        *,
        word_order: WordOrder = "big",
        **kwargs: Any,
    ) -> None:
        super().__init__(address, **kwargs)
        self.word_order = word_order

    def decode(self, words: list[int], scale_exponent: int | None = None) -> Any:
        decoder = decode_float64 if self.count == 4 else decode_float32
        value = decoder(words, word_order=self.word_order)
        if math.isnan(value):
            return None
        return self._scale(value, scale_exponent)

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        factor = self._factor(scale_exponent)
        if factor != 1.0 or self.offset != 0.0:
            # invert the affine transform decode applies
            value = (float(value) - self.offset) / factor
        encoder = encode_float64 if self.count == 4 else encode_float32
        return encoder(value, word_order=self.word_order)


class StringField(RegisterField[str]):
    """A fixed-length null-padded ASCII string over ``count`` registers."""

    def decode(self, words: list[int], scale_exponent: int | None = None) -> str:
        return decode_string(words)

    def encode(self, value: Any, scale_exponent: int | None = None) -> list[int]:
        return encode_string(value, length=self.count)


class IPv4Field(RegisterField[IPv4Address]):
    """An IPv4 address over two registers (read-only)."""

    def decode(
        self, words: list[int], scale_exponent: int | None = None
    ) -> IPv4Address:
        return decode_ipaddr(words)


class IPv6Field(RegisterField[IPv6Address]):
    """An IPv6 address over eight registers (read-only)."""

    def decode(
        self, words: list[int], scale_exponent: int | None = None
    ) -> IPv6Address:
        return decode_ipv6addr(words)


class Eui48Field(RegisterField[str]):
    """An EUI-48 / MAC address over three registers (read-only)."""

    def decode(self, words: list[int], scale_exponent: int | None = None) -> str:
        return decode_eui48(words)


class _BitField:
    """Expose a bit as a component attribute."""

    name: str = ""  # set by __set_name__ when used as a class descriptor
    space: ClassVar[BitSpace]  # which bit space this field's address lives in
    writable: bool | WriteValidator = False  # discrete inputs are never writable
    count = 1  # a bit field occupies a single address in its space

    def __init__(self, address: int, *, stride: int = 0) -> None:
        self.address = address
        self.stride = stride

    def decode(self, words: list[int], scale_exponent: int | None = None) -> bool:
        """Decode the single bit read for this field (scaling does not apply)."""
        return bool(words[0])

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: Any = ...) -> Self: ...

        @overload
        def __get__(self, obj: object, objtype: Any = ...) -> bool | None: ...

    def __get__(self, obj: Any, objtype: Any = None) -> Any:
        if obj is None:
            return self
        return obj._bits.get(self.name)


class CoilField(_BitField):
    """A coil (FC01) exposed as a ``bool | None`` attribute; may be writable."""

    space: ClassVar[BitSpace] = "coil"

    def __init__(
        self,
        address: int,
        *,
        writable: bool | WriteValidator = False,
        stride: int = 0,
    ) -> None:
        super().__init__(address, stride=stride)
        self.writable = writable


class DiscreteInputField(_BitField):
    """Expose a discrete input as a read-only attribute."""

    space: ClassVar[BitSpace] = "discrete"


class PackedBitsField(RegisterField[int]):
    """Expose a run of bits inside one register as an ``int``.

    Writing one packed field must leave the register's other bits alone, so
    the write reads the register back first and merges. See ``merge``.
    """

    def __init__(
        self,
        address: int,
        start: int,
        width: int = 1,
        *,
        writable: bool | WriteValidator = False,
        stride: int = 0,
        unit: str | None = None,
    ) -> None:
        """Initialize a packed-bits field.

        Raises ``ValueError`` if the run does not fit a 16-bit register.
        """
        if start < 0 or width < 1 or start + width > 16:
            raise ValueError(
                f"bits {start}..{start + width - 1} do not fit a 16-bit register"
            )
        super().__init__(address, writable=writable, stride=stride, unit=unit)
        self.start = start
        self.width = width
        self.mask = ((1 << width) - 1) << start

    def decode(self, words: list[int], scale_exponent: int | None = None) -> int:
        """Decode this field's bits out of the register word."""
        return (words[0] & self.mask) >> self.start

    def merge(self, word: int, value: Any) -> int:
        """Return ``word`` with this field's bits replaced by ``value``.

        Raises ``ValueError`` for a value too wide for the run.
        """
        raw = int(value)
        if not 0 <= raw < (1 << self.width):
            raise ValueError(
                f"{raw} does not fit the {self.width} bit(s) of {self.name or 'field'}"
            )
        return (word & ~self.mask) | (raw << self.start)


class PackedBitField(PackedBitsField):
    """Expose a single bit inside a register as a ``bool``."""

    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: Any = ...) -> PackedBitField: ...

        @overload
        def __get__(self, obj: object, objtype: Any = ...) -> bool | None: ...

        def __get__(self, obj: Any, objtype: Any = None) -> Any: ...

    def decode(self, words: list[int], scale_exponent: int | None = None) -> Any:
        """Decode this field's bit as a ``bool``."""
        return bool(super().decode(words))

    def merge(self, word: int, value: Any) -> int:
        """Return ``word`` with this field's bit set to ``value``."""
        return super().merge(word, bool(value))


# -- typed field helpers ------------------------------------------------------


def gauge(
    address: int,
    scale: float,
    *,
    offset: float = 0.0,
    signed: bool = True,
    nan: int | Iterable[int] | None = None,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[float]:
    """Create a scaled numeric register field."""
    return NumberField(
        address,
        scale=scale,
        offset=offset,
        signed=signed,
        nan=nan,
        stride=stride,
        writable=writable,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        unit=unit,
        force_fc16=force_fc16,
    )


@overload
def integer(
    address: int,
    *,
    signed: bool = True,
    nan: int | Iterable[int] | None = None,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[int]: ...


@overload
def integer(
    address: int,
    *,
    offset: float = 0.0,
    signed: bool = True,
    nan: int | Iterable[int] | None = None,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[float]: ...


def integer(
    address: int,
    *,
    offset: float = 0.0,
    signed: bool = True,
    nan: int | Iterable[int] | None = None,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    scale_register: int | None = None,
    scale_register_stride: int = 0,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[int] | NumberField[float]:
    """Create an integer register field."""
    return NumberField(
        address,
        offset=offset,
        signed=signed,
        nan=nan,
        stride=stride,
        writable=writable,
        scale_register=scale_register,
        scale_register_stride=scale_register_stride,
        unit=unit,
        force_fc16=force_fc16,
    )


def raw_register(
    address: int,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    force_fc16: bool = False,
) -> RawField:
    """A raw register word (no scaling or sign handling)."""
    return RawField(
        address,
        stride=stride,
        writable=writable,
        force_fc16=force_fc16,
    )


@overload
def uint32(
    address: int,
    *,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[int]: ...


@overload
def uint32(
    address: int,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[float]: ...


def uint32(
    address: int,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[int] | NumberField[float]:
    """An unsigned 32-bit value over two consecutive registers."""
    return NumberField(
        address,
        count=2,
        word_order=word_order,
        scale=scale,
        offset=offset,
        nan=nan,
        signed=False,
        stride=stride,
        writable=writable,
        unit=unit,
        force_fc16=force_fc16,
    )


@overload
def int32(
    address: int,
    *,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[int]: ...


@overload
def int32(
    address: int,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[float]: ...


def int32(
    address: int,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[int] | NumberField[float]:
    """A signed 32-bit value over two consecutive registers."""
    return NumberField(
        address,
        count=2,
        word_order=word_order,
        scale=scale,
        offset=offset,
        nan=nan,
        signed=True,
        stride=stride,
        writable=writable,
        unit=unit,
        force_fc16=force_fc16,
    )


def float32(
    address: int,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    nan: Any = _UNSET,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> FloatField:
    """An IEEE-754 single-precision float over two consecutive registers.

    ``nan`` is deprecated and ignored: a NaN reading always decodes to ``None``.
    """
    _warn_deprecated_float_nan(nan)
    return FloatField(
        address,
        count=2,
        word_order=word_order,
        scale=scale,
        offset=offset,
        stride=stride,
        writable=writable,
        unit=unit,
        force_fc16=force_fc16,
    )


@overload
def uint64(
    address: int,
    *,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[int]: ...


@overload
def uint64(
    address: int,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[float]: ...


def uint64(
    address: int,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[int] | NumberField[float]:
    """An unsigned 64-bit value over four consecutive registers."""
    return NumberField(
        address,
        count=4,
        word_order=word_order,
        scale=scale,
        offset=offset,
        nan=nan,
        signed=False,
        stride=stride,
        writable=writable,
        unit=unit,
        force_fc16=force_fc16,
    )


@overload
def int64(
    address: int,
    *,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[int]: ...


@overload
def int64(
    address: int,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[float]: ...


def int64(
    address: int,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    nan: int | Iterable[int] | None = None,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> NumberField[int] | NumberField[float]:
    """A signed 64-bit value over four consecutive registers."""
    return NumberField(
        address,
        count=4,
        word_order=word_order,
        scale=scale,
        offset=offset,
        nan=nan,
        signed=True,
        stride=stride,
        writable=writable,
        unit=unit,
        force_fc16=force_fc16,
    )


def float64(
    address: int,
    *,
    scale: float = 1.0,
    offset: float = 0.0,
    nan: Any = _UNSET,
    word_order: WordOrder = "big",
    stride: int = 0,
    writable: bool | WriteValidator = False,
    unit: str | None = None,
    force_fc16: bool = False,
) -> FloatField:
    """An IEEE-754 double-precision float over four consecutive registers.

    ``nan`` is deprecated and ignored: a NaN reading always decodes to ``None``.
    """
    _warn_deprecated_float_nan(nan)
    return FloatField(
        address,
        count=4,
        word_order=word_order,
        scale=scale,
        offset=offset,
        stride=stride,
        writable=writable,
        unit=unit,
        force_fc16=force_fc16,
    )


def string(
    address: int,
    length: int,
    *,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    force_fc16: bool = False,
) -> StringField:
    """A fixed-length null-padded ASCII string over ``length`` registers."""
    return StringField(
        address,
        count=length,
        stride=stride,
        writable=writable,
        force_fc16=force_fc16,
    )


def enum[E: IntEnum](
    address: int,
    enum_type: type[E],
    *,
    count: int = 1,
    signed: bool = False,
    word_order: WordOrder = "big",
    nan: int | Iterable[int] | None = None,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    force_fc16: bool = False,
) -> NumberField[E]:
    """Create a register field mapped to an ``IntEnum``."""
    return NumberField(
        address,
        count=count,
        signed=signed,
        convert=enum_type,
        word_order=word_order,
        nan=nan,
        stride=stride,
        writable=writable,
        force_fc16=force_fc16,
    )


def flags[F: IntFlag](
    address: int,
    flag_type: type[F],
    *,
    count: int = 1,
    signed: bool = False,
    word_order: WordOrder = "big",
    nan: int | Iterable[int] | None = None,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    force_fc16: bool = False,
) -> NumberField[F]:
    """Create a register field mapped to an ``IntFlag``."""
    return NumberField(
        address,
        count=count,
        signed=signed,
        convert=flag_type,
        word_order=word_order,
        nan=nan,
        stride=stride,
        writable=writable,
        force_fc16=force_fc16,
    )


# A 0/1 register's codes: anything else decodes to None (warned once), as an
# out-of-spec code should read as unknown rather than truthy.
_BOOLEAN_CODES = {0: False, 1: True}


def boolean(
    address: int,
    *,
    nan: int | Iterable[int] | None = None,
    stride: int = 0,
    writable: bool | WriteValidator = False,
    force_fc16: bool = False,
) -> NumberField[bool]:
    """A 16-bit 0/1 register decoding to ``bool``.

    For a device that reports on/off state in a holding or input register
    rather than a coil.
    """
    return NumberField(
        address,
        count=1,
        signed=False,
        nan=nan,
        convert=_BOOLEAN_CODES,
        stride=stride,
        writable=writable,
        force_fc16=force_fc16,
    )


def bit(
    address: int,
    index: int,
    *,
    writable: bool | WriteValidator = False,
    stride: int = 0,
) -> PackedBitField:
    """One bit of a register, as ``bool``.

    For a device that packs several settings into one register. A write
    re-reads the register and merges, leaving the other bits alone.
    """
    return PackedBitField(address, index, writable=writable, stride=stride)


def bits(
    address: int,
    start: int,
    width: int,
    *,
    writable: bool | WriteValidator = False,
    stride: int = 0,
    unit: str | None = None,
) -> PackedBitsField:
    """A run of ``width`` bits of a register starting at ``start``, as ``int``.

    Like :func:`bit`, a write re-reads the register and merges.
    """
    return PackedBitsField(
        address, start, width, writable=writable, stride=stride, unit=unit
    )


def coil(
    address: int,
    *,
    writable: bool | WriteValidator = False,
    stride: int = 0,
) -> CoilField:
    """A coil (FC01); pass ``writable=True`` to allow writes."""
    return CoilField(
        address,
        writable=writable,
        stride=stride,
    )


def discrete_input(address: int, *, stride: int = 0) -> DiscreteInputField:
    """A discrete input (FC02, read-only)."""
    return DiscreteInputField(address, stride=stride)
