"""Client detection — finds installed AI coding clients."""

from __future__ import annotations

from contextmcp.clients.base import ClientAdapter
from contextmcp.clients.claude import ClaudeCodeAdapter, ClaudeDesktopAdapter
from contextmcp.clients.cursor import CursorAdapter
from contextmcp.clients.vscode import VSCodeAdapter
from contextmcp.clients.copilot import CopilotAdapter
from contextmcp.clients.opencode import OpenCodeAdapter
from contextmcp.clients.gemini import GeminiCLIAdapter
from contextmcp.clients.windsurf import WindsurfAdapter
from contextmcp.clients.cline import ClineAdapter
from contextmcp.clients.roocode import RooCodeAdapter
from contextmcp.clients.amazonq import AmazonQAdapter
from contextmcp.clients.zcode import ZCodeAdapter
from contextmcp.clients.tabnine import TabnineAdapter
from contextmcp.clients.generic import GenericAdapter


ALL_ADAPTERS: list[type[ClientAdapter]] = [
    ClaudeCodeAdapter,
    ClaudeDesktopAdapter,
    CursorAdapter,
    VSCodeAdapter,
    CopilotAdapter,
    OpenCodeAdapter,
    GeminiCLIAdapter,
    WindsurfAdapter,
    ClineAdapter,
    RooCodeAdapter,
    AmazonQAdapter,
    ZCodeAdapter,
    TabnineAdapter,
]


def detect_clients() -> list[ClientAdapter]:
    """Detect all installed AI coding clients."""
    detected = []
    for adapter_cls in ALL_ADAPTERS:
        adapter = adapter_cls()
        if adapter.detect():
            detected.append(adapter)
    return detected


def get_adapter(name: str) -> ClientAdapter | None:
    """Get a specific adapter by name."""
    for adapter_cls in ALL_ADAPTERS:
        adapter = adapter_cls()
        if adapter.name == name:
            return adapter
    return None


def get_all_adapters() -> list[ClientAdapter]:
    """Get all adapters (detected or not)."""
    return [cls() for cls in ALL_ADAPTERS]
