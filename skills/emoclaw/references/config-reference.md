# Configuration Reference

Full schema for `emoclaw.yaml`.

## Top-Level

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `name` | string | `"my-agent"` | Agent name. Used in socket paths and log messages. |
| `timezone_offset_hours` | float | `0` | UTC offset for time-of-day feature. e.g. EST = -5, CET = 1. |

## `paths`

All paths are relative to the project root.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `state_file` | string | `"memory/emotional-state.json"` | Persisted emotional state |
| `checkpoint_dir` | string | `"emotion_model/checkpoints"` | Model weights directory |
| `data_dir` | string | `"emotion_model/data"` | Training data directory |
| `memory_dir` | string | `"memory"` | Memory files directory |
| `socket_path` | string | `"/tmp/{name}-emotion.sock"` | Unix socket path. `{name}` is replaced with agent name. |

## `dimensions[]`

List of emotion dimension definitions.

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `name` | string | yes | Dimension identifier (lowercase, no spaces) |
| `low` | string | yes | Label for the low end (value near 0) |
| `high` | string | yes | Label for the high end (value near 1) |
| `baseline` | float | yes | Resting state value (0.0-1.0) |
| `decay_hours` | float | yes | Half-life in hours for decay toward baseline |
| `loss_weight` | float | yes | Relative weight during training loss computation |

Example:
```yaml
dimensions:
  - name: valence
    low: negative
    high: positive
    baseline: 0.55
    decay_hours: 6.0
    loss_weight: 1.0
```

## `relationships`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `known` | dict[str, int] | `{"primary": 0, "stranger": 1, "group": 2}` | Map of sender names to embedding indices |
| `embedding_dim` | int | `8` | Dimensionality of relationship embeddings |
| `default_sender` | string | first key in `known` | Default sender when none specified |

Indices must be sequential starting from 0. Add new relationships by assigning the next index.

## `channels`

List of strings. Each channel gets one slot in the context vector's one-hot encoding.

```yaml
channels:
  - chat
  - voice
  - email
```

Adding or removing channels changes the context vector dimension (`CONTEXT_DIM`). A model trained with one set of channels won't load with a different set — retrain after changing channels.

## `longing`

Controls the absence-based desire growth mechanism.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | bool | `true` | Whether longing is active |
| `growth_rate` | float | `0.02` | Per-hour growth added to target dimensions |
| `cap` | float | `0.3` | Maximum total longing boost |
| `threshold_hours` | float | `2` | Hours of absence before longing kicks in |
| `connection_factor` | float | `0.5` | Secondary dimensions get `boost * factor` |
| `target_dimensions` | list[str] | `["desire"]` | Primary dimensions that grow with longing |
| `secondary_dimensions` | list[str] | `["connection"]` | Dimensions that get a partial boost |

Set `enabled: false` to disable entirely.

## `model`

Architecture hyperparameters. Changing these requires retraining.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `encoder_model` | string | `"all-MiniLM-L6-v2"` | Sentence transformer model name |
| `embed_dim` | int | `384` | Must match encoder output dimensionality |
| `hidden_dim` | int | `128` | GRU hidden state size |
| `head_dim` | int | `64` | Emotion head intermediate layer size |
| `dropout` | float | `0.1` | Dropout rate in emotion head |
| `max_context_chars` | int | `500` | Max characters for recent context window |
| `device` | string | `"cpu"` | PyTorch device. `"cpu"` recommended for Apple Silicon. |

## `training`

Training hyperparameters.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `epochs` | int | `100` | Maximum training epochs |
| `learning_rate` | float | `0.001` | Adam learning rate |
| `batch_size` | int | `16` | Training batch size |
| `weight_decay` | float | `0.01` | AdamW weight decay |
| `grad_clip` | float | `1.0` | Gradient norm clipping threshold |
| `patience` | int | `15` | Early stopping patience (epochs without improvement) |
| `val_split` | float | `0.2` | Fraction of data held out for assessment |

## `state`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `max_trajectory_points` | int | `50` | Rolling window of emotion history snapshots |
| `default_absence_seconds` | int | `28800` | Assumed absence time if no timestamp exists (8 hours) |

## `summary`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `templates_file` | string or null | `null` | Path to YAML summary templates. Null = use built-in defaults. |

## `calibration`

Self-calibrating baseline drift. Disabled by default.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | bool | `false` | Whether self-calibration is active |
| `drift_rate` | float | `0.05` | Blend factor per calibration cycle (0.0-1.0) |
| `min_trajectory_points` | int | `20` | Minimum trajectory points before calibration triggers. Also controls cycle frequency. |
| `clamp_range` | float | `0.15` | Maximum drift from original config baseline per dimension |

When enabled, the baseline slowly shifts toward observed emotional patterns. See `calibration-guide.md` for tuning details.

## `bootstrap`

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `source_files` | list[str] | `["SOUL.md", "IDENTITY.md", "MEMORY.md"]` | Files to extract training passages from |
| `memory_patterns` | list[str] | `["memory/20*.md"]` | Glob patterns for additional source files |
