"""Gemini CLI adapter — uses mcpServers in ~/.gemini/settings.json."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from contextmcp.clients.base import ClientAdapter


class GeminiCLIAdapter(ClientAdapter):
    """Google Gemini CLI adapter.

    Config file: ~/.gemini/settings.json
    Root key: mcpServers (standard)
    Supports command, args, env, cwd, timeout, trust fields.
    """

    name = "gemini-cli"
    display_name = "Gemini CLI"

    def detect(self) -> bool:
        import shutil
        return shutil.which("gemini") is not None

    def get_config_path(self, scope: str = "user") -> Path | None:
        if scope == "project":
            return Path.cwd() / ".gemini" / "settings.json"
        return Path.home() / ".gemini" / "settings.json"

    def get_config_snippet(self) -> dict[str, Any]:
        return {
            "command": "promem",
            "args": [],
            "timeout": 30000,
            "trust": False,
        }

    def get_config_key(self) -> str:
        return "mcpServers"
