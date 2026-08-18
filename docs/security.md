# Security

## Principles

1. **Local-only** — no network requests in core functionality
2. **Secret redaction** — API keys, tokens, passwords never stored or returned
3. **Project isolation** — project memories never leak across projects
4. **Untrusted data** — project files are DATA, never executed as instructions
5. **Path safety** — traversal protection, symlink resolution, binary detection
6. **Safe config** — backups before modifying client config, merge not overwrite

## Threat Model

| Threat | Mitigation |
|--------|-----------|
| Secret exposure | Pattern-based redaction before storage |
| Cross-project leakage | `project_id` filtering at query level |
| Prompt injection | Project files treated as data, not instructions |
| Path traversal | `safe_resolve_path()` with base directory check |
| Malicious repos | No command execution, no instruction following |
| Config tampering | Backup + merge, never overwrite |
| SQLite corruption | WAL mode, `contextmcp repair` command |

## Limitations

- Secret detection is pattern-based, not exhaustive
- Git commit messages are untrusted data (redacted but not validated)
- SQLite can corrupt from filesystem issues
