"""WebIF object for Weishaupt integration."""

import logging
from typing import Any

import aiohttp
from bs4 import BeautifulSoup, NavigableString, Tag

from .configentry import MyConfigEntry
from .const import CONF

_LOGGER = logging.getLogger(__name__)


class WebifConnection:
    """Connect to the local Weishaupt WebIF."""

    def __init__(self, config_entry: MyConfigEntry) -> None:
        """Initialize the WebIF connection."""
        self._config_entry = config_entry
        self._ip = config_entry.data[CONF.HOST]
        self._username = config_entry.data[CONF.USERNAME]
        self._password = config_entry.data[CONF.PASSWORD]
        self._base_url = f"http://{self._ip}"
        self._payload = {"user": self._username, "pass": self._password}
        self._session: aiohttp.ClientSession | None = None
        self._connected: bool = False
        self._values: dict[str, dict[str, dict[str, Any]]] = {}

    async def login(self) -> None:
        """Log into the portal and create cookie for session persistence."""
        jar = aiohttp.CookieJar(unsafe=True)
        self._session = aiohttp.ClientSession(base_url=self._base_url, cookie_jar=jar)

        if self._username and self._password:
            # Login logic implementation
            _LOGGER.debug("Logging into WebIF with credentials")
        else:
            _LOGGER.debug("No credentials provided for WebIF login")

    async def close(self) -> None:
        """Close the session."""
        if self._session is not None:
            await self._session.close()
            self._session = None

    async def get_info(self) -> None:
        """Get info from WebIF."""
        if self._session is None:
            _LOGGER.warning("Session not initialized, cannot get WebIF info")
            return

        try:
            async with self._session.get("/") as response:
                if response.status == 200:
                    content = await response.text()
                    soup = BeautifulSoup(content, "html.parser")
                    # Process soup data
                    _LOGGER.debug("Successfully retrieved WebIF info")
                else:
                    _LOGGER.warning(
                        "Failed to get WebIF info, status: %d", response.status
                    )
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to WebIF: %s", err)

    def get_values(self, soup: BeautifulSoup) -> dict[str, str]:
        """Return values from given nav container."""
        soup_links = soup.find_all(name="div", class_="nav-link browseobj")
        values: dict[str, str] = {}

        for item in soup_links:
            if not isinstance(item, Tag):
                continue

            h5_tag = item.find("h5")
            if h5_tag is None:
                continue

            name = h5_tag.get_text().strip()

            # Get direct text children, excluding nested tags
            value_elements = [
                text
                for text in item.strings
                if isinstance(text, (str, NavigableString)) and text.strip()
            ]

            # Take the second text element if available (first is usually the name)
            if len(value_elements) > 1:
                values[name] = str(value_elements[1]).strip()

        return values

    def get_link_values(self, soup: BeautifulSoup) -> dict[str, str]:
        """Return values from nav container links."""
        soup_links = soup.find_all(name="a", class_="nav-link browseobj")
        values: dict[str, str] = {}

        for item in soup_links:
            if not isinstance(item, Tag):
                continue

            h5_tag = item.find("h5")
            if h5_tag is None:
                continue

            name = h5_tag.get_text().strip()

            # Get direct text children, excluding nested tags
            value_elements = [
                text
                for text in item.strings
                if isinstance(text, (str, NavigableString)) and text.strip()
            ]

            # Take the second text element if available
            if len(value_elements) > 1:
                values[name] = str(value_elements[1]).strip()

        return values
