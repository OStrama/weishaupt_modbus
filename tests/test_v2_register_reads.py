"""Tests for controller read limits through the actual v2 polling path."""

import asyncio

from modbus_connection.exceptions import ModbusExceptionError

from custom_components.weishaupt_modbus.modbus.weishaupt_modbus_client.model.device import (
    Weishaupt,
)


class FiveRegisterUnit:
    """Synthetic controller enforcing the documented request length."""

    def __init__(self) -> None:
        """Initialise the synthetic controller and its request trace."""
        self.requests: list[tuple[str, int, int]] = []
        self.missing_hot_water = False

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        """Record a holding-register read."""
        return self.read("holding", address, count)

    async def read_input_registers(self, address: int, count: int) -> list[int]:
        """Record an input-register read."""
        return self.read("input", address, count)

    def read(self, space: str, address: int, count: int) -> list[int]:
        """Supply an address-dependent value or reject an unsupported block."""
        self.requests.append((space, address, count))
        if count > 5 or (
            self.missing_hot_water
            and space == "input"
            and 32102 in range(address, address + count)
        ):
            raise ModbusExceptionError.from_code(2, "synthetic unsupported read")
        return [register % 100 for register in range(address, address + count)]


def test_poll_every_report_with_five_register_limit() -> None:
    """Refresh every report without changing offset or word order."""
    names = (
        "system",
        "heat_pump",
        "heating_circuit",
        "heating_circuit2",
        "heating_circuit3",
        "heating_circuit4",
        "heating_circuit5",
        "domestic_hot_water",
        "second_heat_source",
        "statistics",
        "io",
    )
    unit = FiveRegisterUnit()
    device = Weishaupt(unit, names)
    report = asyncio.run(device.async_update())

    assert report.updated == set(names), report.failed
    assert not report.failed
    assert all(1 <= count <= 5 for _, _, count in unit.requests)
    assert device.heat_pump_input.power_request == 3
    assert device.heating_circuit_input5.flow_temperature == 0.5


def test_failed_report_recovers_without_hiding_system() -> None:
    """An independently failed report recovers on its next successful read."""
    unit = FiveRegisterUnit()
    device = Weishaupt(unit, ("system", "domestic_hot_water"))

    async def poll_twice() -> None:
        unit.missing_hot_water = True
        failed = await device.async_update()
        assert failed.updated == {"system"}
        assert failed.failed.keys() == {"domestic_hot_water"}

        unit.missing_hot_water = False
        recovered = await device.async_update()
        assert recovered.updated == {"system", "domestic_hot_water"}
        assert not recovered.failed

    asyncio.run(poll_twice())
