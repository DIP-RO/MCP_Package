"""Cursor adapter."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from contextmcp.clients.base import ClientAdapter


class CursorAdapter(ClientAdapter):
    """Cursor IDE adapter."""

    name = "cursor"
    display_name = "Cursor"

    def detect(self) -> bool:
        if sys.platform == "darwin":
            return Path("/Applications/Cursor.app").exists()
        elif os.name == "nt":
            local_app = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Cursor"
            return local_app.exists()
        else:
            # Linux — check for cursor in PATH or common locations
            import shutil
            return shutil.which("cursor") is not None

    def get_config_path(self, scope: str = "user") -> Path | None:
        if scope == "project":
            return Path.cwd() / ".cursor" / "mcp.json"
        if sys.platform == "darwin" or os.name != "nt":
            return Path.home() / ".cursor" / "mcp.json"
        else:
            return Path(os.environ.get("USERPROFILE", Path.home())) / ".cursor" / "mcp.json"

    def get_config_snippet(self) -> dict[str, Any]:
        return {
            "command": "promem",
            "args": [],
        }

    def get_config_key(self) -> str:
        return "mcpServers"
