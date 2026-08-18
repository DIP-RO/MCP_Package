"""Test stale context and contradiction detection."""

from __future__ import annotations

from contextmcp.core.context import detect_stale_memories, detect_contradictions


def test_detect_contradictions():
    memories = [
        {"id": "1", "type": "project_rule", "content": "Routers must directly access database"},
        {"id": "2", "type": "project_rule", "content": "Routers must not directly access database"},
    ]
    contradictions = detect_contradictions(memories)
    assert len(contradictions) >= 1
    assert contradictions[0]["status"] == "CONTRADICTION_DETECTED"


def test_no_contradictions():
    memories = [
        {"id": "1", "type": "project_rule", "content": "Use repository pattern"},
        {"id": "2", "type": "project_rule", "content": "Use pytest for testing"},
    ]
    contradictions = detect_contradictions(memories)
    assert len(contradictions) == 0


def test_detect_stale_database_conflict():
    memories = [
        {
            "id": "1",
            "type": "dependency",
            "content": "Database: PostgreSQL",
            "updated_at": "2025-01-01T00:00:00+00:00",
        },
    ]
    current_facts = [
        {"content": "Database: MySQL detected in requirements"},
    ]
    findings = detect_stale_memories(memories, current_facts)
    assert len(findings) >= 1
    assert findings[0]["status"] == "CONFLICT"
