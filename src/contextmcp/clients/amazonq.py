"""Amazon Q CLI adapter — uses mcpServers in settings."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from contextmcp.clients.base import ClientAdapter


class AmazonQAdapter(ClientAdapter):
    """Amazon Q CLI adapter.

    Config file: ~/.amazonq/settings.json or mcp.json
    Root key: mcpServers (standard)
    """

    name = "amazon-q"
    display_name = "Amazon Q"

    def detect(self) -> bool:
        import shutil
        return shutil.which("q") is not None or shutil.which("amazonq") is not None

    def get_config_path(self, scope: str = "user") -> Path | None:
        if scope == "project":
            return Path.cwd() / ".amazonq" / "mcp.json"
        return Path.home() / ".amazonq" / "mcp.json"

    def get_config_snippet(self) -> dict[str, Any]:
        return {
            "command": "promem",
            "args": [],
        }

    def get_config_key(self) -> str:
        return "mcpServers"
