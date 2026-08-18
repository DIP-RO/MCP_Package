"""Project fingerprinting for stable identity."""

from __future__ import annotations

import hashlib
from pathlib import Path

from contextmcp.project.detector import ProjectInfo


def compute_fingerprint(info: ProjectInfo) -> str:
    """Compute a stable project fingerprint.

    Uses multiple signals so the project is recognized even if moved:
    1. Git remote URL (highest weight)
    2. Project name
    3. Directory name
    4. Normalized path hash
    """
    signals = []

    # Git remote — most stable signal
    if info.git_remote:
        signals.append(f"remote:{info.git_remote}")

    # Project name
    signals.append(f"name:{info.name}")

    # Directory name (fallback if name is generic)
    signals.append(f"dir:{info.root.name}")

    # Path hash (lower weight, but helps distinguish same-named projects)
    path_str = str(info.root)
    signals.append(f"path_hash:{hashlib.sha256(path_str.encode()).hexdigest()[:16]}")

    combined = "|".join(signals)
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def compute_file_hash(path: Path, chunk_size: int = 8192) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                h.update(chunk)
    except (OSError, PermissionError):
        return ""
    return h.hexdigest()
