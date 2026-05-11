---
globs: ["**/*clerk*.ts", "**/*middleware*.ts", "**/*auth*.ts", "src/app/api/**/*.ts"]
---

# Clerk Auth Corrections

Claude's training may reference older Clerk patterns. This project uses **Clerk v6+**.

## API Version (CRITICAL)

Clerk deprecated Session Token JWT v1 on **April 14, 2025**. Projects using `@clerk/backend@2.x` require API version `2025-04-10` or later.

| If using... | Required API Version |
|-------------|---------------------|
| `@clerk/backend@2.x` | 2025-04-10+ (v2 tokens) |
| `@clerk/nextjs@6.x` | 2025-04-10+ (v2 tokens) |

## Next.js v6: auth() is Async

```typescript
/* ❌ v5 (synchronous) */
import { auth } from '@clerk/nextjs/server'
const { userId } = auth()

/* ✅ v6 (asynchronous) */
import { auth } from '@clerk/nextjs/server'
const { userId } = await auth()
```

## auth.protect() is Async

```typescript
/* ❌ v5 */
auth.protect()

/* ✅ v6 */
await auth.protect()
```

## Token Verification

Use the `@clerk/backend` SDK's `verifyToken` function for backend token verification.

```typescript
import { verifyToken } from '@clerk/backend';

// Verify JWT from Authorization header
const token = request.headers.get('Authorization')?.replace('Bearer ', '');
const payload = await verifyToken(token, {
  secretKey: env.CLERK_SECRET_KEY,
  authorizedParties: ['https://yourdomain.com'],  // REQUIRED for Cloudflare Workers
});
```

**Cloudflare Workers**: Always set `authorizedParties` to prevent CSRF vulnerabilities.

## Custom JWT Template

Use a custom JWT template in Clerk Dashboard with email and metadata claims:

```json
{
  "user_id": "{{user.id}}",
  "email": "{{user.primary_email_address}}",
  "role": "{{user.public_metadata.role}}"
}
```

This avoids extra API calls to fetch user data.

## JWT Size Limit: 1.2KB

Custom claims in session cookies are limited to **1.2KB**. Browsers cap cookies at 4KB; Clerk reserves 2.8KB for defaults.

**Symptom**: Authentication silently fails if custom claims exceed 1.2KB.

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| Large custom claim objects | Keep claims minimal, fetch extra data via API |
| Storing full user profiles in claims | Store IDs only, fetch profiles on demand |

## JWT vs Session Token

| Token Type | Purpose | Custom Claims |
|------------|---------|---------------|
| **Session Token** | Default auth, includes `sid`, `v` claims | Can add via Dashboard → Sessions → Customize |
| **Custom JWT** | Machine-to-machine, API auth | Cannot include session-tied claims (`sid`, `v`, `pla`, `fea`) |

## API Version 2025-11-10 Changes

```typescript
/* ❌ Old field names */
{ payment_source_id: "...", payment_source: {...} }

/* ✅ New field names */
{ payment_method_id: "...", payment_method: {...} }

/* ❌ Old endpoints */
GET /v1/commerce/plans

/* ✅ New endpoints */
GET /v1/billing/plans
```

## Vite Dev Mode: 431 Error Fix

```json
// package.json - Increase header limit
{
  "scripts": {
    "dev": "NODE_OPTIONS='--max-http-header-size=32768' vite"
  }
}
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `const { userId } = auth()` | `const { userId } = await auth()` |
| `auth.protect()` | `await auth.protect()` |
| `apiKey` | `secretKey` |
| Missing `authorizedParties` | Add `authorizedParties: ['https://yourdomain.com']` |
| `/v1/commerce/*` endpoints | `/v1/billing/*` endpoints |
| `payment_source` | `payment_method` |
