"""Decode documented Weishaupt scalar values without exposing sensor sentinels."""


def decode_temperature(raw: int) -> tuple[int | None, bool]:
    """Return a signed temperature or None, and whether no sensor is installed.

    Modbus returns unsigned register words. The sensor codes in Weishaupt's
    data-point list 83807301 (1/2025-11) are signed short values; only -32768
    means the sensor is absent. Fault and digital-status codes are not numeric
    temperatures, and must remain eligible for a later successful update.
    """
    signed = raw - 65536 if raw >= 32768 else raw
    if signed == -32768:
        return None, True
    if signed in (-32767, -32766, -32758, -32757):
        return None, False
    return signed, False


def decode_percentage(raw: int) -> tuple[int | None, bool]:
    """Reject unavailable and out-of-range percentage readings without clamping."""
    if raw == 65535:
        return None, True
    if not 0 <= raw <= 100:
        return None, False
    return raw, False
