"""Test environment detection and diagnostics."""

from __future__ import annotations

from pathlib import Path

from contextmcp.environment.detector import EnvironmentInfo
from contextmcp.environment.env_parser import parse_env_file, get_env_keys, compare_env_files
from contextmcp.environment.diagnostics import run_diagnostics


def test_environment_info():
    env = EnvironmentInfo()
    assert env.python_version
    assert "." in env.python_version
    assert env.platform


def test_env_parser_no_file(tmp_path: Path):
    result = parse_env_file(tmp_path / ".env")
    assert result == {}


def test_env_parser_redacts_secrets(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "APP_NAME=myapp\n"
        "OPENAI_API_KEY=sk-abc123def456ghi789jkl012mno345\n"
        "DATABASE_URL=postgresql://user:pass@localhost/db\n"
        "PORT=8080\n"
    )
    result = parse_env_file(env_file)
    assert result["APP_NAME"] == "myapp"
    assert result["OPENAI_API_KEY"] == "configured"
    assert result["DATABASE_URL"] == "configured"
    assert result["PORT"] == "8080"


def test_env_parser_handles_comments(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("# Comment\nAPP_NAME=myapp\n\n# Another comment\n")
    result = parse_env_file(env_file)
    assert result == {"APP_NAME": "myapp"}


def test_get_env_keys(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=1\nB=2\nC=3\n")
    keys = get_env_keys(env_file)
    assert keys == ["A", "B", "C"]


def test_compare_env_files(tmp_path: Path):
    env = tmp_path / ".env"
    example = tmp_path / ".env.example"
    env.write_text("A=1\nB=2\n")
    example.write_text("A=1\nB=2\nC=3\n")

    result = compare_env_files(env, example)
    assert "C" in result["missing_from_env"]
    assert result["present_in_env"] == ["A", "B"]


def test_diagnostics(tmp_path: Path):
    result = run_diagnostics(tmp_path)
    assert "findings" in result
    assert "healthy" in result
    assert isinstance(result["findings"], list)
