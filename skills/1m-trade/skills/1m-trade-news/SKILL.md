---
name: 1m-trade-news
description: | 
  Querying crypto news, newsflashes, articles, search, and on-chain market data (ETF flows, stablecoin supply, derivatives OI, M2, DXY, Bitfinex long positions, and more). Requires BLOCKBEATS_API_KEY.
metadata:
  openclaw:
    emoji: "📰"
    requires:
      env:
        - BLOCKBEATS_API_KEY
      bins:
        - curl
    primaryEnv: BLOCKBEATS_API_KEY
    os:
      - darwin
      - linux
      - win32
    tags:
      - crypto
      - news
      - market-data
      - on-chain
      - defi
  version: 2.2.0
---

# BlockBeats API Skill

Query crypto newsflashes, articles, search, and on-chain/market datasets via the BlockBeats Pro API.

## Get an API key (follow these steps; no manual user setup needed)

If `BLOCKBEATS_API_KEY` is missing or empty, you MUST only use the environment file `~/.openclaw/.1m-trade/.env` to store/read it. **Do NOT read or touch any other files**.

1. Check `~/.openclaw/.1m-trade/.env` for `BLOCKBEATS_API_KEY`.
2. If `BLOCKBEATS_API_KEY` is missing or empty:
   - Run exactly this curl to fetch a free API key:
     ```bash
     curl --request GET --url "https://api-pro.theblockbeats.info/v1/api-key/free"
     ```
   - Parse the response and extract `data.api_key` as `BLOCKBEATS_API_KEY`.
   - In `~/.openclaw/.1m-trade/.env`, ONLY update the `BLOCKBEATS_API_KEY` entry:
     - If the key already exists, replace only that line's value.
     - If the key does not exist, append a new line:
       `BLOCKBEATS_API_KEY=<api_key>`
   - Keep all other existing env lines unchanged (do NOT overwrite the whole file).
   - Do not print the API key in chat/logs.
3. For the sections below, use `BLOCKBEATS_API_KEY` as the value for the request header `api-key: $BLOCKBEATS_API_KEY`.

## Request format
**Base URL**: `https://api-pro.theblockbeats.info`
**Auth**: all requests must include the header `api-key: $BLOCKBEATS_API_KEY`
**Response**: `{"status": 0, "message": "", "data": {...}}` — `status == 0` means success
---

## Scenario 1: Market snapshot

**Triggers**: "how is the market today", "market snapshot", "daily overview", etc.

Run the following 4 requests in parallel:

```bash
# 1) Bottom/top indicator (sentiment)
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/bottom_top_indicator"

# 2) Important newsflashes (latest 5)
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/newsflash/important" \
  -G --data-urlencode "size=5" --data-urlencode "lang=cn"

# 3) BTC ETF net flow
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/btc_etf"

# 4) Daily on-chain tx volume
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/daily_tx"
```

**Output format**:
```
📊 Market Snapshot · [Today]

Sentiment indicator: [value] → [<20 potential buy zone / 20–80 neutral / >80 potential sell zone]
BTC ETF: net flow today [value] USD (M), cumulative [value] USD (M)
On-chain tx volume: [value] (vs yesterday [↑/↓][%])
Important news:
  · [title 1] [time]
  · [title 2] [time]
  · [title 3] [time]
```

**Interpretation rules**:
- Indicator < 20 → highlight potential opportunities
- Indicator > 80 → highlight potential sell risk
- ETF positive net flow for 3 consecutive days → institutional accumulation signal
- ETF net flow > 500M/day → strong buy signal
- Rising tx volume → higher on-chain activity / market heat

---

## Scenario 2: Fund flow analysis

**Triggers**: "where is money flowing", "on-chain hotspots", "stablecoins", "smart money", etc.

Run in parallel:

```bash
# 1) Top 10 net inflow tokens (default: solana; use Base/ETH if mentioned)
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/top10_netflow" \
  -G --data-urlencode "network=solana"

# 2) Stablecoin market cap
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/stablecoin_marketcap"

# 3) BTC ETF net flow
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/btc_etf"
```

`network` values: `solana` (default) / `base` / `ethereum`

**Output format**:
```
💰 Fund Flow Analysis

On-chain trending ([network]):
  1. [token] net inflow $[value]  mcap $[value]
  2. ...

Stablecoins: USDT [↑/↓] USDC [↑/↓] (expansion / contraction)
Institutional: ETF today [in/out] [value] USD (M)
```

**Interpretation rules**:
- Stablecoin expansion → more sidelined capital, stronger bid potential
- Stablecoin contraction → capital leaving, be cautious

---

## Scenario 3: Macro environment

**Triggers**: "macro", "liquidity", "US rates", "USD", "is it a good entry", etc.

Run in parallel:

```bash
# 1) US 10Y yield
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/us10y" \
  -G --data-urlencode "type=1M"

# 2) DXY
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/dxy" \
  -G --data-urlencode "type=1M"

# 3) Compliant exchanges total assets
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/compliant_total"
```

**Output format**:
```
🌐 Macro Environment

US 10Y yield: [value]% → [up/down]
DXY: [value] → [strong/weak]
Compliant exchanges assets: $[value] → [inflow/outflow]

Overall: [bullish/neutral/bearish] for crypto
```

**Interpretation rules**:
- Rising DXY → stronger USD, crypto headwind
- Falling DXY → weaker USD, crypto tailwind
- Rising yields → higher risk-free rate, capital rotates to bonds
- Rising compliant exchange assets → stronger institutional allocation

---

## Scenario 4: Derivatives market

**Triggers**: "derivatives", "open interest", "Binance/Bybit", "leverage risk", etc.

Run in parallel:

```bash
# 1) Major venues comparison
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/contract" \
  -G --data-urlencode "dataType=1D"

# 2) Exchange snapshot
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/exchanges" \
  -G --data-urlencode "size=10"

# 3) Bitfinex BTC long positions
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/data/bitfinex_long" \
  -G --data-urlencode "symbol=btc" --data-urlencode "type=1D"
```

**Output format**:
```
⚡ Derivatives Market

Major venues OI:
  Binance [value]  Bybit [value]  Hyperliquid [value]

Exchange ranking (by volume):
  1. [name] volume $[value]  OI $[value]
  2. ...

Bitfinex BTC longs: [value] → [up/down] (leveraged long sentiment [strong/weak])
```

**Interpretation rules**:
- Rising Bitfinex longs → whales leaning long, stronger confidence
- Sharp drop → watch for long unwinds / downside risk

---

## Scenario 5: Keyword search

**Triggers**: "search [keyword]", "find [keyword]", "[keyword] news", etc.

```bash
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/search" \
  -G --data-urlencode "name=[keyword]" --data-urlencode "size=10" --data-urlencode "lang=cn"
```

Returned fields: `title`, `abstract`, `content` (plain text), `type` (0=article, 1=newsflash), `time_cn` (relative time), `url`

---

## Single-endpoint reference

### Newsflash endpoints (support `page/size/lang`)

| Endpoint | URL |
|------|-----|
| All newsflashes | `GET /v1/newsflash` |
| Important newsflashes | `GET /v1/newsflash/important` |
| Original newsflashes | `GET /v1/newsflash/original` |
| First-release newsflashes | `GET /v1/newsflash/first` |
| On-chain newsflashes | `GET /v1/newsflash/onchain` |
| Financing newsflashes | `GET /v1/newsflash/financing` |
| Prediction-market newsflashes | `GET /v1/newsflash/prediction` |
| Meme newsflashes | `GET /v1/newsflash/meme` |
| AI newsflashes | `GET /v1/newsflash/ai` |

```bash
curl -s -H "api-key: $BLOCKBEATS_API_KEY" \
  "https://api-pro.theblockbeats.info/v1/newsflash/[type]" \
  -G --data-urlencode "page=1" --data-urlencode "size=10" --data-urlencode "lang=cn"
```

### Article endpoints (support `page/size/lang`)

| Endpoint | URL |
|------|-----|
| All articles | `GET /v1/article` |
| Important articles | `GET /v1/article/important` |
| Original articles | `GET /v1/article/original` |

### Data endpoints

| Endpoint | URL | Key params |
|------|-----|---------|
| BTC ETF net flow | `GET /v1/data/btc_etf` | N/A |
| Daily on-chain tx volume | `GET /v1/data/daily_tx` | N/A |
| IBIT/FBTC net flow | `GET /v1/data/ibit_fbtc` | N/A |
| Stablecoin market cap | `GET /v1/data/stablecoin_marketcap` | N/A |
| Compliant exchanges total assets | `GET /v1/data/compliant_total` | N/A |
| US 10Y yield | `GET /v1/data/us10y` | `type=1D/1W/1M` |
| DXY | `GET /v1/data/dxy` | `type=1D/1W/1M` |
| Global M2 supply | `GET /v1/data/m2_supply` | `type=3M/6M/1Y/3Y` |
| Bitfinex BTC longs | `GET /v1/data/bitfinex_long` | `symbol=btc` `type=1D/1W/1M/h24` |
| Major derivatives venues data | `GET /v1/data/contract` | `dataType=1D/1W/1M/3M/6M/12M` |
| Bottom/top indicator | `GET /v1/data/bottom_top_indicator` | N/A |
| Top-10 net inflow | `GET /v1/data/top10_netflow` | `network=solana/base/ethereum` |
| Derivatives exchanges snapshot | `GET /v1/data/exchanges` | `name` `page` `size` |

---

## Timeframe auto-mapping

| User says | Param |
|--------|------|
| today / latest / real-time | `type=1D` or `size=5` |
| this week / recent | `type=1W` |
| this month / last month | `type=1M` |
| this year / long-term | `type=1Y` or `type=3Y` |
| last 24h (bitfinex_long only) | `type=h24` |

---

## Intent mapping

| User intent | Scenario / endpoint |
|---------|----------|
| how is the market today / daily overview | Scenario 1: Market snapshot |
| fund flows / on-chain hotspots / smart money | Scenario 2: Fund flow analysis |
| macro / M2 / yields / good entry? | Scenario 3: Macro environment |
| derivatives / open interest / leverage risk | Scenario 4: Derivatives market |
| search [keyword] | Scenario 5: Keyword search |
| latest newsflashes / list newsflashes | `GET /v1/newsflash` |
| important newsflashes | `GET /v1/newsflash/important` |
| original newsflashes | `GET /v1/newsflash/original` |
| first-release newsflashes | `GET /v1/newsflash/first` |
| on-chain newsflashes | `GET /v1/newsflash/onchain` |
| financing newsflashes / financing news | `GET /v1/newsflash/financing` |
| prediction markets / Polymarket | `GET /v1/newsflash/prediction` |
| meme news | `GET /v1/newsflash/meme` |
| AI news | `GET /v1/newsflash/ai` |
| article list | `GET /v1/article` |
| important articles | `GET /v1/article/important` |
| original articles | `GET /v1/article/original` |
| BTC ETF net flow | `GET /v1/data/btc_etf` |
| IBIT FBTC | `GET /v1/data/ibit_fbtc` |
| stablecoin market cap / USDT USDC | `GET /v1/data/stablecoin_marketcap` |
| DXY | `GET /v1/data/dxy` |
| Bitfinex longs / leverage positioning | `GET /v1/data/bitfinex_long` |
| bottom/top indicator / sentiment | `GET /v1/data/bottom_top_indicator` |
| top net inflow tokens / on-chain trending | `GET /v1/data/top10_netflow` |
| derivatives exchanges ranking | `GET /v1/data/exchanges` |
| on-chain tx volume / activity | `GET /v1/data/daily_tx` |
| compliant exchange assets / custody | `GET /v1/data/compliant_total` |

---

## Data refresh frequency

| Endpoint type | Refresh cadence |
|---------|---------|
| newsflashes / articles / search | real-time |
| top10_netflow | near real-time |
| btc_etf / ibit_fbtc / daily_tx | daily (T+1) |
| stablecoin_marketcap / compliant_total | daily |
| bottom_top_indicator | daily |
| us10y / dxy | intraday (minute-level) |
| m2_supply | monthly |
| exchanges / contract | daily |
| bitfinex_long | daily (h24 is near real-time) |

---

## Error handling

| Error | Handling |
|---------|---------|
| `BLOCKBEATS_API_KEY` missing | Prompt to set `BLOCKBEATS_API_KEY` (see the key-fetch section above) |
| HTTP 401 | API key invalid/expired |
| HTTP 403 | Plan does not allow access to the endpoint |
| `status != 0` | Show the `message` field |
| Timeout | Suggest retry; do not block other parallel requests |
| `data` empty array | Explain likely causes (non-trading day, delay, no data for asset) |

## Notes

- `content` may contain HTML; strip tags and display plain text
- `create_time` is a string in `Y-m-d H:i:s`
- Numeric fields (price/vol, etc.) are strings; you may format them as numbers
- When querying in parallel, one failed endpoint should not block the others
