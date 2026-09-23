"""Enums."""

from enum import IntEnum


class SystemOperationMode(IntEnum):
    """Enum."""

    system_operating_mode_automatic = 0
    system_operating_mode_heating = 1
    system_operating_mode_cooling = 2
    system_operating_mode_summer = 3
    system_operating_mode_standby = 4
    system_operating_mode_second_heat_source = 5
