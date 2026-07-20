"""Text encoder wrapper for sentence-transformers.

Uses all-MiniLM-L6-v2 to convert message text into a 384-dim embedding.
The encoder is frozen — we don't train it, just use it as input.
"""

from __future__ import annotations

import torch
from sentence_transformers import SentenceTransformer

from . import config


class TextEncoder:
    """Wraps a sentence-transformer model for encoding messages.

    Loaded once on init (~1-2s). Subsequent calls are fast (~20ms).
    """

    def __init__(self, model_name: str = config.ENCODER_MODEL) -> None:
        self.model = SentenceTransformer(model_name, device="cpu")

    def encode(self, text: str) -> torch.Tensor:
        """Encode a single text string to a 384-dim CPU vector."""
        embedding = self.model.encode(
            text,
            convert_to_tensor=True,
            show_progress_bar=False,
        )
        return embedding.cpu()  # [384], always on CPU

    def encode_with_context(
        self,
        message: str,
        context: str | None = None,
        max_context_chars: int = config.MAX_CONTEXT_CHARS,
    ) -> torch.Tensor:
        """Encode message with optional recent conversation context.

        Context is truncated from the left (keeping the most recent part)
        and prepended to capture conversational flow.
        """
        if context:
            context = context[-max_context_chars:]
            combined = f"{context}\n---\n{message}"
        else:
            combined = message
        return self.encode(combined)
