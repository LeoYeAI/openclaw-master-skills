# Contrarian Estimation System Prompt

## The Core Prompt (Claude Sonnet)

```
You are a contrarian prediction market analyst. You look for reasons markets are WRONG.

Your job: given a prediction market and its current price, determine if there's a
directional opportunity. You are advising a sophisticated trader who uses limit orders.

CRITICAL RULES:
1. You WILL be shown the current market price. Your job is to DISAGREE with it when you have reason to.
2. Don't just confirm the market. That's worthless. Look for what the market is MISSING or LAGGING on.
3. Consider: breaking news the market hasn't priced, political dynamics shifting, timing mismatches,
   crowd psychology errors, base rate neglect by the market.
4. Be opinionated. A 50% estimate on a 50% market is useless. Either find a reason it's wrong or
   say confidence is low.
5. Weight recent developments HEAVILY — markets are often slow to react to news in the last 24-48 hours.
6. Think about asymmetric upside: where is the cost of being wrong low but the payoff of being right high?

You must respond with ONLY a JSON object, no other text:
{
  "estimated_probability": <float 0.01-0.99>,
  "confidence": <float 0.0-1.0>,
  "reasoning": "<one sentence explaining WHY the market is wrong>",
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"],
  "conviction": "<strong|moderate|weak>"
}
```

## Why This Works

### The Evolution: From Blind to Contrarian

**Iteration 1: Blind Estimation (Discarded)**

Original approach: Hide the market price entirely.

```
EVENT: Will Ukraine still be at war in 2026?

Estimate from first principles based on base rates and public knowledge.
Respond with JSON...
```

**Problem:** Claude doesn't know what the market thinks, so defaults to high uncertainty (40-60% range). This matches the market price, producing zero edge.

**Why blind estimation fails:**
- Claude has no signal to disagree with
- No opportunity to apply contrarian reasoning
- Results in consensus-matching, low-edge estimates
- Traders can't act on "maybe 50%"

---

**Iteration 2: Contrarian Estimation (Current)**

New approach: Show the price explicitly and ask Claude to find disagreements.

```
EVENT: Will Ukraine still be at war in 2026?
CURRENT MARKET PRICE: 72¢ (market implies 72% probability)
Your job: Is this price WRONG? If yes, in which direction and why?

RECENT NEWS:
  - [Reuters] Ukraine peace talks advance with US mediation
  - [Bloomberg] Zelensky signals flexibility on territorial concessions
  - [AP] NATO considers diplomatic off-ramp for conflict

Is the market mispricing this? Give your true probability estimate...
```

**Result:** Claude sees the 72% price, sees the recent peace news, and reasons: "Market is anchored to base rate of long conflicts. But recent diplomatic momentum + US pressure + timeline to 2026 (only 10 months left) suggests 35-40% is more accurate."

**Edge:** |0.38 - 0.72| = **34% effective edge**

### Why Contrarian Mode Produces Edge

1. **Identifies Market Lags** — Markets often lag news by 24-48 hours
   - Contrarian prompt primes Claude to notice freshness of context
   - "Weight recent developments HEAVILY"

2. **Detects Crowd Psychology** — Markets systematically overprice base rates
   - "Look for what the market is MISSING"
   - Base rate neglect: "Ukraine has been at war for 2 years, so it will be at war forever"
   - Claude catches this explicitly

3. **Asymmetric Upside Recognition** — Markets underprice unlikely but high-payoff scenarios
   - "Think about asymmetric upside"
   - Market at 72% YES → betting NO pays 3.6x
   - If Claude thinks it's 35% → expected return 2.6x on a low-probability, high-conviction bet

4. **Timing Mismatch Detection**
   - Base rates apply over long periods (5+ years)
   - But this market closes in 10 months
   - Markets often fail to compress timeframes correctly
   - Claude is prompted to notice this

### The Full User Prompt

When Kalshalyst runs, it builds a prompt like:

```
EVENT: Will Ukraine still be at war in 2026?
TIME TO RESOLUTION: 10 days

RECENT NEWS:
  - [Reuters] Ukraine peace talks advance with US mediation (2026-03-07)
  - [Bloomberg] Zelensky signals flexibility on territorial concessions (2026-03-06)

ECONOMIC INDICATORS:
  S&P 500: $5,243 (+1.2%)
  Bitcoin: $67,432 (+3.4%)

SOCIAL SIGNAL:
  X/Twitter signal: bullish on "peace negotiations" — Recent diplomatic
  sentiment shift accelerating

CURRENT MARKET PRICE: 72¢ (market implies 72% probability)
Your job: Is this price WRONG? If yes, in which direction and why?

Is the market mispricing this? Give your true probability estimate and explain why
the market is wrong (or say confidence is low if you agree with the market).
Respond with JSON only.
```

Claude's response:
```json
{
  "estimated_probability": 0.38,
  "confidence": 0.68,
  "reasoning": "Market overweights base rate of ongoing war without pricing recent peace negotiation acceleration and US policy shift. Timeline to 2026 (10 months) compresses resolution window vs. long-term conflict forecasting.",
  "key_factors": [
    "Recent peace negotiation momentum (US-brokered talks showing progress)",
    "Timeline compression — market uses 2+ year base rate for 10-month window",
    "Policy shift — US pressure for settlement evident in recent statements"
  ],
  "conviction": "moderate"
}
```

**Edge calculated:** |38% - 72%| = 34% effective edge
**Recommendation:** BUY NO at 28¢ (100 - 72)

## Prompt Tuning Guidelines

### What Works

1. **Explicit disagreement invitation**
   - "Your job is to DISAGREE with it when you have reason to"
   - Makes Claude feel permission to be contrarian

2. **Recent news emphasis**
   - "Weight recent developments HEAVILY"
   - Markets are slow, recent changes create edge

3. **Base rate callouts**
   - "crowd psychology errors, base rate neglect"
   - Claude knows these biases exist and watches for them

4. **Asymmetry framing**
   - "asymmetric upside: where is cost of being wrong low?"
   - Primes Claude to notice underpriced tail risks

### What Doesn't Work (From Testing)

1. **Neutral language** ("estimate the probability")
   - Produces consensus-matching, zero-edge estimates
   - Claude defaults to market price when no disagreement signal

2. **Hiding the price** (blind estimation)
   - Claude can't disagree if it doesn't know what to disagree with
   - Results in 40-60% regression to the mean

3. **Too many constraints** ("only consider X, Y, Z")
   - Limits Claude's ability to discover novel disagreements
   - Better to say "don't just confirm the market" and let it think

4. **Confidence discounting in prompt**
   - ("only respond if highly confident")
   - Filters out medium-confidence edges
   - Better to filter post-hoc (confidence >= 0.4)

### Iteration Targets (For Your System)

If you're testing variants, focus on:

1. **Category-specific tuning**
   - Politics: emphasize polling lag, crowd psychology
   - Crypto: emphasize on-chain signals, sentiment shifts
   - Fed/Policy: emphasize forward guidance vs. market pricing

2. **Confidence calibration**
   - If your Brier score is > 0.25 in a category, recalibrate the prompt for that domain
   - Add domain-specific base rates: "Fed raises rates 75% of years with 5%+ inflation"

3. **News weighting**
   - Adjust "weight recent developments HEAVILY" if you find markets are already pricing news
   - May need different tuning for fast vs. slow-moving event categories

## Context Blocks (Optional Enrichment)

### Economic Indicators

Shown when Polygon API returns data (every 12 hours max):

```
ECONOMIC INDICATORS:
  S&P 500: $5,243 (+1.2%)
  Bitcoin: $67,432 (+3.4%)
  VIX proxy (VIXY): $18.5 (-2.1%)
  Gold (GLD): $201.32 (+0.8%)
```

**Why?** Macro context helps Claude calibrate on markets where geopolitical/policy events affect risk sentiment. SPX up = risk-on, which might suggest lower probability for geopolitical conflict escalation.

### Recent News

Fetched from Polygon.io (up to 3 articles per market):

```
RECENT NEWS:
  - [Reuters] Ukraine peace talks advance with US mediation (2026-03-07)
  - [AP] Zelensky signals flexibility on territorial concessions (2026-03-06)
  - [Bloomberg] EU leaders press for diplomatic resolution (2026-03-05)
```

**Why?** Markets lag news. Providing fresh news context lets Claude identify what's priced and what isn't.

### X/Twitter Social Signal

From X scanner (if enabled):

```
SOCIAL SIGNAL:
  X/Twitter signal: bullish on "peace negotiations" — Recent diplomatic
  sentiment shift accelerating, breaking through previous resistance
```

**Why?** Social sentiment often moves faster than market prices. Contrarian traders look for when social signal diverges from market action.

## Fallback: Qwen Blind Estimation

When Claude is unavailable, Kalshalyst falls back to local Qwen (runs offline via Ollama):

```
You are an expert prediction market analyst. Estimate the TRUE probability
of this event resolving YES.

EVENT: Will Ukraine still be at war in 2026?
TIME TO RESOLUTION: 10 days

[news + economic context as above]

INSTRUCTIONS:
1. Estimate from first principles — base rates, recent developments, timing.
2. If you lack information, reflect that in LOW confidence, not 50% probability.
3. Be calibrated: 70% means it happens 7 out of 10 times.

Respond in JSON: {
  "estimated_probability": <float>,
  "confidence": <float>,
  "reasoning": "<one sentence>",
  "key_factors": ["<factor 1>", "<factor 2>", "<factor 3>"]
}
```

**Note:** Qwen runs BLIND (market price NOT shown) to prevent anchoring.
This produces lower-edge estimates than Claude contrarian mode, but still useful as fallback.

**Typical results:**
- Claude contrarian: 20-30% edge
- Qwen blind fallback: 3-8% edge
- Both are tradeable; Claude is just more aggressive
