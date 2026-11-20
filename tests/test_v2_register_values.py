"""Regression tests for the Weishaupt input register formats."""

import pytest

from custom_components.weishaupt_modbus.modbus.weishaupt_modbus_client.model.domestic_hot_water import (
    DomesticHotWaterInput,
)
from custom_components.weishaupt_modbus.modbus.weishaupt_modbus_client.model.heat_pump import (
    HeatPumpInput,
)
from custom_components.weishaupt_modbus.modbus.weishaupt_modbus_client.model.heating_circuit import (
    HeatingCircuitInput,
)
from custom_components.weishaupt_modbus.modbus.weishaupt_modbus_client.model.system import (
    SystemStatus,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(0, 0), (55, 55), (100, 100), (101, None), (253, None), (65535, None)],
)
def test_percentage_registers(raw: int, expected: int | None) -> None:
    """Percent values can be valid, out of range or unavailable."""
    assert HeatPumpInput.power_request.decode([raw]) == expected
    assert HeatingCircuitInput.room_humidity.decode([raw]) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (0x8000, None),
        (0x8001, None),
        (0x8002, None),
        (0x800A, None),
        (0x800B, None),
        (65526, -1.0),
        (350, 35.0),
    ],
)
def test_actual_temperature_registers(raw: int, expected: float | None) -> None:
    """Fault and digital statuses are distinct from signed sensor readings."""
    fields = (
        SystemStatus.outside_temperature,
        SystemStatus.intake_temperature,
        HeatingCircuitInput.room_temperature,
        HeatingCircuitInput.flow_temperature,
        DomesticHotWaterInput.temperature,
        HeatPumpInput.flow_temperature,
        HeatPumpInput.return_temperature,
        HeatPumpInput.diverter_temperature,
        HeatPumpInput.precise_flow_temperature,
    )
    for field in fields:
        assert field.decode([raw]) == expected, field.address
