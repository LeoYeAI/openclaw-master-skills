---
name: manychat
description: |
  ManyChat API integration with managed authentication. Manage subscribers, tags, custom fields, and send messages through Facebook Messenger.
  Use this skill when users want to manage ManyChat subscribers, send messages, add/remove tags, or work with custom fields and bot automation.
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

# ManyChat

Access the ManyChat API with managed authentication. Manage subscribers, tags, custom fields, flows, and send messages through chat automation.

## Quick Start

```bash
# Get page info
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/manychat/fb/page/getInfo')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/manychat/{native-api-path}
```

Replace `{native-api-path}` with the actual ManyChat API endpoint path. The gateway proxies requests to `api.manychat.com` and automatically injects your API token.

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

Manage your ManyChat connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=manychat&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'manychat'}).encode()
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
    "app": "manychat",
    "metadata": {}
  }
}
```

Complete the connection by providing your ManyChat API key through the connection URL.

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

If you have multiple ManyChat connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/manychat/fb/page/getInfo')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Page Operations

#### Get Page Info

```bash
GET /manychat/fb/page/getInfo
```

Rate limit: 100 queries per second

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 123456789,
    "name": "Page Name",
    "category": "Business",
    "avatar_link": "https://...",
    "username": "pagename",
    "about": "About text",
    "description": "Page description",
    "is_pro": true,
    "timezone": "America/New_York"
  }
}
```

### Tag Operations

#### List Tags

```bash
GET /manychat/fb/page/getTags
```

Rate limit: 100 queries per second

**Response:**
```json
{
  "status": "success",
  "data": [
    {"id": 1, "name": "VIP"},
    {"id": 2, "name": "Customer"}
  ]
}
```

#### Create Tag

```bash
POST /manychat/fb/page/createTag
Content-Type: application/json

{
  "name": "New Tag"
}
```

Rate limit: 10 queries per second

#### Remove Tag from Page

```bash
POST /manychat/fb/page/removeTag
Content-Type: application/json

{
  "tag_id": 123
}
```

Rate limit: 10 queries per second. Removes tag from page and all subscribers.

#### Remove Tag by Name

```bash
POST /manychat/fb/page/removeTagByName
Content-Type: application/json

{
  "tag_name": "Old Tag"
}
```

Rate limit: 10 queries per second

### Custom Field Operations

#### List Custom Fields

```bash
GET /manychat/fb/page/getCustomFields
```

Rate limit: 100 queries per second

**Response:**
```json
{
  "status": "success",
  "data": [
    {"id": 1, "name": "phone_number", "type": "text"},
    {"id": 2, "name": "purchase_count", "type": "number"}
  ]
}
```

#### Create Custom Field

```bash
POST /manychat/fb/page/createCustomField
Content-Type: application/json

{
  "caption": "Phone Number",
  "type": "text",
  "description": "Customer phone number"
}
```

Rate limit: 10 queries per second

**Field Types:** `text`, `number`, `date`, `datetime`, `boolean`

### Bot Field Operations

#### List Bot Fields

```bash
GET /manychat/fb/page/getBotFields
```

Rate limit: 100 queries per second

#### Create Bot Field

```bash
POST /manychat/fb/page/createBotField
Content-Type: application/json

{
  "name": "counter",
  "type": "number",
  "description": "Global counter",
  "value": 0
}
```

Rate limit: 10 queries per second

#### Set Bot Field

```bash
POST /manychat/fb/page/setBotField
Content-Type: application/json

{
  "field_id": 123,
  "field_value": 42
}
```

Rate limit: 10 queries per second

#### Set Bot Field by Name

```bash
POST /manychat/fb/page/setBotFieldByName
Content-Type: application/json

{
  "field_name": "counter",
  "field_value": 42
}
```

Rate limit: 10 queries per second

#### Set Multiple Bot Fields

```bash
POST /manychat/fb/page/setBotFields
Content-Type: application/json

{
  "fields": [
    {"field_id": 123, "field_value": "value1"},
    {"field_name": "field2", "field_value": "value2"}
  ]
}
```

Rate limit: 10 queries per second. Maximum 20 fields per request.

### Flow Operations

#### List Flows

```bash
GET /manychat/fb/page/getFlows
```

Rate limit: 10 queries per second

**Response:**
```json
{
  "status": "success",
  "data": {
    "flows": [
      {"ns": "content123456", "name": "Welcome Flow", "folder_id": 1}
    ],
    "folders": [
      {"id": 1, "name": "Main Folder"}
    ]
  }
}
```

### Growth Tools

#### List Growth Tools

```bash
GET /manychat/fb/page/getGrowthTools
```

Rate limit: 100 queries per second

### OTN Topics

#### List OTN Topics

```bash
GET /manychat/fb/page/getOtnTopics
```

Rate limit: 100 queries per second

### Subscriber Operations

#### Get Subscriber Info

```bash
GET /manychat/fb/subscriber/getInfo?subscriber_id=123456789
```

Rate limit: 10 queries per second

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 123456789,
    "name": "John Doe",
    "first_name": "John",
    "last_name": "Doe",
    "gender": "male",
    "profile_pic": "https://...",
    "subscribed": "2025-01-15T10:30:00Z",
    "last_interaction": "2025-02-01T14:20:00Z",
    "tags": [{"id": 1, "name": "VIP"}],
    "custom_fields": [{"id": 1, "name": "phone", "value": "+1234567890"}]
  }
}
```

#### Find Subscriber by Name

```bash
GET /manychat/fb/subscriber/findByName?name=John%20Doe
```

Rate limit: 10 queries per second. Maximum 100 results.

#### Find Subscriber by Custom Field

```bash
GET /manychat/fb/subscriber/findByCustomField?field_id=123&field_value=value
```

Rate limit: 10 queries per second. Works with Text and Number fields. Maximum 100 results.

#### Find Subscriber by System Field

```bash
GET /manychat/fb/subscriber/findBySystemField?email=john@example.com
```

```bash
GET /manychat/fb/subscriber/findBySystemField?phone=+1234567890
```

Rate limit: 50 queries per second. Set either `email` OR `phone` parameter.

#### Get Subscriber by User Ref

```bash
GET /manychat/fb/subscriber/getInfoByUserRef?user_ref=123456
```

#### Create Subscriber

```bash
POST /manychat/fb/subscriber/createSubscriber
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "email": "john@example.com",
  "gender": "male",
  "has_opt_in_sms": true,
  "has_opt_in_email": true,
  "consent_phrase": "I agree to receive messages"
}
```

Rate limit: 10 queries per second

**Note:** Importing subscribers with phone or email requires special permissions from ManyChat. Contact ManyChat support to enable this feature for your account.

#### Update Subscriber

```bash
POST /manychat/fb/subscriber/updateSubscriber
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "first_name": "John",
  "last_name": "Smith",
  "phone": "+1234567890",
  "email": "john.smith@example.com"
}
```

Rate limit: 10 queries per second

#### Add Tag to Subscriber

```bash
POST /manychat/fb/subscriber/addTag
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "tag_id": 1
}
```

Rate limit: 10 queries per second

#### Add Tag by Name

```bash
POST /manychat/fb/subscriber/addTagByName
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "tag_name": "VIP"
}
```

Rate limit: 10 queries per second

#### Remove Tag from Subscriber

```bash
POST /manychat/fb/subscriber/removeTag
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "tag_id": 1
}
```

Rate limit: 10 queries per second

#### Remove Tag by Name

```bash
POST /manychat/fb/subscriber/removeTagByName
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "tag_name": "VIP"
}
```

Rate limit: 10 queries per second

#### Set Custom Field

```bash
POST /manychat/fb/subscriber/setCustomField
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "field_id": 1,
  "field_value": "+1234567890"
}
```

Rate limit: 10 queries per second

#### Set Custom Field by Name

```bash
POST /manychat/fb/subscriber/setCustomFieldByName
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "field_name": "phone_number",
  "field_value": "+1234567890"
}
```

Rate limit: 10 queries per second

#### Set Multiple Custom Fields

```bash
POST /manychat/fb/subscriber/setCustomFields
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "fields": [
    {"field_id": 1, "field_value": "value1"},
    {"field_name": "field2", "field_value": "value2"}
  ]
}
```

Rate limit: 10 queries per second. Maximum 20 fields per request.

#### Verify Subscriber by Signed Request

```bash
POST /manychat/fb/subscriber/verifyBySignedRequest
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "signed_request": "signed_request_token"
}
```

Rate limit: 10 queries per second

### Sending Operations

#### Send Content

```bash
POST /manychat/fb/sending/sendContent
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "data": {
    "version": "v2",
    "content": {
      "messages": [
        {
          "type": "text",
          "text": "Hello! How can I help you today?"
        }
      ]
    }
  },
  "message_tag": "CONFIRMED_EVENT_UPDATE"
}
```

Rate limit: 25 queries per second

**Message Tags:** Required for sending outside the 24-hour messaging window
- `CONFIRMED_EVENT_UPDATE`
- `POST_PURCHASE_UPDATE`
- `ACCOUNT_UPDATE`

**OTN (One-Time Notification):**
```json
{
  "subscriber_id": 123456789,
  "data": {...},
  "otn_topic_name": "Price Drop Alert"
}
```

#### Send Content by User Ref

```bash
POST /manychat/fb/sending/sendContentByUserRef
Content-Type: application/json

{
  "user_ref": 123456,
  "data": {
    "version": "v2",
    "content": {
      "messages": [
        {
          "type": "text",
          "text": "Welcome!"
        }
      ]
    }
  }
}
```

Rate limit: 25 queries per second

#### Send Flow

```bash
POST /manychat/fb/sending/sendFlow
Content-Type: application/json

{
  "subscriber_id": 123456789,
  "flow_ns": "content123456"
}
```

Rate limit: 20 queries per second, maximum 100 per subscriber per hour

## Message Content Format

ManyChat uses a structured content format for sending messages:

### Text Message

```json
{
  "version": "v2",
  "content": {
    "messages": [
      {
        "type": "text",
        "text": "Your message here"
      }
    ]
  }
}
```

### Image Message

```json
{
  "version": "v2",
  "content": {
    "messages": [
      {
        "type": "image",
        "url": "https://example.com/image.jpg"
      }
    ]
  }
}
```

### Quick Replies

```json
{
  "version": "v2",
  "content": {
    "messages": [
      {
        "type": "text",
        "text": "Choose an option:",
        "quick_replies": [
          {"type": "node", "caption": "Option 1", "target": "content123"},
          {"type": "node", "caption": "Option 2", "target": "content456"}
        ]
      }
    ]
  }
}
```

### Buttons

```json
{
  "version": "v2",
  "content": {
    "messages": [
      {
        "type": "text",
        "text": "Click a button:",
        "buttons": [
          {"type": "url", "caption": "Visit Website", "url": "https://example.com"},
          {"type": "flow", "caption": "Start Flow", "target": "content123"}
        ]
      }
    ]
  }
}
```

## Code Examples

### JavaScript

```javascript
// Get page info
const response = await fetch(
  'https://gateway.maton.ai/manychat/fb/page/getInfo',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();

// Send a message
const sendResponse = await fetch(
  'https://gateway.maton.ai/manychat/fb/sending/sendContent',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      subscriber_id: 123456789,
      data: {
        version: 'v2',
        content: {
          messages: [{ type: 'text', text: 'Hello!' }]
        }
      }
    })
  }
);
```

### Python

```python
import os
import requests

# Get page info
response = requests.get(
    'https://gateway.maton.ai/manychat/fb/page/getInfo',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()

# Send a message
send_response = requests.post(
    'https://gateway.maton.ai/manychat/fb/sending/sendContent',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    json={
        'subscriber_id': 123456789,
        'data': {
            'version': 'v2',
            'content': {
                'messages': [{'type': 'text', 'text': 'Hello!'}]
            }
        }
    }
)
```

## Notes

- Subscriber IDs are unique within your ManyChat page
- Flow namespaces (flow_ns) are used to identify specific automation flows
- The `message_tag` parameter is required when sending messages outside the 24-hour messaging window
- OTN (One-Time Notification) allows sending one message per topic subscription
- Most POST endpoints return `{"status": "success"}` on success
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing ManyChat connection |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from ManyChat API |

### ManyChat Error Codes

| Code | Meaning |
|------|---------|
| 2011 | Subscriber not found |
| 2012 | User ref not found |
| 3011 | Invalid message content |
| 3021 | Message tag required |
| 3031 | OTN topic not found |

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

1. Ensure your URL path starts with `manychat`. For example:

- Correct: `https://gateway.maton.ai/manychat/fb/page/getInfo`
- Incorrect: `https://gateway.maton.ai/fb/page/getInfo`

## Resources

- [ManyChat API Documentation](https://api.manychat.com/swagger)
- [ManyChat API Key Generation Guide](https://help.manychat.com/hc/en-us/articles/14959510331420)
- [ManyChat Dev Program](https://help.manychat.com/hc/en-us/articles/14281269835548)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
