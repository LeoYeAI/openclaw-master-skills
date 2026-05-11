"""Palaia configuration management."""

from __future__ import annotations

import json
import os
from pathlib import Path

# Standard VPS installation path — checked as fallback when Path.home() differs.
# Mockable in tests via monkeypatch on palaia.config.VPS_OPENCLAW_BASE.
VPS_OPENCLAW_BASE = Path("/home/claw/.openclaw")

DEFAULT_CONFIG = {
    "version": 1,
    "decay_lambda": 0.1,
    "hot_threshold_days": 7,
    "warm_threshold_days": 30,
    "hot_max_entries": 50,
    "hot_min_score": 0.5,
    "warm_min_score": 0.1,
    "default_scope": "team",
    "wal_retention_days": 7,
    "lock_timeout_seconds": 5,
    "embedding_provider": "auto",
    "embedding_model": "",
    "store_version": "",  # Set to palaia __version__ on init/upgrade
    # Bounded memory (Issue #71)
    "max_entries_per_tier": None,  # None = unlimited
    "max_total_chars": None,  # None = unlimited
    "gc_type_weights": {"process": 2.0, "task": 1.5, "memory": 1.0},
}


def find_palaia_root(start: str = ".") -> Path | None:
    """Walk up from start to find .palaia directory.

    Search order:
    1. PALAIA_HOME env var (explicit override)
    2. Walk up from start directory (cwd-based)
    3. ~/.palaia (user home fallback)
    4. ~/.openclaw/workspace/.palaia (OpenClaw standard path)
    """
    # 1. Check PALAIA_HOME env var first
    env_home = os.environ.get("PALAIA_HOME")
    if env_home:
        env_path = Path(env_home)
        # PALAIA_HOME points directly to a .palaia directory
        if env_path.is_dir() and env_path.name == ".palaia":
            return env_path
        # PALAIA_HOME points to parent dir containing .palaia
        candidate = env_path / ".palaia"
        if candidate.is_dir():
            return candidate

    # 2. Walk up from start directory
    current = Path(start).resolve()
    while True:
        candidate = current / ".palaia"
        if candidate.is_dir():
            return candidate
        if current.parent == current:
            break
        current = current.parent

    # 3. ~/.palaia fallback
    home_palaia = Path.home() / ".palaia"
    if home_palaia.is_dir():
        return home_palaia

    # 4. ~/.openclaw/workspace/.palaia fallback (OpenClaw standard path)
    openclaw_palaia = Path.home() / ".openclaw" / "workspace" / ".palaia"
    if openclaw_palaia.is_dir():
        return openclaw_palaia

    # 5. VPS standard path fallback (#51)
    vps_palaia = VPS_OPENCLAW_BASE / "workspace" / ".palaia"
    if vps_palaia != openclaw_palaia and vps_palaia.is_dir():
        return vps_palaia

    return None


def get_root(start: str = ".") -> Path:
    """Get .palaia root or raise."""
    root = find_palaia_root(start)
    if root is None:
        raise FileNotFoundError("No .palaia directory found. Run 'palaia init' first.")
    return root


def load_config(palaia_root: Path) -> dict:
    """Load config from .palaia/config.json, merged with defaults."""
    config_path = palaia_root / "config.json"
    config = dict(DEFAULT_CONFIG)
    if config_path.exists():
        with open(config_path, "r") as f:
            user_config = json.load(f)
        config.update(user_config)
    return config


def save_config(palaia_root: Path, config: dict) -> None:
    """Save config to .palaia/config.json."""
    config_path = palaia_root / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def is_initialized(palaia_root: Path | None = None) -> bool:
    """Check if Palaia has been initialized.

    Returns True if .palaia/config.json exists (agent field is optional).
    """
    if palaia_root is None:
        palaia_root = find_palaia_root()
    if palaia_root is None:
        return False
    config_path = palaia_root / "config.json"
    if not config_path.exists():
        return False
    try:
        json.loads(config_path.read_text())
        return True
    except (json.JSONDecodeError, OSError):
        return False


def get_agent(palaia_root: Path | None = None) -> str | None:
    """Get the configured agent name from .palaia/config.json."""
    if palaia_root is None:
        palaia_root = find_palaia_root()
    if palaia_root is None:
        return None
    config = load_config(palaia_root)
    return config.get("agent") or None


def get_instance(palaia_root: Path | None = None) -> str | None:
    """Get the current session instance from .palaia/current-instance.

    Instance is session-local and set via `palaia instance set`.
    Falls back to PALAIA_INSTANCE env var.
    """
    if palaia_root is None:
        palaia_root = find_palaia_root()
    if palaia_root is None:
        return os.environ.get("PALAIA_INSTANCE") or None
    instance_file = palaia_root / "current-instance"
    if instance_file.exists():
        try:
            value = instance_file.read_text().strip()
            if value:
                return value
        except OSError:
            pass
    return os.environ.get("PALAIA_INSTANCE") or None


def set_instance(palaia_root: Path, instance_name: str) -> None:
    """Set the current session instance in .palaia/current-instance."""
    instance_file = palaia_root / "current-instance"
    instance_file.write_text(instance_name.strip())


def clear_instance(palaia_root: Path) -> None:
    """Clear the current session instance."""
    instance_file = palaia_root / "current-instance"
    if instance_file.exists():
        instance_file.unlink()


# --- Agent Alias System ---


def get_aliases(palaia_root: Path) -> dict[str, str]:
    """Get all agent aliases from config. Returns {from_name: to_name} mapping."""
    config = load_config(palaia_root)
    return dict(config.get("aliases", {}))


def set_alias(palaia_root: Path, from_name: str, to_name: str) -> None:
    """Set an agent alias: from_name is an alias for to_name."""
    if not from_name or not to_name:
        raise ValueError("Both alias source and target names are required.")
    if from_name == to_name:
        raise ValueError("Alias source and target cannot be the same.")
    config = load_config(palaia_root)
    aliases = config.get("aliases", {})
    aliases[from_name] = to_name
    config["aliases"] = aliases
    save_config(palaia_root, config)


def remove_alias(palaia_root: Path, from_name: str) -> bool:
    """Remove an agent alias. Returns True if alias existed."""
    config = load_config(palaia_root)
    aliases = config.get("aliases", {})
    if from_name not in aliases:
        return False
    del aliases[from_name]
    config["aliases"] = aliases
    save_config(palaia_root, config)
    return True


def resolve_agent(palaia_root: Path | None = None, require: bool = False) -> str | None:
    """Resolve the current agent identity.

    Resolution chain:
    1. PALAIA_AGENT environment variable (set per-agent in multi-agent setups)
    2. config.json agent field (static, set during init)
    3. None (no agent identity)

    Args:
        palaia_root: Path to .palaia directory. Auto-detected if None.
        require: If True, raise ValueError when no agent can be resolved.

    Returns:
        Agent name or None.
    """
    # 1. Environment variable (highest priority)
    env_agent = os.environ.get("PALAIA_AGENT", "").strip()
    if env_agent:
        return env_agent

    # 2. Config file
    if palaia_root is None:
        palaia_root = find_palaia_root()
    if palaia_root is not None:
        config = load_config(palaia_root)
        config_agent = config.get("agent")
        if config_agent:
            return config_agent

    if require:
        raise ValueError("Cannot resolve agent identity. Set PALAIA_AGENT env var or run 'palaia init --agent NAME'.")
    return None


def resolve_agent_with_aliases(agent: str, aliases: dict[str, str]) -> set[str]:
    """Resolve an agent name to a set of all names that should match.

    Given aliases like {"default": "HAL"}, querying for "HAL" should also match
    entries with agent="default", and querying for "default" should also match
    entries with agent="HAL".

    Returns a set of agent names to match against.
    """
    names = {agent}
    # Forward: if agent is a key in aliases, add the target
    if agent in aliases:
        names.add(aliases[agent])
    # Reverse: if agent is a value in aliases, add the source(s)
    for src, tgt in aliases.items():
        if tgt == agent:
            names.add(src)
    return names
