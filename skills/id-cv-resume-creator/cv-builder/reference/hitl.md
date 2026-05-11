# HITL Protocol — Human-in-the-Loop Review

HITL Protocol v0.6 — https://github.com/rotorstar/hitl-protocol

When creating CVs, add `"prefer_hitl": true` to request human decision points. This pauses the workflow and returns a review URL for the human. The flow supports up to 5 review types in a chained sequence.

## Review Types

| Type | Actions | Purpose |
|------|---------|---------|
| `confirmation` | confirm / cancel | "For whom is this CV?" or "Is this data correct?" |
| `input` | submit | Human enters or corrects CV data via form |
| `selection` | select | Human picks a slug or template (sub-type in `surface_data.selection_type`) |
| `approval` | approve / edit / reject | Human reviews final CV draft |
| `escalation` | retry / skip / abort | Recovery after rejection |

## Multi-Step Flow

The full flow chains multiple review steps. Each step returns HTTP 202 with a `case_id`. Use `hitl_continue_case_id` to advance to the next step.

```
Step 1: Confirmation  →  "For whom is this CV?"
Step 2: Data Review   →  "Are these details correct?" (or Input form)
Step 3: Slug          →  Human picks personal URL slug
Step 4: Selection     →  Human picks template
Step 5: Approval      →  Human reviews CV draft
Step 6: Escalation    →  (only after rejection)
```

**Agent loop (poll-and-continue):**

```
1. POST /api/agent/cv-simple { prefer_hitl: true, cv_data: {...} }
   → 202 { hitl: { case_id: "C1", type: "confirmation" } }

2. Present review_url to the human

3. Poll GET {poll_url} → wait for "completed"
   → result: { action: "confirm", data: { selected_option: "for_self" } }

4. POST /api/agent/cv-simple { prefer_hitl: true, hitl_continue_case_id: "C1", cv_data: {...} }
   → 202 { hitl: { case_id: "C2", type: "selection", surface_data: { selection_type: "slug" } } }

5. Poll → result: { action: "select", data: { selected_slug: "dev" } }

6. POST /api/agent/cv-simple { prefer_hitl: true, hitl_continue_case_id: "C2", slug: "dev", cv_data: {...} }
   → 202 { hitl: { case_id: "C3", type: "selection" } }  // template selection

7. Repeat poll-and-continue until final approval

8. POST /api/agent/cv-simple { hitl_approved_case_id: "C_last" }
   → 201 { url, claim_token }
```

## Shortcuts (skip steps)

| What you provide | Steps executed |
|-----------------|---------------|
| Only `prefer_hitl` | confirmation → data → slug → selection → approval |
| + `slug` | confirmation → data → selection → approval (slug step skipped) |
| + `template_id` | confirmation → data → slug → approval (template step skipped) |
| + `slug` + `template_id` | confirmation → data → approval (both skipped) |
| + `hitl_step: 'slug'` | Jump directly to slug selection |
| + `hitl_continue_case_id` (from prior step) | Continues from that step |
| `skip_hitl: true` | Direct creation (201), no HITL |
| Neither flag | 400 error — explicit choice required |

## Edit Cycle

If the human chooses `action: "edit"` with feedback:

1. Parse the `note` field from the result for the human's feedback
2. Apply changes to `cv_data`
3. Re-submit with `hitl_continue_case_id` pointing to the edit case
4. Server creates a new approval case (the human reviews again)

## Rejection + Escalation

If the human rejects (up to 3 times):

1. Result: `{ action: "reject", note: "Wrong data" }`
2. Continue with `hitl_continue_case_id` → server creates an escalation case
3. Escalation offers: **retry** (with feedback), **skip** (publish as-is), **abort** (cancel)
4. After 3 rejections, retry is disabled (only skip/abort)

## Human Data Override

When the human submits data via an `input` step, include their changes in the next request:

```json
{
  "prefer_hitl": true,
  "hitl_continue_case_id": "C_input",
  "hitl_cv_data_override": {
    "firstName": "Alexandra",
    "title": "Senior Engineer"
  },
  "cv_data": { ... }
}
```

`hitl_cv_data_override` fields take priority over `cv_data`.

## Example with HITL

```http
POST https://www.talent.de/api/agent/cv-simple
Content-Type: application/json

{
  "prefer_hitl": true,
  "cv_data": {
    "firstName": "Alex",
    "lastName": "Johnson",
    "title": "Software Engineer",
    "email": "alex@example.com"
  }
}
```

Response (202) — confirmation type (inline-capable):
```json
{
  "status": "human_input_required",
  "message": "Please confirm: is this CV for you?",
  "hitl": {
    "spec_version": "0.6",
    "case_id": "review_a7f3b2c8d9e1f0g4",
    "review_url": "https://www.talent.de/en/hitl/review/review_a7f3b2c8d9e1f0g4?token=abc123...",
    "poll_url": "https://www.talent.de/api/hitl/cases/review_a7f3b2c8d9e1f0g4/status",
    "events_url": "https://www.talent.de/api/hitl/cases/review_a7f3b2c8d9e1f0g4/events",
    "submit_url": "https://www.talent.de/api/hitl/cases/review_a7f3b2c8d9e1f0g4/respond",
    "submit_token": "kX9mP2wL7nV5qR8...",
    "inline_actions": ["confirm", "cancel"],
    "type": "confirmation",
    "prompt": "Is this CV for you or someone else?",
    "timeout": "24h",
    "default_action": "skip",
    "created_at": "2026-02-21T10:00:00Z",
    "expires_at": "2026-02-22T10:00:00Z",
    "reminder_at": ["2026-02-21T22:00:00Z"]
  }
}
```

Response (202) — selection type (NOT inline, requires browser):
```json
{
  "status": "human_input_required",
  "message": "Templates available. Please select one for your CV.",
  "hitl": {
    "spec_version": "0.6",
    "case_id": "review_b8g4c3d9e2f1a5h6",
    "review_url": "https://www.talent.de/en/hitl/review/review_b8g4c3d9e2f1a5h6?token=def456...",
    "poll_url": "https://www.talent.de/api/hitl/cases/review_b8g4c3d9e2f1a5h6/status",
    "events_url": "https://www.talent.de/api/hitl/cases/review_b8g4c3d9e2f1a5h6/events",
    "type": "selection",
    "prompt": "Select a template for your CV",
    "timeout": "24h",
    "default_action": "skip",
    "created_at": "2026-02-21T10:00:00Z",
    "expires_at": "2026-02-22T10:00:00Z",
    "reminder_at": ["2026-02-21T22:00:00Z"],
    "context": { "template_selection": true }
  }
}
```

### Reminders

The `reminder_at` array contains ISO timestamps when you should re-send the `review_url` to the user. Default: 12 hours before expiry. If the timeout is shorter than 12h, the array is empty. The agent is responsible for scheduling — the server only provides the timestamps.

## Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `prefer_hitl` | boolean | Enable HITL flow. One of `prefer_hitl` or `skip_hitl` is required. |
| `skip_hitl` | boolean | Skip HITL, create CV directly. For automated pipelines only. |
| `hitl_continue_case_id` | string | Case ID from a completed step to advance to the next step |
| `hitl_approved_case_id` | string | Case ID from a completed approval to finalize and publish CV |
| `hitl_cv_data_override` | object | Human-modified fields that override `cv_data` (from input step) |
| `hitl_step` | string | Skip to a specific step: `context`, `data_review`, `data_input`, `slug`, `template`, `approval` |
| `hitl_callback_url` | string | URL for instant webhook notifications when the human responds |

## Notification Options

Three ways to know when the human has responded:

| Method | Setup | Latency | Recommended for |
|--------|-------|---------|-----------------|
| **Callback** | Include `hitl_callback_url` in request | Instant | Agents with a public endpoint |
| **SSE** | Connect to `events_url` from response | ~2s | Long-lived agent processes |
| **Polling** | GET `poll_url` every 30s | ≤30s | All agents (universal fallback) |

**Callback example:**

```http
POST https://www.talent.de/api/agent/cv-simple
Content-Type: application/json

{
  "access_id": "ak_...",
  "prefer_hitl": true,
  "hitl_callback_url": "https://your-agent.example.com/webhooks/hitl",
  "cv_data": {
    "firstName": "Alex",
    "lastName": "Johnson",
    "title": "Software Engineer",
    "email": "alex@example.com"
  }
}
```

When the human responds, talent.de POSTs to your callback URL:

```json
{
  "event": "review.completed",
  "case_id": "review_a7f3b2c8d9e1f0g4",
  "status": "completed",
  "timestamp": "2026-02-21T10:05:00Z",
  "completed_at": "2026-02-21T10:05:00Z",
  "result": {
    "action": "select",
    "data": { "selected_template_id": "007" }
  }
}
```

Verify the `X-HITL-Signature` header (format: `algorithm=HS256, value={base64url}`). Compute HMAC-SHA256 of the raw request body using your `access_id` as the secret key, then base64url-encode the result.

**SSE example:**

Connect to the `events_url` from the 202 response to receive real-time status updates:

```
GET https://www.talent.de/api/hitl/cases/{case_id}/events
Authorization: Bearer {access_id}
Accept: text/event-stream
```

The stream emits these events:

| Event | When | Payload |
|-------|------|---------|
| `review.status` | On connect | Full current status |
| `review.opened` | Human opens URL | `{ case_id, status, opened_at }` |
| `review.completed` | Human decides | Full status with `result` |
| `review.expired` | 24h timeout | `{ case_id, default_action }` |
| `review.cancelled` | Human cancels | `{ case_id }` |

The stream closes automatically after a terminal event (`completed`, `expired`, `cancelled`). On disconnect, reconnect with the standard `Last-Event-ID` header. The first event will contain the current state as a catchup. Event IDs use the format `{case_id}-{counter}`.

**Polling (enhanced):**

The `poll_url` supports efficient polling with `ETag` and `Retry-After` headers:

```
GET {poll_url}
Authorization: Bearer {access_id}
If-None-Match: "opened-2026-02-21T10:00:00Z"
```

Returns `304 Not Modified` if nothing changed. The `Retry-After` header suggests the optimal poll interval (30s for pending, 10s when human is active). When the case is completed, the response includes `responded_by` (metadata about who responded) and `completed_at`.

**Rate limiting:** The poll endpoint enforces 60 requests per minute per case. If exceeded, you receive `429 Too Many Requests` with a `Retry-After` header. Always respect the `Retry-After` value to avoid being rate-limited.

## Inline Submit (v0.6)

For simple button-based decisions, agents can submit directly via API without the human opening a browser. This enables native button rendering in Telegram, WhatsApp, Slack, and other messengers.

### Which types support inline?

| Type | Inline? | Actions | Why |
|------|---------|---------|-----|
| `confirmation` | YES | `confirm`, `cancel` | Simple 2-button decision |
| `escalation` | YES | `retry`, `skip`, `abort` | 3-button recovery |
| `approval` | YES | `approve`, `reject` | 2-button review (no edit cycle) |
| `selection` | NO | — | Template grid, images, complex UI |
| `input` | NO | — | Dynamic forms, validation |

### How to detect inline capability

Check the 202 response for these fields:
- `submit_url` — endpoint for agent submission
- `submit_token` — Bearer token for auth
- `inline_actions` — array of allowed action strings

If these fields are absent, the type requires the `review_url` (browser).

### Agent submission via Bearer token

The inline submit body is **flat** (not nested under `result`):

```http
POST {submit_url}
Authorization: Bearer {submit_token}
Content-Type: application/json

{
  "action": "confirm",
  "data": {},
  "submitted_via": "telegram_inline_button",
  "submitted_by": {
    "platform": "telegram",
    "platform_user_id": "123456",
    "display_name": "User Name"
  }
}
```

Response (200):
```json
{
  "success": true,
  "case_id": "review_a7f3b2c8d9e1f0g4",
  "status": "completed"
}
```

Error responses:
- `403` — Invalid token OR action not in `inline_actions` (includes `review_url` for fallback)
- `409` — Case already completed
- `410` — Case expired

### Security rules

- The `submit_token` is **separate** from the `review_url` token — different security scopes
- Each token is validated ONLY against its corresponding hash (Spec Section 7.5)
- A leaked `review_url` does NOT grant inline submit access, and vice versa
- **NEVER** embed `submit_token` in messenger callback_data — store it in agent's secure context
- Submit via `Authorization: Bearer` header only
- If the action is not in `inline_actions`, the server returns `403` with `review_url` — redirect the human to the browser
- Review page submit (`{ token, result: { action, data } }`) continues to work for backward compatibility

### Platform rendering guidance

| Platform | Max buttons | Note |
|----------|-------------|------|
| Telegram | Unbounded (keyboard) | Ideal for inline — use inline keyboard buttons |
| WhatsApp | 3 | Works for confirmation/approval, tight for escalation |
| Slack | ~25 (blocks) | Ideal for all inline types |
| Discord | 40 (components) | Works well |
| SMS/Email | 0 | Not inline-capable — use `review_url` |

### Fallback strategy

Always render the `review_url` as a fallback link alongside inline buttons. If the platform doesn't support buttons, or the action requires complex input (notes, data), the human can click through to the full review page.

## Tips for Agents

- **IMPORTANT: Use the `review_url` exactly as returned in the response. Do NOT modify, re-encode, or reconstruct this URL. It contains a cryptographic token — any change will invalidate it.**
- Present the `review_url` to the user as a clickable link. Do NOT attempt to generate your own tokens.
- Use callbacks for instant notification, or poll `poll_url` as a fallback. The case expires after 24h by default.
- If the user rejects, ask for feedback and create a new CV with adjustments.
- If the user requests edits, apply their feedback and submit again with `prefer_hitl: true`.
- **Grace period:** After a human submits, the response can be updated within 5 minutes. After the grace period, the case is final (409 Conflict).
- Use `"skip_hitl": true` for direct creation (201 response). Omitting both `prefer_hitl` and `skip_hitl` returns a 400 error.
