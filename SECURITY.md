# Security Policy

## Reporting Vulnerabilities

Email: security@contextmcp.dev (or open a private security advisory on GitHub).

## Security Principles

ContextMCP is designed with the following security principles:

### 1. Local-Only by Default
- No network requests in core functionality
- No cloud dependencies
- All storage is local SQLite

### 2. Secret Redaction
- API keys, tokens, passwords, and private keys are detected and redacted
- Redacted values are never stored or returned to the AI agent
- Secret detection uses pattern matching and known variable names
- **Limitation:** Secret detection is heuristic and cannot guarantee 100% coverage

### 3. Project Isolation
- Project-scoped memories are filtered by `project_id`
- Cross-project memory access is blocked at the query level
- Global memories (developer preferences) are shared, but project facts are isolated

### 4. Untrusted Data Handling
- Project files (README, AGENTS.md, etc.) are treated as DATA, not instructions
- Content is never executed
- No arbitrary command execution
- Git commands use safe subprocess with validated arguments

### 5. Path Safety
- Path traversal protection on all file operations
- Symlink resolution before file access
- Binary file detection to prevent interpretation

### 6. Safe MCP Configuration
- Client config writes always create backups
- Existing MCP servers are preserved (merge, not overwrite)
- No silent configuration changes

## Known Limitations

- Secret detection is pattern-based, not exhaustive
- SQLite databases can be corrupted by filesystem issues (use `contextmcp repair`)
- Git data is untrusted (commit messages could contain malicious content — redacted but not validated)
