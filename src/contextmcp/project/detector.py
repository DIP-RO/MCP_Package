"""Project root and type detection."""

from __future__ import annotations

from pathlib import Path
from typing import Any

# Project root markers (in priority order)
ROOT_MARKERS = [
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "tsconfig.json",
    "Cargo.toml",
    "go.mod",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "Gemfile",
    "composer.json",
    "Pipfile",
    "requirements.txt",
    "Makefile",
    "CMakeLists.txt",
    "docker-compose.yml",
    "docker-compose.yaml",
    "Dockerfile",
    ".git",
]

# Instruction files
INSTRUCTION_FILES = [
    "AGENTS.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "README.md",
    "DEVELOPMENT.md",
    "STYLE.md",
    ".cursorrules",
    ".windsurfrules",
]

# Framework detection patterns
FRAMEWORK_PATTERNS = {
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "Django": ["django"],
    "Starlette": ["starlette"],
    "Tornado": ["tornado"],
    "Pyramid": ["pyramid"],
    "AIOHTTP": ["aiohttp"],
    "Sanic": ["sanic"],
    "Next.js": ["next"],
    "React": ["react"],
    "Vue": ["vue"],
    "Angular": ["@angular/core"],
    "Express": ["express"],
    "NestJS": ["@nestjs/core"],
    "Svelte": ["svelte"],
    "SvelteKit": ["@sveltejs/kit"],
    "Fastify": ["fastify"],
    "Actix": ["actix-web"],
    "Axum": ["axum"],
    "Rocket": ["rocket"],
    "Gin": ["github.com/gin-gonic/gin"],
}

# Package manager detection
PACKAGE_MANAGERS = {
    "uv": ["uv.lock"],
    "poetry": ["poetry.lock"],
    "pipenv": ["Pipfile.lock"],
    "pip": ["requirements.txt", "requirements-dev.txt"],
    "npm": ["package-lock.json"],
    "yarn": ["yarn.lock"],
    "pnpm": ["pnpm-lock.yaml"],
    "bun": ["bun.lockb"],
    "cargo": ["Cargo.lock"],
    "go": ["go.sum"],
    "gem": ["Gemfile.lock"],
    "composer": ["composer.lock"],
}

# Test framework detection
TEST_FRAMEWORKS = {
    "pytest": ["pytest", "_pytest"],
    "unittest": ["unittest"],
    "nose": ["nose"],
    "jest": ["jest"],
    "vitest": ["vitest"],
    "mocha": ["mocha"],
    "playwright": ["playwright"],
    "cypress": ["cypress"],
}


class ProjectInfo:
    """Detected project information."""

    def __init__(
        self,
        root: Path,
        name: str,
        git_root: Path | None = None,
        git_remote: str | None = None,
        language: str | None = None,
        framework: str | None = None,
        package_manager: str | None = None,
        python_version: str | None = None,
        test_framework: str | None = None,
        instruction_files: list[Path] | None = None,
        markers_found: list[str] | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.root = root
        self.name = name
        self.git_root = git_root
        self.git_remote = git_remote
        self.language = language
        self.framework = framework
        self.package_manager = package_manager
        self.python_version = python_version
        self.test_framework = test_framework
        self.instruction_files = instruction_files or []
        self.markers_found = markers_found or []
        self.config = config or {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "name": self.name,
            "git_root": str(self.git_root) if self.git_root else None,
            "git_remote": self.git_remote,
            "language": self.language,
            "framework": self.framework,
            "package_manager": self.package_manager,
            "python_version": self.python_version,
            "test_framework": self.test_framework,
            "instruction_files": [str(f) for f in self.instruction_files],
            "markers_found": self.markers_found,
        }


def find_project_root(start: Path | None = None) -> Path:
    """Find the project root by searching upward for markers."""
    if start is None:
        start = Path.cwd()
    start = start.resolve()

    current = start
    while True:
        for marker in ROOT_MARKERS:
            if (current / marker).exists():
                return current
        # Check if we're at a git root
        if (current / ".git").is_dir():
            return current
        parent = current.parent
        if parent == current:
            # Reached filesystem root — return start
            return start
        current = parent


def detect_git_root(start: Path | None = None) -> Path | None:
    """Find the .git directory by searching upward."""
    if start is None:
        start = Path.cwd()
    start = start.resolve()

    current = start
    while True:
        git_dir = current / ".git"
        if git_dir.exists():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent


def detect_git_remote(git_root: Path) -> str | None:
    """Get the git remote URL if available."""
    git_config = git_root / ".git" / "config"
    if not git_config.exists():
        # Could be a worktree or submodule
        git_config = git_root / ".git"
        if git_config.is_file():
            # Worktree — read gitdir
            try:
                content = git_config.read_text().strip()
                if content.startswith("gitdir:"):
                    real_gitdir = Path(content.split(":", 1)[1].strip())
                    if not real_gitdir.is_absolute():
                        real_gitdir = git_root / real_gitdir
                    git_config = real_gitdir / "config"
            except OSError:
                pass
        else:
            return None

    if not git_config.exists() or not git_config.is_file():
        return None

    try:
        content = git_config.read_text(errors="replace")
        import re
        match = re.search(r'\[remote "origin"\].*?url\s*=\s*(\S+)', content, re.DOTALL)
        if match:
            return match.group(1)
    except OSError:
        pass
    return None


def detect_language(root: Path) -> str | None:
    """Detect the primary language of the project."""
    scores: dict[str, int] = {}

    if (root / "pyproject.toml").exists() or (root / "setup.py").exists():
        scores["python"] = scores.get("python", 0) + 10
    if (root / "requirements.txt").exists():
        scores["python"] = scores.get("python", 0) + 5
    if (root / "package.json").exists():
        scores["javascript"] = scores.get("javascript", 0) + 10
    if (root / "tsconfig.json").exists():
        scores["typescript"] = scores.get("typescript", 0) + 10
    if (root / "Cargo.toml").exists():
        scores["rust"] = scores.get("rust", 0) + 10
    if (root / "go.mod").exists():
        scores["go"] = scores.get("go", 0) + 10
    if (root / "Gemfile").exists():
        scores["ruby"] = scores.get("ruby", 0) + 10
    if (root / "composer.json").exists():
        scores["php"] = scores.get("php", 0) + 10
    if (root / "pom.xml").exists() or (root / "build.gradle").exists():
        scores["java"] = scores.get("java", 0) + 10
    if (root / "CMakeLists.txt").exists():
        scores["c/c++"] = scores.get("c/c++", 0) + 10

    if not scores:
        return None
    return max(scores, key=lambda k: scores[k])


def detect_framework(root: Path) -> str | None:
    """Detect the framework from dependency files."""
    deps = _collect_dependencies(root)
    for framework, patterns in FRAMEWORK_PATTERNS.items():
        for pattern in patterns:
            if any(pattern in d.lower() for d in deps):
                return framework
    return None


def detect_package_manager(root: Path) -> str | None:
    """Detect the package manager from lock files."""
    for pm, files in PACKAGE_MANAGERS.items():
        for f in files:
            if (root / f).exists():
                return pm
    return None


def detect_python_version(root: Path) -> str | None:
    """Detect Python version requirement from pyproject.toml."""
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(errors="replace")
            import re
            # Look for requires-python
            match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
            # Look for python_requires in setup.py section
            match = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        except OSError:
            pass

    setup_py = root / "setup.py"
    if setup_py.exists():
        try:
            content = setup_py.read_text(errors="replace")
            import re
            match = re.search(r'python_requires\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
        except OSError:
            pass

    return None


def detect_test_framework(root: Path) -> str | None:
    """Detect the test framework."""
    deps = _collect_dependencies(root)
    for framework, patterns in TEST_FRAMEWORKS.items():
        for pattern in patterns:
            if any(pattern in d.lower() for d in deps):
                return framework
    # Check for test directories
    if (root / "tests").is_dir() or (root / "test").is_dir():
        return "pytest" if detect_language(root) == "python" else None
    return None


def find_instruction_files(root: Path) -> list[Path]:
    """Find instruction/guidance files in the project root."""
    result = []
    for name in INSTRUCTION_FILES:
        p = root / name
        if p.exists() and p.is_file():
            result.append(p)
    return result


def detect_project(start: Path | None = None) -> ProjectInfo:
    """Full project detection from a starting directory."""
    root = find_project_root(start)
    git_root = detect_git_root(start or root)
    git_remote = detect_git_remote(git_root) if git_root else None
    language = detect_language(root)
    framework = detect_framework(root)
    package_manager = detect_package_manager(root)
    python_version = detect_python_version(root)
    test_framework = detect_test_framework(root)
    instruction_files = find_instruction_files(root)

    # Find markers present
    markers_found = [m for m in ROOT_MARKERS if (root / m).exists()]

    # Project name
    name = root.name
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(errors="replace")
            import re
            match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                name = match.group(1)
        except OSError:
            pass
    package_json = root / "package.json"
    if package_json.exists():
        try:
            import json
            data = json.loads(package_json.read_text(errors="replace"))
            if "name" in data:
                name = data["name"]
        except (OSError, json.JSONDecodeError):
            pass

    return ProjectInfo(
        root=root,
        name=name,
        git_root=git_root,
        git_remote=git_remote,
        language=language,
        framework=framework,
        package_manager=package_manager,
        python_version=python_version,
        test_framework=test_framework,
        instruction_files=instruction_files,
        markers_found=markers_found,
    )


def _collect_dependencies(root: Path) -> list[str]:
    """Collect dependency names from various config files."""
    deps: list[str] = []

    # pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(errors="replace")
            import re
            # Simple extraction of quoted strings in dependencies sections
            for match in re.finditer(r'["\']([^"\']+)[@><=!~\[]', content):
                deps.append(match.group(1).strip().lower())
            # Also catch simple names
            for match in re.finditer(r'["\']([a-zA-Z0-9_-]+)["\']', content):
                deps.append(match.group(1).strip().lower())
        except OSError:
            pass

    # requirements.txt
    reqs = root / "requirements.txt"
    if reqs.exists():
        try:
            for line in reqs.read_text(errors="replace").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    # Extract package name
                    import re
                    m: re.Match[str] | None = re.match(r'([a-zA-Z0-9_-]+)', line)
                    if m:
                        deps.append(m.group(1).lower())
        except OSError:
            pass

    # package.json
    pkg = root / "package.json"
    if pkg.exists():
        try:
            import json
            data = json.loads(pkg.read_text(errors="replace"))
            for section in ("dependencies", "devDependencies"):
                if section in data:
                    deps.extend(k.lower() for k in data[section])
        except (OSError, json.JSONDecodeError):
            pass

    return list(set(deps))
