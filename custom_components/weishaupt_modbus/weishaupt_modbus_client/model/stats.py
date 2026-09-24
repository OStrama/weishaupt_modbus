"""Weishaupt statistics register models."""

from modbus_connection.model import Component, integer


class StatisticsInput(Component):
    """Weishaupt statistics input registers."""

    register_space = "input"

    total_energy_today = integer(36101)
    total_energy_yesterday = integer(36102)
    total_energy_month = integer(36103)
    total_energy_year = integer(36104)

    heating_energy_today = integer(36201)
    heating_energy_yesterday = integer(36202)
    heating_energy_month = integer(36203)
    heating_energy_year = integer(36204)

    hot_water_energy_today = integer(36301)
    hot_water_energy_yesterday = integer(36302)
    hot_water_energy_month = integer(36303)
    hot_water_energy_year = integer(36304)

    cooling_energy_today = integer(36401)
    cooling_energy_yesterday = integer(36402)
    cooling_energy_month = integer(36403)
    cooling_energy_year = integer(36404)

    defrost_energy_today = integer(36501)
    defrost_energy_yesterday = integer(36502)
    defrost_energy_month = integer(36503)
    defrost_energy_year = integer(36504)

    total_energy_2_today = integer(36601)
    total_energy_2_yesterday = integer(36602)
    total_energy_2_month = integer(36603)
    total_energy_2_year = integer(36604)

    electric_energy_today = integer(36701)
    electric_energy_yesterday = integer(36702)
    electric_energy_month = integer(36703)
    electric_energy_year = integer(36704)

    register_36801 = integer(36801)

    @staticmethod
    def _cop(total_energy: int, electric_energy: int) -> float | None:
        """Calculate the coefficient of performance."""
        if electric_energy == 0:
            return None

        return total_energy / electric_energy

    @property
    def daily_cop(self) -> float | None:
        """Return today's coefficient of performance."""
        return self._cop(
            self.total_energy_today,
            self.electric_energy_today,
        )

    @property
    def yesterday_cop(self) -> float | None:
        """Return yesterday's coefficient of performance."""
        return self._cop(
            self.total_energy_yesterday,
            self.electric_energy_yesterday,
        )

    @property
    def monthly_cop(self) -> float | None:
        """Return this month's coefficient of performance."""
        return self._cop(
            self.total_energy_month,
            self.electric_energy_month,
        )

    @property
    def yearly_cop(self) -> float | None:
        """Return this year's coefficient of performance."""
        return self._cop(
            self.total_energy_year,
            self.electric_energy_year,
        )
