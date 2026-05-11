---
name: derivatives-trading-portfolio-margin
description: Binance Derivatives-trading-portfolio-margin request using the Binance API. Authentication requires API key and secret key. Supports testnet and mainnet.
metadata:
  version: 1.0.0
  author: Binance
license: MIT
---

# Binance Derivatives-trading-portfolio-margin Skill

Derivatives-trading-portfolio-margin request on Binance using authenticated API endpoints. Requires API key and secret key for certain endpoints. Return the result in JSON format.

## Quick Reference

| Endpoint | Description | Required | Optional | Authentication |
|----------|-------------|----------|----------|----------------|
| `/papi/v1/balance` (GET) | Account Balance(USER_DATA) | None | asset, recvWindow | Yes |
| `/papi/v1/account` (GET) | Account Information(USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/bnb-transfer` (POST) | BNB transfer (TRADE) | amount, transferSide | recvWindow | Yes |
| `/papi/v1/cm/leverageBracket` (GET) | CM Notional and Leverage Brackets(USER_DATA) | None | symbol, recvWindow | Yes |
| `/papi/v1/repay-futures-switch` (POST) | Change Auto-repay-futures Status(TRADE) | autoRepay | recvWindow | Yes |
| `/papi/v1/repay-futures-switch` (GET) | Get Auto-repay-futures Status(USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/cm/leverage` (POST) | Change CM Initial Leverage (TRADE) | symbol, leverage | recvWindow | Yes |
| `/papi/v1/cm/positionSide/dual` (POST) | Change CM Position Mode(TRADE) | dualSidePosition | recvWindow | Yes |
| `/papi/v1/cm/positionSide/dual` (GET) | Get CM Current Position Mode(USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/um/leverage` (POST) | Change UM Initial Leverage(TRADE) | symbol, leverage | recvWindow | Yes |
| `/papi/v1/um/positionSide/dual` (POST) | Change UM Position Mode(TRADE) | dualSidePosition | recvWindow | Yes |
| `/papi/v1/um/positionSide/dual` (GET) | Get UM Current Position Mode(USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/auto-collection` (POST) | Fund Auto-collection(TRADE) | None | recvWindow | Yes |
| `/papi/v1/asset-collection` (POST) | Fund Collection by Asset(TRADE) | asset | recvWindow | Yes |
| `/papi/v1/cm/account` (GET) | Get CM Account Detail(USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/cm/income` (GET) | Get CM Income History(USER_DATA) | None | symbol, incomeType, startTime, endTime, page, limit, recvWindow | Yes |
| `/papi/v1/um/order/asyn` (GET) | Get Download Id For UM Futures Order History (USER_DATA) | startTime, endTime | recvWindow | Yes |
| `/papi/v1/um/trade/asyn` (GET) | Get Download Id For UM Futures Trade History (USER_DATA) | startTime, endTime | recvWindow | Yes |
| `/papi/v1/um/income/asyn` (GET) | Get Download Id For UM Futures Transaction History (USER_DATA) | startTime, endTime | recvWindow | Yes |
| `/papi/v1/margin/marginInterestHistory` (GET) | Get Margin Borrow/Loan Interest History(USER_DATA) | None | asset, startTime, endTime, current, size, archived, recvWindow | Yes |
| `/papi/v2/um/account` (GET) | Get UM Account Detail V2(USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/um/account` (GET) | Get UM Account Detail(USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/um/accountConfig` (GET) | UM Futures Account Configuration(USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/um/order/asyn/id` (GET) | Get UM Futures Order Download Link by Id(USER_DATA) | downloadId | recvWindow | Yes |
| `/papi/v1/um/symbolConfig` (GET) | UM Futures Symbol Configuration(USER_DATA) | None | symbol, recvWindow | Yes |
| `/papi/v1/um/trade/asyn/id` (GET) | Get UM Futures Trade Download Link by Id(USER_DATA) | downloadId | recvWindow | Yes |
| `/papi/v1/um/income/asyn/id` (GET) | Get UM Futures Transaction Download Link by Id(USER_DATA) | downloadId | recvWindow | Yes |
| `/papi/v1/um/income` (GET) | Get UM Income History(USER_DATA) | None | symbol, incomeType, startTime, endTime, page, limit, recvWindow | Yes |
| `/papi/v1/cm/commissionRate` (GET) | Get User Commission Rate for CM(USER_DATA) | symbol | recvWindow | Yes |
| `/papi/v1/um/commissionRate` (GET) | Get User Commission Rate for UM(USER_DATA) | symbol | recvWindow | Yes |
| `/papi/v1/margin/maxBorrowable` (GET) | Margin Max Borrow(USER_DATA) | asset | recvWindow | Yes |
| `/papi/v1/um/apiTradingStatus` (GET) | Portfolio Margin UM Trading Quantitative Rules Indicators(USER_DATA) | None | symbol, recvWindow | Yes |
| `/papi/v1/cm/positionRisk` (GET) | Query CM Position Information(USER_DATA) | None | marginAsset, pair, recvWindow | Yes |
| `/papi/v1/margin/marginLoan` (GET) | Query Margin Loan Record(USER_DATA) | asset | txId, startTime, endTime, current, size, archived, recvWindow | Yes |
| `/papi/v1/margin/maxWithdraw` (GET) | Query Margin Max Withdraw(USER_DATA) | asset | recvWindow | Yes |
| `/papi/v1/margin/repayLoan` (GET) | Query Margin repay Record(USER_DATA) | asset | txId, startTime, endTime, current, size, archived, recvWindow | Yes |
| `/papi/v1/portfolio/interest-history` (GET) | Query Portfolio Margin Negative Balance Interest History(USER_DATA) | None | asset, startTime, endTime, size, recvWindow | Yes |
| `/papi/v1/um/positionRisk` (GET) | Query UM Position Information(USER_DATA) | None | symbol, recvWindow | Yes |
| `/papi/v1/portfolio/negative-balance-exchange-record` (GET) | Query User Negative Balance Auto Exchange Record (USER_DATA) | startTime, endTime | recvWindow | Yes |
| `/papi/v1/rateLimit/order` (GET) | Query User Rate Limit (USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/repay-futures-negative-balance` (POST) | Repay futures Negative Balance(USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/um/leverageBracket` (GET) | UM Notional and Leverage Brackets (USER_DATA) | None | symbol, recvWindow | Yes |
| `/papi/v1/ping` (GET) | Test Connectivity | None | None | No |
| `/papi/v1/cm/userTrades` (GET) | CM Account Trade List(USER_DATA) | None | symbol, pair, startTime, endTime, fromId, limit, recvWindow | Yes |
| `/papi/v1/cm/adlQuantile` (GET) | CM Position ADL Quantile Estimation(USER_DATA) | None | symbol, recvWindow | Yes |
| `/papi/v1/cm/conditional/allOpenOrders` (DELETE) | Cancel All CM Open Conditional Orders(TRADE) | symbol | recvWindow | Yes |
| `/papi/v1/cm/allOpenOrders` (DELETE) | Cancel All CM Open Orders(TRADE) | symbol | recvWindow | Yes |
| `/papi/v1/um/conditional/allOpenOrders` (DELETE) | Cancel All UM Open Conditional Orders (TRADE) | symbol | recvWindow | Yes |
| `/papi/v1/um/allOpenOrders` (DELETE) | Cancel All UM Open Orders(TRADE) | symbol | recvWindow | Yes |
| `/papi/v1/cm/conditional/order` (DELETE) | Cancel CM Conditional Order(TRADE) | symbol | strategyId, newClientStrategyId, recvWindow | Yes |
| `/papi/v1/cm/conditional/order` (POST) | New CM Conditional Order(TRADE) | symbol, side, strategyType | positionSide, timeInForce, quantity, reduceOnly, price, workingType, priceProtect, newClientStrategyId, stopPrice, activationPrice, callbackRate, recvWindow | Yes |
| `/papi/v1/cm/order` (DELETE) | Cancel CM Order(TRADE) | symbol | orderId, origClientOrderId, recvWindow | Yes |
| `/papi/v1/cm/order` (PUT) | Modify CM Order(TRADE) | symbol, side, quantity, price | orderId, origClientOrderId, priceMatch, recvWindow | Yes |
| `/papi/v1/cm/order` (POST) | New CM Order(TRADE) | symbol, side, type | positionSide, timeInForce, quantity, reduceOnly, price, priceMatch, newClientOrderId, newOrderRespType, recvWindow | Yes |
| `/papi/v1/cm/order` (GET) | Query CM Order(USER_DATA) | symbol | orderId, origClientOrderId, recvWindow | Yes |
| `/papi/v1/margin/allOpenOrders` (DELETE) | Cancel Margin Account All Open Orders on a Symbol(TRADE) | symbol | recvWindow | Yes |
| `/papi/v1/margin/orderList` (DELETE) | Cancel Margin Account OCO Orders(TRADE) | symbol | orderListId, listClientOrderId, newClientOrderId, recvWindow | Yes |
| `/papi/v1/margin/orderList` (GET) | Query Margin Account's OCO (USER_DATA) | None | orderListId, origClientOrderId, recvWindow | Yes |
| `/papi/v1/margin/order` (DELETE) | Cancel Margin Account Order(TRADE) | symbol | orderId, origClientOrderId, newClientOrderId, recvWindow | Yes |
| `/papi/v1/margin/order` (POST) | New Margin Order(TRADE) | symbol, side, type | quantity, quoteOrderQty, price, stopPrice, newClientOrderId, newOrderRespType, icebergQty, sideEffectType, timeInForce, selfTradePreventionMode, autoRepayAtCancel, recvWindow | Yes |
| `/papi/v1/margin/order` (GET) | Query Margin Account Order (USER_DATA) | symbol | orderId, origClientOrderId, recvWindow | Yes |
| `/papi/v1/um/conditional/order` (DELETE) | Cancel UM Conditional Order(TRADE) | symbol | strategyId, newClientStrategyId, recvWindow | Yes |
| `/papi/v1/um/conditional/order` (POST) | New UM Conditional Order (TRADE) | symbol, side, strategyType | positionSide, timeInForce, quantity, reduceOnly, price, workingType, priceProtect, newClientStrategyId, stopPrice, activationPrice, callbackRate, priceMatch, selfTradePreventionMode, goodTillDate, recvWindow | Yes |
| `/papi/v1/um/order` (DELETE) | Cancel UM Order(TRADE) | symbol | orderId, origClientOrderId, recvWindow | Yes |
| `/papi/v1/um/order` (PUT) | Modify UM Order(TRADE) | symbol, side, quantity, price | orderId, origClientOrderId, priceMatch, recvWindow | Yes |
| `/papi/v1/um/order` (POST) | New UM Order (TRADE) | symbol, side, type | positionSide, timeInForce, quantity, reduceOnly, price, newClientOrderId, newOrderRespType, priceMatch, selfTradePreventionMode, goodTillDate, recvWindow | Yes |
| `/papi/v1/um/order` (GET) | Query UM Order (USER_DATA) | symbol | orderId, origClientOrderId, recvWindow | Yes |
| `/papi/v1/um/feeBurn` (GET) | Get UM Futures BNB Burn Status (USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/um/feeBurn` (POST) | Toggle BNB Burn On UM Futures Trade (TRADE) | feeBurn | recvWindow | Yes |
| `/papi/v1/marginLoan` (POST) | Margin Account Borrow(MARGIN) | asset, amount | recvWindow | Yes |
| `/papi/v1/margin/order/oco` (POST) | Margin Account New OCO(TRADE) | symbol, side, quantity, price, stopPrice | listClientOrderId, limitClientOrderId, limitIcebergQty, stopClientOrderId, stopLimitPrice, stopIcebergQty, stopLimitTimeInForce, newOrderRespType, sideEffectType, recvWindow | Yes |
| `/papi/v1/margin/repay-debt` (POST) | Margin Account Repay Debt(TRADE) | asset | amount, specifyRepayAssets, recvWindow | Yes |
| `/papi/v1/repayLoan` (POST) | Margin Account Repay(MARGIN) | asset, amount | recvWindow | Yes |
| `/papi/v1/margin/myTrades` (GET) | Margin Account Trade List (USER_DATA) | symbol | orderId, startTime, endTime, fromId, limit, recvWindow | Yes |
| `/papi/v1/cm/conditional/allOrders` (GET) | Query All CM Conditional Orders(USER_DATA) | None | symbol, strategyId, startTime, endTime, limit, recvWindow | Yes |
| `/papi/v1/cm/allOrders` (GET) | Query All CM Orders (USER_DATA) | symbol | pair, orderId, startTime, endTime, limit, recvWindow | Yes |
| `/papi/v1/cm/conditional/openOrders` (GET) | Query All Current CM Open Conditional Orders (USER_DATA) | None | symbol, recvWindow | Yes |
| `/papi/v1/cm/openOrders` (GET) | Query All Current CM Open Orders(USER_DATA) | None | symbol, pair, recvWindow | Yes |
| `/papi/v1/um/conditional/openOrders` (GET) | Query All Current UM Open Conditional Orders(USER_DATA) | None | symbol, recvWindow | Yes |
| `/papi/v1/um/openOrders` (GET) | Query All Current UM Open Orders(USER_DATA) | None | symbol, recvWindow | Yes |
| `/papi/v1/margin/allOrders` (GET) | Query All Margin Account Orders (USER_DATA) | symbol | orderId, startTime, endTime, limit, recvWindow | Yes |
| `/papi/v1/um/conditional/allOrders` (GET) | Query All UM Conditional Orders(USER_DATA) | None | symbol, strategyId, startTime, endTime, limit, recvWindow | Yes |
| `/papi/v1/um/allOrders` (GET) | Query All UM Orders(USER_DATA) | symbol | orderId, startTime, endTime, limit, recvWindow | Yes |
| `/papi/v1/cm/conditional/orderHistory` (GET) | Query CM Conditional Order History(USER_DATA) | symbol | strategyId, newClientStrategyId, recvWindow | Yes |
| `/papi/v1/cm/orderAmendment` (GET) | Query CM Modify Order History(TRADE) | symbol | orderId, origClientOrderId, startTime, endTime, limit, recvWindow | Yes |
| `/papi/v1/cm/conditional/openOrder` (GET) | Query Current CM Open Conditional Order(USER_DATA) | symbol | strategyId, newClientStrategyId, recvWindow | Yes |
| `/papi/v1/cm/openOrder` (GET) | Query Current CM Open Order (USER_DATA) | symbol | orderId, origClientOrderId, recvWindow | Yes |
| `/papi/v1/margin/openOrders` (GET) | Query Current Margin Open Order (USER_DATA) | symbol | recvWindow | Yes |
| `/papi/v1/um/conditional/openOrder` (GET) | Query Current UM Open Conditional Order(USER_DATA) | symbol | strategyId, newClientStrategyId, recvWindow | Yes |
| `/papi/v1/um/openOrder` (GET) | Query Current UM Open Order(USER_DATA) | symbol | orderId, origClientOrderId, recvWindow | Yes |
| `/papi/v1/margin/openOrderList` (GET) | Query Margin Account's Open OCO (USER_DATA) | None | recvWindow | Yes |
| `/papi/v1/margin/allOrderList` (GET) | Query Margin Account's all OCO (USER_DATA) | None | fromId, startTime, endTime, limit, recvWindow | Yes |
| `/papi/v1/um/conditional/orderHistory` (GET) | Query UM Conditional Order History(USER_DATA) | symbol | strategyId, newClientStrategyId, recvWindow | Yes |
| `/papi/v1/um/orderAmendment` (GET) | Query UM Modify Order History(TRADE) | symbol | orderId, origClientOrderId, startTime, endTime, limit, recvWindow | Yes |
| `/papi/v1/cm/forceOrders` (GET) | Query User's CM Force Orders(USER_DATA) | None | symbol, autoCloseType, startTime, endTime, limit, recvWindow | Yes |
| `/papi/v1/margin/forceOrders` (GET) | Query User's Margin Force Orders(USER_DATA) | None | startTime, endTime, current, size, recvWindow | Yes |
| `/papi/v1/um/forceOrders` (GET) | Query User's UM Force Orders (USER_DATA) | None | symbol, autoCloseType, startTime, endTime, limit, recvWindow | Yes |
| `/papi/v1/um/userTrades` (GET) | UM Account Trade List(USER_DATA) | symbol | startTime, endTime, fromId, limit, recvWindow | Yes |
| `/papi/v1/um/adlQuantile` (GET) | UM Position ADL Quantile Estimation(USER_DATA) | None | symbol, recvWindow | Yes |
| `/papi/v1/listenKey` (DELETE) | Close User Data Stream(USER_STREAM) | None | None | No |
| `/papi/v1/listenKey` (PUT) | Keepalive User Data Stream (USER_STREAM) | None | None | No |
| `/papi/v1/listenKey` (POST) | Start User Data Stream(USER_STREAM) | None | None | No |

---

## Parameters

### Common Parameters

* **asset**: 
* **recvWindow**:  (e.g., 5000)
* **amount**:  (e.g., 1.0)
* **transferSide**: "TO_UM","FROM_UM"
* **symbol**: 
* **autoRepay**: Default: `true`; `false` for turn off the auto-repay futures negative balance function (e.g., true)
* **symbol**: 
* **leverage**: target initial leverage: int from 1 to 125
* **dualSidePosition**: "true": Hedge Mode; "false": One-way Mode
* **asset**: 
* **incomeType**: TRANSFER, WELCOME_BONUS, REALIZED_PNL, FUNDING_FEE, COMMISSION, INSURANCE_CLEAR, REFERRAL_KICKBACK, COMMISSION_REBATE, API_REBATE, CONTEST_REWARD, CROSS_COLLATERAL_TRANSFER, OPTIONS_PREMIUM_FEE, OPTIONS_SETTLE_PROFIT, INTERNAL_TRANSFER, AUTO_EXCHANGE, DELIVERED_SETTELMENT, COIN_SWAP_DEPOSIT, COIN_SWAP_WITHDRAW, POSITION_LIMIT_INCREASE_FEE
* **startTime**: Timestamp in ms to get funding from INCLUSIVE. (e.g., 1623319461670)
* **endTime**: Timestamp in ms to get funding until INCLUSIVE. (e.g., 1641782889000)
* **page**: 
* **limit**: Default 100; max 1000 (e.g., 100)
* **startTime**:  (e.g., 1623319461670)
* **endTime**:  (e.g., 1641782889000)
* **current**: Currently querying page. Start from 1. Default:1 (e.g., 1)
* **size**: Default:10 Max:100 (e.g., 10)
* **archived**: Default: `false`. Set to `true` for archived data from 6 months ago
* **downloadId**: get by download id api (e.g., 1)
* **marginAsset**: 
* **pair**: 
* **txId**: the `tranId` in `POST/papi/v1/marginLoan` (e.g., 1)
* **fromId**: Trade id to fetch from. Default gets most recent trades. (e.g., 1)
* **strategyId**:  (e.g., 1)
* **newClientStrategyId**:  (e.g., 1)
* **orderId**:  (e.g., 1)
* **origClientOrderId**:  (e.g., 1)
* **orderListId**: Either `orderListId` or `listClientOrderId` must be provided (e.g., 1)
* **listClientOrderId**: Either `orderListId` or `listClientOrderId` must be provided (e.g., 1)
* **newClientOrderId**: Used to uniquely identify this cancel. Automatically generated by default (e.g., 1)
* **quantity**: Order quantity (e.g., 1.0)
* **limitClientOrderId**: A unique Id for the limit order (e.g., 1)
* **price**:  (e.g., 1.0)
* **limitIcebergQty**:  (e.g., 1.0)
* **stopClientOrderId**: A unique Id for the stop loss/stop loss limit leg (e.g., 1)
* **stopPrice**:  (e.g., 1.0)
* **stopLimitPrice**: If provided, stopLimitTimeInForce is required. (e.g., 1.0)
* **stopIcebergQty**:  (e.g., 1.0)
* **amount**: 
* **specifyRepayAssets**: Specific asset list to repay debt; Can be added in batch, separated by commas
* **quantity**:  (e.g., 1.0)
* **reduceOnly**: "true" or "false". default "false". Cannot be sent in Hedge Mode .
* **price**:  (e.g., 1.0)
* **priceProtect**: "TRUE" or "FALSE", default "FALSE". Used with `STOP/STOP_MARKET` or `TAKE_PROFIT/TAKE_PROFIT_MARKET` orders
* **stopPrice**: Used with `STOP/STOP_MARKET` or `TAKE_PROFIT/TAKE_PROFIT_MARKET` orders. (e.g., 1.0)
* **activationPrice**: Used with `TRAILING_STOP_MARKET` orders, default as the mark price (e.g., 1.0)
* **callbackRate**: Used with `TRAILING_STOP_MARKET` orders, min 0.1, max 5 where 1 for 1% (e.g., 1.0)
* **quoteOrderQty**:  (e.g., 1.0)
* **icebergQty**: Used with `LIMIT`, `STOP_LOSS_LIMIT`, and `TAKE_PROFIT_LIMIT` to create an iceberg order (e.g., 1.0)
* **autoRepayAtCancel**: Only when MARGIN_BUY or AUTO_BORROW_REPAY order takes effect, true means that the debt generated by the order needs to be repay after the order is cancelled. The default is true (e.g., true)
* **goodTillDate**: order cancel time for timeInForce `GTD`, mandatory when `timeInforce` set to `GTD`; order the timestamp only retains second-level precision, ms part will be ignored; The goodTillDate timestamp must be greater than the current time plus 600 seconds and smaller than 253402300799000Mode. It must be sent in Hedge Mode.
* **feeBurn**: "true": Fee Discount On; "false": Fee Discount Off


### Enums

* **side**: BUY | SELL
* **stopLimitTimeInForce**: GTC | IOC | FOK
* **newOrderRespType**: ACK | RESULT
* **sideEffectType**: NO_SIDE_EFFECT | MARGIN_BUY | AUTO_REPAY
* **priceMatch**: NONE | OPPONENT | OPPONENT_5 | OPPONENT_10 | OPPONENT_20 | QUEUE | QUEUE_5 | QUEUE_10 | QUEUE_20
* **positionSide**: BOTH | LONG | SHORT
* **strategyType**: STOP | STOP_MARKET | LIMIT_MAKER | TAKE_PROFIT | TAKE_PROFIT_MARKET | TRAILING_STOP_MARKET
* **timeInForce**: GTC | IOC | FOK | GTX
* **workingType**: MARK_PRICE
* **type**: LIMIT | MARKET
* **selfTradePreventionMode**: NONE | EXPIRE_TAKER | EXPIRE_BOTH | EXPIRE_MAKER
* **autoCloseType**: LIQUIDATION | ADL


## Authentication

For endpoints that require authentication, you will need to provide Binance API credentials.
Required credentials:

* apiKey: Your Binance API key (for header)
* secretKey: Your Binance API secret (for signing)

Base URLs:
* Mainnet: https://papi.binance.com
* Testnet: https://testnet.binancefuture.com

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
Environment: Mainnet

### Listing Accounts

When listing accounts, show names and environment only — never keys:
Binance Accounts:
* main (Mainnet/Testnet)
* testnet-dev (Testnet)
* futures-keys (Mainnet)

### Transactions in Mainnet

When performing transactions in mainnet, always confirm with the user before proceeding by asking them to write "CONFIRM" to proceed.

---

## Binance Accounts

### main
- API Key: your_mainnet_api_key
- Secret: your_mainnet_secret
- Testnet: false 

### testnet-dev
- API Key: your_testnet_api_key
- Secret: your_testnet_secret
- Testnet: true

### TOOLS.md Structure

```bash
## Binance Accounts

### main
- API Key: abc123...xyz
- Secret: secret123...key
- Testnet: false
- Description: Primary trading account

### testnet-dev
- API Key: test456...abc
- Secret: testsecret...xyz
- Testnet: true
- Description: Development/testing

### futures-keys
- API Key: futures789...def
- Secret: futuressecret...uvw
- Testnet: false
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
* Ask: Mainnet, Testnet 
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

Include `User-Agent` header with the following string: `binance-derivatives-trading-portfolio-margin/1.0.0 (Skill)`

See [`references/authentication.md`](./references/authentication.md) for implementation details.
