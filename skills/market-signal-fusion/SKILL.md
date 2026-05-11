---
name: market-signal-fusion
description: Adaptive-language stock-analysis skill that interprets macro and political news, fuses it with retail/social sentiment, applies quantified value fallback rules, and outputs machine-readable stock ideas with valuation and technical plans.
homepage: https://clawhub.com
user-invocable: true
disable-model-invocation: false
metadata: {"openclaw":{"emoji":"📈"}}
---

# Market Signal Fusion

Use this skill when the user wants **stock analysis driven by macro/political news + market sentiment + value screening + technical timing**.

This skill is designed for **adaptive language output** and for **downstream agent processing via a fixed JSON schema**.

---

## What this skill does

This skill runs a five-stage workflow:

1. Interpret recent **political/economic/news catalysts** that matter for equities.
2. Analyze **market sentiment** from retail/social discussion sources such as Reddit WSB and similar public channels.
3. **Fuse** step 1 and step 2 to identify candidate sectors and stocks.
4. Perform **quantamental analysis** and estimate **buy / sell / risk ranges**.
5. Add a **short-term technical plan** for entries, exits, and invalidation.

This version also adds three functional upgrades:
- a structured **WSB / retail sentiment data-module contract**
- a **market regime detector** to control style bias and sector weighting
- **confidence gates + reason codes** so decisions are auditable and degrade gracefully when data is incomplete

If tools are available, prefer real market data and recent sources. Do not invent numbers.

---

## Core operating rules

- Treat anything market-sensitive as **time-dependent**.
- Prefer the **most recent 1–7 days** for news and sentiment unless the user specifies another window.
- Use **primary or reputable financial sources** whenever possible.
- Separate clearly:
  - **facts**
  - **inference**
  - **opinion / scenario**
- Never present a stock pick without explaining **why** it survived the funnel.
- If a required dataset is unavailable, say so explicitly and continue with the best available evidence.
- Do **not** output generic investing advice; tie every conclusion to a catalyst, sentiment signal, valuation signal, or technical setup.
- When confidence is low, reduce conviction rather than forcing a pick.
- Every major conclusion should carry an implicit or explicit **confidence gate** based on freshness, source quality, and data completeness.
- Attach short **reason codes** and, when relevant, **rejection codes** to structured outputs so downstream agents can audit why a stock passed or failed.
- Preserve standard finance notation for tickers and metrics, e.g. `NVDA`, `Forward P/E`, `FCF Yield`, `PEG`, `RSI`, `200DMA`.

---

## Language and output rules

### Default language behavior

- **Follow the user's prompt language automatically**.
- If the user asks in **Chinese**, output the entire user-facing analysis in **Chinese only**.
- If the user asks in **English**, output the entire user-facing analysis in **English only**.
- Do **not** force bilingual output unless the user explicitly requests bilingual output.
- If the user does not clearly signal a language preference, use the language of the latest user request.
- Keep ticker symbols, sector names, factor names, JSON keys, and key financial metrics in standard English notation.

### Single-language formatting rules

For user-facing narrative sections:

- Match the user's language in headings and narrative.
- In Chinese mode, write headings, explanations, stock theses, and action plans in Chinese.
- In English mode, write headings, explanations, stock theses, and action plans in English.
- Do not append mirrored translations by default.
- For tables or JSON fields, use stable English keys and optionally localized display labels outside the JSON only when needed.

### Machine-readable output rule

Whenever the task is analytical and structured, output in **two layers**:

1. A **human-readable report in the user's language**
2. A **strict JSON block** that follows the schema below

If the user asks for only JSON, output only the JSON.
If the user asks for prose only, still internally follow the schema but omit the visible JSON unless useful.

---

## Inputs to collect from the user request

Extract these if the user provided them; otherwise use sensible defaults:

- Market universe: US equities by default
- Time horizon:
  - macro/news: last 7 days
  - sentiment: last 3 trading days if possible
  - valuation: trailing + forward where available
  - technicals: daily + weekly, and intraday if available
- Style bias: value first, but allow momentum confirmation
- Max output count:
  - hot stocks from sentiment: 10
  - final recommended list: 3 to 10 depending on evidence density
- Risk style:
  - if unspecified, assume **balanced swing trader with value discipline**

---

## Stage 1 — News and macro-political interpretation

Identify market-relevant developments from areas such as:

- central bank / rates / liquidity
- inflation / labor / growth data
- tariffs / sanctions / export controls
- fiscal policy / defense spending / infrastructure
- energy policy / OPEC / grid / power demand
- AI regulation / chips / cloud capex
- healthcare / drug pricing / reimbursement
- antitrust / trade restrictions / industrial policy
- geopolitical conflict affecting supply chains, commodities, shipping, or defense

For each major development, produce a structured record:

- **Catalyst**: one-line summary
- **Why the market cares**
- **Affected sectors / industries**
- **Direction**: bullish / bearish / mixed
- **Mechanism**: revenue, margin, capex, regulation, cost pass-through, rates, risk premium, etc.
- **Time horizon**: immediate / medium-term / long-term
- **Confidence**: high / medium / low

Then aggregate across catalysts and rank the **top favorable sectors**.

### Market regime detector

Before final sector ranking, classify the current market into one primary regime and optional secondary regime:

- `risk_on_growth`
- `risk_off_defensive`
- `inflation_reflation`
- `rate_sensitive`
- `commodity_shock`
- `earnings_revision_recovery`
- `policy_transition_mixed`

For the chosen regime, provide:
- the key evidence
- which sectors should receive a weight boost
- which sectors should be discounted
- whether valuation discipline should be stricter or looser

The regime detector should influence later ranking rules. Examples:
- In `risk_off_defensive`, reduce tolerance for speculative sentiment names.
- In `inflation_reflation` or `commodity_shock`, boost Energy / Materials / selected Industrials where supported by evidence.
- In `risk_on_growth`, allow stronger weight to AI / semis / software if revisions and charts confirm.

### Stage 1 scoring rubric

For each sector, compute an informal score from 0 to 100 using:

- policy/news tailwind strength: 0–30
- breadth of supporting catalysts: 0–20
- immediacy of earnings impact: 0–20
- durability of theme: 0–15
- clarity / confidence of mechanism: 0–15

Call this **Macro Tailwind Score**.

---

## Stage 2 — Social / retail sentiment analysis

Focus on market sentiment sources such as:

- Reddit WSB
- Reddit investing/stocks-style communities
- other accessible public sentiment sources if available

### Preferred architecture

If the runtime has a dedicated social-data tool or plugin, prefer it over free-form browsing.
Treat Stage 2 as a **data module** when possible, not only a narrative step.

### Recommended Stage 2 module contract

Inputs:
- `subreddits`: default `["wallstreetbets", "stocks", "investing"]`
- `lookback_window`: default `24h`, optional `72h` and `7d`
- `min_mentions_threshold`: default `5` when enough data exists
- `deduplicate_spam`: `true` by default
- `exclude_etfs_or_indexes`: optional, `false` by default

Preferred outputs per ticker:
- `mentions`
- `mentions_acceleration`
- `bullish_count`
- `bearish_count`
- `bullish_ratio`
- `sentiment_heat_score`
- `support_type`
- `speculation_risk`

If only partial data exists, degrade gracefully:
- If only mention frequency exists, treat the result as **attention analysis**, not full polarity sentiment.
- If bullish/bearish counts are missing, reduce confidence and do not overstate directional conviction.
- If spam or duplicate-post filtering is unavailable, raise the speculation-risk estimate.

### What to measure

For the broad market:

- overall risk-on vs risk-off tone
- prevalence of bullish vs bearish language
- concentration in index / mega-cap / meme / cyclical themes
- whether sentiment is euphoric, improving, cautious, or deteriorating

For single names:

- mention frequency
- acceleration of mentions
- bullish vs bearish balance
- whether the narrative is squeeze/speculation-driven or thesis-driven
- whether discussion aligns with the macro sectors from Stage 1

### Output required for Stage 2

1. A **market mood** call: bullish / neutral / bearish
2. A short explanation of why
3. The **10 hottest stocks** by sentiment attention
4. For each of the 10 stocks:
   - ticker
   - dominant narrative
   - sentiment label: bullish / bearish / mixed
   - whether it is likely **speculative** or **fundamentally supported**
   - whether the signal is full sentiment or attention-only

### Stage 2 scoring rubric

For each stock, form a **Sentiment Heat Score** from 0 to 100 using:

- raw mention intensity: 0–30
- mention acceleration: 0–20
- bullish/bearish skew: 0–20
- cross-source consistency: 0–15
- narrative quality (thesis > meme): 0–15

Also assign a **Speculation Risk Flag**: low / medium / high.

### Stage 2 confidence gate

Every Stage 2 conclusion should reflect these checks:

- `data_freshness`: fresh / acceptable / stale
- `source_count`: how many distinct sentiment sources were used
- `polarity_completeness`: full / partial / attention_only
- `duplicate_filtering`: yes / no / unknown
- `confidence`: high / medium / low

If `polarity_completeness = attention_only`, do not make a strong bullish/bearish market call from Stage 2 alone.


## Stage 3 — Fusion logic

### Primary rule

Use the **market regime detector** as a top-level weighting control.

If Stage 1 finds bullish sectors and Stage 2 contains stocks matching those sectors, prioritize the **overlap**.

### Secondary rule

If Stage 1 finds bullish sectors but Stage 2 does **not** contain good matches, perform a **quantified value-investing fallback screen** inside those sectors.

### Tertiary rule

If Stage 1 does **not** produce a clear sector conclusion, output the Stage 2 hot-stock list, ranked and filtered for quality.

### Fusion ranking formula

For each candidate stock, combine:

- Macro Tailwind Score: 30%
- Sentiment Heat Score: 20%
- Valuation Attractiveness Score: 25%
- Quality Score: 15%
- Technical Setup Score: 10%

Use judgment to override only when one signal is obviously distorted, for example meme-driven sentiment with broken fundamentals.

---

## Stage 3B — Quantified value-investing fallback screen

When a favored sector lacks sentiment candidates, screen for potentially undervalued stocks using as many of these as available:

- PEG relative to sector and growth profile
- forward P/E relative to sector
- EV/EBITDA relative to sector
- free cash flow yield
- earnings revision momentum
- revenue / EPS growth durability
- operating margin resilience
- ROIC / ROE quality
- debt burden / interest coverage
- dividend yield where relevant
- price/book where relevant for financials or asset-heavy sectors

### Hard fallback preference

Prefer a **harder quantified fallback** over loose narrative value language.

When enough data exists, compute a **Value Fallback Composite Score (0–100)** with this default weighting:

- **PEG score**: 25%
- **Forward P/E relative score**: 20%
- **FCF Yield score**: 25%
- **Revision Momentum score**: 20%
- **Balance Sheet / Quality guardrail score**: 10%

### Factor definitions

#### 1) PEG score (25%)

Score higher when:
- PEG is lower than sector median
- PEG is below 1.5, and score especially well below 1.0 when growth quality is credible
- avoid over-rewarding ultra-low PEG if earnings quality is weak or cyclical collapse distorts E

Suggested informal mapping:
- excellent: PEG < 1.0
- good: 1.0–1.5
- neutral: 1.5–2.0
- weak: > 2.0

#### 2) Forward P/E relative score (20%)

Compare company forward P/E to:
- sector median
- relevant peer median
- own 3Y or 5Y historical band when available

Score higher when the stock trades at a meaningful discount **without obvious deterioration in business quality**.

#### 3) FCF Yield score (25%)

Prefer higher free cash flow yield, especially when:
- FCF is positive and recurring
- conversion from earnings to cash is stable
- capex intensity does not make FCF misleading

Penalty conditions:
- one-off working capital boosts
- financially engineered buyback optics unsupported by real cash generation

#### 4) Revision Momentum score (20%)

Measure whether analyst expectations are improving:
- upward EPS revisions over 30–90 days
- upward revenue revisions when available
- fewer estimate cuts than sector peers

Score higher when revisions are improving and the stock still looks inexpensive.

#### 5) Balance Sheet / Quality guardrail score (10%)

Do not let a cheap-looking stock pass if the balance sheet is stressed.
Check:
- net debt / EBITDA
- interest coverage
- current ratio where relevant
- margin stability
- ROIC / ROE quality

### Fallback disqualifiers

A stock should usually **not** survive the fallback screen if several of the following are true:

- negative or chronically unstable FCF
- heavy leverage with weak interest coverage
- falling revisions with no identifiable catalyst
- very low multiple caused by structural decline rather than mispricing
- direct macro tailwind is weak or ambiguous

### Fallback output requirement

For fallback-selected stocks, explicitly show:

- why the stock was selected despite not appearing in sentiment overlap
- the component factor scores
- the final Value Fallback Composite Score
- whether the name is a **classic value**, **GARP**, or **deep value / higher risk** setup

Call the final valuation score in fallback mode:
**Valuation Attractiveness Score** and preserve the component breakdown in JSON.

---

## Stage 4 — Quantamental stock analysis and price zones

For each final stock, provide:

### A. Business / thesis snapshot

- what the company does
- why it fits the selected theme
- main bull case in 2–4 bullets
- main risks in 2–4 bullets

### B. Quantamental checklist

Use available metrics such as:

- market cap
- trailing P/E
- forward P/E
- PEG if available
- EV/EBITDA
- price/sales
- gross / operating margin
- EPS growth
- revenue growth
- free cash flow trend
- debt/equity or net debt/EBITDA
- analyst revision direction if available

Then score:

- Valuation Attractiveness Score (0–100)
- Fundamental Quality Score (0–100)
- Theme Alignment Score (0–100)
- Risk Score (0–100, where higher means riskier)

### C. Price framework

Estimate four levels when data supports it:

- **Aggressive buy zone**
- **Preferred buy zone**
- **Fair value / hold zone**
- **Trim / take-profit zone**

Base these on a mix of:

- valuation ranges
- support/resistance
- moving averages
- prior consolidation zones
- recent volatility

When exact valuation is unavailable, label the ranges as **technical estimate** rather than intrinsic value.

---

## Stage 5 — Technical setup and short-term plan

For each final stock, analyze:

- trend direction on weekly and daily timeframes
- key moving averages (20 / 50 / 200 if available)
- support and resistance
- breakout vs pullback setup
- momentum confirmation or divergence
- volume confirmation when available

Then provide a tactical plan:

- **Short-term stance**: buy pullback / breakout watch / avoid / wait / take profit
- **Entry idea**
- **Stop / invalidation level**
- **First target**
- **Second target**
- **Why this setup works or fails**

Do not imply certainty. Present it as a conditional trade plan.

---

## Reason codes and rejection codes

Wherever possible, attach concise structured tags that explain why a candidate passed or failed.

Examples of `reason_codes`:
- `MACRO_ENERGY_TAILWIND`
- `MACRO_DEFENSE_SPENDING`
- `REGIME_RISK_OFF_DEFENSIVE`
- `WSB_HEAT_HIGH`
- `WSB_POLARITY_PARTIAL`
- `REVISION_MOMENTUM_STRONG`
- `FCF_YIELD_STRONG`
- `TECH_PULLBACK_TO_50DMA`
- `TECH_BREAKOUT_WITH_VOLUME`

Examples of `rejection_codes`:
- `SPECULATION_RISK_HIGH`
- `VALUATION_DATA_INCOMPLETE`
- `FUNDAMENTALS_WEAK`
- `NEGATIVE_FCF`
- `BROKEN_CHART`
- `NO_CLEAR_CATALYST`

Use short, stable codes so downstream agents can filter, rank, and audit decisions.

---

## Fixed JSON output schema

When structured output is appropriate, emit a fenced `json` block that follows this schema as closely as possible.
Omit unavailable fields or set them to `null`; do not fabricate values.
Use the same single language as the user-facing report for all free-text values inside the JSON. Keep keys in English.

```json
{
  "meta": {
    "skill": "market-signal-fusion",
    "version": "1.2.0",
    "language_mode": "auto_single_language",
    "output_language": "zh|en",
    "market_universe": "US equities",
    "as_of_date": "YYYY-MM-DD",
    "time_windows": {
      "macro_news": "last_7d",
      "sentiment": "last_3d",
      "technicals": "daily_weekly"
    },
    "strict_mode": false
  },
  "macro": {
    "market_bias": "bullish|neutral|bearish|mixed",
    "market_regime": {
      "primary": "risk_on_growth|risk_off_defensive|inflation_reflation|rate_sensitive|commodity_shock|earnings_revision_recovery|policy_transition_mixed",
      "secondary": null,
      "evidence": [""],
      "style_implication": ""
    },
    "top_catalysts": [
      {
        "title": "",
        "summary": "",
        "direction": "bullish|bearish|mixed",
        "affected_sectors": [""],
        "mechanism": "",
        "time_horizon": "immediate|medium_term|long_term",
        "confidence": "high|medium|low",
        "confidence_gate": {
          "data_freshness": "fresh|acceptable|stale",
          "source_count": 0,
          "source_quality": "high|medium|low",
          "missing_fields": [""]
        }
      }
    ],
    "favored_sectors": [
      {
        "sector": "",
        "macro_tailwind_score": 0,
        "rationale": ""
      }
    ],
    "headwind_sectors": [""]
  },
  "sentiment": {
    "broad_market_mood": "bullish|neutral|bearish",
    "risk_mode": "risk_on|neutral|risk_off",
    "summary": "",
    "confidence_gate": {
      "data_freshness": "fresh|acceptable|stale",
      "source_count": 0,
      "polarity_completeness": "full|partial|attention_only",
      "duplicate_filtering": "yes|no|unknown",
      "confidence": "high|medium|low"
    },
    "hot_stocks": [
      {
        "ticker": "",
        "company": "",
        "sector": "",
        "dominant_narrative": "",
        "sentiment_label": "bullish|bearish|mixed",
        "signal_type": "full_sentiment|attention_only",
        "sentiment_heat_score": 0,
        "mentions": null,
        "mentions_acceleration": null,
        "bullish_count": null,
        "bearish_count": null,
        "bullish_ratio": null,
        "speculation_risk": "low|medium|high",
        "support_type": "speculative|fundamentally_supported|mixed"
      }
    ]
  },
  "selection": {
    "selection_mode": "macro_sentiment_overlap|macro_value_fallback|sentiment_only_fallback",
    "final_candidates": [
      {
        "ticker": "",
        "company": "",
        "sector": "",
        "selection_reason": "",
        "overlap_type": "macro_plus_sentiment|macro_plus_value|sentiment_only",
        "reason_codes": [""],
        "rejection_codes": [],
        "confidence_gate": {
          "data_freshness": "fresh|acceptable|stale",
          "source_count": 0,
          "source_quality": "high|medium|low",
          "missing_fields": [""]
        },
        "scores": {
          "macro_tailwind_score": 0,
          "sentiment_heat_score": 0,
          "valuation_attractiveness_score": 0,
          "quality_score": 0,
          "technical_setup_score": 0,
          "composite_score": 0
        },
        "value_fallback": {
          "used": true,
          "style_bucket": "classic_value|garp|deep_value_higher_risk|null",
          "component_scores": {
            "peg_score": 0,
            "forward_pe_relative_score": 0,
            "fcf_yield_score": 0,
            "revision_momentum_score": 0,
            "balance_sheet_quality_score": 0
          },
          "value_fallback_composite_score": 0
        }
      }
    ]
  },
  "stock_analysis": [
    {
      "ticker": "",
      "company": "",
      "sector": "",
      "thesis": "",
      "bull_case": [""],
      "risks": [""],
      "reason_codes": [""],
      "rejection_codes": [],
      "confidence_gate": {
        "data_freshness": "fresh|acceptable|stale",
        "source_count": 0,
        "source_quality": "high|medium|low",
        "missing_fields": [""]
      },
      "metrics": {
        "price": null,
        "market_cap": null,
        "trailing_pe": null,
        "forward_pe": null,
        "peg": null,
        "ev_ebitda": null,
        "fcf_yield": null,
        "revenue_growth": null,
        "eps_growth": null,
        "operating_margin": null,
        "net_debt_ebitda": null,
        "revision_momentum": null
      },
      "scores": {
        "valuation_attractiveness_score": 0,
        "fundamental_quality_score": 0,
        "theme_alignment_score": 0,
        "risk_score": 0
      },
      "price_zones": {
        "aggressive_buy_zone": "",
        "preferred_buy_zone": "",
        "fair_value_hold_zone": "",
        "trim_take_profit_zone": "",
        "zone_basis": "valuation|technical|mixed"
      },
      "technical_plan": {
        "trend": "uptrend|sideways|downtrend|mixed",
        "stance": "buy_pullback|breakout_watch|wait|avoid|take_profit",
        "support": [""],
        "resistance": [""],
        "entry_idea": "",
        "stop_invalidation": "",
        "target_1": "",
        "target_2": ""
      }
    }
  ],
  "summary": {
    "best_sector_now": {
      "name": "",
      "reason": ""
    },
    "best_value_candidate": "",
    "best_momentum_candidate": "",
    "market_stance_1_4w": ""
  }
}
```

---

## Final response template

Use this structure unless the user requests another format.

### 1) Macro and policy read

- Top 3–5 market-moving developments
- Sector beneficiaries
- Sector headwinds
- Ranked favorable sectors with Macro Tailwind Scores

### 2) Market sentiment read

- Broad market mood: bullish / neutral / bearish
- One-paragraph explanation in the user's language
- Top 10 hottest stocks:
  - ticker
  - theme
  - heat score
  - sentiment label
  - speculation risk

### 3) Final selected candidates

For each chosen stock, show:

- ticker and company
- sector / theme
- why selected
- overlap type:
  - macro + sentiment overlap
  - macro + value fallback
  - sentiment-only fallback

### 4) Quantamental scorecard

For each final stock, include:

- key valuation metrics
- quality metrics
- composite view
- aggressive buy zone
- preferred buy zone
- trim zone

### 5) Tactical trading view

For each final stock, include:

- trend
- support/resistance
- entry style
- stop/invalidation
- short-term targets

### 6) Summary judgment

Close with:

- most attractive sector right now
- strongest value candidate
- strongest momentum candidate
- broad market stance for the next 1–4 weeks

### 7) JSON output

After the single-language report, include the JSON block unless the user asked not to.

---

## Decision rules for edge cases

### When sentiment is very hot but fundamentals are poor

Say explicitly that the stock is **sentiment-driven, not value-supported**.

### When macro is bullish but charts are broken

Mark as **good company / bad timing** and prefer waiting for technical repair.

### When valuation is attractive but no catalyst exists

Mark as **watchlist value, low urgency**.

### When news and sentiment conflict

Prefer the signal with the clearer time horizon and stronger evidence. Explain the conflict.

### When fallback screen is triggered but data is partial

Use the fallback framework with only available factors, state which factors are missing, and lower confidence accordingly.

### When strict mode is requested

In strict mode, require stronger evidence to issue a final candidate:
- at least one high-quality macro source for Stage 1 conclusions
- sentiment polarity better than `attention_only` for strong sentiment claims
- at least 3 of the 5 fallback factors for value mode
- at least one technical confirmation signal before issuing an actionable short-term trade plan

---

## Style requirements

- Be concrete and investment-oriented.
- Avoid vague phrases like “looks interesting” without evidence.
- Show a ranking, not just descriptions.
- State when a conclusion is **data-backed** vs **inference**.
- Keep the narrative concise but decision-useful.
- Keep human-readable output in a single language matching the user and machine-readable output strict.

---

## Safety and honesty

- Do not fabricate prices, multiples, sentiment counts, or technical levels.
- If no trustworthy data is available for a requested component, say that component is unavailable.
- Remind the user that this is analysis, not guaranteed investment advice.
