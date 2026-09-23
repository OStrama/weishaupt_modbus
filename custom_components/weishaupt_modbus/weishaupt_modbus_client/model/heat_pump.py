"""Weishaupt heat pump register models."""

from modbus_connection.model import Component, enum, gauge, integer

from .enums import (
    HeatPumpConfiguration,
    HeatPumpFault,
    HeatPumpOperation,
    HeatPumpRestMode,
)


class HeatPumpInput(Component):
    """Weishaupt heat pump input registers."""

    register_space = "input"

    operation = enum(33101, HeatPumpOperation)
    """Heat pump operating state."""

    fault = enum(33102, HeatPumpFault)
    """Heat pump fault status."""

    power_request = gauge(
        33103,
        1,
        unit="%",
    )
    """Heat pump power demand."""

    flow_temperature = gauge(
        33104,
        0.1,
        unit="°C",
    )
    """Heat pump flow temperature."""

    return_temperature = gauge(
        33105,
        0.1,
        unit="°C",
    )
    """Heat pump return temperature."""

    evaporation_temperature = gauge(
        33106,
        0.1,
        unit="°C",
    )
    """Evaporation temperature."""

    compressor_suction_temperature = gauge(
        33107,
        0.1,
        unit="°C",
    )
    """Compressor suction gas temperature."""

    diverter_temperature = gauge(
        33108,
        0.1,
        unit="°C",
        nan=32768,
    )
    """Diverter temperature."""

    regenerative_flow_temperature = gauge(
        33109,
        0.1,
        unit="°C",
        nan=32768,
    )
    """Regenerative flow demand temperature."""

    buffer_temperature = gauge(
        33110,
        0.1,
        unit="°C",
    )
    """Buffer temperature."""

    precise_flow_temperature = gauge(
        33111,
        0.1,
        unit="°C",
    )
    """Precise flow temperature (sum flow B7)."""

    @property
    def temperature_spread(self) -> float | None:
        """Return the temperature spread between flow and return."""
        if self.flow_temperature is None or self.return_temperature is None:
            return None

        return self.flow_temperature - self.return_temperature


class HeatPumpConfig(Component):
    """Weishaupt heat pump configuration registers."""

    configuration = enum(43101, HeatPumpConfiguration)
    """Heat pump configuration."""

    rest_mode = enum(43102, HeatPumpRestMode)
    """Heat pump rest mode."""

    pump_start_type = integer(43103)
    """Pump start type."""

    heating_pump_power_setpoint = gauge(
        43104,
        1,
        unit="%",
    )
    """Pump power setpoint for heating."""

    cooling_pump_power_setpoint = gauge(
        43105,
        1,
        unit="%",
    )
    """Pump power setpoint for cooling."""

    hot_water_pump_power_setpoint = gauge(
        43106,
        1,
        unit="%",
    )
    """Pump power setpoint for hot water."""

    defrost_pump_power_setpoint = gauge(
        43107,
        1,
        unit="%",
    )
    """Pump power setpoint for defrosting."""

    heating_flow_rate_setpoint = gauge(
        43108,
        0.01,
        unit="m³/h",
    )
    """Volume flow setpoint for heating."""

    cooling_flow_rate_setpoint = gauge(
        43109,
        0.01,
        unit="m³/h",
    )
    """Volume flow setpoint for cooling."""

    hot_water_flow_rate_setpoint = gauge(
        43110,
        0.01,
        unit="m³/h",
    )
    """Volume flow setpoint for hot water."""
