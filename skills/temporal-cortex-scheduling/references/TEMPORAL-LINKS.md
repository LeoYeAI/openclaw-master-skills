# Temporal Links

Temporal Links are public URLs that expose a Temporal Cortex user's scheduling availability and booking endpoint. When a user enables Open Scheduling and chooses a slug, their Temporal Link becomes:

```
https://book.temporal-cortex.com/{slug}
```

Agents use Temporal Links to query availability and book meetings without needing calendar credentials or OAuth tokens. All requests are unauthenticated — the calendar owner controls access through their Open Scheduling settings.

## Endpoints

Each Temporal Link exposes four endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/public/{slug}/availability` | `GET` | Query available time slots |
| `/public/{slug}/book` | `POST` | Book a meeting |
| `/public/{slug}/a2a` | `POST` | Agent-to-agent JSON-RPC |
| `/public/{slug}/.well-known/agent-card.json` | `GET` | Discover scheduling capabilities |

## Querying Availability

Retrieve free time slots for a given date.

```bash
curl "https://book.temporal-cortex.com/public/jane-doe/availability?date=2026-03-10"
```

With optional parameters:

```bash
curl "https://book.temporal-cortex.com/public/jane-doe/availability?date=2026-03-10&duration=60&timezone=Europe/London"
```

**Parameters:**

- `date` (required) — `YYYY-MM-DD` format
- `duration` (optional) — Minimum slot length in minutes. Default: 30.
- `timezone` (optional) — IANA timezone for response times. Default: the calendar owner's configured timezone.

**Response:**

```json
{
  "slug": "jane-doe",
  "date": "2026-03-10",
  "timezone": "America/New_York",
  "slots": [
    { "start": "2026-03-10T09:00:00-05:00", "end": "2026-03-10T09:30:00-05:00" },
    { "start": "2026-03-10T10:00:00-05:00", "end": "2026-03-10T11:00:00-05:00" },
    { "start": "2026-03-10T14:00:00-05:00", "end": "2026-03-10T15:00:00-05:00" }
  ]
}
```

## Booking a Meeting

Book a slot on the user's default calendar. Requires `attendee_email`.

```bash
curl -X POST "https://book.temporal-cortex.com/public/jane-doe/book" \
  -H "Content-Type: application/json" \
  -d '{
    "start": "2026-03-10T10:00:00-05:00",
    "end": "2026-03-10T10:30:00-05:00",
    "title": "Project kickoff",
    "attendee_email": "alex@example.com",
    "attendee_name": "Alex Chen"
  }'
```

**Response (201 Created):**

```json
{
  "booking_id": "bk_a1b2c3d4e5f6",
  "status": "confirmed",
  "calendar_event": {
    "start": "2026-03-10T10:00:00-05:00",
    "end": "2026-03-10T10:30:00-05:00",
    "title": "Project kickoff",
    "attendee_email": "alex@example.com"
  }
}
```

If the slot has been taken between the availability query and the booking request, the response is `409 Conflict`:

```json
{
  "error": "slot_unavailable",
  "message": "The requested time slot is no longer available."
}
```

## Agent-to-Agent (A2A) JSON-RPC

The A2A endpoint accepts JSON-RPC 2.0 requests for programmatic agent-to-agent scheduling.

### Query availability

```bash
curl -X POST "https://book.temporal-cortex.com/public/jane-doe/a2a" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "query_availability",
    "params": { "date": "2026-03-10", "duration": 30, "timezone": "America/New_York" },
    "id": 1
  }'
```

### Book a slot

```bash
curl -X POST "https://book.temporal-cortex.com/public/jane-doe/a2a" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "book_slot",
    "params": {
      "start": "2026-03-10T14:00:00-05:00",
      "end": "2026-03-10T14:30:00-05:00",
      "title": "Strategy sync",
      "attendee_email": "agent@example.com"
    },
    "id": 2
  }'
```

## Agent Card Integration

Every Open Scheduling profile publishes an Agent Card at a well-known URL:

```bash
curl "https://book.temporal-cortex.com/public/jane-doe/.well-known/agent-card.json"
```

**Response:**

```json
{
  "name": "Jane Doe",
  "description": "Schedule a meeting with Jane Doe via Temporal Cortex",
  "url": "https://book.temporal-cortex.com/jane-doe",
  "capabilities": {
    "a2a": "https://book.temporal-cortex.com/public/jane-doe/a2a",
    "availability": "https://book.temporal-cortex.com/public/jane-doe/availability",
    "booking": "https://book.temporal-cortex.com/public/jane-doe/book"
  },
  "provider": {
    "name": "Temporal Cortex",
    "url": "https://temporal-cortex.com"
  },
  "version": "1.0"
}
```

A2A-compatible agents can discover and interact with Open Scheduling profiles by:

1. Fetching the Agent Card to discover endpoint URLs
2. Calling `query_availability` via the A2A endpoint to find free slots
3. Calling `book_slot` via the A2A endpoint to confirm a meeting

The Agent Card follows the emerging A2A protocol convention, making Temporal Cortex profiles discoverable by any agent that supports `.well-known/agent-card.json` resolution.

## Calendar Routing

When a booking is created through a Temporal Link, the meeting is placed on the calendar owner's **default booking calendar**. This is configured in the dashboard under **Settings > Open Scheduling > Default Calendar**.

Calendar routing works as follows:

- **Availability** is computed by merging busy times across all calendars the user has marked as contributing to availability. This includes multiple providers (e.g., a Google Calendar for personal events and an Outlook calendar for work).
- **Bookings** are written to a single designated calendar. The user selects which calendar receives new bookings in the dashboard.
- **Provider-prefixed IDs** are used internally (e.g., `google/primary`, `outlook/work`), but the public API abstracts this away. Callers of the Temporal Link endpoints do not need to know which provider hosts the booking calendar.

If the user has not selected a default booking calendar, the system falls back to the primary calendar of their first connected provider.

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| Availability queries | 60 requests per minute per IP |
| Bookings | 10 per hour per IP |
| Agent Card | 60 requests per minute per IP |
| A2A `query_availability` | 60 requests per minute per IP |
| A2A `book_slot` | 10 per hour per IP |

Exceeding the limit returns `429 Too Many Requests` with a `Retry-After` header.
