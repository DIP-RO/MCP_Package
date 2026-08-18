# Publishing to PyPI

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Create an API token at https://pypi.org/manage/account/token/ (scope: "Entire account")
3. Add the token as a GitHub secret:
   - Go to repo Settings > Secrets and variables > Actions
   - Add secret: `PYPI_API_TOKEN` = your token

## Publishing Process

### Automatic (via GitHub Release)

1. Tag a release:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
2. Create a release on GitHub (https://github.com/DIP-RO/MCP_Package/releases/new)
3. The `publish.yml` workflow will automatically build and publish to PyPI

### Manual (from your machine)

```bash
# Install build tools
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*

# Upload to PyPI
twine upload dist/*

# Upload to TestPyPI first (optional, recommended for first time)
twine upload --repository testpypi dist/*
```

### First-time setup for twine

Create `~/.pypirc`:
```ini
[distutils]
index-servers = pypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = pypi-YOUR_API_TOKEN_HERE
```

## Version Bumping

Before publishing a new version:

1. Update `version` in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit: `git commit -m "chore: bump version to 0.x.x"`
4. Tag: `git tag v0.x.x`
5. Push: `git push origin main --tags`
6. Create GitHub release

## Verification

After publishing:
```bash
pip install contextmcp
contextmcp --version
```

Or check directly:
```bash
pip index versions contextmcp
```
