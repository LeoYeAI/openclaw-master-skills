---
name: zoho-calendar
description: |
  Zoho Calendar API integration with managed OAuth. Manage calendars and events with full scheduling capabilities.
  Use this skill when users want to read, create, update, or delete calendar events, manage calendars, or schedule meetings.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - MATON_API_KEY
---

# Zoho Calendar

Access the Zoho Calendar API with managed OAuth authentication. Manage calendars and events with full CRUD operations, including recurring events and attendee management.

## Quick Start

```bash
# List calendars
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-calendar/api/v1/calendars')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/zoho-calendar/api/v1/{endpoint}
```

The gateway proxies requests to `calendar.zoho.com/api/v1` and automatically injects your OAuth token.

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

Manage your Zoho Calendar OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=zoho-calendar&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'zoho-calendar'}).encode()
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
    "app": "zoho-calendar",
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

If you have multiple Zoho Calendar connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-calendar/api/v1/calendars')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Calendars

#### List Calendars

```bash
GET /zoho-calendar/api/v1/calendars
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-calendar/api/v1/calendars')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "calendars": [
    {
      "uid": "fda9b0b4ad834257b622cb3dc3555727",
      "name": "My Calendar",
      "color": "#8cbf40",
      "textcolor": "#FFFFFF",
      "timezone": "PST",
      "isdefault": true,
      "category": "own",
      "privilege": "owner"
    }
  ]
}
```

#### Get Calendar Details

```bash
GET /zoho-calendar/api/v1/calendars/{calendar_uid}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-calendar/api/v1/calendars/fda9b0b4ad834257b622cb3dc3555727')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Calendar

```bash
POST /zoho-calendar/api/v1/calendars?calendarData={json}
```

**Required Fields:**
- `name` - Calendar name (max 50 characters)
- `color` - Hex color code (e.g., `#FF5733`)

**Optional Fields:**
- `textcolor` - Text color hex code
- `description` - Calendar description (max 1000 characters)
- `timezone` - Calendar timezone
- `include_infreebusy` - Show as Busy/Free (boolean)
- `public` - Visibility level (`disable`, `freebusy`, or `view`)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json, urllib.parse

calendarData = {
    "name": "Work Calendar",
    "color": "#FF5733",
    "textcolor": "#FFFFFF",
    "description": "My work calendar"
}

url = f'https://gateway.maton.ai/zoho-calendar/api/v1/calendars?calendarData={urllib.parse.quote(json.dumps(calendarData))}'
req = urllib.request.Request(url, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "calendars": [
    {
      "uid": "86fb9745076e4672ae4324f05e1f5393",
      "name": "Work Calendar",
      "color": "#FF5733",
      "textcolor": "#FFFFFF"
    }
  ]
}
```

#### Delete Calendar

```bash
DELETE /zoho-calendar/api/v1/calendars/{calendar_uid}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-calendar/api/v1/calendars/86fb9745076e4672ae4324f05e1f5393', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "calendars": [
    {
      "uid": "86fb9745076e4672ae4324f05e1f5393",
      "calstatus": "deleted"
    }
  ]
}
```

### Events

#### List Events

```bash
GET /zoho-calendar/api/v1/calendars/{calendar_uid}/events?range={json}
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `range` | JSON object | **Required.** Start and end dates in format `{"start":"yyyyMMdd","end":"yyyyMMdd"}`. Max 31-day span. |
| `byinstance` | boolean | If true, recurring event instances are returned separately |
| `timezone` | string | Timezone for datetime values |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json, urllib.parse
from datetime import datetime, timedelta

today = datetime.now()
end_date = today + timedelta(days=7)
range_param = json.dumps({
    "start": today.strftime("%Y%m%d"),
    "end": end_date.strftime("%Y%m%d")
})

url = f'https://gateway.maton.ai/zoho-calendar/api/v1/calendars/fda9b0b4ad834257b622cb3dc3555727/events?range={urllib.parse.quote(range_param)}'
req = urllib.request.Request(url)
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "events": [
    {
      "uid": "c63e8b9fcb3e48c2a00b16729932d636@zoho.com",
      "title": "Team Meeting",
      "dateandtime": {
        "timezone": "America/Los_Angeles",
        "start": "20260206T100000-0800",
        "end": "20260206T110000-0800"
      },
      "isallday": false,
      "etag": "1770368451507",
      "organizer": "user@example.com"
    }
  ]
}
```

#### Get Event Details

```bash
GET /zoho-calendar/api/v1/calendars/{calendar_uid}/events/{event_uid}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-calendar/api/v1/calendars/fda9b0b4ad834257b622cb3dc3555727/events/c63e8b9fcb3e48c2a00b16729932d636@zoho.com')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Event

```bash
POST /zoho-calendar/api/v1/calendars/{calendar_uid}/events?eventdata={json}
```

**Required Fields (in eventdata):**
- `dateandtime` - Object with `start`, `end`, and optionally `timezone`
  - Format: `yyyyMMdd'T'HHmmss'Z'` (GMT) for timed events
  - Format: `yyyyMMdd` for all-day events

**Optional Fields:**
- `title` - Event name
- `description` - Event details (max 10,000 characters)
- `location` - Event location (max 255 characters)
- `isallday` - Boolean for all-day events
- `isprivate` - Boolean to hide details from non-delegates
- `color` - Hex color code
- `attendees` - Array of attendee objects
- `reminders` - Array of reminder objects
- `rrule` - Recurrence rule string (e.g., `FREQ=DAILY;COUNT=5`)

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json, urllib.parse
from datetime import datetime, timedelta

start_time = datetime.utcnow() + timedelta(hours=1)
end_time = start_time + timedelta(hours=1)

eventdata = {
    "title": "Team Meeting",
    "dateandtime": {
        "timezone": "America/Los_Angeles",
        "start": start_time.strftime("%Y%m%dT%H%M%SZ"),
        "end": end_time.strftime("%Y%m%dT%H%M%SZ")
    },
    "description": "Weekly team sync",
    "location": "Conference Room A"
}

url = f'https://gateway.maton.ai/zoho-calendar/api/v1/calendars/fda9b0b4ad834257b622cb3dc3555727/events?eventdata={urllib.parse.quote(json.dumps(eventdata))}'
req = urllib.request.Request(url, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "events": [
    {
      "uid": "c63e8b9fcb3e48c2a00b16729932d636@zoho.com",
      "title": "Team Meeting",
      "dateandtime": {
        "timezone": "America/Los_Angeles",
        "start": "20260206T100000-0800",
        "end": "20260206T110000-0800"
      },
      "etag": "1770368451507",
      "estatus": "added"
    }
  ]
}
```

#### Update Event

```bash
PUT /zoho-calendar/api/v1/calendars/{calendar_uid}/events/{event_uid}?eventdata={json}
```

**Required Fields:**
- `dateandtime` - Start and end times
- `etag` - Current etag value (from Get Event Details)

**Optional Fields:** Same as Create Event

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json, urllib.parse
from datetime import datetime, timedelta

start_time = datetime.utcnow() + timedelta(hours=2)
end_time = start_time + timedelta(hours=1)

eventdata = {
    "title": "Updated Team Meeting",
    "dateandtime": {
        "timezone": "America/Los_Angeles",
        "start": start_time.strftime("%Y%m%dT%H%M%SZ"),
        "end": end_time.strftime("%Y%m%dT%H%M%SZ")
    },
    "etag": 1770368451507
}

url = f'https://gateway.maton.ai/zoho-calendar/api/v1/calendars/fda9b0b4ad834257b622cb3dc3555727/events/c63e8b9fcb3e48c2a00b16729932d636@zoho.com?eventdata={urllib.parse.quote(json.dumps(eventdata))}'
req = urllib.request.Request(url, method='PUT')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Delete Event

```bash
DELETE /zoho-calendar/api/v1/calendars/{calendar_uid}/events/{event_uid}
```

**Required Header:**
- `etag` - Current etag value of the event

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json

req = urllib.request.Request('https://gateway.maton.ai/zoho-calendar/api/v1/calendars/fda9b0b4ad834257b622cb3dc3555727/events/c63e8b9fcb3e48c2a00b16729932d636@zoho.com', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('etag', '1770368451507')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "events": [
    {
      "uid": "c63e8b9fcb3e48c2a00b16729932d636@zoho.com",
      "estatus": "deleted",
      "caluid": "fda9b0b4ad834257b622cb3dc3555727"
    }
  ]
}
```

### Attendees

When creating or updating events, include attendees:

```json
{
  "attendees": [
    {
      "email": "user@example.com",
      "permission": 1,
      "attendance": 1
    }
  ]
}
```

**Permission levels:** 0 (Guest), 1 (View), 2 (Invite), 3 (Edit)
**Attendance:** 0 (Non-participant), 1 (Required), 2 (Optional)

### Reminders

```json
{
  "reminders": [
    {
      "action": "popup",
      "minutes": 30
    },
    {
      "action": "email",
      "minutes": 60
    }
  ]
}
```

**Actions:** `email`, `popup`, `notification`

### Recurring Events

Use the `rrule` field with iCalendar RRULE format:

```json
{
  "rrule": "FREQ=DAILY;COUNT=5;INTERVAL=1"
}
```

**Examples:**
- Daily for 5 days: `FREQ=DAILY;COUNT=5;INTERVAL=1`
- Weekly on Mon/Tue: `FREQ=WEEKLY;INTERVAL=1;BYDAY=MO,TU;UNTIL=20250817T064600Z`
- Monthly last Tuesday: `FREQ=MONTHLY;INTERVAL=1;BYDAY=TU;BYSETPOS=-1;COUNT=2`

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/zoho-calendar/api/v1/calendars',
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
    'https://gateway.maton.ai/zoho-calendar/api/v1/calendars',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

## Notes

- Event and calendar data is passed as JSON in the `eventdata` or `calendarData` query parameter
- Date/time format for events: `yyyyMMdd'T'HHmmss'Z'` (GMT) or `yyyyMMdd` for all-day events
- The `range` parameter for listing events cannot exceed 31 days
- The `etag` is required for update and delete operations - always get the latest etag before modifying
- For delete operations, the `etag` must be passed as a header, not a query parameter
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Zoho Calendar connection, missing required parameter, or invalid request |
| 401 | Invalid or missing Maton API key, or OAuth scope mismatch |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Zoho Calendar API |

### Common Errors

| Error | Description |
|-------|-------------|
| `ETAG_MISSING` | etag header required for delete operations |
| `EXTRA_PARAM_FOUND` | Invalid parameter in request |
| `INVALID_DATA` | Malformed request data |

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

1. Ensure your URL path starts with `zoho-calendar`. For example:

- Correct: `https://gateway.maton.ai/zoho-calendar/api/v1/calendars`
- Incorrect: `https://gateway.maton.ai/api/v1/calendars`

## Resources

- [Zoho Calendar API Introduction](https://www.zoho.com/calendar/help/api/introduction.html)
- [Zoho Calendar Events API](https://www.zoho.com/calendar/help/api/events-api.html)
- [Zoho Calendar Calendars API](https://www.zoho.com/calendar/help/api/calendars-api.html)
- [Create Event](https://www.zoho.com/calendar/help/api/post-create-event.html)
- [Get Events List](https://www.zoho.com/calendar/help/api/get-events-list.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
