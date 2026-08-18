"""Input validation and path safety."""

from __future__ import annotations

import os
from pathlib import Path


def safe_resolve_path(path: str | Path, base: str | Path | None = None) -> Path:
    """Safely resolve a path, preventing path traversal.

    Resolves symlinks and ensures the result is within the base directory
    if one is provided.
    """
    p = Path(path).expanduser()
    if base:
        base_path = Path(base).resolve()
        resolved = (base_path / p).resolve() if not p.is_absolute() else p.resolve()
        # Ensure resolved path is within base
        try:
            resolved.relative_to(base_path)
        except ValueError:
            raise ValueError(f"Path {path} escapes base directory {base}")
        return resolved
    return p.resolve()


def is_safe_filename(name: str) -> bool:
    """Check if a filename is safe (no path separators or traversal)."""
    if not name:
        return False
    if "/" in name or "\\" in name:
        return False
    if name in (".", ".."):
        return False
    if name.startswith(".."):
        return False
    return True


def validate_memory_type(mem_type: str) -> bool:
    """Validate that a memory type is allowed."""
    valid_types = {
        "project_rule",
        "architecture",
        "technical_decision",
        "coding_convention",
        "developer_preference",
        "known_issue",
        "todo",
        "dependency",
        "environment_fact",
        "git_fact",
        "session_summary",
    }
    return mem_type in valid_types


def validate_scope(scope: str) -> bool:
    """Validate that a scope is allowed."""
    valid_scopes = {"global", "project", "environment", "git", "session"}
    return scope in valid_scopes


def validate_source_type(source_type: str) -> bool:
    """Validate that a source type is allowed."""
    valid = {"observed", "inferred", "user", "ai"}
    return source_type in valid


def sanitize_query(query: str, max_length: int = 1000) -> str:
    """Sanitize a search query."""
    if not query:
        return ""
    # Truncate
    query = query[:max_length]
    # Remove null bytes
    query = query.replace("\x00", "")
    return query.strip()


def is_binary_file(path: Path, check_bytes: int = 8192) -> bool:
    """Detect if a file is binary by checking for null bytes."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(check_bytes)
        return b"\x00" in chunk
    except (OSError, PermissionError):
        return True


def safe_file_size(path: Path) -> int:
    """Get file size safely, returning 0 on error."""
    try:
        return path.stat().st_size
    except (OSError, PermissionError):
        return 0
