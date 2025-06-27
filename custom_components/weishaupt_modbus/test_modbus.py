"""Module for testing Modbus communication with a remote device."""

import asyncio
from pathlib import Path

from pymodbus import pymodbus_apply_logging_config
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException
from pymodbus.pdu import ExceptionResponse
from pymodbus.pdu.pdu import ModbusPDU


async def main():  # noqa: D103
    pymodbus_apply_logging_config("DEBUG")
    host = "192.168.42.144"  # 10.10.1.225"
    port = 502
    client = AsyncModbusTcpClient(
        host=host,
        port=port,
        timeout=10,
        retries=3,
    )
    await client.connect()

    # binary_out = range(1, 9999)
    # binary_in = range(10001, 19999)
    binary_out = []
    binary_in = []
    input_register = range(30001, 39999)
    holding_register = range(40001, 49999)

    with Path("register.txt").open(mode="w", encoding="UTF-8") as file:  # noqa: ASYNC230
        file.write("Binary out\n\n")

        # Process binary outputs
        for register in binary_out:
            val = await read_coil_register(client, register)
            file.write(f"{register};{val}\n")

        file.write("Binary in: \n\n")

        # Process binary inputs
        for register in binary_in:
            val = await read_coil_register(client, register)
            if val is not None and not isinstance(val, (Exception, ExceptionResponse)):
                file.write(f"{register};{val}\n")

        file.write("Input Register: \n\n")

        # Process input registers
        for register in input_register:
            val = await read_input_register(client, register)
            if val is not None and not isinstance(val, (Exception, ExceptionResponse)):
                file.write(f"{register};{val}\n")

        file.write("Holding Register: \n\n")

        # Process holding registers
        for register in holding_register:
            val = await read_holding_register(client, register)
            if val is not None and not isinstance(val, (Exception, ExceptionResponse)):
                file.write(f"{register};{val}\n")

    client.close()


async def read_coil_register(
    client: AsyncModbusTcpClient, register: int
) -> bool | Exception | ExceptionResponse | ModbusPDU | None:
    """Read a single coil register and return the value or error."""
    try:
        response = await client.read_coils(address=register, count=1, slave=1)

        if response is None:
            return None

        if hasattr(response, "isError") and response.isError():
            return response

        if isinstance(response, ExceptionResponse):
            return response

        if hasattr(response, "bits") and len(response.bits) > 0:
            return response.bits[0]

        return None

    except ModbusException as exc:
        print(f"Modbus error reading coil {register}: {exc}")
        return exc
    except Exception as exc:
        print(f"General error reading coil {register}: {exc}")
        return exc


async def read_input_register(
    client: AsyncModbusTcpClient, register: int
) -> int | Exception | ExceptionResponse | ModbusPDU | None:
    """Read a single input register and return the value or error."""
    try:
        response = await client.read_input_registers(address=register, count=1, slave=1)

        if response is None:
            return None

        if hasattr(response, "isError") and response.isError():
            return response

        if isinstance(response, ExceptionResponse):
            return response

        if hasattr(response, "registers") and len(response.registers) > 0:
            return response.registers[0]

        return None

    except ModbusException as exc:
        print(f"Modbus error reading input register {register}: {exc}")
        return exc
    except Exception as exc:
        print(f"General error reading input register {register}: {exc}")
        return exc


async def read_holding_register(
    client: AsyncModbusTcpClient, register: int
) -> int | Exception | ExceptionResponse | ModbusPDU | None:
    """Read a single holding register and return the value or error."""
    try:
        response = await client.read_holding_registers(
            address=register, count=1, slave=1
        )

        if response is None:
            return None

        if hasattr(response, "isError") and response.isError():
            return response

        if isinstance(response, ExceptionResponse):
            return response

        if hasattr(response, "registers") and len(response.registers) > 0:
            return response.registers[0]

        return None

    except ModbusException as exc:
        print(f"Modbus error reading holding register {register}: {exc}")
        return exc
    except Exception as exc:
        print(f"General error reading holding register {register}: {exc}")
        return exc


if __name__ == "__main__":
    asyncio.run(main())
