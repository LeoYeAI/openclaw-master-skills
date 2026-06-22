# Market Morning Brief — Integration Guide

This document explains how Market Morning Brief integrates with other OpenClaw skills and how to extend it.

## Design: Cache-Based Integration

Instead of calling other skills' APIs directly, Market Morning Brief uses **cache files** as the integration mechanism:

```
Kalshalyst → writes → .kalshi_research_cache.json
Arbiter    → writes → .crossplatform_divergences.json
Xpulse     → writes → .x_signal_cache.json

↓ (brief reads)

Market Morning Brief → consolidates → morning_brief.txt
```

**Why?**
- **Resilience:** If skill fails, cache persists. Brief still shows stale data rather than nothing.
- **Independence:** Market Morning Brief doesn't depend on other skills running at exact times.
- **Speed:** Reading JSON is <100ms. No API calls needed.
- **Upgrade path:** User can install skills independently. Brief adapts as they add skills.

---

## Cache File Schemas

### 1. Kalshalyst Cache

**File:** `state/.kalshi_research_cache.json`

**Written by:** Kalshalyst skill after every edge scanner run

**Write interval:** Every 60 minutes (configurable)

**Schema:**
```json
{
  "insights": [
    {
      "ticker": "POTUS-2028-DEM",
      "title": "Will a Democrat win the 2028 presidential election?",
      "side": "NO",
      "yes_bid": 45,
      "yes_ask": 51,
      "volume": 2500,
      "open_interest": 8000,
      "days_to_close": 672,
      "edge_type": "claude_contrarian",
      "spread_capture_cents": 6,
      "spread_pct": 6.6,
      "market_prob": 0.48,
      "estimated_prob": 0.38,
      "edge_pct": 14.0,
      "effective_edge_pct": 14.0,
      "direction": "overpriced",
      "reasoning": "Market overweighting base rate without pricing recent policy momentum...",
      "confidence": 0.72,
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

**Fields used by brief:**
- `insights[].ticker` — Market identifier
- `insights[].market_prob` — Current market price (decimal, 0.0-1.0)
- `insights[].estimated_prob` — Claude's estimate
- `insights[].edge_pct` — Edge percentage
- `insights[].confidence` — Confidence (0.0-1.0)
- `cached_at` — Timestamp for freshness check

**Reading logic:**
```python
import json
from pathlib import Path

def read_kalshalyst_cache(cache_path):
    try:
        with open(cache_path) as f:
            data = json.load(f)

        # Check freshness
        cached_at = data.get("cached_at")
        age_seconds = (datetime.now() - datetime.fromisoformat(cached_at)).total_seconds()
        if age_seconds > 7200:  # 2 hours
            return None  # Too stale

        return data.get("insights", [])[:3]  # Top 3
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None
```

---

### 2. Prediction Market Arbiter Cache

**File:** `state/.crossplatform_divergences.json`

**Written by:** Prediction Market Arbiter skill periodically

**Write interval:** Every 4 hours (configurable)

**Schema:**
```json
{
  "divergences": [
    {
      "ticker": "UKRAINE-2026-NO",
      "title": "Will the war in Ukraine be ongoing in 2026?",
      "kalshi_price": 0.28,
      "kalshi_bid": 27,
      "kalshi_ask": 29,
      "kalshi_volume": 1200,
      "polymarket_price": 0.31,
      "polymarket_bid": 30,
      "polymarket_ask": 32,
      "polymarket_volume": 850,
      "spread_cents": 3,
      "spread_pct": 10.7,
      "volume_difference_pct": 12,
      "opportunity": "Arbitrage: Buy Kalshi @ 28¢, Sell PM @ 31¢"
    }
  ],
  "last_update": "2026-03-08T14:00:00+00:00",
  "scanner_version": "1.0.0",
  "cached_at": "2026-03-08T15:00:00+00:00"
}
```

**Fields used by brief:**
- `divergences[].ticker` — Market identifier
- `divergences[].kalshi_price` — Kalshi price (decimal)
- `divergences[].polymarket_price` — Polymarket price (decimal)
- `divergences[].spread_cents` — Spread in cents
- `cached_at` — Timestamp for freshness check

**Reading logic:**
```python
def read_arbiter_cache(cache_path):
    try:
        with open(cache_path) as f:
            data = json.load(f)

        # Check freshness (6 hour tolerance for divergences)
        cached_at = data.get("cached_at")
        age_seconds = (datetime.now() - datetime.fromisoformat(cached_at)).total_seconds()
        if age_seconds > 21600:  # 6 hours
            return None

        # Sort by spread, take top 2
        divs = data.get("divergences", [])
        divs.sort(key=lambda x: x.get("spread_cents", 0), reverse=True)
        return divs[:2]
    except (FileNotFoundError, json.JSONDecodeError):
        return None
```

---

### 3. Xpulse Cache

**File:** `state/.x_signal_cache.json`

**Written by:** Xpulse skill (social signal analyzer)

**Write interval:** Every 2 hours (configurable)

**Schema:**
```json
{
  "signals": [
    {
      "signal": "Fed rate cut odds +5%",
      "category": "macroeconomics",
      "confidence": 0.78,
      "reach": 8200,
      "source_count": 3,
      "timestamp": "2026-03-07T15:30:00Z",
      "topics": ["fed", "interest-rates", "inflation"],
      "sources": [
        {
          "username": "bloomberg",
          "followers": 4200000,
          "engagement": 2300
        }
      ]
    },
    {
      "signal": "Ukraine ceasefire talks escalating",
      "category": "geopolitics",
      "confidence": 0.72,
      "reach": 5100,
      "source_count": 2,
      "timestamp": "2026-03-07T14:15:00Z",
      "topics": ["ukraine", "peace", "geopolitics"]
    }
  ],
  "scan_version": "2.0.0",
  "cached_at": "2026-03-08T16:00:00+00:00"
}
```

**Fields used by brief:**
- `signals[].signal` — Signal text
- `signals[].confidence` — Confidence (0.0-1.0)
- `signals[].reach` — Approximate reach (follower count or engagement)
- `signals[].timestamp` — When signal was detected
- `cached_at` — Timestamp for freshness check

**Reading logic:**
```python
def read_xpulse_cache(cache_path):
    try:
        with open(cache_path) as f:
            data = json.load(f)

        # Filter to last 24 hours
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=24)

        signals = []
        for sig in data.get("signals", []):
            ts = datetime.fromisoformat(sig.get("timestamp", ""))
            if ts > cutoff:
                signals.append(sig)

        # Check cache freshness
        cached_at = data.get("cached_at")
        age_seconds = (datetime.now() - datetime.fromisoformat(cached_at)).total_seconds()
        if age_seconds > 14400:  # 4 hours
            return None

        # Sort by confidence, take top 2
        signals.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        return signals[:2]
    except (FileNotFoundError, json.JSONDecodeError):
        return None
```

---

## Cache Directory Structure

Typical OpenClaw skill structure:

```
market-morning-brief/
├── SKILL.md
├── scripts/
│   ├── morning_brief.py
│   └── evening_brief.py
├── references/
│   ├── sections.md
│   └── integration.md
└── state/                    # Created at runtime
    ├── .kalshi_research_cache.json (written by Kalshalyst)
    ├── .crossplatform_divergences.json (written by Arbiter)
    └── .x_signal_cache.json (written by Xpulse)
```

**Cache directory:** Configurable in `config.yaml`

```yaml
cache_paths:
  kalshalyst: "/path/to/state/.kalshi_research_cache.json"
  arbiter: "/path/to/state/.crossplatform_divergences.json"
  xpulse: "/path/to/state/.x_signal_cache.json"
```

---

## Integration Points

### 1. Kalshalyst → Morning Brief

**When:** Every morning at 7:30 AM (configurable)

**Data flow:**
1. Kalshalyst runs edge scanner (hourly)
2. Writes top edges to `.kalshi_research_cache.json`
3. Morning brief reads cache at 7:30 AM
4. Displays top 3 opportunities

**User perspective:**
- Installs Kalshalyst
- Morning brief automatically shows edges (no config needed)
- Edges update every time Kalshalyst runs

**Example:**
```
Before Kalshalyst installed:
EDGES: unavailable (install Kalshalyst skill)

After Kalshalyst installed:
EDGES (Kalshalyst, top 3):
1. POTUS-2028-DEM    NO @ 38%  (+14% edge, 72% conf)
...
```

---

### 2. Prediction Market Arbiter → Morning Brief

**When:** Every morning at 7:30 AM

**Data flow:**
1. Arbiter compares Kalshi ↔ Polymarket prices (every 4h)
2. Writes divergences to `.crossplatform_divergences.json`
3. Morning brief reads cache
4. Displays biggest spreads

**User perspective:**
- Installs Arbiter
- Morning brief automatically shows divergences
- Divergences update every 4 hours (or on demand)

**Example:**
```
Before Arbiter installed:
DIVERGENCES: unavailable (install Prediction Market Arbiter)

After Arbiter installed:
DIVERGENCES (Arbiter):
UKRAINE-2026-NO    Kalshi 28% ↔ PM 31%  ($0.03 spread)
```

---

### 3. Xpulse → Morning Brief

**When:** Every morning at 7:30 AM

**Data flow:**
1. Xpulse scans X/Twitter for market signals (every 2h)
2. Writes top signals to `.x_signal_cache.json`
3. Morning brief reads cache, filters to last 24h
4. Displays top 2 signals by confidence

**User perspective:**
- Installs Xpulse
- Morning brief automatically shows X signals
- Signals refresh every 2 hours

**Example:**
```
Before Xpulse installed:
X SIGNALS: unavailable (install Xpulse)

After Xpulse installed:
X SIGNALS (last 24h):
Fed rate cut odds +5%   (78% conf, 8.2K reach)
```

---

## Extending the Brief

### Adding a New Optional Section

**Step 1:** Create cache file writer in your skill

Write to JSON with these fields:
- `data`: array of opportunities/items
- `cached_at`: ISO timestamp
- `metadata`: optional version/source info

**Step 2:** Add cache path to brief config

```yaml
cache_paths:
  my_skill: "/path/to/state/.my_skill_cache.json"

include:
  my_skill_section: true
```

**Step 3:** Add reading logic to brief script

```python
def format_my_section(cache_path):
    try:
        with open(cache_path) as f:
            data = json.load(f)

        items = data.get("data", [])[:3]
        if not items:
            return None

        lines = ["MY SECTION:"]
        for item in items:
            lines.append(f"  {item['name']}: {item['value']}")

        return "\n".join(lines)
    except FileNotFoundError:
        return "MY SECTION: unavailable (install skill)"
    except Exception as e:
        return f"MY SECTION: unavailable ({e})"
```

**Step 4:** Call in main brief builder

```python
def build_morning_brief(config):
    sections = []

    # ... existing sections ...

    if config.get("include", {}).get("my_skill_section"):
        my_section = format_my_section(config["cache_paths"]["my_skill"])
        if my_section:
            sections.append(my_section)

    return "\n\n".join(sections)
```

---

## Cache Expiration & Refresh Strategy

### Freshness Tiers

**Real-time (always fresh):**
- Polymarket API (public, called live)
- Coinbase API (called live)
- Kalshi portfolio (called live)

**Recently cached (4h tolerance):**
- Xpulse signals (updated every 2h, warn if >4h old)

**Moderately cached (6h tolerance):**
- Arbiter divergences (updated every 4h, warn if >6h old)

**Loosely cached (2h tolerance):**
- Kalshalyst edges (updated hourly, warn if >2h old)

**Implementation:**
```python
def check_cache_freshness(cache_file, max_age_seconds):
    try:
        with open(cache_file) as f:
            data = json.load(f)

        cached_at = data.get("cached_at")
        age = (datetime.now() - datetime.fromisoformat(cached_at)).total_seconds()

        if age > max_age_seconds:
            return "stale"
        return "fresh"
    except FileNotFoundError:
        return "missing"
    except Exception:
        return "error"
```

### Refresh on Demand

Users can manually refresh caches:

```bash
# Refresh Kalshalyst cache
openclaw skill run kalshalyst

# Refresh Arbiter cache
openclaw skill run market-arbiter

# Refresh Xpulse cache
openclaw skill run xpulse

# Then regenerate brief
openclaw skill run market-morning-brief
```

---

## Testing Integration

### Mock Cache Files

For testing without other skills installed:

**Create `.kalshi_research_cache.json`:**
```json
{
  "insights": [
    {
      "ticker": "TEST-EDGE-1",
      "market_prob": 0.45,
      "estimated_prob": 0.60,
      "edge_pct": 15.0,
      "confidence": 0.70
    }
  ],
  "cached_at": "2026-03-08T15:00:00+00:00"
}
```

**Then test:**
```bash
python scripts/morning_brief.py
```

Brief should display the test edge.

### Integration Test Checklist

- [ ] Brief runs without Kalshalyst → "unavailable" message
- [ ] Brief runs with Kalshalyst → shows top 3 edges
- [ ] Brief runs with Arbiter → shows divergences
- [ ] Brief runs with Xpulse → shows X signals
- [ ] Brief runs with all three → consolidates all sections
- [ ] Stale cache (>threshold) → "stale" warning
- [ ] Corrupted cache → "error" message, continues to next section
- [ ] Missing cache → "unavailable" message, continues
- [ ] Cache file deleted → brief doesn't crash, section skipped

---

## Performance Considerations

### Load Times

Typical brief generation:

| Component | Time |
|-----------|------|
| Load Kalshalyst cache | <10ms |
| Load Arbiter cache | <10ms |
| Load Xpulse cache | <10ms |
| Kalshi API (portfolio) | 100-500ms |
| Coinbase API (crypto) | 100-500ms |
| Polymarket API | 100-500ms |
| **Total** | **<2 seconds** |

### Optimization

If brief is slow:
1. Disable live API calls (Coinbase, Polymarket) if not needed
2. Run offline (cache only) for fastest execution
3. Increase API timeouts if network is slow

```yaml
market_morning_brief:
  online_mode: false  # Only read caches, skip live APIs
  api_timeout_seconds: 5  # Increase from default 3
```

---

## Troubleshooting Integration

### "Skill not found" errors

**Problem:** Brief says Kalshalyst unavailable but skill is installed

**Solution:**
1. Check cache path in config matches skill's output path
2. Ensure skill has written cache at least once: `ls -la state/.kalshi_research_cache.json`
3. Check cache is valid JSON: `python -m json.tool state/.kalshi_research_cache.json`

### Cache files not updating

**Problem:** Cache is stale (hours old)

**Solution:**
1. Manually trigger the skill: `openclaw skill run kalshalyst`
2. Check skill is scheduled: `crontab -l | grep kalshalyst`
3. Check skill logs for errors

### Brief shows wrong data

**Problem:** Cache has incorrect data

**Solution:**
1. Check cache file is being written by correct skill
2. Delete cache and let skill regenerate: `rm state/.kalshi_research_cache.json && openclaw skill run kalshalyst`
3. Verify skill configuration

---

## Future Integration Points

Potential skills to integrate with brief:

1. **Crypto futures scanner** → divergences between perpetual and spot prices
2. **Earnings calendar** → filter Kalshi markets by event schedule
3. **Macro events tracker** → link markets to scheduled economic releases
4. **Portfolio optimizer** → suggest position adjustments based on brief data
5. **Slack/Teams integration** → send brief to team channel

Each would follow the same cache-based pattern.
