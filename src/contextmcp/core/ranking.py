"""Relevance ranking for memory retrieval."""

from __future__ import annotations

import math
from datetime import datetime, timezone


def rank_memory(memory: dict, query: str, fts_rank: float = 0.0) -> float:
    """Compute a relevance score for a memory.

    Factors:
    - FTS relevance (if available)
    - Confidence (how trustworthy the source is)
    - Importance (user/system assigned)
    - Recency (newer is better, with decay)
    - Scope priority (project > global > session)
    """
    score = 0.0

    # FTS relevance (BM25 score — lower is better in SQLite, negate)
    if fts_rank and fts_rank != 0:
        score += max(0, -fts_rank) * 10

    # Confidence
    confidence = memory.get("confidence", 0.5)
    score += confidence * 20

    # Importance
    importance = memory.get("importance", 0.5)
    score += importance * 15

    # Recency with decay
    updated = memory.get("updated_at", "")
    if updated:
        try:
            dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age_days = (now - dt).days
            # Exponential decay: half-life of 90 days
            recency = math.exp(-age_days / 90.0)
            score += recency * 10
        except (ValueError, TypeError):
            pass

    # Scope priority
    scope = memory.get("scope", "project")
    scope_weights = {
        "project": 5,
        "global": 3,
        "environment": 4,
        "git": 3,
        "session": 2,
    }
    score += scope_weights.get(scope, 1)

    # Source type bonus
    source_type = memory.get("source_type", "observed")
    source_weights = {
        "user": 10,
        "observed": 5,
        "inferred": 2,
        "ai": 1,
    }
    score += source_weights.get(source_type, 1)

    return score


def rank_memories(memories: list[dict], query: str) -> list[dict]:
    """Rank and sort memories by relevance."""
    for mem in memories:
        fts_rank = mem.pop("_rank", 0.0) if "_rank" in mem else mem.get("rank", 0.0)
        mem["_score"] = rank_memory(mem, query, fts_rank)
    memories.sort(key=lambda m: m.get("_score", 0), reverse=True)
    return memories


def deduplicate(memories: list[dict], similarity_threshold: float = 0.7) -> list[dict]:
    """Remove near-duplicate memories based on content similarity."""
    if not memories:
        return []

    result = []
    seen_content: list[str] = []

    for mem in memories:
        content = mem.get("content", "").lower().strip()
        is_dup = False
        for existing in seen_content:
            if _content_similarity(content, existing) >= similarity_threshold:
                is_dup = True
                break
        if not is_dup:
            result.append(mem)
            seen_content.append(content)

    return result


def _content_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two strings."""
    set_a = set(a.split())
    set_b = set(b.split())
    if not set_a or not set_b:
        return 0.0
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)
