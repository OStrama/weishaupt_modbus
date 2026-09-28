"""SunSpec error types."""


class SunSpecError(Exception):
    """Raised when a device does not behave like a SunSpec device."""


class SunSpecMapShiftError(SunSpecError):
    """The model header no longer matches its discovered location."""
