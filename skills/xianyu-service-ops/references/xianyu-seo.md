# Xianyu Search Ranking and Recommendation Traffic Mechanics

> This document summarizes platform mechanisms that are **directly verifiable from public sources**. Claims that cannot be verified — such as specific weight percentages or definitive boost/penalty rules — are labeled 🔴 with an explicit note that no public evidence supports them. Source coverage focuses on **2024–2026**, with earlier official technical articles cited where they explain foundational architecture and core signals.
>
> Evidence grades: 🔵 Official docs / official tech team publications (including disclosed metrics and A/B results) | 🟢 Empirically tested with reproducible data | 🟡 Multi-person consensus without hard data | 🔴 Unverified / speculative

---

## 1. Search Ranking

### Recall: How the Platform Decides Your Listing Is Findable

🔵 Xianyu search uses **dual-channel recall**:
1. **Text matching** (inverted index): keyword-based matching against titles and descriptions
2. **Vector matching** (neural network semantic recall): similarity matching based on semantic understanding

This means: title keywords are foundational, but they're **not the only recall entry point**. The platform also expands recall via query rewriting, OCR text extraction from listing images, and similar-item information enrichment.

**What this means for sellers:**
- Title keywords remain the most direct entry point and must cover core search terms
- Text in images may be OCR-indexed and used for matching
- The platform "understands" meaning — it doesn't just do literal keyword matching

### Ranking: How the Platform Decides Your Position

🔵 Search ranking is **multi-factor**, with three categories of factors explicitly named in official technical articles:
1. **Conversion efficiency factors** — the listing's demonstrated ability to generate transactions
2. **Relevance factors** — how well the listing matches the user's search query
3. **Business rules** — platform-side policy interventions (e.g., diversity shuffling)

🔵 Relevance uses a **tiered strategy (3 tiers)**: listings are first bucketed by relevance into high / medium / low, then ranked by conversion efficiency within each tier. This means: **relevance is the entry requirement; conversion efficiency determines rank within tier**.

### Confirmed Relevance Features

🔵 The platform's relevance model uses at least three categories of features:

| Feature type | What it includes |
|-------------|-----------------|
| Structural / base matching | Category match, key attribute matching (product type / brand / model) |
| Text matching | Term match count, match rate, synonym matching, term weight, BM25 |
| Semantic matching | Click behavior representation matching, text semantic matching, multimodal semantic matching |

**What this means for sellers:**
- **Getting the category right** is the foundation of structural matching — wrong category = relevance tier drops immediately
- Keyword "match rate" in the title matters (precision over quantity — don't just add more terms)
- The platform does synonym matching, so not every near-synonym needs to be in the title
- Multimodal semantics means image quality may also factor into relevance scoring

### Non-Personalized Sort Options

🔵 Users can manually switch sort order in search results: by credit / price / most recently active / nearest distance. This indicates:
- The platform has a "credit" dimension in its sorting capability (at least in manual sort mode)
- "Most recently active" exists as an explicit sort dimension

### Common Operator Claims That Lack Evidence

🔴 **"Title matching 40% / activity 30% / account weight 20% / transaction data 10%"** — these precise weight breakdowns circulate widely but cannot be traced to any official document or technical article. Do not treat them as real weights.

🔴 **Whether keyword order affects ranking** — not publicly disclosed. Term-level feature processing is confirmed, but claims like "first keyword outweighs last" are unsubstantiated.

🔴 **"Re-editing / refreshing a listing = new-item boost"** — the platform has "new item recommendation" and "new listings" tabs, but "editing an old listing = treated as new by the algorithm" is not confirmed in any official technical document.

🔴 **Whether "want" count or saves directly affect search ranking** — confirmed that recommendation and search use behavioral interaction data in modeling, but whether the specific "wants" or "saves" fields are used this way is not publicly disclosed.

---

## 2. Recommendation Traffic (Feed / "You Might Like")

### Recommendation System Pipeline

🔵 Full pipeline:
```
Trigger (user browse / click / interaction history)
  → Recall (billions of candidates → tens of thousands): i2i, x2i (title tokenization + tag/class/query), deep recall (vector ANN)
  → Coarse ranking (lightweight models like dual-tower)
  → Fine ranking (more cross-features + complex models)
  → Re-ranking (business interventions: category diversity, price diversity, etc.)
```

🔵 Data used in recommendations:
- User baseline information (age / gender / region)
- Listing / content structured data
- Behavioral data (impressions / clicks / interactions)

### Ranking Objectives

🔵 Recommendation ranking uses a **multi-objective model**, including at least:
- **CTR** (click-through rate)
- **CVR** (conversion rate)
- **Interaction objectives**

Scene-level weighting and boosting/suppression expressions are configurable per context.

**What this means for sellers:** The recommendation system optimizes for both clicks and conversions simultaneously. Listings that attract clicks but don't convert will perform progressively worse in recommendations.

### The Satisfaction Gate for Recommendation Triggers

🔵 In feed/discovery scenes, Xianyu uses a satisfaction-triggered mechanism:
- Recommendation display only triggers when the user's click "satisfaction" on the current item is high enough
- Satisfaction signals: **dwell time** + **detail page behavior** (viewing specs, reading reviews, chatting with the seller, etc.)

🔵 Quantified results from this mechanism: while preserving 94.4% of click volume and 96% of secondary-click volume, request volume dropped by 28%, CTR improved by +31.1%, and conversion rate improved by +10%.

**What this means for sellers:** The recommendation system penalizes clickbait. If a buyer clicks your listing but leaves immediately (short dwell time, no deep page interactions), this not only fails to trigger further recommendations — it may actively reduce subsequent distribution. **Detail page quality directly affects recommendation traffic.**

### Search vs. Recommendation Importance

🔵 Official technical article explicitly states: **"Xianyu search is the largest transaction entry point in the Xianyu app — search accounts for more than half of all transaction attribution."**

🔴 The specific share of recommendation traffic (feed / "you might like") has no stable official figure available.

🔴 **Whether video thumbnails provide a definitive traffic boost** — no direct conclusion or A/B data found in accessible official docs and technical articles.

---

## 3. Account System

### Confirmed Mechanisms

🔵 Xianyu has two traffic-related systems operating at the account/content level:
1. **Content safety algorithm**: covers text/image/audio/video; high-confidence cases handled automatically, low-confidence cases go to human review
2. **Violation handling rules**: includes deletion/hiding of content, account point deductions, suspension of partial or full services

🔵 The platform reserves the right to flag "data anomalies" as violations: the terms of service state that the platform can compare user data against aggregate user data to determine whether a violation has occurred.

🔵 "Credit" is one of the available non-personalized sort dimensions (users can manually switch to sort by credit).

### Unconfirmed Claims

🔴 **"Zhima Credit 750+ gets 3× the impressions of 600 and below"** — no verifiable source

🔴 **"How large is the gap between new and established accounts"** — no public data

🔴 **"Specific weighting of positive review rate / reply rate"** — not officially disclosed

🔴 **"Service score 4.2/4.5/4.8 corresponds to 5%/10%/20% traffic support"** — no verifiable Xianyu rule document or official announcement found

---

## 4. Keywords and Title Processing

🔵 Both the search and recommendation pipelines use **tokenization**:
- Search side: query tokenization with weighted term summation
- Recommendation side: listing title tokenization combined with tag/class/brand/query to build an inverted index (x2i recall)

🔵 Search relevance uses **BM25** and similar classical text matching algorithms as features.

🔵 **Synonym matching** is in place — you don't need to include every near-synonym in the title.

🔴 Whether keyword order affects matching weight — not publicly disclosed.

---

## 5. Service Category Specifics

🔵 Virtual service listings use the **same retrieval/recommendation framework** as physical goods — the algorithm documentation consistently uses "products or service information" as its subject.

🔵 **Category selection matters**: category matching is a structural relevance feature, and recommendation re-ranking does category diversity shuffling — meaning category affects both the probability of being judged relevant, and how your listing is distributed alongside competitors.

🔴 Whether service listings vs. physical goods listings have different weight models or preferential treatment — no public evidence.

---

## 6. 2024–2026 Trends

🔵 **AI is deeply embedded**:
- AI smart search / AI market intel covers 45 million users; AI-facilitated transaction value exceeded ¥10 billion
- AI-assisted listing text has an 87% adoption rate; 230 million listings published using AI tools
- AI listing management has covered 66 million listings; inquiry-to-payment conversion improved by 13%

🔵 **Generative Semantic IDs (GSID)**: large model multimodal understanding encodes each listing as a "digital fingerprint" for finer-grained attribute capture and transaction matching — a new dimension beyond traditional category + keywords.

🔵 The Xianyu user service agreement (2025 update) formally classifies "AI publishing" and "AI management" as Xianyu AI Services, confirming AI's deep integration into both supply (publishing) and distribution (recommendation) as a permanent direction.

**What this means for sellers:**
- The platform is shifting from "keyword matching" toward "semantic understanding + multimodal matching"
- The high AI publishing adoption rate indicates the platform is pushing toward standardized content production
- Long-term, "content quality" (completeness and professionalism of images and descriptions) will have growing influence on both matching and recommendation

---

## Actionable Recommendations (based on 🔵-grade evidence only)

1. **Title keyword coverage of core search terms is non-negotiable** — but don't stuff near-synonyms (the platform does synonym matching)
2. **Right category > well-written title**: category is a structural relevance feature; wrong category = immediate tier drop
3. **Conversion efficiency is the core ranking driver**: relevance is the threshold, conversion efficiency determines your position within tier — improving conversion rate matters more than chasing impressions
4. **Detail page quality affects recommendation**: dwell time and detail page depth behavior are recommendation satisfaction signals
5. **Search is still the primary transaction entry point (>50%)**: don't abandon search optimization to chase recommendation traffic
6. **Images may be OCR-indexed**: text in your main image and detail images is a potential matching signal
7. **Common claims like "refresh boost," "Zhima Credit weighting," and "video thumbnail boost" lack hard evidence**: worth experimenting, but don't build core strategy on these assumptions
