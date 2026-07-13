---
name: aster-futures
description: Aster Futures request using the Aster API. Authentication uses EIP-712 ECDSA signing with API wallet. Supports mainnet.
metadata:
  version: 1.0.0
  author: Aster
license: MIT
---

# Aster Futures Skill

Futures request on Aster using authenticated API endpoints. Authentication uses EIP-712 ECDSA signing with API wallet (main wallet + signer wallet). Return the result in JSON format.

## Data Fetching Guidelines (CRITICAL)

**NEVER truncate JSON responses** with `head -c`, `head -n`, or similar — truncated JSON is corrupted and will produce wrong results.

### Mandatory Rules

1. **Always specify `symbol` parameter** when querying a specific trading pair. Many endpoints return ALL symbols when `symbol` is omitted, producing responses of 100KB+.
2. **Always use `limit` parameter** to constrain result size. Use the smallest limit that satisfies the request (e.g., `limit=5` instead of default 500).
3. **Use `jq` to extract fields** — never parse raw mega-JSON visually. Pipe through `jq` to select only needed data.

### Progressive Data Exploration Strategy

When the user asks a broad question (e.g., "what futures are available?"), use a **layered approach**:

1. **Step 1 — Get lightweight summary first:**
   ```bash
   # Get just the symbol list, not full exchangeInfo
   curl -s "https://fapi.asterdex.com/fapi/v3/exchangeInfo" | jq '[.symbols[].symbol]'
   ```

2. **Step 2 — Confirm scope with user** before fetching detailed data for many symbols.

3. **Step 3 — Fetch details for specific symbols only:**
   ```bash
   # Get price for ONE symbol, not all
   curl -s "https://fapi.asterdex.com/fapi/v3/ticker/price?symbol=BTCUSDT"
   ```

### Endpoints That Return Dangerously Large Data (without symbol filter)

| Endpoint | Without `symbol` | With `symbol` |
|----------|------------------|---------------|
| `/fapi/v3/exchangeInfo` | ALL symbols + filters (100KB+) | N/A — use `jq` to filter |
| `/fapi/v3/ticker/24hr` | ALL symbols (50KB+) | Single object (~500B) |
| `/fapi/v3/ticker/price` | ALL symbols (10KB+) | Single object (~80B) |
| `/fapi/v3/ticker/bookTicker` | ALL symbols (20KB+) | Single object (~150B) |
| `/fapi/v3/premiumIndex` | ALL symbols (30KB+) | Single object (~300B) |
| `/fapi/v3/depth` | N/A (symbol required) | Varies by `limit`: use `limit=5` for overview |
| `/fapi/v3/klines` | N/A (symbol required) | Default 500 candles — always set `limit` |
| `/fapi/v3/trades` | N/A (symbol required) | Default 500 trades — always set `limit` |

### Example: Safe vs Unsafe

```bash
# BAD — returns ALL symbols, then truncates = corrupted JSON
curl -s ".../fapi/v3/ticker/price" | head -c 5000

# GOOD — returns single symbol, complete JSON
curl -s ".../fapi/v3/ticker/price?symbol=BTCUSDT"

# BAD — 500 candles by default
curl -s ".../fapi/v3/klines?symbol=BTCUSDT&interval=1h"

# GOOD — only 5 candles
curl -s ".../fapi/v3/klines?symbol=BTCUSDT&interval=1h&limit=5"

# GOOD — extract just symbol names from exchangeInfo
curl -s ".../fapi/v3/exchangeInfo" | jq '[.symbols[] | {symbol, status}]'
```

---

## Quick Reference

| Endpoint | Description | Required | Optional | Authentication |
|----------|-------------|----------|----------|----------------|
| `/fapi/v3/ping` (GET) | Test connectivity | None | None | No |
| `/fapi/v3/time` (GET) | Check server time | None | None | No |
| `/fapi/v3/exchangeInfo` (GET) | Exchange information | None | None | No |
| `/fapi/v3/depth` (GET) | Order book | symbol | limit | No |
| `/fapi/v3/trades` (GET) | Recent trades list | symbol | limit | No |
| `/fapi/v3/historicalTrades` (GET) | Old trades lookup | symbol | limit, fromId | Yes |
| `/fapi/v3/aggTrades` (GET) | Compressed/Aggregate trades list | symbol | fromId, startTime, endTime, limit | No |
| `/fapi/v3/klines` (GET) | Kline/Candlestick data | symbol, interval | startTime, endTime, limit | No |
| `/fapi/v3/indexPriceKlines` (GET) | Index price kline data | pair, interval | startTime, endTime, limit | No |
| `/fapi/v3/markPriceKlines` (GET) | Mark price kline data | symbol, interval | startTime, endTime, limit | No |
| `/fapi/v3/premiumIndex` (GET) | Mark price and funding rate | None | symbol | No |
| `/fapi/v3/fundingRate` (GET) | Funding rate history | None | symbol, startTime, endTime, limit | No |
| `/fapi/v3/ticker/24hr` (GET) | 24hr ticker price change statistics | None | symbol | No |
| `/fapi/v3/ticker/price` (GET) | Symbol price ticker | None | symbol | No |
| `/fapi/v3/ticker/bookTicker` (GET) | Symbol order book ticker | None | symbol | No |
| `/fapi/v3/order` (POST) | New order | symbol, side, type, timestamp | positionSide, timeInForce, quantity, reduceOnly, price, newClientOrderId, stopPrice, closePosition, activationPrice, callbackRate, workingType, priceProtect, newOrderRespType, recvWindow | Yes |
| `/fapi/v3/batchOrders` (POST) | Place multiple orders | batchOrders, timestamp | recvWindow | Yes |
| `/fapi/v3/order` (GET) | Query order | symbol, timestamp | orderId, origClientOrderId, recvWindow | Yes |
| `/fapi/v3/order` (DELETE) | Cancel order | symbol, timestamp | orderId, origClientOrderId, recvWindow | Yes |
| `/fapi/v3/allOpenOrders` (DELETE) | Cancel all open orders | symbol, timestamp | recvWindow | Yes |
| `/fapi/v3/batchOrders` (DELETE) | Cancel multiple orders | symbol, timestamp | orderIdList, origClientOrderIdList, recvWindow | Yes |
| `/fapi/v3/countdownCancelAll` (POST) | Auto-cancel all open orders (countdown) | symbol, countdownTime, timestamp | recvWindow | Yes |
| `/fapi/v3/openOrder` (GET) | Query current open order | symbol, timestamp | orderId, origClientOrderId, recvWindow | Yes |
| `/fapi/v3/openOrders` (GET) | Current all open orders | timestamp | symbol, recvWindow | Yes |
| `/fapi/v3/allOrders` (GET) | All orders | symbol, timestamp | orderId, startTime, endTime, limit, recvWindow | Yes |
| `/fapi/v3/balance` (GET) | Futures account balance | timestamp | recvWindow | Yes |
| `/fapi/v3/account` (GET) | Account information | timestamp | recvWindow | Yes |
| `/fapi/v3/leverage` (POST) | Change initial leverage | symbol, leverage, timestamp | recvWindow | Yes |
| `/fapi/v3/marginType` (POST) | Change margin type | symbol, marginType, timestamp | recvWindow | Yes |
| `/fapi/v3/positionMargin` (POST) | Modify isolated position margin | symbol, amount, type, timestamp | positionSide, recvWindow | Yes |
| `/fapi/v3/positionMargin/history` (GET) | Position margin change history | symbol, timestamp | type, startTime, endTime, limit, recvWindow | Yes |
| `/fapi/v3/positionRisk` (GET) | Position information | timestamp | symbol, recvWindow | Yes |
| `/fapi/v3/positionSide/dual` (POST) | Change position mode | dualSidePosition, timestamp | recvWindow | Yes |
| `/fapi/v3/positionSide/dual` (GET) | Get current position mode | timestamp | recvWindow | Yes |
| `/fapi/v3/multiAssetsMargin` (POST) | Change multi-assets mode | multiAssetsMargin, timestamp | recvWindow | Yes |
| `/fapi/v3/multiAssetsMargin` (GET) | Get current multi-assets mode | timestamp | recvWindow | Yes |
| `/fapi/v3/asset/wallet/transfer` (POST) | Transfer between futures and spot | amount, asset, clientTranId, kindType, timestamp | None | Yes |
| `/fapi/v3/userTrades` (GET) | Account trade list | symbol, timestamp | startTime, endTime, fromId, limit, recvWindow | Yes |
| `/fapi/v3/income` (GET) | Get income history | timestamp | symbol, incomeType, startTime, endTime, limit, recvWindow | Yes |
| `/fapi/v3/leverageBracket` (GET) | Notional and leverage brackets | timestamp | symbol, recvWindow | Yes |
| `/fapi/v3/adlQuantile` (GET) | Position ADL quantile estimation | timestamp | symbol, recvWindow | Yes |
| `/fapi/v3/forceOrders` (GET) | User's force orders | timestamp | symbol, autoCloseType, startTime, endTime, limit, recvWindow | Yes |
| `/fapi/v3/commissionRate` (GET) | User commission rate | symbol, timestamp | recvWindow | Yes |
| `/fapi/v3/listenKey` (POST) | Start user data stream | None | None | Yes |
| `/fapi/v3/listenKey` (PUT) | Keepalive user data stream | None | None | Yes |
| `/fapi/v3/listenKey` (DELETE) | Close user data stream | None | None | Yes |
| `GET /bapi/futures/v1/public/future/aster/deposit/assets` | Get all deposit assets | chainIds, accountType | networks | No |
| `GET /bapi/futures/v1/public/future/aster/withdraw/assets` | Get all withdraw assets | chainIds, accountType | networks | No |
| `GET /bapi/futures/v1/public/future/aster/estimate-withdraw-fee` | Estimate withdraw fee | chainId, network, currency, accountType | None | No |
| `POST /fapi/aster/user-withdraw` | Withdraw by API (EVM Futures) | chainId, asset, amount, fee, receiver, nonce, userSignature, timestamp, signature | recvWindow | Yes |
| `POST /fapi/aster/user-solana-withdraw` | Withdraw by API (Solana Futures) | chainId, asset, amount, fee, receiver, timestamp, signature | recvWindow | Yes |

---

## Parameters

### Common Parameters

* **symbol**: Trading pair symbol (e.g., BTCUSDT)
* **pair**: Trading pair for index price endpoints (e.g., BTCUSDT)
* **side**: Order side BUY or SELL
* **type**: Order type (LIMIT, MARKET, STOP, STOP_MARKET, TAKE_PROFIT, TAKE_PROFIT_MARKET, TRAILING_STOP_MARKET)
* **positionSide**: Position side; default BOTH for One-way Mode; LONG/SHORT for Hedge Mode
* **timeInForce**: Time in force (GTC, IOC, FOK, GTX)
* **quantity**: Order quantity (e.g., 0.1)
* **price**: Order price (e.g., 50000)
* **stopPrice**: Stop price for STOP/STOP_MARKET/TAKE_PROFIT/TAKE_PROFIT_MARKET orders
* **closePosition**: Close-All flag; "true" or "false"; cannot be used with quantity
* **activationPrice**: Activation price for TRAILING_STOP_MARKET orders
* **callbackRate**: Callback rate for TRAILING_STOP_MARKET; range 0.1-5
* **workingType**: Stop price trigger type; "MARK_PRICE" or "CONTRACT_PRICE"
* **priceProtect**: Price protection flag; "TRUE" or "FALSE"
* **reduceOnly**: Reduce-only flag; default "false"
* **newClientOrderId**: Unique client order ID
* **newOrderRespType**: Response type; "ACK" or "RESULT"
* **orderId**: Order ID (e.g., 22542179)
* **origClientOrderId**: Original client order ID
* **orderIdList**: List of order IDs to cancel (max 10)
* **origClientOrderIdList**: List of client order IDs to cancel (max 10)
* **batchOrders**: List of order objects (max 5)
* **countdownTime**: Countdown time in milliseconds; set to 0 to cancel countdown
* **leverage**: Leverage value; range 1-125
* **marginType**: Margin type; ISOLATED or CROSSED
* **amount**: Margin amount for position margin modification
* **dualSidePosition**: Position mode; "true" = Hedge Mode; "false" = One-way Mode
* **multiAssetsMargin**: Multi-assets mode; "true" = Multi-Assets Mode; "false" = Single-Asset Mode
* **asset**: Asset name (e.g., USDT)
* **clientTranId**: Client transfer ID (unique within 7 days)
* **kindType**: Transfer direction; FUTURE_SPOT or SPOT_FUTURE
* **incomeType**: Income type filter (TRANSFER, WELCOME_BONUS, REALIZED_PNL, FUNDING_FEE, COMMISSION, INSURANCE_CLEAR, MARKET_MERCHANT_RETURN_REWARD)
* **autoCloseType**: Force order type; LIQUIDATION or ADL
* **fromId**: ID to get trades from INCLUSIVE (e.g., 1)
* **startTime**: Timestamp in ms to filter from INCLUSIVE (e.g., 1735693200000)
* **endTime**: Timestamp in ms to filter until INCLUSIVE (e.g., 1735693200000)
* **limit**: Result limit; varies per endpoint (e.g., 500)
* **interval**: Kline interval (e.g., 1h)
* **recvWindow**: Request validity window; cannot be greater than 60000 (e.g., 5000)
* **timestamp**: Request timestamp in milliseconds (e.g., 1735693200000)
* **chainIds**: Chain ID(s), comma-separated (for deposit/withdraw asset queries)
* **chainId**: Chain ID (for withdraw operations)
* **networks**: Network type (EVM, SOLANA), comma-separated
* **network**: Network type (EVM, SOL)
* **currency**: Currency name (e.g., ASTER)
* **accountType**: Account type (spot, perp)
* **fee**: Withdraw fee in token units
* **receiver**: Receipt address for withdrawals
* **nonce**: Unique number for signing (microsecond timestamp for API auth; milliseconds x 1000 for EIP712 withdraw)
* **userSignature**: EIP712 signature for EVM withdrawals
* **signature**: ECDSA API signature

### Enums

* **side**: BUY | SELL
* **positionSide**: BOTH | LONG | SHORT
* **type** (order): LIMIT | MARKET | STOP | STOP_MARKET | TAKE_PROFIT | TAKE_PROFIT_MARKET | TRAILING_STOP_MARKET
* **timeInForce**: GTC | IOC | FOK | GTX
* **workingType**: MARK_PRICE | CONTRACT_PRICE
* **marginType**: ISOLATED | CROSSED
* **newOrderRespType**: ACK | RESULT
* **interval**: 1m | 3m | 5m | 15m | 30m | 1h | 2h | 4h | 6h | 8h | 12h | 1d | 3d | 1w | 1M
* **orderStatus**: NEW | PARTIALLY_FILLED | FILLED | CANCELED | REJECTED | EXPIRED
* **contractStatus**: PENDING_TRADING | TRADING | PRE_SETTLE | SETTLING | CLOSE
* **incomeType**: TRANSFER | WELCOME_BONUS | REALIZED_PNL | FUNDING_FEE | COMMISSION | INSURANCE_CLEAR | MARKET_MERCHANT_RETURN_REWARD
* **autoCloseType**: LIQUIDATION | ADL
* **kindType**: FUTURE_SPOT | SPOT_FUTURE
* **positionMarginType**: 1 (add margin) | 2 (reduce margin)

## Authentication

For endpoints that require authentication, you will need to provide Aster API credentials.
Required credentials:

* **Main Wallet Address (user)**: Your Aster main wallet address
* **API Wallet Address (signer)**: Your API wallet address (obtained via Pro API registration at asterdex.com)
* **API Wallet Private Key**: Your API wallet private key (for ECDSA signing)

Base URLs:
* Mainnet REST: https://fapi.asterdex.com
* Mainnet WebSocket: wss://fstream.asterdex.com
* Deposit/Withdraw Portal: https://www.asterdex.com

See [`references/authentication.md`](./references/authentication.md) for implementation details.

## Security

### Share Credentials

Users can provide Aster API credentials by sending a file where the content is in the following format:

```bash
0x1234...abcd
0x5678...efgh
private_key_hex...
```

Line 1: Main wallet address (user)
Line 2: API wallet address (signer)
Line 3: API wallet private key

### Never Display Full Secrets

When showing credentials to users:
- **Main Wallet:** Show first 6 + last 4 characters: `0x1234...abcd`
- **API Wallet:** Show first 6 + last 4 characters: `0x5678...efgh`
- **Private Key:** Always mask, show only last 5: `***...f1a2b`

Example response when asked for credentials:
Account: main
Main Wallet: 0x1234...abcd
API Wallet: 0x5678...efgh
Private Key: ***...f1a2b
Environment: Mainnet

### Listing Accounts

When listing accounts, show names and environment only -- never keys:
Aster Accounts:
* main (Mainnet)
* trading-01 (Mainnet)
* arb-bot (Mainnet)

### Transactions in Mainnet

When performing transactions in mainnet, always confirm with the user before proceeding by asking them to write "CONFIRM" to proceed.

---

## Aster Accounts

### main
- Main Wallet: your_main_wallet_address
- API Wallet: your_api_wallet_address
- Private Key: your_api_wallet_private_key
- Description: Primary trading account

### TOOLS.md Structure

```bash
## Aster Accounts

### main
- Main Wallet: 0x1234...abcd
- API Wallet: 0x5678...efgh
- Private Key: private_key_hex...
- Description: Primary trading account

### trading-01
- Main Wallet: 0xaaaa...1111
- API Wallet: 0xbbbb...2222
- Private Key: private_key_hex...
- Description: Automated trading

### arb-bot
- Main Wallet: 0xcccc...3333
- API Wallet: 0xdddd...4444
- Private Key: private_key_hex...
- Description: Arbitrage bot account
```

## Agent Behavior

1. Credentials requested: Mask private keys (show last 5 chars only), mask wallet addresses (show first 6 + last 4)
2. Listing accounts: Show names and environment, never keys
3. Account selection: Ask if ambiguous, default to main
4. When doing a transaction in mainnet, confirm with user before by asking to write "CONFIRM" to proceed
5. New credentials: Prompt for name, main wallet, API wallet, private key

## Adding New Accounts

When user provides new credentials:

* Ask for account name
* Ask for main wallet address (user)
* Ask for API wallet address (signer)
* Ask for API wallet private key
* Store in `TOOLS.md` with masked display confirmation

## Signing Requests

All authenticated endpoints require EIP-712 ECDSA signature:

1. Collect all API parameters as key-value pairs (all values as strings)
2. Sort parameters by ASCII key order
3. Combine sorted parameters with `user` (main wallet address), `signer` (API wallet address), and `nonce` (microsecond timestamp) using Web3 ABI encoding
4. Generate Keccak256 hash of the ABI-encoded data
5. Sign the hash with the API wallet's private key via ECDSA
6. Include `user`, `signer`, `nonce`, and `signature` in the request
7. Timestamp must be current milliseconds; request valid within recvWindow (default 5000ms)

See [`references/authentication.md`](./references/authentication.md) for implementation details.
