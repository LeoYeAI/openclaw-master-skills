---
name: moltflow-outreach
description: "Bulk messaging, scheduled messages, scheduled reports, and custom groups for WhatsApp outreach. Use when: bulk send, broadcast, schedule message, schedule report, cron, custom group, contact list, ban-safe messaging."
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

# MoltFlow Outreach -- Bulk Send, Scheduled Messages, Reports & Custom Groups

Broadcast to custom contact lists with ban-safe throttling, schedule recurring messages with timezone support, generate automated reports with WhatsApp delivery, and manage targeted contact groups for WhatsApp outreach.

## Real-World Scenarios

**Gym owner** — "Send a 'Happy New Year' promo with a discount code to all my members, spaced out so I don't get banned."

**Freelance consultant** — "Every Friday at 5 PM, send a 'weekend availability' message to my active client list."

**Marketing agency** — "Build a contact group from 3 WhatsApp groups, deduplicate, and blast a product launch announcement."

**Restaurant chain** — "Schedule a weekly report showing how many reservation confirmations were sent and delivered — send it to my WhatsApp every Monday morning."

## When to Use

- "Send bulk message" or "broadcast to group"
- "Schedule a WhatsApp message" or "set up recurring message"
- "Generate a report" or "schedule a report"
- "Send me a usage summary" or "get a lead pipeline report"
- "Create a contact list" or "build custom group"
- "Pause bulk send" or "cancel scheduled message"
- "Export group members as CSV" or "import contacts"
- "Send weekly update" or "set up cron schedule"

## Prerequisites

1. **MOLTFLOW_API_KEY** -- Generate from the [MoltFlow Dashboard](https://molt.waiflow.app) under Settings > API Keys
2. At least one connected WhatsApp session (status: `working`)
3. Base URL: `https://apiv2.waiflow.app/api/v2`

## Required API Key Scopes

| Scope | Access |
|-------|--------|
| `custom-groups` | `read/manage` |
| `bulk-send` | `read/manage` |
| `scheduled` | `read/manage` |
| `reports` | `read/manage` |

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

## Custom Groups

Build targeted contact lists for Bulk Send and Scheduled Messages. Custom Groups are MoltFlow contact lists -- not WhatsApp groups.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/custom-groups` | List all custom groups |
| POST | `/custom-groups` | Create group (with optional initial members) |
| GET | `/custom-groups/contacts` | List all unique contacts across sessions |
| GET | `/custom-groups/wa-groups` | List WhatsApp groups for import |
| POST | `/custom-groups/from-wa-groups` | Create group by importing WA group members |
| GET | `/custom-groups/{id}` | Group details with members |
| PATCH | `/custom-groups/{id}` | Update group name |
| DELETE | `/custom-groups/{id}` | Delete group and members |
| POST | `/custom-groups/{id}/members/add` | Add members (skips duplicates) |
| POST | `/custom-groups/{id}/members/remove` | Remove members by phone |
| GET | `/custom-groups/{id}/export/csv` | Export members as CSV |
| GET | `/custom-groups/{id}/export/json` | Export members as JSON |

### Create Custom Group

**POST** `/custom-groups`

```json
{
  "name": "VIP Clients",
  "members": [
    {"phone": "+15550123456"},
    {"phone": "+15550987654", "name": "Jane Doe"}
  ]
}
```

Members is an array of objects with `phone` (required) and `name` (optional). Omit `members` to create an empty group.

### Create Group from WhatsApp Groups

**POST** `/custom-groups/from-wa-groups`

```json
{
  "name": "Imported Leads",
  "wa_groups": [
    {"wa_group_id": "120363012345@g.us", "session_id": "session-uuid-..."},
    {"wa_group_id": "120363067890@g.us", "session_id": "session-uuid-..."}
  ]
}
```

Resolves participants from each WhatsApp group, deduplicates by phone number, and creates the custom group with all unique members.

### List WhatsApp Groups

**GET** `/custom-groups/wa-groups`

Returns all WhatsApp groups across your connected sessions with participant counts. Use this to discover groups available for import.

**Response** `201 Created`:

```json
{
  "id": "group-uuid-...",
  "name": "VIP Clients",
  "member_count": 2,
  "created_at": "2026-02-12T10:00:00Z"
}
```

### Add Members

**POST** `/custom-groups/{id}/members/add`

```json
{
  "contacts": [
    {"phone": "+15551112222"},
    {"phone": "+15553334444", "name": "Bob Smith"}
  ]
}
```

Each contact is an object with `phone` (required) and `name` (optional). Max 1,000 per request. Duplicates are silently skipped.

### Export Members

**GET** `/custom-groups/{id}/export/csv` -- Returns CSV download
**GET** `/custom-groups/{id}/export/json` -- Returns JSON array

---

## Bulk Send

Broadcast messages to a custom group with ban-safe throttling. Random 30s-2min delays between messages simulate human behavior.

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/bulk-send` | Create bulk send job (quota reserved) |
| GET | `/bulk-send` | List all bulk send jobs |
| GET | `/bulk-send/{id}` | Job details with recipients |
| POST | `/bulk-send/{id}/pause` | Pause running job |
| POST | `/bulk-send/{id}/resume` | Resume paused job |
| POST | `/bulk-send/{id}/cancel` | Cancel job (releases unused quota) |
| GET | `/bulk-send/{id}/progress` | Real-time progress via SSE |

### Create Bulk Send Job

**POST** `/bulk-send`

```json
{
  "session_id": "session-uuid-...",
  "custom_group_id": "custom-group-uuid-...",
  "message_content": "Special offer for our VIP clients!"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `session_id` | UUID | Yes | WhatsApp session to send from |
| `custom_group_id` | UUID | Yes | Target custom group |
| `message_type` | string | No | `text` (default) or `media` |
| `message_content` | string | Conditional | Message text (max 4096 chars). Required if no `media_url` |
| `media_url` | string | Conditional | HTTP(S) URL for media. Required if no `message_content` |

**Response** `201 Created`:

```json
{
  "id": "job-uuid-...",
  "session_id": "session-uuid-...",
  "custom_group_id": "custom-group-uuid-...",
  "status": "running",
  "total_recipients": 127,
  "sent_count": 0,
  "failed_count": 0,
  "created_at": "2026-02-12T10:00:00Z"
}
```

### Stream Progress (SSE)

**GET** `/bulk-send/{id}/progress`

Returns Server-Sent Events with real-time updates:

```
data: {"sent": 45, "total": 127, "failed": 0, "status": "running"}
data: {"sent": 46, "total": 127, "failed": 0, "status": "running"}
```

### Job Status Values

`pending` -> `running` -> `completed` / `paused` / `cancelled` / `failed`

### Anti-Ban Safety

- Random 30s-2min delays between messages
- Typing simulation before each message
- Seen/read indicators marked automatically
- Burst rate limiting (4 msgs/2 min)

---

## Scheduled Messages

Schedule one-time or recurring WhatsApp messages to custom groups with timezone support and full lifecycle control.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/scheduled-messages` | List all scheduled messages |
| POST | `/scheduled-messages` | Create schedule (one-time or recurring) |
| GET | `/scheduled-messages/{id}` | Schedule details with execution history |
| PATCH | `/scheduled-messages/{id}` | Update schedule and recalculate next run |
| POST | `/scheduled-messages/{id}/cancel` | Cancel schedule |
| POST | `/scheduled-messages/{id}/pause` | Pause active schedule |
| POST | `/scheduled-messages/{id}/resume` | Resume paused schedule |
| DELETE | `/scheduled-messages/{id}` | Delete cancelled/completed schedule |
| GET | `/scheduled-messages/{id}/history` | Execution history (paginated) |

### Create One-Time Schedule

**POST** `/scheduled-messages`

```json
{
  "name": "Follow-up",
  "session_id": "session-uuid-...",
  "custom_group_id": "custom-group-uuid-...",
  "schedule_type": "one_time",
  "message_content": "Just checking in on your order!",
  "scheduled_time": "2026-02-15T09:00:00",
  "timezone": "Asia/Jerusalem"
}
```

### Create Recurring Schedule (Cron)

**POST** `/scheduled-messages`

```json
{
  "name": "Weekly Update",
  "session_id": "session-uuid-...",
  "custom_group_id": "custom-group-uuid-...",
  "schedule_type": "cron",
  "message_content": "Weekly team report is ready!",
  "cron_expression": "0 9 * * MON",
  "timezone": "America/New_York"
}
```

**Response** `201 Created`:

```json
{
  "id": "schedule-uuid-...",
  "name": "Weekly Update",
  "status": "active",
  "schedule_type": "cron",
  "cron_expression": "0 9 * * MON",
  "timezone": "America/New_York",
  "next_run_at": "2026-02-17T09:00:00-05:00",
  "created_at": "2026-02-12T10:00:00Z"
}
```

### Schedule Types

- `one_time` -- Single send at `scheduled_time`
- `daily` -- Every day (requires `cron_expression`)
- `weekly` -- Every week (requires `cron_expression`)
- `monthly` -- Every month (requires `cron_expression`)
- `cron` -- Custom cron expression (e.g., `0 9 * * MON-FRI`)

**Note:** All recurring types (`daily`, `weekly`, `monthly`, `cron`) require a `cron_expression`. Minimum interval: 5 minutes.

### Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Schedule name (1-255 chars) |
| `session_id` | UUID | Yes | WhatsApp session to send from |
| `custom_group_id` | UUID | Yes | Target custom group |
| `schedule_type` | string | Yes | One of: `one_time`, `daily`, `weekly`, `monthly`, `cron` |
| `message_type` | string | No | `text` (default) or `media` |
| `message_content` | string | Conditional | Message text (max 4096). Required if no `media_url` |
| `media_url` | string | Conditional | HTTP(S) URL. Required if no `message_content` |
| `scheduled_time` | datetime | Conditional | ISO 8601. Required for `one_time` |
| `cron_expression` | string | Conditional | Cron string. Required for recurring types |
| `timezone` | string | No | IANA timezone (default: `UTC`) |

### Schedule Status Values

`active` -> `paused` / `cancelled` / `completed`

---

## Scheduled Reports

Generate automated summaries of your MoltFlow activity on a schedule. Choose from 10 prebuilt templates covering leads, messaging, sessions, and more. Reports can be viewed in the dashboard or delivered directly to your WhatsApp.

Set `delivery_method` to `"whatsapp"` to receive report summaries directly in your connected WhatsApp session. The report is formatted as plain text and sent to the session owner's own chat.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/templates` | List available report templates |
| POST | `/reports` | Create a new scheduled report |
| GET | `/reports` | List your reports |
| GET | `/reports/{id}` | Get report with execution history |
| PATCH | `/reports/{id}` | Update schedule or settings |
| POST | `/reports/{id}/pause` | Pause a scheduled report |
| POST | `/reports/{id}/resume` | Resume a paused report |
| DELETE | `/reports/{id}` | Delete a report |

### List Report Templates

**GET** `/reports/templates`

Returns all 10 available report templates with descriptions and supported parameters.

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/reports/templates
```

**Response** `200 OK`:

```json
[
  {
    "id": "daily_activity",
    "name": "Daily Activity Summary",
    "description": "Messages sent/received, leads detected, session uptime"
  },
  {
    "id": "lead_pipeline",
    "name": "Lead Pipeline Report",
    "description": "Lead sources, funnel stages, conversion rates"
  }
]
```

### Create a Scheduled Report

**POST** `/reports`

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Lead Pipeline",
    "template_id": "lead_pipeline",
    "schedule_type": "weekly",
    "cron_expression": "0 9 * * MON",
    "timezone": "America/New_York",
    "delivery_method": "whatsapp"
  }' \
  https://apiv2.waiflow.app/api/v2/reports
```

**Response** `201 Created`:

```json
{
  "id": "report-uuid-...",
  "name": "Weekly Lead Pipeline",
  "template_id": "lead_pipeline",
  "schedule_type": "weekly",
  "cron_expression": "0 9 * * MON",
  "timezone": "America/New_York",
  "delivery_method": "whatsapp",
  "status": "active",
  "next_run_at": "2026-02-17T09:00:00-05:00",
  "created_at": "2026-02-13T10:00:00Z"
}
```

### Required Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Report name (1-255 chars) |
| `template_id` | string | Yes | Template ID from `/reports/templates` |
| `schedule_type` | string | Yes | One of: `one_time`, `daily`, `weekly`, `monthly`, `cron` |
| `cron_expression` | string | Conditional | Cron string. Required for recurring types |
| `timezone` | string | No | IANA timezone (default: `UTC`) |
| `delivery_method` | string | No | `dashboard` (default) or `whatsapp` |

### Report Templates

| Template ID | Name | Description |
|-------------|------|-------------|
| `daily_activity` | Daily Activity Summary | Messages, leads, sessions |
| `lead_pipeline` | Lead Pipeline Report | Sources, funnel, conversions |
| `unanswered_contacts` | Unanswered Contacts | Warm leads going cold |
| `vip_contacts` | VIP Contacts | Most active conversations |
| `group_monitoring` | Group Monitoring Digest | Keyword matches, leads |
| `scheduled_messages_status` | Scheduled Messages Status | Executed vs failed |
| `bulk_send_progress` | Bulk Send Progress | Active, completed, stats |
| `usage_plan` | Usage & Plan Utilization | Limits, suggestions |
| `session_health` | Session Health Check | Uptime, connection issues |
| `review_digest` | Review & Testimonial Digest | Sentiment, approvals |

### Delivery Methods

- **`dashboard`** (default) -- Report is generated and viewable in the MoltFlow Reports page with formatted tables and stats.
- **`whatsapp`** -- Report summary is formatted as plain text and sent to your connected WhatsApp session. The message is delivered to the session owner's own chat so you see it directly in WhatsApp.

### Report Status Values

`active` -> `paused` / `cancelled` / `completed`

---

## Examples

### Full workflow: Group -> Bulk Send -> Schedule

```bash
# 1. Create a custom group
curl -X POST https://apiv2.waiflow.app/api/v2/custom-groups \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "VIP Clients"}'

# 2. Add members to the group
curl -X POST https://apiv2.waiflow.app/api/v2/custom-groups/{group_id}/members/add \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"contacts": [{"phone": "+15550123456"}, {"phone": "+15550987654"}, {"phone": "+15551112222"}]}'

# 3. Bulk send to the group
curl -X POST https://apiv2.waiflow.app/api/v2/bulk-send \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-uuid-...",
    "custom_group_id": "group-uuid-...",
    "message_content": "Exclusive offer for our VIP clients!"
  }'

# 4. Schedule a weekly follow-up to the group
curl -X POST https://apiv2.waiflow.app/api/v2/scheduled-messages \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly VIP Update",
    "session_id": "session-uuid-...",
    "custom_group_id": "group-uuid-...",
    "schedule_type": "cron",
    "message_content": "Weekly report is ready!",
    "cron_expression": "0 9 * * MON",
    "timezone": "Asia/Jerusalem"
  }'
```

### Pause and resume a bulk send

```bash
# Pause
curl -X POST https://apiv2.waiflow.app/api/v2/bulk-send/{job_id}/pause \
  -H "X-API-Key: $MOLTFLOW_API_KEY"

# Resume
curl -X POST https://apiv2.waiflow.app/api/v2/bulk-send/{job_id}/resume \
  -H "X-API-Key: $MOLTFLOW_API_KEY"
```

### Export group members

```bash
curl https://apiv2.waiflow.app/api/v2/custom-groups/{group_id}/export/csv \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -o vip-clients.csv
```

---

## Plan Limits

| Feature | Free | Starter | Pro | Business |
|---------|------|---------|-----|----------|
| Custom Groups | 2 | 5 | 20 | 100 |
| Bulk Send | -- | Yes | Yes | Yes |
| Scheduled Messages | -- | Yes | Yes | Yes |
| Scheduled Reports | 2 | 5 | 10 | Unlimited |
| Messages/month | 50 | 500 | 1,500 | 3,000 |

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid input) |
| 401 | Unauthorized (missing or invalid auth) |
| 403 | Forbidden (plan limit or feature gate) |
| 404 | Resource not found |
| 422 | Validation error (missing required fields) |
| 429 | Rate limited |

---

## Related Skills

- **moltflow** -- Core API: sessions, messaging, groups, labels, webhooks
- **moltflow-leads** -- Lead detection, pipeline tracking, bulk operations, CSV/JSON export
- **moltflow-ai** -- AI-powered auto-replies, voice transcription, RAG, style profiles
- **moltflow-a2a** -- Agent-to-Agent protocol, encrypted messaging, content policy
- **moltflow-reviews** -- Review collection and testimonial management
- **moltflow-admin** -- Platform administration, user management, plan configuration

---

## WhatsApp Channels (v7.0)

Broadcast one-way to WhatsApp Channel followers without exposing your phone number. No anti-spam delays needed — channel posts are newsletters, not 1-on-1 messages.

### Real-World Scenarios

**Publisher** — "Post our weekly newsletter to the channel every Monday at 9 AM"

Schedule a recurring channel post with cron `0 9 * * 1`.

**Brand** — "Announce a product launch now to all 3,000 channel followers"

Call `broadcast_channel_post` with the announcement text.

### Key Endpoints

| Action | Method | Path |
|--------|--------|------|
| List channels | GET | `/api/v2/channels` |
| Get channel | GET | `/api/v2/channels/{id}` |
| Create channel | POST | `/api/v2/channels` |
| Discover importable channels | GET | `/api/v2/channels/discover?session_id=` |
| Import existing channel | POST | `/api/v2/channels/import` |
| Delete channel | DELETE | `/api/v2/channels/{id}` |
| Broadcast post | POST | `/api/v2/channels/{id}/broadcast` |
| Sync followers | POST | `/api/v2/channels/{id}/sync-followers` |
| Check media support | GET | `/api/v2/channels/capabilities` |
| Schedule channel post | POST | `/api/v2/scheduled-messages` (target_type: channel) |

### Plan Limits

| Plan | Channels | Posts/Month |
|------|----------|-------------|
| Free | 1 | 10 |
| Starter | 2 | 50 |
| Pro | 5 | 500 |
| Business | 20 | 2,000 |

### Example: Broadcast Now

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/channels/{channel_id}/broadcast \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "New product just launched. Tap the link for early access."}'
```

### Example: Discover and Import Existing Channels

```bash
# Discover and import existing channels
curl "https://apiv2.waiflow.app/api/v2/channels/discover?session_id=$SESSION_ID" \
  -H "X-API-Key: $MOLTFLOW_API_KEY"
# Returns: [{wa_channel_id, name, follower_count, role}, ...]

# Import a discovered channel
curl -X POST https://apiv2.waiflow.app/api/v2/channels/import \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-uuid", "wa_channel_id": "123@newsletter"}'
```

### Example: Schedule Weekly Post

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/scheduled-messages \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Newsletter",
    "session_id": "uuid",
    "channel_id": "uuid",
    "target_type": "channel",
    "message_content": "Weekly update...",
    "schedule_type": "recurring",
    "cron_expression": "0 9 * * 1"
  }'
```
