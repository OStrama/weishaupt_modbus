import pytest

from custom_components.weishaupt_modbus.modbus.descriptions.enums.system_error import (
    WhSystemError,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (65535, WhSystemError.NO_ERROR),
        (1, WhSystemError.REFRIGERANT_SENSOR_EXPANSION_VALVE_INLET),
        (13, WhSystemError.INVERTER_COMMUNICATION),
        (30, WhSystemError.EVAPORATION_TEMPERATURE_TOO_HIGH),
        (40, WhSystemError.FLOW_RATE_TOO_LOW),
        (50, WhSystemError.OUTDOOR_SENSOR_INTERRUPTED),
        (90, WhSystemError.ANALOG_INPUT_AE1_INTERRUPTED),
        (101, WhSystemError.HEAT_PUMP_OUTSIDE_OPERATING_LIMITS),
        (123, WhSystemError.NO_MODBUS_CONNECTION),
        (150, WhSystemError.COMPRESSOR_CURRENT_SENSOR_PHASE_U_FAULT),
        (184, WhSystemError.VOLTAGE_TOO_HIGH),
    ],
)
def test_system_error_values(value: int, expected: WhSystemError) -> None:
    """Test conversion of raw system error values."""
    assert WhSystemError(value) is expected


def test_no_error_value() -> None:
    """Test the special no-error value."""
    assert WhSystemError.NO_ERROR.value == 65535


def test_system_error_is_int_enum() -> None:
    """Test that system errors behave like integer values."""
    assert isinstance(WhSystemError.NO_ERROR, int)
    assert WhSystemError.INVERTER_COMMUNICATION == 13


def test_unknown_system_error_raises() -> None:
    """Test that an unknown error code is rejected."""
    with pytest.raises(ValueError):
        WhSystemError(9999)
