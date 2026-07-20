---
name: emoclaw
description: "Give your AI emotions that grow from its own memories. Emoclaw builds a unique emotional state that shifts with every conversation, decays between sessions, and evolves over time through self-calibration. Train it on your agent's identity files and watch it develop its own emotional fingerprint."
metadata: {"clawdbot": {"emoji": "\ud83e\udec0"}}
---

# Emotion Skill

Emotions for AI agents — built from memories, shaped by relationships, always changing.

Emoclaw trains a lightweight model on your agent's identity and conversation history, producing a persistent emotional state that evolves with every interaction. Emotions decay naturally between sessions, shift based on who's talking and what's being said, and gradually recalibrate as your agent grows. The result is injected into the system prompt as an `[EMOTIONAL STATE]` block, giving your AI a felt sense of its own inner life.

### How it works

1. **Bootstrap** — `extract.py` reads your agent's identity/memory files. `label.py` scores each passage via the Claude API (opt-in). `train` builds a small neural net from those scores. One-time setup.
2. **Encode** — Each incoming message is turned into a 384-dim vector by a frozen MiniLM sentence encoder. No fine-tuning, no network call — runs from a local cache.
3. **Feel** — The encoding + context (who's talking, what channel, previous emotion) flows through a GRU and MLP head, outputting an N-dimensional emotion vector (0-1 per dimension). The GRU hidden state persists across sessions — this is the "emotional residue" that carries forward mood.
4. **Decay** — Between sessions, each dimension drifts back toward its baseline at a configurable half-life (fast for arousal, slow for safety/groundedness). Time apart = cooling off.
5. **Inject** — The emotion vector is formatted as an `[EMOTIONAL STATE]` block and inserted into the agent's system prompt, giving the AI a felt sense of its own inner state.

> Model is ~2MB, runs on CPU, adds <50ms per message. Network access is only used during bootstrap (opt-in).

## Quick Reference

| Situation | Action |
|-----------|--------|
| First-time setup | `python scripts/setup.py` (or manual steps below) |
| Check current state | `python -m emotion_model.scripts.status` |
| Inject state into prompt | `python -m emotion_model.scripts.inject_state` |
| Start the daemon | `bash scripts/daemon.sh start` |
| Send a message to daemon | See [Daemon Protocol](#daemon-protocol) |
| Retrain after new data | `python -m emotion_model.scripts.train` |
| Resume interrupted training | `python -m emotion_model.scripts.train --resume` |
| Add new training data | Add `.jsonl` entries to `emotion_model/data/`, re-run prepare + train |
| Upgrade from v0.1 | See `references/upgrading.md` |
| Change baselines | Edit `emoclaw.yaml` → `dimensions[].baseline` |
| Add a new channel | Edit `emoclaw.yaml` → `channels` list |
| Add a relationship | Edit `emoclaw.yaml` → `relationships.known` |
| Customize summaries | Create a `summary-templates.yaml` and point config at it |

## Setup

### Quick Setup

```bash
python skills/emoclaw/scripts/setup.py
```

This copies the bundled `emotion_model` engine to your project root, creates a venv, installs the package, and copies the config template. Then edit `emoclaw.yaml` to customize for your agent.

### Manual Setup

If you prefer to set up manually:

#### 1. Install the package

```bash
cd <project-root>
# Copy engine and pyproject.toml from the skill
cp -r skills/emoclaw/engine/emotion_model ./emotion_model
cp skills/emoclaw/engine/pyproject.toml ./pyproject.toml

# Create venv and install
python3 -m venv emotion_model/.venv
source emotion_model/.venv/bin/activate
pip install -e .
```

Required: Python 3.10+, PyTorch, sentence-transformers, PyYAML.

#### 2. Copy and customize the config

```bash
cp skills/emoclaw/assets/emoclaw.yaml ./emoclaw.yaml
```

Edit `emoclaw.yaml` to set:
- `name` — your agent's name
- `dimensions` — emotional dimensions with baselines and decay rates
- `relationships.known` — map of relationship names to embedding indices
- `channels` — communication channels your agent uses
- `longing` — absence-based desire growth (can be disabled)
- `model.device` — `cpu` recommended (MPS has issues with sentence-transformers)

See `references/config-reference.md` for the full schema.

### 3. Bootstrap (new agent)

If starting from scratch with identity/memory files:

```bash
# Extract passages from your identity files
python scripts/extract.py

# Auto-label passages using Claude API (requires ANTHROPIC_API_KEY)
python scripts/label.py

# Prepare train/val split and train
python -m emotion_model.scripts.prepare_dataset
python -m emotion_model.scripts.train
```

Or run the full pipeline:

```bash
python scripts/bootstrap.py
```

### 4. Verify

```bash
python -m emotion_model.scripts.status
python -m emotion_model.scripts.diagnose
```

## Usage

### Option A: Daemon (Recommended)

The daemon loads the model once and listens on a Unix socket, avoiding the ~2s sentence-transformer load time per message.

```bash
# Start
bash scripts/daemon.sh start

# Or directly
python -m emotion_model.daemon
python -m emotion_model.daemon --config path/to/emoclaw.yaml
```

### Option B: Direct Python Import

```python
from emotion_model.inference import EmotionEngine

engine = EmotionEngine(
    model_path="emotion_model/checkpoints/best_model.pt",
    state_path="memory/emotional-state.json",
)

block = engine.process_message(
    message_text="Good morning!",
    sender="alice",        # or None for config default
    channel="chat",        # or None for config default
    recent_context="...",  # optional conversation context
)
print(block)
```

### Option C: One-shot State Injection

For system prompt injection without the daemon:

```bash
python -m emotion_model.scripts.inject_state
```

This reads the persisted state, applies time-based decay, and outputs the `[EMOTIONAL STATE]` block.

## Integration

### System Prompt Injection

Add the output block to your system prompt. The block format:

```
[EMOTIONAL STATE]
Valence: 0.55 (balanced)
Arousal: 0.35 (balanced)
Dominance: 0.50 (balanced)
Safety: 0.70 (open)
Desire: 0.20 (neutral)
Connection: 0.50 (balanced)
Playfulness: 0.40 (balanced)
Curiosity: 0.50 (balanced)
Warmth: 0.45 (balanced)
Tension: 0.20 (relaxed)
Groundedness: 0.60 (balanced)

This feels like: present, alive, between one thing and the next
[/EMOTIONAL STATE]
```

### Daemon Protocol

Send JSON over the Unix socket:

```json
{"text": "Good morning!", "sender": "alice", "channel": "chat"}
```

Special commands:
```json
{"command": "ping"}
{"command": "state"}
```

### Heartbeat Integration

The emotional state decays over time and needs to be refreshed at each session start. Add this entry to your `HEARTBEAT.md`:

```yaml
- task: Refresh emotional state
  schedule: session_start
  run: python skills/emoclaw/scripts/inject_state.py
  inject: system_prompt  # append output as [EMOTIONAL STATE] block
```

Or call the daemon / `inject_state` script from your heartbeat/cron:

```bash
# In your heartbeat script
STATE_BLOCK=$(python -m emotion_model.scripts.inject_state 2>/dev/null)
# Inject $STATE_BLOCK into system prompt
```

**Important:** Without heartbeat integration, the emotional state block will go stale between sessions. The `inject_state` script applies time-based decay and outputs the current state — it must be called at least once per session.

## Architecture

The model processes each message through this pipeline:

```
Message Text ──→ [Frozen MiniLM Encoder] ──→ 384-dim embedding
                                                    │
Conversation Context ──→ [Feature Builder] ──→ context vector
                                                    │
Previous Emotion ──────────────────────────→ emotion vector
                                                    │
                                            ┌───────┴───────┐
                                            │ Input Project  │
                                            │ (Linear+LN+GELU)│
                                            └───────┬───────┘
                                                    │
                                            ┌───────┴───────┐
                                            │     GRU       │
                                            │ (hidden state) │ ← emotional residue
                                            └───────┬───────┘
                                                    │
                                            ┌───────┴───────┐
                                            │ Emotion Head  │
                                            │ (MLP+Sigmoid) │
                                            └───────┬───────┘
                                                    │
                                            N-dim emotion vector [0,1]
```

The GRU hidden state persists across sessions — this is the "emotional residue" that carries forward mood, context, and relational memory.

See `references/architecture.md` for full details.

## Security & Privacy

### Data Flow

1. **Extraction** (`scripts/extract.py`) reads markdown files listed in `emoclaw.yaml` → `bootstrap.source_files` and `bootstrap.memory_patterns`. These are configurable and default to identity/memory files within the repo. Extracted passages are written to `emotion_model/data/extracted_passages.jsonl`.

2. **Redaction** — Before writing, extracted text is passed through configurable regex patterns (`bootstrap.redact_patterns`) that replace API keys, tokens, passwords, and other secrets with `[REDACTED]`. Default patterns cover Anthropic keys, GitHub PATs, bearer tokens, SSH keys, and generic `key=value` credentials. Add custom patterns in `emoclaw.yaml`.

3. **Labeling** (`scripts/label.py`) — **opt-in only**. Sends extracted passages to the Anthropic API for emotional scoring. Requires both `ANTHROPIC_API_KEY` and explicit user consent (interactive prompt before any API call). Use `--yes` to skip the prompt for automation. Use `--dry-run` to preview without any network calls.

4. **Training** runs entirely locally. No data leaves the machine during `prepare_dataset` or `train`.

5. **Inference** runs entirely locally. The daemon and `inject_state` script make no network calls.

### Network Access

Network access is **optional** and limited to a single script:

| Script | Network? | Purpose |
|--------|----------|---------|
| `extract.py` | No | Reads local files only |
| `label.py` | Yes (opt-in) | Sends passages to Anthropic API |
| `prepare_dataset` | No | Local data processing |
| `train` | No | Local model training |
| `daemon` / `inject_state` | No | Local inference |

The sentence-transformers encoder downloads model weights on first use (from Hugging Face). After that, it runs from cache with no network needed.

### File Permissions

| Path | Purpose | Created by |
|------|---------|------------|
| `memory/emotional-state.json` | Persisted emotion vector + trajectory | daemon / inference |
| `emotion_model/data/*.jsonl` | Training data (extracted/labeled passages) | extract.py / label.py |
| `emotion_model/checkpoints/` | Model weights | train script |
| `/tmp/{name}-emotion.sock` | Daemon Unix socket | daemon |

The daemon socket is created with permissions `0o660` (owner + group read/write) and cleaned up on shutdown. The socket path is configurable in `emoclaw.yaml` → `paths.socket_path`.

### Path Validation

`extract.py` validates that every file path resolves to within the repository root before reading. Symlink chains and `../` sequences that would escape the repo boundary are rejected. This prevents a misconfigured `source_files` or `memory_patterns` from reading arbitrary files.

### Configuring Redaction

Add or modify patterns in `emoclaw.yaml`:

```yaml
bootstrap:
  redact_patterns:
    - '(?i)sk-ant-[a-zA-Z0-9_-]{20,}'    # Anthropic API keys
    - '(?i)(?:api[_-]?key|token|secret|password|credential)\s*[:=]\s*\S+'
    - 'your-custom-pattern-here'
```

Set `redact_patterns: []` to disable redaction entirely (not recommended).

### Isolation Recommendations

- Run the bootstrap pipeline (extract → label → train) in an isolated environment or review the source file list before running
- Audit `bootstrap.source_files` and `bootstrap.memory_patterns` in your `emoclaw.yaml` to ensure only intended files are included
- Review `emotion_model/data/extracted_passages.jsonl` before running `label.py` to confirm no sensitive content will be sent externally
- The daemon should run under the same user as your agent process — avoid running as root

## Configuration

All configuration lives in `emoclaw.yaml`. The package falls back to built-in defaults if no YAML is found.

Config search order:
1. `EMOCLAW_CONFIG` environment variable
2. `./emoclaw.yaml` (project root)
3. `./skills/emoclaw/emoclaw.yaml`

Key sections:
- `dimensions` — name, labels, baseline, decay half-life, loss weight
- `relationships` — known senders with embedding indices
- `channels` — communication channels (determines context vector size)
- `longing` — absence-based desire modulation
- `model` — architecture hyperparameters
- `training` — training hyperparameters
- `calibration` — self-calibrating baseline drift (opt-in)

See `references/config-reference.md` for the complete schema.

## Bootstrap Pipeline

### Step 1: Extract Passages

`scripts/extract.py` reads identity and memory files, splitting them into labeled passages:

```bash
python scripts/extract.py
# Output: emotion_model/data/extracted_passages.jsonl
```

Source files are configured in `emoclaw.yaml` → `bootstrap.source_files` and `bootstrap.memory_patterns`.

### Step 2: Auto-Label

`scripts/label.py` uses the Claude API to score each passage on every emotion dimension:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python scripts/label.py
# Output: emotion_model/data/passage_labels.jsonl
```

Each passage gets a 0.0-1.0 score per dimension plus a natural language summary.

### Step 3: Prepare & Train

```bash
python -m emotion_model.scripts.prepare_dataset
python -m emotion_model.scripts.train
```

## Retraining

To add new training data:

1. Add entries to `emotion_model/data/` in JSONL format:
   ```json
   {"text": "message text", "labels": {"valence": 0.7, "arousal": 0.4, ...}}
   ```
2. Re-run the preparation and training:
   ```bash
   python -m emotion_model.scripts.prepare_dataset
   python -m emotion_model.scripts.train
   ```

### Incremental Retraining

The training script saves a rich checkpoint (`training_checkpoint.pt`) that preserves the full optimizer state, learning rate schedule, and early stopping counter. To continue training from where you left off:

```bash
# Resume from the last checkpoint automatically
python -m emotion_model.scripts.train --resume

# Or specify a checkpoint file
python -m emotion_model.scripts.train --resume emotion_model/checkpoints/training_checkpoint.pt
```

This is a true continuation — optimizer momentum, cosine annealing position, and patience counter all pick up exactly where they stopped.

## Growth Model

As the AI accumulates real conversation data:

1. **Passive collection** — Log messages + model predictions
2. **Correction events** — When emotion feels wrong, log the correction
3. **Periodic retraining** — Incorporate new data, retrain
4. **Baseline adjustment** — Baselines may shift as the AI develops

The system is designed to grow with the AI, not remain static.

## Resources

- `references/architecture.md` — Model architecture deep-dive
- `references/config-reference.md` — Full YAML config schema
- `references/dimensions.md` — Emotion dimension documentation
- `references/calibration-guide.md` — Baseline, decay, and self-calibration tuning
- `references/upgrading.md` — Version upgrade guide
- `assets/emoclaw.yaml` — Template config for new AIs
- `assets/summary-templates.yaml` — Generic summary templates
- `assets/example-summary-templates.yaml` — Example personality-specific templates
- `engine/` — Bundled `emotion_model` Python package (copied to project root by setup.py)
