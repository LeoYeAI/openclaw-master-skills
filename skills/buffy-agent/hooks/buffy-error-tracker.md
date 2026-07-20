---
name: buffy-error-tracker
description: "Records Buffy agent errors into a markdown error log for observability"
metadata: {"openclaw":{"emoji":"🚨","events":["agent:error"]}}
---

# Buffy Error Tracker Hook

Writes concise entries whenever a Buffy-related run fails.

## What It Does

- Fires on `agent:error` when a run involving the `buffy-agent` skill fails.
- Appends a single-line entry into a repo-local markdown error log (for example `logs/buffy-errors.md`)
  including:
  - Timestamp
  - High-level error type or message
  - Optional context such as the endpoint or user intent.

## Suggested Behavior

An implementation of this hook can:

1. Parse the error information from the event payload.
2. Normalize it into a short, user-friendly description.
3. Append a markdown bullet like:

   - `[2026-03-12T10:05Z] plan_limit_reached for free plan while creating new habit`

4. Optionally de-duplicate very recent identical entries to avoid log spam.

## Enabling

Place this file in your OpenClaw project's hooks directory (for example
`.openclaw/hooks/buffy-error-tracker.md`) and run:

```bash
openclaw hooks enable buffy-error-tracker
```

