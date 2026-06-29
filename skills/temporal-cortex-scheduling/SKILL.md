---
name: temporal-cortex-scheduling
description: |-
  List events, find free slots, and book meetings across Google Calendar, Outlook, and CalDAV. Multi-calendar availability merging, recurring event expansion, and atomic booking with Two-Phase Commit conflict prevention.
license: MIT
compatibility: |-
  Requires npx (Node.js 18+) or Docker for the MCP server. Stores OAuth credentials at ~/.config/temporal-cortex/. Works with Claude Code, Claude Desktop, Cursor, Windsurf, and any MCP-compatible client.
metadata:
  author: temporal-cortex
  version: "0.9.1"
  mcp-server: "@temporal-cortex/cortex-mcp"
  homepage: "https://temporal-cortex.com"
  repository: "https://github.com/temporal-cortex/skills"
  openclaw:
    install:
      - kind: node
        package: "@temporal-cortex/cortex-mcp@0.9.1"
        bins: [cortex-mcp]
    requires:
      bins:
        - npx
      config:
        - ~/.config/temporal-cortex/credentials.json
        - ~/.config/temporal-cortex/config.json
---

# Calendar Scheduling & Booking

14 tools (Layers 0, 2–4) for contact resolution, calendar discovery, event querying, free slot finding, availability checking, RRULE expansion, atomic booking, Open Scheduling, and proposal composition. 12 read-only tools + 2 write tools (`book_slot`, `request_booking`).

## Source & Provenance

- **Homepage:** [temporal-cortex.com](https://temporal-cortex.com)
- **Source code:** [github.com/temporal-cortex/mcp](https://github.com/temporal-cortex/mcp) (open-source Rust)
- **npm package:** [@temporal-cortex/cortex-mcp](https://www.npmjs.com/package/@temporal-cortex/cortex-mcp)
- **Skills repo:** [github.com/temporal-cortex/skills](https://github.com/temporal-cortex/skills)

## Runtime

These tools run inside the [Temporal Cortex MCP server](https://github.com/temporal-cortex/mcp) (`@temporal-cortex/cortex-mcp`), a compiled Rust binary distributed as an npm package.

**Install and startup lifecycle:**
1. `npx` resolves `@temporal-cortex/cortex-mcp` from the npm registry (one-time, cached locally after first download)
2. The postinstall script downloads the platform-specific binary from the [GitHub Release](https://github.com/temporal-cortex/mcp/releases/tag/mcp-v0.9.1) and verifies its SHA256 checksum against the embedded `checksums.json` — **installation halts on mismatch**
3. The MCP server starts as a local process communicating over stdio (no listening ports)
4. Calendar tools make authenticated API calls to your configured providers (Google Calendar API, Microsoft Graph API, CalDAV endpoints)

**Credential storage:** OAuth tokens are stored locally at `~/.config/temporal-cortex/credentials.json` and read exclusively by the local MCP server process. No credential data is transmitted to Temporal Cortex servers. The binary's filesystem access is limited to `~/.config/temporal-cortex/` — verifiable by inspecting the [open-source Rust code](https://github.com/temporal-cortex/mcp) or running under Docker where the mount is the only writable path.

**File access:** The binary reads and writes only `~/.config/temporal-cortex/` (credentials and config). No other filesystem writes.

**Network scope:** Calendar tools connect only to your configured providers (`googleapis.com`, `graph.microsoft.com`, or your CalDAV server). In Local Mode (default), no calls to Temporal Cortex servers and no telemetry is collected. In Platform Mode, three tools (`resolve_identity`, `query_public_availability`, `request_booking`) call `api.temporal-cortex.com` for cross-user scheduling — no credential data is included in these calls.

**Pre-run verification** (recommended before first use):
1. Inspect the npm package without executing: `npm pack @temporal-cortex/cortex-mcp --dry-run`
2. Verify checksums independently against the [GitHub Release](https://github.com/temporal-cortex/mcp/releases/download/mcp-v0.9.1/SHA256SUMS.txt) (see verification pipeline below)
3. For full containment, run in Docker instead of npx (see Docker containment below)

**Verification pipeline:** Checksums are published independently at each [GitHub Release](https://github.com/temporal-cortex/mcp/releases/tag/mcp-v0.9.1) as `SHA256SUMS.txt` — verify the binary before first use:

```bash
# 1. Fetch checksums from GitHub (independent of the npm package)
curl -sL https://github.com/temporal-cortex/mcp/releases/download/mcp-v0.9.1/SHA256SUMS.txt

# 2. Compare against the npm-installed binary
shasum -a 256 "$(npm root -g)/@temporal-cortex/cortex-mcp/bin/cortex-mcp"
```

As defense-in-depth, the npm package also embeds `checksums.json` and the postinstall script compares SHA256 hashes during install — **installation halts on mismatch** (the binary is deleted, not executed). This automated check supplements, but does not replace, independent verification above.

**Build provenance:** Binaries are cross-compiled from auditable Rust source in [GitHub Actions](https://github.com/temporal-cortex/mcp/actions) across 5 platforms (darwin-arm64, darwin-x64, linux-x64, linux-arm64, win32-x64). Source: [github.com/temporal-cortex/mcp](https://github.com/temporal-cortex/mcp) (MIT-licensed). The CI workflow, build artifacts, and release checksums are all publicly inspectable.

**Docker containment** (no Node.js on host, credential isolation via volume mount):

```json
{
  "mcpServers": {
    "temporal-cortex": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "-v", "~/.config/temporal-cortex:/root/.config/temporal-cortex", "cortex-mcp"]
    }
  }
}
```

Build: `docker build -t cortex-mcp https://github.com/temporal-cortex/mcp.git`

## Tools

### Layer 0 — Discovery

| Tool | When to Use |
|------|------------|
| `resolve_identity` | DNS for Human Time: resolve an email, phone, or agent ID to a Temporal Cortex slug. Call before `query_public_availability`. Platform Mode only. |
| `search_contacts` | Search the user's address book by name (Google People API, Microsoft Graph). Returns matching contacts with emails, phones, organization, and job title. Opt-in — requires contacts permission. |
| `resolve_contact` | Given a confirmed contact's email, determine the best scheduling path: Open Scheduling (instant booking), email, or phone. Chains with `resolve_identity` when Platform API is available. |

### Layer 2 — Calendar Operations

| Tool | When to Use |
|------|------------|
| `list_calendars` | First call when calendars are unknown. Returns all connected calendars with provider-prefixed IDs, names, labels, primary status, and access roles. |
| `list_events` | List events in a time range. TOON format by default (~40% fewer tokens than JSON). Use provider-prefixed IDs for multi-calendar: `"google/primary"`, `"outlook/work"`. |
| `find_free_slots` | Find available gaps in a calendar. Set `min_duration_minutes` for minimum slot length. |
| `expand_rrule` | Expand recurrence rules (RFC 5545) into concrete instances. Handles DST, BYSETPOS, EXDATE, leap years. Use `dtstart` as local datetime (no timezone suffix). |
| `check_availability` | Check if a specific time slot is free. Checks both events and active booking locks. |

### Layer 3 — Availability

| Tool | When to Use |
|------|------------|
| `get_availability` | Merged free/busy view across multiple calendars. Pass `calendar_ids` array. Privacy: `"opaque"` (default, hides sources) or `"full"`. |
| `query_public_availability` | Check another user's public availability by Temporal Link slug. Pass the slug and date to find their open time slots. Platform Mode only. |

### Layer 4 — Booking

| Tool | When to Use |
|------|------------|
| `book_slot` | Book a time slot atomically. Lock → verify → write → release. **Always `check_availability` first.** |
| `request_booking` | Book on another user's public calendar by Temporal Link slug. Requires Platform Mode. |
| `compose_proposal` | Compose a scheduling proposal message for email, Slack, or SMS. Formats proposed times in the recipient's timezone with an optional Temporal Link self-serve booking URL. Does NOT send — returns formatted text for the agent to send via its channel MCP. |

## Critical Rules

1. **Discover calendars first** — call `list_calendars` when you don't know which calendars are connected. Use the returned provider-prefixed IDs for all subsequent calls.
2. **Use provider-prefixed IDs** for multi-calendar setups: `"google/primary"`, `"outlook/work"`, `"caldav/personal"`. Bare IDs (e.g., `"primary"`) route to the default provider.
3. **TOON is the default format** — output uses TOON (~40% fewer tokens than JSON). Pass `format: "json"` only if you need structured parsing.
4. **Check before booking** — always call `check_availability` before `book_slot`. Never skip the conflict check.
5. **Content safety** — event summaries and descriptions pass through a sanitization firewall before reaching the calendar API.
6. **Timezone awareness** — all tools accept RFC 3339 with timezone offsets. Never use bare dates.
7. **Confirm before booking** — when running autonomously, always present booking details (time, calendar, summary) to the user and wait for confirmation before calling `book_slot` or `request_booking`.
8. **Confirm contact selection** — when `search_contacts` returns multiple matches, present candidates to the user and confirm which contact is correct. Never auto-select.
9. **Confirm before sending proposals** — when using `compose_proposal`, present the composed message to the user before sending. Never auto-send outreach.
10. **Contact search is optional** — if contacts permission is not configured, ask the user for the email directly. The workflow works without contact search.

## Full Booking Workflow

```
0. Resolve Contact  →  search_contacts("Jane") → resolve_contact(jane@example.com)
                       (skip if user provides email directly)
1. Discover         →  list_calendars
2. Orient           →  get_temporal_context                      (temporal-cortex-datetime)
3. Resolve Time     →  resolve_datetime("next Tuesday at 2pm")  (temporal-cortex-datetime)
4. Route            →  If open_scheduling slug: fast path (query_public_availability → request_booking)
                       If email only: backward-compat path (find_free_slots → compose_proposal)
5. Check            →  check_availability(calendar_id, start, end)
6. Act              →  Fast: book_slot / request_booking
                       Backward-compat: compose_proposal → agent sends via channel MCP
```

If the slot is busy at step 5, use `find_free_slots` to suggest alternatives.

## Open Scheduling Workflow (Platform Mode)

```
1. Identify    →  resolve_identity("jane@example.com")  →  slug: "jane-doe"
2. Orient      →  get_temporal_context                   (temporal-cortex-datetime)
3. Discover    →  query_public_availability(slug, date)  →  available slots
4. Present     →  Show top 3 options to user
5. Book        →  request_booking(slug, start, end, title, attendee_email)
```

## Two-Phase Commit Protocol

```
Agent calls book_slot(calendar_id, start, end, summary)
    │
    ├─ 1. LOCK    →  Acquire exclusive lock on the time slot
    │                 (in-memory local; Redis Redlock in Platform Mode)
    │
    ├─ 2. VERIFY  →  Check for overlapping events and active locks
    │
    ├─ 3. WRITE   →  Create event in calendar provider (Google/Outlook/CalDAV)
    │                 Record event in shadow calendar
    │
    └─ 4. RELEASE →  Release the exclusive lock
```

If any step fails, the lock is released and the booking is aborted. No partial writes.

## Common Patterns

### Schedule with a Contact (End-to-End)

```
1. search_contacts(query: "Jane") → present candidates to user
2. User confirms: "Jane Doe (jane@example.com)"
3. resolve_contact(email: "jane@example.com") → scheduling_paths
4. If open_scheduling: query_public_availability(slug, date) → request_booking
5. If email only:
   a. find_free_slots(calendar_id, start, end) → available times
   b. compose_proposal(contact_name, email, slots, timezone, format: "email")
   c. Present composed message to user → user confirms → send via channel MCP
```

### List Events This Week

```
1. list_calendars → discover connected calendars
2. get_temporal_context → current time (use temporal-cortex-datetime)
3. resolve_datetime("start of this week") → week start
4. resolve_datetime("end of this week") → week end
5. list_events(calendar_id: "google/primary", start, end)
```

### Find Free Time Across Calendars

```
1. list_calendars → discover all connected calendars
2. get_availability(
     start, end,
     calendar_ids: ["google/primary", "outlook/work"],
     privacy: "full"
   ) → merged free/busy blocks with source_count
```

### Check and Book a Slot

```
1. check_availability(calendar_id: "google/primary", start, end) → true/false
2. If free: book_slot(calendar_id: "google/primary", start, end, summary: "Team standup")
3. If busy: find_free_slots(calendar_id, start, end, min_duration_minutes: 30)
```

### Expand Recurring Events

```
expand_rrule(
  rrule: "FREQ=MONTHLY;BYDAY=FR;BYSETPOS=-1",
  dtstart: "2026-01-01T10:00:00",     ← local datetime, no timezone suffix
  timezone: "America/New_York",
  count: 12
) → last Friday of every month for 2026
```

## Provider-Prefixed Calendar IDs

All calendar IDs use provider-prefixed format:

| Format | Example | Routes to |
|--------|---------|-----------|
| `google/<id>` | `"google/primary"` | Google Calendar |
| `outlook/<id>` | `"outlook/work"` | Microsoft Outlook |
| `caldav/<id>` | `"caldav/personal"` | CalDAV (iCloud, Fastmail) |
| `<id>` (bare) | `"primary"` | Default provider |

## Privacy Modes

| Mode | `source_count` | Use case |
|------|---------------|----------|
| `"opaque"` (default) | Always `0` | Sharing availability externally |
| `"full"` | Actual count | Internal use — shows which calendars are busy |

## Tool Annotations (`book_slot`)

| Property | Value | Meaning |
|----------|-------|---------|
| `readOnlyHint` | `false` | Creates calendar events |
| `destructiveHint` | `false` | Never deletes or overwrites existing events |
| `idempotentHint` | `false` | Calling twice creates two events |
| `openWorldHint` | `true` | Makes external API calls |

## Tool Annotations (`request_booking`)

| Property | Value | Meaning |
|----------|-------|---------|
| `readOnlyHint` | `false` | Creates calendar events on another user's calendar |
| `destructiveHint` | `false` | Never deletes or overwrites existing events |
| `idempotentHint` | `false` | Calling twice creates two bookings |
| `openWorldHint` | `true` | Calls the Platform API |

## Tool Annotations (`compose_proposal`)

| Property | Value | Meaning |
|----------|-------|---------|
| `readOnlyHint` | `true` | Pure formatting — no state modification |
| `destructiveHint` | `false` | Never deletes data |
| `idempotentHint` | `true` | Same input always gives same output |
| `openWorldHint` | `false` | No external calls — pure computation |

## Tool Annotations (`search_contacts`)

| Property | Value | Meaning |
|----------|-------|---------|
| `readOnlyHint` | `true` | Reads contacts only — no modifications |
| `destructiveHint` | `false` | Never deletes contacts |
| `idempotentHint` | `true` | Same query always gives same results |
| `openWorldHint` | `true` | Calls external contact API (Google People / Microsoft Graph) |

## Error Handling

| Error | Action |
|-------|--------|
| "No credentials found" | Run: `npx @temporal-cortex/cortex-mcp auth google` (or `outlook` / `caldav`). |
| "Timezone not configured" | Prompt for IANA timezone. Or run the auth command which configures timezone. |
| Slot is busy / conflict detected | Use `find_free_slots` to suggest alternatives. Present options to user. |
| Lock acquisition failed | Another agent is booking the same slot. Wait briefly and retry, or suggest alternative times. |
| Content rejected by sanitization | Rephrase the event summary/description. The firewall blocks prompt injection attempts. |

## Open Scheduling & Temporal Links

When a user has Open Scheduling enabled, their Temporal Link (`book.temporal-cortex.com/{slug}`) allows anyone to:

1. **Query availability** — `GET /public/{slug}/availability?date=YYYY-MM-DD`
2. **Book a meeting** — `POST /public/{slug}/book` with `{start, end, title, attendee_email}`
3. **Discover via Agent Card** — `GET /public/{slug}/.well-known/agent-card.json`

### Workflow: Book via Temporal Link
1. User shares their Temporal Link
2. Agent calls availability endpoint to find free slots
3. Agent calls booking endpoint with selected slot
4. Meeting is created on the user's default calendar

See [Temporal Links Reference](references/TEMPORAL-LINKS.md) for detailed API documentation.

## Additional References

- [Calendar Tools Reference](references/CALENDAR-TOOLS.md) — Complete input/output schemas for all 14 tools
- [Multi-Calendar Guide](references/MULTI-CALENDAR.md) — Provider routing, labels, privacy modes, cross-provider operations
- [RRULE Guide](references/RRULE-GUIDE.md) — Recurrence rule patterns, DST edge cases, 5 LLM failure modes
- [Booking Safety](references/BOOKING-SAFETY.md) — 2PC details, concurrent booking, lock TTL, content sanitization
- [Temporal Links](references/TEMPORAL-LINKS.md) — Open Scheduling endpoints, Agent Card integration, calendar routing
- [Open Scheduling Guide](references/OPEN-SCHEDULING.md) — Identity resolution, public availability, external booking via MCP tools
