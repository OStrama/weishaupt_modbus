"""Heat pump characteristic curves (Kennfeld) runtime, auto-compilation, and Pygal plotting engine."""

import importlib.util
import json
import logging
from pathlib import Path
import shutil
from typing import Any

import aiofiles

from homeassistant.core import HomeAssistant

from .configentry import MyConfigEntry
from .const import CONF, CONST

_LOGGER = logging.getLogger(__name__)

# --- DEVELOPER CONFIGURATION OPTIONS ---
# If True, scans the entire directory on boot and compiles missing data grids.
COMPILE_ALL_MISSING: bool = True

# If True, checks if the SVG graph for the pre-compiled file is missing,
# auto-generates it locally using Pygal, and copies it to /www/local/.
CREATE_MISSING_PLOTS: bool = True

# --- SAFE RUNTIME ENVIRONMENT CHECKS ---
NUMPY_AVAILABLE = importlib.util.find_spec("numpy") is not None
SCIPY_AVAILABLE = importlib.util.find_spec("scipy") is not None
PYGAL_AVAILABLE = importlib.util.find_spec("pygal") is not None

if not NUMPY_AVAILABLE:
    _LOGGER.warning(
        "Numpy is not available. Raw power map compilation will be disabled."
    )

if not SCIPY_AVAILABLE:
    _LOGGER.warning(
        "SciPy is not available. CubicSpline high-precision compilation is disabled."
    )

if not PYGAL_AVAILABLE:
    _LOGGER.warning(
        "Pygal is not available. Adding 'pygal' to manifest.json is recommended "
        "to enable dynamic SVG dashboard maps."
    )


class PowerMap:
    """PowerMap class that loads pre-compiled grids and renders dynamic Pygal SVG graphs."""

    def __init__(self, config_entry: MyConfigEntry, hass: HomeAssistant) -> None:
        """Initialize the PowerMap."""
        self.hass = hass
        self._config_entry = config_entry
        self._compiled_grid: dict[str, list[float]] = {}
        self._known_t: list[int] = [35, 55]
        self._out_range_raw: list[int] = [-300, 400]

    async def initialize(self) -> None:
        """Load the JSON. Auto-compiles and writes back once if compiled_grid is missing."""
        filepath = Path(
            get_filepath(self.hass) / self._config_entry.data[CONF.KENNFELD_FILE]
        )

        # 1. Optionally compile all missing grids in the folder first (non-blocking)
        if COMPILE_ALL_MISSING:
            if NUMPY_AVAILABLE:
                _LOGGER.info("Scanning for missing pre-compiled grids...")
                await self.hass.async_add_executor_job(
                    self._compile_all_missing_blocking
                )
            else:
                _LOGGER.error(
                    "Cannot compile missing curves: Numpy is missing on this host."
                )

        # 2. Load the specific active configuration curve
        try:
            async with aiofiles.open(filepath, encoding="utf-8") as openfile:
                raw_block = await openfile.read()
                data = json.loads(raw_block)

                # Track boundaries
                self._known_t = sorted(data.get("known_t", [35, 55]))
                known_x = data.get("known_x", [-30, 40])
                self._out_range_raw = [min(known_x) * 10, max(known_x) * 10]

                # 3. High-performance path: Compiled grid exists
                if "compiled_grid" in data:
                    self._compiled_grid = data["compiled_grid"]
                    _LOGGER.info(
                        "Using pre-compiled 0.1°C outside-grouped grid: %s",
                        filepath.name,
                    )

                    # Generate the preview plot if missing and allowed
                    if CREATE_MISSING_PLOTS and PYGAL_AVAILABLE:
                        svg_path = filepath.with_suffix(".svg")
                        if not svg_path.exists():
                            _LOGGER.warning(
                                "Generating missing SVG plot for pre-compiled: %s",
                                filepath.name,
                            )
                            await self.hass.async_add_executor_job(
                                self._generate_plot_blocking, data, filepath
                            )

                    # Safely copy the matching preview SVG to Home Assistant's local www directory
                    www_dir = Path(f"{self.hass.config.config_dir}/www/local")
                    await self.hass.async_add_executor_job(
                        self._copy_powermap_plot, filepath, www_dir
                    )
                    return

                # 4. Fallback for the active curve if COMPILE_ALL_MISSING was False
                if not NUMPY_AVAILABLE:
                    _LOGGER.error(
                        "Cannot compile raw curve: Numpy is missing on this host."
                    )
                    return

                _LOGGER.warning(
                    "Pre-compiled grid missing in %s. Compiling once...", filepath.name
                )
                self._compiled_grid = await self.hass.async_add_executor_job(
                    self._compile_and_save_kennfeld_blocking, data, filepath
                )

                # Copy the freshly generated preview SVG to Home Assistant's local www directory
                www_dir = Path(f"{self.hass.config.config_dir}/www/local")
                await self.hass.async_add_executor_job(
                    self._copy_powermap_plot, filepath, www_dir
                )

        except OSError as err:
            _LOGGER.error("Failed to load power map file %s: %s", filepath, err)

    def _compile_all_missing_blocking(self) -> None:
        """Scan the directory and compile any raw curves that lack compiled_grid.

        Runs inside Home Assistant's executor thread pool.
        """
        folder = get_filepath(self.hass)
        if not folder or not folder.exists():
            return

        for filepath in folder.glob("weishaupt*.json"):
            try:
                with filepath.open("r", encoding="utf-8") as f:
                    data = json.load(f)

                # Check if the grid compilation is missing
                if "compiled_grid" not in data:
                    _LOGGER.warning("Auto-compiling missing grid in: %s", filepath.name)
                    known_x = data.get("known_x", [-30, 40])
                    self._out_range_raw = [min(known_x) * 10, max(known_x) * 10]
                    self._compile_and_save_kennfeld_blocking(data, filepath)
                # Check if only the SVG plot is missing and we want to generate it
                elif CREATE_MISSING_PLOTS and PYGAL_AVAILABLE:
                    svg_path = filepath.with_suffix(".svg")
                    if not svg_path.exists():
                        _LOGGER.warning(
                            "Generating missing SVG plot for pre-compiled: %s",
                            filepath.name,
                        )
                        self._generate_plot_blocking(data, filepath)
            except Exception as err:  # noqa: BLE001
                _LOGGER.error(
                    "Failed to compile missing grid for %s: %s", filepath.name, err
                )

    def _compile_and_save_kennfeld_blocking(
        self, data: dict[str, Any], filepath: Path
    ) -> dict[str, list[float]]:
        """Run CubicSpline compilation and write the compact grid back to the JSON file."""
        # On-demand import of Numpy (executed safely inside the thread pool)
        import numpy as np  # noqa: PLC0415

        known_x = data["known_x"]
        known_y = data["known_y"]
        known_t = sorted(data["known_t"])
        raw_range = range(self._out_range_raw[0], self._out_range_raw[1] + 1)

        # On-demand import of SciPy (CubicSpline)
        use_scipy = SCIPY_AVAILABLE
        if use_scipy:
            try:
                from scipy.interpolate import CubicSpline  # noqa: PLC0415
            except ImportError:
                use_scipy = False

        splines = []
        for r_idx in range(len(known_t)):
            if use_scipy and CubicSpline is not None:
                f = CubicSpline(known_x, known_y[r_idx], bc_type="natural")
            else:
                _LOGGER.warning(
                    "SciPy fallback: Using Chebyshev interpolation for: %s",
                    filepath.name,
                )
                from numpy.polynomial import Chebyshev  # noqa: PLC0415

                f = Chebyshev.fit(known_x, known_y[r_idx], deg=8)
            splines.append(f)

        compiled_grid = {}
        for out_val_raw in raw_range:
            compiled_grid[str(out_val_raw)] = [
                round(float(sp(out_val_raw / 10.0)), 1) for sp in splines
            ]

        # Inject and save compactly
        data["compiled_grid"] = compiled_grid

        lines = []
        lines.append("{")
        lines.append(f'  "known_x": {json.dumps(known_x)},')
        lines.append(f'  "known_y": {json.dumps(known_y)},')
        lines.append(f'  "known_t": {json.dumps(known_t)},')
        lines.append('  "compiled_grid": {')
        out_keys = sorted(compiled_grid.keys(), key=int)
        for out_k in out_keys:
            comma = "," if out_k != out_keys[-1] else ""
            lines.append(f'    "{out_k}": {compiled_grid[out_k]}{comma}')
        lines.append("  }")
        lines.append("}")

        try:
            with filepath.open("w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            _LOGGER.info(
                "Injected and saved compact compiled grid back to: %s", filepath.name
            )
        except OSError as err:
            _LOGGER.error("Failed to save compiled power map to disk: %s", err)

        # Plot the curves to SVG if Pygal is available
        if PYGAL_AVAILABLE:
            self._generate_plot_blocking(data, filepath)

        return compiled_grid

    def _generate_plot_blocking(self, data: dict[str, Any], filepath: Path) -> None:
        """Generate an SVG plot using Pygal."""
        if not PYGAL_AVAILABLE:
            return

        import pygal  # noqa: PLC0415
        from pygal.style import Style  # noqa: PLC0415

        compiled_grid = data.get("compiled_grid")
        known_t = sorted(data.get("known_t", [35, 55]))
        known_x = data.get("known_x", [-30, 40])

        # Determine the ranges
        out_min_raw = min(known_x) * 10
        out_max_raw = max(known_x) * 10
        raw_range = range(
            out_min_raw, out_max_raw + 10, 10
        )  # 1°C steps for rendering speed

        # Custom dark-theme style to match Home Assistant Cards
        custom_style = Style(
            background="#1c1c1e",
            plot_background="#1c1c1e",
            foreground="#e5e5ea",
            foreground_strong="#ffffff",
            foreground_subtle="#8e8e93",
            colors=("#30d158", "#0a84ff", "#ff453a", "#bf5af2"),
            stroke_width=2.5,
        )

        try:
            chart = pygal.XY(
                stroke=True,
                show_dots=False,
                width=500,
                height=320,
                style=custom_style,
                legend_at_bottom=True,
            )
            chart.title = f"Kennfeld Heizleistung - {filepath.stem}"

            for r_idx, flow_val in enumerate(known_t):
                # Retrieve the values for this flow temperature curve
                curve_points = []
                for r in raw_range:
                    if str(r) in compiled_grid:
                        curve_points.append((r / 10.0, compiled_grid[str(r)][r_idx]))

                if curve_points:
                    chart.add(f"{flow_val}°C Vorlauf", curve_points)

            svg_path = filepath.with_suffix(".svg")
            chart.render_to_file(str(svg_path))
            _LOGGER.info("Successfully generated missing SVG plot: %s", svg_path.name)
        except Exception as err:  # noqa: BLE001
            _LOGGER.debug("Pygal SVG plot generation failed: %s", err)

    def generate_svg_plot_blocking(
        self, outside_temp_raw: float, flow_temp_raw: float
    ) -> None:
        """Generate a dynamic vector SVG plot of the curves and mark the current operating point.

        Requires only the lightweight, pure-Python Pygal library.
        """
        if not PYGAL_AVAILABLE or not self._compiled_grid:
            return

        import pygal  # noqa: PLC0415
        from pygal.style import Style  # noqa: PLC0415

        # Operational variables
        curr_out = outside_temp_raw / 10.0
        curr_flow = flow_temp_raw / 10.0
        curr_power = self.map(outside_temp_raw, flow_temp_raw)

        # Custom dark-theme style matching Home Assistant Cards
        custom_style = Style(
            background="#1c1c1e",
            plot_background="#1c1c1e",
            foreground="#e5e5ea",
            foreground_strong="#ffffff",
            foreground_subtle="#8e8e93",
            colors=("#30d158", "#0a84ff", "#ff453a", "#bf5af2"),
            stroke_width=2.5,
        )

        try:
            chart = pygal.XY(
                stroke=True,
                show_dots=False,
                width=500,
                height=320,
                style=custom_style,
                legend_at_bottom=True,
            )
            chart.title = f"Betriebspunkt Kennfeld ({curr_power / 1000:.1f} kW) | VL: {curr_flow:.1f}°C | AT: {curr_out:.1f}°C"

            # 1. Add compiled curves
            for r_idx, flow_val in enumerate(self._known_t):
                curve_points = []
                for r in range(self._out_range_raw[0], self._out_range_raw[1] + 10, 10):
                    if str(r) in self._compiled_grid:
                        curve_points.append(
                            (r / 10.0, self._compiled_grid[str(r)][r_idx])
                        )

                if curve_points:
                    chart.add(f"{flow_val}°C Vorlauf", curve_points)

            # 2. Add the dynamic operating point dot
            chart.add(
                "Betriebspunkt",
                [(curr_out, curr_power)],
                show_dots=True,
                dots_size=6,
                stroke=False,
            )

            # 3. Save directly to local www directory
            www_dir = Path(f"{self.hass.config.config_dir}/www/local")
            www_dir.mkdir(parents=True, exist_ok=True)

            svg_path = www_dir / f"{CONST.DOMAIN}_powermap.svg"
            chart.render_to_file(str(svg_path))
            _LOGGER.debug(
                "Dynamic power map SVG updated successfully: %s", svg_path.name
            )

        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Failed to generate dynamic power map SVG: %s", err)

    def _copy_powermap_plot(self, json_filepath: Path, www_dir: Path) -> None:
        """Copy the compiled SVG from the kennfeld folder to Home Assistant's local www directory.

        Runs inside the executor thread pool.
        """
        png_src = json_filepath.with_suffix(".svg")
        if not png_src.exists():
            _LOGGER.debug("No power map plot found at %s to copy", png_src.name)
            return

        try:
            # Ensure the /config/www/local directory exists
            www_dir.mkdir(parents=True, exist_ok=True)

            # Destination file path
            png_dest = www_dir / f"{CONST.DOMAIN}_powermap.svg"

            # Perform metadata-preserving copy
            shutil.copy2(png_src, png_dest)
            _LOGGER.info(
                "Successfully updated dashboard power map image: %s", png_dest.name
            )
        except OSError as err:
            _LOGGER.error(
                "Failed to copy power map image to local www directory: %s", err
            )

    def map(self, outside_temp_raw: float, flow_temp_raw: float) -> float:
        """Map raw temperature values using 1D flow temperature interpolation on the compact grid."""
        if not self._compiled_grid:
            return 0.0

        # Convert flow temp to actual °C for fractional interpolation
        flow_temp = flow_temp_raw / 10

        # Clamp raw outside temperature and actual flow temperature
        outside_raw = max(
            self._out_range_raw[0],
            min(round(outside_temp_raw), self._out_range_raw[1]),
        )
        flow_temp = max(
            float(self._known_t[0]), min(flow_temp, float(self._known_t[-1]))
        )

        # 1. Direct O(1) outside temperature key lookup
        vals = self._compiled_grid.get(str(outside_raw))
        if not vals:
            return 0.0

        # 2. Find surrounding Flow Temp curve intervals in known_t
        y0_idx = 0
        for i in range(len(self._known_t) - 1):
            if self._known_t[i] <= flow_temp <= self._known_t[i + 1]:
                y0_idx = i
                break
        else:
            if flow_temp < self._known_t[0]:
                y0_idx = 0
            else:
                y0_idx = len(self._known_t) - 2
        y1_idx = y0_idx + 1

        # 3. Grab the 2 flow temp boundary values at this outside temperature
        p0 = vals[y0_idx]  # flow y0
        p1 = vals[y1_idx]  # flow y1

        # Calculate fractional flow temp delta
        dy = (flow_temp - self._known_t[y0_idx]) / (
            self._known_t[y1_idx] - self._known_t[y0_idx]
        )

        # 1D Linear Interpolation between the curves
        return p0 + dy * (p1 - p0)


def get_filepath(hass: HomeAssistant) -> Path:
    """Get the filepath to the custom component directory."""
    filepath = Path(
        f"{hass.config.config_dir}/custom_components/{CONST.DOMAIN}/kennfeld"
    )
    if not filepath.exists():
        filepath = Path(Path(__file__).resolve().parent)
    return filepath
