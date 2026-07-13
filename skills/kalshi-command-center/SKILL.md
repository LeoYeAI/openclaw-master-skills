---
name: Kalshi Command Center
description: "Complete Kalshi trading command interface — portfolio P&L, live market scanning with edge scoring, trade execution, and risk management through your OpenClaw agent. Built-in safety: $25 max trade, 100 contract cap, $50 daily loss cutoff. Scan 600+ markets, query positions, execute trades with configurable blocklists and retry logic. Part of the OpenClaw Prediction Market Trading Stack — pairs with Kalshalyst for intelligent execution and feeds portfolio data to Market Morning Brief."
---

# Kalshi Command Center

A complete command-line interface for Kalshi prediction market trading. Provides portfolio visibility, live market scanning, trade execution, and risk management through a unified command API.

## Overview

The Kalshi Command Center bridges your OpenClaw AI assistant with Kalshi's API. Core capabilities:

- **Portfolio Management**: Real-time P&L tracking with emoji-annotated positions
- **Live Market Scanning**: Heuristic edge scoring across 600+ open markets
- **Market Queries**: Fetch live bid/ask data before trading
- **Trade Execution**: Buy/sell with Kelly sizing, risk validation, and audit logging
- **Risk Management**: Hard caps on trade size, position count, and daily loss
- **Research Cache**: Store opportunity rankings for quick reference

## Available Commands

All commands are exposed through `kalshi_commands.py` with argparse routing. Use the module directly or import individual handlers.

### Portfolio & Positions

```bash
python kalshi_commands.py portfolio
python kalshi_commands.py positions
```

**Output**: Cash balance, open positions with P&L, cost basis, and current value. Positions sorted by absolute P&L. Emoji indicators: 🔥 (>20% gain), ✅ (>5% gain), 📉 (break-even), ⚠️ (>15% loss).

Example:
```
📈 P&L: +$42.50 across 3 positions
💵 Cash: $1,234.56  ·  Deployed: $123.45  ·  Value: $165.95

🔥 Will US inflation exceed 4%?: 10x YES @ $50.00 → $62.50 (+25%)
✅ Tech market gains: 5x NO @ $40.00 → $42.10 (+5%)
➖ Political uncertainty: 25x YES @ $25.00 → $25.00 (0%)
```

### Live Market Scanning

```bash
python kalshi_commands.py scan            # macro/default markets
```

**Output**: Top 8 markets ranked by heuristic edge score. Shows bid/ask, spread (%), volume, OI, days to expiration, and composite score.

**Heuristic Scoring Algorithm**:
- Spread tightness (25% weight): Markets with tight spreads = better price discovery
- Distance from extremes (35% weight): Markets in 20-80 range = actionable
- Liquidity (25% weight): Volume + Open Interest, log-scaled
- Time value (15% weight): Sweet spot 14-60 days to close

See [references/scoring.md](references/scoring.md) for detailed algorithm.

Example:
```
🎯 Live Scan — 600 markets scanned, 47 passed filters:

1. Will US inflation exceed 4%?
   35¢/37¢ (spread 2¢ = 5.8%) | vol 1,234 | OI 5,678 | 45d
   Score: 78.5 | ECON-INFL-2026

2. Tech sector rally this quarter?
   42¢/44¢ (spread 2¢ = 4.8%) | vol 892 | OI 3,456 | 60d
   Score: 75.2 | TECH-Q1-2026
```

### Market Data Queries

```bash
python kalshi_commands.py get TICKER
```

**Output**: Live bid/ask for both YES and NO sides, last price, 24h volume, status, and actionable guidance.

Example:
```
📊 Will US inflation exceed 4%? (ECON-INFL-2026)
Status: open | Close: 2026-04-15

YES — Bid: 35¢ | Ask: 37¢ | Spread: 2¢
NO  — Bid: 63¢ | Ask: 65¢ | Spread: 2¢
Last: 35¢ | Vol 24h: 1,234 | Total vol: 12,345

💡 To sell YES contracts: sell at yes_bid (35¢) for instant fill, or post ask at 36¢ for better price.
```

### Cached Opportunities

```bash
python kalshi_commands.py markets          # macro-heavy default
python kalshi_commands.py markets all      # everything in cache
```

**Output**: Top 8 opportunities from research cache with live price refresh. Shows source, edge %, confidence, and reasoning.

### Order Management

```bash
python kalshi_commands.py orders           # list all open/resting orders
python kalshi_commands.py cancel ORDER_ID
```

### Trade Execution

Direct trade placement (low-level):

```bash
python kalshi_commands.py buy TICKER yes 10 35    # buy 10x YES @ 35¢
python kalshi_commands.py sell TICKER no 5 63     # sell 5x NO @ 63¢
```

Intelligent execution from cache (high-level):

```bash
python kalshi_commands.py execute 1              # buy pick #1 with Kelly sizing
python kalshi_commands.py execute 2 qty 25       # buy pick #2 with manual 25 contracts
python kalshi_commands.py execute 3 15 contracts # buy pick #3 with manual override
```

The `execute` handler:
1. Looks up the pick from research cache
2. Fetches live market data
3. Calculates Kelly-sized position (if available)
4. Validates risk limits
5. Places the order with audit logging

### Brier Score Calibration

```bash
python kalshi_commands.py brier           # 90 day full report
python kalshi_commands.py brier claude    # filter by Claude estimator
python kalshi_commands.py brier 30        # 30 day lookback
```

## Prerequisites

### System Requirements

- Python 3.10+

### API SDK

```bash
pip install kalshi-python
```

### Authentication & Configuration

Set environment variables OR edit your OpenClaw config:

#### Option 1: Environment Variables

```bash
export KALSHI_KEY_ID="your-api-key-id"
export KALSHI_KEY_PATH="/path/to/your/private.key"
```

#### Option 2: Config File (`~/.openclaw/config.yaml`)

```yaml
kalshi:
  enabled: true
  api_key_id: "your-key-id"
  private_key_file: "keys/kalshi-private.key"  # relative to ~/.openclaw

  # Optional: friendly names for common tickers
  ticker_names:
    ECON-INFL-2026: "Will US inflation exceed 4%?"
    TECH-Q1-2026: "Tech sector rally this quarter?"
```

**Key Path Resolution**:
1. If `private_key_file` is set: expand as `~/.openclaw/keys/{value}` if relative
2. Fallback to `private_key_path` (legacy, deprecated)
3. Try standard paths if neither set

### Optional: Kelly Position Sizing & Risk Validation

If available, the `execute` handler will use:
- `proactive.triggers.kelly_size` for position sizing
- `proactive.triggers.validate_risk` for risk gate approval

If modules are unavailable, defaults to:
- Quantity: 10 contracts (fallback)
- Risk validation: disabled (log-only)

## Market Filtering

### Blocked Categories

The scanner excludes these categories automatically:

- **Weather**: KXTEMP, KXRAIN, KXSNOW, KXWIND, KXWEATH (irrational/unhedgeable)
- **Entertainment**: KXCELEB, KXMOVIE, KXYT, KXTIKTOK (low signal)
- **Social Media**: KXTWIT, KXSTREAM (low volume)
- **Index Futures**: INX, NASDAQ, FED-MR (not Kalshi core)

See [references/blocklist.md](references/blocklist.md) for complete list.

### Sports Filter

Sports markets are intentionally excluded from the production stack. Recent evaluation did not show durable model edge there, so the system does not route sports markets into scanning or execution.

### Time Window

- Default scan: 7-180 days to expiration (interactive trading sweet spot)
- Includes volume floor (>10 contracts traded)
- Markets with tight spreads and high OI ranked first

## Risk Limits

Hard caps enforced on all trades:

| Limit | Value | Enforced By |
|-------|-------|-------------|
| Max single trade cost | $25.00 USD | `_check_risk()` |
| Max position size | 100 contracts | `_check_risk()` |
| Max daily loss | $50.00 USD | Kelly sizing + risk validator (if available) |

**Trade Audit Log**: All trades (accepted/blocked/failed) logged to `~/.openclaw/logs/trades.jsonl`.

Example audit entry:
```json
{
  "timestamp": "2026-02-26T14:35:22.123456+00:00",
  "event": "trade_placed",
  "ticker": "ECON-INFL-2026",
  "side": "yes",
  "quantity": 10,
  "price_cents": 35,
  "cost_estimate": 3.50
}
```

See [references/risk-limits.md](references/risk-limits.md) for full risk framework.

## Heuristic Edge Scoring

The `scan` command ranks markets by a 4-factor composite score:

### 1. Spread Tightness (25% weight)

```
spread_score = max(0, 20 - spread_pct) / 20
```

- Score 1.0 at 0% spread (mid = bid = ask)
- Score 0.5 at 10% spread
- Score 0.0 at 20%+ spread

Rationale: Tight spreads = more efficient price discovery, easier entry/exit.

### 2. Distance from Extremes (35% weight)

```
centrality = 1 - abs(mid - 50) / 50
if mid < 15 or mid > 85: centrality *= 0.3
```

- Score 1.0 at exactly 50¢ (maximum uncertainty)
- Score 0.5 at 25¢ or 75¢ (moderate certainty)
- Score 0.0 at 0¢ or 100¢ (resolved)
- Heavy penalty (<30% of base score) for near-settled markets

Rationale: Markets in the 20-80 range offer actionable edge. Extremes are near-certain and illiquid.

### 3. Liquidity (25% weight)

```
liq_score = log(1 + volume) * 0.6 + log(1 + oi) * 0.4
```

Log-scaled to avoid mega-markets dominating. Weights recent volume (60%) over open interest (40%).

### 4. Time Value (15% weight)

```
if days_to_close < 14: time_score = days_to_close / 14
elif days_to_close > 60: time_score = max(0.3, 1 - (days_to_close - 60) / 120)
else: time_score = 1.0
```

- Sweet spot: 14-60 days to close (score 1.0)
- Below 14d: linear ramp (less time = lower score)
- Above 60d: logarithmic decay (floor 0.3)

Rationale: Too-short markets have liquidity spikes; too-long markets lack catalysts. 14-60d is where directional bets play out.

### Composite Score

```
edge_score = (
    spread_score * 25
    + centrality * 35
    + liq_score * 25
    + time_score * 15
)
```

Weighted sum of 0-100 scale. Top 8 markets by score displayed.

See [references/scoring.md](references/scoring.md) for worked examples.

## Output Formatting

All output strips Markdown for iMessage compatibility. Emoji indicators:

| Emoji | Meaning |
|-------|---------|
| 📈 | Positive P&L or bullish signal |
| 📉 | Negative P&L or bearish signal |
| 🔥 | High gains (>20%) or strong edge |
| ✅ | Moderate gains (>5%) or approved |
| ⚠️ | Warning (>15% loss) or risk issue |
| 🔻 | Moderate loss (>0%) |
| ➖ | Break-even |
| 🎯 | Live scan results |
| 🏀 | Sports excluded / blocked |
| 💵 | Cash/financial data |
| 📊 | Market data |
| 📎 | Ticker link |
| 💰 | Proceeds/proceeds |

## Error Handling & Retry Logic

The `_get_client()` function retries on transient failures:

```python
_get_client(_retries=1, _backoff=2.0)
```

**Failure Classification**:
- `network`: Timeout, connection reset → retry with 2s backoff
- `auth`: 401/403, invalid key → fail immediately
- `rate_limit`: 429 → retry with backoff
- `unknown`: Other errors → fail immediately

**User-Facing Messages**:
- Network: "Can't reach Kalshi API — network timeout or connection reset."
- Auth: "Kalshi auth failed — API key may be expired or invalid."
- Rate limit: "Kalshi rate limited — too many requests. Try again in a minute."

## Usage Examples

### Daily Portfolio Check

```bash
python kalshi_commands.py portfolio
```

Returns cash, positions, total P&L with emoji-coded performance.

### Find New Edge Right Now

```bash
python kalshi_commands.py scan
```

Scans 600 markets, ranks by heuristic score, shows top 8 with bid/ask and days to close.

### Check Before Buying

```bash
python kalshi_commands.py get ECON-INFL-2026
```

Live bid/ask, spread, volume, and guidance on limit price strategy.

### Execute from Research Cache

```bash
python kalshi_commands.py execute 1 qty 15
```

Looks up pick #1, fetches live market data, places buy order with 15 contracts (manual override skips Kelly).

### Monitor Orders

```bash
python kalshi_commands.py orders
```

Lists all open/resting limit orders with price and remaining count.

### Exit a Position

```bash
python kalshi_commands.py get ECON-INFL-2026  # check live bid
python kalshi_commands.py sell ECON-INFL-2026 yes 10 35
```

Sell 10 contracts at bid (35¢).

## File Structure

```
kalshi-command-center/
├── SKILL.md                          # This file
├── scripts/
│   └── kalshi_commands.py            # Standalone CLI implementation (1100+ lines)
└── references/
    ├── risk-limits.md                # Risk framework documentation
    ├── blocklist.md                  # Complete market blocklist
    └── scoring.md                    # Heuristic scoring algorithm
```

## Implementation Reference

**Source**: `kalshi_commands.py` (standalone implementation)
- Env var support for API credentials
- CLI routing via argparse
- Full retry logic and error classification
- Trade audit logging
- Kelly sizing integration (optional)
- Risk validation gates (optional)

**Key Functions** (all available in `kalshi_commands.py`):
- `portfolio_command()` — cash + positions + P&L
- `scan_command()` — live scan with heuristic scoring
- `markets_command()` — cached research results
- `get_market_command(ticker)` — live bid/ask for single market
- `buy_command()`, `sell_command()` — direct order placement
- `execute_pick_command()` — intelligent execution from cache
- `get_open_orders_command()` — list resting orders
- `cancel_order_command()` — cancel by order ID
- `_get_client()` — API client with retry logic
- `_classify_kalshi_error()` — user-friendly error messages

## Troubleshooting

### "Kalshi is not enabled"

Set `kalshi.enabled: true` in `~/.openclaw/config.yaml`.

### "Kalshi key_id not configured"

Set `KALSHI_KEY_ID` env var OR `kalshi.api_key_id` in config file.

### "Kalshi private key not found"

Set `KALSHI_KEY_PATH` env var (absolute path) OR `kalshi.private_key_file` in config.

### "Auth failed — API key may be expired"

Verify key and private key file exist and are readable. Check Kalshi account for key status.

### "Can't reach Kalshi API — network timeout"

Transient network issue or Kalshi infrastructure down. Retry in 30s.

### "Kalshi rate limited — too many requests"

Back off for 1 minute. The scanner makes ~50-100 API calls per scan.

### No markets after filtering

All 600 open markets filtered out by spread/volume/timeframe. This stack intentionally excludes sports; try widening your non-sports filters instead.

## Advanced Usage

### Custom Ticker Names

Edit `~/.openclaw/config.yaml`:

```yaml
kalshi:
  ticker_names:
    ECON-INFL-2026: "Inflation >4%?"
    TECH-Q1-2026: "Tech rally Q1"
    CRYPTO-BTC-2026: "BTC >$100k?"
```

All commands will use friendly names in output.

### Audit Log Inspection

Trade execution is fully logged to `~/.openclaw/logs/trades.jsonl`:

```bash
tail -20 ~/.openclaw/logs/trades.jsonl | python -m json.tool
```

Parse to monitor trade velocity, P&L, and blocked trades.

### Dry-Run Scanning

To scan without placing orders:

```bash
python kalshi_commands.py scan
# Review output; do NOT call execute
```

## OpenClaw Ecosystem Integration

The Kalshi Command Center is your execution layer in the Prediction Market Trading Stack.

| Connected Skill | How It Connects |
|----------------|-----------------|
| **Kalshalyst** | Feeds edge opportunities → execute trades via `execute` command |
| **Market Morning Brief** | Reads your portfolio for the daily P&L digest |
| **Portfolio Drift Monitor** | Monitors positions you open through this command center |
| **Prediction Market Arbiter** | Flags cross-platform divergences → trade on the Kalshi side here |

**Install the complete stack:**
```bash
clawhub install kalshalyst kalshi-command-center polymarket-command-center prediction-market-arbiter xpulse portfolio-drift-monitor market-morning-brief personality-engine
```

## Agent Bug-Fix Protocol

**CRITICAL**: When you (the agent) discover and fix a bug in any script during a conversation, you MUST write the fix to the source file on disk using file editing tools. Showing the fix in chat is NOT sufficient — the next scheduled run starts a fresh session and will not have your conversational fix.

Checklist after finding a bug:
1. Edit the actual `.py` file on disk (e.g., `~/skills/kalshi-command-center/scripts/kalshi_commands.py`)
2. Also update the installed copy at `~/.openclaw/skills/kalshi-command-center/scripts/kalshi_commands.py`
3. Confirm both files are written before telling the user the fix is done
4. If the fix is significant, stage a git commit in `~/skills/`

Never say "fixed" if you only demonstrated the fix in conversation output.

## Attribution

**Author**: KingMadeLLC
**Version**: 1.0.0


---

## Feedback & Issues

Found a bug? Have a feature request? Want to share results?

- **GitHub Issues**: [github.com/kingmadellc/openclaw-prediction-stack/issues](https://github.com/kingmadellc/openclaw-prediction-stack/issues)
- **X/Twitter**: [@KingMadeLLC](https://x.com/KingMadeLLC)

Part of the **OpenClaw Prediction Stack** — the first prediction market skill suite on ClawHub.
