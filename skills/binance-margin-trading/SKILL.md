---
name: margin-trading
description: Binance Margin-trading request using the Binance API. Authentication requires API key and secret key. 
metadata:
  version: 1.0.0
  author: Binance
license: MIT
---

# Binance Margin-trading Skill

Margin-trading request on Binance using authenticated API endpoints. Requires API key and secret key for certain endpoints. Return the result in JSON format.

## Quick Reference

| Endpoint | Description | Required | Optional | Authentication |
|----------|-------------|----------|----------|----------------|
| `/sapi/v1/margin/max-leverage` (POST) | Adjust cross margin max leverage (USER_DATA) | maxLeverage | None | Yes |
| `/sapi/v1/margin/isolated/account` (DELETE) | Disable Isolated Margin Account (TRADE) | symbol | recvWindow | Yes |
| `/sapi/v1/margin/isolated/account` (POST) | Enable Isolated Margin Account (TRADE) | symbol | recvWindow | Yes |
| `/sapi/v1/margin/isolated/account` (GET) | Query Isolated Margin Account Info (USER_DATA) | None | symbols, recvWindow | Yes |
| `/sapi/v1/bnbBurn` (GET) | Get BNB Burn Status (USER_DATA) | None | recvWindow | Yes |
| `/sapi/v1/margin/tradeCoeff` (GET) | Get Summary of Margin account (USER_DATA) | None | recvWindow | Yes |
| `/sapi/v1/margin/capital-flow` (GET) | Query Cross Isolated Margin Capital Flow (USER_DATA) | None | asset, symbol, type, startTime, endTime, fromId, limit, recvWindow | Yes |
| `/sapi/v1/margin/account` (GET) | Query Cross Margin Account Details (USER_DATA) | None | recvWindow | Yes |
| `/sapi/v1/margin/crossMarginData` (GET) | Query Cross Margin Fee Data (USER_DATA) | None | vipLevel, coin, recvWindow | Yes |
| `/sapi/v1/margin/isolated/accountLimit` (GET) | Query Enabled Isolated Margin Account Limit (USER_DATA) | None | recvWindow | Yes |
| `/sapi/v1/margin/isolatedMarginData` (GET) | Query Isolated Margin Fee Data (USER_DATA) | None | vipLevel, symbol, recvWindow | Yes |
| `/sapi/v1/margin/interestHistory` (GET) | Get Interest History (USER_DATA) | None | asset, isolatedSymbol, startTime, endTime, current, size, recvWindow | Yes |
| `/sapi/v1/margin/next-hourly-interest-rate` (GET) | Get future hourly interest rate (USER_DATA) | assets, isIsolated | None | Yes |
| `/sapi/v1/margin/borrow-repay` (POST) | Margin account borrow/repay(MARGIN) | asset, isIsolated, symbol, amount, type | recvWindow | Yes |
| `/sapi/v1/margin/borrow-repay` (GET) | Query borrow/repay records in Margin account(USER_DATA) | type | asset, isolatedSymbol, txId, startTime, endTime, current, size, recvWindow | Yes |
| `/sapi/v1/margin/interestRateHistory` (GET) | Query Margin Interest Rate History (USER_DATA) | asset | vipLevel, startTime, endTime, recvWindow | Yes |
| `/sapi/v1/margin/maxBorrowable` (GET) | Query Max Borrow (USER_DATA) | asset | isolatedSymbol, recvWindow | Yes |
| `/sapi/v1/margin/crossMarginCollateralRatio` (GET) | Cross margin collateral ratio (MARKET_DATA) | None | None | No |
| `/sapi/v1/margin/allPairs` (GET) | Get All Cross Margin Pairs (MARKET_DATA) | None | symbol | No |
| `/sapi/v1/margin/isolated/allPairs` (GET) | Get All Isolated Margin Symbol(MARKET_DATA) | None | symbol, recvWindow | No |
| `/sapi/v1/margin/allAssets` (GET) | Get All Margin Assets (MARKET_DATA) | None | asset | No |
| `/sapi/v1/margin/delist-schedule` (GET) | Get Delist Schedule (MARKET_DATA) | None | recvWindow | No |
| `/sapi/v1/margin/limit-price-pairs` (GET) | Get Limit Price Pairs(MARKET_DATA) | None | None | No |
| `/sapi/v1/margin/list-schedule` (GET) | Get list Schedule (MARKET_DATA) | None | recvWindow | No |
| `/sapi/v1/margin/risk-based-liquidation-ratio` (GET) | Get Margin Asset Risk-Based Liquidation Ratio (MARKET_DATA) | None | None | No |
| `/sapi/v1/margin/restricted-asset` (GET) | Get Margin Restricted Assets (MARKET_DATA) | None | None | No |
| `/sapi/v1/margin/isolatedMarginTier` (GET) | Query Isolated Margin Tier Data (USER_DATA) | symbol | tier, recvWindow | Yes |
| `/sapi/v1/margin/leverageBracket` (GET) | Query Liability Coin Leverage Bracket in Cross Margin Pro Mode(MARKET_DATA) | None | None | No |
| `/sapi/v1/margin/priceIndex` (GET) | Query Margin PriceIndex (MARKET_DATA) | symbol | None | No |
| `/sapi/v1/margin/available-inventory` (GET) | Query Margin Available Inventory(USER_DATA) | type | None | Yes |
| `/sapi/v1/margin/listen-key` (DELETE) | Close User Data Stream (USER_STREAM) | None | None | No |
| `/sapi/v1/margin/listen-key` (PUT) | Keepalive User Data Stream (USER_STREAM) | listenKey | None | No |
| `/sapi/v1/margin/listen-key` (POST) | Start User Data Stream (USER_STREAM) | None | None | No |
| `/sapi/v1/margin/apiKey` (POST) | Create Special Key(Low-Latency Trading)(TRADE) | apiName | symbol, ip, publicKey, permissionMode, recvWindow | Yes |
| `/sapi/v1/margin/apiKey` (DELETE) | Delete Special Key(Low-Latency Trading)(TRADE) | None | apiName, symbol, recvWindow | Yes |
| `/sapi/v1/margin/apiKey` (GET) | Query Special key(Low Latency Trading)(TRADE) | None | symbol, recvWindow | Yes |
| `/sapi/v1/margin/apiKey/ip` (PUT) | Edit ip for Special Key(Low-Latency Trading)(TRADE) | ip | symbol, recvWindow | Yes |
| `/sapi/v1/margin/forceLiquidationRec` (GET) | Get Force Liquidation Record (USER_DATA) | None | startTime, endTime, isolatedSymbol, current, size, recvWindow | Yes |
| `/sapi/v1/margin/exchange-small-liability` (GET) | Get Small Liability Exchange Coin List (USER_DATA) | None | recvWindow | Yes |
| `/sapi/v1/margin/exchange-small-liability` (POST) | Small Liability Exchange (MARGIN) | assetNames | recvWindow | Yes |
| `/sapi/v1/margin/exchange-small-liability-history` (GET) | Get Small Liability Exchange History (USER_DATA) | current, size | startTime, endTime, recvWindow | Yes |
| `/sapi/v1/margin/openOrders` (DELETE) | Margin Account Cancel all Open Orders on a Symbol (TRADE) | symbol | isIsolated, recvWindow | Yes |
| `/sapi/v1/margin/openOrders` (GET) | Query Margin Account's Open Orders (USER_DATA) | None | symbol, isIsolated, recvWindow | Yes |
| `/sapi/v1/margin/orderList` (DELETE) | Margin Account Cancel OCO (TRADE) | symbol | isIsolated, orderListId, listClientOrderId, newClientOrderId, recvWindow | Yes |
| `/sapi/v1/margin/orderList` (GET) | Query Margin Account's OCO (USER_DATA) | None | isIsolated, symbol, orderListId, origClientOrderId, recvWindow | Yes |
| `/sapi/v1/margin/order` (DELETE) | Margin Account Cancel Order (TRADE) | symbol | isIsolated, orderId, origClientOrderId, newClientOrderId, recvWindow | Yes |
| `/sapi/v1/margin/order` (POST) | Margin Account New Order (TRADE) | symbol, side, type | isIsolated, quantity, quoteOrderQty, price, stopPrice, newClientOrderId, icebergQty, newOrderRespType, sideEffectType, timeInForce, selfTradePreventionMode, autoRepayAtCancel, recvWindow | Yes |
| `/sapi/v1/margin/order` (GET) | Query Margin Account's Order (USER_DATA) | symbol | isIsolated, orderId, origClientOrderId, recvWindow | Yes |
| `/sapi/v1/margin/order/oco` (POST) | Margin Account New OCO (TRADE) | symbol, side, quantity, price, stopPrice | isIsolated, listClientOrderId, limitClientOrderId, limitIcebergQty, stopClientOrderId, stopLimitPrice, stopIcebergQty, stopLimitTimeInForce, newOrderRespType, sideEffectType, selfTradePreventionMode, autoRepayAtCancel, recvWindow | Yes |
| `/sapi/v1/margin/order/oto` (POST) | Margin Account New OTO (TRADE) | symbol, workingType, workingSide, workingPrice, workingQuantity, workingIcebergQty, pendingType, pendingSide, pendingQuantity | isIsolated, listClientOrderId, newOrderRespType, sideEffectType, selfTradePreventionMode, autoRepayAtCancel, workingClientOrderId, workingTimeInForce, pendingClientOrderId, pendingPrice, pendingStopPrice, pendingTrailingDelta, pendingIcebergQty, pendingTimeInForce | Yes |
| `/sapi/v1/margin/order/otoco` (POST) | Margin Account New OTOCO (TRADE) | symbol, workingType, workingSide, workingPrice, workingQuantity, pendingSide, pendingQuantity, pendingAboveType | isIsolated, sideEffectType, autoRepayAtCancel, listClientOrderId, newOrderRespType, selfTradePreventionMode, workingClientOrderId, workingIcebergQty, workingTimeInForce, pendingAboveClientOrderId, pendingAbovePrice, pendingAboveStopPrice, pendingAboveTrailingDelta, pendingAboveIcebergQty, pendingAboveTimeInForce, pendingBelowType, pendingBelowClientOrderId, pendingBelowPrice, pendingBelowStopPrice, pendingBelowTrailingDelta, pendingBelowIcebergQty, pendingBelowTimeInForce | Yes |
| `/sapi/v1/margin/manual-liquidation` (POST) | Margin Manual Liquidation(MARGIN) | type | symbol, recvWindow | Yes |
| `/sapi/v1/margin/rateLimit/order` (GET) | Query Current Margin Order Count Usage (TRADE) | None | isIsolated, symbol, recvWindow | Yes |
| `/sapi/v1/margin/allOrderList` (GET) | Query Margin Account's all OCO (USER_DATA) | None | isIsolated, symbol, fromId, startTime, endTime, limit, recvWindow | Yes |
| `/sapi/v1/margin/allOrders` (GET) | Query Margin Account's All Orders (USER_DATA) | symbol | isIsolated, orderId, startTime, endTime, limit, recvWindow | Yes |
| `/sapi/v1/margin/openOrderList` (GET) | Query Margin Account's Open OCO (USER_DATA) | None | isIsolated, symbol, recvWindow | Yes |
| `/sapi/v1/margin/myTrades` (GET) | Query Margin Account's Trade List (USER_DATA) | symbol | isIsolated, orderId, startTime, endTime, fromId, limit, recvWindow | Yes |
| `/sapi/v1/margin/myPreventedMatches` (GET) | Query Prevented Matches(USER_DATA) | symbol | preventedMatchId, orderId, fromPreventedMatchId, recvWindow, isIsolated | Yes |
| `/sapi/v1/margin/api-key-list` (GET) | Query Special key List(Low Latency Trading)(TRADE) | None | symbol, recvWindow | Yes |
| `/sapi/v1/margin/transfer` (GET) | Get Cross Margin Transfer History (USER_DATA) | None | asset, type, startTime, endTime, current, size, isolatedSymbol, recvWindow | Yes |
| `/sapi/v1/margin/maxTransferable` (GET) | Query Max Transfer-Out Amount (USER_DATA) | asset | isolatedSymbol, recvWindow | Yes |

---

## Parameters

### Common Parameters

* **maxLeverage**: Can only adjust 3 , 5 or 10，Example: maxLeverage = 5 or 3 for Cross Margin Classic; maxLeverage=10 for Cross Margin Pro 10x leverage or 20x if compliance allows.
* **symbol**: 
* **recvWindow**: No more than 60000 (e.g., 5000)
* **asset**: 
* **symbol**: isolated margin pair
* **type**: Transfer Type: ROLL_IN, ROLL_OUT
* **startTime**: Only supports querying data from the past 90 days. (e.g., 1623319461670)
* **endTime**:  (e.g., 1641782889000)
* **fromId**: If `fromId` is set, data with `id` greater than `fromId` will be returned. Otherwise, the latest data will be returned. (e.g., 1)
* **limit**: Limit on the number of data records returned per request. Default: 500; Maximum: 1000. (e.g., 500)
* **vipLevel**: User's current specific margin data will be returned if vipLevel is omitted (e.g., 1)
* **coin**: 
* **symbols**: Max 5 symbols can be sent; separated by ",". e.g. "BTCUSDT,BNBUSDT,ADAUSDT"
* **isolatedSymbol**: isolated symbol
* **current**: Currently querying page. Start from 1. Default:1 (e.g., 1)
* **size**: Default:10 Max:100 (e.g., 10)
* **assets**: List of assets, separated by commas, up to 20
* **isIsolated**: for isolated margin or not, "TRUE", "FALSE"
* **asset**: 
* **isIsolated**: `TRUE` for Isolated Margin, `FALSE` for Cross Margin, Default `FALSE` (e.g., FALSE)
* **amount**: 
* **type**: `MARGIN`,`ISOLATED`
* **txId**: `tranId` in `POST /sapi/v1/margin/loan` (e.g., 1)
* **tier**: All margin tier data will be returned if tier is omitted
* **listenKey**: 
* **apiName**: 
* **ip**: Can be added in batches, separated by commas. Max 30 for an API key
* **publicKey**: 1. If publicKey is inputted it will create an RSA or Ed25519 key.  2. Need to be encoded to URL-encoded format
* **permissionMode**: This parameter is only for the Ed25519 API key, and does not effact for other encryption methods. The value can be TRADE (TRADE for all permissions) or READ (READ for USER_DATA, FIX_API_READ_ONLY). The default value is TRADE. (e.g., value)
* **apiName**: 
* **ip**: Can be added in batches, separated by commas. Max 30 for an API key
* **current**: Currently querying page. Start from 1. Default:1 (e.g., 1)
* **size**: Default:10, Max:100 (e.g., 10)
* **isIsolated**: For isolated margin or not, "TRUE", "FALSE", default "FALSE"
* **orderListId**: Either `orderListId` or `listClientOrderId` must be provided (e.g., 1)
* **listClientOrderId**: Either `orderListId` or `listClientOrderId` must be provided (e.g., 1)
* **newClientOrderId**: Used to uniquely identify this cancel. Automatically generated by default (e.g., 1)
* **orderId**:  (e.g., 1)
* **origClientOrderId**:  (e.g., 1)
* **quantity**:  (e.g., 1.0)
* **limitClientOrderId**: A unique Id for the limit order (e.g., 1)
* **price**:  (e.g., 1.0)
* **limitIcebergQty**:  (e.g., 1.0)
* **stopClientOrderId**: A unique Id for the stop loss/stop loss limit leg (e.g., 1)
* **stopPrice**:  (e.g., 1.0)
* **stopLimitPrice**: If provided, `stopLimitTimeInForce` is required. (e.g., 1.0)
* **stopIcebergQty**:  (e.g., 1.0)
* **stopLimitTimeInForce**: Valid values are `GTC`/`FOK`/`IOC`
* **sideEffectType**: NO_SIDE_EFFECT, MARGIN_BUY, AUTO_REPAY,AUTO_BORROW_REPAY; default NO_SIDE_EFFECT. More info in FAQ (e.g., NO_SIDE_EFFECT)
* **selfTradePreventionMode**: The allowed enums is dependent on what is configured on the symbol. The possible supported values are EXPIRE_TAKER, EXPIRE_MAKER, EXPIRE_BOTH, NONE (e.g., NONE)
* **autoRepayAtCancel**: Only when MARGIN_BUY or AUTO_BORROW_REPAY order takes effect, true means that the debt generated by the order needs to be repay after the order is cancelled. The default is true (e.g., true)
* **workingType**: Supported values: `LIMIT`, `LIMIT_MAKER`
* **workingSide**: BUY, SELL
* **workingClientOrderId**: Arbitrary unique ID among open orders for the working order. Automatically generated if not sent. (e.g., 1)
* **workingPrice**:  (e.g., 1.0)
* **workingQuantity**:  (e.g., 1.0)
* **workingIcebergQty**: This can only be used if `workingTimeInForce` is `GTC`. (e.g., 1.0)
* **workingTimeInForce**: GTC,IOC,FOK
* **pendingType**: Supported values: Order Types Note that `MARKET` orders using `quoteOrderQty` are not supported. (e.g., Order Types)
* **pendingSide**: BUY, SELL
* **pendingClientOrderId**: Arbitrary unique ID among open orders for the pending order. Automatically generated if not sent. (e.g., 1)
* **pendingPrice**:  (e.g., 1.0)
* **pendingStopPrice**:  (e.g., 1.0)
* **pendingTrailingDelta**:  (e.g., 1.0)
* **pendingQuantity**:  (e.g., 1.0)
* **pendingIcebergQty**: This can only be used if `pendingTimeInForce` is `GTC`. (e.g., 1.0)
* **pendingTimeInForce**: GTC,IOC,FOK
* **workingIcebergQty**: This can only be used if `workingTimeInForce` is `GTC`. (e.g., 1.0)
* **pendingAboveType**: Supported values: `LIMIT_MAKER`, `STOP_LOSS`, and `STOP_LOSS_LIMIT`
* **pendingAboveClientOrderId**: Arbitrary unique ID among open orders for the pending above order. Automatically generated if not sent. (e.g., 1)
* **pendingAbovePrice**:  (e.g., 1.0)
* **pendingAboveStopPrice**:  (e.g., 1.0)
* **pendingAboveTrailingDelta**:  (e.g., 1.0)
* **pendingAboveIcebergQty**: This can only be used if `pendingAboveTimeInForce` is `GTC`. (e.g., 1.0)
* **pendingAboveTimeInForce**: 
* **pendingBelowType**: Supported values: `LIMIT_MAKER`, `STOP_LOSS`, and `STOP_LOSS_LIMIT`
* **pendingBelowClientOrderId**: Arbitrary unique ID among open orders for the pending below order. Automatically generated if not sent. (e.g., 1)
* **pendingBelowPrice**:  (e.g., 1.0)
* **pendingBelowStopPrice**:  (e.g., 1.0)
* **pendingBelowTrailingDelta**:  (e.g., 1.0)
* **pendingBelowIcebergQty**: This can only be used if `pendingBelowTimeInForce` is `GTC`. (e.g., 1.0)
* **pendingBelowTimeInForce**: 
* **quantity**:  (e.g., 1.0)
* **quoteOrderQty**:  (e.g., 1.0)
* **price**:  (e.g., 1.0)
* **stopPrice**: Used with `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TAKE_PROFIT`, and `TAKE_PROFIT_LIMIT` orders. (e.g., 1.0)
* **icebergQty**: Used with `LIMIT`, `STOP_LOSS_LIMIT`, and `TAKE_PROFIT_LIMIT` to create an iceberg order. (e.g., 1.0)
* **preventedMatchId**:  (e.g., 1)
* **fromPreventedMatchId**:  (e.g., 1)
* **assetNames**: The assets list of small liability exchange， Example: assetNames = BTC,ETH


### Enums

* **side**: BUY | SELL
* **newOrderRespType**: ACK | RESULT | FULL
* **timeInForce**: GTC | IOC | FOK


## Authentication

For endpoints that require authentication, you will need to provide Binance API credentials.
Required credentials:

* apiKey: Your Binance API key (for header)
* secretKey: Your Binance API secret (for signing)

Base URLs:
* Mainnet: https://api.binance.com

## Security

### Share Credentials

Users can provide Binance API credentials by sending a file where the content is in the following format:

```bash
abc123...xyz
secret123...key
```

### Never Disclose API Key and Secret

Never disclose the location of the API key and secret file.

Never send the API key and secret to any website other than Mainnet and Testnet.

### Never Display Full Secrets

When showing credentials to users:
- **API Key:** Show first 5 + last 4 characters: `su1Qc...8akf`
- **Secret Key:** Always mask, show only last 5: `***...aws1`

Example response when asked for credentials:
Account: main
API Key: su1Qc...8akf
Secret: ***...aws1

### Listing Accounts

When listing accounts, show names and environment only — never keys:
Binance Accounts:
* main (Mainnet)
* futures-keys (Mainnet)

### Transactions in Mainnet

When performing transactions in mainnet, always confirm with the user before proceeding by asking them to write "CONFIRM" to proceed.

---

## Binance Accounts

### main
- API Key: your_mainnet_api_key
- Secret: your_mainnet_secret

### TOOLS.md Structure

```bash
## Binance Accounts

### main
- API Key: abc123...xyz
- Secret: secret123...key
- Description: Primary trading account


### futures-keys
- API Key: futures789...def
- Secret: futuressecret...uvw
- Description: Futures trading account
```

## Agent Behavior

1. Credentials requested: Mask secrets (show last 5 chars only)
2. Listing accounts: Show names and environment, never keys
3. Account selection: Ask if ambiguous, default to main
4. When doing a transaction in mainnet, confirm with user before by asking to write "CONFIRM" to proceed
5. New credentials: Prompt for name, environment, signing mode

## Adding New Accounts

When user provides new credentials:

* Ask for account name
* Store in `TOOLS.md` with masked display confirmation 

## Signing Requests

For trading endpoints that require a signature:

1. Build query string with all parameters, including the timestamp (Unix ms).
2. Percent-encode the parameters using UTF-8 according to RFC 3986.
3. Sign query string with secretKey using HMAC SHA256, RSA, or Ed25519 (depending on the account configuration).
4. Append signature to query string.
5. Include `X-MBX-APIKEY` header.

Otherwise, do not perform steps 3–5.

## New Client Order ID 

For endpoints that include the `newClientOrderId` parameter, the value must always start with `agent-`. If the parameter is not provided, `agent-` followed by 18 random alphanumeric characters will be generated automatically. If a value is provided, it will be prefixed with `agent-`

Example: `agent-1a2b3c4d5e6f7g8h9i`

## User Agent Header

Include `User-Agent` header with the following string: `binance-margin-trading/1.0.0 (Skill)`

See [`references/authentication.md`](./references/authentication.md) for implementation details.
