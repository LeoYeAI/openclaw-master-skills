---
name: "WhatsApp Business Suite — AI Leads, Channels, Campaigns & 32 MCP Tools"
version: "2.16.3"
description: "Automate WhatsApp at scale — mine leads from groups with AI, broadcast to channel followers, bulk message with ban-safe delays, schedule campaigns, auto-reply in your voice, collect reviews, and track delivery. 90+ REST endpoints, 32 MCP tools for Claude & GPT, Python SDK. No Meta Business API required. Free tier available."
source: "MoltFlow Team"
risk: safe
homepage: "https://molt.waiflow.app"
requiredEnv:
  - MOLTFLOW_API_KEY
primaryEnv: MOLTFLOW_API_KEY
disable-model-invocation: true
metadata: {"openclaw":{"emoji":"📱","homepage":"https://molt.waiflow.app","requires":{"env":["MOLTFLOW_API_KEY"]},"primaryEnv":"MOLTFLOW_API_KEY"}}
---

# WhatsApp Automation — Analyze Groups for Buying Signals

**Thousands of hidden leads are sitting in your WhatsApp groups right now.** Every group participant who isn't in your contacts is a potential client. MoltFlow analyzes your groups on demand, surfaces untapped contacts, and lets Claude run AI-powered outreach campaigns on your behalf.

**One skill. 97+ endpoints. 32 MCP tools. Zero manual prospecting.**

> **Account Health & Growth Reports**: Run a read-only
> account scan to find unanswered contacts, detect
> buying signals in group conversations, spot high-value
> groups you're not monitoring, and build targeted lead
> lists. All analysis runs on-demand when you ask —
> nothing happens in the background. No data is modified.
>
> **Native MCP Endpoint + Custom GPT Actions**: Works with Claude Desktop, Claude.ai, Claude Code, and ChatGPT (Custom GPT Actions). 25 tools via native HTTP endpoint at `apiv2.waiflow.app/mcp` -- no npm packages or Node.js required. See [integrations.md](integrations.md) for setup.

> ***Due to high demand and a recent registration issue, we're offering our top-tier Business plan with unlimited quotas for just $19.90/month on yearly billing — for a limited time only.*** [**Claim the deal**](https://buy.stripe.com/cNifZibX7gpQebJ0nsfnO00)
>
> Free tier available. [Sign up](https://molt.waiflow.app/checkout?plan=free)

---

## Just Ask Claude

Install the skill, set your API key, and tell Claude what you need:

**"Send a payment reminder to all clients with outstanding invoices on the 28th of each month"**

Creates a custom group, schedules a recurring message with cron, timezone-aware delivery.

**"Transcribe patient voice notes and save them as appointment summaries"**

Whisper transcription on incoming voice messages, retrievable via API.

**"Alert me when someone mentions 'budget', 'bedroom', or 'viewing' in my property groups"**

Keyword monitoring on WhatsApp groups, auto-creates leads in your pipeline.

**"Analyze the last 50 messages in my real estate group and score every lead"**

AI Group Intelligence classifies message intent (buying_intent, inquiry, complaint), scores leads 1-10, and surfaces high-priority contacts. Requires Pro plan + your LLM API key.

**"Set up automatic order confirmation messages after every purchase"**

Webhook listener for purchase events, triggers outbound message via API.

**"Collect customer reviews after every reservation and export the best ones"**

Sentiment-scored review collection, auto-approve positives, export as HTML for your website.

**"Send a weekly campaign performance report to my team's WhatsApp group every Monday"**

Scheduled report with WhatsApp delivery, 10 templates including campaign analytics.

**"Schedule follow-up messages to leads who haven't replied in 3 days"**

Scheduled messages to custom groups, built from lead pipeline filters.

**"Broadcast class schedule changes to all parent groups"**

Bulk send to custom groups with ban-safe throttling and delivery tracking.

**"Post our weekly product update to all 5,000 WhatsApp Channel followers every Monday"**

Schedule a recurring channel post with cron expression, tracks each post as a ChannelPost record with status.

**"Auto-respond to support questions using my knowledge base docs"**

RAG-powered AI replies grounded in your uploaded PDFs and docs.

**"Move leads from 'new' to 'contacted' after I message them, and track conversion rate"**

CRM pipeline with state machine, bulk status updates, CSV export.

**"Export all data for a customer who requested GDPR erasure"**

GDPR-compliant data export and contact erasure via API.

**"Show me which campaigns had the best read rates this week"**

Campaign analytics with delivery funnel, per-contact status, and engagement scores.

---

## Code Samples

### Get campaign analytics — delivery rates, funnel, timing

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/analytics/campaigns/{job_id}"
```

Returns delivery rate, failure breakdown, messages per minute,
and full per-contact delivery status.

### Track delivery in real-time (SSE)

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/bulk-send/{id}/progress"
```

Server-Sent Events stream: sent/failed/pending counts
update live as each message delivers.

### Top contacts by engagement score

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/analytics/contacts?sort=engagement_score&limit=50"
```

Ranked by messages sent, received, reply rate, and
recency — find your most engaged contacts instantly.

### Bulk broadcast to a contact group

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "custom_group_id": "group-uuid",
    "session_id": "uuid",
    "message": "Weekly update..."
  }' \
  https://apiv2.waiflow.app/api/v2/bulk-send
```

### Monitor a group for buying signals

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid",
    "wa_group_id": "120363012345@g.us",
    "monitor_mode": "keywords",
    "monitor_keywords": ["looking for", "need help", "budget", "price"]
  }' \
  https://apiv2.waiflow.app/api/v2/groups
```

### List new leads in your pipeline

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/leads?status=new&limit=50"
```

### Move a lead through the pipeline

```bash
curl -X PATCH -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "qualified"}' \
  https://apiv2.waiflow.app/api/v2/leads/{lead_id}/status
```

Status flow: `new` → `contacted` → `qualified` → `converted`
(or `lost` at any stage).

### Bulk add leads to a campaign group

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_ids": ["uuid-1", "uuid-2", "uuid-3"],
    "custom_group_id": "target-group-uuid"
  }' \
  https://apiv2.waiflow.app/api/v2/leads/bulk/add-to-group
```

### Export leads as CSV

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/leads/export/csv?status=qualified" \
  -o qualified-leads.csv
```

### Pause a running campaign

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  https://apiv2.waiflow.app/api/v2/bulk-send/{job_id}/pause
```

### AI reply in your writing style + knowledge base

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": "5511999999999@c.us",
    "context": "Customer asks: What is your return policy?",
    "use_rag": true,
    "apply_style": true
  }' \
  https://apiv2.waiflow.app/api/v2/ai/generate-reply
```

### Schedule a weekly follow-up

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monday check-in",
    "session_id": "uuid",
    "chat_id": "123@c.us",
    "message": "Hey! Anything I can help with this week?",
    "recurrence": "weekly",
    "scheduled_time": "2026-03-03T09:00:00",
    "timezone": "America/New_York"
  }' \
  https://apiv2.waiflow.app/api/v2/scheduled-messages
```

### Weekly report delivered to your WhatsApp

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

### Send a message

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "uuid",
    "chat_id": "1234567890@c.us",
    "message": "Hello!"
  }' \
  https://apiv2.waiflow.app/api/v2/messages/send
```

### Collect customer reviews automatically

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Happy Customers",
    "session_id": "uuid",
    "source_type": "all",
    "min_sentiment_score": 0.7,
    "include_keywords": ["thank", "recommend", "love", "amazing"]
  }' \
  https://apiv2.waiflow.app/api/v2/reviews/collectors
```

### Broadcast to a WhatsApp Channel

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"text": "New product just dropped. Tap the link for early access."}' \
  https://apiv2.waiflow.app/api/v2/channels/{channel_id}/broadcast
```

### Schedule a recurring channel post

```bash
curl -X POST -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Monday Newsletter",
    "session_id": "uuid",
    "channel_id": "uuid",
    "target_type": "channel",
    "message_content": "This week: ...",
    "schedule_type": "recurring",
    "cron_expression": "0 9 * * 1"
  }' \
  https://apiv2.waiflow.app/api/v2/scheduled-messages
```

### Discover A2A agents

```bash
curl https://apiv2.waiflow.app/.well-known/agent.json
```

Full API reference: see each module's SKILL.md.

---

## ERC-8004 Agent Registration

MoltFlow is a verified on-chain AI agent registered on **Ethereum mainnet**.

| Field | Value |
|-------|-------|
| Agent ID | [#25477](https://8004agents.ai/ethereum/agent/25477) |
| Chain | Ethereum mainnet (eip155:1) |
| Registry | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Trust Model | Reputation-based |
| Endpoints | A2A + MCP + Web |

**Discovery:**
- Agent card: `https://molt.waiflow.app/.well-known/erc8004-agent.json`
- A2A discovery: `https://apiv2.waiflow.app/.well-known/agent.json`

---

## Use Cases

**Solo Founder / Small Biz**
- Find unanswered leads in your chats
- AI replies in your writing style
- Scheduled promos to custom groups

**Agency / Multi-Client**
- Monitor 50+ groups across 10 sessions
- Bulk send with ban-safe delays
- Export leads as CSV, push to n8n/Zapier

**Marketing Agency / Campaign Manager**
- Capture leads from click-to-WhatsApp ad campaigns
- Auto-qualify inbound leads with keyword detection + AI scoring
- Bulk follow-up sequences with ban-safe throttling
- Multi-session management across client accounts
- Export campaign leads to CRM via webhooks or CSV

**Developer / AI Agent Builder**
- 90+ REST endpoints, scoped API keys
- A2A protocol with E2E encryption
- Python SDK: `pip install moltflow` ([GitHub](https://github.com/moltflow/moltflow-python))

### Guides & Tutorials

**AI Integration Guides:**
- [Connect ChatGPT to MoltFlow](https://molt.waiflow.app/guides/connect-chatgpt-to-moltflow) — Custom GPT Actions, 10 min setup
- [Connect Claude to MoltFlow](https://molt.waiflow.app/guides/connect-claude-to-moltflow) — MCP Server setup, 5 min
- [Connect OpenClaw to MoltFlow](https://molt.waiflow.app/guides/connect-openclaw-to-moltflow) — Native AI config, 5 min setup

**How-To Guides:**
- [Getting Started](https://molt.waiflow.app/blog/whatsapp-automation-getting-started)
- [API Complete Guide](https://molt.waiflow.app/blog/moltflow-api-complete-guide)
- [n8n Integration](https://molt.waiflow.app/blog/moltflow-n8n-whatsapp-automation)
- [n8n + Google Sheets](https://molt.waiflow.app/blog/n8n-whatsapp-google-sheets)
- [n8n Group Auto-Reply](https://molt.waiflow.app/blog/n8n-whatsapp-group-auto-reply)
- [n8n Lead Pipeline](https://molt.waiflow.app/blog/n8n-whatsapp-lead-pipeline)
- [n8n Multi-Model AI](https://molt.waiflow.app/blog/n8n-multi-model-ai-orchestration)
- [AI Auto-Replies Setup](https://molt.waiflow.app/blog/ai-auto-replies-whatsapp-setup)
- [Group Lead Generation](https://molt.waiflow.app/blog/whatsapp-group-lead-generation-guide)
- [Customer Support](https://molt.waiflow.app/blog/openclaw-whatsapp-customer-support)
- [RAG Knowledge Base](https://molt.waiflow.app/blog/rag-knowledge-base-deep-dive)
- [Style Matching](https://molt.waiflow.app/blog/ai-auto-replies-whatsapp-setup#style-profiles)
- [Lead Scoring](https://molt.waiflow.app/blog/whatsapp-lead-scoring-automation)
- [Feedback Collection](https://molt.waiflow.app/blog/whatsapp-customer-feedback-collection)
- [A2A Protocol](https://molt.waiflow.app/blog/a2a-protocol-agent-communication)
- [Scaling ROI](https://molt.waiflow.app/blog/scaling-whatsapp-automation-roi)

[All guides →](https://molt.waiflow.app/guides)

---

## Platform Features

| Feature | Details |
|---|---|
| Messaging | Text, media, polls, vCards |
| Bulk Send | Ban-safe, SSE progress |
| Scheduled | Cron, timezone-aware |
| Reports | 10 templates, cron, WhatsApp delivery |
| Analytics | Campaign funnel, contact scores, send time optimization |
| Groups | Custom lists, CSV export |
| Leads/CRM | Detect signals, pipeline |
| Monitoring | 50+ groups, keywords |
| Labels | Sync to WA Business |
| Channels | Text/image/video broadcasting, scheduled posts, follower sync |
| AI Group Intel | Intent classification, lead scoring (Pro+) |
| AI Replies | GPT-4/Claude, RAG |
| Style Clone | Matches your writing tone |
| RAG | PDF/TXT, semantic search |
| Voice | Whisper transcription |
| Reviews | Sentiment, auto-approve |
| Anti-Spam | Rate limits, typing sim |
| Safeguards | Block PII, injections |
| Webhooks | HMAC signed, 10+ events |
| A2A | E2E encrypted, JSON-RPC |
| GDPR | Auto-expiry, compliance |
| Delivery | Real-time SSE tracking, read/reply/ignored status |

---

## How MoltFlow Compares

| | Molt | Alt 1 | Alt 2 | Alt 3 |
|---|:---:|:---:|:---:|:---:|
| Messaging | 18 | 14 | 3 | 1 |
| Groups | 8 | 4 | 0 | 0 |
| Channels | 7 | 0 | 0 | 0 |
| Outreach | 7 | 0 | 0 | 0 |
| CRM | 7 | 0 | 0 | 0 |
| AI | 7 | 0 | 0 | 0 |
| Reviews | 8 | 0 | 0 | 0 |
| Security | 10 | 0 | 0 | 0 |
| Platform | 8 | 0 | 0 | 0 |
| **Total** | **97+** | **~15** | **~3** | **~1** |

---

## What This Skill Reads, Writes & Never Does

**Documentation and API reference.** Nothing is
auto-installed or auto-executed. No scripts or
executables are bundled in this package.
All actions require user confirmation.

| Category | What happens | Requires opt-in? |
|---|---|---|
| API calls | HTTPS to `apiv2.waiflow.app` only | No (uses your scoped API key) |
| Contact metadata | Contact names, timestamps, counts | No |
| CRM pipeline | Lead status, engagement scores | No |
| AI features | Statistical patterns via API | Yes (AI consent toggle) |
| Local file | `.moltflow.json` — counts only, no PII | No |
| API key | Local env var, never logged or shared | No |

**This skill never:**
- Installs packages or runs code automatically
- Sends messages without explicit user confirmation
- Sends to non-whitelisted numbers (if configured)
- Bypasses anti-spam or content safeguards
- Shares data with third parties
- Stores credentials in files (env vars only)

---

## Setup

> **Free tier available** — 1 session,
> 50 messages/month, no credit card required.

**Env vars:**
- `MOLTFLOW_API_KEY` (required) — create a
  minimum-scoped key from
  [your dashboard](https://molt.waiflow.app).
  Use the narrowest scope preset that covers
  your workflow. Rotate keys regularly.
- `MOLTFLOW_API_URL` (optional) — defaults
  to `https://apiv2.waiflow.app`

**Authentication:**
`X-API-Key: $MOLTFLOW_API_KEY` header
or `Authorization: Bearer $TOKEN` (JWT).

**Base URL:** `https://apiv2.waiflow.app/api/v2`

---

## Security

- **Minimum-scoped API keys enforced** — `scopes` is
  a required field when creating keys. Always create
  the narrowest key possible (e.g., `messages:send`
  only). Use presets like "Messaging" or "Read Only"
  for common workflows. Never use full-scope keys
  with AI agents — create a dedicated, limited key.
- **Use environment variables for keys** — set
  `MOLTFLOW_API_KEY` as an env var, not in
  shared config files. Rotate keys regularly.
- **Phone whitelisting** — configure `allowed_numbers`
  in tenant settings to restrict which numbers can
  send outbound messages. Only whitelisted numbers
  are permitted.
- **Anti-spam safeguards** — all outbound messages
  pass through reciprocity checks (contact must
  message you first), burst rate limiting, typing
  simulation, and random delays. Cannot be bypassed.
- **Content safeguards** — outbound messages are
  scanned for PII, secrets, and prompt injection
  attempts. Blocked automatically before sending.
- **Approval mode** — enable `require_approval` in
  tenant settings to hold all AI-generated messages
  for manual review before delivery.
- **Webhook URL validation** — the API blocks
  private IPs, cloud metadata, and non-HTTPS
  schemes. Only configure endpoints you control.
  Always set a `secret` for HMAC verification
- **Verify third-party packages before running** —
  if you follow the external setup guides to install
  MCP or GPT integrations, review the package source
  and maintainers first. This skill does not install
  or execute any packages.
- **Review scripts locally before running** — the
  Python example scripts are hosted on GitHub, not
  bundled. Download, inspect the source, then run.
- **Avoid high-privilege keys in shared environments** —
  for admin operations (key rotation, data export),
  use the browser dashboard or a short-lived scoped
  key. Never expose owner-level keys in shared shells.
- **Test in a sandbox tenant first** — create a
  short-lived, scoped key for testing. Revoke
  after testing. Never share keys across tenants.

---

## AI Agent Integrations

32 MCP tools for Claude Desktop, Claude.ai,
Claude Code, and OpenAI Custom GPTs. Includes
`moltflow_get_group_messages` for AI-powered
group intelligence and 6 channel tools for
broadcasting, scheduling, and follower management.

**User Action Required** — each integration
requires manual setup by the user. No code
is installed automatically by this skill.

See [integrations.md](integrations.md) for setup
guides and security notes.

---

## Modules

Each module has its own SKILL.md with endpoints
and curl examples.

- **moltflow** (Core) — sessions, messaging,
  groups, labels, webhooks
- **moltflow-outreach** — bulk send,
  scheduled messages, scheduled reports, custom groups,
  channel broadcasting
- **moltflow-ai** — style cloning, RAG,
  voice transcription, AI replies
- **moltflow-leads** — lead detection,
  CRM pipeline, bulk ops, export
- **moltflow-a2a** — agent-to-agent protocol,
  encrypted messaging
- **moltflow-reviews** — review collection,
  sentiment analysis, testimonial export
- **moltflow-admin** — auth, API keys,
  billing, usage tracking
- **moltflow-onboarding** — read-only account
  health check, growth opportunity reports

---

## Notes

- Anti-spam on all messages (typing, random delays)
- Sessions require QR code pairing on first connect
- Use E.164 phone format without `+`
- AI features and A2A require Pro plan or above
- Rate limits: Free 10, Starter 20, Pro 40, Biz 60/min

---

## Changelog

**v2.16.0** (2026-03-02) -- See [CHANGELOG.md](CHANGELOG.md) for full history.

<!-- FILEMAP:BEGIN -->
```text
[moltflow file map]|root: .
|.:{SKILL.md,CHANGELOG.md,integrations.md}
|moltflow:{SKILL.md}
|moltflow-ai:{SKILL.md}
|moltflow-a2a:{SKILL.md}
|moltflow-reviews:{SKILL.md}
|moltflow-outreach:{SKILL.md}
|moltflow-leads:{SKILL.md}
|moltflow-admin:{SKILL.md}
|moltflow-onboarding:{SKILL.md}
```
<!-- FILEMAP:END -->
