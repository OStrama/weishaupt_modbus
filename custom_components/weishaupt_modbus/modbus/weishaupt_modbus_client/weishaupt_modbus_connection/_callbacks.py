"""Provide a callback registry."""

from __future__ import annotations

from collections.abc import Callable


class CallbackRegistry:
    """A list of callbacks with subscribe-returns-unsubscribe and fire-all."""

    def __init__(self) -> None:
        self._callbacks: list[Callable[[], None]] = []

    def subscribe(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Register ``callback``; the returned callable removes it again."""
        self._callbacks.append(callback)

        def unsubscribe() -> None:
            try:
                self._callbacks.remove(callback)
            except ValueError:
                pass

        return unsubscribe

    def fire(self) -> None:
        """Invoke every registered callback."""
        for callback in list(self._callbacks):
            callback()
