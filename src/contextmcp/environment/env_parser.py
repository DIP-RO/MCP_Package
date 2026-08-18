"""Safe .env file parsing — never exposes secret values."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from contextmcp.security.redaction import is_likely_secret


def parse_env_file(path: Path) -> dict[str, str]:
    """Parse a .env file, returning redacted values.

    Returns a dict of variable_name -> 'configured' | 'missing' | actual_value
    for non-secret values.
    """
    if not path.exists() or not path.is_file():
        return {}

    result = {}
    try:
        for line in path.read_text(errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if is_likely_secret(key, value):
                result[key] = "configured"
            else:
                result[key] = value
    except OSError:
        pass

    return result


def get_env_keys(path: Path) -> list[str]:
    """Get just the variable names from a .env file (no values)."""
    if not path.exists() or not path.is_file():
        return []
    keys = []
    try:
        for line in path.read_text(errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, _ = line.partition("=")
            keys.append(key.strip())
    except OSError:
        pass
    return keys


def compare_env_files(env_path: Path, example_path: Path) -> dict[str, Any]:
    """Compare .env with .env.example for diagnostics."""
    env_keys = set(get_env_keys(env_path))
    example_keys = set(get_env_keys(example_path))

    return {
        "present_in_env": sorted(env_keys),
        "present_in_example": sorted(example_keys),
        "missing_from_env": sorted(example_keys - env_keys),
        "extra_in_env": sorted(env_keys - example_keys),
    }
