---
name: mailchimp
description: |
  Mailchimp Marketing API integration with managed OAuth. Access audiences, campaigns, templates, automations, reports, and manage subscribers. Use this skill when users want to manage email marketing, subscriber lists, or automate email campaigns. For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
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

# Mailchimp

Access the Mailchimp Marketing API with managed OAuth authentication. Manage audiences, campaigns, templates, automations, reports, and subscribers for email marketing.

## Quick Start

```bash
# List all audiences
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/lists')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/mailchimp/{native-api-path}
```

Replace `{native-api-path}` with the actual Mailchimp API endpoint path (e.g., `3.0/lists`). The gateway proxies requests to your Mailchimp data center and automatically injects your OAuth token.

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

Manage your Mailchimp OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=mailchimp&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'mailchimp'}).encode()
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
    "app": "mailchimp",
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

If you have multiple Mailchimp connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/lists')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Lists (Audiences)

Within the Mailchimp app, "audience" is the common term, but the API uses "lists" for endpoints.

#### Get All Lists

```bash
GET /mailchimp/3.0/lists
```

Query parameters:
- `count` - Number of records to return (default 10, max 1000)
- `offset` - Number of records to skip (for pagination)
- `fields` - Comma-separated list of fields to include
- `exclude_fields` - Comma-separated list of fields to exclude

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/lists?count=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "lists": [
    {
      "id": "abc123def4",
      "name": "Newsletter Subscribers",
      "contact": {
        "company": "Acme Corp",
        "address1": "123 Main St"
      },
      "stats": {
        "member_count": 5000,
        "unsubscribe_count": 100,
        "open_rate": 0.25
      }
    }
  ],
  "total_items": 1
}
```

#### Get a List

```bash
GET /mailchimp/3.0/lists/{list_id}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/lists/abc123def4')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create a List

```bash
POST /mailchimp/3.0/lists
Content-Type: application/json

{
  "name": "Newsletter",
  "contact": {
    "company": "Acme Corp",
    "address1": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "country": "US"
  },
  "permission_reminder": "You signed up for our newsletter",
  "campaign_defaults": {
    "from_name": "Acme Corp",
    "from_email": "newsletter@acme.com",
    "subject": "",
    "language": "en"
  },
  "email_type_option": true
}
```

#### Update a List

```bash
PATCH /mailchimp/3.0/lists/{list_id}
```

#### Delete a List

```bash
DELETE /mailchimp/3.0/lists/{list_id}
```

### List Members (Subscribers)

Members are contacts within an audience. The API uses MD5 hash of the lowercase email address as the subscriber identifier.

#### Get List Members

```bash
GET /mailchimp/3.0/lists/{list_id}/members
```

Query parameters:
- `status` - Filter by subscription status (subscribed, unsubscribed, cleaned, pending, transactional)
- `count` - Number of records to return
- `offset` - Number of records to skip

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/lists/abc123def4/members?status=subscribed&count=50')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "members": [
    {
      "id": "f4b7c8d9e0",
      "email_address": "john@example.com",
      "status": "subscribed",
      "merge_fields": {
        "FNAME": "John",
        "LNAME": "Doe"
      },
      "tags": [
        {"id": 1, "name": "VIP"}
      ]
    }
  ],
  "total_items": 500
}
```

#### Get a Member

```bash
GET /mailchimp/3.0/lists/{list_id}/members/{subscriber_hash}
```

The `subscriber_hash` is the MD5 hash of the lowercase email address.

**Example:**

```bash
# For email "john@example.com", subscriber_hash = md5("john@example.com")
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/lists/abc123def4/members/b4c9a0d1e2f3g4h5')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Add a Member

```bash
POST /mailchimp/3.0/lists/{list_id}/members
Content-Type: application/json

{
  "email_address": "newuser@example.com",
  "status": "subscribed",
  "merge_fields": {
    "FNAME": "Jane",
    "LNAME": "Smith"
  },
  "tags": ["Newsletter", "Premium"]
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'email_address': 'newuser@example.com', 'status': 'subscribed', 'merge_fields': {'FNAME': 'Jane', 'LNAME': 'Smith'}}).encode()
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/lists/abc123def4/members', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update a Member

```bash
PATCH /mailchimp/3.0/lists/{list_id}/members/{subscriber_hash}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'merge_fields': {'FNAME': 'Jane', 'LNAME': 'Doe'}}).encode()
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/lists/abc123def4/members/b4c9a0d1e2f3g4h5', data=data, method='PATCH')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Add or Update a Member (Upsert)

```bash
PUT /mailchimp/3.0/lists/{list_id}/members/{subscriber_hash}
Content-Type: application/json

{
  "email_address": "user@example.com",
  "status_if_new": "subscribed",
  "merge_fields": {
    "FNAME": "Jane",
    "LNAME": "Smith"
  }
}
```

Creates a new member or updates an existing one based on the email hash. Use `status_if_new` to set the status when creating a new member.

#### Delete a Member

Archives a member (can be re-added later):

```bash
DELETE /mailchimp/3.0/lists/{list_id}/members/{subscriber_hash}
```

Returns `204 No Content` on success.

To permanently delete (GDPR compliant):

```bash
POST /mailchimp/3.0/lists/{list_id}/members/{subscriber_hash}/actions/delete-permanent
```

### Member Tags

#### Get Member Tags

```bash
GET /mailchimp/3.0/lists/{list_id}/members/{subscriber_hash}/tags
```

#### Add or Remove Tags

```bash
POST /mailchimp/3.0/lists/{list_id}/members/{subscriber_hash}/tags
Content-Type: application/json

{
  "tags": [
    {"name": "VIP", "status": "active"},
    {"name": "Old Tag", "status": "inactive"}
  ]
}
```

Returns `204 No Content` on success.

### Segments

#### Get Segments

```bash
GET /mailchimp/3.0/lists/{list_id}/segments
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/lists/abc123def4/segments')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create a Segment

```bash
POST /mailchimp/3.0/lists/{list_id}/segments
Content-Type: application/json

{
  "name": "Active Subscribers",
  "options": {
    "match": "all",
    "conditions": [
      {
        "condition_type": "EmailActivity",
        "field": "opened",
        "op": "date_within",
        "value": "30"
      }
    ]
  }
}
```

#### Update a Segment

```bash
PATCH /mailchimp/3.0/lists/{list_id}/segments/{segment_id}
```

#### Get Segment Members

```bash
GET /mailchimp/3.0/lists/{list_id}/segments/{segment_id}/members
```

#### Delete a Segment

```bash
DELETE /mailchimp/3.0/lists/{list_id}/segments/{segment_id}
```

Returns `204 No Content` on success.

### Campaigns

#### Get All Campaigns

```bash
GET /mailchimp/3.0/campaigns
```

Query parameters:
- `type` - Campaign type (regular, plaintext, absplit, rss, variate)
- `status` - Campaign status (save, paused, schedule, sending, sent)
- `list_id` - Filter by list ID
- `count` - Number of records to return
- `offset` - Number of records to skip

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/campaigns?status=sent&count=20')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "campaigns": [
    {
      "id": "campaign123",
      "type": "regular",
      "status": "sent",
      "settings": {
        "subject_line": "Monthly Newsletter",
        "from_name": "Acme Corp"
      },
      "send_time": "2025-02-01T10:00:00Z",
      "report_summary": {
        "opens": 1500,
        "clicks": 300,
        "open_rate": 0.30,
        "click_rate": 0.06
      }
    }
  ],
  "total_items": 50
}
```

#### Get a Campaign

```bash
GET /mailchimp/3.0/campaigns/{campaign_id}
```

#### Create a Campaign

```bash
POST /mailchimp/3.0/campaigns
Content-Type: application/json

{
  "type": "regular",
  "recipients": {
    "list_id": "abc123def4"
  },
  "settings": {
    "subject_line": "Your Monthly Update",
    "from_name": "Acme Corp",
    "reply_to": "hello@acme.com"
  }
}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'type': 'regular', 'recipients': {'list_id': 'abc123def4'}, 'settings': {'subject_line': 'February Newsletter', 'from_name': 'Acme Corp', 'reply_to': 'newsletter@acme.com'}}).encode()
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/campaigns', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update a Campaign

```bash
PATCH /mailchimp/3.0/campaigns/{campaign_id}
```

#### Delete a Campaign

```bash
DELETE /mailchimp/3.0/campaigns/{campaign_id}
```

Returns `204 No Content` on success.

#### Get Campaign Content

```bash
GET /mailchimp/3.0/campaigns/{campaign_id}/content
```

#### Set Campaign Content

```bash
PUT /mailchimp/3.0/campaigns/{campaign_id}/content
Content-Type: application/json

{
  "html": "<html><body><h1>Hello!</h1><p>Newsletter content here.</p></body></html>",
  "plain_text": "Hello! Newsletter content here."
}
```

Or use a template:

```bash
PUT /mailchimp/3.0/campaigns/{campaign_id}/content
Content-Type: application/json

{
  "template": {
    "id": 12345,
    "sections": {
      "body": "<p>Custom content for the template section</p>"
    }
  }
}
```

#### Get Campaign Send Checklist

Check if a campaign is ready to send:

```bash
GET /mailchimp/3.0/campaigns/{campaign_id}/send-checklist
```

#### Send a Campaign

```bash
POST /mailchimp/3.0/campaigns/{campaign_id}/actions/send
```

#### Schedule a Campaign

```bash
POST /mailchimp/3.0/campaigns/{campaign_id}/actions/schedule
Content-Type: application/json

{
  "schedule_time": "2025-03-01T10:00:00+00:00"
}
```

#### Cancel a Scheduled Campaign

```bash
POST /mailchimp/3.0/campaigns/{campaign_id}/actions/cancel-send
```

### Templates

#### Get All Templates

```bash
GET /mailchimp/3.0/templates
```

Query parameters:
- `type` - Template type (user, base, gallery)
- `count` - Number of records to return
- `offset` - Number of records to skip

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/templates?type=user')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get a Template

```bash
GET /mailchimp/3.0/templates/{template_id}
```

#### Get Template Default Content

```bash
GET /mailchimp/3.0/templates/{template_id}/default-content
```

#### Create a Template

```bash
POST /mailchimp/3.0/templates
Content-Type: application/json

{
  "name": "Newsletter Template",
  "html": "<html><body mc:edit=\"body\"><h1>Title</h1><p>Content here</p></body></html>"
}
```

#### Update a Template

```bash
PATCH /mailchimp/3.0/templates/{template_id}
```

#### Delete a Template

```bash
DELETE /mailchimp/3.0/templates/{template_id}
```

Returns `204 No Content` on success.

### Automations

Mailchimp's classic automations let you build email series triggered by dates, activities, or events.

#### Get All Automations

```bash
GET /mailchimp/3.0/automations
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/automations')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get an Automation

```bash
GET /mailchimp/3.0/automations/{workflow_id}
```

#### Start an Automation

```bash
POST /mailchimp/3.0/automations/{workflow_id}/actions/start-all-emails
```

#### Pause an Automation

```bash
POST /mailchimp/3.0/automations/{workflow_id}/actions/pause-all-emails
```

#### Get Automation Emails

```bash
GET /mailchimp/3.0/automations/{workflow_id}/emails
```

#### Add Subscriber to Automation Queue

Manually add a subscriber to an automation workflow:

```bash
POST /mailchimp/3.0/automations/{workflow_id}/emails/{workflow_email_id}/queue
Content-Type: application/json

{
  "email_address": "subscriber@example.com"
}
```

### Reports

#### Get Campaign Reports

```bash
GET /mailchimp/3.0/reports
```

Query parameters:
- `count` - Number of records to return
- `offset` - Number of records to skip
- `type` - Campaign type

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/reports?count=20')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "reports": [
    {
      "id": "campaign123",
      "campaign_title": "Monthly Newsletter",
      "emails_sent": 5000,
      "opens": {
        "opens_total": 1500,
        "unique_opens": 1200,
        "open_rate": 0.24
      },
      "clicks": {
        "clicks_total": 450,
        "unique_clicks": 300,
        "click_rate": 0.06
      },
      "unsubscribed": 10,
      "bounce_rate": 0.02
    }
  ]
}
```

#### Get Campaign Report

```bash
GET /mailchimp/3.0/reports/{campaign_id}
```

#### Get Campaign Open Details

```bash
GET /mailchimp/3.0/reports/{campaign_id}/open-details
```

#### Get Campaign Click Details

```bash
GET /mailchimp/3.0/reports/{campaign_id}/click-details
```

#### Get List Activity

```bash
GET /mailchimp/3.0/lists/{list_id}/activity
```

Returns recent daily aggregated activity stats (unsubscribes, signups, opens, clicks) for up to 180 days.

### Batch Operations

Process multiple operations in a single call.

#### Create Batch Operation

```bash
POST /mailchimp/3.0/batches
Content-Type: application/json

{
  "operations": [
    {
      "method": "POST",
      "path": "/lists/abc123def4/members",
      "body": "{\"email_address\":\"user1@example.com\",\"status\":\"subscribed\"}"
    },
    {
      "method": "POST",
      "path": "/lists/abc123def4/members",
      "body": "{\"email_address\":\"user2@example.com\",\"status\":\"subscribed\"}"
    }
  ]
}
```

#### Get Batch Status

```bash
GET /mailchimp/3.0/batches/{batch_id}
```

#### List All Batches

```bash
GET /mailchimp/3.0/batches
```

#### Delete a Batch

```bash
DELETE /mailchimp/3.0/batches/{batch_id}
```

Returns `204 No Content` on success.

## Pagination

Mailchimp uses offset-based pagination:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailchimp/3.0/lists?count=50&offset=100')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

Response includes `total_items` for calculating total pages:

```json
{
  "lists": [...],
  "total_items": 250
}
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/mailchimp/3.0/lists',
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
import hashlib

# Get lists
response = requests.get(
    'https://gateway.maton.ai/mailchimp/3.0/lists',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()

# Add a subscriber
list_id = 'abc123def4'
email = 'newuser@example.com'

response = requests.post(
    f'https://gateway.maton.ai/mailchimp/3.0/lists/{list_id}/members',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'email_address': email,
        'status': 'subscribed'
    }
)

# Get subscriber hash for updates
subscriber_hash = hashlib.md5(email.lower().encode()).hexdigest()
```

## Notes

- List IDs are 10-character alphanumeric strings
- Subscriber hashes are MD5 hashes of lowercase email addresses
- Timestamps are in ISO 8601 format
- The API has a 120-second timeout on calls
- Maximum 1000 records per request for list endpoints
- "Audience" and "list" are used interchangeably (app vs API terminology)
- "Contact" and "member" are used interchangeably (app vs API terminology)
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets (`fields[]`, `sort[]`, `records[]`) to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments. You may get "Invalid API key" errors when piping.

## Response Codes

| Status | Meaning |
|--------|---------|
| 200 | Success with response body |
| 204 | Success with no content (DELETE, some POST operations) |
| 400 | Bad request or missing Mailchimp connection |
| 401 | Invalid or missing Maton API key |
| 403 | Forbidden - insufficient permissions |
| 404 | Resource not found |
| 405 | Method not allowed |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Mailchimp API |

Mailchimp error responses include detailed information:

```json
{
  "type": "https://mailchimp.com/developer/marketing/docs/errors/",
  "title": "Invalid Resource",
  "status": 400,
  "detail": "The resource submitted could not be validated.",
  "instance": "abc123-def456",
  "errors": [
    {
      "field": "email_address",
      "message": "This value should be a valid email."
    }
  ]
}
```

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

1. Ensure your URL path starts with `mailchimp`. For example:

- Correct: `https://gateway.maton.ai/mailchimp/3.0/lists`
- Incorrect: `https://gateway.maton.ai/3.0/lists`

## Resources

- [Mailchimp Marketing API Documentation](https://mailchimp.com/developer/marketing/)
- [API Reference](https://mailchimp.com/developer/marketing/api/)
- [Quick Start Guide](https://mailchimp.com/developer/marketing/guides/quick-start/)
- [Release Notes](https://mailchimp.com/developer/release-notes/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
