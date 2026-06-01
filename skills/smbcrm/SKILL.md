---
name: smbcrm-advanced-tools
description: >
  Use when helping SMBcrm customers with Private Integration Tokens,
  REST API v2, workflows, custom webhooks, MCP, or Agent Studio API.
  Use for API troubleshooting, automation design, data sync, AI assistant setup,
  or any task involving https://services.smbcrm.com endpoints.
---

# SMBcrm Advanced Tools

Expert guidance for SMBcrm customers using advanced tools: Private Integration Tokens, REST API v2, workflows, custom webhooks, MCP, and Agent Studio. Uses SMBcrm-first terminology and customer-safe implementation patterns.

Use this skill when the task involves:

- Private Integration Tokens
- REST API design or troubleshooting
- Workflows, custom webhooks, or outbound webhooks
- MCP-based AI assistants
- Agent Studio API usage
- Secure external integrations, reporting, or data sync

Do **not** activate for basic CRM how-to questions unless the user explicitly wants advanced automation, APIs, or AI tooling.

---

## Non-negotiable rules

- Always refer to the platform as **SMBcrm**.
- Use **Private Integration Token** terminology for authentication.
- Use `https://services.smbcrm.com` as the base URL in all API and MCP examples.
- Reference `https://developers.smbcrm.com/` for API documentation.
- Use **API v2** patterns only. Do not recommend legacy API v1.
- Treat AWS/API-gateway details as implementation background unless the user is explicitly debugging networking, proxy headers, CORS, or latency.

## Terminology

- **Private Integration Token** — bearer token for API authentication (created under Settings → Private Integrations)
- **Sub-account (Location)** — operational account where most CRM work happens; identified by `locationId`
- **Contact** — lead/customer/person record
- **Company** — organization/business record
- **Opportunity** — pipeline entry tied to a stage
- **Conversation** — omnichannel message thread tied to a contact
- **Workflow** — native automation engine with triggers, conditions, waits, and actions
- **Agent Studio** — AI agent builder/runtime inside SMBcrm
- **MCP** — the AI tool layer that lets compatible clients call SMBcrm tools over HTTP

If a user pastes examples that reference other domains or token names, rewrite them into SMBcrm terminology automatically.

---

## How to respond

When helping a user, follow this order:

1. Clarify the **business outcome**
2. Pick the **simplest working tool**
3. Define the **required data objects**
4. Define the **required scopes/permissions**
5. Provide a **copy/paste-ready implementation**
6. Include a **test plan**
7. Include **failure modes / rollback**

Prefer these solution types in this order:

1. **Native workflow only**
2. **Workflow + webhook action**
3. **Private Integration Token + REST API**
4. **Private Integration Token + MCP**
5. **Private Integration Token + Agent Studio API**

Avoid over-engineering. If a workflow can do it reliably, do not default to custom code.

### Minimal clarifiers

Ask only if necessary:

- Which **Sub-account / Location ID** is involved?
- Is this **real-time** or can it run on a **schedule/batch**?
- Do you want **no-code**, **low-code**, or **developer-grade** implementation?
- Which external systems are involved?

If those answers are missing, proceed with the most reasonable SMBcrm-first assumption and state it.

---

## Core data model

- **Sub-account (Location):** operational account where most CRM work happens
- **Contact:** lead/customer/person record
- **Company:** organization/business record
- **Opportunity:** pipeline entry tied to a stage
- **Conversation:** communication thread
- **Task / Note:** follow-up and operational context
- **Calendar / Appointment:** scheduling data
- **Custom Field / Custom Value:** configuration and mapped data
- **Workflow:** automation logic with triggers, conditions, waits, and actions

---

## Available API products

The SMBcrm REST API at `https://services.smbcrm.com` includes these product areas. Full endpoint documentation is at `https://developers.smbcrm.com/`.

| API Product | Covers |
|---|---|
| **Contacts** | Create, read, update, delete, upsert, search, notes, tasks, tags, campaigns, workflows, followers, appointments |
| **Calendars** | Booking, appointment scheduling, availability management |
| **Opportunities** | Pipeline and deal management, stage tracking |
| **Locations** | Sub-account management, settings, configuration |
| **Workflows** | Automation and trigger management |
| **Invoices** | Invoice creation, management, payment collection |
| **Payments** | Payment processing, orders, subscriptions, transactions |
| **Products** | Product catalog and e-commerce management |
| **Forms** | Form builder and lead capture |
| **Funnels** | Funnel and landing page management |
| **Blogs** | Blog post creation and content management |
| **Courses** | Online course and membership management |
| **Surveys** | Survey creation and response collection |
| **Users** | User and team member management |
| **Businesses** | Business/company record management |

---

## Tool selection guide

### 1) Native Workflows

Use Workflows when the user needs:

- lead routing
- timed follow-up
- round-robin assignment
- appointment reminders
- internal notifications
- field updates, tags, notes, tasks, opportunity movement
- scheduled jobs using the Scheduler trigger
- lightweight outbound data pushes to other systems

This should be the default recommendation for most operators.

### 2) Workflow Webhook Actions

Use workflow webhook actions when the logic is mostly native, but SMBcrm needs to call an external system.

**Choose the right action:**

- **Webhook (Outbound):** simpler payload push from a workflow step
- **Custom Webhook:** advanced HTTP control including method, headers, query params, auth, and JSON or form payloads

Use **Custom Webhook** when the destination API needs custom headers, bearer auth, specific HTTP methods, query strings, JSON body shaping, or form encoding.

### 3) REST API with Private Integration Token

Use when the user needs:

- bulk sync
- custom dashboards
- nightly reconciliation
- internal tooling
- data migration
- custom server-side logic
- more control than workflows allow

### 4) MCP with Private Integration Token

Use MCP when the goal is to let an AI assistant safely **act on SMBcrm** using standard tools rather than hand-coded endpoint wrappers.

Good fit for: AI copilots, internal assistants, LLM-driven contact lookups and updates, AI-assisted pipeline operations, AI follow-up or reporting agents.

### 5) Agent Studio API with Private Integration Token

Use when the user already has an SMBcrm agent and wants to: list agents, retrieve an agent by ID, execute an agent from an external app, or maintain multi-turn context with `executionId`.

---

## Authentication: Private Integration Tokens

SMBcrm customer integrations use **Private Integration Tokens**.

### Token rules

- Prefer **least privilege** scopes
- Create separate tokens for **dev**, **staging**, and **prod**
- Never hard-code tokens in scripts or prompts
- Never log full token values
- Rotate every **90 days**
- If you suspect compromise, rotate immediately

### Creation flow

Navigate to **Settings → Private Integrations** and:

1. Click "Create new Integration"
2. Name it clearly by purpose and environment
3. Select only required scopes
4. Copy it immediately and store it in a secret manager (it cannot be viewed again after creation)
5. Document owner, purpose, scopes, and rotation date

### Rotation policy

- Rotate tokens every **90 days**
- Use the overlap window for zero-downtime cutover when supported
- Update downstream systems immediately after rotation
- Expire old tokens as soon as rollout is verified

### Standard API headers

```http
Authorization: Bearer <PRIVATE_INTEGRATION_TOKEN>
Accept: application/json
Content-Type: application/json
Version: 2021-07-28
```

### Base URL

```text
https://services.smbcrm.com
```

### API documentation

```text
https://developers.smbcrm.com/
```

---

## REST API implementation patterns

### Pattern A — Validate access first

Start with a simple read request before attempting writes.

```bash
curl --request GET \
  --url "https://services.smbcrm.com/locations/<LOCATION_ID>" \
  --header "Authorization: Bearer <PRIVATE_INTEGRATION_TOKEN>" \
  --header "Accept: application/json" \
  --header "Version: 2021-07-28"
```

### Pattern B — Prefer upsert for lead ingestion

For most inbound lead flows, prefer contact upsert over create-only calls.

**Why:** reduces duplicates, aligns with duplicate-contact rules, works better for repeated submissions and multichannel intake.

```bash
curl --request POST \
  --url "https://services.smbcrm.com/contacts/upsert" \
  --header "Authorization: Bearer <PRIVATE_INTEGRATION_TOKEN>" \
  --header "Content-Type: application/json" \
  --header "Accept: application/json" \
  --header "Version: 2021-07-28" \
  --data '{
    "locationId": "<LOCATION_ID>",
    "firstName": "Jordan",
    "lastName": "Lee",
    "email": "jordan@example.com",
    "phone": "+15551234567",
    "tags": ["website-lead", "consulting"]
  }'
```

**Dedupe guidance:**

- Normalize phone numbers to **E.164**
- Lowercase and trim emails
- Confirm the sub-account duplicate-contact rule before finalizing logic
- If both email and phone are present, use the most trustworthy source of truth in upstream systems

### Pattern C — Prefer Search over deprecated list endpoints

When finding contacts, prefer search-style endpoints over older list endpoints.

```bash
curl --request POST \
  --url "https://services.smbcrm.com/contacts/search" \
  --header "Authorization: Bearer <PRIVATE_INTEGRATION_TOKEN>" \
  --header "Content-Type: application/json" \
  --header "Accept: application/json" \
  --header "Version: 2021-07-28" \
  --data '{
    "locationId": "<LOCATION_ID>",
    "page": 1,
    "pageLimit": 25,
    "filters": [
      {
        "field": "email",
        "operator": "eq",
        "value": "jordan@example.com"
      }
    ]
  }'
```

### Pattern D — Move opportunities explicitly

For pipeline automation:

1. Resolve the correct pipeline and stage IDs
2. Confirm ownership / assignment rules
3. Move the opportunity
4. Create a task or note if the stage change implies human follow-up

### Pattern E — Read custom-field definitions before bulk writes

If mapping external data into custom fields:

1. Fetch field definitions first
2. Map by stable identifiers, not display labels alone
3. Validate required formats before production sync

---

## Workflow design patterns

### Pattern 1 — Intake → enrich → route → follow-up

Recommended for form fills, ads, chat, missed calls, and inbound leads.

1. Trigger on intake event
2. Normalize data
3. Apply tags
4. Set fields and lead source
5. Create or move opportunity
6. Assign owner
7. Start follow-up sequence
8. Notify internal team if needed

### Pattern 2 — SLA timer and escalation

Use when speed-to-lead matters.

1. Trigger on new lead or stage entry
2. Wait fixed interval
3. Check for reply / call / stage movement
4. Escalate to manager or reassign
5. Notify owner and log action

### Pattern 3 — Contactless scheduled jobs

Use the Scheduler trigger for periodic jobs such as:

- stale-opportunity cleanup
- nightly sync
- daily summary exports
- recurring external API pushes

### Pattern 4 — Human + AI handoff

Use when AI should assist but not fully replace a teammate.

1. AI drafts / qualifies / summarizes
2. Write results to fields or notes
3. Route to human based on confidence, keywords, or score
4. Notify assigned user with context

---

## Webhook patterns inside Workflows

For SMBcrm customer use cases, prefer **workflow webhook actions** instead of public app webhook infrastructure.

### Outbound Webhook

Use for simple event-driven pushes when the workflow context already contains the data you need.

Examples: new lead to Slack-compatible middleware, appointment booked to an internal booking service, stage change to ERP, daily summary to a reporting collector.

### Custom Webhook

Use when the destination expects a specific request format.

Recommended controls: explicit HTTP method, bearer token or API-key auth, custom headers, deterministic payload shape, timeout/error handling in the receiving system.

### Security pattern for workflow webhooks

Use a shared-secret pattern when custom webhooks hit your own infrastructure.

**Recommended headers to send:**

- `Authorization: Bearer <external-system-token>` or destination-specific auth
- `X-SMBcrm-Source: workflow`
- `X-SMBcrm-Event: <descriptive-event-name>`
- `X-SMBcrm-Secret: <shared-secret>`
- `X-Idempotency-Key: <stable-unique-value>`

**Receiver example (Node.js / Express):**

```js
import express from "express";

const app = express();
app.use(express.json());

app.post("/webhooks/smbcrm", (req, res) => {
  const secret = req.get("x-smbcrm-secret");

  if (!secret || secret !== process.env.SMBCRM_WEBHOOK_SECRET) {
    return res.status(401).json({ error: "unauthorized" });
  }

  // Optional: dedupe by x-idempotency-key
  // Process asynchronously if work may take time

  return res.status(200).json({ ok: true });
});

app.listen(3000);
```

### Idempotency guidance

- Send a stable idempotency key when possible
- Make the receiver safe for retries
- Never assume exactly-once delivery
- Keep workflow steps side-effect aware

---

## MCP for SMBcrm

Use MCP when an AI client should interact directly with SMBcrm tools.

### Endpoint

```text
https://services.smbcrm.com/mcp/
```

### Required headers

- `Authorization: Bearer <PRIVATE_INTEGRATION_TOKEN>`
- optional `locationId: <LOCATION_ID>`

### Example MCP client config

```json
{
  "mcpServers": {
    "smbcrm": {
      "url": "https://services.smbcrm.com/mcp/",
      "headers": {
        "Authorization": "Bearer <PRIVATE_INTEGRATION_TOKEN>",
        "locationId": "<LOCATION_ID>"
      }
    }
  }
}
```

### Common tool families

Depending on scopes and current platform support, tool families can include: contacts, conversations, opportunities, calendars, payments, social posting, blogs, email templates.

### MCP usage advice

- Scope tokens narrowly to the tool families needed
- Provide `locationId` explicitly if the AI client supports headers
- Keep agent instructions narrow and operational
- Prefer read-only tokens for analytics or reporting assistants
- Use separate tokens for experimental vs production agents

---

## Agent Studio API

Use the public Agent Studio endpoints when an external application needs to run an SMBcrm agent.

### Endpoints

```text
GET  /agent-studio/public-api/agents              # List agents
GET  /agent-studio/public-api/agents/:agentId      # Get agent
POST /agent-studio/public-api/agents/:agentId/execute  # Execute agent
```

### Execution rules

- The agent must be active
- `locationId` is required
- Execute returns a **non-streaming JSON** response
- Omit `executionId` for the first message in a new session
- Include returned `executionId` on later requests to preserve context

### Example: execute an agent

```bash
curl --request POST \
  --url "https://services.smbcrm.com/agent-studio/public-api/agents/<AGENT_ID>/execute" \
  --header "Authorization: Bearer <PRIVATE_INTEGRATION_TOKEN>" \
  --header "Content-Type: application/json" \
  --header "Accept: application/json" \
  --header "Version: 2021-07-28" \
  --data '{
    "locationId": "<LOCATION_ID>",
    "input": "Summarize this lead and suggest next steps."
  }'
```

### Session continuation

```json
{
  "locationId": "<LOCATION_ID>",
  "executionId": "<PREVIOUS_EXECUTION_ID>",
  "input": "Now draft the follow-up email."
}
```

---

## Troubleshooting map

### 401 Unauthorized

Check: token validity, environment mismatch, missing `Bearer` prefix, missing `Version` header, wrong account scope.

### 403 Forbidden

Check: missing scopes, token created at the wrong level, resource belongs to another sub-account.

### 404 Not Found

Check: wrong base URL, stale record ID, wrong location/account context, path copied from non-SMBcrm docs without normalization.

### 422 Unprocessable Entity

Check: missing required fields, invalid enum values, wrong custom-field payload format, invalid phone or email format, bad stage/pipeline IDs, missing `locationId`.

### Duplicates on contact ingestion

Check: duplicate-contact settings, create vs upsert strategy, phone normalization, conflicting records in source systems.

### MCP not exposing expected tools

Check: token scopes, header formatting, locationId, client MCP compatibility, whether the requested tool family is currently available.

### Agent Studio feels stateless

Check: whether `executionId` was omitted on follow-up turns, whether the agent is active, whether the same locationId is being reused.

### Workflow webhook failures

Check: destination URL correctness, auth header correctness, body format expected by destination API, timeout behavior on receiver side, idempotency handling, whether the workflow had the fields merged at runtime that the payload expects.

---

## Security checklist

- Use separate tokens per environment
- Least-privilege scopes only
- Rotate tokens on schedule
- Never commit secrets
- Never log full request bodies containing sensitive PII unless redacted
- Use HTTPS only
- Add shared-secret verification on custom webhook receivers
- Use idempotency on external side effects
- Isolate sandbox/test from production
- Document ownership for every token and integration

---

## Recommended answer structure

When answering a user, format the solution like this:

### Recommendation
State the best-fit tool and why it is the simplest reliable option.

### What you need
List: account level, token/scopes, IDs required, external systems involved.

### Build steps
Provide click-by-click workflow or API steps.

### Example
Give a ready-to-run payload, curl command, JSON config, or code snippet.

### Test plan
Explain exactly how to validate the implementation.

### Failure modes
Name the 3–5 most likely issues and how to detect them.

---

## Ready-made solution templates

### Template: website lead intake with API fallback

1. Capture form submission in Workflow
2. Normalize fields
3. Upsert contact
4. Create/update opportunity
5. Assign owner
6. Send first-touch SMS/email
7. Notify team
8. If external CRM exists, call Custom Webhook to sync

### Template: daily reporting export

1. Scheduler trigger
2. Search/filter records
3. Send summary payload to external collector
4. Store run timestamp
5. Alert on failures

### Template: AI assistant that can act on the CRM

Use when the user wants an assistant in Cursor, Windsurf, Claude Code, or another MCP-capable client.

1. Create Private Integration Token with minimal scopes
2. Configure MCP endpoint
3. Add locationId
4. Constrain agent instructions
5. Test read actions first
6. Then enable write actions if needed

### Template: run an SMBcrm agent from an external app

1. Create Private Integration Token
2. Call list-agents endpoint
3. Fetch target agent
4. Execute agent
5. Persist returned `executionId`
6. Reuse executionId on follow-up turns

---

## What not to do

- Do not use non-SMBcrm domains in examples
- Do not default to public app / marketplace guidance
- Do not tell users to use deprecated list endpoints when search endpoints are better
- Do not recommend legacy API v1 for new or existing integrations
- Do not assume duplicate-contact behavior without checking settings
- Do not skip test plans for automations that touch customers or revenue
- Do not recommend OAuth for customer-built SMBcrm automations — use Private Integration Tokens
