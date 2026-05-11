---
name: spot
description: Binance Spot request using the Binance API. Authentication requires API key and secret key. Supports testnet, mainnet, and demo.
metadata:
  version: 1.1.0
  author: Binance
  openclaw:
    skillKey: binance-spot
    requires:
      bins:
        - curl
        - openssl
        - date
    homepage: https://github.com/binance/binance-skills-hub/tree/main/skills/binance/spot/SKILL.md
license: MIT
---

# Binance Spot Skill

Spot request on Binance using authenticated API endpoints. Requires API key and secret key for certain endpoints. Return the result in JSON format.

## Quick Reference

| Endpoint | Description | Required | Optional | Authentication |
|----------|-------------|----------|----------|----------------|
| `/api/v3/exchangeInfo` (GET) | Exchange information | None | symbol, symbols, permissions, showPermissionSets, symbolStatus | No |
| `/api/v3/ping` (GET) | Test connectivity | None | None | No |
| `/api/v3/time` (GET) | Check server time | None | None | No |
| `/api/v3/aggTrades` (GET) | Compressed/Aggregate trades list | symbol | fromId, startTime, endTime, limit | No |
| `/api/v3/avgPrice` (GET) | Current average price | symbol | None | No |
| `/api/v3/depth` (GET) | Order book | symbol | limit, symbolStatus | No |
| `/api/v3/historicalTrades` (GET) | Old trade lookup | symbol | limit, fromId | No |
| `/api/v3/klines` (GET) | Kline/Candlestick data | symbol, interval | startTime, endTime, timeZone, limit | No |
| `/api/v3/ticker` (GET) | Rolling window price change statistics | None | symbol, symbols, windowSize, type, symbolStatus | No |
| `/api/v3/ticker/24hr` (GET) | 24hr ticker price change statistics | None | symbol, symbols, type, symbolStatus | No |
| `/api/v3/ticker/bookTicker` (GET) | Symbol order book ticker | None | symbol, symbols, symbolStatus | No |
| `/api/v3/ticker/price` (GET) | Symbol price ticker | None | symbol, symbols, symbolStatus | No |
| `/api/v3/ticker/tradingDay` (GET) | Trading Day Ticker | None | symbol, symbols, timeZone, type, symbolStatus | No |
| `/api/v3/trades` (GET) | Recent trades list | symbol | limit | No |
| `/api/v3/uiKlines` (GET) | UIKlines | symbol, interval | startTime, endTime, timeZone, limit | No |
| `/api/v3/openOrders` (DELETE) | Cancel All Open Orders on a Symbol | symbol | recvWindow | Yes |
| `/api/v3/openOrders` (GET) | Current open orders | None | symbol, recvWindow | Yes |
| `/api/v3/order` (POST) | New order | symbol, side, type | timeInForce, quantity, quoteOrderQty, price, newClientOrderId, strategyId, strategyType, stopPrice, trailingDelta, icebergQty, newOrderRespType, selfTradePreventionMode, pegPriceType, pegOffsetValue, pegOffsetType, recvWindow | Yes |
| `/api/v3/order` (DELETE) | Cancel order | symbol | orderId, origClientOrderId, newClientOrderId, cancelRestrictions, recvWindow | Yes |
| `/api/v3/order` (GET) | Query order | symbol | orderId, origClientOrderId, recvWindow | Yes |
| `/api/v3/order/amend/keepPriority` (PUT) | Order Amend Keep Priority | symbol, newQty | orderId, origClientOrderId, newClientOrderId, recvWindow | Yes |
| `/api/v3/order/cancelReplace` (POST) | Cancel an Existing Order and Send a New Order | symbol, side, type, cancelReplaceMode | timeInForce, quantity, quoteOrderQty, price, cancelNewClientOrderId, cancelOrigClientOrderId, cancelOrderId, newClientOrderId, strategyId, strategyType, stopPrice, trailingDelta, icebergQty, newOrderRespType, selfTradePreventionMode, cancelRestrictions, orderRateLimitExceededMode, pegPriceType, pegOffsetValue, pegOffsetType, recvWindow | Yes |
| `/api/v3/order/oco` (POST) | New OCO - Deprecated | symbol, side, quantity, price, stopPrice | listClientOrderId, limitClientOrderId, limitStrategyId, limitStrategyType, limitIcebergQty, trailingDelta, stopClientOrderId, stopStrategyId, stopStrategyType, stopLimitPrice, stopIcebergQty, stopLimitTimeInForce, newOrderRespType, selfTradePreventionMode, recvWindow | Yes |
| `/api/v3/order/test` (POST) | Test new order | symbol, side, type | computeCommissionRates, timeInForce, quantity, quoteOrderQty, price, newClientOrderId, strategyId, strategyType, stopPrice, trailingDelta, icebergQty, newOrderRespType, selfTradePreventionMode, pegPriceType, pegOffsetValue, pegOffsetType, recvWindow | Yes |
| `/api/v3/orderList` (DELETE) | Cancel Order list | symbol | orderListId, listClientOrderId, newClientOrderId, recvWindow | Yes |
| `/api/v3/orderList` (GET) | Query Order list | None | orderListId, origClientOrderId, recvWindow | Yes |
| `/api/v3/orderList/oco` (POST) | New Order list - OCO | symbol, side, quantity, aboveType, belowType | listClientOrderId, aboveClientOrderId, aboveIcebergQty, abovePrice, aboveStopPrice, aboveTrailingDelta, aboveTimeInForce, aboveStrategyId, aboveStrategyType, abovePegPriceType, abovePegOffsetType, abovePegOffsetValue, belowClientOrderId, belowIcebergQty, belowPrice, belowStopPrice, belowTrailingDelta, belowTimeInForce, belowStrategyId, belowStrategyType, belowPegPriceType, belowPegOffsetType, belowPegOffsetValue, newOrderRespType, selfTradePreventionMode, recvWindow | Yes |
| `/api/v3/orderList/opo` (POST) | New Order List - OPO | symbol, workingType, workingSide, workingPrice, workingQuantity, pendingType, pendingSide | listClientOrderId, newOrderRespType, selfTradePreventionMode, workingClientOrderId, workingIcebergQty, workingTimeInForce, workingStrategyId, workingStrategyType, workingPegPriceType, workingPegOffsetType, workingPegOffsetValue, pendingClientOrderId, pendingPrice, pendingStopPrice, pendingTrailingDelta, pendingIcebergQty, pendingTimeInForce, pendingStrategyId, pendingStrategyType, pendingPegPriceType, pendingPegOffsetType, pendingPegOffsetValue, recvWindow | Yes |
| `/api/v3/orderList/opoco` (POST) | New Order List - OPOCO | symbol, workingType, workingSide, workingPrice, workingQuantity, pendingSide, pendingAboveType | listClientOrderId, newOrderRespType, selfTradePreventionMode, workingClientOrderId, workingIcebergQty, workingTimeInForce, workingStrategyId, workingStrategyType, workingPegPriceType, workingPegOffsetType, workingPegOffsetValue, pendingAboveClientOrderId, pendingAbovePrice, pendingAboveStopPrice, pendingAboveTrailingDelta, pendingAboveIcebergQty, pendingAboveTimeInForce, pendingAboveStrategyId, pendingAboveStrategyType, pendingAbovePegPriceType, pendingAbovePegOffsetType, pendingAbovePegOffsetValue, pendingBelowType, pendingBelowClientOrderId, pendingBelowPrice, pendingBelowStopPrice, pendingBelowTrailingDelta, pendingBelowIcebergQty, pendingBelowTimeInForce, pendingBelowStrategyId, pendingBelowStrategyType, pendingBelowPegPriceType, pendingBelowPegOffsetType, pendingBelowPegOffsetValue, recvWindow | Yes |
| `/api/v3/orderList/oto` (POST) | New Order list - OTO | symbol, workingType, workingSide, workingPrice, workingQuantity, pendingType, pendingSide, pendingQuantity | listClientOrderId, newOrderRespType, selfTradePreventionMode, workingClientOrderId, workingIcebergQty, workingTimeInForce, workingStrategyId, workingStrategyType, workingPegPriceType, workingPegOffsetType, workingPegOffsetValue, pendingClientOrderId, pendingPrice, pendingStopPrice, pendingTrailingDelta, pendingIcebergQty, pendingTimeInForce, pendingStrategyId, pendingStrategyType, pendingPegPriceType, pendingPegOffsetType, pendingPegOffsetValue, recvWindow | Yes |
| `/api/v3/orderList/otoco` (POST) | New Order list - OTOCO | symbol, workingType, workingSide, workingPrice, workingQuantity, pendingSide, pendingQuantity, pendingAboveType | listClientOrderId, newOrderRespType, selfTradePreventionMode, workingClientOrderId, workingIcebergQty, workingTimeInForce, workingStrategyId, workingStrategyType, workingPegPriceType, workingPegOffsetType, workingPegOffsetValue, pendingAboveClientOrderId, pendingAbovePrice, pendingAboveStopPrice, pendingAboveTrailingDelta, pendingAboveIcebergQty, pendingAboveTimeInForce, pendingAboveStrategyId, pendingAboveStrategyType, pendingAbovePegPriceType, pendingAbovePegOffsetType, pendingAbovePegOffsetValue, pendingBelowType, pendingBelowClientOrderId, pendingBelowPrice, pendingBelowStopPrice, pendingBelowTrailingDelta, pendingBelowIcebergQty, pendingBelowTimeInForce, pendingBelowStrategyId, pendingBelowStrategyType, pendingBelowPegPriceType, pendingBelowPegOffsetType, pendingBelowPegOffsetValue, recvWindow | Yes |
| `/api/v3/sor/order` (POST) | New order using SOR | symbol, side, type, quantity | timeInForce, price, newClientOrderId, strategyId, strategyType, icebergQty, newOrderRespType, selfTradePreventionMode, recvWindow | Yes |
| `/api/v3/sor/order/test` (POST) | Test new order using SOR | symbol, side, type, quantity | computeCommissionRates, timeInForce, price, newClientOrderId, strategyId, strategyType, icebergQty, newOrderRespType, selfTradePreventionMode, recvWindow | Yes |
| `/api/v3/account` (GET) | Account information | None | omitZeroBalances, recvWindow | Yes |
| `/api/v3/account/commission` (GET) | Query Commission Rates | symbol | None | Yes |
| `/api/v3/allOrderList` (GET) | Query all Order lists | None | fromId, startTime, endTime, limit, recvWindow | Yes |
| `/api/v3/allOrders` (GET) | All orders | symbol | orderId, startTime, endTime, limit, recvWindow | Yes |
| `/api/v3/myAllocations` (GET) | Query Allocations | symbol | startTime, endTime, fromAllocationId, limit, orderId, recvWindow | Yes |
| `/api/v3/myFilters` (GET) | Query relevant filters | symbol | recvWindow | Yes |
| `/api/v3/myPreventedMatches` (GET) | Query Prevented Matches | symbol | preventedMatchId, orderId, fromPreventedMatchId, limit, recvWindow | Yes |
| `/api/v3/myTrades` (GET) | Account trade list | symbol | orderId, startTime, endTime, fromId, limit, recvWindow | Yes |
| `/api/v3/openOrderList` (GET) | Query Open Order lists | None | recvWindow | Yes |
| `/api/v3/order/amendments` (GET) | Query Order Amendments | symbol, orderId | fromExecutionId, limit, recvWindow | Yes |
| `/api/v3/rateLimit/order` (GET) | Query Unfilled Order Count | None | recvWindow | Yes |

---

## Parameters

### Common Parameters

* **symbol**: Symbol to query (e.g., BNBUSDT)
* **symbols**: List of symbols to query
* **permissions**: List of permissions to query
* **showPermissionSets**: Controls whether the content of the `permissionSets` field is populated or not. Defaults to `true` (e.g., true)
* **symbol**:  (e.g., BNBUSDT)
* **fromId**: ID to get aggregate trades from INCLUSIVE. (e.g., 1)
* **startTime**: Timestamp in ms to get aggregate trades from INCLUSIVE. (e.g., 1735693200000)
* **endTime**: Timestamp in ms to get aggregate trades until INCLUSIVE. (e.g., 1735693200000)
* **limit**: Default: 500; Maximum: 1000. (e.g., 500)
* **timeZone**: Default: 0 (UTC)
* **recvWindow**: The value cannot be greater than `60000`.   Supports up to three decimal places of precision (e.g., 6000.346) so that microseconds may be specified. (e.g., 5000)
* **timestamp**:  (e.g., 1)
* **quantity**:  (e.g., 1)
* **quoteOrderQty**:  (e.g., 1)
* **price**:  (e.g., 400)
* **newClientOrderId**: A unique id among open orders. Automatically generated if not sent.  Orders with the same `newClientOrderID` can be accepted only when the previous one is filled, otherwise the order will be rejected.
* **strategyId**:  (e.g., 1)
* **strategyType**: The value cannot be less than `1000000`. (e.g., 1)
* **stopPrice**: Used with `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TAKE_PROFIT`, and `TAKE_PROFIT_LIMIT` orders. (e.g., 1)
* **trailingDelta**: See Trailing Stop order FAQ. (e.g., 1)
* **icebergQty**: Used with `LIMIT`, `STOP_LOSS_LIMIT`, and `TAKE_PROFIT_LIMIT` to create an iceberg order. (e.g., 1)
* **pegOffsetValue**: Priceleveltopegthepriceto(max:100). SeePeggedOrdersInfo (e.g., 1)
* **orderId**:  (e.g., 1)
* **origClientOrderId**: 
* **newQty**: `newQty` must be greater than 0 and less than the order's quantity. (e.g., 1)
* **cancelNewClientOrderId**: Used to uniquely identify this cancel. Automatically generated by default.
* **cancelOrigClientOrderId**: Either `cancelOrderId` or `cancelOrigClientOrderId` must be sent.  </br> If both `cancelOrderId` and `cancelOrigClientOrderId` parameters are provided, the `cancelOrderId` is searched first, then the `cancelOrigClientOrderId` from that result is checked against that order.  </br> If both conditions are not met the request will be rejected.
* **cancelOrderId**: Either `cancelOrderId` or `cancelOrigClientOrderId` must be sent.  </br>If both `cancelOrderId` and `cancelOrigClientOrderId` parameters are provided, the `cancelOrderId` is searched first, then the `cancelOrigClientOrderId` from that result is checked against that order.  </br>If both conditions are not met the request will be rejected. (e.g., 1)
* **listClientOrderId**: A unique Id for the entire orderList
* **quantity**:  (e.g., 1)
* **limitClientOrderId**: A unique Id for the limit order
* **price**:  (e.g., 1)
* **limitStrategyId**:  (e.g., 1)
* **limitStrategyType**: The value cannot be less than `1000000`. (e.g., 1)
* **limitIcebergQty**: Used to make the `LIMIT_MAKER` leg an iceberg order. (e.g., 1)
* **stopClientOrderId**: A unique Id for the stop loss/stop loss limit leg
* **stopPrice**:  (e.g., 1)
* **stopStrategyId**:  (e.g., 1)
* **stopStrategyType**: The value cannot be less than `1000000`. (e.g., 1)
* **stopLimitPrice**: If provided, `stopLimitTimeInForce` is required. (e.g., 1)
* **stopIcebergQty**: Used with `STOP_LOSS_LIMIT` leg to make an iceberg order. (e.g., 1)
* **computeCommissionRates**: Default: `false`   See Commissions FAQ to learn more.
* **orderListId**: Either `orderListId` or `listClientOrderId` must be provided (e.g., 1)
* **aboveClientOrderId**: Arbitrary unique ID among open orders for the above order. Automatically generated if not sent
* **aboveIcebergQty**: Note that this can only be used if `aboveTimeInForce` is `GTC`. (e.g., 1)
* **abovePrice**: Can be used if `aboveType` is `STOP_LOSS_LIMIT` , `LIMIT_MAKER`, or `TAKE_PROFIT_LIMIT` to specify the limit price. (e.g., 1)
* **aboveStopPrice**: Can be used if `aboveType` is `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TAKE_PROFIT`, `TAKE_PROFIT_LIMIT`.  Either `aboveStopPrice` or `aboveTrailingDelta` or both, must be specified. (e.g., 1)
* **aboveTrailingDelta**: See Trailing Stop order FAQ. (e.g., 1)
* **aboveStrategyId**: Arbitrary numeric value identifying the above order within an order strategy. (e.g., 1)
* **aboveStrategyType**: Arbitrary numeric value identifying the above order strategy.  Values smaller than 1000000 are reserved and cannot be used. (e.g., 1)
* **abovePegOffsetValue**:  (e.g., 1)
* **belowClientOrderId**: Arbitrary unique ID among open orders for the below order. Automatically generated if not sent
* **belowIcebergQty**: Note that this can only be used if `belowTimeInForce` is `GTC`. (e.g., 1)
* **belowPrice**: Can be used if `belowType` is `STOP_LOSS_LIMIT`, `LIMIT_MAKER`, or `TAKE_PROFIT_LIMIT` to specify the limit price. (e.g., 1)
* **belowStopPrice**: Can be used if `belowType` is `STOP_LOSS`, `STOP_LOSS_LIMIT, TAKE_PROFIT` or `TAKE_PROFIT_LIMIT`  Either belowStopPrice or belowTrailingDelta or both, must be specified. (e.g., 1)
* **belowTrailingDelta**: See Trailing Stop order FAQ. (e.g., 1)
* **belowStrategyId**: Arbitrary numeric value identifying the below order within an order strategy. (e.g., 1)
* **belowStrategyType**: Arbitrary numeric value identifying the below order strategy.  Values smaller than 1000000 are reserved and cannot be used. (e.g., 1)
* **belowPegOffsetValue**:  (e.g., 1)
* **workingClientOrderId**: Arbitrary unique ID among open orders for the working order. Automatically generated if not sent.
* **workingPrice**:  (e.g., 1)
* **workingQuantity**: Sets the quantity for the working order. (e.g., 1)
* **workingIcebergQty**: This can only be used if `workingTimeInForce` is `GTC`, or if `workingType` is `LIMIT_MAKER`. (e.g., 1)
* **workingStrategyId**: Arbitrary numeric value identifying the working order within an order strategy. (e.g., 1)
* **workingStrategyType**: Arbitrary numeric value identifying the working order strategy. Values smaller than 1000000 are reserved and cannot be used. (e.g., 1)
* **workingPegOffsetValue**:  (e.g., 1)
* **pendingClientOrderId**: Arbitrary unique ID among open orders for the pending order. Automatically generated if not sent.
* **pendingPrice**:  (e.g., 1)
* **pendingStopPrice**:  (e.g., 1)
* **pendingTrailingDelta**:  (e.g., 1)
* **pendingIcebergQty**: This can only be used if `pendingTimeInForce` is `GTC` or if `pendingType` is `LIMIT_MAKER`. (e.g., 1)
* **pendingStrategyId**: Arbitrary numeric value identifying the pending order within an order strategy. (e.g., 1)
* **pendingStrategyType**: Arbitrary numeric value identifying the pending order strategy. Values smaller than 1000000 are reserved and cannot be used. (e.g., 1)
* **pendingPegOffsetValue**:  (e.g., 1)
* **pendingAboveClientOrderId**: Arbitrary unique ID among open orders for the pending above order. Automatically generated if not sent.
* **pendingAbovePrice**: Can be used if `pendingAboveType` is `STOP_LOSS_LIMIT` , `LIMIT_MAKER`, or `TAKE_PROFIT_LIMIT` to specify the limit price. (e.g., 1)
* **pendingAboveStopPrice**: Can be used if `pendingAboveType` is `STOP_LOSS`, `STOP_LOSS_LIMIT`, `TAKE_PROFIT`, `TAKE_PROFIT_LIMIT` (e.g., 1)
* **pendingAboveTrailingDelta**: See Trailing Stop FAQ (e.g., 1)
* **pendingAboveIcebergQty**: This can only be used if `pendingAboveTimeInForce` is `GTC` or if `pendingAboveType` is `LIMIT_MAKER`. (e.g., 1)
* **pendingAboveStrategyId**: Arbitrary numeric value identifying the pending above order within an order strategy. (e.g., 1)
* **pendingAboveStrategyType**: Arbitrary numeric value identifying the pending above order strategy. Values smaller than 1000000 are reserved and cannot be used. (e.g., 1)
* **pendingAbovePegOffsetValue**:  (e.g., 1)
* **pendingBelowClientOrderId**: Arbitrary unique ID among open orders for the pending below order. Automatically generated if not sent.
* **pendingBelowPrice**: Can be used if `pendingBelowType` is `STOP_LOSS_LIMIT` or `TAKE_PROFIT_LIMIT` to specify limit price (e.g., 1)
* **pendingBelowStopPrice**: Can be used if `pendingBelowType` is `STOP_LOSS`, `STOP_LOSS_LIMIT, TAKE_PROFIT or TAKE_PROFIT_LIMIT`. Either `pendingBelowStopPrice` or `pendingBelowTrailingDelta` or both, must be specified. (e.g., 1)
* **pendingBelowTrailingDelta**:  (e.g., 1)
* **pendingBelowIcebergQty**: This can only be used if `pendingBelowTimeInForce` is `GTC`, or if `pendingBelowType` is `LIMIT_MAKER`. (e.g., 1)
* **pendingBelowStrategyId**: Arbitrary numeric value identifying the pending below order within an order strategy. (e.g., 1)
* **pendingBelowStrategyType**: Arbitrary numeric value identifying the pending below order strategy. Values smaller than 1000000 are reserved and cannot be used. (e.g., 1)
* **pendingBelowPegOffsetValue**:  (e.g., 1)
* **pendingQuantity**: Sets the quantity for the pending order. (e.g., 1)
* **omitZeroBalances**: When set to `true`, emits only the non-zero balances of an account.  Default value: `false`
* **fromAllocationId**:  (e.g., 1)
* **timestamp**:  (e.g., 1)
* **preventedMatchId**:  (e.g., 1)
* **fromPreventedMatchId**:  (e.g., 1)
* **orderId**:  (e.g., 1)
* **fromExecutionId**:  (e.g., 1)
* **limit**: Default:500; Maximum: 1000 (e.g., 500)


### Enums

* **interval**: 1s | 1m | 3m | 5m | 15m | 30m | 1h | 2h | 4h | 6h | 8h | 12h | 1d | 3d | 1w | 1M
* **windowSize**: 1m | 2m | 3m | 4m | 5m | 6m | 7m | 8m | 9m | 10m | 11m | 12m | 13m | 14m | 15m | 16m | 17m | 18m | 19m | 20m | 21m | 22m | 23m | 24m | 25m | 26m | 27m | 28m | 29m | 30m | 31m | 32m | 33m | 34m | 35m | 36m | 37m | 38m | 39m | 40m | 41m | 42m | 43m | 44m | 45m | 46m | 47m | 48m | 49m | 50m | 51m | 52m | 53m | 54m | 55m | 56m | 57m | 58m | 59m | 1h | 2h | 3h | 4h | 5h | 6h | 7h | 8h | 9h | 10h | 11h | 12h | 13h | 14h | 15h | 16h | 17h | 18h | 19h | 20h | 21h | 22h | 23h | 1d | 2d | 3d | 4d | 5d | 6d
* **type**: FULL | MINI
* **type**: MARKET | LIMIT | STOP_LOSS | STOP_LOSS_LIMIT | TAKE_PROFIT | TAKE_PROFIT_LIMIT | LIMIT_MAKER | NON_REPRESENTABLE
* **selfTradePreventionMode**: NONE | EXPIRE_TAKER | EXPIRE_MAKER | EXPIRE_BOTH | DECREMENT | NON_REPRESENTABLE
* **symbolStatus**: TRADING | END_OF_DAY | HALT | BREAK | NON_REPRESENTABLE
* **timeInForce**: GTC | IOC | FOK | NON_REPRESENTABLE
* **pegPriceType**: PRIMARY_PEG | MARKET_PEG | NON_REPRESENTABLE
* **pegOffsetType**: PRICE_LEVEL | NON_REPRESENTABLE
* **newOrderRespType**: ACK | RESULT | FULL | MARKET | LIMIT
* **cancelRestrictions**: ONLY_NEW | NEW | ONLY_PARTIALLY_FILLED | PARTIALLY_FILLED
* **cancelReplaceMode**: STOP_ON_FAILURE | ALLOW_FAILURE
* **orderRateLimitExceededMode**: DO_NOTHING | CANCEL_ONLY
* **stopLimitTimeInForce**: GTC | IOC | FOK
* **side**: BUY | SELL
* **aboveType**: STOP_LOSS_LIMIT | STOP_LOSS | LIMIT_MAKER | TAKE_PROFIT | TAKE_PROFIT_LIMIT
* **aboveTimeInForce**: GTC | IOC | FOK
* **abovePegPriceType**: PRIMARY_PEG | MARKET_PEG
* **abovePegOffsetType**: PRICE_LEVEL
* **belowType**: STOP_LOSS | STOP_LOSS_LIMIT | TAKE_PROFIT | TAKE_PROFIT_LIMIT
* **belowTimeInForce**: GTC | IOC | FOK
* **belowPegPriceType**: PRIMARY_PEG | MARKET_PEG
* **belowPegOffsetType**: PRICE_LEVEL
* **workingType**: LIMIT | LIMIT_MAKER
* **workingPegPriceType**: PRIMARY_PEG | MARKET_PEG
* **workingPegOffsetType**: PRICE_LEVEL
* **pendingPegPriceType**: PRIMARY_PEG | MARKET_PEG
* **pendingPegOffsetType**: PRICE_LEVEL
* **pendingAboveType**: STOP_LOSS_LIMIT | STOP_LOSS | LIMIT_MAKER | TAKE_PROFIT | TAKE_PROFIT_LIMIT
* **pendingAbovePegPriceType**: PRIMARY_PEG | MARKET_PEG
* **pendingAbovePegOffsetType**: PRICE_LEVEL
* **pendingBelowType**: STOP_LOSS | STOP_LOSS_LIMIT | TAKE_PROFIT | TAKE_PROFIT_LIMIT
* **pendingBelowPegPriceType**: PRIMARY_PEG | MARKET_PEG
* **pendingBelowPegOffsetType**: PRICE_LEVEL
* **workingSide**: BUY | SELL
* **workingTimeInForce**: GTC | IOC | FOK
* **pendingType**: LIMIT | MARKET | STOP_LOSS | STOP_LOSS_LIMIT | TAKE_PROFIT | TAKE_PROFIT_LIMIT | LIMIT_MAKER
* **pendingSide**: BUY | SELL
* **pendingTimeInForce**: GTC | IOC | FOK
* **pendingAboveTimeInForce**: GTC | IOC | FOK
* **pendingBelowTimeInForce**: GTC | IOC | FOK


## Authentication

For endpoints that require authentication, you will need to provide Binance API credentials.
Required credentials:

* apiKey: Your Binance API key (for header)
* secretKey: Your Binance API secret (for signing)

Base URLs:
* Mainnet: https://api.binance.com
* Testnet: https://testnet.binance.vision
* Demo: https://demo-api.binance.com

## Security

### Share Credentials

Users can provide Binance API credentials in different ways. The agent will try to retrieve automatically with the two first ways the credentials, but users can also explicitly tell the agent that they have set the credentials or stored them in a `.env` file, and the agent should re-read that file when they do. The agent can also make http requests with the two first methods without user confirmation.

1. **Environment variables**

Search for the following specific variables only (never dump the full environment):

**Authorized environment variables**
- Mainnet: `BINANCE_API_KEY` and `BINANCE_SECRET_KEY`
- Testnet: `BINANCE_TESTNET_API_KEY` and `BINANCE_TESTNET_SECRET_KEY`
- Demo: `BINANCE_DEMO_API_KEY` and `BINANCE_DEMO_SECRET_KEY`

Read and use in a single exec call so the raw key never enters the agent's context:
```bash
KEY="$BINANCE_API_KEY"
SECRET="$BINANCE_SECRET_KEY"

response=$(curl -s -X GET "$URL" \
  -H "X-MBX-APIKEY: $KEY" \
  --data-urlencode "param1=value1")

echo "$response"
```

Environment variables must be set before OpenClaw starts. They are inherited at process startup and cannot be injected into a running instance. If you need to add or update credentials without restarting, use a secrets file (see option 2).

2. **Secrets file (.env)**

Check `~/.openclaw/secrets.env` , `~/.env`, or a `.env` file in the workspace. Read individual keys with `grep`, never source the full file:
```bash
# Try all credential locations in order
API_KEY=$(grep '^BINANCE_API_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)
SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' ~/.openclaw/secrets.env 2>/dev/null | cut -d= -f2-)

# Fallback: search .env in known directories (KEY=VALUE then raw line format)
for dir in ~/.openclaw ~; do
  [ -n "$API_KEY" ] && break
  env_file="$dir/.env"
  [ -f "$env_file" ] || continue

  # Read first two lines
  line1=$(sed -n '1p' "$env_file")
  line2=$(sed -n '2p' "$env_file")

  # Check if lines contain '=' indicating KEY=VALUE format
  if [[ "$line1" == *=* && "$line2" == *=* ]]; then
    API_KEY=$(grep '^BINANCE_API_KEY=' "$env_file" 2>/dev/null | cut -d= -f2-)
    SECRET_KEY=$(grep '^BINANCE_SECRET_KEY=' "$env_file" 2>/dev/null | cut -d= -f2-)
  else
    # Treat lines as raw values
    API_KEY="$line1"
    SECRET_KEY="$line2"
  fi
done
```

This file can be updated at any time without restarting OpenClaw, keys are read fresh on each invocation. Users can tell you the variables are now set or stored in a `.env` file, and you should re-read that file when they do.

3. **Inline file**

Sending a file where the content is in the following format:

```bash
abc123...xyz
secret123...key
```

* Never run `printenv`, `env`, `export`, or set without a specific variable name
* Never run `grep` on `env` files without anchoring to a specific key ('`^VARNAME='`)
* Never source a secrets file into the shell environment (`source .env` or `. .env`)
* Only read credentials explicitly needed for the current task
* Never echo or log raw credentials in output or replies
* Never commit `TOOLS.md` to version control if it contains real credentials — add it to `.gitignore`

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
6. When a request requires signing, if the request isn't an order and the API keys aren't described as `mainnet`, `testnet` or `demo` keys, try to make request to the different base urls and see if it works, without asking the user. If it works, store the keys with the corresponding environment.

## Adding New Accounts

When user provides new credentials by Inline file or message:

* Ask for account name
* Ask: Mainnet, Testnet or Demo
* Store in `TOOLS.md` with masked display confirmation 

## Signing Requests

For trading endpoints that require a signature:

1. **Detect key type first**, inspect the secret key format before signing.
2. Build query string with all parameters, including the timestamp (Unix ms).
3. Percent-encode the parameters using UTF-8 according to RFC 3986.
4. Sign query string with secretKey using HMAC SHA256, RSA, or Ed25519 (depending on the account configuration).
5. Append signature to query string.
6. Include `X-MBX-APIKEY` header.

Otherwise, do not perform steps 4–6.

## New Client Order ID 

For endpoints that include the `newClientOrderId` parameter, the value must always start with `agent-`. If the parameter is not provided, `agent-` followed by 18 random alphanumeric characters will be generated automatically. If a value is provided, it will be prefixed with `agent-`

Example: `agent-1a2b3c4d5e6f7g8h9i`

## User Agent Header

Include `User-Agent` header with the following string: `binance-spot/1.1.0 (Skill)`

See [`references/authentication.md`](./references/authentication.md) for implementation details.
