"""Context feature engineering and relationship embeddings.

Builds the context feature vector from non-textual signals:
relationship identity, temporal features, session state, and channel.

Vector layout (CONTEXT_DIM = RELATIONSHIP_EMBED_DIM + 5 + len(CHANNELS)):
    [0:R]     relationship embedding (learned, R dims)
    [R]       log(time since last message) normalized
    [R+1]     log(time since last session) normalized
    [R+2]     conversation depth (message_count / 50, capped at 1)
    [R+3]     is_first_message flag
    [R+4]     hour of day / 24
    [R+5:]    channel one-hot (one slot per configured channel)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn as nn

from . import config


@dataclass
class ConversationContext:
    """Non-textual context for a single message."""

    sender_id: str                    # e.g. "primary", "stranger", "group"
    channel: str                      # e.g. "chat", "voice", "email"
    time_since_last_message: float    # seconds
    time_since_last_session: float    # seconds
    message_count_this_session: int
    is_first_message: bool
    hour_of_day: float                # 0.0 - 24.0 (timezone-adjusted)


class RelationshipEmbeddings(nn.Module):
    """Learned embeddings for known relationships.

    Each person gets an embedding vector that the model learns to associate
    with emotional responses.
    """

    def __init__(self) -> None:
        super().__init__()
        self.embeddings = nn.Embedding(
            num_embeddings=config.NUM_RELATIONSHIPS,
            embedding_dim=config.RELATIONSHIP_EMBED_DIM,
        )

    def forward(self, relationship_id: int) -> torch.Tensor:
        """Returns [RELATIONSHIP_EMBED_DIM] vector."""
        idx = torch.tensor(relationship_id, dtype=torch.long)
        return self.embeddings(idx)


def build_context_features(
    ctx: ConversationContext,
    rel_embeddings: RelationshipEmbeddings,
) -> torch.Tensor:
    """Build the context feature vector.

    Returns a tensor of size CONTEXT_DIM.
    """
    # Relationship embedding
    rel_id = config.KNOWN_RELATIONSHIPS.get(ctx.sender_id, 1)  # default: stranger
    rel_embed = rel_embeddings(rel_id)  # [RELATIONSHIP_EMBED_DIM]

    # Temporal features (log-scaled, normalized to ~[0, 1])
    time_msg = min(math.log(ctx.time_since_last_message + 1) / 15.0, 1.0)
    time_session = min(math.log(ctx.time_since_last_session + 1) / 15.0, 1.0)

    # Session features
    depth = min(ctx.message_count_this_session / 50.0, 1.0)
    is_first = 1.0 if ctx.is_first_message else 0.0
    hour = ctx.hour_of_day / 24.0

    # Channel one-hot (dynamic from config)
    channel_features = [
        1.0 if ctx.channel == ch else 0.0
        for ch in config.CHANNELS
    ]

    scalar_features = torch.tensor(
        [time_msg, time_session, depth, is_first, hour] + channel_features,
        dtype=torch.float32,
    )

    return torch.cat([rel_embed.detach(), scalar_features])  # [CONTEXT_DIM]
