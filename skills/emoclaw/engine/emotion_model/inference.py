"""EmotionEngine — main inference pipeline.

Orchestrates: text encoding, feature building, model inference,
state update, and formatted output. This is the entry point called
by the daemon or shell client.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

import torch

from . import config
from .encoder import TextEncoder
from .features import ConversationContext, RelationshipEmbeddings, build_context_features
from .model import EmotionModel
from .state import load_state, save_state
from .summary import generate_summary


class EmotionEngine:
    """Loads model + encoder once, runs inference per message.

    Usage:
        engine = EmotionEngine("checkpoints/best_model.pt")
        block = engine.process_message("Good morning!", sender="primary")
        print(block)
    """

    def __init__(
        self,
        model_path: str | Path | None = None,
        state_path: str | Path = config.STATE_PATH,
        device: str = "cpu",
    ) -> None:
        self.device = device
        self.state_path = Path(state_path)

        # Load text encoder (~1-2s first time)
        self.encoder = TextEncoder()

        # Load emotion model
        self.model = EmotionModel()
        if model_path and Path(model_path).exists():
            try:
                self.model.load_state_dict(
                    torch.load(model_path, map_location=device, weights_only=True)
                )
            except RuntimeError as e:
                if "size mismatch" in str(e):
                    raise RuntimeError(
                        f"Checkpoint was trained with different dimensions than "
                        f"current config ({config.NUM_EMOTION_DIMS} dims). "
                        f"You must retrain the model. Original error: {e}"
                    ) from e
                raise
        self.model.train(False)  # inference mode

        # Relationship embeddings
        self.rel_embeddings = RelationshipEmbeddings()
        rel_path = config.CHECKPOINT_DIR / "rel_embeddings.pt"
        if rel_path.exists():
            self.rel_embeddings.load_state_dict(
                torch.load(rel_path, map_location=device, weights_only=True)
            )

        # Load persisted emotional state
        self.state = load_state(self.state_path)

    def process_message(
        self,
        message_text: str,
        sender: str | None = None,
        channel: str | None = None,
        recent_context: str | None = None,
    ) -> str:
        """Process one incoming message and return the [EMOTIONAL STATE] block.

        Args:
            message_text: The incoming message content
            sender: Who sent it ("primary", "stranger", "group")
            channel: Which channel ("chat", "voice", "email")
            recent_context: Optional recent conversation text for context

        Returns:
            Formatted [EMOTIONAL STATE] block string
        """
        t0 = time.time()
        now = datetime.now(timezone.utc)

        # Apply config defaults if not specified
        if sender is None:
            sender = config.DEFAULT_SENDER
        if channel is None:
            channel = config.CHANNELS[0] if config.CHANNELS else "default"

        # Build conversation context
        ctx = ConversationContext(
            sender_id=sender,
            channel=channel,
            time_since_last_message=self.state.seconds_since_last_message(now),
            time_since_last_session=self.state.seconds_since_last_session(now),
            message_count_this_session=self.state.message_count + 1,
            is_first_message=(self.state.message_count == 0),
            hour_of_day=self._local_hour(now),
        )

        # Encode message text
        text_embed = self.encoder.encode_with_context(message_text, recent_context)

        # Build context features
        context_features = build_context_features(ctx, self.rel_embeddings)

        # Get decayed previous emotion (accounts for time elapsed)
        prev_emotion = self.state.get_decayed_emotion(now)

        # Run model inference
        with torch.no_grad():
            text_embed_t = text_embed.unsqueeze(0)  # [1, 384]
            context_t = context_features.unsqueeze(0)  # [1, 16]
            prev_t = torch.tensor(
                prev_emotion, dtype=torch.float32
            ).unsqueeze(0)  # [1, 11]
            hidden = self.state.get_hidden_state()

            emotion, new_hidden = self.model(text_embed_t, context_t, prev_t, hidden)

        emotion_vec = emotion.squeeze(0).tolist()

        # Update and persist state
        self.state.update(
            emotion_vector=emotion_vec,
            hidden_state=new_hidden,
            timestamp=now,
        )
        save_state(self.state, self.state_path)

        # Generate output
        summary = generate_summary(emotion_vec)
        block = self._format_block(emotion_vec, summary)

        elapsed_ms = (time.time() - t0) * 1000
        return block

    def _format_block(self, emotion: list[float], summary: str) -> str:
        """Format the [EMOTIONAL STATE] context block."""
        lines = ["[EMOTIONAL STATE]"]

        for i, dim_name in enumerate(config.EMOTION_DIMS):
            val = emotion[i]
            low, high = config.DIM_DESCRIPTORS[dim_name]
            if val < 0.35:
                label = low
            elif val > 0.65:
                label = high
            else:
                label = "balanced"
            lines.append(f"{dim_name.capitalize()}: {val:.2f} ({label})")

        lines.append(f"\nThis feels like: {summary}")
        lines.append("[/EMOTIONAL STATE]")

        return "\n".join(lines)

    @staticmethod
    def _local_hour(dt_utc: datetime) -> float:
        """Convert UTC to local hour using configured timezone offset."""
        offset = config.TIMEZONE_OFFSET_HOURS
        return (dt_utc.hour + offset) % 24 + dt_utc.minute / 60.0
