"""Shared types for the modbus_connection abstraction."""

from typing import Literal

WordOrder = Literal["big", "little"]
"""Order of 16-bit registers within a multi-register value.

``"big"`` puts the most-significant word first (the common Modbus convention);
``"little"`` puts the least-significant word first.
"""

BitSpace = Literal["coil", "discrete"]
"""Which bit space a field is read from: coil (FC01) or discrete input (FC02)."""

SocketFraming = Literal["socket", "rtu", "ascii"]
"""Wire framing for a TCP/UDP connection: native Modbus (MBAP), RTU or ASCII."""

SerialFraming = Literal["rtu", "ascii"]
"""Wire framing for a serial connection: binary RTU or ASCII."""
