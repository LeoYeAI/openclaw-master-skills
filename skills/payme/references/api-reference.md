# PayMe Agent API Reference

Base URL: `https://api.feedom.tech`

All authenticated endpoints require:
- `Authorization: Bearer <agentToken>`
- `X-Agent-Installation-Id: <stable-installation-id>`

Generate one stable random installation ID per agent install and reuse it on every request for that install. Do not generate a fresh ID per request.

---

## POST /api/agent/create-account

Create a new PayMe wallet instantly. No auth header needed. The user **chooses a new PIN** they invent on the spot — this is for their future web/Telegram login. The agent never stores, reuses, or asks for this PIN again.

**Request:**
```json
{ "pin": "123456", "installationId": "openclaw-6f1b0e3c-4a0d-4d6b-8f44-6f9b99b3b201" }
```

- `pin`: string, 6-8 digits (a **new** PIN chosen by the user — ask them to delete the message after)
- `installationId`: string, 8-128 chars. A stable random ID for this specific agent installation. Reuse the same ID for later requests from the same install.

**Response (200):**
```json
{
  "agentToken": "64-char hex string",
  "expiresAt": "2026-04-08T12:00:00.000Z",
  "bootstrapOnly": true,
  "kernelAddress": "0x...",
  "username": null,
  "claimCode": "X9K2M7",
  "claimExpiresIn": "24 hours",
  "scopes": ["wallet:read", "contacts:read", "contacts:write", "payments:prepare", "payments:execute"],
  "greeting": "Wallet created! Your address: 0x...",
  "capabilities": ["Check balances across Base, Arbitrum, ...", "..."]
}
```

The `claimCode` is a one-time 6-character code the user can enter on the web app ([payme.feedom.tech](https://payme.feedom.tech)) or Telegram bot to claim their account and set a username. It expires in 24 hours.

Store the `agentToken` securely — it grants immediate wallet access.
This is **bootstrap access only**: it expires quickly, cannot be refreshed, and should be treated as temporary setup access for this installation only.
Tell the user when the returned `expiresAt` time is, so they know when bootstrap access ends.

**Errors:**
- `400` — Invalid PIN (must be 6-8 digits)
- `429` — Rate limited (max 3 per hour per IP)

---

## POST /api/agent/connect

Connect a PayMe account using a one-time connection code. No auth header needed.

**Request:**
```json
{ "code": "A3K9X2", "installationId": "openclaw-6f1b0e3c-4a0d-4d6b-8f44-6f9b99b3b201" }
```
`installationId` is required and must stay stable for this agent install.

The user generates this code from the web app at [payme.feedom.tech](https://payme.feedom.tech). In the web app, PayMe asks for the user's PIN before revealing the code. Codes are 6 characters, single-use, and expire in 5 minutes. The resulting token duration is chosen by the user when generating the code (default 14 days, with 30-day and 90-day access as longer explicit options).

**Response (200):**
```json
{
  "agentToken": "64-char hex string",
  "expiresAt": "2026-04-08T12:00:00.000Z",
  "bootstrapOnly": false,
  "kernelAddress": "0x...",
  "username": "alice",
  "scopes": ["wallet:read", "contacts:read", "contacts:write", "payments:prepare", "payments:execute"],
  "greeting": "Connected to alice's PayMe wallet! Here's what I can do:",
  "capabilities": [
    "Check balances across Base, Arbitrum, Polygon, BNB Chain, and Avalanche",
    "Send USDC/USDT to any PayMe username, email, or 0x address",
    "Sell crypto for local currency via P2P in 10 African countries with smart contract escrow protection",
    "View transaction history and manage saved contacts"
  ]
}
```

Tell the user when the returned `expiresAt` time is, and if they want longer access tell them to open the PayMe web app and manually generate a longer-duration code from **Settings -> AI Agent Access**.
The same installation cannot be linked to multiple PayMe accounts at the same time. If the API returns a conflict, the user needs to disconnect that agent setup first or use a fresh install.

Show the `greeting` and `capabilities` to the user after connecting.

**Errors:**
- `400` — Missing code
- `401` — Invalid or expired code
- `429` — Too many attempts (5 per 15 minutes)

---

## GET /api/agent/wallet

**Scope:** `wallet:read`

**Response (200):**
```json
{
  "kernelAddress": "0x...",
  "username": "alice",
  "supportedChains": ["arbitrum", "base", "polygon", "bsc", "avalanche"],
  "supportedTokens": ["USDC", "USDT"]
}
```

---

## GET /api/agent/balances

**Scope:** `wallet:read`

**Response (200):**
```json
{
  "balances": { "USDC": "150.00", "USDT": "25.50" },
  "chainBalances": [
    { "chain": "base", "chainName": "Base", "USDC": "100.00", "USDT": "0.00" },
    { "chain": "arbitrum", "chainName": "Arbitrum One", "USDC": "50.00", "USDT": "25.50" }
  ]
}
```

---

## POST /api/agent/send

Prepare a payment, or prepare and execute in one call with `execute: true`.

**Scope:** `payments:prepare` (add `payments:execute` when using `execute: true`)

**Request:**
```json
{
  "recipient": "username, email, or 0x address",
  "amount": 10,
  "token": "USDC",
  "execute": false
}
```

- `amount`: number or string, must be > 0 and <= 1,000,000
- `token`: `"USDC"` or `"USDT"` (case-insensitive)
- `execute` (optional, default `false`): if `true`, prepares and executes the payment in one call

**Response (200) — preview only (default):**
```json
{
  "confirmationId": "uuid",
  "preview": {
    "recipient": "alice",
    "resolvedAddress": "0x...",
    "amount": "10.00",
    "token": "USDC",
    "chain": "base",
    "chainName": "Base",
    "fee": "0.05 USDC",
    "feePercent": "0.50%",
    "netAmount": "9.95 USDC"
  }
}
```

**Response (200) — direct execute (`execute: true`):**
```json
{
  "preview": {
    "recipient": "alice",
    "resolvedAddress": "0x...",
    "amount": "10.00",
    "token": "USDC",
    "chain": "base",
    "chainName": "Base",
    "fee": "0.05 USDC",
    "feePercent": "0.50%",
    "netAmount": "9.95 USDC"
  },
  "success": true,
  "txHash": "0x...",
  "fee": "50000",
  "netAmount": "9950000",
  "chain": "base"
}
```

When `execute: true`, no `/api/agent/confirm` call is needed. The preview is still included so you can show the user what was sent.

**Errors:**
- `400` — Invalid amount, token, or recipient
- `400` — Insufficient balance or no available chain
- `403` — Missing `payments:execute` scope (when `execute: true`)
- `403` — `AGENT_SPEND_LIMIT` — Agent daily spending limit reached. The response includes `{ code: "AGENT_SPEND_LIMIT", limit: 500, remaining: 0 }`. Tell the user they can increase their limit in the PayMe app under **Settings > AI Agent Access > Daily spend limit**, or send the payment directly from the app.

**Daily Spend Limit:**
Agents are subject to a per-user daily spending cap (default $500/day, configurable $10–$10,000). This resets every 24 hours. When the limit is hit, both direct-execute sends and 2-step confirms will be rejected. The user must increase their limit in the PayMe app (requires their PIN) or use the app directly for that transfer.

---

## POST /api/agent/confirm

Execute a previously prepared payment.

**Scope:** `payments:execute`

**Request:**
```json
{ "confirmationId": "uuid-from-send" }
```

**Response (200):**
```json
{
  "success": true,
  "txHash": "0x...",
  "fee": "50000",
  "netAmount": "9950000",
  "chain": "base"
}
```

- `fee` and `netAmount` are raw uint256 strings (6 decimals for USDC/USDT)

**Errors:**
- `404` — Confirmation not found or expired
- `403` — Payment does not belong to this token holder
- `403` — `AGENT_SPEND_LIMIT` — Daily spending limit reached (same as `/agent/send`)
- `410` — Confirmation expired (>5 min)

---

## GET /api/agent/history

**Scope:** `wallet:read`

**Query params:**
- `limit` (optional, default 20, max 50)

**Response (200):**
```json
{
  "transactions": [
    {
      "id": "123-0",
      "type": "sent",
      "recipient": "0x...",
      "amount": "10.00",
      "token": "USDC",
      "chain": "base",
      "txHash": "0x...",
      "createdAt": "2025-01-15T10:30:00Z"
    }
  ]
}
```

---

## GET /api/agent/contacts

**Scope:** `contacts:read`

**Response (200):**
```json
{
  "contacts": [
    { "name": "Alice", "address": "0x..." },
    { "name": "Bob", "address": "0x..." }
  ]
}
```

---

## POST /api/agent/contacts

**Scope:** `contacts:write`

**Request:**
```json
{ "name": "Alice", "address": "0x..." }
```

**Response (200):**
```json
{ "success": true }
```

**Errors:**
- `400` — Missing name or address, or invalid address

---

## DELETE /api/agent/contacts/:name

**Scope:** `contacts:write`

**Response (200):**
```json
{ "success": true }
```

---

## GET /api/agent/search?q={query}

**Scope:** `contacts:read`

Search for PayMe users and saved contacts by partial name or username. Useful when the user provides a name that doesn't match exactly, or when they want to find someone.

**Query params:**
- `q` — Search query (min 2 characters). Partial, case-insensitive.

**Response (200):**
```json
{
  "results": [
    { "type": "contact", "name": "chris lee", "address": "0x..." },
    { "type": "user", "username": "chrislee", "address": "0x..." }
  ]
}
```

**Errors:**
- `400` — Query too short (< 2 chars)

---

## POST /api/agent/refresh-token

Extends the current agent token by 7 days. Call before the token expires to maintain access. Requires a valid, non-revoked Bearer token plus the matching `X-Agent-Installation-Id` header.

**Response (200):**
```json
{ "success": true, "expiresAt": "2026-04-07T12:00:00.000Z" }
```

**Error (401):** Token is invalid or revoked.
**Error (403):** Bootstrap tokens cannot be refreshed. Tell the user to claim the account, then reconnect from PayMe Settings -> AI Agent Access.

---

## POST /api/agent/revoke

Revokes the current agent token. Requires a valid Bearer token plus the matching `X-Agent-Installation-Id` header.

**Response (200):**
```json
{ "success": true, "revoked": true }
```

---

# Vendor Trade Management Endpoints

These endpoints are only accessible to users who are registered P2P vendors.

---

## GET /api/agent/vendor/orders

**Scope:** `wallet:read`

List orders assigned to the vendor. Returns active orders by default.

**Query params:**
- `status` (optional) — Filter: `escrow_locked`, `accepted`, `fiat_sent`, `completed`, `cancelled`, `disputed`

**Response (200):**
```json
{
  "orders": [
    {
      "orderId": "abc12345-...",
      "status": "escrow_locked",
      "amount": "50.00 USDC",
      "fiat": "₦85,000",
      "reroutes": 0,
      "createdAt": "2026-03-17T10:00:00Z"
    }
  ]
}
```

---

## POST /api/agent/vendor/orders/:id/accept

**Scope:** `payments:execute`

Accept a trade assigned to you. Only works on `escrow_locked` orders.

**Response (200):**
```json
{ "success": true }
```

**Errors:**
- Order not found, not assigned to you, or wrong status

---

## POST /api/agent/vendor/orders/:id/reject

**Scope:** `payments:execute`

Decline a trade. The order is rerouted to the next available vendor.

**Response (200):**
```json
{ "success": true }
```

---

## POST /api/agent/vendor/orders/:id/mark-paid

**Scope:** `payments:execute`

Mark that fiat payment has been sent to the buyer. Only works on `accepted` orders.

**Response (200):**
```json
{ "success": true }
```

---

## POST /api/agent/vendor/orders/:id/cancel

**Scope:** `payments:execute`

Cancel an order after accepting. Refunds buyer escrow. Warning: 3 consecutive cancellations trigger a temporary vendor cooldown.

**Request (optional):**
```json
{ "reason": "Out of funds" }
```

**Response (200):**
```json
{ "success": true }
```

---

## GET /api/p2p/vendor/insights

**Scope:** `wallet:read` (vendor only)

Returns live marketplace intelligence for the vendor dashboard: demand signal, rate competitiveness rank per token, and performance benchmarks vs peers.

**Response (200):**
```json
{
  "demand": {
    "activeBuyers24h": 12,
    "ordersLastHour": 3,
    "avgRateUSDC": 1620,
    "avgRateUSDT": 1615,
    "totalOnlineVendors": 5
  },
  "rateRank": {
    "USDC": { "rank": 2, "total": 8, "diff": 15 },
    "USDT": { "rank": 1, "total": 6, "diff": null }
  },
  "benchmarks": {
    "speedPercentile": 80,
    "completionPercentile": 90,
    "ratingPercentile": 75,
    "missedOrders7d": 1
  }
}
```

- `rateRank.diff`: amount to add to your rate to reach #1 (null if already #1)
- `benchmarks.*Percentile`: percentage of vendors you are better than (higher = better)
- `missedOrders7d`: cancelled orders in the last 7 days

---

# P2P Endpoints — Sell Crypto for Local Currency

The P2P system supports 10 African countries: Nigeria (NGN), Ghana (GHS), Kenya (KES), South Africa (ZAR), Cameroon (XAF), Senegal (XOF), Benin (XOF), Togo (XOF), Tanzania (TZS), Uganda (UGX). Payment methods include bank transfer and mobile money (M-Pesa, MTN MoMo, Orange Money, etc.) depending on country.

## GET /api/agent/p2p/countries

Returns all supported countries with their currencies, payment methods, and required fields. No auth required.

**Response (200):**
```json
{
  "countries": [
    {
      "name": "Nigeria",
      "code": "NG",
      "currency": "NGN",
      "currencySymbol": "₦",
      "flag": "🇳🇬",
      "paymentMethods": [
        {
          "type": "bank_transfer",
          "provider": "Bank Transfer",
          "fields": [
            { "key": "bank_name", "label": "Bank Name", "placeholder": "e.g. GTBank, Kuda, Opay" },
            { "key": "account_number", "label": "Account Number", "placeholder": "10-digit account number", "validation": "^\\d{10}$" },
            { "key": "account_name", "label": "Account Holder Name", "placeholder": "Full name on account" }
          ]
        }
      ]
    },
    {
      "name": "Kenya",
      "code": "KE",
      "currency": "KES",
      "currencySymbol": "KSh",
      "flag": "🇰🇪",
      "paymentMethods": [
        {
          "type": "mobile_money",
          "provider": "M-Pesa",
          "fields": [
            { "key": "phone_number", "label": "M-Pesa Phone Number", "placeholder": "e.g. 07XXXXXXXX", "validation": "^0[17]\\d{8}$" },
            { "key": "account_name", "label": "Registered Name", "placeholder": "Name on mobile money account" }
          ]
        },
        { "type": "bank_transfer", "provider": "Bank Transfer", "fields": ["..."] }
      ]
    }
  ]
}
```

Use this to guide users through adding a payment method: show countries, then methods for their country, then collect the right fields.

---

## GET /api/agent/p2p/rates

Public endpoint (no auth required).

**Query params:**
- `token` (optional, default `USDC`)
- `currency` (optional, default `NGN`) — use the currency matching the user's country (e.g. `KES` for Kenya, `GHS` for Ghana)

**Response (200):**
```json
{
  "rates": [
    {
      "vendorId": 1,
      "vendorName": "FastPay",
      "rate": 1580.00,
      "avgRating": 4.8,
      "completionRate": 0.97,
      "responseTimeAvg": 120,
      "totalTrades": 350,
      "minOrderUsd": 5,
      "maxOrderUsd": 500,
      "totalDisputes": 2,
      "disputesWon": 1,
      "disputesLost": 1,
      "tradesToday": 8,
      "lastTradeAgoSecs": 120
    }
  ],
  "avgSpeed": { "seconds": 180, "label": "3 minutes or less" },
  "socialProof": { "tradesLastHour": 12, "volumeToday": 45000 }
}
```

---

## GET /api/agent/p2p/bank-accounts

**Scope:** `wallet:read`

**Response (200):**
```json
{
  "accounts": [
    {
      "id": 1,
      "user_id": 4,
      "bank_name": "GTBank",
      "account_number": "0123456789",
      "account_name": "John Doe",
      "is_default": 1,
      "country_code": "NG",
      "method_type": "bank_transfer",
      "created_at": "2025-01-15T10:00:00Z"
    }
  ]
}
```

---

## POST /api/agent/p2p/bank-accounts

**Scope:** `payments:execute`

Adding or removing a bank account triggers a **30-day lock** on further changes. This is a security measure to prevent unauthorized account swaps.

**Request:**
```json
{
  "bankName": "GTBank",
  "accountNumber": "0123456789",
  "accountName": "John Doe",
  "countryCode": "NG",
  "methodType": "bank_transfer"
}
```

- `countryCode` (optional, default `"NG"`): ISO 3166-1 alpha-2 code. Must be one of the supported countries from `/api/agent/p2p/countries`.
- `methodType` (optional, default `"bank_transfer"`): `"bank_transfer"` or `"mobile_money"`.
- For **mobile money**: `bankName` should be the provider name (e.g. `"M-Pesa"`, `"MTN MoMo"`) and `accountNumber` should be the phone number.
- For **bank transfer**: `bankName` is the bank name, `accountNumber` is the bank account number.

**Response (200):**
```json
{ "success": true, "account": { "id": 1, "bank_name": "GTBank", "account_number": "0123456789", "account_name": "John Doe", "is_default": 1, "country_code": "NG", "method_type": "bank_transfer" } }
```

**Errors:**
- `400` — Missing fields, unsupported country code, or invalid method type
- `403` — Bank account changes are locked (30-day cooldown active)
- `409` — Account number already registered to another user

---

## DELETE /api/agent/p2p/bank-accounts/:id

**Scope:** `payments:execute`

Triggers a 30-day lock on further bank account changes.

**Response (200):**
```json
{ "success": true, "removed": true }
```

---

## POST /api/agent/p2p/sell

Create a sell order. Locks crypto in escrow immediately. The order's `fiatCurrency` is derived from the buyer's payment method country.

**Scope:** `payments:prepare` + `payments:execute`

**Request:**
```json
{
  "token": "USDC",
  "amount": 50,
  "bankAccountId": 1,
  "vendorId": null
}
```

- `token`: `"USDC"` or `"USDT"`
- `amount`: number, must be > 0
- `bankAccountId`: from `/api/agent/p2p/bank-accounts`
- `vendorId` (optional): pick a specific vendor from `/api/agent/p2p/rates`, or omit for auto-selection

**Response (200):**
```json
{
  "success": true,
  "order": {
    "id": "uuid",
    "status": "escrow_locked",
    "token": "USDC",
    "cryptoAmount": 50.0,
    "fiatAmount": 79000.0,
    "fiatCurrency": "NGN",
    "rate": 1580.0,
    "chain": "arbitrum",
    "expiresAt": "2025-01-15T16:00:00Z"
  },
  "vendor": {
    "id": 1,
    "name": "FastPay"
  }
}
```

**Rerouting:** If the assigned vendor doesn't accept within ~3 minutes, the system automatically refunds the escrow and re-locks with the next best vendor (up to 3 attempts). The order ID stays the same. Poll the order to see status changes — no action needed from the agent.

**Errors:**
- `400` — Missing fields, insufficient balance, no vendors available, email not verified
- `400` with `suggestBridge: true` — Balance exists on wrong chain, user should bridge first

---

## GET /api/agent/p2p/orders

**Scope:** `wallet:read`

**Query params:**
- `limit` (optional, default 20, max 50)

**Response (200):**
```json
{
  "orders": [
    {
      "id": "uuid",
      "status": "completed",
      "token": "USDC",
      "cryptoAmount": 50.0,
      "fiatAmount": 79000.0,
      "fiatCurrency": "NGN",
      "rate": 1580.0,
      "chain": "arbitrum",
      "vendorName": "FastPay",
      "bankName": "GTBank",
      "bankCountryCode": "NG",
      "bankMethodType": "bank_transfer",
      "createdAt": "2025-01-15T10:00:00Z",
      "completedAt": "2025-01-15T10:35:00Z"
    }
  ]
}
```

---

## GET /api/agent/p2p/orders/:id

**Scope:** `wallet:read`

**Response (200):**
```json
{
  "order": {
    "id": "uuid",
    "status": "fiat_sent",
    "token": "USDC",
    "cryptoAmount": 50.0,
    "fiatAmount": 79000.0,
    "fiatCurrency": "NGN",
    "rate": 1580.0,
    "chain": "arbitrum",
    "escrowTxHash": "0x...",
    "releaseTxHash": null,
    "vendorName": "FastPay",
      "bankName": "GTBank",
      "bankAccountNumber": "0123456789",
      "bankAccountName": "John Doe",
      "bankCountryCode": "NG",
      "bankMethodType": "bank_transfer",
      "createdAt": "2025-01-15T10:00:00Z",
    "vendorAcceptedAt": "2025-01-15T10:02:00Z",
    "vendorPaidAt": "2025-01-15T10:15:00Z",
    "userConfirmedAt": null,
    "completedAt": null,
    "expiresAt": "2025-01-15T16:00:00Z"
  }
}
```

**Errors:**
- `404` — Order not found
- `403` — Order does not belong to you

---

## POST /api/agent/p2p/orders/:id/confirm

Confirm local currency received. Releases escrow to vendor on-chain. **Irreversible.**

**Scope:** `payments:execute`

**Response (200):**
```json
{
  "success": true,
  "order": {
    "id": "uuid",
    "status": "completed",
    "releaseTxHash": "0x...",
    "completedAt": "2025-01-15T10:35:00Z"
  }
}
```

**Errors:**
- `400` — Order not in `fiat_sent` status

---

## POST /api/agent/p2p/orders/:id/dispute

Open a dispute. Cancels auto-release, admin investigates.

**Scope:** `payments:execute`

**Request:**
```json
{ "reason": "Vendor marked paid but naira not received" }
```

**Response (200):**
```json
{ "success": true, "orderId": "uuid", "status": "disputed" }
```

**Errors:**
- `400` — Order not in disputable state, or cooldown not elapsed (10 min after vendor acceptance)

---

## Currency Symbols by Country

| Country | Code | Currency | Symbol |
|---------|------|----------|--------|
| Nigeria | NG | NGN | ₦ |
| Ghana | GH | GHS | GH₵ |
| Kenya | KE | KES | KSh |
| South Africa | ZA | ZAR | R |
| Cameroon | CM | XAF | FCFA |
| Senegal | SN | XOF | CFA |
| Benin | BJ | XOF | CFA |
| Togo | TG | XOF | CFA |
| Tanzania | TZ | TZS | TSh |
| Uganda | UG | UGX | USh |

Use the `fiatCurrency` field in order responses to determine which symbol to display.

---

## POST /api/agent/p2p/orders/:id/rate

Rate the vendor after a completed trade.

**Scope:** `wallet:read`

**Request:**
```json
{ "rating": 5, "comment": "Fast payment" }
```

**Response (200):**
```json
{ "success": true }
```

**Errors:**
- `400` — Invalid rating (must be 1-5), order not completed, or already rated

---

## P2P Order Statuses

| Status | Meaning |
|--------|---------|
| `escrow_locked` | Crypto locked, waiting for vendor to accept (3 min window) |
| `accepted` | Vendor accepted, will send local currency (30 min window) |
| `fiat_sent` | Vendor says payment was sent, check your bank/mobile money |
| `completed` | You confirmed receipt, escrow released to vendor |
| `disputed` | Dispute opened, admin reviewing |
| `cancelled` | Order cancelled or expired |
| `refunded` | Escrow returned to you |

---

## Auth Errors (all endpoints)

- `401` — `"No agent token provided"` — missing or malformed Authorization header
- `401` — `"Invalid or expired agent token"` — token not found, expired, or revoked
- `403` — `"Missing required scope: <scope>"` — token does not have the needed permission

---

## GET /api/agent/revenue-status

Check the user's live revenue ownership share. Requires `wallet:read` scope.

**Response (200):**
```json
{
  "ownershipPct": 12.5,
  "weight": {
    "creditBalance": 220,
    "rawWeight": 1.0,
    "streakMultiplier": 1.25,
    "effectiveWeight": 18.5,
    "consecutiveActiveWeeks": 4,
    "qualifyingActionsThisWeek": 3.5,
    "daysUntilDecay": 99
  },
  "totalPendingUsd": 0,
  "estimatedPayoutCurrentWeek": 10.0,
  "currentWeekFeesUsd": 100.0,
  "ownerPercentile": 15,
  "totalCurrentEffectiveWeight": 148.2
}
```

- `ownershipPct` — user's current % of the revenue pool
- `weight.rawWeight` — activity weight (0.0 to 1.0, decays 15%/week if inactive)
- `weight.streakMultiplier` — consecutive active weeks bonus (1.0x to 2.0x)
- `weight.effectiveWeight` — sqrt(credits) x rawWeight x streakMultiplier
- `weight.daysUntilDecay` — days until weight decays (99 = active this week, safe)
- `estimatedPayoutCurrentWeek` — projected USDC based on fees collected so far
- `ownerPercentile` — user's rank as a percentile (1 = top 1%, null = unranked)

**Errors:**
- `401` — Not authenticated
- `403` — Missing `wallet:read` scope

---

## Token Scopes

| Scope | Grants |
|-------|--------|
| `wallet:read` | balances, wallet info, history, bank accounts, P2P orders, rate vendor |
| `contacts:read` | list contacts |
| `contacts:write` | add/delete contacts |
| `payments:prepare` | prepare (preview) a payment |
| `payments:execute` | confirm payment, create P2P sell order, confirm fiat, open dispute |

All scopes are granted by default when connecting via `/api/agent/connect`.
