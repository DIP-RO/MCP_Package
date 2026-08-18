"""Base client adapter."""

from __future__ import annotations

import json
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ClientAdapter(ABC):
    """Base class for AI client adapters."""

    name: str = "generic"
    display_name: str = "Generic MCP Client"

    @abstractmethod
    def detect(self) -> bool:
        """Check if this client is installed/available."""
        ...

    @abstractmethod
    def get_config_path(self, scope: str = "user") -> Path | None:
        """Get the config file path for this client."""
        ...

    @abstractmethod
    def get_config_snippet(self) -> dict:
        """Get the MCP server config snippet for this client."""
        ...

    @abstractmethod
    def get_config_key(self) -> str:
        """Get the JSON key for MCP servers (e.g. 'mcpServers' or 'servers')."""
        ...

    def is_configured(self) -> bool:
        """Check if ContextMCP is already in the client's config."""
        config_path = self.get_config_path()
        if config_path is None or not config_path.exists():
            return False
        try:
            data = json.loads(config_path.read_text(errors="replace"))
            servers = data.get(self.get_config_key(), {})
            return "contextmcp" in servers
        except (json.JSONDecodeError, OSError):
            return False

    def write_config(self, backup: bool = True) -> dict:
        """Write ContextMCP config to the client. Returns result dict."""
        config_path = self.get_config_path()
        if config_path is None:
            return {"success": False, "error": "No config path available"}

        # Ensure parent directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing config
        existing: dict[str, Any] = {}
        if config_path.exists():
            try:
                existing = json.loads(config_path.read_text(errors="replace"))
            except (json.JSONDecodeError, OSError):
                existing = {}

            # Backup
            if backup:
                backup_path = config_path.with_suffix(f".backup{config_path.suffix}")
                try:
                    shutil.copy2(config_path, backup_path)
                except OSError:
                    pass

        # Merge — don't overwrite other servers
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
            return {
                "success": True,
                "message": "Configuration written",
                "path": str(config_path),
            }
        except OSError as e:
            return {"success": False, "error": str(e)}

    def get_instructions(self) -> str:
        """Get manual configuration instructions if auto-config isn't possible."""
        key = self.get_config_key()
        snippet = json.dumps({key: {"contextmcp": self.get_config_snippet()}}, indent=2)
        config_path = self.get_config_path()
        path_str = str(config_path) if config_path else "<client config file>"
        return (
            f"Add the following to {path_str}:\n\n"
            f"```json\n{snippet}\n```"
        )
