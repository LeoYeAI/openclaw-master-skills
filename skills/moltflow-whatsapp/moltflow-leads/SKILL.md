---
name: moltflow-leads
description: "WhatsApp lead detection and CRM pipeline. Detect purchase-intent signals in groups, track lead status, bulk operations, CSV/JSON export. Use when: leads, lead detection, pipeline, qualify, convert, bulk status, export leads."
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

# MoltFlow Leads -- Detection & CRM Pipeline

Detect purchase-intent signals from monitored WhatsApp groups, track leads through a sales pipeline, perform bulk operations, and export for your CRM.

## Real-World Scenarios

**Real estate agent** — "Monitor my property groups for keywords like 'looking for', '3 bedrooms', and 'budget' — anyone who matches goes straight into my lead pipeline."

**Car dealership** — "When a lead moves from 'contacted' to 'qualified', automatically add them to my VIP follow-up group for a test drive invite."

**Insurance broker** — "Export all converted leads from this quarter as a CSV so I can import them into my CRM for commission tracking."

**Wedding planner** — "Show me all new leads from my vendor groups that I haven't contacted yet, sorted by detection date."

## When to Use

- "List leads" or "show detected leads"
- "Update lead status" or "mark lead as contacted"
- "Bulk update leads" or "change status for multiple leads"
- "Add leads to group" or "bulk add to custom group"
- "Export leads as CSV" or "download leads JSON"
- "Check lead reciprocity" or "has this lead messaged me?"
- "Filter leads by status" or "search leads"

## Prerequisites

1. **MOLTFLOW_API_KEY** -- Generate from the [MoltFlow Dashboard](https://molt.waiflow.app) under Settings > API Keys
2. At least one monitored WhatsApp group with keyword detection enabled
3. Base URL: `https://apiv2.waiflow.app/api/v2`

## Required API Key Scopes

| Scope | Access |
|-------|--------|
| `leads` | `read/manage` |
| `groups` | `read` |

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

## How Lead Detection Works

1. You configure group monitoring via the Groups API (see `moltflow` skill)
2. Set `monitor_mode: "keywords"` with keywords like `"looking for"`, `"price"`, `"interested"`
3. When a keyword match is detected, MoltFlow auto-creates a lead
4. Leads appear in the Leads API with status `new` and the triggering keyword highlighted
5. You track them through the pipeline: `new` -> `contacted` -> `qualified` -> `converted`

## AI Group Intelligence (Pro+ Plans)

When AI monitoring is enabled on a group (`monitor_mode: "ai_analysis"`), each message is classified by an LLM using your own API key (OpenAI, Anthropic, Groq, or Mistral). Results are available on each message and on the `lead.detected` webhook.

**AI analysis fields** — available via `GET /api/v2/groups/{group_id}/messages` and the MCP tool `moltflow_get_group_messages`:

| Field | Type | Description |
|-------|------|-------------|
| `intent` | string | `buying_intent`, `product_inquiry`, `support_request`, `complaint`, `off_topic`, `spam_noise`, `unknown` |
| `lead_score` | integer | 1-10 (10 = highest buying signal) |
| `confidence` | float | 0.0-1.0 classifier confidence |
| `reason` | string | Human-readable explanation for the classification |

**Webhook events for AI leads:**
- `lead.detected` — fires immediately when a lead is created; includes `ai_analysis` field (may be null if AI hasn't completed yet)
- `group.message.analyzed` — fires after AI analysis completes (Pro/Business only); includes full `ai_analysis` object

**Setup:**
1. Go to Settings > AI Configuration and add your LLM API key
2. Set `monitor_mode: "ai_analysis"` on the group (via PATCH `/api/v2/groups/{id}` or dashboard)
3. Optionally set `monitor_prompt` for custom classification instructions

---

## Leads API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/leads` | List leads (filter by status, group, search) |
| GET | `/leads/{id}` | Get lead details |
| PATCH | `/leads/{id}/status` | Update lead status (state machine validated) |
| GET | `/leads/{id}/reciprocity` | Check if lead messaged you first (anti-spam) |
| POST | `/leads/bulk/status` | Bulk update lead status |
| POST | `/leads/bulk/add-to-group` | Bulk add leads to custom group |
| GET | `/leads/export/csv` | Export as CSV (Pro+ plan, max 10,000) |
| GET | `/leads/export/json` | Export as JSON (Pro+ plan, max 10,000) |

### List Leads

**GET** `/leads`

Query parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status (`new`, `contacted`, `qualified`, `converted`, `lost`) |
| `source_group_id` | UUID | Filter by source monitored group |
| `search` | string | Search in contact name, phone, or keyword |
| `limit` | int | Page size (default 50) |
| `offset` | int | Pagination offset |

**Response** `200 OK`:

```json
{
  "leads": [
    {
      "id": "lead-uuid-...",
      "contact_phone": "+15550123456",
      "contact_name": "John D.",
      "lead_status": "new",
      "lead_score": 0,
      "lead_detected_at": "2026-02-12T14:30:00Z",
      "source_group": {
        "id": "group-uuid-...",
        "name": "Real Estate IL"
      },
      "trigger": {
        "matched_keyword": "interested in buying",
        "message_preview": "Hi, I'm interested in buying a 3-bedroom...",
        "monitor_mode": "keywords",
        "detected_at": "2026-02-12T14:30:00Z"
      }
    }
  ],
  "total": 47,
  "limit": 50,
  "offset": 0
}
```

### Get Lead Details

**GET** `/leads/{id}`

Returns full lead info including group context, detection metadata, message count, and status.

### Update Lead Status

**PATCH** `/leads/{id}/status`

```json
{
  "status": "contacted"
}
```

**State machine validation** -- only valid transitions are allowed:

- `new` -> `contacted`, `qualified`, `converted`, `lost`
- `contacted` -> `qualified`, `converted`, `lost`
- `qualified` -> `converted`, `lost`
- `converted` -> (terminal -- no further transitions)
- `lost` -> `new` (reopen only)

Invalid transitions return `400 Bad Request`.

### Reciprocity Check

**GET** `/leads/{id}/reciprocity?session_id=session-uuid`

The `session_id` query parameter is **required** -- it specifies which WhatsApp session to check inbound messages from.

```json
{
  "lead_id": "lead-uuid-...",
  "has_messaged_first": true,
  "last_inbound_at": "2026-02-12T15:00:00Z"
}
```

Use this before reaching out -- if the lead hasn't messaged you directly, sending a cold message may trigger WhatsApp spam detection.

### Bulk Status Update

**POST** `/leads/bulk/status`

```json
{
  "lead_ids": ["uuid1", "uuid2", "uuid3"],
  "status": "contacted"
}
```

**Response** `200 OK`:

```json
{
  "updated": 3,
  "failed": 0,
  "errors": []
}
```

Each lead is individually validated against the state machine. Leads with invalid transitions are reported in `errors` but don't block the rest.

### Bulk Add to Custom Group

**POST** `/leads/bulk/add-to-group`

```json
{
  "lead_ids": ["uuid1", "uuid2"],
  "custom_group_id": "custom-group-uuid-..."
}
```

Adds leads' phone numbers to the specified custom group for use with Bulk Send or Scheduled Messages.

### Export Leads

**GET** `/leads/export/csv` -- Returns CSV file download
**GET** `/leads/export/json` -- Returns JSON array

Both support optional filters: `status`, `source_group_id`, `search`. Max 10,000 rows per export.

**Requires Pro plan or above.**

---

## Examples

### Full workflow: Detect -> Qualify -> Outreach

```bash
# 1. List new leads from a specific group
curl "https://apiv2.waiflow.app/api/v2/leads?status=new&source_group_id=group-uuid" \
  -H "X-API-Key: $MOLTFLOW_API_KEY"

# 2. Check reciprocity before reaching out
curl "https://apiv2.waiflow.app/api/v2/leads/{lead_id}/reciprocity?session_id=session-uuid" \
  -H "X-API-Key: $MOLTFLOW_API_KEY"

# 3. Update status to contacted
curl -X PATCH https://apiv2.waiflow.app/api/v2/leads/{lead_id}/status \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "contacted"}'

# 4. Bulk add qualified leads to a custom group for follow-up
curl -X POST https://apiv2.waiflow.app/api/v2/leads/bulk/add-to-group \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_ids": ["uuid1", "uuid2", "uuid3"],
    "custom_group_id": "follow-up-group-uuid"
  }'

# 5. Export all converted leads as CSV
curl "https://apiv2.waiflow.app/api/v2/leads/export/csv?status=converted" \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -o converted-leads.csv
```

---

## Plan Requirements

| Feature | Free | Starter | Pro | Business |
|---------|------|---------|-----|----------|
| Lead detection | Yes (2 groups) | Yes (5 groups) | Yes (20 groups) | Yes (100 groups) |
| Lead list & detail | Yes | Yes | Yes | Yes |
| Status update | Yes | Yes | Yes | Yes |
| Bulk operations | -- | -- | Yes | Yes |
| CSV/JSON export | -- | -- | Yes | Yes |

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Invalid status transition or bad request |
| 401 | Unauthorized (missing or invalid auth) |
| 403 | Forbidden (plan limit or feature gate) |
| 404 | Lead not found |
| 429 | Rate limited |

---

## Related Skills

- **moltflow** -- Core API: sessions, messaging, groups, labels, webhooks
- **moltflow-outreach** -- Bulk Send, Scheduled Messages, Custom Groups
- **moltflow-ai** -- AI-powered auto-replies, voice transcription, RAG, style profiles
- **moltflow-a2a** -- Agent-to-Agent protocol, encrypted messaging, content policy
- **moltflow-reviews** -- Review collection and testimonial management
- **moltflow-admin** -- Platform administration, user management, plan configuration
