"""Token estimation and budget enforcement."""

from __future__ import annotations

from typing import Any

from contextmcp.config.settings import get_settings


def estimate_tokens(text: str) -> int:
    """Estimate token count for a string.

    Uses a simple heuristic: ~4 characters per token.
    This is labeled as 'estimated_tokens' — never claimed as exact.
    """
    if not text:
        return 0
    settings = get_settings()
    return max(1, len(text) // settings.token_estimate_chars_per_token)


def estimate_memory_tokens(memory: dict[str, Any]) -> int:
    """Estimate tokens for a memory dict (content + metadata)."""
    parts = [
        memory.get("content", ""),
        memory.get("source", "") or "",
        memory.get("type", "") or "",
        ", ".join(memory.get("tags", []) or []),
    ]
    return estimate_tokens(" ".join(parts))


def fit_to_budget(
    memories: list[dict[str, Any]], token_budget: int,
) -> tuple[list[dict[str, Any]], int]:
    """Fit memories into a token budget.

    Returns (selected_memories, total_estimated_tokens).
    Memories should already be ranked/sorted.
    """
    if token_budget <= 0:
        return [], 0

    selected: list[dict[str, Any]] = []
    total = 0

    for mem in memories:
        mem_tokens = estimate_memory_tokens(mem)
        if total + mem_tokens > token_budget:
            # Try to include at least one memory
            if not selected:
                selected.append(mem)
                total = mem_tokens
            break
        selected.append(mem)
        total += mem_tokens

    return selected, total


def format_memory_compact(memory: dict[str, Any]) -> str:
    """Format a memory in a compact, token-efficient representation."""
    parts = []
    mem_type = memory.get("type", "")
    content = memory.get("content", "")
    source = memory.get("source", "")
    confidence = memory.get("confidence", 0)

    if mem_type:
        parts.append(f"[{mem_type}]")
    parts.append(content)
    if source:
        parts.append(f"(source: {source})")
    if confidence and confidence < 0.8:
        parts.append(f"(confidence: {confidence:.0%})")

    return " ".join(parts)
