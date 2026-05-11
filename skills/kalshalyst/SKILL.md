---
name: Kalshalyst
description: "Contrarian prediction market scanner that finds mispricings on Kalshi using Claude Sonnet analysis, Brier score calibration, and Kelly Criterion position sizing. Five-phase pipeline: fetch markets, classify, estimate contrarian probabilities, calculate edge, and alert. Tracks estimate accuracy over time so you know when to trust the signal. Part of the OpenClaw Prediction Market Trading Stack — feeds edge data to Market Morning Brief and pairs with Kalshi Command Center for execution."
license: MIT
---

# Kalshalyst — Contrarian Prediction Market Scanner

## Overview

Kalshalyst is a complete intelligence system for finding and trading prediction market opportunities. It combines:

- **Claude Sonnet contrarian estimation** — sees market prices and finds reasons they're WRONG
- **Brier score tracking** — measures how well your estimates calibrate against actual outcomes
- **Kelly Criterion position sizing** — calculates optimal trade size for each opportunity
- **Five-phase pipeline** — FETCH → CLASSIFY → ESTIMATE → EDGE → ALERT

The key insight: blind estimation (not seeing prices) produces consensus-matching estimates with zero edge. **Contrarian mode** (showing Claude the price and asking it to disagree) produces opinionated, directional calls with real edge.

## When to Use This Skill

- You want to find mispricings on Kalshi prediction markets
- You're looking for contrarian opportunities where the market is wrong
- You need to track how accurate your probability estimates are over time
- You want to size positions intelligently based on edge and confidence
- You're building a systematic prediction market trading system

First run does not require Kalshi credentials. If they are missing, Kalshalyst prints a realistic demo scan and writes demo cache data so downstream tools like Market Morning Brief still have something useful to show.

## Requirements

### API Keys & Credentials

<!-- CODEX: reconciled skill requirements and cost guidance with the public code path. -->

1. **Kalshi API Key** (free at kalshi.com)
   - Sign up at https://kalshi.com
   - Navigate to Settings → API
   - Generate API credentials (key ID + private key file)
   - Cost: Free tier supports unlimited reads, small position limits

2. **Anthropic API Key** (for Claude Sonnet)
   - Create account at https://console.anthropic.com
   - Generate an API key
   - The public reference implementation calls Anthropic directly
   - Budget: variable by scan volume; expect non-zero Claude cost if you run frequent scans

3. **Polygon.io API Key** (optional, free tier available)
   - Sign up at https://polygon.io
   - Free tier includes market data + basic news
   - Cost: Free tier sufficient, paid plans for higher volume

### Python & Dependencies

- Python 3.10 or higher
- Required packages:
  ```bash
  pip install kalshi-python requests anthropic pyyaml
  ```

- Optional (for local fallback estimation):
  - Ollama (https://ollama.ai) with Qwen model
  - Install from https://ollama.ai (macOS, Linux, Windows)
  - Then: `ollama pull qwen3:latest`

## Configuration

Create or update your `config.yaml` file with:

```yaml
kalshi:
  enabled: true
  api_key_id: "your-key-id-here"
  private_key_file: "path/to/private.key"
  ticker_names: {}  # Optional: custom display names for tickers

anthropic:
  api_key: "sk-ant-..."

polygon:
  api_key: "pk_..."  # Optional

kalshalyst:
  enabled: true
  check_interval_minutes: 60
  min_volume: 50
  min_days_to_close: 7
  max_days_to_close: 365
  max_pages: 10
  max_markets_to_analyze: 50
  min_edge_pct: 3.0
  min_qwen_confidence: 0.4
  alert_edge_pct: 6.0
  max_alerts: 5
  max_fetch_seconds: 30
  page_timeout_seconds: 8
```

## The Five-Phase Pipeline

### Phase 1: FETCH — Kalshi Market Discovery

Fetches all open markets from Kalshi and applies pre-filters:

**Blocklist Filtering:**
- **Ticker prefixes**: KXHIGH, KXLOW, KXRAIN, KXSNOW, INX, NASDAQ (weather, intraday noise)
- **Category slugs**: weather, climate, entertainment, sports, social-media
- **Micro-timeframes**: "in next 15 min", "in next 5 hours" (coin flips)
- **Sports tokens**: NFL, NBA, soccer, esports (blocked from the production stack)

**Timeframe Gates:**
- Minimum days to close: 7 (default)
- Maximum days to close: 365 (default)
- Markets without expiration dates are blocked (usually garbage)

**Volume Floor:**
- Minimum volume: 50 contracts (default)
- Filters out illiquid, low-interest markets

**Price Availability:**
- Must have at least one price signal (yes_bid, yes_ask, yes_price, or last_price)
- Resolves multiple price sources (bid/ask mid preferred)

**Output:** List of ~100-500 pre-filtered markets ready for analysis

### Phase 2: CLASSIFY — Market Classification

**Status: Disabled (Qwen unreliable)** — Markets pass through with defaults.

When re-enabled, would use local Qwen to classify each market by:
- Category: politics, economics, crypto, policy, technology, etc.
- Tradability: 0.0-1.0 score (how analyzable with public info?)
- News sensitivity: True if breaking news would materially shift the probability

For now, all markets receive default classification values and proceed to Phase 3.

### Phase 3: ESTIMATE — Claude Contrarian Probability Estimation

**The core IP.** Claude sees the market price and is asked to find reasons it's WRONG.

**System Prompt (Contrarian Mode):**
```
You are a contrarian prediction market analyst. You look for reasons markets are WRONG.

Your job: given a prediction market and its current price, determine if there's a
directional opportunity. You are advising a sophisticated trader who uses limit orders.

CRITICAL RULES:
1. You WILL be shown the current market price. Your job is to DISAGREE with it when you have reason to.
2. Don't just confirm the market. That's worthless. Look for what the market is MISSING or LAGGING on.
3. Consider: breaking news the market hasn't priced, political dynamics shifting, timing mismatches,
   crowd psychology errors, base rate neglect by the market.
4. Be opinionated. A 50% estimate on a 50% market is useless. Either find a reason it's wrong or
   say confidence is low.
5. Weight recent developments HEAVILY — markets are often slow to react to news in the last 24-48 hours.
6. Think about asymmetric upside: where is the cost of being wrong low but the payoff of being right high?

You must respond with ONLY a JSON object:
{
  "estimated_probability": <float 0.01-0.99>,
  "confidence": <float 0.0-1.0>,
  "reasoning": "<one sentence explaining WHY the market is wrong>",
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"],
  "conviction": "<strong|moderate|weak>"
}
```

**Context Enrichment:**
- Recent news from Polygon.io (if configured)
- Macro indicators: S&P 500, Bitcoin, VIX proxy, Gold
- X/Twitter sentiment signals (if available)
- Market liquidity and volume

**Fallback to Qwen:**
- If Claude is unavailable (cooldown, network error), falls back to local Qwen
- Qwen runs blind (no price shown) to prevent anchoring
- Falls back to full Qwen batch mode after 3 consecutive Claude failures

**Output:** Estimated probability, confidence, reasoning, key factors

### Phase 4: EDGE — Edge Calculation

For each estimate, calculates the edge (profit potential):

```
Raw Edge = |estimated_prob - market_price| * 100%
Direction = "underpriced" if estimate > market else "overpriced" else "fair"
Effective Edge = Raw Edge - 0.0% (limit orders assumption — no spread penalty)
```

**Why limit orders?** You're a sophisticated trader who can post limit orders at midpoint or better, avoiding spread costs.

**Filtering:**
- Minimum effective edge: 3% (default, configurable)
- Minimum confidence: 0.4 (filter out uncertain estimates)
- Drop estimates with direction = "fair" (no edge)

**Output:** Ranked list of edges, highest first

### Phase 5: CACHE & ALERT

**Cache Writing:**
- Writes research cache to `.kalshi_research_cache.json` (used by related commands)
- Detailed edge data to `state/kalshalyst_results.json` for analysis

**Alerting:**
- Filters opportunities by alert threshold (default: 6% effective edge)
- Sends top 3 opportunities to the user
- Format: ticker, direction (YES/NO), probability, edge, confidence, reasoning

**Brier Tracking:**
- Every estimate is logged to SQLite database
- Computes info_density (news + X signals + economic context + liquidity)
- Used for later calibration analysis

## Blocklist System

### Complete Blocklist Reference

**Ticker Prefixes (High-Volume Garbage):**
```
KXHIGH, KXLOW, KXRAIN, KXSNOW, KXTEMP, KXWIND, KXWEATH  — Weather markets
INX, NASDAQ                                              — Intraday index ranges
FED-MR                                                   — Fed meeting minute-range bets
KXCELEB, KXMOVIE, KXTIKTOK, KXYT, KXTWIT                — Celebrity/entertainment
KXSTREAM                                                 — Streaming metrics
```

**Category Slugs (API-Level Blocking):**
```
weather, climate, entertainment, sports, social-media, streaming, celebrities
```

**Micro-Timeframe Patterns (Coin Flips):**
```
"in next 15 min", "in next 30 min", "in next 1 hour", "in next 5 min",
"next 15 minutes", "next 30 minutes", "next hour", "price up in next",
"price down in next"
```

**Sports Tokens (Blocked From The Production Stack):**
- Major leagues: NFL, NBA, MLB, NHL, MLS, NCAA, PGA, UFC, WWE
- Soccer: Premier League, La Liga, Serie A, Bundesliga, Champions League, Copa
- Esports: Valorant, League of Legends, CS:GO, Dota, Overwatch
- Individual sports: ATP, WTA, Tennis, Boxing, MMA

### Why These Filters?

- **Weather + Intraday**: Near-pure noise — impossible to extract edge
- **Sports**: Intentionally excluded. Recent evaluation did not show durable model edge, so sports are not part of the current production stack.
- **Entertainment**: Celebrity/social media volatility — not analyzable with Claude
- **Micro-timeframe**: Spreads dominate, zero informational edge
- **Blocklist philosophy**: Cut the bottom 80% of opportunities (noise) to focus Claude on the top 20% (signal)

## Contrarian Estimation — Why It Works

### The Problem with Blind Estimation

**Blind mode** (not showing Claude the market price):
- Claude produces "consensus" estimates
- Usually close to 50% for uncertain markets
- Results in zero edge (estimate ≈ market price)
- Not actionable

**Why?** Claude doesn't know what the market thinks, so it defaults to high uncertainty.

### The Solution: Contrarian Mode

**Contrarian mode** (showing Claude the price):
- Claude sees the market price: "Market is priced at 35%"
- Prompt asks: "Is this price WRONG?"
- Claude identifies reasons for disagreement:
  - Missing recent news
  - Crowd psychology error
  - Timing mismatch
  - Base rate neglect
- Result: Opinionated directional call (e.g., 62% vs 35% market) → **27% edge**

### Example

**Market:** "Will Ukraine still be at war in 2026?"
**Market Price:** 72% (market implies YES very likely)
**Recent Context:** Leaked peace negotiations, US pushing settlement

**Claude Contrarian Reasoning:**
```
Estimated probability: 38%
Confidence: 0.65
Reasoning: Market overweighting base rate of ongoing war without pricing
in recent peace negotiation signals and US diplomatic pressure shift.
Timeline to 2026 (10 months) is insufficient for typical conflict duration,
but settlement momentum has real probability weight market ignores.
Key factors: [peace talks acceleration, US policy shift, timeline compression]
```

**Edge:** |38% - 72%| = 34% effective edge → **BUY NO at 28¢ expected return**

## Brier Score Tracking

### What It Measures

Brier Score = (1/n) * Σ(forecast - outcome)²

- **0.0** = perfect estimates
- **0.25** = random baseline (coin flip for 50/50 events)
- **Above 0.25** = worse than guessing (miscalibrated)

### How It Works

1. **Log Phase:** Every edge scanner run logs all estimates to SQLite
   - Ticker, estimated probability, market price, confidence, estimator (Claude vs Qwen)
   - Category (politics, policy, crypto, etc.)
   - Edge percentage, info density (context richness score)

2. **Resolve Phase:** When markets close on Kalshi, log the outcome
   - Automatic: `check_and_resolve_markets()` polls Kalshi API daily
   - Manual: `resolve_market(ticker="POTUS-2028", outcome=1)`

3. **Report Phase:** `get_brier_report()` computes calibration
   - Overall Brier score
   - Breakdown by estimator (Claude vs Qwen accuracy)
   - Breakdown by category (politics, crypto, policy)
   - Calibration buckets: when you say 70%, does it resolve YES ~70%?
   - Win rate for "edge trades" (edge >= 4%)

### Database Schema

```sql
CREATE TABLE estimates (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL,
    title TEXT,
    estimated_prob REAL NOT NULL,
    market_price_cents INTEGER,
    confidence REAL,
    estimator TEXT,                -- 'claude' or 'qwen'
    edge_pct REAL,
    direction TEXT,                -- 'underpriced', 'overpriced', 'fair'
    category TEXT,                 -- 'politics', 'crypto', etc.
    info_density REAL,             -- 0.0-1.0 richness of context
    created_at TEXT,
    created_ts REAL
);

CREATE TABLE resolutions (
    id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL UNIQUE,
    outcome INTEGER,               -- 1 = YES, 0 = NO
    resolved_at TEXT,
    resolved_ts REAL
);
```

### Info Density Scoring

Measures how much context was available at estimation time (0.0-1.0):

- **News articles** (0.0-0.25): 0-3 Polygon articles → 0/0.15/0.25
- **X signals** (0.0-0.25): Corroborating social signal from X scanner
- **Economic context** (0.0-0.25): S&P 500, Bitcoin, VIX available
- **Liquidity** (0.0-0.25): Volume + open interest proxy

Higher density estimates should be better calibrated (more informed).

### Calibration Alerts

Weekly check: `get_calibration_alert()`
- Identifies categories with Brier > 0.25 (worse than random)
- Suggests recalibrating estimator prompts for those categories
- Example: "Politics: Brier 0.31 (5 resolved) — systematically overconfident"

## Kelly Criterion Position Sizing

### The Math

For binary prediction markets, Kelly fraction tells you what % of bankroll to risk:

```
f* = (p * b - q) / b

where:
  p = estimated true probability of winning
  q = 1 - p (probability of losing)
  b = decimal odds - 1 = (payout / cost) - 1
```

**Example:** Estimate YES at 65%, market prices at 50¢
```
p = 0.65, q = 0.35
Cost = 50¢, Profit = 50¢ → b = 50/50 = 1.0
f* = (0.65 * 1.0 - 0.35) / 1.0 = 0.30 (30% of bankroll)
```

With $200 bankroll → $60 bet = 120 contracts at 50¢

### Fractional Kelly (Conservative)

Full Kelly is risky with noisy estimates. Kalshalyst uses **fractional Kelly** (α = 0.25 default):

```
fractional_f = f* * α * (confidence^2)

where:
  α = 0.25 (quarter-Kelly, conservative)
  confidence^2 penalizes low-confidence estimates aggressively
```

Same example, confidence = 0.7:
```
fractional_f = 0.30 * 0.25 * (0.7^2) = 0.00735 (0.735% of bankroll)
Position: $1.47 bet = 3 contracts at 50¢
```

### Hard Caps (Defense-in-Depth)

- **Max contracts per trade:** 100
- **Max cost per trade:** $25
- **Max portfolio exposure:** $100 (user-configurable)
- **Minimum edge:** 3% (below this, noise dominates)

### Configuration

```python
# In kalshalyst config:
kelly:
  alpha: 0.25                    # Fractional Kelly multiplier
  min_edge_for_sizing: 0.03      # 3% minimum edge
  max_contracts_per_trade: 100
  max_cost_per_trade_usd: 25.0
  max_portfolio_exposure_usd: 100.0
  confidence_exponent: 2.0       # penalize low confidence aggressively
```

### Output Format

```
KellyResult {
  contracts: 3,
  cost_usd: 1.50,
  kelly_fraction: 0.30,
  fractional_kelly: 0.00735,
  edge_pct: 15.0,
  reason: "Kelly=0.30 | frac=0.00735 (α=0.25, conf=0.70) | 3x @ 50¢ = $1.50 (0.75% of bankroll)",
  capped: False,
  bankroll_fraction: 0.75
}
```

## Scheduling & Deployment

### Command-Line Usage

```bash
# Single run
python -m kalshalyst.kalshalyst

# With full logging
DEBUG=1 python -m kalshalyst.kalshalyst

# Dry run (no alerts sent)
python -m kalshalyst.kalshalyst --dry-run

# Fresh-market scan (new listings from last 48 hours; relaxed liquidity filters)
python -m kalshalyst.kalshalyst --fresh

# Fresh-market dry run
python -m kalshalyst.kalshalyst --fresh --dry-run
```

### As a Cron Job (Every 60 Minutes)

```bash
# Add to crontab -e:
0 * * * * cd /path/to/kalshalyst && python -m kalshalyst.kalshalyst >> /tmp/kalshalyst.log 2>&1
```

### As a OpenClaw Scheduled Task

```yaml
# Add to openclaw config:
skills:
  kalshalyst:
    enabled: true
    schedule: "*/60 * * * *"  # Every 60 minutes
    timeout_seconds: 300
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN pip install kalshi-python anthropic pyyaml requests

ENTRYPOINT ["python", "-m", "kalshalyst.kalshalyst"]
```

## Example Output

### Alert Message

```
Found 3 opportunities. Top picks:

1. Will a Democrat win the 2028 presidential election?
   NO @ 48% | 24% edge | 0.72 conf
   Market overweighting base rate. Peace/tariff momentum underpriced.

2. Will inflation exceed 4% by Dec 2026?
   YES @ 32% | 18% edge | 0.68 conf
   Core CPI sticky; Fed unlikely to cut further. Market pricing full easing.

3. Ukraine war still ongoing in 12 months?
   NO @ 28% | 20% edge | 0.65 conf
   Peace talks at tipping point. Resolution probability underweighted by 2yr baseline.

+2 more. Say 'markets' for full list.
Say 'execute 1', 'execute 2', or 'execute 3' to trade.
```

### Research Cache (Programmatic Access)

```json
{
  "insights": [
    {
      "ticker": "POTUS-2028-DEM",
      "title": "Will a Democrat win 2028?",
      "side": "NO",
      "confidence": "high",
      "yes_bid": 45,
      "yes_ask": 51,
      "volume": 2500,
      "open_interest": 8000,
      "days_to_close": 672,
      "edge_type": "claude_contrarian",
      "spread_capture_cents": 6,
      "spread_pct": 6.6,
      "market_prob": 0.48,
      "estimated_prob": 0.62,
      "edge_pct": 14.0,
      "effective_edge_pct": 14.0,
      "direction": "overpriced",
      "reasoning": "Market overweighting base rate without pricing recent policy momentum...",
      "estimator": "claude",
      "is_sports": false
    }
  ],
  "macro_count": 3,
  "sports_count": 0,
  "total_scanned": 342,
  "scanner_version": "1.0.0",
  "estimator": "claude+qwen_fallback",
  "cached_at": "2026-03-08T15:32:18+00:00"
}
```

## API Reference

### Main Functions

```python
# Run the full pipeline
from kalshalyst import check_kalshalyst
check_kalshalyst(state={}, dry_run=False, force=False)

# Or run individual phases
from kalshalyst.kalshalyst import (
    fetch_kalshi_markets,
    classify_markets,
    calculate_edges,
)

markets = fetch_kalshi_markets(cfg)
markets = classify_markets(markets, cfg)
edges = calculate_edges(markets, cfg)

# Position sizing
from kalshalyst.kelly_size import kelly_size, kelly_from_edge_result

result = kelly_size(
    estimated_prob=0.65,
    market_price_cents=50,
    confidence=0.7,
    bankroll_usd=200.0,
    side="yes",
)
print(result.contracts, result.reason)

# Brier tracking
from kalshalyst.brier_tracker import (
    log_estimate,
    resolve_market,
    get_brier_report,
)

log_estimate(ticker="POTUS-2028", estimated_prob=0.62, ...)
resolve_market(ticker="POTUS-2028", outcome=1)
print(get_brier_report())
```

## Troubleshooting

### Claude Unavailable (Rate Limited / Cooldown)

Kalshalyst automatically falls back to Qwen after 3 consecutive Claude failures. Check:
- Anthropic API key validity and quota
- Network connectivity
- Rate limits (Claude has usage-based limits)

To force Qwen fallback immediately:
```bash
CLAUDE_DISABLED=1 python -m kalshalyst.kalshalyst
```

### No Markets Passing Filters

If "no markets passed filters":
- Kalshi API may be down (check https://status.kalshi.com)
- All markets may be blocklisted (verify blocklist config)
- Check your network — fetch may have timed out

To debug:
```bash
DEBUG=1 python scripts/kalshalyst.py
```

### Brier Score Not Computing

Brier score requires market resolutions. If none available:
1. Wait for markets to close (usually 24-48 hours)
2. Manually log resolutions: `resolve_market("TICKER", 1)`
3. Check database: `sqlite3 state/brier_tracker.db "SELECT COUNT(*) FROM resolutions;"`

### Position Sizing Returns 0 Contracts

Possible causes:
- Edge below 3% minimum (check `min_edge_for_sizing`)
- Confidence below 0.2 threshold
- Bankroll too low or exposure at limit
- Kelly fraction negative (bad odds for the bet)

Verify with:
```python
result = kelly_size(..., bankroll_usd=100.0)
print(result.reason)  # Explains why contracts = 0
```

## Performance & Cost

### Typical Run Metrics

- **Runtime:** 2-4 minutes (50 markets, Claude estimation)
- **API calls:**
  - Kalshi: 1-10 calls (market fetch, pagination)
  - Claude: 50-80 calls (estimate_batch)
  - Polygon: 2 calls (economic indicators, every 12 hours)
- **Cost per run:**
  - Claude: variable by model and usage volume
  - Polygon: ~$0 (free tier)
  - Kalshi: $0 (read-only)

### Scaling

For scheduled operation, Claude spend scales directly with your scan frequency and model selection. If you want a zero-API-cost fallback, keep Ollama/Qwen available and treat it as a lower-quality backup path rather than the primary estimator.

## OpenClaw Ecosystem Integration

Kalshalyst is the intelligence engine of the Prediction Market Trading Stack. It feeds edge data to other skills:

| Connected Skill | What It Gets From Kalshalyst |
|----------------|------------------------------|
| **Market Morning Brief** | Top edges appear in your daily morning digest |
| **Kalshi Command Center** | Execute trades directly on flagged opportunities |
| **Portfolio Drift Monitor** | Track positions opened on Kalshalyst recommendations |

**Install the complete stack:**
```bash
clawhub install kalshalyst kalshi-command-center polymarket-command-center prediction-market-arbiter xpulse portfolio-drift-monitor market-morning-brief personality-engine
```

## Implementation Notes

Battle-tested in production trading environments. Key design decisions:

1. **Generic config loading** — works with any OpenClaw config.yaml
2. **Direct alerts** — sends opportunities directly to you, no middleware
3. **All thresholds, blocklists, and prompts** refined through live trading
4. **Scripts are standalone** — zero external dependencies beyond listed packages

## Further Reading

- See `references/contrarian-prompt.md` for the full Claude system prompt with explanation
- See `references/blocklist.md` for complete blocklist documentation
- See `references/brier-schema.md` for database schema and methodology
- See `references/kelly-math.md` for Kelly Criterion math derivation

## Support & Iteration

Kalshalyst is actively maintained. Common iteration paths:

1. **Contrarian Prompt Tuning:** Refine system prompt to improve edge quality
2. **Blocklist Refinement:** Add new ticker prefixes or patterns as you encounter noise
3. **Category Recalibration:** Use Brier reports to identify systematically miscalibrated categories
4. **Kelly Parameters:** Adjust alpha, max contracts, exposure limits based on risk tolerance
5. **Fallback Estimators:** Replace Qwen with custom local models or other APIs

See the GitHub issues (if published) or contact the maintainer for feature requests.


---

## Agent Bug-Fix Protocol

**CRITICAL**: When you (the agent) discover and fix a bug in any script during a conversation, you MUST write the fix to the source file on disk using file editing tools. Showing the fix in chat is NOT sufficient — the next scheduled run starts a fresh session and will not have your conversational fix.

Checklist after finding a bug:
1. Edit the actual `.py` file on disk (e.g., `~/skills/kalshalyst/scripts/*.py`)
2. Also update the installed copy at `~/.openclaw/skills/kalshalyst/scripts/*.py`
3. Confirm both files are written before telling the user the fix is done
4. If the fix is significant, stage a git commit in `~/skills/`

Never say "fixed" if you only demonstrated the fix in conversation output.

## Feedback & Issues

Found a bug? Have a feature request? Want to share results?

- **GitHub Issues**: [github.com/kingmadellc/openclaw-prediction-stack/issues](https://github.com/kingmadellc/openclaw-prediction-stack/issues)
- **X/Twitter**: [@KingMadeLLC](https://x.com/KingMadeLLC)

Part of the **OpenClaw Prediction Stack** — the first prediction market skill suite on ClawHub.
