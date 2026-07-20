# Upgrading the Emotion Skill

## v1.0.2 to v1.0.3 — Security & Transparency

Addresses all five items from the OpenClaw registry security review. No breaking changes — this is a drop-in upgrade.

### What Changed

| Concern | Resolution |
|---------|-----------|
| **Undeclared credentials** | `_meta.json` now declares `ANTHROPIC_API_KEY` as optional, with description of when it's needed. |
| **Unconstrained file reads** | `extract.py` validates every path resolves within the repo root before reading. Traversal attempts are rejected with a warning. |
| **No secret redaction** | Extracted passages are filtered through configurable regex patterns before writing to JSONL. Covers API keys, tokens, PATs, SSH keys, and generic credentials by default. |
| **No API consent** | `label.py` shows passage count, character total, and source file list, then requires explicit `y` before any API call. `--yes` flag available for automation. |
| **Missing security docs** | SKILL.md now has a "Security & Privacy" section covering data flow, network access, file permissions, redaction config, and isolation recommendations. |

### Upgrade Steps

**1. Update the skill files**

Copy the updated scripts and config into your installed skill:

```bash
# From your project root
cp skills/emoclaw/scripts/extract.py skills/emoclaw/scripts/extract.py
cp skills/emoclaw/scripts/label.py skills/emoclaw/scripts/label.py
```

Or re-run setup if you prefer a clean install.

**2. Add redact_patterns to your emoclaw.yaml** (optional)

If you have a customized `emoclaw.yaml`, add the new `bootstrap.redact_patterns` section:

```yaml
bootstrap:
  # ... existing source_files and memory_patterns ...
  redact_patterns:
    - '(?i)sk-ant-[a-zA-Z0-9_-]{20,}'
    - '(?i)(?:api[_-]?key|token|secret|password|credential)\s*[:=]\s*\S+'
    - '(?i)bearer\s+[a-zA-Z0-9._~+/=-]+'
    - 'ghp_[a-zA-Z0-9]{36}'
    - '(?i)ssh-(?:rsa|ed25519)\s+\S+'
```

If you don't add these, the built-in defaults apply automatically.

**3. Verify**

```bash
# Confirm path validation works
python scripts/extract.py

# Confirm consent prompt appears
python scripts/label.py --dry-run
```

### Breaking Changes

None. All changes are additive and backward-compatible.

---

## v0.1 to v0.3

v0.3 adds three features: **custom dimensions**, **incremental retraining**, and **self-calibration**. This is a code-only upgrade — your trained model, data, and emotional state are all forward-compatible.

### What Changed

| Area | What's New |
|------|-----------|
| **Dimensions** | Fully dynamic. Add/remove/reorder dimensions in YAML without touching code. |
| **Training** | Rich checkpoints with `--resume`. Picks up exactly where you stopped. |
| **Calibration** | Opt-in baseline drift toward observed emotional patterns. |
| **Config** | Two new sections: `calibration` and `training.patience`/`training.val_split`. |
| **State format** | Still v2. Migration handles dimension changes automatically. |

### Upgrade Steps

**1. Pull the updated code**

```bash
git pull   # or however you sync your repo
```

**2. Update your `emoclaw.yaml`**

Add the new `calibration` section (you can copy from the template):

```yaml
# Add this anywhere in your emoclaw.yaml
calibration:
  enabled: false              # Leave disabled until you're ready
  drift_rate: 0.05
  min_trajectory_points: 20
  clamp_range: 0.15
```

The `training` section now supports two additional fields (these have sensible defaults, so adding them is optional):

```yaml
training:
  # ... your existing training config ...
  patience: 15              # Early stopping patience (was hardcoded)
  val_split: 0.2            # Validation split fraction (was hardcoded)
```

If you don't add these, the built-in defaults apply automatically. **No action required.**

**3. Verify your installation**

```bash
source emotion_model/.venv/bin/activate

# Run the test suite — should be 26 tests now
PYTHONPATH=. python -m pytest emotion_model/tests/ -v

# Run diagnostics
PYTHONPATH=. python -m emotion_model.scripts.diagnose
```

**4. That's it.**

Your existing `best_model.pt`, `rel_embeddings.pt`, training data, and emotional state file all work unchanged.

### What You Can Now Do

#### Resume Training

If you add new labeled data and want to continue training from where you left off:

```bash
# First time after upgrade — train normally (creates training_checkpoint.pt)
python -m emotion_model.scripts.train

# Later, after adding more data — resume from last checkpoint
python -m emotion_model.scripts.train --resume

# Or resume from a specific checkpoint file
python -m emotion_model.scripts.train --resume path/to/training_checkpoint.pt
```

The `--resume` flag restores everything: model weights, optimizer momentum, learning rate schedule, early stopping counter. This is a true continuation, not fine-tuning from scratch.

**Note:** Your first training run after the upgrade won't have a `training_checkpoint.pt` yet (the old training script didn't create one). Just run a normal training first, and future runs can resume.

#### Enable Self-Calibration

Once you have a stable model and enough conversation data:

```yaml
calibration:
  enabled: true
  drift_rate: 0.05            # 5% blend per cycle
  min_trajectory_points: 20   # Recalibrate every 20 messages
  clamp_range: 0.15           # Baseline can drift +/- 0.15 from config
```

This lets your emotional baseline slowly adapt. See `references/calibration-guide.md` for tuning details.

#### Custom Dimensions

To add a new dimension, just add it to your YAML:

```yaml
dimensions:
  # ... existing dimensions ...
  - name: wonder
    low: mundane
    high: awestruck
    baseline: 0.35
    decay_hours: 4.0
    loss_weight: 0.8
```

Then **retrain** — the model architecture adjusts automatically, but needs new weights for the extra output dimension:

```bash
python -m emotion_model.scripts.prepare_dataset
python -m emotion_model.scripts.train
```

Your existing state file and trajectory will be migrated automatically (new dimensions get padded with the baseline value).

### Breaking Changes

None. Everything is backward-compatible:

- State v2 format is unchanged
- Existing checkpoints load without issues
- Config YAML is additive (new sections have defaults)
- API is identical (`EmotionEngine.process_message()`)

### Compatibility Notes

| Scenario | Compatible? | Action Needed |
|----------|-------------|---------------|
| Existing model + same dimensions | Yes | Nothing |
| Existing model + new dimensions added | Partial | Must retrain (model output size changed) |
| Existing model + dimensions removed | Partial | Must retrain |
| Existing model + dimensions reordered | Partial | Must retrain |
| Existing state file + dimension change | Yes | Auto-migrated on load |
| Existing training data + dimension change | No | Must relabel (vectors have wrong length) |
| Existing `emoclaw.yaml` + no changes | Yes | New config sections use defaults |

### Troubleshooting

**"Checkpoint was trained with N dimensions but current config has M"**
You changed dimensions without retraining. Run `python -m emotion_model.scripts.train` to train a new model.

**"No training checkpoint found, training from scratch"**
Expected on first run after upgrade. The old training script didn't create `training_checkpoint.pt`. After this training run completes, `--resume` will work.

**Tests fail with import errors**
Make sure you're using the venv: `source emotion_model/.venv/bin/activate`
