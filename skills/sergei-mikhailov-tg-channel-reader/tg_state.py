"""
tg-reader state tracking — load/save per-channel last_read_id.

Tracks which posts have already been fetched so subsequent runs
return only new (unread) posts. No heavy dependencies (no Pyrogram/Telethon).
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

_DEFAULT_STATE_FILE = str(Path.home() / ".tg-reader-state.json")


def load_tracking_config(config_file=None):
    """Load tracking configuration from config file and env vars.

    Priority: env vars > config file > defaults.
    Env vars: TG_READ_UNREAD ("true"/"1"), TG_STATE_FILE.

    Returns:
        (read_unread: bool, state_file: str)
    """
    read_unread = False
    state_file = _DEFAULT_STATE_FILE

    config_path = Path(config_file) if config_file else Path.home() / ".tg-reader.json"
    if config_path.exists():
        try:
            with open(config_path) as f:
                cfg = json.load(f)
            read_unread = cfg.get("read_unread", False)
            state_file = cfg.get("state_file", state_file)
        except (json.JSONDecodeError, OSError):
            pass

    # Env vars override config file
    env_read_unread = os.environ.get("TG_READ_UNREAD", "").strip().lower()
    if env_read_unread in ("true", "1"):
        read_unread = True
    elif env_read_unread in ("false", "0"):
        read_unread = False

    env_state_file = os.environ.get("TG_STATE_FILE", "").strip()
    if env_state_file:
        state_file = env_state_file

    return read_unread, state_file


def _normalize_channel(channel: str) -> str:
    """Normalize channel name for state key: strip @ and lowercase."""
    return channel.lstrip("@").lower()


def load_state(state_file: str) -> dict:
    """Load state from file. Returns empty state if file doesn't exist or is invalid."""
    path = Path(state_file)
    if not path.exists():
        return {"version": 1, "channels": {}}
    try:
        with open(path) as f:
            data = json.load(f)
        if not isinstance(data, dict) or "channels" not in data:
            return {"version": 1, "channels": {}}
        return data
    except (json.JSONDecodeError, OSError):
        return {"version": 1, "channels": {}}


def get_last_read_id(state: dict, channel: str) -> int:
    """Get last_read_id for a channel. Returns 0 if not tracked yet."""
    key = _normalize_channel(channel)
    ch_data = state.get("channels", {}).get(key, {})
    return ch_data.get("last_read_id", 0)


def update_state(state: dict, channel: str, last_read_id: int) -> dict:
    """Update state with new last_read_id for a channel. Returns the modified state."""
    key = _normalize_channel(channel)
    if "channels" not in state:
        state["channels"] = {}
    state["channels"][key] = {
        "last_read_id": last_read_id,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    return state


def save_state(state: dict, state_file: str) -> None:
    """Save state atomically using write-to-temp + os.replace."""
    path = Path(state_file)
    tmp_path = Path(state_file + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")
    os.replace(str(tmp_path), str(path))
