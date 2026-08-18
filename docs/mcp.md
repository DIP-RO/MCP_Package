# MCP Integration

## Server

ContextMCP uses the official MCP Python SDK v2 (`mcp>=2.0.0`).

The server is defined in `src/contextmcp/mcp/server.py`:

```python
from mcp.server import MCPServer

mcp = MCPServer("ContextMCP")

@mcp.tool()
def ctx_search(query: str, ...) -> str:
    """Search persistent project context."""
    ...

mcp.run()  # defaults to stdio
```

## Transport

ContextMCP uses **stdio** transport only — the host client launches `contextmcp` as a subprocess and communicates over stdin/stdout.

## Tools

| Tool | Description |
|------|-------------|
| `ctx_search` | Search context with token budget |
| `ctx_get` | Get memory by ID |
| `ctx_save` | Save memory/decision/rule |
| `ctx_update` | Update memory |
| `ctx_delete` | Delete memory |
| `ctx_project` | Project information |
| `ctx_rules` | Project rules + conventions |
| `ctx_decisions` | Technical decisions |
| `ctx_recent` | Recent memories + session |
| `ctx_git` | Git intelligence |
| `ctx_environment` | Environment info |
| `ctx_diagnostics` | Environment diagnostics |
| `ctx_summary` | Compact handoff summary |

## Client Configuration

See `docs/client-support.md` for per-client setup instructions.
