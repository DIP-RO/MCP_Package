"""Test Git intelligence."""

from __future__ import annotations

from pathlib import Path

from contextmcp.git.analyzer import GitAnalyzer


def test_git_analyzer_no_git(tmp_path: Path):
    analyzer = GitAnalyzer(None)
    assert analyzer.get_recent_commits() == []
    assert analyzer.get_current_branch() is None


def test_git_analyzer_with_repo(tmp_git_project: Path):
    analyzer = GitAnalyzer(tmp_git_project)
    commits = analyzer.get_recent_commits(5)
    assert len(commits) >= 1
    assert "Initial commit" in commits[0]["message"]

    branch = analyzer.get_current_branch()
    assert branch is not None


def test_git_find_todos(tmp_git_project: Path):
    # Add a file with TODO
    (tmp_git_project / "todo.py").write_text("# TODO: fix this\nprint('hello')\n")

    import subprocess
    subprocess.run(["git", "add", "."], cwd=str(tmp_git_project), capture_output=True)
    subprocess.run(["git", "commit", "-m", "Add todo"], cwd=str(tmp_git_project), capture_output=True)

    analyzer = GitAnalyzer(tmp_git_project)
    todos = analyzer.find_todos_fixmes()
    assert any("TODO" in t["text"] for t in todos)
