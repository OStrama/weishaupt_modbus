"""SunSpec model-chain scanning."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from ...decode import decode_uint32
from .errors import SunSpecError

if TYPE_CHECKING:
    from ..._protocol import ModbusUnit

_SUNSPEC_MARKER: Final = 0x53756E53  # "SunS"
_END_MODEL_ID: Final = 0xFFFF
# Sanity limit against malformed maps sending the chain walk astray.
_MAX_MODELS: Final = 100


@dataclass(frozen=True)
class SunSpecModel:
    """Locate a SunSpec model in the register map."""

    model_id: int
    address: int

    length: int
    """Data length from the header, excluding it; see ``span`` for the block."""

    @property
    def span(self) -> int:
        """Registers the whole block occupies: the two header words plus data.

        This is what a read of the model takes as its count, and the step to
        the next model's header.
        """
        return self.length + 2


class SunSpecModels(dict[int, list[SunSpecModel]]):
    """The discovered models by ID, a plain dict with lookup helpers."""

    @property
    def chain(self) -> list[SunSpecModel]:
        """Return every discovered model in chain order.

        A device may repeat a model ID. Their place in the chain separates the
        repeats: a meter's identity block is the ``1`` that precedes it,
        whichever meter model follows.
        """
        return sorted(
            (model for found in self.values() for model in found),
            key=lambda model: model.address,
        )

    def at(self, address: int) -> SunSpecModel | None:
        """Return the model whose header sits at ``address``, or ``None``."""
        for found in self.values():
            for model in found:
                if model.address == address:
                    return model
        return None

    def first(self, *model_ids: int) -> SunSpecModel | None:
        """Return the first discovered model among ``model_ids``.

        The IDs are tried in the order given, so earlier IDs take priority
        (e.g. preferred model variants before their fallbacks). For an ID
        discovered more than once, the first location in chain order is
        returned. Returns ``None`` when no ID matches.
        """
        for model_id in model_ids:
            if found := self.get(model_id):
                return found[0]
        return None


async def scan(unit: ModbusUnit, base_address: int) -> SunSpecModels:
    """Return the discovered SunSpec models by ID.

    Raises ``SunSpecError`` if the marker is absent or the chain is invalid.
    """
    marker = await unit.read_holding_registers(base_address, 2)
    if decode_uint32(marker) != _SUNSPEC_MARKER:
        raise SunSpecError(f"No SunSpec marker found at register {base_address}")

    models = SunSpecModels()
    address = base_address + 2
    for _ in range(_MAX_MODELS):
        model_id, length = await unit.read_holding_registers(address, 2)
        if model_id == _END_MODEL_ID:
            return models
        model = SunSpecModel(model_id=model_id, address=address, length=length)
        models.setdefault(model_id, []).append(model)
        address += model.span
    raise SunSpecError(f"Model chain not terminated after {_MAX_MODELS} models")
