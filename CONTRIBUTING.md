# Contributing to ContextMCP

## Contribution Workflow

This project uses a **protected branch** workflow. No one can push directly to `main`.

### How to Contribute

1. **Fork** the repository
2. **Clone** your fork:
   ```bash
   git clone https://github.com/<your-username>/MCP_Package.git
   cd MCP_Package
   ```
3. **Create a feature branch** (never work on `main`):
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** and write tests
5. **Run tests locally**:
   ```bash
   pip install -e ".[dev]"
   pytest
   ruff check src/ tests/
   ```
6. **Commit** your changes:
   ```bash
   git add .
   git commit -m "feat: description of your change"
   ```
7. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Open a Pull Request** to `main` in the original repository

### Review Process

- All PRs require **review and approval** from the maintainer (DIP-RO) before merging
- No direct pushes to `main` — enforced by branch protection rules
- CI checks (lint, test, build) must pass before merge
- Only the maintainer can merge PRs after approval

### Branch Protection Rules

The `main` branch is protected with:
- **No direct pushes** — all changes via PR only
- **Pull request reviews required** — at least 1 approval needed
- **Status checks required** — CI must pass (lint, test, build)
- **No force pushes** — history is preserved
- **No branch deletion** — `main` cannot be deleted

### Commit Convention

Use conventional commits:
- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `refactor:` — code refactoring
- `test:` — adding tests
- `chore:` — maintenance tasks

### Security

If you find a security issue, please see `SECURITY.md` — do not open a public issue.

## Development Setup

```bash
git clone https://github.com/<your-username>/MCP_Package.git
cd MCP_Package
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest                    # all tests
pytest -v                 # verbose
pytest --cov=contextmcp   # with coverage
```

## Running Benchmarks

```bash
python -m benchmarks.run
```

## Code Style

- Python 3.10+
- `ruff` for linting: `ruff check src/ tests/`
- `mypy` for type checking: `mypy src/contextmcp/`
- Line length: 100 characters

## Architecture

See `docs/architecture.md` for the full architecture overview.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
