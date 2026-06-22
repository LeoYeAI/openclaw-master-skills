---
name: mailgun
description: |
  Mailgun API integration with managed OAuth. Transactional email service for sending, receiving, and tracking emails.
  Use this skill when users want to send emails, manage domains, routes, templates, mailing lists, or suppressions in Mailgun.
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

# Mailgun

Access the Mailgun API with managed OAuth authentication. Send transactional emails, manage domains, routes, templates, mailing lists, suppressions, and webhooks.

## Quick Start

```bash
# List domains
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailgun/v3/domains')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/mailgun/v3/{resource}
```

Replace `{resource}` with the actual Mailgun API endpoint path. The gateway proxies requests to `api.mailgun.net/v3` (US region) and automatically injects your OAuth token.

**Regional Note:** Mailgun has US and EU regions. The gateway defaults to US region (api.mailgun.net).

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

Manage your Mailgun OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=mailgun&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'mailgun'}).encode()
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
    "connection_id": "78b5a036-c621-40c2-b74b-276195735af2",
    "status": "ACTIVE",
    "creation_time": "2026-02-12T02:24:16.551210Z",
    "last_updated_time": "2026-02-12T02:25:03.542838Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "mailgun",
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

If you have multiple Mailgun connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/mailgun/v3/domains')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '78b5a036-c621-40c2-b74b-276195735af2')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

**Important:** Mailgun API uses `application/x-www-form-urlencoded` for POST/PUT requests, not JSON.

### Domains

#### List Domains

```bash
GET /mailgun/v3/domains
```

Returns all domains for the account.

#### Get Domain

```bash
GET /mailgun/v3/domains/{domain_name}
```

#### Create Domain

```bash
POST /mailgun/v3/domains
Content-Type: application/x-www-form-urlencoded

name=example.com&smtp_password=supersecret
```

#### Delete Domain

```bash
DELETE /mailgun/v3/domains/{domain_name}
```

### Messages

#### Send Message

```bash
POST /mailgun/v3/{domain_name}/messages
Content-Type: application/x-www-form-urlencoded

from=sender@example.com&to=recipient@example.com&subject=Hello&text=Hello World
```

Parameters:
- `from` (required) - Sender email address
- `to` (required) - Recipient(s), comma-separated
- `cc` - CC recipients
- `bcc` - BCC recipients
- `subject` (required) - Email subject
- `text` - Plain text body
- `html` - HTML body
- `template` - Name of stored template to use
- `o:tag` - Tag for tracking
- `o:tracking` - Enable/disable tracking (yes/no)
- `o:tracking-clicks` - Enable click tracking
- `o:tracking-opens` - Enable open tracking
- `h:X-Custom-Header` - Custom headers (prefix with h:)
- `v:custom-var` - Custom variables for templates (prefix with v:)

#### Send MIME Message

```bash
POST /mailgun/v3/{domain_name}/messages.mime
Content-Type: multipart/form-data

to=recipient@example.com&message=<MIME content>
```

### Events

#### List Events

```bash
GET /mailgun/v3/{domain_name}/events
```

Query parameters:
- `begin` - Start time (RFC 2822 or Unix timestamp)
- `end` - End time
- `ascending` - Sort order (yes/no)
- `limit` - Results per page (max 300)
- `event` - Filter by event type (accepted, delivered, failed, opened, clicked, unsubscribed, complained, stored)
- `from` - Filter by sender
- `to` - Filter by recipient
- `tags` - Filter by tags

### Routes

Routes are defined globally per account, not per domain.

#### List Routes

```bash
GET /mailgun/v3/routes
```

Query parameters:
- `skip` - Number of records to skip
- `limit` - Number of records to return

#### Create Route

```bash
POST /mailgun/v3/routes
Content-Type: application/x-www-form-urlencoded

priority=0&description=My Route&expression=match_recipient(".*@example.com")&action=forward("https://example.com/webhook")
```

Parameters:
- `priority` - Route priority (lower = higher priority)
- `description` - Route description
- `expression` - Filter expression (match_recipient, match_header, catch_all)
- `action` - Action(s) to take (forward, store, stop)

#### Get Route

```bash
GET /mailgun/v3/routes/{route_id}
```

#### Update Route

```bash
PUT /mailgun/v3/routes/{route_id}
Content-Type: application/x-www-form-urlencoded

priority=1&description=Updated Route
```

#### Delete Route

```bash
DELETE /mailgun/v3/routes/{route_id}
```

### Webhooks

#### List Webhooks

```bash
GET /mailgun/v3/domains/{domain_name}/webhooks
```

#### Create Webhook

```bash
POST /mailgun/v3/domains/{domain_name}/webhooks
Content-Type: application/x-www-form-urlencoded

id=delivered&url=https://example.com/webhook
```

Webhook types: `accepted`, `delivered`, `opened`, `clicked`, `unsubscribed`, `complained`, `permanent_fail`, `temporary_fail`

#### Get Webhook

```bash
GET /mailgun/v3/domains/{domain_name}/webhooks/{webhook_type}
```

#### Update Webhook

```bash
PUT /mailgun/v3/domains/{domain_name}/webhooks/{webhook_type}
Content-Type: application/x-www-form-urlencoded

url=https://example.com/new-webhook
```

#### Delete Webhook

```bash
DELETE /mailgun/v3/domains/{domain_name}/webhooks/{webhook_type}
```

### Templates

#### List Templates

```bash
GET /mailgun/v3/{domain_name}/templates
```

#### Create Template

```bash
POST /mailgun/v3/{domain_name}/templates
Content-Type: application/x-www-form-urlencoded

name=my-template&description=Welcome email&template=<html><body>Hello {{name}}</body></html>
```

#### Get Template

```bash
GET /mailgun/v3/{domain_name}/templates/{template_name}
```

#### Delete Template

```bash
DELETE /mailgun/v3/{domain_name}/templates/{template_name}
```

### Mailing Lists

#### List Mailing Lists

```bash
GET /mailgun/v3/lists/pages
```

#### Create Mailing List

```bash
POST /mailgun/v3/lists
Content-Type: application/x-www-form-urlencoded

address=newsletter@example.com&name=Newsletter&description=Monthly newsletter&access_level=readonly
```

Access levels: `readonly`, `members`, `everyone`

#### Get Mailing List

```bash
GET /mailgun/v3/lists/{list_address}
```

#### Update Mailing List

```bash
PUT /mailgun/v3/lists/{list_address}
Content-Type: application/x-www-form-urlencoded

name=Updated Newsletter
```

#### Delete Mailing List

```bash
DELETE /mailgun/v3/lists/{list_address}
```

### Mailing List Members

#### List Members

```bash
GET /mailgun/v3/lists/{list_address}/members/pages
```

#### Add Member

```bash
POST /mailgun/v3/lists/{list_address}/members
Content-Type: application/x-www-form-urlencoded

address=member@example.com&name=John Doe&subscribed=yes
```

#### Get Member

```bash
GET /mailgun/v3/lists/{list_address}/members/{member_address}
```

#### Update Member

```bash
PUT /mailgun/v3/lists/{list_address}/members/{member_address}
Content-Type: application/x-www-form-urlencoded

name=Jane Doe&subscribed=no
```

#### Delete Member

```bash
DELETE /mailgun/v3/lists/{list_address}/members/{member_address}
```

### Suppressions

#### Bounces

```bash
# List bounces
GET /mailgun/v3/{domain_name}/bounces

# Add bounce
POST /mailgun/v3/{domain_name}/bounces
Content-Type: application/x-www-form-urlencoded

address=bounced@example.com&code=550&error=Mailbox not found

# Get bounce
GET /mailgun/v3/{domain_name}/bounces/{address}

# Delete bounce
DELETE /mailgun/v3/{domain_name}/bounces/{address}
```

#### Unsubscribes

```bash
# List unsubscribes
GET /mailgun/v3/{domain_name}/unsubscribes

# Add unsubscribe
POST /mailgun/v3/{domain_name}/unsubscribes
Content-Type: application/x-www-form-urlencoded

address=unsubscribed@example.com&tag=*

# Delete unsubscribe
DELETE /mailgun/v3/{domain_name}/unsubscribes/{address}
```

#### Complaints

```bash
# List complaints
GET /mailgun/v3/{domain_name}/complaints

# Add complaint
POST /mailgun/v3/{domain_name}/complaints
Content-Type: application/x-www-form-urlencoded

address=complainer@example.com

# Delete complaint
DELETE /mailgun/v3/{domain_name}/complaints/{address}
```

#### Whitelists

```bash
# List whitelists
GET /mailgun/v3/{domain_name}/whitelists

# Add to whitelist
POST /mailgun/v3/{domain_name}/whitelists
Content-Type: application/x-www-form-urlencoded

address=allowed@example.com

# Delete from whitelist
DELETE /mailgun/v3/{domain_name}/whitelists/{address}
```

### Statistics

#### Get Stats

```bash
GET /mailgun/v3/{domain_name}/stats/total?event=delivered&event=opened
```

Query parameters:
- `event` (required) - Event type(s): accepted, delivered, failed, opened, clicked, unsubscribed, complained
- `start` - Start date (RFC 2822 or Unix timestamp)
- `end` - End date
- `resolution` - Data resolution (hour, day, month)
- `duration` - Period to show stats for

### Tags

#### List Tags

```bash
GET /mailgun/v3/{domain_name}/tags
```

#### Get Tag

```bash
GET /mailgun/v3/{domain_name}/tags/{tag_name}
```

#### Delete Tag

```bash
DELETE /mailgun/v3/{domain_name}/tags/{tag_name}
```

### IPs

#### List IPs

```bash
GET /mailgun/v3/ips
```

#### Get IP

```bash
GET /mailgun/v3/ips/{ip_address}
```

### Domain Tracking

#### Get Tracking Settings

```bash
GET /mailgun/v3/domains/{domain_name}/tracking
```

#### Update Open Tracking

```bash
PUT /mailgun/v3/domains/{domain_name}/tracking/open
Content-Type: application/x-www-form-urlencoded

active=yes
```

#### Update Click Tracking

```bash
PUT /mailgun/v3/domains/{domain_name}/tracking/click
Content-Type: application/x-www-form-urlencoded

active=yes
```

#### Update Unsubscribe Tracking

```bash
PUT /mailgun/v3/domains/{domain_name}/tracking/unsubscribe
Content-Type: application/x-www-form-urlencoded

active=yes&html_footer=<a href="%unsubscribe_url%">Unsubscribe</a>
```

### Credentials

#### List Credentials

```bash
GET /mailgun/v3/domains/{domain_name}/credentials
```

#### Create Credential

```bash
POST /mailgun/v3/domains/{domain_name}/credentials
Content-Type: application/x-www-form-urlencoded

login=alice&password=supersecret
```

#### Delete Credential

```bash
DELETE /mailgun/v3/domains/{domain_name}/credentials/{login}
```

## Pagination

Mailgun uses cursor-based pagination:

```json
{
  "items": [...],
  "paging": {
    "first": "https://api.mailgun.net/v3/.../pages?page=first&limit=100",
    "last": "https://api.mailgun.net/v3/.../pages?page=last&limit=100",
    "next": "https://api.mailgun.net/v3/.../pages?page=next&limit=100",
    "previous": "https://api.mailgun.net/v3/.../pages?page=prev&limit=100"
  }
}
```

Use `limit` parameter to control page size (default: 100).

## Code Examples

### JavaScript - Send Email

```javascript
const formData = new URLSearchParams();
formData.append('from', 'sender@example.com');
formData.append('to', 'recipient@example.com');
formData.append('subject', 'Hello');
formData.append('text', 'Hello World!');

const response = await fetch(
  'https://gateway.maton.ai/mailgun/v3/example.com/messages',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: formData.toString()
  }
);
const result = await response.json();
console.log(result);
```

### Python - Send Email

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/mailgun/v3/example.com/messages',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    data={
        'from': 'sender@example.com',
        'to': 'recipient@example.com',
        'subject': 'Hello',
        'text': 'Hello World!'
    }
)
print(response.json())
```

### Python - List Domains

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/mailgun/v3/domains',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
domains = response.json()
for domain in domains['items']:
    print(f"{domain['name']}: {domain['state']}")
```

### Python - Create Route and Webhook

```python
import os
import requests

headers = {'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
domain = 'example.com'

# Create route
route_response = requests.post(
    'https://gateway.maton.ai/mailgun/v3/routes',
    headers=headers,
    data={
        'priority': 0,
        'description': 'Forward to webhook',
        'expression': 'match_recipient("support@example.com")',
        'action': 'forward("https://myapp.com/incoming-email")'
    }
)
print(f"Route created: {route_response.json()}")

# Create webhook
webhook_response = requests.post(
    f'https://gateway.maton.ai/mailgun/v3/domains/{domain}/webhooks',
    headers=headers,
    data={
        'id': 'delivered',
        'url': 'https://myapp.com/webhook/delivered'
    }
)
print(f"Webhook created: {webhook_response.json()}")
```

## Notes

- Mailgun uses `application/x-www-form-urlencoded` for POST/PUT requests, not JSON
- Domain names must be included in most endpoint paths
- Routes are global (per account), not per domain
- Sandbox domains require authorized recipients for sending
- Dates are returned in RFC 2822 format
- Event logs are stored for at least 3 days
- Stats require at least one `event` parameter
- Templates use Handlebars syntax by default
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq`, environment variables may not expand correctly. Use Python examples instead.

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Sending | Varies by plan |
| API calls | No hard limit, but excessive requests may be throttled |

When rate limited, implement exponential backoff for retries.

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request or missing Mailgun connection |
| 401 | Invalid or missing Maton API key |
| 403 | Forbidden (e.g., sandbox domain restrictions) |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Mailgun API |

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

1. Ensure your URL path starts with `mailgun`. For example:

- Correct: `https://gateway.maton.ai/mailgun/v3/domains`
- Incorrect: `https://gateway.maton.ai/v3/domains`

### Troubleshooting: Sandbox Domain Restrictions

Sandbox domains can only send to authorized recipients. To send emails:
1. Upgrade to a paid plan, or
2. Add recipient addresses to authorized recipients in the Mailgun dashboard

## Resources

- [Mailgun API Documentation](https://documentation.mailgun.com/docs/mailgun/api-reference/api-overview)
- [Mailgun API Reference](https://mailgun-docs.redoc.ly/docs/mailgun/api-reference/intro/)
- [Mailgun Postman Collection](https://www.postman.com/mailgun/mailgun-s-public-workspace/documentation/ik8dl61/mailgun-api)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
