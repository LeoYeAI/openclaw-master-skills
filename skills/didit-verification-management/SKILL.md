---
name: didit-verification-management
description: >
  Full Didit identity verification platform management — account creation, API keys,
  sessions, workflows, questionnaires, users, billing, blocklist, and webhooks. Use when
  someone needs to create a Didit account, get API keys, set up verification workflows,
  create or retrieve verification sessions, approve or decline sessions, manage users,
  check credit balance, top up credits, configure blocklists, configure webhooks
  programmatically, handle webhook signatures, or perform any platform administration.
  45+ endpoints across 9 categories.
version: 4.1.0
metadata:
  openclaw:
    requires:
      env: []
    primaryEnv: DIDIT_API_KEY
    emoji: "🛡️"
    homepage: https://docs.didit.me
---

# Didit Identity Verification Platform

The single skill for the entire Didit verification platform. Covers account creation, session management, workflow configuration, questionnaires, user management, billing, blocklist, and webhook configuration — 45+ endpoints across 9 categories.

**For standalone verification APIs** (ID scan, liveness, face match, AML, etc.), see the individual `didit-*` skills.

**API Reference Links:**
- **Account Setup:** [Register](https://docs.didit.me/auth-api/register) | [Verify Email](https://docs.didit.me/auth-api/verify-email) | [Login](https://docs.didit.me/auth-api/login) | [Get Credentials](https://docs.didit.me/auth-api/get-credentials)
- **Sessions:** [Create](https://docs.didit.me/sessions-api/create-session) | [Retrieve](https://docs.didit.me/sessions-api/retrieve-session) | [List](https://docs.didit.me/sessions-api/list-sessions) | [Delete](https://docs.didit.me/sessions-api/delete-session) | [Update Status](https://docs.didit.me/sessions-api/update-status) | [PDF](https://docs.didit.me/sessions-api/generate-pdf) | [Share](https://docs.didit.me/sessions-api/share-session/share) | [Import](https://docs.didit.me/sessions-api/share-session/import)
- **Workflows:** [Create](https://docs.didit.me/management-api/workflows/create) | [List](https://docs.didit.me/management-api/workflows/list) | [Get](https://docs.didit.me/management-api/workflows/get) | [Update](https://docs.didit.me/management-api/workflows/update) | [Delete](https://docs.didit.me/management-api/workflows/delete)
- **Questionnaires:** [Create](https://docs.didit.me/management-api/questionnaires/create) | [List](https://docs.didit.me/management-api/questionnaires/list) | [Get](https://docs.didit.me/management-api/questionnaires/get) | [Update](https://docs.didit.me/management-api/questionnaires/update) | [Delete](https://docs.didit.me/management-api/questionnaires/delete)
- **Users:** [List](https://docs.didit.me/management-api/users/list) | [Get](https://docs.didit.me/management-api/users/get) | [Update](https://docs.didit.me/management-api/users/update) | [Delete](https://docs.didit.me/management-api/users/delete)
- **Billing:** [Balance](https://docs.didit.me/management-api/billing/balance) | [Top Up](https://docs.didit.me/management-api/billing/top-up)
- **Blocklist:** [Add](https://docs.didit.me/sessions-api/blocklist/add) | [Remove](https://docs.didit.me/sessions-api/blocklist/remove) | [List](https://docs.didit.me/sessions-api/blocklist/list)
- **Session Operations:** [Batch Delete](https://docs.didit.me/management-api/sessions/batch-delete) | [List Reviews](https://docs.didit.me/management-api/sessions/list-reviews) | [Create Review](https://docs.didit.me/management-api/sessions/create-review)
- **Webhook Config:** [Get](https://docs.didit.me/management-api/webhook/get) | [Update](https://docs.didit.me/management-api/webhook/update)
- **Guides:** [Programmatic Registration](https://docs.didit.me/integration/programmatic-registration) | [Webhooks](https://docs.didit.me/integration/webhooks) | [AI Agent Integration](https://docs.didit.me/integration/ai-agent-integration) | [API Overview](https://docs.didit.me/sessions-api/management-api)

---

## Getting Started — Zero to Verifying

Go from nothing to a live verification link in **4 API calls**, no browser needed:

```python
import requests

# 1. Register (any email, no business email required)
requests.post("https://apx.didit.me/auth/v2/programmatic/register/",
    json={"email": "you@gmail.com", "password": "MyStr0ng!Pass"})

# 2. Check email for 6-char OTP, then verify → get api_key
resp = requests.post("https://apx.didit.me/auth/v2/programmatic/verify-email/",
    json={"email": "you@gmail.com", "code": "A3K9F2"})
api_key = resp.json()["application"]["api_key"]
headers = {"x-api-key": api_key, "Content-Type": "application/json"}

# 3. Create a KYC workflow
wf = requests.post("https://verification.didit.me/v3/workflows/",
    headers=headers,
    json={"workflow_label": "My KYC", "workflow_type": "kyc",
          "is_liveness_enabled": True, "is_face_match_enabled": True}).json()

# 4. Create a session → send user to the URL
session = requests.post("https://verification.didit.me/v3/session/",
    headers=headers,
    json={"workflow_id": wf["uuid"], "vendor_data": "user-123"}).json()
print(f"Send user to: {session['url']}")
```

**To add credits:** `GET /v3/billing/balance/` to check, `POST /v3/billing/top-up/` with `{"amount_in_dollars": 50}` for a Stripe checkout link.

---

## Authentication

Two auth schemes are used across the platform:

| Endpoints | Auth | Header |
|---|---|---|
| Register, Verify Email, Login | **None** | (unauthenticated) |
| List Organizations, Get Credentials | **Bearer** | `Authorization: Bearer <access_token>` |
| Everything else (sessions, workflows, etc.) | **API Key** | `x-api-key: <api_key>` |

Get your `api_key` via programmatic registration (above) or from [Didit Business Console](https://business.didit.me) → API & Webhooks.

---

## Account Setup

**Base URL:** `https://apx.didit.me/auth/v2`

### 1. Register

```
POST /programmatic/register/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `email` | string | **Yes** | Any email address |
| `password` | string | **Yes** | Min 8 chars, 1 upper, 1 lower, 1 digit, 1 special |

**Response (201):** `{"message": "Registration successful...", "email": "..."}`

Rate limit: 5 per IP per hour.

### 2. Verify Email & Get Credentials

```
POST /programmatic/verify-email/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `email` | string | **Yes** | Same email from register |
| `code` | string | **Yes** | 6-character alphanumeric OTP from email |

**Response (200):**

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "expires_in": 86400,
  "organization": {"uuid": "...", "name": "..."},
  "application": {"uuid": "...", "client_id": "...", "api_key": "YOUR_KEY_HERE"}
}
```

**`application.api_key`** is the `x-api-key` for all subsequent calls.

### 3. Login (Existing Accounts)

```
POST /programmatic/login/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `email` | string | **Yes** | Account email |
| `password` | string | **Yes** | Account password |

**Response (200):** `{"access_token": "...", "refresh_token": "...", "expires_in": 86400}`

Progressive lockout: 5 fails = 15min, 10 = 1hr, 20 = 24hr.

### 4. List Organizations

```
GET /organizations/me/
```

**Auth:** `Authorization: Bearer <access_token>`

**Response (200):** Array of `{"uuid": "...", "name": "...", "contact_email": "..."}`

### 5. Get Application Credentials

```
GET /organizations/me/{org_id}/applications/{app_id}/
```

**Auth:** `Authorization: Bearer <access_token>`

**Response (200):** `{"uuid": "...", "client_id": "...", "api_key": "..."}`

---

## Workflows

**Base URL:** `https://verification.didit.me/v3`

Workflows define verification steps, thresholds, and accepted documents. Each has a UUID used as `workflow_id` when creating sessions.

**Workflow Types:**

| Type | Purpose | Typical Features |
|---|---|---|
| `kyc` | Full identity verification (ID + selfie) | ID Verification, Liveness, Face Match, AML, NFC |
| `adaptive_age_verification` | Age gating with ID fallback for borderline cases | Age Estimation, Liveness, per-country age restrictions |
| `biometric_authentication` | Re-verify returning users (no document) | Liveness, Face Match against stored portrait |
| `address_verification` | Verify proof of address documents | Proof of Address, geocoding, name matching |
| `questionnaire_verification` | Custom form/questionnaire verification | Questionnaire, optional ID/liveness add-ons |
| `email_verification` | Email OTP verification as a workflow | Email send/check, breach/disposable detection |
| `phone_verification` | Phone OTP verification as a workflow | Phone send/check, carrier/VoIP detection |

**Features (toggleable per workflow):** ID Verification, Liveness, Face Match, NFC, AML, Phone, Email, Proof of Address, Database Validation, IP Analysis, Age Estimation, Questionnaire.

### 1. List Workflows

```
GET /v3/workflows/
```

**Response (200):** Array of workflow objects with `uuid`, `workflow_label`, `workflow_type`, `is_default`, `features`, `total_price`.

### 2. Create Workflow

```
POST /v3/workflows/
```

| Body | Type | Default | Description |
|---|---|---|---|
| `workflow_label` | string | auto | Display name |
| `workflow_type` | string | `kyc` | Workflow template type |
| `is_default` | boolean | `false` | Set as default |
| `is_liveness_enabled` | boolean | `false` | Liveness detection |
| `face_liveness_method` | string | `passive` | `"passive"`, `"active_3d"`, `"flashing"` |
| `face_liveness_score_decline_threshold` | integer | `50` | Below this → auto-decline |
| `is_face_match_enabled` | boolean | `false` | Selfie-to-document match |
| `face_match_score_decline_threshold` | integer | `50` | Below this → auto-decline |
| `face_match_score_review_threshold` | integer | `70` | Below this → manual review |
| `is_aml_enabled` | boolean | `false` | AML/PEP/sanctions screening |
| `aml_decline_threshold` | integer | `80` | Above this → auto-decline |
| `is_phone_verification_enabled` | boolean | `false` | Phone verification step |
| `is_email_verification_enabled` | boolean | `false` | Email verification step |
| `is_database_validation_enabled` | boolean | `false` | Gov database validation |
| `is_ip_analysis_enabled` | boolean | `false` | IP risk analysis |
| `is_nfc_enabled` | boolean | `false` | NFC chip reading (mobile only, ePassports) |
| `is_age_restrictions_enabled` | boolean | `false` | Enable per-country age restrictions (for `adaptive_age_verification`) |
| `documents_allowed` | object | `{}` | Restrict accepted countries/doc types (empty = accept all) |
| `duplicated_user_action` | string | `no_action` | `no_action`, `review`, `decline` (set after creation via update) |
| `max_retry_attempts` | integer | `3` | Max retries per session |
| `retry_window_days` | integer | `7` | Days within which retries are allowed |

**Response (201):** Workflow object with `uuid`.

```python
wf = requests.post("https://verification.didit.me/v3/workflows/",
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json={"workflow_label": "KYC + AML", "workflow_type": "kyc",
          "is_liveness_enabled": True, "is_face_match_enabled": True,
          "is_aml_enabled": True}).json()
```

### 3. Get Workflow

```
GET /v3/workflows/{settings_uuid}/
```

### 4. Update Workflow

```
PATCH /v3/workflows/{settings_uuid}/
```

Partial update — only send fields to change.

### 5. Delete Workflow

```
DELETE /v3/workflows/{settings_uuid}/
```

**Response:** `204 No Content`. Existing sessions are not affected.

---

## Sessions

**Base URL:** `https://verification.didit.me/v3`

Sessions are the core unit of verification. Every verification starts by creating a session linked to a workflow.

**Lifecycle:** `Create → User verifies at URL → Webhook/poll decision → Optionally update status`

**Statuses:** `Not Started`, `In Progress`, `In Review`, `Approved`, `Declined`, `Abandoned`, `Expired`, `Resubmitted`

**Rate limits:** 300 req/min per method. Session creation: 600/min. Decision polling: 100/min.

### 1. Create Session

```
POST /v3/session/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `workflow_id` | uuid | **Yes** | Workflow UUID |
| `vendor_data` | string | No | Your user identifier |
| `callback` | url | No | Redirect URL (Didit appends `verificationSessionId` + `status`) |
| `callback_method` | string | No | `"initiator"`, `"completer"`, or `"both"` |
| `metadata` | JSON string | No | Custom data stored with session |
| `language` | string | No | ISO 639-1 UI language |
| `contact_details.email` | string | No | Pre-fill email for email verification step |
| `contact_details.phone` | string | No | Pre-fill phone (E.164) for phone verification step |
| `contact_details.send_notification_emails` | boolean | No | Send status update emails to user |
| `contact_details.email_lang` | string | No | Language for email notifications (ISO 639-1) |
| `expected_details.first_name` | string | No | Triggers mismatch warning if different (fuzzy match) |
| `expected_details.last_name` | string | No | Expected last name (fuzzy match) |
| `expected_details.date_of_birth` | string | No | `YYYY-MM-DD` |
| `expected_details.gender` | string | No | `"M"`, `"F"`, or `null` |
| `expected_details.nationality` | string | No | ISO 3166-1 alpha-3 country code |
| `expected_details.id_country` | string | No | ISO alpha-3 for expected ID document country (overrides nationality) |
| `expected_details.poa_country` | string | No | ISO alpha-3 for expected PoA document country |
| `expected_details.address` | string | No | Expected address (human-readable, for PoA matching) |
| `expected_details.identification_number` | string | No | Expected document/personal/tax number |
| `expected_details.ip_address` | string | No | Expected IP address (logs warning if different) |
| `portrait_image` | base64 | No | Reference portrait for Biometric Auth (max 1MB) |

**Response (201):**

```json
{
  "session_id": "...",
  "session_number": 1234,
  "session_token": "abcdef123456",
  "url": "https://verify.didit.me/session/abcdef123456",
  "status": "Not Started",
  "workflow_id": "..."
}
```

Send the user to `url` to complete verification.

### 2. Retrieve Session (Get Decision)

```
GET /v3/session/{sessionId}/decision/
```

Returns all verification results. Image URLs expire after 60 minutes.

**Response (200):** Full decision with `status`, `features`, `id_verifications`, `liveness_checks`, `face_matches`, `aml_screenings`, `phone_verifications`, `email_verifications`, `poa_verifications`, `database_validations`, `ip_analyses`, `reviews`.

### 3. List Sessions

```
GET /v3/sessions/
```

| Query | Type | Default | Description |
|---|---|---|---|
| `vendor_data` | string | — | Filter by your user identifier |
| `status` | string | — | Filter by status (e.g. `Approved`, `Declined`, `In Review`) |
| `country` | string | — | Filter by ISO 3166-1 alpha-3 country code |
| `workflow_id` | string | — | Filter by workflow UUID |
| `offset` | integer | `0` | Number of items to skip |
| `limit` | integer | `20` | Max items to return |

**Response (200):** Paginated list with `count`, `next`, `previous`, `results[]`.

### 4. Delete Session

```
DELETE /v3/session/{sessionId}/delete/
```

**Response:** `204 No Content`. Permanently deletes all associated data.

### 5. Batch Delete Sessions

```
POST /v3/sessions/delete/
```

| Body | Type | Description |
|---|---|---|
| `session_numbers` | array | List of session numbers to delete |
| `delete_all` | boolean | Delete all sessions (use with caution) |

### 6. Update Session Status

```
PATCH /v3/session/{sessionId}/update-status/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `new_status` | string | **Yes** | `"Approved"`, `"Declined"`, or `"Resubmitted"` |
| `comment` | string | No | Reason for change |
| `send_email` | boolean | No | Send notification email |
| `email_address` | string | Conditional | Required when `send_email` is `true` |
| `email_language` | string | No | Email language (default: `"en"`) |
| `nodes_to_resubmit` | array | No | For Resubmitted: `[{"node_id": "feature_ocr", "feature": "OCR"}]` |

Resubmit requires session to be Declined, In Review, or Abandoned.

### 7. Generate PDF Report

```
GET /v3/session/{sessionId}/generate-pdf
```

Rate limit: 100 req/min.

### 8. Share Session

```
POST /v3/session/{sessionId}/share/
```

Generates a `share_token` for B2B KYC sharing. Only works for finished sessions.

### 9. Import Shared Session

```
POST /v3/session/import-shared/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `share_token` | string | **Yes** | Token from sharing partner |
| `trust_review` | boolean | **Yes** | `true`: keep original status; `false`: set to "In Review" |
| `workflow_id` | string | **Yes** | Your workflow ID |
| `vendor_data` | string | No | Your user identifier |

A session can only be imported once per partner application.

### 10. List Session Reviews

```
GET /v3/sessions/{session_id}/reviews/
```

**Response (200):** Array of review activity items:

```json
[
  {
    "id": 1,
    "action": "status_change",
    "old_status": "In Review",
    "new_status": "Approved",
    "note": "Document verified manually",
    "created_at": "2025-06-01T15:00:00Z"
  }
]
```

### 11. Create Session Review

```
POST /v3/sessions/{session_id}/reviews/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `new_status` | string | **Yes** | `"Approved"`, `"Declined"`, or `"In Review"` |
| `comment` | string | No | Review note |

**Response (201):** The created review item.

---

## Blocklist

Block entities from a session to auto-decline future matches.

### 1. Add to Blocklist

```
POST /v3/blocklist/add/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `session_id` | uuid | **Yes** | Session to blocklist items from |
| `blocklist_face` | boolean | No | Block biometric face template |
| `blocklist_document` | boolean | No | Block document fingerprint |
| `blocklist_phone` | boolean | No | Block phone number |
| `blocklist_email` | boolean | No | Block email address |

**Warning tags on match:** `FACE_IN_BLOCKLIST`, `ID_DOCUMENT_IN_BLOCKLIST`, `PHONE_NUMBER_IN_BLOCKLIST`, `EMAIL_IN_BLOCKLIST`

### 2. Remove from Blocklist

```
POST /v3/blocklist/remove/
```

Same structure with `unblock_face`, `unblock_document`, `unblock_phone`, `unblock_email`.

### 3. List Blocklist

```
GET /v3/blocklist/
```

| Query | Type | Description |
|---|---|---|
| `item_type` | string | `"face"`, `"document"`, `"phone"`, `"email"`. Omit for all. |

---

## Questionnaires

Custom forms attached to verification workflows. Support 7 element types: `short_text`, `long_text`, `multiple_choice`, `checkbox`, `file_upload`, `date`, `number`.

### 1. List Questionnaires

```
GET /v3/questionnaires/
```

### 2. Create Questionnaire

```
POST /v3/questionnaires/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `title` | string | **Yes** | Display title |
| `description` | string | No | Description shown to users |
| `default_language` | string | No | Default language code |
| `languages` | array | No | Supported languages |
| `form_elements` | array | **Yes** | Question objects |

**Form element:**

| Field | Type | Required | Description |
|---|---|---|---|
| `element_type` | string | **Yes** | One of the 7 types above |
| `label` | object | **Yes** | Translations: `{"en": "Question?", "es": "¿Pregunta?"}` |
| `is_required` | boolean | No | Mandatory answer |
| `options` | array | Conditional | Required for `multiple_choice`/`checkbox` |

```python
requests.post("https://verification.didit.me/v3/questionnaires/",
    headers=headers,
    json={
        "title": "Employment Details",
        "default_language": "en",
        "form_elements": [
            {"element_type": "short_text",
             "label": {"en": "Occupation?"}, "is_required": True},
            {"element_type": "multiple_choice",
             "label": {"en": "Employment status"},
             "options": [{"label": {"en": "Employed"}}, {"label": {"en": "Student"}}]},
        ]
    })
```

### 3. Get Questionnaire

```
GET /v3/questionnaires/{questionnaire_uuid}/
```

### 4. Update Questionnaire

```
PATCH /v3/questionnaires/{questionnaire_uuid}/
```

### 5. Delete Questionnaire

```
DELETE /v3/questionnaires/{questionnaire_uuid}/
```

**Response:** `204 No Content`.

---

## Users

Manage verified individuals identified by `vendor_data`.

### 1. List Users

```
GET /v3/users/
```

| Query | Type | Description |
|---|---|---|
| `status` | string | `Approved`, `Declined`, `In Review`, `Pending` |
| `search` | string | Search by name or identifier |
| `country` | string | ISO 3166-1 alpha-3 |
| `limit` | integer | Results per page (max 200) |
| `offset` | integer | Pagination offset |

**Response (200):** Paginated list with `vendor_data`, `full_name`, `status`, `session_count`, `issuing_states`, `approved_emails`, `approved_phones`.

### 2. Get User

```
GET /v3/users/{vendor_data}/
```

### 3. Update User

```
PATCH /v3/users/{vendor_data}/
```

| Body | Type | Description |
|---|---|---|
| `display_name` | string | Custom display name |
| `status` | string | Manual override: `Approved`, `Declined`, `In Review` |
| `metadata` | object | Custom JSON metadata |

### 4. Batch Delete Users

```
POST /v3/users/delete/
```

| Body | Type | Description |
|---|---|---|
| `vendor_data_list` | array | List of vendor_data strings |
| `delete_all` | boolean | Delete all users |

---

## Billing

### 1. Get Credit Balance

```
GET /v3/billing/balance/
```

**Response (200):**

```json
{
  "balance": "142.5000",
  "auto_refill_enabled": true,
  "auto_refill_amount": "100.0000",
  "auto_refill_threshold": "10.0000"
}
```

### 2. Top Up Credits

```
POST /v3/billing/top-up/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `amount_in_dollars` | number | **Yes** | Minimum $50 |
| `success_url` | string | No | Redirect after payment |
| `cancel_url` | string | No | Redirect on cancel |

**Response (200):**

```json
{
  "checkout_session_id": "cs_live_...",
  "checkout_session_url": "https://checkout.stripe.com/..."
}
```

Present `checkout_session_url` to the user for payment.

---

## Webhook Configuration

Set up webhooks **programmatically** — no console needed.

### 1. Get Webhook Configuration

```
GET /v3/webhook/
```

**Response (200):**

```json
{
  "webhook_url": "https://myapp.com/webhooks/didit",
  "webhook_version": "v3",
  "secret_shared_key": "whsec_a1b2c3d4e5f6g7h8i9j0...",
  "capture_method": "both",
  "data_retention_months": null
}
```

| Field | Type | Description |
|---|---|---|
| `webhook_url` | string/null | URL where notifications are sent (`null` if not configured) |
| `webhook_version` | string | `"v1"`, `"v2"`, or `"v3"` (v3 recommended) |
| `secret_shared_key` | string | HMAC secret for verifying webhook signatures |
| `capture_method` | string | `"mobile"`, `"desktop"`, or `"both"` |
| `data_retention_months` | integer/null | Months to retain session data (`null` = unlimited) |

### 2. Update Webhook Configuration

```
PATCH /v3/webhook/
```

| Body | Type | Required | Description |
|---|---|---|---|
| `webhook_url` | string/null | No | URL for notifications (set `null` to disable) |
| `webhook_version` | string | No | `"v1"`, `"v2"`, or `"v3"` |
| `rotate_secret_key` | boolean | No | `true` to generate a new secret (old one immediately invalidated) |
| `capture_method` | string | No | `"mobile"`, `"desktop"`, or `"both"` |
| `data_retention_months` | integer/null | No | 1–120 months, or `null` for unlimited |

**Example — set webhook URL:**

```python
requests.patch(
    "https://verification.didit.me/v3/webhook/",
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json={"webhook_url": "https://myapp.com/webhooks/didit", "webhook_version": "v3"},
)
```

**Example — rotate secret:**

```python
r = requests.patch(
    "https://verification.didit.me/v3/webhook/",
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json={"rotate_secret_key": True},
)
new_secret = r.json()["secret_shared_key"]
```

**Example — disable webhooks:**

```python
requests.patch(
    "https://verification.didit.me/v3/webhook/",
    headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
    json={"webhook_url": None},
)
```

**Response (200):** Same shape as GET — returns the updated configuration.

---

## Webhook Events & Signatures

Didit sends `POST` requests to your webhook URL when session status changes. Retries up to 2 times with exponential backoff (1 min, 4 min).

### Payload

```json
{
  "session_id": "...",
  "status": "Approved",
  "webhook_type": "status.updated",
  "vendor_data": "user-123",
  "timestamp": 1627680000,
  "decision": { ... }
}
```

**Event types:** `status.updated` (status change), `data.updated` (KYC/POA data manually updated).

### Signature Verification (V2 — recommended)

Two headers: `X-Signature-V2` (HMAC-SHA256 hex) and `X-Timestamp` (Unix seconds).

```python
import hashlib, hmac, time, json

def verify_webhook_v2(body_dict: dict, signature: str, timestamp: str, secret: str) -> bool:
    if abs(time.time() - int(timestamp)) > 300:
        return False
    def process_value(v):
        if isinstance(v, float) and v == int(v):
            return int(v)
        if isinstance(v, dict):
            return {k: process_value(val) for k, val in v.items()}
        if isinstance(v, list):
            return [process_value(i) for i in v]
        return v
    canonical = json.dumps(process_value(body_dict), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    message = f"{timestamp}:{canonical}"
    expected = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

### Simple Signature (Fallback)

Header: `X-Signature-Simple` — HMAC of key fields only.

```python
def verify_webhook_simple(session_id, status, webhook_type, timestamp, signature, secret):
    message = f"{timestamp}:{session_id}:{status}:{webhook_type}"
    expected = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)
```

---

## Error Responses (All Endpoints)

| Code | Meaning | Action |
|---|---|---|
| `400` | Invalid request | Check required fields and formats |
| `401` | Invalid or missing API key | Verify `x-api-key` header |
| `403` | Insufficient credits or no permission | Check balance, API key permissions |
| `404` | Resource not found | Verify IDs |
| `429` | Rate limited | Check `Retry-After` header, exponential backoff |

---

## Common Workflows

### Full KYC Onboarding

```
1. POST /programmatic/register/      → register
2. POST /programmatic/verify-email/  → get api_key
3. POST /v3/workflows/               → create KYC workflow
4. PATCH /v3/webhook/                → set webhook_url + webhook_version "v3"
5. POST /v3/session/                 → create session → get URL
6. User completes verification at URL
7. Webhook fires → GET /v3/session/{id}/decision/ → read results
```

### Programmatic Review + Blocklist

```
1. Webhook: status "In Review"
2. GET /v3/session/{id}/decision/   → inspect results
3. If fraud: PATCH update-status → Declined + POST /v3/blocklist/add/
   If legit: PATCH update-status → Approved
```

### B2B KYC Sharing

```
Service A: POST /v3/session/{id}/share/       → get share_token
Service B: POST /v3/session/import-shared/    → import with trust_review=true
```

### Check Balance Before Sessions

```
1. GET /v3/billing/balance/    → check if balance > 0
2. If low: POST /v3/billing/top-up/ → get Stripe checkout URL
3. POST /v3/session/           → create session
```

### Questionnaire + Workflow

```
1. POST /v3/questionnaires/  → create form → save uuid
2. POST /v3/workflows/       → questionnaire_verification type
3. POST /v3/session/         → session with workflow_id
```

---

## Utility Scripts

### setup_account.py — Register and verify accounts

```bash
pip install requests
python scripts/setup_account.py register you@gmail.com 'MyStr0ng!Pass'
# (check email for code)
python scripts/setup_account.py verify you@gmail.com A3K9F2
# Prints api_key, org_uuid, app_uuid
python scripts/setup_account.py login you@gmail.com 'MyStr0ng!Pass'
```

### manage_workflows.py — CRUD workflows

```bash
export DIDIT_API_KEY="your_key"
python scripts/manage_workflows.py list
python scripts/manage_workflows.py create --label "My KYC" --type kyc --liveness --face-match
python scripts/manage_workflows.py get <uuid>
python scripts/manage_workflows.py update <uuid> --enable-aml --aml-threshold 75
python scripts/manage_workflows.py delete <uuid>
```

### create_session.py — Create verification sessions

```bash
export DIDIT_API_KEY="your_key"
python scripts/create_session.py --workflow-id <uuid> --vendor-data user-123
python scripts/create_session.py --workflow-id <uuid> --vendor-data user-123 --callback https://myapp.com/done
```

All scripts can be imported as libraries:

```python
from scripts.setup_account import register, verify_email, login
from scripts.manage_workflows import list_workflows, create_workflow
from scripts.create_session import create_session
```
