# PolyVision Response Schemas

Detailed JSON response shapes for all PolyVision tools and endpoints.

## `analyze_wallet` Response

The MCP tool returns this structure. The REST API wraps the `analysis` dict inside an `AnalysisResponse` envelope.

### MCP Tool Response

```json
{
  "wallet_address": "0x...",
  "mode": "quick",
  "cached": false,
  "analysis": { /* see Analysis Object below */ },
  "usage": {
    "used_today": 5
  }
}
```

### REST API Response (`GET /v1/analyze/{wallet_address}`)

```json
{
  "wallet_address": "0x...",
  "mode": "quick",
  "cached": false,
  "analysis": { /* see Analysis Object below */ },
  "usage": {
    "used_today": 5
  }
}
```

### Analysis Object

The `analysis` dict contains ~50 fields from the comprehensive analysis engine:

```json
{
  // ── Identity ──
  "wallet": "0x...",
  "userName": "polytrader",
  "xUsername": "polytrader_x",
  "account_age_days": 365,
  "is_anonymous": false,

  // ── Position Counts ──
  "closed_count": 150,
  "open_count": 12,
  "open_winners": 8,
  "open_losers": 4,
  "total_positions": 162,
  "closed_trades": 150,

  // ── P&L Summary ──
  "total_pnl": 12500.50,
  "net_pnl": 12500.50,
  "total_unrealized_gain": 800.00,
  "total_unrealized_loss": -200.00,
  "total_closed_realized": 11900.50,
  "total_current_cash": 600.00,
  "portfolio_value": 5000.00,
  "volume": 50000.00,
  "total_invested": 50000.00,
  "total_buy_volume": 50000.00,
  "rank": 1234,

  // ── Win/Loss Stats ──
  "winners": 95,
  "losers": 50,
  "break_even": 5,
  "win_rate": 65.5,
  "avg_pnl": 83.33,
  "avg_size": 333.33,
  "worst_pnl": -500.00,
  "best_pnl": 2000.00,
  "worst_trade": -500.00,
  "best_trade": 2000.00,
  "worst_trade_pct": -4.0,

  // ── P&L Distribution ──
  "all_pnls": [100.0, -50.0, 200.0],
  "pnl_percentiles": {
    "10": -150.00,
    "25": -30.00,
    "50": 50.00,
    "75": 200.00,
    "90": 500.00
  },
  "pnl_warnings": [],

  // ── Timeline ──
  "track_record_days": 180,
  "track_record_source": "activity",
  "trading_days": 150.5,
  "first_trade_time": "2024-06-01T12:00:00",
  "last_trade_time": "2024-12-01T15:30:00",

  // ── Scoring ──
  "copy_trading_score": 7,
  "copy_trading_recommendation": "Moderate Copy — decent performance with some concerns",

  // ── Categories ──
  "categories": {
    "Sports": 45,
    "Politics": 30,
    "Crypto": 20,
    "Other": 5
  },

  // ── Category Performance ──
  "category_performance": {
    "Sports": {
      "count": 45,
      "total_pnl": 5000.00,
      "avg_pnl": 111.11,
      "win_rate": 70.0,
      "percentage_of_trades": 30.0
    },
    "Politics": {
      "count": 30,
      "total_pnl": 3000.00,
      "avg_pnl": 100.00,
      "win_rate": 60.0,
      "percentage_of_trades": 20.0
    }
  },

  // ── Risk Metrics ──
  "risk_metrics": {
    "sharpe_ratio": 1.25,
    "sortino_ratio": 1.80,
    "max_drawdown": 2500.00,
    "max_drawdown_pct": 15.0,
    "risk_rating": "🟡 Medium Risk"
  },

  // ── Red Flags ──
  "red_flags": [
    "✅ No major red flags detected"
  ],

  // ── Position Sizing ──
  "position_sizing": {
    "avg_size": 333.33,
    "median_size": 250.00,
    "min_size": 10.00,
    "max_size": 2000.00,
    "std_dev": 200.00,
    "coefficient_of_variation": 60.0,
    "consistency_rating": "Moderate"
  },

  // ── Recent Performance Windows ──
  "recent_7d": {
    "days": 7,
    "positions": 5,
    "total_pnl": 500.00,
    "avg_pnl": 100.00,
    "winners": 4,
    "losers": 1,
    "win_rate": 80.0,
    "best": 200.00,
    "worst": -50.00
  },
  "recent_30d": {
    "days": 30,
    "positions": 20,
    "total_pnl": 2000.00,
    "avg_pnl": 100.00,
    "winners": 14,
    "losers": 6,
    "win_rate": 70.0,
    "best": 500.00,
    "worst": -200.00
  },
  "recent_90d": {
    "days": 90,
    "positions": 60,
    "total_pnl": 5000.00,
    "avg_pnl": 83.33,
    "winners": 40,
    "losers": 20,
    "win_rate": 66.7,
    "best": 1000.00,
    "worst": -400.00
  },

  // ── Streaks ──
  "streaks": {
    "current_streak": 3,
    "current_streak_type": "win",
    "longest_win_streak": 8,
    "longest_loss_streak": 4
  },

  // ── Open Positions Detail ──
  "open_positions_detail": [
    {
      "title": "Russia x Ukraine ceasefire by March 31?",
      "slug": "russia-x-ukraine-ceasefire-march-31",
      "outcome": "No",
      "entry_price": 0.81,
      "current_price": 0.94,
      "size": 50000,
      "initial_value": 40500.00,
      "current_value": 47000.00,
      "unrealized_pnl": 6500.00,
      "pnl_percent": 16.05,
      "end_date": "2026-03-31"
    }
  ],

  // ── Timing (full mode only) ──
  "timing": {
    "count": 100,
    "avg_seconds": 86400.0,
    "avg_hours": 24.0,
    "avg_days": 1.0,
    "median_hours": 18.0,
    "min_hours": 0.5,
    "max_hours": 720.0,
    "percentiles": {
      "10": 2.0,
      "25": 8.0,
      "50": 18.0,
      "75": 48.0,
      "90": 168.0
    }
  }
}
```

### Field Notes

- `timing` is an empty object `{}` in quick mode. Full mode includes holding duration analysis.
- `recent_7d`, `recent_30d`, `recent_90d` contain only `{"days": N, "positions": 0}` when no trades occurred in that window.
- `streaks` may include `"unavailable": true` when activity data is not available.
- `all_pnls` is an array of every individual position P&L — can be large for active traders.
- `rank` can be an integer or the string `"N/A"` if the wallet is not on the Polymarket leaderboard.
- `red_flags` always has at least one entry: `"✅ No major red flags detected"` if clean.
- `risk_metrics.risk_rating` values: `"🟢 Low Risk"`, `"🟡 Medium Risk"`, or `"🔴 High Risk"`.
- `position_sizing.consistency_rating` values: `"Consistent"` (cv < 50), `"Moderate"` (cv < 100), or `"Highly Variable"`.
- `track_record_source` is `"activity"`, `"estimated"`, or `null`.
- `open_positions_detail` is an array of all individual open positions sorted by unrealized P&L descending (biggest winners first). Each entry includes market title, slug, outcome, entry/current price, size, values, P&L, and resolution date. The slug can be used to construct Polymarket URLs: `https://polymarket.com/event/{slug}`.

## `get_score` Response

### MCP Tool Response

```json
{
  "wallet_address": "0x...",
  "score": 7,
  "recommendation": "Moderate Copy — decent performance with some concerns",
  "tier": "yellow",
  "total_pnl": 12500.50,
  "win_rate": 65.5,
  "trade_count": 162,
  "sharpe_ratio": 1.25,
  "red_flags": ["✅ No major red flags detected"],
  "cached": true,
  "usage": {
    "used_today": 5
  }
}
```

### REST API Response (`GET /v1/score/{wallet_address}`)

Same shape as the MCP tool response. Note: the REST API coerces `score` to a float (e.g. `7.0`) via Pydantic serialization.

## `check_quota` Response

```json
{
  "used_today": 5,
  "tier": "api"
}
```

## `health` Response

```json
{
  "status": "ok"
}
```

Possible values: `"ok"` or `"degraded"`.

## `get_hot_bets` Response

### MCP Tool Response

```json
{
  "scan_date": "2026-02-14",
  "total_count": 20,
  "bets": [
    {
      "rank": 1,
      "trader": "cqs",
      "trader_wallet": "0x1234...abcd",
      "trader_username": "cqs",
      "trader_score": 10.0,
      "trader_win_rate": 68.0,
      "market_title": "Russia x Ukraine ceasefire by March 31?",
      "market_slug": "russia-x-ukraine-ceasefire-march-31",
      "outcome": "No",
      "entry_price": 0.81,
      "current_price": 0.94,
      "current_value": 47000.00,
      "unrealized_pnl": 43111.00,
      "pnl_percent": 13.0,
      "end_date": "2026-03-31",
      "days_until_resolution": 45,
      "entry_date": "2026-02-01",
      "days_since_entry": 13,
      "trader_hold_hours": 312.5,
      "polymarket_url": "https://polymarket.com/event/russia-x-ukraine-ceasefire-march-31"
    }
  ]
}
```

### REST API Response (`GET /v1/hot-bets`)

```json
{
  "scan_date": "2026-02-14",
  "total_count": 20,
  "page": 0,
  "limit": 20,
  "bets": [
    {
      "rank": 1,
      "trader_wallet": "0x1234...abcd",
      "trader_username": "cqs",
      "trader_score": 10.0,
      "trader_win_rate": 68.0,
      "market_title": "Russia x Ukraine ceasefire by March 31?",
      "market_slug": "russia-x-ukraine-ceasefire-march-31",
      "outcome": "No",
      "entry_price": 0.81,
      "current_price": 0.94,
      "current_value": 47000.00,
      "unrealized_pnl": 43111.00,
      "pnl_percent": 13.0,
      "end_date": "2026-03-31",
      "days_until_resolution": 45,
      "entry_date": "2026-02-01",
      "days_since_entry": 13,
      "trader_hold_hours": 312.5
    }
  ]
}
```

### Field Notes

- MCP response includes `trader` (display name, username or truncated wallet) and `polymarket_url` fields; REST API does not.
- REST API includes `page` and `limit` for pagination; MCP returns all results up to `limit` in a single response.
- `sort_by=rank` orders by the strategy report ranking; `sort_by=pnl` orders by `unrealized_pnl` descending.
- All price fields are in dollars. `pnl_percent` is a percentage (e.g., `13.0` means +13%).
- Nullable fields: `trader_username`, `trader_score`, `trader_win_rate`, `market_slug`, `entry_price`, `current_price`, `current_value`, `unrealized_pnl`, `pnl_percent`, `end_date`, `days_until_resolution`, `entry_date`, `days_since_entry`, `trader_hold_hours`.

## `get_leaderboard` Response

### MCP Tool Response

```json
{
  "scan_date": "2026-02-14",
  "total_count": 10,
  "entries": [
    {
      "rank": 1,
      "wallet_address": "0x1234...abcd",
      "username": "cqs",
      "x_username": "cqs_crypto",
      "total_pnl": 1250000.50,
      "volume": 5000000.00,
      "roi_percent": 25.0,
      "win_rate": 68.0,
      "sharpe_ratio": 2.1,
      "max_drawdown": 50000.00,
      "profit_factor": 3.5,
      "copy_score": 10.0,
      "recommendation": "Strong Copy — consistently profitable with strong risk management",
      "tier": "green",
      "red_flags": ["✅ No major red flags detected"],
      "track_record_days": 365,
      "last_trade_date": "2026-02-14",
      "categories": {
        "politics_pct": 60.0,
        "crypto_pct": 20.0,
        "sports_pct": 20.0
      }
    }
  ]
}
```

### REST API Response (`GET /v1/leaderboard`)

Same shape as the MCP tool response (no `page`/`limit` — always returns all entries, max 10).

### Field Notes

- `tier` is derived from `copy_score`: green (8-10), yellow (6-7.9), orange (4-5.9), red (0-3.9).
- `categories` contains `politics_pct`, `crypto_pct`, `sports_pct` — percentage of trades in each category.
- `red_flags` is a list of strings (see Red Flag Reference in SKILL.md).
- `sort_by=rank` uses the scan pipeline ranking; `sort_by=score` sorts by `copy_score` descending; `sort_by=pnl` sorts by `total_pnl` descending.
- Nullable fields: `username`, `x_username`, `total_pnl`, `volume`, `roi_percent`, `win_rate`, `sharpe_ratio`, `max_drawdown`, `profit_factor`, `copy_score`, `recommendation`, `tier`, `track_record_days`, `last_trade_date`.

## `get_strategy` Response

### MCP Tool Response

```json
{
  "scan_date": "2026-02-15",
  "total_count": 3,
  "profiles": [
    {
      "profile_name": "conservative",
      "min_price": 0.10,
      "max_price": 0.90,
      "min_score": 8.0,
      "max_trades_per_day": 3,
      "min_trade_size": 50.0,
      "position_sizing": "flat",
      "category_filter": null,
      "total_trades": 245,
      "win_rate": 0.62,
      "roi_pct": 18.5,
      "sharpe_ratio": 1.82,
      "max_drawdown_pct": 12.3,
      "profit_factor": 2.1,
      "ev_per_trade": 15.50,
      "total_pnl": 3797.50,
      "avg_win": 42.30,
      "avg_loss": 28.10,
      "adj_roi_pct": 15.2,
      "adj_total_pnl": 3124.00,
      "description": "Conservative: Entry odds 10%-90%, score 8+, max 3 trades/day, min $50. Backtested 245 trades over 90 days with 62% win rate and 1.82 Sharpe ratio. Use flat position sizing.",
      "lookback_days": 90,
      "trader_count": 10
    }
  ]
}
```

### REST API Response (`GET /v1/strategy`)

Same shape as the MCP tool response.

### Field Notes

- Always returns up to 3 profiles: `conservative`, `moderate`, `aggressive`.
- Profiles are ordered: conservative first, aggressive last.
- `win_rate` is 0.0-1.0 (not a percentage). Multiply by 100 for display.
- `position_sizing` values: `"flat"` (equal-sized), `"proportional"` (match trader allocation), `"kelly"` (Kelly criterion).
- `adj_roi_pct` and `adj_total_pnl` include realistic trading costs (0.5% slippage + 2% fee on profit).
- `description` is a plain-English summary of the profile suitable for display to users.
- All numeric fields except `profile_name`, `position_sizing`, `category_filter`, and `description` are nullable.
- `category_filter` is `null` when the profile applies to all market categories.

## `get_recent_trades` Response

### MCP Tool Response

```json
{
  "wallet_address": "0x1234...abcd",
  "since": null,
  "count": 3,
  "trades": [
    {
      "side": "BUY",
      "size": 10.5,
      "price": 0.65,
      "timestamp": 1700000000,
      "title": "Will X happen?",
      "outcome": "Yes",
      "slug": "will-x-happen",
      "transaction_hash": "0xabc123..."
    }
  ]
}
```

### REST API Response (`GET /v1/trades/{wallet_address}`)

Same shape as the MCP tool response.

### Field Notes

- `since` is `null` when no timestamp filter was applied.
- `side` is `"BUY"` or `"SELL"`.
- `timestamp` is a Unix timestamp (seconds since epoch).
- `title`, `outcome`, `slug`, and `transaction_hash` may be `null` depending on upstream data availability.
- `limit` is clamped to 1-100 (default 50).

## `discover_wallet` Response

### MCP Tool Response

```json
{
  "wallet_address": "0x1234...abcd",
  "pool_size": 250,
  "message": "Analyze this wallet with analyze_wallet or get_score tools"
}
```

### REST API Response (`GET /v1/discover`)

```json
{
  "wallet_address": "0x1234...abcd",
  "pool_size": 250,
  "message": "Analyze this wallet with /v1/analyze/{wallet} or /v1/score/{wallet}"
}
```

### Field Notes

- `wallet_address` is `null` and `pool_size` is `0` when the discovery pool is empty.
- Each call returns a different random wallet from the curated pool of 250+ elite traders.
- The returned wallet is ready to be passed to `analyze_wallet`, `get_score`, or the corresponding REST endpoints.

## `get_portfolio` Response

### MCP Tool Response

```json
{
  "total_count": 2,
  "page": 0,
  "limit": 10,
  "wallets": [
    {
      "wallet_address": "0x1234...abcd",
      "nickname": "Top Trader",
      "score": 8.5,
      "last_analyzed": "2026-02-14 12:00:00",
      "notifications_enabled": false
    }
  ]
}
```

### REST API Response (`GET /v1/portfolio`)

Same shape as the MCP tool response.

### Field Notes

- `score` is the cached copy trading score (1-10) from the last analysis, or `null` if never analyzed.
- `last_analyzed` is an ISO-ish datetime string or `null`.
- `notifications_enabled` indicates whether trade alerts are active for this wallet.
- Portfolio limits: free users can track 3 wallets, premium users can track 20.

## `add_to_portfolio` Response

### MCP Tool Response (success)

```json
{
  "wallet_address": "0x1234...abcd",
  "nickname": "Top Trader",
  "message": "Wallet added to portfolio"
}
```

### MCP Tool Response (error)

```json
{
  "error": "Wallet already in portfolio"
}
```

Possible error values: `"Wallet already in portfolio"`, `"Portfolio limit reached (3). Upgrade to premium for more slots."`, `"Failed to add wallet to portfolio"`.

### REST API Response (`POST /v1/portfolio`)

Success returns same shape as MCP. Errors return HTTP status codes: `409` (duplicate), `400` (limit reached or invalid nickname), `500` (internal error).

### REST API Request Body

```json
{
  "wallet_address": "0x1234...abcd",
  "nickname": "Top Trader"
}
```

`nickname` is optional — defaults to first 10 characters of the wallet address.

## `remove_from_portfolio` Response

### MCP Tool Response (success)

```json
{
  "wallet_address": "0x1234...abcd",
  "message": "Wallet removed from portfolio"
}
```

### MCP Tool Response (error)

```json
{
  "error": "Wallet not found in portfolio"
}
```

### REST API Response (`DELETE /v1/portfolio/{wallet_address}`)

Success returns same shape as MCP. Errors return HTTP status codes: `404` (not found), `400` (invalid address).

## Error Response

All error responses follow this shape:

```json
{
  "error": "error_type",
  "message": "Human-readable error message",
  "detail": "Optional additional context"
}
```

MCP tool errors return plain text messages instead of JSON (e.g. `"Invalid input. Please check the wallet address format."`).

## Auth Responses

### `GET /v1/auth/me`

```json
{
  "email": "you@example.com",
  "name": "My App",
  "key_prefix": "pv_live_abc12345",
  "tier": "api",
  "used_today": 5,
  "key_created_at": "2024-06-01T12:00:00",
  "key_last_used_at": "2024-12-01T15:30:00"
}
```
