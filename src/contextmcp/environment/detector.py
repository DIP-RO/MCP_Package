"""Environment detection."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any


class EnvironmentInfo:
    """Detected environment information."""

    def __init__(self):
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.python_path = sys.executable
        self.virtual_env = self._detect_virtualenv()
        self.venv_type = self._detect_venv_type()
        self.installed_packages = self._get_installed_packages()
        self.env_vars = self._get_safe_env_vars()
        self.env_files = self._detect_env_files()
        self.docker = self._detect_docker()
        self.platform = sys.platform

    def _detect_virtualenv(self) -> str | None:
        """Detect if running in a virtual environment."""
        venv = os.environ.get("VIRTUAL_ENV")
        if venv:
            return venv
        # Check if python path suggests a venv
        exe = Path(sys.executable)
        if exe.parent.name in ("Scripts", "bin") and exe.parent.parent.name in (".venv", "venv", "env"):
            return str(exe.parent.parent)
        return None

    def _detect_venv_type(self) -> str | None:
        """Detect the type of virtual environment."""
        if not self._detect_virtualenv():
            return None
        venv_path = Path(self._detect_virtualenv())
        if (venv_path / "pyvenv.cfg").exists():
            try:
                cfg = (venv_path / "pyvenv.cfg").read_text(errors="replace")
                if "uv" in cfg.lower():
                    return "uv"
                if "poetry" in cfg.lower():
                    return "poetry"
                return "venv"
            except OSError:
                return "venv"
        if (venv_path / ".conda").exists():
            return "conda"
        return "venv"

    def _get_installed_packages(self) -> list[str]:
        """Get list of installed packages."""
        try:
            import importlib.metadata
            return sorted(
                f"{dist.metadata['Name']}=={dist.version}"
                for dist in importlib.metadata.distributions()
            )
        except Exception:
            return []

    def _get_safe_env_vars(self) -> dict[str, str]:
        """Get environment variables with secrets redacted."""
        from contextmcp.security.redaction import redact_env_vars
        return redact_env_vars(dict(os.environ))

    def _detect_env_files(self) -> list[str]:
        """Detect .env files in the current directory."""
        env_files = []
        cwd = Path.cwd()
        for name in [".env", ".env.local", ".env.example", ".env.test", ".env.production"]:
            p = cwd / name
            if p.exists() and p.is_file():
                env_files.append(name)
        return env_files

    def _detect_docker(self) -> dict | None:
        """Detect Docker configuration."""
        cwd = Path.cwd()
        docker = {}
        if (cwd / "Dockerfile").exists():
            docker["dockerfile"] = True
        if (cwd / "docker-compose.yml").exists() or (cwd / "docker-compose.yaml").exists():
            docker["compose"] = True
        return docker if docker else None

    def to_dict(self) -> dict:
        return {
            "python_version": self.python_version,
            "python_path": self.python_path,
            "virtual_env": self.virtual_env,
            "venv_type": self.venv_type,
            "platform": self.platform,
            "env_files": self.env_files,
            "docker": self.docker,
            "package_count": len(self.installed_packages),
        }

    def to_detailed_dict(self) -> dict:
        d = self.to_dict()
        d["installed_packages"] = self.installed_packages
        d["env_vars"] = self.env_vars
        return d
