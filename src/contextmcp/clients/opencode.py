"""OpenCode adapter — uses 'mcp' root key with array command format."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from contextmcp.clients.base import ClientAdapter


class OpenCodeAdapter(ClientAdapter):
    """OpenCode (by Anomaly) adapter.

    Config format differs from standard MCP:
    - Root key is 'mcp' (not 'mcpServers')
    - command is an array: ["contextmcp"]
    - type field required: "local"
    - Config file: opencode.json (project) or ~/.config/opencode/opencode.json (global)
    """

    name = "opencode"
    display_name = "OpenCode"

    def detect(self) -> bool:
        import shutil
        return shutil.which("opencode") is not None

    def get_config_path(self, scope: str = "user") -> Path | None:
        if scope == "project":
            return Path.cwd() / "opencode.json"
        if sys.platform == "darwin" or os.name != "nt":
            return Path.home() / ".config" / "opencode" / "opencode.json"
        else:
            appdata = os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
            return Path(appdata) / "opencode" / "opencode.json"

    def get_config_snippet(self) -> dict:
        return {
            "type": "local",
            "command": ["contextmcp"],
            "enabled": True,
        }

    def get_config_key(self) -> str:
        return "mcp"

    def write_config(self, backup: bool = True) -> dict:
        """Write config with OpenCode's nested 'mcp' structure."""
        config_path = self.get_config_path()
        if config_path is None:
            return {"success": False, "error": "No config path available"}

        config_path.parent.mkdir(parents=True, exist_ok=True)

        existing: dict = {}
        if config_path.exists():
            try:
                existing = json.loads(config_path.read_text(errors="replace"))
            except (json.JSONDecodeError, OSError):
                existing = {}
            if backup:
                backup_path = config_path.with_suffix(f".backup{config_path.suffix}")
                try:
                    import shutil
                    shutil.copy2(config_path, backup_path)
                except OSError:
                    pass

        key = self.get_config_key()
        if key not in existing:
            existing[key] = {}

        if "contextmcp" in existing[key]:
            return {
                "success": True,
                "message": "ContextMCP already configured",
                "path": str(config_path),
            }

        existing[key]["contextmcp"] = self.get_config_snippet()

        try:
            config_path.write_text(json.dumps(existing, indent=2))
            return {"success": True, "message": "Configuration written", "path": str(config_path)}
        except OSError as e:
            return {"success": False, "error": str(e)}

    def get_instructions(self) -> str:
        snippet = json.dumps({"mcp": {"contextmcp": self.get_config_snippet()}}, indent=2)
        config_path = self.get_config_path()
        path_str = str(config_path) if config_path else "opencode.json"
        return (
            f"OpenCode uses a unique config format (root key is 'mcp', command is an array).\n\n"
            f"Add the following to {path_str}:\n\n"
            f"```json\n{snippet}\n```"
        )
