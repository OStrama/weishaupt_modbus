"""Standalone, block-reading Modbus TCP client package for Weishaupt heat pumps."""

from .modbus_api import WeishauptModbusClient

__all__ = ["WeishauptModbusClient"]
