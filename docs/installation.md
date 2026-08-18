# Installation

## pip

```bash
pip install contextmcp
```

## uv

```bash
uv add contextmcp
```

## pipx (global CLI)

```bash
pipx install contextmcp
```

## From source

```bash
git clone https://github.com/contextmcp/contextmcp.git
cd contextmcp
pip install -e .
```

## Requirements

- Python 3.10+
- No external database
- No cloud services
- No daemon process

## Verification

```bash
contextmcp --version
# contextmcp, version 0.1.0
```

## Virtual Environments

ContextMCP works in any Python environment:

- `venv` / `virtualenv`
- `uv`
- `pipx`
- System Python

No virtual environment is required, but one is recommended.
