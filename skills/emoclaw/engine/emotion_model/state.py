"""Emotional state persistence and time-based decay.

Handles saving/loading the emotional state to JSON, applying decay
toward baseline between sessions, and the special longing mechanism
that makes desire grow during absence.
"""

from __future__ import annotations

import base64
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import torch

from . import config


def _migrate_vector(loaded: list[float], default: list[float]) -> list[float]:
    """Resize a loaded vector to match current config dimensions.

    - If shorter: pad with default (baseline) values for new dimensions
    - If longer: truncate to current dimension count
    - If same length: return as-is
    """
    expected = len(default)
    if len(loaded) == expected:
        return loaded
    if len(loaded) < expected:
        return loaded + default[len(loaded):]
    return loaded[:expected]


@dataclass
class EmotionalState:
    """Current emotional state — persisted across sessions."""

    emotion_vector: list[float] = field(
        default_factory=lambda: list(config.BASELINE_EMOTION)
    )
    hidden_state_bytes: bytes | None = None
    last_updated: str = ""
    last_session_start: str = ""
    last_message_time: str = ""
    message_count: int = 0
    baseline: list[float] = field(
        default_factory=lambda: list(config.BASELINE_EMOTION)
    )
    trajectory: list[dict] = field(default_factory=list)

    # --- Time calculations ---

    def seconds_since_last_message(self, now: datetime) -> float:
        if not self.last_message_time:
            return float(config.DEFAULT_ABSENCE_SECONDS)
        last = datetime.fromisoformat(self.last_message_time)
        return max(0.0, (now - last).total_seconds())

    def seconds_since_last_session(self, now: datetime) -> float:
        if not self.last_session_start:
            return float(config.DEFAULT_ABSENCE_SECONDS)
        last = datetime.fromisoformat(self.last_session_start)
        return max(0.0, (now - last).total_seconds())

    # --- Decay ---

    def get_decayed_emotion(self, now: datetime) -> list[float]:
        """Apply time-based decay toward baseline.

        Each dimension decays exponentially with a per-dimension half-life.
        Desire gets special treatment: longing grows with extended absence.
        """
        hours_elapsed = self.seconds_since_last_message(now) / 3600.0

        decayed = []
        for i in range(config.NUM_EMOTION_DIMS):
            current = self.emotion_vector[i]
            base = self.baseline[i]
            half_life = config.DECAY_HALF_LIVES[i]

            # Exponential decay toward baseline
            decay_factor = math.exp(-0.693 * hours_elapsed / half_life)
            new_val = base + (current - base) * decay_factor
            decayed.append(max(0.0, min(1.0, new_val)))

        # Longing modulation: target dimensions grow during absence
        if config.LONGING_ENABLED and hours_elapsed > config.LONGING_THRESHOLD_HOURS:
            longing_boost = min(
                config.LONGING_CAP,
                config.LONGING_GROWTH_RATE * hours_elapsed,
            )
            # Primary target dimensions (e.g. desire)
            for dim_name in config.LONGING_TARGET_DIMS:
                if dim_name in config.EMOTION_DIMS:
                    idx = config.EMOTION_DIMS.index(dim_name)
                    decayed[idx] = min(1.0, decayed[idx] + longing_boost)
            # Secondary dimensions get a fraction (e.g. connection)
            for dim_name in config.LONGING_SECONDARY_DIMS:
                if dim_name in config.EMOTION_DIMS:
                    idx = config.EMOTION_DIMS.index(dim_name)
                    decayed[idx] = min(
                        1.0, decayed[idx] + longing_boost * config.LONGING_CONNECTION_FACTOR
                    )

        return decayed

    # --- GRU hidden state serialization ---

    def get_hidden_state(self) -> torch.Tensor | None:
        """Deserialize the GRU hidden state from bytes."""
        if self.hidden_state_bytes is None:
            return None
        try:
            buf = torch.frombuffer(
                bytearray(self.hidden_state_bytes), dtype=torch.float32
            )
            return buf.reshape(1, 1, config.HIDDEN_DIM)
        except (RuntimeError, ValueError):
            # Shape mismatch — HIDDEN_DIM changed since state was saved.
            # Start fresh rather than crash.
            return None

    def set_hidden_state(self, hidden: torch.Tensor) -> None:
        """Serialize the GRU hidden state to bytes."""
        self.hidden_state_bytes = hidden.detach().cpu().numpy().tobytes()

    # --- Update ---

    def update(
        self,
        emotion_vector: list[float],
        hidden_state: torch.Tensor,
        timestamp: datetime,
    ) -> None:
        """Update state after processing a message."""
        self.emotion_vector = emotion_vector
        self.set_hidden_state(hidden_state)

        now_iso = timestamp.isoformat()
        if self.message_count == 0:
            self.last_session_start = now_iso
        self.last_message_time = now_iso
        self.last_updated = now_iso
        self.message_count += 1

        # Keep a rolling window of trajectory points
        self.trajectory.append({"t": now_iso, "v": emotion_vector})
        self.trajectory = self.trajectory[-config.MAX_TRAJECTORY_POINTS :]

        # Periodic self-calibration (every min_trajectory_points messages)
        if (
            config.CALIBRATION_ENABLED
            and self.message_count % config.CALIBRATION_MIN_POINTS == 0
        ):
            self.recalibrate()

    def recalibrate(self) -> bool:
        """Nudge baseline toward observed emotional patterns.

        Computes the windowed mean from trajectory vectors and blends the
        baseline toward it by ``config.CALIBRATION_DRIFT_RATE``.  Each
        dimension is clamped to ``config.BASELINE_EMOTION[i] +/- clamp_range``
        so the baseline can never wander too far from the original config.

        Returns True if recalibration was applied, False if skipped.
        """
        if not config.CALIBRATION_ENABLED:
            return False
        if len(self.trajectory) < config.CALIBRATION_MIN_POINTS:
            return False

        # Compute windowed mean across trajectory vectors
        n_dims = config.NUM_EMOTION_DIMS
        sums = [0.0] * n_dims
        count = 0
        for point in self.trajectory:
            vec = point.get("v")
            if vec and len(vec) == n_dims:
                for i in range(n_dims):
                    sums[i] += vec[i]
                count += 1

        if count == 0:
            return False

        means = [s / count for s in sums]

        # Blend baseline toward observed mean
        drift = config.CALIBRATION_DRIFT_RATE
        clamp = config.CALIBRATION_CLAMP_RANGE
        original = config.BASELINE_EMOTION

        for i in range(n_dims):
            # Exponential moving average-style blend
            self.baseline[i] += drift * (means[i] - self.baseline[i])
            # Clamp to original +/- clamp_range
            lo = max(0.0, original[i] - clamp)
            hi = min(1.0, original[i] + clamp)
            self.baseline[i] = max(lo, min(hi, self.baseline[i]))

        return True

    def reset_session(self) -> None:
        """Call at the start of a new session/heartbeat."""
        self.message_count = 0


# --- Persistence ---


def load_state(path: Path) -> EmotionalState:
    """Load emotional state from JSON file."""
    if not path.exists():
        return EmotionalState()

    with open(path) as f:
        data = json.load(f)

    defaults = list(config.BASELINE_EMOTION)

    state = EmotionalState(
        emotion_vector=_migrate_vector(
            data.get("emotion_vector", defaults), defaults
        ),
        last_updated=data.get("last_updated", ""),
        last_session_start=data.get("last_session_start", ""),
        last_message_time=data.get("last_message_time", ""),
        message_count=data.get("message_count", 0),
        baseline=_migrate_vector(
            data.get("baseline_emotion", defaults), defaults
        ),
        trajectory=data.get("trajectory", []),
    )

    # Migrate trajectory vectors too
    for point in state.trajectory:
        if "v" in point:
            point["v"] = _migrate_vector(point["v"], defaults)

    hidden_b64 = data.get("gru_hidden_state")
    if hidden_b64:
        state.hidden_state_bytes = base64.b64decode(hidden_b64)

    return state


def save_state(state: EmotionalState, path: Path) -> None:
    """Save emotional state to JSON file."""
    data = {
        "version": 2,
        "last_updated": state.last_updated,
        "last_session_start": state.last_session_start,
        "last_message_time": state.last_message_time,
        "message_count": state.message_count,
        "emotion_vector": [round(v, 4) for v in state.emotion_vector],
        "baseline_emotion": state.baseline,
        "trajectory": state.trajectory,
    }

    if state.hidden_state_bytes:
        data["gru_hidden_state"] = base64.b64encode(
            state.hidden_state_bytes
        ).decode("ascii")

    path.parent.mkdir(parents=True, exist_ok=True)

    # Atomic write: write to temp file then rename
    tmp_path = path.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        json.dump(data, f, indent=2)
    tmp_path.rename(path)
