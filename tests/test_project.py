"""Test project detection."""

from __future__ import annotations

import os
from pathlib import Path

from contextmcp.project.detector import (
    detect_project,
    find_project_root,
    detect_language,
    detect_framework,
    detect_package_manager,
)
from contextmcp.project.identity import compute_fingerprint, compute_file_hash
from contextmcp.project.ignore import IgnoreMatcher


def test_find_project_root(tmp_project: Path):
    root = find_project_root(tmp_project / "src")
    assert root == tmp_project


def test_find_project_root_from_subdir(tmp_project: Path):
    subdir = tmp_project / "src"
    subdir.mkdir(exist_ok=True)
    root = find_project_root(subdir)
    assert root == tmp_project


def test_detect_language(tmp_project: Path):
    lang = detect_language(tmp_project)
    assert lang == "python"


def test_detect_framework(tmp_project: Path):
    fw = detect_framework(tmp_project)
    assert fw == "FastAPI"


def test_detect_package_manager(tmp_project: Path):
    pm = detect_package_manager(tmp_project)
    # pyproject.toml exists but no lock file — should be None or pip
    assert pm is None or pm == "pip"


def test_detect_project(tmp_project: Path):
    info = detect_project(tmp_project)
    assert info.name == "test-project"
    assert info.language == "python"
    assert info.framework == "FastAPI"
    assert info.root == tmp_project


def test_project_fingerprint_stable(tmp_project: Path):
    info1 = detect_project(tmp_project)
    fp1 = compute_fingerprint(info1)

    info2 = detect_project(tmp_project)
    fp2 = compute_fingerprint(info2)

    assert fp1 == fp2
    assert len(fp1) == 16


def test_project_fingerprint_different(tmp_project: Path, tmp_path: Path):
    other = tmp_path / "other-project"
    other.mkdir()
    (other / "package.json").write_text('{"name": "other"}')

    info1 = detect_project(tmp_project)
    info2 = detect_project(other)

    fp1 = compute_fingerprint(info1)
    fp2 = compute_fingerprint(info2)

    assert fp1 != fp2


def test_ignore_matcher(tmp_project: Path):
    matcher = IgnoreMatcher(tmp_project)

    assert matcher.is_ignored(tmp_project / "__pycache__" / "test.pyc")
    assert matcher.is_ignored(tmp_project / ".git" / "config")
    assert not matcher.is_ignored(tmp_project / "src" / "main.py")


def test_compute_file_hash(tmp_project: Path):
    file = tmp_project / "src" / "main.py"
    h1 = compute_file_hash(file)
    h2 = compute_file_hash(file)
    assert h1 == h2
    assert len(h1) == 64  # SHA256 hex


def test_detect_project_no_markers(tmp_path: Path):
    """Test detection in a directory with no project markers."""
    empty = tmp_path / "empty"
    empty.mkdir()
    info = detect_project(empty)
    # Should fall back to the start directory
    assert info.root == empty
