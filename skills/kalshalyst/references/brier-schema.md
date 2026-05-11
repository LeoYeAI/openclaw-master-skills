# Brier Score Tracking — Schema & Methodology

## What Is the Brier Score?

The Brier Score measures how accurate your probability estimates are:

```
Brier Score = (1/n) * Σ(forecast - outcome)²
```

- **0.0** = perfect estimates (forecast exactly matches outcome every time)
- **0.25** = random baseline (for binary 50/50 events, coin flip = 0.25 Brier)
- **Above 0.25** = worse than a coin flip (systematically miscalibrated)

### Example

You make 5 estimates and markets resolve:

```
Market 1: Estimate 70%, resolves YES (outcome = 1)   → error² = (0.70 - 1)² = 0.09
Market 2: Estimate 30%, resolves NO (outcome = 0)    → error² = (0.30 - 0)² = 0.09
Market 3: Estimate 60%, resolves YES (outcome = 1)   → error² = (0.60 - 1)² = 0.16
Market 4: Estimate 50%, resolves NO (outcome = 0)    → error² = (0.50 - 0)² = 0.25
Market 5: Estimate 80%, resolves YES (outcome = 1)   → error² = (0.80 - 1)² = 0.04

Brier = (0.09 + 0.09 + 0.16 + 0.25 + 0.04) / 5 = 0.126
```

**Interpretation:** Brier of 0.126 is excellent (well below 0.25 baseline).

## Database Schema

Kalshalyst uses SQLite for persistence. Schema:

```sql
-- estimates: every probability forecast logged here
CREATE TABLE estimates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,                    -- Market identifier
    title TEXT,                              -- Human-readable market title
    estimated_prob REAL NOT NULL,            -- Forecast probability (0.01-0.99)
    market_price_cents INTEGER NOT NULL,     -- Market price at time of estimate
    confidence REAL,                         -- Estimator confidence (0.0-1.0)
    estimator TEXT DEFAULT 'unknown',        -- 'claude', 'qwen', or other
    edge_pct REAL,                           -- Calculated edge %
    direction TEXT,                          -- 'underpriced', 'overpriced', 'fair'
    category TEXT DEFAULT 'unknown',         -- 'politics', 'crypto', 'policy', etc.
    info_density REAL DEFAULT 0.0,           -- 0.0-1.0 context richness score
    created_at TEXT NOT NULL,                -- ISO 8601 timestamp
    created_ts REAL NOT NULL                 -- Unix timestamp
);

-- resolutions: market outcomes after they close
CREATE TABLE resolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL UNIQUE,             -- Must match estimates.ticker
    outcome INTEGER NOT NULL,                -- 1 = YES, 0 = NO
    resolved_at TEXT NOT NULL,               -- ISO 8601 timestamp
    resolved_ts REAL NOT NULL                -- Unix timestamp
);

-- indexes for fast querying
CREATE INDEX idx_estimates_ticker ON estimates(ticker);
CREATE INDEX idx_estimates_estimator ON estimates(estimator);
CREATE INDEX idx_estimates_created ON estimates(created_ts);
CREATE INDEX idx_resolutions_ticker ON resolutions(ticker);
```

## Data Flow

### Phase 1: Logging (During Kalshalyst Run)

When kalshalyst.py finds opportunities:

```python
from brier_tracker import log_estimates_batch

# After computing edges
edges = [
    {
        "ticker": "POTUS-2028-DEM",
        "title": "Will a Democrat win 2028?",
        "estimated_probability": 0.62,
        "yes_price": 48,
        "confidence": 0.70,
        "estimator": "claude",
        "effective_edge_pct": 14.0,
        "direction": "overpriced",
    },
    ...
]

# Log all estimates
logged = log_estimates_batch(edges)
print(f"Logged {logged} estimates to Brier tracker")
```

**Fields captured:**
- `ticker`: Unique market identifier
- `estimated_prob`: Claude/Qwen's estimate
- `market_price_cents`: Current market price (50 = 50¢ = 50%)
- `confidence`: Estimator's confidence level
- `estimator`: "claude" or "qwen"
- `edge_pct`: Calculated edge (|estimate - market|)
- `direction`: Whether market is overpriced or underpriced
- `category`: Inferred from ticker/title (politics, crypto, etc.)
- `info_density`: Richness of context at estimation time

### Phase 2: Auto-Resolution (Daily, Via Scheduler)

Periodically check Kalshi API for resolved markets:

```python
from brier_tracker import check_and_resolve_markets

# Call once per day (or when markets are expected to close)
resolved_count = check_and_resolve_markets()
print(f"Auto-resolved {resolved_count} markets")
```

**What happens:**
1. Query estimates table for all unique tickers WITHOUT a matching resolution
2. For each ticker, call Kalshi API to get market status
3. If status = "settled" or "finalized", record the outcome:
   - `result == "yes"` → `outcome = 1`
   - `result == "no"` → `outcome = 0`
4. Insert into resolutions table

**Polling strategy:** Kalshi keeps markets open for resolution debate for ~7 days after close, then finalizes. Reasonable polling window: daily for 2 weeks after expected close date.

### Phase 3: Reporting (Weekly/On-Demand)

Generate calibration report:

```python
from brier_tracker import get_brier_report

report = get_brier_report(
    estimator=None,      # None = all estimators
    category=None,       # None = all categories
    days=90              # Lookback 90 days
)
print(report)
```

**Output:**
```
BRIER SCORE REPORT (90d lookback)
24 resolved estimates

Overall Brier: 0.142
  Excellent calibration

By Estimator:
  claude: 0.128 (18 estimates)
  qwen: 0.198 (6 estimates)

By Category:
  politics: 0.118 (8)
  crypto: 0.155 (7)
  policy: 0.178 (5)
  other: 0.142 (4)

Calibration:
  0%-20%: forecast 8% vs actual 0% (5n) [OK]
  20%-40%: forecast 31% vs actual 25% (4n) [OK]
  40%-60%: forecast 52% vs actual 60% (5n) [OFF]
  60%-80%: forecast 69% vs actual 78% (6n) [OFF]
  80%-100%: forecast 89% vs actual 100% (4n) [OK]

Edge trades (edge >= 4%): 62% win rate (13 trades)
```

## Info Density Scoring

Info density measures how much context was available at estimation time (0.0-1.0 scale).

Rationale: Estimates made with rich context (recent news, macro data, social signals) should be better calibrated than estimates made with zero context.

### Components (Each 0.0-0.25, Max 1.0)

```python
def compute_info_density(market: dict) -> float:
    score = 0.0

    # News articles (0.0-0.25)
    news = market.get("news", [])
    if len(news) >= 3:
        score += 0.25
    elif len(news) >= 1:
        score += 0.15

    # X signal (0.0 or 0.25)
    if market.get("x_signal"):
        score += 0.25

    # Economic context (0.0 or 0.25)
    if market.get("has_economic_context"):
        score += 0.25

    # Liquidity proxy (0.0-0.25)
    volume = market.get("volume", 0)
    oi = market.get("open_interest", 0)
    liquidity = volume + oi
    if liquidity >= 5000:
        score += 0.25
    elif liquidity >= 1000:
        score += 0.15
    elif liquidity >= 100:
        score += 0.08

    return min(score, 1.0)
```

### Examples

**High density (0.75):**
- 3+ recent news articles
- X signal confirming direction
- S&P 500 + Bitcoin price data available
- High liquidity (volume + OI > 5000)
- Expected Brier: < 0.15

**Medium density (0.5):**
- 1 news article
- No X signal
- Economic data available
- Medium liquidity (500-1000)
- Expected Brier: 0.15-0.20

**Low density (0.25):**
- No news
- No social signal
- No economic context
- Low liquidity (< 100)
- Expected Brier: > 0.20 (harder to estimate blind)

## Calibration Methodology

### Calibration Buckets

Divide estimates into confidence bands and check if actual frequencies match claims:

```python
def _calibration_buckets(estimates: list[tuple[float, int]], n_buckets=5):
    """
    If you claim 70% probability, does it resolve YES ~70% of the time?
    """
    # Group estimates into buckets: 0-20%, 20-40%, 40-60%, 60-80%, 80-100%
    # For each bucket:
    #   - Calculate average forecast (what you claimed)
    #   - Calculate actual frequency (what actually happened)
    #   - Error = |forecast - actual|

    buckets = [
        {
            "range": "60%-80%",
            "count": 6,
            "avg_forecast": 0.69,
            "actual_rate": 0.78,
            "error": 0.09
        },
        ...
    ]
```

**Interpretation:**
- Error < 0.10 = Well calibrated ("OK")
- Error 0.10-0.20 = Slightly off ("OFF")
- Error > 0.20 = Badly miscalibrated ("BAD")

### Category Breakdown

Identify which **domains** you're good/bad at:

```
By Category:
  politics: Brier 0.118 ✓ (excellent — you understand politics)
  crypto: Brier 0.201   ⚠ (fair — crypto moves too fast)
  fed: Brier 0.268      ✗ (poor — fed policy is hard to forecast)
```

**Action:** If category Brier > 0.25, consider:
1. Recalibrating the Claude prompt for that domain
2. Adding domain-specific base rates to the context
3. Increasing confidence threshold for that category before alerting

### Estimator Comparison

Compare Claude vs Qwen:

```
By Estimator:
  claude: Brier 0.128 (18 estimates) ✓ Better
  qwen: Brier 0.198 (6 estimates)   ⚠ Fallback only
```

**Insight:** Claude's contrarian mode outperforms Qwen's blind estimation. Use Qwen only as fallback.

## Practical Use Cases

### Weekly Calibration Report

Add to your scheduler:

```python
# Every Monday morning
from brier_tracker import get_brier_report

report = get_brier_report(days=7)
send_to_user(report)
```

**Output helps you:**
- Identify which estimator is performing better
- See if specific categories are systematically wrong
- Spot-check that you're well-calibrated (Brier < 0.20)

### Calibration Alert (Automatic)

Check if you're worse than random:

```python
from brier_tracker import get_calibration_alert

alert = get_calibration_alert()
if alert:
    print(alert)
    # Send alert: "Politics category worse than random — recalibrate"
```

### Before Big Bets

Query Brier for category-specific accuracy:

```python
# About to trade a crypto market? Check crypto calibration first
db = _get_db()
rows = db.execute("""
    SELECT estimated_prob, outcome
    FROM estimates e
    JOIN resolutions r ON e.ticker = r.ticker
    WHERE e.category = 'crypto' AND e.created_ts > ?
""", (time.time() - 30*86400,)).fetchall()

brier = _brier_score([(p, o) for p, o in rows])
if brier > 0.25:
    print(f"WARNING: Crypto Brier is {brier:.3f} (worse than random)")
    print("Consider lowering confidence threshold or not trading")
```

## Calibration Tuning

### When Brier Is Too High (> 0.25)

**Diagnosis:** You're miscalibrated in a category.

**Options:**

1. **Tighten confidence threshold**
   ```python
   # Before: min_confidence = 0.4
   # After: min_confidence = 0.6 (for that category)
   # Fewer trades, but better accuracy
   ```

2. **Recalibrate Claude prompt**
   - Add domain-specific base rates
   - Example for "fed" (if Brier is high):
   ```python
   context += """
   BASE RATES (recent Fed behavior):
   - 75% of rate hikes are followed by cuts within 6 months
   - Inflation takes 12-18 months to respond to rate changes
   - The market tends to front-run Fed moves by 2-3 months
   """
   ```

3. **Use Qwen for that category** (fallback)
   ```python
   if category == "fed" and brier > 0.25:
       use_estimator = "qwen"  # Blind estimation for fed
   ```

4. **Build category-specific models**
   - Politics: Use polling aggregates as anchor
   - Crypto: Use on-chain metrics
   - Fed: Use economic calendar

### When Brier Is Excellent (< 0.15)

**Opportunity:** You can be more aggressive (higher Kelly, larger positions).

```python
# If brier < 0.15 in category:
kelly_alpha = 0.5  # Full Kelly (normally 0.25)

# Or lower confidence threshold:
min_confidence = 0.3  # Normally 0.4
```

## Maintenance

### Monthly

```python
# Check that auto-resolution is working
db = _get_db()
recent_estimates = db.execute("""
    SELECT COUNT(*) FROM estimates
    WHERE created_ts > ?
""", (time.time() - 30*86400,)).fetchone()[0]

unresolved = db.execute("""
    SELECT COUNT(*) FROM estimates e
    LEFT JOIN resolutions r ON e.ticker = r.ticker
    WHERE r.ticker IS NULL AND e.created_ts > ?
""", (time.time() - 30*86400,)).fetchone()[0]

if unresolved > recent_estimates * 0.5:
    print("WARNING: {unresolved} recent estimates still unresolved")
    print("Run check_and_resolve_markets() to catch up")
```

### Quarterly

Archive and analyze quarterly trends:

```python
# Q1 2026: What categories improved?
q1_report = get_brier_report(days=90)

# Q2 2026: Compare
q2_report = get_brier_report(days=90)

# Identify winners and losers
```

### Annually

Full audit:

```python
# 1. Check data integrity
db.execute("PRAGMA integrity_check")

# 2. Analyze trend (Brier improving or degrading?)
yearly_report = get_brier_report(days=365)

# 3. Export to CSV for external analysis
import csv
rows = db.execute("""
    SELECT e.*, r.outcome
    FROM estimates e
    LEFT JOIN resolutions r ON e.ticker = r.ticker
""").fetchall()

with open("brier_annual.csv", "w") as f:
    w = csv.writer(f)
    w.writerows(rows)
```

## Troubleshooting

### Brier Not Computing ("No resolved estimates")

**Cause:** Estimates haven't resolved yet or auto-resolution isn't running.

**Fix:**
```python
# 1. Check that estimates are being logged
db.execute("SELECT COUNT(*) FROM estimates")  # Should be > 0

# 2. Manually resolve a market (for testing)
from brier_tracker import resolve_market
resolve_market("POTUS-2028-DEM", outcome=1)

# 3. Run auto-resolution
from brier_tracker import check_and_resolve_markets
check_and_resolve_markets()

# 4. Now Brier should compute
get_brier_report()
```

### Brier Is Unexpectedly High (> 0.3)

**Diagnosis:**
1. Is your blocklist working? (filtering garbage markets)
2. Is Claude seeing good context? (news, economic data)
3. Is the confidence threshold too low? (logging low-confidence estimates)

**Debug:**
```python
# Which category is worst?
db.execute("""
    SELECT e.category, COUNT(*), AVG((e.estimated_prob - r.outcome) ** 2)
    FROM estimates e
    JOIN resolutions r ON e.ticker = r.ticker
    GROUP BY e.category
    ORDER BY AVG((e.estimated_prob - r.outcome) ** 2) DESC
""")

# Were estimates well-calibrated in that category?
# If yes → add more context
# If no → recalibrate prompt
```

### Estimates Table Growing Too Large

**Cause:** Logging every estimate, and not archiving old data.

**Fix:**
```python
# Archive estimates older than 1 year
db.execute("""
    DELETE FROM estimates
    WHERE created_ts < ? AND outcome IS NOT NULL
""", (time.time() - 365*86400,))

# Or export to CSV first:
rows = db.execute("SELECT * FROM estimates WHERE created_ts < ?", (...))
# [write to CSV]
```
