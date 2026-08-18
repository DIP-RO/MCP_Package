"""Test fixtures."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from contextmcp.config.settings import reset_settings, Settings


@pytest.fixture
def tmp_data_dir(tmp_path: Path, monkeypatch) -> Path:
    """Create a temporary project-local data directory for ContextMCP.

    Storage is per-project: .contextmcp/ inside the project root.
    """
    from contextmcp.config.settings import reset_settings
    from contextmcp.core.lifecycle import reset_engine

    reset_settings()
    reset_engine()
    # Simulate project-local storage
    data_dir = tmp_path / ".contextmcp"
    data_dir.mkdir()
    monkeypatch.setenv("CONTEXTMCP_DATA_DIR", str(data_dir))
    return data_dir


@pytest.fixture
def settings(tmp_data_dir: Path) -> Settings:
    """Create settings with a temporary data directory."""
    reset_settings()
    os.environ["CONTEXTMCP_DATA_DIR"] = str(tmp_data_dir)
    s = Settings.from_env()
    return s


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory with markers."""
    project = tmp_path / "test-project"
    project.mkdir()
    (project / "pyproject.toml").write_text(
        '[project]\nname = "test-project"\nversion = "0.1.0"\nrequires-python = ">=3.10"\n'
        'dependencies = ["fastapi", "pytest"]\n'
    )
    (project / "README.md").write_text("# Test Project\n\nA test project for ContextMCP.\n")
    (project / "src").mkdir()
    (project / "src" / "main.py").write_text("print('hello')\n")
    (project / "tests").mkdir()
    (project / "tests" / "test_main.py").write_text("def test_basic():\n    assert True\n")
    return project


@pytest.fixture
def tmp_git_project(tmp_project: Path) -> Path:
    """Create a temporary project with a git repo."""
    import subprocess
    subprocess.run(["git", "init"], cwd=str(tmp_project), capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(tmp_project), capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(tmp_project), capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=str(tmp_project), capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=str(tmp_project), capture_output=True,
    )
    return tmp_project
