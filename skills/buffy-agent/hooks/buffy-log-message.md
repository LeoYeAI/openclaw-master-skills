---
name: buffy-log-message
description: "Logs Buffy agent conversations to a markdown observability log after each message"
metadata: {"openclaw":{"emoji":"📓","events":["agent:post-message"]}}
---

# Buffy Log Message Hook

Captures brief Buffy conversation snippets for observability after each message.

## What It Does

- Fires on `agent:post-message` after the `buffy-agent` skill has replied.
- Appends a short entry to a markdown log file (for example `logs/buffy-conversations.md`)
  including:
  - Timestamp
  - User message (truncated if very long)
  - Buffy reply (truncated)
  - Optional tags such as `#habit`, `#task`, or `#bug`.

## Suggested Behavior

An implementation of this hook can:

1. Inspect the event payload to extract:
   - The user message text.
   - The Buffy reply text.
2. Construct a markdown entry such as:

   - `[2026-03-12T10:00Z] user: "Remind me to drink water" → buffy: "Created a habit …" #habit`

3. Append it to `logs/buffy-conversations.md` (creating the file and `logs/` directory if they do not exist).

## Privacy / compliance

Enabling this hook persists user message and reply content to repo-local files. Integrators should ensure this complies with their privacy and retention policies and that log location and access are controlled.
