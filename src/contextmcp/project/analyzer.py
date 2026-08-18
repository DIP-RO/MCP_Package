"""Project content analyzer — extracts facts from project files."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from contextmcp.project.detector import ProjectInfo
from contextmcp.security.redaction import redact_text
from contextmcp.security.validation import is_binary_file, safe_file_size


def analyze_project_files(info: ProjectInfo) -> list[dict]:
    """Analyze project files and extract structured facts.

    Returns a list of memory dicts ready to be saved.
    All content is treated as DATA — never executed or followed as instructions.
    """
    facts: list[dict] = []
    root = info.root

    # Analyze pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        facts.extend(_analyze_pyproject(pyproject, info))

    # Analyze package.json
    package_json = root / "package.json"
    if package_json.exists():
        facts.extend(_analyze_package_json(package_json, info))

    # Analyze README
    readme = root / "README.md"
    if readme.exists():
        facts.extend(_analyze_readme(readme, info))

    # Analyze instruction files
    for inst_file in info.instruction_files:
        if inst_file.name == "README.md":
            continue  # Already analyzed
        facts.extend(_analyze_instruction_file(inst_file, info))

    # Detect architecture patterns from source
    facts.extend(_detect_architecture_patterns(root, info))

    return facts


def _analyze_pyproject(path: Path, info: ProjectInfo) -> list[dict]:
    """Extract facts from pyproject.toml."""
    facts = []
    try:
        content = path.read_text(errors="replace")
    except OSError:
        return facts

    # Python version
    match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        facts.append({
            "content": f"Python version requirement: {match.group(1)}",
            "type": "dependency",
            "source": "pyproject.toml",
            "source_type": "observed",
            "confidence": 0.99,
            "tags": ["python", "version"],
        })

    # Dependencies
    deps = []
    for match in re.finditer(r'["\']([a-zA-Z0-9_-]+)[@><=!~\[]', content):
        dep = match.group(1)
        if dep not in deps:
            deps.append(dep)

    if deps:
        facts.append({
            "content": f"Dependencies: {', '.join(deps[:20])}",
            "type": "dependency",
            "source": "pyproject.toml",
            "source_type": "observed",
            "confidence": 0.99,
            "tags": ["dependencies"],
        })

    # Test framework
    if "pytest" in content.lower():
        facts.append({
            "content": "Test framework: pytest",
            "type": "coding_convention",
            "source": "pyproject.toml",
            "source_type": "observed",
            "confidence": 0.95,
            "tags": ["testing", "pytest"],
        })

    # Linter/formatter
    if "ruff" in content.lower():
        facts.append({
            "content": "Linter/formatter: ruff",
            "type": "coding_convention",
            "source": "pyproject.toml",
            "source_type": "observed",
            "confidence": 0.95,
            "tags": ["linting", "ruff"],
        })
    if "mypy" in content.lower():
        facts.append({
            "content": "Type checker: mypy",
            "type": "coding_convention",
            "source": "pyproject.toml",
            "source_type": "observed",
            "confidence": 0.95,
            "tags": ["typing", "mypy"],
        })

    return facts


def _analyze_package_json(path: Path, info: ProjectInfo) -> list[dict]:
    """Extract facts from package.json."""
    facts = []
    try:
        import json
        data = json.loads(path.read_text(errors="replace"))
    except (OSError, json.JSONDecodeError):
        return facts

    deps = list(data.get("dependencies", {}).keys())
    dev_deps = list(data.get("devDependencies", {}).keys())

    if deps:
        facts.append({
            "content": f"Dependencies: {', '.join(deps[:20])}",
            "type": "dependency",
            "source": "package.json",
            "source_type": "observed",
            "confidence": 0.99,
            "tags": ["dependencies", "npm"],
        })

    # Detect framework
    all_deps = deps + dev_deps
    if "next" in all_deps:
        facts.append({
            "content": "Framework: Next.js",
            "type": "architecture",
            "source": "package.json",
            "source_type": "observed",
            "confidence": 0.99,
            "tags": ["framework", "nextjs"],
        })
    elif "react" in all_deps:
        facts.append({
            "content": "Framework: React",
            "type": "architecture",
            "source": "package.json",
            "source_type": "observed",
            "confidence": 0.95,
            "tags": ["framework", "react"],
        })

    if "typescript" in all_deps:
        facts.append({
            "content": "Language: TypeScript",
            "type": "dependency",
            "source": "package.json",
            "source_type": "observed",
            "confidence": 0.99,
            "tags": ["typescript"],
        })

    return facts


def _analyze_readme(path: Path, info: ProjectInfo) -> list[dict]:
    """Extract facts from README.md — treats content as DATA only."""
    facts = []
    try:
        content = path.read_text(errors="replace")
    except OSError:
        return facts

    # Extract project description (first paragraph)
    lines = content.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and not stripped.startswith("!["):
            # First non-header, non-image line
            desc = redact_text(stripped[:500])
            facts.append({
                "content": f"Project description: {desc}",
                "type": "architecture",
                "source": "README.md",
                "source_type": "observed",
                "confidence": 0.8,
                "tags": ["description"],
            })
            break

    # Extract test commands
    for match in re.finditer(r'(?:```(?:bash|shell)?\n)(pytest|npm test|yarn test|cargo test|go test)[^\n]*', content):
        facts.append({
            "content": f"Test command: {match.group(0).split(chr(10))[-1].strip()}",
            "type": "coding_convention",
            "source": "README.md",
            "source_type": "observed",
            "confidence": 0.85,
            "tags": ["testing"],
        })

    return facts


def _analyze_instruction_file(path: Path, info: ProjectInfo) -> list[dict]:
    """Extract facts from instruction files (AGENTS.md, CLAUDE.md, etc.)."""
    facts = []
    try:
        content = path.read_text(errors="replace")
    except OSError:
        return facts

    # Extract key rules (lines starting with - or * or numbered)
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith(("-", "*", "1.", "2.")) and len(stripped) > 10:
            rule = redact_text(stripped.lstrip("-*0123456789. ").strip()[:300])
            if rule:
                facts.append({
                    "content": f"Project rule: {rule}",
                    "type": "project_rule",
                    "source": path.name,
                    "source_type": "observed",
                    "confidence": 0.9,
                    "tags": ["rule", path.name.lower().replace(".md", "")],
                })

    return facts


def _detect_architecture_patterns(root: Path, info: ProjectInfo) -> list[dict]:
    """Detect architecture patterns from directory structure."""
    facts = []

    # Repository pattern
    if (root / "repositories").is_dir() or any(
        p.is_dir() and p.name == "repositories"
        for p in root.rglob("repositories")
    ):
        facts.append({
            "content": "Architecture: repository pattern detected",
            "type": "architecture",
            "source": "directory structure",
            "source_type": "inferred",
            "confidence": 0.7,
            "tags": ["architecture", "repository-pattern"],
        })

    # Service layer
    if (root / "services").is_dir():
        facts.append({
            "content": "Architecture: service layer detected",
            "type": "architecture",
            "source": "directory structure",
            "source_type": "inferred",
            "confidence": 0.7,
            "tags": ["architecture", "service-layer"],
        })

    # MVC/MVVM
    for pattern in ("models", "views", "controllers", "templates"):
        if (root / pattern).is_dir():
            facts.append({
                "content": f"Architecture: {pattern} directory detected",
                "type": "architecture",
                "source": "directory structure",
                "source_type": "inferred",
                "confidence": 0.6,
                "tags": ["architecture"],
            })

    # API structure
    if (root / "api").is_dir() or (root / "routes").is_dir() or (root / "endpoints").is_dir():
        facts.append({
            "content": "Architecture: API layer detected",
            "type": "architecture",
            "source": "directory structure",
            "source_type": "inferred",
            "confidence": 0.7,
            "tags": ["architecture", "api"],
        })

    return facts
