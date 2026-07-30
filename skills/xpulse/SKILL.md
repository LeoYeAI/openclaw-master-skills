---
name: Xpulse
description: "Real-time X/Twitter social signal scanner for prediction market traders. Scans via DuckDuckGo (zero API cost) with two-stage local Qwen AI filtering: tradeable signal detection, then materiality gating to prevent alert fatigue. Position-aware — only alerts on signals matching your active Kalshi positions. Fail-closed design: silence over noise. Part of the OpenClaw Prediction Market Trading Stack — signals feed into Market Morning Brief and correlate with Prediction Market Arbiter divergences."
---

# Xpulse — Real-Time Social Signal Scanner

## Overview

Xpulse is a real-time X/Twitter signal scanner optimized for prediction market traders. It detects market-relevant signals on configurable topics using a three-stage intelligence pipeline:

1. **Stage 1: Signal Detection** — Scans X via DuckDuckGo (site:x.com queries), analyzes posts with local Qwen for tradeable signals
2. **Stage 2: Materiality Gate** — Compares against 48h signal history, filters out noise and repeat signals (fail-closed)
3. **Stage 3: Position Matching** — Only alerts on signals that match active Kalshi positions (keyword overlap, 2+ keywords required)

**Key philosophy:** Zero API costs (DuckDuckGo + local Qwen), fail-closed design (silence over noise), position-aware filtering (no irrelevant alerts).

## When to Use This Skill

- You're actively trading prediction markets on Kalshi
- You want real-time social signals for your active positions
- You prefer local LLM analysis over expensive API calls
- You need to prevent notification fatigue from generic social signals
- You want signals cached for morning brief consumption

## Requirements

### Python & Dependencies

- Python 3.10 or higher
- Required packages:
  ```bash
  pip install ddgs pyyaml
  ```

### Local Infrastructure

- **Ollama** (https://ollama.ai) with Qwen model
  - Install from https://ollama.ai (macOS, Linux, Windows)
  - Then: `ollama pull qwen3:latest`
  - Must be running: `ollama serve` (background process)

### Kalshi API (for position matching)

- Free Kalshi account with API credentials (https://kalshi.com)
  - API key ID
  - Private key file (ES256 format)
  - Cost: Free (read-only access to positions)

## Configuration

Create or update your `config.yaml`:

```yaml
kalshi:
  enabled: true
  api_key_id: "your-key-id"
  private_key_file: "/path/to/private.key"

ollama:
  enabled: true
  model: "qwen3:latest"
  timeout_seconds: 30

xpulse:
  enabled: true
  check_interval_minutes: 30
  topics:
    - "tariff"
    - "Ukraine"
    - "inflation"
    - "Fed rate"
    - "Trump policy"
  min_confidence: 0.7       # Stage 1: signal confidence threshold
  materiality_gate: true    # Stage 2: enable 48h deduplication
  position_gate: true       # Stage 3: only alert on matched positions
  max_history_entries: 200
```

### Topics Configuration

`topics` list should contain:
- Market-relevant keywords you're interested in
- DuckDuckGo will search: `site:x.com {topic}`
- Examples: "Trump tariff", "inflation CPI", "Fed rate", "crypto SEC", "presidential election"

### Thresholds

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `min_confidence` | 0.7 | Stage 1: Only keep signals with ≥70% AI confidence of being tradeable |
| `check_interval_minutes` | 30 | Minimum minutes between scans (prevent API hammering) |
| `materiality_gate` | true | Stage 2: Enable/disable deduplication filter |
| `position_gate` | true | Stage 3: Enable/disable Kalshi position matching |
| `max_history_entries` | 200 | Max entries in 48h signal history (auto-trimmed) |

## The Three-Stage Pipeline

### Stage 1: Signal Detection

**Input:** List of topics (e.g., ["tariff", "inflation", "Ukraine"])

**Process:**
1. For each topic, search X/Twitter via DuckDuckGo: `site:x.com {topic}`
2. Fetch up to 5 recent posts
3. Feed posts to local Qwen with this prompt:

```
You are a prediction market analyst. Given these recent X/Twitter posts about '{topic}',
determine if there's a tradeable signal.

{combined_posts}

Respond in JSON: {"has_signal": true/false, "confidence": 0.0-1.0,
"direction": "bullish/bearish/neutral", "summary": "one line"}
```

**Thresholding:** Only keep signals where:
- `has_signal == true`
- `confidence >= min_confidence` (default 0.7)

**Output:** List of candidate signals with direction + confidence

---

### Stage 2: Materiality Gate (Fail-Closed)

**Input:** Candidate signals from Stage 1 + 48h signal history

**Purpose:** Prevent alert fatigue by filtering out:
- Repeat signals about the same story (different wording)
- Ongoing background noise (tariffs in news for days)
- Speculation with no concrete new event
- Minor updates to previously alerted developments

**Process:**
1. Load recently sent signal history (last 20 alerts, 48h window)
2. Build prompt with:
   - Candidate new signals
   - What the user already knows (recent alerts)
3. Send to Qwen:

```
You are a personal alert filter for a prediction market trader.
Your job is to PREVENT notification fatigue.

RECENTLY SENT ALERTS (what the user already knows):
- [3h ago] tariff: Trump announces new steel tariffs (confidence: 0.82)
- [6h ago] inflation: Core CPI steady at 3.2% (confidence: 0.75)

CANDIDATE NEW SIGNALS:
- [tariff] Trump discusses additional tariffs (confidence: 0.68)
- [inflation] Fed signals no near-term cuts (confidence: 0.79)

RULES:
- REJECT if same story as recent alert (even different wording)
- REJECT if ongoing background noise
- REJECT if no concrete new event
- ACCEPT only if genuinely new development or significant escalation
- When in doubt, REJECT. The user prefers silence over noise.

Respond in JSON: {"keep": [list of topic strings to keep], "reasoning": "..."}
```

**Fail-Closed Design:**
- If Qwen fails (timeout, error, unparseable): **drop all signals**
- This prevents spam of uncertain signals when the filter breaks
- Better to miss a signal than spam the user

**Output:** Filtered list (subset of Stage 1 candidates)

---

### Stage 3: Position Matching Gate

**Input:** Filtered signals from Stage 2 + active Kalshi positions

**Purpose:** Only alert the user about signals that match their active positions

**Process:**
1. Fetch active Kalshi positions (unsettled)
2. Extract keywords from ticker + market title (>2 char words)
   - Example: "POTUS-2028-DEM" → keywords: {potus, 2028, dem}
3. For each signal, extract keywords from topic + summary
4. Match if 2+ keyword overlap

**Example:**
```
Signal: topic="Trump tariff", summary="Trump announces new steel tariffs"
Signal words: {trump, tariff, steel, announces, new}

Kalshi position: ticker="TRUMP-TARIFF-2025", title="Will Trump enact steel tariffs?"
Position keywords: {trump, tariff, 2025, steel, enact}

Overlap: {trump, tariff, steel} = 3 keywords ✓ MATCH
→ Signal passes to iMessage alert
```

**Suppressed Signals:**
- Signals without matching positions are logged silently
- Available in cache (`.x_signal_cache.json`) for morning brief
- Not sent to user

**Output:** Critical signals matched to positions → iMessage alert

---

## Signal Caching

All signals (pre-filter) are cached in `.x_signal_cache.json`:

```json
{
  "signals": [
    {
      "topic": "tariff",
      "confidence": 0.82,
      "direction": "bearish",
      "summary": "Trump announces new steel tariffs",
      "post_count": 3
    }
  ],
  "topics_scanned": 5,
  "timestamp": 1709990400.0
}
```

**Used for:**
- Morning brief consumption (all signals, even suppressed ones)
- On-demand signal review (what was detected but not alerted)
- Debugging signal pipeline

---

## Running Xpulse

### Command Line

```bash
# Single run
python -m xpulse.xpulse

# With full logging
DEBUG=1 python -m xpulse.xpulse

# Dry run (logs but doesn't send alerts)
python -m xpulse.xpulse --dry-run

# Force a run regardless of interval
python -m xpulse.xpulse --force
```

### Scheduled (Every 30 Minutes)

**Via OpenClaw config:**
```yaml
skills:
  xpulse:
    enabled: true
    schedule: "*/30 * * * *"
    timeout_seconds: 120
```

**Via crontab:**
```bash
# Add to crontab -e:
*/30 * * * * cd /path/to/xpulse && python -m xpulse.xpulse >> /tmp/xpulse.log 2>&1
```

**Via launchd (macOS):**
```xml
<!-- ~/.launchd/com.xpulse.scanner.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.xpulse.scanner</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/path/to/xpulse.py</string>
  </array>
  <key>StartInterval</key>
  <integer>1800</integer>
  <key>StandardOutPath</key>
  <string>/tmp/xpulse.log</string>
  <key>StandardErrorPath</key>
  <string>/tmp/xpulse.log</string>
</dict>
</plist>
```

---

## Example Output

### Alert to iMessage (Stage 3 Pass)

```
⚠️ X signal — affects your Kalshi positions:

  📈 Trump tariff: Trump announces new 25% steel tariffs (82% conf) [TRUMP-TARIFF-2025]
  📉 Inflation: Core CPI stays sticky, Fed unlikely to cut (75% conf) [FED-RATE-2026]
  ➡️  Ukraine: Peace talks accelerate, settlement probability rising (68% conf) [UKRAINE-2026]
```

### Signal Cache (Stage 1 → Morning Brief)

```json
{
  "signals": [
    {
      "topic": "Trump tariff",
      "confidence": 0.82,
      "direction": "bearish",
      "summary": "Trump announces new 25% steel tariffs",
      "post_count": 3
    },
    {
      "topic": "inflation",
      "confidence": 0.75,
      "direction": "bearish",
      "summary": "Core CPI stays sticky, Fed unlikely to cut further",
      "post_count": 2
    }
  ],
  "topics_scanned": 5,
  "timestamp": 1709990400.0
}
```

---

## Materiality Gate — Technical Details

See `references/materiality-gate.md` for detailed explanation of:
- How the 48h rolling window works
- Example filtering scenarios (signal vs noise)
- Fail-closed behavior

---

## Position Matching — Technical Details

See `references/position-matching.md` for:
- Keyword extraction algorithm (>2 char threshold)
- Overlap matching logic (2+ keyword requirement)
- Example position-signal pairs

---

## Troubleshooting

### Ollama Not Running

**Error:** `Connection refused` or `ollama: command not found`

**Fix:**
```bash
# Start Ollama in background
ollama serve &

# Or install if missing:
# Install from https://ollama.ai, then:
ollama pull qwen:latest
```

### Qwen Model Not Found

**Error:** `ollama run qwen:latest` fails

**Fix:**
```bash
ollama pull qwen:latest
# Or use qwen3 if available:
# ollama pull qwen3:latest
```

### DuckDuckGo Returning No Results

**Likely causes:**
- Topic is too specific or niche
- No recent posts on X about that topic
- DuckDuckGo rate limiting (try again later)

**Debug:**
```python
from ddgs import DDGS
d = DDGS()
results = list(d.text("site:x.com Trump tariff", max_results=5))
print(results)
```

### No Kalshi Positions (Stage 3 Suppresses All)

**Expected behavior:** If you have no active Kalshi positions, all signals are suppressed (logged silently). This is intentional — position-aware alerting is the goal.

**To test:** Either:
1. Create a test Kalshi position matching your topic
2. Disable Stage 3: set `position_gate: false` in config (alerts all non-materiality signals)

### Signal History Growing Too Large

**Automatic:** History is capped at 200 entries (oldest trimmed first)

**Manual reset:**
```bash
rm ~/.openclaw/state/x_signal_history.json
```

---

## Qwen Prompts (Core IP)

### Stage 1 Prompt: Signal Detection

```
You are a prediction market analyst. Given these recent X/Twitter posts about '{topic}',
determine if there's a tradeable signal.

{combined_posts}

Respond in JSON: {"has_signal": true/false, "confidence": 0.0-1.0,
"direction": "bullish/bearish/neutral", "summary": "one line"}
```

### Stage 2 Prompt: Materiality Gate

```
You are a personal alert filter for a prediction market trader.
Your job is to PREVENT notification fatigue. Only let through signals that are genuinely NEW and MATERIAL.

RECENTLY SENT ALERTS (what the user already knows):
{history_block}

CANDIDATE NEW SIGNALS:
{candidate_block}

RULES:
- REJECT if the signal covers the same story/development as a recent alert (even with different wording)
- REJECT if it's ongoing background noise (e.g. 'Trump discusses tariffs' when tariffs have been in the news for days)
- REJECT if there's no concrete new event, just commentary or speculation
- ACCEPT only if: (a) a genuinely new development occurred (vote, announcement, emergency, data release, market move),
OR (b) a significant escalation/reversal of something previously reported
- When in doubt, REJECT. The user prefers silence over noise.

Respond in JSON: {"keep": [list of topic strings to keep], "reasoning": "one line explaining why"}
```

---

## OpenClaw Ecosystem Integration

Social signal intelligence layer for the Prediction Market Trading Stack.

| Connected Skill | How It Connects |
|----------------|-----------------|
| **Market Morning Brief** | X signals appear in your daily morning digest |
| **Kalshalyst** | Social signals validate or challenge contrarian edges |
| **Prediction Market Arbiter** | Correlate social sentiment with cross-platform divergences |
| **Kalshi Command Center** | Act on position-matched signals via trade execution |

**Install the complete stack:**
```bash
clawhub install kalshalyst kalshi-command-center polymarket-command-center prediction-market-arbiter xpulse portfolio-drift-monitor market-morning-brief personality-engine
```

## Implementation Notes

Battle-tested in production trading environments. Design principles:

1. **Standalone implementation** — zero external dependencies beyond listed packages
2. **Direct alerts** — sends signals straight to you via your OpenClaw agent
3. **All thresholds, filters, and prompts** — refined through live social signal monitoring
4. **Fail-closed design** — no signal is better than a false positive
5. **Scripts are standalone** — works with any OpenClaw setup

---

## Performance & Cost

### Typical Run

- **Runtime:** 1-2 minutes (5 topics, Qwen Stage 1+2)
- **API calls:**
  - DuckDuckGo: 5 calls (1 per topic)
  - Kalshi: 1 call (fetch positions)
  - Ollama (local): 2 calls (Stage 1 + 2)
- **Cost:** $0 (DuckDuckGo free, Ollama local, Kalshi free read-only)

### Scaling

10 runs per day = ~10-20 minutes total runtime + zero API cost. Minimal resource usage.

---

## Further Reading

- `references/materiality-gate.md` — Signal deduplication + 48h window
- `references/position-matching.md` — Keyword overlap logic

---

## API Reference

### Main Function

```python
from xpulse import check_x_signals

# Single run
result = check_x_signals(state={}, dry_run=False, force=False)
# Returns: bool (True if alert sent, False otherwise)
```

### State Management

```python
# State dict tracks:
state = {
  "last_x_signal_check": 1709990400.0,  # Unix timestamp of last scan
  "last_x_signals_silent": [...]        # Suppressed signals (logged only)
}
```

---

## Support & Iteration

Xpulse is designed for iteration:

1. **Topic Tuning:** Add/remove topics as your trading focus changes
2. **Confidence Threshold:** Lower `min_confidence` to catch more signals (noisier), raise to reduce false positives
3. **Materiality Gate:** Disable if you're missing important signals, enable if too noisy
4. **Position Gate:** Disable `position_gate: false` if you want ALL signals (not recommended)
5. **Qwen Prompts:** Customize Stage 1/2 prompts for your trading style

---

## License & Attribution

**Author**: KingMadeLLC


---

## Feedback & Issues

Found a bug? Have a feature request? Want to share results?

- **GitHub Issues**: [github.com/kingmadellc/openclaw-prediction-stack/issues](https://github.com/kingmadellc/openclaw-prediction-stack/issues)
- **X/Twitter**: [@KingMadeLLC](https://x.com/KingMadeLLC)

Part of the **OpenClaw Prediction Stack** — the first prediction market skill suite on ClawHub.
