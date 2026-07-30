---
name: humanos
description: Require verifiable human approval before high-risk agent actions.
version: 0.1.1
homepage: https://github.com/Humanos-App/humanos-openclaw
user-invocable: true
metadata:
  openclaw:
    requires:
      env:
        - VIA_API_KEY
        - VIA_SIGNATURE_SECRET
      bins:
        - curl
        - jq
        - openssl
    os:
      - darwin
      - linux
    primaryEnv: VIA_API_KEY
    emoji: "shield"
---

# Humanos - Programmable Human Authorization for Agent Actions

AI agents can execute actions.
Humanos lets them prove human authorization before they do.

Require a mandate signature before high-risk execution.

## What It Does

- Collect human approval before sensitive agent actions
- Issue machine-verifiable mandate signatures
- Support scoped delegation (amount, duration, action type)
- Enable revocation of previously granted authority

Humanos provides the authorization proof.
Your runtime decides whether to execute.

## When To Use It

Use Humanos when your agent can:

- Move money or sign transactions
- Initiate payouts, refunds, or batch payments
- Modify or delete user data
- Export or share sensitive data
- Change account permissions or roles
- Rotate API keys or security credentials
- Update billing details or subscription plans
- Execute contracts or legal agreements
- Accept updated terms on behalf of a user
- Grant third-party access to data
- Release funds from escrow
- Increase transaction or withdrawal limits
- File claims, applications, or regulatory forms
- Approve loan or credit changes
- Post or publish under a user's identity
- Control IoT or physical access devices
- Act on behalf of a user
- Delegate authority to another agent

If the action affects money, data, identity, ownership, or legal position, require a mandate signature.

## How It Works

1. Agent prepares a structured action
2. Agent calls `requestMandate(action, constraints)`
3. Human approves via SMS, email, wallet, API, or any programmable channel
4. Humanos returns a signed mandate signature
5. Agent verifies with `verifyMandate(signature)`
6. Agent decides whether to execute

No valid mandate signature -> execution should not proceed.

## Core API

`requestMandate(action, constraints) -> mandate_signature`
`verifyMandate(mandate_signature) -> true / false`
`revokeMandate(mandate_signature)`

Simple. Programmable. Deterministic.

## VIA Humanos - Operational Instructions for Agents

Use this skill whenever the agent is about to do something that requires a human to say "yes" first. It sends a secure approval request to the right person - they receive a link, review the details, and approve or reject. The result comes back as a W3C Verifiable Credential with cryptographic proof that the action was authorized.

**The agent should NEVER proceed with a sensitive action (payment, signing, data access, transfer) without first using this skill to get authorization.**

## When to use this skill

Use this skill when the user says things like:

- "I need approval from [someone] before doing [something]"
- "Get authorization from my manager for this payment"
- "Send this contract/document to [someone] for signing"
- "Check if [someone] approved the request"
- "Has the mandate been approved or rejected?"
- "Verify this person's identity before proceeding"
- "Get consent from the user for data processing"
- "Cancel the pending approval request"
- "Look up user [email/phone/DID]"
- "Is this mandate still valid?"

Also use this skill when the agent is about to:

- **Make a payment or transfer** — get approval first
- **Sign or send a contract** — collect digital signature
- **Access sensitive data** — verify authorization exists
- **Execute a high-value action** — check mandate constraints (amount limits, time bounds)
- **Start an onboarding flow** — combine contract + form + consent in one request

Trigger keywords: approval, authorize, mandate, sign, consent, credential, KYC, identity verification, human approval, compliance, permission, delegation.

## Prerequisites

1. A VIA Protocol account with an API key from [app.humanos.id](https://app.humanos.id)
2. Environment variables set:
   - `VIA_API_KEY` — Bearer token for API authentication
   - `VIA_SIGNATURE_SECRET` — HMAC secret for request signing
   - Optional: `VIA_API_URL` — Override API base URL (default: `https://api.humanos.id`)

Windows note: this skill is currently supported on macOS/Linux shells. On Windows, use WSL or Git Bash with `bash`, `curl`, `jq`, and `openssl` installed.

## Authentication

All API requests require:

```
Authorization: Bearer $VIA_API_KEY
X-Timestamp: <unix-timestamp-ms>
X-Signature: <hmac-sha256 of (timestamp + "." + body) using VIA_SIGNATURE_SECRET>
```

Use the signing script: `scripts/sign-request.sh`

Official API documentation: https://humanos.mintlify.app/essentials/introduction

## Operation Index (Fast Lookup)

Use this as the primary lookup table before reading detailed sections.

| Goal | Script | Method | Endpoint | Required Args |
| --- | --- | --- | --- | --- |
| Create approval request | `scripts/create-request.sh` | `POST` | `/v1/request` | `--contact`, `--type`, `--name` |
| Check request status | `scripts/get-request.sh` | `GET` | `/v1/request/:id` | `--id` |
| Find requests | `scripts/find-requests.sh` | `GET` | `/v1/request?contact|did|internalId` | one of `--contact`, `--did`, `--internal-id` |
| Get credential proof | `scripts/get-credential.sh` | `GET` | `/v1/credential/:id` | `--id` |
| Get mandate | `scripts/get-mandate.sh` | `GET` | `/v1/via/mandates/:id` | `--id` |
| Get mandate VC | `scripts/get-mandate-vc.sh` | `GET` | `/v1/via/mandates/:id/vc` | `--id` |
| Resolve DID | `scripts/resolve-did.sh` | `GET` | `/v1/via/dids/:did` | `--did` |
| Look up user | `scripts/get-user.sh` | `GET` | `/v1/user?contact|did|internalId` | one of `--contact`, `--did`, `--internal-id` |
| Cancel request | `scripts/cancel-request.sh` | `DELETE` | `/v1/request/:id` | `--id` |
| Resend OTP | `scripts/resend-otp.sh` | `PATCH` | `/v1/request/resend/:id` | `--id` (and optional `--contact`) |

## Create Request Rules (Critical)

Follow these rules to avoid generic `400 Failed to generate credentials request` responses.

1. Use `--type` as: `document`, `consent`, or `json` (lowercase input; script converts internally).
2. `form` is not supported as inline credential in this script. Use resource IDs for forms.
3. `--data` should be JSON array of fields. A single object is also accepted and auto-wrapped.
4. Every field should follow:
   - `label` (string)
   - `type` (`string`, `number`, `boolean`, `date`, `url`, `pdf`, `object`, `array`)
   - `value` (matches `type`)
   - `hidden` (boolean; defaults to `false`)
5. Type-specific mandatory fields:
   - `consent`: must include `{"label":"text","type":"string","value":"...","hidden":false}`
   - `document`: must include `{"label":"pdf","type":"pdf","value":"<base64>","hidden":false}`

### Valid examples (copy/paste)

**Consent (recommended for simple approvals):**
```bash
scripts/create-request.sh \
  --contact "+351919307983" \
  --type "consent" \
  --name "Football approval" \
  --data '[{"label":"text","type":"string","value":"I approve football tomorrow.","hidden":false}]'
```

**JSON mandate:**
```bash
scripts/create-request.sh \
  --contact "user@example.com" \
  --type "json" \
  --name "Hotel Booking Authorization" \
  --data '[
    {"label":"amount","type":"number","value":450,"hidden":false},
    {"label":"currency","type":"string","value":"EUR","hidden":false}
  ]'
```

**Document signature:**
```bash
scripts/create-request.sh \
  --contact "user@example.com" \
  --type "document" \
  --name "NDA Signature" \
  --data '[{"label":"pdf","type":"pdf","value":"<base64-pdf>","hidden":false}]'
```

## Signing Algorithm (Exact Bytes, Critical)

All `401 Invalid signature` incidents should be debugged against this section.

1. Build the request body once.
2. Keep the body as a compact JSON string.
3. Generate `timestamp` in unix milliseconds (13 digits).
4. Compute payload as:
   - `timestamp + "." + body` when body is not empty
   - `timestamp` when body is empty
5. Compute `signature = HMAC_SHA256_HEX(payload, VIA_SIGNATURE_SECRET)`.
6. Send exactly the same body bytes in the HTTP request.

### Deterministic checklist

- Use `jq -c` or `jq -n` to build compact JSON.
- Use `printf`, not `echo`, when signing (avoid accidental newline).
- Do not reformat body after signature generation.
- Sign and send immediately (avoid stale timestamps).
- Keep UTF-8 text unchanged (accents and symbols must match).

### Common failure modes

- Timestamp includes non-digits (for example, `%3N` incompatibility on macOS).
- Body was pretty-printed for signing but compacted for sending (or vice versa).
- Body key order/escaping changed between signature and request.
- Wrong base URL or environment points to different backend.
- Secret/token mismatch between environments.

## Core Operations

### 1. Create a Credential Request (Get Human Approval)

When the agent needs human authorization for an action:

```bash
scripts/create-request.sh \
  --contact "user@example.com" \
  --type "json" \
  --name "Hotel Booking Authorization" \
  --security "CONTACT" \
  --data '[{"label":"amount","type":"number","value":450,"hidden":false}]'
```

**Parameters:**
- `--contact` — Email or phone number of the person who must approve (required)
- `--type` — Type of credential: `document`, `json`, or `consent` (required). `form` inline is not supported.
- `--name` — Human-readable name for the approval (required)
- `--security` — Security level: `CONTACT`, `ORGANIZATION_KYC`, `HUMANOS_KYC` (default: CONTACT)
- `--data` — JSON array of mandate fields (optional for `json`; strongly recommended for `consent`/`document`)
- `--language` — Language for the approval UI: `ENG` or `PRT` (default: ENG)
- `--redirect` — URL to redirect user after approval (optional)
- `--internal-id` — Your internal reference ID (optional)

**What happens:**
1. The API creates the request and sends an OTP code to the contact
2. The person opens the link, enters the code, and sees the approval
3. They approve or reject with optional digital signature
4. You receive a webhook or poll for the result

**Response includes:** `requestId` — save this to check status later.

### 2. Check Request Status

```bash
scripts/get-request.sh --id "request-id-here"
```

Returns the full request with all credentials and their statuses (`PENDING`, `APPROVED`, `REJECTED`).

### 3. Find Requests by User

```bash
scripts/find-requests.sh --contact "user@example.com"
# or
scripts/find-requests.sh --did "did:key:z6Mk..."
# or
scripts/find-requests.sh --internal-id "order-123"
```

### 4. Get a Credential with Proofs

```bash
scripts/get-credential.sh --id "credential-id-here"
```

Returns the W3C Verifiable Credential with cryptographic proofs that the human authorized the action.

### 5. Get a Mandate

```bash
scripts/get-mandate.sh --id "mdt_uuid-here"
```

Returns mandate details including scope, validity period, and constraints.

### 6. Get Mandate as Verifiable Credential

```bash
scripts/get-mandate-vc.sh --id "mdt_uuid-here"
```

Returns the mandate in W3C Verifiable Credential format for use in Verifiable Presentations.

### 7. Resolve a DID

```bash
scripts/resolve-did.sh --did "did:key:z6Mk..."
```

Returns the DID Document with verification methods. Use this to verify signatures on credentials.

### 8. Look Up a User

```bash
scripts/get-user.sh --contact "user@example.com"
```

Returns user details, identity information, and associated DIDs.

### 9. Cancel a Request

```bash
scripts/cancel-request.sh --id "request-id-here"
```

Cancels a pending request. This is irreversible.

### 10. Resend OTP

```bash
scripts/resend-otp.sh --id "request-id-here" --contact "user@example.com"
```

Resends the verification code to the user if they didn't receive it.

## Decision Flow

When you need human approval, follow this flow:

1. **Create request** → `scripts/create-request.sh`
2. **Wait for approval** → Poll with `scripts/get-request.sh` or wait for webhook
3. **Check result:**
   - `APPROVED` → Proceed with the action. The credential contains cryptographic proof.
   - `REJECTED` → Do NOT proceed. Inform the user the action was denied.
   - `PENDING` → Still waiting. Ask the user if they want to resend the OTP.

## Security Levels

| Level | Description | Use When |
| --- | --- | --- |
| `CONTACT` | OTP verification only | Low-risk actions (view data, basic approvals) |
| `ORGANIZATION_KYC` | Organization-level identity check | Medium-risk (sign documents, access records) |
| `HUMANOS_KYC` | Full KYC with identity verification | High-risk (payments, legal signatures) |
| `HUMANOS_REVALIDATION` | Re-verification of previously verified identity | Periodic re-checks |

## Credential Types

| Type | Description | User Experience |
| --- | --- | --- |
| `document` | PDF document for review and signature | User sees PDF, can draw signature |
| `form` | Dynamic form with fields | User fills form fields step by step |
| `json` | Structured data for review | User sees data and approves/rejects |
| `consent` | Consent text or URL | User reads and agrees to terms |

## Rate Limits

- Request creation: 60 requests per 60 seconds
- Max 10 credentials per request
- Max 100 contacts per request

## Error Handling

- **401 Unauthorized** — Check VIA_API_KEY and signature
- **404 Not Found** — Request or credential doesn't exist
- **429 Too Many Requests** — Rate limit hit, wait and retry
- **400 Bad Request** — Check request body format

## 401 Invalid Signature Playbook

Follow this exact sequence before escalating:

1. Confirm endpoint is `https://api.humanos.id`.
2. Confirm timestamp is 13-digit numeric milliseconds.
3. Confirm signing payload is exactly:
   - `timestamp + "." + body` (non-empty body), or
   - `timestamp` (empty body).
4. Confirm signed body bytes are the same bytes sent to `curl`.
5. Confirm `VIA_SIGNATURE_SECRET` and `VIA_API_KEY` come from the same environment.
6. Retry with a minimal JSON payload (single credential, no optional fields).
7. If GET works and POST still fails, capture request metadata for backend support:
   - endpoint path
   - timestamp
   - body length
   - `sha256(body)`
   - signature format (hex/base64)

Escalation note for support: "GET succeeds with same key/secret, POST returns 401 Invalid signature using payload=`timestamp.body`."

## Output Format

Always present results to the user in this format:

**For request creation:**
> Request created successfully. An approval link has been sent to [contact].
> Request ID: [id]
> Status: PENDING

**For status checks:**
> Request [id] — Status: [APPROVED/REJECTED/PENDING]
> Credential: [name] — [status]
> Approved by: [contact] on [date]

**For errors:**
> Failed to [action]: [error message]
> Suggestion: [what to do next]

## External Endpoints

| Endpoint | Data Sent | Purpose |
| --- | --- | --- |
| `$VIA_API_URL/v1/request` | Contacts, credential data | Create approval requests |
| `$VIA_API_URL/v1/request/:id` | Request ID | Check approval status |
| `$VIA_API_URL/v1/credential/:id` | Credential ID | Retrieve signed credentials |
| `$VIA_API_URL/v1/via/mandates/:id` | Mandate ID | Get mandate details |
| `$VIA_API_URL/v1/via/mandates?scope=<scope>&toolName=<tool>` | Scope, tool name | Query mandates for policy checks |
| `$VIA_API_URL/v1/via/dids/:did` | DID identifier | Resolve DID documents |
| `$VIA_API_URL/v1/user` | Contact/DID/internal ID | Look up users |

Default base URL is `https://api.humanos.id` when `VIA_API_URL` is not set.

## Security and Privacy

- API keys are read from environment variables, never hardcoded
- All requests are signed with HMAC-SHA256
- Credentials contain W3C Verifiable Credential proofs (EdDSA)
- User contact information (email/phone) is sent to the VIA API for OTP delivery
- No data is stored locally by this skill
