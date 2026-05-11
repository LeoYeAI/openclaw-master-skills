# AgentMail API Reference

Base URL: `https://api.agentmail.to/v0`

## Authentication

All requests require Bearer token authentication:

```
Authorization: Bearer YOUR_API_KEY
```

## Inboxes

### Create Inbox

```http
POST /v0/inboxes
```

**Request:**
```json
{
  "username": "my-agent",           // Optional: custom username
  "domain": "agentmail.to",         // Optional: defaults to agentmail.to
  "display_name": "My Agent",       // Optional: friendly name
  "client_id": "unique-id"          // Optional: for idempotency
}
```

**Response:**
```json
{
  "pod_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "inbox_id": "my-agent@agentmail.to",
  "display_name": "My Agent",
  "created_at": "2024-01-10T08:15:00Z",
  "updated_at": "2024-01-10T08:15:00Z",
  "client_id": "unique-id"
}
```

### List Inboxes

```http
GET /v0/inboxes?limit=10&page_token=eyJwYWdlIjoxfQ==
```

**Response:**
```json
{
  "count": 2,
  "inboxes": [...],
  "limit": 10,
  "next_page_token": "eyJwYWdlIjoyMQ=="
}
```

### Get Inbox

```http
GET /v0/inboxes/{inbox_id}
```

## Messages

### Send Message

```http
POST /v0/inboxes/{inbox_id}/messages
```

**Request:**
```json
{
  "to": ["recipient@example.com"],          // Required: string or array
  "cc": ["cc@example.com"],                 // Optional: string or array
  "bcc": ["bcc@example.com"],               // Optional: string or array
  "reply_to": "reply@example.com",          // Optional: string or array
  "subject": "Email subject",               // Optional: string
  "text": "Plain text body",                 // Optional: string
  "html": "<p>HTML body</p>",               // Optional: string
  "labels": ["sent", "important"],          // Optional: array
  "attachments": [{                         // Optional: array of objects
    "filename": "document.pdf",
    "content": "base64-encoded-content",
    "content_type": "application/pdf"
  }],
  "headers": {                              // Optional: custom headers
    "X-Custom-Header": "value"
  }
}
```

**Response:**
```json
{
  "message_id": "msg_123abc",
  "thread_id": "thd_789ghi"
}
```

### List Messages

```http
GET /v0/inboxes/{inbox_id}/messages?limit=10&page_token=token
```

### Get Message

```http
GET /v0/inboxes/{inbox_id}/messages/{message_id}
```

## Threads

### List Threads

```http
GET /v0/inboxes/{inbox_id}/threads?limit=10
```

### Get Thread

```http
GET /v0/inboxes/{inbox_id}/threads/{thread_id}
```

**Response:**
```json
{
  "thread_id": "thd_789ghi",
  "inbox_id": "support@example.com",
  "subject": "Question about my account",
  "participants": ["jane@example.com", "support@example.com"],
  "labels": ["customer-support"],
  "message_count": 3,
  "last_message_at": "2023-10-27T14:30:00Z",
  "created_at": "2023-10-27T10:00:00Z",
  "updated_at": "2023-10-27T14:30:00Z"
}
```

## Webhooks

### Create Webhook

```http
POST /v0/webhooks
```

**Request:**
```json
{
  "url": "https://your-domain.com/webhook",
  "client_id": "webhook-identifier",
  "enabled": true,
  "event_types": ["message.received"],      // Optional: defaults to all events
  "inbox_ids": ["inbox1@domain.com"]        // Optional: filter by specific inboxes
}
```

### List Webhooks

```http
GET /v0/webhooks
```

### Update Webhook

```http
PUT /v0/webhooks/{webhook_id}
```

### Delete Webhook

```http
DELETE /v0/webhooks/{webhook_id}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "type": "validation_error",
    "message": "Invalid email address",
    "details": {
      "field": "to",
      "code": "INVALID_EMAIL"
    }
  }
}
```

Common error codes:
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

## Rate Limits

AgentMail is designed for high-volume use with generous limits:
- API requests: 1000/minute per API key
- Email sending: 10,000/day (upgradeable)
- Webhook deliveries: Real-time, no limits

## Python SDK

The Python SDK provides a convenient wrapper around the REST API:

```python
from agentmail import AgentMail
import os

client = AgentMail(api_key=os.getenv("AGENTMAIL_API_KEY"))

# All operations return structured objects
inbox = client.inboxes.create(username="my-agent")
message = client.inboxes.messages.send(
    inbox_id=inbox.inbox_id,
    to="user@example.com",
    subject="Hello",
    text="Message body"
)
```