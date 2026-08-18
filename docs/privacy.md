# Privacy

## Default: Local Only

- **No network requests** — ContextMCP never sends data anywhere
- **No cloud dependencies** — all storage is local SQLite
- **No telemetry** — no usage data collected or transmitted
- **No external APIs** — no calls to OpenAI, Anthropic, Google, GitHub, etc.

## What's Stored Locally

- Project metadata (name, language, framework, path)
- Memories (rules, decisions, conventions, facts)
- File index (paths, hashes, mtimes)
- Session summaries
- Usage stats (query count, latency)

## What's NOT Stored

- Secret values (redacted before storage)
- File contents (only metadata and extracted facts)
- AI conversation content (ContextMCP cannot see conversations)

## Verification

```bash
contextmcp privacy
```

## Data Location

ContextMCP uses **project-local storage** — no centralized OS directory.

| Location | Path |
|----------|------|
| Project-local (default) | `<project-root>/.contextmcp/` |

Each project gets its own `.contextmcp/contextmcp.db`. No global storage. No wasted space on user's home directory.

Override with `CONTEXTMCP_DATA_DIR` environment variable.

## Deletion

```bash
contextmcp reset
```

Permanently deletes all ContextMCP data (with confirmation prompt).
