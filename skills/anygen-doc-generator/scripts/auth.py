"""AnyGen API key resolution and config management."""

import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "anygen"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_API_KEY = "ANYGEN_API_KEY"


def load_config():
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config):
    """Save configuration to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    CONFIG_FILE.chmod(0o600)


def get_api_key(args_api_key=None):
    """Get API key with priority: command line > env var > config file."""
    if args_api_key:
        return args_api_key
    env_key = os.getenv(ENV_API_KEY)
    if env_key:
        return env_key
    config = load_config()
    return config.get("api_key")
