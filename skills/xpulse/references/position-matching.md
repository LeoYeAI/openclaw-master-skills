# Position Matching — Signal-to-Kalshi Position Alignment

## Purpose

Stage 3 filters signals to match only active Kalshi positions. This prevents alerts about market-moving events that don't affect your portfolio.

**Philosophy:** Only alert about signals that matter to YOUR trading.

---

## Keyword Extraction

### From Kalshi Position

Each active position contributes keywords extracted from:
- **Ticker** (e.g., `TRUMP-TARIFF-2025`)
- **Market title** (e.g., `Will Trump enact 25% tariffs on steel by 2025?`)
- **Event ticker** (if present)

### Algorithm

```python
keywords = set()
for field in [ticker, title, event_ticker]:
    for word in field.lower().replace("-", " ").replace("_", " ").split():
        if len(word) > 2:  # Minimum 3 characters
            keywords.add(word)
```

### Example

**Position 1:**
- Ticker: `TRUMP-TARIFF-2025`
- Title: `Will Trump enact steel tariffs?`
- Keywords: {trump, tariff, 2025, steel, enact, will}

**Position 2:**
- Ticker: `FED-RATE-HOLD-JUN`
- Title: `Will the Fed hold rates in June?`
- Keywords: {fed, rate, hold, jun, will, the} → {fed, rate, hold, jun}

(Stop words "will", "the" typically have >2 char threshold, so excluded)

---

## Signal-Position Matching

### From Signal

Keywords extracted from:
- **Topic** (e.g., `Trump tariff`)
- **Summary** (e.g., `Trump announces 25% steel tariffs`) — only words >3 chars

```python
signal_topic = signal.get("topic", "").lower()
signal_summary = signal.get("summary", "").lower()
signal_words = set(signal_topic.replace("-", " ").replace("_", " ").split())
signal_words |= set(w for w in signal_summary.split() if len(w) > 3)
```

### Match Logic

```python
def _signal_matches_position(signal: dict, positions: list) -> dict:
    """Check if signal matches any position. Returns matched position or None."""
    signal_words = extract_signal_keywords(signal)

    best_match = None
    best_overlap = 0

    for pos in positions:
        overlap = len(signal_words & pos["keywords"])
        if overlap >= 2 and overlap > best_overlap:  # 2+ keyword overlap required
            best_overlap = overlap
            best_match = pos

    return best_match
```

**Requirements:**
- Minimum 2 keywords must overlap
- Returns best match (highest overlap count)
- Returns None if no match

---

## Example Matchings

### Match 1: Direct Topic Alignment ✓

**Signal:**
- Topic: `Trump tariff`
- Summary: `Trump announces 25% steel tariffs`
- Words: {trump, tariff, announces, steel, tariffs}

**Position:**
- Ticker: `TRUMP-TARIFF-2025`
- Title: `Will Trump enact steel tariffs?`
- Keywords: {trump, tariff, 2025, steel, enact}

**Overlap:** {trump, tariff, steel} = 3 words ✓ **MATCH**

---

### Match 2: Indirect Alignment ✓

**Signal:**
- Topic: `Fed decision`
- Summary: `Fed holds rates steady as inflation cools`
- Words: {holds, rates, steady, inflation, cools}

**Position:**
- Ticker: `FED-RATE-HOLD-JUN`
- Title: `Will the Fed hold rates in June?`
- Keywords: {fed, rate, hold, jun}

**Overlap:** {hold} = 1 word ✗ **NO MATCH** (needs 2+)

---

### Match 3: Weak Signal, Strong Position Context ✓

**Signal:**
- Topic: `tariff`
- Summary: `Trump extends tariff policy`
- Words: {trump, extends, tariff, policy}

**Position:**
- Ticker: `TRUMP-TARIFF-2025`
- Title: `Will Trump enact steel tariffs by 2025?`
- Keywords: {trump, tariff, 2025, steel, enact}

**Overlap:** {trump, tariff} = 2 words ✓ **MATCH**

---

### No Match: Unrelated Event ✗

**Signal:**
- Topic: `UK election`
- Summary: `UK Labour party gains in polls`
- Words: {labour, party, gains, polls}

**Position:**
- Ticker: `TRUMP-TARIFF-2025`
- Keywords: {trump, tariff, 2025, steel}

**Overlap:** {} = 0 words ✗ **NO MATCH**

---

### Match 4: Semantic Alignment with Synonyms

**Signal:**
- Topic: `inflation data`
- Summary: `CPI rises faster than expected`
- Words: {inflation, data, cpi, rises, faster, expected}

**Position 1:**
- Ticker: `CPI-Q1-2026`
- Keywords: {cpi, q1, 2026}

**Overlap:** {cpi} = 1 word ✗ **NO MATCH**

**Position 2:**
- Ticker: `INFLATION-STICKY-2026`
- Title: `Will inflation stay above 3% through 2026?`
- Keywords: {inflation, sticky, 2026, stay, will, above}

**Overlap:** {inflation} = 1 word ✗ **NO MATCH**

**Note:** This signal wouldn't match either position (both only 1-word overlap).
This is intentional — it prevents false positives on related-but-not-directly-relevant signals.

---

## Position State

### Fetching Active Positions

```python
def _get_active_kalshi_topics() -> list:
    """Fetch unsettled Kalshi positions and extract keywords."""
    client = _get_client()  # Kalshi API
    resp = client.call_api(
        "GET",
        "https://api.elections.kalshi.com/trade-api/v2/portfolio/positions?limit=100&settlement_status=unsettled"
    )
    data = json.loads(resp.read())
    positions = data.get("market_positions", [])

    topics = []
    for pos in positions:
        ticker = pos.get("ticker", "")
        title = pos.get("market_title", "")
        event_ticker = pos.get("event_ticker", "")

        keywords = extract_keywords(ticker, title, event_ticker)

        topics.append({
            "ticker": ticker,
            "title": title,
            "keywords": keywords,
            "side": pos.get("side", ""),  # "yes" or "no"
            "quantity": pos.get("total_traded", 0),
        })

    return topics
```

### Caching

Positions are fetched fresh on every run (no caching). This ensures:
- Recently closed positions don't trigger alerts
- New positions immediately start matching signals
- No stale state

---

## Silent Suppression

Signals that fail to match any position are logged silently:

```python
for s in signals:
    match = _signal_matches_position(s, kalshi_positions)
    if not match:
        silent_signals.append(s)

state["last_x_signals_silent"] = [
    {"topic": s["topic"], "summary": s["summary"][:80], "confidence": s["confidence"]}
    for s in silent_signals
]
```

These are:
1. **Logged to console** (DEBUG output)
2. **Stored in state** (accessible programmatically)
3. **Cached** (available in `.x_signal_cache.json` for morning brief)
4. **Not sent to iMessage** (silent)

---

## Alert Output

Signals passing all 3 stages are formatted for iMessage:

```
⚠️ X signal — affects your Kalshi positions:

  📈 Trump tariff: Trump announces 25% steel tariffs (82% conf) [TRUMP-TARIFF-2025]
  📉 Inflation: Core CPI sticky, Fed unlikely to cut (75% conf) [FED-RATE-2026]
  ➡️  Ukraine: Peace talks accelerate, settlement rising (68% conf) [UKRAINE-2026]
```

**Format per signal:**
- Icon (📈/📉/➡️ based on direction)
- Topic + summary (first 80 chars)
- Confidence (percentage)
- Matched position ticker

Max 3 signals per message (sorted by confidence, highest first).

---

## Configuration

### Enable/Disable

```yaml
xpulse:
  position_gate: true   # Default: enable matching
```

### Testing Without Positions

To test signal detection without active Kalshi positions:

```yaml
xpulse:
  position_gate: false   # Skip Stage 3, alert all materiality-filtered signals
```

**Warning:** This will alert you to all X signals about your topics, even ones not related to your positions. Recommended for debugging only.

---

## Performance

- **Runtime:** ~1 second (fetch positions + keyword matching)
- **API call:** 1 Kalshi API call (positions list)
- **Cost:** $0 (free Kalshi read-only)

---

## Failure Modes

### No Active Positions

```python
if not kalshi_positions:
    _log("X scanner: no active Kalshi positions — all signals suppressed (logged only)")
    return False
```

All signals are silently suppressed. Logged in state, cached, but not alerted.

**Behavior:** Safe silence when portfolio is empty.

### Kalshi API Error

```python
except Exception as e:
    _log(f"Kalshi position gate error: {e}")
    return []  # Fail closed — don't send if we can't verify positions
```

If position fetch fails (API down, credentials invalid), all signals are suppressed.

**Behavior:** Better to miss signals than send alerts without position context.

---

## Integration with Morning Brief

Position matches are cached with metadata:

```json
{
  "signals": [
    {
      "topic": "Trump tariff",
      "confidence": 0.82,
      "direction": "bearish",
      "summary": "Trump announces 25% steel tariffs",
      "matched_position": "TRUMP-TARIFF-2025",
      "position_side": "yes"
    },
    {
      "topic": "tariff",
      "confidence": 0.68,
      "summary": "Trump discusses additional tariffs",
      "matched_position": null,
      "suppressed_reason": "no matching position"
    }
  ]
}
```

Morning brief can show both:
- Signals that alerted (matched positions)
- Signals that were suppressed (no match)
