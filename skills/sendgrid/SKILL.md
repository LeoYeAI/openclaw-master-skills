---
name: sendgrid
description: |
  SendGrid API integration with managed OAuth. Send emails, manage contacts, templates, suppressions, and view email statistics.
  Use this skill when users want to send transactional or marketing emails, manage email lists, handle bounces/unsubscribes, or analyze email performance.
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

# SendGrid

Access the SendGrid API with managed OAuth authentication. Send transactional and marketing emails, manage contacts, templates, suppressions, and analyze email performance.

## Quick Start

```bash
# Get user profile
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/sendgrid/v3/user/profile')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/sendgrid/{native-api-path}
```

Replace `{native-api-path}` with the actual SendGrid API endpoint path. The gateway proxies requests to `api.sendgrid.com` and automatically injects your OAuth token.

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

Manage your SendGrid OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=sendgrid&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'sendgrid'}).encode()
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
    "connection_id": "943c6cd5-9a56-4f5b-8adf-ecd4a140049f",
    "status": "ACTIVE",
    "creation_time": "2026-02-11T10:53:41.817938Z",
    "last_updated_time": "2026-02-11T10:54:05.554084Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "sendgrid",
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

If you have multiple SendGrid connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/sendgrid/v3/user/profile')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '943c6cd5-9a56-4f5b-8adf-ecd4a140049f')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

All SendGrid API endpoints follow this pattern:

```
/sendgrid/v3/{resource}
```

---

## Mail Send

### Send Email

```bash
POST /sendgrid/v3/mail/send
Content-Type: application/json

{
  "personalizations": [
    {
      "to": [{"email": "recipient@example.com", "name": "Recipient"}],
      "subject": "Hello from SendGrid"
    }
  ],
  "from": {"email": "sender@example.com", "name": "Sender"},
  "content": [
    {
      "type": "text/plain",
      "value": "This is a test email."
    }
  ]
}
```

**With HTML content:**
```bash
POST /sendgrid/v3/mail/send
Content-Type: application/json

{
  "personalizations": [
    {
      "to": [{"email": "recipient@example.com"}],
      "subject": "HTML Email"
    }
  ],
  "from": {"email": "sender@example.com"},
  "content": [
    {
      "type": "text/html",
      "value": "<h1>Hello</h1><p>This is an HTML email.</p>"
    }
  ]
}
```

**With template:**
```bash
POST /sendgrid/v3/mail/send
Content-Type: application/json

{
  "personalizations": [
    {
      "to": [{"email": "recipient@example.com"}],
      "dynamic_template_data": {
        "first_name": "John",
        "order_id": "12345"
      }
    }
  ],
  "from": {"email": "sender@example.com"},
  "template_id": "d-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

---

## User Profile

### Get User Profile

```bash
GET /sendgrid/v3/user/profile
```

**Response:**
```json
{
  "type": "user",
  "userid": 59796657
}
```

### Get Account Details

```bash
GET /sendgrid/v3/user/account
```

---

## Marketing Contacts

### List Contacts

```bash
GET /sendgrid/v3/marketing/contacts
```

**Response:**
```json
{
  "result": [],
  "contact_count": 0,
  "_metadata": {
    "self": "https://api.sendgrid.com/v3/marketing/contacts"
  }
}
```

### Search Contacts

```bash
POST /sendgrid/v3/marketing/contacts/search
Content-Type: application/json

{
  "query": "email LIKE '%@example.com%'"
}
```

### Add/Update Contacts

```bash
PUT /sendgrid/v3/marketing/contacts
Content-Type: application/json

{
  "contacts": [
    {
      "email": "contact@example.com",
      "first_name": "John",
      "last_name": "Doe"
    }
  ]
}
```

**Response:**
```json
{
  "job_id": "2387e363-4104-4225-8960-4a5758492351"
}
```

**Note:** Contact operations are asynchronous. Use the job status endpoint to check progress.

### Get Import Job Status

```bash
GET /sendgrid/v3/marketing/contacts/imports/{job_id}
```

**Response:**
```json
{
  "id": "2387e363-4104-4225-8960-4a5758492351",
  "status": "pending",
  "job_type": "upsert_contacts",
  "results": {
    "requested_count": 1,
    "created_count": 1
  },
  "started_at": "2026-02-11T11:00:14Z"
}
```

### Delete Contacts

```bash
DELETE /sendgrid/v3/marketing/contacts?ids=contact_id_1,contact_id_2
```

### Get Contact by ID

```bash
GET /sendgrid/v3/marketing/contacts/{contact_id}
```

### Get Contact by Email

```bash
POST /sendgrid/v3/marketing/contacts/search/emails
Content-Type: application/json

{
  "emails": ["contact@example.com"]
}
```

---

## Marketing Lists

### List All Lists

```bash
GET /sendgrid/v3/marketing/lists
```

**Response:**
```json
{
  "result": [],
  "_metadata": {
    "self": "https://api.sendgrid.com/v3/marketing/lists?page_size=100&page_token="
  }
}
```

### Create List

```bash
POST /sendgrid/v3/marketing/lists
Content-Type: application/json

{
  "name": "My Contact List"
}
```

**Response:**
```json
{
  "name": "My Contact List",
  "id": "b050f139-4231-47c8-bf32-94ad76376d3b",
  "contact_count": 0,
  "_metadata": {
    "self": "https://api.sendgrid.com/v3/marketing/lists/b050f139-4231-47c8-bf32-94ad76376d3b"
  }
}
```

### Get List by ID

```bash
GET /sendgrid/v3/marketing/lists/{list_id}
```

### Update List

```bash
PATCH /sendgrid/v3/marketing/lists/{list_id}
Content-Type: application/json

{
  "name": "Updated List Name"
}
```

### Delete List

```bash
DELETE /sendgrid/v3/marketing/lists/{list_id}
```

### Add Contacts to List

```bash
PUT /sendgrid/v3/marketing/contacts
Content-Type: application/json

{
  "list_ids": ["list_id"],
  "contacts": [
    {"email": "contact@example.com"}
  ]
}
```

---

## Segments

### List Segments

```bash
GET /sendgrid/v3/marketing/segments
```

### Create Segment

```bash
POST /sendgrid/v3/marketing/segments
Content-Type: application/json

{
  "name": "Active Users",
  "query_dsl": "email_clicks > 0"
}
```

### Get Segment by ID

```bash
GET /sendgrid/v3/marketing/segments/{segment_id}
```

### Delete Segment

```bash
DELETE /sendgrid/v3/marketing/segments/{segment_id}
```

---

## Templates

### List Templates

```bash
GET /sendgrid/v3/templates
```

**With generation filter:**
```bash
GET /sendgrid/v3/templates?generations=dynamic
```

### Create Template

```bash
POST /sendgrid/v3/templates
Content-Type: application/json

{
  "name": "My Template",
  "generation": "dynamic"
}
```

**Response:**
```json
{
  "id": "d-ffcdb43ed8a04beba48a702e1717ddb5",
  "name": "My Template",
  "generation": "dynamic",
  "updated_at": "2026-02-11 11:00:20",
  "versions": []
}
```

### Get Template by ID

```bash
GET /sendgrid/v3/templates/{template_id}
```

### Update Template

```bash
PATCH /sendgrid/v3/templates/{template_id}
Content-Type: application/json

{
  "name": "Updated Template Name"
}
```

### Delete Template

```bash
DELETE /sendgrid/v3/templates/{template_id}
```

### Create Template Version

```bash
POST /sendgrid/v3/templates/{template_id}/versions
Content-Type: application/json

{
  "name": "Version 1",
  "subject": "{{subject}}",
  "html_content": "<html><body><h1>Hello {{name}}</h1></body></html>",
  "active": 1
}
```

**Response:**
```json
{
  "id": "54230a99-1e89-4edf-821d-d4925b40c64b",
  "template_id": "d-ffcdb43ed8a04beba48a702e1717ddb5",
  "active": 1,
  "name": "Version 1",
  "html_content": "<html><body><h1>Hello {{name}}</h1></body></html>",
  "plain_content": "Hello {{name}}",
  "generate_plain_content": true,
  "subject": "{{subject}}",
  "editor": "code",
  "thumbnail_url": "//..."
}
```

---

## Senders

### List Senders

```bash
GET /sendgrid/v3/senders
```

### Create Sender

```bash
POST /sendgrid/v3/senders
Content-Type: application/json

{
  "nickname": "My Sender",
  "from": {"email": "sender@example.com", "name": "Sender Name"},
  "reply_to": {"email": "reply@example.com", "name": "Reply To"},
  "address": "123 Main St",
  "city": "San Francisco",
  "country": "USA"
}
```

**Response:**
```json
{
  "id": 8513177,
  "nickname": "My Sender",
  "from": {"email": "sender@example.com", "name": "Sender Name"},
  "reply_to": {"email": "reply@example.com", "name": "Reply To"},
  "address": "123 Main St",
  "city": "San Francisco",
  "country": "USA",
  "verified": {"status": false, "reason": null},
  "updated_at": 1770786031,
  "created_at": 1770786031,
  "locked": false
}
```

**Note:** Sender verification is required before use. Check `verified.status`.

### Get Sender by ID

```bash
GET /sendgrid/v3/senders/{sender_id}
```

### Update Sender

```bash
PATCH /sendgrid/v3/senders/{sender_id}
Content-Type: application/json

{
  "nickname": "Updated Sender Name"
}
```

### Delete Sender

```bash
DELETE /sendgrid/v3/senders/{sender_id}
```

---

## Suppressions

### Bounces

```bash
# List bounces
GET /sendgrid/v3/suppression/bounces

# Get bounce by email
GET /sendgrid/v3/suppression/bounces/{email}

# Delete bounces
DELETE /sendgrid/v3/suppression/bounces
Content-Type: application/json

{
  "emails": ["bounce@example.com"]
}
```

### Blocks

```bash
# List blocks
GET /sendgrid/v3/suppression/blocks

# Get block by email
GET /sendgrid/v3/suppression/blocks/{email}

# Delete blocks
DELETE /sendgrid/v3/suppression/blocks
Content-Type: application/json

{
  "emails": ["blocked@example.com"]
}
```

### Invalid Emails

```bash
# List invalid emails
GET /sendgrid/v3/suppression/invalid_emails

# Delete invalid emails
DELETE /sendgrid/v3/suppression/invalid_emails
Content-Type: application/json

{
  "emails": ["invalid@example.com"]
}
```

### Spam Reports

```bash
# List spam reports
GET /sendgrid/v3/suppression/spam_reports

# Delete spam reports
DELETE /sendgrid/v3/suppression/spam_reports
Content-Type: application/json

{
  "emails": ["spam@example.com"]
}
```

### Global Unsubscribes

```bash
# List global unsubscribes
GET /sendgrid/v3/suppression/unsubscribes

# Add to global unsubscribes
POST /sendgrid/v3/asm/suppressions/global
Content-Type: application/json

{
  "recipient_emails": ["unsubscribe@example.com"]
}
```

---

## Unsubscribe Groups (ASM)

### List Groups

```bash
GET /sendgrid/v3/asm/groups
```

### Create Group

```bash
POST /sendgrid/v3/asm/groups
Content-Type: application/json

{
  "name": "Weekly Newsletter",
  "description": "Weekly newsletter updates"
}
```

**Response:**
```json
{
  "name": "Weekly Newsletter",
  "id": 122741,
  "description": "Weekly newsletter updates",
  "is_default": false
}
```

### Get Group by ID

```bash
GET /sendgrid/v3/asm/groups/{group_id}
```

### Update Group

```bash
PATCH /sendgrid/v3/asm/groups/{group_id}
Content-Type: application/json

{
  "name": "Updated Group Name"
}
```

### Delete Group

```bash
DELETE /sendgrid/v3/asm/groups/{group_id}
```

### Add Suppressions to Group

```bash
POST /sendgrid/v3/asm/groups/{group_id}/suppressions
Content-Type: application/json

{
  "recipient_emails": ["user@example.com"]
}
```

### List Suppressions in Group

```bash
GET /sendgrid/v3/asm/groups/{group_id}/suppressions
```

---

## Statistics

### Get Global Stats

```bash
GET /sendgrid/v3/stats?start_date=2026-02-01
```

**With end date:**
```bash
GET /sendgrid/v3/stats?start_date=2026-02-01&end_date=2026-02-28
```

**Response:**
```json
[
  {
    "date": "2026-02-01",
    "stats": [
      {
        "metrics": {
          "blocks": 0,
          "bounce_drops": 0,
          "bounces": 0,
          "clicks": 0,
          "deferred": 0,
          "delivered": 0,
          "invalid_emails": 0,
          "opens": 0,
          "processed": 0,
          "requests": 0,
          "spam_report_drops": 0,
          "spam_reports": 0,
          "unique_clicks": 0,
          "unique_opens": 0,
          "unsubscribe_drops": 0,
          "unsubscribes": 0
        }
      }
    ]
  }
]
```

### Category Stats

```bash
GET /sendgrid/v3/categories/stats?start_date=2026-02-01&categories=category1,category2
```

### Mailbox Provider Stats

```bash
GET /sendgrid/v3/mailbox_providers/stats?start_date=2026-02-01
```

### Browser Stats

```bash
GET /sendgrid/v3/browsers/stats?start_date=2026-02-01
```

---

## API Keys

### List API Keys

```bash
GET /sendgrid/v3/api_keys
```

**Response:**
```json
{
  "result": [
    {
      "name": "MatonTest",
      "api_key_id": "WJBgv5EKR8y0nn2F8Qfk5w"
    }
  ]
}
```

### Create API Key

```bash
POST /sendgrid/v3/api_keys
Content-Type: application/json

{
  "name": "New API Key",
  "scopes": ["mail.send", "alerts.read"]
}
```

### Get API Key by ID

```bash
GET /sendgrid/v3/api_keys/{api_key_id}
```

### Update API Key

```bash
PATCH /sendgrid/v3/api_keys/{api_key_id}
Content-Type: application/json

{
  "name": "Updated Key Name"
}
```

### Delete API Key

```bash
DELETE /sendgrid/v3/api_keys/{api_key_id}
```

---

## Pagination

SendGrid uses token-based pagination for marketing endpoints:

```bash
GET /sendgrid/v3/marketing/lists?page_size=100&page_token={token}
```

**Response includes:**
```json
{
  "result": [...],
  "_metadata": {
    "self": "https://api.sendgrid.com/v3/marketing/lists?page_size=100&page_token=",
    "next": "https://api.sendgrid.com/v3/marketing/lists?page_size=100&page_token=abc123"
  }
}
```

For suppression endpoints, use `limit` and `offset`:

```bash
GET /sendgrid/v3/suppression/bounces?limit=100&offset=0
```

## Code Examples

### JavaScript

```javascript
// Send an email
const response = await fetch(
  'https://gateway.maton.ai/sendgrid/v3/mail/send',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      personalizations: [{
        to: [{email: 'recipient@example.com'}],
        subject: 'Hello'
      }],
      from: {email: 'sender@example.com'},
      content: [{type: 'text/plain', value: 'Hello World'}]
    })
  }
);
```

### Python

```python
import os
import requests

# Get email stats
response = requests.get(
    'https://gateway.maton.ai/sendgrid/v3/stats',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'start_date': '2026-02-01'}
)
data = response.json()
for day in data:
    metrics = day['stats'][0]['metrics']
    print(f"{day['date']}: {metrics['delivered']} delivered, {metrics['opens']} opens")
```

## Notes

- All requests use JSON content type
- Dates are in YYYY-MM-DD format
- Template IDs for dynamic templates start with `d-`
- Mail send returns 202 Accepted on success (not 200)
- Marketing contact operations are asynchronous - use job status endpoints
- Suppression endpoints support date filtering with `start_time` and `end_time` (Unix timestamps)
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or validation error |
| 401 | Invalid or missing Maton API key |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 429 | Rate limited |
| 500 | Internal server error |

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

1. Ensure your URL path starts with `sendgrid`. For example:

- Correct: `https://gateway.maton.ai/sendgrid/v3/user/profile`
- Incorrect: `https://gateway.maton.ai/v3/user/profile`

## Resources

- [SendGrid API Documentation](https://www.twilio.com/docs/sendgrid/api-reference)
- [Mail Send API](https://www.twilio.com/docs/sendgrid/api-reference/mail-send)
- [Marketing Campaigns API](https://www.twilio.com/docs/sendgrid/api-reference/contacts)
- [Suppressions Overview](https://www.twilio.com/docs/sendgrid/api-reference/suppressions)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
