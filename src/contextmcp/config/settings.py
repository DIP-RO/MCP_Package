"""Configuration with sensible defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _get_project_data_dir() -> Path:
    """Return project-local data directory (.contextmcp/ inside project root).

    This is per-project, NOT centralized. Each project gets its own SQLite DB
    inside its own directory. No waste of user's home/global storage.
    """
    cwd = Path.cwd()
    # Walk up to find project root (same logic as detector, but lightweight)
    markers = [
        "pyproject.toml", "setup.py", "package.json", "tsconfig.json",
        "Cargo.toml", "go.mod", "Gemfile", "pom.xml", "build.gradle",
        "Makefile", "CMakeLists.txt", "Dockerfile", ".git",
    ]
    current = cwd
    while True:
        for marker in markers:
            if (current / marker).exists():
                return current / ".contextmcp"
        parent = current.parent
        if parent == current:
            return cwd / ".contextmcp"
        current = parent


@dataclass
class Settings:
    """Global settings with defaults. No config file required.

    Storage is PROJECT-LOCAL: .contextmcp/ inside the project root.
    No centralized OS directory — each project manages its own context.
    """

    data_dir: Path = field(default_factory=_get_project_data_dir)
    db_name: str = "contextmcp.db"
    max_file_size: int = 1_048_576  # 1 MB — skip files larger than this
    max_indexed_files: int = 5000
    ignore_patterns: list[str] = field(
        default_factory=lambda: [
            ".git",
            ".contextmcp",
            ".venv",
            "venv",
            "env",
            "node_modules",
            "__pycache__",
            ".mypy_cache",
            ".ruff_cache",
            ".pytest_cache",
            "dist",
            "build",
            "coverage",
            ".tox",
            ".eggs",
            "*.egg-info",
            ".env",
            ".env.local",
            "*.pyc",
            "*.pyo",
            "*.so",
            "*.dylib",
            "*.dll",
            "*.bin",
            "*.exe",
            "*.png",
            "*.jpg",
            "*.jpeg",
            "*.gif",
            "*.bmp",
            "*.webp",
            "*.ico",
            "*.svg",
            "*.tiff",
            "*.pdf",
            "*.zip",
            "*.tar",
            "*.gz",
            "*.bz2",
            "*.7z",
            "*.rar",
            "*.wasm",
            "*.lock",
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
        ]
    )
    token_estimate_chars_per_token: int = 4
    default_search_limit: int = 5
    default_token_budget: int = 1000
    max_token_budget: int = 10000
    stale_threshold_days: int = 30
    enable_git_analysis: bool = True
    enable_env_analysis: bool = True

    # Override from environment
    @classmethod
    def from_env(cls) -> Settings:
        s = cls()
        env_dir = os.environ.get("CONTEXTMCP_DATA_DIR")
        if env_dir:
            s.data_dir = Path(env_dir)
        return s

    @property
    def db_path(self) -> Path:
        return self.data_dir / self.db_name

    def ensure_data_dir(self) -> Path:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir


def get_settings() -> Settings:
    """Get global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings


_settings: Settings | None = None


def reset_settings() -> None:
    global _settings
    _settings = None
