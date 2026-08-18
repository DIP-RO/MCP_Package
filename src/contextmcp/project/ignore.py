"""Ignore pattern matching for file indexing."""

from __future__ import annotations

import fnmatch
from pathlib import Path

from contextmcp.config.settings import get_settings


class IgnoreMatcher:
    """Matches files against ignore patterns and .gitignore."""

    def __init__(self, project_root: Path, extra_patterns: list[str] | None = None):
        self.root = project_root
        settings = get_settings()
        self.patterns = list(settings.ignore_patterns)
        if extra_patterns:
            self.patterns.extend(extra_patterns)
        self._gitignore_patterns = self._load_gitignore()

    def _load_gitignore(self) -> list[str]:
        """Load .gitignore patterns if available."""
        gitignore = self.root / ".gitignore"
        if not gitignore.exists():
            return []
        try:
            patterns = []
            for line in gitignore.read_text(errors="replace").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
            return patterns
        except OSError:
            return []

    def is_ignored(self, path: Path) -> bool:
        """Check if a path should be ignored."""
        try:
            rel = path.resolve().relative_to(self.root.resolve())
        except ValueError:
            return True

        rel_str = str(rel).replace("\\", "/")
        parts = rel.parts

        # Check against default patterns
        for pattern in self.patterns:
            # Check each path component
            for part in parts:
                if fnmatch.fnmatch(part, pattern):
                    return True
            # Also check full relative path
            if fnmatch.fnmatch(rel_str, pattern):
                return True

        # Check against .gitignore patterns
        for pattern in self._gitignore_patterns:
            if fnmatch.fnmatch(rel_str, pattern):
                return True
            # Directory patterns like "dir/"
            if pattern.endswith("/") and fnmatch.fnmatch(rel_str + "/", pattern):
                return True
            # Check each component
            for part in parts:
                if fnmatch.fnmatch(part, pattern.rstrip("/")):
                    return True

        return False

    def should_index(self, path: Path) -> bool:
        """Check if a file should be indexed (not ignored, not binary, reasonable size)."""
        from contextmcp.config.settings import get_settings
        from contextmcp.security.validation import is_binary_file, safe_file_size

        if self.is_ignored(path):
            return False

        if not path.is_file():
            return False

        size = safe_file_size(path)
        settings = get_settings()
        if size > settings.max_file_size:
            return False

        if is_binary_file(path):
            return False

        return True
