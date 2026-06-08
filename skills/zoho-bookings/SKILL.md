---
name: zoho-bookings
description: |
  Zoho Bookings API integration with managed OAuth. Manage appointments, services, staff, and workspaces.
  Use this skill when users want to book appointments, manage services, view staff availability, or manage workspaces in Zoho Bookings.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Zoho Bookings

Access the Zoho Bookings API with managed OAuth authentication. Manage appointments, services, staff, and workspaces with full CRUD operations.

## Quick Start

```bash
# List workspaces
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/workspaces')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/zoho-bookings/bookings/v1/json/{endpoint}
```

The gateway proxies requests to `www.zohoapis.com/bookings/v1/json` and automatically injects your OAuth token.

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

Manage your Zoho Bookings OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=zoho-bookings&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'zoho-bookings'}).encode()
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
    "connection_id": "3c358231-7ca7-4a63-8a3c-3a9d21be53ca",
    "status": "ACTIVE",
    "creation_time": "2026-02-18T00:17:23.498742Z",
    "last_updated_time": "2026-02-18T00:18:59.299114Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "zoho-bookings",
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

If you have multiple Zoho Bookings connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/workspaces')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '3c358231-7ca7-4a63-8a3c-3a9d21be53ca')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Workspaces

#### Fetch Workspaces

```bash
GET /zoho-bookings/bookings/v1/json/workspaces
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `workspace_id` | string | Filter by specific workspace ID |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/workspaces')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "response": {
    "returnvalue": {
      "data": [
        {
          "name": "Main Office",
          "id": "4753814000000048016"
        }
      ]
    },
    "status": "success"
  }
}
```

#### Create Workspace

```bash
POST /zoho-bookings/bookings/v1/json/createworkspace
Content-Type: application/x-www-form-urlencoded
```

**Form Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Workspace name (2-50 chars, no special characters) |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
from urllib.parse import urlencode
form_data = urlencode({'name': 'New York Office'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/createworkspace', data=form_data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Services

#### Fetch Services

```bash
GET /zoho-bookings/bookings/v1/json/services?workspace_id={workspace_id}
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | string | Yes | Workspace ID |
| `service_id` | string | No | Filter by specific service ID |
| `staff_id` | string | No | Filter by staff ID |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/services?workspace_id=4753814000000048016')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "response": {
    "returnvalue": {
      "data": [
        {
          "id": "4753814000000048054",
          "name": "Product Demo",
          "duration": "30 mins",
          "service_type": "APPOINTMENT",
          "price": 0,
          "currency": "USD",
          "assigned_staffs": ["4753814000000048014"],
          "assigned_workspace": "4753814000000048016",
          "embed_url": "https://example.zohobookings.com/portal-embed#/4753814000000048054",
          "let_customer_select_staff": true
        }
      ],
      "next_page_available": false,
      "page": 1
    },
    "status": "success"
  }
}
```

#### Create Service

```bash
POST /zoho-bookings/bookings/v1/json/createservice
Content-Type: application/x-www-form-urlencoded
```

**Form Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `name` | string | Yes | Service name |
| `workspace_id` | string | Yes | Workspace ID |
| `duration` | integer | No | Duration in minutes |
| `cost` | number | No | Service price |
| `pre_buffer` | integer | No | Buffer time before (minutes) |
| `post_buffer` | integer | No | Buffer time after (minutes) |
| `description` | string | No | Service description |
| `assigned_staffs` | string | No | JSON array of staff IDs |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
from urllib.parse import urlencode
form_data = urlencode({
    'name': 'Consultation',
    'workspace_id': '4753814000000048016',
    'duration': '60'
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/createservice', data=form_data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Staff

#### Fetch Staff

```bash
GET /zoho-bookings/bookings/v1/json/staffs?workspace_id={workspace_id}
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workspace_id` | string | Yes | Workspace ID |
| `staff_id` | string | No | Filter by specific staff ID |
| `service_id` | string | No | Filter by service ID |
| `staff_email` | string | No | Filter by email (partial match) |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/staffs?workspace_id=4753814000000048016')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "response": {
    "returnvalue": {
      "data": [
        {
          "id": "4753814000000048014",
          "name": "John Doe",
          "email": "john@example.com",
          "designation": "Consultant",
          "assigned_services": ["4753814000000048054"],
          "assigned_workspaces": ["4753814000000048016"],
          "embed_url": "https://example.zohobookings.com/portal-embed#/4753814000000048014"
        }
      ]
    },
    "status": "success"
  }
}
```

### Appointments

#### Book Appointment

```bash
POST /zoho-bookings/bookings/v1/json/appointment
Content-Type: application/x-www-form-urlencoded
```

**Form Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `service_id` | string | Yes | Service ID |
| `staff_id` | string | Yes* | Staff ID (*or resource_id/group_id) |
| `from_time` | string | Yes | Start time: `dd-MMM-yyyy HH:mm:ss` (24-hour) |
| `timezone` | string | No | Timezone (e.g., `America/Los_Angeles`) |
| `customer_details` | string | Yes | JSON string with `name`, `email`, `phone_number` |
| `notes` | string | No | Appointment notes |
| `additional_fields` | string | No | JSON string with custom fields |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
from urllib.parse import urlencode
form_data = urlencode({
    'service_id': '4753814000000048054',
    'staff_id': '4753814000000048014',
    'from_time': '20-Feb-2026 10:00:00',
    'timezone': 'America/Los_Angeles',
    'customer_details': json.dumps({
        'name': 'Jane Smith',
        'email': 'jane@example.com',
        'phone_number': '+15551234567'
    })
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/appointment', data=form_data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "response": {
    "returnvalue": {
      "booking_id": "#NU-00001",
      "service_name": "Product Demo",
      "staff_name": "John Doe",
      "start_time": "20-Feb-2026 10:00:00",
      "end_time": "20-Feb-2026 10:30:00",
      "duration": "30 mins",
      "customer_name": "Jane Smith",
      "customer_email": "jane@example.com",
      "status": "upcoming",
      "time_zone": "America/Los_Angeles"
    },
    "status": "success"
  }
}
```

#### Get Appointment

```bash
GET /zoho-bookings/bookings/v1/json/getappointment?booking_id={booking_id}
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `booking_id` | string | Yes | Booking ID (URL-encoded, e.g., `%23NU-00001`) |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/getappointment?booking_id=%23NU-00001')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Fetch Appointments

```bash
POST /zoho-bookings/bookings/v1/json/fetchappointment
Content-Type: application/x-www-form-urlencoded
```

**Form Parameters:**

Send parameters wrapped in a `data` field as JSON:

| Parameter | Type | Description |
|-----------|------|-------------|
| `from_time` | string | Start date: `dd-MMM-yyyy HH:mm:ss` |
| `to_time` | string | End date: `dd-MMM-yyyy HH:mm:ss` |
| `status` | string | `UPCOMING`, `CANCEL`, `COMPLETED`, `NO_SHOW`, `PENDING` |
| `service_id` | string | Filter by service |
| `staff_id` | string | Filter by staff |
| `customer_name` | string | Filter by customer name (partial match) |
| `customer_email` | string | Filter by email (partial match) |
| `page` | integer | Page number |
| `per_page` | integer | Results per page (max 100) |

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
from urllib.parse import urlencode
form_data = urlencode({
    'data': json.dumps({
        'from_time': '17-Feb-2026 00:00:00',
        'to_time': '20-Feb-2026 23:59:59'
    })
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/fetchappointment', data=form_data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "response": {
    "returnvalue": {
      "response": [
        {
          "booking_id": "#NU-00001",
          "service_name": "Product Demo",
          "staff_name": "John Doe",
          "start_time": "20-Feb-2026 10:00:00",
          "customer_name": "Jane Smith",
          "status": "upcoming"
        }
      ],
      "next_page_available": false,
      "page": 1
    },
    "status": "success"
  }
}
```

#### Update Appointment

```bash
POST /zoho-bookings/bookings/v1/json/updateappointment
Content-Type: application/x-www-form-urlencoded
```

**Form Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `booking_id` | string | Yes | Booking ID |
| `action` | string | Yes | `completed`, `cancel`, or `noshow` |

**Example - Cancel Appointment:**

```bash
python <<'EOF'
import urllib.request, os, json
from urllib.parse import urlencode
form_data = urlencode({
    'booking_id': '#NU-00001',
    'action': 'cancel'
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/updateappointment', data=form_data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Pagination

Appointments use page-based pagination:

```bash
python <<'EOF'
import urllib.request, os, json
from urllib.parse import urlencode
form_data = urlencode({
    'data': json.dumps({
        'from_time': '01-Feb-2026 00:00:00',
        'to_time': '28-Feb-2026 23:59:59',
        'page': 1,
        'per_page': 50
    })
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/zoho-bookings/bookings/v1/json/fetchappointment', data=form_data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/x-www-form-urlencoded')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

Response includes pagination info:

```json
{
  "response": {
    "returnvalue": {
      "response": [...],
      "next_page_available": true,
      "page": 1
    },
    "status": "success"
  }
}
```

## Code Examples

### JavaScript

```javascript
// Fetch workspaces
const response = await fetch(
  'https://gateway.maton.ai/zoho-bookings/bookings/v1/json/workspaces',
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

# Fetch services
response = requests.get(
    'https://gateway.maton.ai/zoho-bookings/bookings/v1/json/services',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'workspace_id': '4753814000000048016'}
)
data = response.json()
```

## Notes

- Date/time format: `dd-MMM-yyyy HH:mm:ss` (e.g., `20-Feb-2026 10:00:00`)
- Booking IDs include `#` prefix (URL-encode as `%23`)
- `customer_details` must be a JSON string, not an object
- `fetchappointment` requires parameters wrapped in `data` field as JSON
- Other POST endpoints use regular form fields
- Service types: `APPOINTMENT`, `RESOURCE`, `CLASS`, `COLLECTIVE`
- Status values: `UPCOMING`, `CANCEL`, `ONGOING`, `PENDING`, `COMPLETED`, `NO_SHOW`
- Default pagination: 50 appointments per page (max 100)
- If you receive a scope error, contact Maton support at support@maton.ai with the specific operations/APIs you need and your use-case
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Zoho Bookings connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Zoho Bookings API |

### Rate Limits

| Plan | Daily Limit |
|------|-------------|
| Free | 250 calls/user |
| Basic | 1,000 calls/user |
| Premium | 3,000 calls/user |
| Zoho One | 3,000 calls/user |

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

1. Ensure your URL path starts with `zoho-bookings`. For example:

- Correct: `https://gateway.maton.ai/zoho-bookings/bookings/v1/json/workspaces`
- Incorrect: `https://gateway.maton.ai/bookings/v1/json/workspaces`

## Resources

- [Zoho Bookings API Documentation](https://www.zoho.com/bookings/help/api/v1/oauthauthentication.html)
- [Book Appointment API](https://www.zoho.com/bookings/help/api/v1/book-appointment.html)
- [Fetch Appointments API](https://www.zoho.com/bookings/help/api/v1/fetch-appointment.html)
- [Fetch Services API](https://www.zoho.com/bookings/help/api/v1/fetch-services.html)
- [Fetch Staff API](https://www.zoho.com/bookings/help/api/v1/fetch-staff.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
