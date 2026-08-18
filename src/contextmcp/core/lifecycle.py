"""Lazy initialization lifecycle for ContextMCP."""

from __future__ import annotations

from pathlib import Path

from contextmcp.core.memory import MemoryManager
from contextmcp.core.retrieval import Retriever
from contextmcp.project.detector import ProjectInfo, detect_project
from contextmcp.project.identity import compute_fingerprint
from contextmcp.storage.manager import StorageManager
from contextmcp.storage.sqlite import SQLiteStore


class ContextEngine:
    """Central context engine — lazily initialized on first use."""

    def __init__(self, start_dir: Path | None = None):
        self.start_dir = start_dir or Path.cwd()
        self._initialized = False
        self._project_info: ProjectInfo | None = None
        self._project_id: str | None = None
        self._storage: StorageManager | None = None
        self._memory: MemoryManager | None = None
        self._retriever: Retriever | None = None

    def ensure_initialized(self) -> None:
        """Lazily initialize all components."""
        if self._initialized:
            return

        # Detect project
        self._project_info = detect_project(self.start_dir)
        self._project_id = compute_fingerprint(self._project_info)

        # Initialize storage — PROJECT-LOCAL (.contextmcp/ inside project root)
        from contextmcp.config.settings import Settings, reset_settings
        reset_settings()
        settings = Settings(data_dir=self._project_info.root / ".contextmcp")
        import contextmcp.config.settings as s
        s._settings = settings

        self._storage = StorageManager()
        store = self._storage.get_store()

        # Register project in DB
        store.upsert_project(
            project_id=self._project_id,
            name=self._project_info.name,
            root_path=str(self._project_info.root),
            git_remote=self._project_info.git_remote,
            git_root=str(self._project_info.git_root) if self._project_info.git_root else None,
            language=self._project_info.language,
            framework=self._project_info.framework,
            package_manager=self._project_info.package_manager,
            python_version=self._project_info.python_version,
            metadata=self._project_info.to_dict(),
        )

        # Initialize managers
        self._memory = MemoryManager(store)
        self._retriever = Retriever(store)

        self._initialized = True

    @property
    def project_info(self) -> ProjectInfo:
        self.ensure_initialized()
        assert self._project_info is not None
        return self._project_info

    @property
    def project_id(self) -> str:
        self.ensure_initialized()
        assert self._project_id is not None
        return self._project_id

    @property
    def storage(self) -> StorageManager:
        self.ensure_initialized()
        assert self._storage is not None
        return self._storage

    @property
    def memory(self) -> MemoryManager:
        self.ensure_initialized()
        assert self._memory is not None
        return self._memory

    @property
    def retriever(self) -> Retriever:
        self.ensure_initialized()
        assert self._retriever is not None
        return self._retriever

    @property
    def store(self) -> SQLiteStore:
        self.ensure_initialized()
        assert self._storage is not None
        return self._storage.get_store()

    def close(self) -> None:
        if self._storage:
            self._storage.close()
        self._initialized = False


# Global singleton
_engine: ContextEngine | None = None


def get_engine(start_dir: Path | None = None) -> ContextEngine:
    """Get or create the global context engine."""
    global _engine
    if _engine is None:
        _engine = ContextEngine(start_dir)
    return _engine


def reset_engine() -> None:
    global _engine
    if _engine:
        _engine.close()
    _engine = None
