# Development

## Setup

```bash
git clone https://github.com/contextmcp/contextmcp.git
cd contextmcp
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Tests

```bash
pytest                    # all tests
pytest -v                 # verbose
pytest --cov=contextmcp   # with coverage
pytest tests/test_storage.py  # specific module
```

## Linting

```bash
ruff check src/ tests/
mypy src/contextmcp/
```

## Benchmarks

```bash
python -m benchmarks.run
```

## Build

```bash
python -m build
```

Produces `dist/contextmcp-0.1.0.tar.gz` and `dist/contextmcp-0.1.0-py3-none-any.whl`.

## Project Structure

```
src/contextmcp/
    cli/          # CLI entry point + commands
    mcp/          # MCP server + tools
    core/         # Context engine, memory, retrieval, ranking, token budget
    storage/      # SQLite, migrations, storage manager
    project/      # Detection, identity, analyzer, indexer, ignore
    git/          # Git intelligence
    environment/  # Environment detection, .env parsing, diagnostics
    clients/      # Client adapters (Claude, Cursor, VS Code, etc.)
    security/     # Redaction, isolation, validation
    config/       # Settings
tests/            # Test suite
benchmarks/       # Benchmark scripts
docs/             # Documentation
```
