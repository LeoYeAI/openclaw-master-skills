---
name: calendly
description: |
  Calendly API integration with managed OAuth. Access event types, scheduled events, invitees, availability, and manage webhooks. Use this skill when users want to view scheduling data, check availability, book meetings, or integrate with Calendly workflows. For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - MATON_API_KEY
---

# Calendly

Access the Calendly API with managed OAuth authentication. Retrieve event types, scheduled events, invitees, availability data, and manage webhook subscriptions for scheduling automation.

## Quick Start

```bash
# Get current user
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/users/me')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/calendly/{native-api-path}
```

Replace `{native-api-path}` with the actual Calendly API endpoint path. The gateway proxies requests to `api.calendly.com` and automatically injects your OAuth token.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Calendly OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=calendly&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'calendly'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
    "status": "ACTIVE",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "calendly",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Calendly connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/users/me')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Users

#### Get Current User

```bash
GET /calendly/users/me
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/users/me')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "resource": {
    "uri": "https://api.calendly.com/users/AAAAAAAAAAAAAAAA",
    "name": "Alice Johnson",
    "slug": "alice-johnson",
    "email": "alice.johnson@acme.com",
    "scheduling_url": "https://calendly.com/alice-johnson",
    "timezone": "America/New_York",
    "avatar_url": "https://example.com/avatar.png",
    "created_at": "2024-01-15T10:30:00.000000Z",
    "updated_at": "2025-06-20T14:45:00.000000Z",
    "current_organization": "https://api.calendly.com/organizations/BBBBBBBBBBBBBBBB"
  }
}
```

#### Get a User

```bash
GET /calendly/users/{uuid}
```

### Event Types

#### List Event Types

```bash
GET /calendly/event_types
```

Query parameters:
- `user` - User URI to filter event types
- `organization` - Organization URI to filter event types
- `active` - Filter by active status (true/false)
- `count` - Number of results to return (default 20, max 100)
- `page_token` - Token for pagination
- `sort` - Sort order (e.g., `name:asc`, `created_at:desc`)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/event_types?user=https://api.calendly.com/users/AAAAAAAAAAAAAAAA&active=true')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "collection": [
    {
      "uri": "https://api.calendly.com/event_types/CCCCCCCCCCCCCCCC",
      "name": "30 Minute Meeting",
      "active": true,
      "slug": "30min",
      "scheduling_url": "https://calendly.com/alice-johnson/30min",
      "duration": 30,
      "kind": "solo",
      "type": "StandardEventType",
      "color": "#0066FF",
      "created_at": "2024-02-01T09:00:00.000000Z",
      "updated_at": "2025-05-15T11:30:00.000000Z",
      "description_plain": "A quick 30-minute catch-up call",
      "description_html": "<p>A quick 30-minute catch-up call</p>",
      "profile": {
        "type": "User",
        "name": "Alice Johnson",
        "owner": "https://api.calendly.com/users/AAAAAAAAAAAAAAAA"
      }
    }
  ],
  "pagination": {
    "count": 1,
    "next_page_token": null
  }
}
```

#### Get an Event Type

```bash
GET /calendly/event_types/{uuid}
```

### Scheduled Events

#### List Scheduled Events

```bash
GET /calendly/scheduled_events
```

Query parameters:
- `user` - User URI to filter events
- `organization` - Organization URI to filter events
- `invitee_email` - Filter by invitee email
- `status` - Filter by status (`active`, `canceled`)
- `min_start_time` - Filter events starting after this time (ISO 8601)
- `max_start_time` - Filter events starting before this time (ISO 8601)
- `count` - Number of results (default 20, max 100)
- `page_token` - Token for pagination
- `sort` - Sort order (e.g., `start_time:asc`)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/scheduled_events?user=https://api.calendly.com/users/AAAAAAAAAAAAAAAA&status=active&min_start_time=2025-03-01T00:00:00Z')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "collection": [
    {
      "uri": "https://api.calendly.com/scheduled_events/DDDDDDDDDDDDDDDD",
      "name": "30 Minute Meeting",
      "status": "active",
      "start_time": "2025-03-15T14:00:00.000000Z",
      "end_time": "2025-03-15T14:30:00.000000Z",
      "event_type": "https://api.calendly.com/event_types/CCCCCCCCCCCCCCCC",
      "location": {
        "type": "zoom",
        "join_url": "https://zoom.us/j/123456789"
      },
      "invitees_counter": {
        "total": 1,
        "active": 1,
        "limit": 1
      },
      "created_at": "2025-03-10T09:15:00.000000Z",
      "updated_at": "2025-03-10T09:15:00.000000Z",
      "event_memberships": [
        {
          "user": "https://api.calendly.com/users/AAAAAAAAAAAAAAAA"
        }
      ]
    }
  ],
  "pagination": {
    "count": 1,
    "next_page_token": null
  }
}
```

#### Get a Scheduled Event

```bash
GET /calendly/scheduled_events/{uuid}
```

#### Cancel a Scheduled Event

```bash
POST /calendly/scheduled_events/{uuid}/cancellation
Content-Type: application/json

{
  "reason": "Meeting rescheduled"
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'reason': 'Meeting rescheduled'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/calendly/scheduled_events/DDDDDDDDDDDDDDDD/cancellation', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Invitees

#### List Event Invitees

```bash
GET /calendly/scheduled_events/{event_uuid}/invitees
```

Query parameters:
- `status` - Filter by status (`active`, `canceled`)
- `email` - Filter by invitee email
- `count` - Number of results (default 20, max 100)
- `page_token` - Token for pagination
- `sort` - Sort order (e.g., `created_at:asc`)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/scheduled_events/DDDDDDDDDDDDDDDD/invitees')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "collection": [
    {
      "uri": "https://api.calendly.com/scheduled_events/DDDDDDDDDDDDDDDD/invitees/EEEEEEEEEEEEEEEE",
      "email": "bob.smith@example.com",
      "name": "Bob Smith",
      "status": "active",
      "timezone": "America/Los_Angeles",
      "event": "https://api.calendly.com/scheduled_events/DDDDDDDDDDDDDDDD",
      "created_at": "2025-03-10T09:15:00.000000Z",
      "updated_at": "2025-03-10T09:15:00.000000Z",
      "questions_and_answers": [
        {
          "question": "What would you like to discuss?",
          "answer": "Project timeline review",
          "position": 0
        }
      ],
      "tracking": {
        "utm_source": null,
        "utm_medium": null,
        "utm_campaign": null
      },
      "cancel_url": "https://calendly.com/cancellations/EEEEEEEEEEEEEEEE",
      "reschedule_url": "https://calendly.com/reschedulings/EEEEEEEEEEEEEEEE"
    }
  ],
  "pagination": {
    "count": 1,
    "next_page_token": null
  }
}
```

#### Get an Invitee

```bash
GET /calendly/scheduled_events/{event_uuid}/invitees/{invitee_uuid}
```

#### Create Event Invitee (Scheduling API)

Schedule a meeting programmatically by creating an invitee. Requires a paid Calendly plan.

```bash
POST /calendly/event_types/{event_type_uuid}/invitees
Content-Type: application/json

{
  "start_time": "2025-03-20T15:00:00Z",
  "email": "bob.smith@example.com",
  "name": "Bob Smith",
  "timezone": "America/Los_Angeles",
  "location": {
    "kind": "zoom"
  },
  "questions_and_answers": [
    {
      "question_uuid": "QQQQQQQQQQQQQQQ",
      "answer": "Project timeline review"
    }
  ]
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'start_time': '2025-03-20T15:00:00Z', 'email': 'bob.smith@example.com', 'name': 'Bob Smith'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/calendly/event_types/CCCCCCCCCCCCCCCC/invitees', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Note:** The `start_time` must correspond to a valid available slot. Use the `/event_type_available_times` endpoint to find available times.

### Availability

#### Get Event Type Available Times

```bash
GET /calendly/event_type_available_times
```

Query parameters:
- `event_type` - Event type URI (required)
- `start_time` - Start of time range (ISO 8601, required)
- `end_time` - End of time range (ISO 8601, required, max 7 days from start)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/event_type_available_times?event_type=https://api.calendly.com/event_types/CCCCCCCCCCCCCCCC&start_time=2025-03-15T00:00:00Z&end_time=2025-03-22T00:00:00Z')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "collection": [
    {
      "status": "available",
      "invitees_remaining": 1,
      "start_time": "2025-03-17T14:00:00.000000Z",
      "scheduling_url": "https://calendly.com/alice-johnson/30min/2025-03-17T14:00:00Z"
    },
    {
      "status": "available",
      "invitees_remaining": 1,
      "start_time": "2025-03-17T14:30:00.000000Z",
      "scheduling_url": "https://calendly.com/alice-johnson/30min/2025-03-17T14:30:00Z"
    }
  ]
}
```

#### Get User Busy Times

```bash
GET /calendly/user_busy_times
```

Query parameters:
- `user` - User URI (required)
- `start_time` - Start of time range (ISO 8601, required)
- `end_time` - End of time range (ISO 8601, required, max 7 days from start)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/user_busy_times?user=https://api.calendly.com/users/AAAAAAAAAAAAAAAA&start_time=2025-03-15T00:00:00Z&end_time=2025-03-22T00:00:00Z')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "collection": [
    {
      "type": "calendly",
      "start_time": "2025-03-17T10:00:00.000000Z",
      "end_time": "2025-03-17T11:00:00.000000Z"
    },
    {
      "type": "external",
      "start_time": "2025-03-18T14:00:00.000000Z",
      "end_time": "2025-03-18T15:00:00.000000Z"
    }
  ]
}
```

#### Get User Availability Schedules

```bash
GET /calendly/user_availability_schedules
```

Query parameters:
- `user` - User URI (required)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/user_availability_schedules?user=https://api.calendly.com/users/AAAAAAAAAAAAAAAA')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Organization

#### List Organization Memberships

```bash
GET /calendly/organization_memberships
```

Query parameters:
- `organization` - Organization URI (required)
- `user` - User URI to filter
- `email` - Email to filter
- `count` - Number of results (default 20, max 100)
- `page_token` - Token for pagination

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/organization_memberships?organization=https://api.calendly.com/organizations/BBBBBBBBBBBBBBBB')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "collection": [
    {
      "uri": "https://api.calendly.com/organization_memberships/FFFFFFFFFFFFFFFF",
      "role": "admin",
      "user": {
        "uri": "https://api.calendly.com/users/AAAAAAAAAAAAAAAA",
        "name": "Alice Johnson",
        "email": "alice.johnson@acme.com"
      },
      "organization": "https://api.calendly.com/organizations/BBBBBBBBBBBBBBBB",
      "created_at": "2024-01-15T10:30:00.000000Z",
      "updated_at": "2025-06-20T14:45:00.000000Z"
    }
  ],
  "pagination": {
    "count": 1,
    "next_page_token": null
  }
}
```

### Webhooks

Webhooks require a paid Calendly plan (Standard, Teams, or Enterprise).

#### List Webhook Subscriptions

```bash
GET /calendly/webhook_subscriptions
```

Query parameters:
- `organization` - Organization URI (required)
- `scope` - Filter by scope (`user`, `organization`)
- `user` - User URI to filter (when scope is `user`)
- `count` - Number of results (default 20, max 100)
- `page_token` - Token for pagination

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/webhook_subscriptions?organization=https://api.calendly.com/organizations/BBBBBBBBBBBBBBBB&scope=organization')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Webhook Subscription

```bash
POST /calendly/webhook_subscriptions
Content-Type: application/json

{
  "url": "https://example.com/webhook",
  "events": ["invitee.created", "invitee.canceled"],
  "organization": "https://api.calendly.com/organizations/BBBBBBBBBBBBBBBB",
  "scope": "organization",
  "signing_key": "your-secret-key"
}
```

Available events:
- `invitee.created` - Triggered when an invitee schedules an event
- `invitee.canceled` - Triggered when an invitee cancels an event
- `routing_form_submission.created` - Triggered when a routing form is submitted

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'url': 'https://example.com/webhook', 'events': ['invitee.created', 'invitee.canceled'], 'organization': 'https://api.calendly.com/organizations/BBBBBBBBBBBBBBBB', 'scope': 'organization'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/calendly/webhook_subscriptions', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "resource": {
    "uri": "https://api.calendly.com/webhook_subscriptions/GGGGGGGGGGGGGGGG",
    "callback_url": "https://example.com/webhook",
    "created_at": "2025-03-01T12:00:00.000000Z",
    "updated_at": "2025-03-01T12:00:00.000000Z",
    "retry_started_at": null,
    "state": "active",
    "events": ["invitee.created", "invitee.canceled"],
    "scope": "organization",
    "organization": "https://api.calendly.com/organizations/BBBBBBBBBBBBBBBB",
    "user": null,
    "creator": "https://api.calendly.com/users/AAAAAAAAAAAAAAAA"
  }
}
```

#### Get a Webhook Subscription

```bash
GET /calendly/webhook_subscriptions/{uuid}
```

#### Delete a Webhook Subscription

```bash
DELETE /calendly/webhook_subscriptions/{uuid}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/webhook_subscriptions/GGGGGGGGGGGGGGGG', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

Returns `204 No Content` on success.

## Pagination

Use `page_token` for pagination. Response includes `pagination.next_page_token` when more results exist:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/calendly/scheduled_events?user=USER_URI&page_token=NEXT_PAGE_TOKEN')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/calendly/scheduled_events?user=https://api.calendly.com/users/AAAAAAAAAAAAAAAA&status=active',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/calendly/scheduled_events',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={
        'user': 'https://api.calendly.com/users/AAAAAAAAAAAAAAAA',
        'status': 'active'
    }
)
data = response.json()
```

## Notes

- Resource identifiers are URIs (e.g., `https://api.calendly.com/users/AAAAAAAAAAAAAAAA`)
- Timestamps are in ISO 8601 format
- The Scheduling API (Create Event Invitee) requires a paid Calendly plan
- Webhooks are not available on Calendly's free plan
- Availability endpoints have a 7-day maximum range per request and `start_time` must be in the future
- The API does not support creating or managing event types programmatically
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments. You may get "Invalid API key" errors when piping.

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or missing Calendly connection |
| 401 | Invalid or missing Maton API key |
| 403 | Forbidden - insufficient permissions or plan restrictions |
| 404 | Resource not found |
| 424 | External calendar error (calendar integration issue on Calendly side) |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Calendly API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `calendly`. For example:

- Correct: `https://gateway.maton.ai/calendly/users/me`
- Incorrect: `https://gateway.maton.ai/users/me`

## Resources

- [Calendly Developer Portal](https://developer.calendly.com/)
- [API Reference](https://developer.calendly.com/api-docs)
- [API Use Cases](https://developer.calendly.com/api-use-cases)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
