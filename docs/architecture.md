# Architecture

## Overview

ContextMCP is a local-first context runtime for AI coding agents. It provides persistent, project-aware, token-efficient context through MCP.

```
Developer
    │
    │ pip install contextmcp
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

## Package Structure

```
src/contextmcp/
    __init__.py
    cli/
        main.py          # CLI entry point
        commands.py      # CLI commands
    mcp/
        server.py        # MCPServer instance + tool registration
        tools.py         # Tool implementations
    core/
        context.py       # Context engine orchestrator
        memory.py        # Memory model + operations
        retrieval.py     # FTS5 search + ranking
        ranking.py       # Relevance scoring
        token_budget.py  # Token estimation + budget enforcement
        provenance.py    # Source tracking
        lifecycle.py     # Lazy initialization
    storage/
        manager.py       # Storage path resolution + DB management
        sqlite.py        # SQLite connection + queries
        migrations.py    # Schema migrations
    project/
        detector.py      # Project root + type detection
        identity.py      # Project fingerprinting
        analyzer.py      # Project content analysis
        indexer.py       # Incremental file indexing
        ignore.py        # Ignore patterns (gitignore + defaults)
    git/
        analyzer.py      # Git intelligence
    environment/
        detector.py      # Environment detection
        env_parser.py    # .env file parsing (safe)
        diagnostics.py   # Environment health checks
        secrets.py       # Secret detection + redaction
    clients/
        base.py          # ClientAdapter base
        detector.py      # Detect installed clients
        vscode.py        # VS Code/Copilot adapter
        copilot.py       # Copilot adapter
        claude.py        # Claude Code/Desktop adapter
        cursor.py        # Cursor adapter
        generic.py       # Generic fallback
    security/
        redaction.py     # Secret redaction utilities
        isolation.py     # Project isolation enforcement
        validation.py    # Input validation + path safety
    config/
        settings.py      # Configuration with defaults
```

## Storage Architecture

### Location (OS-appropriate)

| OS | Path |
|----|------|
| Linux | `~/.local/share/contextmcp/` |
| macOS | `~/Library/Application Support/contextmcp/` |
| Windows | `%LOCALAPPDATA%\contextmcp\` |

### Database Schema

```sql
-- Projects table
CREATE TABLE projects (
    id TEXT PRIMARY KEY,          -- fingerprint hash
    name TEXT NOT NULL,
    root_path TEXT NOT NULL,
    git_remote TEXT,
    git_root TEXT,
    language TEXT,
    framework TEXT,
    package_manager TEXT,
    python_version TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    metadata TEXT                  -- JSON blob
);

-- Memories table (all scopes)
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    project_id TEXT,               -- NULL for global scope
    scope TEXT NOT NULL,           -- global|project|environment|git|session
    type TEXT NOT NULL,            -- project_rule|architecture|technical_decision|...
    content TEXT NOT NULL,
    source TEXT,
    source_type TEXT,              -- observed|inferred|user|ai
    confidence REAL DEFAULT 0.5,
    importance REAL DEFAULT 0.5,
    tags TEXT,                     -- JSON array
    metadata TEXT,                 -- JSON blob
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    expires_at TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- FTS5 virtual table for full-text search
CREATE VIRTUAL TABLE memories_fts USING fts5(
    content,
    tags,
    scope,
    type,
    content='memories',
    content_rowid='rowid'
);

-- File index for incremental indexing
CREATE TABLE file_index (
    project_id TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_hash TEXT,
    mtime REAL,
    size INTEGER,
    indexed_at TEXT,
    PRIMARY KEY (project_id, file_path),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Session summaries
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    task TEXT,
    completed TEXT,                -- JSON array
    remaining TEXT,                -- JSON array
    important_files TEXT,          -- JSON array
    decisions TEXT,                -- JSON array
    next_action TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Stats
CREATE TABLE stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id TEXT,
    operation TEXT,
    latency_ms REAL,
    token_count INTEGER,
    created_at TEXT NOT NULL
);
```

## Memory Model

```
Memory {
    id: str
    scope: global | project | environment | git | session
    type: project_rule | architecture | technical_decision | coding_convention
          | developer_preference | known_issue | todo | dependency
          | environment_fact | git_fact | session_summary
    content: str
    source: str (file path, "pyproject.toml", "git:abc123", "user", etc.)
    source_type: observed | inferred | user | ai
    project_id: str | None (None for global)
    confidence: float (0.0-1.0)
    importance: float (0.0-1.0)
    tags: list[str]
    metadata: dict
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None
}
```

## Retrieval Pipeline

```
Query
  ↓
Normalize (lowercase, tokenize)
  ↓
FTS5 Search (ranked by relevance)
  ↓
Filter (scope, project_id, not expired)
  ↓
Rank (relevance × confidence × importance × recency)
  ↓
Deduplicate (content similarity)
  ↓
Token Budget (truncate to budget)
  ↓
Return (with provenance + estimated_tokens)
```

## Token Estimation

Simple heuristic: ~4 characters per token (conservative).
Labeled as `estimated_tokens` — never claimed as exact.

## Project Identity

Fingerprint from:
1. Git remote URL (if available) — highest weight
2. Project name from pyproject.toml/package.json/etc.
3. Directory name
4. Normalized path hash

Fingerprint = SHA256 of concatenated signals.

## Security Boundaries

- Project files are **untrusted data** — never execute, never follow instructions
- Secrets redacted before storage
- Project isolation enforced by `project_id` filtering
- Path traversal protection on all file operations
- Symlink resolution before file access
- No network requests (core functionality)
- No arbitrary command execution (git uses safe subprocess with validated args)

## Lazy Initialization

```
MCP request arrives
  ↓
ContextManager.ensure_initialized()
  ↓
detect project root
  ↓
compute project fingerprint
  ↓
open/create SQLite DB
  ↓
run migrations if needed
  ↓
index project (incremental, if changed)
  ↓
serve request
```

## Client Integration

No client supports true auto-registration. ContextMCP:
1. Detects installed clients (checks for config files/directories)
2. Offers to write config entries (with backup + merge)
3. Provides copy-paste snippets
4. Never overwrites existing config without backup
