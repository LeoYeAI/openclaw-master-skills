---
name: acuity-scheduling
description: |
  Acuity Scheduling API integration with managed OAuth. Manage appointments, calendars, clients, and availability. Use this skill when users want to schedule, reschedule, or cancel appointments, check availability, or manage clients and calendars. For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
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

# Acuity Scheduling

Access the Acuity Scheduling API with managed OAuth authentication. Manage appointments, calendars, clients, availability, and more.

## Quick Start

```bash
# List appointments
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/acuity-scheduling/api/v1/appointments?max=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/acuity-scheduling/{native-api-path}
```

Replace `{native-api-path}` with the actual Acuity API endpoint path. The gateway proxies requests to `acuityscheduling.com` and automatically injects your OAuth token.

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

Manage your Acuity Scheduling OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=acuity-scheduling&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'acuity-scheduling'}).encode()
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
    "app": "acuity-scheduling",
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

If you have multiple Acuity Scheduling connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/acuity-scheduling/api/v1/appointments')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Account Information

#### Get Account Info

```bash
GET /acuity-scheduling/api/v1/me
```

Returns account information including timezone, scheduling page URL, and plan details.

**Response:**
```json
{
  "id": 12345,
  "email": "user@example.com",
  "timezone": "America/Los_Angeles",
  "name": "My Business",
  "schedulingPage": "https://app.acuityscheduling.com/schedule.php?owner=12345",
  "plan": "Professional",
  "currency": "USD"
}
```

### Appointments

#### List Appointments

```bash
GET /acuity-scheduling/api/v1/appointments
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `max` | integer | Maximum results (default: 100) |
| `minDate` | date | Appointments on or after this date |
| `maxDate` | date | Appointments on or before this date |
| `calendarID` | integer | Filter by calendar |
| `appointmentTypeID` | integer | Filter by appointment type |
| `canceled` | boolean | Include canceled appointments (default: false) |
| `firstName` | string | Filter by client first name |
| `lastName` | string | Filter by client last name |
| `email` | string | Filter by client email |
| `excludeForms` | boolean | Omit intake forms for faster response |
| `direction` | string | Sort order: ASC or DESC (default: DESC) |

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/acuity-scheduling/api/v1/appointments?max=10&minDate=2026-02-01')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
[
  {
    "id": 1630290133,
    "firstName": "Jane",
    "lastName": "McTest",
    "phone": "1235550101",
    "email": "jane.mctest@example.com",
    "date": "February 4, 2026",
    "time": "9:30am",
    "endTime": "10:20am",
    "datetime": "2026-02-04T09:30:00-0800",
    "type": "Consultation",
    "appointmentTypeID": 88791369,
    "duration": "50",
    "calendar": "Chris",
    "calendarID": 13499175,
    "canceled": false,
    "confirmationPage": "https://app.acuityscheduling.com/schedule.php?..."
  }
]
```

#### Get Appointment

```bash
GET /acuity-scheduling/api/v1/appointments/{id}
```

#### Create Appointment

```bash
POST /acuity-scheduling/api/v1/appointments
Content-Type: application/json

{
  "datetime": "2026-02-15T09:00",
  "appointmentTypeID": 123,
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "phone": "555-123-4567",
  "timezone": "America/New_York"
}
```

**Required Fields:**
- `datetime` - Date and time (parseable by PHP's strtotime)
- `appointmentTypeID` - Appointment type ID
- `firstName` - Client's first name
- `lastName` - Client's last name
- `email` - Client's email

**Optional Fields:**
- `phone` - Client phone number
- `calendarID` - Specific calendar (auto-selected if omitted)
- `timezone` - Client's timezone
- `certificate` - Package or coupon code
- `notes` - Admin notes
- `addonIDs` - Array of addon IDs
- `fields` - Array of form field values

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    'datetime': '2026-02-15T09:00',
    'appointmentTypeID': 123,
    'firstName': 'John',
    'lastName': 'Doe',
    'email': 'john.doe@example.com'
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/acuity-scheduling/api/v1/appointments', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update Appointment

```bash
PUT /acuity-scheduling/api/v1/appointments/{id}
Content-Type: application/json

{
  "firstName": "Jane",
  "lastName": "Smith",
  "email": "jane.smith@example.com"
}
```

#### Cancel Appointment

```bash
PUT /acuity-scheduling/api/v1/appointments/{id}/cancel
```

Returns the canceled appointment with `canceled: true`.

#### Reschedule Appointment

```bash
PUT /acuity-scheduling/api/v1/appointments/{id}/reschedule
Content-Type: application/json

{
  "datetime": "2026-02-20T10:00"
}
```

**Note:** The new datetime must be an available time slot.

### Calendars

#### List Calendars

```bash
GET /acuity-scheduling/api/v1/calendars
```

**Response:**
```json
[
  {
    "id": 13499175,
    "name": "Chris",
    "email": "",
    "replyTo": "chris@example.com",
    "description": "",
    "location": "",
    "timezone": "America/Los_Angeles"
  }
]
```

### Appointment Types

#### List Appointment Types

```bash
GET /acuity-scheduling/api/v1/appointment-types
```

**Query Parameters:**
- `includeDeleted` (boolean) - Include deleted types

**Response:**
```json
[
  {
    "id": 88791369,
    "name": "Consultation",
    "active": true,
    "description": "",
    "duration": 50,
    "price": "45.00",
    "category": "",
    "color": "#ED7087",
    "private": false,
    "type": "service",
    "calendarIDs": [13499175],
    "schedulingUrl": "https://app.acuityscheduling.com/schedule.php?..."
  }
]
```

### Availability

#### Get Available Dates

```bash
GET /acuity-scheduling/api/v1/availability/dates?month=2026-02&appointmentTypeID=123
```

**Required Parameters:**
- `month` - Month to check (e.g., "2026-02")
- `appointmentTypeID` - Appointment type ID

**Optional Parameters:**
- `calendarID` - Specific calendar
- `timezone` - Timezone for results (e.g., "America/New_York")

**Response:**
```json
[
  {"date": "2026-02-09"},
  {"date": "2026-02-10"},
  {"date": "2026-02-11"}
]
```

#### Get Available Times

```bash
GET /acuity-scheduling/api/v1/availability/times?date=2026-02-10&appointmentTypeID=123
```

**Required Parameters:**
- `date` - Date to check
- `appointmentTypeID` - Appointment type ID

**Optional Parameters:**
- `calendarID` - Specific calendar
- `timezone` - Timezone for results

**Response:**
```json
[
  {"time": "2026-02-10T09:00:00-0800", "slotsAvailable": 1},
  {"time": "2026-02-10T09:50:00-0800", "slotsAvailable": 1},
  {"time": "2026-02-10T10:40:00-0800", "slotsAvailable": 1}
]
```

### Clients

#### List Clients

```bash
GET /acuity-scheduling/api/v1/clients
```

**Query Parameters:**
- `search` - Filter by first name, last name, or phone

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/acuity-scheduling/api/v1/clients?search=John')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
[
  {
    "firstName": "Jane",
    "lastName": "McTest",
    "email": "jane.mctest@example.com",
    "phone": "(123) 555-0101",
    "notes": ""
  }
]
```

#### Create Client

```bash
POST /acuity-scheduling/api/v1/clients
Content-Type: application/json

{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "phone": "555-123-4567"
}
```

#### Update Client

```bash
PUT /acuity-scheduling/api/v1/clients
Content-Type: application/json

{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.updated@example.com"
}
```

**Note:** Client update/delete only works for clients with existing appointments.

#### Delete Client

```bash
DELETE /acuity-scheduling/api/v1/clients
Content-Type: application/json

{
  "firstName": "John",
  "lastName": "Doe"
}
```

### Blocks

#### List Blocks

```bash
GET /acuity-scheduling/api/v1/blocks
```

**Query Parameters:**
- `max` - Maximum results (default: 100)
- `minDate` - Blocks on or after this date
- `maxDate` - Blocks on or before this date
- `calendarID` - Filter by calendar

#### Get Block

```bash
GET /acuity-scheduling/api/v1/blocks/{id}
```

#### Create Block

```bash
POST /acuity-scheduling/api/v1/blocks
Content-Type: application/json

{
  "start": "2026-02-15T12:00",
  "end": "2026-02-15T13:00",
  "calendarID": 1234,
  "notes": "Lunch break"
}
```

**Response:**
```json
{
  "id": 9589304654,
  "calendarID": 13499175,
  "start": "2026-02-15T12:00:00-0800",
  "end": "2026-02-15T13:00:00-0800",
  "notes": "Lunch break",
  "description": "Sunday, February 15, 2026 12:00pm - 1:00pm"
}
```

#### Delete Block

```bash
DELETE /acuity-scheduling/api/v1/blocks/{id}
```

Returns 204 No Content on success.

### Forms

#### List Forms

```bash
GET /acuity-scheduling/api/v1/forms
```

**Response:**
```json
[
  {
    "id": 123,
    "name": "Client Intake Form",
    "appointmentTypeIDs": [456, 789],
    "fields": [
      {
        "id": 1,
        "name": "How did you hear about us?",
        "type": "dropdown",
        "options": ["Google", "Friend", "Social Media"],
        "required": true
      }
    ]
  }
]
```

### Labels

#### List Labels

```bash
GET /acuity-scheduling/api/v1/labels
```

**Response:**
```json
[
  {"id": 23116714, "name": "Checked In", "color": "green"},
  {"id": 23116715, "name": "Completed", "color": "pink"},
  {"id": 23116713, "name": "Confirmed", "color": "yellow"}
]
```

## Pagination

Acuity Scheduling uses the `max` parameter to limit results. Use `minDate` and `maxDate` to paginate through date ranges:

```bash
# First page
GET /acuity-scheduling/api/v1/appointments?max=100&minDate=2026-01-01&maxDate=2026-01-31

# Next page
GET /acuity-scheduling/api/v1/appointments?max=100&minDate=2026-02-01&maxDate=2026-02-28
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/acuity-scheduling/api/v1/appointments?max=10',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const appointments = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/acuity-scheduling/api/v1/appointments',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'max': 10}
)
appointments = response.json()
```

## Notes

- Datetime values must be parseable by PHP's `strtotime()` function
- Timezones use IANA format (e.g., "America/New_York", "America/Los_Angeles")
- Client update/delete requires clients to have existing appointments
- Rescheduling requires the new datetime to be an available time slot
- Use `excludeForms=true` for faster appointment list responses
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments. You may get "Invalid API key" errors when piping.

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Invalid request (e.g., time not available, client not found) |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Acuity API |

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

1. Ensure your URL path starts with `acuity-scheduling`. For example:

- Correct: `https://gateway.maton.ai/acuity-scheduling/api/v1/appointments`
- Incorrect: `https://gateway.maton.ai/api/v1/appointments`

## Resources

- [Acuity Scheduling API Quick Start](https://developers.acuityscheduling.com/reference/quick-start)
- [Appointments API](https://developers.acuityscheduling.com/reference/get-appointments)
- [Availability API](https://developers.acuityscheduling.com/reference/get-availability-dates)
- [Calendars API](https://developers.acuityscheduling.com/reference/get-calendars)
- [Clients API](https://developers.acuityscheduling.com/reference/clients)
- [OAuth2 Documentation](https://developers.acuityscheduling.com/docs/oauth2)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
