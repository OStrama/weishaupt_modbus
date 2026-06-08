"""Integration for Weishaupt WebIF connection."""

import asyncio
import http.cookiejar
import logging
from pathlib import Path
import time
from typing import Any

import aiofiles
from bs4 import BeautifulSoup
from bs4.element import Tag
import httpx

from homeassistant.core import HomeAssistant

from .configentry import MyConfigEntry
from .const import CONF, CONST

_LOGGER = logging.getLogger(__name__)

UNITS = [" °C", " KW", " K", "m3/h", " BAR", " %", " h", " rpm"]
Info = {
    "Heizkreis": "http://10.10.1.225/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C1900000000000000F9AF020003000401",
    "Waermepumpe": "http://10.10.1.225/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2200000000000000F9AF020003000401",
    "2WEZ": "http://10.10.1.225/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2300000000000000F9AF020003000401",
    "Statistik": "http://10.10.1.225/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C2700000000000000F9AF020003000401",
}


class WebifConnection:
    """Connect to the local Weishaupt Webif."""

    def __init__(self, hass: HomeAssistant, config_entry: MyConfigEntry) -> None:
        """Initialize the WebIf connection."""
        self._hass = hass
        self._config_entry = config_entry
        self._ip: str = config_entry.data[CONF.HOST]
        self._username: str = config_entry.data[CONF.USERNAME]
        self._password: str = config_entry.data[CONF.PASSWORD]
        self._client: httpx.AsyncClient | None = None
        self._request_lock = asyncio.Lock()
        self._request_delay: float = 10.0
        self._last_request_time: float | None = None
        self._cookies_loaded: bool = False
        self._cookie_file: Path = (
            Path(hass.config.config_dir)
            / f"weishaupt_modbus_{config_entry.entry_id}_cookies.txt"
        )
        self._cookie_jar: http.cookiejar.MozillaCookieJar = (
            http.cookiejar.MozillaCookieJar(str(self._cookie_file))
        )
        self._pages: dict[str, str] = {}
        self._payload: dict[str, str] = {
            "user": config_entry.data[CONF.USERNAME],
            "pass": config_entry.data[CONF.PASSWORD],
        }
        self._base_url: str = f"http://{self._ip}"
        self._login_url: str = "/login.html"
        self._connected: bool = False
        self._values: dict[str, Any] = {}
        self._hass = hass

    async def _ensure_cookies_loaded(self) -> None:
        """Load cookies from disk once."""
        if self._cookies_loaded:
            return

        if self._cookie_file.exists():
            try:
                await self._hass.async_add_executor_job(
                    self._cookie_jar.load,
                    ignore_discard=True,
                    ignore_expires=True,
                )
                _LOGGER.debug("Loaded WebIF cookies from %s", self._cookie_file)
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Failed to load WebIF cookies: %s", err)
        self._cookies_loaded = True

    async def _sync_cookies_from_response(self, response: httpx.Response) -> None:
        """Extract cookies from httpx response and sync to jar."""
        try:
            for cookie in response.cookies.jar:
                self._cookie_jar.set_cookie(cookie)
            await self._save_cookies()
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Failed to sync cookies from response: %s", err)

    async def _save_cookies(self) -> None:
        """Save cookies to disk after requests."""
        if not self._cookie_jar:
            return

        try:
            await self._hass.async_add_executor_job(
                self._cookie_jar.save,
                ignore_discard=True,
                ignore_expires=True,
            )
            _LOGGER.debug(
                "Saved WebIF cookies to %s, count: %d",
                self._cookie_file,
                len(self._cookie_jar),
            )
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Failed to save WebIF cookies: %s", err)

    def _discover_pages(self, soup: BeautifulSoup) -> None:
        """Discover navigational links from the WebIF page."""
        try:
            self._pages = self.get_links(soup)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Failed to parse WebIF page links: %s", err)
            self._pages = {}

        if self._pages:
            _LOGGER.debug("Discovered WebIF page links: %s", self._pages)

    def _find_export_url(self) -> str | None:
        """Return the configured export URL if discovered."""
        for url in self._pages.values():
            if "settings_export.html" in url:
                return url
        return None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            # ToDo: Check header!
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "de,en-US;q=0.7,en;q=0.3",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": self._base_url,
                "Referer": f"{self._base_url}/login.html",  # Tell the MCU we came from the login page!
                # "Connection": "keep-alive",
                "Connection": "close",  # do not keep alive. suggested by gemini & chatgpt due to embeded servers not good at handling long connections
            }

            # ToDo: check the cookie part!
            cookies = httpx.Cookies()
            for cookie in self._cookie_jar:
                cookies.set(
                    cookie.name, cookie.value, domain=cookie.domain, path=cookie.path
                )
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers=headers,
                # ToDo: Check if redirect is necesary
                follow_redirects=True,
                timeout=httpx.Timeout(60.0, connect=20.0),
                verify=False,  # Local device on HTTP, no SSL verification needed
                limits=httpx.Limits(
                    max_connections=1, max_keepalive_connections=0
                ),  # do not keep alive. suggested by gemini & chatgpt due to embeded servers not good at handling long connections
                cookies=cookies,
            )
        return self._client

    async def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """Perform a serialized request through the shared client."""
        async with self._request_lock:
            if self._last_request_time is not None and self._request_delay > 0:
                elapsed = time.monotonic() - self._last_request_time
                if elapsed < self._request_delay:
                    await asyncio.sleep(self._request_delay - elapsed)

            await self._ensure_cookies_loaded()
            client = self._get_client()

            start = time.monotonic()

            try:
                response = await client.request(method, url, **kwargs)

                duration = time.monotonic() - start

                _LOGGER.warning(
                    "WEBIF %s %s -> %s in %.3fs conn=%s set-cookie=%s",
                    method,
                    response.url,
                    response.status_code,
                    duration,
                    response.headers.get("Connection"),
                    response.headers.get("Set-Cookie"),
                )

                self._last_request_time = time.monotonic()
                await self._save_cookies()
                return response

            except Exception as err:
                duration = time.monotonic() - start

                _LOGGER.warning(
                    "WEBIF %s %s FAILED after %.3fs: %s",
                    method,
                    url,
                    duration,
                    err,
                )

                raise

    async def login(self) -> None:
        """Log into the portal. Create cookie to stay logged in for the session."""
        _LOGGER.warning("Trying to log in")
        if not self._username or not self._password:
            _LOGGER.warning("No user / password specified for webif")
            self._connected = False
            return

        await self._ensure_cookies_loaded()

        try:
            if len(self._cookie_jar) > 0:
                _LOGGER.debug("Attempting to reuse saved WebIF cookie session")
                response = await self._request("GET", "/home.html")
                main_page = BeautifulSoup(markup=response.text, features="html.parser")
                welcome_string = f"Hello {self._username}"
                if response.status_code == 200 and main_page.find(
                    string=welcome_string
                ):
                    self._discover_pages(main_page)
                    self._connected = True
                    _LOGGER.warning("Reused existing WebIF cookie session")
                    return
                _LOGGER.debug("Saved WebIF cookie is no longer valid; logging in again")

            response = await self._request(
                "POST",
                "/login.html",
                data={"user": self._username, "pass": self._password},
            )
            main_page = BeautifulSoup(markup=response.text, features="html.parser")
            # print(main_page.prettify())
            welcome_string = f"Hello {self._username}"
            find_welcome = main_page.find(string=welcome_string)
            final_url = str(response.url)
            _LOGGER.info(f"Final URL received: {final_url}")

            if "wrongpassword" in final_url:
                _LOGGER.error("❌ The heat pump rejected the password!")
            elif "nocon" in final_url:
                _LOGGER.error(
                    "❌ Microcontroller error: No connection to the internal database!"
                )
            elif "home.html" in final_url or welcome_string in response.text:
                _LOGGER.info("✅ Successful Login!")

            if find_welcome == welcome_string:
                self._discover_pages(main_page)
                self._connected = True
                _LOGGER.warning("Successfully logged in to WEBIF")
            else:
                self._connected = True
                # _LOGGER.warning("Login failed")

        except TimeoutError:
            self._connected = False
            _LOGGER.debug("Timeout while logging in")

    async def return_test_data(self) -> dict[str, Any]:
        """Return some values for testing."""
        return {
            "Webifsensor": "TESTWERT",
            "Außentemperatur": 2,
            "AT Mittelwert": -1,
            "AT Langzeitwert": -1,
            "Raumsolltemperatur": 22.0,
            "Vorlaufsolltemperatur": 32.5,
            "Vorlauftemperatur": 32.4,
        }

    async def close(self) -> None:
        """Close connection to WebIf."""
        if self._client:
            await self._client.aclose()

    async def get_info(self) -> dict[str, Any] | None:
        """Return Info -> Heizkreis1."""
        if not self._connected or not self._client:
            # print(self._connected)
            # print(self._client)
            return None
        try:
            url = self._find_export_url()
            if url is None:
                url = "/settings_export.html?stack=0C00000100000000008000F9AF010002000301,0C000C1900000000000000F9AF020003000401"

            response = await self._request("GET", url)
            if response.status_code != 200:
                _LOGGER.debug("Error: %s", response.status_code)
                return None
            main_page = BeautifulSoup(markup=response.text, features="html.parser")
            navs = main_page.find_all("div", class_="col-3")
            # print(main_page.prettify())
            if len(navs) == 3:
                values_nav = navs[2]
                if isinstance(values_nav, Tag):
                    self._values["Info"] = {
                        "Heizkreis": self.get_values(soup=values_nav)
                    }
                    _LOGGER.debug("Values: %s", self._values)
                    return self._values["Info"]["Heizkreis"]

            _LOGGER.debug("Update failed. return None")
            return None
        except (TimeoutError, httpx.HTTPError) as ex:
            _LOGGER.debug("Error while getting info: %s", ex)
            return None

    def get_links(self, soup: Tag) -> dict[str, str]:
        """Return links from given nav container."""
        soup_links = soup.find_all(name="a")
        links: dict[str, str] = {}
        for link in soup_links:
            if not isinstance(link, Tag):
                continue
            h5_tag = link.find("h5")
            if h5_tag and h5_tag.text and link.get("href"):
                name = h5_tag.text.strip()
                url = str(link["href"])
                links[name] = url
        return links

    def get_values(self, soup: Tag) -> dict[str, Any]:
        """Return values from given nav container."""
        soup_links = soup.find_all(name="div", class_="nav-link browseobj")
        values: dict[str, Any] = {}
        for item in soup_links:
            if not isinstance(item, Tag):
                continue
            h5_tag = item.find("h5")
            if h5_tag and h5_tag.text:
                name = h5_tag.text.strip()
                value_list = item.find_all(string=True, recursive=False)
                value = "".join(value_list)
                # Remove units,
                for unit in UNITS:
                    value = value.replace(unit, "").strip()
                values[name] = value
                # if len(value) > 1:
                #    string_value = str(value[1]) if value[1] else ""
                #    my_value = string_value.strip()
                #    values[name] = my_value
        return values

    def get_link_values(self, soup: Tag) -> dict[str, str]:
        """Return values from given nav container which are inside a link."""
        soup_links = soup.find_all(name="a", class_="nav-link browseobj")
        values: dict[str, str] = {}
        for item in soup_links:
            if not isinstance(item, Tag):
                continue
            h5_tag = item.find("h5")
            if h5_tag and h5_tag.text:
                name = h5_tag.text.strip()
                value = item.find_all(string=True, recursive=False)
                if len(value) > 1:
                    string_value = str(value[1]) if value[1] else ""
                    values[name] = string_value.strip()
        return values

    async def get_info_hk1(self) -> dict[str, Any] | None:
        """Return Info -> Heizkreis1."""
        filepath = Path(get_filepath(self._hass) / "info_hk1.html")
        async with aiofiles.open(filepath, encoding="utf-8") as openfile:
            html = await openfile.read()
        main_page = BeautifulSoup(markup=html, features="html.parser")
        navs = main_page.find_all("div", class_="col-3")
        # print(main_page.prettify())
        if len(navs) == 3:
            values_nav = navs[2]
            if isinstance(values_nav, Tag):
                self._values["Info"] = {"Heizkreis": self.get_values(soup=values_nav)}
                _LOGGER.debug("Values: %s", self._values)
                return self._values["Info"]["Heizkreis"]

            _LOGGER.debug("Update failed. return None")

        return None


def get_filepath(hass: HomeAssistant) -> Path | None:
    """Get the filepath to the custom component directory."""
    filepath = Path(
        f"{hass.config.config_dir}/custom_components/{CONST.DOMAIN}/webif_test_html"
    )

    # on some installations custom_components resides in /core/
    if not filepath.exists():
        filepath = Path(Path(__file__).resolve().parent)

    # we do not find any path..
    if not filepath.exists():
        return None
    return filepath
