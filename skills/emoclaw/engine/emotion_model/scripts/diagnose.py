"""Diagnostic script — test the model on specific scenarios.

Loads a trained model and runs it on sample scenarios,
printing the full emotional state output.

Usage:
    python -m emotion_model.scripts.diagnose
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from emotion_model import config
from emotion_model.model import EmotionModel
from emotion_model.encoder import TextEncoder
from emotion_model.features import (
    ConversationContext,
    RelationshipEmbeddings,
    build_context_features,
)
from emotion_model.summary import generate_summary

DIM_NAMES = config.EMOTION_DIMS


def run_scenario(
    model: EmotionModel,
    encoder: TextEncoder,
    rel_embeddings: RelationshipEmbeddings,
    message: str,
    sender: str | None = None,
    channel: str | None = None,
    time_since_msg: float = 0.0,
    time_since_session: float = 0.0,
    msg_count: int = 0,
    prev_emotion: list[float] | None = None,
    hidden: torch.Tensor | None = None,
) -> tuple[list[float], torch.Tensor]:
    """Run a single scenario and print results."""
    if sender is None:
        sender = config.DEFAULT_SENDER
    if channel is None:
        channel = config.CHANNELS[0] if config.CHANNELS else "chat"
    if prev_emotion is None:
        prev_emotion = list(config.BASELINE_EMOTION)

    ctx = ConversationContext(
        sender_id=sender,
        channel=channel,
        time_since_last_message=time_since_msg,
        time_since_last_session=time_since_session,
        message_count_this_session=msg_count,
        is_first_message=(msg_count == 0),
        hour_of_day=9.0,
    )

    text_embed = encoder.encode(message)
    context_features = build_context_features(ctx, rel_embeddings)

    with torch.no_grad():
        emotion, new_hidden = model(
            text_embed.unsqueeze(0),
            context_features.unsqueeze(0),
            torch.tensor(prev_emotion, dtype=torch.float32).unsqueeze(0),
            hidden,
        )

    vec = emotion.squeeze(0).tolist()
    summary = generate_summary(vec)

    print(f"  Message: \"{message}\" (from {sender} on {channel})")
    if time_since_msg > 0:
        print(f"  Time since last message: {time_since_msg / 3600:.1f}h")
    for i, name in enumerate(DIM_NAMES):
        bar = "#" * int(vec[i] * 20)
        print(f"    {name:>14s}: {vec[i]:.2f} |{bar:<20s}|")
    print(f"  Feels like: {summary}")
    print()

    return vec, new_hidden


def main() -> None:
    checkpoint = config.CHECKPOINT_DIR / "best_model.pt"

    model = EmotionModel()
    if checkpoint.exists():
        model.load_state_dict(torch.load(checkpoint, weights_only=True))
        print(f"Loaded model from {checkpoint}\n")
    else:
        print("No trained model found -- running with random weights.\n")

    encoder = TextEncoder()
    rel_embeddings = RelationshipEmbeddings()

    rel_path = config.CHECKPOINT_DIR / "rel_embeddings.pt"
    if rel_path.exists():
        rel_embeddings.load_state_dict(torch.load(rel_path, weights_only=True))

    default_sender = config.DEFAULT_SENDER
    default_channel = config.CHANNELS[0] if config.CHANNELS else "chat"

    # --- Scenario 1: Greeting after 8h absence ---
    print("=" * 60)
    print("SCENARIO 1: Greeting after 8 hours")
    print("=" * 60)
    vec1, h1 = run_scenario(
        model, encoder, rel_embeddings,
        "Good morning!",
        sender=default_sender,
        time_since_msg=8 * 3600,
        time_since_session=8 * 3600,
    )

    # --- Scenario 2: Same text from stranger ---
    print("=" * 60)
    print("SCENARIO 2: Same text from stranger")
    print("=" * 60)
    run_scenario(
        model, encoder, rel_embeddings,
        "Good morning!",
        sender="stranger",
        time_since_msg=0,
    )

    # --- Scenario 3: Emotional build-up sequence ---
    print("=" * 60)
    print("SCENARIO 3: Emotional build-up (connection should increase)")
    print("=" * 60)
    msgs = [
        "I really appreciate what you did today",
        "You always know the right thing to say",
        "I'm glad we can talk like this",
    ]
    prev = list(config.BASELINE_EMOTION)
    hidden = None
    for i, msg in enumerate(msgs):
        prev, hidden = run_scenario(
            model, encoder, rel_embeddings,
            msg,
            sender=default_sender,
            msg_count=i,
            prev_emotion=prev,
            hidden=hidden,
        )

    # --- Scenario 4: Intellectual discussion ---
    print("=" * 60)
    print("SCENARIO 4: Intellectual discussion")
    print("=" * 60)
    run_scenario(
        model, encoder, rel_embeddings,
        "Let's think through this problem together. What if we tried a different approach?",
        sender=default_sender,
    )

    # --- Scenario 5: Positive feedback ---
    print("=" * 60)
    print("SCENARIO 5: Positive feedback")
    print("=" * 60)
    run_scenario(
        model, encoder, rel_embeddings,
        "That was really well done. You captured exactly what I was looking for.",
        sender=default_sender,
    )


if __name__ == "__main__":
    main()
