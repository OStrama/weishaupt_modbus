# main.py

import asyncio
import logging
import sys

# Adjust imports depending on your exact project root structure.
# This assumes main.py is in the parent directory of custom_components/
from .modbus_api import WeishauptModbusClient
from .const import ALL_GROUPS

# Configure basic logging to see connection events or Modbus warnings
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

_LOGGER = logging.getLogger(__name__)

# Replace with your actual heat pump IP address
HOST_IP = "10.10.1.225"


async def main():
    _LOGGER.info("Initializing Weishaupt Modbus test client...")
    client = WeishauptModbusClient(host=HOST_IP)

    try:
        # 1. Connect
        _LOGGER.info("Connecting to heat pump at %s...", HOST_IP)
        if not await client.connect():
            _LOGGER.error("Could not connect to %s. Exiting.", HOST_IP)
            return

        _LOGGER.info("Connection successful!")

        # 2. Run our new statistic block-read test
        _LOGGER.info("Reading optimized statistics blocks defined in const.py...")
        stats_data = await client.update()

        # 3. Print out the parsed results nicely
        print("\n" + "=" * 50)
        print("          MODBUS REGISTER READ RESULTS          ")
        print("=" * 50)

        # Iterate over the original register groups to format outputs together
        for start, count in ALL_GROUPS:
            print(f"\nBlock starting at address {start} (count: {count}):")
            for offset in range(count):
                addr = start + offset
                val = stats_data.get(addr)
                if val is not None:
                    print(f"  Register {addr:5d} -> Raw Value: {val}")
                else:
                    print(f"  Register {addr:5d} -> Read Failed / Missing")

        print("=" * 50 + "\n")

        print(stats_data)

    except Exception as err:
        _LOGGER.exception("An unexpected error occurred during testing: %s", err)

    finally:
        # 4. Clean up connection
        _LOGGER.info("Disconnecting from Modbus client...")
        await client.disconnect()
        _LOGGER.info("Test finished.")


if __name__ == "__main__":
    # Workaround for Windows event loop policy if running locally on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
