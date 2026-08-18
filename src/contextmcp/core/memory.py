"""Memory model and operations."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from contextmcp.security.validation import (
    validate_memory_type,
    validate_scope,
    validate_source_type,
)
from contextmcp.storage.sqlite import SQLiteStore


class MemoryError(Exception):
    pass


class MemoryManager:
    """Manages memory CRUD operations with validation."""

    def __init__(self, store: SQLiteStore):
        self.store = store

    def save(
        self,
        content: str,
        scope: str = "project",
        mem_type: str = "project_rule",
        project_id: str | None = None,
        source: str | None = None,
        source_type: str = "observed",
        confidence: float = 0.5,
        importance: float = 0.5,
        tags: list[str] | None = None,
        metadata: dict | None = None,
        expires_at: str | None = None,
        deduplicate: bool = True,
    ) -> dict:
        """Save a memory. Returns the saved memory dict."""
        if not content or not content.strip():
            raise MemoryError("Content cannot be empty")
        if not validate_scope(scope):
            raise MemoryError(f"Invalid scope: {scope}")
        if not validate_memory_type(mem_type):
            raise MemoryError(f"Invalid memory type: {mem_type}")
        if not validate_source_type(source_type):
            raise MemoryError(f"Invalid source type: {source_type}")

        # Enforce project isolation: project-scoped memories need project_id
        if scope != "global" and project_id is None:
            raise MemoryError(f"Non-global scope '{scope}' requires project_id")

        # Deduplicate: check for similar existing memories
        if deduplicate:
            similar = self.store.find_similar(content, project_id, limit=3)
            for sim in similar:
                if _content_similarity(content.lower(), sim["content"].lower()) > 0.85:
                    # Update existing memory instead of creating duplicate
                    self.store.update_memory(
                        sim["id"],
                        content=content,
                        confidence=max(confidence, sim.get("confidence", 0.5)),
                        importance=max(importance, sim.get("importance", 0.5)),
                        tags=tags or sim.get("tags"),
                        metadata=metadata or sim.get("metadata"),
                    )
                    return self.store.get_memory(sim["id"])

        mem_id = str(uuid.uuid4())
        self.store.insert_memory(
            mem_id=mem_id,
            project_id=project_id,
            scope=scope,
            mem_type=mem_type,
            content=content,
            source=source,
            source_type=source_type,
            confidence=confidence,
            importance=importance,
            tags=tags,
            metadata=metadata,
            expires_at=expires_at,
        )
        return self.store.get_memory(mem_id)

    def get(self, mem_id: str) -> dict | None:
        return self.store.get_memory(mem_id)

    def update(
        self,
        mem_id: str,
        content: str | None = None,
        confidence: float | None = None,
        importance: float | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> dict | None:
        success = self.store.update_memory(
            mem_id, content, confidence, importance, tags, metadata
        )
        if success:
            return self.store.get_memory(mem_id)
        return None

    def delete(self, mem_id: str) -> bool:
        return self.store.delete_memory(mem_id)

    def list(
        self,
        project_id: str | None = None,
        scope: str | None = None,
        mem_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        return self.store.list_memories(project_id, scope, mem_type, limit, offset)

    def count(self, project_id: str | None = None) -> int:
        return self.store.count_memories(project_id)

    def save_decision(
        self,
        decision: str,
        reason: str | None = None,
        affected: list[str] | None = None,
        project_id: str | None = None,
        source: str = "user",
    ) -> dict:
        """Save a technical decision as a first-class memory."""
        content = f"Decision: {decision}"
        if reason:
            content += f"\nReason: {reason}"
        if affected:
            content += f"\nAffected: {', '.join(affected)}"

        return self.save(
            content=content,
            scope="project",
            mem_type="technical_decision",
            project_id=project_id,
            source=source,
            source_type="user" if source == "user" else "ai",
            confidence=0.95,
            importance=0.9,
            tags=["decision"] + (affected or []),
            metadata={"reason": reason, "affected": affected},
        )

    def save_session_summary(
        self,
        project_id: str,
        task: str,
        completed: list[str] | None = None,
        remaining: list[str] | None = None,
        important_files: list[str] | None = None,
        decisions: list[str] | None = None,
        next_action: str | None = None,
    ) -> dict:
        """Save a session summary for continuity."""
        session_id = str(uuid.uuid4())
        self.store.insert_session(
            session_id=session_id,
            project_id=project_id,
            task=task,
            completed=completed,
            remaining=remaining,
            important_files=important_files,
            decisions=decisions,
            next_action=next_action,
        )

        # Also save as a memory with expiry
        content_parts = [f"Task: {task}"]
        if completed:
            content_parts.append(f"Completed: {', '.join(completed)}")
        if remaining:
            content_parts.append(f"Remaining: {', '.join(remaining)}")
        if next_action:
            content_parts.append(f"Next: {next_action}")

        expires = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()

        return self.save(
            content="\n".join(content_parts),
            scope="session",
            mem_type="session_summary",
            project_id=project_id,
            source="ai",
            source_type="ai",
            confidence=0.8,
            importance=0.7,
            tags=["session", "handoff"],
            metadata={
                "session_id": session_id,
                "important_files": important_files,
                "decisions": decisions,
            },
            expires_at=expires,
        )


def _content_similarity(a: str, b: str) -> float:
    """Jaccard similarity between two strings."""
    set_a = set(a.split())
    set_b = set(b.split())
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)
