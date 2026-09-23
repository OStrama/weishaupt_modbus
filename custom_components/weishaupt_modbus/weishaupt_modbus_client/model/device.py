"""Weishaupt device model."""

from modbus_connection.model import ComponentGroup, Device, UpdateReport

from .domestic_hot_water import DomesticHotWaterConfig, DomesticHotWaterInput
from .heat_pump import HeatPumpConfig, HeatPumpInput
from .heating_circuit import HeatingCircuitConfigs, HeatingCircuitInputs
from .system import SystemConfig, SystemStatus

READINGS = (
    "system",
    "heat_pump",
    "heating_circuit",
    "domestic_hot_water",
    # "heating_circuit_configs",
)


class Weishaupt(Device):
    """Weishaupt WBB device reached through a ModbusUnit."""

    def __init__(self, unit) -> None:
        """__init__ ."""
        super().__init__(unit)

        self.system_config = SystemConfig(unit)
        self.system_input = SystemStatus(unit)
        self.system = ComponentGroup(
            unit,
            [self.system_config, self.system_input],
        )

        self.heat_pump_config = HeatPumpConfig(unit)
        self.heat_pump_input = HeatPumpInput(unit)
        self.heat_pump = ComponentGroup(
            unit,
            [self.heat_pump_config, self.heat_pump_input],
        )

        self.heating_circuit_configs = HeatingCircuitConfigs(unit)
        self.heating_circuit_inputs = HeatingCircuitInputs(unit)

        self.heating_circuit_config = self.heating_circuit_configs.heating_circuits[0]
        self.heating_circuit_input = self.heating_circuit_inputs.heating_circuits[0]

        self.heating_circuit = ComponentGroup(
            unit,
            [
                self.heating_circuit_config,
                self.heating_circuit_input,
            ],
        )

        self.domestic_hot_water_config = DomesticHotWaterConfig(unit)
        self.domestic_hot_water_input = DomesticHotWaterInput(unit)

        self.domestic_hot_water = ComponentGroup(
            unit,
            [
                self.domestic_hot_water_config,
                self.domestic_hot_water_input,
            ],
        )

    async def async_update(self) -> UpdateReport:
        """Refresh all device data."""
        return await self.async_poll(READINGS)
