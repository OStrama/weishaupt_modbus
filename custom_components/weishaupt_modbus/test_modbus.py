"""Scan all possible modbus registers for a value."""

import asyncio

from pymodbus import ExceptionResponse, ModbusException, pymodbus_apply_logging_config
import pymodbus.client as ModbusClient


async def main():  # noqa: D103
    pymodbus_apply_logging_config("DEBUG")
    host = "192.168.42.144"  # 10.10.1.225"
    port = 502
    client = ModbusClient.AsyncModbusTcpClient(
        host,
        port=port,
    )
    await client.connect()

    # binary_out = range(1, 9999)
    # binary_in = range(10001, 19999)
    binary_out = []
    binary_in = []
    input_register = range(30001, 39999)
    holding_register = range(40001, 49999)

    file = open(file="register.txt", mode="w", encoding="UTF-8")  # noqa: ASYNC230, PTH123

    file.write("Binary out\n\n")

    for register in binary_out:
        try:
            rr = await client.read_coils(register, 1, slave=1)
            if len(rr.registers) > 0:
                val = rr.registers[0]
                print(rr)  # noqa: T201
        except ModbusException as exc:
            val = exc
            print(val)  # noqa: T201
        if rr.isError():
            val = rr
        if isinstance(rr, ExceptionResponse):
            val = rr

        file.write(str(register) + ";" + str(val) + "\n")

    file.write("Binary in: \n\n")

    for register in binary_in:
        writeit = False
        try:
            rr = await client.read_coils(register, 1, slave=1)
            print(rr)  # noqa: T201
        except ModbusException as exc:
            val = exc
            print(val)  # noqa: T201
        if rr.isError() or isinstance(rr, ExceptionResponse):
            val = rr
            writeit = False
        elif len(rr.registers) > 0:
            val = rr.registers[0]
            writeit = True

        if writeit is True:
            file.write(str(register) + ";" + str(val) + "\n")

    file.write("Input Register: \n\n")

    for register in input_register:
        writeit = False
        try:
            rr = await client.read_input_registers(register, slave=1)
            print(rr)  # noqa: T201
        except ModbusException as exc:
            val = exc
            print(val)  # noqa: T201
        if rr.isError() or isinstance(rr, ExceptionResponse):
            val = rr
            writeit = False
        elif len(rr.registers) > 0:
            val = rr.registers[0]
            writeit = True

        if writeit is True:
            file.write(str(register) + ";" + str(val) + "\n")

    file.write("Holding Register: \n\n")

    for register in holding_register:
        writeit = False
        try:
            rr = await client.read_holding_registers(register, slave=1)
            print(rr)  # noqa: T201
        except ModbusException as exc:
            val = exc
            print(val)  # noqa: T201
        if rr.isError() or isinstance(rr, ExceptionResponse):
            val = rr
            writeit = False
        elif len(rr.registers) > 0:
            val = rr.registers[0]
            writeit = True

        if writeit is True:
            file.write(str(register) + ";" + str(val) + "\n")

    client.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
