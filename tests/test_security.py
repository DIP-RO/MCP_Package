"""Test security: redaction, isolation, validation."""

from __future__ import annotations

from pathlib import Path

from contextmcp.security.redaction import (
    redact_value,
    redact_env_vars,
    redact_text,
    is_likely_secret,
)
from contextmcp.security.validation import (
    safe_resolve_path,
    is_safe_filename,
    validate_memory_type,
    validate_scope,
    sanitize_query,
    is_binary_file,
)
from contextmcp.security.isolation import (
    assert_project_scope,
    filter_project_memories,
    ProjectIsolationError,
)


def test_redact_secret_value():
    assert redact_value("OPENAI_API_KEY", "sk-abc123def456ghi789jkl012mno345") == "redacted"
    assert redact_value("DATABASE_URL", "postgresql://user:pass@localhost/db") == "redacted"
    assert redact_value("SECRET_KEY", "my-secret-key") == "redacted"


def test_redact_non_secret_value():
    assert redact_value("APP_NAME", "myapp") == "myapp"
    assert redact_value("PORT", "8080") == "8080"


def test_redact_env_vars():
    env = {
        "OPENAI_API_KEY": "sk-abc123def456ghi789jkl012mno345",
        "APP_NAME": "myapp",
        "DATABASE_URL": "postgresql://user:pass@localhost/db",
        "PORT": "8080",
    }
    redacted = redact_env_vars(env)
    assert redacted["OPENAI_API_KEY"] == "configured"
    assert redacted["DATABASE_URL"] == "configured"
    assert redacted["APP_NAME"] == "myapp"
    assert redacted["PORT"] == "8080"


def test_redact_text():
    text = "My key is sk-abc123def456ghi789jkl012mno345pqr678"
    redacted = redact_text(text)
    assert "sk-abc123" not in redacted
    assert "[REDACTED]" in redacted


def test_is_likely_secret():
    assert is_likely_secret("OPENAI_API_KEY", "sk-abc123def456ghi789jkl012mno345")
    assert is_likely_secret("DATABASE_URL", "postgresql://user:pass@localhost/db")
    assert not is_likely_secret("APP_NAME", "myapp")


def test_safe_resolve_path(tmp_path: Path):
    base = tmp_path / "project"
    base.mkdir()

    # Normal path
    p = safe_resolve_path("src/main.py", base)
    assert str(base) in str(p)

    # Path traversal should fail
    try:
        safe_resolve_path("../../etc/passwd", base)
        assert False, "Should have raised"
    except ValueError:
        pass


def test_is_safe_filename():
    assert is_safe_filename("hello.py")
    assert not is_safe_filename("../hello.py")
    assert not is_safe_filename("..")
    assert not is_safe_filename("a/b.py")


def test_validate_memory_type():
    assert validate_memory_type("project_rule")
    assert validate_memory_type("architecture")
    assert not validate_memory_type("invalid_type")


def test_validate_scope():
    assert validate_scope("global")
    assert validate_scope("project")
    assert not validate_scope("invalid")


def test_sanitize_query():
    assert sanitize_query("hello world") == "hello world"
    assert sanitize_query("") == ""
    assert sanitize_query("a\x00b") == "ab"


def test_is_binary_file(tmp_path: Path):
    binary = tmp_path / "binary.dat"
    binary.write_bytes(b"\x00\x01\x02\x03")
    assert is_binary_file(binary)

    text = tmp_path / "text.py"
    text.write_text("print('hello')")
    assert not is_binary_file(text)


def test_project_isolation_filter():
    memories = [
        {"project_id": "proj_a", "scope": "project", "content": "A"},
        {"project_id": "proj_b", "scope": "project", "content": "B"},
        {"project_id": None, "scope": "global", "content": "Global"},
    ]

    filtered = filter_project_memories(memories, "proj_a")
    pids = {m["project_id"] for m in filtered}
    assert "proj_b" not in pids
    assert None in pids  # Global is allowed


def test_project_isolation_assert():
    mem = {"project_id": "proj_a", "scope": "project"}
    assert_project_scope(mem, "proj_a")  # Should not raise

    try:
        assert_project_scope(mem, "proj_b")
        assert False, "Should have raised"
    except ProjectIsolationError:
        pass

    # Global scope should pass for any project
    global_mem = {"project_id": None, "scope": "global"}
    assert_project_scope(global_mem, "proj_a")
