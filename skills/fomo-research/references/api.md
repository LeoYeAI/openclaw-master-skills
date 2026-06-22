# Cope Capital API Reference (v0.3.0)

Full interactive docs: https://api.cope.capital/docs

## Base URL

```
https://api.cope.capital
```

## Authentication

All endpoints (except POST /v1/register) require:
```
Authorization: Bearer cope_YOUR_KEY
```

## Response Formats

### Activity Item
```json
{
  "fomo_handle": "frankdegods",
  "wallet": "A5SEXYJY4jTEi6sjMLfZs5KAP8SVFvLDPDV67GgSSZSk",
  "chain": "solana",
  "action": "buy",
  "token_mint": "DezX7iJ4W8VqRXPpWLNq6YYr5ky2nrSR1GvSa8L7pump",
  "token_symbol": "BONK",
  "usd_amount": 2400.50,
  "timestamp": 1707603400
}
```

### Leaderboard Entry
```json
{
  "handle": "frankdegods",
  "display_name": "[PN] frank",
  "solana_address": "A5SEXY...",
  "base_address": "0x542b6b...",
  "pnl": 295066.84,
  "num_trades": 1404,
  "swap_count": 3686,
  "total_volume": 28357527.58,
  "followers": 73288,
  "total_holdings": 14
}
```

### Handle Stats (NEW in v0.2.0)
```json
{
  "handle": "frankdegods",
  "wallets": 2,
  "chains": ["solana", "base"],
  "stats": {
    "total_trades": 42,
    "wins": 28,
    "win_rate": 66.7,
    "total_pnl": 15234.50,
    "total_invested": 32100.00,
    "roi_pct": 47.5,
    "avg_pnl": 362.73,
    "best_trade": 5430.00,
    "worst_trade": -1200.00,
    "first_trade": 1769900000,
    "last_trade": 1770800000
  },
  "by_chain": [
    { "chain": "solana", "trades": 30, "wins": 20, "pnl": 12000.00, "win_rate": 66.7 }
  ],
  "top_trades": [
    { "symbol": "BONK", "pnl": 5430.00, "usd_in": 1000.00, "roi_pct": 543.0, "chain": "solana" }
  ],
  "open_positions": 5,
  "open_cost_basis": 2500.00
}
```

### Token Thesis (NEW in v0.2.0)
```json
{
  "token": { "mint": "...", "chain": "base", "symbol": "KELLY", "price_usd": 0.00015, "market_cap": 150000 },
  "thesis_count": 5,
  "sentiment": {
    "holding": 4,
    "closed": 1,
    "total_exposure_usd": 52000.00,
    "avg_unrealized_pnl_pct": 12.5
  },
  "theses": [
    {
      "handle": "Stacco",
      "display_name": "Stacco",
      "comment": "Kelly is the only answer for this meta. Dev is competent.",
      "created_at": "2026-02-19T00:12:06.007Z",
      "likes": 3,
      "replies": 1,
      "position": {
        "usd_value": 17178.83,
        "unrealized_pnl_usd": 2246.33,
        "unrealized_pnl_pct": 15.04,
        "is_closed": false
      }
    }
  ]
}
```

### Convergence Event (NEW in v0.2.0)
```json
{
  "id": 1,
  "token": { "mint": "...", "symbol": "MUSHU", "chain": "solana" },
  "wallet_count": 5,
  "wallets": [
    { "handle": "quotes", "amount_usd": 3076, "win_rate": 0.846 }
  ],
  "total_usd_in": 15400,
  "price_at_detection": 0.000189,
  "mcap_at_detection": 159000,
  "peak_price_after": 0.000567,
  "max_gain_pct": 200.0,
  "detected_at": 1771348000
}
```

### Hot Token (NEW in v0.2.0)
```json
{
  "token_mint": "...",
  "token_symbol": "BONK",
  "chain": "solana",
  "buyer_count": 8,
  "total_usd": 45000.00,
  "top_buyers": ["frankdegods", "randomxbt", "quotes"]
}
```

### Traders Search Result (NEW in v0.3.0)
```json
{
  "traders": [
    {
      "handle": "frankdegods",
      "address": "A5SEXY...",
      "chain": "solana",
      "win_rate": 0.75,
      "total_trades": 142,
      "realized_pnl": 45000.00,
      "total_volume": 280000.00
    }
  ],
  "count": 15
}
```

### Handle Positions (NEW in v0.3.0)
```json
{
  "handle": "frankdegods",
  "positions": [
    {
      "token_mint": "DezX7iJ4...",
      "token_symbol": "BONK",
      "chain": "solana",
      "status": "open",
      "total_bought_usd": 5000.00,
      "total_sold_usd": 2000.00,
      "net_usd": -3000.00,
      "buy_count": 3,
      "sell_count": 1,
      "first_buy_at": 1770800000,
      "last_activity_at": 1771200000
    }
  ]
}
```

### Handle Theses (NEW in v0.3.0)
```json
{
  "handle": "frankdegods",
  "theses": [
    {
      "token_mint": "DezX7iJ4...",
      "token_symbol": "BONK",
      "chain": "solana",
      "comment": "This is the play for the cycle",
      "created_at": "2026-02-19T00:12:06.007Z",
      "likes": 5,
      "replies": 2,
      "position": {
        "usd_value": 5000.00,
        "unrealized_pnl_pct": 25.0,
        "is_closed": false
      }
    }
  ]
}
```

## Query Parameters

### GET /v1/activity
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| watchlist_id | string | — | Filter to specific watchlist |
| handle | string | — | Filter to specific Fomo handle |
| chain | string | all | `solana`, `base`, or `all` |
| action | string | all | `buy`, `sell`, or `all` |
| min_usd | number | — | Minimum trade size in USD |
| since | number | — | Unix ms timestamp |
| limit | number | 50 | Max results (1-100) |
| cursor | string | — | Pagination cursor |

### GET /v1/activity/poll
Same filters as /v1/activity. Returns `{ count, latest_at }` only.

### GET /v1/leaderboard
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| timeframe | string | 7d | `24h`, `7d`, `30d`, or `all` |
| limit | number | 50 | Max results (1-100) |

### GET /v1/trending/handles
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| limit | number | 20 | Max results (1-100) |

### GET /v1/tokens/hot (NEW)
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| hours | number | 24 | Lookback window (max 168) |
| chain | string | all | `solana` or `base` |
| limit | number | 20 | Max results (max 50) |

### GET /v1/handle/:handle/stats (NEW)
No query params. Returns full stats for the given Fomo handle.

### GET /v1/tokens/:mint/thesis (NEW)
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| chain | string | solana | `solana` or `base` |
| limit | number | 10 | Max theses (max 50) |

### GET /v1/convergence (NEW)
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| since | number | — | Unix ms timestamp |
| chain | string | all | `solana` or `base` |
| limit | number | 20 | Max results |

### GET /v1/traders/search (NEW in v0.3.0)
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| min_win_rate | number | — | Minimum win rate (0-100) |
| max_win_rate | number | — | Maximum win rate (0-100) |
| min_trades | number | — | Minimum total trades |
| min_pnl | number | — | Minimum realized PnL in USD |
| sort_by | string | win_rate | `win_rate`, `pnl`, `trades`, `volume` |
| chain | string | all | `solana` or `base` |
| limit | number | 50 | Max results (1-100) |

### GET /v1/handle/:handle/positions (NEW in v0.3.0)
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| status | string | all | `open`, `closed`, or `all` |
| chain | string | all | `solana` or `base` |

### GET /v1/handle/:handle/theses (NEW in v0.3.0)
No query params. Returns all theses by the given handle (up to 20 recent tokens).

## Rate Limits

| Tier | Rate | Daily Activity Calls | Watchlists | Handles/Watchlist |
|------|------|---------------------|------------|-------------------|
| Free | 10/min | 250 (resets midnight UTC) | 1 | 10 |
| x402 | 300/min | Unlimited ($0.005/call) | 10 | 100 |

Only `/v1/activity` counts toward the daily limit. All other endpoints are always free with no cap.

## Chains

Only `solana` and `base` are supported. Invalid chain values return 400.

## Actions

Only `buy` and `sell` are supported. Invalid action values return 400.
