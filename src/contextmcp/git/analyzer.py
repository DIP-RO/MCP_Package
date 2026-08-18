"""Git intelligence — incremental analysis of recent changes."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from contextmcp.security.redaction import redact_text


class GitAnalyzer:
    """Analyze Git repository for context."""

    def __init__(self, git_root: Path | None = None):
        self.git_root = git_root

    def _run_git(self, args: list[str], timeout: float = 10.0) -> str | None:
        """Run a git command safely."""
        if not self.git_root:
            return None
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=str(self.git_root),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            if result.returncode != 0:
                return None
            return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return None

    def get_recent_commits(self, count: int = 10) -> list[dict[str, Any]]:
        """Get recent commits with messages."""
        output = self._run_git([
            "log", f"-{count}", "--format=%H|%an|%ad|%s", "--date=short"
        ])
        if not output:
            return []
        commits = []
        for line in output.splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "hash": parts[0],
                    "author": parts[1],
                    "date": parts[2],
                    "message": redact_text(parts[3]),
                })
        return commits

    def get_changed_files(self, since: str = "HEAD~10") -> list[str]:
        """Get files changed since a given ref."""
        output = self._run_git(["diff", "--name-only", since])
        if not output:
            # Fallback: try with fewer commits
            output = self._run_git(["diff", "--name-only", "HEAD~1"])
        if not output:
            # Fallback: list all tracked files
            output = self._run_git(["ls-files"])
        if not output:
            return []
        return [f for f in output.splitlines() if f]

    def get_current_branch(self) -> str | None:
        """Get the current branch name."""
        return self._run_git(["rev-parse", "--abbrev-ref", "HEAD"])

    def get_branches(self) -> list[str]:
        """Get all branch names."""
        output = self._run_git(["branch", "--list", "--format=%(refname:short)"])
        if not output:
            return []
        return [b.strip() for b in output.splitlines() if b.strip()]

    def get_frequently_changed_files(self, count: int = 20) -> list[dict[str, Any]]:
        """Get files that are frequently changed."""
        output = self._run_git([
            "log", "--name-only", "--format=", f"-{count * 3}",
        ])
        if not output:
            return []
        from collections import Counter
        files = [f.strip() for f in output.splitlines() if f.strip()]
        counter = Counter(files)
        return [
            {"file": f, "changes": c}
            for f, c in counter.most_common(count)
        ]

    def find_todos_fixmes(self) -> list[dict[str, Any]]:
        """Find TODO/FIXME comments in recently changed files."""
        changed = self.get_changed_files("HEAD~20")
        if not changed:
            # Fallback: scan all tracked files
            all_files = self._run_git(["ls-files"])
            changed = all_files.splitlines() if all_files else []
        results = []
        for filepath in changed[:50]:  # Limit to recent 50 files
            full_path = self.git_root / filepath if self.git_root else Path(filepath)
            if not full_path.exists() or not full_path.is_file():
                continue
            try:
                content = full_path.read_text(errors="replace")
                for i, line in enumerate(content.splitlines(), 1):
                    stripped = line.strip()
                    if "TODO" in stripped or "FIXME" in stripped or "HACK" in stripped:
                        results.append({
                            "file": filepath,
                            "line": i,
                            "text": redact_text(stripped[:200]),
                        })
            except (OSError, UnicodeDecodeError):
                continue
        return results[:50]  # Limit results

    def get_summary(self) -> dict[str, Any]:
        """Get a comprehensive git summary."""
        return {
            "root": str(self.git_root) if self.git_root else None,
            "branch": self.get_current_branch(),
            "branches": self.get_branches()[:10],
            "recent_commits": self.get_recent_commits(10),
            "frequently_changed": self.get_frequently_changed_files(20),
            "todos_fixmes": self.find_todos_fixmes(),
        }
