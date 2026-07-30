# Materiality Gate — Signal Deduplication System

## Purpose

The materiality gate filters Stage 1 signals to prevent notification fatigue. It answers: **"Is this a genuinely NEW development, or just noise about something the user already knows?"**

## Design Philosophy

**Fail-Closed:** If the filter breaks (Ollama timeout, parse error), drop ALL signals rather than spam the user. A missed signal is acceptable; false positives are not.

---

## The 48-Hour Rolling Window

### Data Structure

Signal history is stored in `.openclaw/state/x_signal_history.json`:

```json
[
  {
    "topic": "tariff",
    "summary": "Trump announces 25% steel tariffs",
    "direction": "bearish",
    "confidence": 0.82,
    "matched_position": "TRUMP-TARIFF-2025",
    "timestamp": 1709987400.0
  },
  {
    "topic": "inflation",
    "summary": "Core CPI stays sticky at 3.2%",
    "direction": "neutral",
    "confidence": 0.75,
    "timestamp": 1709983800.0
  }
]
```

### Pruning

- **Max entries:** 200 (auto-trimmed, oldest first)
- **Time window:** 48 hours from current time
  ```python
  cutoff = time.time() - 48 * 3600
  history = [h for h in history if h["timestamp"] > cutoff]
  ```
- **Result:** History never grows unbounded, always reflects recent context

---

## Filter Algorithm

### Input

```
Stage 1 candidates (pre-filter):
[
  {"topic": "Trump tariff", "summary": "New 25% steel tariff announced", "confidence": 0.82},
  {"topic": "tariff", "summary": "Trump discusses additional tariffs", "confidence": 0.68},
  {"topic": "inflation", "summary": "Core CPI sticky, Fed won't cut", "confidence": 0.79},
]

History (last 48h alerts):
[
  {"topic": "tariff", "summary": "Trump announces 25% steel tariffs", "timestamp": 3h ago},
  {"topic": "Fed rate", "summary": "Fed signals no near-term cuts", "timestamp": 6h ago},
]
```

### Process

1. **Build context blocks** for Qwen
   - Recent alerts block (what user already knows)
   - Candidate signals block (what's new)

2. **Call Qwen Stage 2 prompt:**
   ```
   You are a personal alert filter for a prediction market trader.
   Your job is to PREVENT notification fatigue.

   RECENTLY SENT ALERTS:
   - [3h ago] tariff: Trump announces 25% steel tariffs
   - [6h ago] Fed rate: Fed signals no near-term cuts

   CANDIDATE NEW SIGNALS:
   - [Trump tariff] New 25% steel tariff announced (conf: 82%, bearish)
   - [tariff] Trump discusses additional tariffs (conf: 68%, bearish)
   - [inflation] Core CPI sticky, Fed won't cut (conf: 79%, neutral)

   RULES:
   - REJECT if same story as recent alert (even different wording)
   - REJECT if ongoing background noise
   - REJECT if no concrete new event
   - ACCEPT only if genuinely new development or significant escalation
   - When in doubt, REJECT.

   Respond: {"keep": [topic strings to keep], "reasoning": "..."}
   ```

3. **Parse response:**
   ```python
   parsed = json.loads(qwen_output)
   keep_topics = set(parsed.get("keep", []))
   # Result: {"keep": ["inflation"], "reasoning": "New CPI data unknown to user..."}
   ```

4. **Filter:**
   ```python
   filtered = [s for s in candidates if s["topic"] in keep_topics]
   # Returns: [{"topic": "inflation", ...}]
   ```

---

## Example Filtering Scenarios

### Scenario 1: Repeat Alert (REJECT)

**Candidate:** `{"topic": "tariff", "summary": "Trump discusses additional tariffs"}`

**History:** `{"topic": "tariff", "summary": "Trump announces 25% steel tariffs", 2h ago}`

**Qwen Decision:**
```
REJECT: Same story as recent alert. "Trump discusses tariffs" is ongoing commentary
about the steel tariff announcement from 2 hours ago. No new concrete development.
```

**Reasoning:** Noise — user already knows about tariff story

---

### Scenario 2: Genuine Escalation (ACCEPT)

**Candidate:** `{"topic": "tariff", "summary": "Trump extends tariffs to EU, Canada, Mexico"}`

**History:** `{"topic": "tariff", "summary": "Trump announces 25% steel tariffs", 5h ago}`

**Qwen Decision:**
```
ACCEPT: Significant escalation. Original alert was steel tariffs only.
This signal reports tariffs extended to additional trading partners and regions.
Concrete new development.
```

**Reasoning:** Material change — expansion beyond original announcement

---

### Scenario 3: Background Noise (REJECT)

**Candidate:** `{"topic": "inflation", "summary": "Inflation debate continues on Wall Street"}`

**History:**
- `{"topic": "inflation", "summary": "Core CPI released at 3.2%", 4h ago}`
- `{"topic": "inflation", "summary": "Fed signals rate hold", 6h ago}`

**Qwen Decision:**
```
REJECT: Background noise. "Inflation debate continues" is generic commentary.
User already knows about CPI release and Fed position. No new data, announcement,
or concrete development.
```

**Reasoning:** Ongoing background chatter, not material

---

### Scenario 4: New Data Release (ACCEPT)

**Candidate:** `{"topic": "inflation", "summary": "PCE inflation beats expectations, 2.8% vs 3.1% forecast"}`

**History:**
- `{"topic": "inflation", "summary": "Core CPI released at 3.2%", 4h ago}`
- `{"topic": "inflation", "summary": "Fed signals rate hold", 6h ago}`

**Qwen Decision:**
```
ACCEPT: Concrete new development. PCE data is different from CPI data released earlier.
Beats market expectations (2.8% vs 3.1% forecast). Material market-moving event.
```

**Reasoning:** New economic data, unexpected direction

---

### Scenario 5: Speculation (REJECT)

**Candidate:** `{"topic": "Ukraine", "summary": "Experts suggest peace talks could happen in Q2"}`

**History:** `{"topic": "Ukraine", "summary": "Peace negotiations underway", 3h ago}`

**Qwen Decision:**
```
REJECT: Pure speculation. "Experts suggest... could happen" is commentary and prediction,
not a concrete event. User already knows negotiations are underway.
No new announcement, decision, or development.
```

**Reasoning:** Speculation vs. hard news

---

## Fail-Closed Behavior

### When Qwen Fails

```python
if result.returncode != 0:
    _log("Stage 2 filter: Qwen failed, dropping all signals (fail-closed)")
    return []  # Fail closed — silence over noise when filter is broken
```

**Trigger points:**
- Ollama timeout (>45 seconds)
- Ollama not running
- Qwen crashes or returns unparseable JSON
- Network error

**Action:** Drop ALL candidate signals, log nothing

**Philosophy:** One missed signal is better than 5 false alerts when the system breaks

---

## Configuration

In `config.yaml`:

```yaml
xpulse:
  materiality_gate: true    # Enable/disable filtering
  max_history_entries: 200  # Cap on history size
```

### Disabling (For Testing/Debugging)

```yaml
xpulse:
  materiality_gate: false   # All Stage 1 candidates pass to Stage 3
```

**Warning:** This will increase alert frequency. Only for debugging.

---

## Performance Impact

- **Stage 2 runtime:** 30-45 seconds per run (Qwen LLM call)
- **Network:** 1 call to local Ollama
- **Cost:** $0 (local inference)

---

## Integration with Morning Brief

The full Stage 1 cache (pre-materiality) is stored separately:

```json
{
  "signals": [
    {"topic": "tariff", "confidence": 0.82, ...},    // sent to iMessage
    {"topic": "tariff", "confidence": 0.68, ...},    // filtered out
    {"topic": "inflation", "confidence": 0.79, ...}  // sent to iMessage
  ],
  "timestamp": 1709990400.0
}
```

Morning brief can consume this cache to show:
- What was alerted
- What was filtered (and why)
- Full context of X scanning activity
