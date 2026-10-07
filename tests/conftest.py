from pathlib import Path

import pytest

from homeassistant import loader
from homeassistant.core import HomeAssistant


@pytest.fixture
def enable_custom_integrations(hass: HomeAssistant) -> None:
    """Enable custom integrations from this repository."""
    import custom_components

    integration_path = Path(__file__).parents[1] / "custom_components"

    custom_components.__path__ = [str(integration_path)]

    hass.data.pop(loader.DATA_CUSTOM_COMPONENTS, None)
