"""Kennfeld."""

import logging
import json
import aiofiles

import numpy as np
from numpy.polynomial import Chebyshev

from .configentry import MyConfigEntry

from .const import CONF, CONST

logging.basicConfig()
log = logging.getLogger(__name__)

SPLINE_AVAILABLE = True
try:
    import scipy  # noqa F401 pylint: disable=W0611
except ModuleNotFoundError:
    log.warning(
        "Scipy not available, use less precise Chebyshef interpolation for heating power"
    )
    SPLINE_AVAILABLE = False

if SPLINE_AVAILABLE is True:
    log.info(
        "Scipy available, use precise cubic spline interpolation for heating power"
    )
    from scipy.interpolate import CubicSpline  # pylint: disable=E0401


class PowerMap:
    """Power map class."""

    # these are values extracted from the characteristic curves of heating power found ion the documentation of my heat pump.
    # there are two diagrams:
    #  - heating power vs. outside temperature @ 35 °C flow temperature
    #  - heating power vs. outside temperature @ 55 °C flow temperature
    known_x = [-30, -25, -22, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25, 30, 35, 40]
    # known power values read out from the graphs plotted in documentation. Only 35 °C and 55 °C available
    known_y = [
        [
            5700,
            5700,
            5700,
            5700,
            6290,
            7580,
            8660,
            9625,
            10300,
            10580,
            10750,
            10790,
            10830,
            11000,
            11000,
            11000,
        ],
        [
            5700,
            5700,
            5700,
            5700,
            6860,
            7300,
            8150,
            9500,
            10300,
            10580,
            10750,
            10790,
            10830,
            11000,
            11000,
            11000,
        ],
    ]

    # the known x values for linear interpolation
    known_t = [35, 55]

    # the aim is generating a 2D power map that gives back the actual power for a certain flow temperature and a given outside temperature
    # the map should have values on every integer temperature point
    # at first, all flow temoperatures are lineary interpolated

    _config_entry = None
    _steps = None
    _max_power = []
    _interp_y = []
    _r_to_interpolate = 0

    def __init__(self, config_entry: MyConfigEntry) -> None:
        """Initialise the PowerMap class."""
        # try to load values from json file
        self._config_entry = config_entry
        self._steps = 21
        self._max_power = []
        self._interp_y = []
        self._r_to_interpolate = 0

    async def initialize(self):
        """Initialize the power map."""
        try:
            filepath = (
                self._config_entry.runtime_data.config_dir
                + "/custom_components/"
                + CONST.DOMAIN
                + "/"
                + self._config_entry.data[CONF.KENNFELD_FILE]
            )
            async with aiofiles.open(filepath, encoding="utf-8") as openfile:
                raw_block = await openfile.read()
                json_object = json.loads(raw_block)
                self.known_x = json_object["known_x"]
                self.known_y = json_object["known_y"]
                self.known_t = json_object["known_t"]
                log.info("Reading power map file %s successful", filepath)
        except OSError:
            kennfeld = {
                "known_x": self.known_x,
                "known_y": self.known_y,
                "known_t": self.known_t,
            }
            async with aiofiles.open(filepath, "w", encoding="utf-8") as outfile:
                raw_block = json.dumps(kennfeld)
                await outfile.write(raw_block)
                log.info(
                    "Writing power map file %s with generic content successful",
                    filepath,
                )

        self._r_to_interpolate = np.linspace(
            self.known_t[0], self.known_t[1], self._steps
        )
        # the output matrix
        self._max_power = []
        self._interp_y = []

        # build the matrix with linear interpolated samples
        # 1st and last row are populated by known values from diagrem, the rest is zero
        self._interp_y.append(self.known_y[0])
        v = np.linspace(0, self._steps - 3, self._steps - 2)
        for _idx in v:
            self._interp_y.append(np.zeros_like(self.known_x))
        self._interp_y.append(self.known_y[1])

        for idx in range(len(self.known_x)):
            # the known y for every column
            yk = [self._interp_y[0][idx], self._interp_y[self._steps - 1][idx]]

            # linear interpolation
            ip = np.interp(self._r_to_interpolate, self.known_t, yk)

            # sort the interpolated values into the array
            for r in range(len(self._r_to_interpolate)):
                self._interp_y[r][idx] = ip[r]

        # at second step, power vs. outside temp are interpolated using cubic splines
        # we want to have samples at every integer °C
        t = np.linspace(-30, 40, 71)
        # cubic spline interpolation of power curves
        for idx in range(len(self._r_to_interpolate)):
            if SPLINE_AVAILABLE is True:
                f = CubicSpline(self.known_x, self._interp_y[idx], bc_type="natural")
            else:
                f = Chebyshev.fit(self.known_x, self._interp_y[idx], deg=8)
            self._max_power.append(f(t))

    def map(self, x, y):
        """Map."""
        x = x / 10 - self.known_x[0]
        x = max(x, 0)
        x = min(x, 70)
        y = y / 10 - self.known_t[0]
        y = max(y, 0)
        y = min(y, self._steps - 1)

        return self._max_power[int(y)][int(x)]


# map = PowerMap()

# plt.plot(t, np.transpose(map.max_power))
# plt.ylabel("Max Power")
# plt.xlabel("°C")
# plt.show()

# kennfeld = {'known_x': map.known_x,
#            'known_y': map.known_y,
#            'known_t': map.known_t}

# with open("sample1.json", "w") as outfile:
#    outfile.write(kennfeld)


# with open("sample2.json", "w") as outfile:
#    json.dump(kennfeld, outfile)

# with open('sample2.json', 'r') as openfile:

# Reading from json file
# json_object = json.load(openfile)

# map.known_x = json_object['known_x']
# map.known_y = json_object['known_y']
# map.known_t = json_object['known_t']

# print(map.known_x)
# print(map.known_y)
# print(map.known_t)
