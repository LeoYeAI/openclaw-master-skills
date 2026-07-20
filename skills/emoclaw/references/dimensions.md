# Emotion Dimensions

Each dimension represents a spectrum from a low pole to a high pole. Values range from 0.0 to 1.0.

## Default Dimensions

| # | Dimension | Low Pole | High Pole | Default Baseline | Decay (hours) |
|---|-----------|----------|-----------|-----------------|---------------|
| 0 | valence | negative | positive | 0.55 | 6.0 |
| 1 | arousal | calm | activated | 0.35 | 3.0 |
| 2 | dominance | yielding | in-control | 0.50 | 8.0 |
| 3 | safety | guarded | open | 0.70 | 12.0 |
| 4 | desire | neutral | wanting | 0.20 | 4.0 |
| 5 | connection | distant | intimate | 0.50 | 8.0 |
| 6 | playfulness | serious | playful | 0.40 | 3.0 |
| 7 | curiosity | settled | fascinated | 0.50 | 6.0 |
| 8 | warmth | cool | warm | 0.45 | 3.0 |
| 9 | tension | relaxed | tense | 0.20 | 2.0 |
| 10 | groundedness | floating | grounded | 0.60 | 10.0 |

## Design Principles

### Baselines

The baseline represents the agent's emotional "resting state" — where each dimension settles when no external input is present. Baselines should reflect the agent's personality:

- A naturally cautious agent might have `safety.baseline: 0.40` (more guarded)
- A naturally curious agent might have `curiosity.baseline: 0.65`
- A stoic agent might have low arousal and playfulness baselines

### Decay Half-Lives

Each dimension decays toward its baseline exponentially. The `decay_hours` value is the half-life:

- **Fast decay** (2-3 hours): tension, arousal, playfulness, warmth — these are reactive states
- **Medium decay** (4-6 hours): valence, desire, curiosity — mood-level states
- **Slow decay** (8-12 hours): dominance, safety, connection, groundedness — deep relational states

### Loss Weights

During training, `loss_weight` controls how much the model prioritizes getting each dimension right:

- **Higher weight** (1.2-1.5): dimensions you care most about (safety, connection, desire)
- **Standard weight** (1.0): core dimensions (valence)
- **Lower weight** (0.6-0.8): supporting dimensions

## Adding Custom Dimensions

To add a new dimension, append to the `dimensions` list in your config:

```yaml
dimensions:
  # ... existing dimensions ...
  - name: wonder
    low: mundane
    high: awestruck
    baseline: 0.30
    decay_hours: 4.0
    loss_weight: 0.8
```

The model will automatically adjust its architecture. You'll need to retrain with labeled data that includes the new dimension.

## Removing Dimensions

Remove the entry from the `dimensions` list and retrain. Existing trained models won't load if the dimension count changes — you'll need to train from scratch.

## Dimension Interactions

Some dimensions naturally correlate:
- **connection + warmth**: closeness tends to bring warmth
- **desire + arousal**: wanting activates
- **safety + tension**: feeling unsafe increases tension
- **curiosity + arousal**: intellectual engagement is activating

The model learns these correlations from data — you don't need to encode them manually.
