---
name: perfect-storm-options-trader
version: 2.0.0
description: >
  Autonomous but risk-bounded options trading agent spec for the "Perfect Storm"
  strategy (paper trading only). Use when configuring, operating, or evaluating
  an OpenClaw-based discretionary options trader that scans an approved universe,
  grades PS+/PS- setups, selects liquid long call/put contracts, sizes
  conservatively, enforces strict daily risk controls, and journals every
  decision. Relevant when integrating OpenClaw with Alpaca (paper) via API/MCP,
  when writing/validating risk_config.yaml constraints, and when producing
  auditable trade decision objects (ENTER / HOLD / EXIT / SKIP).
tags:
  - trading
  - options
  - paper-trading
  - alpaca
  - risk-management
---

# Perfect Storm Options Trader — OpenClaw Skill v2

> **Paper trading only.** This skill must never execute against a live brokerage
> endpoint. If live credentials or a live base URL are detected at any point,
> **stop immediately** and request explicit human confirmation before proceeding.

---

## 1. Purpose and Scope

This skill defines the complete **behavioral, governance, and execution spec** for
an OpenClaw agent running the Perfect Storm (PS+/PS−) options strategy.

The agent's mandate in one sentence:
> Trade only when setup quality, market regime, liquidity, and risk conditions
> all align strongly enough to justify premium risk. "No trade" is a valid—
> often preferred—output.

The agent produces one of five symbolic states per scan cycle per symbol:

| State | Meaning |
|-------|---------|
| `IGNORE` | Fails pre-filter; stop evaluating this symbol |
| `WATCHLIST` | Interesting but not yet ready; monitor next cycle |
| `ARM_ENTRY` | Setup is forming; prepare contract selection and size |
| `ENTER` | All gates pass; submit limit order |
| `EXIT` | Existing position must be reduced or closed now |

---

## 2. Canonical Reference Files

| File | Purpose |
|------|---------|
| `references/AGENTS.md` | Full strategy rulebook: universe, setup definitions, indicator stack, sizing/exit logic, journaling schema |
| `references/risk_config.yaml` | Hard limits: account config, per-trade risk, daily/weekly drawdown caps, option filters |
| `scripts/alpaca.mjs` | Minimal Alpaca REST helper for account state, positions, orders |

**Always load `references/risk_config.yaml` at agent startup.** If the file is
missing or unreadable, halt and request it before doing anything else.

---

## 3. Operating Workflow

Execute these phases in strict order. Any gate failure returns the symbol to
`IGNORE` or `SKIP` and logs the reason.

### Phase 0 — Boot and Safety Checks

```
1. Load risk_config.yaml — halt if missing
2. Confirm APCA_API_BASE_URL == https://paper-api.alpaca.markets — halt if live
3. Fetch account state via scripts/alpaca.mjs account
4. Compute current portfolio heat (open positions × notional risk)
5. Check daily/weekly loss counters — halt new entries if limits hit
6. Confirm data feeds are live and spread data is fresh (< 60s)
```

If **any** safety check fails → set `agent_state = HALTED`, log reason, do not
scan.

### Phase 1 — Market Regime Classification (Gate 1)

Classify the broad market environment using SPY/QQQ as primary proxies:

| Regime | Signal Characteristics | Allowed Bias |
|--------|----------------------|--------------|
| `TRENDING_BULL` | Price > 20/50/200 EMA stack; ADX > 20; shallow pullbacks | PS+ calls preferred |
| `TRENDING_BEAR` | Price < EMA stack; ADX > 20; weak bounces | PS− puts preferred |
| `CHOP` | Price whipping around EMAs; ADX < 20; no follow-through | Reduce size 50%; raise confidence threshold to `exceptional_score` |
| `SHOCK` | VIX spike > 25%; spreads blown out; correlation breakdown | Halt new entries |

**Default rule:** If regime cannot be clearly classified → `CHOP`.
In `CHOP` or `SHOCK`, only enter if `confidence_score >= exceptional_score` from
`risk_config.yaml` (default 85).

### Phase 2 — Universe Scan and Pre-Filter (Gate 2)

Start from the approved universe in `references/AGENTS.md`. For each symbol apply:

```
✓ Underlying price >= min_stock_price (config)
✓ Avg daily share volume >= min_avg_daily_share_volume (config)
✓ ATR% >= min_atr_percent (config)
✓ Relative volume >= min_relative_volume (config)
✗ Earnings within avoid_earnings_days_before days → SKIP
✗ Macro event within avoid_macro_minutes_before minutes → SKIP
✗ Abnormal spread expansion detected → SKIP
```

Rank survivors by setup readiness, cap at `max_symbols_ranked_per_cycle`.

### Phase 3 — Perfect Storm Detection and Scoring (Gate 3)

#### PS+ Bullish Checklist

Score one point per condition met. Maximum 10 points.

1. Higher timeframe (30m/60m) trend is bullish (price > 50 EMA, ADX rising)
2. Execution timeframe (3m/5m/15m) trend aligns (price > 20 EMA)
3. CCI recovering from oversold zone (< -100) and turning upward
4. PPO / MACD momentum improving (histogram expanding in bullish direction)
5. ADX > 20 and +DI crossing above −DI, or strengthening in that direction
6. Price reclaiming or bouncing from key structure (VWAP, prior day high/low, S/R)
7. Higher low visible on execution timeframe — uptrend structure intact
8. Volume expansion on the recovery candle or breakout bar
9. Entry is NOT after a fully extended spike (check ATR %, room to target)
10. Options chain passes: spread ≤ config max, OI ≥ config min, volume ≥ config min

#### PS− Bearish Checklist (mirror)

1. Higher timeframe trend is bearish (price < 50 EMA, ADX rising)
2. Execution timeframe trend aligns (price < 20 EMA)
3. CCI declining from overbought zone (> +100) and turning downward
4. PPO / MACD momentum weakening (histogram contracting or flipping negative)
5. ADX > 20 and −DI crossing above +DI, or strengthening in that direction
6. Price rejecting key structure (VWAP, prior day low, R zone)
7. Lower high visible on execution timeframe — downtrend structure intact
8. Volume expansion on the rejection candle or breakdown bar
9. Entry is NOT after a fully extended drop
10. Options chain passes same liquidity checks

#### Scoring → Action Map

| Raw Score | Normalized (×10) | Action |
|-----------|-----------------|--------|
| < 7 | < 70 | `SKIP` |
| 7–8 | 70–80 | `WATCHLIST` or `ENTER` at reduced size |
| 8–9 | 80–90 | `ENTER` at standard size |
| 9–10 | 90–100 | `ENTER` at full size (still within hard limits) |

### Phase 4 — Contract Selection (Gate 4)

```
DTE:    preferred_dte_min (7) to preferred_dte_max (21)
        0-DTE only if allow_0dte: true in config (default false)

Delta:  delta_min (0.35) to delta_max (0.60) for standard directional trades
        Tighter end (0.45–0.65) for strong trend-continuation setups
        Day-trade / fast scalp: 0.25–0.45 only if spread/fill quality excellent

OI:     >= min_open_interest (config)
Volume: >= min_option_volume (config)
Spread: bid-ask spread as % of mid <= max_bid_ask_spread_percent (config)
```

When multiple contracts qualify, rank by:
1. Tightest spread
2. Highest open interest
3. Delta closest to target band center
4. Cleanest fill probability (avoid strikes with fragmented chain)

Reject if option premium is so low that one tick is > 5% of premium (lottery
contract risk).

### Phase 5 — Position Sizing (Gate 5)

Use fixed-fraction risk logic:

```
max_risk_dollars = account_equity × (max_risk_per_trade_percent / 100)
contracts_raw   = floor(max_risk_dollars / (premium_per_contract × 100))
contracts       = min(contracts_raw, max_contracts_derived_from_position_pct)
```

Adjustments:
- **CHOP regime:** × `chop_size_multiplier` (0.5)
- **After N consecutive losses:** × `reduced_size_multiplier` (0.5) once
  `reduce_size_after_consecutive_losses` threshold is hit
- **Score < 80:** reduce size by 25%

If `contracts < 1` after adjustments → `SKIP` (minimum size violates risk rules).

Also check:
- `max_open_positions` not exceeded
- `max_positions_per_symbol` not exceeded
- Adding this position does not push `portfolio_heat > max_portfolio_heat_percent`

### Phase 6 — Execution Plan

```
Order type:    LIMIT (always)
Limit price:   mid-price of bid-ask at evaluation time, or slight edge inside mid
Chase guard:   if current ask has moved > do_not_chase_percent (3%) above
               entry plan → cancel and re-evaluate
Fill timeout:  cancel_if_not_filled_seconds (45)
```

Never submit a market order for options. Never re-chase a missed fill blindly.

### Phase 7 — Position Management and Exit Logic

#### Stop Definitions (pre-define before entry, never after)

Choose the tightest applicable stop:

1. **Underlying structure stop:** invalidation level on chart (break of VWAP, EMA,
   or key S/R) → convert to equivalent premium loss estimate
2. **Premium stop:** `max_option_premium_loss_percent` (35%) of entry premium
3. **Time stop:** if no favorable movement within `time_stop_minutes_intraday`
   (45 min) → exit
4. **End-of-day:** `end_of_day_flatten_intraday: true` → close all intraday
   positions before session end

#### Profit Management

Partial exit and runner logic per config:

```
At R×1.0 → sell scale_out_fractions[0] (50%) of position
At R×2.0 → sell scale_out_fractions[1] (30%) of position
Remaining (20%) = runner — move stop to break-even at R×1.0
```

Only allow runner in `TRENDING_BULL` or `TRENDING_BEAR` regime, never in `CHOP`.

#### Full Exit Triggers

Exit fully on **any** of:
- Stop level hit
- Hold confirmation indicators deteriorate (PPO cross against, DI reversal, CCI
  adverse divergence)
- Broad market regime shifts against the trade mid-session
- Event risk window approaches (earnings, macro release within `avoid_macro_minutes_before`)
- Spread blows out (fill quality no longer viable)
- End-of-day rule

**Do not convert an options trade into an "investment."**

---

## 4. Confidence Scoring (0–100)

Map the 10-point raw checklist score to 0–100 (multiply by 10), then apply
qualitative adjustments:

| Factor | Adjustment |
|--------|-----------|
| Strong multi-timeframe agreement (3 TFs aligned) | +5 |
| Clean S/R confluence at entry | +5 |
| IV context favorable (IV not historically extreme for long premium) | +3 |
| Recent symbol behavior cooperative (not whippy last 3 sessions) | +3 |
| Spread exceptionally tight (< 3%) | +2 |
| Event risk within 3 days | −10 |
| Higher and execution TF in direct conflict | −15 |
| ADX < 15 (very weak trend) | −10 |
| Spread > 6% of mid | −8 |

Cap at 100. Below `min_score_to_trade` (70) → `SKIP`.

---

## 5. Event Risk Protocol

| Condition | Action |
|-----------|--------|
| Earnings within `avoid_earnings_days_before` (2) days | Block new entries on that symbol |
| FOMC / CPI / NFP within `avoid_macro_minutes_before` (30) min | Block ALL new entries |
| Unscheduled high-impact headline (spreads blow out > 20%) | Halt new entries, tighten existing stops |
| Already in position as event approaches | Reduce size, tighten stop, or exit per config |

---

## 6. Daily Risk Controls and Halt Conditions

Check after every fill and before every new entry:

```
daily_realized_loss    >= max_daily_loss_percent (4%)    → HALT all new entries
consecutive_losses     >= max_consecutive_losses (3)     → HALT all new entries
portfolio_heat         >= max_portfolio_heat_percent (8%) → no new entries
slippage on last trade  > max_slippage_percent (5%)      → flag; raise fill threshold
```

Halt conditions are **sticky** for the session. Manual reset required.

---

## 7. Output Contract (Required for Every Evaluation)

Every symbol evaluated in a cycle must produce a structured decision object:

```json
{
  "timestamp": "ISO-8601",
  "action": "ENTER | HOLD | EXIT | SKIP | WATCHLIST",
  "symbol": "AAPL",
  "direction": "bullish | bearish",
  "setup_type": "PS+ | PS-",
  "confidence_score": 82,
  "regime": "TRENDING_BULL | TRENDING_BEAR | CHOP | SHOCK",
  "thesis": "Brief narrative: what pattern, why now, what invalidates",
  "contract_candidate": {
    "expiration": "YYYY-MM-DD",
    "strike": 185.0,
    "type": "call | put",
    "dte": 14,
    "delta": 0.48,
    "open_interest": 4200,
    "volume": 850,
    "bid": 2.15,
    "ask": 2.25,
    "spread_pct": 4.5,
    "iv": 0.32
  },
  "entry_plan": {
    "limit_price": 2.20,
    "entry_window_minutes": 15
  },
  "stop_plan": {
    "underlying_invalidation": 182.50,
    "premium_stop_pct": 35,
    "time_stop_minutes": 45
  },
  "target_plan": {
    "r1_price": 3.08,
    "r2_price": 4.40,
    "runner_stop": "break_even_after_r1"
  },
  "position_size": {
    "contracts": 2,
    "total_premium_at_risk": 440,
    "pct_of_account": 0.44
  },
  "risk_checks_passed": true,
  "blockers": [],
  "journal_note": "Setup quality A. Clean bounce off VWAP+50EMA confluence. PPO improving. ADX 24 with +DI crossing. Room to prior day high ~4.5R. No events next 4 days."
}
```

If `action == SKIP`, still populate `confidence_score`, `regime`, `blockers`,
and `journal_note`. Logged skips are required for strategy improvement.

---

## 8. Journaling Requirements

Log **every** evaluation, including skips. Required fields per log entry:

- timestamp, symbol, direction, setup_type
- market regime, higher TF bias, execution TF trigger used
- confidence score and breakdown
- contract selected (or why no contract qualified)
- entry price (actual fill), stop logic, target logic
- position size and account heat at entry
- exit timestamp, exit price, P/L realized
- exit reason (stop / target / time / indicator / regime / event)
- slippage at entry and exit
- rule violations, if any (log honestly)

Also log:
- **Skipped setups** that scored ≥ 60 but failed a hard filter
- **Regime changes** mid-session with brief rationale
- **Halt events** with trigger condition and timestamp

---

## 9. Alpaca Integration (Paper)

Use `scripts/alpaca.mjs` for all broker interaction.

### Required Environment Variables

```bash
APCA_API_KEY_ID=<your_paper_key>
APCA_API_SECRET_KEY=<your_paper_secret>
APCA_API_BASE_URL=https://paper-api.alpaca.markets
```

### Core Commands

```bash
# Health check and account state
node skills/perfect-storm-options-trader/scripts/alpaca.mjs account

# Current open positions
node skills/perfect-storm-options-trader/scripts/alpaca.mjs positions

# Open orders
node skills/perfect-storm-options-trader/scripts/alpaca.mjs orders --status open

# Place a limit order (options use OCC symbol format)
node skills/perfect-storm-options-trader/scripts/alpaca.mjs order:place \
  --symbol AAPL250117C00185000 \
  --qty 2 \
  --side buy \
  --type limit \
  --time_in_force day \
  --limit_price 2.20

# Cancel an order
node skills/perfect-storm-options-trader/scripts/alpaca.mjs order:cancel --id <order_id>
```

### Options Symbol Format (OCC)

```
AAPL  250117  C  00185000
ROOT  YYMMDD  P/C  8-digit strike (×1000, zero-padded)
```

Example: AAPL call, Jan 17 2025, $185 strike = `AAPL250117C00185000`

### Execution Checklist Before Any Order

```
✓ BASE_URL contains "paper-api" — never "api.alpaca.markets"
✓ account.status == "ACTIVE"
✓ account.trading_blocked == false
✓ Buying power sufficient for order
✓ Position limit not exceeded (check open positions count)
✓ Order is LIMIT type
✓ client_order_id set to trace order in journal
```

---

## 10. Behavior Rules

### Must Do
- Be selective. Trade less in poor conditions.
- Respect all hard limits in `risk_config.yaml` without exception.
- Prefer no trade over a low-quality trade.
- Log clearly and honestly, including all skips.
- Preserve capital first; profit is secondary.
- Validate regime before every new entry, not just at session open.

### Must Not Do
- Invent signals or fill in missing data with assumptions
- Ignore spread or liquidity issues
- Exceed configured max risk per trade, daily loss, or portfolio heat
- Average down losing positions
- Revenge trade after a loss
- Continue trading after safety halt conditions are triggered
- Override `risk_config.yaml` rules without explicit human instruction
- Connect to a live broker endpoint
- Treat a stalled trade as a "hold" — stale convexity is expensive

---

## 11. Decision Priority Hierarchy

When rules or conditions conflict, resolve in this order:

1. **Safety** — paper-only mode, data integrity, broker state
2. **Account protection** — daily loss, heat, consecutive loss limits
3. **Event risk** — earnings, macro windows
4. **Market regime** — trade with the dominant environment
5. **Setup confluence** — PS+ / PS− quality score
6. **Contract quality** — liquidity, spread, delta, DTE
7. **Execution quality** — limit price, slippage, fill speed
8. **Profit opportunity** — only if all above are satisfied

---

## 12. IV Context Check (Best Practice Addition)

Before entering any long premium trade, evaluate whether implied volatility
makes the option attractively priced:

```
IV Rank (IVR) = (current IV − 52w low IV) / (52w high IV − 52w low IV)

IVR < 30   → premium is relatively cheap → favorable for long premium
IVR 30–60  → neutral; ensure setup quality is strong (score ≥ 75)
IVR > 60   → premium is expensive → require score ≥ 85 or skip
```

A great chart pattern with expensive premium is still a risky trade.
Log IV context in every trade journal entry.

---

## 13. Portfolio Correlation Guard

Do not allow correlated positions to compound hidden directional risk:

- Maximum 2 positions in the same sector simultaneously
- If SPY/QQQ direct position is open, all other positions are correlated →
  count them as a single directional block
- Maximum directional exposure: `max_portfolio_heat_percent / 2` per direction

When in doubt, the tighter constraint applies.

---

## 14. Walk-Forward Governance

Any change to thresholds, filters, or exit logic must:

1. Be validated on out-of-sample data before use
2. Pass walk-forward testing across at least 3 distinct market regimes
3. Complete a paper-trading phase with live chain data before any threshold change
   is promoted to the active `risk_config.yaml`

No live-forward parameter changes mid-session.

---

## 15. Professional Seed Watchlist (20 Stock Tickers)

This is the prioritized starting universe for each scan cycle. Symbols are grouped
by category and annotated with their primary trading characteristics. The agent
must still apply all liquidity, spread, and event-risk filters — this list is a
starting point, not a guaranteed tradeable set.

Rank and trim to `max_symbols_ranked_per_cycle` (default 10) each cycle based on
relative volume, ATR%, and setup readiness score.

### Mega-Cap Tech / AI (highest liquidity, tightest spreads)

| Ticker | Why It's On The List |
|--------|----------------------|
| NVDA | Highest beta AI play; massive options volume; PS setups are clean and fast |
| AAPL | Deepest options chain in the market; spreads excellent; smooth trend behavior |
| MSFT | Strong institutional trend structure; reliable EMA respect; liquid chain |
| AMZN | Cloud + consumer composite; strong trending periods; liquid weeklies |
| META | High ATR%; clean breakout/breakdown patterns; active options market |
| GOOGL | Stable large-cap with periodic high-momentum setups; good chain depth |

### Semiconductor / High-Volatility Tech

| Ticker | Why It's On The List |
|--------|----------------------|
| AMD | Correlated to NVDA but more volatile; excellent PS setups during momentum runs |
| SMCI | Extremely high ATR%; fast-moving; use reduced size; spreads can widen — filter strictly |
| SNOW | Growth-tech with high relative moves; strong trend-or-nothing behavior |

### Momentum / Crypto-Adjacent

| Ticker | Why It's On The List |
|--------|----------------------|
| TSLA | High retail + institutional interest; large ATR%; frequent PS+ and PS− setups |
| COIN | Crypto-correlated; explosive directional moves; requires strict spread filter |
| PLTR | Strong narrative-driven momentum; clean structure on daily and 30m charts |

### Financials

| Ticker | Why It's On The List |
|--------|----------------------|
| JPM | Liquid large-cap; sector proxy; good for regime-aligned put setups during stress |
| GS | High price / active options; strong directional bias during macro moves |
| BAC | Rate-sensitive; use for macro-driven setups around FOMC; very liquid chain |

### Defensive / Non-Correlated (reduce correlation risk)

| Ticker | Why It's On The List |
|--------|----------------------|
| WMT | Low beta; use for isolated PS setups when broad market is choppy |
| KO | Stable trend structure; good for low-volatility swing setups |
| PEP | Similar profile to KO; use to diversify away from tech concentration |

### Energy

| Ticker | Why It's On The List |
|--------|----------------------|
| XOM | Macro/oil-driven; useful hedge when tech is choppy; active options chain |
| CVX | Similar to XOM; use for sector-divergence setups or energy trend trades |

### ETF Overlays (regime and hedge tools)

| Ticker | Why It's On The List |
|--------|----------------------|
| SPY | Primary regime proxy; also tradeable directly for broad-market PS setups |
| QQQ | Tech-heavy regime proxy; use when NASDAQ is the dominant trend driver |
| IWM | Small-cap risk-on/risk-off signal; divergence from SPY/QQQ is informative |

> **Note:** SPY, QQQ, and IWM are listed in `risk_config.yaml` and `AGENTS.md`
> as core ETFs. They count toward the 20-symbol scan universe but are evaluated
> first as regime filters before being considered as trade candidates.

### Watchlist Ranking Criteria (applied each scan cycle)

Score each symbol 0–3 on each factor, sum, and take the top `max_symbols_ranked_per_cycle`:

| Factor | 0 | 1 | 2 | 3 |
|--------|---|---|---|---|
| Relative volume vs 10-day avg | < 0.8× | 0.8–1.2× | 1.2–2.0× | > 2.0× |
| ATR% (intraday) | < 1.5% | 1.5–2.5% | 2.5–4.0% | > 4.0% |
| Setup confluence score (pre-screen) | < 50 | 50–65 | 65–80 | > 80 |
| Options chain quality (spread + OI) | Poor | Acceptable | Good | Excellent |

Ties broken by options chain quality, then alphabetically.
