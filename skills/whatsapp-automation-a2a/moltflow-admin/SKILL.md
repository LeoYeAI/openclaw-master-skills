---
name: moltflow-admin
description: "Manage MoltFlow authentication, billing, API keys, usage tracking, and tenant settings."
source: "MoltFlow Team"
version: "2.16.1"
risk: safe
requiredEnv:
  - MOLTFLOW_API_KEY
primaryEnv: MOLTFLOW_API_KEY
disable-model-invocation: true
---

> **MoltFlow** — WhatsApp Business automation for teams. Connect, monitor, and automate WhatsApp at scale.
> ***Due to high demand and a recent registration issue, we're offering our top-tier Business plan with unlimited quotas for just $19.90/month on yearly billing — for a limited time only.*** [**Claim the deal**](https://buy.stripe.com/cNifZibX7gpQebJ0nsfnO00)
> Free tier available. [Sign up](https://molt.waiflow.app/checkout?plan=free)

# MoltFlow Admin Skill

Manage authentication, billing, API keys, usage tracking, and tenant settings for MoltFlow.

## Real-World Scenarios

**Agency managing 5 clients** — "Create a scoped API key for each client that only lets them send messages and read their own groups — nothing else."

**Startup scaling up** — "Check my current plan usage and tell me if I'm about to hit my message limit so I can upgrade before the campaign."

**Compliance officer** — "Show me the daily usage breakdown for this month so I can audit how many messages each session sent."

## When to Use

Use this skill when you need to:
- Authenticate with MoltFlow (login, token refresh, magic link)
- Manage API keys (create, rotate, revoke)
- Check subscription status, plan limits, or usage
- Create a Stripe checkout session or billing portal link
Trigger phrases: "login to MoltFlow", "create API key", "check subscription", "billing portal", "usage report"

## Prerequisites

- **MOLTFLOW_API_KEY** — required for most endpoints. Generate from [MoltFlow Dashboard > API Keys](https://molt.waiflow.app/api-keys)
- Auth endpoints (`/auth/*`) accept email/password — no API key needed for initial login

## Base URL

```
https://apiv2.waiflow.app/api/v2
```

## Required API Key Scopes

| Scope | Access |
|-------|--------|
| `settings` | `manage` |
| `usage` | `read` |
| `billing` | `manage` |
| `account` | `manage` |

## Authentication

All requests (except login/signup) require one of:
- `Authorization: Bearer <access_token>` (JWT from login)
- `X-API-Key: <api_key>` (API key from dashboard)

---

## Auth Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Login with email/password |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user profile |
| POST | `/auth/logout` | Invalidate session |
| POST | `/auth/forgot-password` | Request password reset email |
| POST | `/auth/reset-password` | Confirm password reset |
| POST | `/auth/verify-email` | Verify email address |
| POST | `/auth/magic-link/request` | Request magic link login |
| POST | `/auth/magic-link/verify` | Verify magic link token |
| POST | `/auth/setup-password` | Set password for magic-link users |

### Login — Request/Response

```json
// POST /auth/login
{
  "email": "user@example.com",
  "password": "your-password"
}

// Response
{
  "access_token": "eyJhbGciOi...",
  "refresh_token": "eyJhbGciOi...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "owner",
    "tenant_id": "uuid"
  }
}
```

---

## User Management

Self-service user profile endpoints (authenticated user):

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/me` | Get own profile |
| PATCH | `/users/me` | Update own profile |

---

## API Keys

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api-keys` | List all API keys |
| POST | `/api-keys` | Create new key |
| GET | `/api-keys/{id}` | Get key details |
| DELETE | `/api-keys/{id}` | Revoke key |
| POST | `/api-keys/{id}/rotate` | Rotate key (new secret) |

### Create API Key — Request/Response

```json
// POST /api-keys
{
  "name": "outreach-bot",
  "scopes": ["messages:send", "custom-groups:manage", "bulk-send:manage"],
  "expires_in_days": 90
}

// Response (raw key shown ONCE — save it immediately)
{
  "id": "uuid",
  "name": "outreach-bot",
  "key_prefix": "mf_abc1",
  "raw_key": "mf_abc1234567890abcdef...",
  "scopes": ["messages:send", "custom-groups:manage", "bulk-send:manage"],
  "expires_at": "2026-04-15T10:00:00Z",
  "created_at": "2026-01-15T10:00:00Z",
  "is_active": true
}
```

- `scopes`: **Required** array of permission scopes. Specify only the scopes needed (e.g., `["sessions:read", "messages:send"]`). See main SKILL.md for the complete scope reference.
- `expires_in_days`: Optional expiry in days (default: no expiry).

**Important:** The `raw_key` is only returned at creation time. It is stored as a SHA-256 hash — it cannot be retrieved later.

---

## Billing & Subscription

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/billing/subscription` | Current plan, limits, and usage |
| POST | `/billing/checkout` | Create Stripe checkout session |
| POST | `/billing/portal` | Get Stripe billing portal URL |
| POST | `/billing/cancel` | Cancel subscription |
| GET | `/billing/plans` | List available plans and pricing |
| POST | `/billing/signup-checkout` | Checkout for new signups |

### Check Subscription — Response

```json
{
  "plan_id": "pro",
  "display_name": "Pro",
  "status": "active",
  "billing_cycle": "monthly",
  "current_period_end": "2026-02-15T00:00:00Z",
  "limits": {
    "max_sessions": 3,
    "max_messages_per_month": 5000,
    "max_groups": 10,
    "max_labels": 50,
    "ai_replies_per_month": 500
  },
  "usage": {
    "sessions": 2,
    "messages_this_month": 1247,
    "groups": 5,
    "labels": 12,
    "ai_replies_this_month": 89
  }
}
```

### Create Checkout — Request

```json
// POST /billing/checkout
{
  "plan_id": "pro",
  "billing_cycle": "monthly"
}

// Response
{
  "checkout_url": "https://checkout.stripe.com/c/pay/cs_live_...",
  "session_id": "cs_live_..."
}
```

---

## Usage Tracking

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/usage/current` | Current month usage summary |
| GET | `/usage/history` | Historical usage by month |
| GET | `/usage/daily` | Daily breakdown for current month |

---

## Tenant Settings

Self-service tenant configuration (owner/admin role required for writes).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tenant/settings` | Get current tenant settings |
| PATCH | `/tenant/settings` | Update tenant settings (owner/admin only) |

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `allowed_numbers` | `string[]` | Phone numbers allowed for outbound messaging |
| `require_approval` | `bool` | Whether outbound messages require admin approval |
| `ai_consent_enabled` | `bool` | Whether AI features (auto-reply, style matching) are enabled |

#### Get Tenant Settings

```bash
curl https://apiv2.waiflow.app/tenant/settings \
  -H "X-API-Key: $MOLTFLOW_API_KEY"
```

### Get Settings — Response

```json
{
  "allowed_numbers": ["+5511999999999"],
  "require_approval": false,
  "ai_consent_enabled": true
}
```

#### Update Tenant Settings

```bash
curl -X PATCH https://apiv2.waiflow.app/tenant/settings \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"ai_consent_enabled": true}'
```

### Update Settings — Request Body

All fields are optional. Only provided fields are updated.

```json
{
  "allowed_numbers": ["+5511999999999", "+5511888888888"],
  "require_approval": true,
  "ai_consent_enabled": true
}
```

**Notes:**
- `ai_consent_enabled` records a GDPR consent entry (consent type `ai_processing`, version `1.0`) with the user's IP and user-agent.
- Any authenticated user can read settings; only `owner` or `admin` roles can update.

---

## curl Examples

### 1. Login and Get Token

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'
```

### 2. Create a Scoped API Key

```bash
curl -X POST https://apiv2.waiflow.app/api/v2/api-keys \
  -H "X-API-Key: $MOLTFLOW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "outreach-bot",
    "scopes": ["messages:send", "custom-groups:manage", "bulk-send:manage"],
    "expires_in_days": 90
  }'
```

### 3. Check Subscription and Usage

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/billing/subscription"
```

### 4. Check Current Month Usage

```bash
curl -H "X-API-Key: $MOLTFLOW_API_KEY" \
  "https://apiv2.waiflow.app/api/v2/usage/current"
```

---

## Error Responses

| Status | Meaning |
|--------|---------|
| 400 | Invalid request body or parameters |
| 401 | Missing or invalid authentication |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict (duplicate email, plan ID, etc.) |
| 422 | Validation error |
| 429 | Rate limit exceeded |

---

## Tips

- **API key security**: The raw key is only shown once at creation. Store it in a secrets manager.
- **Token refresh**: Access tokens expire in 30 minutes. Use the refresh endpoint to get new ones without re-authenticating.
- **Magic links**: For passwordless login, use `magic-link/request` then `magic-link/verify`.
- **Plan limits**: Use `GET /billing/subscription` to check remaining quotas before making API calls.
- **Scoped keys**: Always use the minimum scopes needed for your workflow.

---

## Related Skills

- **moltflow** -- Core API: sessions, messaging, groups, labels, webhooks
- **moltflow-outreach** -- Bulk Send, Scheduled Messages, Custom Groups
- **moltflow-leads** -- Lead detection, pipeline tracking, bulk operations, CSV/JSON export
- **moltflow-ai** -- AI-powered auto-replies, voice transcription, RAG knowledge base, style profiles
- **moltflow-a2a** -- Agent-to-Agent protocol, encrypted messaging, content policy
- **moltflow-reviews** -- Review collection and testimonial management
