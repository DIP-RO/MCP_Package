"""Test CLI commands."""

from __future__ import annotations

import os
from pathlib import Path

from click.testing import CliRunner

from contextmcp import __version__
from contextmcp.cli.main import cli


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Promem-MCP" in result.output


def test_cli_privacy(tmp_data_dir: Path):
    os.environ["CONTEXTMCP_DATA_DIR"] = str(tmp_data_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ["privacy"])
    assert result.exit_code == 0
    assert "Local only" in result.output
    assert "No external requests" in result.output


def test_cli_status(tmp_project: Path, tmp_data_dir: Path, monkeypatch):
    monkeypatch.chdir(tmp_project)
    os.environ["CONTEXTMCP_DATA_DIR"] = str(tmp_data_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "Promem-MCP" in result.output


def test_cli_search(tmp_project: Path, tmp_data_dir: Path, monkeypatch):
    monkeypatch.chdir(tmp_project)
    os.environ["CONTEXTMCP_DATA_DIR"] = str(tmp_data_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ["search", "test"])
    assert result.exit_code == 0


def test_cli_config_list(tmp_data_dir: Path):
    os.environ["CONTEXTMCP_DATA_DIR"] = str(tmp_data_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ["config"])
    assert result.exit_code == 0
