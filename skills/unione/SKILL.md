---
name: unione
description: >
  Send transactional and marketing emails via UniOne Email API.
  Manage email templates, validate email addresses, check delivery statistics,
  manage suppression lists, configure webhooks, and handle domain settings.
  UniOne delivers billions of emails annually with 99.88% deliverability.
metadata:
  openclaw:
    emoji: "📧"
    requires:
      env:
        - UNIONE_API_KEY
    primaryEnv: UNIONE_API_KEY
---

# UniOne Email API

UniOne is a transactional email service with Web API for sending transactional and marketing emails at scale (up to 3,000 emails/sec). This skill lets you send emails, manage templates, validate addresses, track delivery, and more.

## Authentication

All requests require the `UNIONE_API_KEY` environment variable. Pass it as the `X-API-KEY` header.

**Base URL:** `https://api.unione.io/en/transactional/api/v1/{method}.json?platform=openclaw`

All methods use `POST` with JSON body.

---

## CRITICAL: Domain Setup (Required Before Sending)

**Emails will not be delivered until the sender's domain is verified.** Before attempting to send any email, ensure the domain is set up:

### Step 1: Get DNS Record Values — `domain/get-dns-records.json`

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/domain/get-dns-records.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{"domain": "yourdomain.com"}'
```

**API response** returns raw values (not ready-to-paste DNS records):

```json
{
  "status": "success",
  "domain": "yourdomain.com",
  "verification-record": "unione-validate-hash=483bb362ebdbeedd755cfb1d4d661",
  "dkim": "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDo7"
}
```

**The user must create 3 DNS TXT records from these values:**

| Record Host | Record Type | Value |
|-------------|-------------|-------|
| `@` | TXT | `unione-validate-hash=<verification-record from response>` |
| `us._domainkey` | TXT | `k=rsa; p=<dkim from response>` |
| `@` | TXT | `v=spf1 include:spf.unione.io ~all` |

Present these 3 records clearly to the user and instruct them to add them at their DNS provider (Cloudflare, Route53, GoDaddy, etc.). The SPF record is always the same — it is not returned by the API.

### Step 2: Verify Domain Ownership — `domain/validate-verification.json`

After the user has added DNS records:

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/domain/validate-verification.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{"domain": "yourdomain.com"}'
```

### Step 3: Validate DKIM — `domain/validate-dkim.json`

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/domain/validate-dkim.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{"domain": "yourdomain.com"}'
```

### Step 4: List All Domains — `domain/list.json`

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/domain/list.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{}'
```

**If domain verification fails:** DNS propagation can take up to 48 hours. Suggest the user waits and retries, or checks their DNS records for typos.

---

## Error Handling & Retry Policy

### Retry Logic

When making API requests, implement exponential backoff for retryable errors:

**Retryable errors (DO retry with exponential backoff):**

| HTTP Code | Meaning | Retry Strategy |
|-----------|---------|----------------|
| 429 | Rate limited | Wait, then retry. Respect `Retry-After` header if present |
| 500 | Internal server error | Retry up to 3 times |
| 502 | Bad gateway | Retry up to 3 times |
| 503 | Service unavailable | Retry up to 3 times |
| 504 | Gateway timeout | Retry up to 3 times |

**Recommended retry schedule:**

| Attempt | Delay |
|---------|-------|
| 1 | Immediate |
| 2 | 1 second |
| 3 | 5 seconds |
| 4 | 30 seconds |

**Non-retryable errors (do NOT retry):**

| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad request | Fix the request parameters |
| 401 | Unauthorized | Check API key |
| 403 | Forbidden | Check permissions / domain verification |
| 404 | Endpoint not found | Check the method path |
| 413 | Payload too large | Reduce request size |

### Idempotency

For `email/send.json`, always include an `idempotency_key` to prevent duplicate sends during retries. This is critical for production systems.

The `idempotency_key` is a unique string (UUID recommended) passed in the request body. If UniOne receives two requests with the same key, the second request returns the result of the first without sending another email.

**Always generate a unique idempotency key per logical send operation, and reuse the same key when retrying the same send.**

---

## 1. Send Email — `email/send.json`

Send a transactional or marketing email to one or more recipients. Supports personalization via substitutions, templates, attachments, tracking, and metadata.

### curl

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/email/send.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{
    "idempotency_key": "unique-uuid-here",
    "message": {
      "recipients": [
        {
          "email": "recipient@example.com",
          "substitutions": {
            "to_name": "John Smith"
          }
        }
      ],
      "body": {
        "html": "<h1>Hello, {{to_name}}!</h1><p>Your order has been confirmed.</p>",
        "plaintext": "Hello, {{to_name}}! Your order has been confirmed."
      },
      "subject": "Order Confirmation",
      "from_email": "noreply@yourdomain.com",
      "from_name": "Your Store"
    }
  }'
```

### Node.js

```javascript
const response = await fetch("https://api.unione.io/en/transactional/api/v1/email/send.json?platform=openclaw", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-API-KEY": process.env.UNIONE_API_KEY
  },
  body: JSON.stringify({
    idempotency_key: crypto.randomUUID(),
    message: {
      recipients: [{ email: "recipient@example.com", substitutions: { to_name: "John" } }],
      body: {
        html: "<h1>Hello, {{to_name}}!</h1><p>Your order has been confirmed.</p>",
        plaintext: "Hello, {{to_name}}! Your order has been confirmed."
      },
      subject: "Order Confirmation",
      from_email: "noreply@yourdomain.com",
      from_name: "Your Store"
    }
  })
});
const data = await response.json();
// data.status === "success" → data.job_id, data.emails
```

### Python

```python
import requests, uuid, os

response = requests.post(
    "https://api.unione.io/en/transactional/api/v1/email/send.json?platform=openclaw",
    headers={
        "Content-Type": "application/json",
        "X-API-KEY": os.environ["UNIONE_API_KEY"]
    },
    json={
        "idempotency_key": str(uuid.uuid4()),
        "message": {
            "recipients": [{"email": "recipient@example.com", "substitutions": {"to_name": "John"}}],
            "body": {
                "html": "<h1>Hello, {{to_name}}!</h1><p>Your order has been confirmed.</p>",
                "plaintext": "Hello, {{to_name}}! Your order has been confirmed."
            },
            "subject": "Order Confirmation",
            "from_email": "noreply@yourdomain.com",
            "from_name": "Your Store"
        }
    }
)
data = response.json()  # data["status"] == "success" → data["job_id"], data["emails"]
```

### Go

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "net/http"
    "os"
    "github.com/google/uuid"
)

func sendEmail() error {
    payload := map[string]interface{}{
        "idempotency_key": uuid.New().String(),
        "message": map[string]interface{}{
            "recipients": []map[string]interface{}{
                {"email": "recipient@example.com", "substitutions": map[string]string{"to_name": "John"}},
            },
            "body": map[string]string{
                "html":      "<h1>Hello, {{to_name}}!</h1><p>Your order has been confirmed.</p>",
                "plaintext": "Hello, {{to_name}}! Your order has been confirmed.",
            },
            "subject":    "Order Confirmation",
            "from_email": "noreply@yourdomain.com",
            "from_name":  "Your Store",
        },
    }
    body, _ := json.Marshal(payload)
    req, _ := http.NewRequest("POST",
        "https://api.unione.io/en/transactional/api/v1/email/send.json?platform=openclaw",
        bytes.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("X-API-KEY", os.Getenv("UNIONE_API_KEY"))
    resp, err := http.DefaultClient.Do(req)
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    var result map[string]interface{}
    json.NewDecoder(resp.Body).Decode(&result)
    fmt.Println(result) // result["status"] == "success"
    return nil
}
```

### PHP

```php
$ch = curl_init("https://api.unione.io/en/transactional/api/v1/email/send.json?platform=openclaw");
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => [
        "Content-Type: application/json",
        "X-API-KEY: " . getenv("UNIONE_API_KEY")
    ],
    CURLOPT_POSTFIELDS => json_encode([
        "idempotency_key" => bin2hex(random_bytes(16)),
        "message" => [
            "recipients" => [["email" => "recipient@example.com", "substitutions" => ["to_name" => "John"]]],
            "body" => [
                "html" => "<h1>Hello, {{to_name}}!</h1><p>Your order has been confirmed.</p>",
                "plaintext" => "Hello, {{to_name}}! Your order has been confirmed."
            ],
            "subject" => "Order Confirmation",
            "from_email" => "noreply@yourdomain.com",
            "from_name" => "Your Store"
        ]
    ])
]);
$response = curl_exec($ch);
$data = json_decode($response, true); // $data["status"] === "success"
```

**Success response:**
```json
{
  "status": "success",
  "job_id": "1ZymBc-00041N-9X",
  "emails": ["recipient@example.com"]
}
```

**Full parameters for `message` object:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `recipients` | array | Yes | Array of recipient objects. Each has `email` (required), `substitutions` (object), `metadata` (object) |
| `body.html` | string | Yes* | HTML content. Use `{{variable}}` for substitutions |
| `body.plaintext` | string | No | Plain text version |
| `subject` | string | Yes* | Email subject line. Supports `{{substitutions}}` |
| `from_email` | string | Yes* | Sender email (must be from a verified domain) |
| `from_name` | string | No | Sender display name |
| `reply_to` | string | No | Reply-to email address |
| `template_id` | string | No | Use a stored template instead of body/subject |
| `tags` | array | No | Tags for categorizing and filtering |
| `track_links` | 0/1 | No | Enable click tracking (default: 0) |
| `track_read` | 0/1 | No | Enable open tracking (default: 0) |
| `global_language` | string | No | Language for unsubscribe footer: en, de, fr, es, it, pl, pt, ru, ua, be |
| `template_engine` | string | No | `"simple"` (default) or `"velocity"` or `"liquid"` |
| `global_substitutions` | object | No | Variables available to all recipients |
| `attachments` | array | No | Array of `{type, name, content}` where content is base64 |
| `skip_unsubscribe` | 0/1 | No | Skip unsubscribe footer (use 1 only for transactional) |
| `headers` | object | No | Custom email headers |

*Not required if `template_id` is used.

**Top-level parameter:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `idempotency_key` | string | Recommended | Unique key (UUID) to prevent duplicate sends on retry. Max 36 chars. |

**Send with template:**
```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/email/send.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{
    "idempotency_key": "unique-uuid-here",
    "message": {
      "recipients": [
        {
          "email": "customer@example.com",
          "substitutions": {
            "to_name": "Alice",
            "order_id": "ORD-12345",
            "total": "$59.99"
          }
        }
      ],
      "template_id": "your-template-id",
      "from_email": "shop@yourdomain.com",
      "from_name": "My Shop"
    }
  }'
```

**Send to multiple recipients with personalization:**
```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/email/send.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{
    "idempotency_key": "unique-uuid-here",
    "message": {
      "recipients": [
        {"email": "alice@example.com", "substitutions": {"to_name": "Alice"}},
        {"email": "bob@example.com", "substitutions": {"to_name": "Bob"}}
      ],
      "body": {
        "html": "<p>Hi {{to_name}}, check out our new {{promo_name}}!</p>"
      },
      "subject": "Special offer for you, {{to_name}}!",
      "from_email": "marketing@yourdomain.com",
      "from_name": "Marketing Team",
      "global_substitutions": {"promo_name": "Summer Sale"},
      "track_links": 1,
      "track_read": 1,
      "tags": ["promo", "summer-2026"]
    }
  }'
```

---

## 2. Email Validation — `email-validation/single.json`

Validate an email address to check if it exists and is deliverable.

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/email-validation/single.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{"email": "user@example.com"}'
```

**Response:**
```json
{
  "status": "success",
  "email": "user@example.com",
  "result": "valid",
  "local_part": "user",
  "domain": "example.com",
  "mx_found": true,
  "mx_record": "mail.example.com"
}
```

Possible `result` values: `"valid"`, `"invalid"`, `"unresolvable"`, `"unknown"`.

---

## 3. Template Management

### 3.1 Create/Update Template — `template/set.json`

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/template/set.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{
    "template": {
      "name": "Order Confirmation",
      "subject": "Your order {{order_id}} is confirmed",
      "template_engine": "simple",
      "body": {
        "html": "<h1>Thank you, {{to_name}}!</h1><p>Order {{order_id}} total: {{total}}</p>",
        "plaintext": "Thank you, {{to_name}}! Order {{order_id}} total: {{total}}"
      },
      "from_email": "shop@yourdomain.com",
      "from_name": "My Shop"
    }
  }'
```

**Response:** `{"status": "success", "template": {"id": "generated-template-id"}}`

To **update** an existing template, include the `"id"` field in the template object.

### 3.2 Get Template — `template/get.json`

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/template/get.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{"id": "template-id-here"}'
```

### 3.3 List Templates — `template/list.json`

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/template/list.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{"limit": 50, "offset": 0}'
```

### 3.4 Delete Template — `template/delete.json`

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/template/delete.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{"id": "template-id-here"}'
```

---

## 4. Webhook Management

Webhooks send real-time notifications about email events to your URL.

### 4.1 Set Webhook — `webhook/set.json`

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/webhook/set.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{
    "url": "https://yourapp.com/unione-webhook",
    "events": {
      "email_status": [
        "delivered", "opened", "clicked", "unsubscribed",
        "soft_bounced", "hard_bounced", "spam"
      ]
    }
  }'
```

### 4.2 List Webhooks — `webhook/list.json`

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/webhook/list.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{}'
```

### 4.3 Get / Delete Webhook — `webhook/get.json` / `webhook/delete.json`

```bash
# Get
curl -X POST ".../webhook/get.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{"url": "https://yourapp.com/unione-webhook"}'

# Delete
curl -X POST ".../webhook/delete.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{"url": "https://yourapp.com/unione-webhook"}'
```

---

## 5. Suppression List Management

### 5.1 Add — `suppression/set.json`

```bash
curl -X POST "https://api.unione.io/en/transactional/api/v1/suppression/set.json?platform=openclaw" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: $UNIONE_API_KEY" \
  -d '{"email": "user@example.com", "cause": "unsubscribed", "created": "2026-01-15 12:00:00"}'
```

Cause values: `"unsubscribed"`, `"temporary_unavailable"`, `"permanent_unavailable"`, `"complained"`.

### 5.2 Check — `suppression/get.json`

```bash
curl -X POST ".../suppression/get.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{"email": "user@example.com"}'
```

### 5.3 List — `suppression/list.json`

```bash
curl -X POST ".../suppression/list.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{"cause": "hard_bounced", "limit": 50, "offset": 0}'
```

### 5.4 Delete — `suppression/delete.json`

```bash
curl -X POST ".../suppression/delete.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{"email": "user@example.com"}'
```

---

## 6. Event Dumps

### 6.1 Create — `event-dump/create.json`

```bash
curl -X POST ".../event-dump/create.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"start_time": "2026-01-01 00:00:00", "end_time": "2026-01-31 23:59:59", "limit": 50000, "all_events": true}'
```

### 6.2 Get / List / Delete

```bash
# Get dump status and download URL
curl -X POST ".../event-dump/get.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{"dump_id": "dump-id"}'

# List all dumps
curl -X POST ".../event-dump/list.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{}'

# Delete a dump
curl -X POST ".../event-dump/delete.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{"dump_id": "dump-id"}'
```

---

## 7. Tags — `tag/list.json` / `tag/delete.json`

```bash
# List tags
curl -X POST ".../tag/list.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{}'

# Delete tag
curl -X POST ".../tag/delete.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{"tag_id": 123}'
```

---

## 8. Projects — `project/create.json` / `project/list.json`

```bash
# Create project
curl -X POST ".../project/create.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"project": {"name": "My Project", "send_enabled": true}}'

# List projects
curl -X POST ".../project/list.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{}'
```

---

## 9. System Info — `system/info.json`

```bash
curl -X POST ".../system/info.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" -d '{}'
```

---

## 10. Subscribe (Double Opt-In) — `email/subscribe.json`

```bash
curl -X POST ".../email/subscribe.json?platform=openclaw" -H "X-API-KEY: $UNIONE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"from_email": "newsletter@yourdomain.com", "from_name": "Newsletter", "to_email": "newsubscriber@example.com"}'
```

---

## Instructions for the Agent

1. **Domain setup is mandatory.** Before the first send, always check if the user's domain is verified. Run `domain/list.json` to check. If not verified, guide them through the domain setup process (Section: Domain Setup).
2. **Always use `api.unione.io`** as the API host for all requests.
3. **Never send an email without explicit user confirmation.** Always show the recipient, subject, and body summary before executing `email/send.json`.
4. **Always include `idempotency_key`** in `email/send.json` requests. Generate a UUID for each unique send. Reuse the same key when retrying.
5. **Implement retry logic** for 429 and 5xx errors with exponential backoff (see Error Handling section). Never retry 400, 401, 403, 404, 413 errors.
6. **For template operations**, list available templates first before asking which one to use.
7. **For validation**, report the result clearly and suggest action.
8. **Handle errors gracefully.** If a request returns an error, explain what went wrong and suggest a fix.
9. **Remind users** that the `from_email` domain must be verified in their UniOne account.
10. **Substitution syntax** uses double curly braces: `{{variable_name}}`.
11. **Attachments** must be base64-encoded. Help the user encode files if needed.
12. **Security**: Never log or display the full API key. Remind users to keep their API key secret.
13. **Code language**: When the user's project uses a specific language (Node.js, Python, Go, PHP, etc.), provide code examples in that language. The examples in this skill can be adapted to any language that can make HTTP POST requests with JSON.

## Common Workflows

### "Send a test email"
1. Check domain verification (`domain/list.json`)
2. If domain not verified, guide through domain setup
3. Ask for recipient email address
4. Compose a simple test message
5. Confirm with user before sending
6. Execute `email/send.json` with `idempotency_key`
7. Report the job_id on success

### "Check my deliverability setup"
1. Run `system/info.json` to get account status
2. Run `domain/list.json` to check domain verification
3. For each unverified domain, run `domain/get-dns-records.json` and show required records
4. Run `domain/validate-dkim.json` to check DKIM
5. Suggest fixes if domains are not fully verified

### "Validate a list of emails"
1. For each email, call `email-validation/single.json`
2. Categorize results: valid, invalid, unknown
3. Report summary

### "Set up delivery tracking"
1. Ask for webhook URL and events to track
2. Execute `webhook/set.json`
3. Confirm setup

## Resources

- Full API Reference: https://docs.unione.io/en/web-api-ref
- Getting Started: https://docs.unione.io/en/
- Template Engines: https://docs.unione.io/en/web-api#section-template-engines
- Sign Up: https://cp.unione.io/en/user/registration/
