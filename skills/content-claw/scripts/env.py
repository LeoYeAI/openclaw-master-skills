"""Scoped .env loader for Content Claw. Only loads declared keys."""

import os
from pathlib import Path

ALLOWED_KEYS = {"FAL_KEY", "EXA_API_KEY"}


def load_env(extra_keys: set[str] | None = None):
    """Load only allowed keys from .env into process environment."""
    allowed = ALLOWED_KEYS | (extra_keys or set())
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key in allowed:
            os.environ.setdefault(key, value.strip())
