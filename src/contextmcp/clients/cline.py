"""Cline adapter — uses mcpServers in ~/.cline/mcp.json or cline_mcp_settings.json."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from contextmcp.clients.base import ClientAdapter


class ClineAdapter(ClientAdapter):
    """Cline (VS Code extension) adapter.

    Config file: ~/.cline/mcp.json (CLI) or cline_mcp_settings.json (IDE)
    Root key: mcpServers (standard)
    Extra fields: disabled, autoApprove
    """

    name = "cline"
    display_name = "Cline"

    def detect(self) -> bool:
        import shutil
        cli = shutil.which("cline") is not None
        # Check for VS Code extension
        if sys.platform == "darwin":
            ext = Path.home() / ".vscode" / "extensions"
            if ext.exists():
                return cli or any("cline" in d.name.lower() for d in ext.iterdir())
        elif os.name == "nt":
            ext = Path(os.environ.get("USERPROFILE", Path.home())) / ".vscode" / "extensions"
            if ext.exists():
                return cli or any("cline" in d.name.lower() for d in ext.iterdir())
        return cli

    def get_config_path(self, scope: str = "user") -> Path | None:
        if scope == "project":
            return Path.cwd() / ".cline" / "mcp.json"
        return Path.home() / ".cline" / "mcp.json"

    def get_config_snippet(self) -> dict:
        return {
            "command": "dmcp",
            "args": [],
            "disabled": False,
            "autoApprove": [],
        }

    def get_config_key(self) -> str:
        return "mcpServers"
