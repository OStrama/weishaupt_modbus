"""Weishaupt IO register models."""

from ..weishaupt_modbus_connection.model import Component, gauge, integer


class IOInput(Component):
    """Weishaupt IO input registers."""

    register_space = "input"

    sg_ready_1 = integer(35101)
    """SG-Ready input 1."""

    sg_ready_2 = integer(35102)
    """SG-Ready input 2."""

    output_h1_2 = integer(35103)
    """H1.2 output status."""

    output_h1_3 = integer(35104)
    """H1.3 output status."""

    output_h1_4 = integer(35105)
    """H1.4 output status."""

    output_h1_5 = integer(35106)
    """H1.5 output status."""

    input_de1 = gauge(
        35107,
        1,
        unit=None,
    )
    """DE1 input status."""

    input_de2 = gauge(
        35108,
        1,
        unit=None,
    )
    """DE2 input status."""


class IOConfig(Component):
    """Weishaupt IO configuration registers."""

    register_space = "holding"

    sg_ready_1 = integer(
        45101,
        writable=True,
    )
    """SG-Ready input 1 configuration."""

    sg_ready_2 = integer(
        45102,
        writable=True,
    )
    """SG-Ready input 2 configuration."""

    output_h1_2 = integer(
        45103,
        writable=True,
    )
    """H1.2 output configuration."""

    output_h1_3 = integer(
        45104,
        writable=True,
    )
    """H1.3 output configuration."""

    output_h1_4 = integer(
        45105,
        writable=True,
    )
    """H1.4 output configuration."""

    output_h1_5 = integer(
        45106,
        writable=True,
    )
    """H1.5 output configuration."""

    input_de1 = integer(
        45107,
        writable=True,
    )
    """DE1 input configuration."""

    input_de2 = integer(
        45108,
        writable=True,
    )
    """DE2 input configuration."""
