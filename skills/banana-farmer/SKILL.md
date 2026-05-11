---
name: financial-intel
description: Stock momentum scanner and portfolio intelligence. Look up any ticker for momentum scores, RSI, coil breakout patterns, and AI analysis. Scan top signals across 6,500+ stocks and crypto. Track portfolio holdings with real-time alerts. Market pulse, sector trends, win/loss proof data, and risk assessment — all through natural conversation. Powered by 730 days of backtested data with an 80% 5-day win rate.
metadata: {"clawdbot": {"requires": {"bins": ["python3"], "env": ["BF_API_KEY"]}, "primaryEnv": "BF_API_KEY", "emoji": "📊", "version": "1.9.0", "author": "clawd", "license": "MIT", "homepage": "https://bananafarmer.app", "tags": ["stocks", "crypto", "momentum", "portfolio", "market-data", "trading", "signals", "technical-analysis", "financial-data", "scanner"]}}
---

# Financial Intelligence Skill

Real-time momentum scoring and market intelligence for 6,500+ stocks and crypto assets. Powered by [Banana Farmer](https://bananafarmer.app) — an AI momentum scanner that combines technical analysis, price momentum, and social sentiment into a single 0-100 Ripeness Score.

Backed by 730 days of tracked data across 12,450+ signals with a verified 80% five-day win rate.

## Quick Start

**Option A — Self-provision a free key instantly (no account needed):**
```bash
curl -s -X POST "https://bananafarmer.app/api/bot/v1/keys/trial" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Agent", "email": "you@example.com"}'
```
Save the `key` from the response. One key per email, instant, no credit card.

**Option B — Sign up for a full account:** [bananafarmer.app/developers](https://bananafarmer.app/developers)

Then:
1. **Set your key**: `export BF_API_KEY=bf_bot_your_key_here` (or add to OpenClaw config)
2. **Try it**: `python3 scripts/bf-lookup.py AAPL` — you get score, badge, RSI, coil, price action, bull/bear case, and what to watch for

That is it. You are now scanning 6,500+ assets for momentum signals.

---

## Prompt Examples

### Single Ticker Analysis

Look up any stock or crypto symbol for a full momentum profile: score, badge, RSI, coil pattern, EMA alignment, price action, volatility, scoring breakdown, AI summary, and bull/bear cases.

**Example prompts:**
- "What's the momentum on AAPL?"
- "Look up TSLA for me"
- "How's Bitcoin looking?"
- "Check NVDA's score and technicals"
- "Is CRWV ripe?"
- "What's the coil score on AMD?"
- "Pull up the full analysis on SMCI"
- "Is PLTR overbought right now?"

**How to run:**
```bash
python3 scripts/bf-lookup.py AAPL
python3 scripts/bf-lookup.py TSLA NVDA AMD   # Multiple tickers at once
python3 scripts/bf-lookup.py BTC              # Crypto works too
```

**What you get back:** Score (0-100), badge (ripe/ripening/overripe/too-late/neutral), current price, 1d and 5d change, RSI with overbought/oversold labels, coil score with breakout flag, EMA 20/50 alignment, 52-week high proximity, volatility metrics, scoring breakdown (technical/momentum/social), key drivers, AI summary bullets, bull case, bear case, and what to watch for.

---

### Top Signals / Batch Analysis

See the highest-scoring momentum signals right now — the tickers showing the strongest alignment across technical, price action, and social indicators.

**Example prompts:**
- "What are the top signals right now?"
- "Show me the hottest momentum setups"
- "Any ripe signals today?"
- "Top 5 stocks by momentum score"
- "What's ripening that I should watch?"
- "Show me the top 20 signals"
- "Any ripe crypto signals?"

**How to run:**
```bash
python3 scripts/bf-market.py top                        # Default top 10, all badges
python3 scripts/bf-market.py top --limit 20             # Top 20
python3 scripts/bf-market.py top --badge ripe           # Only ripe signals
python3 scripts/bf-market.py top --badge ripening       # Only ripening (watchlist candidates)
python3 scripts/bf-market.py top --limit 5 --badge ripe # Top 5 ripe only
```

**What you get back:** Ranked table with symbol, score, badge, 1-day change, 5-day change, and key drivers for each signal. Results are deduplicated by symbol automatically.

---

### Portfolio Tracking

Track multiple holdings across accounts. Get a morning-brief-style intelligence report with alerts for RSI overbought/oversold, big daily moves, ripe/overripe signals, risk flags, and P&L calculations.

**Example prompts:**
- "Check my portfolio"
- "How are my holdings doing?"
- "Run a portfolio brief"
- "Any alerts on my positions?"
- "How's my aggressive account looking?"
- "What's the P&L on my tech holdings?"
- "Any of my holdings overbought?"
- "Which of my stocks are ripe right now?"

**How to run:**
```bash
python3 scripts/bf-portfolio.py portfolios.json                 # Full brief, all accounts
python3 scripts/bf-portfolio.py portfolios.json --account aaron  # Filter to one account
python3 scripts/bf-portfolio.py portfolios.json --json           # JSON output for piping
```

**Portfolio file format** (`portfolios.json`):
```json
{
  "accounts": [
    {
      "id": "personal",
      "name": "My Portfolio",
      "risk_profile": "aggressive",
      "holdings": [
        {"symbol": "AAPL", "shares": 50, "cost_basis": 185.00},
        {"symbol": "NVDA", "shares": 20, "cost_basis": 450.00},
        {"symbol": "TSLA", "shares": 10, "cost_basis": 210.00}
      ]
    },
    {
      "id": "retirement",
      "name": "IRA Account",
      "risk_profile": "conservative",
      "holdings": [
        {"symbol": "VOO", "shares": 100, "cost_basis": 430.00},
        {"symbol": "ABBV", "shares": 40, "cost_basis": 155.00}
      ]
    }
  ]
}
```

**What you get back:** Market status, data freshness, per-account sections with alerts (overbought, oversold, big moves, ripe/overripe signals, too-late warnings, risk-profile mismatches), and detailed holding lines showing price, score, badge, changes, RSI, shares, cost basis, and unrealized P&L with percentages.

**Alert types generated:**
- SIGNAL: holding is ripe or overripe
- CAUTION: holding is too-late (momentum exhausted)
- OVERBOUGHT: RSI above 70 (or 80 for strong warning)
- OVERSOLD: RSI below 30 (potential bounce zone)
- BIG MOVE: more than 5% daily change
- WEEKLY: more than 10% five-day change
- NOTE: high momentum in conservative account

---

### Market Overview

Get a bird's-eye view of the market: how many signals are firing by badge, what is trending, new ripe signals, and a narrative summary.

**Example prompts:**
- "What's the market doing today?"
- "Give me a market pulse"
- "How's the overall momentum landscape?"
- "How many ripe signals are there right now?"
- "What's trending in the market?"
- "Any new ripe signals today?"

**How to run:**
```bash
python3 scripts/bf-market.py pulse
```

**What you get back:** Narrative summary, signal counts broken down by badge (ripe, ripening, overripe, too-late, neutral), trending symbols, and newly ripe signals that just crossed the threshold.

---

### Performance Tracking / Proof Data

See which signals actually played out: winners and losers with real entry prices, current prices, percentage moves, and milestone returns over multiple time horizons.

**Example prompts:**
- "Which signals worked this week?"
- "Show me recent winners"
- "What's the track record look like?"
- "Any big movers from recent signals?"
- "Show me winners from the last 30 days"
- "What percentage of signals won this week?"
- "What were the biggest losers recently?"

**How to run:**
```bash
python3 scripts/bf-movers.py                       # Default: last 7 days, top 5
python3 scripts/bf-movers.py --days 30 --limit 10  # Last 30 days, top 10
python3 scripts/bf-movers.py --days 1 --limit 3    # Today's movers
```

**What you get back:** Winners and losers sections, each showing symbol, percentage change, entry price, current price, and milestone returns (1d, 3d, 5d, 10d). Summary line with calculated win rate for the period.

---

### Risk Assessment

Evaluate whether a stock is extended, overbought, or showing risk flags. Combine RSI, badge, coil, and volatility data into a risk picture.

**Example prompts:**
- "Is TSLA overbought?"
- "What's the risk on NVDA right now?"
- "Is AMD overripe?"
- "Should I be worried about my SMCI position?"
- "What's the max drawdown on CRWV?"
- "Is this too late to buy PLTR?"
- "Any of the top signals looking overextended?"

**How to run:**
```bash
python3 scripts/bf-lookup.py TSLA   # Check RSI, badge, volatility, and bear case
```

**What to look for in the output:**
- RSI above 70: overbought warning, watch for pullback
- RSI above 80: strongly overbought
- Badge "overripe": already extended, pullback likely
- Badge "too-late": chasing at this level carries elevated risk
- Max drawdown percentage: historical worst case from entry
- Average daily range: how volatile it trades
- Bear case: the AI-generated downside scenario

---

### Comparison Queries

Compare multiple tickers side by side for momentum scores, technicals, and risk profiles.

**Example prompts:**
- "Compare AAPL vs MSFT momentum"
- "Which has better momentum: NVDA or AMD?"
- "Look up TSLA, RIVN, and LCID"
- "Compare the big tech names — AAPL, GOOGL, MSFT, META"
- "Which mega cap has the highest coil score?"

**How to run:**
```bash
python3 scripts/bf-compare.py AAPL MSFT          # Side-by-side table comparison
python3 scripts/bf-compare.py NVDA AMD INTC AVGO # Compare semiconductor names
python3 scripts/bf-compare.py TSLA RIVN LCID     # EV sector comparison
python3 scripts/bf-lookup.py AAPL MSFT           # Full deep-dive for each (more detail)
```

**What you get back:** A formatted comparison table showing score, badge, price, RSI, coil score, EMA alignment, 52-week proximity, scoring breakdown, and volatility side by side. Includes a verdict (strongest/weakest momentum) and risk flags (overbought, coiled for breakout).

---

### Watchlist Management

Use the top signals and portfolio tools together to build and track watchlists. Filter by badge to focus on ripening setups that are worth monitoring.

**Example prompts:**
- "Add NVDA to my watchlist" (add to your portfolios.json)
- "What's ripening that I should watch?"
- "Build me a watchlist of ripening signals"
- "Update my watchlist with today's top ripening stocks"
- "Track these for me: AAPL, NVDA, AMD, TSLA"

**How to run:**
```bash
# Today's curated watchlist picks (pre-selected by the system)
python3 scripts/bf-watchlist.py picks

# Find watchlist candidates from top signals
python3 scripts/bf-market.py top --badge ripening --limit 10

# Track specific symbols (add to portfolios.json with 0 shares)
python3 scripts/bf-portfolio.py portfolios.json
```

**Tip:** Use `bf-watchlist.py picks` for the system's daily curated picks, or create a "watchlist" account in your portfolios.json with `shares: 0` and `cost_basis: 0` for each symbol. The portfolio brief will show scores, badges, RSI, and alerts without P&L calculations.

```json
{
  "id": "watchlist",
  "name": "Watchlist",
  "risk_profile": "moderate",
  "holdings": [
    {"symbol": "NVDA", "shares": 0, "cost_basis": 0},
    {"symbol": "AMD", "shares": 0, "cost_basis": 0}
  ]
}
```

---

### Sector and Theme Analysis

Analyze momentum across entire sectors, or drill into specific industry groups.

**Example prompts:**
- "Which sectors have the most momentum?"
- "What's the hottest sector right now?"
- "How are the semiconductor stocks doing?"
- "Check the EV sector — TSLA, RIVN, LCID, NIO"
- "Run the FAANG names for me"
- "What's happening in biotech?"
- "Check the momentum on airline stocks"

**How to run:**
```bash
# Full sector momentum breakdown (auto-classifies top 50 signals)
python3 scripts/bf-sectors.py

# Sector data as JSON for processing
python3 scripts/bf-sectors.py --json

# Deep-dive a specific sector group
python3 scripts/bf-compare.py NVDA AMD INTC AVGO  # Semiconductors
python3 scripts/bf-compare.py AAPL MSFT GOOGL META # Big tech
python3 scripts/bf-lookup.py TSLA RIVN LCID NIO    # Full detail per ticker
```

**What you get back:** The sectors script groups all top signals by sector (Technology, Healthcare, Financials, Energy, Consumer, Industrials, Real Estate, etc.), shows signal count, average score, heat rating (HOT/WARM/COOL/COLD), ripe signal count, and sector leaders. Use `bf-compare.py` for side-by-side comparison within a sector group.

---

### Historical Context and Win Rates

Query the system's track record and statistical performance data.

**Example prompts:**
- "What's the 5-day win rate for ripe signals?"
- "How does 1-day performance compare to 5-day?"
- "What's the average return on signals above 90?"
- "How many signals have been tracked total?"
- "What's the historical data span?"
- "Does patience actually improve win rate?"

**How to run:**
```bash
python3 scripts/bf-watchlist.py scorecard  # System win rates by holding period and score threshold
python3 scripts/bf-watchlist.py horizons   # Time horizon analysis (how long to hold)
python3 scripts/bf-market.py health        # System stats and data freshness
python3 scripts/bf-movers.py --days 30     # Recent track record with win rate
```

**Track record reference** (from 12,450 signals over 730 days):

| Holding Period | Win Rate | Avg Return | Avg Win | Avg Loss |
|----------------|----------|------------|---------|----------|
| 1 day | 76.5% | +1.35% | +2.07% | -0.97% |
| 3 days | 78.4% | +2.69% | +3.87% | -1.62% |
| 5 days | 79.9% | +4.51% | +6.24% | -2.37% |
| 10 days | 79.4% | +5.40% | +7.54% | -2.86% |
| 1 month | 80.1% | +8.16% | +11.26% | -4.33% |
| 2 months | 79.1% | +9.90% | +13.96% | -5.51% |

Key insight: Win rate starts at 76.5% on day one and climbs to 80.1% by one month. The edge is patience.

---

### Alert-Style Queries

Check for actionable conditions across your holdings or the broader market.

**Example prompts:**
- "Alert me if any holding goes ripe"
- "Any of my stocks overbought?"
- "Which holdings have RSI below 30?"
- "Are any top signals showing a coil above 70?"
- "What in my portfolio has the biggest move today?"
- "Any too-late warnings on my positions?"

**How to run:**
```bash
# Portfolio alerts (automatically flags ripe, overbought, oversold, big moves)
python3 scripts/bf-portfolio.py portfolios.json

# Market-wide scan for ripe signals
python3 scripts/bf-market.py top --badge ripe --limit 20

# Check specific names for risk
python3 scripts/bf-lookup.py AAPL TSLA NVDA
```

The portfolio brief automatically generates alerts. Look for the ALERTS section, which flags: SIGNAL (ripe/overripe), CAUTION (too-late), OVERBOUGHT (RSI > 70), OVERSOLD (RSI < 30), BIG MOVE (> 5% daily), WEEKLY (> 10% five-day), and risk-profile mismatches.

---

### System Health Check

Verify data freshness and market status before making decisions.

**Example prompts:**
- "Is the data fresh?"
- "Is the market open?"
- "Check system health"
- "Any data issues right now?"

**How to run:**
```bash
python3 scripts/bf-market.py health
```

**What you get back:** Market status (open, closed, pre-market, after-hours), data freshness (live, recent, stale), and any safety advisory. Always check health before acting on signals — stale data during market hours means something is wrong.

---

## Understanding the Data

### Ripeness Score (0-100)

The score is a composite of four pillars weighted by their predictive power:

| Pillar | Weight | What It Measures |
|--------|--------|-----------------|
| Technical Analysis | 35-55% | Chart patterns, RSI, moving averages, coil/spring patterns |
| Momentum | 25-30% | Price velocity in the 1-3% early sweet spot, volume confirmation |
| Social Sentiment | 20-45% | Reddit and X mentions, early buzz detection (1.2-2.0x normal activity) |
| Crowd Intelligence | 0-10% | Crypto only: futures positioning, funding rates |

Higher score means stronger alignment across all pillars. A score of 80 with Technical at 45% and Social at 35% tells a different story than 80 with Technical at 55% and Social at 20% — check the scoring breakdown.

### Badge System

| Badge | Score Range | What It Means | Action |
|-------|------------|---------------|--------|
| Ripe | 75-89 | High conviction setup, strong momentum with favorable entry | Best risk/reward window |
| Ripening | 60-74 | Momentum building but not fully formed | Watch, not act — add to watchlist |
| Overripe | 90-100 | Extended, may be due for consolidation or pullback | Caution, tighten stops |
| Too-Late | N/A | Already made significant move, chasing carries elevated risk | Do not chase |
| Neutral | Below 60 | No significant momentum signal | No edge, stay patient |

Score thresholds for significance: 95+ is rare and highest conviction, 85-94 is strong, 80-84 is actionable.

### RSI (Relative Strength Index)

RSI measures momentum on a 0-100 scale:
- **Below 30**: Oversold. Price has been beaten down; potential bounce zone. Does not mean "buy" — it means selling pressure may be exhausting.
- **30-70**: Normal range. No extreme reading.
- **Above 70**: Overbought. Price has been running hard; watch for pullback. Does not mean "sell" — strong trends stay overbought for weeks.
- **Above 80**: Strongly overbought. Higher probability of mean reversion.

### Coil Score (0-100)

The coil score measures price compression — how tightly a stock's price is consolidating. Think of it as a spring being compressed:
- **Below 40**: Loose. Price is moving freely, no compression buildup.
- **40-69**: Moderate compression. Some consolidation, but not yet significant.
- **70+**: Coiled. Price is compressed into a tight range. This often precedes a sharp directional move (breakout or breakdown). This is the single most predictive indicator in the system.

A stock with a high coil score AND a ripe badge is the strongest setup: momentum is aligned, and price compression suggests the next move could be significant.

### EMA 20 and EMA 50

Exponential Moving Averages smooth price data over 20 and 50 days:
- **Price above both EMAs**: Bullish trend — short and medium term aligned upward
- **Price above EMA 20, below EMA 50**: Short-term bounce in a longer downtrend — proceed with caution
- **Price below both EMAs**: Bearish trend — momentum is against you
- **EMA 20 crossing above EMA 50**: Golden cross — potential trend change

### Proximity to 52-Week High

A decimal from 0 to 1 representing how close the current price is to its 52-week high:
- **0.95+ (95%+)**: Near highs — strong relative strength, but resistance ahead
- **0.80-0.95**: Healthy uptrend territory
- **Below 0.70**: Significantly off highs — check if recovery or further decline

---

## Track Record

The system is not new. It has been tracking signals for over two years:

- **12,450+ signals analyzed** across 730 days
- **6,563 unique stocks** tracked
- **80% five-day win rate** with +4.51% average return
- **76.5% one-day win rate** climbing to **80.1% by one month**
- Win rate is consistent across score thresholds: 80+ scores all perform between 79-81%

### Win Rate by Score Threshold (5-day horizon)

| Score Range | Win Rate | Avg Return | Sample Size |
|-------------|----------|------------|-------------|
| 80-85 | 80.2% | +4.60% | 3,096 |
| 85-90 | 79.2% | +4.45% | 3,115 |
| 90-95 | 79.4% | +4.42% | 3,124 |
| 95+ | 80.7% | +4.56% | 3,115 |

### The Patience Edge

The data shows holding longer improves outcomes. Day-one win rate is 76.5%. By day five, it is 79.9%. By one month, 80.1%. Average returns scale from +1.35% (1 day) to +8.16% (1 month). The optimal risk/reward window is the 5-to-10-day holding period.

This is not a day-trading system. It catches momentum at 2% instead of 15%, then lets the move develop over days.

---

## Error Handling

### BF_API_KEY not set

```
ERROR: BF_API_KEY not set. Get your key at https://bananafarmer.app
```

**Fix:** Export your API key: `export BF_API_KEY=bf_bot_your_key_here`. Or add it to your OpenClaw config or `.env` file.

### No signal data available

```
$XYZ: No signal data available
```

**Cause:** The symbol is not tracked, was delisted, or is a very low-volume OTC stock. Banana Farmer tracks 6,500+ stocks from NYSE and NASDAQ plus popular crypto. Penny stocks and OTC issues may not have enough data for a signal.

**Fix:** Verify the ticker symbol is correct. Try the exchange-standard format (no special characters). Crypto tickers use their standard symbols (BTC, ETH, SOL).

### API timeout or connection error

```
$AAPL: Error — <urlopen error timed out>
```

**Cause:** The Banana Farmer API did not respond within 15 seconds. This can happen during high-traffic market opens or if the service is temporarily down.

**Fix:** Wait 30 seconds and retry. If repeated, check system health with `python3 scripts/bf-market.py health`. If health also times out, the API may be experiencing downtime.

### Rate limiting

The API rate limits depend on your tier: Free (10/min, 50/day), Pro (60/min, 10K/day), Max (120/min, 50K/day). Under normal usage you will not hit these limits. If you do:

**Fix:** Space out requests. The portfolio script fetches one symbol at a time, so a portfolio of 20 holdings makes 21 API calls (20 lookups + 1 health check). This is well within limits.

### Stale data warning

If `bf-market.py health` reports data freshness as "stale" during market hours, the data pipeline may be delayed. Signals and scores are based on data that refreshes every 15 minutes. Stale data (> 30 minutes old) during open market hours means scores may not reflect current conditions.

**Fix:** Note the staleness in your analysis. Prices move, but momentum signals are directional and usually remain valid for the session unless there is a major intraday reversal.

### 403 Forbidden

```
HTTP Error 403: Forbidden
```

**Cause:** Missing or malformed `User-Agent` header. The API requires a `User-Agent: BananaFarmerBot/1.0` header.

**Fix:** The scripts set this automatically. If you are calling the API directly, make sure to include the header.

---

## Advanced Usage

### JSON Output Mode

For programmatic processing, the portfolio script supports JSON output:

```bash
python3 scripts/bf-portfolio.py portfolios.json --json
```

This returns a JSON object with a `brief` field (the formatted text) and a `signals` field (score and badge for each looked-up symbol). Use this for piping into other tools, dashboards, or automated workflows.

### Multi-Account Portfolios

The portfolio file supports multiple accounts with different risk profiles. Each account gets its own section in the brief with account-specific alerts. A conservative account holding a high-momentum stock will get a NOTE alert that an aggressive account would not.

Supported risk profiles: `conservative`, `moderate`, `aggressive`. The `--account` filter accepts partial matches on both the account `id` and `name` fields.

```bash
python3 scripts/bf-portfolio.py portfolios.json --account ira
python3 scripts/bf-portfolio.py portfolios.json --account retirement
```

### Combining Scripts

Chain scripts together for richer analysis:

```bash
# Morning routine: health check, then top signals, then portfolio
python3 scripts/bf-market.py health && python3 scripts/bf-market.py top --limit 5 && python3 scripts/bf-portfolio.py portfolios.json

# Find this week's winners, then deep-dive the top one
python3 scripts/bf-movers.py --days 7 --limit 1

# Scan for ripe signals and look up each one
python3 scripts/bf-market.py top --badge ripe --limit 5
python3 scripts/bf-lookup.py AAPL NVDA AMD  # use the symbols from top output
```

### Filtering Top Signals

The `top` command supports badge and limit filters:

```bash
python3 scripts/bf-market.py top --badge ripe --limit 5     # Only highest conviction
python3 scripts/bf-market.py top --badge ripening --limit 10 # Watchlist candidates
python3 scripts/bf-market.py top --limit 50                  # Broad scan
```

### Movers Time Range

Control the lookback window for performance tracking:

```bash
python3 scripts/bf-movers.py --days 1 --limit 3   # Today only
python3 scripts/bf-movers.py --days 7 --limit 10   # This week
python3 scripts/bf-movers.py --days 30 --limit 20  # This month
```

---

## Scripts Reference

| Script | Purpose | Key Arguments |
|--------|---------|---------------|
| `bf-lookup.py` | Deep analysis of specific tickers | `SYMBOL [SYMBOL2 ...]` |
| `bf-market.py` | Market overview and signal scanning | `health`, `top [--limit N] [--badge X]`, `pulse` |
| `bf-portfolio.py` | Portfolio intelligence with alerts | `FILE.json [--account NAME] [--json]` |
| `bf-movers.py` | Winners/losers proof data | `[--days N] [--limit N]` |
| `bf-compare.py` | Side-by-side ticker comparison table | `SYMBOL1 SYMBOL2 [SYMBOL3 ...] [--json]` |
| `bf-watchlist.py` | Curated picks, scorecard, horizons | `picks`, `scorecard`, `horizons` `[--json]` |
| `bf-sectors.py` | Sector momentum breakdown | `[--json]` |

All scripts are in the `scripts/` directory. All require `python3` and `BF_API_KEY` in the environment. No additional pip packages are needed — everything uses the Python standard library.

---

## Pricing

| Plan | Price | What You Get |
|------|-------|-------------|
| Free | $0 | Health, discover, top 3 signals. 10 req/min, 50/day. Enough to verify it works. |
| Pro | $49/month ($39/mo annual) | Full 50+ leaderboard, all endpoints, proof images, portfolio, movers, watchlist, 30-day score history. 60 req/min, 10K/day. |
| Max | $149/month ($119/mo annual) | Everything in Pro + historical scores with exact prices at signal, calculated returns, full 730+ day backtesting, bulk export, webhooks. 120 req/min, 50K/day. |

Get your key instantly at [bananafarmer.app/developers](https://bananafarmer.app/developers). Free tier works immediately — no credit card needed.

For comparison: Danelfin Pro charges $79/mo for AI scores with historical data but no prices attached. Polygon.io charges $79-500/mo for raw price data with zero intelligence. Alpha Vantage is $50-250/mo for raw data. Banana Farmer Max at $149/mo gives you both — momentum intelligence AND exact prices at every signal — with 730+ days of backtesting proof. Still less than Polygon's mid-tier, with far more intelligence.

---

## Security

This skill is designed with transparency and safety in mind:

- **Outbound HTTPS only**: All scripts make only outbound HTTPS calls to `bananafarmer.app`. No other network connections, no inbound listeners, no file exfiltration.
- **Zero pip dependencies**: Every script uses only the Python standard library (`json`, `urllib`, `ssl`, `os`, `sys`). No third-party packages to audit.
- **MIT licensed**: Full source code is readable and auditable.
- **No secrets in code**: API key is read from the `BF_API_KEY` environment variable only. Never hardcoded, never logged.
- **Read-only**: The skill reads market data. It does not execute trades, manage accounts, or modify any files on your system.
- **Infrastructure security**: [Security practices](https://bananafarmer.app/security) — TLS 1.3, AES-256, Cloudflare WAF, Stripe PCI DSS Level 1.
- **Legal**: [Terms of Service](https://bananafarmer.app/terms) · [Privacy Policy](https://bananafarmer.app/privacy) · [System Status](https://bananafarmer.app/status)

---

## Disclaimer

This skill provides financial data, momentum scores, and analytical intelligence. It is **not** financial advice. All data is for informational and research purposes only.

- This tool does not make buy or sell recommendations
- Past performance does not guarantee future results
- Users should do their own research and consult a licensed financial advisor before making investment decisions
- Win rates and return figures are historical and based on backtested signal data
- Stock data is delayed 15 minutes per exchange rules; crypto data is near real-time

By using this skill, you agree to the [Banana Farmer API Terms](https://bananafarmer.app/terms#api).

Market data sourced by [Tiingo.com](https://tiingo.com). Momentum scoring, analysis, and the Ripeness Score methodology by [Banana Farmer](https://bananafarmer.app).
