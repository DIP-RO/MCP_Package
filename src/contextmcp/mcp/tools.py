"""MCP tool implementations — all context_* tools."""

from __future__ import annotations

import json
from typing import Annotated, Any
from typing import Literal

from pydantic import Field

from contextmcp.core.lifecycle import get_engine
from contextmcp.core.memory import MemoryError, MemoryManager
from contextmcp.core.retrieval import Retriever
from contextmcp.core.token_budget import estimate_tokens
from contextmcp.environment.diagnostics import run_diagnostics
from contextmcp.environment.detector import EnvironmentInfo
from contextmcp.git.analyzer import GitAnalyzer
from contextmcp.project.analyzer import analyze_project_files
from contextmcp.project.indexer import Indexer
from contextmcp.core.context import detect_stale_memories, detect_contradictions
from contextmcp.project.detector import detect_project
from contextmcp.security.redaction import redact_text


def _get_engine_components():
    """Get engine and its components."""
    engine = get_engine()
    return engine, engine.memory, engine.retriever, engine.store, engine.project_id, engine.project_info


def context_search(
    query: Annotated[str, Field(description="Natural language search query for project context")],
    scope: Annotated[str | None, Field(description="Filter by scope: global, project, environment, git, session")] = None,
    limit: Annotated[int, Field(ge=1, le=50, description="Maximum number of results")] = 5,
    token_budget: Annotated[int, Field(ge=100, le=10000, description="Max estimated tokens to return")] = 1000,
    context_pack: Annotated[str | None, Field(description="Focus area: backend, frontend, database, testing, deployment, architecture")] = None,
) -> str:
    """Search persistent project context. Returns relevant memories within token budget.

    Use this to find project rules, architecture decisions, coding conventions,
    and other stored context before writing code or answering questions.
    """
    engine, memory, retriever, store, project_id, _ = _get_engine_components()
    result = retriever.search(
        query=query,
        project_id=project_id,
        scope=scope,
        limit=limit,
        token_budget=token_budget,
        context_pack=context_pack,
    )
    return json.dumps(result.to_dict(), indent=2)


def context_get(
    memory_id: Annotated[str, Field(description="ID of the memory to retrieve")],
) -> str:
    """Get a specific memory by ID. Returns full memory with provenance."""
    engine, memory, _, _, _, _ = _get_engine_components()
    mem = memory.get(memory_id)
    if mem is None:
        return json.dumps({"error": "Memory not found", "id": memory_id})
    return json.dumps(mem, indent=2, default=str)


def context_save(
    content: Annotated[str, Field(description="The context/memory content to store")],
    type: Annotated[str, Field(description="Memory type: project_rule, architecture, technical_decision, coding_convention, developer_preference, known_issue, todo, dependency, environment_fact, git_fact, session_summary")] = "project_rule",
    scope: Annotated[str, Field(description="Memory scope: global, project, environment, git, session")] = "project",
    source: Annotated[str | None, Field(description="Where this memory came from")] = None,
    source_type: Annotated[str, Field(description="Source type: observed, inferred, user, ai")] = "user",
    confidence: Annotated[float, Field(ge=0.0, le=1.0, description="Confidence in this memory (0.0-1.0)")] = 0.8,
    importance: Annotated[float, Field(ge=0.0, le=1.0, description="Importance level (0.0-1.0)")] = 0.5,
    tags: Annotated[list[str] | None, Field(description="Tags for categorization")] = None,
) -> str:
    """Save a memory, decision, rule, or fact to persistent context.

    Use this to store technical decisions, project rules, coding conventions,
    or any important context that should persist across sessions.
    """
    engine, memory, _, store, project_id, _ = _get_engine_components()

    # Global scope doesn't need project_id
    pid = None if scope == "global" else project_id

    try:
        mem = memory.save(
            content=content,
            scope=scope,
            mem_type=type,
            project_id=pid,
            source=source,
            source_type=source_type,
            confidence=confidence,
            importance=importance,
            tags=tags,
        )
        return json.dumps({"status": "saved", "memory": mem}, indent=2, default=str)
    except MemoryError as e:
        return json.dumps({"error": str(e)})


def context_update(
    memory_id: Annotated[str, Field(description="ID of the memory to update")],
    content: Annotated[str | None, Field(description="New content")] = None,
    confidence: Annotated[float | None, Field(ge=0.0, le=1.0, description="New confidence value")] = None,
    importance: Annotated[float | None, Field(ge=0.0, le=1.0, description="New importance value")] = None,
    tags: Annotated[list[str] | None, Field(description="New tags")] = None,
) -> str:
    """Update an existing memory. Only provided fields are changed."""
    engine, memory, _, _, _, _ = _get_engine_components()
    mem = memory.update(memory_id, content, confidence, importance, tags)
    if mem is None:
        return json.dumps({"error": "Memory not found or no changes", "id": memory_id})
    return json.dumps({"status": "updated", "memory": mem}, indent=2, default=str)


def context_delete(
    memory_id: Annotated[str, Field(description="ID of the memory to delete")],
) -> str:
    """Delete a memory from persistent context."""
    engine, memory, _, _, _, _ = _get_engine_components()
    success = memory.delete(memory_id)
    if success:
        return json.dumps({"status": "deleted", "id": memory_id})
    return json.dumps({"error": "Memory not found", "id": memory_id})


def context_project() -> str:
    """Get current project information: name, language, framework, root, git status."""
    engine, _, _, store, project_id, info = _get_engine_components()
    return json.dumps({
        "project_id": project_id,
        "name": info.name,
        "root": str(info.root),
        "language": info.language,
        "framework": info.framework,
        "package_manager": info.package_manager,
        "python_version": info.python_version,
        "test_framework": info.test_framework,
        "git_root": str(info.git_root) if info.git_root else None,
        "git_remote": info.git_remote,
        "markers_found": info.markers_found,
        "instruction_files": [str(f) for f in info.instruction_files],
    }, indent=2)


def context_rules() -> str:
    """Get all project rules and coding conventions."""
    engine, memory, _, store, project_id, _ = _get_engine_components()
    rules = memory.list(project_id=project_id, mem_type="project_rule", limit=50)
    conventions = memory.list(project_id=project_id, mem_type="coding_convention", limit=50)
    global_rules = memory.list(scope="global", mem_type="developer_preference", limit=20)

    all_rules = rules + conventions + global_rules
    compact = []
    for r in all_rules:
        compact.append({
            "content": r.get("content"),
            "source": r.get("source"),
            "type": r.get("type"),
            "confidence": r.get("confidence"),
        })
    return json.dumps({"rules": compact, "count": len(compact)}, indent=2)


def context_decisions() -> str:
    """Get all technical/architecture decisions with reasoning."""
    engine, memory, _, store, project_id, _ = _get_engine_components()
    decisions = memory.list(project_id=project_id, mem_type="technical_decision", limit=50)
    compact = []
    for d in decisions:
        compact.append({
            "content": d.get("content"),
            "source": d.get("source"),
            "metadata": d.get("metadata", {}),
            "created_at": d.get("created_at"),
        })
    return json.dumps({"decisions": compact, "count": len(compact)}, indent=2)


def context_recent(
    limit: Annotated[int, Field(ge=1, le=50, description="Number of recent items")] = 10,
) -> str:
    """Get recent memories and latest session summary for continuity."""
    engine, memory, _, store, project_id, _ = _get_engine_components()
    recent = memory.list(project_id=project_id, limit=limit)
    session = store.get_latest_session(project_id)

    result = {
        "recent_memories": [
            {
                "content": m.get("content"),
                "type": m.get("type"),
                "source": m.get("source"),
                "updated_at": m.get("updated_at"),
            }
            for m in recent
        ],
        "latest_session": session,
    }
    return json.dumps(result, indent=2, default=str)


def context_git(
    detail: Annotated[str, Field(description="Level of detail: summary, commits, files, todos")] = "summary",
) -> str:
    """Get Git intelligence: recent commits, changed files, branches, TODOs/FIXMEs."""
    engine, _, _, _, _, info = _get_engine_components()
    if not info.git_root:
        return json.dumps({"error": "No Git repository detected"})

    analyzer = GitAnalyzer(info.git_root)

    if detail == "summary":
        return json.dumps(analyzer.get_summary(), indent=2, default=str)
    elif detail == "commits":
        return json.dumps({"commits": analyzer.get_recent_commits(20)}, indent=2, default=str)
    elif detail == "files":
        return json.dumps({"changed_files": analyzer.get_changed_files()}, indent=2, default=str)
    elif detail == "todos":
        return json.dumps({"todos_fixmes": analyzer.find_todos_fixmes()}, indent=2, default=str)
    else:
        return json.dumps(analyzer.get_summary(), indent=2, default=str)


def context_environment(
    detailed: Annotated[bool, Field(description="Include installed packages and env vars")] = False,
) -> str:
    """Get environment intelligence: Python version, venv, dependencies, Docker, .env status."""
    env = EnvironmentInfo()
    if detailed:
        data = env.to_detailed_dict()
    else:
        data = env.to_dict()
    return json.dumps(data, indent=2, default=str)


def context_diagnostics() -> str:
    """Run environment diagnostics: missing env vars, config issues, health checks."""
    engine, _, _, _, _, info = _get_engine_components()
    result = run_diagnostics(info.root)
    return json.dumps(result, indent=2, default=str)


def context_summary() -> str:
    """Get a compact project context summary for handoff between sessions/agents.

    Includes project info, key rules, recent decisions, environment status, and latest session.
    """
    engine, memory, _, store, project_id, info = _get_engine_components()

    # Gather compact context
    project = {
        "name": info.name,
        "language": info.language,
        "framework": info.framework,
        "root": str(info.root),
    }

    rules = memory.list(project_id=project_id, mem_type="project_rule", limit=5)
    decisions = memory.list(project_id=project_id, mem_type="technical_decision", limit=5)
    architecture = memory.list(project_id=project_id, mem_type="architecture", limit=5)
    session = store.get_latest_session(project_id)

    env = EnvironmentInfo()
    env_summary = {
        "python_version": env.python_version,
        "virtual_env": env.virtual_env,
        "venv_type": env.venv_type,
    }

    # Check for stale/contradictions
    all_memories = memory.list(project_id=project_id, limit=100)
    stale = detect_stale_memories(all_memories, [])
    contradictions = detect_contradictions(all_memories)

    summary = {
        "project": project,
        "key_rules": [r.get("content") for r in rules],
        "recent_decisions": [d.get("content") for d in decisions],
        "architecture": [a.get("content") for a in architecture],
        "environment": env_summary,
        "latest_session": session,
        "stale_warnings": len(stale),
        "contradiction_warnings": len(contradictions),
        "total_memories": memory.count(project_id),
    }

    estimated = estimate_tokens(json.dumps(summary))
    summary["estimated_tokens"] = estimated

    return json.dumps(summary, indent=2, default=str)
