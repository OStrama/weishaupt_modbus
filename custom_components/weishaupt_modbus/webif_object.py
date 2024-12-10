"""webif Object.

A webif object that contains a webif item and communicates with the webif.
It contains a webif client for setting and getting webif values
"""

import asyncio
import logging
import time

import aiohttp
from bs4 import BeautifulSoup
from bs4.element import NavigableString, ResultSet, Tag

from .configentry import MyConfigEntry
from .const import CONF
from .fake_html_responses import INFO_2WEZ, INFO_HK1, INFO_STATISTIK, INFO_WP

logging.basicConfig()
log: logging.Logger = logging.getLogger(name=__name__)


class WebifConnection:
    """Connect to the local Weishaupt Webif."""

    _config_entry: MyConfigEntry = None
    _ip: str = ""
    _username: str = ""
    _password: str = ""
    _session = None
    _payload: dict[str, str] = {"user": _username, "pass": _password}
    _base_url: str = "http://" + _ip
    _login_url: str = "/login.html"
    _connected: bool = False
    _values = {}
    _last_api_call = 0
    _time_between_api_calls = 5

    def __init__(self, config_entry: MyConfigEntry) -> None:
        """Initialize the WebIf connection.

        Todo: Get info from config.

        """
        self._ip = config_entry.data[CONF.HOST]
        self._username = config_entry.data[CONF.USERNAME]
        self._password = config_entry.data[CONF.PASSWORD]
        self._base_url = "http://" + self._ip
        self._config_entry = config_entry

    async def login(self) -> None:
        """Log into the portal. Create cookie to stay logged in for the session."""
        self._connected = False
        jar = aiohttp.CookieJar(unsafe=True)
        self._session = aiohttp.ClientSession(base_url=self._base_url, cookie_jar=jar)
        if self._username == "" or self._password == "":
            logging.error("No user / password specified for webif")

        try:
            async with self._session.post(
                "/login.html",
                data={"user": self._username, "pass": self._password},
            ) as response:
                self._last_api_call = time.time()
                if response.status != 200:
                    logging.error(
                        msg="HTTP Error: " & response.status & " while logging in."
                    )

                main_page = BeautifulSoup(markup=INFO_WP, features="html.parser")
                navs: Tag | NavigableString | None = main_page.findAll(
                    "div", class_="col-3"
                )
                if len(navs) == 1:
                    self._connected = True

        except TimeoutError:
            self._connected = False
            logging.error(msg="Timeout while logging in")

    async def close(self) -> None:
        """Close connection to WebIf."""
        await self._session.close()

    async def get_info_hk(self) -> None:
        """Return Info -> Heizkreis1."""
        if self._connected is False:
            return None
        try:
            async with self._session.get(
                # token = F9AF
                # token = 0F4C
                url="/settings_export.html?stack=0C00000100000000008000"
                + self._config_entry.data[CONF.WEBIF_TOKEN]
                + "010002000301,0C000C1900000000000000"
                + self._config_entry.data[CONF.WEBIF_TOKEN]
                + "020003000401"
            ) as response:
                self._last_api_call = time.time()
                if response.status != 200:
                    logging.debug(msg="Error: " & str(response.status))
                    return None
                main_page = BeautifulSoup(
                    markup=await response.text(), features="html.parser"
                )
                navs: Tag | NavigableString | None = main_page.findAll(
                    "div", class_="col-3"
                )

                if len(navs) == 3:
                    values_nav = navs[2]
                    self._values["Info"] = {
                        "Heizkreis": self.get_values(soup=values_nav)
                    }
                    logging.debug(msg=self._values)
                    return self._values["Info"]["Heizkreis"]
                logging.debug("Update failed. return None")
                return None
        except TimeoutError:
            logging.debug(msg="Timeout while getting info")
            return None

    async def fake_info_wp(self) -> None:
        """Return FAKE Info -> Wärmepumpe."""
        main_page = BeautifulSoup(markup=INFO_WP, features="html.parser")
        navs: Tag | NavigableString | None = main_page.findAll("div", class_="col-3")
        if len(navs) == 3:
            values_nav = navs[2]
            self._values["Info"] = {"Wärmepumpe": self.get_values(soup=values_nav)}
            logging.debug(msg=self._values)
            return self._values["Info"]["Wärmepumpe"]
        logging.debug("Update failed. return None")
        return None

    async def get_fake_info(self):
        """Collect all fake info and return it as dict."""
        myreturn = {}
        await self.wait_cooldown()
        info_wp = await self.fake_info_wp()
        await self.wait_cooldown()
        info_2wez = await self.fake_info_2wez()
        await self.wait_cooldown()
        info_hk1 = await self.fake_info_hk1()
        await self.wait_cooldown()
        info_statistics = await self.fake_info_statistik()
        myreturn.update(info_wp)
        myreturn.update(info_2wez)
        myreturn.update(info_hk1)
        myreturn.update(info_statistics)
        return myreturn

    async def wait_cooldown(self):
        """Wait if the last API call was less than 60 seconds ago.

        This prevents hammering the API and killing the server.
        """
        time_since_last_call = time.time() - self._last_api_call
        if (time_since_last_call) < self._time_between_api_calls:
            await asyncio.sleep(self._time_between_api_calls - time_since_last_call)
        self._last_api_call = time.time()

    async def fake_info_hk1(self) -> None:
        """Return FAKE Info -> Heizkreis1."""

        main_page = BeautifulSoup(markup=INFO_HK1, features="html.parser")
        navs: Tag | NavigableString | None = main_page.findAll("div", class_="col-3")
        if len(navs) == 3:
            values_nav = navs[2]
            self._values["Info"] = {"Heizkreis1": self.get_values(soup=values_nav)}
            logging.debug(msg=self._values)
            return self._values["Info"]["Heizkreis1"]
        logging.debug("Update failed. return None")
        return None

    async def fake_info_2wez(self) -> None:
        """Return FAKE Info -> 2. Wärmeerzeuger."""

        main_page = BeautifulSoup(markup=INFO_2WEZ, features="html.parser")
        navs: Tag | NavigableString | None = main_page.findAll("div", class_="col-3")
        if len(navs) == 3:
            values_nav = navs[2]
            self._values["Info"] = {"2.WEZ": self.get_values(soup=values_nav)}
            logging.debug(msg=self._values)
            return self._values["Info"]["2.WEZ"]
        logging.debug("Update failed. return None")
        return None

    async def fake_info_statistik(self) -> None:
        """Return FAKE Info -> Heizkreis1."""

        main_page = BeautifulSoup(markup=INFO_STATISTIK, features="html.parser")
        navs: Tag | NavigableString | None = main_page.findAll("div", class_="col-3")
        if len(navs) == 3:
            values_nav = navs[2]
            self._values["Info"] = {"Statistik": self.get_values(soup=values_nav)}
            logging.debug(msg=self._values)
            return self._values["Info"]["Statistik"]
        logging.debug("Update failed. return None")
        return None

    def get_links(self, soup: BeautifulSoup) -> dict:
        """Return links from given nav container."""
        soup_links = soup.find_all(name="a")
        links = {}
        for link in soup_links:
            name = link.find("h5").text.strip()
            url = link["href"]
            links[name] = url
        return links

    def get_values(self, soup: BeautifulSoup) -> dict:
        """Return values from given nav container."""
        soup_links = soup.find_all(name="div", class_="nav-link browseobj")
        values = {}
        for item in soup_links:
            name = item.find("h5").text.strip()
            value = item.findAll(string=True, recursive=False)
            myValue = value[1].strip()
            values[name] = myValue
        return values

    def get_link_values(self, soup: BeautifulSoup) -> dict:
        """Return values from given nav container witch are inside a link."""
        soup_links: ResultSet[logging.Any] = soup.find_all(
            name="a", class_="nav-link browseobj"
        )
        values = {}
        for item in soup_links:
            name = item.find("h5").text.strip()
            value = item.findAll(string=True, recursive=False)
            values[name] = value[1].strip()
        return values
