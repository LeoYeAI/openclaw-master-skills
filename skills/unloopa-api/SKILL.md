---
name: unloopa-api
description: Make your agent sell websites to local businesses on autopilot. Finds leads from Google Maps, builds a custom AI website for each one, sends outreach emails, and can even call them. Use when the user wants to find leads, generate websites, send emails, or make voice calls.
metadata:
  author: unloopa
  version: "1.3"
  openclaw:
    primaryEnv: UNLOOPA_API_KEY
    requires:
      env:
        - UNLOOPA_API_KEY
---

# Unloopa API

You control the Unloopa platform through its REST API. All requests go to `https://dashboard.unloopa.com/api/v1/` with Bearer token authentication.

## Authentication

Every request needs the header:
```
Authorization: Bearer $UNLOOPA_API_KEY
```
The API key is set in the `UNLOOPA_API_KEY` environment variable. Keys start with `unlpa_live_`.

If the user hasn't configured their key yet, tell them:
1. Go to https://dashboard.unloopa.com/settings and click the "API" tab
2. Click "Create API Key" and copy the key (it's only shown once)
3. Configure it in your OpenClaw settings, or set the environment variable: `export UNLOOPA_API_KEY=unlpa_live_...`

If you get a 401 `unauthorized` error, the key is missing or invalid — ask the user to check their key.

## First Call: Always Start With GET /quota

**Before doing anything else**, call `GET /quota` to discover:
- What **plan** the user is on (starter or pro)
- Whether **voice** and **video** features are enabled
- How many **leads** and **credits** remain
- **Purchase links** if they need to upgrade or buy credits

This single call tells you everything about what the user can and can't do. Adapt your behavior based on the response:

| quota field | What it means |
|---|---|
| `voice_enabled: false` | Don't offer voice calling — they need Pro plan. Share `purchase_links.upgrade` |
| `video_enabled: false` | Don't offer video generation — they need Pro plan |
| `voice_credits: 0` | Can't make calls — share `purchase_links.voice_credits` |
| `websites.remaining: 0` | Can't generate leads — quota resets at `resets_at` |

## Error Format

All errors return:
```json
{ "error": { "code": "error_code", "message": "Human-readable message", "details": {} } }
```

Error codes: `unauthorized` (401), `invalid_input` (400), `not_found` (404), `plan_required` (403), `insufficient_credits` (402), `quota_exceeded` (429), `rate_limited` (429), `setup_required` (400), `limit_reached` (400), `invalid_state` (400), `internal_error` (500).

When you get `plan_required` (403), share the upgrade link from quota. When you get `insufficient_credits` (402), share the credit purchase links. When rate limited, check the `Retry-After` header (seconds).

## Plans

- **Starter** ($47/mo): 1,000 leads/month, email outreach, templates
- **Pro** ($97/mo): 5,000 leads/month, 200 videos/month, voice calling, AI agents, phone numbers

---

## Workflows

### 1. Full Lead Pipeline (any plan)
The `/command` endpoint runs the **entire pipeline automatically**: scrape leads → generate websites → enrich emails → send outreach. Just describe what you want.
```
1. GET  /quota                    → check websites.remaining > 0
2. POST /command                  → submit natural language command (full pipeline runs automatically)
3. GET  /jobs/{job_id}            → poll every 5-10s until status=completed
4. GET  /leads?job_id={job_id}    → view generated leads with websites, emails, etc.
```

### 2. Email Outreach (any plan)
```
1. GET  /outreach/status          → verify configured=true, remaining_today > 0
2. GET  /leads?has_email=true     → find leads with emails
3. GET  /outreach/templates       → pick a template
4. POST /outreach/send            → queue emails
```
If `configured=false`, tell the user to connect an email account at the `setup_url` in the response.

### 3. Voice Calling (Pro plan only)
**Skip this workflow entirely if `voice_enabled=false` in /quota.** Tell the user they need Pro and share the upgrade link.

Prerequisites: voice_enabled=true + voice_credits > 0 + at least 1 phone number + at least 1 voice agent.
```
1. GET  /quota                    → voice_enabled? voice_credits > 0?
   If voice_credits=0 → share purchase_links.voice_credits
2. GET  /phone-numbers            → count > 0? (max 3)
   If empty → POST /phone-numbers/search + POST /phone-numbers/buy
3. GET  /voice/agents             → count > 0? (max 3)
   If empty → POST /voice/agents (create one)
4. POST /voice/call               → single call, OR:
5. POST /voice/campaigns          → bulk campaign (starts as draft)
6. PATCH /voice/campaigns/{id}    → action=activate, then action=trigger
```

### 4. Full Funnel
The `/command` endpoint now handles steps 1-3 automatically. Voice calling is the only manual step.
```
1. GET  /quota                    → know the plan, adapt accordingly
2. POST /command → poll /jobs/{id} → GET /leads  (scrape + websites + emails + outreach all automatic)
3. Voice (Pro only): /phone-numbers → /voice/agents → /voice/campaigns
```

---

## Endpoints Reference

### POST /command
Submit a natural language lead generation command. The API automatically runs the **full pipeline**: scrape → generate websites → enrich emails/socials → send outreach. No need to mention each step in the command.

**Body:**
```json
{
  "command": "Find 50 plumbers in Miami",
  "max_results": 50,
  "with_video": false,
  "with_vsl": false
}
```
- `command` (required, string, max 1000 chars) — just describe the niche and location. **Any number mentioned in the command is ignored** — use `max_results` to control lead count.
- `max_results` (optional, 1-100, default: **100**, or **10** when `with_video`/`with_vsl` is true)
- `with_video` (optional, bool, Pro plan only)
- `with_vsl` (optional, bool, Pro plan only)

**Default behavior:** The API always overrides what's in the command text. It scrapes up to `max_results` leads (default 100), generates a website for each, finds email addresses, enriches social profiles, and sends outreach emails — all automatically. Numbers in the command like "Find 15 plumbers" are ignored; use `max_results` instead.

**Response:** `{ job_id, status: "processing", defaults: { max_results, generate_websites, enrich_emails, send_outreach, with_video, with_vsl }, quota: { used, limit, remaining } }`

---

### GET /jobs
List submitted commands.

**Query:** `?limit=20&offset=0` (limit max 100)

**Response:** `{ jobs: [{ job_id, command, intent, status, error, created_at, updated_at }], total, limit, offset }`

---

### GET /jobs/{id}
Poll a job for progress and results.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "processing|completed|failed",
  "progress": 75,
  "current_step": "Generating websites...",
  "steps": [{ "name": "scraping", "status": "completed", "message": "Found 50 leads", "count": 50 }],
  "result": {
    "websites": [{ "id": "uuid", "url": "https://...", "business_name": "...", "city": "...", "industry": "..." }],
    "leads_scraped": 50,
    "emails_sent": 0
  },
  "error": null
}
```
Poll every 5-10 seconds. Jobs take 30s to 5 minutes depending on count and video.

---

### GET /leads
List and filter leads.

**Query params (all optional):**
- `limit` (1-100, default 50), `offset` (default 0)
- `city` — partial match (e.g. "miami")
- `industry` — partial match (e.g. "plumber")
- `has_phone=true` — only leads with phone numbers
- `has_email=true` — only leads with email addresses
- `min_rating` — minimum Google rating (e.g. 4.0)
- `min_reviews` — minimum review count
- `job_id` — leads from a specific command
- `search` — free text search across name, city, industry
- `created_after` — ISO date (e.g. "2025-01-15")
- `created_before` — ISO date
- `has_website=true` — only leads with generated website URLs
- `has_video=true` — only leads with video
- `video_status` — pending|generating|completed|failed

**Response:**
```json
{
  "leads": [{
    "id": "uuid",
    "business_name": "Acme Plumbing",
    "city": "Miami",
    "industry": "Plumber",
    "phone": "+13055551234",
    "email": "info@acme.com",
    "rating": 4.8,
    "reviews": 127,
    "url": "https://unlora.com/acme-plumbing-miami",
    "language": "en",
    "video_url": "https://...",
    "video_status": "completed",
    "vsl_url": "https://...",
    "vsl_status": "completed",
    "socials": { "instagram": "...", "facebook": "...", "linkedin": "...", "twitter": "..." },
    "created_at": "2025-01-15T..."
  }],
  "total": 50, "limit": 50, "offset": 0
}
```

---

### GET /leads/{id}
Full lead detail including existing website analysis.

**Response:** Same fields as list plus:
- `slug` — URL slug
- `existing_website: { url, pagespeed_score, load_time, mobile_optimized }` or null

---

### GET /websites
Simpler list of generated websites.

**Query:** `?limit=20&offset=0`

**Response:** `{ websites: [{ id, url, slug, business_name, city, industry, phone, email, language, video_url, vsl_url, created_at }], total, limit, offset }`

---

### GET /quota
Check plan, usage, credits, and purchase links.

**Response:**
```json
{
  "plan": "pro",
  "plan_status": "active",
  "websites": { "used": 150, "limit": 5000, "remaining": 4850 },
  "videos": { "used": 0, "limit": 200, "remaining": 200 },
  "voice_credits": 45,
  "voice_enabled": true,
  "video_enabled": true,
  "resets_at": "2025-02-01T00:00:00.000Z",
  "purchase_links": {
    "voice_credits": {
      "50_credits_$10": "https://whop.com/checkout/plan_xBEWrVWZ8MRvM/",
      "200_credits_$35": "https://whop.com/checkout/plan_ucYBrssGb4E2G/",
      "500_credits_$75": "https://whop.com/checkout/plan_zTX2bQyWLCqlx/"
    },
    "upgrade": "https://whop.com/unloopa/"
  }
}
```

---

### GET /outreach/status
Check email configuration, daily capacity, DNS health.

**Response:**
```json
{
  "configured": true,
  "accounts": [{
    "id": "uuid",
    "email": "outreach@company.com",
    "display_name": "Company",
    "daily_limit": 25,
    "sent_today": 10,
    "remaining_today": 15,
    "warmup_enabled": true,
    "warmup_day": 14,
    "health": { "score": 85, "status": "good", "checked_at": "2025-01-15T..." },
    "created_at": "2025-01-01T..."
  }],
  "summary": {
    "total_accounts": 1,
    "total_daily_capacity": 25,
    "total_sent_today": 10,
    "total_remaining_today": 15,
    "pending_in_queue": 5,
    "accounts_with_health_issues": 0
  },
  "setup_url": "https://dashboard.unloopa.com/settings?tab=email"
}
```
New SMTP accounts warm up over 4 weeks: 5/day -> 10/day -> 15/day -> 25/day.

---

### GET /outreach/templates
List prebuilt and custom email templates.

**Response:** `{ templates: [{ id, name, subject, body, is_custom: false, is_default: true, language }], custom_templates: [{ id, name, subject, body, is_custom: true, is_default, language }] }`

Templates support placeholders: `{{business_name}}`, `{{city}}`, `{{industry}}`, `{{website_url}}`, `{{video_url}}` (Pro only).

---

### POST /outreach/templates
Create custom email template.

**Body:**
```json
{
  "name": "Miami Pitch",
  "subject": "{{business_name}} - New Website Ready",
  "body": "Hi! I built a website for {{business_name}} in {{city}}...",
  "language": "en",
  "is_default": true
}
```
Required: name, subject, body.

---

### PATCH /outreach/templates/{id}
Update a custom template. Only custom templates can be edited.

**Body:** `{ name?, subject?, body?, language?, is_default? }`

---

### DELETE /outreach/templates/{id}
Delete a custom template.

---

### POST /outreach/send
Send emails to leads.

**Body:**
```json
{
  "lead_ids": ["uuid1", "uuid2"],
  "template_id": "uuid",
  "custom_subject": "Optional override",
  "custom_body": "Optional override"
}
```
- `lead_ids` (required, 1-100 UUIDs)
- `template_id` (optional if custom_subject + custom_body provided)

**Response:** `{ emails_queued, emails_waiting_for_video, skipped_duplicates, failed, manual_outreach: [] }`

Requires SMTP configured (check `/outreach/status` first). Duplicate detection prevents re-sending.

---

### GET /phone-numbers
List active phone numbers. Pro plan required.

**Response:** `{ numbers: [{ id, phone_number, area_code, locality, region, country, monthly_cost_cents, created_at }], count: 2, limit: 3 }`

Max 3 phone numbers. Check `count` vs `limit` before buying.

---

### POST /phone-numbers/search
Search available numbers by area code. Pro plan required.

**Body:** `{ "area_code": "305", "country": "US" }`
- `area_code` (required, 3 digits)
- `country` (optional, default "US")

**Response:** `{ numbers: [{ phone_number: "+13055551234", friendly_name, locality, region }] }`

---

### POST /phone-numbers/buy
Purchase a phone number. Pro plan required. $1/month per number.

**Body:** `{ "phone_number": "+13055551234" }`
Must be E.164 format from search results.

**Response:** `{ number: { id, phone_number, area_code, monthly_cost_cents, created_at } }`

---

### DELETE /phone-numbers/{id}
Release a phone number. Pro plan required.

**Response:** `{ success: true }`

---

### GET /voice/agents
List voice agents. Pro plan required.

**Response:** `{ agents: [{ id, name, voice_id, voice_name, elevenlabs_agent_id, has_script, has_first_message, created_at }], count: 1, limit: 3 }`

Max 3 agents.

---

### POST /voice/agents
Create a voice agent. Pro plan required.

**Body:**
```json
{
  "name": "Sales Agent",
  "voice_id": "cjVigY5qzO86Huf0OWal",
  "voice_name": "Eric",
  "script": "You are a friendly sales rep calling {{business_name}} in {{city}}...",
  "first_message": "Hi there, do you have just a moment?",
  "agent_config": { "stability": 0.3, "similarityBoost": 0.85 }
}
```
Required: name, voice_id, script.

Scripts support dynamic variables: `{{business_name}}`, `{{city}}`, `{{industry}}`, `{{website_url}}` — auto-populated from lead data during calls.

---

### PATCH /voice/agents/{id}
Update a voice agent. Syncs changes to ElevenLabs automatically.

**Body:** `{ name?, voice_id?, voice_name?, script?, first_message?, agent_config? }`

---

### DELETE /voice/agents/{id}
Delete a voice agent. Also removes from ElevenLabs.

---

### POST /voice/call
Make a single outbound call. Costs 1 voice credit. Pro plan required.

**Body:**
```json
{
  "agent_id": "uuid",
  "phone_number": "+13055551234",
  "dynamic_variables": { "business_name": "Acme", "city": "Miami", "industry": "Plumbing", "website_url": "https://..." }
}
```
Required: agent_id, phone_number.

**Response:** `{ call_id, conversation_id, status: "initiated", phone_number }`

---

### GET /voice/calls
List voice calls with filters. Pro plan required.

**Query:** `?limit=50&offset=0&campaign_id=uuid&status=completed&outcome=interested`
- `status`: pending, queued, in_progress, completed, failed, cancelled
- `outcome`: interested, not_interested, voicemail, no_answer, callback

**Response:** `{ calls: [{ id, campaign_id, business_name, phone_number, status, outcome, outcome_notes, duration_secs, transcript, analysis, started_at, completed_at, created_at }], total, limit, offset }`

---

### GET /voice/calls/{id}
Full call detail with transcript and analysis.

**Response:** `{ call_id, business_name, phone_number, status, outcome, outcome_notes, duration_secs, transcript, analysis, started_at, completed_at, created_at }`

---

### GET /voice/campaigns
List voice campaigns with stats. Pro plan required.

**Response:**
```json
{
  "campaigns": [{
    "id": "uuid",
    "name": "Miami Plumbers",
    "status": "active",
    "stats": { "total": 50, "connected": 30, "interested": 8, "not_interested": 15, "no_answer": 7, "failed": 0, "avg_duration_secs": 45 },
    "created_at": "...", "updated_at": "..."
  }]
}
```

---

### POST /voice/campaigns
Create a calling campaign. Starts as `draft`. Pro plan + voice credits required.

**Body:**
```json
{
  "name": "Miami Plumbers Campaign",
  "phone_number_id": "uuid",
  "agent_id": "uuid",
  "lead_filter": { "city": "Miami", "industry": "plumber" },
  "timezone": "America/New_York",
  "calling_window_start": "09:00",
  "calling_window_end": "17:00",
  "calling_days": ["mon", "tue", "wed", "thu", "fri"],
  "calls_per_hour": 10,
  "max_calls": 50
}
```
Required: name, phone_number_id, and either `agent_id` OR `voice_id` + `script`.
Lead selection: provide `lead_ids` (array of UUIDs) or `lead_filter` (dynamic). Only leads with phone numbers are included.

**Response:** `{ campaign: { id, name, status: "draft", leads_count, callable_leads, created_at } }`

---

### GET /voice/campaigns/{id}
Campaign detail with full config and stats.

**Response includes:** id, name, status, script, script_version, first_message, voice_id, voice_name, timezone, calling_window, calling_days, calls_per_hour, max_calls, stats (with pending count), timestamps.

---

### PATCH /voice/campaigns/{id}
Control campaign lifecycle or update fields.

**Lifecycle actions** (body: `{ "action": "..." }`):
- `activate` — draft/paused -> active
- `pause` — active -> paused
- `cancel` — any -> completed (cancels pending calls)
- `trigger` — active campaign: initiate up to 10 pending calls immediately. Each call costs 1 voice credit. Optional: `{ "action": "trigger", "limit": 5 }`

**Field updates** (draft/paused only, body: `{ "updates": {...} }`):
- script, voice_id, voice_name, first_message, calling_window_start, calling_window_end, timezone, calling_days, calls_per_hour, agent_config

Trigger response: `{ triggered: 5, calls: [{ id, business_name, conversation_id }] }`

---

## Important Notes

- Job processing takes ~8-10 minutes for a full pipeline run. Scraping is fast (~20 seconds), but website generation takes ~8 minutes for all websites. Do NOT assume the job is stuck — poll every 15-20 seconds and be patient during the website_generation step
- Email warmup: new SMTP accounts start at 5/day, ramping to 25/day over 4 weeks
- Voice campaigns must be: created (draft) -> activated -> triggered
- The `trigger` action initiates up to 10 calls at a time, costing 1 credit each
- Dynamic variables (`{{business_name}}`, etc.) are auto-populated from lead data
- Duplicate email detection prevents re-sending to the same lead
- Video features (`with_video`, `with_vsl`) are Pro plan only
- Phone numbers and voice agents have a hard limit of 3 each
- Always check preconditions before taking action (quota, credits, SMTP, plan)
