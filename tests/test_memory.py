"""Test memory operations."""

from __future__ import annotations

from pathlib import Path

from contextmcp.core.memory import MemoryManager, MemoryError
from contextmcp.storage.manager import StorageManager


def _get_memory_manager(tmp_data_dir: Path) -> tuple[MemoryManager, StorageManager]:
    sm = StorageManager()
    store = sm.get_store()
    store.upsert_project("test_proj", "test", "/tmp/test")
    return MemoryManager(store), sm


def test_save_and_get_memory(tmp_data_dir: Path):
    mm, sm = _get_memory_manager(tmp_data_dir)

    mem = mm.save(
        content="Use repository pattern",
        scope="project",
        mem_type="project_rule",
        project_id="test_proj",
        source="user",
        confidence=0.9,
    )
    assert mem is not None
    assert mem["content"] == "Use repository pattern"

    retrieved = mm.get(mem["id"])
    assert retrieved is not None
    assert retrieved["content"] == "Use repository pattern"

    sm.close()


def test_save_invalid_scope(tmp_data_dir: Path):
    mm, sm = _get_memory_manager(tmp_data_dir)
    try:
        mm.save(content="test", scope="invalid", mem_type="project_rule", project_id="test_proj")
        assert False, "Should have raised"
    except MemoryError:
        pass
    sm.close()


def test_save_invalid_type(tmp_data_dir: Path):
    mm, sm = _get_memory_manager(tmp_data_dir)
    try:
        mm.save(content="test", scope="project", mem_type="invalid", project_id="test_proj")
        assert False, "Should have raised"
    except MemoryError:
        pass
    sm.close()


def test_save_global_memory_no_project(tmp_data_dir: Path):
    mm, sm = _get_memory_manager(tmp_data_dir)
    mem = mm.save(
        content="Prefer type hints",
        scope="global",
        mem_type="developer_preference",
        project_id=None,
    )
    assert mem is not None
    assert mem["scope"] == "global"
    sm.close()


def test_save_non_global_requires_project(tmp_data_dir: Path):
    mm, sm = _get_memory_manager(tmp_data_dir)
    try:
        mm.save(content="test", scope="project", mem_type="project_rule", project_id=None)
        assert False, "Should have raised"
    except MemoryError:
        pass
    sm.close()


def test_update_memory(tmp_data_dir: Path):
    mm, sm = _get_memory_manager(tmp_data_dir)
    mem = mm.save(
        content="Original",
        scope="project",
        mem_type="project_rule",
        project_id="test_proj",
    )
    updated = mm.update(mem["id"], content="Updated", confidence=0.95)
    assert updated is not None
    assert updated["content"] == "Updated"
    assert updated["confidence"] == 0.95
    sm.close()


def test_delete_memory(tmp_data_dir: Path):
    mm, sm = _get_memory_manager(tmp_data_dir)
    mem = mm.save(
        content="To delete",
        scope="project",
        mem_type="project_rule",
        project_id="test_proj",
    )
    assert mm.delete(mem["id"])
    assert mm.get(mem["id"]) is None
    sm.close()


def test_save_decision(tmp_data_dir: Path):
    mm, sm = _get_memory_manager(tmp_data_dir)
    mem = mm.save_decision(
        decision="Use repository pattern",
        reason="Keep persistence logic outside API layer",
        affected=["app/repositories/", "app/services/"],
        project_id="test_proj",
    )
    assert mem is not None
    assert "repository pattern" in mem["content"].lower()
    assert mem["type"] == "technical_decision"
    sm.close()


def test_memory_deduplication(tmp_data_dir: Path):
    mm, sm = _get_memory_manager(tmp_data_dir)

    mem1 = mm.save(
        content="Framework: FastAPI",
        scope="project",
        mem_type="architecture",
        project_id="test_proj",
        deduplicate=False,
    )

    # Save similar content — should update, not create new
    mem2 = mm.save(
        content="Framework: FastAPI",
        scope="project",
        mem_type="architecture",
        project_id="test_proj",
        deduplicate=True,
    )

    assert mem2["id"] == mem1["id"]
    sm.close()
