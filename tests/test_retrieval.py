"""Test retrieval and token budgeting."""

from __future__ import annotations

from pathlib import Path

from contextmcp.core.memory import MemoryManager
from contextmcp.core.retrieval import Retriever
from contextmcp.core.token_budget import estimate_tokens, fit_to_budget
from contextmcp.storage.manager import StorageManager


def _setup(tmp_data_dir: Path) -> tuple[MemoryManager, Retriever, StorageManager, str]:
    sm = StorageManager()
    store = sm.get_store()
    store.upsert_project("test_proj", "test", "/tmp/test")
    mm = MemoryManager(store)
    rv = Retriever(store)
    return mm, rv, sm, "test_proj"


def test_search_basic(tmp_data_dir: Path):
    mm, rv, sm, pid = _setup(tmp_data_dir)

    mm.save(
        content="Use repository pattern for database access",
        scope="project",
        mem_type="project_rule",
        project_id=pid,
        source="user",
    )
    mm.save(
        content="All API routes use /v1 prefix",
        scope="project",
        mem_type="project_rule",
        project_id=pid,
        source="user",
    )

    result = rv.search("repository pattern", project_id=pid)
    assert len(result.memories) >= 1
    assert "repository" in result.memories[0]["content"].lower()
    sm.close()


def test_search_token_budget(tmp_data_dir: Path):
    mm, rv, sm, pid = _setup(tmp_data_dir)

    for i in range(10):
        mm.save(
            content=f"Rule number {i}: do something specific with database and API",
            scope="project",
            mem_type="project_rule",
            project_id=pid,
        )

    result = rv.search("database", project_id=pid, token_budget=100)
    assert result.estimated_tokens <= 200  # Should be within budget (with some margin)
    sm.close()


def test_search_empty_query(tmp_data_dir: Path):
    mm, rv, sm, pid = _setup(tmp_data_dir)
    result = rv.search("", project_id=pid)
    assert len(result.memories) == 0
    sm.close()


def test_search_scope_filter(tmp_data_dir: Path):
    mm, rv, sm, pid = _setup(tmp_data_dir)

    mm.save(
        content="Project rule about testing",
        scope="project",
        mem_type="project_rule",
        project_id=pid,
    )
    mm.save(
        content="Global preference for type hints",
        scope="global",
        mem_type="developer_preference",
        project_id=None,
    )

    # Search project scope only
    result = rv.search("testing", project_id=pid, scope="project")
    scopes = {m["scope"] for m in result.memories}
    assert "global" not in scopes
    sm.close()


def test_estimate_tokens():
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello") == 1
    assert estimate_tokens("hello world this is a test") == 6


def test_fit_to_budget():
    memories = [
        {"content": "a" * 100, "source": "", "type": "", "tags": []},
        {"content": "b" * 100, "source": "", "type": "", "tags": []},
        {"content": "c" * 100, "source": "", "type": "", "tags": []},
    ]
    selected, total = fit_to_budget(memories, token_budget=30)
    assert len(selected) <= 3
    assert total <= 30 + 25  # First item might exceed budget slightly


def test_cross_project_isolation(tmp_data_dir: Path):
    sm = StorageManager()
    store = sm.get_store()
    store.upsert_project("proj_a", "A", "/tmp/a")
    store.upsert_project("proj_b", "B", "/tmp/b")

    mm = MemoryManager(store)
    rv = Retriever(store)

    mm.save(
        content="Project A architecture rule", scope="project",
        mem_type="project_rule", project_id="proj_a",
    )
    mm.save(
        content="Project B architecture rule", scope="project",
        mem_type="project_rule", project_id="proj_b",
    )

    result_a = rv.search("architecture", project_id="proj_a")
    for m in result_a.memories:
        assert m["project_id"] == "proj_a"

    result_b = rv.search("architecture", project_id="proj_b")
    for m in result_b.memories:
        assert m["project_id"] == "proj_b"

    sm.close()
