"""Encode Python values into Modbus register words."""

from __future__ import annotations

import struct

from ._types import WordOrder

__all__ = [
    "encode_float32",
    "encode_float64",
    "encode_int",
    "encode_int16",
    "encode_int32",
    "encode_int64",
    "encode_string",
    "encode_uint16",
    "encode_uint32",
    "encode_uint64",
    "split_words",
]


def split_words(
    raw: int,
    *,
    count: int,
    word_order: WordOrder = "big",
) -> list[int]:
    """Split an integer into ``count`` register words per word order."""
    words = [(raw >> (16 * (count - 1 - i))) & 0xFFFF for i in range(count)]
    return words if word_order == "big" else list(reversed(words))


def encode_int(
    value: int,
    *,
    count: int,
    word_order: WordOrder = "big",
) -> list[int]:
    """Encode an integer into ``count`` register words.

    Raises ``OverflowError`` if the value does not fit.
    """
    raw = int(value)
    bits = 16 * count
    if not -(1 << (bits - 1)) <= raw < (1 << bits):
        raise OverflowError(f"{value} does not fit in {count} register(s)")
    if raw < 0:
        raw += 1 << bits
    return split_words(raw, count=count, word_order=word_order)


def encode_uint16(value: int) -> list[int]:
    """Encode an unsigned/signed 16-bit integer into one register."""
    return encode_int(value, count=1)


def encode_int16(value: int) -> list[int]:
    """Encode a signed 16-bit integer into one register."""
    return encode_int(value, count=1)


def encode_uint32(value: int, *, word_order: WordOrder = "big") -> list[int]:
    """Encode a 32-bit integer into two registers."""
    return encode_int(value, count=2, word_order=word_order)


def encode_int32(value: int, *, word_order: WordOrder = "big") -> list[int]:
    """Encode a signed 32-bit integer into two registers."""
    return encode_int(value, count=2, word_order=word_order)


def encode_uint64(value: int, *, word_order: WordOrder = "big") -> list[int]:
    """Encode a 64-bit integer into four registers."""
    return encode_int(value, count=4, word_order=word_order)


def encode_int64(value: int, *, word_order: WordOrder = "big") -> list[int]:
    """Encode a signed 64-bit integer into four registers."""
    return encode_int(value, count=4, word_order=word_order)


def encode_float32(value: float, *, word_order: WordOrder = "big") -> list[int]:
    """Encode an IEEE-754 single-precision float into two registers."""
    raw = struct.pack(">f", float(value))
    words = [int.from_bytes(raw[i : i + 2], "big") for i in range(0, len(raw), 2)]
    return words if word_order == "big" else list(reversed(words))


def encode_float64(value: float, *, word_order: WordOrder = "big") -> list[int]:
    """Encode an IEEE-754 double-precision float into four registers."""
    raw = struct.pack(">d", float(value))
    words = [int.from_bytes(raw[i : i + 2], "big") for i in range(0, len(raw), 2)]
    return words if word_order == "big" else list(reversed(words))


def encode_string(value: str, *, length: int) -> list[int]:
    """Encode a string into ``length`` registers, null-padded (two chars per word)."""
    raw = str(value).encode("ascii", errors="ignore")[: length * 2]
    raw = raw.ljust(length * 2, b"\x00")
    return [int.from_bytes(raw[i : i + 2], "big") for i in range(0, len(raw), 2)]
