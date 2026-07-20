---
title: Budget Tracking
description: Monitor and control agent costs
---

Ship Loop tracks token usage and estimated costs for every agent invocation. Set limits to prevent runaway spending.

## Configuration

```yaml
budget:
  max_usd_per_segment: 10.0    # Halt if a single segment exceeds this
  max_usd_per_run: 50.0        # Halt if the entire run exceeds this
  max_tokens_per_segment: 500000
  halt_on_breach: true          # false = warn but continue
```

## How Costs Are Estimated

Ship Loop parses token usage from agent output when available. For agents that don't report tokens, it estimates based on:
- Prompt size (input tokens)
- Output length and duration (output tokens)
- Standard pricing models

These are estimates, not exact billing. Check your agent provider's dashboard for actual costs.

## Checking the Budget

```bash
shiploop budget
```

Output:

```
💰 Budget Summary: My App
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total cost:       $3.84
  Budget remaining:  $46.16
  Total records:    8

  By segment:
    dark-mode: $0.42
    contact-form: $3.42
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Budget Enforcement

When `halt_on_breach: true`:
- If a segment exceeds `max_usd_per_segment`, it's marked failed
- If the total run exceeds `max_usd_per_run`, the pipeline stops

When `halt_on_breach: false`:
- A warning is printed but execution continues

## Storage

Budget data is stored in `.shiploop/metrics.json` in your project directory. This file is auto-created and can be deleted to reset tracking.
