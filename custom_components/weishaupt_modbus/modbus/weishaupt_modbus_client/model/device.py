"""Weishaupt device model."""

from modbus_connection.model import ComponentGroup, Device, UpdateReport

from .domestic_hot_water import DomesticHotWaterConfig, DomesticHotWaterInput
from .heat_pump import HeatPumpConfig, HeatPumpInput
from .heating_circuit import HeatingCircuitConfigs, HeatingCircuitInputs
from .second_heat_source import SecondHeatSourceConfig, SecondHeatSourceInput
from .stats import StatisticsInput
from .system import SystemConfig, SystemStatus

# READINGS = (
#    "system",
#    "heat_pump",
#    "heating_circuit",
#    "heating_circuit2",
#    "heating_circuit3",
#    "heating_circuit4",
#    "domestic_hot_water",
#    "second_heat_source",
#    "statistics",
# "heating_circuit_configs",
# )


class Weishaupt(Device):
    """Weishaupt WBB device reached through a ModbusUnit."""

    def __init__(self, unit, readings) -> None:
        """__init__ ."""
        super().__init__(unit)
        self._readings = readings
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
        self.heating_circuit_config2 = self.heating_circuit_configs.heating_circuits[1]
        self.heating_circuit_input2 = self.heating_circuit_inputs.heating_circuits[1]

        self.heating_circuit2 = ComponentGroup(
            unit,
            [
                self.heating_circuit_config2,
                self.heating_circuit_input2,
            ],
        )

        self.heating_circuit_config3 = self.heating_circuit_configs.heating_circuits[2]
        self.heating_circuit_input3 = self.heating_circuit_inputs.heating_circuits[2]

        self.heating_circuit3 = ComponentGroup(
            unit,
            [
                self.heating_circuit_config3,
                self.heating_circuit_input3,
            ],
        )

        self.heating_circuit_config4 = self.heating_circuit_configs.heating_circuits[3]
        self.heating_circuit_input4 = self.heating_circuit_inputs.heating_circuits[3]

        self.heating_circuit4 = ComponentGroup(
            unit,
            [
                self.heating_circuit_config4,
                self.heating_circuit_input4,
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
        self.domestic_hot_water_config = DomesticHotWaterConfig(unit)
        self.domestic_hot_water_input = DomesticHotWaterInput(unit)

        self.domestic_hot_water = ComponentGroup(
            unit,
            [
                self.domestic_hot_water_config,
                self.domestic_hot_water_input,
            ],
        )

        self.second_heat_source_config = SecondHeatSourceConfig(unit)
        self.second_heat_source_input = SecondHeatSourceInput(unit)

        self.second_heat_source = ComponentGroup(
            unit,
            [
                self.second_heat_source_config,
                self.second_heat_source_input,
            ],
        )

        self.statistics_input = StatisticsInput(unit)

        self.statistics = ComponentGroup(
            unit,
            [self.statistics_input],
        )

    async def async_update(self) -> UpdateReport:
        """Refresh all device data."""
        return await self.async_poll(self._readings)
