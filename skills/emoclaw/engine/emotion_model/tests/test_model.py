"""Tests for EmotionModel."""

import torch
import pytest

from emotion_model import config
from emotion_model.model import EmotionModel


@pytest.fixture
def model():
    return EmotionModel()


def test_forward_pass_shape(model):
    """Model outputs correct shapes."""
    batch = 4
    text_embed = torch.randn(batch, config.EMBED_DIM)
    context = torch.randn(batch, config.CONTEXT_DIM)
    prev_emotion = torch.rand(batch, config.NUM_EMOTION_DIMS)

    emotion, hidden = model(text_embed, context, prev_emotion)

    assert emotion.shape == (batch, config.NUM_EMOTION_DIMS)
    assert hidden.shape == (1, batch, config.HIDDEN_DIM)


def test_output_range(model):
    """All output values are in [0, 1] (sigmoid)."""
    text_embed = torch.randn(1, config.EMBED_DIM)
    context = torch.randn(1, config.CONTEXT_DIM)
    prev_emotion = torch.rand(1, config.NUM_EMOTION_DIMS)

    emotion, _ = model(text_embed, context, prev_emotion)

    assert (emotion >= 0.0).all()
    assert (emotion <= 1.0).all()


def test_hidden_state_continuity(model):
    """Hidden state carries information between calls."""
    text_embed = torch.randn(1, config.EMBED_DIM)
    context = torch.randn(1, config.CONTEXT_DIM)
    prev = torch.rand(1, config.NUM_EMOTION_DIMS)

    # First call -- no hidden state
    emotion1, hidden1 = model(text_embed, context, prev)

    # Second call -- with hidden state from first call
    emotion2, hidden2 = model(text_embed, context, emotion1, hidden1)

    # Hidden states should differ (GRU updated)
    assert not torch.allclose(hidden1, hidden2)


def test_single_example(model):
    """Works with batch size 1."""
    text_embed = torch.randn(1, config.EMBED_DIM)
    context = torch.randn(1, config.CONTEXT_DIM)
    prev = torch.rand(1, config.NUM_EMOTION_DIMS)

    emotion, hidden = model(text_embed, context, prev)
    assert emotion.shape == (1, config.NUM_EMOTION_DIMS)


def test_parameter_count(model):
    """Model is lightweight (under 200K params)."""
    total = sum(p.numel() for p in model.parameters())
    assert total < 200_000, f"Model has {total:,} params -- expected under 200K"


def test_inference_deterministic(model):
    """Same input produces same output in inference mode."""
    model.eval()
    text_embed = torch.randn(1, config.EMBED_DIM)
    context = torch.randn(1, config.CONTEXT_DIM)
    prev = torch.rand(1, config.NUM_EMOTION_DIMS)

    with torch.no_grad():
        e1, _ = model(text_embed, context, prev)
        e2, _ = model(text_embed, context, prev)

    assert torch.allclose(e1, e2)
