# Kalshalyst Blocklist — Complete Reference

## Why Blocklists Matter

Kalshi has ~3000 open markets at any given time. Without aggressive filtering:
- 80% are noise (weather, micro-timeframes, celebrity gossip, intraday index ranges)
- 15% are sports (requires domain-specific models)
- 5% are tradeable with contrarian reasoning

The blocklist cuts through the noise to focus Claude on the 5% that matter.

## Tier 1: Ticker Prefix Blocklist

These are markets whose tickers start with specific prefixes. They are systematically non-tradeable (noise, coin flips, or spam).

### Weather Markets (High Volume, Pure Noise)

```
KXHIGH     — Will the high temperature in [CITY] exceed X°F on [DATE]?
KXLOW      — Will the low temperature in [CITY] drop below X°F on [DATE]?
KXRAIN     — Will it rain in [CITY] on [DATE]?
KXSNOW     — Will it snow in [CITY] on [DATE]?
KXTEMP     — Will the average temperature in [CITY] be in range [X-Y]°F?
KXWIND     — Will wind speed in [CITY] exceed X mph on [DATE]?
KXWEATH    — General weather category
```

**Why block?**
- Pure noise once you get inside 48 hours
- Meteorological forecasts are accurate to 3-4 days
- After that, coin flip probabilities
- Market makers know this → tight spreads, low edges
- Example: "Will it rain tomorrow in SF?" at 6pm → coin flip, no edge

**Typical volume:** 10,000+ contracts (high interest, zero tradeable edge)

### Intraday Index Range Bets (Coin Flips)

```
INX        — Intraday S&P 500 settlement range bets
NASDAQ     — Intraday Nasdaq settlement range bets
```

**Why block?**
- Market settlement range = purely random walk within day
- No amount of contrarian reasoning fixes randomness within 6 hours
- Market has perfect information (can see all the way to settlement)
- Edges impossible

**Typical edge:** 0% (mathematically)

### Fed Meeting Minute-Range Bets (Garbage)

```
FED-MR     — FOMC statement released at minute X (e.g., 2:00 PM ± 2 min)
```

**Why block?**
- Pure event timing bet
- No edge (Fed publishes exact time ~1 week before)
- Market resolves instantly when announcement time becomes known
- Impossible for Claude to predict

**Typical edge:** 0% (settled before Claude can estimate)

### Entertainment & Celebrity (Noise)

```
KXCELEB    — Will [Celebrity] do [trivial action] by [DATE]?
KXMOVIE    — Will [Movie] gross $X domestically?
KXTIKTOK   — Will [TikTok Video] reach X views?
KXYT       — Will [YouTube Video] reach X views?
KXTWIT     — Will [Twitter Account] reach X followers?
KXSTREAM   — Will [Streamer] reach X viewers?
```

**Why block?**
- Highly volatile, celebrity-driven market sentiment
- No public information edge possible
- Requires domain-specific models (which movie, which streamer)
- Often resolved based on celebrity whim (can change marketing spend)

**Typical edge:** Negative (market makers have better info)

## Tier 2: Category Slug Blocklist

Markets tagged with these Kalshi API category slugs are filtered out:

```
weather            — All weather forecasting markets
climate            — Long-term climate events
entertainment      — Movies, TV, celebrity
sports             — All sports (tracked separately, not blocked)
social-media       — Twitter followers, TikTok trends, etc.
streaming          — Twitch, YouTube streaming metrics
celebrities        — Celebrity gossip, personal milestones
```

**Note:** These are API-level category tags that Kalshi assigns. Used as a secondary filter after ticker prefix checks.

## Tier 3: Micro-Timeframe Patterns (Text-Based Filtering)

Markets matching these patterns in their title are blocked:

```
"in next 15 min"        — Too short, pure noise
"in next 30 min"        — Too short, pure noise
"in next 1 hour"        — Too short, pure noise
"in next 5 min"         — Coin flip
"next 15 minutes"       — Coin flip
"next 30 minutes"       — Coin flip
"next hour"             — Micro-timeframe
"price up in next"      — Intraday price movement (noise)
"price down in next"    — Intraday price movement (noise)
```

**Why block?**
- Markets closing in < 2 hours are dominated by bid-ask spread
- Spreads on these markets: 2-4 cents typical
- Edge needs to be >> spread cost to be tradeable
- Contract duration too short for contrarian reasoning to apply

**Example:** "Will BTC price go up in next 15 minutes?" at 11:45 AM
- Market price: 48¢ (implied 48% probability)
- Spread: 3¢ (typical)
- Cost to trade: 1.5% of capital
- Required edge to breakeven: 1.5%+
- Realistic edge from Claude: 3-5%
- But in 15 minutes, noise >> signal

## Sports Tokens (Tracked But Not Blocked)

Sports markets are NOT automatically filtered. They're tracked separately because they require domain-specific models and have different risk profiles.

### Major League Sports

```
nfl, nba, mlb, nhl, mls, ncaa, pga, ufc, wwe
super bowl, superbowl, march madness, world series,
stanley cup, finals, playoff, mvp, heisman
rushing, passing, touchdown, home run, strikeout,
quarterback, pitcher, espn, sports
```

### Soccer / Football (Most Common Kalshalyst Misses)

```
Premier League, La Liga, Serie A, Bundesliga, Ligue 1
Champions League, Europa League, Copa (any)
MLS, Eredivisie, Liga MX, Primera División
Süper Lig, Premier Liga (Portugal), Chinese Super League
Thai League, Egyptian Premier League

Team names: Arsenal, Chelsea, Liverpool, Man City, Man United
Barcelona, Real Madrid, Juventus, Bayern, PSG
Zamalek, Al Ahly, Al Ittihad, Al Hilal, Al Nassr
(and ~50 more global football clubs)
```

### Esports

```
Valorant, League of Legends, Counter-Strike, CS2, Dota 2
Overwatch, Fortnite, Call of Duty
NRG, Paper Rex, Fnatic, Sentinels, Team Liquid
Gentle Mates, Cloud9, 100 Thieves, FaZe, OpTic
Team Nemesis, NaVi, G2 Esports
```

### Individual Sports (Tennis, Golf, Fighting)

```
ATP, WTA, Tennis (general)
Badminton (professional)
Boxing, MMA, Bellator
```

### Racing

```
Formula 1, F1 (any), NASCAR, IndyCar
```

**Why track separately?**
- Sports markets have strong domain dependencies
- Require specialized models (team stats, form, injuries)
- Kalshi sport markets often have embedded arbitrage (multiple legs)
- Not suitable for general contrarian estimation
- Future enhancement: sports-specific estimator module

## Implementation in Code

### In `kalshalyst.py`

```python
# Category Filtering
_ALLOWED_CATEGORIES = {
    "politics", "policy", "government", "election", "geopolitics",
    "economics", "macro", "fed", "regulation", "legal", "trade",
    "crypto", "finance", "technology", "ai",
}

# Ticker Prefixes (High-Volume Garbage)
_BLOCKED_TICKER_PREFIXES = {
    "KXHIGH", "KXLOW", "KXRAIN", "KXSNOW", "KXTEMP", "KXWIND",
    "KXWEATH", "INX", "NASDAQ", "FED-MR", "KXCELEB", "KXMOVIE",
    "KXTIKTOK", "KXYT", "KXTWIT", "KXSTREAM",
}

# Event Category Slugs (API-Level)
_BLOCKED_CATEGORIES_API = {
    "weather", "climate", "entertainment", "sports",
    "social-media", "streaming", "celebrities",
}

# Micro-Timeframe Patterns
_MICRO_TIMEFRAME_PATTERNS = {
    "in next 15 min", "in next 30 min", "in next 1 hour",
    "in next 5 min", "in next 10 min", "next 15 minutes",
    "next 30 minutes", "next hour", "price up in next",
    "price down in next",
}

# Sports Token Detection (tracked separately, not filtered)
_SPORTS_TOKENS = {
    "nfl", "nba", "mlb", "nhl", ...,
    # (full list of ~200 sports keywords)
}

# Blocklist check
def _is_blocked(ticker: str, category: str = "", title: str = "") -> bool:
    ticker_upper = ticker.upper()
    if any(ticker_upper.startswith(prefix) for prefix in _BLOCKED_TICKER_PREFIXES):
        return True
    if category and category.lower().strip() in _BLOCKED_CATEGORIES_API:
        return True
    title_lower = title.lower()
    if any(pat in title_lower for pat in _MICRO_TIMEFRAME_PATTERNS):
        return True
    return False
```

## Tuning the Blocklist (For Your System)

### When to Add a New Block

Add a prefix/pattern if you see:
1. **High volume markets with zero edge** (10,000+ contracts but edge always < 2%)
2. **Systematic false positives** (Claude estimates high confidence but markets are noise)
3. **Toxic spreads** (spreads > 3 cents on median markets)

**Example:** You notice KXSPORTS-XYZ markets have average 8,000 contracts but edges averaging 0.5%. Add "KXSPORTS" to blocklist.

### When to Remove a Block

Remove a prefix/pattern if:
1. You find consistent tradeable edges despite blocklist rationale
2. Recent market changes (e.g., improved liquidity, tighter spreads)
3. New information sources make category analyzable (e.g., sports ML model added)

**Example:** If you build a sports-specific estimator, consider removing sports token blocking.

### Category-Specific Allowlists

Kalshalyst uses allowlist (only specified categories pass) rather than blocklist:

```python
_ALLOWED_CATEGORIES = {
    "politics", "policy", "government", "election",
    "economics", "macro", "fed", "regulation",
    "crypto", "finance", "technology", "ai", "geopolitics"
}
```

Modify this if you want to specialize:
- **Political focus only:** `{"politics", "government", "election"}`
- **Macro-only:** `{"economics", "macro", "fed", "policy"}`
- **Crypto-only:** `{"crypto", "blockchain", "finance"}`

## Performance Impact

### Typical Filter Results (50,000 raw markets)

```
Raw markets from API:        5,000
After ticker prefix block:   3,200 (-36%)
After category API block:    2,100 (-34%)
After micro-timeframe:       1,950 (-10%)
After volume floor:          900 (-54%)
After timeframe gates:       450 (-50%)

Final: 9% pass all filters (90% noise removed)
```

### Speed Impact

Blocklist checks are fast (< 10ms for 5,000 markets):
- Ticker prefix check: O(n) where n = number of prefixes (~15)
- Category slug check: O(1) set lookup
- Micro-timeframe check: O(p) where p = patterns (~10)

Total: ~50-100 microseconds per market.

## Common Misses

### Sports Markets (Intentional)

If you're seeing sports markets in output, they're tagged `is_sports: true` but not filtered:

```json
{
  "ticker": "NFLSB-2026-KC",
  "title": "Will Kansas City Chiefs win Super Bowl 2026?",
  "is_sports": true,
  ...
}
```

To filter them in downstream processing:
```python
non_sports = [m for m in markets if not m.get('is_sports')]
```

### Micro-Timeframe Markets That Slip Through

Sometimes Kalshi markets use different phrasing:
- "within next hour" (catches "next hour" ✓)
- "before 3pm" (no pattern match ✗ — add if seen)
- "settle by close" (no pattern match ✗ — add if seen)

If you see false negatives, add patterns:
```python
_MICRO_TIMEFRAME_PATTERNS = {
    ...,
    "before ", "by end of day", "settle by close"
}
```

### Entertainment Markets Using Allowed Categories

Rare edge case: "Will Taylor Swift attend the Golden Globes?" might be tagged "entertainment" (blocked) OR "celebrity" (blocked) OR "events" (not on blocklist).

Solution: Use title text matching as secondary layer:

```python
if any(term in title.lower() for term in ["grammy", "oscar", "golden globe", "nfl draft"]):
    return True  # Block, even if category allows
```

## Maintenance Checklist

### Monthly

- [ ] Check Kalshi category slugs for new categories
- [ ] Review top 10 blocked markets — still noise?
- [ ] Run Brier report, check for systematic miscalibration (might indicate blocklist is wrong)

### Quarterly

- [ ] Audit `_BLOCKED_TICKER_PREFIXES` for new patterns
- [ ] Review any low-edge markets that passed — should they be blocked?
- [ ] Tune sports token list if you have sports-specific models

### Annually

- [ ] Full blocklist audit — what's changed in Kalshi API?
- [ ] Update documentation
- [ ] Archive old performance metrics
