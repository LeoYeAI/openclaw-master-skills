# WEEX Futures API Quick Reference

## Base URL
`https://api-contract.weex.com`

## Authentication Headers
| Header | Description |
|--------|-------------|
| ACCESS-KEY | Your API Key |
| ACCESS-SIGN | Base64(HMAC-SHA256(secret, timestamp+method+path+body)) |
| ACCESS-PASSPHRASE | Your passphrase |
| ACCESS-TIMESTAMP | Unix millisecond timestamp |

## Market Data Endpoints (No Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /capi/v2/market/time | Server time |
| GET | /capi/v2/market/contracts | All contracts info |
| GET | /capi/v2/market/ticker?symbol={symbol} | Single ticker |
| GET | /capi/v2/market/tickers | All tickers |
| GET | /capi/v2/market/depth?symbol={symbol}&limit={15\|200} | Order book |
| GET | /capi/v2/market/trades?symbol={symbol}&limit={n} | Recent trades |
| GET | /capi/v2/market/candles?symbol={symbol}&granularity={1m\|5m\|15m\|30m\|1h\|4h\|12h\|1d\|1w} | Candlesticks |
| GET | /capi/v2/market/index?symbol={symbol} | Index price |
| GET | /capi/v2/market/open_interest?symbol={symbol} | Open interest |
| GET | /capi/v2/market/currentFundRate?symbol={symbol} | Current funding rate |
| GET | /capi/v2/market/getHistoryFundRate?symbol={symbol}&limit={n} | Historical funding rates |
| GET | /capi/v2/market/funding_time?symbol={symbol} | Next funding time |

## Account Endpoints (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /capi/v2/account/getAccounts | Account list with settings |
| GET | /capi/v2/account/getAccount?coin={coin} | Single account by coin |
| GET | /capi/v2/account/assets | Account assets |
| GET | /capi/v2/account/settings?symbol={symbol} | User settings |
| POST | /capi/v2/account/leverage | Change leverage |
| POST | /capi/v2/account/adjustMargin | Adjust position margin |
| POST | /capi/v2/account/modifyAutoAppendMargin | Auto margin top-up |
| POST | /capi/v2/account/bills | Account bill history |

## Position Endpoints (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /capi/v2/account/position/allPosition | All positions |
| GET | /capi/v2/account/position/singlePosition?symbol={symbol} | Single position |
| POST | /capi/v2/account/position/changeHoldModel | Change margin mode |

## Order Endpoints (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /capi/v2/order/placeOrder | Place order |
| POST | /capi/v2/order/cancel_order | Cancel order |
| POST | /capi/v2/order/cancelAllOrders | Cancel all orders |
| POST | /capi/v2/order/closePositions | Close all positions |
| GET | /capi/v2/order/current | Current open orders |
| GET | /capi/v2/order/detail?orderId={id} | Order details |
| GET | /capi/v2/order/history | Order history |
| GET | /capi/v2/order/fills | Trade fills |

## Trigger Order Endpoints (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /capi/v2/order/plan_order | Place trigger order |
| POST | /capi/v2/order/cancel_plan | Cancel trigger order |
| GET | /capi/v2/order/currentPlan | Current trigger orders |
| GET | /capi/v2/order/historyPlan | Trigger order history |

## TP/SL Order Endpoints (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /capi/v2/order/placeTpSlOrder | Place TP/SL order |
| POST | /capi/v2/order/modifyTpSlOrder | Modify TP/SL order |

## AI Integration (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /capi/v2/order/uploadAiLog | Upload AI trading log |

## Order Parameters

### type (Order Direction)
- `1` - Open Long (buy to open long position)
- `2` - Open Short (sell to open short position)
- `3` - Close Long (sell to close long position)
- `4` - Close Short (buy to close short position)

### order_type (Execution Type)
- `0` - Normal order
- `1` - Post-only (maker only, rejected if would take)
- `2` - FOK (fill or kill - all or nothing)
- `3` - IOC (immediate or cancel - partial fill ok)

### match_price (Price Type)
- `0` - Limit order (uses price parameter)
- `1` - Market order (ignores price)

### marginMode
- `1` - Cross margin
- `3` - Isolated margin

## Response Format

All responses follow this format:
```json
{
  "code": "00000",
  "msg": "success",
  "requestTime": 1716710918113,
  "data": { ... }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 00000 | Success |
| 40001 | Invalid parameter |
| 40101 | Authentication failed |
| 40301 | Access denied / IP not whitelisted |
| 42901 | Rate limit exceeded |
| 50001 | Internal server error |

## WebSocket Endpoints

| Endpoint | Description |
|----------|-------------|
| wss://ws-contract.weex.com/v2/ws/public | Public market data |
| wss://ws-contract.weex.com/v2/ws/private | Private account data |

### Public Channels
- `ticker.{symbol}` - Real-time ticker
- `depth.{symbol}.{levels}` - Order book (5, 15, 50, 200 levels)
- `trades.{symbol}` - Real-time trades
- `kline.LAST_PRICE.{symbol}.{interval}` - Candlesticks
