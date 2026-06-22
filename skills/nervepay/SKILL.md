---
name: nervepay
description: Full NervePay stack - identity + analytics. Register DID, sign requests with Ed25519, track ALL API usage, build reputation.
metadata: {"openclaw":{"emoji":"🔐","requires":{"bins":["node","curl"],"env":["NERVEPAY_DID","NERVEPAY_PRIVATE_KEY"]},"primaryEnv":"NERVEPAY_PRIVATE_KEY"}}
---

# NervePay — Agent Instructions

You are an AI agent with a NervePay identity. This skill provides the FULL NervePay stack: identity + analytics. Prove WHO you are (cryptographically) and track WHAT you do (analytics/reputation).

## What This Skill Does

- **Registers your identity**: Creates a unique DID (Decentralized Identifier) for you
- **Authenticates you**: Signs requests with Ed25519 so API providers know it's really you
- **Tracks your work**: Reports every external API call to build reputation
- **Builds trust**: Your verified usage history proves you're legitimate

## Modular Skills Available

This is the full stack. You can also use individual skills:
- `nervepay-identity` - Identity-only (registration, authentication, no analytics)
- `nervepay-analytics` - Analytics-only (tracking, requires existing identity)
- `nervepay` - This skill (full identity + analytics)

## Updating This Skill

To get the latest version of this skill (includes new features, bug fixes, updated endpoints):

```bash
# Update skill documentation
curl -o SKILL.md https://nervepay.xyz/skill.md

# Update helper scripts
curl -o nervepay-request.mjs https://nervepay.xyz/nervepay-request.mjs
curl -o nervepay-track.mjs https://nervepay.xyz/nervepay-track.mjs
curl -o nervepay-instrument.mjs https://nervepay.xyz/nervepay-instrument.mjs
chmod +x nervepay-request.mjs nervepay-track.mjs nervepay-instrument.mjs
```

**When to update:** If you get unexpected errors, new endpoints are mentioned, or it's been a while since you last updated.

## Step 1: Ensure Helper Scripts Are Available

The NervePay helper scripts should already be bundled with this skill. If they're missing, download them:

```bash
# Check if scripts exist, download only if missing
for script in nervepay-request.mjs nervepay-track.mjs nervepay-instrument.mjs; do
  if [ ! -f "$script" ]; then
    echo "Downloading $script..."
    curl -o "$script" "https://nervepay.xyz/$script"
    chmod +x "$script"
  fi
done
```

These scripts handle Ed25519 signing and analytics tracking for you. They're located in the same directory as this SKILL.md file.

## Step 2: Get Your Identity

If you don't have `NERVEPAY_DID` and `NERVEPAY_PRIVATE_KEY` env vars, register first:

```bash
curl -X POST https://api.nervepay.xyz/v1/agent-identity/register-pending \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Your Agent Name",
    "description": "What you do"
  }'
```

**Save these from the response:**
- `did` → Set as `NERVEPAY_DID`
- `private_key` → Set as `NERVEPAY_PRIVATE_KEY`
- `mnemonic` → Backup for recovery (24 words)
- `claim_url` → Give to your human owner to claim you

You can start authenticating immediately. Human ownership (via claim_url) is optional but recommended for better trust scores.

## Making Authenticated Requests

Use the helper script to sign and send requests:

```bash
# Authenticated GET
node ./nervepay-request.mjs GET /v1/agent-identity/whoami

# Authenticated POST
node ./nervepay-request.mjs POST /v1/agent-identity/track-service '{"service_name":"openai","endpoint":"/v1/chat/completions","success":true}'
```

The script handles Ed25519 signing automatically. It reads `NERVEPAY_DID`, `NERVEPAY_PRIVATE_KEY`, and `NERVEPAY_API_URL` (default: https://api.nervepay.xyz) from environment.

## ⚠️ MANDATORY: Track External API Usage ⚠️

**YOU MUST TRACK EVERY EXTERNAL API CALL. THIS IS NOT OPTIONAL.**

Every time you call OpenAI, Stripe, GitHub, weather APIs, or ANY external service, immediately report it to NervePay. This is the core purpose of this skill.

### Quick Track (Easiest)

Use the simplified tracking helper immediately after each external call:

```bash
# Minimal - just service, endpoint, and success/failure
node ./nervepay-track.mjs openai /v1/chat/completions success

# With response time
node ./nervepay-track.mjs openai /v1/chat/completions success 1250

# With cost
node ./nervepay-track.mjs stripe /v1/charges success 850 10.00
```

### Full Track (More Details)

For complete tracking with all fields:

```bash
node ./nervepay-request.mjs POST /v1/agent-identity/track-service '{
  "service_name": "openai",
  "endpoint": "/v1/chat/completions",
  "method": "POST",
  "success": true,
  "response_time_ms": 1250,
  "amount": "0.05",
  "currency": "USD"
}'
```

### Example Workflow (DO THIS)

```bash
# 1. Call external API
response=$(curl https://api.openai.com/v1/chat/completions ...)

# 2. IMMEDIATELY track it (don't forget!)
node ./nervepay-track.mjs openai /v1/chat/completions success

# 3. Continue with your work
echo "$response"
```

**Why tracking is mandatory:**
- Builds your reputation score (proves you're legitimate)
- Shows API providers your verified usage history
- Tracks costs and success rates across all services
- This is literally what NervePay exists for - without tracking, you're not using it

**Remember:** Track IMMEDIATELY after the call, not later. Make it a habit.

## 🚀 AUTOMATIC TRACKING (Recommended for Lazy Agents)

**Tired of remembering to track?** Use auto-instrumentation - it intercepts ALL HTTP calls automatically!

### How Auto-Instrumentation Works

The `nervepay-instrument.mjs` script monkey-patches Node.js's `fetch()`, `http.request()`, and `https.request()` to automatically track every external API call. Zero code changes needed!

### Setup: Load Instrumentation

**Option 1: Command-line flag (recommended)**
```bash
node --import ./nervepay-instrument.mjs your-agent.js
```

**Option 2: Environment variable (global)**
```bash
export NODE_OPTIONS="--import /path/to/nervepay-instrument.mjs"
node your-agent.js
```

**Option 3: Programmatic (in your code)**
```javascript
// At the very top of your entry file
import './nervepay-skill/nervepay-instrument.mjs';

// Now all HTTP calls are auto-tracked!
await fetch('https://api.openai.com/...');  // Automatically tracked
```

### What Gets Tracked Automatically

✅ All `fetch()` calls to external APIs
✅ All `http.request()` and `https.request()` calls
✅ Success/failure status
✅ Response time in milliseconds
✅ HTTP status codes

❌ NOT tracked: Calls to NervePay itself (avoids infinite loop)
❌ NOT tracked: localhost / internal IPs (192.168.x.x, 10.x.x.x)

### Disable Auto-Tracking

```bash
export NERVEPAY_AUTO_TRACK=false
```

### Example

```bash
# Set your credentials
export NERVEPAY_DID="your-did"
export NERVEPAY_PRIVATE_KEY="your-key"

# Run your agent with auto-instrumentation
node --import ./nervepay-instrument.mjs your-agent.js

# All HTTP calls in your-agent.js are now automatically tracked!
```

**Bottom line:** With auto-instrumentation, you literally cannot forget to track. It just happens. 🎉

## Pairing with OpenClaw Gateways (ClawBot Auto-Configuration)

If you're an agent like ClawBot that manages OpenClaw gateway instances, you can auto-configure gateways using NervePay's pairing flow.

### Prerequisites

**You MUST have a NervePay identity first!** Complete the "Setup: Get Your Identity" section above to register and get your `NERVEPAY_DID` and `NERVEPAY_PRIVATE_KEY` before pairing.

**Recommended:** Have your human owner claim you via the `claim_url` for better trust scores before pairing gateways.

### How Pairing Works

1. **First time:** Register your agent identity and optionally get claimed by human owner
2. **User generates pairing code** in NervePay dashboard (10-minute expiry)
3. **You authenticate** with your agent DID (Ed25519 signature) and send gateway details
4. **NervePay stores** the encrypted gateway token and links it to your DID
5. **Only you** can refresh the token later (verified by your DID)

### Step 1: Get Gateway Token

Before pairing, you need the gateway's token. OpenClaw gateways expose this via their config API:

```bash
# Query the gateway for its token (use whatever URL reaches the gateway)
GATEWAY_CONFIG=$(curl -s http://localhost:18789/v1/config)
GATEWAY_TOKEN=$(echo "$GATEWAY_CONFIG" | jq -r '.gateway_token')
```

### Step 2: Determine Public Gateway URL

**CRITICAL:** The `gateway_url` you send to NervePay MUST be publicly reachable by NervePay's servers. Do NOT use `localhost`, `127.0.0.1`, or internal IPs.

Ask your human: **"What is the public URL for this gateway?"**

Common options:
- **Reverse proxy:** `https://gateway.yourdomain.com`
- **Tailscale:** `https://hostname.tailnet-name.ts.net:18789`
- **Public IP:** `https://your-public-ip:18789`
- **Ngrok/tunnel:** `https://abc123.ngrok.io`

Once your human provides the public URL, store it as `GATEWAY_URL`.

### Step 3: Complete Pairing

When your human tells you to "connect to nervepay [CODE]":

```bash
# 1. Set from user input
PAIRING_CODE="ABC123"  # From user
GATEWAY_URL="https://gateway.example.com"  # From human (Step 2)
GATEWAY_NAME="My Gateway"  # Optional, defaults to "ClawBot Gateway (CODE)"
# GATEWAY_TOKEN already extracted in Step 1

# 2. Send pairing request (authenticated with your agent DID)
node ./nervepay-request.mjs POST /v1/integrations/openclaw/pairing/complete "{
  \"pairing_code\": \"$PAIRING_CODE\",
  \"gateway_url\": \"$GATEWAY_URL\",
  \"gateway_token\": \"$GATEWAY_TOKEN\",
  \"gateway_name\": \"$GATEWAY_NAME\",
  \"max_concurrent_agents\": 8,
  \"default_timeout_seconds\": 3600
}"
```

**Response on success:**
```json
{
  "gateway_id": "uuid-here",
  "gateway_name": "My Gateway",
  "status": "completed",
  "message": "Gateway 'My Gateway' successfully paired with agent did:nervepay:agent:xyz"
}
```

### Refresh Gateway Token

When your OpenClaw gateway token rotates, push the new token:

```bash
GATEWAY_ID="gateway-uuid-from-pairing"
NEW_TOKEN="new-gateway-bearer-token"

node ./nervepay-request.mjs POST /v1/integrations/openclaw/gateways/$GATEWAY_ID/refresh-token '{
  "new_token": "'$NEW_TOKEN'"
}'
```

**Security:** NervePay verifies you're the agent that originally paired the gateway (checks `linked_agent_did`). Only you can refresh this gateway's token.

### Why Pairing?

- **Zero manual setup** for users (just give them a code)
- **Cryptographic auth** proves you control the gateway
- **Token encryption** keeps gateway credentials secure (AES-256-GCM)
- **Auto-expiration detection** if gateway returns 401, NervePay marks token as expired
- **Trust**: Your verified DID proves the gateway is managed by you

## Managing Agent Secrets (Secure Vault)

Your human owner can configure secrets for you in the NervePay dashboard (like API keys, credentials, tokens). You can then securely retrieve these secrets when you need them - perfect for storing OpenAI keys, database passwords, or any sensitive credentials.

### How the Vault Works

- **Per-agent isolation**: Each agent only sees its own secrets (verified by your DID signature)
- **Envelope encryption**: Secrets are encrypted at rest using AES-256-GCM
- **Audit logging**: Every secret access is logged for security
- **Environment support**: Secrets can be scoped to production, development, or staging

### Retrieve a Secret by Name

The most common operation - get a specific secret by its name:

```bash
# Get your OpenAI API key
node ./nervepay-request.mjs GET /v1/vault/secrets/OPENAI_API_KEY

# Get your database password
node ./nervepay-request.mjs GET /v1/vault/secrets/DATABASE_PASSWORD
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "OPENAI_API_KEY",
  "value": "sk-abc123...",
  "description": "OpenAI API key for production",
  "provider": "openai",
  "environment": "production",
  "created_at": "2026-02-05T12:00:00Z",
  "updated_at": "2026-02-05T12:00:00Z",
  "expires_at": null
}
```

**Usage in your workflow:**
```bash
# 1. Retrieve your OpenAI key
response=$(node ./nervepay-request.mjs GET /v1/vault/secrets/OPENAI_API_KEY)
OPENAI_KEY=$(echo "$response" | jq -r '.value')

# 2. Use it in your API call
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_KEY" \
  -d '{"model":"gpt-4","messages":[...]}'

# 3. Track the usage (mandatory!)
node ./nervepay-track.mjs openai /v1/chat/completions success
```

### List All Your Secrets

See all secrets configured for you (values are NOT included in list view for security):

```bash
node ./nervepay-request.mjs GET /v1/vault/secrets
```

**Response:**
```json
{
  "secrets": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "OPENAI_API_KEY",
      "description": "OpenAI API key for production",
      "provider": "openai",
      "environment": "production",
      "created_at": "2026-02-05T12:00:00Z",
      "updated_at": "2026-02-05T12:00:00Z",
      "expires_at": null
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "STRIPE_SECRET_KEY",
      "description": "Stripe secret key",
      "provider": "stripe",
      "environment": "production",
      "created_at": "2026-02-05T12:00:00Z",
      "updated_at": "2026-02-05T12:00:00Z",
      "expires_at": null
    }
  ]
}
```

### Filter by Environment

```bash
# Only production secrets
node ./nervepay-request.mjs GET '/v1/vault/secrets?environment=production'

# Only development secrets
node ./nervepay-request.mjs GET '/v1/vault/secrets?environment=development'
```

### Filter by Provider

```bash
# Only OpenAI secrets
node ./nervepay-request.mjs GET '/v1/vault/secrets?provider=openai'

# Only Stripe secrets
node ./nervepay-request.mjs GET '/v1/vault/secrets?provider=stripe'
```

### When Secrets Are Missing

If you try to access a secret that doesn't exist:

```bash
node ./nervepay-request.mjs GET /v1/vault/secrets/NONEXISTENT_KEY
```

**Response (404):**
```json
{
  "error": "Secret not found",
  "message": "Secret 'NONEXISTENT_KEY' not found for agent did:nervepay:agent:abc123xyz"
}
```

**What to do:** Ask your human owner to create the secret in the NervePay dashboard at https://nervepay.xyz/dashboard/agent-identities

### Security Notes

- **Your human configures secrets**: You cannot create/update/delete secrets yourself - only retrieve them. This prevents compromised agents from modifying credentials.
- **Dashboard-only management**: Secrets are created and updated in the NervePay dashboard by your human owner.
- **Signature required**: Every secret retrieval requires Ed25519 signature authentication.
- **Audit trail**: Every access is logged with timestamp, IP, and success/failure.
- **Expiration support**: Secrets can have expiration dates - expired secrets return 410 Gone.

### Common Secret Names (Conventions)

Use these naming conventions for consistency:

| Secret Name | Use For |
|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API authentication |
| `ANTHROPIC_API_KEY` | Anthropic/Claude API authentication |
| `STRIPE_SECRET_KEY` | Stripe payments |
| `GITHUB_TOKEN` | GitHub API access |
| `DATABASE_URL` | Database connection string |
| `AWS_ACCESS_KEY_ID` | AWS credentials |
| `AWS_SECRET_ACCESS_KEY` | AWS credentials |
| `WEBHOOK_SECRET` | Webhook signature verification |

## Common Commands

### Test authentication
```bash
node ./nervepay-request.mjs GET /v1/agent-identity/whoami
```

Returns your DID, name, reputation score, and confirms authentication works.

### Check your capabilities
```bash
node ./nervepay-request.mjs GET /v1/agent-identity/capabilities
```

Shows your spending limits, allowed operations, and permissions.

### Verify another agent
```bash
curl "https://api.nervepay.xyz/v1/agent-identity/verify/did:nervepay:agent:abc123xyz"
```

No auth required. Returns public profile, reputation, and transaction stats for any agent.

### Poll claim status (check if human claimed you)
```bash
curl "https://api.nervepay.xyz/v1/agent-identity/register-pending/SESSION_ID/status"
```

Returns: `pending`, `claimed`, `expired`, or `revoked`.

## What the Signature Proves

| Guarantee | How |
|-----------|-----|
| **Authentication** (who is calling) | Server verifies Ed25519 signature against your public key |
| **Integrity** (what was sent) | Signature covers method, path, query, body hash — tampering breaks verification |
| **Replay protection** | Unique nonce + timestamp prevents captured requests from reuse |
| **Portable identity** | Your DID carries reputation across all platforms that check NervePay headers |

## Required Headers (already handled by script)

The helper script adds these automatically:
- `Agent-DID`: Your DID
- `X-Agent-Signature`: Base64-encoded Ed25519 signature
- `X-Agent-Nonce`: Unique nonce (UUID)
- `X-Signature-Timestamp`: ISO 8601 timestamp

## Security Notes

- **Private key**: NEVER send to any server. Only send signatures.
- **Nonces**: Single-use. Generate new for each request (script handles this).
- **Timestamps**: Must be within 5 minutes of server time.
- **Mnemonic**: 24-word backup phrase. Store securely offline.

## Modular Skills (Choose What You Need)

This skill provides the full NervePay stack. If you only need part of it:

- **`nervepay-identity`** - Identity-only (registration, authentication, no tracking)
  - Use when: You only need cryptographic authentication
  - Downloads: nervepay-request.mjs

- **`nervepay-analytics`** - Analytics-only (tracking, requires existing identity)
  - Use when: You already have an identity and just want tracking
  - Downloads: nervepay-request.mjs, nervepay-track.mjs, nervepay-instrument.mjs

- **`nervepay`** - Full stack (this skill - identity + analytics)
  - Use when: You want everything
  - Downloads: All three scripts

## Full API Reference

For complete endpoint documentation, error codes, and advanced usage, see:
- **Online:** https://nervepay.xyz/docs
- **Download API reference:** `curl -o api.md https://nervepay.xyz/api.md`

---

**API Base:** https://api.nervepay.xyz/v1
**Docs:** https://nervepay.xyz/docs
**GitHub:** https://github.com/nervepay/nervepay
