"""Build command-line tools that query modelled devices."""

from __future__ import annotations

import argparse
import importlib
import inspect
import sys
from collections.abc import Callable, Iterable
from enum import Flag, IntEnum
from typing import TYPE_CHECKING

from ._client import BaseModbusConnection
from ._protocol import ModbusUnit
from .exceptions import ModbusError
from .model import (
    CoilField,
    Component,
    DiscreteInputField,
    ManualComponent,
    RegisterField,
    RepeatingGroupField,
)

if TYPE_CHECKING:
    from types import ModuleType
    from typing import TextIO

__all__ = [
    "CountingUnit",
    "add_connection_args",
    "connect_from_args",
    "field_rows",
    "group_rows",
    "print_component",
]

# The framings each transport accepts. A framer of ``None`` means "no framing
# choice", which is the backend default (and the only option for TLS).
_FRAMERS = ("socket", "rtu", "ascii")
_TRANSPORT_FRAMERS: dict[str, tuple[str, ...]] = {
    "tcp": _FRAMERS,
    "udp": _FRAMERS,
    "tls": (),
    "serial": ("rtu", "ascii"),
}
# What a tool reaches for when it says nothing. A caller wanting UDP, TLS or
# ASCII passes it to ``add_connection_args``.
_DEFAULT_CONNECTIONS: tuple[tuple[str, str | None], ...] = (
    ("tcp", None),
    ("serial", None),
)


# -- connection from arguments -----------------------------------------------


def _import_backend(name: str) -> ModuleType | None:
    """Return an optional backend's connect surface."""
    try:
        return importlib.import_module(f".{name}", __package__)
    except ImportError:
        return None


def _load_backend(transport: str, framer: str | None) -> ModuleType:
    """Return an installed backend for the requested connection.

    Raises ``ModbusError`` if no installed backend supports the request.
    """
    tmodbus_supported = not (transport == "tcp" and framer == "ascii") and not (
        transport == "udp" and framer in ("rtu", "ascii")
    )
    if tmodbus_supported and (backend := _import_backend("tmodbus")) is not None:
        return backend
    if (backend := _import_backend("pymodbus")) is not None:
        return backend

    if tmodbus_supported:
        detail = "install the 'tmodbus' or 'pymodbus' extra"
    else:
        detail = (
            f"{transport} with {framer or 'default'} framing requires pymodbus; "
            "install the 'pymodbus' extra"
        )
    raise ModbusError(f"no installed Modbus backend supports this connection; {detail}")


class _TransportAction(argparse.Action):
    """Store ``--transport`` and set the framer that transport is fixed to."""

    def __init__(
        self, *args: object, framers: dict[str, str | None], **kwargs: object
    ) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self._framers = framers

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: object,
        option_string: str | None = None,
    ) -> None:
        setattr(namespace, self.dest, values)
        if values in self._framers:
            namespace.framer = self._framers[values]  # type: ignore[index]


def add_connection_args(
    parser: argparse.ArgumentParser,
    *,
    connections: Iterable[tuple[str, str | None]] = _DEFAULT_CONNECTIONS,
) -> argparse._ArgumentGroup:
    """Add the connection-specifying arguments to *parser*.

    Raises ``ValueError`` for an empty or invalid connection set.
    """
    pairs = tuple(connections)
    if not pairs:
        raise ValueError("connections must be non-empty")
    for transport, framer in pairs:
        if transport not in _TRANSPORT_FRAMERS:
            raise ValueError(
                f"unknown transport {transport!r}; expected one of "
                f"{tuple(_TRANSPORT_FRAMERS)}"
            )
        if framer is not None and framer not in _TRANSPORT_FRAMERS[transport]:
            raise ValueError(
                f"framer {framer!r} is not valid for transport {transport!r}"
            )

    transports = tuple(dict.fromkeys(t for t, _ in pairs))
    chosen_framers = {f for _, f in pairs if f is not None}
    framer_choices = tuple(f for f in _FRAMERS if f in chosen_framers)
    # A lone named framer applies only to the transports whose pairs name it.
    # The other transports keep the backend default.
    fixed_framers: dict[str, str | None] = {}
    if len(framer_choices) == 1:
        framed = {t for t, f in pairs if f is not None}
        fixed_framers = {
            t: framer_choices[0] if t in framed else None for t in transports
        }

    network = any(t in ("tcp", "udp") for t in transports)
    serial_ok = "serial" in transports
    tls_ok = "tls" in transports

    # What a target may look like, for the transports offered. The
    # serial one takes a URL as well as a port path, which is how it reaches a
    # serial server, so a reader should not have to find that out elsewhere.
    net_names = [t for t in ("tcp", "udp", "tls") if t in transports]
    serial_help = "a serial port or URL (/dev/ttyUSB0, socket://192.168.1.50:8899)"
    if net_names and serial_ok:
        target_help = (
            f"host or IP for {'/'.join(net_names)} (192.168.1.50), or {serial_help}"
        )
    elif serial_ok:
        target_help = serial_help
    else:
        target_help = "host or IP of the device (192.168.1.50)"

    primary = transports[0]
    group = parser.add_argument_group("Modbus connection")
    group.add_argument("target", help=target_help)
    if len(transports) > 1:
        group.add_argument(
            "--transport",
            choices=transports,
            default=primary,
            action=_TransportAction,
            framers=fixed_framers,
            help=f"wire transport (default: {primary})",
        )
    else:
        parser.set_defaults(transport=primary)
    if network or tls_ok:
        # Name only the transports on offer, and the default that follows.
        if net_names == ["tls"]:
            port_help = "TLS port (default: 802)"
        elif "tls" in net_names:
            port_help = (
                f"{'/'.join(n.upper() for n in net_names)} port "
                "(default: 502 for tcp/udp, 802 for tls)"
            )
        else:
            port_help = f"{'/'.join(n.upper() for n in net_names)} port (default: 502)"
        group.add_argument("--port", type=int, default=None, help=port_help)
    if len(framer_choices) > 1:
        group.add_argument(
            "--framer",
            choices=framer_choices,
            default=None,
            help="wire framing (backend default if unset)",
        )
    elif fixed_framers:
        parser.set_defaults(framer=fixed_framers[primary])
    group.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="per-request timeout in seconds (default: 10, or what a device asks)",
    )

    if serial_ok:
        serial = parser.add_argument_group("Modbus serial")
        serial.add_argument("--baudrate", type=int, default=9600)
        serial.add_argument("--bytesize", type=int, choices=(7, 8), default=8)
        serial.add_argument("--parity", choices=("N", "E", "O"), default="N")
        serial.add_argument("--stopbits", type=int, choices=(1, 2), default=1)

    if tls_ok:
        tls = parser.add_argument_group("Modbus/TLS")
        tls.add_argument(
            "--tls-no-verify",
            action="store_true",
            help="do not verify the server certificate (self-signed devices)",
        )
        tls.add_argument(
            "--tls-ca",
            default=None,
            help="verify against this CA bundle file or directory instead",
        )
        tls.add_argument(
            "--tls-no-check-hostname",
            action="store_true",
            help="verify the certificate but not the hostname",
        )
        tls.add_argument("--tls-client-cert", default=None, help="client cert for mTLS")
        tls.add_argument("--tls-client-key", default=None, help="client key for mTLS")
        tls.add_argument("--tls-client-key-password", default=None)
    return group


async def connect_from_args(
    args: argparse.Namespace, *, message_spacing: float = 0.0
) -> BaseModbusConnection:
    """Open the connection described by ``args``.

    Raises ``ModbusError`` if no backend is available and
    ``ModbusConnectionError`` if the connection fails.
    """
    # Resolved lazily so the module (and --help) loads without any backend.
    common = {"timeout": args.timeout, "message_spacing": message_spacing}
    # port/framer may be omitted for a narrowed argument set (see
    # add_connection_args); fall back to the backend default.
    port = getattr(args, "port", None)
    framer = getattr(args, "framer", None)
    backend = _load_backend(args.transport, framer)

    if args.transport == "serial":
        return await backend.connect_serial(
            args.target,
            baudrate=args.baudrate,
            bytesize=args.bytesize,
            parity=args.parity,
            stopbits=args.stopbits,
            **({"framer": framer} if framer else {}),
            **common,
        )

    if args.transport == "tls":
        verify: bool | str
        if args.tls_no_verify:
            verify = False
        elif args.tls_ca:
            verify = args.tls_ca
        else:
            verify = True
        return await backend.connect_tls(
            args.target,
            verify=verify,
            check_hostname=not args.tls_no_check_hostname,
            client_cert=args.tls_client_cert,
            client_key=args.tls_client_key,
            client_key_password=args.tls_client_key_password,
            **({"port": port} if port is not None else {}),
            **common,
        )

    connect = backend.connect_udp if args.transport == "udp" else backend.connect_tcp
    return await connect(
        args.target,
        **({"port": port} if port is not None else {}),
        **({"framer": framer} if framer else {}),
        **common,
    )


# -- read counting -----------------------------------------------------------


class CountingUnit:
    """Count block reads made through a ``ModbusUnit``."""

    def __init__(self, unit: ModbusUnit) -> None:
        self._unit = unit
        self.reads = 0

    @property
    def connected(self) -> bool:
        return self._unit.connected

    # -- counted block reads --------------------------------------------------

    async def read_holding_registers(self, address: int, count: int) -> list[int]:
        self.reads += 1
        return await self._unit.read_holding_registers(address, count)

    async def read_input_registers(self, address: int, count: int) -> list[int]:
        self.reads += 1
        return await self._unit.read_input_registers(address, count)

    async def read_coils(self, address: int, count: int) -> list[bool]:
        self.reads += 1
        return await self._unit.read_coils(address, count)

    async def read_discrete_inputs(self, address: int, count: int) -> list[bool]:
        self.reads += 1
        return await self._unit.read_discrete_inputs(address, count)

    # -- delegated pass-through -----------------------------------------------

    async def write_register(self, address: int, value: int) -> None:
        await self._unit.write_register(address, value)

    async def write_registers(self, address: int, values: list[int]) -> None:
        await self._unit.write_registers(address, values)

    async def write_coil(self, address: int, value: bool) -> None:
        await self._unit.write_coil(address, value)

    async def write_coils(self, address: int, values: list[bool]) -> None:
        await self._unit.write_coils(address, values)

    async def read_exception_status(self) -> int:
        return await self._unit.read_exception_status()

    async def report_server_id(self) -> bytes:
        return await self._unit.report_server_id()

    async def mask_write_register(
        self, address: int, and_mask: int, or_mask: int
    ) -> None:
        await self._unit.mask_write_register(address, and_mask, or_mask)

    async def read_write_registers(
        self,
        read_address: int,
        read_count: int,
        write_address: int,
        write_values: list[int],
    ) -> list[int]:
        return await self._unit.read_write_registers(
            read_address, read_count, write_address, write_values
        )

    async def read_fifo_queue(self, address: int) -> list[int]:
        return await self._unit.read_fifo_queue(address)

    async def read_device_identification(self) -> dict[int, bytes]:
        return await self._unit.read_device_identification()

    async def read_file_record(self, file: int, record: int, length: int) -> list[int]:
        return await self._unit.read_file_record(file, record, length)

    async def write_file_record(
        self, file: int, record: int, values: list[int]
    ) -> None:
        await self._unit.write_file_record(file, record, values)

    async def diagnostics(self, sub_function: int, data: int = 0) -> int:
        return await self._unit.diagnostics(sub_function, data)

    async def get_comm_event_counter(self) -> tuple[bool, int]:
        return await self._unit.get_comm_event_counter()

    async def get_comm_event_log(self) -> bytes:
        return await self._unit.get_comm_event_log()

    def set_message_spacing(self, seconds: float) -> None:
        self._unit.set_message_spacing(seconds)

    def require_timeout(self, seconds: float | None) -> None:
        self._unit.require_timeout(seconds)

    def require_connect_delay(self, seconds: float | None) -> None:
        self._unit.require_connect_delay(seconds)

    def on_connection_lost(self, callback: Callable[[], None]) -> Callable[[], None]:
        return self._unit.on_connection_lost(callback)

    async def disconnect(self) -> None:
        await self._unit.disconnect()


# -- field reflection --------------------------------------------------------


def _format_flag(value: Flag) -> str:
    """Render a flag value as the lowercased names of the bits it has set.

    A ``flags()`` field decodes to an ``IntFlag``. That is a ``ReprEnum``
    whose ``__str__`` is ``int``'s, and not an ``IntEnum``, so the generic
    path would print a status or fault word as a bare number. An ``IntFlag``
    also keeps bits its type does not name. Those are reported as a hex
    remainder rather than dropped, so a fault word never hides a set bit. An
    empty flag renders as ``none``.
    """
    names: list[str] = []
    named_bits = 0
    for member in type(value):
        if member.name and member in value:
            names.append(member.name.lower())
            if isinstance(member, int):
                named_bits |= int(member)
    if isinstance(value, int) and (unnamed := int(value) & ~named_bits):
        names.append(f"0x{unnamed:x}")
    return "|".join(names) if names else "none"


def _format_value(value: object) -> str:
    """Render a decoded field value for display."""
    if value is None:
        return "—"
    if isinstance(value, Flag):
        return _format_flag(value)
    if isinstance(value, IntEnum):
        return value.name.lower()
    return str(value)


# What ``Component`` itself defines, which a device value never is.
_BASE_ATTRS = frozenset(dir(Component))


def _row(name: str, decoded: object, unit: str | None) -> tuple[str, str]:
    value = _format_value(decoded)
    # A field with no value carries no unit: "— °C" reads as a measurement
    # that came back empty, when nothing was measured at all.
    return (name, f"{value} {unit}" if unit and decoded is not None else value)


def field_rows(component: Component | ManualComponent) -> list[tuple[str, str]]:
    """Return display rows for every field ``component`` serves.

    A field ``restrict_fields`` dropped is left out rather than shown empty.
    """
    if isinstance(component, ManualComponent):
        return [
            _row(key, component.get(key), field.unit)
            for key, (field, _) in component._registers.items()
        ] + [_row(key, component.get(key), None) for key in component._bits]

    cls = type(component)
    served = set(component._register_fields) | set(component._bit_fields)
    rows: list[tuple[str, str]] = []
    for name in dir(component):
        if name.startswith("_") or name in _BASE_ATTRS:
            continue
        descriptor = inspect.getattr_static(cls, name, None)
        if isinstance(descriptor, (RegisterField, CoilField, DiscreteInputField)):
            if name not in served:
                continue
            unit = descriptor.unit if isinstance(descriptor, RegisterField) else None
        elif isinstance(descriptor, property):
            unit = None
        else:
            continue
        rows.append(_row(name, getattr(component, name), unit))
    return rows


def group_rows(
    component: Component | ManualComponent,
) -> list[tuple[str, list[Component]]]:
    """Return each ``repeating_group`` on ``component`` with its instances.

    An unread register-counted group has no instances yet and yields an empty
    list.
    """
    if isinstance(component, ManualComponent):
        return [
            (key, component.get(key))
            for key in (*component._static_groups, *component._repeating_fields)
        ]

    cls = type(component)
    groups: list[tuple[str, list[Component]]] = []
    for name in dir(component):
        if name.startswith("_") or name in _BASE_ATTRS:
            continue
        if isinstance(inspect.getattr_static(cls, name, None), RepeatingGroupField):
            groups.append((name, list(getattr(component, name))))
    return groups


def print_component(
    component: Component | ManualComponent,
    *,
    title: str | None = None,
    file: TextIO | None = None,
    indent: str = "",
) -> None:
    """Print every field on ``component`` under a heading.

    Each ``repeating_group``'s instances follow as indented sub-blocks, so a
    device modelled as repeated sub-units dumps in full. ``indent`` prefixes
    every line, for embedding the output in a wider report.
    """
    rows = field_rows(component)
    out = file if file is not None else sys.stdout
    heading = title if title is not None else type(component).__name__
    print(f"{indent}{heading}", file=out)
    print(f"{indent}{'-' * len(heading)}", file=out)
    width = max((len(name) for name, _ in rows), default=0)
    for name, value in rows:
        print(f"{indent}  {name.ljust(width)}  {value}", file=out)
    for name, instances in group_rows(component):
        for index, instance in enumerate(instances, start=1):
            print(file=out)
            print_component(
                instance,
                title=f"{name}[{index}]",
                file=out,
                indent=f"{indent}  ",
            )
