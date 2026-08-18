# Research: MCP & AI Client Integration Mechanisms

## MCP Python SDK

**Current stable:** v2.0.0 (supports 2026-07-28 spec and all earlier revisions)

```bash
pip install "mcp[cli]"
```

### Server API (v2)

```python
from mcp.server import MCPServer

mcp = MCPServer("ServerName")

@mcp.tool()
def my_tool(query: str, limit: int = 10) -> str:
    """Tool description becomes the MCP tool description."""
    return "result"

if __name__ == "__main__":
    mcp.run()  # defaults to stdio
```

Key points:
- `MCPServer` (formerly `FastMCP` in v1) is the high-level server class
- `@mcp.tool()` decorator auto-generates schema from type hints + docstring
- `mcp.run()` with no args = stdio transport (default for local servers)
- `Annotated[type, Field(...)]` for parameter descriptions/constraints
- `async def` for I/O tools, plain `def` for compute
- v1.x still maintained but `pip install mcp` now gives v2

### Transport

| Transport | Use case |
|-----------|----------|
| stdio | Local servers (default). Host launches as subprocess |
| streamable-http | Deployed servers |
| sse | Deprecated |

For ContextMCP: **stdio only**. The host client launches `contextmcp` as a subprocess.

---

## Client Configuration Mechanisms

### Claude Code (CLI)

- **Config file:** `~/.claude.json` (user/local scope) or `.mcp.json` (project scope)
- **Key:** `mcpServers`
- **CLI:** `claude mcp add`, `claude mcp add-json`, `claude mcp list`, `claude mcp remove`
- **Scopes:** local (default, per-project private), project (`.mcp.json`, shared via git), user (global)
- **Env injection:** `CLAUDE_PROJECT_DIR` injected into stdio server env
- **Auto-registration possible?** No — must use `claude mcp add` CLI or edit config file

Config format:
```json
{
  "mcpServers": {
    "contextmcp": {
      "command": "contextmcp",
      "args": []
    }
  }
}
```

### Claude Desktop

- **Config file:** `claude_desktop_config.json`
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- **Key:** `mcpServers`
- **CLI:** `mcp install server.py --name "Name"` (from MCP SDK)
- **Auto-registration possible?** Partially — `mcp install` can write config, but requires the server file path

Config format:
```json
{
  "mcpServers": {
    "contextmcp": {
      "command": "/absolute/path/to/contextmcp",
      "args": []
    }
  }
}
```

### Cursor

- **Config file:** `.cursor/mcp.json` (project) or `~/.cursor/mcp.json` (global)
  - Windows: `%USERPROFILE%\.cursor\mcp.json`
- **Key:** `mcpServers`
- **Auto-registration possible?** No — must edit config file manually
- **Project config takes precedence over global**

Config format:
```json
{
  "mcpServers": {
    "contextmcp": {
      "command": "contextmcp",
      "args": []
    }
  }
}
```

### VS Code / GitHub Copilot

- **Config file:** `.vscode/mcp.json` (workspace) or user profile `mcp.json`
- **Key:** `servers` (NOT `mcpServers` — this is the key difference!)
- **CLI:** `code --add-mcp '{...}'`
- **Command palette:** `MCP: Add Server`
- **Auto-registration possible?** No — must edit config or use command palette
- **Also supports:** `.mcp.json` at project root (portable across Agent Host)
- **User config:** `~/.copilot/mcp-config.json`

Config format:
```json
{
  "servers": {
    "contextmcp": {
      "type": "stdio",
      "command": "contextmcp",
      "args": []
    }
  }
}
```

### Windsurf

- Uses `mcpServers` key (similar to Cursor/Claude)
- Config at `~/.codeium/windsurf/mcp_config.json`

---

## Summary: Auto-Registration Feasibility

| Client | Auto-register? | Mechanism |
|--------|---------------|-----------|
| Claude Code | No | `claude mcp add` CLI or edit `~/.claude.json` |
| Claude Desktop | Partial | `mcp install` writes config, or manual edit |
| Cursor | No | Edit `.cursor/mcp.json` or `~/.cursor/mcp.json` |
| VS Code/Copilot | No | Edit `.vscode/mcp.json` or command palette |
| Windsurf | No | Edit `mcp_config.json` |

**Conclusion:** No client supports true zero-config auto-registration. ContextMCP must:
1. Detect installed clients
2. Offer to write config files (with backup + merge, never overwrite)
3. Provide exact copy-paste config snippets
4. Be technically honest about what's possible

---

## Dependency Strategy

Core dependencies (minimal):
- `mcp>=2.0.0` — MCP protocol SDK
- `pydantic>=2.0` — data models (comes with mcp)
- No external databases, no cloud, no daemon

Standard library for:
- SQLite (`sqlite3`) — persistent storage
- FTS5 — full-text search (built into SQLite)
- `pathlib` — path handling
- `json` — config files
- `subprocess` — git commands
- `hashlib` — file hashing, project fingerprints
- `os`/`sys` — environment detection
- `re` — pattern matching for secrets
- `click` — CLI (lightweight, well-maintained)

---

## Python Version Support

- MCP SDK v2 requires Python 3.10+
- Target: Python 3.10, 3.11, 3.12, 3.13
