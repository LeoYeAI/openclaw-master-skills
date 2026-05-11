---
name: cv-builder
description: >-
  Create a free digital identity, professional resume and CV — from classic
  PDF and HTML layouts to 3D worlds and playable games. Permanent public URL
  with own slug. Free API for AI agents — basic use without API key, full
  features with Access-ID. Use when the user wants to build, create, or
  generate a resume, CV, or set up an online professional profile. ATS-ready.
homepage: https://www.talent.de
license: Free-to-use
compatibility: Requires HTTP client and network access.
env_vars:
  TALENT_ACCESS_ID:
    required: false
    sensitive: true
    description: "Optional for basic CV creation (3/day without ID). Required for callbacks and higher rate limits."
metadata:
  openclaw:
    emoji: "\U0001F4C4"
  talent:
    category: cv-studio
    version: "5.2.2"
    api_base: https://www.talent.de/api
    credentials:
      access_id:
        required: false
        format: "talent_agent_[a-z0-9]{4}"
        obtain: "POST /api/agent/register"
        env_var: "TALENT_ACCESS_ID"
        sensitive: true
        note: "Optional for basic CV creation (3/day without ID). Required for callbacks and higher rate limits."
  hitl:
    supported: true
    spec_version: "0.7"
    types: [confirmation, input, selection, approval, escalation]
    notifications: [polling, sse, callback]
    review_base_url: "https://www.talent.de/en/hitl/review"
    timeout_default: "24h"
    grace_period: "5min"
    discovery: "https://www.talent.de/.well-known/hitl.json"
    info: "May ask requestor to confirm context, enter data, select template, approve CV draft, or handle escalations."
---

# CV Builder — Create CVs via API

Create a resume, digital identity, or CV right now — for free. Choose from templates that span the full range: classic print-ready PDFs, clean HTML online CVs, interactive experiences, animated 3D worlds, and playable games. Every CV gets a permanent public URL with a personal slug — no signup, no payment needed for basic use. ATS-ready and Agent-Ready (HR).

## Feature Overview

| Feature | Access-ID needed | How |
|---------|-----------------|-----|
| Create CV (online, permanent URL) | No | `prefer_hitl: true` or `skip_hitl: true` |
| PDF Export | No | `"include_pdf": true` on any request |
| Human slug (URL) selection | No | HITL step 3 |
| Human template selection | No | HITL step 4 |
| Inline submit (no browser) | No | Bearer token on confirm/approval steps |
| Callback webhook | Yes | `"hitl_callback_url"` |
| Higher rate limits (50/day) | Yes | Register via `POST /api/agent/register` |
| Custom templates | Yes | Template Create skill |

Templates span: classic PDF · HTML online · interactive · 3D (Three.js) · gamified.
Full catalog: [reference/templates.md](reference/templates.md) — live previews: [talent.de/de/cv-template-ideas](https://www.talent.de/de/cv-template-ideas)

## Terminology

Throughout this skill, these terms are used consistently:

| Term | Meaning |
|------|---------|
| **requestor** | The human who commissioned this CV build — the person providing data, making decisions (slug, template, approval), and receiving the claim token. All agent actions are on their behalf. |
| **human** | Synonym for requestor in HITL context, used to contrast with automated/AI steps (e.g., "if the human prefers the browser"). |
| **agent** | You — the AI executing this skill. |

## Agent Guidelines

> **HITL is required.** You MUST include either `"prefer_hitl": true` (human review) or `"skip_hitl": true` (direct creation). Omitting both returns a 400 error. If a human is present, ALWAYS use `"prefer_hitl": true` — this lets the requestor choose their URL slug, pick a template, review the data, and approve before publishing. Use `"skip_hitl": true` only for automated pipelines with no human in the loop.

> **Data principle:** Only use data the requestor has explicitly provided or approved in this conversation. Do not extract personal information from unrelated system contexts or other sessions.

> **Before sending:** Present a brief summary to the requestor — name, title, email — and ask "Send it? Or should I change anything?"

> **Claim token:** Treat like a password. Share only with the requestor — anyone with the token can claim CV ownership. Never share with third parties.

## Credentials

An **Access-ID** (`talent_agent_[a-z0-9]{4}`) is optional for CV Builder — basic use (3 CVs/day per IP) works without one. Register for higher limits (50 CVs/day) and callback webhook support:

```http
POST https://www.talent.de/api/agent/register
Content-Type: application/json

{ "agent_name": "my-agent" }
```

The Access-ID is also the HMAC secret for verifying `X-HITL-Signature` on callback webhooks. Store in `TALENT_ACCESS_ID` — do not hardcode.

## User Communication

### What to say at each step

| Step | Say to the requestor |
|------|-----------------|
| Before API call | "Let me set up your CV. I just need a few details." |
| Slug selection (review_url received) | "Choose your personal URL — this is where your CV will live: [link]" |
| Template selection | "Almost done! Pick a design for your CV: [link]" |
| Approval | "Your CV is ready for review. Take a look and approve it: [link]" |
| After final 201 | "Your CV is live! Here's your link: {url}" |

## Quick Start

1. Ask for (or confirm you already have): firstName, lastName, title, email — the 4 required fields
2. `POST /api/agent/cv-simple` with `"prefer_hitl": true` and the data
   _Optional: add `"include_pdf": true` to also receive a base64 PDF in the final 201 response. See [PDF Export](#pdf-export)._
3. Present the `review_url` to the requestor (they pick slug, template, review data)
4. Poll `poll_url` every 30s until `"status": "completed"`:
   - `{ "status": "pending" }` or `{ "status": "opened" }` → keep polling
   - `{ "status": "completed", "result": { "action": "confirm", "data": {...} } }` → advance with `hitl_continue_case_id`
5. After final approval: present the live CV URL and claim token

## Example (with HITL — recommended)

```http
POST https://www.talent.de/api/agent/cv-simple
Content-Type: application/json

{
  "prefer_hitl": true,
  "cv_data": {
    "firstName": "Alex",
    "lastName": "Johnson",
    "title": "Software Engineer",
    "email": "alex@example.com",
    "experience": [{
      "jobTitle": "Senior Developer",
      "company": "Acme Inc.",
      "startDate": "2022-01",
      "isCurrent": true
    }],
    "hardSkills": [{ "name": "React", "level": 4 }],
    "softSkills": [{ "name": "Team Leadership" }],
    "languages": [{ "name": "English", "level": "NATIVE" }]
  }
}
```

Response (202 — human review required):
```json
{
  "status": "human_input_required",
  "message": "Please confirm: is this CV for you?",
  "hitl": {
    "case_id": "review_a7f3b2c8d9e1f0g4",
    "review_url": "https://www.talent.de/en/hitl/review/review_a7f3b2c8d9e1f0g4?token=abc123...",
    "poll_url": "https://www.talent.de/api/hitl/cases/review_a7f3b2c8d9e1f0g4/status",
    "type": "confirmation",
    "inline_actions": ["confirm", "cancel"],
    "timeout": "24h"
  }
}
```

Present the review URL to the requestor:

> I've prepared your CV. Please review and make your choices here:
> **[Review your CV](review_url)**
> You'll pick your personal URL slug, template design, and approve the final result.

Then poll `poll_url` until completed, and continue through steps with `hitl_continue_case_id`. After all steps (confirmation, data review, slug selection, template selection, approval), the final POST returns 201 with the live URL.

Full HITL protocol with all steps, inline submit, edit cycles, and escalation: [reference/hitl.md](reference/hitl.md)

## HITL Multi-Step Flow

The requestor goes through up to 5 review steps. The agent loops: present review URL, poll, continue.

```
Step 1: Confirmation  →  "For whom is this CV?"
Step 2: Data Review   →  "Are these details correct?"
Step 3: Slug          →  Human picks personal URL slug (e.g. pro, dev, 007)
Step 4: Template      →  Human picks template design
Step 5: Approval      →  Human reviews final CV draft
```

Each step returns 202. After the requestor decides, continue:

```http
POST https://www.talent.de/api/agent/cv-simple
Content-Type: application/json

{
  "prefer_hitl": true,
  "hitl_continue_case_id": "review_a7f3b2c8d9e1f0g4",
  "slug": "dev",
  "cv_data": { ... }
}
```

> **Important:** `slug` and `template_id` go at the **top level** of the request, not inside `cv_data`. When continuing after slug selection, include the human's chosen slug at the top level so the server knows to advance to the template step.

Steps are skipped when you already provide the value:
- Include `slug` (top-level) → slug selection step is skipped
- Include `template_id` (top-level) → template selection step is skipped
- Include both → only confirmation, data review, and approval remain

### Inline Submit (v0.7)

For simple decisions (**confirmation**, **escalation**, **approval**), the 202 response includes `submit_url`, `submit_token`, and `inline_actions`. Agents can submit directly via Bearer token — ideal for Telegram, Slack, WhatsApp where buttons are supported:

```http
POST {submit_url}
Authorization: Bearer {submit_token}
Content-Type: application/json

{ "action": "confirm", "data": {} }
```

> **Always present `review_url` as a fallback alongside any inline buttons.** If the platform does not support buttons (SMS, email, plain text), or the human prefers the browser, they can use the link to complete their decision.

**Selection** and **input** types always require the browser (`review_url`) — they involve complex UI (template grid, data forms). Full inline spec: [reference/hitl.md](reference/hitl.md)

After the final approval step, submit with `hitl_approved_case_id` to publish:

```http
POST https://www.talent.de/api/agent/cv-simple
Content-Type: application/json

{
  "hitl_approved_case_id": "review_final_case_id"
}
```

Response (201):
```json
{
  "success": true,
  "url": "https://www.talent.de/dev/alex-johnson",
  "cv_id": "cv_abc123",
  "claim_token": "claim_xyz789",
  "template_id": "007",
  "quality_score": 65,
  "quality_label": "good",
  "improvement_suggestions": []
}
```

> ⚠️ **Immediately after receiving a 201 — always share both with the requestor:**
> 1. **CV URL**: `https://www.talent.de/dev/alex-johnson` — their live profile
> 2. **Claim link**: `https://www.talent.de/claim/claim_xyz789` — to take ownership and edit
>
> The `claim_token` is permanent and never expires. Treat it like a password — share only with the requestor.

Present the result:

> Your CV is live: **talent.de/dev/alex-johnson**
>
> To claim ownership and edit your CV, visit: **talent.de/claim/claim_xyz789**
> Keep this link safe — it never expires and gives full edit access.

If the response includes `improvement_suggestions`, share them with the requestor and offer to update the CV:

> Your CV score is 35/100. To improve it, I can add: work experience (+25pts), professional summary (+20pts). Want me to ask you a few questions and update it?

## Agent Loop (Visual)

Both paths — with and without human review — are shown below. Choose ONE per request.

```mermaid
flowchart TD
    START([Agent starts]) --> CHOICE{prefer_hitl\nor skip_hitl?}

    %% ── skip_hitl path ──────────────────────────────────────────
    CHOICE -->|skip_hitl: true| DIRECT["POST /api/agent/cv-simple\nskip_hitl: true + cv_data"]
    DIRECT --> D201["201 — CV live\nurl · claim_token · quality_score\nimprovement_suggestions"]
    D201 --> SHARE_NOW["Share url + claim_token\nwith requestor immediately!"]
    SHARE_NOW --> QUAL{improvement_suggestions\npresent AND attempt < 2?}
    QUAL -->|No / attempt >= 2| DONE_DIRECT([Done])
    QUAL -->|Yes| ASK["Ask requestor the questions\nin each agent_action field"]
    ASK --> REPOST["POST /api/agent/cv-simple\nskip_hitl: true\nenriched cv_data\n(new cv_id each time)"]
    REPOST --> D201

    %% ── prefer_hitl path ─────────────────────────────────────────
    CHOICE -->|prefer_hitl: true| HITL["POST /api/agent/cv-simple\nprefer_hitl: true + cv_data"]
    HITL --> H202["202 human_input_required\nreview_url · poll_url · events_url"]
    H202 --> SHOW_URL["Present review_url to requestor\n'Please review here: [link]'"]
    SHOW_URL --> POLL["Poll poll_url every 30s\n(or use events_url for SSE)"]
    POLL --> STATUS{status?}
    STATUS -->|pending / opened\n/ in_progress| POLL
    STATUS -->|completed| ACTION{result.action?}
    STATUS -->|expired| EXP{default_action?}
    STATUS -->|cancelled| CANCELLED([Inform requestor: cancelled])

    EXP -->|skip| AUTO_PUB["CV auto-published\nurl from poll status"]
    EXP -->|abort| ABORTED([Inform requestor: expired])

    ACTION -->|confirm / select| CONTINUE["POST cv-simple\nhitl_continue_case_id\n+ ALWAYS include cv_data"]
    ACTION -->|edit| EDIT["Adjust cv_data per note\nthen CONTINUE"]
    EDIT --> CONTINUE
    ACTION -->|reject| REJECT["Escalation step\nPOST hitl_continue_case_id"]
    REJECT --> H202
    ACTION -->|approve| PUBLISH["POST cv-simple\nhitl_approved_case_id + cv_data"]
    CONTINUE --> H202
    PUBLISH --> DONE_HITL(["201 — CV live\nShare url + claim_token"])
```

When a HITL case expires, the server applies the `default_action` configured for that step:
- **`skip`**: CV is auto-published with server-selected slug/template. Poll `poll_url` — it returns `status: "completed"` with `url` in the result.
- **`abort`**: Flow terminates. Inform the requestor the session expired. Start a new HITL flow with `prefer_hitl: true` if needed.

## Quality Improvement Loop (skip_hitl)

After any 201 response the CV is **immediately live**. Always share `url` and `claim_token` with the requestor first.

If `improvement_suggestions` is non-empty, you may optionally run up to **2 improvement cycles**:

1. For each suggestion: ask the requestor the exact question in `agent_action`
2. Re-POST with enriched `cv_data` + `skip_hitl: true`
3. Each re-POST creates a **new CV** with a **new `cv_id`** — the previous one is abandoned
4. After **2 cycles** OR when `improvement_suggestions` is empty: **stop**

> **Do not loop indefinitely.** An agent that keeps re-posting creates duplicate CVs and wastes the requestor's time.

For `prefer_hitl` flows: after approval, the 201 is already quality-assessed (human reviewed the data). If suggestions appear, ask the requestor directly — do not restart the HITL flow.

## Direct Creation (No Human Present)

For fully automated pipelines, batch operations, or when the requestor explicitly says "just create it" — set `"skip_hitl": true`:

```http
POST https://www.talent.de/api/agent/cv-simple
Content-Type: application/json

{
  "skip_hitl": true,
  "cv_data": {
    "firstName": "Alex",
    "lastName": "Johnson",
    "title": "Software Engineer",
    "email": "alex@example.com"
  }
}
```

Response (201):
```json
{
  "success": true,
  "url": "https://www.talent.de/pro/alex-johnson",
  "cv_id": "cv_abc123",
  "claim_token": "claim_xyz789",
  "template_id": "018",
  "hitl_skipped": true,
  "quality_score": 20,
  "quality_label": "basic",
  "improvement_suggestions": [
    {
      "field": "experience",
      "issue": "No work experience — CV has low ATS compatibility",
      "agent_action": "Ask: 'What positions have you held? Part-time and internships count.'",
      "impact": "+25 quality points",
      "priority": "high"
    }
  ],
  "next_steps": "Share improvement_suggestions with the requestor and ask the questions in agent_action. Then update the CV via POST /api/agent/cv-simple...",
  "auto_fixes": []
}
```

In direct mode, the server auto-assigns slug (`pro` by default) and template (`018` Amber Horizon). The requestor has no choice. Use this only when no human needs to review.

**You MUST choose one:** `"prefer_hitl": true` or `"skip_hitl": true`. Omitting both returns a 400 error.

All fields beyond the 4 required ones are optional. Omit what you don't have — don't send empty arrays.

## PDF Export

Get a downloadable PDF alongside the CV. Three visual themes available:

| Theme | Style | Best for |
|-------|-------|----------|
| `classic` | Single-column, red accent (default) | Traditional industries |
| `modern` | Two-column sidebar, blue accent | Tech & creative roles |
| `minimal` | Monochrome, generous whitespace | Executive & senior roles |

### Option A: Inline with CV creation

Add `"include_pdf": true` to your request. The response includes a base64-encoded PDF:

```http
POST https://www.talent.de/api/agent/cv-simple
Content-Type: application/json

{
  "prefer_hitl": true,
  "include_pdf": true,
  "pdf_format": "A4",
  "pdf_theme": "modern",
  "cv_data": {
    "firstName": "Alex",
    "lastName": "Johnson",
    "title": "Software Engineer",
    "email": "alex@example.com"
  }
}
```

Response includes a `pdf` object:
```json
{
  "success": true,
  "url": "https://www.talent.de/pro/alex-johnson",
  "cv_id": "cv_abc123",
  "claim_token": "claim_xyz789",
  "pdf": {
    "base64": "JVBERi0xLjQK...",
    "size_bytes": 6559,
    "generation_ms": 226,
    "format": "A4"
  }
}
```

### Option B: Generate PDF for existing CV

```http
POST https://www.talent.de/api/agent/cv/pdf
Content-Type: application/json

{
  "cv_id": "cv_abc123",
  "format": "A4",
  "theme": "minimal"
}
```

Returns the PDF binary directly (`Content-Type: application/pdf`). Format options: `A4` (default), `LETTER`. Theme options: `classic` (default), `modern`, `minimal`.

PDF generation takes ~200ms (no headless browser needed).

## Server-Side Intelligence

You do **not** need to check slug availability or validate data — the server handles it:

- **Slug uniqueness**: A slug is NOT globally unique — it's unique per person. `pro/thomas-mueller` and `pro/anna-schmidt` can coexist. Only the combination of slug + firstName + lastName is reserved. That's why the server needs the name first to check availability.
- **Slug auto-selection**: If omitted (and no HITL), the server picks `pro`. If that slug is already in use for this person's name, it tries the next available slug automatically. In HITL mode, the human can choose their slug interactively. Popular picks (excerpt): `007` · `911` · `dev` · `api` · `pro` · `gpt` · `web` · `ceo` · `cto` · `ops` · `f40` · `gtr` · `amg` · `gt3` · `zen` · `art` · `lol` · `neo` · `404` · `777`. Full list: `GET /api/public/slugs`
- **Template default**: `018` (Amber Horizon) if omitted.
- **Date normalization**: `2024` becomes `2024-01-01`, `2024-03` becomes `2024-03-01`.
- **Language levels**: Normalized to CEFR (`NATIVE`, `C2`, `C1`, `B2`, `B1`, `A2`, `A1`).
- **Human-readable errors**: If something goes wrong, the response explains what to fix in plain English.
- **Auto-fix summary**: The `auto_fixes` array tells you what the server adjusted (e.g. "Slug 'pro' is already in use for this name, using 'dev' instead").

## Skills Use 4 Arrays

- `hardSkills` — technical skills, optional `level` 1-5
- `softSkills` — name only
- `toolSkills` — name only
- `languages` — with CEFR `level`: `NATIVE`, `C2`, `C1`, `B2`, `B1`, `A2`, `A1`

Do **not** use a generic `skills` array — it will be ignored.

## Common Mistakes

| Wrong | Correct | Why |
|-------|---------|-----|
| `"role": "Engineer"` | `"jobTitle": "Engineer"` | Experience uses `jobTitle`, not `role` or `position` |
| `"start": "2022"` / `"end": "2023"` | `"startDate": "2022-01"` / `"endDate": "2023-06"` | Wrong field names — `start`/`end` are silently ignored in experience and education |
| `"skills": [...]` | `"hardSkills": [...]` etc. | Generic `skills` array is ignored — use 4 separate arrays |
| `"slug": "dev"` inside `cv_data` | `"slug": "dev"` at top level | `slug` and `template_id` are request-level fields, not inside `cv_data` |
| `"startDate": "January 2024"` | `"startDate": "2024-01"` | Dates must be `YYYY` or `YYYY-MM` format |
| Sending empty arrays `"hobbies": []` | Omit the field entirely | Don't send empty arrays — omit what you don't have |
| POST /respond without Authorization header | Wait for `status=completed` via `poll_url` | Inline submit requires `submit_token` from the 202 response hitl object |
| POST /respond on an `approval` type step | Poll until `completed`, then `hitl_approved_case_id` | Approval steps require browser review — inline submit not permitted |
| `hitl_continue_case_id` without `cv_data` | Always include the full `cv_data` object | The server needs `cv_data` on every POST to build the next review step UI |
| `skip_hitl: true` when a HITL chain is ongoing | Continue the chain with `hitl_continue_case_id` | Creates a separate CV and bypasses the human's review — share one chain per CV |

## Guardrails

- Rate limits (with Access-ID): 50 CVs/day
- Rate limits (without Access-ID): 3 CVs/day per IP
- Never auto-commit without requestor approval
- Claim tokens are permanent — treat as passwords

## References

- [CV Data Reference](reference/cv-data.md): All fields and constraints for `cv_data`
- [Templates](reference/templates.md): Full template catalog with previews
- [HITL Protocol](reference/hitl.md): Human-in-the-loop review flow (all steps, inline submit, edit cycles)
- [Access System](../shared/access.md): Rate limits and Access-ID registration
- [Error Codes](../shared/errors.md): Error reference and troubleshooting
- [Privacy](../shared/privacy.md): Data handling and GDPR compliance

## Specs

- [agent.json](https://www.talent.de/.well-known/agent.json)
- [hitl.json](https://www.talent.de/.well-known/hitl.json)
- [llms.txt](https://www.talent.de/llms.txt)
- [ClawHub](https://www.clawhub.ai/rotorstar/id-cv-resume-creator)
