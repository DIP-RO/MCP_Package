"""Tabnine adapter — uses mcpServers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from contextmcp.clients.base import ClientAdapter


class TabnineAdapter(ClientAdapter):
    """Tabnine adapter.

    Config file: ~/.tabnine/mcp.json
    Root key: mcpServers (standard)
    """

    name = "tabnine"
    display_name = "Tabnine"

    def detect(self) -> bool:
        import shutil
        return shutil.which("tabnine") is not None

    def get_config_path(self, scope: str = "user") -> Path | None:
        if scope == "project":
            return Path.cwd() / ".tabnine" / "mcp.json"
        return Path.home() / ".tabnine" / "mcp.json"

    def get_config_snippet(self) -> dict[str, Any]:
        return {
            "command": "promem",
            "args": [],
        }

    def get_config_key(self) -> str:
        return "mcpServers"
