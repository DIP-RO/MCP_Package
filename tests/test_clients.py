"""Test client adapters."""

from __future__ import annotations

from contextmcp.clients.claude import ClaudeCodeAdapter
from contextmcp.clients.cursor import CursorAdapter
from contextmcp.clients.detector import get_adapter, get_all_adapters
from contextmcp.clients.generic import GenericAdapter
from contextmcp.clients.vscode import VSCodeAdapter


def test_get_all_adapters():
    adapters = get_all_adapters()
    assert len(adapters) >= 5
    names = {a.name for a in adapters}
    assert "claude-code" in names
    assert "claude-desktop" in names
    assert "cursor" in names
    assert "vscode" in names


def test_get_adapter():
    adapter = get_adapter("cursor")
    assert adapter is not None
    assert adapter.name == "cursor"

    assert get_adapter("nonexistent") is None


def test_vscode_uses_servers_key():
    adapter = VSCodeAdapter()
    assert adapter.get_config_key() == "servers"


def test_cursor_uses_mcp_servers_key():
    adapter = CursorAdapter()
    assert adapter.get_config_key() == "mcpServers"


def test_claude_code_uses_mcp_servers_key():
    adapter = ClaudeCodeAdapter()
    assert adapter.get_config_key() == "mcpServers"


def test_config_snippets():
    for adapter in get_all_adapters():
        snippet = adapter.get_config_snippet()
        assert "command" in snippet
        assert "contextmcp" in snippet["command"]


def test_generic_adapter_instructions():
    adapter = GenericAdapter()
    instructions = adapter.get_instructions()
    assert "mcpServers" in instructions
    assert "contextmcp" in instructions


def test_vscode_adapter_instructions():
    adapter = VSCodeAdapter()
    instructions = adapter.get_instructions()
    assert "servers" in instructions
    # VS Code instructions mention 'mcpServers' to explain the difference — that's fine
    assert '"servers"' in instructions
