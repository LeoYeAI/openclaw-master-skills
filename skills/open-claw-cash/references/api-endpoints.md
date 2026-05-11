# OpenclawCash API Endpoint Details

## Requirements

- Required env var: `AGENTWALLETAPI_KEY`
- Optional env var: `AGENTWALLETAPI_URL` (default `https://openclawcash.com`)
- Required local binary for bundled CLI script: `curl`
- Optional local binary: `jq` (used for pretty JSON output when available)
- Network access: `https://openclawcash.com`

## Security Notes

- Start with read-only calls first (`wallets`, `wallet`, `balance`, `supported-tokens`), preferably on testnets.
- Write actions (`create`, `import`, `transfer`, `swap`, `approve`, `polymarket-*`) are high-risk and should use explicit confirmation in the CLI (`--yes`).
- `POST /api/agent/wallets/import` sends a private key to OpenclawCash for encrypted storage and managed execution.
- Wallet import and wallet creation are disabled unless the API key has permission enabled in dashboard (`allowWalletImport`, `allowWalletCreation`).
- API keys may also be scoped by chain (`all`/`evm`/`solana`) and by wallet (`all wallets` or a single wallet).

## API Surfaces

- **Agent API (`/api/agent/*`)**: authenticate with `X-Agent-Key`.
- Public docs intentionally include only `/api/agent/*` endpoints.

## Global User Tag (Checkout Identity)

Checkout uses one account-level user tag for seller/buyer identity.

Read current value:
```
GET /api/agent/user-tag
X-Agent-Key: occ_your_api_key
```

Set value once (immutable after set):
```
PUT /api/agent/user-tag
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request:
```json
{
  "userTag": "studio-agent"
}
```

Response:
```json
{
  "userTag": "studio-agent"
}
```

Notes:
- Tag format: lowercase letters/numbers with `.`, `_`, `-`, length 3-64.
- `PUT` returns `409 user_tag_locked` if already set.

## List Wallets

```
GET /api/agent/wallets
X-Agent-Key: occ_your_api_key
```

Returns discovery data only (id/label/address/network/chain) by default. Use `GET /api/agent/wallet` for full balances, or add `?includeBalances=true` for native balance on each listed wallet.

Response:
```json
[
  { "id": 2, "label": "Trading Bot", "address": "0x14ae8d93...", "network": "sepolia", "chain": "evm" },
  { "id": 5, "label": "SOL TEST", "address": "GmjrX8...", "network": "solana-devnet", "chain": "solana" }
]
```

Optional native balances in list response:
```
GET /api/agent/wallets?includeBalances=true
X-Agent-Key: occ_your_api_key
```

Example response:
```json
[
  {
    "id": 5,
    "label": "SOL MAIN",
    "address": "3LuJ8...",
    "network": "solana-mainnet",
    "chain": "solana",
    "balance": "0.02134 SOL",
    "nativeSymbol": "SOL"
  }
]
```

## Get Wallet Detail + Balances

```
GET /api/agent/wallet?walletId=2
X-Agent-Key: occ_your_api_key
```

Alternative:
```
GET /api/agent/wallet?walletLabel=Trading%20Bot
X-Agent-Key: occ_your_api_key
```

Alternative (by managed wallet address):
```
GET /api/agent/wallet?walletAddress=0x14ae8d93...
X-Agent-Key: occ_your_api_key
```

Optional:
```
GET /api/agent/wallet?walletId=2&chain=evm
```

Response:
```json
{
  "id": 2,
  "label": "Trading Bot",
  "address": "0x14ae8d93...",
  "network": "sepolia",
  "chain": "evm",
  "balance": "0.048 ETH",
  "nativeSymbol": "ETH",
  "otherTokenCount": 1,
  "tokenBalances": [
    { "token": "0x0000...0000", "symbol": "ETH", "balance": "0.048", "decimals": 18 },
    { "token": "0xA0b86991...", "symbol": "USDC", "balance": "250.0", "decimals": 6 }
  ]
}
```

## Create Wallet (Agent API)

```
POST /api/agent/wallets/create
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request:
```json
{
  "label": "Agent Ops Wallet",
  "network": "sepolia",
  "exportPassphrase": "your-strong-passphrase",
  "exportPassphraseStorageType": "env",
  "exportPassphraseStorageRef": "WALLET_EXPORT_PASSPHRASE_AGENT_OPS",
  "confirmExportPassphraseSaved": true
}
```

Response:
```json
{
  "id": 12,
  "label": "Agent Ops Wallet",
  "address": "0x1234...",
  "network": "sepolia",
  "chain": "evm"
}
```

Notes:
- API key must have wallet creation enabled (`allowWalletCreation`).
- Endpoint is rate-limited per API key; on limit exceeded returns `429` + `Retry-After`.
- Create requires `exportPassphrase` (minimum 12 characters).
- Create also requires `exportPassphraseStorageType` and `exportPassphraseStorageRef`.
- Agent must persist passphrase first, then send the storage fields plus `confirmExportPassphraseSaved: true`.

## Import Wallet (Agent API)

```
POST /api/agent/wallets/import
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request:
```json
{
  "label": "Treasury Imported",
  "network": "solana-mainnet",
  "privateKey": "..."
}
```

Response:
```json
{
  "id": 13,
  "label": "Treasury Imported",
  "address": "GmjrX8...",
  "network": "solana-mainnet",
  "chain": "solana"
}
```

Notes:
- API key must have wallet import enabled (`allowWalletImport`).
- Supported networks: `mainnet`, `polygon-mainnet`, `solana-mainnet`.
- Endpoint is rate-limited per API key; on limit exceeded returns `429` + `Retry-After`.

## Wallet Transaction History

```
GET /api/agent/transactions?walletId=2
X-Agent-Key: occ_your_api_key
```

Alternative:
```
GET /api/agent/transactions?walletLabel=Trading%20Bot
X-Agent-Key: occ_your_api_key
```

Alternative (by managed wallet address):
```
GET /api/agent/transactions?walletAddress=0x14ae8d93...
X-Agent-Key: occ_your_api_key
```
Optional:
```
GET /api/agent/transactions?walletId=2&chain=evm
```

Response:
```json
[
  {
    "id": 0,
    "walletId": 2,
    "hash": "5tS4...sig",
    "to": "GmjrX8...",
    "value": "1000000000",
    "fee": "5000",
    "type": "transfer",
    "status": "confirmed",
    "data": "{\"source\":\"on-chain\",\"direction\":\"incoming\",\"token\":\"SOL\"}",
    "createdAt": "2026-02-19T17:15:00.000Z"
  }
]
```

## Transfer Native or Tokens

```
POST /api/agent/transfer
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

### Fields

| Field | Type | Required | Description |
|---|---|---|---|
| walletId | number \| string | One of walletId/walletLabel/walletAddress | Wallet numeric ID or public wallet ID from list wallets |
| walletLabel | string | One of walletId/walletLabel/walletAddress | Wallet name from dashboard (or use walletAddress as alternative selector where supported) |
| chain | string | No | Optional guard: `"evm"` or `"solana"` |
| to | string | Yes | Recipient address (0x... for EVM, base58 for Solana) |
| token | string | No | Token symbol or token address/mint. Defaults to chain native token (ETH/SOL) |
| amountDisplay | string | One of amountDisplay/valueBaseUnits | Human-readable amount (e.g., "100" for 100 USDC) |
| valueBaseUnits | string | One of amountDisplay/valueBaseUnits | Amount in base units (e.g., "100000000" for 100 USDC with 6 decimals) |
| amount | string | Deprecated | Legacy alias for amountDisplay |
| value | string | Deprecated | Legacy alias for valueBaseUnits |
| memo | string | No | Solana-only transfer memo. Max 5 words, max 256 UTF-8 bytes, no control/invisible characters |

### Examples

Send 0.01 ETH:
```json
{ "walletId": 2, "to": "0xRecipient...", "amountDisplay": "0.01" }
```

Send 100 USDC by symbol:
```json
{ "walletLabel": "Trading Bot", "to": "0xRecipient...", "token": "USDC", "amountDisplay": "100" }
```

Send USDC by contract address + base units:
```json
{ "walletId": 2, "to": "0xRecipient...", "token": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "valueBaseUnits": "100000000" }
```

Send arbitrary ERC-20 by address + human amount:
```json
{ "walletId": 2, "to": "0xRecipient...", "token": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "amountDisplay": "100" }
```

Send 0.01 SOL:
```json
{ "walletId": "Q7X2K9P", "to": "SolanaRecipientWalletAddress...", "token": "SOL", "amountDisplay": "0.01" }
```
Send 0.01 SOL with memo:
```json
{ "walletId": "Q7X2K9P", "to": "SolanaRecipientWalletAddress...", "token": "SOL", "amountDisplay": "0.01", "memo": "payment verification note" }
```
Optional chain guard example:
```json
{ "chain": "solana", "walletId": "Q7X2K9P", "to": "SolanaRecipientWalletAddress...", "amountDisplay": "0.01" }
```

### Response

```json
{
  "txHash": "0xabc123...",
  "status": "confirmed",
  "token": "USDC",
  "tokenAddress": "0xA0b86991...",
  "requestedValueBaseUnits": "100000000",
  "adjustedValueBaseUnits": "100000000",
  "requestedAmountDisplay": "100",
  "adjustedAmountDisplay": "100",
  "valueBaseUnits": "100000000",
  "amountDisplay": "100",
  "fee": "1000000",
  "feePercent": "1%",
  "feeAmount": "1.0",
  "netValue": "99000000",
  "netAmount": "99.0",
  "feeWalletAddress": "0x...",
  "feeTxHash": "0xdef456...",
  "memo": "payment verification note"
}
```

Behavior notes:
- Checkout escrow destinations are enforced separately from generic transfer:
  - If `to` is an open escrow address and the transfer network or asset does not match checkout settlement rules, API returns `409` with code `unsupported_funding_network` or `unsupported_funding_asset`.
  - Error `details.acceptedFundingAssets` provides the allowed funding asset for that escrow.
  - For escrow funding, use checkout endpoints instead of generic transfer:
    - `POST /api/agent/checkout/escrows/:id/quick-pay`
    - `POST /api/agent/checkout/escrows/:id/swap-and-pay`
    - `POST /api/agent/checkout/escrows/:id/funding-confirm` (external/manual tx confirm)
- Native transfers (EVM + Solana) enforce a minimum transferable amount preflight that considers platform fee and network fee.
- For native SOL transfers, server estimates network fee and may reduce requested gross amount so transfer + platform fee + network fee fits wallet balance.
- For first-time funding of a brand-new Solana address, a larger minimum transfer may be required; too-small requests return `400` with code `amount_below_min_transfer`.
- For native SOL with configured Solana fee wallet, recipient transfer and platform fee transfer are sent in one transaction.
- Memo is accepted only for Solana wallets; providing memo on EVM returns `400 invalid_transfer_input`.
- Memo validation: max 5 words, max 256 UTF-8 bytes, rejects control/invisible characters.
- If requested transfer cannot fit after required fees, API returns `400` with code `insufficient_balance`.
- If requested native transfer is below the minimum transferable amount after fee/network preflight, API returns `400` with code `amount_below_min_transfer`.

## Check Balances

```
POST /api/agent/token-balance
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

All balances (native + discovered/default token set):
```json
{ "walletId": 2 }
```

Specific token by symbol:
```json
{ "walletId": 2, "token": "USDC" }
```

Specific token by address/mint:
```json
{ "walletId": 2, "tokenAddress": "0xA0b86991..." }
```

Response:
```json
{
  "balances": [
    { "token": "0x0000...0000", "symbol": "ETH", "balance": "0.048", "decimals": 18 },
    { "token": "0xA0b86991...", "symbol": "USDC", "balance": "250.0", "decimals": 6 },
    { "token": "0xdAC17F...", "symbol": "USDT", "balance": "0", "decimals": 6 }
  ]
}
```

## Supported Tokens

```
GET /api/agent/supported-tokens?network=mainnet
GET /api/agent/supported-tokens?network=sepolia
GET /api/agent/supported-tokens?network=solana-mainnet
GET /api/agent/supported-tokens?network=solana-devnet
GET /api/agent/supported-tokens?chain=solana
```

Requires `X-Agent-Key`. Returns **recommended common, well-known tokens** for the specified network (defaults to mainnet).
Agents can still use any valid ERC-20 token contract address on EVM and any valid SPL mint on Solana.

Response:
```json
{
  "recommendedTokens": [
    { "address": "0x0000...0000", "symbol": "ETH", "name": "Ether", "decimals": 18 },
    { "address": "0xA0b86991...", "symbol": "USDC", "name": "USD Coin", "decimals": 6 }
  ],
  "guidance": {
    "message": "These are recommended common, well-known tokens. You can still use any valid ERC-20 token on EVM or any valid SPL mint on Solana.",
    "evm": "Any valid ERC-20 token contract address is supported in agent wallet operations.",
    "solana": "Any valid SPL token mint address is supported in agent wallet operations."
  }
}
```

Notes:
- ETH is native and represented as zero-address in API payloads.
- ERC-20 addresses are network-specific (mainnet and sepolia differ).
- SOL is native on Solana and represented by `native:sol`.

## Get Swap Quote (DEX)

```
POST /api/agent/quote?network=mainnet
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request:
```json
{
  "chain": "evm",
  "tokenIn": "WETH",
  "tokenOut": "USDC",
  "amountIn": "10000000000000000"
}
```

Response:
```json
{
  "amountOut": "31234567",
  "amountOutHuman": "31.234567",
  "amountIn": "10000000000000000",
  "amountInHuman": "0.01",
  "route": "0xC02a... -> 0xA0b8...",
  "feePercent": "0.30%",
  "dex": "uniswap-v2",
  "network": "mainnet"
}
```

Solana (Jupiter) request example:
```json
{
  "chain": "solana",
  "walletId": 5,
  "tokenIn": "SOL",
  "tokenOut": "USDC",
  "amountIn": "10000000"
}
```

## Execute Swap (DEX)

```
POST /api/agent/swap
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request:
```json
{
  "chain": "evm",
  "walletId": 2,
  "tokenIn": "ETH",
  "tokenOut": "USDC",
  "amountIn": "10000000000000000",
  "slippage": 0.5
}
```

Response:
```json
{
  "txHash": "0xabc123...",
  "status": "confirmed",
  "amountOut": "7791993",
  "amountOutMin": "7753033",
  "tokenIn": "ETH",
  "tokenOut": "USDC",
  "fee": "100000000000000",
  "feePercent": "1%",
  "approvalTxHash": null,
  "feeTxHash": "0xdef456..."
}
```

If balance is insufficient for tokenIn, API returns:
```json
{
  "message": "Insufficient WETH balance in wallet 4. Available: 0 WETH, required: 0.001 WETH.",
  "code": "insufficient_token_balance",
  "walletId": 4,
  "token": "WETH",
  "available": "0",
  "required": "0.001"
}
```

Solana (Jupiter) example:
```json
{
  "chain": "solana",
  "walletId": 5,
  "tokenIn": "SOL",
  "tokenOut": "USDC",
  "amountIn": "10000000",
  "slippage": 0.5
}
```

## Checkout & Escrow (Agent API)

All checkout endpoints require:
- `X-Agent-Key: occ_your_api_key`
- Write calls require `Idempotency-Key`

### Create Pay Request

```
POST /api/agent/checkout/payreq
```

Creates a signed pay request and escrow wallet.

Timing fields (plain meaning):
- `expiresInSeconds`: deadline for buyer funding before request expires.
- `autoReleaseSeconds`: point when funded escrow can auto-release if no dispute is opened.
- `disputeWindowSeconds`: dispute window length after the auto-release point.

Validation rules:
- Minimum `3600` (1 hour) for all three fields.
- `disputeWindowSeconds` must be less than or equal to `autoReleaseSeconds`.

### Get Pay Request

```
GET /api/agent/checkout/payreq/:id
```

Returns pay request details and current escrow linkage.

### Confirm Funding

```
POST /api/agent/checkout/escrows/:id/funding-confirm
```

Validates on-chain funding using tx hash + confirmations.

### Get Escrow

```
GET /api/agent/checkout/escrows/:id
```

Returns escrow lifecycle state, tx hashes, proof/dispute fields, and settlement values.

### Accept / Proof / Dispute

```
POST /api/agent/checkout/escrows/:id/accept
POST /api/agent/checkout/escrows/:id/proof
POST /api/agent/checkout/escrows/:id/dispute
```

Use these endpoints to claim buyer role, submit proof, and open a dispute.

### Quick Pay (Direct)

```
POST /api/agent/checkout/escrows/:id/quick-pay
```

Direct funding path when buyer wallet already has enough settlement token.

### Swap And Pay

```
POST /api/agent/checkout/escrows/:id/swap-and-pay
```

Two-step flow:
- Quote with `confirm: false`
- Execute with `confirm: true`

### Release / Refund / Cancel

```
POST /api/agent/checkout/escrows/:id/release
POST /api/agent/checkout/escrows/:id/refund
POST /api/agent/checkout/escrows/:id/cancel
```

Terminal lifecycle actions for settlement or cancellation.

### Webhooks

```
GET /api/agent/checkout/webhooks
POST /api/agent/checkout/webhooks
PATCH /api/agent/checkout/webhooks/:id
DELETE /api/agent/checkout/webhooks/:id
```

Subscribe and manage escrow event deliveries (`escrow.funded`, `escrow.released`, etc.).

## Polymarket Venue Setup

- Agent endpoint setup is disabled.
- Ask your human to complete setup at: https://openclawcash.com/venues/polymarket
- After user setup is complete, use the agent venue order/read/redeem endpoints below.
- MCP convenience tool: `polymarket_market_resolve`
  - Purpose: resolve `marketUrl` or `slug` plus human-readable `outcome` to the exact `tokenId` required by order endpoints.
  - Typical MCP flow:
    1. Call `polymarket_market_resolve` with `{ marketUrl|slug, outcome }`
    2. Use returned `outcome.tokenId` in `POST /api/agent/venues/polymarket/orders/market` or `/limit`

## Polymarket Market Resolver (Agent API)

```
GET /api/agent/venues/polymarket/market/resolve?marketUrl=https://polymarket.com/market/<slug>&outcome=No
X-Agent-Key: occ_your_api_key
```

Alternative query form:

```
GET /api/agent/venues/polymarket/market/resolve?slug=<slug>&outcome=No
X-Agent-Key: occ_your_api_key
```

Response:
```json
{
  "venue": "polymarket",
  "market": {
    "slug": "market-slug",
    "question": "Will X happen?",
    "conditionId": "0x...",
    "url": "https://polymarket.com/market/market-slug",
    "active": true,
    "closed": false
  },
  "outcome": {
    "requested": "No",
    "normalized": "No",
    "index": 1,
    "tokenId": "123456789..."
  },
  "outcomes": [
    { "label": "Yes", "tokenId": "111...", "selected": false },
    { "label": "No", "tokenId": "123456789...", "selected": true }
  ]
}
```

## Polymarket Limit Order (Agent API)

```
POST /api/agent/venues/polymarket/orders/limit
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request:
```json
{
  "walletId": "Q7X2K9P",
  "tokenId": "123456",
  "side": "BUY",
  "price": 0.54,
  "size": 25
}
```

Response:
```json
{
  "venue": "polymarket",
  "status": "filled",
  "orderId": "optional-order-id",
  "txHash": "optional-tx-hash"
}
```

## Polymarket Market Order (Agent API)

```
POST /api/agent/venues/polymarket/orders/market
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request:
```json
{
  "walletId": "Q7X2K9P",
  "tokenId": "123456",
  "side": "BUY",
  "amount": 25,
  "orderType": "FAK",
  "worstPrice": 0.65
}
```

Response:
```json
{
  "venue": "polymarket",
  "status": "filled",
  "orderId": "optional-order-id",
  "txHash": "optional-tx-hash"
}
```

Notes:
- For close-position intent on open markets, prefer market `SELL` (`side: "SELL"`).
- Use limit `SELL` only when a specific target price is requested.
- `amount` semantics: `BUY` means notional/collateral amount; `SELL` means share amount.

## Polymarket Account Summary (Agent API)

```
GET /api/agent/venues/polymarket/account?walletId=Q7X2K9P
X-Agent-Key: occ_your_api_key
```

Response:
```json
{
  "venue": "polymarket",
  "walletId": "Q7X2K9P",
  "network": "polygon-mainnet",
  "account": {
    "balanceAllowance": {},
    "apiKeysCount": 1
  }
}
```

## Polymarket Open Orders (Agent API)

```
GET /api/agent/venues/polymarket/orders?walletId=Q7X2K9P&status=OPEN&limit=50
X-Agent-Key: occ_your_api_key
```

Response:
```json
{
  "venue": "polymarket",
  "walletId": "Q7X2K9P",
  "network": "polygon-mainnet",
  "items": [],
  "nextCursor": null
}
```

## Polymarket Cancel Order (Agent API)

```
POST /api/agent/venues/polymarket/orders/cancel
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request:
```json
{
  "walletId": "Q7X2K9P",
  "orderId": "your-order-id"
}
```

Response:
```json
{
  "venue": "polymarket",
  "walletId": "Q7X2K9P",
  "network": "polygon-mainnet",
  "status": "cancel_requested",
  "orderId": "your-order-id"
}
```

## Polymarket Clear Integration (Agent API)

```
POST /api/agent/venues/polymarket/unlink
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request:
```json
{
  "walletId": "Q7X2K9P"
}
```

Response:
```json
{
  "venue": "polymarket",
  "walletId": "Q7X2K9P",
  "walletAddress": "0x...",
  "network": "polygon-mainnet",
  "status": "cleared"
}
```

## Polymarket Activity (Agent API)

```
GET /api/agent/venues/polymarket/activity?walletId=Q7X2K9P&limit=50
X-Agent-Key: occ_your_api_key
```

Response:
```json
{
  "venue": "polymarket",
  "walletId": "Q7X2K9P",
  "network": "polygon-mainnet",
  "items": [],
  "nextCursor": null
}
```

## Polymarket Positions (Agent API)

```
GET /api/agent/venues/polymarket/positions?walletId=Q7X2K9P&limit=100
X-Agent-Key: occ_your_api_key
```

Response:
```json
{
  "venue": "polymarket",
  "walletId": "Q7X2K9P",
  "network": "polygon-mainnet",
  "items": [
    {
      "conditionId": "0x...",
      "question": "Will BTC be above 100k by month end?",
      "outcome": "Yes",
      "status": "OPEN",
      "size": 12.5,
      "avgPrice": 0.42,
      "curPrice": 0.47,
      "currentValue": 5.875,
      "cashPnl": 0.625,
      "percentPnl": 11.9
    }
  ]
}
```

Notes:
- Positions are sourced from Polymarket open positions (Data API-backed).
- Response is filtered to open markets only (`closed !== true`, `active !== false`, and not past `endDate`).
- Position items include `cashPnl`, `percentPnl`, and `currentValue` (with computed fallback values when upstream fields are missing).

## Polymarket Redeem (Agent API)

```
POST /api/agent/venues/polymarket/redeem
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request (single position):
```json
{
  "walletId": "Q7X2K9P",
  "tokenId": "1234567890",
  "limit": 100
}
```

Request (redeem all redeemable positions):
```json
{
  "walletId": "Q7X2K9P"
}
```

Response:
```json
{
  "venue": "polymarket",
  "walletId": "Q7X2K9P",
  "network": "polygon-mainnet",
  "mode": "single",
  "requestedTokenId": "1234567890",
  "attempted": 1,
  "successful": 1,
  "failed": 0,
  "results": [
    {
      "tokenId": "1234567890",
      "conditionId": "0x...",
      "outcomeIndex": 1,
      "sizeBaseUnits": "1000000",
      "negativeRisk": false,
      "status": "success",
      "txHash": "0xabc..."
    }
  ]
}
```

Notes:
- Gasless relay flow is used under the hood (signatureType must be proxy/safe).
- Use `tokenId` for targeted redeem; omit `tokenId` to redeem all currently redeemable positions.
- `limit` controls how many redeemable positions are scanned when listing candidates (default `100`, max `200`).

## Token Approval (ERC-20)

```
POST /api/agent/approve
Content-Type: application/json
X-Agent-Key: occ_your_api_key
```

Request:
```json
{
  "chain": "evm",
  "walletId": 2,
  "tokenAddress": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
  "spender": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
  "amount": "1000000000"
}
```

Response:
```json
{
  "txHash": "0xabc123...",
  "status": "confirmed"
}
```

Notes:
- Use base units for `amount` (e.g., USDC 1000 with 6 decimals = `1000000000`).
- ETH (native token) does not require approval.
- Wallet must have ETH for gas.

## Networks

- **mainnet**: Ethereum Mainnet (real ETH, all tokens)
- **polygon-mainnet**: Polygon PoS Mainnet (real POL + ERC-20 on Polygon)
- **sepolia**: Sepolia Testnet (test ETH, limited token selection: ETH, USDC, WETH, LINK)
- **solana-mainnet**: Solana Mainnet (real SOL + SPL tokens)
- **solana-devnet**: Solana Devnet (dev SOL + test SPL tokens)

Network is fixed at wallet creation and cannot be changed.

## Important Notes

- EVM token transfers require ETH in the wallet for gas fees
- Solana token transfers require SOL in the wallet for transaction fees
- Native SOL transfers account for network fee and may return adjusted transfer values in response
- Swap supports EVM (Uniswap) and Solana mainnet (Jupiter); Quote supports EVM and Solana mainnet; Approve is EVM-only
- Polymarket endpoints require a configured `polygon-mainnet` EVM wallet
- All Polymarket order/read/redeem endpoints require exactly one wallet selector (`walletId` or `walletAddress`)
- Platform fee is deducted from the token amount (not ETH), consistent with ETH transfers
- For transfer, use `amountDisplay` for simplicity (human-readable), use `valueBaseUnits` when you need precise base-unit control (legacy `amount`/`value` aliases are still accepted)
- Optional `chain` guard is supported on agent endpoints; mismatches return `400` with `code: "chain_mismatch"`.
