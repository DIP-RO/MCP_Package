"""ZCode / GLM (Zhipu AI) adapter."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from contextmcp.clients.base import ClientAdapter


class ZCodeAdapter(ClientAdapter):
    """ZCode (Zhipu AI / GLM) adapter.

    Config file: .zcode/config.json (project-level)
    Root key: mcpServers (standard, accepted by ZCode)
    """

    name = "zcode"
    display_name = "ZCode (GLM/Zhipu)"

    def detect(self) -> bool:
        import shutil
        return shutil.which("zcode") is not None

    def get_config_path(self, scope: str = "user") -> Path | None:
        if scope == "project":
            return Path.cwd() / ".zcode" / "config.json"
        # ZCode primarily uses project-level config
        return Path.cwd() / ".zcode" / "config.json"

    def get_config_snippet(self) -> dict:
        return {
            "type": "stdio",
            "command": "contextmcp",
            "args": [],
        }

    def get_config_key(self) -> str:
        return "mcpServers"
