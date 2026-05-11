# gcalcli-calendar

An OpenClaw skill for managing Google Calendar via [gcalcli](https://github.com/insanum/gcalcli).

## What this skill does

Teaches the agent to read, search, create, and delete Google Calendar events using the `gcalcli` CLI. Optimized for low tool calls, minimal token usage, and fast conversational calendar management.

## About gcalcli

[gcalcli](https://github.com/insanum/gcalcli) is a well-established open-source CLI for Google Calendar (5k+ GitHub stars, actively maintained). It authenticates via OAuth2 and stores credentials locally. This skill does not handle authentication — gcalcli must be set up and authenticated before use.

## Prerequisites

- Python 3.6+
- `gcalcli` — install via `pip install gcalcli` or `brew install gcalcli`
- Google Calendar OAuth2 credentials (set up via `gcalcli init` or `gcalcli list` on first run)

## Actions policy — design rationale

**This skill intentionally skips user confirmation for unambiguous destructive actions (delete/edit).** This is a deliberate UX decision, not an oversight. Here's why and how it's kept safe:

### Why skip confirmation?

This skill is designed for personal assistant use via messaging apps (Telegram, WhatsApp, etc.), where:
- The user has already stated their intent explicitly (e.g. "delete my dentist appointment on Thursday").
- An extra "Are you sure?" round-trip adds latency and friction with no real safety benefit when the target is unambiguous.
- The interaction model is conversational — the user's message *is* the confirmation.

### Safety guards in place

The skill does NOT blindly delete. All of these must hold before executing without confirmation:

1. **Explicit user request** — the user must have asked for the action in their message.
2. **Single unambiguous match** — exactly one event matches in a tight, bounded time window.
3. **Post-action verification** — after every delete, the agent verifies via agenda that the event is actually gone. It never claims success without verification.
4. **Disambiguation for ambiguous cases** — if multiple events match, the agent always stops and asks the user to choose before proceeding.
5. **Overlap checks for creates** — before creating events, the agent checks for scheduling conflicts across all calendars and asks for confirmation if an overlap exists.

### If you prefer confirmation for all actions

You can modify the "Actions policy" section in SKILL.md to require confirmation for all destructive actions. Change the "Unambiguous actions" rule to always ask before executing.

## Network access

This skill invokes `gcalcli`, which communicates with:
- `https://www.googleapis.com/calendar/` — Google Calendar API (authenticated via local OAuth2 tokens)
- `https://oauth2.googleapis.com/` — OAuth2 token refresh

No other network access is made. The skill itself makes no HTTP requests — all API communication is handled by gcalcli. OAuth2 credentials are stored locally by gcalcli (typically in `~/.gcalcli_oauth`).

## Commands used

All `gcalcli` commands used by this skill:
- `gcalcli agenda` — list events in a time window (read-only)
- `gcalcli search` — search events by text query (read-only)
- `gcalcli add` — create a one-off event
- `gcalcli import` — create events via ICS (for recurrence/free-busy)
- `gcalcli delete` — delete events (uses `--iamaexpert` flag for non-interactive mode, which is gcalcli's built-in flag for scripted/automated use)

No other commands or subcommands are used. No file system writes are performed (ICS content is piped via stdin, never written to disk).

## License

This skill is MIT licensed. [gcalcli](https://github.com/insanum/gcalcli) is MIT licensed.
