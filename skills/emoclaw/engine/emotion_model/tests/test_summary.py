"""Tests for summary generation."""

from emotion_model import config
from emotion_model.summary import generate_summary, SUMMARY_TEMPLATES


def _make_emotion(**overrides: float) -> list[float]:
    """Build a neutral emotion vector with specific dimension overrides."""
    vec = [0.5] * config.NUM_EMOTION_DIMS
    for name, val in overrides.items():
        vec[config.EMOTION_DIMS.index(name)] = val
    return vec


def test_generates_string():
    """Summary is always a non-empty string."""
    emotion = [0.5] * config.NUM_EMOTION_DIMS
    summary = generate_summary(emotion)
    assert isinstance(summary, str)
    assert len(summary) > 0


def test_high_connection_matches():
    """High connection + safety + valence should match warm templates."""
    emotion = _make_emotion(valence=0.9, safety=0.9, connection=0.9)
    summary = generate_summary(emotion)
    warm_templates = SUMMARY_TEMPLATES[("connection_high", "safety_high", "valence_high")]
    assert summary in warm_templates


def test_guarded_matches():
    """Low safety + low dominance should match guarded templates."""
    emotion = _make_emotion(dominance=0.2, safety=0.2)
    summary = generate_summary(emotion)
    guarded_templates = SUMMARY_TEMPLATES[("safety_low", "dominance_low")]
    assert summary in guarded_templates


def test_default_fallback():
    """All-neutral values should fall back to default templates."""
    emotion = [0.5] * config.NUM_EMOTION_DIMS  # all balanced
    summary = generate_summary(emotion)
    default_templates = SUMMARY_TEMPLATES[()]
    assert summary in default_templates


def test_all_template_keys_valid():
    """All template keys reference valid dimension names."""
    valid_suffixes = {"_high", "_low"}
    for key in SUMMARY_TEMPLATES:
        for tag in key:
            parts = tag.rsplit("_", 1)
            assert len(parts) == 2, f"Invalid tag format: {tag}"
            dim_name, suffix = parts
            assert f"_{suffix}" in valid_suffixes, f"Invalid suffix in {tag}"
            assert dim_name in config.EMOTION_DIMS, f"Unknown dimension in {tag}: {dim_name}"


def test_all_templates_non_empty():
    """Every template key has at least one summary string."""
    for key, templates in SUMMARY_TEMPLATES.items():
        assert len(templates) > 0, f"Empty templates for key {key}"
        for t in templates:
            assert isinstance(t, str) and len(t) > 0
