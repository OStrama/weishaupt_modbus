"""The backend-neutral connection base class and its params dataclasses."""

from __future__ import annotations

import asyncio
import ssl
import warnings
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from ._callbacks import CallbackRegistry
from ._pacing import Pacer
from ._tls import build_tls_context
from .exceptions import ClientClosedError

if TYPE_CHECKING:
    from ._protocol import ModbusUnit

__all__ = [
    "BaseModbusConnection",
    "ModbusSerialParams",
    "ModbusTcpParams",
    "ModbusTlsParams",
    "ModbusUdpParams",
]

# The per-request timeout applied when neither the caller nor any unit asks
# for one. Message spacing and the connect delay default to none.
_DEFAULT_TIMEOUT = 10.0

# How long disconnect() and close() wait for the request in flight. A healthy
# request answers in milliseconds, so this is long enough for one to finish and
# short enough that a wedged request never holds up recycling the link.
_TEARDOWN_GRACE = 0.5


# RTU and ASCII frame a serial line. Carrying one over a socket is a serial
# link on a socket transport, which both backends already reach through a
# ``socket://`` serial device, so ``ModbusSerialParams`` is what it should be
# built from. ``ModbusTcpParams`` keeps accepting these framings for now.
_SERIAL_FRAMINGS = ("rtu", "ascii")


def _normalize_host(host: str) -> str:
    """Fold the host to lower case without changing its IPv6 scope identifier."""
    address, separator, scope = host.partition("%")
    return address.lower() + separator + scope


def _socket_device(host: str, port: int) -> str:
    """The serial device for a socket transport to this host and port.

    An IPv6 literal is bracketed. Without the brackets the URL does not parse,
    because the address's own colons are read as the port separator.
    """
    address = f"[{host}]" if ":" in host else host
    return f"socket://{address}:{port}"


@dataclass(frozen=True, kw_only=True)
class ModbusTcpParams:
    """Connection parameters for a Modbus TCP link."""

    host: str
    """Host name or IP address of the device, folded to lower case."""

    port: int = 502
    """TCP port."""

    framer: Literal["socket", "rtu", "ascii"] | None = None
    """Wire framing. Deprecated; omit it. Reads back as ``"socket"``."""

    def __post_init__(self) -> None:
        """Normalize the host, and warn for a framing that was passed."""
        object.__setattr__(self, "host", _normalize_host(self.host))
        if self.framer is None:
            object.__setattr__(self, "framer", "socket")
            return
        if self.framer not in ("socket", "rtu", "ascii"):
            raise ValueError(
                f"unknown framer {self.framer!r}; expected 'socket', 'rtu', or 'ascii'"
            )
        if self.framer in _SERIAL_FRAMINGS:
            advice = (
                f"{self.framer.upper()} frames a serial line, so carrying it over "
                "a socket is a serial link: use "
                f'ModbusSerialParams(device="{_socket_device(self.host, self.port)}"'
                f", framer={self.framer!r}) instead."
            )
        else:
            advice = "A Modbus TCP link is always MBAP-framed, so omit the argument."
        warnings.warn(
            f"ModbusTcpParams(framer={self.framer!r}) is deprecated. {advice}",
            DeprecationWarning,
            stacklevel=3,
        )

    @property
    def endpoint(self) -> tuple[str, str, int] | tuple[str, str]:
        """Hashable identity of the addressed device.

        Two params objects with equal endpoints point at the same device. A
        serial framing gives the same identity as the ``ModbusSerialParams``
        for that link.
        """
        if self.framer in _SERIAL_FRAMINGS:
            return ("serial", _socket_device(self.host, self.port))
        return ("tcp", self.host, self.port)


@dataclass(frozen=True, kw_only=True)
class ModbusUdpParams:
    """Connection parameters for a Modbus UDP link."""

    host: str
    """Host name or IP address of the device, folded to lower case."""

    port: int = 502
    """UDP port."""

    framer: Literal["socket", "rtu", "ascii"] = "socket"
    """Wire framing."""

    def __post_init__(self) -> None:
        """Normalize the host and validate the wire framing."""
        object.__setattr__(self, "host", _normalize_host(self.host))
        if self.framer not in ("socket", "rtu", "ascii"):
            raise ValueError(
                f"unknown framer {self.framer!r}; expected 'socket', 'rtu', or 'ascii'"
            )

    @property
    def endpoint(self) -> tuple[str, str, int]:
        """Hashable identity of the addressed device: transport, host, and port.

        Two params objects with equal endpoints point at the same device even
        when link settings such as ``framer`` differ.
        """
        return ("udp", self.host, self.port)


@dataclass(frozen=True, kw_only=True)
class ModbusTlsParams:
    """Connection parameters for a Modbus/TLS (Modbus Security) link."""

    host: str
    """Host name or IP address of the device, folded to lower case."""

    port: int = 802
    """TLS port."""

    verify: bool | str = True
    """Whether and how to verify the server certificate."""

    check_hostname: bool = True
    """Whether to verify the certificate hostname."""

    client_cert: str | None = None
    """Path to the client certificate."""

    client_key: str | None = None
    """Path to the private key belonging to ``client_cert``."""

    client_key_password: str | None = None
    """Password for ``client_key``, if it is encrypted."""

    sslctx: ssl.SSLContext | None = None
    """TLS context overriding the other TLS options."""

    def __post_init__(self) -> None:
        """Fold the host to lower case."""
        object.__setattr__(self, "host", _normalize_host(self.host))

    @property
    def endpoint(self) -> tuple[str, str, int]:
        """Hashable identity of the addressed device: transport, host, and port.

        Two params objects with equal endpoints point at the same device even
        when the TLS settings differ. The transport tag is ``"tcp"``: a TLS
        link and a plain-TCP link to the same host and port target the same
        TCP endpoint, and therefore the same device.
        """
        return ("tcp", self.host, self.port)

    async def create_ssl_context(self) -> ssl.SSLContext:
        """Return the supplied TLS context or build one from these parameters."""
        if self.sslctx is not None:
            return self.sslctx
        return await asyncio.to_thread(
            build_tls_context,
            self.verify,
            self.check_hostname,
            self.client_cert,
            self.client_key,
            self.client_key_password,
        )


@dataclass(frozen=True, kw_only=True)
class ModbusSerialParams:
    """Connection parameters for a Modbus serial link."""

    device: str
    """Serial port device path (e.g. ``/dev/ttyUSB0``)."""

    baudrate: int = 9600
    """Line speed in baud."""

    bytesize: Literal[7, 8] = 8
    """Data bits per character."""

    parity: Literal["N", "E", "O"] = "N"
    """Parity: none, even, or odd."""

    stopbits: Literal[1, 2] = 1
    """Stop bits per character."""

    framer: Literal["rtu", "ascii"] = "rtu"
    """Serial framing."""

    def __post_init__(self) -> None:
        """Validate the serial framing."""
        if self.framer not in ("rtu", "ascii"):
            raise ValueError(
                f"unknown serial framer {self.framer!r}; expected 'rtu' or 'ascii'"
            )

    @property
    def endpoint(self) -> tuple[str, str]:
        """Hashable identity of the addressed serial port: transport and device.

        Two params objects with equal endpoints point at the same serial port
        even when line settings such as ``baudrate``, ``parity``, or ``framer``
        differ. The device path is compared verbatim; aliases of the same port
        (e.g. a ``/dev/serial/by-id`` symlink versus ``/dev/ttyUSB0``) are not
        resolved.
        """
        return ("serial", self.device)


def _record(required: dict[int, float], unit_id: int, seconds: float | None) -> None:
    """Store a unit's requirement, dropping it when the unit withdraws."""
    if seconds is None:
        required.pop(unit_id, None)
    else:
        required[unit_id] = seconds


def _resolved(base: float | None, required: dict[int, float], default: float) -> float:
    """The largest value asked for, or ``default`` when nothing was asked.

    A default nobody chose must not outrank a unit asking for less.
    """
    asked = list(required.values())
    if base is not None:
        asked.append(base)
    return max(asked, default=default)


def _consume_failure(task: asyncio.Task[None]) -> None:
    """Observe a fire-and-forget task's failure so asyncio does not warn."""
    if not task.cancelled():
        task.exception()


def _target(
    params: ModbusTcpParams | ModbusUdpParams | ModbusTlsParams | ModbusSerialParams,
) -> str:
    if isinstance(params, ModbusSerialParams):
        return params.device
    return f"{params.host}:{params.port}"


class BaseModbusConnection(ABC):
    """Represent a shared link to a Modbus network."""

    def __init__(
        self,
        params: (
            ModbusTcpParams | ModbusUdpParams | ModbusTlsParams | ModbusSerialParams
        ),
        *,
        timeout: float | None = None,
        message_spacing: float | None = None,
        connect_delay: float | None = None,
    ) -> None:
        self._params = params
        self._pacer = Pacer(message_spacing or 0.0)
        # What the caller asked the connection for; None where it asked for
        # nothing.
        self._base_timeout = timeout
        self._base_connect_delay = connect_delay
        self._unit_timeouts: dict[int, float] = {}
        self._unit_connect_delays: dict[int, float] = {}
        self._timeout = _DEFAULT_TIMEOUT if timeout is None else timeout
        self._connect_delay = connect_delay or 0.0
        # The timeout the live (or in-flight) backend client carries. It is
        # built with the value, so raising it needs a new client.
        self._client_timeout = self._timeout
        self._lost_callbacks = CallbackRegistry()
        self._target = _target(params)
        self._closed = False
        # The single in-flight connect attempt shared by concurrent callers.
        self._connect_task: asyncio.Task[None] | None = None
        # The connected backend client; ``None`` whenever the link is down (not
        # yet connected, dropped, or closed).
        self._client: Any = None

    @property
    def connected(self) -> bool:
        return self._client is not None

    async def connect(self) -> None:
        """Establish the connection; a no-op if already connected.

        Raises ``ModbusConnectionError`` if the connection fails and
        ``ClientClosedError`` if the connection was closed.
        """
        if self._closed:
            raise ClientClosedError("connection is closed")
        if self._client is not None:
            return
        task = self._connect_task
        if task is None:
            task = self._connect_task = asyncio.create_task(self._do_connect())
            task.add_done_callback(self._connect_done)
        await asyncio.shield(task)

    def _connect_done(self, task: asyncio.Task[None]) -> None:
        """Clear a completed connect flight and consume an unobserved failure."""
        if self._connect_task is task:
            self._connect_task = None
        if not task.cancelled():
            task.exception()

    async def _do_connect(self) -> None:
        self._client_timeout = self._timeout
        client = await self._connect_client()
        if self._connect_delay:
            # Some devices need a pause after the link opens before they answer
            # reliably. Inside the shared flight, so concurrent callers all wait
            # it out rather than racing a half-ready device.
            await asyncio.sleep(self._connect_delay)
        if self._closed:
            # A concurrent close() marked the connection closed while this
            # client was still being established; dispose of it and refuse.
            try:
                await self._close_client(client)
            except Exception:
                pass
            raise ClientClosedError("connection is closed")
        self._client = client

    @abstractmethod
    def for_unit(self, unit_id: int) -> ModbusUnit:
        """Return this backend's unit handle bound to ``unit_id``."""

    def on_connection_lost(self, callback: Callable[[], None]) -> Callable[[], None]:
        """Register a callback fired when the link drops; returns an unsubscribe."""
        return self._lost_callbacks.subscribe(callback)

    def _require_timeout(self, unit_id: int, seconds: float | None) -> None:
        """Raise the link's timeout to at least ``seconds`` for ``unit_id``."""
        if seconds is not None and seconds < 0:
            raise ValueError("timeout must be non-negative")
        _record(self._unit_timeouts, unit_id, seconds)
        self._timeout = _resolved(
            self._base_timeout, self._unit_timeouts, _DEFAULT_TIMEOUT
        )
        if self._timeout > self._client_timeout and (
            self._client is not None or self._connect_task is not None
        ):
            # A relaxed timeout can wait for the next connect. A raised one
            # cannot: the unit that needs it would go on giving up early.
            task = asyncio.create_task(self.disconnect())
            task.add_done_callback(_consume_failure)

    def _require_connect_delay(self, unit_id: int, seconds: float | None) -> None:
        """Raise the link's connect delay to at least ``seconds`` for ``unit_id``."""
        if seconds is not None and seconds < 0:
            raise ValueError("connect_delay must be non-negative")
        _record(self._unit_connect_delays, unit_id, seconds)
        self._connect_delay = _resolved(
            self._base_connect_delay, self._unit_connect_delays, 0.0
        )

    async def disconnect(self) -> None:
        """Drop the link; the next request establishes a new one.

        Use it to recycle a link that is up but unusable, such as a peer that
        keeps the socket open but stops answering. Unlike ``close()``, the
        connection stays usable: existing unit handles and components
        reconnect on their next request. A connection is lost when the
        transport takes it away. This is the owner tearing it down, so
        ``on_connection_lost`` callbacks do not fire. A no-op when there is no
        link.

        Waits up to ``_TEARDOWN_GRACE`` for a request that is about to answer.
        A wedged one is cut. Raises ``ModbusConnectionError`` if tearing the
        old link down fails. The link is dropped regardless.
        """
        if (task := self._connect_task) is not None:
            # Wait a shared connect attempt out so its client is published and
            # disposed of here rather than leaked. Shielded so cancelling this
            # teardown does not kill the flight for concurrent connect() callers.
            try:
                await asyncio.shield(task)
            except Exception:
                pass
        async with self._pacer.exclusive(_TEARDOWN_GRACE):
            client = self._client
            if client is None:
                return
            self._client = None
            await self._close_client(client)

    async def close(self) -> None:
        """Close the connection permanently.

        The connection is marked closed first, so no further request can
        start. The link is then dropped as in ``disconnect()``: waits up to
        ``_TEARDOWN_GRACE`` for a request that is about to answer, cuts a
        wedged one, and does not fire ``on_connection_lost`` callbacks.
        """
        self._closed = True
        await self.disconnect()

    # -- backend hooks ----------------------------------------------------------

    @abstractmethod
    async def _connect_client(self) -> Any:
        """Build and connect a client."""

    @abstractmethod
    async def _close_client(self, client: Any) -> None:
        """Close a client."""
