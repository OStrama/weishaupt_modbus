"""Weishaupt heat pump register models."""

from modbus_connection.model import enum, gauge, integer

from .component import WeishauptComponent
from .enums import (
    HeatPumpConfiguration,
    HeatPumpFault,
    HeatPumpOperation,
    HeatPumpRestMode,
)
from .register_values import percentage, sensor_temperature


class HeatPumpInput(WeishauptComponent):
    """Weishaupt heat pump input registers."""

    register_space = "input"

    operation = enum(33101, HeatPumpOperation)
    """Heat pump operating state."""

    fault = enum(33102, HeatPumpFault)
    """Heat pump fault status."""

    power_request = percentage(33103)
    """Heat pump power demand."""

    flow_temperature = sensor_temperature(33104)
    """Heat pump flow temperature."""

    return_temperature = sensor_temperature(33105)
    """Heat pump return temperature."""

    evaporation_temperature = sensor_temperature(33106)
    """Evaporation temperature."""

    compressor_suction_temperature = sensor_temperature(33107)
    """Compressor suction gas temperature."""

    diverter_temperature = sensor_temperature(33108)
    """Diverter temperature."""

    regenerative_flow_temperature = sensor_temperature(33109)
    """Regenerative flow demand temperature."""

    buffer_temperature = sensor_temperature(33110)
    """Buffer temperature."""

    precise_flow_temperature = sensor_temperature(33111)
    """Precise flow temperature (sum flow B7)."""

    @property
    def temperature_spread(self) -> float | None:
        """Return the temperature spread between flow and return."""
        if self.precise_flow_temperature is None or self.return_temperature is None:
            return None

        return self.precise_flow_temperature - self.return_temperature


class HeatPumpConfig(WeishauptComponent):
    """Weishaupt heat pump configuration registers."""

    configuration = enum(
        43101,
        HeatPumpConfiguration,
        writable=True,
    )
    """Heat pump configuration."""

    rest_mode = enum(
        43102,
        HeatPumpRestMode,
        writable=True,
    )
    """Heat pump rest mode."""

    pump_start_type = integer(
        43103,
        writable=True,
    )
    """Pump start type."""

    heating_pump_power_setpoint = gauge(
        43104,
        1,
        unit="%",
        writable=True,
    )
    """Pump power setpoint for heating."""

    cooling_pump_power_setpoint = gauge(
        43105,
        1,
        unit="%",
        writable=True,
    )
    """Pump power setpoint for cooling."""

    hot_water_pump_power_setpoint = gauge(
        43106,
        1,
        unit="%",
        writable=True,
    )
    """Pump power setpoint for hot water."""

    defrost_pump_power_setpoint = gauge(
        43107,
        1,
        unit="%",
        writable=True,
    )
    """Pump power setpoint for defrosting."""

    heating_flow_rate_setpoint = gauge(
        43108,
        0.01,
        unit="m³/h",
        writable=True,
    )
    """Volume flow setpoint for heating."""

    cooling_flow_rate_setpoint = gauge(
        43109,
        0.01,
        unit="m³/h",
        writable=True,
    )
    """Volume flow setpoint for cooling."""

    hot_water_flow_rate_setpoint = gauge(
        43110,
        0.01,
        unit="m³/h",
        writable=True,
    )
    """Volume flow setpoint for hot water."""
