"""Test storage layer."""

from __future__ import annotations

from pathlib import Path

from contextmcp.storage.manager import StorageManager
from contextmcp.storage.sqlite import SQLiteStore, get_connection


def test_storage_manager_creates_dir(tmp_data_dir: Path):
    sm = StorageManager()
    assert sm.data_dir.exists()
    assert sm.db_path.parent == sm.data_dir


def test_database_initialization(tmp_data_dir: Path):
    sm = StorageManager()
    store = sm.get_store()

    # Tables should exist
    tables = store.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_names = {t[0] for t in tables}
    assert "projects" in table_names
    assert "memories" in table_names
    assert "memories_fts" in table_names
    assert "file_index" in table_names
    assert "sessions" in table_names
    assert "stats" in table_names

    sm.close()


def test_project_upsert_and_get(tmp_data_dir: Path):
    sm = StorageManager()
    store = sm.get_store()

    store.upsert_project(
        project_id="test123",
        name="test-project",
        root_path="/tmp/test",
        language="python",
        framework="FastAPI",
    )

    project = store.get_project("test123")
    assert project is not None
    assert project["name"] == "test-project"
    assert project["language"] == "python"
    assert project["framework"] == "FastAPI"

    sm.close()


def test_memory_insert_and_search(tmp_data_dir: Path):
    sm = StorageManager()
    store = sm.get_store()

    # Create a project first
    store.upsert_project("proj1", "test", "/tmp/test")

    # Insert memory
    store.insert_memory(
        mem_id="mem1",
        project_id="proj1",
        scope="project",
        mem_type="project_rule",
        content="Use repository pattern for database access",
        source="user",
        confidence=0.9,
        importance=0.8,
        tags=["architecture", "database"],
    )

    # Search
    results = store.search_memories_fts("repository pattern", project_id="proj1")
    assert len(results) >= 1
    assert "repository pattern" in results[0]["content"].lower()

    sm.close()


def test_memory_update(tmp_data_dir: Path):
    sm = StorageManager()
    store = sm.get_store()
    store.upsert_project("proj1", "test", "/tmp/test")

    store.insert_memory(
        mem_id="mem1",
        project_id="proj1",
        scope="project",
        mem_type="project_rule",
        content="Original content",
    )

    success = store.update_memory("mem1", content="Updated content", confidence=0.95)
    assert success

    mem = store.get_memory("mem1")
    assert mem["content"] == "Updated content"
    assert mem["confidence"] == 0.95

    sm.close()


def test_memory_delete(tmp_data_dir: Path):
    sm = StorageManager()
    store = sm.get_store()
    store.upsert_project("proj1", "test", "/tmp/test")

    store.insert_memory(
        mem_id="mem1",
        project_id="proj1",
        scope="project",
        mem_type="project_rule",
        content="To be deleted",
    )

    assert store.delete_memory("mem1")
    assert store.get_memory("mem1") is None

    sm.close()


def test_cross_project_isolation(tmp_data_dir: Path):
    sm = StorageManager()
    store = sm.get_store()

    store.upsert_project("proj_a", "Project A", "/tmp/a")
    store.upsert_project("proj_b", "Project B", "/tmp/b")

    store.insert_memory(
        mem_id="mem_a",
        project_id="proj_a",
        scope="project",
        mem_type="project_rule",
        content="Project A specific rule",
    )
    store.insert_memory(
        mem_id="mem_b",
        project_id="proj_b",
        scope="project",
        mem_type="project_rule",
        content="Project B specific rule",
    )

    # Search in project A should not return project B memories
    results_a = store.search_memories_fts("specific rule", project_id="proj_a")
    pids = {r["project_id"] for r in results_a}
    assert "proj_b" not in pids

    sm.close()


def test_reset(tmp_data_dir: Path):
    sm = StorageManager()
    store = sm.get_store()
    store.upsert_project("proj1", "test", "/tmp/test")
    sm.reset()

    assert not sm.db_path.exists()
