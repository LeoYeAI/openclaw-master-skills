"""Configuration loader — reads from emoclaw.yaml or falls back to defaults.

All public names (EMOTION_DIMS, BASELINE_EMOTION, etc.) are derived from
a merged config dict. Consumers import as before:

    from emotion_model import config
    config.EMOTION_DIMS  # works identically
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths (always derived from file location)
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent
REPO_ROOT = PROJECT_ROOT.parent

# ---------------------------------------------------------------------------
# Default configuration
# ---------------------------------------------------------------------------

_DEFAULT_DIMENSIONS: list[dict[str, Any]] = [
    {"name": "valence",      "low": "negative",  "high": "positive",   "baseline": 0.55, "decay_hours": 6.0,  "loss_weight": 1.0},
    {"name": "arousal",      "low": "calm",      "high": "activated",  "baseline": 0.35, "decay_hours": 3.0,  "loss_weight": 0.8},
    {"name": "dominance",    "low": "yielding",  "high": "in-control", "baseline": 0.50, "decay_hours": 8.0,  "loss_weight": 0.6},
    {"name": "safety",       "low": "guarded",   "high": "open",       "baseline": 0.70, "decay_hours": 12.0, "loss_weight": 1.2},
    {"name": "desire",       "low": "neutral",   "high": "wanting",    "baseline": 0.20, "decay_hours": 4.0,  "loss_weight": 1.2},
    {"name": "connection",   "low": "distant",   "high": "intimate",   "baseline": 0.50, "decay_hours": 8.0,  "loss_weight": 1.5},
    {"name": "playfulness",  "low": "serious",   "high": "playful",    "baseline": 0.40, "decay_hours": 3.0,  "loss_weight": 0.8},
    {"name": "curiosity",    "low": "settled",   "high": "fascinated", "baseline": 0.50, "decay_hours": 6.0,  "loss_weight": 0.8},
    {"name": "warmth",       "low": "cool",      "high": "warm",       "baseline": 0.45, "decay_hours": 3.0,  "loss_weight": 0.7},
    {"name": "tension",      "low": "relaxed",   "high": "tense",      "baseline": 0.20, "decay_hours": 2.0,  "loss_weight": 0.7},
    {"name": "groundedness", "low": "floating",  "high": "grounded",   "baseline": 0.60, "decay_hours": 10.0, "loss_weight": 0.8},
]

_DEFAULTS: dict[str, Any] = {
    "name": "my-agent",
    "paths": {
        "state_file": "memory/emotional-state.json",
        "checkpoint_dir": "emotion_model/checkpoints",
        "data_dir": "emotion_model/data",
        "memory_dir": "memory",
        "socket_path": "/tmp/{name}-emotion.sock",
    },
    "dimensions": _DEFAULT_DIMENSIONS,
    "relationships": {
        "known": {"primary": 0, "stranger": 1, "group": 2},
        "embedding_dim": 8,
        "default_sender": "primary",
    },
    "channels": ["chat", "voice", "email"],
    "longing": {
        "enabled": True,
        "growth_rate": 0.02,
        "cap": 0.3,
        "threshold_hours": 2,
        "connection_factor": 0.5,
        "target_dimensions": ["desire"],
        "secondary_dimensions": ["connection"],
    },
    "model": {
        "encoder_model": "all-MiniLM-L6-v2",
        "embed_dim": 384,
        "hidden_dim": 128,
        "head_dim": 64,
        "dropout": 0.1,
        "max_context_chars": 500,
        "device": "cpu",
    },
    "training": {
        "epochs": 100,
        "learning_rate": 1e-3,
        "batch_size": 16,
        "weight_decay": 0.01,
        "grad_clip": 1.0,
        "patience": 15,
        "val_split": 0.2,
    },
    "state": {
        "max_trajectory_points": 50,
        "default_absence_seconds": 8 * 3600,
    },
    "summary": {
        "templates_file": None,
    },
    "timezone_offset_hours": 0,  # UTC (customize in emoclaw.yaml)
    "calibration": {
        "enabled": False,
        "drift_rate": 0.05,
        "min_trajectory_points": 20,
        "clamp_range": 0.15,
    },
    "bootstrap": {
        "source_files": ["SOUL.md", "IDENTITY.md", "MEMORY.md"],
        "memory_patterns": ["memory/20*.md"],
        "redact_patterns": [
            r"(?i)sk-ant-[a-zA-Z0-9_-]{20,}",
            r"(?i)(?:api[_-]?key|token|secret|password|credential)\s*[:=]\s*\S+",
            r"(?i)bearer\s+[a-zA-Z0-9._~+/=-]+",
            r"ghp_[a-zA-Z0-9]{36}",
            r"(?i)ssh-(?:rsa|ed25519)\s+\S+",
        ],
    },
}

# ---------------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------------


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, recursing into nested dicts."""
    merged = dict(base)
    for key, value in override.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _find_config() -> Path | None:
    """Search for emoclaw.yaml in standard locations."""
    # 1. Environment variable
    env_path = os.environ.get("EMOCLAW_CONFIG")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p

    # 2. Repo root
    candidate = REPO_ROOT / "emoclaw.yaml"
    if candidate.exists():
        return candidate

    # 3. Skills directory
    candidate = REPO_ROOT / "skills" / "emoclaw" / "emoclaw.yaml"
    if candidate.exists():
        return candidate

    return None


def _load_config() -> dict[str, Any]:
    """Load config from YAML (if found) merged with defaults."""
    config_path = _find_config()
    if config_path is None:
        return dict(_DEFAULTS)

    try:
        import yaml
        with open(config_path) as f:
            user_config = yaml.safe_load(f) or {}
        return _deep_merge(_DEFAULTS, user_config)
    except ImportError:
        # PyYAML not installed — use defaults
        return dict(_DEFAULTS)
    except Exception:
        # Bad YAML — fall back to defaults
        return dict(_DEFAULTS)


# Load once at import time
_cfg = _load_config()

# ---------------------------------------------------------------------------
# Public API — same names as the original config.py
# ---------------------------------------------------------------------------

# Agent name
AGENT_NAME: str = _cfg["name"]

# Paths (resolved relative to REPO_ROOT)
MEMORY_DIR = REPO_ROOT / _cfg["paths"]["memory_dir"]
STATE_PATH = REPO_ROOT / _cfg["paths"]["state_file"]
CHECKPOINT_DIR = REPO_ROOT / _cfg["paths"]["checkpoint_dir"]
DATA_DIR = REPO_ROOT / _cfg["paths"]["data_dir"]
SOCKET_PATH: str = _cfg["paths"]["socket_path"].format(name=AGENT_NAME)

# Emotion Dimensions
_dims = _cfg["dimensions"]
EMOTION_DIMS: list[str] = [d["name"] for d in _dims]
NUM_EMOTION_DIMS: int = len(EMOTION_DIMS)

DIM_DESCRIPTORS: dict[str, tuple[str, str]] = {
    d["name"]: (d["low"], d["high"]) for d in _dims
}

BASELINE_EMOTION: list[float] = [d["baseline"] for d in _dims]
DECAY_HALF_LIVES: list[float] = [d["decay_hours"] for d in _dims]
DIM_LOSS_WEIGHTS: list[float] = [d["loss_weight"] for d in _dims]

# Relationships
KNOWN_RELATIONSHIPS: dict[str, int] = _cfg["relationships"]["known"]
NUM_RELATIONSHIPS: int = len(KNOWN_RELATIONSHIPS)
RELATIONSHIP_EMBED_DIM: int = _cfg["relationships"]["embedding_dim"]
DEFAULT_SENDER: str = _cfg["relationships"].get(
    "default_sender",
    next(iter(KNOWN_RELATIONSHIPS)) if KNOWN_RELATIONSHIPS else "stranger",
)

# Channels
CHANNELS: list[str] = _cfg["channels"]

# Longing
_longing = _cfg["longing"]
LONGING_ENABLED: bool = _longing["enabled"]
LONGING_GROWTH_RATE: float = _longing["growth_rate"]
LONGING_CAP: float = _longing["cap"]
LONGING_THRESHOLD_HOURS: float = _longing["threshold_hours"]
LONGING_CONNECTION_FACTOR: float = _longing["connection_factor"]
LONGING_TARGET_DIMS: list[str] = _longing.get("target_dimensions", ["desire"])
LONGING_SECONDARY_DIMS: list[str] = _longing.get("secondary_dimensions", ["connection"])

# Model Architecture
_model = _cfg["model"]
EMBED_DIM: int = _model["embed_dim"]
HIDDEN_DIM: int = _model["hidden_dim"]
HEAD_DIM: int = _model["head_dim"]
DROPOUT: float = _model["dropout"]
ENCODER_MODEL: str = _model["encoder_model"]
MAX_CONTEXT_CHARS: int = _model["max_context_chars"]
DEVICE: str = _model.get("device", "cpu")

# Context dimension — dynamic: relationship embed + 5 temporal/session + channels
CONTEXT_DIM: int = RELATIONSHIP_EMBED_DIM + 5 + len(CHANNELS)

# Training
_training = _cfg["training"]
TRAIN_EPOCHS: int = _training["epochs"]
TRAIN_LR: float = _training["learning_rate"]
TRAIN_BATCH_SIZE: int = _training["batch_size"]
TRAIN_WEIGHT_DECAY: float = _training["weight_decay"]
GRAD_CLIP: float = _training["grad_clip"]
TRAIN_PATIENCE: int = _training["patience"]
TRAIN_VAL_SPLIT: float = _training["val_split"]

# State
_state = _cfg["state"]
MAX_TRAJECTORY_POINTS: int = _state["max_trajectory_points"]
DEFAULT_ABSENCE_SECONDS: int = _state["default_absence_seconds"]

# Summary
SUMMARY_TEMPLATES_FILE: str | None = _cfg["summary"].get("templates_file")

# Timezone
TIMEZONE_OFFSET_HOURS: float = _cfg.get("timezone_offset_hours", 0)

# Calibration (self-calibrating baseline)
_calibration = _cfg.get("calibration", {})
CALIBRATION_ENABLED: bool = _calibration.get("enabled", False)
CALIBRATION_DRIFT_RATE: float = _calibration.get("drift_rate", 0.05)
CALIBRATION_MIN_POINTS: int = _calibration.get("min_trajectory_points", 20)
CALIBRATION_CLAMP_RANGE: float = _calibration.get("clamp_range", 0.15)

# Bootstrap
_bootstrap = _cfg.get("bootstrap", {})
BOOTSTRAP_SOURCE_FILES: list[str] = _bootstrap.get(
    "source_files", ["SOUL.md", "IDENTITY.md", "MEMORY.md"]
)
BOOTSTRAP_MEMORY_PATTERNS: list[str] = _bootstrap.get(
    "memory_patterns", ["memory/20*.md"]
)
BOOTSTRAP_REDACT_PATTERNS: list[str] = _bootstrap.get(
    "redact_patterns", []
)
