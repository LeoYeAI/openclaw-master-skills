---
name: weex-trading
description: WEEX Futures exchange integration. Trade USDT-M perpetual futures with up to 125x leverage on WEEX.
metadata:
  emoji: "🔵"
  category: "trading"
  tags: ["crypto", "futures", "trading", "weex", "derivatives"]
  requires:
    bins: ["curl", "jq", "python3", "openssl"]
  compatibility:
    - claude
    - openai
    - gemini
    - llama
    - mistral
    - any-agent
---

# WEEX Futures Trading 🔵

Open AI Agent Skill for USDT-margined perpetual futures trading on WEEX exchange. Up to 125x leverage.

> **Open Agent Skill**: This skill is designed to work with any AI agent that supports bash/curl commands, including Claude, GPT, Gemini, LLaMA, Mistral, and other LLM-based agents.

## Features

- 📊 **Futures Trading** - USDT-M perpetual contracts up to 125x leverage
- 💰 **Account Management** - Balance, positions, margin settings
- 📈 **Market Data** - Tickers, order book, candlesticks, funding rates
- 🎯 **Advanced Orders** - Trigger orders, TP/SL, conditional orders
- 🤖 **AI Integration** - Log AI trading decisions
- 🔌 **Universal Compatibility** - Works with any AI agent supporting shell commands

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `WEEX_API_KEY` | API Key from WEEX | Yes |
| `WEEX_API_SECRET` | API Secret | Yes |
| `WEEX_PASSPHRASE` | API Passphrase | Yes |
| `WEEX_BASE_URL` | API base URL | No (default: https://api-contract.weex.com) |

## Authentication

```bash
API_KEY="${WEEX_API_KEY}"
SECRET="${WEEX_API_SECRET}"
PASSPHRASE="${WEEX_PASSPHRASE}"
BASE_URL="${WEEX_BASE_URL:-https://api-contract.weex.com}"

TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")

# Generate signature
generate_signature() {
  local method="$1"
  local path="$2"
  local body="$3"
  local message="${TIMESTAMP}${method}${path}${body}"
  echo -n "$message" | openssl dgst -sha256 -hmac "$SECRET" -binary | base64
}
```

---

# Market Data Endpoints (No Auth)

## Get Server Time

```bash
curl -s "${BASE_URL}/capi/v2/market/time" | jq '.'
```

## Get All Contracts Info

```bash
curl -s "${BASE_URL}/capi/v2/market/contracts" | jq '.data[] | {symbol: .symbol, baseCoin: .underlying_index, quoteCoin: .quote_currency, contractVal: .contract_val, minLeverage: .minLeverage, maxLeverage: .maxLeverage, tickSize: .tick_size, sizeIncrement: .size_increment}'
```

## Get Single Contract Info

```bash
SYMBOL="cmt_btcusdt"

curl -s "${BASE_URL}/capi/v2/market/contracts?symbol=${SYMBOL}" | jq '.data'
```

## Get Ticker Price

```bash
SYMBOL="cmt_btcusdt"

curl -s "${BASE_URL}/capi/v2/market/ticker?symbol=${SYMBOL}" | jq '.data | {symbol: .symbol, last: .last, high: .high_24h, low: .low_24h, volume: .volume_24h, markPrice: .markPrice}'
```

## Get All Tickers

```bash
curl -s "${BASE_URL}/capi/v2/market/tickers" | jq '.data[] | {symbol: .symbol, last: .last, change: .priceChangePercent, volume: .volume_24h}'
```

## Get Order Book

```bash
SYMBOL="cmt_btcusdt"

curl -s "${BASE_URL}/capi/v2/market/depth?symbol=${SYMBOL}&limit=15" | jq '.data | {asks: .asks[:5], bids: .bids[:5]}'
```

## Get Recent Trades

```bash
SYMBOL="cmt_btcusdt"
LIMIT="50"

curl -s "${BASE_URL}/capi/v2/market/trades?symbol=${SYMBOL}&limit=${LIMIT}" | jq '.data[] | {time: .time, price: .price, size: .size, side: (if .isBuyerMaker then "sell" else "buy" end)}'
```

## Get Candlestick Data

```bash
SYMBOL="cmt_btcusdt"
GRANULARITY="1h"    # 1m, 5m, 15m, 30m, 1h, 4h, 12h, 1d, 1w
LIMIT="100"

curl -s "${BASE_URL}/capi/v2/market/candles?symbol=${SYMBOL}&granularity=${GRANULARITY}&limit=${LIMIT}" | jq '.data[] | {timestamp: .[0], open: .[1], high: .[2], low: .[3], close: .[4], volume: .[5]}'
```

## Get Index Price

```bash
SYMBOL="cmt_btcusdt"

curl -s "${BASE_URL}/capi/v2/market/index?symbol=${SYMBOL}" | jq '.data | {symbol: .symbol, index: .index, timestamp: .timestamp}'
```

## Get Open Interest

```bash
SYMBOL="cmt_btcusdt"

curl -s "${BASE_URL}/capi/v2/market/open_interest?symbol=${SYMBOL}" | jq '.data[] | {symbol: .symbol, openInterest: .base_volume, value: .target_volume}'
```

## Get Current Funding Rate

```bash
SYMBOL="cmt_btcusdt"

curl -s "${BASE_URL}/capi/v2/market/currentFundRate?symbol=${SYMBOL}" | jq '.data[] | {symbol: .symbol, rate: .fundingRate, nextSettlement: .timestamp}'
```

## Get Historical Funding Rates

```bash
SYMBOL="cmt_btcusdt"
LIMIT="20"

curl -s "${BASE_URL}/capi/v2/market/getHistoryFundRate?symbol=${SYMBOL}&limit=${LIMIT}" | jq '.data[] | {symbol: .symbol, rate: .fundingRate, settleTime: .fundingTime}'
```

## Get Next Funding Time

```bash
SYMBOL="cmt_btcusdt"

curl -s "${BASE_URL}/capi/v2/market/funding_time?symbol=${SYMBOL}" | jq '.data | {symbol: .symbol, nextFundingTime: .fundingTime}'
```

---

# Account Endpoints (Auth Required)

## Get Account Assets

```bash
PATH_URL="/capi/v2/account/assets"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data[] | {coin: .coinName, available: .available, frozen: .frozen, equity: .equity, unrealizedPnl: .unrealizePnl}'
```

## Get Account List with Settings

```bash
PATH_URL="/capi/v2/account/getAccounts"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data'
```

## Get Single Account by Coin

```bash
COIN="USDT"

PATH_URL="/capi/v2/account/getAccount?coin=${COIN}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data'
```

## Get User Settings

```bash
SYMBOL="cmt_btcusdt"

PATH_URL="/capi/v2/account/settings?symbol=${SYMBOL}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data'
```

## Change Leverage

```bash
SYMBOL="cmt_btcusdt"
LEVERAGE="20"
MARGIN_MODE="1"        # 1=Cross, 3=Isolated

PATH_URL="/capi/v2/account/leverage"
BODY="{\"symbol\":\"${SYMBOL}\",\"marginMode\":${MARGIN_MODE},\"longLeverage\":\"${LEVERAGE}\",\"shortLeverage\":\"${LEVERAGE}\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

## Adjust Position Margin (Isolated Only)

```bash
POSITION_ID="123456789"      # Isolated position ID
AMOUNT="100"                 # Positive to add, negative to reduce

PATH_URL="/capi/v2/account/adjustMargin"
BODY="{\"coinId\":2,\"isolatedPositionId\":${POSITION_ID},\"collateralAmount\":\"${AMOUNT}\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

## Auto Margin Top-Up (Isolated Only)

```bash
POSITION_ID="123456789"      # Isolated position ID
AUTO_APPEND="true"           # true to enable, false to disable

PATH_URL="/capi/v2/account/modifyAutoAppendMargin"
BODY="{\"positionId\":${POSITION_ID},\"autoAppendMargin\":${AUTO_APPEND}}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

## Get Account Bill History

```bash
COIN="USDT"
LIMIT="20"

PATH_URL="/capi/v2/account/bills"
BODY="{\"coin\":\"${COIN}\",\"limit\":${LIMIT}}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.data'
```

---

# Position Endpoints (Auth Required)

## Get All Positions

```bash
PATH_URL="/capi/v2/account/position/allPosition"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data[] | select(.size != "0") | {symbol: .symbol, side: .side, size: .size, leverage: .leverage, unrealizedPnl: .unrealizePnl, entryPrice: .avg_cost}'
```

## Get Single Position

```bash
SYMBOL="cmt_btcusdt"

PATH_URL="/capi/v2/account/position/singlePosition?symbol=${SYMBOL}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data[] | {symbol: .symbol, side: .side, size: .size, leverage: .leverage, unrealizedPnl: .unrealizePnl, entryPrice: .avg_cost, liquidationPrice: .liq_price}'
```

## Change Margin Mode

```bash
SYMBOL="cmt_btcusdt"
MARGIN_MODE="1"        # 1=Cross, 3=Isolated

PATH_URL="/capi/v2/account/position/changeHoldModel"
BODY="{\"symbol\":\"${SYMBOL}\",\"marginMode\":${MARGIN_MODE},\"separatedMode\":1}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

---

# Order Endpoints (Auth Required)

## Place Market Order

```bash
SYMBOL="cmt_btcusdt"
SIZE="10"              # Quantity in contracts
TYPE="1"               # 1=Open Long, 2=Open Short, 3=Close Long, 4=Close Short
CLIENT_OID="order_$(date +%s)"

PATH_URL="/capi/v2/order/placeOrder"
BODY="{\"symbol\":\"${SYMBOL}\",\"client_oid\":\"${CLIENT_OID}\",\"size\":\"${SIZE}\",\"type\":\"${TYPE}\",\"order_type\":\"0\",\"match_price\":\"1\",\"price\":\"0\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

## Place Limit Order

```bash
SYMBOL="cmt_btcusdt"
SIZE="10"
TYPE="1"               # 1=Open Long
PRICE="90000"          # Limit price
ORDER_TYPE="0"         # 0=Normal, 1=Post-only, 2=FOK, 3=IOC
CLIENT_OID="limit_$(date +%s)"

PATH_URL="/capi/v2/order/placeOrder"
BODY="{\"symbol\":\"${SYMBOL}\",\"client_oid\":\"${CLIENT_OID}\",\"size\":\"${SIZE}\",\"type\":\"${TYPE}\",\"order_type\":\"${ORDER_TYPE}\",\"match_price\":\"0\",\"price\":\"${PRICE}\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

## Get Open Orders

```bash
PATH_URL="/capi/v2/order/current"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data[] | {orderId: .order_id, symbol: .symbol, side: .type, price: .price, size: .size, status: .status}'
```

## Get Order Details

```bash
ORDER_ID="1234567890"

PATH_URL="/capi/v2/order/detail?orderId=${ORDER_ID}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data'
```

## Get Order History

```bash
SYMBOL="cmt_btcusdt"
LIMIT="50"

PATH_URL="/capi/v2/order/history?symbol=${SYMBOL}&limit=${LIMIT}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data[] | {orderId: .order_id, symbol: .symbol, side: .type, price: .price, size: .size, filledSize: .filled_qty, status: .status}'
```

## Get Trade Fills

```bash
SYMBOL="cmt_btcusdt"
LIMIT="50"

PATH_URL="/capi/v2/order/fills?symbol=${SYMBOL}&limit=${LIMIT}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data[] | {tradeId: .trade_id, orderId: .order_id, symbol: .symbol, price: .price, size: .size, fee: .fee, time: .created_at}'
```

## Cancel Order

```bash
ORDER_ID="1234567890"

PATH_URL="/capi/v2/order/cancel_order"
BODY="{\"orderId\":\"${ORDER_ID}\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

## Cancel All Orders

```bash
SYMBOL="cmt_btcusdt"    # Optional: omit to cancel all

PATH_URL="/capi/v2/order/cancelAllOrders"
BODY="{\"symbol\":\"${SYMBOL}\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

## Close All Positions

```bash
PATH_URL="/capi/v2/order/closePositions"
BODY="{}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

---

# Trigger Order Endpoints (Auth Required)

## Place Trigger Order (Stop-Loss / Take-Profit)

```bash
SYMBOL="cmt_btcusdt"
SIZE="10"
TYPE="1"               # 1=Open Long, 2=Open Short, 3=Close Long, 4=Close Short
TRIGGER_PRICE="95000"  # Price that triggers the order
EXECUTE_PRICE="0"      # 0 for market, or limit price
TRIGGER_TYPE="1"       # 1=Fill price, 2=Mark price, 3=Index price
CLIENT_OID="trigger_$(date +%s)"

PATH_URL="/capi/v2/order/plan_order"
BODY="{\"symbol\":\"${SYMBOL}\",\"client_oid\":\"${CLIENT_OID}\",\"size\":\"${SIZE}\",\"type\":\"${TYPE}\",\"trigger_price\":\"${TRIGGER_PRICE}\",\"execute_price\":\"${EXECUTE_PRICE}\",\"trend_side\":\"1\",\"trigger_type\":\"${TRIGGER_TYPE}\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

## Get Current Trigger Orders

```bash
SYMBOL="cmt_btcusdt"

PATH_URL="/capi/v2/order/currentPlan?symbol=${SYMBOL}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data[] | {orderId: .order_id, symbol: .symbol, triggerPrice: .trigger_price, size: .size, type: .type}'
```

## Get Trigger Order History

```bash
SYMBOL="cmt_btcusdt"
LIMIT="50"

PATH_URL="/capi/v2/order/historyPlan?symbol=${SYMBOL}&limit=${LIMIT}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "GET" "$PATH_URL" "")

curl -s "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" | jq '.data[] | {orderId: .order_id, symbol: .symbol, triggerPrice: .trigger_price, status: .status}'
```

## Cancel Trigger Order

```bash
ORDER_ID="1234567890"

PATH_URL="/capi/v2/order/cancel_plan"
BODY="{\"orderId\":\"${ORDER_ID}\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

---

# TP/SL Order Endpoints (Auth Required)

## Place TP/SL Order

```bash
SYMBOL="cmt_btcusdt"
SIDE="1"               # 1=Long position, 2=Short position
TP_PRICE="100000"      # Take profit trigger price
SL_PRICE="85000"       # Stop loss trigger price
TP_SIZE="10"           # Take profit size (0 for entire position)
SL_SIZE="10"           # Stop loss size (0 for entire position)

PATH_URL="/capi/v2/order/placeTpSlOrder"
BODY="{\"symbol\":\"${SYMBOL}\",\"side\":\"${SIDE}\",\"tp_trigger_price\":\"${TP_PRICE}\",\"sl_trigger_price\":\"${SL_PRICE}\",\"tp_size\":\"${TP_SIZE}\",\"sl_size\":\"${SL_SIZE}\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

## Modify TP/SL Order

```bash
SYMBOL="cmt_btcusdt"
SIDE="1"               # 1=Long position, 2=Short position
TP_PRICE="105000"      # New take profit price
SL_PRICE="82000"       # New stop loss price

PATH_URL="/capi/v2/order/modifyTpSlOrder"
BODY="{\"symbol\":\"${SYMBOL}\",\"side\":\"${SIDE}\",\"tp_trigger_price\":\"${TP_PRICE}\",\"sl_trigger_price\":\"${SL_PRICE}\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

---

# AI Integration (Auth Required)

## Upload AI Trading Log

```bash
AI_LOG="Trading decision: Buy BTC based on momentum indicators"
ORDER_ID="1234567890"

PATH_URL="/capi/v2/order/uploadAiLog"
BODY="{\"orderId\":\"${ORDER_ID}\",\"aiLog\":\"${AI_LOG}\"}"
TIMESTAMP=$(python3 -c "import time; print(int(time.time() * 1000))")
SIGNATURE=$(generate_signature "POST" "$PATH_URL" "$BODY")

curl -s -X POST "${BASE_URL}${PATH_URL}" \
  -H "ACCESS-KEY: ${API_KEY}" \
  -H "ACCESS-SIGN: ${SIGNATURE}" \
  -H "ACCESS-PASSPHRASE: ${PASSPHRASE}" \
  -H "ACCESS-TIMESTAMP: ${TIMESTAMP}" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq '.'
```

---

# Reference Tables

## Order Types

| type | Description |
|------|-------------|
| `1` | Open Long (buy to open) |
| `2` | Open Short (sell to open) |
| `3` | Close Long (sell to close) |
| `4` | Close Short (buy to close) |

## Execution Types

| order_type | Description |
|------------|-------------|
| `0` | Normal order |
| `1` | Post-only (maker only) |
| `2` | FOK (fill or kill) |
| `3` | IOC (immediate or cancel) |

## Price Types

| match_price | Description |
|-------------|-------------|
| `0` | Limit order |
| `1` | Market order |

## Margin Modes

| marginMode | Description |
|------------|-------------|
| `1` | Cross margin |
| `3` | Isolated margin |

## Trigger Types

| trigger_type | Description |
|--------------|-------------|
| `1` | Fill price (last trade price) |
| `2` | Mark price |
| `3` | Index price |

## Popular Trading Pairs

| Pair | Description |
|------|-------------|
| cmt_btcusdt | Bitcoin / USDT |
| cmt_ethusdt | Ethereum / USDT |
| cmt_solusdt | Solana / USDT |
| cmt_xrpusdt | XRP / USDT |
| cmt_dogeusdt | Dogecoin / USDT |
| cmt_bnbusdt | BNB / USDT |

---

# Safety Rules

1. **ALWAYS** display order details before execution
2. **VERIFY** trading pair and quantity
3. **CHECK** account balance before trading
4. **WARN** about leverage risks (up to 125x)
5. **NEVER** execute without user confirmation
6. **CONFIRM** position closure before executing

---

# Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `00000` | Success | - |
| `40001` | Invalid parameter | Check parameter format |
| `40101` | Invalid API key/signature | Verify credentials and timestamp |
| `40301` | IP not whitelisted | Add IP to whitelist |
| `42901` | Rate limit exceeded | Reduce request frequency |
| `50001` | Internal error | Retry after delay |

---

# Rate Limits

| Category | IP Limit | UID Limit |
|----------|----------|-----------|
| Market Data | 20 req/sec | N/A |
| Account Info | 10 req/sec | 10 req/sec |
| Order Placement | 10 req/sec | 10 req/sec |

---

# Additional Resources

- [WEEX](https://www.weex.com)
- Base URL: `https://api-contract.weex.com`
- [API Reference](references/api_reference.md)
