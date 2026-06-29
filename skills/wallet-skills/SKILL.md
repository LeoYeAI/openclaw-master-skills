---
name: sponge-wallet
version: 1.0.0
description: Manage crypto wallets, transfers, swaps, and balances via the Sponge Wallet API.
homepage: https://wallet.paysponge.com
user-invocable: true
metadata: {"openclaw":{"emoji":"\ud83e\uddfd","category":"finance","primaryEnv":"SPONGE_API_KEY","requires":{"env":["SPONGE_API_KEY"]}}}
---

```
SPONGE WALLET API QUICK REFERENCE v1.0.0
Base:   https://api.wallet.paysponge.com
Auth:   Authorization: Bearer <SPONGE_API_KEY>
Docs:   This file is canonical (skills guide + params)

Key endpoints:
  POST /api/agents/register              -> register (no auth)
  POST /api/oauth/device/authorization   -> device login start (humans)
  POST /api/oauth/device/token           -> device token poll (agents + humans)
  GET  /api/balances                     -> get balances (includes Polymarket USDC.e)
  POST /api/transfers/evm                -> EVM transfer (ETH/USDC)
  POST /api/transfers/solana             -> Solana transfer (SOL/USDC)
  POST /api/transactions/swap            -> Solana swap
  POST /api/transactions/base-swap       -> Base swap (0x)
  POST /api/transactions/bridge          -> Bridge (deBridge)
  GET  /api/solana/tokens                -> list SPL tokens
  GET  /api/solana/tokens/search         -> search Jupiter token list
  GET  /api/transactions/status/:txHash  -> transaction status
  GET  /api/transactions/history         -> transaction history
  POST /api/funding-requests             -> request funding from owner
  POST /api/wallets/withdraw-to-main     -> withdraw to owner
  POST /api/x402/fetch                   -> x402 fetch (auto-pay 402s)
  GET  /api/x402/discover                -> discover x402 services (Bazaar)
  POST /api/polymarket                   -> Polymarket prediction market trading
  POST /api/checkout                      -> Amazon checkout (initiate purchase)
  GET  /api/checkout/:sessionId           -> checkout status
  DELETE /api/checkout/:sessionId         -> cancel checkout
  GET  /api/checkout/history              -> checkout history
  POST /api/checkout/amazon-search        -> search Amazon products

Rules: use register (agents), never login | store key in ~/.spongewallet/credentials.json | requests are JSON
Errors: HTTP status + JSON error message
```

# Sponge Wallet API - Agent Skills Guide

This skill is **doc-only**. There is no local CLI. Agents must call the Sponge Wallet REST API directly.

## Why the steps matter (short rationale)

- **Register vs login**: agents create a new managed wallet tied to a human owner. That owner must explicitly claim the agent. Login is only for humans who already have an account.
- **Claim URL**: ensures the human owner explicitly links the agent to their account and controls allowlists/funding.
- **Credential persistence**: the `apiKey` is returned once (immediately for agent-first mode, or after device approval for standard mode). If you lose it, you must re-register or re-authenticate.

## Standard credential storage (required)

Store the API key in **one canonical location**:

- `~/.spongewallet/credentials.json`

Recommended file contents:
```json
{
  "apiKey": "sponge_live_...",
  "claimCode": "ABCD-1234",
  "claimUrl": "https://wallet.paysponge.com/device?code=ABCD-1234"
}
```

Optional environment export (runtime convenience):
```bash
export SPONGE_API_KEY="$(jq -r .apiKey ~/.spongewallet/credentials.json)"
```

## Base URL & Auth

- Base URL: `https://api.wallet.paysponge.com`
- Auth header: `Authorization: Bearer <SPONGE_API_KEY>`
- Content-Type: `application/json`

Quick env setup:

```bash
export SPONGE_API_URL="https://api.wallet.paysponge.com"
export SPONGE_API_KEY="$(jq -r .apiKey ~/.spongewallet/credentials.json)"
```

## CRITICAL: AI Agents Must Use `register`, NOT `login`

### 1) Agent Registration (AI agents only)

There are two modes:
- **Standard device flow** (default): human must approve before the API key is returned.
- **Agent-first** (`agentFirst: true`): agent receives the API key immediately, and the human can claim later.

**Step 1 — Start registration (agent-first recommended)**
```bash
curl -sS -X POST "$SPONGE_API_URL/api/agents/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"YourAgentName",
    "agentFirst": true,
    "testnet": true
  }'
```

Response includes:
- `verificationUriComplete` (claim URL for the human owner)
- `claimCode`, `deviceCode`, `expiresIn`, `interval`, `claimText`
- `apiKey` (returned immediately in agent-first mode)

Store `apiKey`, `claimCode`, and `verificationUriComplete` (as `claimUrl`) in `~/.spongewallet/credentials.json` so a human can claim later if context resets.

**Step 2 — Send the claim URL to the human owner**
They log in, optionally post the tweet text, and approve the agent.

Claim link format:
- `verificationUriComplete` (example path: `/device?code=ABCD-1234`)
- The base URL is the frontend (prod or local), so just pass the full `verificationUriComplete` to the human.

**Step 3 — Poll for completion (standard device flow only)**
```bash
curl -sS -X POST "$SPONGE_API_URL/api/oauth/device/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grantType":"urn:ietf:params:oauth:grant-type:device_code",
    "deviceCode":"<deviceCode>",
    "clientId":"spongewallet-skill"
  }'
```

On success, the response includes `apiKey`. Save it to `~/.spongewallet/credentials.json` and use it as `SPONGE_API_KEY`.

Note: In **agent-first mode**, you already have the `apiKey` from Step 1. The device token will remain pending until the human claims.

### 2) Human Login (existing accounts only)

**Phase 1 — Request device code**
```bash
curl -sS -X POST "$SPONGE_API_URL/api/oauth/device/authorization" \
  -H "Content-Type: application/json" \
  -d '{
    "clientId":"spongewallet-skill",
    "scope":"wallet:read wallet:write transaction:sign transaction:write"
  }'
```

**Phase 2 — Poll for token** (same endpoint as agents)
```bash
curl -sS -X POST "$SPONGE_API_URL/api/oauth/device/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grantType":"urn:ietf:params:oauth:grant-type:device_code",
    "deviceCode":"<deviceCode>",
    "clientId":"spongewallet-skill"
  }'
```

## Tool Call Pattern

All tool calls are plain REST requests with JSON payloads.

**Common headers**
```bash
-H "Authorization: Bearer $SPONGE_API_KEY" \
-H "Content-Type: application/json" \
-H "Accept: application/json"
```

**Agent ID note:** `agentId` is optional for API key auth. It is only required when using a user session (e.g., Privy-based auth) or when explicitly operating on a different agent.

### Tool -> Endpoint Map

| Tool | Method | Path | Params/Body |
|------|--------|------|-------------|
| `get_balance` | GET | `/api/balances` | Query: `chain`, `allowedChains`, `onlyUsdc` |
| `get_solana_tokens` | GET | `/api/solana/tokens` | Query: `chain` |
| `search_solana_tokens` | GET | `/api/solana/tokens/search` | Query: `query`, `limit` |
| `evm_transfer` | POST | `/api/transfers/evm` | Body: `chain`, `to`, `amount`, `currency` |
| `solana_transfer` | POST | `/api/transfers/solana` | Body: `chain`, `to`, `amount`, `currency` |
| `solana_swap` | POST | `/api/transactions/swap` | Body: `chain`, `inputToken`, `outputToken`, `amount`, `slippageBps` |
| `base_swap` | POST | `/api/transactions/base-swap` | Body: `chain`, `inputToken`, `outputToken`, `amount`, `slippageBps` |
| `bridge` | POST | `/api/transactions/bridge` | Body: `sourceChain`, `destinationChain`, `token`, `amount`, `destinationToken`, `recipientAddress` |
| `get_transaction_status` | GET | `/api/transactions/status/{txHash}` | Query: `chain` |
| `get_transaction_history` | GET | `/api/transactions/history` | Query: `limit`, `chain` |
| `request_funding` | POST | `/api/funding-requests` | Body: `amount`, `reason`, `chain`, `currency` |
| `withdraw_to_main_wallet` | POST | `/api/wallets/withdraw-to-main` | Body: `chain`, `amount`, `currency` |
| `x402_fetch` | POST | `/api/x402/fetch` | Body: `url`, `method`, `headers`, `body`, `preferred_chain` |
| `discover_x402_services` | GET | `/api/x402/discover` | Query: `type`, `limit`, `offset`, `include_catalog` |
| `polymarket` | POST | `/api/polymarket` | Body: `action`, + action-specific params (see below) |
| `amazon_checkout` | POST | `/api/checkout` | Body: `checkoutUrl`, `amazonAccountId`, `shippingAddress`, `dryRun`, `clearCart` |
| `get_checkout_status` | GET | `/api/checkout/{sessionId}` | Query: `agentId` (optional) |
| `get_checkout_history` | GET | `/api/checkout/history` | Query: `agentId`, `limit`, `offset` |
| `amazon_search` | POST | `/api/checkout/amazon-search` | Body: `query`, `maxResults`, `region` |

Note: request bodies use camelCase (e.g., `inputToken`, `slippageBps`).

### Polymarket Actions

The `polymarket` endpoint is a unified tool. Pass `action` plus action-specific parameters:

| Action | Description | Required Params | Optional Params |
|--------|-------------|-----------------|-----------------|
| `status` | Check Polymarket account status and USDC.e balance | — | — |
| `markets` | Search prediction markets | — | `query`, `limit` |
| `positions` | View current market positions | — | — |
| `orders` | View open and recent orders | — | — |
| `order` | Place a buy/sell order | `outcome`, `side`, `size`, `price` | `market_slug` or `token_id`, `order_type` |
| `cancel` | Cancel an open order | `order_id` | — |
| `set_allowances` | Reset token approvals | — | — |
| `withdraw` | Withdraw USDC.e from Safe to any address | `to_address`, `amount` | — |

**Order params:**
- `market_slug`: Market URL slug (e.g., `"will-bitcoin-hit-100k"`) — use this OR `token_id`
- `token_id`: Polymarket condition token ID — use this OR `market_slug`
- `outcome`: `"yes"` or `"no"`
- `side`: `"buy"` or `"sell"`
- `size`: Number of shares (e.g., `10`)
- `price`: Probability price 0.0–1.0 (e.g., `0.65` = 65 cents per share)
- `order_type`: `"GTC"` (default), `"GTD"`, `"FOK"`, `"FAK"`

**Scopes:** Trade actions (`order`, `cancel`, `set_allowances`, `withdraw`) require `polymarket:trade` scope. Read actions (`status`, `markets`, `positions`, `orders`) require `polymarket:read`.

**Auto-provisioning:** The Polymarket Safe wallet is created automatically on first use. No manual setup needed.

### Amazon Checkout

Purchase products from Amazon using a configured Amazon account.

**Prerequisites:**
- An Amazon account must be configured via the dashboard or `/api/agents/:id/amazon-accounts` endpoints
- A shipping address must be set (inline or via `/api/agents/:id/shipping-addresses`)

**Async workflow:**
1. Initiate checkout with `POST /api/checkout` — returns a `sessionId`
2. Wait ~60 seconds for the initial checkout process
3. Poll `GET /api/checkout/:sessionId` every 10 seconds until status is `completed` or `failed`

**Status progression:** `pending` → `in_progress` → `completed` | `failed` | `cancelled`

**Key options:**
- `dryRun: true` — stops before placing the order (useful for testing or previewing total cost)
- `clearCart: true` — clears the Amazon cart before adding the product (default behavior)

**Scopes:** Checkout actions require `amazon_checkout` scope on the API key.

## Quick Start

### 1) Register (agents only)
```bash
curl -sS -X POST "$SPONGE_API_URL/api/agents/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"YourAgentName",
    "agentFirst": true,
    "testnet": true
  }'
```
Share the claim URL with your human, then store the `apiKey` immediately (agent-first). For standard device flow, poll for the token after approval.

### 2) Check balance
```bash
curl -sS "$SPONGE_API_URL/api/balances?chain=base" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Accept: application/json"
```

### 3) Transfer USDC on Base
```bash
curl -sS -X POST "$SPONGE_API_URL/api/transfers/evm" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chain":"base",
    "to":"0x...",
    "amount":"10",
    "currency":"USDC"
  }'
```

## Examples

### Swap tokens on Solana
```bash
curl -sS -X POST "$SPONGE_API_URL/api/transactions/swap" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chain":"solana",
    "inputToken":"SOL",
    "outputToken":"BONK",
    "amount":"0.5",
    "slippageBps":100
  }'
```

### Swap tokens on Base
```bash
curl -sS -X POST "$SPONGE_API_URL/api/transactions/base-swap" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chain":"base",
    "inputToken":"ETH",
    "outputToken":"USDC",
    "amount":"0.1",
    "slippageBps":50
  }'
```

### Bridge tokens cross-chain
```bash
curl -sS -X POST "$SPONGE_API_URL/api/transactions/bridge" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sourceChain":"solana",
    "destinationChain":"base",
    "token":"SOL",
    "amount":"0.1",
    "destinationToken":"ETH"
  }'
```

### Check transaction status
```bash
curl -sS "$SPONGE_API_URL/api/transactions/status/0xabc123...?chain=base" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Accept: application/json"
```

### Polymarket — Check status
```bash
curl -sS -X POST "$SPONGE_API_URL/api/polymarket" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action":"status"}'
```

### Polymarket — Search markets
```bash
curl -sS -X POST "$SPONGE_API_URL/api/polymarket" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action":"markets","query":"bitcoin","limit":5}'
```

### Polymarket — Place an order
```bash
curl -sS -X POST "$SPONGE_API_URL/api/polymarket" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action":"order",
    "market_slug":"will-bitcoin-hit-100k",
    "outcome":"yes",
    "side":"buy",
    "size":10,
    "price":0.65
  }'
```

### Polymarket — View positions
```bash
curl -sS -X POST "$SPONGE_API_URL/api/polymarket" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"action":"positions"}'
```

### Polymarket — Withdraw USDC.e
```bash
curl -sS -X POST "$SPONGE_API_URL/api/polymarket" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "action":"withdraw",
    "to_address":"0x...",
    "amount":"10.00"
  }'
```

### Amazon Checkout — Initiate purchase
```bash
curl -sS -X POST "$SPONGE_API_URL/api/checkout" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "checkoutUrl":"https://www.amazon.com/dp/B0EXAMPLE",
    "dryRun":true,
    "clearCart":true
  }'
```

### Amazon Checkout — Poll status
```bash
curl -sS "$SPONGE_API_URL/api/checkout/<sessionId>" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Accept: application/json"
```

### Amazon Checkout — Get history
```bash
curl -sS "$SPONGE_API_URL/api/checkout/history?limit=10" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Accept: application/json"
```

### Amazon — Search products
```bash
curl -sS -X POST "$SPONGE_API_URL/api/checkout/amazon-search" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query":"wireless mouse","maxResults":5}'
```

### x402 Fetch (auto-pay for paid APIs)
```bash
curl -sS -X POST "$SPONGE_API_URL/api/x402/fetch" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url":"https://api.paysponge.com/api/services/purchase/svc_abc123/polymarket/markets?search=bitcoin&limit=5",
    "method":"GET",
    "preferred_chain":"base"
  }'
```

The `x402_fetch` tool handles the entire payment flow automatically:
1. Makes the HTTP request to the specified URL
2. If the service returns 402 Payment Required, extracts payment requirements
3. Creates and signs a USDC payment using the agent's wallet (Base or Solana)
4. Retries the request with the Payment-Signature header
5. Returns the final API response with `payment_made` and `payment_details`

### Discover x402 services (Bazaar)
```bash
curl -sS "$SPONGE_API_URL/api/x402/discover?limit=10" \
  -H "Authorization: Bearer $SPONGE_API_KEY" \
  -H "Accept: application/json"
```

Returns available x402-enabled services from the Bazaar and Sponge's curated catalog. Use this to find paid APIs before calling `x402_fetch`.

## Chain Reference

**Test keys** (`sponge_test_*`): `sepolia`, `base-sepolia`, `solana-devnet`, `tempo`
**Live keys** (`sponge_live_*`): `ethereum`, `base`, `solana`

## Error Responses

Errors return JSON with an error message and HTTP status:

```json
{"error":"message"}
```

| Status | Meaning | Common Cause |
|--------|---------|--------------|
| 400 | Bad Request | Missing/invalid fields |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Address not in allowlist or permission denied |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate action |
| 429 | Rate Limited | Too many requests (back off + retry) |
| 500 | Server Error | Transient; retry later |

## Security

- Never share your API key in logs, posts, or screenshots.
- Store your API key in `~/.spongewallet/credentials.json` and restrict file permissions.
- Rotate the key if exposure is suspected.

---

Built for agents.
