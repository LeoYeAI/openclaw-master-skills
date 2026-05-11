---
name: gcalcli-calendar
description: "Google Calendar via gcalcli: today-only agenda by default, bounded meaning-first lookup via agenda scans, and fast create/delete with verification--optimized for low tool calls and minimal output."
metadata: {"openclaw":{"emoji":"📅","requires":{"bins":["gcalcli"]}}}
---

# gcalcli-calendar

Use `gcalcli` to read/search/manage Google Calendar with minimal tool calls and minimal output.

## Rules

### CLI flag placement (critical)
- Global flags (`--nocolor`, `--calendar`) go BEFORE the subcommand.
- Subcommand-specific flags go AFTER the subcommand name.
- Example: `gcalcli --nocolor delete --iamaexpert "query" start end` — NOT `gcalcli --nocolor --iamaexpert delete ...`.
- This applies to ALL subcommand flags: `--iamaexpert` (delete), `--noprompt`/`--allday` (add), `--use-legacy-import` (import), etc.

### Output & language
- Don't print CLI commands/flags/tool details unless the user explicitly asks (e.g. "show commands used", "/debug", "/commands").
- If asked for commands: print ALL executed commands in order (including retries) and nothing else.
- Don't mix languages within one reply.
- Be concise. No scope unless nothing found.

### Dates & formatting
- Human-friendly dates by default. ISO only if explicitly requested.
- Don't quote event titles unless needed to disambiguate.

### Calendar scope
- Trust gcalcli config (default/ignore calendars). Don't broaden scope unless user asks "across all calendars" or results are clearly wrong.

### Agenda (today-only by default)
- If user asks "agenda" without a period, return today only.
- Expand only if explicitly asked (tomorrow / next N days / date range).

### Weekday requests (no mental math)
If user says "on Monday/Tuesday/..." without a date:
1) fetch next 14 days agenda once,
2) pick matching day/event from tool output,
3) proceed (or disambiguate if multiple).

### Finding events: prefer deterministic agenda scan (meaning-first)
When locating events to cancel/delete/edit:
- Prefer `agenda` over `search`.
- Use a bounded window and match events by meaning (semantic match) rather than exact text.
- Default locate windows:
  - If user gives an exact date: scan that day only.
  - If user gives a weekday: scan next 14 days.
  - If user gives only meaning words ("train", "lecture", etc.) with no date: scan next 30 days first.
  - If still not found: expand to 180 days and say so only if still empty.

Use gcalcli `search` only as a fallback when:
- the time window would be too large to scan via agenda (token-heavy), or
- the user explicitly asked to "search".

### Search (bounded)
- Default search window: next ~180 days (unless user specified otherwise).
- If no matches: say "No matches in next ~6 months (<from>-><to>)" and offer to expand.
- Show scope only when nothing is found.

### Tool efficiency
- Default: use `--nocolor` to reduce formatting noise and tokens.
- Use `--tsv` only if you must parse/dedupe/sort.

## Actions policy (optimized for conversational speed)

This skill is designed for personal assistant use where the user expects fast, low-friction calendar management. The confirmation policy below is an intentional UX choice — see README.md for rationale and safety guards.

### Unambiguous actions: execute immediately
For cancel/delete/edit actions, skip confirmation when ALL of these hold:
- The user explicitly requested the action (e.g. "delete my dentist appointment").
- Exactly one event matches in a tight time window.
- The match is unambiguous (single clear result on an exact date, or user specified date+time).

### Ambiguous actions: always ask first
If multiple candidates match, or the match is uncertain:
- Ask a short disambiguation question listing the candidates (1-3 lines) and wait for the user's choice.

### Create events: overlap check MUST be cross-calendar (non-ignored scope)
When creating an event:
- Always run a best-effort overlap check across ALL non-ignored calendars by scanning agenda WITHOUT `--calendar`.
  - This ensures overlaps are detected even if the new event is created into a specific calendar.
- If overlap exists with busy events:
  - Ask for confirmation before creating.
- If no overlap:
  - Create immediately.

### Choose the right create method
- **`add`** — default for one-off events. Supports `--allday`, `--reminder`, `--noprompt`. Does NOT support recurrence or free/busy (transparency).
- **`import` via stdin** — use ONLY when you need recurrence (RRULE) or free/busy (TRANSP:TRANSPARENT). Pipe ICS content via stdin; NEVER write temp .ics files (working directory is unreliable in exec sandbox).
- **`quick`** — avoid unless user explicitly asks for natural-language add. Less deterministic.

### Deletes must be verified
- Use non-interactive delete with `--iamaexpert` (a `delete` subcommand flag — goes AFTER `delete`). This is gcalcli's built-in flag for non-interactive/scripted deletion.
- Always verify via agenda in the same tight window after deletion.
- If verification still shows the event, do one retry with `--refresh`.
- Never claim success unless verification confirms the event is gone.

## Canonical commands

### Agenda (deterministic listing)
- Today: `gcalcli --nocolor agenda today tomorrow`
- Next 14d (weekday resolution): `gcalcli --nocolor agenda today +14d`
- Next 30d (meaning-first locate): `gcalcli --nocolor agenda today +30d`
- Custom: `gcalcli --nocolor agenda <start> <end>`

### Search (fallback / explicit request)
- Default (~6 months): `gcalcli --nocolor search "<query>" today +180d`
- Custom: `gcalcli --nocolor search "<query>" <start> <end>`

### Create — `add` (one-off events)
- Overlap preflight (tight, cross-calendar):
  - `gcalcli --nocolor agenda <start> <end>`
  - IMPORTANT: do NOT add `--calendar` here; overlaps must be checked across all non-ignored calendars.
- Timed event:
  - `gcalcli --nocolor --calendar "<Cal>" add --noprompt --title "<Title>" --when "<Start>" --duration <minutes>`
- All-day event:
  - `gcalcli --nocolor --calendar "<Cal>" add --noprompt --allday --title "<Title>" --when "<Date>"`
- With reminders (repeatable flag):
  - `--reminder "20160 popup"` → 14 days before (20160 = 14×24×60)
  - `--reminder "10080 popup"` → 7 days before
  - `--reminder "0 popup"` → at event start
  - Time unit suffixes: `w` (weeks), `d` (days), `h` (hours), `m` (minutes). No suffix = minutes.
  - Method: `popup` (default), `email`, `sms`.

### Create — `import` via stdin (recurrence / free/busy)
Use ONLY when `add` can't cover the need (recurring events, TRANSP, etc.).
Pipe ICS directly via stdin — never write temp files.
```
echo 'BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART;VALUE=DATE:20260308
SUMMARY:Event Title
RRULE:FREQ=YEARLY
TRANSP:TRANSPARENT
END:VEVENT
END:VCALENDAR' | gcalcli import --calendar "<Cal>"
```
- `DTSTART;VALUE=DATE:YYYYMMDD` for all-day; `DTSTART:YYYYMMDDTHHmmSS` for timed.
- `RRULE:FREQ=YEARLY` — yearly recurrence. Also: `DAILY`, `WEEKLY`, `MONTHLY`.
- `TRANSP:TRANSPARENT` — free; `TRANSP:OPAQUE` — busy (default).
- One import call = one event (one VEVENT block). For multiple events, run separate piped imports.
- Add `--reminder "TIME"` flag(s) to set reminders (overrides any VALARM in ICS).
- All import-specific flags (`--use-legacy-import`, `--verbose`, etc.) go AFTER `import`.

### Delete (with post-delete verification)
- Locate via agenda (preferred):
  - `gcalcli --nocolor agenda <dayStart> <dayEnd>` (exact date)
  - `gcalcli --nocolor agenda today +14d` (weekday)
  - `gcalcli --nocolor agenda today +30d` (meaning only)
- Delete (non-interactive, bounded):
  - `gcalcli --nocolor delete --iamaexpert "<query>" <start> <end>`
- Verify (same window):
  - `gcalcli --nocolor agenda <dayStart> <dayEnd>`
- Optional one retry if still present:
  - `gcalcli --nocolor --refresh agenda <dayStart> <dayEnd>`

### Edit / Modify existing events
- `gcalcli edit` is interactive — cannot be used in non-interactive exec.
- To change properties not editable in-place: **delete + recreate** the event.
  - Locate → delete (with `--iamaexpert`) → create with updated properties → verify.
- For bulk property changes (e.g. setting all events to free): iterate delete+recreate per event.
