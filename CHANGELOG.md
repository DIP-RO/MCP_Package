# Changelog

## 0.1.0 — 2026-08-18

### Added
- Initial release
- MCP server with 13 tools (ctx_search, ctx_save, ctx_get, ctx_update, ctx_delete, ctx_project, ctx_rules, ctx_decisions, ctx_recent, ctx_git, ctx_environment, ctx_diagnostics, ctx_summary)
- Automatic project detection (language, framework, package manager, test framework)
- Project fingerprinting for stable identity across directory moves
- SQLite + FTS5 persistent storage (auto-created, no setup)
- Token-budget-aware retrieval with ranking and deduplication
- Memory model with scopes (global, project, environment, git, session)
- Provenance tracking (source, source_type, confidence)
- Secret detection and redaction
- Project isolation enforcement
- Stale context and contradiction detection
- Git intelligence (commits, changed files, TODOs/FIXMEs)
- Environment intelligence (Python version, venv, .env diagnostics)
- Client adapters (Claude Code, Claude Desktop, Cursor, VS Code/Copilot)
- CLI (status, doctor, stats, search, memory, decision, privacy, config, repair, reset)
- Incremental file indexing with mtime/hash checks
- Session continuity and handoff summaries
- Cross-platform support (macOS, Linux, Windows)
