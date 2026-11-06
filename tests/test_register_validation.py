"""Regression tests for documented Weishaupt scalar decoding."""

import pytest

from custom_components.weishaupt_modbus.register_validation import (
    decode_percentage,
    decode_temperature,
)


@pytest.mark.parametrize(
    ("raw", "expected", "absent"),
    [
        (0, 0, False),
        (215, 215, False),
        (65436, -100, False),
        (-100, -100, False),
        (32768, None, True),
        (-32768, None, True),
        (32769, None, False),
        (-32767, None, False),
        (32770, None, False),
        (-32766, None, False),
        (32778, None, False),
        (-32758, None, False),
        (32779, None, False),
        (-32757, None, False),
    ],
)
def test_temperature_codes(raw: int, expected: int | None, absent: bool) -> None:
    """Distinguish signed values, absent sensors, faults and digital states."""
    assert decode_temperature(raw) == (expected, absent)


@pytest.mark.parametrize(
    ("raw", "expected", "absent"),
    [
        (0, 0, False),
        (100, 100, False),
        (101, None, False),
        (150, None, False),
        (-1, None, False),
        (65535, None, True),
    ],
)
def test_percentage_range(raw: int, expected: int | None, absent: bool) -> None:
    """Reject impossible percentages while preserving the availability sentinel."""
    assert decode_percentage(raw) == (expected, absent)
