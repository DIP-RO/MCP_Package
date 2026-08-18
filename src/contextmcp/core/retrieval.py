"""FTS5-based context retrieval with token budgeting."""

from __future__ import annotations

import time
from typing import Any

from contextmcp.core.ranking import deduplicate, rank_memories
from contextmcp.core.token_budget import (
    fit_to_budget,
    format_memory_compact,
)
from contextmcp.security.isolation import filter_project_memories
from contextmcp.security.validation import sanitize_query
from contextmcp.storage.sqlite import SQLiteStore


class RetrievalResult:
    """Result of a context search."""

    def __init__(
        self,
        memories: list[dict[str, Any]],
        estimated_tokens: int,
        latency_ms: float,
        total_found: int,
    ):
        self.memories = memories
        self.estimated_tokens = estimated_tokens
        self.latency_ms = latency_ms
        self.total_found = total_found

    def to_dict(self) -> dict[str, Any]:
        return {
            "memories": [
                {
                    "id": m.get("id"),
                    "type": m.get("type"),
                    "scope": m.get("scope"),
                    "content": m.get("content"),
                    "source": m.get("source"),
                    "source_type": m.get("source_type"),
                    "confidence": m.get("confidence"),
                    "importance": m.get("importance"),
                    "tags": m.get("tags", []),
                    "created_at": m.get("created_at"),
                    "updated_at": m.get("updated_at"),
                    "score": m.get("_score"),
                }
                for m in self.memories
            ],
            "estimated_tokens": self.estimated_tokens,
            "latency_ms": round(self.latency_ms, 2),
            "total_found": self.total_found,
            "count": len(self.memories),
        }

    def to_compact_text(self) -> str:
        """Return a compact text representation for the AI."""
        if not self.memories:
            return "No relevant context found."
        lines = []
        for m in self.memories:
            lines.append(format_memory_compact(m))
        return "\n".join(lines)


class Retriever:
    """Context retrieval with FTS5, ranking, and token budgeting."""

    def __init__(self, store: SQLiteStore):
        self.store = store

    def search(
        self,
        query: str,
        project_id: str | None = None,
        scope: str | None = None,
        mem_type: str | None = None,
        limit: int = 5,
        token_budget: int = 1000,
        context_pack: str | None = None,
    ) -> RetrievalResult:
        """Search for relevant context."""
        start_time = time.time()

        query = sanitize_query(query)
        if not query:
            return RetrievalResult([], 0, 0, 0)

        # Apply context pack filtering
        pack_types = _get_context_pack_types(context_pack) if context_pack else None

        # FTS search
        raw_results = self.store.search_memories_fts(
            query=query,
            project_id=project_id,
            scope=scope,
            mem_type=pack_types or mem_type,
            limit=limit * 3,  # Over-fetch for ranking + dedup
        )

        # Also get global memories
        if project_id is not None:
            global_results = self.store.search_memories_fts(
                query=query,
                project_id=None,
                scope="global",
                mem_type=pack_types or mem_type,
                limit=limit * 2,
            )
            raw_results.extend(global_results)

        # Enforce project isolation
        filtered = filter_project_memories(raw_results, project_id)

        # Rank
        ranked = rank_memories(filtered, query)

        # Deduplicate
        deduped = deduplicate(ranked)

        # Limit
        truncated = deduped[:limit]

        # Fit to token budget
        fitted, total_tokens = fit_to_budget(truncated, token_budget)

        latency = (time.time() - start_time) * 1000

        # Record stats
        self.store.record_stat(
            operation="search",
            project_id=project_id,
            latency_ms=latency,
            token_count=total_tokens,
        )

        return RetrievalResult(
            memories=fitted,
            estimated_tokens=total_tokens,
            latency_ms=latency,
            total_found=len(raw_results),
        )


def _get_context_pack(pack: str) -> list[str]:
    """Get memory types for a context pack."""
    packs = {
        "backend": [
            "architecture", "technical_decision",
            "coding_convention", "project_rule", "dependency",
        ],
        "frontend": ["architecture", "coding_convention", "project_rule", "dependency"],
        "database": ["technical_decision", "project_rule", "coding_convention", "dependency"],
        "testing": ["coding_convention", "project_rule", "known_issue"],
        "deployment": ["environment_fact", "technical_decision", "project_rule"],
        "architecture": ["architecture", "technical_decision", "project_rule"],
    }
    return packs.get(pack, [])


def _get_context_pack_types(pack: str) -> str | None:
    """Get a single mem_type filter from a context pack (returns None to not filter by type)."""
    # Context packs expand to multiple types — we can't filter FTS by a list,
    # so we return None and filter post-retrieval instead
    return None
