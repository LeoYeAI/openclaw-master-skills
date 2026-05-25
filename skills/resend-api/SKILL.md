---
name: resend
description: |
  Resend API integration with managed authentication. Send transactional emails, manage domains, contacts, templates, and broadcasts.
  Use this skill when users want to send emails, manage email templates, create contact lists, or set up email broadcasts.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
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

# Resend

Access the Resend API with managed authentication. Send transactional emails, manage domains, contacts, templates, broadcasts, and webhooks.

## Quick Start

```bash
# List sent emails
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/emails')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/resend/{endpoint}
```

The gateway proxies requests to `api.resend.com` and automatically injects your API key.

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

Manage your Resend connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=resend&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'resend'}).encode()
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
    "connection_id": "528c8f70-23f4-46d5-bd9f-01d0d043e573",
    "status": "ACTIVE",
    "creation_time": "2026-03-13T00:19:36.809599Z",
    "last_updated_time": "2026-03-13T09:59:08.443568Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "resend",
    "metadata": {},
    "method": "API_KEY"
  }
}
```

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

If you have multiple Resend connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/emails')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '528c8f70-23f4-46d5-bd9f-01d0d043e573')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Emails

Send and manage transactional emails.

#### Send Email

```bash
POST /resend/emails
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    'from': 'you@yourdomain.com',
    'to': ['recipient@example.com'],
    'subject': 'Hello from Resend',
    'html': '<p>Welcome to our service!</p>'
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/resend/emails', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from` | string | Yes | Sender email (must be from verified domain) |
| `to` | string[] | Yes | Recipient email addresses |
| `subject` | string | Yes | Email subject |
| `html` | string | No | HTML content |
| `text` | string | No | Plain text content |
| `cc` | string[] | No | CC recipients |
| `bcc` | string[] | No | BCC recipients |
| `reply_to` | string[] | No | Reply-to addresses |
| `attachments` | object[] | No | File attachments |
| `tags` | object[] | No | Email tags for tracking |
| `scheduled_at` | string | No | ISO 8601 datetime for scheduled send |

**Response:**
```json
{
  "id": "a52ac168-338f-4fbc-9354-e6049b193d99"
}
```

#### Send Batch Emails

```bash
POST /resend/emails/batch
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps([
    {'from': 'you@yourdomain.com', 'to': ['a@example.com'], 'subject': 'Email 1', 'text': 'Content 1'},
    {'from': 'you@yourdomain.com', 'to': ['b@example.com'], 'subject': 'Email 2', 'text': 'Content 2'}
]).encode()
req = urllib.request.Request('https://gateway.maton.ai/resend/emails/batch', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### List Emails

```bash
GET /resend/emails
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/emails')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "id": "a52ac168-338f-4fbc-9354-e6049b193d99",
      "from": "you@yourdomain.com",
      "to": ["recipient@example.com"],
      "subject": "Hello from Resend",
      "created_at": "2026-03-13T10:00:00.000Z"
    }
  ]
}
```

#### Get Email

```bash
GET /resend/emails/{email_id}
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/emails/{email_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Update Email

```bash
PATCH /resend/emails/{email_id}
```

#### Cancel Scheduled Email

```bash
DELETE /resend/emails/{email_id}
```

### Domains

Manage sending domains.

#### List Domains

```bash
GET /resend/domains
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/domains')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "data": [
    {
      "id": "5eb93a2e-e849-40a1-81b7-ed0fb574ddd8",
      "name": "yourdomain.com",
      "status": "verified",
      "created_at": "2026-03-13T10:00:00.000Z"
    }
  ]
}
```

#### Create Domain

```bash
POST /resend/domains
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'name': 'yourdomain.com'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/resend/domains', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "id": "5eb93a2e-e849-40a1-81b7-ed0fb574ddd8",
  "name": "yourdomain.com",
  "status": "pending",
  "records": [
    {"type": "MX", "name": "...", "value": "..."},
    {"type": "TXT", "name": "...", "value": "..."}
  ]
}
```

#### Get Domain

```bash
GET /resend/domains/{domain_id}
```

#### Update Domain

```bash
PATCH /resend/domains/{domain_id}
```

#### Delete Domain

```bash
DELETE /resend/domains/{domain_id}
```

#### Verify Domain

```bash
POST /resend/domains/{domain_id}/verify
```

### Contacts

Manage contact lists.

#### List Contacts

```bash
GET /resend/contacts
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/contacts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Contact

```bash
POST /resend/contacts
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    'email': 'contact@example.com',
    'first_name': 'John',
    'last_name': 'Doe'
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/resend/contacts', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "id": "3cdc4bbb-0c79-46e5-be2a-48a89c29203d"
}
```

#### Get Contact

```bash
GET /resend/contacts/{contact_id}
```

#### Update Contact

```bash
PATCH /resend/contacts/{contact_id}
```

#### Delete Contact

```bash
DELETE /resend/contacts/{contact_id}
```

### Templates

Manage email templates.

#### List Templates

```bash
GET /resend/templates
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/templates')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Template

```bash
POST /resend/templates
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    'name': 'Welcome Email',
    'subject': 'Welcome to our service!',
    'html': '<h1>Welcome!</h1><p>Thanks for signing up.</p>'
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/resend/templates', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "id": "9b84737c-8a80-448a-aca1-c6e1fddd0f23"
}
```

#### Get Template

```bash
GET /resend/templates/{template_id}
```

#### Update Template

```bash
PATCH /resend/templates/{template_id}
```

#### Delete Template

```bash
DELETE /resend/templates/{template_id}
```

#### Publish Template

```bash
POST /resend/templates/{template_id}/publish
```

#### Duplicate Template

```bash
POST /resend/templates/{template_id}/duplicate
```

### Segments

Create audience segments for targeting.

#### List Segments

```bash
GET /resend/segments
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/segments')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Segment

```bash
POST /resend/segments
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    'name': 'Active Users',
    'filter': {
        'and': [
            {'field': 'email', 'operator': 'contains', 'value': '@'}
        ]
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/resend/segments', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Segment

```bash
GET /resend/segments/{segment_id}
```

#### Delete Segment

```bash
DELETE /resend/segments/{segment_id}
```

### Broadcasts

Send emails to segments.

#### List Broadcasts

```bash
GET /resend/broadcasts
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/broadcasts')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Broadcast

```bash
POST /resend/broadcasts
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    'name': 'Weekly Newsletter',
    'from': 'newsletter@yourdomain.com',
    'subject': 'This Week\'s Update',
    'html': '<h1>Weekly Update</h1><p>Here\'s what happened...</p>',
    'segment_id': 'segment-uuid'
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/resend/broadcasts', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Get Broadcast

```bash
GET /resend/broadcasts/{broadcast_id}
```

#### Update Broadcast

```bash
PATCH /resend/broadcasts/{broadcast_id}
```

#### Delete Broadcast

```bash
DELETE /resend/broadcasts/{broadcast_id}
```

#### Send Broadcast

```bash
POST /resend/broadcasts/{broadcast_id}/send
```

### Webhooks

Configure event notifications.

#### List Webhooks

```bash
GET /resend/webhooks
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/webhooks')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create Webhook

```bash
POST /resend/webhooks
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    'endpoint': 'https://yoursite.com/webhook',
    'events': ['email.delivered', 'email.bounced', 'email.opened']
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/resend/webhooks', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Webhook Events:**
- `email.sent` - Email was sent
- `email.delivered` - Email was delivered
- `email.opened` - Email was opened
- `email.clicked` - Link in email was clicked
- `email.bounced` - Email bounced
- `email.complained` - Recipient marked as spam

#### Get Webhook

```bash
GET /resend/webhooks/{webhook_id}
```

#### Update Webhook

```bash
PATCH /resend/webhooks/{webhook_id}
```

#### Delete Webhook

```bash
DELETE /resend/webhooks/{webhook_id}
```

### API Keys

Manage API keys.

#### List API Keys

```bash
GET /resend/api-keys
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/resend/api-keys')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Create API Key

```bash
POST /resend/api-keys
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'name': 'Production Key'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/resend/api-keys', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

> **Note:** The actual API key value is only returned once on creation.

#### Delete API Key

```bash
DELETE /resend/api-keys/{api_key_id}
```

### Topics

Manage subscription topics.

#### List Topics

```bash
GET /resend/topics
```

#### Create Topic

```bash
POST /resend/topics
```

**Example:**

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    'name': 'Newsletter',
    'default_subscription': 'subscribed'
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/resend/topics', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

> **Note:** `default_subscription` is required. Values: `subscribed` or `unsubscribed`.

#### Get Topic

```bash
GET /resend/topics/{topic_id}
```

#### Update Topic

```bash
PATCH /resend/topics/{topic_id}
```

#### Delete Topic

```bash
DELETE /resend/topics/{topic_id}
```

### Contact Properties

Manage custom contact properties.

#### List Contact Properties

```bash
GET /resend/contact-properties
```

#### Create Contact Property

```bash
POST /resend/contact-properties
```

#### Get Contact Property

```bash
GET /resend/contact-properties/{property_id}
```

#### Update Contact Property

```bash
PATCH /resend/contact-properties/{property_id}
```

#### Delete Contact Property

```bash
DELETE /resend/contact-properties/{property_id}
```

## Code Examples

### JavaScript

```javascript
// Send an email
const response = await fetch('https://gateway.maton.ai/resend/emails', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    from: 'you@yourdomain.com',
    to: ['recipient@example.com'],
    subject: 'Hello!',
    html: '<p>Welcome!</p>'
  })
});
const data = await response.json();
console.log(data.id);
```

### Python

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/resend/emails',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'from': 'you@yourdomain.com',
        'to': ['recipient@example.com'],
        'subject': 'Hello!',
        'html': '<p>Welcome!</p>'
    }
)
email = response.json()
print(f"Email sent: {email['id']}")
```

## Notes

- Sending emails requires a verified domain
- Rate limit: 2 requests per second
- Batch emails accept up to 100 emails per request
- Scheduled emails can be set up to 7 days in advance
- Attachments support base64 encoded content or URLs
- The `from` address must use a verified domain
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or missing Resend connection |
| 401 | Invalid or missing Maton API key |
| 403 | Domain not verified or permission denied |
| 404 | Resource not found |
| 422 | Validation error (missing required fields) |
| 429 | Rate limited (2 req/sec) |
| 4xx/5xx | Passthrough error from Resend API |

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

### Troubleshooting: Domain Not Verified

To send emails, you must first add and verify a domain:

1. Create a domain: `POST /resend/domains`
2. Add the DNS records provided in the response
3. Verify the domain: `POST /resend/domains/{id}/verify`

## Resources

- [Resend API Documentation](https://resend.com/docs/api-reference/introduction)
- [Resend Dashboard](https://resend.com)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
