"""Stale context and contradiction detection."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any


def detect_stale_memories(
    memories: list[dict[str, Any]], current_facts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Detect memories that may be stale based on current evidence.

    Compares stored memories against freshly observed facts.
    Returns list of stale memory findings.
    """
    findings = []

    # Build a map of current fact keywords
    current_keywords = set()
    for fact in current_facts:
        content = fact.get("content", "").lower()
        current_keywords.update(content.split())

    for mem in memories:
        content = mem.get("content", "").lower()
        mem_type = mem.get("type", "")

        # Only check factual memories
        if mem_type not in ("dependency", "architecture", "environment_fact", "project_rule"):
            continue

        # Check if memory mentions something that conflicts with current state
        # Look for specific patterns
        conflicts = _check_conflicts(mem, current_facts)
        if conflicts:
            findings.append({
                "memory_id": mem.get("id"),
                "memory_content": mem.get("content"),
                "memory_type": mem_type,
                "status": "CONFLICT",
                "evidence": conflicts,
            })
            continue

        # Check age
        updated = mem.get("updated_at", "")
        if updated:
            try:
                dt = datetime.fromisoformat(updated.replace("Z", "+00:00"))
                age = datetime.now(timezone.utc) - dt
                if age > timedelta(days=30):
                    findings.append({
                        "memory_id": mem.get("id"),
                        "memory_content": mem.get("content"),
                        "memory_type": mem_type,
                        "status": "POTENTIALLY_STALE",
                        "evidence": f"Last updated {age.days} days ago",
                    })
            except (ValueError, TypeError):
                pass

    return findings


def _check_conflicts(memory: dict[str, Any], current_facts: list[dict[str, Any]]) -> str | None:
    """Check if a memory conflicts with current facts."""
    mem_content = memory.get("content", "").lower()

    # Extract database type from memory
    db_match = re.search(r"(postgresql|mysql|sqlite|mongodb|redis|dynamo)", mem_content)
    if db_match:
        mem_db = db_match.group(1)
        for fact in current_facts:
            fact_content = fact.get("content", "").lower()
            fact_dbs = re.findall(r"(postgresql|mysql|sqlite|mongodb|redis|dynamo)", fact_content)
            for fdb in fact_dbs:
                if fdb != mem_db:
                    return f"Memory says {mem_db}, current evidence suggests {fdb}"

    # Extract framework
    fw_match = re.search(r"(framework:\s*(\w+))", mem_content)
    if fw_match:
        mem_fw = fw_match.group(2)
        for fact in current_facts:
            fact_content = fact.get("content", "").lower()
            fw_facts = re.findall(r"framework:\s*(\w+)", fact_content)
            for fwf in fw_facts:
                if fwf != mem_fw:
                    return f"Memory says {mem_fw}, current evidence suggests {fwf}"

    return None


def detect_contradictions(memories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect contradictory rules in stored memories."""
    findings = []

    # Group by type
    rules = [m for m in memories if m.get("type") in ("project_rule", "coding_convention")]

    for i, rule_a in enumerate(rules):
        for rule_b in rules[i + 1:]:
            if _is_contradiction(rule_a.get("content", ""), rule_b.get("content", "")):
                findings.append({
                    "rule_a": {
                        "id": rule_a.get("id"),
                        "content": rule_a.get("content"),
                        "source": rule_a.get("source"),
                    },
                    "rule_b": {
                        "id": rule_b.get("id"),
                        "content": rule_b.get("content"),
                        "source": rule_b.get("source"),
                    },
                    "status": "CONTRADICTION_DETECTED",
                })

    return findings


def _is_contradiction(a: str, b: str) -> bool:
    """Heuristic check if two rules contradict each other."""
    a_lower = a.lower()
    b_lower = b.lower()

    # Check for direct negation patterns
    negation_pairs = [
        ("must", "must not"),
        ("should", "should not"),
        ("always", "never"),
        ("required", "forbidden"),
        ("directly", "not directly"),
        ("can", "cannot"),
        ("may", "may not"),
    ]

    for pos, neg in negation_pairs:
        if pos in a_lower and neg in b_lower:
            # Check if they're talking about the same thing
            a_words = set(a_lower.split())
            b_words = set(b_lower.split())
            overlap = a_words & b_words
            # Remove the negation words from overlap check
            meaningful_overlap = overlap - {pos, neg, "not", "the", "a", "an", "is", "are"}
            if len(meaningful_overlap) >= 2:
                return True
        if neg in a_lower and pos in b_lower:
            a_words = set(a_lower.split())
            b_words = set(b_lower.split())
            overlap = a_words & b_words
            meaningful_overlap = overlap - {pos, neg, "not", "the", "a", "an", "is", "are"}
            if len(meaningful_overlap) >= 2:
                return True

    return False
