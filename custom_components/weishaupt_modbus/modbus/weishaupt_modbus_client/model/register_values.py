"""Value formats shared by Weishaupt input registers."""

from modbus_connection.model import NumberField, gauge

# Weishaupt WWP data-point list 83807301, FormatSensor (raw unsigned words).
_TEMPERATURE_STATUS_CODES = (0x8000, 0x8001, 0x8002, 0x800A, 0x800B)


def sensor_temperature(address: int) -> NumberField[float]:
    """Decode a signed temperature in tenths of a degree, or a sensor status."""
    return gauge(address, 0.1, unit="°C", nan=_TEMPERATURE_STATUS_CODES)


def _valid_percentage(value: int) -> int | None:
    return value if 0 <= value <= 100 else None


def percentage(address: int) -> NumberField[int]:
    """Decode an unsigned 0–100 percent reading."""
    return NumberField(address, signed=False, convert=_valid_percentage, unit="%")
