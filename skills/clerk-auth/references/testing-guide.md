# Clerk Authentication - Testing Guide

**Last Updated**: 2025-10-28
**Source**: https://clerk.com/docs/guides/development/testing/overview

This guide covers testing Clerk authentication in your applications, including test credentials, session tokens, testing tokens, and E2E testing with Playwright.

---

## Overview

Testing authentication flows is essential for reliable applications. Clerk provides several tools to make testing easier:

1. **Test Emails & Phone Numbers** - Fake credentials with fixed OTP codes
2. **Session Tokens** - Generate valid tokens via Backend API
3. **Testing Tokens** - Bypass bot detection in test suites
4. **Framework Integrations** - Playwright and Cypress helpers

---

## Quick Start: Test Mode

### Enable Test Mode

Every **development instance** has test mode enabled by default.

For **production instances** (NOT recommended for real customer data):
1. Navigate to Clerk Dashboard → **Settings**
2. Enable the **Enable test mode** toggle

> **WARNING**: Never use test mode on instances managing actual customers.

---

## Test Emails & Phone Numbers

### Fake Email Addresses

Any email with the `+clerk_test` subaddress is a test email address:

```
jane+clerk_test@example.com
john+clerk_test@gmail.com
test+clerk_test@mycompany.com
```

**Behavior**:
- ✅ No emails sent (saves your email quota)
- ✅ Fixed OTP code: `424242`
- ✅ Works in all sign-up/sign-in flows

### Fake Phone Numbers

Any [fictional phone number](https://en.wikipedia.org/wiki/555_(telephone_number)) is a test phone number:

**Format**: `+1 (XXX) 555-0100` to `+1 (XXX) 555-0199`

**Examples**:
```
+12015550100
+19735550133
+14155550142
```

**Behavior**:
- ✅ No SMS sent (saves your SMS quota)
- ✅ Fixed OTP code: `424242`
- ✅ Works in all verification flows

### Monthly Limits (Development Instances)

Clerk development instances have limits:
- **20 SMS messages** per month
- **100 emails** per month

**Excluded from limits**:
- SMS to US numbers
- SMS/emails to test addresses (with `+clerk_test` or 555 numbers)
- Self-delivered messages (your own SMTP/SMS provider)
- Paid subscription apps

To request higher limits, contact Clerk support.

---

## Code Examples: Test Credentials

### Sign In with Test Email

```tsx
import { useSignIn } from '@clerk/clerk-react'

const testSignInWithEmailCode = async () => {
  const { signIn } = useSignIn()

  const emailAddress = 'john+clerk_test@example.com'

  // Step 1: Create sign-in attempt
  const signInResp = await signIn.create({ identifier: emailAddress })

  // Step 2: Find email code factor
  const { emailAddressId } = signInResp.supportedFirstFactors.find(
    (ff) => ff.strategy === 'email_code' && ff.safeIdentifier === emailAddress,
  )! as EmailCodeFactor

  // Step 3: Prepare email verification
  await signIn.prepareFirstFactor({
    strategy: 'email_code',
    emailAddressId: emailAddressId,
  })

  // Step 4: Verify with fixed code
  const attemptResponse = await signIn.attemptFirstFactor({
    strategy: 'email_code',
    code: '424242', // Fixed test code
  })

  if (attemptResponse.status === 'complete') {
    console.log('Sign in successful!')
  } else {
    console.error('Sign in failed')
  }
}
```

### Sign Up with Test Phone

```tsx
import { useSignUp } from '@clerk/clerk-react'

const testSignUpWithPhoneNumber = async () => {
  const { signUp } = useSignUp()

  // Step 1: Create sign-up with test phone
  await signUp.create({
    phoneNumber: '+12015550100',
  })

  // Step 2: Prepare phone verification
  await signUp.preparePhoneNumberVerification()

  // Step 3: Verify with fixed code
  const res = await signUp.attemptPhoneNumberVerification({
    code: '424242', // Fixed test code
  })

  if (res.verifications.phoneNumber.status === 'verified') {
    console.log('Sign up successful!')
  } else {
    console.error('Sign up failed')
  }
}
```

---

## Session Tokens (Backend API)

For testing API endpoints or backend services, you need valid session tokens.

### Flow: Generate Session Token

**4-Step Process**:

1. **Create User** (if needed)
2. **Create Session** for user
3. **Create Session Token** from session ID
4. **Use Token** in Authorization header

### Step-by-Step Implementation

#### Step 1: Create User

**Endpoint**: `POST https://api.clerk.com/v1/users`

```bash
curl -X POST https://api.clerk.com/v1/users \
  -H "Authorization: Bearer sk_test_YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": ["test+clerk_test@example.com"],
    "password": "TestPassword123!"
  }'
```

**Response**:
```json
{
  "id": "user_2abc123def456",
  "email_addresses": [
    {
      "id": "idn_2xyz789",
      "email_address": "test+clerk_test@example.com"
    }
  ]
}
```

**Save**: `user_id` for next step

#### Step 2: Create Session

**Endpoint**: `POST https://api.clerk.com/v1/sessions`

```bash
curl -X POST https://api.clerk.com/v1/sessions \
  -H "Authorization: Bearer sk_test_YOUR_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_2abc123def456"
  }'
```

**Response**:
```json
{
  "id": "sess_2xyz789abc123",
  "user_id": "user_2abc123def456",
  "status": "active"
}
```

**Save**: `session_id` for next step

#### Step 3: Create Session Token

**Endpoint**: `POST https://api.clerk.com/v1/sessions/{session_id}/tokens`

```bash
curl -X POST https://api.clerk.com/v1/sessions/sess_2xyz789abc123/tokens \
  -H "Authorization: Bearer sk_test_YOUR_SECRET_KEY"
```

**Response**:
```json
{
  "jwt": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "object": "token"
}
```

**Save**: `jwt` token

#### Step 4: Use Token in Requests

```bash
curl https://yourdomain.com/api/protected \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Token Lifetime

**CRITICAL**: Session tokens are valid for **60 seconds only**.

**Refresh Strategies**:

**Option 1: Before Each Test**
```typescript
beforeEach(async () => {
  sessionToken = await refreshSessionToken(sessionId)
})
```

**Option 2: Interval Timer**
```typescript
setInterval(async () => {
  sessionToken = await refreshSessionToken(sessionId)
}, 50000) // Refresh every 50 seconds
```

### Node.js Script Example

See `scripts/generate-session-token.js` for a complete implementation.

---

## Testing Tokens (Bot Detection Bypass)

Testing Tokens bypass Clerk's bot detection mechanisms during automated testing.

### What Are Testing Tokens?

- **Purpose**: Prevent "Bot traffic detected" errors in test suites
- **Lifetime**: Short-lived (expires after use)
- **Scope**: Valid only for specific Clerk instance
- **Source**: Obtained via Backend API

### When to Use

**Use Testing Tokens when**:
- Running E2E tests with Playwright or Cypress
- Automated test suites triggering bot detection
- CI/CD pipelines running authentication flows

**Alternatives**:
- Use `@clerk/testing` package (handles automatically)
- Playwright integration (recommended)
- Cypress integration (recommended)

### Obtain Testing Token

**Endpoint**: `POST https://api.clerk.com/v1/testing_tokens`

```bash
curl -X POST https://api.clerk.com/v1/testing_tokens \
  -H "Authorization: Bearer sk_test_YOUR_SECRET_KEY"
```

**Response**:
```json
{
  "token": "1713877200-c_2J2MvPu9PnXcuhbPZNao0LOXqK9A7YrnBn0HmIWxy"
}
```

### Use Testing Token

Add `__clerk_testing_token` query parameter to Frontend API requests:

```
POST https://happy-hippo-1.clerk.accounts.dev/v1/client/sign_ups?__clerk_testing_token=1713877200-c_2J2MvPu9PnXcuhbPZNao0LOXqK9A7YrnBn0HmIWxy
```

### Production Limitations

Testing Tokens work in **both development and production**, but:

**❌ Not Supported in Production**:
- Code-based authentication (SMS OTP, Email OTP)

**✅ Supported in Production**:
- Email + password authentication
- Email magic link (sign-in via email)

---

## E2E Testing with Playwright

Clerk provides first-class Playwright support via `@clerk/testing`.

### Install

```bash
npm install -D @clerk/testing
```

### Set Environment Variables

In your test runner (e.g., `.env.test` or GitHub Actions secrets):

```bash
CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
```

**Security**: Use GitHub Actions secrets or similar for CI/CD.

### Global Setup

Configure `clerkSetup()` to obtain Testing Token once for all tests:

**File**: `global.setup.ts`

```typescript
import { clerkSetup } from '@clerk/testing/playwright'
import { test as setup } from '@playwright/test'

// Run setup serially (important for fully parallel Playwright config)
setup.describe.configure({ mode: 'serial' })

setup('global setup', async ({}) => {
  await clerkSetup()
})
```

**What This Does**:
- Obtains Testing Token from Clerk Backend API
- Stores token in `CLERK_TESTING_TOKEN` environment variable
- Makes token available for all tests

### Use in Tests

Import `setupClerkTestingToken()` and call before navigating to auth pages:

**File**: `auth.spec.ts`

```typescript
import { setupClerkTestingToken } from '@clerk/testing/playwright'
import { test, expect } from '@playwright/test'

test('sign up flow', async ({ page }) => {
  // Inject Testing Token for this test
  await setupClerkTestingToken({ page })

  // Navigate to sign-up page
  await page.goto('/sign-up')

  // Fill form with test credentials
  await page.fill('input[name="emailAddress"]', 'test+clerk_test@example.com')
  await page.fill('input[name="password"]', 'TestPassword123!')
  await page.click('button[type="submit"]')

  // Verify with fixed OTP
  await page.fill('input[name="code"]', '424242')
  await page.click('button[type="submit"]')

  // Assert success
  await expect(page).toHaveURL('/dashboard')
})

test('sign in with test phone', async ({ page }) => {
  await setupClerkTestingToken({ page })

  await page.goto('/sign-in')
  await page.fill('input[name="identifier"]', '+12015550100')
  await page.click('button[type="submit"]')

  // Enter fixed OTP
  await page.fill('input[name="code"]', '424242')
  await page.click('button[type="submit"]')

  await expect(page).toHaveURL('/dashboard')
})
```

### Manual Testing Token Setup (Alternative)

Instead of `clerkSetup()`, manually set the environment variable:

```bash
export CLERK_TESTING_TOKEN="1713877200-c_2J2MvPu9PnXcuhbPZNao0LOXqK9A7YrnBn0HmIWxy"
```

Then run tests as usual. `setupClerkTestingToken()` will use this value.

### Demo Repository

Clerk provides a complete example:

**Repository**: https://github.com/clerk/clerk-playwright-nextjs

**Features**:
- Next.js App Router with Clerk
- Playwright E2E tests
- Testing Tokens setup
- Test user authentication

**To Run**:
1. Clone repo
2. Add Clerk API keys to `.env.local`
3. Create test user with username + password
4. Enable username/password auth in Clerk Dashboard
5. Run `npm test`

---

## Testing Email Links (Magic Links)

Email links are challenging to test in E2E suites.

**Recommendation**: Use email verification codes instead.

### Enable Email Verification Code

1. Clerk Dashboard → **Email, Phone, Username**
2. Enable **Email verification code** strategy
3. Use the code flow in tests (easier to automate)

**Code flow** and **link flow** are functionally equivalent for most use cases.

---

## Best Practices

### Development Testing

✅ **Do**:
- Use test emails (`+clerk_test`) and phone numbers (555-01XX)
- Fixed OTP: `424242`
- Enable test mode in Clerk Dashboard
- Use `@clerk/testing` for Playwright/Cypress

❌ **Don't**:
- Send real emails/SMS during tests (wastes quota)
- Use production keys in tests
- Enable test mode on production instances with real users

### Backend/API Testing

✅ **Do**:
- Generate session tokens via Backend API
- Refresh tokens before each test or on interval
- Use test users created via API
- Store `CLERK_SECRET_KEY` securely

❌ **Don't**:
- Hardcode session tokens (expire in 60 seconds)
- Reuse expired tokens
- Expose secret keys in logs or version control

### E2E Testing

✅ **Do**:
- Use `@clerk/testing` for automatic Testing Token management
- Configure global setup for token generation
- Use test credentials in all flows
- Run tests in CI/CD with secret environment variables

❌ **Don't**:
- Skip `setupClerkTestingToken()` (triggers bot detection)
- Manually implement Testing Token logic (use helpers)
- Test code-based auth in production with Testing Tokens

---

## Troubleshooting

### "Bot traffic detected" Error

**Cause**: Missing Testing Token in test suite

**Solution**:
1. Install `@clerk/testing`
2. Configure `clerkSetup()` in global setup
3. Call `setupClerkTestingToken({ page })` in tests

### Session Token Expired

**Cause**: Token lifetime is 60 seconds

**Solution**:
- Refresh token before each test: `beforeEach(() => refreshToken())`
- Use interval timer: `setInterval(() => refreshToken(), 50000)`

### Test Email Not Working

**Cause**: Test mode not enabled, or wrong email format

**Solution**:
- Ensure email has `+clerk_test` subaddress
- Enable test mode in Clerk Dashboard
- Use fixed OTP: `424242`

### 20 SMS / 100 Email Limit Reached

**Cause**: Exceeded monthly limit for development instance

**Solution**:
- Use test credentials (excluded from limits)
- Contact Clerk support to request higher limits
- Use self-delivered SMS/email provider

---

## Reference Links

**Official Docs**:
- Testing Overview: https://clerk.com/docs/guides/development/testing/overview
- Test Emails & Phones: https://clerk.com/docs/guides/development/testing/test-emails-and-phones
- Playwright Integration: https://clerk.com/docs/guides/development/testing/playwright/overview
- Backend API Reference: https://clerk.com/docs/reference/backend-api

**Packages**:
- `@clerk/testing`: https://github.com/clerk/javascript/tree/main/packages/testing
- Demo Repository: https://github.com/clerk/clerk-playwright-nextjs

**API Endpoints**:
- Create User: `POST /v1/users`
- Create Session: `POST /v1/sessions`
- Create Session Token: `POST /v1/sessions/{session_id}/tokens`
- Create Testing Token: `POST /v1/testing_tokens`

---

**Last Updated**: 2025-10-28
