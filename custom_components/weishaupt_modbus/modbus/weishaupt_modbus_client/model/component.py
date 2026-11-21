"""Common register read constraints for Weishaupt WWP controllers."""

from modbus_connection.model import Component


class WeishauptComponent(Component):
    """Keep reads contiguous and within the controller's five-point limit."""

    # Weishaupt WWP data-point list 83807301, section 3.1.
    max_gap = 0
    max_span = 5
