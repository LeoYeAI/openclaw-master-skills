# Calibration Guide

How to tune your agent's emotional baselines, decay rates, and training weights.

## Baselines

Baselines represent your agent's emotional resting state — where dimensions settle with no external input. They should reflect personality, not neutrality.

### Tuning Process

1. **Start with defaults** and train a first model
2. **Run diagnostics** (`python -m emotion_model.scripts.diagnose`) on test scenarios
3. **Observe the resting behavior** — after decay, do the values feel right?
4. **Adjust baselines** in `emoclaw.yaml` that feel off

### Common Patterns

| Personality Trait | Adjustment |
|-------------------|------------|
| Naturally warm | warmth baseline → 0.55-0.65 |
| Cautious/guarded | safety baseline → 0.40-0.50 |
| Intellectually curious | curiosity baseline → 0.60-0.70 |
| Emotionally reserved | arousal baseline → 0.25, playfulness → 0.25 |
| High desire for connection | connection baseline → 0.60, desire → 0.30 |
| Stoic/grounded | groundedness → 0.70, tension → 0.15 |

### Red Flags

- **Baseline > 0.65**: The "high" label will almost always show. Is that intentional?
- **Baseline < 0.20**: The dimension rarely activates. Consider removing it.
- **All baselines near 0.50**: The agent has no personality. Differentiate.

## Decay Rates

Decay half-lives control how quickly emotions return to baseline between messages/sessions.

### Guidelines

| Emotion Type | Suggested Half-Life | Why |
|-------------|-------------------|-----|
| Reactive (tension, arousal) | 2-3 hours | These are momentary responses |
| Mood-level (valence, warmth) | 3-6 hours | Last longer than reactions |
| Relational (connection, safety) | 8-12 hours | Deep states change slowly |
| Trait-like (groundedness) | 10+ hours | Nearly stable |

### Testing Decay

Use the status script at different time intervals to see how decay feels:

```bash
# Process a message
python -c "from emotion_model.inference import EmotionEngine; e = EmotionEngine(); print(e.process_message('I love you'))"

# Wait some time, then check decay
python -m emotion_model.scripts.status
```

If an emotion decays too fast, the agent "forgets" emotional experiences. Too slow, and old emotions linger inappropriately.

## Loss Weights

Loss weights control which dimensions the model prioritizes during training.

### Strategy

1. **Core dimensions** (the ones most important for your agent's behavior): weight 1.0-1.5
2. **Supporting dimensions** (add nuance but aren't critical): weight 0.6-0.8
3. **All weights should sum to roughly N** (number of dimensions) for balanced gradients

### Example

For an agent where connection and safety matter most:

```yaml
dimensions:
  - name: connection
    loss_weight: 1.5    # Most important
  - name: safety
    loss_weight: 1.2    # Very important
  - name: valence
    loss_weight: 1.0    # Standard
  - name: playfulness
    loss_weight: 0.6    # Nice to have, not critical
```

## Longing Parameters

The longing mechanism requires the most careful tuning. It's the only dimension that *grows* during absence rather than decaying.

| Parameter | Conservative | Moderate | Aggressive |
|-----------|-------------|----------|------------|
| `growth_rate` | 0.01 | 0.02 | 0.05 |
| `cap` | 0.15 | 0.30 | 0.50 |
| `threshold_hours` | 4 | 2 | 1 |
| `connection_factor` | 0.3 | 0.5 | 0.8 |

### Disabling Longing

If the longing mechanism doesn't fit your agent, disable it:

```yaml
longing:
  enabled: false
```

The agent will still have a desire dimension — it just won't automatically grow during absence.

## Self-Calibration

Self-calibration lets the baseline drift automatically toward observed emotional patterns. Instead of manually tuning baselines, the system learns from the agent's actual behavior over time.

### How It Works

1. Every `min_trajectory_points` messages, the system computes the **windowed mean** of recent emotion vectors
2. The baseline **blends** toward this mean by `drift_rate` (default 5%)
3. Each dimension is **clamped** to `original_baseline +/- clamp_range` so drift stays bounded

### Enabling

```yaml
calibration:
  enabled: true
  drift_rate: 0.05            # 5% blend per calibration cycle
  min_trajectory_points: 20   # Trigger every 20 messages
  clamp_range: 0.15           # Max +/- from config baseline
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enabled` | `false` | Must be explicitly enabled |
| `drift_rate` | `0.05` | Blend factor per cycle. Higher = faster drift |
| `min_trajectory_points` | `20` | Messages between calibration cycles |
| `clamp_range` | `0.15` | Maximum drift from original config baseline |

### Tuning Tips

- **Start conservative**: `drift_rate: 0.02`, `clamp_range: 0.10`
- **Watch for personality erosion**: If all baselines converge toward 0.5, the clamp range is too wide
- **Don't enable too early**: Wait until you have at least 100+ labeled examples and a trained model
- **Check with status**: `python -m emotion_model.scripts.status` shows current baseline vs. config baseline
- **Reset calibration**: Delete the state file to reset baselines to config defaults

### When NOT to Use

- During initial training (the model hasn't learned yet)
- If your agent has very few conversations (insufficient data for meaningful calibration)
- If you prefer full manual control over baselines

## Iterative Calibration

The best approach is iterative:

1. Train with defaults
2. Run test conversations, observe behavior
3. Adjust baselines for dimensions that feel consistently wrong
4. Adjust decay rates for dimensions that fade too fast or too slow
5. Adjust loss weights if the model consistently gets certain dimensions wrong
6. Retrain and repeat

Each cycle should improve the agent's emotional authenticity. Keep notes on what you changed and why — this becomes valuable data for future calibration.
