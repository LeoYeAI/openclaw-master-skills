---
name: nextcloud-aio-oc (NextCloud AIO OpenClaw)
description: Reliable Nextcloud integration for Notes, Tasks, Calendar, Files, and Contacts (CardDAV-safe vCard handling with robust contact create/update).
license: MIT
compatibility: Requires Node.js 20+. Needs network access to Nextcloud instance.
required-binaries:
  - node>=20
required-env-vars:
  - NEXTCLOUD_URL
  - NEXTCLOUD_USER
  - NEXTCLOUD_TOKEN
optional-env-vars:
  - NEXTCLOUD_TIMEZONE
requiredBinaries:
  - node
requiredEnv:
  - NEXTCLOUD_URL
  - NEXTCLOUD_USER
  - NEXTCLOUD_TOKEN
optionalEnv:
  - NEXTCLOUD_TIMEZONE
primaryEnv: NEXTCLOUD_TOKEN
allowed-tools: Bash Read
---

# NextCloud AIO OpenClaw Skill

This skill connects OpenClaw to Nextcloud for:
- Notes API
- CalDAV Tasks and Events
- WebDAV Files
- CardDAV Contacts

Primary goal: Predictable, loss-resistant Nextcloud reads/writes.

This skill is validated against:
- Nextcloud Hub 25 Autumn (`32.0.6`)
- OpenClaw (`2026.3.2`)

## Required Configuration

Set these environment variables:
- `NEXTCLOUD_URL` (example: `https://cloud.example.com`)
- `NEXTCLOUD_USER`
- `NEXTCLOUD_TOKEN` (App Password strongly preferred)
- `NEXTCLOUD_TIMEZONE` (recommended, IANA timezone like `America/Los_Angeles`; used for timezone-less date/time inputs)

## Runtime and Metadata Contract

This section is the source of truth for registry metadata parity.

- Required binary: `node` (Node.js `20+`)
- Required environment variables: `NEXTCLOUD_URL`, `NEXTCLOUD_USER`, `NEXTCLOUD_TOKEN`
- Optional environment variable: `NEXTCLOUD_TIMEZONE`
- Required network target: the host defined by `NEXTCLOUD_URL` (plus normal redirects from that host)

If a registry entry says "no required binaries" or "no required env vars", treat it as stale metadata and fix before publishing.

## Preflight Audit Gate

Before first execution in any new environment:

- Complete the bundled script review checklist below.
- Confirm no unexpected endpoints or privileged system calls are present.
- If checks are incomplete, do not run the skill.
- Prefer sandbox/container validation and least-privilege app credentials first.

## Security and Publish Safety

- Never hardcode credentials in `SKILL.md`, scripts, examples, commit messages, or changelog text.
- Store secrets only in environment variables or local secret stores.
- Use dedicated app passwords for integrations; rotate if leaked or shared.
- Keep local `.env` files out of git (see `.gitignore`).
- Before publishing, run a quick scan for obvious secrets and remove any accidental values.

## Bundled Script Review Checklist (Before First Use)

The skill ships two scripts: `scripts/nextcloud.js` (Node.js, text operations) and `scripts/files_binary.py` (Python 3, binary file transfers). Review both before running in new environments:

1. Confirm runtime requirements:
   - `node --version` (must be `20+`)
2. Check obvious outbound endpoints:
   - `rg -n "https?://" scripts/nextcloud.js`
3. Check sensitive capability usage:
   - `rg -n "child_process|spawn\\(|exec\\(|require\\(\"fs\"\\)|require\\('fs'\\)|fs\\." scripts/nextcloud.js`
4. Verify credentials are env-driven only:
   - `rg -n "NEXTCLOUD_URL|NEXTCLOUD_USER|NEXTCLOUD_TOKEN|NEXTCLOUD_TIMEZONE" scripts/nextcloud.js`
5. Run in low-risk mode first:
   - Use a dedicated low-privilege Nextcloud app password
   - Test against non-production data when possible

If review confidence is low, do not run until code is reviewed by a trusted maintainer.

### Static audit snapshot (current bundle)

Quick grep-style checks on `scripts/nextcloud.js` should currently show:

- Config is read from `process.env.NEXTCLOUD_URL|USER|TOKEN|TIMEZONE`.
- Request path is built as `${CONFIG.url}${endpoint}` and uses `fetch(...)`.
- No obvious `child_process` or `fs` usage in the bundle entry path.

Quick checks on `scripts/files_binary.py`:

- Config is read from `os.environ.get("NEXTCLOUD_URL|USER|TOKEN")`.
- DAV URL is built as `{url}/remote.php/dav/files/{user}/{path}`.
- Uses only stdlib (`urllib`, `base64`, `xml.etree`); no third-party deps.

This is not a full security audit. Re-run checks after every bundle update.

## Run

```bash
node scripts/nextcloud.js <command> <subcommand> [options]
```

## Commands

### Notes
- `notes list`
- `notes get --id <id>`
- `notes create --title <title> --content <content> [--category <category>]`
- `notes edit --id <id> [--title <title>] [--content <content>] [--category <category>]`
- `notes delete --id <id>`

### Tasks
- `tasks list [--calendar <calendar-name>]`
- `tasks create --title <title> [--calendar <calendar-name>] [--due <iso>] [--priority <0-9>] [--description <text>] [--timezone <IANA>]`
- `tasks edit --uid <uid> [--calendar <calendar-name>] [--title <title>] [--due <iso>] [--priority <0-9>] [--description <text>] [--timezone <IANA>]`
- `tasks delete --uid <uid> [--calendar <calendar-name>]`
- `tasks complete --uid <uid> [--calendar <calendar-name>]`

### Calendar Events
- `calendar list [--from <iso>] [--to <iso>]` (default: next 7 days)
- `calendar create --summary <summary> --start <iso-or-date> --end <iso-or-date> [--calendar <calendar-name>] [--description <text>] [--timezone <IANA>] [--all-day]`
- `calendar edit --uid <uid> [--calendar <calendar-name>] [--summary <summary>] [--start <iso-or-date>] [--end <iso-or-date>] [--description <text>] [--timezone <IANA>] [--all-day]`
- `calendar delete --uid <uid> [--calendar <calendar-name>]`

Important:
- In many setups, `Contact birthdays` appears as an events calendar but is read-only.
- Birthdays must be managed through `contacts create/edit --birthday ...`, not through `calendar create/edit`.
- `calendar list` returns event `summary`, `start`, `end`, and may include `location` and `description` when present.

### Calendar Discovery
- `calendars list [--type <tasks|events>]`

### Files (text)
- `files list [--path <path>]`
- `files search --query <query>` (supports natural-language input; ranks by filename/path token relevance)
- `files get --path <path>` (accepts relative user path or full DAV href)
- `files upload --path <path> --content <content>`
- `files delete --path <path>`

### Files (binary) — ODT, DOCX, PDF, images, etc.

`nextcloud.js` passes file content as text strings, which corrupts binary formats.
Use the companion Python script for any binary file:

```bash
python3 scripts/files_binary.py download <nc_path> <local_path>
python3 scripts/files_binary.py upload   <local_path> <nc_path>
python3 scripts/files_binary.py exists   <nc_path>
python3 scripts/files_binary.py list     [<nc_path>]
```

Reads the same `NEXTCLOUD_URL`, `NEXTCLOUD_USER`, `NEXTCLOUD_TOKEN` env vars.
Auto-detects MIME type from file extension (ODT, DOCX, XLSX, PDF, PNG, JPG, and more).

**When to use which:**

| Situation | Command |
|-----------|---------|
| Plain text files (`.md`, `.txt`, `.csv`) | `node scripts/nextcloud.js files get/upload` |
| Binary files (`.odt`, `.docx`, `.pdf`, images) | `python3 scripts/files_binary.py download/upload` |

### Contacts
- `contacts list [--addressbook <name>]`
- `contacts get --uid <uid> [--addressbook <name>]`
- `contacts search --query <query> [--addressbook <name>]`
- `contacts create [--name <full-name>] [--first-name <given>] [--last-name <family>] [--middle-name <middle>] [--prefix <prefix>] [--suffix <suffix>] [--addressbook <name>] [--email <single>] [--emails <csv>] [--phone <single>] [--phones <csv>] [--organization <org>] [--title <title>] [--note <note>] [--birthday <YYYY-MM-DD|YYYYMMDD|--MM-DD|--MMDD>]`
- `contacts edit --uid <uid> [--addressbook <name>] [--name <full-name>] [--first-name <given>] [--last-name <family>] [--middle-name <middle>] [--prefix <prefix>] [--suffix <suffix>] [--email <single>] [--emails <csv>] [--phone <single>] [--phones <csv>] [--organization <org>] [--title <title>] [--note <note>] [--birthday <YYYY-MM-DD|YYYYMMDD|--MM-DD|--MMDD>]`
- `contacts delete --uid <uid> [--addressbook <name>]`

### Address Book Discovery
- `addressbooks list`

## Contact Data Contract (Important)

Use `fullName` and `structuredName` as canonical name fields.

Contact output includes:
- `uid`
- `addressBook`
- `fullName`
- `structuredName` with:
  - `familyName`
  - `givenName`
  - `additionalNames`
  - `honorificPrefixes`
  - `honorificSuffixes`
- `nameRaw` (raw `N` value for diagnostics only; do not display to users by default)
- `emails` array or `null`
- `phones` array or `null`
- `organization`, `title`, `note`
- `birthday` normalized for readability (`YYYY-MM-DD` or `--MM-DD` when possible)
- `birthdayRaw` (raw CardDAV value)

## Reliability Rules (Quick Reference)

Apply these on every write to prevent corruption and confusion:

1) Identity and naming
- Never infer `UID` from URL; always use payload `uid`.
- Use `fullName` and `structuredName` for user-facing names; keep `nameRaw` diagnostic-only.

2) Contact and birthday integrity
- Birthday input formats: `YYYY-MM-DD`, `YYYYMMDD`, `--MM-DD`, `--MMDD`.
- Never add trailing semicolons to `BDAY`.
- Birthdays are contact fields: use `contacts create/edit --birthday ...`; never edit birthday-derived calendar entries directly.

3) Intent-preserving updates
- Modify only fields explicitly requested by the user.
- To clear a value, pass explicit empty values.
- Respect explicit `--addressbook`; otherwise use remembered default or ask once.

4) Calendar and task validation
- Validate date/datetime inputs before sending; require `end > start` for timed events.
- Escape ICS text fields (`SUMMARY`, `DESCRIPTION`).
- Validate task priority range (`0..9`).
- For timezone-less timed input, use `--timezone` or `NEXTCLOUD_TIMEZONE`.
- For all-day events, use `VALUE=DATE` semantics with exclusive `DTEND`.

5) Capability and safety checks
- Do not assume listed event calendars are writable.
- Treat `Contact birthdays` as read-only/system calendar.
- If no writable event calendar exists, explain event mutation is unavailable until writable access exists.
- Some calendars are multi-component (`VEVENT` + `VTODO`); keep them eligible for both event/task flows.

6) Files and post-write verification
- Require non-empty file paths for `files upload/get/delete`.
- Escape XML filter/search values for CardDAV/WebDAV operations.
- After mutations (`create`, `edit`, `complete`, `delete`), verify with follow-up read/list when practical.
- For propagation delay, retry around `0.5s`, `1s`, `2s` before declaring failure.

## Known Nextcloud/CardDAV Behaviors

- Servers/clients may negotiate or normalize vCard versions (`3.0` vs `4.0`) and content on write/read.
- `FN` and `N` should each appear once in valid contacts.
- `BDAY` failures are often malformed input (for example stray delimiters), not server instability.
- Folded vCard lines must be unfolded before parsing.

## Error to Action Map (Fast)

- `HTTP 403` on `calendar create/edit/delete` -> likely read-only/system calendar or missing permission; switch to writable events calendar.
- `HTTP 501` on `files search` -> WebDAV `SEARCH` unsupported; fallback to recursive `PROPFIND` + client-side filter.
- `HTTP 415` on task/event update -> malformed ICS payload; normalize formatting and retry once.
- Contact write succeeded but UI still stale -> run verification retry cycle before reporting failure.

## Agent Behavior: Default Calendar Selection

When user creates tasks/events without explicit calendar:
1. Run `calendars list --type tasks` or `calendars list --type events`.
2. For `events`, filter out likely read-only calendars first (`Contact birthdays`, `Holidays`, names containing `read only` or `readonly`).
3. If at least one writable calendar remains, ask for selection.
4. Ask whether to remember as default.
5. Store in memory.
6. If no writable events calendar remains, explain why event mutation is unavailable and suggest creating a writable calendar in Nextcloud Calendar.

Memory keys:
- `default_task_calendar`
- `default_event_calendar`

## Agent Behavior: Default Address Book Selection

When user creates contacts without explicit address book:
1. Run `addressbooks list`.
2. Ask for selection.
3. Ask whether to remember default.
4. Store in memory.

Memory key:
- `default_addressbook`

## Agent Behavior Playbooks (Condensed)

These playbooks are execution shortcuts. Reliability and safety rules above still apply.

### Contacts and Birthdays
1. Resolve address book (`--addressbook` or remembered default).
2. For create/edit, pass only user-requested fields; use explicit empty values when user wants fields cleared.
3. Use `--name` for full-name input; use structured-name flags for split-name input.
4. Pass multiple emails/phones as CSV values.
5. Birthday changes always go through contacts (`contacts create/edit --birthday ...`), never calendar mutation commands.
6. Verify birthday/name-sensitive writes with `contacts get --uid ...` when confidence is important.

### Tasks
1. Resolve task calendar when omitted.
2. Validate due and priority (`0..9`) before write.
3. After create/edit/complete/delete, verify via focused list/get when practical.

### Calendar Events
1. Resolve writable events calendar; treat `Contact birthdays` and system calendars as read-only.
2. Validate `start`/`end` and require `end > start` for timed events.
3. For timezone-less date-times, pass `--timezone` or use `NEXTCLOUD_TIMEZONE`.
4. For all-day intent, use `--all-day` with date values (not timed midnight ranges).
5. Re-list in a focused window after mutation when confidence is important.

All-day end-date normalization behavior:
- `start=YYYY-MM-DD`, `end=YYYY-MM-DD` -> inclusive single-day input, normalized.
- `start=YYYY-MM-DD`, `end=next-day` -> already-exclusive single-day input.
- Multi-day inclusive ranges -> normalized to canonical exclusive `DTEND`.

### Appointment briefing workflow (high priority intent)
Use this when user asks for appointment details, address, or "what is my appointment today":
1. Determine "today" in `NEXTCLOUD_TIMEZONE` (or ask if timezone is unclear).
2. Run `calendar list --from <start-of-day-iso> --to <end-of-day-iso>`.
3. Filter events by user terms (for example `dermatology`, `doctor`, provider name).
4. For the selected event, include `summary`, time window, `location`, and key lines from `description`.
5. If multiple events match, ask a quick disambiguation question.
6. If none match, clearly say none found for today and offer to check tomorrow or full week.
7. Provide a plain-text message suitable for SMS/chat (short lines, no markdown).

### Files
1. Require explicit file path for mutating operations.
2. `files get/upload/delete` accept either a relative user path (for example `/Share-Family/file.docx`) or a full DAV href returned by search.
3. For binary files (ODT, DOCX, PDF, images), use `python3 scripts/files_binary.py` — never pass binary content through `nextcloud.js files upload`.
4. Use deterministic test paths for temporary validation files.
5. Read back uploaded content and then delete test files.
6. Use `files search` with user phrasing directly; it auto-normalizes query text and ranks likely matches.
7. On large instances, prefer narrower path-based listing before broad search to reduce load.

### Notes
1. Create with explicit title/content.
2. Read back by id after create/edit.
3. Delete temporary test notes after verification.

## Internal Smoke Test Protocol

When validating this skill in a live environment:
1. Contacts: create -> get -> edit -> get -> optional delete.
2. Notes: create -> get -> edit -> get -> delete.
3. Files: upload -> get -> search/list -> delete.
4. Tasks: create -> list/locate -> edit -> complete -> delete.
5. Calendar: create -> list/locate -> edit -> delete.

Use a unique timestamped suffix on all test data and clean up all temporary artifacts unless the user requests keeping them.
Use least-privilege credentials for tests and monitor outbound traffic; the process should only communicate with `NEXTCLOUD_URL`.

Calendar exception handling:
- If no writable event calendar exists, mark calendar mutation tests as intentionally skipped (environment limitation), and still run `calendar list`.
- Do not treat this as a skill failure; treat it as a server capability/permission constraint.

## Persistent Rules (Store These)

Persist these high-value rules in memory/rules:

1. Birthdays are contact fields: use `contacts create/edit --birthday ...`; never mutate `Contact birthdays` directly.
2. For all-day events, always use `calendar create/edit --all-day` with date values (avoid timed midnight ranges).
3. For timezone-less timed values, use `--timezone` or `NEXTCLOUD_TIMEZONE`; ask if timezone is unknown.
4. Prefer writable user calendars for event mutations; if `403`, report likely read-only/permission issue.
5. Verify event/contact writes with a focused read/list before declaring final success.
6. Keep canonical all-day encoding (`VALUE=DATE`); avoid duplicate compatibility events unless explicitly requested.

## Troubleshooting Playbook

- Birthday was updated but not visible in Nextcloud UI yet:
  - Run `contacts get --uid ...` immediately.
  - If value is correct in API, advise short wait + UI refresh.
  - Re-check after retry intervals before escalating.

- `contacts get` and `contacts search` disagree briefly:
  - Prefer retry cycle and then trust latest consistent result.
  - Do not create duplicate contact entries while waiting.

- Event creation keeps failing:
  - Run `calendars list --type events` and verify at least one writable non-system calendar exists.
  - If only birthday/system calendars exist, explain limitation and stop mutation attempts.

## Output Envelope

All commands return JSON:

Success:
```json
{
  "status": "success",
  "data": {}
}
```

Error:
```json
{
  "status": "error",
  "message": "Error description"
}
```
