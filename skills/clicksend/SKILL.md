---
name: clicksend
description: |
  ClickSend API integration with managed authentication. Send SMS, MMS, and voice messages, manage contacts and lists.
  Use this skill when users want to send text messages, make voice calls, manage contact lists, or track message delivery.
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

# ClickSend

Access the ClickSend API with managed authentication. Send SMS, MMS, and voice messages, manage contacts and lists, and track message delivery.

## Quick Start

```bash
# Get account info
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clicksend/v3/account')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/clicksend/{native-api-path}
```

Replace `{native-api-path}` with the actual ClickSend API endpoint path. The gateway proxies requests to `rest.clicksend.com` and automatically injects your authentication.

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

Manage your ClickSend connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=clicksend&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'clicksend'}).encode()
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
    "connection_id": "37beee67-29f7-43b6-b0b2-5f0f7a5d6440",
    "status": "ACTIVE",
    "creation_time": "2026-02-10T10:04:12.418030Z",
    "last_updated_time": "2026-02-10T10:06:17.059090Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "clicksend",
    "metadata": {}
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

If you have multiple ClickSend connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/clicksend/v3/account')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '37beee67-29f7-43b6-b0b2-5f0f7a5d6440')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Response Format

All ClickSend API responses follow this structure:

```json
{
  "http_code": 200,
  "response_code": "SUCCESS",
  "response_msg": "Description of the result",
  "data": { ... }
}
```

---

## Account

### Get Account

```bash
GET /clicksend/v3/account
```

**Response:**
```json
{
  "http_code": 200,
  "response_code": "SUCCESS",
  "response_msg": "Here's your account",
  "data": {
    "user_id": 672721,
    "username": "user@example.com",
    "user_email": "user@example.com",
    "balance": "2.005718",
    "user_phone": "+18019234886",
    "user_first_name": "John",
    "user_last_name": "Doe",
    "country": "US",
    "default_country_sms": "US",
    "timezone": "America/Chicago",
    "_currency": {
      "currency_name_short": "USD",
      "currency_prefix_d": "$"
    }
  }
}
```

---

## SMS

### Send SMS

```bash
POST /clicksend/v3/sms/send
Content-Type: application/json

{
  "messages": [
    {
      "to": "+15551234567",
      "body": "Hello from ClickSend!",
      "source": "api"
    }
  ]
}
```

**Parameters:**

| Field | Type | Description |
|-------|------|-------------|
| `to` | string | Recipient phone number (E.164 format) |
| `body` | string | SMS message content |
| `source` | string | Source identifier (e.g., "api", "sdk") |
| `from` | string | Sender ID (optional) |
| `schedule` | int | Unix timestamp for scheduled send (optional) |
| `custom_string` | string | Custom reference (optional) |

### Get SMS Price

```bash
POST /clicksend/v3/sms/price
Content-Type: application/json

{
  "messages": [
    {
      "to": "+15551234567",
      "body": "Test message",
      "source": "api"
    }
  ]
}
```

### SMS History

```bash
GET /clicksend/v3/sms/history
```

**Query Parameters:**

| Parameter | Description |
|-----------|-------------|
| `date_from` | Unix timestamp for start date |
| `date_to` | Unix timestamp for end date |
| `page` | Page number (default: 1) |
| `limit` | Results per page (default: 15) |

### Inbound SMS

```bash
GET /clicksend/v3/sms/inbound
```

### SMS Receipts (Delivery Reports)

```bash
GET /clicksend/v3/sms/receipts
```

### Cancel Scheduled SMS

```bash
PUT /clicksend/v3/sms/{message_id}/cancel
```

### Cancel All Scheduled SMS

```bash
PUT /clicksend/v3/sms/cancel-all
```

---

## SMS Templates

### List Templates

```bash
GET /clicksend/v3/sms/templates
```

**Response:**
```json
{
  "http_code": 200,
  "response_code": "SUCCESS",
  "response_msg": "Here are your templates.",
  "data": {
    "total": 1,
    "per_page": 15,
    "current_page": 1,
    "data": [
      {
        "template_id": 632497,
        "body": "Hello {name}, this is a test message.",
        "template_name": "Test Template"
      }
    ]
  }
}
```

### Create Template

```bash
POST /clicksend/v3/sms/templates
Content-Type: application/json

{
  "template_name": "Welcome Message",
  "body": "Hello {name}, welcome to our service!"
}
```

### Update Template

```bash
PUT /clicksend/v3/sms/templates/{template_id}
Content-Type: application/json

{
  "template_name": "Updated Template",
  "body": "Updated message content"
}
```

### Delete Template

```bash
DELETE /clicksend/v3/sms/templates/{template_id}
```

---

## MMS

### Send MMS

```bash
POST /clicksend/v3/mms/send
Content-Type: application/json

{
  "messages": [
    {
      "to": "+15551234567",
      "body": "Check out this image!",
      "media_file": "https://example.com/image.jpg",
      "source": "api"
    }
  ]
}
```

### MMS History

```bash
GET /clicksend/v3/mms/history
```

### Get MMS Price

```bash
POST /clicksend/v3/mms/price
Content-Type: application/json

{
  "messages": [...]
}
```

### MMS Receipts

```bash
GET /clicksend/v3/mms/receipts
```

---

## Voice

### Send Voice Message

```bash
POST /clicksend/v3/voice/send
Content-Type: application/json

{
  "messages": [
    {
      "to": "+15551234567",
      "body": "Hello, this is a voice message.",
      "voice": "female",
      "lang": "en-us",
      "source": "api"
    }
  ]
}
```

**Voice Parameters:**

| Field | Description |
|-------|-------------|
| `to` | Recipient phone number |
| `body` | Text to be spoken |
| `voice` | Voice gender: `male` or `female` |
| `lang` | Language code (e.g., `en-us`, `en-gb`, `de-de`) |
| `schedule` | Unix timestamp for scheduled call |
| `require_input` | Require keypad input (0-1) |
| `machine_detection` | Detect answering machine (0-1) |

### Available Languages

```bash
GET /clicksend/v3/voice/lang
```

Returns list of supported languages with codes and available genders.

### Voice History

```bash
GET /clicksend/v3/voice/history
```

**Note:** Requires voice access enabled on account.

### Get Voice Price

```bash
POST /clicksend/v3/voice/price
```

### Cancel Voice Message

```bash
PUT /clicksend/v3/voice/{message_id}/cancel
```

---

## Contact Lists

### List All Lists

```bash
GET /clicksend/v3/lists
```

**Response:**
```json
{
  "http_code": 200,
  "response_code": "SUCCESS",
  "response_msg": "Here are your contact lists.",
  "data": {
    "total": 2,
    "data": [
      {
        "list_id": 3555277,
        "list_name": "Opt-Out List",
        "_contacts_count": 0
      },
      {
        "list_id": 3555278,
        "list_name": "Example List",
        "_contacts_count": 10
      }
    ]
  }
}
```

### Get List

```bash
GET /clicksend/v3/lists/{list_id}
```

### Create List

```bash
POST /clicksend/v3/lists
Content-Type: application/json

{
  "list_name": "My New List"
}
```

### Update List

```bash
PUT /clicksend/v3/lists/{list_id}
Content-Type: application/json

{
  "list_name": "Updated List Name"
}
```

### Delete List

```bash
DELETE /clicksend/v3/lists/{list_id}
```

### Remove Duplicates

```bash
PUT /clicksend/v3/lists/{list_id}/remove-duplicates
```

---

## Contacts

### List Contacts in a List

```bash
GET /clicksend/v3/lists/{list_id}/contacts
```

**Query Parameters:**

| Parameter | Description |
|-----------|-------------|
| `page` | Page number |
| `limit` | Results per page |
| `updated_after` | Filter contacts updated after timestamp |

### Get Contact

```bash
GET /clicksend/v3/lists/{list_id}/contacts/{contact_id}
```

**Response:**
```json
{
  "http_code": 200,
  "response_code": "SUCCESS",
  "data": {
    "contact_id": 1581565666,
    "list_id": 3555278,
    "phone_number": "+18019234886",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "custom_1": "",
    "custom_2": "",
    "custom_3": "",
    "custom_4": "",
    "organization_name": "",
    "address_city": "",
    "address_state": "",
    "address_country": "US"
  }
}
```

### Create Contact

```bash
POST /clicksend/v3/lists/{list_id}/contacts
Content-Type: application/json

{
  "phone_number": "+15551234567",
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com"
}
```

**Contact Fields:**

| Field | Description |
|-------|-------------|
| `phone_number` | Phone number (E.164 format) |
| `first_name` | First name |
| `last_name` | Last name |
| `email` | Email address |
| `fax_number` | Fax number |
| `organization_name` | Company name |
| `custom_1` - `custom_4` | Custom fields |
| `address_line_1`, `address_line_2` | Address |
| `address_city`, `address_state`, `address_postal_code`, `address_country` | Address components |

### Update Contact

```bash
PUT /clicksend/v3/lists/{list_id}/contacts/{contact_id}
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Smith"
}
```

### Delete Contact

```bash
DELETE /clicksend/v3/lists/{list_id}/contacts/{contact_id}
```

### Copy Contact to Another List

```bash
PUT /clicksend/v3/lists/{from_list_id}/contacts/{contact_id}/copy/{to_list_id}
```

### Transfer Contact to Another List

```bash
PUT /clicksend/v3/lists/{from_list_id}/contacts/{contact_id}/transfer/{to_list_id}
```

---

## Email Addresses

### List Verified Email Addresses

```bash
GET /clicksend/v3/email/addresses
```

### Add Email Address

```bash
POST /clicksend/v3/email/addresses
Content-Type: application/json

{
  "email_address": "sender@example.com"
}
```

### Delete Email Address

```bash
DELETE /clicksend/v3/email/addresses/{email_address_id}
```

---

## Utility Endpoints

### List Countries

```bash
GET /clicksend/v3/countries
```

Returns list of all supported countries with codes.

---

## Pagination

ClickSend uses page-based pagination:

```bash
GET /clicksend/v3/lists?page=2&limit=50
```

**Response includes:**
```json
{
  "data": {
    "total": 100,
    "per_page": 50,
    "current_page": 2,
    "last_page": 2,
    "next_page_url": null,
    "prev_page_url": "...?page=1",
    "from": 51,
    "to": 100,
    "data": [...]
  }
}
```

**Parameters:**
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 15)

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/clicksend/v3/sms/send',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      messages: [
        {
          to: '+15551234567',
          body: 'Hello from ClickSend!',
          source: 'api'
        }
      ]
    })
  }
);
const data = await response.json();
console.log(data);
```

### Python

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/clicksend/v3/sms/send',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'messages': [
            {
                'to': '+15551234567',
                'body': 'Hello from ClickSend!',
                'source': 'api'
            }
        ]
    }
)
data = response.json()
print(f"Status: {data['response_code']}")
```

## Notes

- Phone numbers must be in E.164 format (e.g., `+15551234567`)
- All timestamps are Unix timestamps (seconds since epoch)
- Use `source` field to identify your application in analytics
- Templates support placeholders like `{name}`, `{custom_1}`, etc.
- SMS messages over 160 characters are split into multiple segments
- Voice access requires account-level permissions
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request |
| 401 | Unauthorized - invalid credentials |
| 403 | Forbidden - insufficient permissions |
| 404 | Resource not found |
| 429 | Rate limited |
| 500 | Internal server error |

**Response codes:**
- `SUCCESS` - Operation completed successfully
- `FORBIDDEN` - Access denied to resource
- `BAD_REQUEST` - Invalid request parameters
- `INVALID_RECIPIENT` - Invalid phone number

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

1. Ensure your URL path starts with `clicksend`. For example:

- Correct: `https://gateway.maton.ai/clicksend/v3/account`
- Incorrect: `https://gateway.maton.ai/v3/account`

## Resources

- [ClickSend Developer Portal](https://developers.clicksend.com/)
- [ClickSend REST API v3 Documentation](https://developers.clicksend.com/docs)
- [ClickSend PHP SDK](https://github.com/ClickSend/clicksend-php)
- [ClickSend Help Center](https://help.clicksend.com/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
