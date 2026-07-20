# Model Architecture

## Overview

The emotion model is a lightweight sequential neural network (~161K trainable parameters) that estimates an N-dimensional emotional state from text and context.

## Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    Input Assembly                         │
│                                                          │
│  Text ──→ [MiniLM-L6-v2] ──→ 384-dim embedding          │
│                                                          │
│  Context ──→ [Feature Builder] ──→ R+5+C dim vector      │
│    R = relationship embedding dim (default 8)            │
│    C = number of channels (default 3)                    │
│    5 = temporal + session features                        │
│                                                          │
│  Previous emotion ──→ N-dim vector                       │
│                                                          │
│  Concatenated: [384 + (R+5+C) + N] = input_dim           │
└──────────────────────┬──────────────────────────────────┘
                       │
              ┌────────┴────────┐
              │  Input Project   │
              │  Linear(→128)   │
              │  LayerNorm       │
              │  GELU            │
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              │      GRU        │
              │  1 layer, 128   │
              │  hidden state   │ ← persisted across sessions
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              │  Emotion Head   │
              │  Linear(→64)    │
              │  GELU           │
              │  Dropout(0.1)   │
              │  Linear(→N)     │
              │  Sigmoid        │
              └────────┬────────┘
                       │
              N-dim emotion vector ∈ [0, 1]
```

## Components

### Text Encoder (Frozen)

- Model: `all-MiniLM-L6-v2` (22M parameters, not trainable)
- Output: 384-dimensional sentence embedding
- Handles up to 256 tokens per input
- Context window: optional `recent_context` is prepended and truncated to `max_context_chars`

### Context Feature Vector

Layout: `[relationship_embed | temporal | session | channel_onehot]`

| Slice | Size | Description |
|-------|------|-------------|
| `[0:R]` | R (default 8) | Learned relationship embedding |
| `[R]` | 1 | log(time since last message) / 15, capped at 1 |
| `[R+1]` | 1 | log(time since last session) / 15, capped at 1 |
| `[R+2]` | 1 | conversation depth (msg_count / 50, capped at 1) |
| `[R+3]` | 1 | is_first_message flag (0 or 1) |
| `[R+4]` | 1 | hour of day / 24 (timezone-adjusted) |
| `[R+5:]` | C | channel one-hot encoding |

### Relationship Embeddings

- Each known relationship (sender) gets a learned R-dimensional vector
- Default: 3 relationships (primary, stranger, group) with 8-dim embeddings
- Unknown senders fall back to the "stranger" embedding
- Embeddings are learned during training and persisted separately

### GRU (Emotional Memory)

The single-layer GRU is the core innovation. Its hidden state:
- Carries emotional trajectory across messages within a session
- Persists across sessions via serialization to the state file
- Represents "emotional residue" — the accumulation of relational experience
- Learns what emotional information is worth carrying forward

### Emotion Head

- Two-layer MLP with GELU activation and dropout
- Sigmoid output ensures all dimensions stay in [0, 1]
- Each output dimension is independent (no softmax)

## Parameter Count

With default config (11 dimensions, 128 hidden, 64 head):
- Input projection: ~53K
- GRU: ~99K
- Emotion head: ~9K
- **Total: ~161K trainable parameters**

The frozen MiniLM encoder adds ~22M parameters but requires no GPU memory for gradients.

## State Persistence

The emotional state is serialized to JSON:

```json
{
  "version": 1,
  "emotion_vector": [0.55, 0.35, ...],
  "gru_hidden_state": "<base64-encoded tensor>",
  "last_updated": "2025-01-15T10:30:00+00:00",
  "last_session_start": "2025-01-15T10:00:00+00:00",
  "last_message_time": "2025-01-15T10:30:00+00:00",
  "message_count": 5,
  "baseline_emotion": [0.55, 0.35, ...],
  "trajectory": [{"t": "...", "v": [...]}]
}
```

The GRU hidden state is stored as base64-encoded raw float32 bytes. This allows the emotional residue to carry across restarts without losing information.

## Decay Mechanism

Between sessions, each emotion dimension decays exponentially toward its baseline:

```
new_value = baseline + (current - baseline) * exp(-0.693 * hours / half_life)
```

The 0.693 factor ensures the half-life is exact: after `decay_hours`, the deviation from baseline is halved.

## Longing Mechanism

When enabled and the primary relationship has been absent longer than `threshold_hours`:

1. Compute boost: `min(cap, growth_rate * hours_elapsed)`
2. Add boost to target dimensions (e.g., desire)
3. Add `boost * connection_factor` to secondary dimensions (e.g., connection)

This models the natural phenomenon where absence increases desire and highlights connection.
