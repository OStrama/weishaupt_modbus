"""Pace requests on a Modbus connection."""

from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager


class Pacer:
    """Serializes requests on one connection and enforces the gaps between them."""

    def __init__(self, message_spacing: float = 0.0) -> None:
        if message_spacing < 0:
            raise ValueError("message_spacing must be non-negative")
        self._message_spacing = message_spacing
        self._lock = asyncio.Lock()
        self._last_finished_at = 0.0
        self._unit_spacing: dict[int, float] = {}
        self._unit_last_finished_at: dict[int, float] = {}

    def set_unit_spacing(self, unit_id: int, seconds: float) -> None:
        """Set (or, with ``0``, clear) the per-unit gap for ``unit_id``."""
        if seconds < 0:
            raise ValueError("message_spacing must be non-negative")
        if seconds:
            self._unit_spacing[unit_id] = seconds
        else:
            self._unit_spacing.pop(unit_id, None)
            self._unit_last_finished_at.pop(unit_id, None)

    @asynccontextmanager
    async def exclusive(self, timeout: float) -> AsyncIterator[None]:
        """Hold the connection for teardown, or proceed after ``timeout``.

        A request that is about to answer gets to deliver its result. A wedged
        one must not hold the teardown up, so the wait is bounded.
        """
        try:
            await asyncio.wait_for(self._lock.acquire(), timeout)
        except TimeoutError:
            yield
            return
        try:
            yield
        finally:
            self._lock.release()

    @asynccontextmanager
    async def paced(self, unit_id: int) -> AsyncIterator[None]:
        """Hold the connection for one request, after the configured gaps."""
        async with self._lock:
            unit_spacing = self._unit_spacing.get(unit_id, 0.0)
            if self._message_spacing or unit_spacing:
                now = time.monotonic()
                wait = self._message_spacing - (now - self._last_finished_at)
                if unit_spacing:
                    last_unit = self._unit_last_finished_at.get(unit_id, 0.0)
                    wait = max(wait, unit_spacing - (now - last_unit))
                if wait > 0:
                    await asyncio.sleep(wait)
            try:
                yield
            finally:
                finished = time.monotonic()
                self._last_finished_at = finished
                if unit_spacing:
                    self._unit_last_finished_at[unit_id] = finished
