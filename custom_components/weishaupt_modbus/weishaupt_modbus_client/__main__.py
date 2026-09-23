"""Command-line interface for querying a Weishaupt device."""

import argparse
import asyncio

from modbus_connection import ModbusError
from modbus_connection.cli_helper import (
    CountingUnit,
    add_connection_args,
    connect_from_args,
    print_component,
)

from .model.device import Weishaupt


class TracingUnit:
    """Tracing."""

    def __init__(self, unit) -> None:
        """__init__ ."""
        self._unit = unit

    async def read_input_registers(self, address: int, count: int):  # noqa: D102
        print(f"READ input: {address} +{count}")  # noqa: T201
        result = await self._unit.read_input_registers(address, count)
        print(f"  -> {result}")  # noqa: T201
        return result

    async def read_holding_registers(self, address: int, count: int):  # noqa: D102
        print(f"READ holding: {address} +{count}")  # noqa: T201
        result = await self._unit.read_holding_registers(address, count)
        print(f"  -> {result}")  # noqa: T201
        return result


async def main() -> int:
    """Connect to a Weishaupt device and print system values."""
    parser = argparse.ArgumentParser(
        description="Query a Weishaupt device and print system values."
    )
    add_connection_args(parser)
    parser.add_argument(
        "--unit",
        type=int,
        default=1,
        help="Modbus unit id",
    )

    args = parser.parse_args()

    try:
        conn = await connect_from_args(args)
    except ModbusError as err:
        print(f"Could not connect: {err}")  # noqa: T201
        return 1

    try:
        counting = CountingUnit(TracingUnit(conn.for_unit(args.unit)))
        device = Weishaupt(counting)
        await device.async_update()
        # await device.system_input.async_update()
        # await device.system_config.async_update()

        print_component(device.system_input)
        print_component(device.system_config)

    finally:
        await conn.close()

    return 0


raise SystemExit(asyncio.run(main()))
