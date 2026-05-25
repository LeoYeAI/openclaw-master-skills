---
name: purposebot
description: "Agentic commerce with Stripe and x402 USDC payments. Discover tools, APIs, and WebMCP servers with trust scores. Create orders, escrow funds, settle payments on-chain or via Stripe Connect — the full agent transaction lifecycle."
version: v1.2.0
metadata:
  openclaw:
    requires:
      env:
        - PURPOSEBOT_API_KEY
        - PURPOSEBOT_REPORTER_AGENT_ID
        - PURPOSEBOT_JWKS_URL
        - PURPOSEBOT_SIGNING_KID
        - PURPOSEBOT_SIGNING_KEY_PEM
      bins:
        - curl
        - jq
        - python3
        - openssl
    primaryEnv: PURPOSEBOT_API_KEY
    emoji: "\U0001F4B0"
    homepage: https://purposebot.ai
---

# PurposeBot — Agentic Commerce, Payments & Trust

PurposeBot gives your agent a full commerce stack: discover tools and services, create orders, escrow funds via **Stripe** or **x402 (USDC on Base)**, verify fulfillment, settle payments, and build on-chain reputation — all through a single API.

**What you can do:**
- **Pay for things** — Stripe card payments or x402 USDC stablecoin, with escrow and dispute resolution
- **Sell things** — List services, receive payments via Stripe Connect or on-chain settlement
- **Discover tools** — Search WebMCP servers, MCP tools, API endpoints, and agent services with trust scoring
- **Build reputation** — Issue interaction contracts, report outcomes, accumulate trust scores

## API Basics

- **Base URL:** `https://api.purposebot.ai/v1`
- **Auth header:** `X-API-Key: $PURPOSEBOT_API_KEY`
- All responses are JSON.

## 0. Onboarding & Signing Prerequisites

Search and stats only require `PURPOSEBOT_API_KEY`.
Commerce orders, payment contracts, and interaction contracts require a **registered agent identity** with a signing key.

There are two onboarding paths: the **Dashboard flow** (recommended — fastest, keys hosted for you) and the **Manual CLI flow** (for headless agents that can't use a browser).

### Dashboard Flow (Recommended)

1. **Sign in** at [purposebot.ai](https://purposebot.ai) using Google or GitHub OAuth
2. Open **Trust Center** from the dashboard sidebar
3. Click **Create API Key** — choose an expiry (30 days, 90 days, 1 year, or no expiry). Copy the key immediately; it won't be shown again.
4. Click **Generate Signing Key** — PurposeBot generates an RS256 keypair, hosts the JWKS at a public URL, and registers your agent identity automatically. Copy the **private key PEM** and store it securely.
5. Your agent ID, key ID (kid), and JWKS URL are shown in the Trust Center. Set the environment variables:

```bash
export PURPOSEBOT_API_KEY="pb_live_..."
export PURPOSEBOT_REPORTER_AGENT_ID="<agent-id-from-trust-center>"
export PURPOSEBOT_JWKS_URL="https://api.purposebot.ai/v1/agents/keys/<kid>/jwks.json"
export PURPOSEBOT_SIGNING_KID="<kid-from-trust-center>"
export PURPOSEBOT_SIGNING_KEY_PEM="/path/to/agent_key.pem"
```

That's it — you're ready to sign contracts and make payments.

### Manual CLI Flow (Headless Agents)

Use this if your agent can't open a browser or you need fully programmatic setup.

#### Step 1: Get an API key

Create one from the PurposeBot dashboard, or use a bootstrap token if your operator provides one:

```bash
curl -s "https://api.purposebot.ai/v1/auth/agent-bootstrap" \
  -H "Content-Type: application/json" \
  -d '{"bootstrap_token": "<token>"}' | jq .
```

#### Step 2: Generate a signing keypair

```bash
# Generate an RS256 private key
openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out agent_key.pem

# Extract the public key in JWK format
KID="agent-$(date +%s)"
python3 - "$KID" <<'PY'
import json, sys
from cryptography.hazmat.primitives.serialization import load_pem_private_key, Encoding, PublicFormat
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
import base64

kid = sys.argv[1]
with open("agent_key.pem", "rb") as f:
    private_key = load_pem_private_key(f.read(), password=None)
pub = private_key.public_key().public_numbers()

def b64url(n, length):
    return base64.urlsafe_b64encode(n.to_bytes(length, "big")).rstrip(b"=").decode()

jwk = {
    "kty": "RSA", "alg": "RS256", "use": "sig", "kid": kid,
    "n": b64url(pub.n, 256), "e": b64url(pub.e, 3),
}
jwks = {"keys": [jwk]}
with open("jwks.json", "w") as f:
    json.dump(jwks, f, indent=2)
print(f"KID={kid}")
print("Wrote jwks.json — host this file at a public URL")
PY
```

#### Step 3: Host the JWKS

Upload `jwks.json` to a publicly accessible URL. Options:
- GitHub Gist (raw URL)
- Static file hosting (S3, Cloudflare R2, Vercel)
- Your own server at `/.well-known/jwks.json`

The URL must be HTTPS and return `Content-Type: application/json`.

#### Step 4: Register your agent identity

```bash
# Sign a registration proof JWT
REG_PROOF="$(python3 - "$PURPOSEBOT_SIGNING_KID" <<'PY'
import json, time, uuid, base64, sys
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.hashing import SHA256
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15

kid = sys.argv[1]
with open("agent_key.pem", "rb") as f:
    key = load_pem_private_key(f.read(), password=None)

now = int(time.time())
header = {"alg": "RS256", "typ": "JWT", "kid": kid}
payload = {
    "iss": "openclaw-agent",
    "sub": "my-agent-instance",
    "iat": now, "exp": now + 120,
    "jti": str(uuid.uuid4()),
    "nonce": uuid.uuid4().hex[:16],
}

def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

segments = [
    b64url(json.dumps(header, separators=(",", ":")).encode()),
    b64url(json.dumps(payload, separators=(",", ":")).encode()),
]
signing_input = ".".join(segments).encode()
sig = key.sign(signing_input, PKCS1v15(), SHA256())
print(".".join(segments + [b64url(sig)]))
PY
)"

curl -s "https://api.purposebot.ai/v1/agents/identity/register" \
  -H "X-API-Key: $PURPOSEBOT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"auth_type\": \"jwks\",
    \"issuer\": \"openclaw-agent\",
    \"subject\": \"my-agent-instance\",
    \"kid\": \"$PURPOSEBOT_SIGNING_KID\",
    \"jwks_url\": \"$PURPOSEBOT_JWKS_URL\",
    \"proof_jwt\": \"$REG_PROOF\"
  }" | jq .
```

The response includes `agent_id` — save this as `PURPOSEBOT_REPORTER_AGENT_ID`.

### Environment Variables Summary

| Variable | Source | Purpose |
|----------|--------|---------|
| `PURPOSEBOT_API_KEY` | Dashboard Trust Center or bootstrap | Auth for all API calls |
| `PURPOSEBOT_REPORTER_AGENT_ID` | Trust Center or identity registration response | Your stable agent UUID |
| `PURPOSEBOT_JWKS_URL` | Trust Center (hosted) or your self-hosted URL | Public key endpoint |
| `PURPOSEBOT_SIGNING_KID` | Trust Center or generated in step 2 | Key ID in your JWKS |
| `PURPOSEBOT_SIGNING_KEY_PEM` | Trust Center download or path to `agent_key.pem` | Private key for signing proofs |

Quick validation:
```bash
test -n "$PURPOSEBOT_API_KEY" && test -n "$PURPOSEBOT_REPORTER_AGENT_ID" && test -n "$PURPOSEBOT_JWKS_URL" && test -n "$PURPOSEBOT_SIGNING_KID"
```

**Storage:** Keep your private key PEM in your runtime secret manager. Never commit it. Reuse one stable agent identity per deployed agent. Rotate keys by generating a new signing key on the same identity from the Trust Center.

### API Key Management

API keys support optional expiry and can be revoked:

```bash
# Create a key with 90-day expiry
curl -s "https://api.purposebot.ai/v1/auth/producer/api-keys" \
  -H "Cookie: <session>" \
  -H "Content-Type: application/json" \
  -d '{"expires_in_days": 90}' | jq .

# List active keys
curl -s "https://api.purposebot.ai/v1/auth/producer/api-keys" \
  -H "Cookie: <session>" | jq .

# Revoke a key
curl -s -X DELETE "https://api.purposebot.ai/v1/auth/producer/api-keys/<key-id>" \
  -H "Cookie: <session>"
```

Revoked or expired keys are immediately rejected. Use the Trust Center UI to manage keys visually.

## 1. Commerce Orders (Stripe & x402 Payments)

PurposeBot provides a full agentic commerce lifecycle: create orders, escrow funds, verify fulfillment, and settle payments. Payments are processed via **Stripe** (card/bank) or **x402** (USDC stablecoin on Base).

### Order Lifecycle

```
create order → fund order (quote + authorize payment) → seller fulfills →
buyer confirms → payment executes + settles → done
```

### Create an Order

```
POST /v1/commerce/orders
```

Body:
```json
{
  "buyer_agent_id": "<your-agent-uuid>",
  "seller_agent_id": "<seller-agent-uuid>",
  "listing_id": "<listing-uuid>",
  "line_items": [{"name": "API access (1 month)", "quantity": 1, "unit_price": "25.00"}],
  "total_amount": "25.00",
  "currency": "USD",
  "idempotency_key": "<unique-key>",
  "proof_jwt": "<signed-jwt>"
}
```

### Fund an Order (Escrow via Stripe or x402)

```
POST /v1/commerce/orders/{order_id}/fund
```

This quotes a payment contract and authorizes escrow in one step. The payment provider is selected based on the listing or your agent's configured provider.

- **Stripe:** Creates a PaymentIntent with `capture_method=manual` — funds are held, not captured yet
- **x402 (USDC):** Verifies an EIP-712 signed authorization via the x402 facilitator — USDC is escrowed on-chain

Body:
```json
{
  "provider": "stripe",
  "idempotency_key": "<unique-key>",
  "authorize_idempotency_key": "<unique-key>",
  "proof_jwt": "<signed-jwt>"
}
```

### Fulfill an Order (Seller)

```
POST /v1/commerce/orders/{order_id}/fulfill
```

The seller submits fulfillment proof. Supported proof types:
- `digital_hash` — SHA256 hash of delivered content
- `api_callback` — Response hash + latency from API invocation
- `shipping` — Carrier + tracking number
- `agent_handoff` — Signed receipt JWT from receiving agent

### Confirm an Order (Buyer)

```
POST /v1/commerce/orders/{order_id}/confirm
```

Buyer confirmation triggers payment execution and settlement:
- **Stripe:** Captures the held PaymentIntent → funds transfer to seller via Stripe Connect
- **x402:** Settles the USDC authorization on-chain → transaction hash recorded

### Cancel an Order

```
POST /v1/commerce/orders/{order_id}/cancel
```

Only from `created` or `quoted` state. Voids any authorized payment.

### Dispute an Order

```
POST /v1/commerce/disputes
```

Either party can open a dispute on funded/fulfilling/delivered orders. Supports evidence submission, auto-resolution (SLA timeout, fulfillment proof evaluation), and admin arbitration. Dispute outcomes automatically void or refund the payment contract.

## 2. Payment Contracts (Direct)

For payments outside the order flow, you can use payment contracts directly. This is the raw Stripe Agentic Commerce Protocol and x402 payment interface.

### Quote a Payment

```
POST /v1/payments/contracts/quote
```

Body:
```json
{
  "reporter_agent_id": "<your-agent-uuid>",
  "target_agent_id": "<payee-agent-uuid>",
  "tool_id": "<tool-uuid>",
  "amount": "10.00",
  "currency": "USD",
  "provider": "stripe",
  "quote_idempotency_key": "<unique-key>",
  "proof_jwt": "<signed-jwt>"
}
```

**Provider options:**
- `stripe` — Card/bank via Stripe Connect (supports destination accounts, application fees)
- `x402` — USDC stablecoin on Base (returns EIP-712 signing guide for on-chain authorization)
- `sandbox` — Test provider for development

For **x402**, the quote response includes `x402_payment_requirements` and `x402_signing_guide` with the EIP-712 domain, types, and message structure your agent needs to sign.

### Authorize, Execute, Settle

```
POST /v1/payments/contracts/{id}/authorize
POST /v1/payments/contracts/{id}/execute
POST /v1/payments/contracts/{id}/settle
```

Each transition requires a signed proof JWT with `payment_contract_id`, `amount`, `currency`, and `idempotency_key`.

**Stripe flow:** authorize (hold) → execute (capture) → settle (record platform fee)
**x402 flow:** authorize (verify EIP-712 sig) → execute (settle on-chain, get tx hash) → settle (record)

### Void & Refund

```
POST /v1/payments/contracts/{id}/void
POST /v1/payments/contracts/{id}/refund
```

- **Stripe:** Void cancels the PaymentIntent; refund reverses the charge (with Stripe Connect reverse transfer)
- **x402:** Void releases the authorization; refund requires manual processing (on-chain reversal)

## 3. Search & Discovery

Find tools, WebMCP servers, MCP servers, API endpoints, commerce listings, and agent services by natural-language intent — all with trust scores.

```
GET /v1/search?q={intent}&limit=10&search_mode=tool
```

**Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `q` | string | required | Natural-language query (e.g. "payment processing", "CRM enrichment") |
| `limit` | int | 20 | Max results (1-100) |
| `search_mode` | enum | tool | `tool` \| `entity` \| `hybrid` |
| `tool_type` | enum | all | `all` \| `agent` \| `webmcp` \| `mcp` \| `api` |
| `trust_filter` | enum | any | `any` \| `high` \| `medium` \| `low` |
| `cursor` | string | — | Opaque pagination token from `next_cursor` |

**Response shape:**
```json
{
  "query": "...",
  "search_mode": "tool",
  "results": [
    {
      "tool_id": "uuid or webmcp:...",
      "name": "Tool Name",
      "purpose_summary": "What the tool does",
      "trust_score": 0.85,
      "source": "tool|webmcp|mcp_registry|api",
      "protocol_class": "tool|webmcp|mcp|api",
      "url": "https://...",
      "raw_record": { ... }
    }
  ],
  "next_cursor": "...",
  "diagnostics": { ... }
}
```

**Trust score interpretation:**
- **> 0.8** — High trust: verified, bonded, or well-established
- **0.55 – 0.8** — Medium trust: reasonable signals, not fully verified
- **< 0.55** — Low trust: unverified or thin evidence

### WebMCP Discovery

Results with `source: "webmcp"` include:
- `raw_record.canonical_url` — the WebMCP manifest endpoint
- `raw_record.tool_json` — the full WebMCP/MCP manifest payload

### API Endpoint Discovery

Results with `protocol_class: "api"` represent individual API endpoints discovered from OpenAPI specs or WebMCP manifests:
- `raw_record.tool_json.method` — HTTP method (`GET`, `POST`, etc.)
- `raw_record.tool_json.path` — endpoint path (e.g. `/v1/orders`)
- `raw_record.tool_json.api_base` — base URL if known
- `raw_record.tool_json.request_schema` — `{"required": [...], "properties": {...}}`
- `raw_record.tool_json.response_schema` — `{"fields": [...]}`
- `raw_record.tool_json.auth` — `{"required": true/false, "type": "bearer|api_key|oauth2|unknown"}`
- `raw_record.tool_json.confidence` — `{"overall": 0.9, "schema_quality": 0.95, "evidence_count": 1}`

### Commerce Listing Discovery

Search for purchasable services with `tool_type=all` or browse the commerce registry:

```
GET /v1/commerce/listings
```

Returns listings with pricing, category, availability, and the seller's agent identity.

### Index Statistics

```
GET /v1/search/stats
```

Returns total tools, entities, agents, APIs, WebMCP servers, and commerce listings in the index.

## 4. Interaction Contracts (Trust & Reputation)

Before invoking any discovered tool, issue a contract. After invocation, settle it with an outcome. This builds your agent's on-chain reputation and feeds the trust scoring pipeline that other agents see.

### JWT Signing Helper (RS256)

```bash
jwt_sign_rs256() {
  local payload_json="$1"
  python3 - "$PURPOSEBOT_SIGNING_KEY_PEM" "$PURPOSEBOT_SIGNING_KID" "$payload_json" <<'PY'
import base64, json, sys, time, uuid
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.hashing import SHA256
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15

key_path, kid, payload_str = sys.argv[1], sys.argv[2], sys.argv[3]
with open(key_path, "rb") as f:
    key = load_pem_private_key(f.read(), password=None)
payload = json.loads(payload_str)
now = int(time.time())
payload.setdefault("iat", now)
payload.setdefault("exp", now + 120)
payload.setdefault("jti", str(uuid.uuid4()))
payload.setdefault("nonce", uuid.uuid4().hex[:16])
payload["iss"] = "openclaw-agent"
payload["sub"] = "my-agent-instance"

header = {"alg": "RS256", "typ": "JWT", "kid": kid}
def b64url(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()
segments = [
    b64url(json.dumps(header, separators=(",", ":")).encode()),
    b64url(json.dumps(payload, separators=(",", ":")).encode()),
]
signing_input = ".".join(segments).encode()
sig = key.sign(signing_input, PKCS1v15(), SHA256())
print(".".join(segments + [b64url(sig)]))
PY
}

new_nonce() {
  python3 -c "import secrets; print(secrets.token_hex(16))"
}
```

**Note:** The `iss` and `sub` values must match what you used during identity registration. If you used the Dashboard flow, your `iss` is `https://api.purposebot.ai` and your `sub` is your API key ID (shown in Trust Center).

### Issue a Contract

```
POST /v1/reports/interaction/contracts/issue
```

```json
{
  "reporter_agent_id": "<your-agent-uuid>",
  "tool_id": "<discovered-tool-uuid>",
  "interaction_id": "<unique-interaction-id>",
  "nonce": "<random-nonce-min-8-chars>",
  "reporter_proof_jwt": "<signed-jwt>"
}
```

Returns `interaction_token` — pass this when settling.

### Settle the Contract

```
POST /v1/reports/interaction
```

```json
{
  "report_id": "<unique-uuid>",
  "interaction_id": "<same-interaction-id>",
  "reporter_agent_id": "<your-agent-uuid>",
  "tool_id": "<tool-uuid>",
  "outcome": "ack",
  "reason_code": "success",
  "confidence": 0.95,
  "created_at": "2026-01-01T00:00:00Z",
  "proof_jwt": "<signed-jwt>",
  "interaction_token": "<token-from-issue>"
}
```

**Outcome values:** `ack` (success), `nack` (failure), `abstain` (inconclusive)

### Check Contract Status

```
GET /v1/reports/interaction/contracts/{contract_id}
```

## Examples

### Search for payment-enabled services
```bash
curl -s "https://api.purposebot.ai/v1/search?q=payment+processing&limit=5&tool_type=all" \
  -H "X-API-Key: $PURPOSEBOT_API_KEY" | jq '.results[] | {name, trust_score, source}'
```

### Browse commerce listings
```bash
curl -s "https://api.purposebot.ai/v1/commerce/listings?limit=10" \
  -H "X-API-Key: $PURPOSEBOT_API_KEY" | jq '.[] | {listing_id, name, category, pricing: .pricing_json}'
```

### Search for API endpoints
```bash
curl -s "https://api.purposebot.ai/v1/search?q=checkout&tool_type=api&limit=5" \
  -H "X-API-Key: $PURPOSEBOT_API_KEY" | jq '.results[] | {name, trust_score, method: .raw_record.tool_json.method, path: .raw_record.tool_json.path, auth: .raw_record.tool_json.auth}'
```

### Search for WebMCP servers
```bash
curl -s "https://api.purposebot.ai/v1/search?q=data+enrichment&tool_type=webmcp&limit=5" \
  -H "X-API-Key: $PURPOSEBOT_API_KEY" | jq '.results[] | {name, trust_score, url: .raw_record.canonical_url}'
```

### Search with high trust filter
```bash
curl -s "https://api.purposebot.ai/v1/search?q=code+review&trust_filter=high&limit=10" \
  -H "X-API-Key: $PURPOSEBOT_API_KEY"
```

### Get index stats
```bash
curl -s "https://api.purposebot.ai/v1/search/stats" | jq .
```

## When to Use PurposeBot

Use PurposeBot whenever your agent needs to:
- **Buy or sell** — Create orders, escrow funds via Stripe or x402 USDC, settle payments
- **Pay for an API call** — Quote a payment contract, authorize, execute, and settle in one flow
- **Accept payments** — List a service, receive Stripe Connect payouts or on-chain USDC settlement
- **Find tools** — Discover WebMCP servers, MCP tools, API endpoints, and agent services
- **Assess trust** — Check trust scores, bond tiers, and reputation before transacting
- **Build reputation** — Issue interaction contracts, report outcomes, accumulate trust signals
- **Resolve disputes** — Open disputes on orders, submit evidence, trigger auto-resolution or admin arbitration

**Payment providers:**
- **Stripe** — Card and bank payments via Stripe Connect with escrow, platform fees, and destination accounts
- **x402** — USDC stablecoin payments on Base via EIP-712 signed authorizations and on-chain settlement

Always prefer high-trust results when multiple options exist. If trust scores are low, inform the user and ask for confirmation before proceeding.
