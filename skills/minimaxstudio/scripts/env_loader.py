"""
Load environment variables from .env file.

Searches for .env in the following order:
1. MiniMaxStudio project root (parent of scripts/) — primary location
2. Current working directory — fallback

Only sets variables that are not already defined in the environment.
No external dependencies required.
"""

import os
import pathlib


def load_dotenv():
    """Load .env file into os.environ. Existing env vars take precedence."""
    env_paths = [
        pathlib.Path(__file__).resolve().parent.parent / ".env",
        pathlib.Path.cwd() / ".env",
    ]

    for env_path in env_paths:
        if env_path.is_file():
            _parse_env_file(env_path)
            return str(env_path)
    return None


def _parse_env_file(path):
    """Parse a .env file and set variables not already in os.environ."""
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Remove surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            # Only set if not already in environment
            if key not in os.environ:
                os.environ[key] = value
