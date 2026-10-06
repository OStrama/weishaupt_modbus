#!/usr/bin/env python3

import json
from pathlib import Path


TRANSLATION_DIR = Path("")
MASTER = TRANSLATION_DIR / "de.json"


def get_keys(data: dict, prefix: str = "") -> set[str]:
    """Return all nested keys as dot-separated paths."""
    keys: set[str] = set()

    for key, value in data.items():
        path = f"{prefix}.{key}" if prefix else key
        keys.add(path)

        if isinstance(value, dict):
            keys.update(get_keys(value, path))

    return keys


def load_keys(path: Path) -> set[str]:
    """Load translation keys from a JSON file."""
    with path.open(encoding="utf-8") as file:
        return get_keys(json.load(file))


def check_translation_keys() -> None:
    """Check that all translation files have the same keys as de.json."""
    master_keys = load_keys(MASTER)

    for filename in ("en.json", "nl.json"):
        path = TRANSLATION_DIR / filename
        keys = load_keys(path)

        missing = master_keys - keys
        extra = keys - master_keys

        assert not missing, f"{filename} is missing translation keys:\n" + "\n".join(
            f"  {key}" for key in sorted(missing)
        )

        assert not extra, f"{filename} has extra translation keys:\n" + "\n".join(
            f"  {key}" for key in sorted(extra)
        )


def main() -> int:
    """Run the translation check."""
    check_translation_keys()
    print("All translation files have the same keys as de.json.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
