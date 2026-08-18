"""Environment diagnostics — health checks."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from contextmcp.environment.detector import EnvironmentInfo
from contextmcp.environment.env_parser import compare_env_files


def run_diagnostics(project_root: Path | None = None) -> dict:
    """Run environment diagnostics and return findings."""
    findings: list[dict] = []
    env = EnvironmentInfo()

    root = project_root or Path.cwd()

    # Check Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    findings.append({
        "check": "python_version",
        "status": "ok",
        "detail": f"Python {env.python_version}",
    })

    # Check virtual environment
    if env.virtual_env:
        findings.append({
            "check": "virtual_env",
            "status": "ok",
            "detail": f"{env.venv_type} at {env.virtual_env}",
        })
    else:
        findings.append({
            "check": "virtual_env",
            "status": "warning",
            "detail": "No virtual environment detected. Using system Python.",
        })

    # Check .env files
    env_path = root / ".env"
    example_path = root / ".env.example"

    if env_path.exists():
        findings.append({
            "check": "env_file",
            "status": "ok",
            "detail": ".env exists",
        })

        if example_path.exists():
            comparison = compare_env_files(env_path, example_path)
            if comparison["missing_from_env"]:
                findings.append({
                    "check": "env_completeness",
                    "status": "warning",
                    "detail": f"Missing from .env: {', '.join(comparison['missing_from_env'])}",
                })
            else:
                findings.append({
                    "check": "env_completeness",
                    "status": "ok",
                    "detail": "All .env.example variables present in .env",
                })
    else:
        if example_path.exists():
            findings.append({
                "check": "env_file",
                "status": "error",
                "detail": ".env.example exists but .env is missing. Copy .env.example to .env.",
            })
        else:
            findings.append({
                "check": "env_file",
                "status": "info",
                "detail": "No .env file found (may not be needed).",
            })

    # Check Docker
    dockerfile = root / "Dockerfile"
    compose = root / "docker-compose.yml"
    if dockerfile.exists():
        findings.append({
            "check": "docker",
            "status": "ok",
            "detail": "Dockerfile found",
        })
    if compose.exists():
        findings.append({
            "check": "docker_compose",
            "status": "ok",
            "detail": "docker-compose.yml found",
        })

    # Check for common issues
    # Missing required env vars (heuristic)
    required_vars = ["DATABASE_URL", "SECRET_KEY", "OPENAI_API_KEY"]
    for var in required_vars:
        if var in os.environ:
            findings.append({
                "check": f"env_var:{var}",
                "status": "ok",
                "detail": f"{var} is set",
            })

    # Summary
    errors = sum(1 for f in findings if f["status"] == "error")
    warnings = sum(1 for f in findings if f["status"] == "warning")

    return {
        "findings": findings,
        "errors": errors,
        "warnings": warnings,
        "healthy": errors == 0,
    }
