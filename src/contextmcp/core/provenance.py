"""Provenance tracking for memories."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def create_provenance(
    source: str,
    source_type: str = "observed",
    confidence: float = 0.5,
) -> dict[str, Any]:
    """Create a provenance record for a memory."""
    return {
        "source": source,
        "source_type": source_type,
        "confidence": confidence,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def format_provenance(memory: dict[str, Any]) -> str:
    """Format provenance for display."""
    source = memory.get("source", "unknown")
    source_type = memory.get("source_type", "observed")
    confidence = memory.get("confidence", 0)

    return f"source={source} type={source_type} confidence={confidence:.0%}"


def merge_provenance(
    existing: dict[str, Any], new_source: str, new_confidence: float,
) -> dict[str, Any]:
    """Merge a new source into existing provenance, boosting confidence."""
    sources = existing.get("sources", [])
    if new_source not in sources:
        sources.append(new_source)

    # Confidence increases with multiple sources
    base_conf = existing.get("confidence", 0.5)
    merged_conf = min(1.0, base_conf + new_confidence * 0.1)

    return {
        "sources": sources,
        "confidence": merged_conf,
        "source_type": existing.get("source_type", "observed"),
    }
