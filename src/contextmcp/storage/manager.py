"""Storage manager — automatic path resolution and DB lifecycle."""

from __future__ import annotations

from pathlib import Path

from contextmcp.config.settings import Settings, get_settings
from contextmcp.storage.sqlite import SQLiteStore, get_connection


class StorageManager:
    """Manages local storage directory and database connections."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()
        self._store: SQLiteStore | None = None

    @property
    def data_dir(self) -> Path:
        return self.settings.ensure_data_dir()

    @property
    def db_path(self) -> Path:
        return self.settings.db_path

    def get_store(self) -> SQLiteStore:
        """Get or create the SQLite store (lazy)."""
        if self._store is None:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            conn = get_connection(self.db_path)
            self._store = SQLiteStore(conn)
        return self._store

    def close(self) -> None:
        if self._store is not None:
            self._store.close()
            self._store = None

    def reset(self) -> None:
        """Delete the entire database file."""
        self.close()
        if self.db_path.exists():
            self.db_path.unlink()
        # Also remove WAL and SHM files
        for suffix in ("-wal", "-shm"):
            p = Path(str(self.db_path) + suffix)
            if p.exists():
                p.unlink()
