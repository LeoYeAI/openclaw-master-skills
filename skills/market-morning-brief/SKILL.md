---
name: Market Morning Brief
description: "Daily morning and evening intelligence digest for prediction market traders. Morning brief: Kalshi portfolio P&L, Polymarket trending markets, crypto prices — scannable in 30 seconds. Evening brief: lightweight market summary or AI-filtered news digest with two-stage Qwen materiality gate. Works standalone; unlocks additional sections automatically when paired with Kalshalyst (edges), Prediction Market Arbiter (divergences), and Xpulse (social signals). Hub of the OpenClaw Prediction Market Trading Stack."
---

# Market Brief — Daily Morning & Evening Intelligence Digest

## Overview

Market Morning Brief is a lightweight, resilient daily intelligence system designed to be the first thing you read each morning. It combines:

- **Portfolio P&L** — Your Kalshi positions and unrealized gains/losses
- **Top opportunities** — Markets with highest edge (if Kalshalyst cache available)
- **Cross-platform divergences** — Kalshi vs Polymarket pricing mismatches (if Arbiter cache available)
- **X signal summaries** — Top-performing prediction signals from Twitter/X (if Xpulse cache available)
- **Crypto prices** — Bitcoin, Ethereum, plus any configured altcoins (if Coinbase configured)
- **Polymarket insights** — Notable markets and volume activity

The brief is designed for **30-second scanning** — each section is 3-8 lines maximum. If a data source is unavailable, the section gracefully degrades to "unavailable" and the brief continues.
If Kalshi credentials are not configured yet, the brief shows a realistic preview portfolio and edge block so first-time users still see value immediately.

## When to Use This Skill

- You trade prediction markets (Kalshi, Polymarket) and want daily market context
- You need a quick morning summary: portfolio status + opportunities + signals
- You want an evening briefing: either lightweight trading summary or AI-filtered news digest
- You want integration with your other market intelligence tools (Kalshalyst, Arbiter, Xpulse)
- You want plain text output suitable for SMS, iMessage, or any messaging platform
- You want AI-powered news curation: two-stage filtering to prevent notification fatigue

**Every Evening (Default: 6:00 PM):** Day's activity summary (positions opened/closed, realized P&L), watch list for overnight risks, top X signals from the day, and unusual market activity.

## Architecture

### Design Philosophy

**Resilience through isolation.** Each section:
- Wrapped in try/except to prevent one failure from breaking the entire brief
- Reads from cache files (not live APIs) for speed and reliability
- Gracefully degrades if data unavailable ("unavailable, check Kalshalyst directly")
- Logs failures without interrupting output

**Plain text output.** No markdown, no emojis, no formatting — designed for chat delivery:
- Compatible with iMessage, SMS, email, web chat, any platform
- Scannable: max 80 chars per line, clear section headers
- Readable at a glance in <30 seconds

**Configurable integration.** The brief reads from:
- Optional Kalshalyst cache (`.kalshi_research_cache.json`)
- Optional Arbiter cache (`.crossplatform_divergences.json`)
- Optional Xpulse cache (`.x_signal_cache.json`)
- Optional Coinbase API (if configured)
- Public Polymarket API (no auth)

If a cache file doesn't exist (skill not installed), that section simply shows "unavailable".

## Configuration

Create or update your `config.yaml` when you want live account data. The first run works without it and shows preview output:

```yaml
market_morning_brief:
  enabled: true
  morning_time: "07:30"     # Schedule for morning brief
  evening_time: "18:00"     # Schedule for evening brief
  timezone: "America/New_York"

  # Kalshi API (required for portfolio section)
  kalshi:
    enabled: true
    api_key_id: "your-key-id"
    private_key_file: "/path/to/private.key"

  # Coinbase API (optional, for crypto prices)
  coinbase:
    enabled: false
    api_key: "sk-..."
    tickers: ["BTC", "ETH"]  # Customize as needed

  # Cache paths (for reading other skills' data)
  cache_paths:
    kalshalyst: "./state/.kalshi_research_cache.json"
    arbiter: "./state/.crossplatform_divergences.json"
    xpulse: "./state/.x_signal_cache.json"

  # Which sections to include
  include:
    portfolio: true
    kalshalyst_edges: true      # Requires Kalshalyst skill
    arbiter_divergences: true   # Requires Prediction Market Arbiter skill
    xpulse_signals: true        # Requires Xpulse skill
    crypto: false               # Requires Coinbase API key
    polymarket: true            # Free (public API)
```

## Section-by-Section Breakdown

### 1. Portfolio Summary

**Data source:** Kalshi API (read-only)

**Example output:**
```
PORTFOLIO (3 positions, +$24 unrealized):
POTUS-2028-DEM    YES  100@48¢  $48 cost  +$18 unrl (exp: 242 days)
UKRAINE-2026-NO    YES   50@28¢  $14 cost   +$8 unrl (exp: 118 days)
FED-MAR-CUT        NO   200@35¢  $70 cost  -$2 unrl (exp: 8 days)
```

**Fields:**
- Ticker | Side (YES/NO) | Quantity @ Price | Cost | Unrealized P&L | Days to Expiration

**Graceful degradation:** If Kalshi API unavailable:
```
PORTFOLIO: unavailable (check Kalshi API)
```

### 2. Kalshalyst Edges (Optional)

**Data source:** Kalshalyst cache (`.kalshi_research_cache.json`)

**Example output:**
```
EDGES (Kalshalyst, top 3):
1. POTUS-2028-DEM    NO @ 38%  (+14% edge, 72% conf)
2. INFLATION-2026    YES @ 68%  (+8% edge, 65% conf)
3. UKRAINE-PEACE     YES @ 55%  (+6% edge, 58% conf)
```

**Fields:**
- Ticker | Side | Market Price | Edge % | Confidence %

**Graceful degradation:** If Kalshalyst skill not installed:
```
EDGES: unavailable — unlock with: clawhub install kalshalyst
```

### 3. Cross-Platform Divergences (Optional)

**Data source:** Prediction Market Arbiter cache (`.crossplatform_divergences.json`)

**Example output:**
```
DIVERGENCES (Arbiter, Kalshi ↔ Polymarket):
UKRAINE-2026-NO    Kalshi 28% ↔ PM 31%  ($0.03 spread, 12% vol diff)
POTUS-2028-DEM     Kalshi 38% ↔ PM 40%  ($0.02 spread, 8% vol diff)
```

**Fields:**
- Ticker | Kalshi Price ↔ Polymarket Price | Spread | Volume Difference

**Graceful degradation:** If Arbiter skill not installed:
```
DIVERGENCES: unavailable — unlock with: clawhub install prediction-market-arbiter
```

### 4. X Signal Summaries (Optional)

**Data source:** Xpulse cache (`.x_signal_cache.json`)

**Example output:**
```
X SIGNALS (Xpulse, last 24h):
Fed rate cut odds +5%   (confidence: 78%, reach: 8.2K)
Ukraine ceasefire talks (+3%, 72% conf, 5.1K reach)
```

**Fields:**
- Signal | Magnitude | Confidence % | Reach/Strength

**Graceful degradation:** If Xpulse skill not installed:
```
X SIGNALS: unavailable — unlock with: clawhub install xpulse
```

### 5. Crypto Prices (Optional)

**Data source:** Coinbase API (requires key + configuration)

**Example output:**
```
CRYPTO:
BTC  $62,400  (+1.2%)   | ETH  $3,140  (-0.8%)
SOL  $142     (-2.1%)   | AVAX $38     (+0.5%)
```

**Fields:**
- Ticker | Price | 24h Change %

**Graceful degradation:** If Coinbase not configured:
```
CRYPTO: unavailable (configure Coinbase API for crypto prices)
```

### 6. Polymarket Activity

**Data source:** Public Polymarket API (free)

**Example output:**
```
POLYMARKET (top 3 by volume):
POTUS 2028: $2.4M vol, 48% DEM (vs 52% GOP)
Inflation >4% 2026: $1.1M vol, 32% prob
Bitcoin $100K by 2026: $0.8M vol, 58% prob
```

**Fields:**
- Market | Volume | Implied Probability | (Context)

**Graceful degradation:** If Polymarket API unavailable:
```
POLYMARKET: unavailable (check Polymarket directly)
```

## Evening Brief — Lightweight Market Summary + AI-Filtered News

Sent at configured evening time (default: 6:00 PM). Two variants: **lightweight market update** or **full news digest with materiality filtering**.

### Lightweight Market Variant (6-8 lines, trading-focused)

```
EVENING BRIEFING — Thursday, March 7, 2026

ACTIVITY:
Current positions: 3 | Cost: $132 | Unrealized: +$24

OVERNIGHT WATCH:
• FED-MAR-CUT expires in 8 days — monitor Fed speakers before FOMC
• UKRAINE-2026 low liquidity (9 contracts asking) — wide spreads

TOP X SIGNALS TODAY:
• Ukraine ceasefire talks +3% (78% conf)
• Fed rate cut odds stabilizing (72% conf)
```

**Key differences from morning brief:**
- Shorter (6-8 lines max)
- Focus on intraday activity (current positions, cost, unrealized P&L)
- Overnight watch items (expirations, geopolitical risks, liquidity alerts)
- Top X signals from that day (not 24h rolling)

### Full Evening News Digest (News-focused with AI filtering)

```
EVENING NEWS BRIEFING — Thursday, March 7, 2026

🏛️ Fed Signals Cautious Stance on Rate Cuts (87% conf, Reuters)
📈 Tech Stocks Rally on Earnings Beat (82% conf, Bloomberg)
🌍 Geopolitical Tensions Escalate Over Trade Deal (79% conf, AP)
💻 AI Policy Bill Advances in Congress (76% conf, TechCrunch)
📌 Crypto Markets Stabilize After Volatility (71% conf, CoinDesk)
```

**Features:**
- Category icons: 🏛️ policy, 📈 markets, 💻 technology, 🌍 geopolitics, 📌 general
- Confidence scores (0-100%) show Qwen relevance assessment
- Two-stage filtering pipeline (see below)
- 48-hour rolling history prevents repeated news
- Fail-closed design: if Qwen unavailable, no news sent (silence over noise)

## Evening Briefing: Two-Stage News Filtering Pipeline

Evening briefing combines DuckDuckGo news search with local Qwen LLM for AI-powered news curation. Designed to prevent notification fatigue while surfacing genuinely material developments.

### Architecture

**Stage 1: Relevance & Significance Filter**
1. Search for recent news across configured topics (default: prediction markets, AI policy, federal reserve)
2. Run each article through Qwen: is this significant? (0-1 confidence score, category classification)
3. Filter to articles with confidence >= min_confidence (default: 0.7)
4. Limit to top 10 most confident articles for Stage 2

**Stage 2: Materiality Gate (Prevents Notification Fatigue)**
1. Load history of previously sent articles (48h rolling, max 200 entries)
2. Compare candidate articles against recent history
3. Qwen decision: is this NEW and MATERIAL? Or just ongoing background noise?
4. Drop duplicates, commentary, routine announcements
5. Only pass through genuinely new developments or significant escalations

**Fail-Closed Design:**
- If Qwen unavailable during Stage 1 or Stage 2: **drop all articles** (silence over noise)
- If no material news: send nothing (don't interrupt with noise)
- History persistence: `~/.openclaw/state/evening_news_history.json` (max 200 entries, auto-cleanup)

### Example Configuration

```yaml
market_morning_brief:
  evening_briefing:
    enabled: true
    mode: "news"                    # "market" for activity summary, "news" for full news digest
    time: "18:00"                   # Briefing time (30-min window)
    materiality_gate: true          # Enable Stage 2 filter (prevents fatigue)
    min_confidence: 0.7             # Minimum relevance threshold (0-1)
    max_per_topic: 3                # Max articles per topic to search
    topics:
      - "prediction markets"
      - "AI policy"
      - "federal reserve"
      - "geopolitics"
```

### Command Usage

```bash
# Lightweight market variant (activity + watch list)
python scripts/evening_brief.py --mode market

# Full news digest variant
python scripts/evening_brief.py --mode news

# Force send regardless of time/already-sent-today
python scripts/evening_brief.py --force

# Dry run (print without sending)
python scripts/evening_brief.py --dry-run

# Enable verbose logging
python scripts/evening_brief.py --debug
```


### News History

Stored at `~/.openclaw/state/evening_news_history.json`. Max 200 entries, auto-cleans after 48 hours. Used by Stage 2 materiality gate to prevent duplicate notifications.

## Cache File Integration

Each optional skill writes a cache file that the Morning Brief reads automatically:

| Skill | Cache File | Section Unlocked |
|-------|-----------|-----------------|
| **Kalshalyst** | `state/.kalshi_research_cache.json` | Edge opportunities |
| **Prediction Market Arbiter** | `state/.crossplatform_divergences.json` | Cross-platform divergences |
| **Xpulse** | `state/.x_signal_cache.json` | X/Twitter signals |

If a cache file doesn't exist, that section shows "unavailable" with the install command. See `references/integration.md` for cache file schemas.

## Example Complete Morning Brief

```
MARKET MORNING BRIEF — Thursday, March 7, 2026

PORTFOLIO (3 positions, +$24 unrealized):
POTUS-2028-DEM    YES  100@48¢  $48 cost  +$18 unrl (exp: 242 days)
UKRAINE-2026-NO    YES   50@28¢  $14 cost   +$8 unrl (exp: 118 days)
FED-MAR-CUT        NO   200@35¢  $70 cost  -$2 unrl (exp: 8 days)

EDGES (Kalshalyst, top 3):
1. POTUS-2028-DEM    NO @ 38%  (+14% edge, 72% conf)
2. INFLATION-2026    YES @ 68%  (+8% edge, 65% conf)
3. UKRAINE-PEACE     YES @ 55%  (+6% edge, 58% conf)

DIVERGENCES (Arbiter):
UKRAINE-2026-NO    Kalshi 28% ↔ PM 31%  ($0.03 spread)
POTUS-2028-DEM     Kalshi 38% ↔ PM 40%  ($0.02 spread)

X SIGNALS (last 24h):
Fed rate cut odds +5%   (78% conf, 8.2K reach)
Ukraine ceasefire +3%   (72% conf, 5.1K reach)

CRYPTO:
BTC  $62,400  (+1.2%)   | ETH  $3,140  (-0.8%)

POLYMARKET (top 3 by vol):
POTUS 2028 DEM: $2.4M vol, 48% prob
Inflation >4% 2026: $1.1M vol, 32% prob
Bitcoin >$100K 2026: $0.8M vol, 58% prob
```

## Scheduling & Commands

### Morning Brief (Default: 7:30 AM)

```bash
# Manual trigger
python scripts/morning_brief.py

# With debug output
python scripts/morning_brief.py --debug

# Dry run (print without side effects)
python scripts/morning_brief.py --dry-run

# Custom config path
python scripts/morning_brief.py --config /path/to/config.yaml

# Via OpenClaw (if integrated):
openclaw skill run market-morning-brief morning
```

### Cron Scheduling

```bash
30 7 * * * python /path/to/scripts/morning_brief.py              # Morning at 7:30 AM
0 18 * * * python /path/to/scripts/evening_brief.py --mode market  # Evening at 6:00 PM
```

## Dependencies

**Required:** Python 3.10+, `pip install kalshi-python requests pyyaml`

**For evening news digest:** Ollama + Qwen model (`ollama pull qwen3:latest`), plus `pip install ddgs` (or `duckduckgo-search` as fallback).

**Optional skills** for additional brief sections: Kalshalyst, Prediction Market Arbiter, Xpulse (see Implementation Notes below).

## Performance & Cost

### Morning Brief

- **Runtime:** <5 seconds (all cached data)
- **API calls:** 1 (Polymarket public API) + 1 (Kalshi portfolio) = 2 calls
- **Cost:** $0 (Kalshi free tier, Polymarket free)

### With Optional Skills

If Kalshalyst, Arbiter, Xpulse installed:
- **Runtime:** <2 seconds (reads cache files)
- **Cost:** Only the skill installation costs (brief itself has no additional cost)

## Troubleshooting

**Portfolio not showing:** Verify Kalshi API key is configured and not rate-limited. Run `python scripts/morning_brief.py --debug`.

**Sections showing "unavailable":** Expected if the skill isn't installed. Install with the `clawhub install` command shown in the output, then run the skill once to generate its cache file.

**Evening news empty:** Check Ollama is running (`ollama list`), test Qwen (`ollama run qwen3:latest "test"`), and verify ddgs (`python -c "from ddgs import DDGS; print('OK')"`).

**Stage 2 drops everything:** The materiality gate filters out non-novel news. Clear history with `rm ~/.openclaw/state/evening_news_history.json` and retry, or disable with `--no-materiality-gate`.

**Qwen timeout:** Reduce article count with `--max-per-topic 2` or skip Stage 2 with `--no-materiality-gate`.

## Implementation Notes

This skill is designed for **standalone operation** but unlocks its full potential with the OpenClaw Prediction Market Trading Stack.

**Standalone:** Portfolio P&L + Polymarket trending + Crypto prices (if configured). No other skills required.

**With the full stack:** Each additional skill adds a new section to your daily brief automatically — no configuration needed. Install skills, run them once, and the Morning Brief picks up their cache files on the next run.

| Skill | Unlocks | Install |
|-------|---------|---------|
| **Kalshalyst** | Contrarian edge analysis with Kelly sizing | `clawhub install kalshalyst` |
| **Prediction Market Arbiter** | Cross-platform Kalshi↔Polymarket divergences | `clawhub install prediction-market-arbiter` |
| **Xpulse** | Real-time X/Twitter social signals | `clawhub install xpulse` |
| **Portfolio Drift Monitor** | Position drift alerts between briefs | `clawhub install portfolio-drift-monitor` |
| **Kalshi Command Center** | Direct trade execution from edge alerts | `clawhub install kalshi-command-center` |

**Install the complete stack:**
```bash
clawhub install kalshalyst kalshi-command-center polymarket-command-center prediction-market-arbiter xpulse portfolio-drift-monitor market-morning-brief personality-engine
```

## Further Reading

- See `references/sections.md` for detailed section documentation
- See `references/integration.md` for technical integration guide
- See `references/evening-pipeline.md` for evening briefing pipeline documentation

## Support

For issues: run with `DEBUG=1` for verbose output, review `references/sections.md` and `references/integration.md`, or check `/tmp/market-morning-brief.log`.

**Author**: KingMadeLLC


---

## Feedback & Issues

Found a bug? Have a feature request? Want to share results?

- **GitHub Issues**: [github.com/kingmadellc/openclaw-prediction-stack/issues](https://github.com/kingmadellc/openclaw-prediction-stack/issues)
- **X/Twitter**: [@KingMadeLLC](https://x.com/KingMadeLLC)

Part of the **OpenClaw Prediction Stack** — the first prediction market skill suite on ClawHub.
