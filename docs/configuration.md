# Configuration

ContextMCP works with zero configuration. All settings have sensible defaults.

## Optional Configuration

### Environment Variable

```bash
CONTEXTMCP_DATA_DIR=/custom/path contextmcp status
```

### Configuration Precedence

1. Environment variables (highest)
2. Default values (lowest)

No config file is required for normal operation.

## Available Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `data_dir` | OS-appropriate | Storage directory |
| `db_name` | `contextmcp.db` | SQLite filename |
| `max_file_size` | 1 MB | Skip files larger than this |
| `max_indexed_files` | 5000 | Maximum files to index |
| `token_estimate_chars_per_token` | 4 | Token estimation heuristic |
| `default_search_limit` | 5 | Default search result count |
| `default_token_budget` | 1000 | Default token budget |
| `stale_threshold_days` | 30 | Days before memory is considered stale |
| `enable_git_analysis` | true | Enable Git intelligence |
| `enable_env_analysis` | true | Enable environment intelligence |

## Ignore Patterns

Default ignore patterns include: `.git`, `.venv`, `node_modules`, `__pycache__`, `dist`, `build`, `coverage`, binary files, images, archives, lock files.

`.gitignore` is also respected where appropriate.
