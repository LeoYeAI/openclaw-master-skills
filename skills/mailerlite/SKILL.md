---
name: mailerlite
description: |
  MailerLite API integration with managed OAuth. Manage email subscribers, groups, campaigns, automations, and forms.
  Use this skill when users want to add subscribers, create email campaigns, manage groups, or work with MailerLite automations.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
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

# MailerLite

Access the MailerLite API with managed OAuth authentication. Manage subscribers, groups, campaigns, automations, forms, fields, segments, and webhooks.

## Quick Start

```bash
# List subscribers
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailerlite/api/subscribers?limit=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/mailerlite/{native-api-path}
```

Replace `{native-api-path}` with the actual MailerLite API endpoint path. The gateway proxies requests to `connect.mailerlite.com` and automatically injects your OAuth token.

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

Manage your MailerLite OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=mailerlite&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'mailerlite'}).encode()
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
    "app": "mailerlite",
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

If you have multiple MailerLite connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailerlite/api/subscribers')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Subscriber Operations

#### List Subscribers

```bash
GET /mailerlite/api/subscribers
```

Query parameters:
- `filter[status]` - Filter by status: `active`, `unsubscribed`, `unconfirmed`, `bounced`, `junk`
- `limit` - Results per page (default: 25)
- `cursor` - Pagination cursor
- `include` - Include related data: `groups`

#### Get Subscriber

```bash
GET /mailerlite/api/subscribers/{subscriber_id_or_email}
```

#### Create/Upsert Subscriber

```bash
POST /mailerlite/api/subscribers
Content-Type: application/json

{
  "email": "subscriber@example.com",
  "fields": {
    "name": "John Doe",
    "company": "Acme Inc"
  },
  "groups": ["12345678901234567"],
  "status": "active"
}
```

Returns 201 for new subscribers, 200 for updates.

#### Update Subscriber

```bash
PUT /mailerlite/api/subscribers/{subscriber_id}
Content-Type: application/json

{
  "fields": {
    "name": "Jane Doe"
  },
  "status": "active"
}
```

#### Delete Subscriber

```bash
DELETE /mailerlite/api/subscribers/{subscriber_id}
```

#### Get Subscriber Activity

```bash
GET /mailerlite/api/subscribers/{subscriber_id}/activity-log
```

Query parameters:
- `filter[log_name]` - Filter by activity type: `campaign_send`, `automation_email_sent`, `email_open`, `link_click`, `email_bounce`, `spam_complaint`, `unsubscribed`
- `limit` - Results per page (default: 100)
- `page` - Page number (starts from 1)

#### Forget Subscriber (GDPR)

```bash
POST /mailerlite/api/subscribers/{subscriber_id}/forget
```

### Group Operations

#### List Groups

```bash
GET /mailerlite/api/groups
```

Query parameters:
- `limit` - Results per page
- `page` - Page number (starts from 1)
- `filter[name]` - Filter by name (partial match)
- `sort` - Sort by: `name`, `total`, `open_rate`, `click_rate`, `created_at` (prepend `-` for descending)

#### Create Group

```bash
POST /mailerlite/api/groups
Content-Type: application/json

{
  "name": "Newsletter Subscribers"
}
```

#### Update Group

```bash
PUT /mailerlite/api/groups/{group_id}
Content-Type: application/json

{
  "name": "Updated Group Name"
}
```

#### Delete Group

```bash
DELETE /mailerlite/api/groups/{group_id}
```

#### Get Group Subscribers

```bash
GET /mailerlite/api/groups/{group_id}/subscribers
```

Query parameters:
- `filter[status]` - Filter by status: `active`, `unsubscribed`, `unconfirmed`, `bounced`, `junk`
- `limit` - Results per page (1-1000, default: 50)
- `cursor` - Pagination cursor

#### Assign Subscriber to Group

```bash
POST /mailerlite/api/subscribers/{subscriber_id}/groups/{group_id}
```

#### Remove Subscriber from Group

```bash
DELETE /mailerlite/api/subscribers/{subscriber_id}/groups/{group_id}
```

### Campaign Operations

#### List Campaigns

```bash
GET /mailerlite/api/campaigns
```

Query parameters:
- `filter[status]` - Filter by status: `sent`, `draft`, `ready`
- `filter[type]` - Filter by type: `regular`, `ab`, `resend`, `rss`
- `limit` - Results per page: 10, 25, 50, or 100 (default: 25)
- `page` - Page number (starts from 1)

#### Get Campaign

```bash
GET /mailerlite/api/campaigns/{campaign_id}
```

#### Create Campaign

```bash
POST /mailerlite/api/campaigns
Content-Type: application/json

{
  "name": "My Newsletter",
  "type": "regular",
  "emails": [
    {
      "subject": "Weekly Update",
      "from_name": "Newsletter",
      "from": "newsletter@example.com"
    }
  ],
  "groups": ["12345678901234567"]
}
```

#### Update Campaign

```bash
PUT /mailerlite/api/campaigns/{campaign_id}
Content-Type: application/json

{
  "name": "Updated Campaign Name",
  "emails": [
    {
      "subject": "New Subject Line",
      "from_name": "Newsletter",
      "from": "newsletter@example.com"
    }
  ]
}
```

Note: Only draft campaigns can be updated.

#### Schedule Campaign

```bash
POST /mailerlite/api/campaigns/{campaign_id}/schedule
Content-Type: application/json

{
  "delivery": "instant"
}
```

For scheduled delivery:
```json
{
  "delivery": "scheduled",
  "schedule": {
    "date": "2026-03-15",
    "hours": "10",
    "minutes": "30"
  }
}
```

#### Cancel Campaign

```bash
POST /mailerlite/api/campaigns/{campaign_id}/cancel
```

Reverts a ready campaign to draft status.

#### Delete Campaign

```bash
DELETE /mailerlite/api/campaigns/{campaign_id}
```

#### Get Campaign Subscriber Activity

```bash
GET /mailerlite/api/campaigns/{campaign_id}/reports/subscriber-activity
```

Query parameters:
- `filter[type]` - Filter by activity: `opened`, `unopened`, `clicked`, `unsubscribed`, `forwarded`, `hardbounced`, `softbounced`, `junk`
- `filter[search]` - Search by email
- `limit` - Results per page (10, 25, 50, or 100)
- `page` - Page number (starts from 1)

### Automation Operations

#### List Automations

```bash
GET /mailerlite/api/automations
```

Query parameters:
- `filter[enabled]` - Filter by status: `true` or `false`
- `filter[name]` - Filter by name
- `filter[group]` - Filter by group ID
- `page` - Page number (starts from 1)
- `limit` - Results per page (default: 10)

#### Get Automation

```bash
GET /mailerlite/api/automations/{automation_id}
```

#### Create Automation

```bash
POST /mailerlite/api/automations
Content-Type: application/json

{
  "name": "Welcome Series"
}
```

Creates a draft automation.

#### Get Automation Activity

```bash
GET /mailerlite/api/automations/{automation_id}/activity
```

Query parameters:
- `filter[status]` - Required: `completed`, `active`, `canceled`, `failed`
- `filter[date_from]` - Start date (Y-m-d)
- `filter[date_to]` - End date (Y-m-d)
- `filter[search]` - Search by email
- `page` - Page number (starts from 1)
- `limit` - Results per page (default: 10)

#### Delete Automation

```bash
DELETE /mailerlite/api/automations/{automation_id}
```

### Field Operations

#### List Fields

```bash
GET /mailerlite/api/fields
```

Query parameters:
- `limit` - Results per page (max 100)
- `page` - Page number (starts from 1)
- `filter[keyword]` - Filter by keyword (partial match)
- `filter[type]` - Filter by type: `text`, `number`, `date`
- `sort` - Sort by: `name`, `type` (prepend `-` for descending)

#### Create Field

```bash
POST /mailerlite/api/fields
Content-Type: application/json

{
  "name": "Company",
  "type": "text"
}
```

#### Update Field

```bash
PUT /mailerlite/api/fields/{field_id}
Content-Type: application/json

{
  "name": "Organization"
}
```

#### Delete Field

```bash
DELETE /mailerlite/api/fields/{field_id}
```

### Segment Operations

#### List Segments

```bash
GET /mailerlite/api/segments
```

Query parameters:
- `limit` - Results per page (max 250)
- `page` - Page number (starts from 1)

#### Get Segment Subscribers

```bash
GET /mailerlite/api/segments/{segment_id}/subscribers
```

Query parameters:
- `filter[status]` - Filter by status: `active`, `unsubscribed`, `unconfirmed`, `bounced`, `junk`
- `limit` - Results per page
- `cursor` - Pagination cursor

#### Update Segment

```bash
PUT /mailerlite/api/segments/{segment_id}
Content-Type: application/json

{
  "name": "High Engagement Subscribers"
}
```

#### Delete Segment

```bash
DELETE /mailerlite/api/segments/{segment_id}
```

### Form Operations

#### List Forms

```bash
GET /mailerlite/api/forms/{type}
```

Path parameters:
- `type` - Form type: `popup`, `embedded`, `promotion`

Query parameters:
- `limit` - Results per page
- `page` - Page number (starts from 1)
- `filter[name]` - Filter by name (partial match)
- `sort` - Sort by: `created_at`, `name`, `conversions_count`, `opens_count`, `visitors`, `conversion_rate`, `last_registration_at` (prepend `-` for descending)

#### Get Form

```bash
GET /mailerlite/api/forms/{form_id}
```

#### Update Form

```bash
PUT /mailerlite/api/forms/{form_id}
Content-Type: application/json

{
  "name": "Newsletter Signup"
}
```

#### Delete Form

```bash
DELETE /mailerlite/api/forms/{form_id}
```

#### Get Form Subscribers

```bash
GET /mailerlite/api/forms/{form_id}/subscribers
```

Query parameters:
- `filter[status]` - Filter by status: `active`, `unsubscribed`, `unconfirmed`, `bounced`, `junk`
- `limit` - Results per page (default: 25)
- `cursor` - Pagination cursor

### Webhook Operations

#### List Webhooks

```bash
GET /mailerlite/api/webhooks
```

#### Get Webhook

```bash
GET /mailerlite/api/webhooks/{webhook_id}
```

#### Create Webhook

```bash
POST /mailerlite/api/webhooks
Content-Type: application/json

{
  "name": "Subscriber Updates",
  "events": ["subscriber.created", "subscriber.updated"],
  "url": "https://example.com/webhook"
}
```

#### Update Webhook

```bash
PUT /mailerlite/api/webhooks/{webhook_id}
Content-Type: application/json

{
  "name": "Updated Webhook",
  "enabled": true
}
```

#### Delete Webhook

```bash
DELETE /mailerlite/api/webhooks/{webhook_id}
```

## Pagination

MailerLite uses cursor-based pagination for most endpoints and page-based pagination for some.

### Cursor-based Pagination

```bash
GET /mailerlite/api/subscribers?limit=25&cursor=eyJpZCI6MTIzNDU2fQ
```

Response includes pagination links:
```json
{
  "data": [...],
  "links": {
    "first": "https://connect.mailerlite.com/api/subscribers?cursor=...",
    "last": null,
    "prev": null,
    "next": "https://connect.mailerlite.com/api/subscribers?cursor=eyJpZCI6MTIzNDU2fQ"
  },
  "meta": {
    "path": "https://connect.mailerlite.com/api/subscribers",
    "per_page": 25,
    "next_cursor": "eyJpZCI6MTIzNDU2fQ",
    "prev_cursor": null
  }
}
```

### Page-based Pagination

```bash
GET /mailerlite/api/groups?limit=25&page=2
```

Response includes page metadata:
```json
{
  "data": [...],
  "meta": {
    "current_page": 2,
    "from": 26,
    "last_page": 4,
    "per_page": 25,
    "to": 50,
    "total": 100
  }
}
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/mailerlite/api/subscribers?limit=10',
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
    'https://gateway.maton.ai/mailerlite/api/subscribers',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'limit': 10}
)
data = response.json()
```

### Create Subscriber Example

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/mailerlite/api/subscribers',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'email': 'newuser@example.com',
        'fields': {'name': 'John Doe'},
        'status': 'active'
    }
)
data = response.json()
```

## Notes

- Rate limit: 120 requests per minute
- Subscriber emails are used as unique identifiers (POST creates or updates)
- Group names have a maximum length of 255 characters
- Only draft campaigns can be updated
- API versioning can be overridden via `X-Version: YYYY-MM-DD` header
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing MailerLite connection |
| 401 | Invalid or missing Maton API key |
| 403 | Forbidden - insufficient permissions |
| 404 | Resource not found |
| 422 | Validation error |
| 429 | Rate limited (120 req/min) |
| 4xx/5xx | Passthrough error from MailerLite API |

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

1. Ensure your URL path starts with `mailerlite`. For example:

- Correct: `https://gateway.maton.ai/mailerlite/api/subscribers`
- Incorrect: `https://gateway.maton.ai/api/subscribers`

## Resources

- [MailerLite API Documentation](https://developers.mailerlite.com/docs/)
- [MailerLite Subscribers API](https://developers.mailerlite.com/docs/subscribers.html)
- [MailerLite Groups API](https://developers.mailerlite.com/docs/groups.html)
- [MailerLite Campaigns API](https://developers.mailerlite.com/docs/campaigns.html)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
