"""SQLite connection and query operations."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from contextmcp.storage.migrations import apply_migrations


def get_connection(db_path: Path) -> sqlite3.Connection:
    """Get a SQLite connection with optimal settings."""
    conn = sqlite3.connect(str(db_path), timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    apply_migrations(conn)
    return conn


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_dumps(value: Any) -> str:
    if value is None:
        return "[]"
    return json.dumps(value)


def _json_loads(value: str | None) -> Any:
    if value is None or value == "":
        return None
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None


class SQLiteStore:
    """Low-level SQLite operations for ContextMCP."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    # --- Projects ---

    def upsert_project(
        self,
        project_id: str,
        name: str,
        root_path: str,
        git_remote: str | None = None,
        git_root: str | None = None,
        language: str | None = None,
        framework: str | None = None,
        package_manager: str | None = None,
        python_version: str | None = None,
        metadata: dict | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO projects (id, name, root_path, git_remote, git_root,
                language, framework, package_manager, python_version, metadata, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                root_path=excluded.root_path,
                git_remote=COALESCE(excluded.git_remote, git_remote),
                git_root=COALESCE(excluded.git_root, git_root),
                language=COALESCE(excluded.language, language),
                framework=COALESCE(excluded.framework, framework),
                package_manager=COALESCE(excluded.package_manager, package_manager),
                python_version=COALESCE(excluded.python_version, python_version),
                metadata=COALESCE(excluded.metadata, metadata),
                updated_at=excluded.updated_at
            """,
            (
                project_id, name, root_path, git_remote, git_root,
                language, framework, package_manager, python_version,
                _json_dumps(metadata) if metadata else None, _now_iso(),
            ),
        )
        self.conn.commit()

    def get_project(self, project_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["metadata"] = _json_loads(d.get("metadata"))
        return d

    def get_all_projects(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["metadata"] = _json_loads(d.get("metadata"))
            result.append(d)
        return result

    def delete_project(self, project_id: str) -> None:
        self.conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()

    # --- Memories ---

    def insert_memory(
        self,
        mem_id: str,
        project_id: str | None,
        scope: str,
        mem_type: str,
        content: str,
        source: str | None = None,
        source_type: str = "observed",
        confidence: float = 0.5,
        importance: float = 0.5,
        tags: list[str] | None = None,
        metadata: dict | None = None,
        expires_at: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO memories (id, project_id, scope, type, content, source,
                source_type, confidence, importance, tags, metadata, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                mem_id, project_id, scope, mem_type, content, source,
                source_type, confidence, importance,
                _json_dumps(tags), _json_dumps(metadata), expires_at,
            ),
        )
        self.conn.commit()

    def update_memory(
        self,
        mem_id: str,
        content: str | None = None,
        confidence: float | None = None,
        importance: float | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> bool:
        sets = []
        params: list[Any] = []
        if content is not None:
            sets.append("content = ?")
            params.append(content)
        if confidence is not None:
            sets.append("confidence = ?")
            params.append(confidence)
        if importance is not None:
            sets.append("importance = ?")
            params.append(importance)
        if tags is not None:
            sets.append("tags = ?")
            params.append(_json_dumps(tags))
        if metadata is not None:
            sets.append("metadata = ?")
            params.append(_json_dumps(metadata))
        if not sets:
            return False
        sets.append("updated_at = ?")
        params.append(_now_iso())
        params.append(mem_id)
        cursor = self.conn.execute(
            f"UPDATE memories SET {', '.join(sets)} WHERE id = ?", params
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def delete_memory(self, mem_id: str) -> bool:
        cursor = self.conn.execute("DELETE FROM memories WHERE id = ?", (mem_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def get_memory(self, mem_id: str) -> dict | None:
        row = self.conn.execute("SELECT * FROM memories WHERE id = ?", (mem_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_memory(row)

    def search_memories_fts(
        self,
        query: str,
        project_id: str | None = None,
        scope: str | None = None,
        mem_type: str | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Full-text search using FTS5."""
        # Build the FTS query — use simple token matching
        fts_query = _build_fts_query(query)
        if not fts_query:
            return []

        sql = """
            SELECT m.*, bm25(memories_fts) as rank
            FROM memories_fts
            JOIN memories m ON m.rowid = memories_fts.rowid
            WHERE memories_fts MATCH ?
        """
        params: list[Any] = [fts_query]

        if project_id is not None:
            sql += " AND m.project_id = ?"
            params.append(project_id)
        if scope is not None:
            sql += " AND m.scope = ?"
            params.append(scope)
        if mem_type is not None:
            sql += " AND m.type = ?"
            params.append(mem_type)

        # Filter out expired memories
        sql += " AND (m.expires_at IS NULL OR m.expires_at > datetime('now'))"

        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)

        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_memory(r) for r in rows]

    def list_memories(
        self,
        project_id: str | None = None,
        scope: str | None = None,
        mem_type: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        sql = "SELECT * FROM memories WHERE 1=1"
        params: list[Any] = []
        if project_id is not None:
            sql += " AND project_id = ?"
            params.append(project_id)
        if scope is not None:
            sql += " AND scope = ?"
            params.append(scope)
        if mem_type is not None:
            sql += " AND type = ?"
            params.append(mem_type)
        sql += " AND (expires_at IS NULL OR expires_at > datetime('now'))"
        sql += " ORDER BY importance DESC, updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_memory(r) for r in rows]

    def count_memories(self, project_id: str | None = None) -> int:
        sql = (
            "SELECT COUNT(*) FROM memories "
            "WHERE (expires_at IS NULL OR expires_at > datetime('now'))"
        )
        params: list[Any] = []
        if project_id is not None:
            sql += " AND project_id = ?"
            params.append(project_id)
        row = self.conn.execute(sql, params).fetchone()
        return row[0] if row else 0

    def find_similar(self, content: str, project_id: str | None, limit: int = 5) -> list[dict]:
        """Find memories with similar content for deduplication."""
        fts_query = _build_fts_query(content)
        if not fts_query:
            return []
        sql = """
            SELECT m.*, bm25(memories_fts) as rank
            FROM memories_fts
            JOIN memories m ON m.rowid = memories_fts.rowid
            WHERE memories_fts MATCH ?
        """
        params: list[Any] = [fts_query]
        if project_id is not None:
            sql += " AND m.project_id = ?"
            params.append(project_id)
        sql += " ORDER BY rank LIMIT ?"
        params.append(limit)
        rows = self.conn.execute(sql, params).fetchall()
        return [self._row_to_memory(r) for r in rows]

    # --- File Index ---

    def upsert_file(
        self,
        project_id: str,
        file_path: str,
        file_hash: str | None = None,
        mtime: float | None = None,
        size: int | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO file_index (project_id, file_path, file_hash, mtime, size, indexed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(project_id, file_path) DO UPDATE SET
                file_hash=excluded.file_hash,
                mtime=excluded.mtime,
                size=excluded.size,
                indexed_at=excluded.indexed_at
            """,
            (project_id, file_path, file_hash, mtime, size, _now_iso()),
        )
        self.conn.commit()

    def get_file(self, project_id: str, file_path: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM file_index WHERE project_id = ? AND file_path = ?",
            (project_id, file_path),
        ).fetchone()
        return dict(row) if row else None

    def get_indexed_files(self, project_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT * FROM file_index WHERE project_id = ?", (project_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def delete_file(self, project_id: str, file_path: str) -> None:
        self.conn.execute(
            "DELETE FROM file_index WHERE project_id = ? AND file_path = ?",
            (project_id, file_path),
        )
        self.conn.commit()

    # --- Sessions ---

    def insert_session(
        self,
        session_id: str,
        project_id: str,
        task: str | None = None,
        completed: list[str] | None = None,
        remaining: list[str] | None = None,
        important_files: list[str] | None = None,
        decisions: list[str] | None = None,
        next_action: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO sessions (id, project_id, task, completed, remaining,
                important_files, decisions, next_action)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id, project_id, task,
                _json_dumps(completed), _json_dumps(remaining),
                _json_dumps(important_files), _json_dumps(decisions),
                next_action,
            ),
        )
        self.conn.commit()

    def get_latest_session(self, project_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM sessions WHERE project_id = ? ORDER BY created_at DESC LIMIT 1",
            (project_id,),
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        for key in ("completed", "remaining", "important_files", "decisions"):
            d[key] = _json_loads(d.get(key))
        return d

    # --- Stats ---

    def record_stat(
        self,
        operation: str,
        project_id: str | None = None,
        latency_ms: float | None = None,
        token_count: int | None = None,
    ) -> None:
        self.conn.execute(
            "INSERT INTO stats (project_id, operation, "
            "latency_ms, token_count) VALUES (?, ?, ?, ?)",
            (project_id, operation, latency_ms, token_count),
        )
        self.conn.commit()

    def get_stats_summary(self, project_id: str | None = None) -> dict:
        sql = (
            "SELECT COUNT(*) as count, AVG(latency_ms) as avg_latency "
            "FROM stats WHERE operation = 'search'"
        )
        params: list[Any] = []
        if project_id is not None:
            sql += " AND project_id = ?"
            params.append(project_id)
        row = self.conn.execute(sql, params).fetchone()
        return {
            "queries": row["count"] if row else 0,
            "avg_latency_ms": round(row["avg_latency"], 2) if row and row["avg_latency"] else 0,
        }

    # --- Utility ---

    def _row_to_memory(self, row: sqlite3.Row) -> dict:
        d = dict(row)
        d["tags"] = _json_loads(d.get("tags")) or []
        d["metadata"] = _json_loads(d.get("metadata")) or {}
        if "rank" in d:
            d["_rank"] = d.pop("rank")
        return d

    def close(self) -> None:
        self.conn.close()

    def execute(self, sql: str, params: list[Any] | None = None) -> sqlite3.Cursor:
        if params:
            return self.conn.execute(sql, params)
        return self.conn.execute(sql)


def _build_fts_query(query: str) -> str:
    """Build a safe FTS5 query from user input."""
    # Escape special FTS5 characters and build OR query
    import re
    tokens = re.findall(r'\w+', query.lower())
    if not tokens:
        return ""
    # Use prefix matching for each token
    escaped = [f'"{t}"*' for t in tokens if len(t) >= 2]
    if not escaped:
        return ""
    return " OR ".join(escaped)
