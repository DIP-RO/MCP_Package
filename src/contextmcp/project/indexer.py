"""Incremental file indexer."""

from __future__ import annotations

import time
from pathlib import Path

from contextmcp.project.detector import ProjectInfo
from contextmcp.project.identity import compute_file_hash
from contextmcp.project.ignore import IgnoreMatcher
from contextmcp.storage.sqlite import SQLiteStore


class Indexer:
    """Incremental file indexer using file hashes and mtime."""

    def __init__(self, store: SQLiteStore, project_id: str, project_root: Path):
        self.store = store
        self.project_id = project_id
        self.root = project_root
        self.ignore = IgnoreMatcher(project_root)

    def index_incremental(self) -> dict:
        """Index only changed files. Returns stats dict."""
        start = time.time()
        indexed = 0
        skipped = 0
        removed = 0

        # Get currently indexed files
        existing = {f["file_path"]: f for f in self.store.get_indexed_files(self.project_id)}

        # Walk the project
        seen_paths = set()
        for path in self._walk():
            rel = str(path.relative_to(self.root))
            seen_paths.add(rel)

            try:
                stat = path.stat()
            except (OSError, PermissionError):
                continue

            old = existing.get(rel)
            # Check if file changed (mtime + size)
            if old and old.get("mtime") == stat.st_mtime and old.get("size") == stat.st_size:
                skipped += 1
                continue

            # Compute hash for changed files
            file_hash = compute_file_hash(path)
            self.store.upsert_file(
                project_id=self.project_id,
                file_path=rel,
                file_hash=file_hash,
                mtime=stat.st_mtime,
                size=stat.st_size,
            )
            indexed += 1

        # Remove files that no longer exist
        for rel in set(existing.keys()) - seen_paths:
            self.store.delete_file(self.project_id, rel)
            removed += 1

        elapsed = time.time() - start
        return {
            "indexed": indexed,
            "skipped": skipped,
            "removed": removed,
            "total": len(seen_paths),
            "elapsed_ms": round(elapsed * 1000, 2),
        }

    def _walk(self) -> list[Path]:
        """Walk the project directory, respecting ignore patterns."""
        from contextmcp.config.settings import get_settings
        settings = get_settings()
        results = []
        count = 0

        for path in self.root.rglob("*"):
            if count >= settings.max_indexed_files:
                break
            if not path.is_file():
                continue
            if self.ignore.should_index(path):
                results.append(path)
                count += 1

        return results

    def get_stats(self) -> dict:
        """Get indexing statistics."""
        files = self.store.get_indexed_files(self.project_id)
        total_size = sum(f.get("size", 0) or 0 for f in files)
        return {
            "file_count": len(files),
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }
