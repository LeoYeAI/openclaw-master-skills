# Anti-SEO Deep Consumer Researcher — Detailed Reference Manual

> This document supplements SKILL.md. The AI only needs SKILL.md for the core workflow; consult this document for uncertain details.

## 1. category_profile Design Reference

### Field Design Intent

**locale / language / currency**: Drive ALL region-specific behavior. The AI detects these from the user's query and sets them in the profile. Every downstream script reads these fields to determine which platform configs, search templates, and labels to use.

**evaluation_dimensions**: AI generates based on the category's consumer decision logic. 3-6 dimensions, max 0.4 weight per dimension, all weights must sum to 1.0. Each dimension includes key_parameters (specific parameters to collect) and data_sources (best data sources for this dimension).

**platform_relevance**: AI dynamically adjusts each platform's credibility weight based on category. Different categories have very different discussion ecosystems:
- Tech/digital: Enthusiast forums get highest weight (Chiphell/Head-Fi/AVSForum)
- Beauty/skincare: Social platforms get higher weight (Xiaohongshu/Reddit r/SkincareAddiction)
- Baby products: Parenting communities get higher weight (BabyCenter/Tieba mom forums)

**regional_platforms**: The AI generates this based on detected locale. This is the most critical regionalization field — it defines which platforms exist in the user's market, their domains for `site:` searches, and their base credibility weights.

**marketing_signals**: Region-specific manipulation patterns. Each region has different advertising tactics:
- China: "zhong cao" (种草) culture, WeChat marketing, fake review patterns
- US: Affiliate disclaimers, Amazon Vine, influencer partnerships
- Japan: Stealth marketing (ステマ), PR articles
- Universal: Excessive superlatives, zero-defect reviews, brand-voice mimicry

**authenticity_signals**: Region-specific indicators of genuine reviews:
- Long-term use phrases in the target language
- Defect/complaint vocabulary
- Purchase proof terms
- Time unit expressions

**ecommerce_search_strategy**: E-commerce review indirect search strategy. AI generates platform-appropriate templates:
- `primary_platforms`: Regional e-commerce platforms (JD/Taobao for China, Amazon for US, Rakuten for Japan)
- `search_templates`: Three categories — `review_aggregation`, `negative_reviews`, `long_term_reviews`
- `high_value_indicators`: Follow-up review signals in target language
- `low_value_indicators`: Fake/incentivized review indicators in target language

**comment_section_strategy**: Social comment section indirect search strategy:
- `primary_platforms`: Regional social platforms (Xiaohongshu/Zhihu for China, Reddit/YouTube for US)
- `search_templates`: Two categories — `debunk_feedback`, `experience_sharing`

**report_labels**: All UI-facing text labels in the user's language. Scripts use these for output instead of hardcoded strings.

**safety_search_config**: Region-specific safety search configuration:
- `general_keywords`: Recall/safety terms in target language
- `regulatory_keywords`: Regional regulatory body names
- `source_domains`: Authoritative regulatory and news domains for the region

### Category Examples by Region

**Food (Baby Formula) — China Market**:
- Dimensions: Formula quality 30% / Safety record 25% / Real user feedback 25% / Value 20%
- safety_risk_types.critical: Cronobacter sakazakii, Bacillus cereus, melamine
- regulatory_authorities: SAMR, CFDA
- ecommerce: JD.com, Taobao follow-up reviews

**Food (Baby Formula) — US Market**:
- Dimensions: Ingredients quality 30% / Safety record 25% / Real user feedback 25% / Value 20%
- safety_risk_types.critical: Cronobacter contamination, heavy metals, FDA recall
- regulatory_authorities: FDA, CPSC
- ecommerce: Amazon verified purchase reviews, Walmart reviews

**Electronics (Phone) — Global**:
- Dimensions: Performance 30% / Display 20% / Battery 20% / Build quality 15% / Value 15%
- safety_risk_types.critical: Battery fire, explosion, overheating
- Enthusiast forums: Chiphell (CN), XDA/Reddit (US), Kakaku (JP)

**Durable Goods (Ergonomic Chair) — China Market**:
- Dimensions: Ergonomic design / Material & build / Safety & durability / Comfort / Value
- safety_risk_types.critical: Gas cylinder explosion, seat collapse
- Forums: V2EX, Chiphell (CN)

**Durable Goods (Office Chair) — US Market**:
- Dimensions: Ergonomic design / Material & build / Durability / Comfort / Value
- safety_risk_types.critical: Gas cylinder failure, tilt mechanism failure
- Forums: Reddit r/officechairs, Reddit r/ErgonomicSetups

### E-commerce Search Strategy Differences by Category

**High-ticket Durables (chairs/appliances/mattresses)**:
- Follow-up reviews are extremely valuable — 3-6 month post-purchase reviews
- Focus search: "[model] long-term review 6 months problems"
- high_value_indicators: "follow-up review", "update after 6 months", "long-term use"

**FMCG (formula/snacks/toiletries)**:
- Follow-up review value is moderate — short use cycle
- Focus search: "[brand] negative review allergy adverse reaction"
- Safety signals in negative reviews are most important

**Digital Products (phones/headphones/monitors)**:
- Negative reviews and follow-up reviews both highly valuable
- Focus search: "[model] review defect quality customer service"

**Beauty/Personal Care (skincare/cosmetics)**:
- Social comment sections > e-commerce reviews (more detailed usage feelings)
- Allergy information in negative reviews is critical

## 2. Search Strategy Reference

### Search Keyword Construction Templates (adapt to user's language)

**Neutral factual search (40%)**:
```
[product] [category] review comparison specs
[product] [category] [key_parameters]
```

**Positive experience search (20%)**:
```
[product] [category] long-term use satisfied recommend
```

**Negative experience search (40%)**:
```
[product] [category] [pain_point_keywords.quality]
[product] [category] [pain_point_keywords.experience]
[product] [category] [pain_point_keywords.trust]
```

### Platform Search Command Templates

```
# High-credibility platforms (sort by category weight, use platforms from regional_platforms)
web_search("site:<platform_domain> [category] [pain point keywords]")

# Year-appended instant window
web_search("site:<platform_domain> [category] [pain point keywords] 2026")
web_search("[category] [safety keywords] 2026 2025")
```

### Safety Event Search Templates

```
# General safety keywords (from safety_search_config.general_keywords)
web_search("[brand] recall withdrawn banned [year]")
web_search("[brand] safety issue warning")

# Regulatory keywords (from safety_search_config.regulatory_keywords)
web_search("[brand] [regulatory_body] notice penalty")

# Category-specific safety keywords (from safety_risk_types.critical)
web_search("[brand] [critical_safety_risk]")
```

## 3. Safety Event Classification

### General Layer (category-independent)

| Level | Trigger Keywords |
|-------|-----------------|
| CRITICAL | Global recall, death, mass recall, FDA warning, forced removal |
| HIGH | Recall, removal, ban, regulatory notice, failed testing, exceeds limits |
| MEDIUM | Rectification, resolved, historical issue |
| LOW | Complaint, foreign object, odor, controversy, questioning |

### Category Layer (from category_profile.safety_risk_types)

Different categories have different critical safety risks — these are defined in the profile and vary by region.

### Safety Capping Rules

When safety score falls below threshold, overall score is capped at 54:
- food: threshold 30
- personal_care: threshold 25
- electronics: threshold 20
- durable_goods: threshold 15

### Source Type Classification

Safety event search results are classified by source:
- official_announcement: Regulatory bodies (highest weight)
- safety_alert: Recall notices
- news_report: News media
- community_discussion: Community discussion
- ecommerce_review: E-commerce reviews

## 4. Report Output Format

```markdown
## Safety Risk Warning (only appears when safety events are found)
> The following brands had potential risk information in safety event searches

## Product Scores
<!-- Table headers dynamically generated from category_profile.evaluation_dimensions -->
| Product | [Dim 1] | [Dim 2] | ... | Safety | Overall | Confidence | Verdict |

## Research Conclusions
After filtering X suspected ad posts, based on Y real user reviews, recommendations are:

**Recommend: [model]** (score XX, verdict: Recommend)
- Reasons + real user quotes
- Known defects
- Source links

**Avoid: [model]** (score XX, verdict: Avoid)
- Reasons + quotes
- Ad content ratio

## Category Parameter Comparison
<!-- Headers from evaluation_dimensions[].key_parameters -->

## Data Transparency
- Searched N platforms, retrieved M results
- Filtered X suspected ads
- Y real reviews included in analysis
- AI deep-analyzed Z posts
- W safety-related results found
```

## 5. Credibility Scoring Reference

### AI Semantic Analysis 5 Dimensions

| Dimension | Assessment | Full Score Indicator | Zero Score Indicator |
|-----------|-----------|---------------------|---------------------|
| Tone Authenticity | Is language natural/colloquial? | Personal emotion, hesitation, uncertainty | Highly standardized, template writing |
| Narrative Logic | Is narrative natural and flowing? | Timeline clues, cause-effect logic | Feature-by-feature listing, like a spec sheet |
| Detail Richness | Are there unique personal details? | Specific use scenarios, precise timing | Only public specs |
| Emotional Consistency | Do emotions match content? | Genuine trade-offs and weighing | One-sided, trivial "cons" (fake defects) |
| Interest Disclosure | Any commercial guidance? | No links, no coupons, no promotion | Clear commercial partnership signs |

### AI Cost Control

| Strategy | Description | Expected Effect |
|----------|-------------|----------------|
| Gray zone filter | Only invoke AI for regex scores 30-85 | ~40-50% fewer AI calls |
| Batch cap | Max 20 posts per research session | Cost ceiling |
| Cache | Cache analysis results by URL in local JSON | Zero cost on repeat research |
