"""Secret detection and redaction."""

from __future__ import annotations

import re

# Known secret variable name patterns
SECRET_VAR_PATTERNS = [
    re.compile(r"(?i)(password|passwd|pwd|secret|token|api[_-]?key|auth[_-]?key|"
               r"private[_-]?key|access[_-]?key|client[_-]?secret|"
               r"connection[_-]?string|db[_-]?url|database[_-]?url|"
               r"redis[_-]?url|mongo[_-]?url|aws[_-]?secret|"
               r"stripe[_-]?key|openai[_-]?key|anthropic[_-]?key|"
               r"github[_-]?token|gitlab[_-]?token|hf[_-]?token|"
               r"jwt[_-]?secret|session[_-]?secret|encryption[_-]?key)"),
]

# Secret value patterns
SECRET_VALUE_PATTERNS = [
    # API keys (common formats)
    re.compile(r"(?:sk|pk|rk)_[a-zA-Z0-9]{20,}"),  # Stripe-like
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),  # OpenAI-like
    re.compile(r"gh[pousr]_[A-Za-z0-9]{36}"),  # GitHub tokens
    re.compile(r"glpat-[A-Za-z0-9_-]{20}"),  # GitLab tokens
    re.compile(r"hf_[A-Za-z0-9]{30,}"),  # HuggingFace tokens
    # AWS
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access key
    re.compile(r"aws_secret_access_key\s*=\s*[A-Za-z0-9/+=]{40}"),
    # Private keys
    re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    # JWT
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
    # Generic long hex/base64 secrets (40+ chars, high entropy)
    re.compile(r"[a-f0-9]{40,}"),  # SHA-like
    re.compile(r"[A-Za-z0-9+/]{44}={0,2}"),  # base64 32 bytes
]

# Database URLs with credentials
DB_URL_PATTERN = re.compile(
    r"(?P<scheme>\w+://)(?P<user>[^:]+):(?P<pass>[^@]+)@(?P<rest>.+)"
)


def redact_value(name: str, value: str) -> str:
    """Redact a secret value, returning 'configured' or 'redacted'."""
    if not value:
        return value
    # Check if the variable name looks like a secret
    for pattern in SECRET_VAR_PATTERNS:
        if pattern.search(name):
            return "redacted"
    # Check if the value matches secret patterns
    for pattern in SECRET_VALUE_PATTERNS:
        if pattern.search(value):
            return "redacted"
    # Check for database URLs with embedded credentials
    if DB_URL_PATTERN.search(value):
        return "redacted"
    return value


def redact_env_vars(env_vars: dict[str, str]) -> dict[str, str]:
    """Redact secrets from an environment variables dict."""
    result = {}
    for key, value in env_vars.items():
        redacted = redact_value(key, value)
        if redacted == "redacted":
            result[key] = "configured"
        else:
            result[key] = value
    return result


def redact_text(text: str) -> str:
    """Redact secrets found in arbitrary text."""
    result = text
    for pattern in SECRET_VALUE_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    # Redact credentials in URLs
    result = DB_URL_PATTERN.sub(
        lambda m: f"{m.group('scheme')}{m.group('user')}:***@{m.group('rest')}",
        result,
    )
    return result


def is_likely_secret(name: str, value: str) -> bool:
    """Check if a name=value pair is likely a secret."""
    if redact_value(name, value) != value:
        return True
    return False
