#!/usr/bin/env python3

from pathlib import Path


REPLACEMENTS = {
    "aussentemp": "system_outside_temperature",
    "luftansautgemp": "system_intake_temperature",
    "fehler": "system_error",
    "warnung": "system_warning",
    "fehlerfrei": "system_error_free",
    "betriebsanzeige": "system_operating_display",
    "sys_operationmode": "system_config_operating_mode",
    "sys_pv": "system_config_pv_setpoint",
}


def replace_keys(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    replacements = 0

    for old_key, new_key in REPLACEMENTS.items():
        old = f'"{old_key}": {{'
        new = f'"{new_key}": {{'

        count = text.count(old)

        if count:
            text = text.replace(old, new)
            replacements += count
            print(f"{path.name}: {old_key} -> {new_key} ({count})")

    path.write_text(text, encoding="utf-8")

    print(f"{path.name}: {replacements} replacement(s)")


if __name__ == "__main__":
    directory = Path(__file__).resolve().parent

    for filename in ("de.json", "en.json", "nl.json"):
        path = directory / filename

        if not path.exists():
            print(f"{filename}: not found")
            continue

        replace_keys(path)
