# Environment Intelligence

## Detection

ContextMCP automatically detects:

- Python version and path
- Virtual environment (venv, uv, poetry, conda)
- Installed packages
- Environment variables (secrets redacted)
- `.env` files (`.env`, `.env.local`, `.env.example`, `.env.test`, `.env.production`)
- Docker configuration (Dockerfile, docker-compose.yml)

## .env Diagnostics

- Detects missing variables (`.env.example` expects `REDIS_URL` but `.env` doesn't have it)
- Detects extra variables
- Never exposes secret values — shows `configured` or `missing`

## Secret Redaction

Patterns detected:
- API keys (OpenAI `sk-...`, Stripe `sk_...`, GitHub `ghp_...`)
- AWS credentials (`AKIA...`)
- Private keys (`-----BEGIN ... PRIVATE KEY-----`)
- JWT tokens
- Database URLs with embedded credentials
- Known secret variable names (`PASSWORD`, `SECRET_KEY`, `API_KEY`, etc.)

**Limitation:** Secret detection is heuristic. It cannot guarantee 100% coverage.

## Diagnostics Command

```bash
contextmcp doctor
```

Checks:
- Storage accessibility
- Database health
- Project detection
- Git status
- Environment health
- Client support
