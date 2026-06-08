# Bubble Detection Quick Reference (English)

## Daily Checklist (5 minutes)

### Morning Routine (Before Market Open)

```
□ Step 1: Update Bubble-O-Meter (2 min)
   - Score 8 indicators (0-2 points each)
   - Check risk budget based on total score

□ Step 2: Position Management (2 min)
   - Update ATR trailing stops
   - Check stair-step profit targets
   - Evaluate new entry eligibility

□ Step 3: Signal Check (1 min)
   - Media/Social trends (Google Trends, Twitter)
   - Major indices distance from 52-week highs
   - VIX & Put/Call ratio
```

---

## Emergency Assessment: 3 Questions

When uncertain about an investment decision, answer these 3 questions:

### Q1: "Are non-investors recommending it?"
- YES → Mass penetration complete, likely late stage
- NO → Still early to mid stage

### Q2: "Has the narrative become 'common sense'?"
- YES → Euphoria stage, contrarian views socially unacceptable
- NO → Healthy skepticism still functions

### Q3: "Is 'this time is different' the catchphrase?"
- YES → Classic historical bubble signal
- NO → Healthy caution still present

**All 3 YES → Critical zone, prioritize profit-taking/exit**

---

## Action Matrix by Bubble Phase

| Phase | Score | Risk Budget | Entry | Profit-Taking | Stop | Short |
|-------|-------|------------|-------|---------------|------|-------|
| **Normal** | 0-4 | 100% | Normal | At target | 2.0 ATR | No |
| **Caution** | 5-8 | 70% | 50% reduced | 25% at +20% | 1.8 ATR | No |
| **Euphoria** | 9-12 | 40% | Stopped | 50% at +20% | 1.5 ATR | After confirm |
| **Critical** | 13-16 | 20% | Stopped | 75-100% now | 1.2 ATR | Recommended |

---

## 8 Indicators Quick Scoring

### 1. Mass Penetration
```
0 pts: Investors only
1 pt: General awareness but investment limited
2 pts: Taxi drivers/family recommending
```

### 2. Media Saturation
```
0 pts: Normal coverage
1 pt: Search trends 2-3x normal
2 pts: TV specials/magazine covers, 5x+ search spike
```

### 3. New Accounts & Inflows
```
0 pts: Normal account openings
1 pt: 50-100% YoY increase
2 pts: 200%+ YoY, first-time investor flood
```

### 4. New Issuance Flood
```
0 pts: Normal IPO volume
1 pt: IPO/SPAC/ETFs up 50%+
2 pts: Low-quality IPO flood, "theme" fund proliferation
```

### 5. Leverage Indicators
```
0 pts: Margin debt in normal range
1 pt: Margin debt 1.5x average
2 pts: All-time high margin, funding rates elevated, extreme positioning
```

### 6. Price Acceleration
```
0 pts: Annualized returns near historical median
1 pt: Returns exceed 90th percentile
2 pts: Returns at 95-99th percentile, or positive second derivative
```

### 7. Valuation Disconnect
```
0 pts: Fundamentally explainable
1 pt: High valuation but "growth expectations" provide cover
2 pts: Pure "narrative" dependent, fundamentals ignored
```

### 8. Breadth & Correlation
```
0 pts: Only leader stocks rising
1 pt: Sector-wide participation
2 pts: Low-quality/zombie companies rising (last buyers in)
```

---

## Profit-Taking Strategy Templates

### Template 1: Stair-Step (Conservative)

```
Position: $10,000 initial investment
Targets: +20%, +40%, +60%, +80%

+20% ($12,000) → Sell 25% = $3,000 secured
+40% ($14,000) → Sell 25% = $3,500 secured
+60% ($16,000) → Sell 25% = $4,000 secured
+80% ($18,000) → Sell 25% = $4,500 secured

Total profit secured: $15,000 (+50% equivalent)
```

### Template 2: ATR Trailing (Aggressive)

```python
def calculate_trailing_stop(current_price, atr_20d, bubble_phase):
    """
    Calculate trailing stop based on bubble phase
    
    bubble_phase: 'normal', 'caution', 'euphoria', 'critical'
    """
    multipliers = {
        'normal': 2.0,
        'caution': 1.8,
        'euphoria': 1.5,
        'critical': 1.2
    }
    multiplier = multipliers.get(bubble_phase, 2.0)
    stop_price = current_price - (atr_20d * multiplier)
    return stop_price
```

### Template 3: Hybrid (Recommended)

```
Stage 1 (Boom):
  → Stair-step reduces 50% of position
  
Stage 2 (Euphoria):
  → Apply ATR trailing to remaining 50%, ride upside
  
Stage 3 (Panic signals):
  → Exit immediately when ATR stop hit
```

---

## Short-Selling Timing Decision (Critical)

### ❌ Absolutely Avoid: Early Contrarian

```
Reason: Often 2-3x further rise after "obviously too high"
Risk: "Markets can remain irrational longer than you can remain solvent"
```

### ✅ Recommended: After Composite Conditions Met

**Need at least 3 of 7 conditions before considering:**

1. □ Weekly chart shows clear lower highs
2. □ Volume peaked out (3 weeks declining)
3. □ Leverage metrics drop sharply (margin debt -20%+)
4. □ Media/search trends peaked out
5. □ Weak stocks in sector breaking down first
6. □ VIX spike (+30%+)
7. □ Fed or policy reversal signals

**Execution example:**

```
Conditions check:
[✓] 1. Weekly lower highs
[✓] 2. Volume declining 3 weeks
[×] 3. Margin debt still elevated
[✓] 4. Google trends -40%
[×] 5. Still broad rally
[✓] 6. VIX +35% spike
[×] 7. No policy change

→ 4/7 met, short consideration OK
→ Small size (25% of normal) test entry
```

---

## Common Failure Patterns & Solutions

### Failure 1: "Too late" mentality, perpetual waiting

**Psychology:** Regret aversion (FOMO about missing out)  
**Solution:**
- Run Bubble-O-Meter when feeling too late
- If score ≤8, small entry OK
- If score ≥9, correct to wait

### Failure 2: Re-entry after taking profits (buying high)

**Psychology:** Hindsight bias ("I knew it would go up")  
**Solution:**
- 72-hour re-entry ban after profit-taking
- Re-entry only after Bubble-O-Meter check

### Failure 3: "Still going up" paralysis on profit-taking

**Psychology:** Greed + Overconfidence  
**Solution:**
- Automate stair-step (preset limit orders)
- Target "satisfaction" not "perfection"

### Failure 4: Premature short selling

**Psychology:** Subjective "obviously too high"  
**Solution:**
- Mechanically check composite conditions
- Wait for minimum 3 conditions

---

## Emergency Response Flowchart

```
Market shock detected
    ↓
Q: Have positions?
    ↓YES
Q: Down -5%+ ?
    ↓YES
Q: ATR stop hit?
    ↓YES
→ Sell immediately (no debate)
    
    ↓NO (stop not hit)
Q: Bubble-O-Meter 13+?
    ↓YES
→ Consider 75%+ profit-taking
    
    ↓NO (score ≤12)
Q: VIX spike +30%+?
    ↓YES
→ Take 50% profits, tighten stops on rest
    
    ↓NO
→ Normal monitoring, stay calm
```

---

## Golden Rules (Post on Your Wall)

1. **Watch the process, not the price**

2. **When taxi drivers talk stocks, exit**

3. **"This time is different" is the same every time**

4. **Mechanical rules protect your psychology**

5. **Short after confirmation, take profits early**

6. **When skepticism hurts socially, the end begins**

7. **Aim for satisfaction, abandon perfection**

8. **Bubbles last longer than expected, crashes faster**

9. **Leverage is an express ticket to ruin**

10. **"Markets can remain irrational longer than you can remain solvent"**

---

## Key Data Sources

### Instantly Accessible Indicators

| Indicator | Source | URL Example |
|-----------|--------|-------------|
| Google Search Trends | Google Trends | trends.google.com |
| VIX (Fear Index) | CBOE | cboe.com/vix |
| Put/Call Ratio | CBOE | cboe.com/data |
| Margin Debt | FINRA | finra.org/data |
| Futures Positioning | CFTC COT | cftc.gov/reports |
| IPO Statistics | Renaissance IPO | renaissancecapital.com |

### API-Accessible for Automation

```python
# Example: Google Trends (pytrends)
from pytrends.request import TrendReq
pytrends = TrendReq()
pytrends.build_payload(['SPY', 'stock market'])
data = pytrends.interest_over_time()

# Example: VIX (yfinance)
import yfinance as yf
vix = yf.Ticker('^VIX')
current_vix = vix.history(period='1d')['Close'].iloc[-1]
```

---

## Further Learning

### Books
- "Manias, Panics, and Crashes" - Charles Kindleberger
- "Irrational Exuberance" - Robert Shiller
- "The Alchemy of Finance" - George Soros

### Research
- Hyman Minsky's Financial Instability Hypothesis
- Behavioral Finance classics

### Data & Tools
- TradingView: Charts & technical indicators
- FRED (Federal Reserve): Economic time series
- Finviz: Screening & heatmaps
- Google Trends: Social trends

---

**Last Updated:** 2025 Edition  
**License:** Educational/personal use only
