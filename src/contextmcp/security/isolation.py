"""Project isolation enforcement."""

from __future__ import annotations


class ProjectIsolationError(Exception):
    """Raised when project isolation would be violated."""
    pass


def assert_project_scope(memory: dict, project_id: str | None) -> None:
    """Ensure a memory belongs to the correct project scope."""
    mem_project = memory.get("project_id")
    mem_scope = memory.get("scope")

    # Global scope memories have no project_id — allowed everywhere
    if mem_scope == "global" and mem_project is None:
        return

    # Project-scoped memories must match
    if mem_project != project_id:
        raise ProjectIsolationError(
            f"Memory project_id={mem_project!r} does not match requested project_id={project_id!r}. "
            "Cross-project memory access is blocked."
        )


def filter_project_memories(memories: list[dict], project_id: str | None) -> list[dict]:
    """Filter memories to only include those belonging to the project or global scope."""
    result = []
    for mem in memories:
        scope = mem.get("scope")
        mem_pid = mem.get("project_id")
        if scope == "global" and mem_pid is None:
            result.append(mem)
        elif mem_pid == project_id:
            result.append(mem)
    return result
