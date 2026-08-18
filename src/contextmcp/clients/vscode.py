"""VS Code / GitHub Copilot adapter."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from contextmcp.clients.base import ClientAdapter


class VSCodeAdapter(ClientAdapter):
    """VS Code / GitHub Copilot adapter.

    NOTE: VS Code uses 'servers' key, NOT 'mcpServers'.
    """

    name = "vscode"
    display_name = "VS Code / GitHub Copilot"

    def detect(self) -> bool:
        if sys.platform == "darwin":
            return Path("/Applications/Visual Studio Code.app").exists() or \
                   Path("/Applications/VSCode.app").exists()
        elif os.name == "nt":
            local_app = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code"
            return local_app.exists()
        else:
            import shutil
            return shutil.which("code") is not None

    def get_config_path(self, scope: str = "user") -> Path | None:
        if scope == "project":
            return Path.cwd() / ".vscode" / "mcp.json"
        return None  # User config is opened via command palette

    def get_config_snippet(self) -> dict:
        return {
            "type": "stdio",
            "command": "contextmcp",
            "args": [],
        }

    def get_config_key(self) -> str:
        return "servers"  # VS Code uses 'servers', NOT 'mcpServers'

    def get_instructions(self) -> str:
        snippet = json.dumps({"servers": {"contextmcp": self.get_config_snippet()}}, indent=2)
        return (
            "VS Code uses a different config format (key is 'servers', not 'mcpServers').\n\n"
            "Option 1 — Workspace config (.vscode/mcp.json):\n"
            f"```json\n{snippet}\n```\n\n"
            "Option 2 — Via Command Palette:\n"
            "  1. Press Cmd+Shift+P (macOS) or Ctrl+Shift+P (Windows/Linux)\n"
            "  2. Run 'MCP: Add Server'\n"
            "  3. Choose 'Workspace' or 'Global'\n"
            "  4. Enter: contextmcp as the server name\n"
            "  5. Enter: contextmcp as the command\n"
            "  6. Leave args empty\n\n"
            "Option 3 — CLI:\n"
            "  code --add-mcp '{\"name\":\"contextmcp\",\"command\":\"contextmcp\",\"args\":[]}'"
        )
