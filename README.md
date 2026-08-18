# Promem-MCP

> Project Memory MCP — persistent project context for AI coding agents. Built by DIP-RO.

```bash
pip install promem-mcp
```

**No database. No cloud. No daemon. No manual memory management.**

ContextMCP is a local-first, MCP-native context runtime that gives AI coding agents persistent project understanding — architecture, rules, decisions, conventions, environment intelligence, and Git context — without repeated explanations or context waste.

## Quick Start

```bash
pip install promem-mcp
```

Then register ContextMCP with your AI coding client:

```bash
# See which clients are detected
promem config

# Auto-configure a specific client (with backup + merge)
promem config cursor
promem config claude-code
promem config claude-desktop
promem config vscode
```

Or manually add to your client's MCP config:

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

> **VS Code note:** VS Code uses `"servers"` key, not `"mcpServers"`. Run `promem config vscode` for the correct format.

That's it. Your AI coding agent now has persistent project context.

## How It Works

```
pip install promem-mcp
        │
        ▼
┌───────────────────┐
│    ContextMCP     │
│  Python Package   │
└─────────┬─────────┘
          │
  automatic project detection
          │
  ┌───────┼───────┐
  ▼       ▼       ▼
Project  Env    Git
Context  Context Context
  │       │       │
  └───────┼───────┘
          ▼
  Persistent Memory (SQLite)
          ▼
  Intelligent Retrieval (FTS5)
          ▼
  Token Optimization
          ▼
  MCP Server (stdio)
          ▼
  AI Coding Agent
```

## Features

- **Zero-setup storage** — SQLite database created automatically in OS-appropriate directory
- **Automatic project detection** — language, framework, package manager, test framework
- **Persistent memory** — rules, decisions, conventions, environment facts, Git intelligence
- **Token-efficient retrieval** — FTS5 search with token budgeting, returns only relevant context
- **Provenance tracking** — every memory knows where it came from and how confident it is
- **Secret redaction** — API keys, tokens, passwords are never stored or returned
- **Project isolation** — project memories never leak across projects
- **Stale context detection** — flags memories that conflict with current project state
- **Contradiction detection** — identifies conflicting project rules
- **Session continuity** — handoff summaries for switching between agents/sessions
- **Git intelligence** — recent commits, changed files, TODOs/FIXMEs
- **Environment diagnostics** — Python version, venv, .env completeness, Docker
- **Local-first** — no network requests, no cloud, no external services

## MCP Tools

| Tool | Description |
|------|-------------|
| `ctx_search` | Search persistent project context with token budget |
| `ctx_get` | Get a specific memory by ID |
| `ctx_save` | Save a memory, decision, rule, or fact |
| `ctx_update` | Update an existing memory |
| `ctx_delete` | Delete a memory |
| `ctx_project` | Get current project information |
| `ctx_rules` | Get all project rules and conventions |
| `ctx_decisions` | Get all technical/architecture decisions |
| `ctx_recent` | Get recent memories and latest session |
| `ctx_git` | Get Git intelligence |
| `ctx_environment` | Get environment intelligence |
| `ctx_diagnostics` | Run environment diagnostics |
| `ctx_summary` | Get compact project summary for handoff |

## CLI

```bash
contextmcp --version        # Version
promem status           # Project + storage status
promem doctor           # Health checks
promem stats            # Usage statistics
promem search "query"   # Search context
promem memory list      # List memories
promem decision "text"  # Save a decision
promem privacy          # Privacy info
promem config           # Client configuration
promem repair           # Rebuild index, optimize DB
promem reset            # Delete all data (with confirmation)
```

## Client Support

| Client | Auto-config? | Config Key |
|--------|-------------|------------|
| Claude Code | `promem config claude-code` | `mcpServers` |
| Claude Desktop | `promem config claude-desktop` | `mcpServers` |
| Cursor | `promem config cursor` | `mcpServers` |
| VS Code / Copilot | `promem config vscode` | `servers` |
| OpenCode | `promem config opencode` | `mcp` |
| Gemini CLI | `promem config gemini-cli` | `mcpServers` |
| Windsurf | `promem config windsurf` | `mcpServers` |
| Cline | `promem config cline` | `mcpServers` |
| Roo Code | `promem config roo-code` | `mcpServers` |
| Amazon Q | `promem config amazon-q` | `mcpServers` |
| ZCode (GLM/Zhipu) | `promem config zcode` | `mcpServers` |
| Tabnine | `promem config tabnine` | `mcpServers` |

No client supports true zero-config auto-registration. ContextMCP detects installed clients, offers to write config (with backup + merge), and provides exact copy-paste snippets.

## Privacy

- **Local only** — no network requests
- **Project contents not uploaded**
- **Secrets redacted** — never stored or returned
- **No cloud dependencies**

```bash
promem privacy
```

## Storage Location

ContextMCP uses **project-local storage** — no centralized OS directory, no wasted space.

| Location | Path |
|----------|------|
| Project-local (default) | `<project-root>/.contextmcp/` |

Each project gets its own `.contextmcp/contextmcp.db`. Storage travels with the project. No global storage bloat.

Add `.contextmcp/` to your `.gitignore` (already included by default in ContextMCP's ignore patterns).

Override with `CONTEXTMCP_DATA_DIR` environment variable if needed.

## Installation

```bash
# pip
pip install promem-mcp

# uv
uv add contextmcp

# pipx (global CLI)
pipx install contextmcp
```

Works in venv, virtualenv, uv, pipx, and system Python.

## Development

```bash
git clone https://github.com/contextmcp/contextmcp.git
cd contextmcp
pip install -e ".[dev]"
pytest
```

## License

MIT
