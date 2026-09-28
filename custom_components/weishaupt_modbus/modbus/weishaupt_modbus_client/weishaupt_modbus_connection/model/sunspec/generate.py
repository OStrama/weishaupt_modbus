"""Generate components from SunSpec model definitions."""

from __future__ import annotations

import argparse
import json
import keyword
import re
import sys
import textwrap
import urllib.request
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any

from ..component import Component
from . import SunSpecComponent

_MODEL_URL = (
    "https://raw.githubusercontent.com/sunspec/models/master/json/model_{model_id}.json"
)

# Point types emitted as a same-named numeric helper call.
_NUMERIC_TYPES = frozenset({"int16", "uint16", "int32", "uint32", "int64", "uint64"})
_ACC_TYPES = frozenset({"acc16", "acc32", "acc64"})
_ENUM_TYPES = frozenset({"enum16", "enum32"})
_BITFIELD_TYPES = frozenset({"bitfield16", "bitfield32", "bitfield64"})
_PLAIN_TYPES = frozenset(
    {"sunssf", "float32", "float64", "ipaddr", "ipv6addr", "eui48"}
)
# The point types _emit_point marks writable. A block write puts every register
# of the run on the wire, so it needs every field of the block to be one.
_WRITABLE_TYPES = _NUMERIC_TYPES | _ENUM_TYPES | _BITFIELD_TYPES | frozenset({"string"})

# Attribute names the generated classes must not shadow: everything the
# component base classes already define, plus the helper names the generated
# module imports at top level (a field named after a helper would break later
# fields in the same class body).
_RESERVED_ATTRS = frozenset(dir(Component)) | frozenset(dir(SunSpecComponent))


class SunSpecGenerationError(Exception):
    """A model definition cannot be expressed as a component layout."""


@dataclass
class _Point:
    """One point of a model group, placed at its model-relative address."""

    name: str
    type: str
    size: int
    address: int
    sf: str | int | None
    units: str | None
    writable: bool
    label: str | None
    desc: str | None
    symbols: list[tuple[str, int]]


def _snake(name: str) -> str:
    """Convert a SunSpec point name (``AphA``, ``DCA_SF``) to snake_case."""
    s = re.sub(r"[^0-9A-Za-z]+", "_", name)
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", s)
    s = re.sub(r"__+", "_", s).strip("_").lower()
    if not s or s[0].isdigit():
        s = f"p_{s}"
    if keyword.iskeyword(s):
        s += "_"
    return s


def _camel(name: str) -> str:
    """Convert a group or point name to a CamelCase class name."""
    parts = [p for p in re.split(r"[^0-9A-Za-z]+", name) if p]
    return "".join(p[:1].upper() + p[1:] for p in parts) or "Group"


def _member(name: str) -> str:
    """Sanitize a symbol name into a valid enum member name."""
    s = re.sub(r"[^0-9A-Za-z]+", "_", name).strip("_")
    if not s or s[0].isdigit():
        s = f"V_{s}"
    if keyword.iskeyword(s):
        s += "_"
    return s


def _attr_docstring(point: _Point) -> list[str]:
    """Return a point's attribute docstring."""
    parts: list[str] = []
    for text in (point.label, point.desc):
        if text:
            cleaned = " ".join(text.split()).rstrip(".")
            if cleaned and cleaned.lower() not in (p.lower() for p in parts):
                parts.append(cleaned)
    if not parts:
        return []
    text = ". ".join(parts).replace("\\", "\\\\") + "."
    lines = textwrap.wrap(text, width=78)
    if len(lines) == 1:
        return [f'    """{lines[0]}"""']
    return [
        f'    """{lines[0]}',
        *(f"    {line}" for line in lines[1:-1]),
        f'    {lines[-1]}"""',
    ]


def _parse_points(raw_points: list[Any], start: int) -> list[_Point]:
    """Assign consecutive model-relative addresses to a group's points."""
    points = []
    address = start
    for raw in raw_points:
        size = int(raw["size"])
        points.append(
            _Point(
                name=raw["name"],
                type=raw["type"],
                size=size,
                address=address,
                sf=raw.get("sf"),
                units=raw.get("units"),
                writable=raw.get("access") == "RW",
                label=raw.get("label"),
                desc=raw.get("desc"),
                symbols=[(s["name"], int(s["value"])) for s in raw.get("symbols", [])],
            )
        )
        address += size
    return points


class _ClassWriter:
    """Accumulates the body of one generated component class."""

    def __init__(self, name: str, base: str, docstring: str) -> None:
        self.name = name
        self.base = base
        self.docstring = docstring
        self.field_lines: list[str] = []
        self._attrs: dict[str, str] = {}
        self.attr_order: list[str] = []
        """Attributes claimed, in order; a leaf block's are exactly its fields."""

    def attr_name(self, point_name: str) -> str:
        """A unique, non-shadowing snake_case attribute for a point.

        The same point name always gets the same attribute, so a count point a
        stride refers to can be named before its field is emitted.
        """
        if (attr := self._attrs.get(point_name)) is not None:
            return attr
        attr = _snake(point_name)
        taken = set(self._attrs.values())
        while attr in _RESERVED_ATTRS or attr in taken:
            attr += "_"
        self._attrs[point_name] = attr
        self.attr_order.append(attr)
        return attr

    def add_field(self, lines: list[str]) -> None:
        """Append one field block, blank-line separated from the previous."""
        if self.field_lines:
            self.field_lines.append("")
        self.field_lines.extend(lines)

    def render(self) -> str:
        lines = [f"class {self.name}({self.base}):", f'    """{self.docstring}"""']
        if self.field_lines:
            lines.append("")
            lines.extend(self.field_lines)
        else:
            lines.append("")
            lines.append("    # This model defines no points beyond the header.")
        return "\n".join(lines)


class _ModuleWriter:
    """Accumulates the generated module: imports and rendered classes."""

    def __init__(self) -> None:
        self.enum_imports: set[str] = set()
        self.stdlib_imports: dict[str, set[str]] = {}
        self.model_imports: set[str] = set()
        self.sunspec_imports: set[str] = set()
        self.classes: list[str] = []
        self.sources: list[str] = []
        self.class_names: set[str] = set()
        self.enums: dict[str, tuple[str, tuple[tuple[str, int], ...]]] = {}
        self.enum_classes: list[str] = []
        self.helpers: list[str] = []
        """Module-level helper functions the generated classes rely on."""
        self.class_fields: dict[str, list[str]] = {}
        """Field attributes per generated class, for a block write's docstring."""

    def stdlib_import(self, module: str, *names: str) -> None:
        """Record a standard-library import the generated module needs."""
        self.stdlib_imports.setdefault(module, set()).update(names)

    def claim_enum(self, point: _Point, base: str, owner: str) -> str:
        """Emit an enum for a point and return its name."""
        symbols = tuple(point.symbols)
        content = (base, symbols)
        label = _camel(point.label) if point.label else ""
        first = label if label and not label[0].isdigit() else _camel(point.name)
        name = None
        for candidate in (first, f"{owner}{first}"):
            if self.enums.get(candidate) == content:
                return candidate
            if candidate not in self.class_names:
                name = candidate
                break
        if name is None:
            name = f"{owner}{first}"
            while name in self.class_names:
                name += "_"
        self.class_names.add(name)
        self.enums[name] = content
        lines = [f"class {name}({base}):"]
        for symbol, value in symbols:
            literal = f"1 << {value}" if base == "IntFlag" else str(value)
            lines.append(f"    {_member(symbol)} = {literal}")
        self.enum_classes.append("\n".join(lines))
        return name

    def claim_class(self, preferred: str, model_id: int | None = None) -> str:
        """Return a unique module-level class name."""
        name = preferred
        if name in self.class_names and model_id is not None:
            name = f"{preferred}{model_id}"
        while name in self.class_names:
            name += "_"
        self.class_names.add(name)
        return name

    def render(self) -> str:
        header = [
            '"""Provide generated SunSpec components."""',
            f"# Source: https://github.com/sunspec/models ({', '.join(self.sources)})",
            "",
            "from __future__ import annotations",
            "",
        ]
        stdlib = dict(self.stdlib_imports)
        if self.enum_imports:
            stdlib.setdefault("enum", set()).update(self.enum_imports)
        for module in sorted(stdlib):
            header.append(f"from {module} import {', '.join(sorted(stdlib[module]))}")
        if stdlib:
            header.append("")
        if self.model_imports:
            header.append(
                "from modbus_connection.model import "
                + ", ".join(sorted(self.model_imports))
            )
        names = sorted(self.sunspec_imports)
        header.append("from modbus_connection.model.sunspec import (")
        header.extend(f"    {name}," for name in names)
        header.append(")")
        # Helpers and enums first: the component class bodies reference them.
        blocks = self.helpers + self.enum_classes + self.classes
        return "\n".join(header) + "\n\n\n" + "\n\n\n".join(blocks) + "\n"


def _emit_point(
    point: _Point,
    writer: _ClassWriter,
    module: _ModuleWriter,
    scale_addresses: Mapping[str, int],
    model_id: int,
) -> None:
    """Append one point's field (and enum class, if any) to its class body."""
    attr = writer.attr_name(point.name)
    args = [str(point.address)]
    kwargs: list[str] = []
    if point.type in _NUMERIC_TYPES or point.type in _ACC_TYPES:
        helper = point.type
        if isinstance(point.sf, str):
            if point.sf not in scale_addresses:
                raise SunSpecGenerationError(
                    f"model {model_id}: point {point.name} references scale"
                    f" factor {point.sf}, which is not in the fixed block or"
                    " its own group"
                )
            kwargs.append(f"scale_register={scale_addresses[point.sf]}")
        elif isinstance(point.sf, int):
            kwargs.append(f"scale={10.0**point.sf!r}")
        if point.writable and point.type in _NUMERIC_TYPES:
            kwargs.append("writable=True")
        if point.units is not None:
            kwargs.append(f"unit={point.units!r}")
    elif point.type in _ENUM_TYPES or point.type in _BITFIELD_TYPES:
        helper = point.type
        if point.symbols:
            enum_base = "IntFlag" if point.type in _BITFIELD_TYPES else "IntEnum"
            module.enum_imports.add(enum_base)
            args.append(module.claim_enum(point, enum_base, writer.name))
        if point.writable:
            kwargs.append("writable=True")
    elif point.type == "string":
        helper = "string"
        args.append(str(point.size))
        if point.writable:
            kwargs.append("writable=True")
    elif point.type == "count":
        # The repeat-count point; also read from repeating_group, see below.
        helper = "uint16"
    elif point.type in _PLAIN_TYPES:
        helper = point.type
        if point.writable and point.type in ("float32", "float64"):
            kwargs.append("writable=True")
        if point.units is not None and point.type in ("float32", "float64"):
            kwargs.append(f"unit={point.units!r}")
    else:
        raise SunSpecGenerationError(
            f"model {model_id}: point {point.name} has unsupported type {point.type!r}"
        )
    module.sunspec_imports.add(helper)
    call = f"{helper}({', '.join(args + kwargs)})"
    writer.add_field([f"    {attr} = {call}", *_attr_docstring(point)])


def _emitted(point: _Point, referenced_sf: frozenset[str]) -> bool:
    """Return whether a point becomes its own field."""
    if point.type == "pad":
        return False
    if point.type == "sunssf" and point.name in referenced_sf:
        return False
    return True


@dataclass
class _Group:
    """One (possibly nested) block of a model, placed at its instance-0 offset."""

    name: str
    start: int
    raw_count: Any  # int, or the name of the point holding the repeat count
    points: list[_Point]
    children: list[_Group]
    size: int | None  # fixed registers per instance; None when unknowable
    # registers per instance on top of ``size``, per count point of the
    # model's fixed block: a curve of NPt two-register points has {"NPt": 2}
    terms: dict[str, int] = field(default_factory=dict)
    # the names of same-shaped sibling blocks this one stands for (see
    # ``_parse_group``); a property per name indexes the repeated block
    aliases: list[str] = field(default_factory=list)


def _fixed_count(raw_count: Any) -> int | None:
    """The statically-known repeat count, or None for a device-sized block."""
    if isinstance(raw_count, int) and raw_count > 0:
        return raw_count
    return None


def _referenced_scale_factors(group: _Group) -> set[str]:
    """Names of every ``sunssf`` point that some point references via ``sf``."""
    names = {p.sf for p in group.points if isinstance(p.sf, str)}
    for child in group.children:
        names |= _referenced_scale_factors(child)
    return names


def _count_names(raw: Mapping[str, Any]) -> set[str]:
    """Names of every point a block or its children is repeated by."""
    names = {raw["count"]} if isinstance(raw.get("count"), str) else set()
    for sub in raw.get("groups", []):
        names |= _count_names(sub)
    return names


def _shape(raw: Mapping[str, Any]) -> Any:
    """A block's layout, to tell a same-shaped sibling from a different block."""
    return (
        raw.get("count", 1),
        tuple(
            (p["name"], p["type"], int(p["size"]), p.get("sf"))
            for p in raw.get("points", [])
        ),
        tuple(_shape(sub) for sub in raw.get("groups", [])),
    )


def _parse_group(
    raw: Mapping[str, Any], start: int, model_id: int, counts: Mapping[str, int]
) -> _Group:
    """Place a block's points and nested blocks.

    ``counts`` supplies a value for a count point the device would otherwise
    report at poll time, which makes the block it sizes a fixed-count repeat.

    A device-sized block has no fixed size, so nothing can follow it except
    same-shaped blocks, which collapse into one repeat of it. The trip models
    put three such regions in each curve.
    """
    points = _parse_points(raw.get("points", []), start)
    offset = start + sum(p.size for p in points)
    children: list[_Group] = []
    size: int | None = offset - start
    terms: dict[str, int] = {}
    subs = list(raw.get("groups", []))
    while subs:
        if size is None or terms:
            raise SunSpecGenerationError(
                f"model {model_id}: group {children[-1].name!r} has a"
                " device-dependent size but is not the last block, so later"
                " addresses are unknown"
            )
        sub = subs.pop(0)
        child = _parse_group(sub, offset, model_id, counts)
        count = _fixed_count(child.raw_count)
        if count is not None and child.terms:
            aliases = [child.name]
            while subs and _shape(subs[0]) == _shape(sub):
                aliases.append(subs.pop(0)["name"])
            if len(aliases) > 1:
                count *= len(aliases)
                child = replace(child, name="region", raw_count=count, aliases=aliases)
        children.append(child)
        if child.size is None:
            size = None
        elif count is None:
            if isinstance(child.raw_count, str) and not child.terms:
                terms[child.raw_count] = terms.get(child.raw_count, 0) + child.size
            else:
                # a count of 0 fills the model length; a device count of
                # device-sized blocks is a product no stride expresses
                size = None
        else:
            offset += count * child.size
            size = offset - start
            for name, registers in child.terms.items():
                terms[name] = terms.get(name, 0) + count * registers
    raw_count = raw.get("count", 1)
    if isinstance(raw_count, str):
        raw_count = counts.get(raw_count, raw_count)
    return _Group(raw.get("name", ""), start, raw_count, points, children, size, terms)


def _count_expression(
    raw_count: Any,
    scopes: list[_Group],
    module: _ModuleWriter,
    model_id: int,
    group_name: str,
) -> tuple[str, bool] | None:
    """Return a repeated block's count expression and whether it is in-block.

    A count point of the enclosing block moves with that block's instances. One
    in the model's fixed block stays put whatever block it sizes.

    Raises ``SunSpecGenerationError`` for an unknown count point, or one in a
    repeated block between the two.
    """
    if isinstance(raw_count, str):
        for scope, in_block in ((scopes[-1], True), (scopes[0], False)):
            for point in scope.points:
                if point.name == raw_count:
                    module.sunspec_imports.add("uint16")
                    return f"uint16({point.address})", in_block
        if any(point.name == raw_count for scope in scopes for point in scope.points):
            raise SunSpecGenerationError(
                f"model {model_id}: group {group_name} count references point"
                f" {raw_count!r} in an enclosing repeated block, which has a"
                " different address per instance"
            )
        raise SunSpecGenerationError(
            f"model {model_id}: group {group_name} count references point"
            f" {raw_count!r}, which is not defined in the model"
        )
    count = int(raw_count)
    if count > 0:
        return str(count), True
    count_points = [p for p in scopes[-1].points if p.type == "count"]
    if len(count_points) == 1:
        module.sunspec_imports.add("uint16")
        return f"uint16({count_points[0].address})", True
    return None


def _stride_expression(child: _Group, count_attrs: Mapping[str, str]) -> str | None:
    """A repeated block's stride: an int, or a lambda over the model's counts."""
    if child.size is None:
        return None
    if not child.terms:
        return str(child.size)
    parts = [str(child.size)] if child.size else []
    for name, registers in child.terms.items():
        attr = f"m.{count_attrs[name]}"
        parts.append(attr if registers == 1 else f"{registers} * {attr}")
    return f"lambda m: {' + '.join(parts)}"


# Emitted once into a module that has at least one all-writable repeated block.
# A curve is a run of writable points a device expects whole, and writing it a
# field at a time costs a request each, plus a read of the scale register before
# every scaled write. The generator only calls this for blocks it has already
# checked are gapless and writable throughout, so the helper itself does not
# re-derive that.
_WRITE_BLOCK_HELPER = '''\
async def write_block(
    component: Component, group: str, values: Sequence[Mapping[str, Any]]
) -> None:
    """Write the leading instances of a repeated block in one request.

    ``values`` holds one mapping per instance, keyed by that instance's field
    names, and has to set every field of each instance it covers: the write
    puts a whole run of registers on the wire, so a field left out would be
    written with a value nobody chose. Instances past ``values`` are untouched.

    Each scale register is read once for the whole block rather than once per
    field, so a four-point curve costs one write and two reads instead of
    eight of each.
    """
    instances = getattr(component, group)
    if len(values) > len(instances):
        raise IndexError(
            f"{group!r} has {len(instances)} instance(s),"
            f" got {len(values)} set(s) of values"
        )
    targets = [
        (resolved, mapping[name])
        for instance, mapping in zip(instances, values, strict=False)
        for name, resolved in instance.resolved_fields.items()
    ]
    targets.sort(key=lambda target: target[0].address)

    unit = component.modbus_unit
    exponents: dict[int, int] = {}
    for resolved, _value in targets:
        address = resolved.scale_address
        if address is not None and address not in exponents:
            (word,) = await unit.read_holding_registers(address, 1)
            exponents[address] = word - 0x10000 if word & 0x8000 else word

    words: list[int] = []
    for resolved, value in targets:
        address = resolved.scale_address
        words += resolved.field.encode(
            value, None if address is None else exponents[address]
        )
    await unit.write_registers(targets[0][0].address, words)'''


def _block_writable(group: _Group, referenced_sf: frozenset[str]) -> bool:
    """Whether every field of one instance of this block can be written.

    A block write covers a gapless run of registers, so a block with a nested
    block, a read-only point or a point type that is never writable (a scale
    factor, an accumulator) cannot be written that way.
    """
    emitted = [point for point in group.points if _emitted(point, referenced_sf)]
    return (
        not group.children
        and bool(emitted)
        and all(point.writable and point.type in _WRITABLE_TYPES for point in emitted)
    )


def _claim_write_block(module: _ModuleWriter) -> None:
    """Emit the shared block-write helper, once per module."""
    if module.helpers:
        return
    module.helpers.append(_WRITE_BLOCK_HELPER)
    module.model_imports.add("Component")
    module.stdlib_import("collections.abc", "Mapping", "Sequence")
    module.stdlib_import("typing", "Any")


def _block_write_method(
    child: _Group,
    child_class: str,
    attr: str,
    writer: _ClassWriter,
    module: _ModuleWriter,
) -> list[str]:
    """Emit the method that writes a whole repeated block, on its owner.

    Named after the block, because one class can own several writable blocks
    (model 704 owns four) and each needs its own method.
    """
    fields = module.class_fields.get(child_class, [])
    method = writer.attr_name(f"write_{attr}")
    return [
        f"    async def {method}(self, values: Sequence[Mapping[str, Any]]) -> None:",
        f'        """Write consecutive {child.name!r} instances in one request.',
        "",
        "        Each mapping sets one instance and must set every field:",
        f"        {', '.join(fields)}. Instances past ``values`` are untouched.",
        '        """',
        f'        await write_block(self, "{attr}", values)',
    ]


def _wire_child(
    child: _Group,
    child_class: str,
    scopes: list[_Group],
    writer: _ClassWriter,
    module: _ModuleWriter,
    model_id: int,
    referenced_sf: frozenset[str],
    count_attrs: Mapping[str, str],
) -> list[str]:
    """Emit the parent field for a nested block.

    Raises ``SunSpecGenerationError`` for a block whose stride no expression
    over the model's count points gives.
    """
    attr = writer.attr_name(child.name)
    counted = _count_expression(child.raw_count, scopes, module, model_id, child.name)
    if counted is None:
        if len(scopes) != 1 or not child.size or child.terms:
            # A nested block does not own the remainder of the model. Its
            # enclosing block's length must be known before it can be sized.
            return [
                f"    # {child.name!r} repeats to fill the model length and"
                " defines no count",
                "    # point; size it from the scanned model.length:",
                f"    # {attr} = repeating_group(N, {child_class},"
                f" stride={child.size})",
            ]
        module.sunspec_imports.add("model_length_group")
        call = (
            f"model_length_group({child_class}, start={child.start},"
            f" stride={child.size})"
        )
    else:
        stride = _stride_expression(child, count_attrs)
        if stride is None:
            raise SunSpecGenerationError(
                f"model {model_id}: group {child.name} repeats a block whose size is"
                " not a fixed number of registers plus multiples of the model's"
                " count points"
            )
        count_expr, in_block = counted
        module.model_imports.add("repeating_group")
        args = [count_expr, child_class, f"stride={stride}"]
        if not in_block:
            args.append("count_in_block=False")
        call = f"repeating_group({', '.join(args)})"
    lines = [f"    {attr} = {call}"]
    for index, name in enumerate(child.aliases):
        lines += [
            "",
            "    @property",
            f"    def {writer.attr_name(name)}(self) -> {child_class}:",
            f'        """The {name!r} block."""',
            f"        return self.{attr}[{index}]",
        ]
    if _block_writable(child, referenced_sf):
        _claim_write_block(module)
        lines.append("")
        lines += _block_write_method(child, child_class, attr, writer, module)
    return lines


def _block_scales(
    group: _Group,
    top_scales: Mapping[str, int],
    model_id: int,
    scopes: list[_Group],
) -> tuple[Mapping[str, int], bool]:
    """Return the scale-factor scope of a repeated block.

    Raises ``SunSpecGenerationError`` for incompatible scale-factor scopes.
    """
    own_scales = {p.name: p.address for p in group.points if p.type == "sunssf"}
    in_block = fixed = False
    for point in group.points:
        if not isinstance(point.sf, str):
            continue
        if point.sf in own_scales:
            in_block = True
        elif point.sf in top_scales:
            fixed = True
        elif any(
            p.name == point.sf and p.type == "sunssf"
            for scope in scopes[1:]
            for p in scope.points
        ):
            raise SunSpecGenerationError(
                f"model {model_id}: point {point.name} references scale"
                f" factor {point.sf} in an enclosing repeating block, which"
                " shifts with neither the model nor this block's instances"
            )
    if in_block and fixed:
        raise SunSpecGenerationError(
            f"model {model_id}: group {group.name} mixes in-block and"
            " fixed-block scale factors, which one class cannot express"
        )
    return (own_scales, True) if in_block else (top_scales, False)


def _emit_group_class(
    group: _Group,
    prefix: str,
    module: _ModuleWriter,
    top_scales: Mapping[str, int],
    model_id: int,
    scopes: list[_Group],
    referenced_sf: frozenset[str],
    count_attrs: Mapping[str, str],
) -> str:
    """Emit one block's ``Component`` class (children first); return its name."""
    class_name = module.claim_class(f"{prefix}{_camel(group.name)}")
    writer = _ClassWriter(
        class_name,
        "Component",
        f"One {group.name!r} block of SunSpec model {model_id}.",
    )
    module.model_imports.add("Component")
    wiring: list[list[str]] = []
    for child in group.children:
        child_class = _emit_group_class(
            child,
            class_name,
            module,
            top_scales,
            model_id,
            [*scopes, group],
            referenced_sf,
            count_attrs,
        )
        wiring.append(
            _wire_child(
                child,
                child_class,
                [*scopes, group],
                writer,
                module,
                model_id,
                referenced_sf,
                count_attrs,
            )
        )
    scale_addresses, scale_in_block = _block_scales(group, top_scales, model_id, scopes)
    if scale_in_block:
        writer.add_field(
            ["    scale_in_block = True  # each instance carries its own scale factors"]
        )
    for point in group.points:
        if _emitted(point, referenced_sf):
            _emit_point(point, writer, module, scale_addresses, model_id)
    for block in wiring:
        writer.add_field(block)
    module.classes.append(writer.render())
    # Recorded before the parent wires this block up, so a block-write method
    # on the parent can name the fields each mapping has to set.
    module.class_fields[class_name] = list(writer.attr_order)
    return class_name


def _generate_model(
    model: Mapping[str, Any], module: _ModuleWriter, counts: Mapping[str, int]
) -> None:
    """Append one model's classes (innermost blocks first) to the module."""
    model_id = int(model["id"])
    module.sources.append(f"json/model_{model_id}.json")

    unknown = set(counts) - _count_names(model["group"])
    if unknown:
        raise SunSpecGenerationError(
            f"model {model_id}: no group is repeated by {', '.join(sorted(unknown))}"
        )
    top = _parse_group(model["group"], 0, model_id, counts)
    # ID and L are the model header; SunSpecComponent already declares them
    # (model_id / model_length at 0 and 1), so they are parsed for the address
    # walk but not emitted.
    data_points = [p for p in top.points if p.name not in ("ID", "L")]
    scale_addresses = {p.name: p.address for p in top.points if p.type == "sunssf"}

    label = model["group"].get("label") or top.name
    class_name = module.claim_class(
        _camel(top.name) if top.name else f"Model{model_id}", model_id
    )
    writer = _ClassWriter(
        class_name, "SunSpecComponent", f"SunSpec model {model_id}: {label}."
    )
    module.sunspec_imports.add("SunSpecComponent")

    referenced_sf = frozenset(_referenced_scale_factors(top))
    # A callable stride reads a count point off the model instance, so the
    # count points' attributes are named before the blocks that use them.
    count_names = _count_names(model["group"])
    count_attrs = {
        p.name: writer.attr_name(p.name) for p in data_points if p.name in count_names
    }
    wiring: list[list[str]] = []
    for child in top.children:
        child_class = _emit_group_class(
            child,
            class_name,
            module,
            scale_addresses,
            model_id,
            [top],
            referenced_sf,
            count_attrs,
        )
        wiring.append(
            _wire_child(
                child,
                child_class,
                [top],
                writer,
                module,
                model_id,
                referenced_sf,
                count_attrs,
            )
        )
    for point in data_points:
        if _emitted(point, referenced_sf):
            _emit_point(point, writer, module, scale_addresses, model_id)
    for block in wiring:
        writer.add_field(block)
    module.classes.append(writer.render())


def generate_source(
    models: Iterable[Mapping[str, Any]],
    counts: Mapping[int, Mapping[str, int]] | None = None,
) -> str:
    """Render parsed SunSpec model JSON into a Python module's source.

    ``counts`` maps a model ID to the values of its count points, read from
    the device the generated classes target. A block sized by one of them is
    emitted as a fixed-count ``repeating_group`` instead of one sized at poll
    time.
    """
    module = _ModuleWriter()
    counts = counts or {}
    for model in models:
        _generate_model(model, module, counts.get(int(model["id"]), {}))
    if not module.classes:
        raise SunSpecGenerationError("no models given")
    return module.render()


def _load(spec: str) -> Any:
    """Load one model: a numeric ID (fetched from GitHub) or a local path."""
    if spec.isdigit():
        url = _MODEL_URL.format(model_id=int(spec))
        with urllib.request.urlopen(url) as response:
            return json.load(response)
    with open(spec, encoding="utf-8") as file:
        return json.load(file)


def _parse_count(spec: str) -> tuple[int, str, int]:
    """Parse a ``MODEL:POINT=N`` count override."""
    model, _, rest = spec.partition(":")
    point, sep, value = rest.partition("=")
    if not (model.isdigit() and point and sep and value.isdigit()):
        raise argparse.ArgumentTypeError(f"expected MODEL:POINT=N, got {spec!r}")
    if int(value) < 1:
        raise argparse.ArgumentTypeError(f"count must be 1 or more, got {spec!r}")
    return int(model), point, int(value)


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        prog="python -m modbus_connection.model.sunspec.generate",
        description=(
            "Generate typed SunSpec components from the official model"
            " definitions (https://github.com/sunspec/models)."
        ),
    )
    parser.add_argument(
        "models",
        nargs="+",
        help="SunSpec model IDs (fetched from the official repository)"
        " or paths to local model_N.json files",
    )
    parser.add_argument(
        "-o",
        "--out",
        help="write the generated module here instead of stdout",
    )
    parser.add_argument(
        "--count",
        action="append",
        default=[],
        type=_parse_count,
        metavar="MODEL:POINT=N",
        help="the value a count point holds on the target device, e.g."
        " --count 705:NCrv=3; the block it sizes is then emitted as a"
        " fixed-count repeating_group instead of one sized at poll time."
        " Repeatable.",
    )
    options = parser.parse_args(argv)
    counts: dict[int, dict[str, int]] = {}
    for model_id, point, value in options.count:
        counts.setdefault(model_id, {})[point] = value
    try:
        source = generate_source((_load(spec) for spec in options.models), counts)
    except (OSError, SunSpecGenerationError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    if options.out:
        with open(options.out, "w", encoding="utf-8") as file:
            file.write(source)
    else:
        sys.stdout.write(source)
    return 0


if __name__ == "__main__":
    sys.exit(main())
