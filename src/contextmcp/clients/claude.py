"""Claude Code / Claude Desktop adapter."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from contextmcp.clients.base import ClientAdapter


class ClaudeCodeAdapter(ClientAdapter):
    """Claude Code (CLI) adapter."""

    name = "claude-code"
    display_name = "Claude Code"

    def detect(self) -> bool:
        return shutil.which("claude") is not None

    def get_config_path(self, scope: str = "user") -> Path | None:
        if sys.platform == "darwin":
            return Path.home() / ".claude.json"
        elif os.name == "nt":
            return Path.home() / ".claude.json"
        else:
            return Path.home() / ".claude.json"

    def get_config_snippet(self) -> dict:
        return {
            "command": "contextmcp",
            "args": [],
        }

    def get_config_key(self) -> str:
        return "mcpServers"


class ClaudeDesktopAdapter(ClientAdapter):
    """Claude Desktop adapter."""

    name = "claude-desktop"
    display_name = "Claude Desktop"

    def detect(self) -> bool:
        if sys.platform == "darwin":
            app_path = Path("/Applications/Claude.app")
            return app_path.exists()
        elif os.name == "nt":
            # Check common Windows install locations
            local_app = Path(os.environ.get("LOCALAPPDATA", "")) / "Claude"
            return local_app.exists()
        return False

    def get_config_path(self, scope: str = "user") -> Path | None:
        if sys.platform == "darwin":
            return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
        elif os.name == "nt":
            return Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "Claude" / "claude_desktop_config.json"
        return None

    def get_config_snippet(self) -> dict:
        # Use absolute path to contextmcp executable
        exe = shutil.which("contextmcp")
        command = exe or "contextmcp"
        return {
            "command": command,
            "args": [],
        }

    def get_config_key(self) -> str:
        return "mcpServers"
