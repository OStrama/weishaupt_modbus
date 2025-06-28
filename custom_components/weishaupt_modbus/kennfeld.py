"""Kennfeld power map for Weishaupt heat pumps."""

import json
import logging
from pathlib import Path
from typing import Any, Protocol

import aiofiles
import numpy as np
from numpy.polynomial import Chebyshev

from homeassistant.core import HomeAssistant

from .configentry import MyConfigEntry
from .const import CONF, CONST

_LOGGER = logging.getLogger(__name__)

# Check for optional dependencies
SPLINE_AVAILABLE = True
try:
    from scipy.interpolate import CubicSpline
except ImportError:
    _LOGGER.warning("Scipy not available, using less precise Chebyshev interpolation")
    SPLINE_AVAILABLE = False
    CubicSpline = None

MATPLOTLIB_AVAILABLE = True
try:
    import matplotlib.pyplot as plt
except ImportError:
    _LOGGER.warning("Matplotlib not available, cannot create power map image file")
    MATPLOTLIB_AVAILABLE = False
    plt = None


class InterpolationProtocol(Protocol):
    """Protocol for interpolation functions."""

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Evaluate the interpolation at given points."""
        ...


class ChebyshevWrapper:
    """Wrapper to make Chebyshev polynomial callable like CubicSpline."""

    def __init__(self, chebyshev: Chebyshev) -> None:
        """Initialize with a Chebyshev polynomial."""
        self._chebyshev = chebyshev

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Evaluate the Chebyshev polynomial at given points."""
        return self._chebyshev(x)


class PowerMap:
    """Power map for heat pump heating power calculations.

    Values extracted from characteristic curves in heat pump documentation:
    - Heating power vs. outside temperature @ 35°C flow temperature
    - Heating power vs. outside temperature @ 55°C flow temperature
    """

    # Known temperature points (°C)
    known_x: list[float] = [
        -30.0,
        -25.0,
        -22.0,
        -20.0,
        -15.0,
        -10.0,
        -5.0,
        0.0,
        5.0,
        10.0,
        15.0,
        20.0,
        25.0,
        30.0,
        35.0,
        40.0,
    ]

    # Known power values (W) at 35°C and 55°C flow temperatures
    known_y: list[list[float]] = [
        [
            5700.0,
            5700.0,
            5700.0,
            5700.0,
            6290.0,
            7580.0,
            8660.0,
            9625.0,
            10300.0,
            10580.0,
            10750.0,
            10790.0,
            10830.0,
            11000.0,
            11000.0,
            11000.0,
        ],
        [
            5700.0,
            5700.0,
            5700.0,
            5700.0,
            6860.0,
            7300.0,
            8150.0,
            9500.0,
            10300.0,
            10580.0,
            10750.0,
            10790.0,
            10830.0,
            11000.0,
            11000.0,
            11000.0,
        ],
    ]

    # Known flow temperatures (°C)
    known_t: list[float] = [35.0, 55.0]

    def __init__(self, config_entry: MyConfigEntry, hass: HomeAssistant) -> None:
        """Initialize the PowerMap class."""
        self.hass = hass
        self._config_entry = config_entry
        self._steps = 21
        self._max_power: list[np.ndarray] = []
        self._interp_y: list[list[float]] = []
        self._r_to_interpolate: np.ndarray | None = None
        self._all_t: np.ndarray | None = None

    async def initialize(self) -> None:
        """Initialize the power map from file or create default."""
        if self._config_entry is None:
            msg = "Config entry is None"
            raise ValueError(msg)

        filepath_base = get_filepath(self.hass)
        if filepath_base is None:
            msg = "Cannot determine file path for kennfeld file"
            raise ValueError(msg)

        filepath = filepath_base / self._config_entry.data[CONF.KENNFELD_FILE]

        try:
            async with aiofiles.open(filepath, encoding="utf-8") as openfile:
                raw_block = await openfile.read()
                json_object: dict[str, Any] = json.loads(raw_block)
                # Convert to float lists for type safety
                self.known_x = [float(x) for x in json_object["known_x"]]
                self.known_y = [
                    [float(y) for y in row] for row in json_object["known_y"]
                ]
                self.known_t = [float(t) for t in json_object["known_t"]]
                _LOGGER.debug("Reading power map file successful")
        except (OSError, json.JSONDecodeError, KeyError) as err:
            _LOGGER.debug("Creating default kennfeld file due to error: %s", err)
            kennfeld: dict[str, Any] = {
                "known_x": self.known_x,
                "known_y": self.known_y,
                "known_t": self.known_t,
            }
            try:
                async with aiofiles.open(filepath, "w", encoding="utf-8") as outfile:
                    raw_block = json.dumps(kennfeld, indent=2)
                    await outfile.write(raw_block)
                    _LOGGER.debug("Created default power map file")
            except OSError as write_err:
                _LOGGER.warning("Failed to create kennfeld file: %s", write_err)

        # Perform interpolation calculations
        await self._perform_interpolation()

    async def _perform_interpolation(self) -> None:
        """Perform interpolation calculations."""
        self._r_to_interpolate = np.linspace(
            start=self.known_t[0], stop=self.known_t[1], num=self._steps
        )

        # Initialize output matrices
        self._max_power = []
        self._interp_y = []

        # Build matrix with linear interpolated samples
        # First and last rows are populated by known values, rest is zero
        self._interp_y.append(self.known_y[0].copy())

        # Create intermediate rows filled with zeros
        for _ in range(self._steps - 2):
            self._interp_y.append([0.0] * len(self.known_x))

        self._interp_y.append(self.known_y[1].copy())

        # Linear interpolation for each outside temperature point
        for idx in range(len(self.known_x)):
            # Known y values for current column
            yk = [
                self._interp_y[0][idx],
                self._interp_y[self._steps - 1][idx],
            ]

            # Linear interpolation between flow temperatures
            ip = np.interp(self._r_to_interpolate, self.known_t, yk)

            # Sort interpolated values into the array
            for r in range(len(self._r_to_interpolate)):
                self._interp_y[r][idx] = float(ip[r])

        # Second step: interpolate power vs. outside temperature
        # Sample at every integer °C
        self._all_t = np.linspace(start=-30.0, stop=40.0, num=71)

        # Interpolation of power curves
        for idx in range(len(self._r_to_interpolate)):
            interpolation_func = self._create_interpolation_func(
                np.array(self.known_x), np.array(self._interp_y[idx])
            )

            if interpolation_func is not None:
                try:
                    interpolated_values = interpolation_func(self._all_t)
                    self._max_power.append(interpolated_values)
                except Exception as exc:
                    _LOGGER.warning("Interpolation failed for index %d: %s", idx, exc)
                    # Use linear interpolation as fallback
                    linear_values = np.interp(
                        self._all_t, self.known_x, self._interp_y[idx]
                    )
                    self._max_power.append(linear_values)
            else:
                # Ultimate fallback - use linear interpolation
                linear_values = np.interp(
                    self._all_t, self.known_x, self._interp_y[idx]
                )
                self._max_power.append(linear_values)

        # Plot kennfeld if matplotlib is available
        if (
            MATPLOTLIB_AVAILABLE
            and plt is not None
            and self._config_entry.runtime_data is not None
        ):
            try:
                await self.hass.async_add_executor_job(self.plot_kennfeld_to_file)
            except RuntimeError as exc:
                _LOGGER.warning("Error plotting kennfeld: %s", exc)

    def _create_interpolation_func(
        self, x_data: np.ndarray, y_data: np.ndarray
    ) -> InterpolationProtocol | None:
        """Create interpolation function with fallback strategy."""
        # Validate input data
        if len(x_data) != len(y_data) or len(x_data) < 2:
            _LOGGER.debug("Invalid data for interpolation")
            return None

        if SPLINE_AVAILABLE and CubicSpline is not None:
            try:
                return CubicSpline(x_data, y_data, bc_type="natural")
            except Exception as exc:
                _LOGGER.debug("CubicSpline failed, using Chebyshev: %s", exc)

        # Fallback to Chebyshev
        try:
            degree = min(8, len(x_data) - 1)  # Ensure degree is valid
            cheb = Chebyshev.fit(x_data, y_data, deg=degree)
            return ChebyshevWrapper(cheb)
        except Exception as exc:
            _LOGGER.warning("Chebyshev interpolation failed: %s", exc)
            return None

    def map(self, outside_temp: float, flow_temp: float) -> float:
        """Map outside temperature and flow temperature to heating power."""
        if not self._max_power or self._all_t is None or self._r_to_interpolate is None:
            msg = "PowerMap not initialized"
            raise ValueError(msg)

        # Convert temperatures to array indices
        x_idx = int((outside_temp + 30) * 71 / 70)  # Map -30 to 40°C range to 0-70
        x_idx = max(0, min(70, x_idx))

        y_idx = int(
            (flow_temp - self.known_t[0])
            / (self.known_t[1] - self.known_t[0])
            * (self._steps - 1)
        )
        y_idx = max(0, min(self._steps - 1, y_idx))

        return float(self._max_power[y_idx][x_idx])

    def plot_kennfeld_to_file(self) -> None:
        """Plot kennfeld to file (runs in executor)."""
        if not MATPLOTLIB_AVAILABLE or plt is None:
            return

        if not self._max_power or self._all_t is None or self._r_to_interpolate is None:
            _LOGGER.warning("PowerMap not fully initialized")
            return

        try:
            # Create the plot
            fig, ax = plt.subplots(figsize=(10, 6))

            ax.plot(self._all_t, np.transpose(self._max_power))
            ax.set_ylabel("Max Power (W)")
            ax.set_xlabel("Outside Temperature (°C)")
            ax.set_title("Heat Pump Power Map")
            ax.grid(True)
            ax.set_xlim(-25, 40)
            ax.set_ylim(2000, 12000)

            # Add legend for flow temperatures
            legend_temps = self._r_to_interpolate[::4]  # Every 4th temperature
            ax.legend(
                [f"{temp:.1f}°C" for temp in legend_temps], title="Flow Temperature"
            )

            # Save plot
            if (
                self._config_entry is not None
                and self._config_entry.runtime_data is not None
            ):
                config_dir = self._config_entry.runtime_data.config_dir
                filepath = (
                    Path(config_dir) / "www" / "local" / f"{CONST.DOMAIN}_powermap.png"
                )

                # Ensure directory exists
                filepath.parent.mkdir(parents=True, exist_ok=True)
                fig.savefig(filepath, dpi=150, bbox_inches="tight")
                _LOGGER.debug("Power map image saved")

            plt.close(fig)

        except Exception as exc:
            _LOGGER.warning("Failed to create kennfeld plot: %s", exc)


def get_filepath(hass: HomeAssistant) -> Path | None:
    """Get the file path for kennfeld data storage."""
    if hass.config.config_dir is None:
        _LOGGER.error("Home Assistant config directory not available")
        return None

    # Try main config directory first
    filepath = Path(hass.config.config_dir) / "custom_components" / CONST.DOMAIN

    if filepath.exists():
        return filepath

    # Fall back to package directory
    filepath = Path(__file__).resolve().parent
    if filepath.exists():
        return filepath

    # No valid path found
    return None
