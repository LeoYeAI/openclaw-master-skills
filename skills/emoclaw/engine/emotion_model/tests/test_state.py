"""Tests for emotional state persistence and decay."""

import math
from datetime import datetime, timedelta, timezone
from pathlib import Path

import torch
import pytest

from emotion_model import config
from emotion_model.state import EmotionalState, load_state, save_state

# Dynamic helpers — no hardcoded dimension counts
N = config.NUM_EMOTION_DIMS
DESIRE_IDX = config.EMOTION_DIMS.index("desire")
LONGING_DIMS = {
    config.EMOTION_DIMS.index(d)
    for d in config.LONGING_TARGET_DIMS + config.LONGING_SECONDARY_DIMS
    if d in config.EMOTION_DIMS
}


@pytest.fixture
def tmp_state_path(tmp_path):
    return tmp_path / "emotional-state.json"


def test_default_state():
    """Fresh state starts at baseline."""
    state = EmotionalState()
    assert state.emotion_vector == config.BASELINE_EMOTION
    assert state.message_count == 0
    assert state.hidden_state_bytes is None


def test_save_load_roundtrip(tmp_state_path):
    """State survives JSON serialization."""
    state = EmotionalState()
    state.emotion_vector = [0.1 * i for i in range(N)]
    state.last_updated = "2026-02-07T10:00:00+00:00"
    state.last_message_time = "2026-02-07T10:00:00+00:00"
    state.message_count = 5

    # Set a hidden state
    hidden = torch.randn(1, 1, config.HIDDEN_DIM)
    state.set_hidden_state(hidden)

    save_state(state, tmp_state_path)
    loaded = load_state(tmp_state_path)

    assert loaded.emotion_vector == [round(v, 4) for v in state.emotion_vector]
    assert loaded.message_count == 5
    assert loaded.last_updated == state.last_updated

    # Hidden state should roundtrip
    loaded_hidden = loaded.get_hidden_state()
    assert loaded_hidden is not None
    assert torch.allclose(hidden, loaded_hidden, atol=1e-6)


def test_load_missing_file(tmp_path):
    """Loading from nonexistent path gives default state."""
    state = load_state(tmp_path / "nope.json")
    assert state.emotion_vector == config.BASELINE_EMOTION


def test_decay_at_zero_time():
    """No time elapsed means no decay."""
    state = EmotionalState()
    state.emotion_vector = [0.9] * N
    now_str = "2026-02-07T10:00:00+00:00"
    state.last_message_time = now_str

    now = datetime.fromisoformat(now_str)
    decayed = state.get_decayed_emotion(now)

    # Should be very close to original (no time passed)
    for i in range(N):
        assert abs(decayed[i] - 0.9) < 0.001


def test_decay_toward_baseline():
    """After long time, emotions approach baseline."""
    state = EmotionalState()
    state.emotion_vector = [1.0] * N  # everything maxed
    state.last_message_time = "2026-02-01T00:00:00+00:00"

    # 7 days later -- should be very close to baseline
    now = datetime(2026, 2, 8, 0, 0, 0, tzinfo=timezone.utc)
    decayed = state.get_decayed_emotion(now)

    # Skip longing target/secondary dims — longing boost pushes these above baseline
    # after extended absence, which is correct behavior
    for i in range(N):
        if i in LONGING_DIMS:
            continue
        # After 168 hours, even the slowest decay (12h half-life)
        # should be very close to baseline
        assert abs(decayed[i] - config.BASELINE_EMOTION[i]) < 0.05, (
            f"Dim {config.EMOTION_DIMS[i]}: {decayed[i]:.3f} "
            f"far from baseline {config.BASELINE_EMOTION[i]}"
        )


def test_longing_boost():
    """Desire grows during extended absence."""
    state = EmotionalState()
    state.emotion_vector = list(config.BASELINE_EMOTION)
    state.last_message_time = "2026-02-07T00:00:00+00:00"

    # 6 hours later
    now = datetime(2026, 2, 7, 6, 0, 0, tzinfo=timezone.utc)
    decayed = state.get_decayed_emotion(now)

    # Desire should be boosted above baseline
    baseline_desire = config.BASELINE_EMOTION[DESIRE_IDX]
    assert decayed[DESIRE_IDX] > baseline_desire, (
        f"Desire {decayed[DESIRE_IDX]:.3f} should be above baseline {baseline_desire}"
    )

    # Longing boost = 0.02 * 6 = 0.12
    expected_boost = config.LONGING_GROWTH_RATE * 6
    assert decayed[DESIRE_IDX] >= baseline_desire + expected_boost * 0.5  # rough check


def test_longing_caps():
    """Longing boost doesn't exceed cap."""
    state = EmotionalState()
    state.emotion_vector = list(config.BASELINE_EMOTION)
    state.last_message_time = "2026-02-01T00:00:00+00:00"

    # 100 hours later -- way past cap
    now = datetime(2026, 2, 5, 4, 0, 0, tzinfo=timezone.utc)
    decayed = state.get_decayed_emotion(now)

    # Desire should not exceed 1.0
    assert decayed[DESIRE_IDX] <= 1.0


def test_update_increments_count():
    """update() increments message count and sets timestamps."""
    state = EmotionalState()
    now = datetime(2026, 2, 7, 10, 0, 0, tzinfo=timezone.utc)
    hidden = torch.zeros(1, 1, config.HIDDEN_DIM)

    state.update([0.5] * N, hidden, now)
    assert state.message_count == 1
    assert state.last_session_start != ""

    state.update([0.6] * N, hidden, now + timedelta(minutes=5))
    assert state.message_count == 2


def test_trajectory_rolling_window():
    """Trajectory keeps only the last N points."""
    state = EmotionalState()
    hidden = torch.zeros(1, 1, config.HIDDEN_DIM)

    for i in range(config.MAX_TRAJECTORY_POINTS + 20):
        now = datetime(2026, 2, 7, tzinfo=timezone.utc) + timedelta(minutes=i)
        state.update([0.5] * N, hidden, now)

    assert len(state.trajectory) == config.MAX_TRAJECTORY_POINTS


def test_reset_session():
    """reset_session clears message count."""
    state = EmotionalState()
    state.message_count = 10
    state.reset_session()
    assert state.message_count == 0


# --- Self-Calibration tests ---


def test_recalibrate_disabled_by_default():
    """Baseline stays unchanged when calibration is disabled (default)."""
    state = EmotionalState()
    # Fill trajectory with high-valence data
    for i in range(30):
        state.trajectory.append({"t": "2026-02-07T10:00:00+00:00", "v": [0.9] * N})

    original_baseline = list(state.baseline)
    result = state.recalibrate()

    assert result is False
    assert state.baseline == original_baseline


def test_recalibrate_drifts_toward_observed(monkeypatch):
    """When enabled, baseline shifts toward observed trajectory mean."""
    monkeypatch.setattr(config, "CALIBRATION_ENABLED", True)
    monkeypatch.setattr(config, "CALIBRATION_DRIFT_RATE", 0.05)
    monkeypatch.setattr(config, "CALIBRATION_MIN_POINTS", 5)
    monkeypatch.setattr(config, "CALIBRATION_CLAMP_RANGE", 0.15)

    state = EmotionalState()
    original_baseline = list(state.baseline)

    # Fill trajectory with consistently high values
    high_vec = [0.9] * N
    for i in range(10):
        state.trajectory.append({"t": "2026-02-07T10:00:00+00:00", "v": list(high_vec)})

    result = state.recalibrate()
    assert result is True

    # Every baseline dimension should have moved toward 0.9
    for i in range(N):
        if original_baseline[i] < 0.9:
            assert state.baseline[i] > original_baseline[i], (
                f"Dim {config.EMOTION_DIMS[i]}: baseline {state.baseline[i]:.3f} "
                f"should have increased from {original_baseline[i]:.3f}"
            )


def test_recalibrate_respects_clamp(monkeypatch):
    """Baseline never drifts beyond clamp_range from original config."""
    monkeypatch.setattr(config, "CALIBRATION_ENABLED", True)
    monkeypatch.setattr(config, "CALIBRATION_DRIFT_RATE", 1.0)  # aggressive drift
    monkeypatch.setattr(config, "CALIBRATION_MIN_POINTS", 5)
    monkeypatch.setattr(config, "CALIBRATION_CLAMP_RANGE", 0.15)

    state = EmotionalState()

    # Fill trajectory with max values
    for i in range(10):
        state.trajectory.append({"t": "2026-02-07T10:00:00+00:00", "v": [1.0] * N})

    # Run calibration multiple times to push hard
    for _ in range(20):
        state.recalibrate()

    for i in range(N):
        original = config.BASELINE_EMOTION[i]
        lo = max(0.0, original - 0.15)
        hi = min(1.0, original + 0.15)
        assert lo <= state.baseline[i] <= hi, (
            f"Dim {config.EMOTION_DIMS[i]}: baseline {state.baseline[i]:.3f} "
            f"outside clamp [{lo:.2f}, {hi:.2f}]"
        )


def test_recalibrate_requires_min_points(monkeypatch):
    """Calibration skipped when trajectory has too few points."""
    monkeypatch.setattr(config, "CALIBRATION_ENABLED", True)
    monkeypatch.setattr(config, "CALIBRATION_MIN_POINTS", 20)

    state = EmotionalState()
    original_baseline = list(state.baseline)

    # Only 5 points — not enough
    for i in range(5):
        state.trajectory.append({"t": "2026-02-07T10:00:00+00:00", "v": [0.9] * N})

    result = state.recalibrate()
    assert result is False
    assert state.baseline == original_baseline
