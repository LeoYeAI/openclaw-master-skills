---
name: personal-finish-notifier
description: Add a simple "Claude has finished." alert to Claude Code or other agent workflows through an OpenClaw-configured transport.
version: 0.1.4
---

# Personal Finish Notifier

Use this skill to wire agent completion events into a simple notification channel.

## Principles

- Treat notifications like a person checking back in, not a machine event log.
- Keep the routing layer engine-agnostic.
- Prefer a user-configured target and transport over hardcoded routing.
- Prefer OpenClaw transports over engine-specific delivery logic.

## Layout

- `scripts/notify.sh` - core formatter + transport adapter
- `scripts/install-claude-hook.sh` - install/update Claude hook wiring
- `scripts/test-openclaw.sh` - send a live self-test through OpenClaw
- `references/architecture.md` - rationale and extension points

## Default setup

For Claude Code on this machine:

```bash
./scripts/install-claude-hook.sh
```

For a live delivery check:

```bash
./scripts/test-openclaw.sh
```

## Inputs

The notifier reads hook JSON from stdin and settings from `~/.claude/mac-notify.env`.

Required routing values:

- `OPENCLAW_NOTIFY_CHANNEL`
- `OPENCLAW_NOTIFY_TARGET`

Optional safety value:

- `OPENCLAW_NOTIFY_SELF_TARGET`

If `OPENCLAW_NOTIFY_SELF_TARGET` is set, the script refuses to send when the target differs.

## Adapters

- Claude Code: `Stop`, `TaskCompleted`
- OpenClaw transport: WhatsApp now
- Future adapters: Codex completion hooks, native node notify, webhook, APNs

## Message style

Human tone rules:

- short
- specific
- reads like a teammate checking back in
- avoid raw event names like `Stop` or `end_turn`

If you need architecture context or to add a new transport, read `references/architecture.md`.
