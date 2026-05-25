---
name: moltflow
description: "WhatsApp Business automation API for sessions, messaging, groups, labels, and webhooks. Use when: whatsapp, send message, create session, qr code, monitor group, label contacts, webhook."
source: "MoltFlow Team"
version: "2.16.1"
risk: safe
requiredEnv:
  - MOLTFLOW_API_KEY
primaryEnv: MOLTFLOW_API_KEY
disable-model-invocation: true
---

> **MoltFlow** -- WhatsApp Business automation for teams. Connect, monitor, and automate WhatsApp at scale.
> ***Due to high demand and a recent registration issue, we're offering our top-tier Business plan with unlimited quotas for just $19.90/month on yearly billing — for a limited time only.*** [**Claim the deal**](https://buy.stripe.com/cNifZibX7gpQebJ0nsfnO00)
> Free tier available. [Sign up](https://molt.waiflow.app/checkout?plan=free)

# MoltFlow Core API

Manage WhatsApp sessions, send messages, monitor groups, organize with labels, and receive real-time events via webhooks.

## Real-World Scenarios

**Dental clinic** — "Send an appointment confirmation to each patient after they book, and a reminder 24 hours before their visit."

**Property manager** — "Monitor my tenant WhatsApp groups for maintenance keywords like 'leak', 'broken', and 'urgent', and flag them instantly."

**E-commerce store** — "When a customer messages my support number, auto-label them as 'New Inquiry' and route the chat to the right team."

**Logistics company** — "Set up a webhook so my dispatch system gets notified the moment a driver sends a delivery confirmation photo."

## When to Use

- "Connect WhatsApp" or "create a session"
- "Send a WhatsApp message" or "send text to contact"
- "Monitor a WhatsApp group" or "list groups"
- "Label contacts" or "sync labels from WhatsApp"
- "Set up a webhook" or "listen for WhatsApp events"
- "Get QR code" or "start session"
- "List chats" or "get conversations"

## Prerequisites

1. **MOLTFLOW_API_KEY** -- Generate from the [MoltFlow Dashboard](https://molt.waiflow.app) under Settings > API Keys
2. All requests require authentication via `Authorization: Bearer <token>` or `X-API-Key: <key>`
3. Base URL: `https://apiv2.waiflow.app/api/v2`

## Required API Key Scopes

| Scope | Access |
|-------|--------|
| `sessions` | `read/manage` |
| `messages` | `read/send` |
| `groups` | `read/manage` |
| `labels` | `read/manage` |
| `webhooks` | `read/manage` |

## Authentication

Every request must include one of:

```
Authorization: Bearer <jwt_token>
```

or

```
X-API-Key: <your_api_key>
```

---

## Sessions

Manage WhatsApp connections. Each session represents one WhatsApp account linked via QR code.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/sessions` | List all sessions |
| POST | `/sessions` | Create a new session |
| GET | `/sessions/{id}` | Get session details |
| DELETE | `/sessions/{id}` | Delete a session |
| POST | `/sessions/{id}/start` | Start session (triggers QR scan) |
| POST | `/sessions/{id}/stop` | Stop a running session |
| POST | `/sessions/{id}/restart` | Restart a session |
| POST | `/sessions/{id}/logout` | Logout and clear auth state |
| GET | `/sessions/{id}/qr` | Get QR code for pairing |
| GET | `/sessions/{id}/events` | SSE stream of session events |

### Session Status Values

Sessions progress through these states: `stopped` -> `starting` -> `qr_code` -> `working` -> `failed`

### Create Session

**POST** `/sessions`

```json
{
  "name": "My WhatsApp"
}
```

**Response** `201 Created`:

```json
{
  "id": "a1b2c3d4-...",
  "name": "My WhatsApp",
  "status": "stopped",
  "phone_number": null,
  "is_business": false,
  "created_at": "2026-02-11T10:00:00Z"
}
```

### Start Session and Get QR

After creating a session, start it and retrieve the QR code:

1. `POST /sessions/{id}/start` -- begins the WAHA engine
2. Wait for status to become `qr_code` (use SSE events or poll)
3. `GET /sessions/{id}/qr` -- returns the QR code image

### SSE Events

`GET /sessions/{id}/events?token=<jwt>` returns a Server-Sent Events stream. Events include session status changes, incoming messages, and connection updates.

### Session Settings

**PATCH** `/sessions/{id}/settings`

Configure per-session behavior. Settings are stored in the session's `config` JSON field.

```json
// Request
{
  "auto_transcribe": true
}

// Response
{
  "status": "ok",
  "config": {
    "auto_transcribe": true
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `auto_transcribe` | boolean | Automatically transcribe incoming voice messages |

---

## Messages

Send and retrieve WhatsApp messages through connected sessions.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/messages/send` | Send a text message |
| POST | `/messages/send/poll` | Send a poll message |
| POST | `/messages/send/sticker` | Send a sticker |
| POST | `/messages/send/gif` | Send a GIF |
| GET | `/messages/chats/{session_id}` | List all chats for a session |
| GET | `/messages/chat/{session_id}/{chat_id}` | Get chat messages |
| GET | `/messages/{message_id}` | Get a single message |

### Send Text Message

**POST** `/messages/send`

```json
{
  "session_id": "a1b2c3d4-...",
  "chat_id": "5511999999999@c.us",
  "message": "Hello from MoltFlow!"
}
```

**Response** `201 Created`:

```json
{
  "id": "msg-uuid-...",
  "chat_id": "chat-uuid-...",
  "wa_message_id": "ABCD1234",
  "direction": "outbound",
  "message_type": "text",
  "content_preview": "Hello from MoltFlow!",
  "status": "sent",
  "sent_at": "2026-02-11T10:05:00Z",
  "created_at": "2026-02-11T10:05:00Z"
}
```

### Chat ID Format

- Individual contacts: `<phone>@c.us` (e.g., `5511999999999@c.us`)
- Groups: `<group_id>@g.us` (e.g., `120363012345678901@g.us`)

### Send Poll

**POST** `/messages/send/poll`

```json
{
  "session_id": "a1b2c3d4-...",
  "chat_id": "5511999999999@c.us",
  "title": "Preferred meeting time?",
  "options": ["Morning", "Afternoon", "Evening"],
  "allow_multiple": false
}
```

---

## Groups

Monitor WhatsApp groups for keywords, messages, and activity.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/groups` | List monitored groups |
| GET | `/groups/available/{session_id}` | List available WA groups |
| POST | `/groups` | Add group to monitoring |
| GET | `/groups/{id}` | Get monitored group details |
| PATCH | `/groups/{id}` | Update monitoring settings |
| DELETE | `/groups/{id}` | Remove from monitoring |
| POST | `/groups/create` | Create a new WA group |
| POST | `/groups/{wa_group_id}/participants/add` | Add participants |
| POST | `/groups/{wa_group_id}/participants/remove` | Remove participants |
| POST | `/groups/{wa_group_id}/admin/promote` | Promote to admin |
| POST | `/groups/{wa_group_id}/admin/demote` | Demote from admin |

### Add Group to Monitoring

**POST** `/groups`

```json
{
  "session_id": "a1b2c3d4-...",
  "wa_group_id": "120363012345678901@g.us",
  "monitor_mode": "keywords",
  "monitor_keywords": ["urgent", "support", "help"]
}
```

### Monitor Modes

- `all` -- Capture every message in the group
- `keywords` -- Only capture messages matching specified keywords
- `mentions` -- Only when your account is mentioned
- `first_message` -- Only first messages from new users (default for new groups)
- `ai_analysis` -- AI-powered intent classification and lead scoring (Pro+ only)

### Group Messages (AI Intelligence)

**GET** `/groups/{group_id}/messages`

Retrieve paginated messages from a monitored group, including AI analysis results.

Query parameters: `limit` (default 50, max 100), `offset` (default 0)

**Requires scope:** `groups:read`

```json
{
  "items": [
    {
      "id": "msg-uuid",
      "sender_phone": "+15550123456",
      "sender_name": "John D.",
      "content_preview": "I'm interested in the 3BR property",
      "wa_timestamp": "2026-02-20T14:30:00Z",
      "ai_analysis": {
        "intent": "buying_intent",
        "lead_score": 9,
        "confidence": 0.92,
        "reason": "Explicit interest in a specific property with buying signal"
      }
    }
  ],
  "total": 142,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

`ai_analysis` is null when AI hasn't processed the message or AI monitoring is not enabled.

### MCP Tool: moltflow_get_group_messages

Retrieve messages from a monitored WhatsApp group via Claude or any MCP client.

**Args:**
- `group_id` (required): UUID of the monitored group
- `limit` (optional): Max messages 1-100 (default: 50)
- `offset` (optional): Skip count for pagination (default: 0)
- `response_format` (optional): `"markdown"` or `"json"`

**Returns:** Paginated list of messages with sender info, content preview, timestamp, and `ai_analysis` (intent, lead_score, confidence, reason) when AI has processed the message.

**Requires scope:** `groups:read`

---

## Labels

Organize contacts and chats with color-coded labels. Supports sync with WhatsApp Business native labels.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/labels` | List all labels |
| POST | `/labels` | Create a label |
| GET | `/labels/{id}` | Get label details |
| PATCH | `/labels/{id}` | Update a label |
| DELETE | `/labels/{id}` | Delete a label |
| POST | `/labels/{id}/sync` | Sync label to WhatsApp |
| POST | `/labels/sync-from-whatsapp` | Import labels from WA |
| GET | `/labels/business-check` | Check WA Business status |
| GET | `/labels/{id}/chats` | List chats with this label |
| GET | `/labels/chat/{chat_id}` | Get labels for a chat |
| PUT | `/labels/chat/{chat_id}` | Set labels for a chat |

### Create Label

**POST** `/labels`

```json
{
  "name": "VIP Customer",
  "color": "#FF6B35",
  "description": "High-value accounts"
}
```

**Response** `201 Created`:

```json
{
  "id": "label-uuid-...",
  "name": "VIP Customer",
  "color": "#FF6B35",
  "description": "High-value accounts",
  "chat_count": 0,
  "synced": false,
  "created_at": "2026-02-11T10:00:00Z"
}
```

> **Note:** Syncing labels to WhatsApp requires a WhatsApp Business account. Use `GET /labels/business-check` to verify.

---

## Webhooks

Receive real-time notifications when events occur in your WhatsApp sessions.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/webhooks` | List all webhooks |
| POST | `/webhooks` | Create a webhook |
| GET | `/webhooks/{id}` | Get webhook details |
| PATCH | `/webhooks/{id}` | Update a webhook |
| DELETE | `/webhooks/{id}` | Delete a webhook |
| POST | `/webhooks/{id}/test` | Send a test delivery |

### Supported Events

| Event | Description |
|-------|-------------|
| `message.received` | Inbound message received |
| `message.sent` | Outbound message sent |
| `session.connected` | Session connected to WhatsApp |
| `session.disconnected` | Session disconnected |
| `lead.detected` | New lead detected (includes `ai_analysis` when available) |
| `group.message` | Message in a monitored group |
| `group.message.analyzed` | AI analysis completed for a group message (Pro/Business only) |

### Create Webhook

**POST** `/webhooks`

> **Security:** Webhook URLs are validated server-side — private IPs, cloud metadata endpoints, and non-HTTPS schemes are blocked. Only configure endpoints you control. Always set a `secret` for HMAC signature verification.

```json
{
  "name": "CRM Integration",
  "url": "https://example.com/webhooks/moltflow",
  "events": ["message.received", "lead.detected"],
  "secret": "whsec_mysecretkey123"
}
```

**Response** `201 Created`:

```json
{
  "id": "wh-uuid-...",
  "name": "CRM Integration",
  "url": "https://example.com/webhooks/moltflow",
  "events": ["message.received", "lead.detected"],
  "is_active": true,
  "created_at": "2026-02-11T10:00:00Z"
}
```

### Webhook Payload

Deliveries include an HMAC-SHA256 signature in the `X-Webhook-Signature` header (if a secret is configured). Verify this to ensure authenticity.

```json
{
  "event": "message.received",
  "timestamp": "2026-02-11T10:05:00Z",
  "data": {
    "session_id": "a1b2c3d4-...",
    "chat_id": "5511999999999@c.us",
    "message": "Hello!",
    "direction": "inbound"
  }
}
```

---

## Examples

### Full workflow: Create session and send first message

```bash
# 1. Create a session
curl -X POST https://apiv2.waiflow.app/api/v2/sessions \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "Sales Team"}'

# 2. Start the session (triggers QR)
curl -X POST https://apiv2.waiflow.app/api/v2/sessions/{session_id}/start \
  -H "X-API-Key: $MOLTFLOW_API_KEY"

# 3. Get QR code (scan with WhatsApp)
curl https://apiv2.waiflow.app/api/v2/sessions/{session_id}/qr \
  -H "X-API-Key: $MOLTFLOW_API_KEY"

# 4. Send a message (after session status is "working")
curl -X POST https://apiv2.waiflow.app/api/v2/messages/send \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "{session_id}",
    "chat_id": "5511999999999@c.us",
    "message": "Hello from MoltFlow!"
  }'
```

### Set up a webhook for incoming messages

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/webhooks \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Incoming Messages",
    "url": "https://myapp.com/webhooks/whatsapp",
    "events": ["message.received", "session.connected"],
    "secret": "whsec_my_secret"
  }'
```

### Monitor a group for keywords

```bash
# List available groups from a connected session
curl https://apiv2.waiflow.app/api/v2/groups/available/{session_id} \
  -H "X-API-Key: $MOLTFLOW_API_KEY"

# Add a group to monitoring
curl -X POST https://apiv2.waiflow.app/api/v2/groups \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "{session_id}",
    "wa_group_id": "120363012345678901@g.us",
    "monitor_mode": "keywords",
    "monitor_keywords": ["urgent", "support"]
  }'
```

---

## Error Responses

All endpoints return standard error responses:

```json
{
  "detail": "Session not found"
}
```

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid input) |
| 401 | Unauthorized (missing or invalid auth) |
| 403 | Forbidden (plan limit or permission) |
| 404 | Resource not found |
| 429 | Rate limited |
| 500 | Internal server error |

---

## Rate Limits

API requests are rate-limited per tenant. Limits vary by plan:

| Plan | Requests/min |
|------|-------------|
| Free | 10 |
| Starter | 20 |
| Pro | 40 |
| Business | 60 |

Rate limit headers are included in every response: `X-RateLimit-Remaining`, `X-RateLimit-Reset`.

---

## Related Skills

- **moltflow-outreach** -- Bulk Send, Scheduled Messages, Custom Groups
- **moltflow-leads** -- Lead detection, pipeline tracking, bulk operations, CSV/JSON export
- **moltflow-ai** -- AI-powered auto-replies, voice transcription, RAG knowledge base, style profiles
- **moltflow-a2a** -- Agent-to-Agent protocol, encrypted messaging, content policy
- **moltflow-reviews** -- Review collection and testimonial management
- **moltflow-admin** -- Platform administration, user management, plan configuration
