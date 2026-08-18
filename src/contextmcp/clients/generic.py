"""Generic fallback adapter."""

from __future__ import annotations

import json

from contextmcp.clients.base import ClientAdapter


class GenericAdapter(ClientAdapter):
    """Generic MCP client adapter — provides config snippet without detection."""

    name = "generic"
    display_name = "Generic MCP Client"

    def detect(self) -> bool:
        return False

    def get_config_path(self, scope: str = "user") -> None:
        return None

    def get_config_snippet(self) -> dict:
        return {
            "command": "contextmcp",
            "args": [],
        }

    def get_config_key(self) -> str:
        return "mcpServers"

    def get_instructions(self) -> str:
        snippet = json.dumps({"mcpServers": {"contextmcp": self.get_config_snippet()}}, indent=2)
        return (
            "Add the following to your MCP client's configuration file:\n\n"
            f"```json\n{snippet}\n```"
        )


import json
