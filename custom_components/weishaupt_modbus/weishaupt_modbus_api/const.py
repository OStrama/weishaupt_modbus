"""Constants for the Weishaupt Modbus API."""

DEFAULT_PORT = 502

# Weishaupt Hardware-level limits
MAX_BLOCK_READ_COUNT = 5


# Connection backoff constants imported from legacy modbusobject.py
BACKOFF_BASE_SECONDS = 5 * 60  # 5 minutes
BACKOFF_MAX_SECONDS = 60 * 60  # 60 minutes
BACKOFF_THRESHOLD_FAILURES = 3
