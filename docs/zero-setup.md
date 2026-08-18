# Zero-Setup Design

ContextMCP is designed to be as close to zero-setup as technically possible.

## What's Automatic

- **Storage** — SQLite database created automatically in OS-appropriate directory
- **Project detection** — Language, framework, package manager detected on first use
- **Project identity** — Stable fingerprint computed from git remote, name, path
- **Indexing** — Incremental file indexing on first MCP request
- **Memory initialization** — Lazy initialization on first tool call

## What's Not Automatic

No MCP client supports true zero-config server registration. ContextMCP requires one configuration step:

```bash
contextmcp config <client-name>
```

This writes the MCP server entry to the client's config file (with backup + merge, never overwriting existing servers).

## Why Not Fully Zero-Setup?

Each AI coding client (Claude Code, Cursor, VS Code, etc.) requires an entry in its own config file to know how to launch the MCP server. There is no universal auto-discovery mechanism. ContextMCP:

1. Detects installed clients
2. Offers to write config automatically (with backup)
3. Provides exact copy-paste snippets if auto-write isn't desired
4. Never claims zero-setup where it's not technically possible

## No Mandatory Commands

There is no required `init`, `setup`, `serve`, or `start` command. Running `contextmcp` with no arguments starts the MCP server over stdio — that's how MCP hosts launch it.
