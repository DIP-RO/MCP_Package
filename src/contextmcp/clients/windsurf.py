"""Windsurf adapter — uses mcpServers in ~/.codeium/mcp_config.json."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from contextmcp.clients.base import ClientAdapter


class WindsurfAdapter(ClientAdapter):
    """Windsurf (Codeium) adapter.

    Config file: ~/.codeium/mcp_config.json
    Root key: mcpServers (standard)
    """

    name = "windsurf"
    display_name = "Windsurf"

    def detect(self) -> bool:
        if sys.platform == "darwin":
            return Path("/Applications/Windsurf.app").exists()
        elif os.name == "nt":
            local_app = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Windsurf"
            return local_app.exists()
        else:
            import shutil
            return shutil.which("windsurf") is not None

    def get_config_path(self, scope: str = "user") -> Path | None:
        if scope == "project":
            return Path.cwd() / ".codeium" / "mcp_config.json"
        return Path.home() / ".codeium" / "mcp_config.json"

    def get_config_snippet(self) -> dict[str, Any]:
        return {
            "command": "promem",
            "args": [],
        }

    def get_config_key(self) -> str:
        return "mcpServers"
