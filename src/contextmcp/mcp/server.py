"""MCP server — the core entry point for AI coding agents.

Running `dmcp` (or `python -m contextmcp.mcp.server`) starts the MCP
server over stdio, which is how MCP hosts launch it as a subprocess.
"""

from __future__ import annotations

from mcp.server import MCPServer

from contextmcp.mcp.tools import (
    context_decisions,
    context_delete,
    context_diagnostics,
    context_environment,
    context_get,
    context_git,
    context_project,
    context_recent,
    context_rules,
    context_save,
    context_search,
    context_summary,
    context_update,
)

mcp = MCPServer("D-MCP")


@mcp.tool()
def ctx_search(
    query: str,
    scope: str | None = None,
    limit: int = 5,
    token_budget: int = 1000,
    context_pack: str | None = None,
) -> str:
    """Search persistent project context for rules, decisions, conventions, and facts.

    Use this BEFORE writing code to understand project patterns and avoid inconsistencies.
    Returns relevant memories within the specified token budget.
    """
    return context_search(query, scope, limit, token_budget, context_pack)


@mcp.tool()
def ctx_get(memory_id: str) -> str:
    """Get a specific memory by its ID with full provenance."""
    return context_get(memory_id)


@mcp.tool()
def ctx_save(
    content: str,
    type: str = "project_rule",
    scope: str = "project",
    source: str | None = None,
    source_type: str = "user",
    confidence: float = 0.8,
    importance: float = 0.5,
    tags: list[str] | None = None,
) -> str:
    """Save a memory, decision, rule, or fact to persistent context.

    Use this to store technical decisions, project rules, coding conventions,
    or any important context that should persist across AI coding sessions.
    """
    return context_save(content, type, scope, source, source_type, confidence, importance, tags)


@mcp.tool()
def ctx_update(
    memory_id: str,
    content: str | None = None,
    confidence: float | None = None,
    importance: float | None = None,
    tags: list[str] | None = None,
) -> str:
    """Update an existing memory. Only provided fields are changed."""
    return context_update(memory_id, content, confidence, importance, tags)


@mcp.tool()
def ctx_delete(memory_id: str) -> str:
    """Delete a memory from persistent context."""
    return context_delete(memory_id)


@mcp.tool()
def ctx_project() -> str:
    """Get current project information: name, language, framework, root, git status."""
    return context_project()


@mcp.tool()
def ctx_rules() -> str:
    """Get all project rules and coding conventions."""
    return context_rules()


@mcp.tool()
def ctx_decisions() -> str:
    """Get all technical/architecture decisions with reasoning."""
    return context_decisions()


@mcp.tool()
def ctx_recent(limit: int = 10) -> str:
    """Get recent memories and latest session summary for continuity between sessions."""
    return context_recent(limit)


@mcp.tool()
def ctx_git(detail: str = "summary") -> str:
    """Get Git intelligence: recent commits, changed files, branches, TODOs/FIXMEs.

    detail can be: summary, commits, files, todos
    """
    return context_git(detail)


@mcp.tool()
def ctx_environment(detailed: bool = False) -> str:
    """Get environment intelligence: Python version, venv, dependencies, Docker, .env status."""
    return context_environment(detailed)


@mcp.tool()
def ctx_diagnostics() -> str:
    """Run environment diagnostics: missing env vars, config issues, health checks."""
    return context_diagnostics()


@mcp.tool()
def ctx_summary() -> str:
    """Get a compact project context summary for handoff between sessions or agents.

    Includes project info, key rules, recent decisions, environment status, and latest session.
    """
    return context_summary()


def run() -> None:
    """Run the MCP server over stdio (default transport)."""
    mcp.run()


if __name__ == "__main__":
    run()
