"""Copilot adapter — same as VS Code adapter for now."""

from __future__ import annotations

from contextmcp.clients.vscode import VSCodeAdapter


class CopilotAdapter(VSCodeAdapter):
    """GitHub Copilot adapter (uses VS Code's MCP config)."""

    name = "copilot"
    display_name = "GitHub Copilot (VS Code)"
