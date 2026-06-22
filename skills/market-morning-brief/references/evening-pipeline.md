# Evening Briefing: Two-Stage AI-Filtered News Pipeline

## Overview

The evening briefing news mode implements a sophisticated two-stage filtering pipeline designed to deliver material market news while preventing notification fatigue.

**Key design principle:** Fail-closed silence. If the AI filter breaks, we send nothing rather than spam.

## Architecture

### Stage 1: Relevance & Significance Filter

```
DuckDuckGo News Search
    ↓
[Article 1] [Article 2] [Article 3] ...
    ↓
Qwen LLM Analysis (per article)
  "is_significant: true/false?"
  "confidence: 0-1"
  "category: policy|markets|technology|geopolitics|other"
  "summary: one-liner"
    ↓
Filter by min_confidence (default: 0.7)
    ↓
Limit to top 10 by confidence (prevent timeout)
    ↓
[Significant 1] [Significant 2] ... [Significant 10]
```

**Purpose:** Quick relevance assessment. Filters out obvious noise, opinion pieces, and off-topic articles.

**Qwen prompt:** "Is this article significant for prediction markets? Rate confidence 0-1."

**Timeout:** 30 seconds per article (fail if exceeded)

### Stage 2: Materiality Gate

```
[Significant articles from Stage 1]
    ↓
Load news history (last 48h, max 200 entries)
    ↓
Qwen LLM Comparison
  Candidates: [list of new articles]
  History: [recently sent articles]
  Decision: "Which candidates are genuinely NEW and MATERIAL?"
    ↓
Fail-closed: if Qwen fails → return []
    ↓
Keep only articles marked "keep"
    ↓
[Material articles ready to send]
```

**Purpose:** Prevent notification fatigue. Detect:
- Duplicate stories (same development, different wording)
- Background noise (Fed rate discussion when ongoing for weeks)
- Commentary without new events
- Routine updates (earnings, minor announcements)

**Qwen prompt:** "Given recent news history, which candidates represent genuinely NEW developments?"

**Timeout:** 90 seconds (longer for context window)

### Fail-Closed Design

If either stage fails:
- **Stage 1 Qwen timeout/crash:** Skip that article, continue processing others
- **Stage 1 complete failure:** Return empty (no articles found)
- **Stage 2 Qwen timeout/crash:** Drop all candidates (fail closed)
- **No articles pass filter:** Send empty briefing (no interruption)

This design prioritizes **silence over noise**. Better to miss a news item than spam the user with false positives.

## Configuration

### Basic Config

```yaml
market_morning_brief:
  evening_briefing:
    enabled: true
    mode: "news"                           # or "market"
    time: "18:00"                          # Briefing time (HH:MM)
    timezone: "America/New_York"           # Optional timezone
    materiality_gate: true                 # Enable Stage 2 filter
    min_confidence: 0.7                    # Minimum relevance (0-1)
    max_per_topic: 3                       # Articles per topic to search
    topics:
      - "prediction markets"
      - "AI policy"
      - "federal reserve"
      - "geopolitics"
```

### Tuning Parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `min_confidence` | 0.7 | Lower = more articles pass Stage 1, higher = stricter |
| `max_per_topic` | 3 | More = more search results, slower, more to filter |
| `materiality_gate` | true | Disable to see all Stage 1 results (skip Stage 2) |
| `time` | 18:00 | Briefing window: time ± 30 minutes |

### Tuning Examples

**More news (lower bar):**
```yaml
min_confidence: 0.6
materiality_gate: false  # Skip Stage 2
max_per_topic: 5
```

**Less noise (higher bar):**
```yaml
min_confidence: 0.8
materiality_gate: true   # Enforce Stage 2
max_per_topic: 2
```

## Data Flow

### Input: DuckDuckGo News Search

For each topic:
```
Search: "prediction markets"
Results: [
  {
    "title": "Polymarket Volume Hits Record High",
    "body": "Trading activity on Polymarket surged 45% as election season approaches...",
    "source": "CoinDesk",
    "date": "2026-03-08T14:30:00Z",
    "url": "https://...",
  },
  ...
]
```

### Processing: Stage 1 Qwen Analysis

Input article + prompt:
```
Topic: prediction markets
Title: Polymarket Volume Hits Record High
Body: Trading activity on Polymarket surged 45% as election season approaches...
Source: CoinDesk

Qwen analysis → JSON output:
{
  "is_significant": true,
  "confidence": 0.82,
  "category": "markets",
  "summary": "Polymarket trading volume surged 45% as election season approaches"
}
```

### Processing: Stage 2 Qwen Materiality Gate

Input: candidates + history

```
Recently sent (history):
- [12h ago] Polymarket Market Launches New Category
- [24h ago] Fed Signals Rate Cut Hesitation
- [36h ago] Tech Stocks Rally on Earnings

Candidates to evaluate:
- Polymarket Volume Hits Record High
- Fed Continues Hawkish Messaging
- Crypto Markets Stabilize

Qwen decision:
- Polymarket Volume: REJECT (story covered 12h ago as "new category launch")
- Fed Continues: REJECT (Fed discussion ongoing for weeks, no new event)
- Crypto Stabilize: ACCEPT (genuinely new market movement)
```

### Output: Evening News Briefing

```
EVENING NEWS BRIEFING — Thursday, March 8, 2026

📰 Crypto Markets Stabilize After Volatility (82% conf, CoinDesk)
```

## History Persistence

Stored at `~/.openclaw/state/evening_news_history.json`:

```json
[
  {
    "topic": "prediction markets",
    "title": "Polymarket Volume Hits Record High",
    "summary": "Trading activity surged 45% as election season approaches",
    "category": "markets",
    "confidence": 0.82,
    "timestamp": 1709950200
  },
  {
    "topic": "AI policy",
    "title": "Congress Advances AI Regulation Bill",
    "summary": "Bipartisan bill moves forward with new guardrails",
    "category": "policy",
    "confidence": 0.85,
    "timestamp": 1709946600
  }
]
```

**Cleanup rules:**
- Auto-remove entries older than 48 hours
- Keep max 200 entries (oldest removed first)
- Updated each time evening briefing sends articles

## Usage Examples

### Basic: Daily evening news at 6 PM

```bash
# Add to cron
0 18 * * * /usr/bin/python3 /path/to/scripts/evening_brief.py --mode news
```

### With custom topics and stricter filter

```bash
python scripts/evening_brief.py --mode news \
  --topics "crypto,tech,geopolitics" \
  --min-confidence 0.8 \
  --max-per-topic 3
```

### Testing: Force send with debug output

```bash
python scripts/evening_brief.py --mode news \
  --force --debug --dry-run
```

Output:
```
[DEBUG] Evening brief mode: news
[DEBUG] Config: {"topics": [...], "min_confidence": 0.7, ...}
[DEBUG] Time check: 18:05:30, target 18:00, diff 5min, in_window=true
[DEBUG] Evening news briefing starting... (4 topics)
[DEBUG]   prediction markets: 3 articles found
[DEBUG]   AI policy: 3 articles found
[DEBUG]   federal reserve: 3 articles found
[DEBUG]   geopolitics: 3 articles found
[DEBUG] Evening news briefing: 12 articles found, analyzing relevance...
[DEBUG]   Stage 1: Qwen processed 12 articles
[DEBUG] Evening news briefing: 8 significant articles after Stage 1
[DEBUG] Loaded 45 articles from 48h history
[DEBUG] Stage 2 filter: 8 candidates → 3 kept. Reason: new market movements and policy developments
[DEBUG] Evening news briefing: 3 material articles sent

EVENING NEWS BRIEFING — Thursday, March 8, 2026

📈 Crypto Markets Rally on Fed Comments (87% conf, Bloomberg)
🏛️ Congress Advances AI Regulation Bill (85% conf, Reuters)
🌍 Geopolitical Tensions Escalate (78% conf, AP)

[DEBUG] Evening brief generated successfully
```

### Lightweight market mode: Activity only

```bash
python scripts/evening_brief.py --mode market --force
```

Output:
```
EVENING BRIEFING — Thursday, March 8, 2026

ACTIVITY:
Current positions: 3 | Cost: $132 | Unrealized: +$24

OVERNIGHT WATCH:
• FED-MAR-CUT expires in 8 days — monitor Fed speakers before FOMC
• UKRAINE-2026 low liquidity (9 contracts asking) — wide spreads

X SIGNALS TODAY:
• Ukraine ceasefire talks +3% (78% conf)
• Fed rate cut odds stabilizing (72% conf)
```

## Troubleshooting

### No articles appear

**Checklist:**

1. Is it the right time? (default 18:00 ± 30 min)
   ```bash
   python scripts/evening_brief.py --mode news --force --debug
   ```

2. Is Ollama running?
   ```bash
   ollama list
   ollama run qwen3:latest "test"
   ```

3. Do news sources work?
   ```bash
   python -c "from ddgs import DDGS; print(list(DDGS().news('test', max_results=1)))"
   ```

4. Check debug output for stage 1/2 filters
   ```bash
   python scripts/evening_brief.py --mode news --debug | grep -i "stage"
   ```

### Stage 1 finds articles but Stage 2 drops all

**This is expected.** Stage 2 is designed to reject non-material stories.

**To verify:**
```bash
# Disable Stage 2, see Stage 1 output
python scripts/evening_brief.py --mode news --no-materiality-gate --debug

# Clear history to remove context (temporary debugging)
rm ~/.openclaw/state/evening_news_history.json
python scripts/evening_brief.py --mode news --debug
```

### Qwen timeout (30s or 90s)

**Reduce load on Qwen:**
```bash
# Fewer articles to process
python scripts/evening_brief.py --mode news \
  --max-per-topic 2 \
  --min-confidence 0.8
```

**Or skip Stage 2:**
```bash
python scripts/evening_brief.py --mode news --no-materiality-gate
```

### Memory issues or Ollama crashes

```bash
# Restart ollama
launchctl stop local.ollama
sleep 2
launchctl start local.ollama

# Or try smaller model
ollama pull qwen2:1.5b
# Then update config to use qwen2:1.5b
```

## Performance

### Stage 1: Relevance Filter

| Input | Process | Output | Time |
|-------|---------|--------|------|
| 9 articles (3 topics × 3) | Qwen per-article analysis | ~6-7 significant | 3-5 min |
| 15 articles (5 topics × 3) | Same | ~10-12 significant | 5-8 min |

**Timeout:** 30 seconds per article (fail if exceeded)

### Stage 2: Materiality Gate

| Input | Process | Output | Time |
|-------|---------|--------|------|
| 10 candidates | Single Qwen call | ~3-5 material | 30-60 sec |
| 3 candidates | Single Qwen call | ~2-3 material | 20-40 sec |

**Timeout:** 90 seconds total

**Load:** Qwen context window ~12K tokens (history + candidates)

### Overall Pipeline

- **Fastest:** 2 topics × 2 articles/topic, Stage 2 skipped = 1-2 min
- **Default:** 3 topics × 3 articles/topic, Stage 2 enabled = 4-7 min
- **Slowest:** 5 topics × 5 articles/topic, Stage 2 enabled = 10-15 min

**Network:** DuckDuckGo search ~10-30 sec (varies by connection)

## Design Rationale

### Why Two Stages?

1. **Stage 1** filters for relevance: Is this about prediction markets/finance/geopolitics?
2. **Stage 2** filters for materiality: Is this NEW? Or just noise?

Separating them allows:
- Parallel batch processing in Stage 1 (could be)
- Context-aware comparison in Stage 2 (requires history)
- Different timeouts (30s vs 90s)
- Independent tuning (min_confidence vs materiality_gate toggle)

### Why Fail-Closed?

If Qwen fails or times out, we drop articles rather than send potentially spam. Rationale:

- User training: "If I get notified, it's important"
- Missing news is worse than false positives
- News cycles always provide another opportunity
- Prevents cascading failures (spam → user ignores → broken feedback)

### Why 48-Hour History?

- **Short enough** to catch duplicates (most news repeats within 24h)
- **Long enough** to span weekends (no Saturday news means Sunday gets fresh perspective)
- **Matches briefing frequency** (once per day, so max ~2 briefings overlap)

### Why Category Icons?

Categories help users scan at a glance:
- 🏛️ policy = actionable regulations/statements
- 📈 markets = price moves, trading activity
- 💻 technology = AI, crypto tech, infrastructure
- 🌍 geopolitics = international events, tensions
- 📌 other = miscellaneous

## Future Enhancements

- [ ] Per-topic confidence thresholds
- [ ] Time-aware filtering (different thresholds at different times)
- [ ] User feedback loop (user marks articles as useful/noise)
- [ ] Category-specific materiality gates
- [ ] Streaming Stage 1 results (don't wait for all articles)
- [ ] Personalized topic weights
