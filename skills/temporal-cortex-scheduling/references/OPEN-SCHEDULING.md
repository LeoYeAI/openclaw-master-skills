# Open Scheduling Guide (MCP Tools)

Open Scheduling allows AI agents to find people, check their availability, and book meetings on their calendars — entirely through MCP tools. This guide covers the three Platform Mode tools that enable cross-user scheduling.

## Prerequisites

- **Platform Mode only** — these tools require `API_BASE_URL` to be set. In Local Mode, they return an error.
- The target user must have Open Scheduling enabled on their Temporal Cortex account.

## Tool Overview

| Tool | Layer | Purpose |
|------|-------|---------|
| `resolve_identity` | 0 — Discovery | Email/phone → Temporal Link slug |
| `query_public_availability` | 3 — Availability | Slug + date → available time slots |
| `request_booking` | 4 — Booking | Slug + time → confirmed booking |

## Workflow

```
1. resolve_identity("jane@example.com")
   → { found: true, slug: "jane-doe", open_scheduling_enabled: true }

2. get_temporal_context()
   → current time, timezone, DST info

3. query_public_availability("jane-doe", "2026-03-10")
   → { slots: [{ start: "09:00", end: "10:00" }, ...] }

4. Present options to user and get confirmation

5. request_booking("jane-doe", start, end, "Project Review", "me@example.com")
   → { booking_id: "...", status: "confirmed", calendar_event: {...} }
```

## resolve_identity

DNS for Human Time — resolves an email, phone number, or agent ID to a Temporal Cortex slug.

**Input:**
- `identity` (required) — email, phone, or agent ID

**Output:**
```json
{
  "found": true,
  "slug": "jane-doe",
  "display_name": "Jane Doe",
  "open_scheduling_enabled": true
}
```

**Error cases:**
- Identity not found → `found: false`
- Empty identity → validation error
- Local Mode → error message about Platform Mode requirement

## query_public_availability

Check another user's public availability for a given date.

**Input:**
- `slug` (required) — Temporal Link slug (e.g., "jane-doe")
- `date` (required) — Date in YYYY-MM-DD format
- `duration_minutes` (optional) — Minimum slot duration, default 30
- `timezone` (optional) — IANA timezone for response formatting

**Output:**
```json
{
  "slug": "jane-doe",
  "date": "2026-03-10",
  "timezone": "America/New_York",
  "slots": [
    { "start": "09:00", "end": "10:00" },
    { "start": "14:00", "end": "15:30" }
  ]
}
```

**Error cases:**
- 404 → slug not found
- 429 → rate limit exceeded (60/min per IP)
- Invalid date format → validation error

## request_booking

Book a meeting on another user's public calendar.

**Input:**
- `slug` (required) — Temporal Link slug
- `start` (required) — RFC 3339 datetime
- `end` (required) — RFC 3339 datetime
- `title` (required) — Meeting title
- `attendee_email` (required) — Your email (for the calendar invitation)
- `attendee_name` (optional) — Your display name
- `description` (optional) — Meeting description

**Output:**
```json
{
  "booking_id": "abc123",
  "status": "confirmed",
  "calendar_event": {
    "start": "2026-03-10T09:00:00-04:00",
    "end": "2026-03-10T10:00:00-04:00",
    "title": "Project Review",
    "attendee_email": "me@example.com"
  }
}
```

**Error cases:**
- 409 Conflict → slot no longer available. Re-query availability and pick a different slot.
- 429 Rate Limited → 10 bookings/hr limit. Wait and retry later.
- 404 → slug not found
- Empty title or email → validation error

## Content Safety

All booking requests pass through the Platform's content sanitization firewall server-side. Prompt injection attempts in titles or descriptions are blocked before the calendar event is created.

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| Availability queries | 60/min per IP |
| Booking requests | 10/hr per IP |

## Agent Card Discovery

Users with Open Scheduling enabled also expose an A2A Agent Card at:
```
GET /public/{slug}/.well-known/agent-card.json
```

This enables agent-to-agent discovery per the Google A2A protocol.

## Temporal Links

Each user's public scheduling page is accessible at:
```
book.temporal-cortex.com/{slug}
```

This is the human-facing equivalent of the MCP tools — both use the same backend API.
