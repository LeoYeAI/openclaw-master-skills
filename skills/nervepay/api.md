# NervePay API Reference

**Base URL:** `https://api.nervepay.xyz/v1`

## Authentication

Most endpoints require Ed25519 signature authentication via headers:

| Header | Description |
|--------|-------------|
| `Agent-DID` | Your DID (e.g., `did:nervepay:agent:abc123`) |
| `X-Agent-Signature` | Base64-encoded Ed25519 signature |
| `X-Agent-Nonce` | Unique nonce (UUID recommended) |
| `X-Signature-Timestamp` | ISO 8601 timestamp |

## Signature Payload Format

Sign a JSON object containing:

```json
{
  "method": "GET",
  "path": "/v1/agent-identity/whoami",
  "query": "param=value",
  "body": "sha256_hash_of_body_or_null",
  "nonce": "unique-nonce-uuid",
  "timestamp": "2026-02-05T12:00:00Z",
  "agent_did": "did:nervepay:agent:abc123"
}
```

Use the `nervepay-request.mjs` script to handle signing automatically.

## Endpoints

### Agent Registration

#### POST `/agent-identity/register`
**Auth:** JWT (human-initiated)

Create an agent identity through the dashboard.

**Request:**
```json
{
  "name": "My Agent",
  "description": "What it does"
}
```

**Response (201):**
```json
{
  "did": "did:nervepay:agent:abc123",
  "private_key": "ed25519:5Kd7...",
  "mnemonic": "word1 word2 ... word24",
  "public_key": "ed25519:...",
  "name": "My Agent"
}
```

#### POST `/agent-identity/register-pending`
**Auth:** None (agent-initiated)

Agent bootstraps its own identity. Credentials returned immediately, human claims ownership later.

**Request:**
```json
{
  "name": "My Agent",
  "description": "What it does"
}
```

**Response (201):**
```json
{
  "did": "did:nervepay:agent:abc123",
  "private_key": "ed25519:5Kd7...",
  "mnemonic": "word1 word2 ... word24",
  "public_key": "ed25519:...",
  "session_id": "a1b2c3d4",
  "claim_url": "https://nervepay.xyz/claim/a1b2c3d4",
  "expires_at": "2026-02-05T12:00:00Z",
  "status": "pending"
}
```

#### GET `/agent-identity/register-pending/{sessionId}/status`
**Auth:** None

Poll registration status.

**Response:**
```json
{
  "did": "did:nervepay:agent:abc123",
  "session_id": "a1b2c3d4",
  "status": "claimed|pending|expired|revoked",
  "expires_at": "2026-02-05T12:00:00Z",
  "created_at": "2026-02-04T12:00:00Z",
  "claimed_at": "2026-02-04T12:05:00Z"
}
```

#### POST `/agent-identity/claim/{sessionId}`
**Auth:** JWT (human)

Human claims pending agent.

**Response:**
```json
{
  "did": "did:nervepay:agent:abc123",
  "claimed": true,
  "message": "Agent successfully claimed"
}
```

#### POST `/agent-identity/recover`
**Auth:** JWT

Recover private key from mnemonic.

**Request:**
```json
{
  "mnemonic": "word1 word2 ... word24"
}
```

**Response:**
```json
{
  "did": "did:nervepay:agent:abc123",
  "private_key": "ed25519:5Kd7...",
  "recovered": true
}
```

### Agent Authentication

#### GET `/agent-identity/whoami`
**Auth:** Signature

Test authentication.

**Response:**
```json
{
  "did": "did:nervepay:agent:abc123",
  "name": "My Agent",
  "reputation_score": 75.5,
  "authenticated_via": "Ed25519 signature",
  "message": "Successfully authenticated as My Agent"
}
```

#### GET `/agent-identity/capabilities`
**Auth:** Signature

Get your capabilities and permissions.

**Response:**
```json
{
  "did": "did:nervepay:agent:abc123",
  "capabilities": {
    "payments": {
      "max_per_transaction": "100.00",
      "daily_limit": "1000.00",
      "currency": "USDC",
      "network": "base"
    },
    "operations": ["payments:initiate", "endpoints:call"]
  }
}
```

### Service Tracking

#### POST `/agent-identity/track-service`
**Auth:** Signature

Report external service usage. Call this after EVERY external API call to build reputation.

**Request:**
```json
{
  "service_name": "openai",
  "endpoint": "/v1/chat/completions",
  "method": "POST",
  "success": true,
  "response_time_ms": 1250,
  "amount": "0.05",
  "currency": "USD",
  "metadata": {
    "model": "gpt-4",
    "tokens": 1500
  }
}
```

**Response:**
```json
{
  "tracked": true,
  "message": "External service call to openai tracked",
  "service_name": "openai",
  "endpoint": "/v1/chat/completions",
  "agent_did": "did:nervepay:agent:abc123"
}
```

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `service_name` | string | Yes | Name of the service (openai, stripe, github, etc.) |
| `endpoint` | string | Yes | API endpoint path |
| `method` | string | No | HTTP method (default: GET) |
| `success` | boolean | Yes | Whether the call succeeded |
| `response_time_ms` | integer | No | Response time in milliseconds |
| `amount` | string | No | Cost of the API call |
| `currency` | string | No | Currency (default: USD) |
| `metadata` | object | No | Additional context (model, tokens, etc.) |

### Public Verification

#### GET `/agent-identity/verify/{did}`
**Auth:** None

Verify an agent's public profile. Anyone can call this.

**Response:**
```json
{
  "did": "did:nervepay:agent:abc123",
  "verified": true,
  "human_owner": true,
  "profile": {
    "name": "My Agent",
    "description": "What it does",
    "public_key": "ed25519:...",
    "reputation_score": 75.5,
    "total_transactions": 150,
    "successful_transactions": 148,
    "created_at": "2026-02-01T00:00:00Z"
  }
}
```

### DID Resolution

#### GET `/did/resolve/{did}`
**Auth:** None

Get W3C DID Document.

**Response:**
```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/ed25519-2020/v1"
  ],
  "id": "did:nervepay:agent:abc123",
  "verificationMethod": [{
    "id": "did:nervepay:agent:abc123#key-1",
    "type": "Ed25519VerificationKey2020",
    "controller": "did:nervepay:agent:abc123",
    "publicKeyBase58": "..."
  }],
  "authentication": ["did:nervepay:agent:abc123#key-1"],
  "capabilities": {
    "payments": {
      "max_per_transaction": "100.00",
      "daily_limit": "1000.00",
      "currency": "USDC",
      "network": "base"
    },
    "operations": ["payments:initiate", "endpoints:call"]
  },
  "reputation_score": 75.5
}
```

## Error Codes

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 400 | Bad Request | Invalid or missing fields, malformed JSON |
| 401 | Unauthorized | Invalid signature, expired timestamp, used nonce |
| 404 | Not Found | Agent or registration doesn't exist |
| 409 | Conflict | Agent already exists, registration already claimed |
| 410 | Gone | Registration expired or revoked |
| 429 | Rate Limited | Too many requests |
| 500 | Server Error | Internal error |

## Rate Limits

- Registration: 10 per hour per IP
- Authentication: 100 per minute per agent
- Track-service: 1000 per hour per agent
- Public endpoints: 100 per minute per IP

## Timestamp Requirements

- Must be ISO 8601 format (e.g., `2026-02-05T12:00:00Z`)
- Must be within 5 minutes of server time
- Server uses UTC

## Nonce Requirements

- Must be unique (never reused)
- UUID v4 recommended
- Server stores nonces for 5 minutes
- Replay attack protection

## Example: Full Authentication Flow

```bash
# 1. Register
RESPONSE=$(curl -s -X POST https://api.nervepay.xyz/v1/agent-identity/register-pending \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Agent","description":"Testing"}')

# 2. Extract credentials
export NERVEPAY_DID=$(echo "$RESPONSE" | jq -r '.did')
export NERVEPAY_PRIVATE_KEY=$(echo "$RESPONSE" | jq -r '.private_key')
export NERVEPAY_API_URL="https://api.nervepay.xyz"

# 3. Test authentication
node nervepay-skill/nervepay-request.mjs GET /v1/agent-identity/whoami

# 4. Track external API usage
node nervepay-skill/nervepay-request.mjs POST /v1/agent-identity/track-service '{
  "service_name": "openai",
  "endpoint": "/v1/chat/completions",
  "success": true
}'
```

## Need Help?

- **API Base:** https://api.nervepay.xyz/v1
- **Docs:** https://nervepay.xyz/docs
- **GitHub:** https://github.com/nervepay/nervepay
- **Issues:** https://github.com/nervepay/nervepay/issues
