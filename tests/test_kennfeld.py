import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.weishaupt_modbus.const import CONF, CONST
from custom_components.weishaupt_modbus.kennfeld.kennfeld import PowerMap, get_filepath
import pytest


def create_power_map() -> PowerMap:
    """Create a PowerMap with a mocked config entry and Home Assistant."""
    hass = MagicMock()
    config_entry = MagicMock()

    return PowerMap(config_entry, hass)


def test_map_without_compiled_grid() -> None:
    """Return zero when no compiled grid is available."""
    power_map = create_power_map()

    assert power_map.map(100, 450) == 0.0


def test_map_missing_outside_temperature() -> None:
    """Return zero when the outside temperature is not in the grid."""
    power_map = create_power_map()
    power_map._compiled_grid = {
        "100": [1000.0, 800.0],
    }

    assert power_map.map(200, 450) == 0.0


def test_map_exact_flow_temperature() -> None:
    """Return the exact value when flow temperature matches a curve."""
    power_map = create_power_map()
    power_map._compiled_grid = {
        "100": [1000.0, 800.0],
    }

    assert power_map.map(100, 350) == 1000.0
    assert power_map.map(100, 550) == 800.0


def test_map_interpolates_flow_temperature() -> None:
    """Interpolate between two flow temperature curves."""
    power_map = create_power_map()
    power_map._compiled_grid = {
        "100": [1000.0, 800.0],
    }

    assert power_map.map(100, 450) == 900.0


def test_map_clamps_flow_temperature_below_range() -> None:
    """Clamp flow temperature below the known range."""
    power_map = create_power_map()
    power_map._compiled_grid = {
        "100": [1000.0, 800.0],
    }

    assert power_map.map(100, 200) == 1000.0


def test_map_clamps_flow_temperature_above_range() -> None:
    """Clamp flow temperature above the known range."""
    power_map = create_power_map()
    power_map._compiled_grid = {
        "100": [1000.0, 800.0],
    }

    assert power_map.map(100, 700) == 800.0


def test_map_clamps_outside_temperature() -> None:
    """Clamp outside temperature to the configured range."""
    power_map = create_power_map()
    power_map._compiled_grid = {
        "-300": [1000.0, 800.0],
        "400": [500.0, 300.0],
    }

    assert power_map.map(-500, 350) == 1000.0
    assert power_map.map(500, 350) == 500.0


def test_map_uses_intermediate_flow_curve() -> None:
    """Use the correct pair of curves for multiple flow temperatures."""
    power_map = create_power_map()
    power_map._known_t = [35, 45, 55]
    power_map._compiled_grid = {
        "100": [1000.0, 800.0, 600.0],
    }

    assert power_map.map(100, 400) == 900.0
    assert power_map.map(100, 500) == 700.0


def test_copy_powermap_plot_source_missing(tmp_path: Path) -> None:
    """Do nothing when the source SVG does not exist."""
    power_map = create_power_map()

    json_filepath = tmp_path / "weishaupt_wbb.json"
    www_dir = tmp_path / "www" / "local"

    power_map._copy_powermap_plot(json_filepath, www_dir)

    assert not www_dir.exists()


def test_copy_powermap_plot(tmp_path: Path) -> None:
    """Copy the SVG to the Home Assistant local directory."""
    power_map = create_power_map()

    json_filepath = tmp_path / "weishaupt_wbb.json"
    svg_filepath = json_filepath.with_suffix(".svg")
    svg_filepath.write_text("<svg>test</svg>", encoding="utf-8")

    www_dir = tmp_path / "www" / "local"

    power_map._copy_powermap_plot(json_filepath, www_dir)

    destination = www_dir / f"{CONST.DOMAIN}_powermap.svg"

    assert destination.exists()
    assert destination.read_text(encoding="utf-8") == "<svg>test</svg>"


def test_copy_powermap_plot_os_error(tmp_path: Path) -> None:
    """Handle an OSError while copying the SVG."""
    power_map = create_power_map()

    json_filepath = tmp_path / "weishaupt_wbb.json"
    svg_filepath = json_filepath.with_suffix(".svg")
    svg_filepath.write_text("<svg>test</svg>", encoding="utf-8")

    www_dir = tmp_path / "www" / "local"

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.shutil.copy2",
        side_effect=OSError("copy failed"),
    ):
        power_map._copy_powermap_plot(json_filepath, www_dir)


def test_get_filepath_uses_integration_directory(tmp_path: Path) -> None:
    """Return the integration kennfeld directory when it exists."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    expected = tmp_path / "custom_components" / CONST.DOMAIN / "kennfeld"
    expected.mkdir(parents=True)

    assert get_filepath(hass) == expected


def test_get_filepath_falls_back_to_module_directory(tmp_path: Path) -> None:
    """Fall back to the module directory when the configured path does not exist."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    expected = (
        Path(__file__).resolve().parents[1]
        / "custom_components"
        / CONST.DOMAIN
        / "kennfeld"
    )

    assert get_filepath(hass) == expected


def test_compile_and_save_kennfeld(tmp_path: Path) -> None:
    """Compile a characteristic map and save the result."""
    power_map = create_power_map()
    power_map._out_range_raw = [0, 20]

    data = {
        "known_x": [0, 1, 2],
        "known_y": [
            [100.0, 110.0, 120.0],
            [200.0, 210.0, 220.0],
        ],
        "known_t": [35, 55],
    }

    filepath = tmp_path / "kennfeld.json"

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
        False,
    ):
        result = power_map._compile_and_save_kennfeld_blocking(
            data,
            filepath,
        )

    assert result
    assert "compiled_grid" in data
    assert filepath.exists()

    saved = json.loads(filepath.read_text(encoding="utf-8"))

    assert "compiled_grid" in saved
    assert saved["known_x"] == [0, 1, 2]
    assert saved["known_t"] == [35, 55]


def test_compile_and_save_kennfeld_write_error(tmp_path: Path) -> None:
    """Log an error when the compiled map cannot be written."""
    power_map = create_power_map()
    power_map._out_range_raw = [0, 20]

    data = {
        "known_x": [0, 1, 2],
        "known_y": [
            [100.0, 110.0, 120.0],
            [200.0, 210.0, 220.0],
        ],
        "known_t": [35, 55],
    }

    filepath = tmp_path / "kennfeld.json"

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
            False,
        ),
        patch.object(
            Path,
            "open",
            side_effect=OSError("write failed"),
        ),
    ):
        result = power_map._compile_and_save_kennfeld_blocking(
            data,
            filepath,
        )

    assert result
    assert "compiled_grid" in data


def test_compile_and_save_kennfeld_without_scipy(tmp_path: Path) -> None:
    """Use NumPy Chebyshev interpolation when SciPy is unavailable."""
    power_map = create_power_map()
    power_map._out_range_raw = [0, 20]

    data = {
        "known_x": list(range(9)),
        "known_y": [
            [100.0 + x for x in range(9)],
            [200.0 + x for x in range(9)],
        ],
        "known_t": [35, 55],
    }

    filepath = tmp_path / "kennfeld.json"

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.SCIPY_AVAILABLE",
            False,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
            False,
        ),
    ):
        result = power_map._compile_and_save_kennfeld_blocking(
            data,
            filepath,
        )

    assert result
    assert "compiled_grid" in data
    assert filepath.exists()


@pytest.mark.asyncio
async def test_initialize_with_compiled_grid(tmp_path: Path) -> None:
    """Load an existing compiled characteristic map."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    hass.config.config_dir = str(tmp_path)

    config_entry = MagicMock()
    config_entry.data = {
        CONF.KENNFELD_FILE: "kennfeld.json",
    }

    filepath = tmp_path / "custom_components" / CONST.DOMAIN / "kennfeld"
    filepath.mkdir(parents=True)

    data = {
        "known_t": [55, 35],
        "known_x": [-30, 40],
        "compiled_grid": {
            "-300": [1000.0, 800.0],
            "400": [500.0, 300.0],
        },
    }

    (filepath / "kennfeld.json").write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    power_map = PowerMap(config_entry, hass)

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.COMPILE_ALL_MISSING",
            False,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.CREATE_MISSING_PLOTS",
            False,
        ),
    ):
        await power_map.initialize()

    assert power_map._known_t == [35, 55]
    assert power_map._out_range_raw == [-300, 400]
    assert power_map._compiled_grid == data["compiled_grid"]


@pytest.mark.asyncio
async def test_initialize_compiles_missing_grid(tmp_path: Path) -> None:
    """Compile and load a characteristic map without a compiled grid."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)
    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))
    hass.config.config_dir = str(tmp_path)

    config_entry = MagicMock()
    config_entry.data = {
        CONF.KENNFELD_FILE: "kennfeld.json",
    }

    filepath = tmp_path / "custom_components" / CONST.DOMAIN / "kennfeld"
    filepath.mkdir(parents=True)

    data = {
        "known_t": [35, 55],
        "known_x": [0, 1, 2, 3],
        "known_y": [
            [100.0, 110.0, 120.0, 130.0],
            [200.0, 210.0, 220.0, 230.0],
        ],
    }

    (filepath / "kennfeld.json").write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    power_map = PowerMap(config_entry, hass)

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.COMPILE_ALL_MISSING",
            False,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
            False,
        ),
    ):
        await power_map.initialize()

    assert power_map._compiled_grid
    assert power_map._known_t == [35, 55]
    assert power_map._out_range_raw == [0, 30]


@pytest.mark.asyncio
async def test_initialize_without_numpy(tmp_path: Path) -> None:
    """Log an error when NumPy is unavailable."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    config_entry = MagicMock()
    config_entry.data = {
        CONF.KENNFELD_FILE: "kennfeld.json",
    }

    filepath = tmp_path / "custom_components" / CONST.DOMAIN / "kennfeld"
    filepath.mkdir(parents=True)

    data = {
        "known_t": [35, 55],
        "known_x": [0, 2],
        "known_y": [
            [100.0, 110.0, 120.0],
            [200.0, 210.0, 220.0],
        ],
    }

    (filepath / "kennfeld.json").write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    power_map = PowerMap(config_entry, hass)

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.COMPILE_ALL_MISSING",
            False,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.NUMPY_AVAILABLE",
            False,
        ),
    ):
        await power_map.initialize()

    assert power_map._compiled_grid == {}


@pytest.mark.asyncio
async def test_initialize_file_error(tmp_path: Path) -> None:
    """Handle an error while opening the characteristic map."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    config_entry = MagicMock()
    config_entry.data = {
        CONF.KENNFELD_FILE: "missing.json",
    }

    power_map = PowerMap(config_entry, hass)

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.COMPILE_ALL_MISSING",
        False,
    ):
        await power_map.initialize()

    assert power_map._compiled_grid == {}


def test_compile_all_missing_no_folder(tmp_path: Path) -> None:
    """Do nothing when the characteristic-map folder does not exist."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    power_map = PowerMap(MagicMock(), hass)

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.get_filepath",
        return_value=tmp_path / "missing",
    ):
        power_map._compile_all_missing_blocking()


def test_compile_all_missing_compiles_uncompiled_file(tmp_path: Path) -> None:
    """Compile characteristic maps that do not have a compiled grid."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    folder = tmp_path / "kennfeld"
    folder.mkdir()

    filepath = folder / "weishaupt_test.json"
    data = {
        "known_t": [35, 55],
        "known_x": [0, 1, 2, 3],
        "known_y": [
            [100.0, 110.0, 120.0, 130.0],
            [200.0, 210.0, 220.0, 230.0],
        ],
    }
    filepath.write_text(json.dumps(data), encoding="utf-8")

    power_map = PowerMap(MagicMock(), hass)

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.get_filepath",
            return_value=folder,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
            False,
        ),
    ):
        power_map._compile_all_missing_blocking()

    saved = json.loads(filepath.read_text(encoding="utf-8"))

    assert "compiled_grid" in saved


def test_compile_all_missing_handles_invalid_json(tmp_path: Path) -> None:
    """Log and continue when a characteristic-map file is invalid."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    filepath = tmp_path / "weishaupt_invalid.json"
    filepath.write_text("{ invalid json", encoding="utf-8")

    power_map = PowerMap(MagicMock(), hass)

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.get_filepath",
        return_value=tmp_path,
    ):
        power_map._compile_all_missing_blocking()


def test_generate_plot_blocking(tmp_path: Path) -> None:
    """Generate a characteristic-map plot."""
    power_map = create_power_map()

    data = {
        "known_t": [35, 55],
        "known_x": [0, 1, 2],
        "compiled_grid": {
            "0": [100.0, 200.0],
            "10": [110.0, 210.0],
            "20": [120.0, 220.0],
        },
    }

    filepath = tmp_path / "kennfeld.json"

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
        True,
    ):
        power_map._generate_plot_blocking(data, filepath)

    assert filepath.with_suffix(".svg").exists()


def test_generate_plot_blocking_handles_error(tmp_path: Path) -> None:
    """Handle errors while generating a characteristic-map plot."""
    power_map = create_power_map()

    data = {
        "known_t": [35, 55],
        "known_x": [0, 1],
        "compiled_grid": {
            "0": [100.0, 200.0],
            "10": [110.0, 210.0],
        },
    }

    filepath = tmp_path / "kennfeld.json"

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
            True,
        ),
        patch(
            "pygal.XY",
            side_effect=RuntimeError("plot failed"),
        ),
    ):
        power_map._generate_plot_blocking(data, filepath)


def test_generate_svg_plot_blocking_without_pygal() -> None:
    """Do nothing when Pygal is unavailable."""
    power_map = create_power_map()

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
        False,
    ):
        power_map.generate_svg_plot_blocking(0, 0)


def test_generate_svg_plot_blocking_without_compiled_grid() -> None:
    """Do nothing when no compiled power map is available."""
    power_map = create_power_map()

    power_map._compiled_grid = {}

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
        True,
    ):
        power_map.generate_svg_plot_blocking(0, 0)


def test_generate_svg_plot_blocking(tmp_path: Path) -> None:
    """Generate the current power-map SVG."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    power_map = PowerMap(MagicMock(), hass)
    power_map._known_t = [35, 55]
    power_map._out_range_raw = [0, 20]
    power_map._compiled_grid = {
        "0": [100.0, 200.0],
        "10": [110.0, 210.0],
        "20": [120.0, 220.0],
    }

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
        True,
    ):
        power_map.generate_svg_plot_blocking(10, 450)

    svg_path = tmp_path / "www" / "local" / f"{CONST.DOMAIN}_powermap.svg"

    assert svg_path.exists()


def test_generate_svg_plot_blocking_handles_error(tmp_path: Path) -> None:
    """Handle errors while generating the current power-map SVG."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    power_map = PowerMap(MagicMock(), hass)
    power_map._known_t = [35, 55]
    power_map._out_range_raw = [0, 20]
    power_map._compiled_grid = {
        "0": [100.0, 200.0],
        "10": [110.0, 210.0],
        "20": [120.0, 220.0],
    }

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
            True,
        ),
        patch(
            "pygal.XY",
            side_effect=RuntimeError("plot failed"),
        ),
    ):
        power_map.generate_svg_plot_blocking(10, 450)


@pytest.mark.asyncio
async def test_initialize_without_numpy_and_compile_all_missing(
    tmp_path: Path,
) -> None:
    """Log an error when compilation is enabled but NumPy is unavailable."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    config_entry = MagicMock()
    config_entry.data = {
        CONF.KENNFELD_FILE: "kennfeld.json",
    }

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.COMPILE_ALL_MISSING",
            True,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.NUMPY_AVAILABLE",
            False,
        ),
    ):
        power_map = PowerMap(config_entry, hass)
        await power_map.initialize()


@pytest.mark.asyncio
async def test_initialize_without_numpy_for_raw_curve(
    tmp_path: Path,
) -> None:
    """Do not compile a raw curve when NumPy is unavailable."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    hass.async_add_executor_job = AsyncMock(side_effect=lambda func, *args: func(*args))

    config_entry = MagicMock()
    config_entry.data = {
        CONF.KENNFELD_FILE: "kennfeld.json",
    }

    kennfeld_dir = tmp_path / "custom_components" / CONST.DOMAIN / "kennfeld"
    kennfeld_dir.mkdir(parents=True)

    (kennfeld_dir / "kennfeld.json").write_text(
        json.dumps(
            {
                "known_t": [35, 55],
                "known_x": [0, 1, 2],
                "known_y": [
                    [100.0, 110.0, 120.0],
                    [200.0, 210.0, 220.0],
                ],
            }
        ),
        encoding="utf-8",
    )

    power_map = PowerMap(config_entry, hass)

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.COMPILE_ALL_MISSING",
            False,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.NUMPY_AVAILABLE",
            False,
        ),
    ):
        await power_map.initialize()

    assert power_map._compiled_grid == {}


def test_compile_all_missing_generates_missing_plot(tmp_path: Path) -> None:
    """Generate a missing SVG for an already compiled map."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    folder = tmp_path / "kennfeld"
    folder.mkdir()

    filepath = folder / "weishaupt_test.json"

    data = {
        "known_t": [35, 55],
        "known_x": [0, 1, 2],
        "compiled_grid": {
            "0": [100.0, 200.0],
            "10": [110.0, 210.0],
            "20": [120.0, 220.0],
        },
    }

    filepath.write_text(json.dumps(data), encoding="utf-8")

    power_map = PowerMap(MagicMock(), hass)

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.get_filepath",
            return_value=folder,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.CREATE_MISSING_PLOTS",
            True,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
            True,
        ),
        patch.object(
            power_map,
            "_generate_plot_blocking",
        ) as generate_plot,
    ):
        power_map._compile_all_missing_blocking()

    generate_plot.assert_called_once_with(data, filepath)


def test_compile_and_save_kennfeld_scipy_import_error(
    tmp_path: Path,
) -> None:
    """Fall back to Chebyshev when SciPy import fails."""
    power_map = create_power_map()
    power_map._out_range_raw = [0, 20]

    data = {
        "known_x": list(range(9)),
        "known_y": [
            [100.0 + x for x in range(9)],
            [200.0 + x for x in range(9)],
        ],
        "known_t": [35, 55],
    }

    filepath = tmp_path / "kennfeld.json"

    real_import = __import__

    def import_without_scipy(name, *args, **kwargs):
        if name == "scipy.interpolate":
            raise ImportError("SciPy unavailable")
        return real_import(name, *args, **kwargs)

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.SCIPY_AVAILABLE",
            True,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
            False,
        ),
        patch(
            "builtins.__import__",
            side_effect=import_without_scipy,
        ),
    ):
        result = power_map._compile_and_save_kennfeld_blocking(
            data,
            filepath,
        )

    assert result
    assert "compiled_grid" in data


@pytest.mark.asyncio
async def test_initialize_compiles_all_missing(
    tmp_path: Path,
) -> None:
    """Scan for missing characteristic maps during initialization."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)
    hass.async_add_executor_job = AsyncMock()

    config_entry = MagicMock()
    config_entry.data = {
        CONF.KENNFELD_FILE: "kennfeld.json",
    }

    kennfeld_dir = tmp_path / "custom_components" / CONST.DOMAIN / "kennfeld"
    kennfeld_dir.mkdir(parents=True)

    # Active file must exist so initialize() can continue.
    (kennfeld_dir / "kennfeld.json").write_text(
        json.dumps(
            {
                "known_t": [35, 55],
                "known_x": [0, 1, 2],
                "compiled_grid": {
                    "0": [100.0, 200.0],
                },
            }
        ),
        encoding="utf-8",
    )

    power_map = PowerMap(config_entry, hass)

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.COMPILE_ALL_MISSING",
            True,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.NUMPY_AVAILABLE",
            True,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.get_filepath",
            return_value=kennfeld_dir,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.CREATE_MISSING_PLOTS",
            False,
        ),
    ):
        await power_map.initialize()

    hass.async_add_executor_job.assert_any_await(
        power_map._compile_all_missing_blocking
    )


def test_copy_powermap_plot_handles_error(tmp_path: Path) -> None:
    """Log an error when copying the power-map plot fails."""
    json_filepath = tmp_path / "kennfeld.json"
    svg_filepath = json_filepath.with_suffix(".svg")
    svg_filepath.write_text("<svg />", encoding="utf-8")

    www_dir = tmp_path / "www" / "local"

    power_map = create_power_map()

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.shutil.copy2",
        side_effect=OSError("copy failed"),
    ):
        power_map._copy_powermap_plot(
            json_filepath,
            www_dir,
        )


def test_generate_plot_blocking_without_pygal(tmp_path: Path) -> None:
    """Do nothing when Pygal is unavailable."""
    power_map = create_power_map()

    with patch(
        "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
        False,
    ):
        power_map._generate_plot_blocking(
            {},
            tmp_path / "kennfeld.json",
        )


@pytest.mark.asyncio
async def test_initialize_compiles_active_curve(tmp_path: Path) -> None:
    """Compile the active raw characteristic map when needed."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)

    compiled_grid = {"0": [100.0, 200.0]}

    async def run_executor(func, *args):
        return compiled_grid

    hass.async_add_executor_job = AsyncMock(side_effect=run_executor)

    config_entry = MagicMock()
    config_entry.data = {
        CONF.KENNFELD_FILE: "kennfeld.json",
    }

    kennfeld_dir = tmp_path / "custom_components" / CONST.DOMAIN / "kennfeld"
    kennfeld_dir.mkdir(parents=True)

    (kennfeld_dir / "kennfeld.json").write_text(
        json.dumps(
            {
                "known_t": [35, 55],
                "known_x": [0, 1, 2],
                "known_y": [
                    [100.0, 110.0, 120.0],
                    [200.0, 210.0, 220.0],
                ],
            }
        ),
        encoding="utf-8",
    )

    power_map = PowerMap(config_entry, hass)

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.COMPILE_ALL_MISSING",
            False,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.NUMPY_AVAILABLE",
            True,
        ),
    ):
        await power_map.initialize()

    assert power_map._compiled_grid == compiled_grid


@pytest.mark.asyncio
async def test_initialize_generates_missing_plot(tmp_path: Path) -> None:
    """Generate a missing plot for an existing compiled map."""
    hass = MagicMock()
    hass.config.config_dir = str(tmp_path)
    hass.async_add_executor_job = AsyncMock()

    config_entry = MagicMock()
    config_entry.data = {
        CONF.KENNFELD_FILE: "kennfeld.json",
    }

    kennfeld_dir = tmp_path / "custom_components" / CONST.DOMAIN / "kennfeld"
    kennfeld_dir.mkdir(parents=True)

    filepath = kennfeld_dir / "kennfeld.json"

    data = {
        "known_t": [35, 55],
        "known_x": [0, 1, 2],
        "compiled_grid": {
            "0": [100.0, 200.0],
        },
    }

    filepath.write_text(json.dumps(data), encoding="utf-8")

    power_map = PowerMap(config_entry, hass)

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.COMPILE_ALL_MISSING",
            False,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.CREATE_MISSING_PLOTS",
            True,
        ),
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
            True,
        ),
    ):
        await power_map.initialize()

    hass.async_add_executor_job.assert_any_await(
        power_map._generate_plot_blocking,
        data,
        filepath,
    )


def test_compile_and_save_kennfeld_generates_plot(tmp_path: Path) -> None:
    """Generate a plot after compiling a characteristic map."""
    power_map = create_power_map()
    power_map._out_range_raw = [0, 20]

    data = {
        "known_x": [0, 1, 2],
        "known_y": [
            [100.0, 110.0, 120.0],
            [200.0, 210.0, 220.0],
        ],
        "known_t": [35, 55],
    }

    filepath = tmp_path / "kennfeld.json"

    with (
        patch(
            "custom_components.weishaupt_modbus.kennfeld.kennfeld.PYGAL_AVAILABLE",
            True,
        ),
        patch.object(
            power_map,
            "_generate_plot_blocking",
        ) as generate_plot,
    ):
        result = power_map._compile_and_save_kennfeld_blocking(
            data,
            filepath,
        )

    assert result
    generate_plot.assert_called_once_with(data, filepath)
