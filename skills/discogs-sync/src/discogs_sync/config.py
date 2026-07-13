"""Credential and configuration persistence."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from .exceptions import ConfigError

DEFAULT_CONFIG_DIR = Path.home() / ".discogs-sync"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.json"


def get_config_path() -> Path:
    return DEFAULT_CONFIG_FILE


def load_config() -> dict:
    """Load configuration from disk. Returns empty dict if file doesn't exist."""
    path = get_config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise ConfigError(f"Failed to read config file {path}: {e}") from e


def save_config(config: dict) -> None:
    """Save configuration to disk."""
    path = get_config_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        # Restrict permissions to owner-only on non-Windows platforms
        if sys.platform != "win32":
            path.chmod(0o600)
    except OSError as e:
        raise ConfigError(f"Failed to write config file {path}: {e}") from e


def get_cache_ttl() -> int:
    """Return the cache TTL in seconds.

    Reads ``cache_ttl_hours`` from the config file. If not set, defaults to
    24 hours (86400 seconds). The value may be a float (e.g. 0.5 for 30 minutes).
    """
    config = load_config()
    hours = config.get("cache_ttl_hours", 24)
    try:
        return int(float(hours) * 3600)
    except (TypeError, ValueError):
        return 86400


def get_auth_mode() -> str:
    """Return the configured auth mode ('token' or 'oauth'). Defaults to 'token'."""
    config = load_config()
    return config.get("auth_mode", "oauth" if config.get("access_token") else "token")


def get_tokens() -> dict | None:
    """Return stored credentials, or None if not configured.

    Supports both personal access token and OAuth modes.
    Legacy configs (no auth_mode key) are treated as OAuth.
    """
    config = load_config()
    auth_mode = config.get("auth_mode")

    # Token mode
    if auth_mode == "token":
        user_token = config.get("user_token")
        if user_token:
            return {
                "auth_mode": "token",
                "user_token": user_token,
                "username": config.get("username"),
            }
        return None

    # OAuth mode (explicit or legacy config without auth_mode)
    token = config.get("access_token")
    secret = config.get("access_token_secret")
    if token and secret:
        return {
            "auth_mode": "oauth",
            "access_token": token,
            "access_token_secret": secret,
            "consumer_key": config.get("consumer_key", ""),
            "consumer_secret": config.get("consumer_secret", ""),
            "username": config.get("username"),
        }
    return None


def save_tokens(
    consumer_key: str,
    consumer_secret: str,
    access_token: str,
    access_token_secret: str,
    username: str | None = None,
) -> None:
    """Store OAuth tokens to config file."""
    config = load_config()
    config.update(
        {
            "auth_mode": "oauth",
            "consumer_key": consumer_key,
            "consumer_secret": consumer_secret,
            "access_token": access_token,
            "access_token_secret": access_token_secret,
            "username": username,
        }
    )
    save_config(config)


def save_user_token(user_token: str, username: str | None = None) -> None:
    """Store a personal access token to config file."""
    config = load_config()
    config.update(
        {
            "auth_mode": "token",
            "user_token": user_token,
            "username": username,
        }
    )
    save_config(config)


def clear_tokens() -> None:
    """Remove all stored credentials (both token and OAuth)."""
    config = load_config()
    for key in [
        "auth_mode", "user_token",
        "access_token", "access_token_secret",
        "consumer_key", "consumer_secret",
        "username",
    ]:
        config.pop(key, None)
    save_config(config)
