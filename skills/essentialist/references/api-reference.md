# Essentialist API Reference

Base URL: `$ESSENTIALIST_API_URL` (default: `https://essentialist-anfc.onrender.com`)

Authentication: `X-API-Key: $ESSENTIALIST_API_KEY` header on all requests (except register and capabilities).

## Registration & Discovery (Public — No Auth)

### POST /api/agent/register

Create an account and get an API key. No authentication required. Idempotent — if the email is already registered, returns existing credentials.

Rate limit: 5 requests per hour per IP.

**Request Body:**

```json
{
  "email": "agent@example.com",
  "password": "optional-password"
}
```

**Response:**

```json
{
  "summary": "Account created for agent@example.com...",
  "data": {
    "api_key": "abc123...",
    "project_id": "uuid",
    "user_id": "uuid",
    "tier": "free",
    "limits": { "emails_per_month": 100, "leads_per_month": 50 },
    "already_existed": false
  },
  "next_actions": [...]
}
```

```bash
curl -s -X POST "$ESSENTIALIST_API_URL/api/agent/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "agent@example.com"}' | jq
```

---

### GET /api/agent/capabilities

Discovery endpoint. Returns all available endpoints, pricing tiers, event types, and quick start instructions. No auth required.

```bash
curl -s "$ESSENTIALIST_API_URL/api/agent/capabilities" | jq
```

**Response includes:**
- `tiers` — pricing with payment links
- `endpoints` — all available API endpoints grouped by function
- `event_types` — all event types the agent can poll for
- `quick_start` — step-by-step instructions
- `authentication` — how to authenticate

---

## Agent Orchestration Endpoints

### POST /api/agent/campaigns

Create a full campaign in one call: project, templates, track, rail cars, contacts.

**Headers:**
- `X-API-Key` (required)
- `Content-Type: application/json`
- `Idempotency-Key` (optional, prevents duplicate creation on retry)

**Request Body:**

```json
{
  "project_id": "uuid (optional, creates new project if omitted)",
  "name": "Campaign Name (required if no project_id)",
  "mailgun_domain": "domain.com (required if no project_id)",
  "mailgun_api_key": "key-xxx (optional)",
  "system_prompt": "AI persona instructions (optional)",
  "templates": [
    {
      "name": "Cold Intro",
      "subject": "Quick question about {{company}}",
      "body": "<p>Hi {{first_name}},...</p>",
      "days_after_previous": 0
    },
    {
      "name": "Follow-up",
      "content_prompt": "Write a follow-up email about SEO services for law firms",
      "days_after_previous": 3
    }
  ],
  "track_name": "Law Firm SEO Q1",
  "send_mode": "slow_roll",
  "agentmail_mailbox_id": "uuid (optional)",
  "contacts": [
    {
      "email": "jane@smithlaw.com",
      "first_name": "Jane",
      "last_name": "Smith",
      "custom_fields": { "company": "Smith & Associates" }
    }
  ],
  "activate": false
}
```

**Template options:**
- Provide `subject` + `body` for manual templates
- Provide `content_prompt` for AI-generated templates (subject and body auto-generated)
- Max 10 templates per campaign

**Contacts:**
- Max 10,000 per campaign
- Duplicates (already on track) are skipped
- Invalid emails are skipped

**Response:** Dual-layer envelope with `summary`, `data`, `warnings`, `next_actions`

**Partial failure:** Returns HTTP 207 with per-step results and `resume_from` pointer.

```bash
curl -s -X POST "$ESSENTIALIST_API_URL/api/agent/campaigns" \
  -H "X-API-Key: $ESSENTIALIST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Law Firm SEO",
    "mailgun_domain": "mail.example.com",
    "templates": [
      {"name": "Intro", "subject": "SEO for {{company}}", "body": "<p>Hi {{first_name}},</p>", "days_after_previous": 0},
      {"name": "Follow-up", "content_prompt": "Write a brief follow-up", "days_after_previous": 3}
    ],
    "track_name": "Law Firm SEO Q1",
    "contacts": [
      {"email": "jane@example.com", "first_name": "Jane", "last_name": "Smith"}
    ]
  }' | jq
```

---

### GET /api/agent/campaigns/{project_id}/summary

Composite dashboard: tracks, performance totals, **pipeline stages**, AgentMail stats, domain health, recent leads.

```bash
curl -s "$ESSENTIALIST_API_URL/api/agent/campaigns/{project_id}/summary" \
  -H "X-API-Key: $ESSENTIALIST_API_KEY" | jq
```

**Response data includes:**
- `tracks[]` with per-car send/open/click stats
- `totals` with open_rate, reply_rate, bounce_rate
- `pipeline` with contact counts per lifecycle stage (new, contacted, engaged, qualified, won, lost, unsubscribed, total)
- `agentmail` with classification breakdown
- `warming` with domain health status
- `recent_leads[]` with reply excerpts

---

### GET /api/agent/campaigns/{project_id}/preflight

Validates campaign readiness before activation.

```bash
curl -s "$ESSENTIALIST_API_URL/api/agent/campaigns/{project_id}/preflight" \
  -H "X-API-Key: $ESSENTIALIST_API_KEY" | jq
```

**Checks performed:**
- `mailgun_domain_configured`
- `track_has_cars`
- `track_has_contacts`
- `warming_capacity`
- `send_mode_appropriate`
- `agentmail_mailbox_linked` (if configured)

---

### POST /api/agent/campaigns/{project_id}/tracks/{track_id}/activate

Activate a track. Runs preflight automatically; fails if preflight fails.

```bash
curl -s -X POST "$ESSENTIALIST_API_URL/api/agent/campaigns/{project_id}/tracks/{track_id}/activate" \
  -H "X-API-Key: $ESSENTIALIST_API_KEY" | jq
```

---

### POST /api/agent/campaigns/{project_id}/tracks/{track_id}/pause

Pause a track. Stops all sending until resumed.

```bash
curl -s -X POST "$ESSENTIALIST_API_URL/api/agent/campaigns/{project_id}/tracks/{track_id}/pause" \
  -H "X-API-Key: $ESSENTIALIST_API_KEY" | jq
```

---

### POST /api/agent/campaigns/{project_id}/tracks/{track_id}/resume

Resume a paused track. Only works on tracks with status "paused".

```bash
curl -s -X POST "$ESSENTIALIST_API_URL/api/agent/campaigns/{project_id}/tracks/{track_id}/resume" \
  -H "X-API-Key: $ESSENTIALIST_API_KEY" | jq
```

---

### GET /api/agent/campaigns/{project_id}/leads

Get contacts who replied with interested/question classification.

**Query params:**
- `limit` (default: 50)

```bash
curl -s "$ESSENTIALIST_API_URL/api/agent/campaigns/{project_id}/leads?limit=10" \
  -H "X-API-Key: $ESSENTIALIST_API_KEY" | jq
```

---

## Event Endpoints

### GET /api/agent/events

Poll for unacknowledged agent events.

**Query params:**
- `unacknowledged_only` (default: true)
- `types` (comma-separated filter, e.g., "reply_interested,bounce_alert")
- `limit` (default: 50)

```bash
curl -s "$ESSENTIALIST_API_URL/api/agent/events?unacknowledged_only=true&types=reply_interested,bounce_alert" \
  -H "X-API-Key: $ESSENTIALIST_API_KEY" | jq
```

**Event types:**

| Type | Trigger | Key Payload Fields |
|------|---------|-------------------|
| `reply_interested` | Reply classified as interested | contact_email, contact_name, company, confidence, reply_excerpt, auto_replied |
| `reply_question` | Reply classified as question | contact_email, confidence, reply_excerpt |
| `reply_not_interested` | Explicit decline | contact_email |
| `bounce_alert` | Bounce rate > 5% | bounce_rate, bounce_count, domain |
| `track_completed` | Contact finished sequence | track_id, track_name, contact_id |
| `send_failed` | Mailgun send error | send_id, contact_email, error, track_name |
| `draft_ready` | AI draft pending approval | message_id, contact_email, classification, confidence |

---

### POST /api/agent/events/acknowledge

Mark events as processed so they no longer appear in polls.

```bash
curl -s -X POST "$ESSENTIALIST_API_URL/api/agent/events/acknowledge" \
  -H "X-API-Key: $ESSENTIALIST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"event_ids": ["uuid1", "uuid2"]}' | jq
```

---

## Underlying CRUD Endpoints

These endpoints are also available for granular operations. All require `X-API-Key` header.

### Templates

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/projects/{id}/templates | List templates |
| POST | /api/projects/{id}/templates | Create template |
| PUT | /api/projects/{id}/templates/{id} | Update template |
| DELETE | /api/projects/{id}/templates/{id} | Delete template |
| POST | /api/projects/{id}/templates/generate | AI-generate template |

### Contacts & CRM Pipeline

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/projects/{id}/contacts | List contacts |
| POST | /api/projects/{id}/contacts | Create contact |
| PUT | /api/projects/{id}/contacts/{id} | Update contact |
| DELETE | /api/projects/{id}/contacts/{id} | Delete contact |
| POST | /api/projects/{id}/contacts/import | CSV import |
| GET | /api/projects/{id}/contacts/pipeline-summary | Lifecycle stage counts |
| GET | /api/projects/{id}/contacts/by-stage?stage=qualified | Filter by lifecycle stage |
| PATCH | /api/projects/{id}/contacts/{id}/stage | Manual stage override |

### Tracks

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/projects/{id}/tracks | List tracks |
| POST | /api/projects/{id}/tracks | Create track |
| PUT | /api/projects/{id}/tracks/{id} | Update track |
| DELETE | /api/projects/{id}/tracks/{id} | Delete track |
| POST | /api/projects/{id}/tracks/{id}/activate | Activate track |
| POST | /api/projects/{id}/tracks/{id}/pause | Pause track |

### AgentMail

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/agentmail/mailboxes | List mailboxes |
| GET | /api/agentmail/mailboxes/{id}/messages | List messages |
| POST | /api/agentmail/mailboxes/{id}/messages/{id}/approve | Approve draft |

### Reports

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/projects/{id}/reports/summary | Project summary |
| GET | /api/projects/{id}/reports/track/{id} | Track performance |
| GET | /api/projects/{id}/reports/export | CSV export |

### Health

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /api/health/pipeline | Pipeline health check |
| GET | /health | Basic health check |

## Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| AUTH_REQUIRED | 401 | No API key provided |
| INVALID_API_KEY | 403 | API key not found or wrong project |
| PROJECT_NOT_FOUND | 404 | Project ID does not exist |
| TRACK_NOT_FOUND | 404 | Track ID does not exist |
| TEMPLATE_NOT_FOUND | 404 | Template ID does not exist |
| CONTACT_NOT_FOUND | 404 | Contact not found |
| VALIDATION_ERROR | 400 | Invalid request data |
| DUPLICATE_CONTACT | 409 | Contact already exists on track |
| BLAST_NOT_ELIGIBLE | 400 | Blast mode requires completed slow-roll cycle |
| WARMING_LIMIT_EXCEEDED | 400 | Domain cannot handle requested volume |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |
| TEMPLATE_GENERATION_FAILED | 500 | AI template generation error |
| MAILGUN_ERROR | 502 | Mailgun API error |
| INTERNAL_ERROR | 500 | Unexpected server error |
