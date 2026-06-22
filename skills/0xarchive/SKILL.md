---
name: 0xarchive
version: 1.5.0
description: >
  Query historical crypto market data from 0xArchive across Hyperliquid, Lighter.xyz, and HIP-3.
  Covers orderbooks, trades, candles, funding rates, open interest, liquidations, and data quality.
  Use when the user asks about crypto market data, orderbooks, trades, funding rates, or historical prices on Hyperliquid, Lighter.xyz, or HIP-3.
allowed-tools: Bash
argument-hint: "query, e.g. 'BTC funding rate' or 'ETH 4h candles last week'"
metadata: {"openclaw":{"requires":{"env":["OXARCHIVE_API_KEY"]},"primaryEnv":"OXARCHIVE_API_KEY"}}
---

# 0xArchive API Skill

Query historical and real-time crypto market data from **0xArchive** using `curl`. Three exchanges are supported: **Hyperliquid** (perps DEX), **Lighter.xyz** (order-book DEX), and **HIP-3** (Hyperliquid builder perps). Data types: orderbooks, trades, candles, funding rates, open interest, liquidations, and data quality metrics.

## Authentication

All endpoints require the `x-api-key` header. The key is read from `$OXARCHIVE_API_KEY`.

```bash
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" "https://api.0xarchive.io/v1/..."
```

## Exchanges & Coin Naming

| Exchange | Path prefix | Coin format | Examples |
|----------|-------------|-------------|---------|
| Hyperliquid | `/v1/hyperliquid` | UPPERCASE | `BTC`, `ETH`, `SOL` |
| HIP-3 | `/v1/hyperliquid/hip3` | Case-sensitive, `builder:NAME` | `km:US500`, `xyz:GOLD`, `hyna:BTC`, `vntl:SPACEX`, `flx:TSLA`, `cash:NVDA` |
| Lighter | `/v1/lighter` | UPPERCASE | `BTC`, `ETH` |

Hyperliquid and Lighter auto-uppercase the symbol server-side. HIP-3 coin names are passed through as-is.

## Timestamps

All timestamps are **Unix milliseconds**. Use these shell helpers:

```bash
NOW=$(( $(date +%s) * 1000 ))
HOUR_AGO=$(( NOW - 3600000 ))
DAY_AGO=$(( NOW - 86400000 ))
WEEK_AGO=$(( NOW - 604800000 ))
```

## Response Format

Every response follows this shape:

```json
{
  "success": true,
  "data": [ ... ],
  "meta": {
    "count": 100,
    "request_id": "uuid",
    "next_cursor": "1706000000000"   // present when more pages exist
  }
}
```

## Endpoint Reference

### Hyperliquid (`/v1/hyperliquid`)

| Endpoint | Params | Notes |
|----------|--------|-------|
| `GET /instruments` | -- | List all instruments |
| `GET /instruments/{symbol}` | -- | Single instrument details |
| `GET /orderbook/{symbol}` | `timestamp`, `depth` | Latest or at timestamp |
| `GET /orderbook/{symbol}/history` | `start`, `end`, `limit`, `cursor`, `depth` | Historical snapshots |
| `GET /trades/{symbol}` | `start`, `end`, `limit`, `cursor` | Trade history |
| `GET /candles/{symbol}` | `start`, `end`, `limit`, `cursor`, `interval` | OHLCV candles |
| `GET /funding/{symbol}/current` | -- | Current funding rate |
| `GET /funding/{symbol}` | `start`, `end`, `limit`, `cursor`, `interval` | Funding rate history |
| `GET /openinterest/{symbol}/current` | -- | Current open interest |
| `GET /openinterest/{symbol}` | `start`, `end`, `limit`, `cursor`, `interval` | OI history |
| `GET /liquidations/{symbol}` | `start`, `end`, `limit`, `cursor` | Liquidation events |
| `GET /liquidations/{symbol}/volume` | `start`, `end`, `limit`, `cursor`, `interval` | Aggregated liquidation volume (USD) |
| `GET /liquidations/user/{address}` | `start`, `end`, `limit`, `cursor`, `coin` | Liquidations for a user |
| `GET /freshness/{symbol}` | -- | Data freshness per data type |
| `GET /summary/{symbol}` | -- | Combined market summary (price, funding, OI, volume, liquidations) |
| `GET /prices/{symbol}` | `start`, `end`, `limit`, `cursor`, `interval` | Mark/oracle/mid price history |
| `GET /orders/{symbol}/history` | `start`, `end`, `user`, `status`, `order_type`, `limit`, `cursor` | Order history with user attribution (Build+) |
| `GET /orders/{symbol}/flow` | `start`, `end`, `interval`, `limit` | Order flow aggregation (Build+) |
| `GET /orders/{symbol}/tpsl` | `start`, `end`, `user`, `triggered`, `limit`, `cursor` | TP/SL order history (Pro+) |
| `GET /orderbook/{symbol}/l4` | `timestamp`, `depth` | L4 orderbook reconstruction (Pro+) |
| `GET /orderbook/{symbol}/l4/diffs` | `start`, `end`, `limit`, `cursor` | L4 orderbook diffs (Build+) |
| `GET /orderbook/{symbol}/l4/history` | `start`, `end`, `limit`, `cursor` | L4 orderbook checkpoints (Pro+) |

### HIP-3 (`/v1/hyperliquid/hip3`)

Coin names are **case-sensitive** (e.g., `km:US500`). Orderbook requires Pro+ tier.

| Endpoint | Params | Notes |
|----------|--------|-------|
| `GET /instruments` | -- | List HIP-3 instruments |
| `GET /instruments/{coin}` | -- | Single instrument |
| `GET /orderbook/{coin}` | `timestamp`, `depth` | Requires Pro+ tier |
| `GET /orderbook/{coin}/history` | `start`, `end`, `limit`, `cursor`, `depth` | Requires Pro+ tier |
| `GET /trades/{coin}` | `start`, `end`, `limit`, `cursor` | Trade history |
| `GET /trades/{coin}/recent` | `limit` | Recent trades (no time range needed) |
| `GET /candles/{coin}` | `start`, `end`, `limit`, `cursor`, `interval` | OHLCV candles |
| `GET /funding/{coin}/current` | -- | Current funding rate |
| `GET /funding/{coin}` | `start`, `end`, `limit`, `cursor`, `interval` | Funding history |
| `GET /openinterest/{coin}/current` | -- | Current OI |
| `GET /openinterest/{coin}` | `start`, `end`, `limit`, `cursor`, `interval` | OI history |
| `GET /liquidations/{coin}` | `start`, `end`, `limit`, `cursor` | Liquidation events |
| `GET /liquidations/{coin}/volume` | `start`, `end`, `limit`, `cursor`, `interval` | Aggregated liquidation volume (USD) |
| `GET /freshness/{coin}` | -- | Data freshness per data type |
| `GET /summary/{coin}` | -- | Combined market summary (price, funding, OI) |
| `GET /prices/{coin}` | `start`, `end`, `limit`, `cursor`, `interval` | Mark/oracle/mid price history |
| `GET /orders/{coin}/history` | `start`, `end`, `user`, `status`, `order_type`, `limit`, `cursor` | Order history with user attribution (Build+) |
| `GET /orders/{coin}/flow` | `start`, `end`, `interval`, `limit` | Order flow aggregation (Build+) |
| `GET /orders/{coin}/tpsl` | `start`, `end`, `user`, `triggered`, `limit`, `cursor` | TP/SL order history (Pro+) |
| `GET /orderbook/{coin}/l4` | `timestamp`, `depth` | L4 orderbook reconstruction (Pro+) |
| `GET /orderbook/{coin}/l4/diffs` | `start`, `end`, `limit`, `cursor` | L4 orderbook diffs (Build+) |
| `GET /orderbook/{coin}/l4/history` | `start`, `end`, `limit`, `cursor` | L4 orderbook checkpoints (Pro+) |

### Lighter (`/v1/lighter`)

Same data types as Hyperliquid except: no liquidations. Adds `granularity` on orderbook history and `/recent` trades.

| Endpoint | Params | Notes |
|----------|--------|-------|
| `GET /instruments` | -- | List Lighter instruments |
| `GET /instruments/{symbol}` | -- | Single instrument |
| `GET /orderbook/{symbol}` | `timestamp`, `depth` | Latest or at timestamp |
| `GET /orderbook/{symbol}/history` | `start`, `end`, `limit`, `cursor`, `depth`, `granularity` | Default granularity: `checkpoint` |
| `GET /trades/{symbol}` | `start`, `end`, `limit`, `cursor` | Trade history |
| `GET /trades/{symbol}/recent` | `limit` | Recent trades (no time range needed) |
| `GET /candles/{symbol}` | `start`, `end`, `limit`, `cursor`, `interval` | OHLCV candles |
| `GET /funding/{symbol}/current` | -- | Current funding rate |
| `GET /funding/{symbol}` | `start`, `end`, `limit`, `cursor`, `interval` | Funding history |
| `GET /openinterest/{symbol}/current` | -- | Current OI |
| `GET /openinterest/{symbol}` | `start`, `end`, `limit`, `cursor`, `interval` | OI history |
| `GET /freshness/{symbol}` | -- | Data freshness per data type |
| `GET /summary/{symbol}` | -- | Combined market summary (price, funding, OI) |
| `GET /prices/{symbol}` | `start`, `end`, `limit`, `cursor`, `interval` | Mark/oracle price history |
| `GET /l3orderbook/{symbol}` | `timestamp`, `depth`, `account` | L3 order-level orderbook (Pro+) |
| `GET /l3orderbook/{symbol}/history` | `start`, `end`, `limit`, `cursor`, `granularity`, `account` | Historical L3 snapshots (Pro+) |

### Data Quality (`/v1/data-quality`)

| Endpoint | Params | Notes |
|----------|--------|-------|
| `GET /status` | -- | System health status |
| `GET /coverage` | -- | Coverage summary, all exchanges |
| `GET /coverage/{exchange}` | -- | Coverage for one exchange |
| `GET /coverage/{exchange}/{symbol}` | `from`, `to` | Symbol-level coverage + gaps |
| `GET /incidents` | `status`, `exchange`, `since`, `limit`, `offset` | List incidents |
| `GET /incidents/{id}` | -- | Single incident |
| `GET /latency` | -- | Ingestion latency metrics |
| `GET /sla` | `year`, `month` | SLA compliance report |

### WebSocket Channels

Additional real-time channels available via WebSocket (`wss://api.0xarchive.io/ws?apiKey=KEY`):

| Channel | Notes |
|---------|-------|
| `l4_diffs` | L4 orderbook diffs with user attribution (Build+, real-time only) |
| `l4_orders` | Order lifecycle events with user attribution (Build+, real-time only) |
| `lighter_l3_orderbook` | Lighter L3 order-level orderbook snapshots (Pro+, historical only) |
| `hip3_liquidations` | HIP-3 liquidation events with long/short direction (Build+, historical only) |
| `hip3_l4_diffs` | HIP-3 L4 orderbook diffs (Build+, real-time only) |
| `hip3_l4_orders` | HIP-3 order lifecycle events (Build+, real-time only) |

### Web3 Authentication (`/v1`)

Get API keys programmatically using an Ethereum wallet (SIWE). No API key required for these endpoints.

| Endpoint | Params | Notes |
|----------|--------|-------|
| `POST /auth/web3/challenge` | `address` (wallet address) | Returns SIWE message to sign |
| `POST /web3/signup` | `message`, `signature` | Returns free-tier API key |
| `POST /web3/keys` | `message`, `signature` | List all keys for wallet |
| `POST /web3/keys/revoke` | `message`, `signature`, `key_id` | Revoke a key |
| `POST /web3/subscribe` | `tier` (`build` or `pro`), `payment-signature` header | x402 USDC subscription (see flow below) |

**Free-tier flow:** Call `/auth/web3/challenge` with wallet address → sign the returned message with `personal_sign` (EIP-191) → submit to `/web3/signup` with the message and signature → receive API key.

**Paid-tier flow (x402):**

1. `POST /web3/subscribe` with `{ "tier": "build" }` → server returns 402 with `payment.amount` (micro-USDC), `payment.pay_to` (treasury address), `payment.network`.
2. Sign an EIP-712 `TransferWithAuthorization` (EIP-3009) on USDC Base:
   - Domain: `{ name: "USD Coin", version: "2", chainId: 8453, verifyingContract: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913" }`
   - Type: `TransferWithAuthorization(address from, address to, uint256 value, uint256 validAfter, uint256 validBefore, bytes32 nonce)`
   - Message: `{ from: <wallet>, to: <pay_to>, value: <amount>, validAfter: 0, validBefore: <now+3600>, nonce: <32 random bytes hex> }`
3. Build x402 v2 payment payload:
   ```json
   {
     "x402Version": 2,
     "payload": {
       "signature": "0x<EIP-712 signature hex>",
       "authorization": {
         "from": "0x<wallet>",
         "to": "0x<pay_to from step 1>",
         "value": "<amount as string>",
         "validAfter": "0",
         "validBefore": "<unix timestamp as string>",
         "nonce": "0x<64 hex chars>"
       }
     }
   }
   ```
4. Base64-encode the JSON and retry: `POST /web3/subscribe` with `{ "tier": "build" }` and header `payment-signature: <base64 payload>` → receive API key + subscription.

**Important:** All `authorization` values (`value`, `validAfter`, `validBefore`) must be strings, not numbers. See `scripts/web3_subscribe.py` for a complete working Python implementation.

## Common Parameters

| Param | Type | Description |
|-------|------|-------------|
| `start` | int | Start timestamp (Unix ms). Defaults to 24h ago. |
| `end` | int | End timestamp (Unix ms). Defaults to now. |
| `limit` | int | Max records. Default 100, max 1000 (max 10000 for candles). |
| `cursor` | string | Pagination cursor from `meta.next_cursor`. |
| `interval` | string | Candle interval: `1m`, `5m`, `15m`, `30m`, `1h`, `4h`, `1d`, `1w`. Default: `1h`. For OI/funding: `5m`, `15m`, `30m`, `1h`, `4h`, `1d`. Omit for raw data. |
| `depth` | int | Orderbook depth (number of price levels per side). |
| `granularity` | string | Lighter orderbook resolution: `checkpoint` (default), `30s`, `10s`, `1s`, `tick`. |
| `account` | int | Lighter L3 orderbook: filter by account index (e.g., `281474976710654` for LLP vault). |

## Smart Defaults

When the user does not specify a time range, default to the **last 24 hours**:

```bash
NOW=$(( $(date +%s) * 1000 ))
DAY_AGO=$(( NOW - 86400000 ))
```

For candles with no explicit range, default to a range that makes sense for the interval (e.g., last 7 days for 4h candles, last 30 days for 1d candles).

## Pagination

When `meta.next_cursor` is present in the response, more data is available. Append `&cursor=VALUE` to fetch the next page:

```bash
# First page
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/trades/BTC?start=$START&end=$END&limit=1000"

# Next page (use next_cursor from previous response)
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/trades/BTC?start=$START&end=$END&limit=1000&cursor=1706000000000_12345"
```

## Tier Limits

| Tier | Price | Coins | Orderbook Depth | Lighter Granularity | Historical Depth | Rate Limit |
|------|-------|-------|-----------------|---------------------|------------------|------------|
| Free | $0 | BTC only (HIP-3: km:US500 only) | 20 levels | -- | 30 days | 15 RPS |
| Build | $49/mo | All | 50 levels | checkpoint, 30s, 10s | 1 year | 50 RPS |
| Pro | $199/mo | All | 100 levels | + 1s | Full history | 150 RPS |
| Enterprise | Custom | All | Full depth | + tick | Full history | Custom |

## Error Handling

| HTTP Status | Meaning | Action |
|-------------|---------|--------|
| 400 | Bad request / validation error | Check params (missing start/end, invalid interval) |
| 401 | Missing or invalid API key | Set `$OXARCHIVE_API_KEY` |
| 403 | Tier restriction | Upgrade plan (e.g., non-BTC coin on Free tier) |
| 404 | Symbol not found | Check coin name spelling and exchange |
| 429 | Rate limited | Back off and retry |

Error responses return `{ "code": 400, "error": "description" }`.

## Example Queries

```bash
# List Hyperliquid instruments
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/instruments" | jq '.data | length'

# Current BTC orderbook (top 10 levels)
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/orderbook/BTC?depth=10" | jq '.data'

# ETH trades from the last hour
NOW=$(( $(date +%s) * 1000 )); HOUR_AGO=$(( NOW - 3600000 ))
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/trades/ETH?start=$HOUR_AGO&end=$NOW&limit=100" | jq '.data'

# SOL 4h candles for the last week
NOW=$(( $(date +%s) * 1000 )); WEEK_AGO=$(( NOW - 604800000 ))
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/candles/SOL?start=$WEEK_AGO&end=$NOW&interval=4h" | jq '.data'

# Current BTC funding rate
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/funding/BTC/current" | jq '.data'

# BTC open interest aggregated to 1h intervals (last week)
NOW=$(( $(date +%s) * 1000 )); WEEK_AGO=$(( NOW - 604800000 ))
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/openinterest/BTC?start=$WEEK_AGO&end=$NOW&interval=1h" | jq '.data'

# ETH funding rates aggregated to 4h intervals (last 30 days)
NOW=$(( $(date +%s) * 1000 )); MONTH_AGO=$(( NOW - 2592000000 ))
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/funding/ETH?start=$MONTH_AGO&end=$NOW&interval=4h" | jq '.data'

# HIP-3 km:US500 candles (last 24h, 1h interval)
NOW=$(( $(date +%s) * 1000 )); DAY_AGO=$(( NOW - 86400000 ))
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/hip3/candles/km:US500?start=$DAY_AGO&end=$NOW&interval=1h" | jq '.data'

# Lighter BTC orderbook history (30s granularity, last hour)
NOW=$(( $(date +%s) * 1000 )); HOUR_AGO=$(( NOW - 3600000 ))
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/lighter/orderbook/BTC/history?start=$HOUR_AGO&end=$NOW&granularity=30s&limit=100" | jq '.data'

# System health status
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/data-quality/status" | jq '.'

# SLA report for current month
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/data-quality/sla" | jq '.'

# BTC market summary (price, funding, OI, volume, liquidations in one call)
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/summary/BTC" | jq '.data'

# BTC data freshness (lag per data type)
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/freshness/BTC" | jq '.data'

# BTC price history (mark/oracle/mid) aggregated to 1h
NOW=$(( $(date +%s) * 1000 )); DAY_AGO=$(( NOW - 86400000 ))
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/prices/BTC?start=$DAY_AGO&end=$NOW&interval=1h" | jq '.data'

# BTC liquidation volume aggregated to 4h buckets
NOW=$(( $(date +%s) * 1000 )); WEEK_AGO=$(( NOW - 604800000 ))
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/hyperliquid/liquidations/BTC/volume?start=$WEEK_AGO&end=$NOW&interval=4h" | jq '.data'

# Data coverage for Hyperliquid BTC
curl -s -H "x-api-key: $OXARCHIVE_API_KEY" \
  "https://api.0xarchive.io/v1/data-quality/coverage/hyperliquid/BTC" | jq '.'
```

