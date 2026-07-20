"""EmotionModel — lightweight emotion state estimator.

Takes text embedding + context features + previous emotion vector,
outputs an N-dimensional emotional state in [0, 1].

The GRU hidden state carries emotional trajectory across messages
and persists across sessions — this IS the "emotional residue."
"""

from __future__ import annotations

import torch
import torch.nn as nn

from . import config


class EmotionModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()

        input_dim = config.EMBED_DIM + config.CONTEXT_DIM + config.NUM_EMOTION_DIMS

        # Project heterogeneous input into a shared representation
        self.input_proj = nn.Sequential(
            nn.Linear(input_dim, config.HIDDEN_DIM),
            nn.LayerNorm(config.HIDDEN_DIM),
            nn.GELU(),
        )

        # Temporal state — learns what emotional information to carry forward
        self.gru = nn.GRU(
            input_size=config.HIDDEN_DIM,
            hidden_size=config.HIDDEN_DIM,
            num_layers=1,
            batch_first=True,
        )

        # Map hidden representation to emotion dimensions
        self.emotion_head = nn.Sequential(
            nn.Linear(config.HIDDEN_DIM, config.HEAD_DIM),
            nn.GELU(),
            nn.Dropout(config.DROPOUT),
            nn.Linear(config.HEAD_DIM, config.NUM_EMOTION_DIMS),
            nn.Sigmoid(),
        )

    def forward(
        self,
        text_embed: torch.Tensor,       # [batch, EMBED_DIM]
        context_features: torch.Tensor,  # [batch, CONTEXT_DIM]
        prev_emotion: torch.Tensor,      # [batch, NUM_EMOTION_DIMS]
        hidden: torch.Tensor | None = None,  # [1, batch, HIDDEN_DIM]
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Run one step of emotion inference.

        Returns:
            emotion: [batch, NUM_EMOTION_DIMS] — the new emotional state vector
            hidden:  [1, batch, HIDDEN_DIM] — updated GRU hidden state
        """
        x = torch.cat([text_embed, context_features, prev_emotion], dim=-1)
        x = self.input_proj(x)
        x = x.unsqueeze(1)  # [batch, 1, hidden] — single timestep for GRU

        if hidden is None:
            hidden = torch.zeros(1, x.size(0), config.HIDDEN_DIM, device=x.device)

        gru_out, hidden = self.gru(x, hidden)
        emotion = self.emotion_head(gru_out.squeeze(1))

        return emotion, hidden
