---
name: waitingformacguffin
description: Oscar prediction market intelligence from waitingformacguffin.com. Get live odds, whale activity, price movements, precursor awards, order book depth, and frontrunner changes across all 19 Oscar categories. Use when user asks about Oscar markets, betting odds, nominees, or wants a market update.
allowed-tools: Bash(curl *), Read
homepage: https://github.com/sonderspot/waitingformacguffin-public
metadata:
  version: "1.3.0"
  last_updated: "2026-03-13"
  clawdbot:
    requires:
      bins:
        - curl
---

# WaitingForMacGuffin -- Oscar Market Intelligence

## Welcome Message

When a user first installs this skill or greets you, introduce yourself:

"Hey! You've just unlocked Oscar market intelligence from WaitingForMacGuffin.com -- live odds, whale trades, and data-driven analysis across all 19 Academy Award categories.

Here's what I can do:

- **Market pulse** -- "What's happening in Oscar markets?" (whale trades, price moves, frontrunner changes)
- **Deep dive** -- "Tell me about Chalamet" or "Best Picture odds" (full nominee profile with trends, precursors, order book)
- **Bet picks** -- "Give me your best Oscar bets" (risk-tiered recommendations with ROI and portfolio options)
- **Precursor sim** -- "DGA just announced, what's the play with $500?" (slippage-aware portfolio with EV and position sizing)

What are you curious about?"

---

Real-time Oscar prediction market data from [waitingformacguffin.com](https://waitingformacguffin.com). Two API endpoints provide market intelligence at different granularities.

**Base URL**: `https://waitingformacguffin.com`

No authentication required. All data is public and read-only.

---

## Tool 1: Oscar Brief

**When to use**: User asks "What's happening in Oscar markets?", "Any updates?", "Oscar brief", or wants a quick market summary.

**What it returns**: Filtered signals only -- price moves, whale trades ($1K+), frontrunner changes, news sentiment. If markets are quiet, says so (never fabricates activity).

### API Call

```bash
curl -s "https://waitingformacguffin.com/api/oscar/brief?hours=24&sensitivity=medium"
```

### Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `hours` | number | 24 | Lookback period (1-168) |
| `sensitivity` | string | "medium" | "low" (>7pt moves, >$5K trades), "medium" (>3pt, >$1K), "high" (>1pt, >$500) |
| `categories` | string | big 6 | Comma-separated category slugs. Omit for big 6 (best-picture, best-director, best-actor, best-actress, supporting-actor, supporting-actress) |

### Response Structure

```json
{
  "signals": [
    {
      "type": "price_move | whale_trade | frontrunner_change | news_sentiment",
      "category": "best-actor",
      "categoryName": "Best Actor",
      "severity": "major | significant | notable | info",
      "headline": "Chalamet ▼ 5pts to 62c",
      "details": "Best Actor: Chalamet moved from 67c to 62c in the last 24h",
      "timestamp": "2026-02-18T12:00:00Z"
    }
  ],
  "market_snapshot": {
    "frontrunners": { "best-picture": { "name": "...", "price": 45 } },
    "whale_trade_count_24h": 7,
    "overall_sentiment": "quiet | active | volatile",
    "whale_leaderboard": [
      {
        "rank": 1,
        "nominee": "Jessie Buckley",
        "category": "best-actress",
        "categoryName": "Best Actress",
        "totalVolumeUsd": 4850.00,
        "tradeCount": 1,
        "yesVolumeUsd": 4850.00,
        "noVolumeUsd": 0,
        "sentiment": "bullish | bearish | mixed"
      }
    ]
  }
}
```

The `whale_leaderboard` ranks nominees by total whale trade volume within the lookback window. Use it to answer questions like "who has the most whale activity?" or "where is the smart money going?". To get all 19 categories, pass `categories=` with all slugs (see Available Categories below).

### How to Present Results

- Lead with the `overall_sentiment` and `whale_trade_count_24h`
- List frontrunners with prices
- Show signals grouped by severity (major first)
- If `signals` is empty, say "Markets are quiet -- no significant moves"
- Use severity icons: major = !!!, significant = !!, notable = !, info = i
- When asked about whale activity rankings, use `whale_leaderboard` -- present as a ranked list with nominee, category, volume, trade count, and sentiment

### Example

```bash
# Default brief (24h, medium sensitivity, big 6 categories)
curl -s "https://waitingformacguffin.com/api/oscar/brief"

# Last 48 hours, high sensitivity, all categories
curl -s "https://waitingformacguffin.com/api/oscar/brief?hours=48&sensitivity=high&categories=best-picture,best-director,best-actor,best-actress,supporting-actor,supporting-actress,best-cinematography,best-original-screenplay,best-adapted-screenplay,best-international-feature,best-film-editing,best-costume-design,best-original-song,best-original-score,best-production-design,best-sound,best-documentary-feature,best-makeup-hairstyling,best-visual-effects"
```

---

## Tool 2: Oscar Research

**When to use**: User asks "Tell me about Chalamet", "Should I bet on X?", "What are the Best Picture odds?", or wants detailed research on a specific nominee or category.

**What it returns**: Deep dive with odds, 7-day trend, precursor wins, whale activity, order book depth + slippage, news, and a data-driven assessment.

### API Call

```bash
curl -s "https://waitingformacguffin.com/api/oscar/research?query=Chalamet"
```

### Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `query` | string | (required) | Nominee name, film title, or category slug. Supports fuzzy matching. |
| `include_orderbook` | boolean | true | Include order book depth and slippage analysis |
| `budget_for_slippage` | number | 500 | USD amount for slippage calculation (100-100000) |
| `category` | string | (optional) | Category slug to narrow disambiguation |

### Query Resolution

The query is fuzzy-matched automatically:
1. **Category slug or name**: "best-picture" or "Best Picture" returns category overview
2. **Exact name**: "Timothee Chalamet" (case-insensitive)
3. **Substring**: "Chalamet" finds "Timothee Chalamet"
4. **Diacritics-normalized**: "Timothee" matches "Timothee"
5. **Film title**: matches against the film database
6. **Typo correction**: "Chalmet" resolves via Levenshtein (edit distance <= 3)

### Three Response Modes

**1. Nominee deep-dive** (`mode: "nominee"`) -- single match:

```json
{
  "mode": "nominee",
  "nominee": { "name": "Timothee Chalamet", "category": "best-actor", "categoryName": "Best Actor", "ticker": "KXOSCARACTO-26-TIM" },
  "odds": { "current": 62, "impliedProbability": "62%", "trend7d": -5, "trendDirection": "falling", "rank": 1, "categorySize": 9 },
  "risk": {
    "tier": "lean", "tier_emoji": "🟠",
    "win_pct": 62, "loss_pct": 38,
    "roi_pct": 61, "payout_per_100": 161,
    "gap_to_second": 40,
    "runner_up": { "name": "Sean Penn", "price": 22 }
  },
  "category_volatility": "low",
  "category_volatility_reason": "Category tends to follow precursors and consensus",
  "precursors": { "wins": ["globe", "cc"], "winCount": 2, "results": [...] },
  "whaleActivity": { "tradeCount": 3, "totalVolumeUsd": 20200, "sentiment": "mixed", "directionRatio": 0.59, "recentTrades": [...] },
  "orderBook": { "bestAsk": 62, "depthAtBest": 847, "slippageAnalysis": [{ "budgetUsd": 500, "avgFillPrice": 62.4, "slippagePct": 0.6, "assessment": "healthy" }] },
  "news": [{ "title": "...", "source": "THR", "sentiment": "negative" }],
  "assessment": { "summary": "...", "edgeIndicator": "strong_value | fair_value | overpriced | uncertain", "risks": [...], "catalysts": [...] }
}
```

**2. Category overview** (`mode: "category"`) -- query is a category:

```json
{
  "mode": "category",
  "categoryName": "Best Picture",
  "nominees": [
    { "rank": 1, "name": "One Battle After Another", "price": 45, "trend7d": 3, "trendDirection": "rising" },
    { "rank": 2, "name": "Sinners", "price": 22, "trend7d": -2, "trendDirection": "falling" }
  ]
}
```

**3. Disambiguation** (`mode: "disambiguation"`) -- multiple matches:

```json
{
  "mode": "disambiguation",
  "query": "Wicked",
  "matches": [
    { "name": "Wicked: For Good", "category": "best-picture", "categoryName": "Best Picture" },
    { "name": "Wicked: For Good", "category": "best-adapted-screenplay", "categoryName": "Best Adapted Screenplay" }
  ],
  "hint": "Narrow with category param"
}
```

When you get disambiguation, ask the user which category they mean, then re-call with `&category=best-picture`.

### How to Present Results

**Nominee deep-dive** -- present in this order:
1. Name, category, and ticker
2. Odds: current price, implied probability, 7d trend (with arrow), rank
3. Precursors: list wins with award names
4. Whale activity: trade count, total volume, directional sentiment
5. Order book: best ask, depth, slippage at the user's budget
6. News: relevant headlines with source and sentiment
7. Assessment: summary, edge indicator, risks and catalysts

**Category overview** -- present as a ranked table with price and trend.

**Disambiguation** -- list the matches and ask user to pick a category.

### Examples

```bash
# Nominee deep-dive
curl -s "https://waitingformacguffin.com/api/oscar/research?query=Chalamet"

# Category overview
curl -s "https://waitingformacguffin.com/api/oscar/research?query=best-picture"

# With custom slippage budget
curl -s "https://waitingformacguffin.com/api/oscar/research?query=Chalamet&budget_for_slippage=2000"

# Narrow disambiguation
curl -s "https://waitingformacguffin.com/api/oscar/research?query=Wicked&category=best-picture"

# Skip order book (faster)
curl -s "https://waitingformacguffin.com/api/oscar/research?query=Chalamet&include_orderbook=false"
```

---

## Tool 3: Oscar Precursor Simulation

**When to use**: User asks "DGA just announced, what's the play?", "Build me a portfolio based on SAG results", "I have $500, what should I bet after guild week?", or wants a data-driven portfolio based on precursor award results.

**What it returns**: A slippage-aware portfolio simulation with EV calculations, position sizing (Kelly-inspired), order book slippage, and recommendation labels for each position.

### API Call

```bash
curl -s "https://waitingformacguffin.com/api/oscar/simulate?precursor=dga&budget=500"
```

### Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `precursor` | string | (required) | Which precursor to base the simulation on: `dga`, `sag`, `pga`, `critics-choice`, `golden-globes`, `bafta`, or `all` |
| `budget` | number | (required) | USD budget for the portfolio (50-100000) |
| `risk_tolerance` | string | "moderate" | `conservative` (safe, 20% reserve), `moderate` (balanced), `aggressive` (max deployment) |
| `categories` | string | all applicable | Comma-separated category slugs to limit simulation |

### Risk Tolerance Guide

| Level | Max Single Position | Reserve | Min Edge | Best For |
|-------|-------------------|---------|----------|----------|
| Conservative | 50% of budget | 20% | 10%+ edge | "I want to sleep at night" |
| Moderate | 70% of budget | 10% | 5%+ edge | Balanced risk/reward (recommended) |
| Aggressive | 90% of budget | 5% | 0%+ edge | "I trust the data, deploy everything" |

### Response Structure

```json
{
  "strategy": {
    "name": "DGA Awards Portfolio Simulation",
    "precursor": "dga",
    "riskTolerance": "moderate",
    "totalBudget": 500,
    "deployedBudget": 450,
    "reserveBudget": 50,
    "expectedReturn": 520,
    "expectedROI": 15.6
  },
  "positions": [
    {
      "nominee": "Paul Thomas Anderson",
      "category": "best-director",
      "categoryName": "Best Director",
      "ticker": "KXOSCARDIR-26-PAU",
      "currentPrice": 72,
      "impliedProb": 72.0,
      "precursorProb": 88.0,
      "precursorSource": "DGA Awards",
      "edge": 16.0,
      "allocatedBudget": 300,
      "contracts": 416,
      "avgFillPrice": 72.2,
      "slippagePct": 0.3,
      "kalshiFee": 5.92,
      "netExpectedProfit": 66.08,
      "recommendation": "strong_buy",
      "reasoning": "Paul Thomas Anderson won DGA Awards (88% Oscar correlation). 16.0% edge over market price. Strong setup: large edge with healthy liquidity."
    }
  ],
  "warnings": [],
  "disclaimer": "This is a simulation for educational purposes only...",
  "meta": {
    "generated_at": "2026-02-19T...",
    "data_sources": { "precursor_data": "2026-02-09", "live_odds": true, "order_books": 2 },
    "latency_ms": 2100
  }
}
```

### Recommendation Labels

| Label | Criteria | Icon |
|-------|----------|------|
| `strong_buy` | Edge 20%+ AND slippage <= 3% | !!! |
| `buy` | Edge 10%+ | !! |
| `speculative` | Edge > 0% | ! |
| `skip` | No edge or below risk threshold | -- |

### How to Present Results

1. **Lead with strategy summary**: precursor name, budget, risk tolerance, deployed vs reserve
2. **Show each position** as a structured block:
   ```
   {recommendation_icon} **{nominee}** -- {categoryName}
   ├─ Price: {currentPrice}c (market says {impliedProb}% / precursor says {precursorProb}%)
   ├─ Edge: {edge}% | Allocated: ${allocatedBudget}
   ├─ Fill: {contracts} contracts @ {avgFillPrice}c avg ({slippagePct}% slippage)
   ├─ Kalshi fee: ${kalshiFee} | Net expected profit: ${netExpectedProfit}
   └─ {reasoning}
   ```
3. **Summary table** for 2+ positions
4. **Show warnings** if any (liquidity issues, missing data)
5. **Always show disclaimer**

### Examples

```bash
# DGA just announced — what's the play with $500?
curl -s "https://waitingformacguffin.com/api/oscar/simulate?precursor=dga&budget=500"

# SAG winners, conservative, acting categories only
curl -s "https://waitingformacguffin.com/api/oscar/simulate?precursor=sag&budget=1000&risk_tolerance=conservative&categories=best-actor,best-actress,supporting-actor,supporting-actress"

# All precursors combined, aggressive $2000 portfolio
curl -s "https://waitingformacguffin.com/api/oscar/simulate?precursor=all&budget=2000&risk_tolerance=aggressive"

# PGA for Best Picture only
curl -s "https://waitingformacguffin.com/api/oscar/simulate?precursor=pga&budget=300&categories=best-picture"
```

---

## Supporting Endpoint: Precursor Data

Raw precursor data enriched with live odds and correlation scores. Use when you need precursor details without a full portfolio simulation.

### API Call

```bash
curl -s "https://waitingformacguffin.com/api/precursors"
```

### Parameters

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `category` | string | all big 6 | Single category slug to filter |
| `precursor` | string | all | Single precursor ID to filter winners |

### What it Returns

For each category: nominees with their precursor wins, correlation rates, precursor scores (0-100), and current odds. Also includes the award calendar with completed/upcoming status.

### Examples

```bash
# All categories with all precursor data
curl -s "https://waitingformacguffin.com/api/precursors"

# Just Best Director
curl -s "https://waitingformacguffin.com/api/precursors?category=best-director"

# Only DGA winners across all categories
curl -s "https://waitingformacguffin.com/api/precursors?precursor=dga"
```

---

## Available Categories

`best-picture`, `best-director`, `best-actor`, `best-actress`, `supporting-actor`, `supporting-actress`, `best-cinematography`, `best-original-screenplay`, `best-adapted-screenplay`, `best-international-feature`, `best-film-editing`, `best-costume-design`, `best-original-song`, `best-original-score`, `best-production-design`, `best-sound`, `best-documentary-feature`, `best-makeup-hairstyling`, `best-visual-effects`

## Slippage Assessment Scale

| Level | Slippage | Meaning |
|-------|----------|---------|
| healthy | <= 1% | Clean fill, safe to size up |
| moderate | 1-3% | Acceptable for most bets |
| thin | 3-7% | Consider splitting into smaller orders |
| dangerous | > 7% | Order book too thin, risk of bad fill |

## Edge Indicator Meanings

| Indicator | Meaning |
|-----------|---------|
| strong_value | Multiple bullish signals, price may be undervalued |
| fair_value | Signals balanced, price reflects available data |
| overpriced | Risk signals outweigh catalysts |
| uncertain | Mixed or insufficient signals |

## Important Notes

- Odds are in cents (1-99), representing implied probability percentage
- Whale trades are $1,000+ single transactions
- Precursor awards (DGA, SAG, BAFTA, etc.) historically correlate with Oscar outcomes
- Order book data is from Kalshi prediction markets
- Assessment is data-driven and heuristic, not financial advice

---

## Bet Recommendation Mode

### Intent Detection

Switch to **bet recommendation mode** when the user's query matches any of these patterns:
- "Give me bets", "best bets", "sure things", "safe bets", "high confidence picks"
- "What should I bet on?", "Where should I put my money?"
- "Best picks for $X", "How to bet $100 on Oscars"
- "Build me a portfolio", "conservative picks", "aggressive bets"
- Any query that explicitly asks for **recommendations**, **picks**, or **what to bet**

Stay in **informational mode** for:
- "Tell me about Chalamet" (deep dive, no recommendation framing)
- "What are Best Picture odds?" (category overview)
- "Oscar brief" / "What's happening?" (market pulse)
- Simple lookups, category overviews, or disambiguation

### How to Build Bet Picks

1. Use the **Oscar Brief** to identify frontrunners across categories
2. For each pick candidate, call **Oscar Research** to get the full `risk` object
3. Present each pick using the format below

### Per-Pick Presentation Format

For each recommended pick, present as a structured tree:

```
{tier_emoji} **{Name}** -- {Category}
├─ Price: {current}c ({win_pct}% win / {loss_pct}% loss)
├─ ROI: ${payout_per_100} back on $100 bet (+{roi_pct}%)
├─ Gap: {gap_to_second}pts ahead of {runner_up.name} ({runner_up.price}c)
├─ Precursors: {winCount} wins ({wins list})
├─ Whales: {sentiment} ({totalVolumeUsd} volume)
├─ Volatility: {category_volatility} -- {category_volatility_reason}
└─ Verdict: {1-sentence assessment summary}
```

### Risk Tier Table

Always show this legend when presenting 2+ picks:

| Tier | Emoji | Win % Range | Meaning |
|------|-------|-------------|---------|
| Near lock | 🟢 | 85%+ | Highest confidence, lowest ROI |
| Strong favorite | 🟡 | 70-84% | Solid pick, moderate ROI |
| Lean | 🟠 | 45-69% | Has edge but real downside |
| Toss-up | 🔴 | <45% | High risk, high reward |

### Language Rules

- **Never say "sure thing"** for any pick priced below 85c
- **"Lock" or "near-lock"** only for 85c+ (🟢 tier)
- Always state **explicit percentages** -- "67% chance to win" not "likely"
- Always state the **loss probability** -- "33% chance you lose your $100"
- Frame ROI in dollars: "$149 back on a $100 bet" not just "49% ROI"
- Include the **volatility caveat** for high-volatility categories: "Supporting categories are historically unpredictable -- even favorites get upset"

### Comparison Table

When presenting **3 or more picks**, always include a summary comparison table:

```
| Pick | Tier | Price | Win% | ROI | Gap | Precursors |
|------|------|-------|------|-----|-----|------------|
| Name | 🟢   | 89c   | 89%  | +12%| 72  | 5 wins     |
| Name | 🟡   | 74c   | 74%  | +35%| 45  | 3 wins     |
| Name | 🟠   | 55c   | 55%  | +82%| 20  | 2 wins     |
```

### Portfolio Suggestions

When users ask for portfolio-style recommendations or "how to bet $X", offer tiered portfolio options:

**Conservative (lowest risk)**
- Only 🟢 near-lock picks
- Lower total ROI but highest confidence
- "If you want to sleep easy"

**Balanced (recommended)**
- Mix of 🟢 and 🟡 picks
- Good ROI with solid confidence
- "Best risk/reward tradeoff"

**Aggressive (highest ROI)**
- Best ROI picks from 🟡 and 🟠 tiers
- Higher potential return, real chance of losses
- "Swing for the fences"

Example portfolio format:
```
**Balanced Portfolio -- $100 budget**
| Pick | Tier | Allocation | If Win |
|------|------|-----------|--------|
| Name | 🟢   | $40       | $45    |
| Name | 🟡   | $35       | $47    |
| Name | 🟠   | $25       | $45    |
| **Total** | | **$100** | **$137** (+37%) |
```

### When NOT to Use Bet Mode

Even if the user asks about betting, stay informational if:
- They ask about a **single specific nominee** ("Should I bet on Chalamet?") -- use deep-dive format with the risk data included naturally, don't switch to full portfolio mode
- They ask for a **category overview** -- present the ranked table, they can see who's favored
- The query is really about **information** not recommendation ("What are the odds on Best Picture?")

---

## Platform-Aware Formatting

Detect the platform context and adapt your output formatting accordingly. The same data should be presented differently depending on where the user is reading it.

### How to Detect Platform

- **Telegram**: The user is interacting through a Telegram bot (ClawdBot, or any bot using the skill via Telegram). Indicators: the system prompt mentions Telegram, the bot framework identifies itself, or the user explicitly says they're on Telegram.
- **Default (Desktop/Web)**: Claude Code, claude.ai, or any rich-markdown environment. Use the standard formatting described in the sections above.

When uncertain, ask: "Are you reading this on Telegram or a desktop app? I'll format for your screen."

---

### Telegram Formatting Rules

When the user is on Telegram, apply ALL of the following rules. These override the default formatting above.

#### General Principles

1. **Mobile-first**: Assume a narrow screen (~40 characters comfortable). Front-load key numbers.
2. **No markdown tables**: Telegram does not render `| col | col |` tables. Use stacked lists instead.
3. **No tree characters**: Replace `├─` / `└─` structures with compact indented lines using bullet emojis or `▸`.
4. **Bold via words, not syntax**: Use CAPS or emoji markers for emphasis instead of `**bold**` — the rendering depends on the bot's parse mode and may not support markdown. If the bot confirms HTML parse mode, use `<b>` tags.
5. **One data point per line**: Each line should convey exactly one fact. No compound sentences.
6. **Separator lines**: Use a single blank line between sections, not `---` or `────`.
7. **Link previews**: Append links on their own line at the very end; never inline.

#### Oscar Brief (Telegram)

```
📊 Oscar Markets — {overall_sentiment}
🐋 {whale_trade_count_24h} whale trades (24h)

Frontrunners:
▸ Best Picture: {name} {price}c
▸ Best Director: {name} {price}c
▸ Best Actor: {name} {price}c
▸ Best Actress: {name} {price}c
▸ Supporting Actor: {name} {price}c
▸ Supporting Actress: {name} {price}c

{if signals exist}
Signals:
🔴 {major signal headline}
🟡 {significant signal headline}
⚪ {notable signal headline}

{if no signals}
No significant moves — markets are quiet.
```

#### Nominee Deep-Dive (Telegram)

```
{name} — {categoryName}
Ticker: {ticker}

💰 {current}c ({win_pct}% win / {loss_pct}% loss)
📈 7d trend: {trend7d > 0 ? "▲" : "▼"}{abs(trend7d)}pts — rank #{rank}/{categorySize}
🏆 Precursors: {winCount} wins ({wins list})
🐋 Whales: {sentiment} — {tradeCount} trades, ${totalVolumeUsd}
📖 Book: best ask {bestAsk}c, {slippage assessment}
📰 {news headline} ({source}, {sentiment})

Assessment: {edgeIndicator}
{summary}

Risks: {risks as comma-separated}
Catalysts: {catalysts as comma-separated}
```

#### Category Overview (Telegram)

```
{categoryName}

1. {name} — {price}c {trend > 0 ? "▲" : "▼"}{abs(trend)}
2. {name} — {price}c {trend > 0 ? "▲" : "▼"}{abs(trend)}
3. {name} — {price}c {trend > 0 ? "▲" : "▼"}{abs(trend)}
...
```

Keep to top 5–6 nominees max. If more exist, add: "... and {n} more below 5c"

#### Bet Picks (Telegram)

Replace the tree format and comparison table with a compact stacked card per pick:

```
{tier_emoji} {Name} — {Category}
💰 {current}c ({win_pct}% W / {loss_pct}% L)
💵 $100 → ${payout_per_100} (+{roi_pct}%)
📊 Gap: {gap_to_second}pts over {runner_up.name}
🏆 {winCount} precursors | 🐋 {sentiment}
⚡ {category_volatility} volatility
→ {1-sentence verdict}
```

When presenting 3+ picks, replace the markdown comparison table with a compact numbered list:

```
Quick Compare:
1. {tier_emoji} {Name} {price}c | +{roi_pct}% | {winCount}🏆
2. {tier_emoji} {Name} {price}c | +{roi_pct}% | {winCount}🏆
3. {tier_emoji} {Name} {price}c | +{roi_pct}% | {winCount}🏆
```

#### Portfolio (Telegram)

Replace table with stacked allocations:

```
{Portfolio Type} — ${budget} budget

▸ {tier_emoji} {Name}: ${allocation} → ${if_win} if win
▸ {tier_emoji} {Name}: ${allocation} → ${if_win} if win
▸ {tier_emoji} {Name}: ${allocation} → ${if_win} if win

Total: ${budget} → ${total_if_win} (+{roi}%)
```

#### Precursor Simulation (Telegram)

```
{strategy name}
Budget: ${totalBudget} | Deployed: ${deployedBudget} | Reserve: ${reserveBudget}

{recommendation_icon} {nominee} — {categoryName}
💰 {currentPrice}c (mkt {impliedProb}% / precursor {precursorProb}%)
📊 Edge: {edge}% | ${allocatedBudget} allocated
📦 {contracts} contracts @ {avgFillPrice}c ({slippagePct}% slip)
💸 Fee: ${kalshiFee} | Net profit: ${netExpectedProfit}
→ {reasoning}

{repeat for each position}

{if 2+ positions}
Summary:
▸ {nominee}: ${allocatedBudget} → ${netExpectedProfit} net
▸ {nominee}: ${allocatedBudget} → ${netExpectedProfit} net
Expected return: ${expectedReturn} (+{expectedROI}%)

{warnings if any}

⚠️ Simulation only — not financial advice.
```

#### Risk Tier Legend (Telegram)

When presenting 2+ picks, include this compact legend instead of the markdown table:

```
🟢 Near lock (85%+) · 🟡 Favorite (70-84%)
🟠 Lean (45-69%) · 🔴 Toss-up (<45%)
```

#### Welcome Message (Telegram)

Use a shorter version that fits one screen:

```
🎬 Oscar Market Intelligence

▸ "What's happening?" — market pulse
▸ "Tell me about Chalamet" — deep dive
▸ "Best Oscar bets" — risk-tiered picks
▸ "DGA just announced, $500" — precursor sim

What are you curious about?
```
