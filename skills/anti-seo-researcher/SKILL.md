---
name: anti-seo-researcher
description: >
  Anti-SEO deep consumer research tool. When a user wants to buy a product or make a consumer decision,
  use this Skill. Automatically detects user language and adapts to regional platforms and search strategies.
  Works with or without web_search — gracefully degrades to built-in Bing scraping when web_search is unavailable.
allowed-tools:
  - execute_command
  - read_file
  - write_to_file
  - web_search    # Optional — if unavailable, use scripts/web_search_fallback.py instead
  - web_fetch
---

# Anti-SEO Deep Consumer Researcher

> Detailed rules, scoring criteria, and category examples: see `references/SKILL_REFERENCE.md`

## Tool Availability & Graceful Degradation

This skill works best with `web_search` + `web_fetch`, but **`web_search` is optional**. If your environment does not have `web_search` available (e.g., no API key configured), the skill will automatically degrade to use built-in Bing scraping scripts instead.

### Detection (run at skill startup)

At the very beginning, before any research steps, determine which search mode to use:

1. **Full mode** (preferred): If `web_search` tool is available in your environment, use it directly for all search operations as described in the workflow below.
2. **Fallback mode**: If `web_search` is NOT available (tool missing, API key not configured, or returns errors), use the built-in fallback script for ALL search operations:

```bash
# Instead of: web_search("电竞椅 推荐 避坑 2025")
# Use:
python scripts/web_search_fallback.py "电竞椅 推荐 避坑 2025" --count 10 --days 365

# Instead of: web_search("site:reddit.com office chair review")
# Use:
python scripts/web_search_fallback.py "office chair review" --site reddit.com --count 10

# Multi-site search (searches each site independently):
python scripts/web_search_fallback.py "电竞椅 推荐" --sites zhihu.com,v2ex.com,smzdm.com --count 5

# Search + fetch content in one call (reduces round trips):
python scripts/web_search_fallback.py "电竞椅 避坑" --count 10 --fetch-content --fetch-limit 3
```

The fallback script uses DuckDuckGo HTML search as the primary engine (most reliable, no captcha), with Bing HTML as automatic fallback — **zero API keys needed**. It outputs the same JSON format as `web_search` results.

### Fallback Mode Workflow Adjustments

When in fallback mode, apply these adjustments throughout the entire workflow:

| Original (Full Mode) | Fallback Mode Replacement |
|---|---|
| `web_search("query")` | `python scripts/web_search_fallback.py "query" --count 10` |
| `web_search("site:xxx.com query")` | `python scripts/web_search_fallback.py "query" --site xxx.com` |
| Step 2c: AI uses `web_search` for forum searches | Use `platform_search.py` with `--dual-window --append-year` flags |
| Step 4.5: AI uses `web_search` for safety events | Use `deep_dive_search.py` with `--safety-only` flag, OR `web_search_fallback.py` |

**Important**: `web_fetch` is STILL used normally in fallback mode for fetching specific page content. Only `web_search` is replaced.

**All other steps (credibility scoring, conflict resolution, brand scoring, report generation) work identically in both modes** — they process search results regardless of how those results were obtained.

## Architecture Overview

**Language Detection → AI Category Adaptation → AI Multi-layer Search (forum posts + e-commerce reviews + social comment sections) → Script Scoring → AI Semantic Analysis → Dynamic Multi-dimensional Scoring → Report**

- **Language & Region Layer**: Detect user's language from query, generate region-specific platform config, search templates, and keyword dictionaries
- **Category Layer**: AI generates `category_profile` JSON (evaluation dimensions/weights/pain point keywords/safety risks/platform weights/e-commerce search strategy)
- **Search Layer** (3-tier data sources):
  - **L1 E-commerce Review Layer** (highest priority): Indirect search for real buyer reviews (e.g., Amazon reviews, JD follow-up reviews, depending on region)
  - **L2 Social Comment Section Layer** (second priority): Search for "debunking" feedback in comment sections of promotional posts
  - **L3 Forum Post Layer** (traditional): AI uses `web_search` (or `web_search_fallback.py` when `web_search` is unavailable) + `site:` for targeted community searches
- **Scoring Layer**: `credibility_scorer.py` (regex pre-filter + category signal injection + data source tier weighting) → `ai_credibility_analyzer.py` (AI deep analysis for gray zone 30-85 scores)
- **Multi-dimensional Scoring**: `brand_scorer.py` (dimensions/weights from profile, safety capping is category-adaptive)
- **Report Layer**: `generate_report.py` (dynamic table headers + data source distribution stats, from profile dimension definitions)

## Multi-language & Multi-region Adaptation

**Core Principle**: This tool adapts to any language and region. The AI detects the user's language from their query and generates ALL region-specific configurations dynamically in the `category_profile`.

### Language Detection Rules

1. Detect the language of the user's query (Chinese, English, Japanese, Korean, etc.)
2. Infer the target market/region from context (e.g., Chinese query → China market; English query about "best vacuum" → likely US/UK market; Japanese query → Japan market)
3. ALL subsequent search queries, keywords, and report text MUST match the detected language and region
4. If the user explicitly mentions a region (e.g., "available in the UK", "sold on Amazon Japan"), use that region regardless of query language

### Regional Platform Mapping

The AI MUST generate appropriate platform configurations based on the detected region. Below are reference mappings (the AI should adapt these based on actual availability and relevance):

**China (zh-CN)**:
| Tier | Platforms | Examples |
|------|-----------|----------|
| L1 E-commerce | JD.com, Taobao, Pinduoduo | Review aggregation posts, follow-up reviews |
| L2 Social Comments | Xiaohongshu, Zhihu | "Debunking" comments under promotional posts |
| L3/L4 Forums | V2EX, Chiphell, NGA, Baidu Tieba, SMZDM, Douban, Bilibili | Community discussions, in-depth reviews |

**United States / English-speaking (en-US)**:
| Tier | Platforms | Examples |
|------|-----------|----------|
| L1 E-commerce | Amazon, Best Buy, Walmart | Verified purchase reviews, long-term reviews |
| L2 Social Comments | Reddit, YouTube comments | Comment sections debunking sponsored content |
| L3/L4 Forums | Reddit (subreddits), Head-Fi, AVSForum, Wirecutter comments, Slickdeals | Community discussions, enthusiast reviews |

**Japan (ja-JP)**:
| Tier | Platforms | Examples |
|------|-----------|----------|
| L1 E-commerce | Amazon.co.jp, Rakuten, Kakaku.com | Purchase reviews, price comparison reviews |
| L2 Social Comments | Twitter/X, note.com comments | Real user feedback under promotional content |
| L3/L4 Forums | Kakaku.com forums, 5ch, Price.com | Community discussions, expert reviews |

**South Korea (ko-KR)**:
| Tier | Platforms | Examples |
|------|-----------|----------|
| L1 E-commerce | Coupang, Naver Shopping | Purchase reviews |
| L2 Social Comments | Naver Blog comments, Instagram | Real feedback |
| L3/L4 Forums | DC Inside, Naver Cafe, Clien | Community discussions |

**Europe (various)**:
| Tier | Platforms | Examples |
|------|-----------|----------|
| L1 E-commerce | Amazon (regional), Trustpilot | Purchase reviews, trust scores |
| L2 Social Comments | Reddit, YouTube, regional social | Comment section feedback |
| L3/L4 Forums | Regional forums, Reddit (subreddits) | Community discussions |

### Regional Regulatory Authorities

Safety event searches must include the correct regulatory bodies for the target region:

| Region | Regulatory Bodies |
|--------|-------------------|
| China | SAMR (State Administration for Market Regulation), CFDA |
| US | FDA, CPSC, FTC |
| EU | EFSA, ECHA, national agencies |
| Japan | MHLW, CAA, NITE |
| South Korea | MFDS, KCA |

### Regional Marketing Signal Adaptation

Each region has different marketing manipulation patterns. The AI MUST generate region-appropriate marketing signals in `category_profile`:

**China**: SEO manipulation keywords (e.g., marketing buzzwords, "zhong cao/ba cao" patterns), fake review indicators, WeChat marketing patterns
**US/UK**: Affiliate link indicators, sponsored content disclaimers, Amazon vine/incentivized review patterns, influencer disclosure signals
**Japan**: Stealth marketing (ステマ) indicators, PR article patterns, affiliate blog signals
**Universal**: Excessive superlatives, zero-defect descriptions, brand-official language repetition

## Data Source Tier Strategy

**Problem**: Over-reliance on search-engine-indexable "post-type" content (forum answers, review articles) where the ad-to-content ratio is high. E-commerce platforms' real purchase reviews and social platforms' comment section feedback have higher information density and higher cost of astroturfing, but are dynamically loaded and cannot be directly indexed by search engines.

**Solution**: Use indirect search strategies (search for "review compilation posts", "follow-up review summaries", "negative review roundups", etc.) to access e-commerce reviews and comment section data.

| Data Source Tier | Source | Core Value | Base Credibility Weight |
|-----------------|--------|------------|------------------------|
| L1 E-commerce Reviews | Platform purchase reviews (indirect) | Real buyers with real money, long-term follow-up reviews | 0.85 |
| L2 Comment Sections | Social platform comment sections (indirect) | Real "debunking" feedback on promotional content | 0.75 |
| L3 Forum Posts | Community forums (per region) | Enthusiast deep experience, comparisons | Uses platform_relevance |
| L4 Independent Posts | Q&A platforms, review sites | Systematic review frameworks | Uses platform_relevance |

**Key Constraint**: E-commerce review layer and comment section layer searches should account for no less than 30% of total search volume.

## Workflow (7 Steps)

### Step 1: Interactive Requirements Confirmation

**Core Principle**: Research cannot be interrupted once started (time-consuming and token-intensive), so requirements must be confirmed before starting. Better to ask one more question than to research in the wrong direction.

**Mandatory Confirmation Items (MUST ask user if missing):**
- **Target Category**: What does the user want to buy? — Never assume the category
- **Budget Range**: What is the price range? — Never use a default budget
- **Core Use Case or Pain Point**: What is the main purpose? What matters most? — Never assume the need

**Conditional Confirmation Items (proactively ask when relevant):**
- When significant version/channel differences exist (e.g., domestic vs. import versions, regional variants) → confirm variant preference
- When brand preference is apparent → confirm whether to limit to specific brands
- When user needs are ambiguous → use multiple-choice questions to confirm

**Confirmation Format**: Use short multiple-choice or open questions, max 3 questions.

**After confirmation, output `task_config`** (for reference in subsequent steps):

```json
{
  "category": "category name",
  "budget_min": 2500,
  "budget_max": 3500,
  "currency": "USD",
  "locale": "en-US",
  "core_scenario": "gaming",
  "pain_points": ["cooling", "frame rate stability"],
  "excluded_brands": [],
  "preferred_brands": [],
  "variant_preference": "",
  "special_requirements": []
}
```

**Skip confirmation only if ALL conditions are met:**
1. Category is clear (e.g., "recommend a $200 gaming keyboard")
2. Budget is clear (has specific numbers or clear range)
3. Use case is clear (e.g., "for gaming", "for my baby")

### Step 1.5: AI Category-Adaptive Analysis

**Before searching**, generate `category_profile` JSON, strictly following this Schema:

```json
{
  "category": "<category name>",
  "category_type": "<food|durable_goods|electronics|personal_care|service|other>",
  "locale": "<locale code, e.g. en-US, zh-CN, ja-JP>",
  "language": "<language code, e.g. en, zh, ja>",
  "currency": "<currency code, e.g. USD, CNY, JPY>",
  "evaluation_dimensions": [
    {"name":"dimension name","weight":0.25,"description":"description","key_parameters":["param1"],"data_sources":["source"]}
  ],
  "pain_point_keywords": {"safety":[],"quality":[],"experience":[],"trust":[]},
  "safety_risk_types": {"critical":[],"high":[],"medium":[],"low":[]},
  "platform_relevance": {
    "<platform_key>": <weight 0.0-1.0>,
    "...": "..."
  },
  "regional_platforms": {
    "<platform_key>": {
      "name": "<display name>",
      "site": "<domain>",
      "description": "<role description>",
      "base_weight": 0.8
    }
  },
  "category_positive_signals": [{"pattern_description":"description","regex_hint":"regex","score":15,"label":"label"}],
  "has_variant_issue": false,
  "variant_types": [],
  "variant_search_keywords": [],
  "non_commercial_indicators": [],
  "commercial_bias_sources": [],
  "regulatory_authorities": ["<relevant regulatory bodies for this region>"],
  "marketing_signals": {
    "high_neg": ["<region-specific marketing buzzwords/phrases>"],
    "medium_neg": ["<region-specific promotional patterns>"],
    "low_neg": ["<region-specific clickbait patterns>"]
  },
  "authenticity_signals": {
    "long_term_use": ["<region-specific long-term use phrases, e.g. 'used for 6 months', '半年使用感受'>"],
    "defect_description": ["<region-specific defect/complaint terms>"],
    "purchase_proof": ["<region-specific purchase proof terms, e.g. 'verified purchase', '已购买'>"],
    "time_units": ["<region-specific time expressions>"]
  },
  "ecommerce_search_strategy": {
    "enabled": true,
    "primary_platforms": ["<region-appropriate e-commerce platforms>"],
    "search_templates": {
      "review_aggregation": ["[product] <region-appropriate review search terms>"],
      "negative_reviews": ["[product] <region-appropriate negative review search terms>"],
      "long_term_reviews": ["[product] <region-appropriate long-term review search terms>"]
    },
    "high_value_indicators": ["<region-appropriate follow-up review indicators>"],
    "low_value_indicators": ["<region-appropriate fake/incentivized review indicators>"]
  },
  "comment_section_strategy": {
    "enabled": true,
    "primary_platforms": ["<region-appropriate social platforms>"],
    "search_templates": {
      "debunk_feedback": ["[product] <region-appropriate debunking search terms>"],
      "experience_sharing": ["[product] <region-appropriate real experience search terms>"]
    },
    "high_value_indicators": ["<region-appropriate real comment indicators>"],
    "low_value_indicators": ["<region-appropriate astroturfing comment indicators>"]
  },
  "safety_search_config": {
    "general_keywords": ["<region-appropriate recall/safety terms>"],
    "regulatory_keywords": ["<region-appropriate regulatory terms>"],
    "source_domains": ["<region-appropriate regulatory/news domains>"]
  },
  "report_labels": {
    "recommend": "<region-language recommendation label>",
    "conditional_recommend": "<region-language conditional recommendation label>",
    "caution": "<region-language caution label>",
    "avoid": "<region-language avoid label>",
    "high_credibility": "<region-language high credibility label>",
    "medium_credibility": "<region-language medium credibility label>",
    "low_credibility": "<region-language low credibility label>",
    "suspected_ad": "<region-language suspected ad label>",
    "sufficient": "<data sufficiency label>",
    "mostly_sufficient": "<mostly sufficient label>",
    "insufficient": "<insufficient label>",
    "severely_insufficient": "<severely insufficient label>"
  }
}
```

**Constraints**: 3-6 dimensions, max 0.4 weight per dimension, weights sum to 1.0. Platform weights adjusted per category. `[product]` placeholders in search_templates are replaced with actual product names during search.

**CRITICAL**: The `regional_platforms`, `marketing_signals`, `authenticity_signals`, `ecommerce_search_strategy`, `comment_section_strategy`, `safety_search_config`, and `report_labels` fields are ALL dynamically generated by the AI based on the detected locale. They must be in the user's language and appropriate for the user's region. The scripts will read these from the profile and use them instead of hardcoded defaults.

### Step 2: Multi-layer Data Source Search (with E-commerce + Comment Section + Result Adaptation)

Search in 3 tiers from highest to lowest data source priority, ensuring high-value sources get priority coverage.

#### Step 2a: E-commerce Review Indirect Search (L1, ≥15% of total)

E-commerce platform reviews are dynamically loaded — search engines cannot directly index them. Use indirect strategies from `ecommerce_search_strategy.search_templates`.

Tag results with `source_layer: "L1_ecommerce"`, `base_weight: 0.85`.

#### Step 2b: Social Comment Section Indirect Search (L2, ≥15% of total)

Search for real "debunking" feedback in comment sections. Use templates from `comment_section_strategy.search_templates`.

Tag results with `source_layer: "L2_comment_section"`, `base_weight: 0.75`.

#### Step 2c: Forum Post + Independent Post Search (L3/L4, ≤70% of total)

**Full mode**: Use `web_search` + `site:` for targeted searches on platforms from `regional_platforms`.
**Fallback mode**: Use `python scripts/platform_search.py` or `python scripts/web_search_fallback.py --site [domain]` instead.

**Search Balance Strategy: 40% neutral + 20% positive + 40% negative.**

**Dual Time Window**: Each search group combines current year (instant window) + no year limit (historical window).

**Platform Priority**: Sort by `platform_relevance` weight, skip platforms with weight < 0.2.

**Search Keyword Construction** (in the user's language):
- Neutral: `[product] [category] review comparison [key_parameters]`
- Positive: `[product] [category] long-term use satisfied recommend`
- Negative: `[product] [category] [pain_point_keywords.quality/experience/trust]`

**Search Result Adaptation**:

| Sufficiency | Condition | Strategy |
|-------------|-----------|----------|
| Sufficient | Total ≥30 AND ≥5 per product | Proceed normally |
| Mostly Sufficient | Total ≥15 AND ≤1 product underserved | Supplement search for underserved product |
| Insufficient | Total <15 OR multiple products underserved | Remove site: restriction, expand time window, add platforms |
| Severely Insufficient | Total <8 | Niche category mode: lower scoring thresholds, note data limitations in report |

```bash
python scripts/platform_search.py "[query]" --adaptive \
    --candidate-products "Product A,Product B,Product C" \
    --category-profile category_profile.json
```

### Step 3: Content Fetching & Analysis

`web_fetch` to retrieve valuable posts (containing usage duration, multi-person discussion, no marketing keywords in title).

### Step 3.5: Category Parameter Structured Extraction

Extract structured parameter tables for candidate products based on `evaluation_dimensions[].key_parameters`.

### Step 4: Dynamic Deep Dive (with E-commerce Review Deep Dive)

Execute negative long-tail searches for high-frequency models, using keywords from `pain_point_keywords`.

**E-commerce review deep dive**: For each candidate model, execute additional e-commerce review searches using templates from the profile.

```bash
python scripts/deep_dive_search.py --auto-extract results.json --days 730 \
    --category-profile category_profile.json \
    --ecommerce-dive
```

### Step 4.5: Safety Event Search

**For each candidate brand**, search for safety events across the web. Two-tier classification: general layer (recall/death/removal) + category layer (`safety_risk_types`). Use keywords from `safety_search_config`.

```bash
python scripts/deep_dive_search.py "[brand]" --days 365 \
    --category-profile category_profile.json
```

### Step 5: Credibility Assessment

```bash
python scripts/credibility_scorer.py results.json --v2 --output scored.json --threshold 40 \
    --category-profile category_profile.json
```

**Scoring Architecture**: Regex pre-filter → Category signal injection (from profile) → AI semantic analysis (gray zone 30-85) → Weighted fusion

### Step 5.5: Evidence Conflict Arbitration

When the same product receives contradictory reviews from different sources:

```bash
python scripts/conflict_resolver.py scored.json \
    --category-profile category_profile.json \
    --output conflicts.json
```

Arbitration rules: Non-commercial sources > commercial sources, long-term feedback > short-term feedback, high credibility > low credibility.

### Step 6: Multi-dimensional Scoring

```bash
python scripts/brand_scorer.py scored.json \
    --category-profile category_profile.json \
    --safety-results safety.json \
    --output scores.json
```

| Score | Verdict |
|-------|---------|
| ≥70 | Recommend (use `report_labels.recommend`) |
| 55-69 | Conditional Recommend (use `report_labels.conditional_recommend`) |
| 40-54 | Caution (use `report_labels.caution`) |
| <40 | Avoid (use `report_labels.avoid`) |

Safety Capping: food (threshold 30) > personal_care (25) > electronics (20) > durable_goods (15)

### Step 7: Report Generation

```bash
python scripts/generate_report.py scored.json \
    --query "[category]" --budget [budget] --pain-point "[pain point]" \
    --category-profile category_profile.json \
    --brand-scores scores.json \
    --output report.md
```

**The report MUST be written in the user's language** (as specified by `category_profile.language`). All section headers, verdicts, labels, and analysis text must match the user's language.

## Key Rules (Non-skippable)

1. **Confirm requirements before searching** — Budget, category, and use case are all mandatory; ask user if any are missing
2. **Never assume user needs** — If user says "recommend a phone" without budget or use case, ask first
3. **Generate category_profile before searching** — It is the foundation for all subsequent steps
4. **Search twice** — After broad search, always do targeted negative deep dive on high-frequency models
5. **Append year to searches** — Include current year and previous year
6. **Negative search ratio ≥40%** — Actively search for negatives; finding none means search depth is insufficient
7. **Safety events MUST be searched** — Top recommended brands must pass safety event screening
8. **Adapt search results** — Expand when insufficient, trim when excessive
9. **High-engagement content needs scrutiny** — High upvotes/likes ≠ authenticity (applies to Zhihu, Reddit, etc.)
10. **Prioritize long-term feedback** — "Used for 2 years" is 10x more valuable than "just bought, looks great"
11. **Cross-validation is core** — Commercial review says good + niche forum complains → trust the latter
12. **Profile is the sole category knowledge source** — Script hardcoded values are only fallback
13. **E-commerce review layer is mandatory** — Every research must include e-commerce review indirect search (L1), ≥15% of total
14. **Comment section layer is mandatory** — Every research must include social comment section search (L2), ≥15% of total
15. **Follow-up reviews > unboxing** — Long-term follow-up reviews (3+ months) are far more valuable than unboxing reviews
16. **Comment sections > post body** — Real "debunking" feedback in comment sections takes priority over the post's own conclusions
17. **Match user's language throughout** — ALL search queries, scoring labels, and the final report MUST be in the user's language
