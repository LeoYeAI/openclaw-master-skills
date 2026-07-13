# Kalshi Command Center — Market Blocklist

Complete reference for market filtering in the live scan command.

## Blocklist Purpose

The scanner automatically filters out categories and ticker prefixes that:
- Lack information-efficient pricing (entertainment, sports)
- Are irrational/unhedgeable (celebrity deaths, weather)
- Have low trading volume or institutional interest
- Contain harmful content

Filters apply to both `scan` (default) and `scan sports` commands.

## Ticker Prefix Blocklist

These prefixes are excluded from all scans:

### Weather Markets
| Prefix | Examples |
|--------|----------|
| `KXHIGH` | High temperature predictions |
| `KXLOW` | Low temperature predictions |
| `KXRAIN` | Rainfall predictions |
| `KXSNOW` | Snow predictions |
| `KXTEMP` | Temperature general |
| `KXWIND` | Wind speed predictions |
| `KXWEATH` | Weather general (catch-all) |

**Rationale**: Weather is data-driven but lacks stable APIs; predictions are noisy and affected by forecast model drift.

### Index & Futures Markets
| Prefix | Examples |
|--------|----------|
| `INX` | Index contracts |
| `NASDAQ` | NASDAQ futures |
| `FED-MR` | Federal Reserve meetings |

**Rationale**: These are infrastructure markets with low utility for directional traders; best served by CME or CBOT.

### Entertainment Markets
| Prefix | Examples |
|--------|----------|
| `KXCELEB` | Celebrity gossip |
| `KXMOVIE` | Movie releases |
| `KXYT` | YouTube metrics |

**Rationale**: Driven by publicity & memes, not fundamentals. Highly volatile and hard to model.

### Social Media Markets
| Prefix | Examples |
|--------|----------|
| `KXTWIT` | Twitter/X metrics |
| `KXSTREAM` | Streaming service metrics |
| `KXTIKTOK` | TikTok metrics |

**Rationale**: Platform metrics are proprietary & gamed by influencers. Poor signal.

## Category Blocklist

These categories are excluded from default scans:

| Category | Sports Filter | Rationale |
|----------|----------------|-----------|
| `weather` | Excluded | Low information efficiency |
| `climate` | Excluded | Long-term, non-tradeable for short-term |
| `entertainment` | Excluded | Irrational & meme-driven |
| `sports` | **Excluded** from default, **Included** in `scan sports` | Requires specialized knowledge; excluded by default to focus on macro |
| `social-media` | Excluded | Platform-gamed metrics |
| `streaming` | Excluded | Entertainment subcategory |
| `celebrities` | Excluded | Unhedgeable, meme-driven |

### Category Matching

Categories from Kalshi API may include:
- `market.category` field (primary)
- `market.series_ticker` field (fallback, for sub-categories)

Both are normalized to lowercase and matched against blocklist.

## Sports Token Blocklist

When `scan` (default) is used, these keywords in market title or ticker trigger exclusion:

### Professional Sports Leagues

```
"nfl", "nba", "mlb", "nhl", "mls", "ncaa",
"pga", "ufc", "wwe"
```

Examples:
- "Will the Warriors win the Finals?"
- "NFL MVP voting"
- "NCAA March Madness winner"

### Events & Championships

```
"super bowl", "superbowl", "march madness", "world series",
"stanley cup", "finals", "playoff", "mvp", "heisman"
```

Examples:
- "Super Bowl MMXXVI winner"
- "2026 World Series champion"
- "Stanley Cup Finals result"

### Sports Terminology

```
"rushing", "passing", "touchdown", "home run", "strikeout",
"quarterback", "pitcher", "espn", "sports"
```

Examples:
- "Will player achieve 1000 rushing yards?"
- "Total strikeouts this season"
- "ESPN March Madness bracket"

### Esports & Gaming

```
"valorant", "league of legends", "counter-strike", "dota",
"overwatch", "fortnite", "call of duty", "esports", "e-sports"
```

Examples:
- "Valorant Champions 2026 winner"
- "League of Legends Worlds champion"
- "CS:GO Major tournament"

### Tennis & Racquet Sports

```
"atp", "wta", "tennis", "match:", "vs.", "round of"
```

Examples:
- "Wimbledon champion 2026"
- "ATP Finals winner"
- "WTA rankings leader"

### Combat Sports

```
"boxing", "mma", "bellator", "formula 1", "f1 ", "nascar", "indycar"
```

Examples:
- "Olympic boxing medal count"
- "UFC heavyweight champion"
- "Formula 1 world champion 2026"

## Enabling Sports Markets

To include sports in scan:

```bash
python kalshi_commands.py scan sports
```

This:
1. **Reverses sports filter**: Markets with sports keywords are ONLY included
2. **Keeps other blocklists active**: Still filters out weather, entertainment, etc.
3. **Returns sports-specific insights**: "Will Lakers win NBA Finals?" etc.

Example output:
```
🏀 Sports Scan — 600 markets scanned, 18 passed filters:

1. Will Lakers win the 2026 NBA Finals?
   45¢/47¢ (spread 2¢ = 4.5%) | vol 892 | OI 3,456 | 120d
   Score: 71.2 | NBA-FINALS-2026
```

## Volume Filter

All scans exclude markets with total volume < 10 contracts.

**Rationale**: Very low volume markets have:
- Stale/uninformed pricing
- High bid-ask spreads (>10%)
- Difficulty executing even small orders

Markets must show recent trading activity to be actionable.

## Timeframe Filter

Scans only include markets with 7-180 days to expiration.

| Days to Close | Status | Rationale |
|---------------|--------|-----------|
| < 7d | ❌ Excluded | Too little time; sharp gamma from certainty |
| 7-180d | ✅ Included | Sweet spot for directional trading |
| > 180d | ❌ Excluded | Too long; thesis may invalidate; illiquid |

**Examples**:
- "Will US inflation exceed 4% by June 2026?" (60d) → ✅ Included
- "Will Tesla break $500 by end of March?" (7d) → ✅ Included
- "Which party wins 2028 presidential election?" (1000d) → ❌ Excluded (too long)
- "Will inflation drop below 3% this week?" (2d) → ❌ Excluded (too short)

## Spread Filter

Markets are excluded if spread ≥ 20% of mid-price.

| Spread % | Example | Status |
|----------|---------|--------|
| 0% | 35¢ bid/ask | ✅ Perfect |
| 2-5% | 35¢/37¢ | ✅ Good |
| 5-10% | 35¢/40¢ | ✅ Acceptable |
| 10-20% | 35¢/45¢ | ⚠️ Wide |
| > 20% | 35¢/55¢ | ❌ Excluded |

**Rationale**: Wide spreads indicate illiquidity or information asymmetry. Hard to execute at reasonable prices.

## Liquidity Scoring

Heuristic scoring (detailed in [scoring.md](scoring.md)) includes liquidity component:

```
liq_score = log(1 + volume) * 0.6 + log(1 + oi) * 0.4
```

Log-scaling prevents mega-markets from dominating results. Markets with both:
- High volume (recent trades)
- High open interest (large positions)

...score highest and rank first in results.

## Customization

To override blocklists, edit `kalshi_commands.py`:

```python
# Line ~170-180 in scan_command()
blocked_prefixes = {
    # Add/remove prefixes here
}

blocked_categories = {
    # Add/remove categories here
}

sports_tokens = {
    # Add/remove keywords here
}
```

Then reinstall:

```bash
cp kalshi_commands.py ~/.openclaw/scripts/  # or wherever you use it
```

### Example: Include Weather Markets

```python
blocked_prefixes = {
    # "KXHIGH", "KXLOW", "KXRAIN", "KXSNOW", "KXTEMP", "KXWIND",  # REMOVED
    # "KXWEATH",  # REMOVED
    "INX", "NASDAQ", "FED-MR", "KXCELEB", "KXMOVIE",
    "KXTIKTOK", "KXYT", "KXTWIT", "KXSTREAM",
}
```

### Example: Sports-Only Mode

```python
# In scan_command(), replace entire sports_tokens with:
if query == "sports":
    # Only include sports
    is_sport = any(tok in combined for tok in sports_tokens)
    if not is_sport:
        continue
else:
    # Default: exclude sports
    is_sport = any(tok in combined for tok in sports_tokens)
    if is_sport:
        continue
```

## Market Status Filter

Only `status == "open"` markets are included in scans.

| Status | Included? | Meaning |
|--------|-----------|---------|
| `open` | ✅ Yes | Market active, can trade |
| `closed` | ❌ No | Market closed (timed out or manually) |
| `settled` | ❌ No | Outcome resolved, no more trading |
| `paused` | ❌ No | Temporarily paused (e.g., API issues) |

## Order Book Quality

Markets are excluded if:
- `yes_bid == 0` or `yes_bid is null` → No buyers on YES side
- `yes_ask == 0` or `yes_ask is null` → No sellers on YES side

Both sides must have functioning bids/asks.

**Example**: If a market shows `yes_bid=0, yes_ask=35`, it's excluded (no YES buyers = cannot sell YES into the order book).

## Error Handling

If blocklist filtering returns 0 markets:

```bash
python kalshi_commands.py scan
# ❌ No actionable markets right now. All filtered out by spread/volume/timeframe.
```

Try:
1. **Loosen timeframe**: Markets closing soon (< 7d) or far out (> 180d)
2. **Check category filters**: May be excluding macro/econ markets
3. **Use sports filter**: If sports markets are higher quality
4. **Check volume**: No recent trading on open markets
5. **Verify API**: Kalshi may be down or in maintenance

## Bypass (Advanced)

To scan ALL markets without any filtering:

```python
# In kalshi_commands.py, comment out all filter checks:

# if any(ticker_upper.startswith(p) for p in blocked_prefixes):
#     continue
# if category and category.lower().strip() in blocked_categories:
#     continue
# if is_sport and not include_sports:
#     continue
```

Then rebuild scoring without filters. Use with caution — results will be noisy.

## References

- **Kalshi API Categories**: https://kalshi.com/api/documentation
- **Market Status Codes**: Check Kalshi UI for live examples
- **Blocklist Rationale**: See [SKILL.md](../SKILL.md) "Market Filtering" section
