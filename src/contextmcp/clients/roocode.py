"""Roo Code adapter — uses mcpServers, similar to Cline."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from contextmcp.clients.base import ClientAdapter


class RooCodeAdapter(ClientAdapter):
    """Roo Code (VS Code extension) adapter.

    Config file: roo_mcp_settings.json (in VS Code settings)
    Root key: mcpServers (standard)
    """

    name = "roo-code"
    display_name = "Roo Code"

    def detect(self) -> bool:
        if sys.platform == "darwin":
            ext = Path.home() / ".vscode" / "extensions"
            if ext.exists():
                return any("roo" in d.name.lower() for d in ext.iterdir())
        elif os.name == "nt":
            ext = Path(os.environ.get("USERPROFILE", Path.home())) / ".vscode" / "extensions"
            if ext.exists():
                return any("roo" in d.name.lower() for d in ext.iterdir())
        return False

    def get_config_path(self, scope: str = "user") -> Path | None:
        # Roo Code stores MCP settings in VS Code's globalStorage
        if sys.platform == "darwin":
            base = Path.home() / "Library" / "Application Support" / "Code" / "User" / "globalStorage"
        elif os.name == "nt":
            base = Path(os.environ.get("APPDATA", "")) / "Code" / "User" / "globalStorage"
        else:
            base = Path.home() / ".config" / "Code" / "User" / "globalStorage"

        # Try to find roo code extension directory
        if base.exists():
            for d in base.iterdir():
                if "roo" in d.name.lower() and d.is_dir():
                    return d / "roo_mcp_settings.json"

        return base / "rooveterinaryinc.roo-cline" / "roo_mcp_settings.json"

    def get_config_snippet(self) -> dict:
        return {
            "command": "contextmcp",
            "args": [],
            "disabled": False,
            "autoApprove": [],
        }

    def get_config_key(self) -> str:
        return "mcpServers"
