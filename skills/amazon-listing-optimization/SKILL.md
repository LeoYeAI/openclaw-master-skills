---
name: amazon-listing-optimization
description: "Amazon listing builder and optimizer for sellers. Two modes: (A) Create — build keyword-optimized listings from scratch using keyword lists + product characteristics + AI copywriting, (B) Optimize — audit existing listings, find keyword gaps, score across 8 dimensions, and rewrite with missing keywords. Integrates with amazon-keyword-research for keyword input. Works on 12 Amazon marketplaces. No API key required. Use when: (1) creating a new Amazon listing from keywords, (2) auditing an existing listing for SEO and conversion, (3) checking keyword coverage in title/bullets/description, (4) generating listing copy with target keywords and tone, (5) comparing listings against competitors, (6) preparing a listing for launch or relaunch."
metadata: {"clawdbot":{"emoji":"📝"}}
---

# Amazon Listing Optimization 📝

Build keyword-optimized listings from scratch, or audit and optimize existing ones. No API key — works out of the box.

## Installation

```bash
npx skills add nexscope-ai/Amazon-Skills --skill amazon-listing-optimization -g
```

## Two Modes

| Mode | When to Use | Input | Output |
|------|-------------|-------|--------|
| **A — Create** | Building a new listing | Keywords and/or competitor ASINs + product info + tone | Full listing copy + keyword coverage score |
| **B — Optimize** | Improving an existing listing | Your ASIN or URL (+ optional keywords or competitor ASINs) | Optimized listing copy + audit report + gap analysis |

## Mode A — Three Ways to Start

| Input Source | How it Works |
|-------------|-------------|
| **Keywords** | User provides keyword list → skill prioritizes and generates listing |
| **Competitor ASINs** | User provides 1-3 competitor ASINs → skill fetches their listings, extracts their keywords, then generates a listing that covers all their keywords and more |
| **Both** | User provides keywords + competitor ASINs → skill merges both sources for maximum coverage |

## Capabilities

- **Keyword-driven listing generation**: Import keywords (from amazon-keyword-research, manual list, or extracted from competitor ASINs), rank by priority, generate copy that maximizes keyword coverage
- **Competitor keyword extraction**: Fetch competitor listings and automatically extract their title/bullet keywords as your baseline
- **8-dimension audit & scoring**: Title, bullets, description, images, A+ content, pricing, reviews, SEO coverage
- **Keyword coverage tracking**: Visual map showing which keywords appear in title / bullets / description / missing
- **Tone selection**: Professional, Friendly, Urgent, Luxury — affects AI copywriting style
- **Competitive benchmarking**: Compare your listing against competitors
- **Multi-marketplace**: US, UK, DE, FR, IT, ES, JP, CA, AU, IN, MX, BR

## Usage Examples

### Mode A — Create from Keywords

```
Create a listing for a portable blender. Keywords: portable blender, smoothie maker, USB rechargeable, travel blender, personal blender. Material: BPA-free Tritan. Color: White. Capacity: 380ml. Tone: Friendly.
```

```
I have these keywords from my research: [paste keyword list]. Product: silicone kitchen utensil set, 12 pieces, heat resistant to 480°F. Generate a full listing.
```

### Mode A — Create from Competitor ASINs

```
I want to sell a dog t-shirt on Amazon US. Here are 3 competitors I want to beat: B0D72TSM62, B0ABC12345, B0XYZ67890. My product is 100% cotton, 6 colors, XS-XL, funny print. Analyze their listings and create one that's better. Friendly tone.
```

```
Create a listing for my yoga mat. Look at this competitor: B09V3KXJPB. Extract their keywords, find what they're missing, and build a listing that covers more keywords than them. Product: 6mm TPE, non-slip, carrying strap included. Tone: Professional.
```

### Mode A — Create from Keywords + Competitor ASINs

```
Use amazon-keyword-research to find keywords for "portable blender", also analyze these competitors: B0CPY1GFVZ, B0CXLF3Y19. Combine all keywords and create a listing. Product: 380ml, USB-C, BPA-free Tritan. Tone: Professional.
```

### Mode B — Optimize Existing

```
Audit the listing for ASIN B0D72TSM62 on Amazon US
```

```
Optimize B0D72TSM62 using these keywords: dog shirt, pet clothes, puppy clothing — show me what's missing and rewrite
```

```
Optimize my listing B0D72TSM62 by analyzing these competitors: B0ABC12345, B0XYZ67890. Find what keywords they have that I don't, and rewrite my listing to beat them.
```

---

## Mode A Workflow — Create Listing from Keywords

### Step A1: Collect Keywords

Keywords can come from four sources (use one or combine multiple):

1. **From [amazon-keyword-research](https://github.com/nexscope-ai/Amazon-Skills/tree/main/amazon-keyword-research) skill** (recommended): Run keyword research first, then feed results directly. Install: `npx skills add nexscope-ai/Amazon-Skills --skill amazon-keyword-research -g`
2. **From competitor ASINs**: User provides 1-3 competitor ASINs → run `<skill>/scripts/fetch-listing.sh` on each → extract keywords from their titles, bullets, and descriptions → use as your keyword baseline. This is the fastest way to start — you inherit what's already working for competitors, then add more.
3. **From user's keyword list**: User pastes their own keyword list (e.g. from Helium 10 Cerebro, Jungle Scout, or manual research)
4. **Auto-discover**: Use `web_search` to find top keywords for the product category

When competitor ASINs are provided, always fetch and analyze them first. Extract every meaningful keyword from their titles and bullets, then merge with any user-provided keywords. The goal: cover everything competitors cover, plus keywords they missed.

### Step A2: Prioritize Keywords

Organize keywords into tiers:

```
🔴 Primary (must appear in Title):
  - [keyword] — [search volume if known]
  - [keyword] — [search volume if known]

🟡 Secondary (must appear in Bullets):
  - [keyword]
  - [keyword]

🟢 Tertiary (should appear in Description or Backend):
  - [keyword]
  - [keyword]

⚪ Long-tail (use where natural):
  - [keyword phrase]
  - [keyword phrase]
```

Priority rules:
- Highest search volume → Title (front-loaded)
- Medium volume + high relevance → Bullets (one primary keyword per bullet)
- Lower volume / long-tail → Description
- Remaining → Backend search terms (advise seller to add in Seller Central)

### Step A3: Collect Product Characteristics

Ask or extract from user input:
- **Product name / type**
- **Brand name**
- **Key attributes**: Material, color, size, weight, capacity, quantity
- **Key features**: What makes it different (3-5 features)
- **Target audience**: Who buys this?
- **Use cases**: Top 3 scenarios
- **What's in the box**: Everything included

### Step A4: Select Tone

| Tone | Style | Best for |
|------|-------|----------|
| **Professional** | Authoritative, spec-focused, trust-building | Electronics, tools, B2B |
| **Friendly** | Conversational, benefit-focused, relatable | Kitchen, lifestyle, gifts |
| **Urgent** | Scarcity-driven, action words, problem-solving | Health, safety, seasonal |
| **Luxury** | Premium, sensory language, exclusivity | Beauty, fashion, premium goods |

Default: **Professional** if not specified.

### Step A5: Generate Listing Copy

Generate each component following these rules:

**Title (max 200 characters):**
- Format: `[Brand] + [Primary Keyword] + [Key Attribute 1] + [Key Attribute 2] + [Secondary Keyword] + [Differentiator]`
- Primary keyword as close to the front as possible (after brand)
- No ALL CAPS except brand name
- No promotional claims ("best", "#1", "top rated")
- Include size/color/quantity if relevant to search

**Bullet Points (5 bullets, max 500 chars each):**
- Each bullet: `[BENEFIT HEADER IN CAPS] — [Benefit explanation with keyword naturally embedded]`
- Bullet 1: Primary feature + primary keyword
- Bullet 2: Key use case + secondary keyword
- Bullet 3: Quality/material + trust signal
- Bullet 4: What's included / compatibility
- Bullet 5: Guarantee / differentiator / social proof hint
- Each bullet should contain at least 1 target keyword

**Description (max 2000 characters):**
- Opening: Problem/pain point the product solves
- Middle: Features → benefits (expand on bullets, don't repeat verbatim)
- Close: Call to action + what's in the box
- Embed remaining keywords not used in title/bullets
- Use line breaks for readability

### Step A6: Keyword Coverage Score

After generating, produce a coverage map:

```
## Keyword Coverage Report

| Keyword | Volume | In Title? | In Bullets? | In Description? | Status |
|---------|--------|-----------|-------------|-----------------|--------|
| portable blender | 45,000 | ✅ | ✅ | ✅ | 🟢 Covered |
| smoothie maker | 22,000 | ❌ | ✅ | ✅ | 🟡 Add to title |
| USB rechargeable | 18,000 | ✅ | ✅ | ❌ | 🟢 Covered |
| travel blender | 12,000 | ❌ | ❌ | ✅ | 🟡 Add to bullets |
| mini blender | 8,000 | ❌ | ❌ | ❌ | 🔴 Missing |

Coverage: 18/22 keywords (82%)
Title keywords: 6/8 slots used
Bullet keywords: 12/15 target keywords covered
Uncovered → recommend for Backend Search Terms
```

**Scoring:**
- 🟢 90%+ coverage = Excellent
- 🟡 70-89% = Good, minor gaps
- 🔴 <70% = Needs work, significant keywords missing

---

## Mode B Workflow — Optimize Existing Listing

### Step B1: Fetch Listing Data

Run the bundled script:

```bash
<skill>/scripts/fetch-listing.sh "<ASIN>" [marketplace]
```

**Parameters:**
- `ASIN` (required): e.g. B09V3KXJPB
- `marketplace` (optional): `us` (default), `uk`, `de`, `fr`, `it`, `es`, `jp`, `ca`, `au`, `in`, `mx`, `br`

**Extracts:** Title, brand, price, bullet points, description, image count, A+ content presence, rating, review count, BSR, categories, date first available.

If script returns incomplete data, fall back to `web_fetch` on the product URL.

### Step B2: Discover Target Keywords

If user provides keywords, use those. Otherwise, auto-discover:

1. Extract apparent keywords from current title and bullets
2. Run `web_search` for `site:amazon.com "[product type]"` to find competitors
3. Extract keywords from top 3 competitor titles and bullets
4. (Optional) Chain with `amazon-keyword-research` skill for deeper analysis
5. Compile a combined keyword list with estimated priority

### Step B3: Keyword Gap Analysis

Compare current listing against target keywords:

```
## Keyword Gap Analysis: [ASIN]

### ✅ Keywords Found in Listing
| Keyword | In Title | In Bullets | In Description |
|---------|----------|------------|----------------|
| [kw] | ✅ | ✅ | ❌ |

### ❌ Missing Keywords (Competitors Have, You Don't)
| Keyword | Competitor 1 | Competitor 2 | Competitor 3 | Priority |
|---------|-------------|-------------|-------------|----------|
| [kw] | ✅ Title | ✅ Bullet | ❌ | 🔴 High |

### Coverage: X/Y keywords (Z%)
```

### Step B4: 8-Dimension Audit

Score each on the scale shown, with keyword integration factored in:

| Dimension | Max Score | Key Criteria |
|-----------|-----------|-------------|
| **Title** | /15 | Primary keyword near front? Brand? Attributes? Under 200 chars? Not truncated on mobile? |
| **Bullet Points** | /15 | All 5 used? Benefit-first? Keywords embedded naturally? Under 500 chars each? |
| **Images** | /15 | 7+ images? White bg main? Infographic? Lifestyle? Size ref? Video? |
| **A+ Content** | /10 | Present? Brand story? Comparison chart? Lifestyle imagery? |
| **Description** | /10 | Keywords not in title/bullets? Readable? Problem→solution flow? |
| **Pricing** | /10 | Competitive? Coupon/deal present? |
| **Reviews** | /15 | 4.0+ stars? 100+ reviews? Recent reviews positive? |
| **SEO Coverage** | /10 | Primary kw in title+bullets+desc? Long-tail present? No wasted repeats? **Keyword coverage %** |

### Step B5: Generate Optimized Copy

Rewrite the listing incorporating missing keywords:
- Show **before vs after** for each component
- Highlight which keywords were added and where
- Maintain the brand's existing tone unless a different tone is requested

---

## Output Formats

The primary deliverable is always a **ready-to-use listing** that the seller can copy-paste directly into Seller Central. Diagnostic data (scores, keyword analysis) comes after as supporting evidence.

### Mode A Output — New Listing

```
# ✅ Your Listing — Ready to Use

## Title
[title text — copy this directly into Seller Central]

## Bullet Points
1. [BENEFIT HEADER] — [text with keyword]
2. [BENEFIT HEADER] — [text with keyword]
3. [BENEFIT HEADER] — [text with keyword]
4. [BENEFIT HEADER] — [text with keyword]
5. [BENEFIT HEADER] — [text with keyword]

## Description
[description text — copy this directly into Seller Central]

## Backend Search Terms
[comma-separated keywords to paste into Seller Central → Keywords → Search Terms]

---

# 📊 How We Built This Listing (Diagnostic)

**Marketplace:** Amazon [XX] | **Tone:** [tone] | **Keywords imported:** [count]
**Title characters:** [X]/200 | **Description characters:** [X]/2000

## Keyword Coverage: [X]%

| Keyword | Volume | In Title | In Bullets | In Description | Status |
|---------|--------|----------|------------|----------------|--------|
| [kw] | [vol] | ✅/❌ | ✅/❌ | ✅/❌ | 🟢🟡🔴 |

## Keyword Priority Breakdown
🔴 Primary (Title): [list]
🟡 Secondary (Bullets): [list]
🟢 Tertiary (Description): [list]
⚪ Backend: [list]
```

### Mode B Output — Audit + Optimized Listing

```
# ✅ Optimized Listing — Ready to Use

## Title
[optimized title — copy this directly into Seller Central]

## Bullet Points
1. [BENEFIT HEADER] — [optimized text]
2. [BENEFIT HEADER] — [optimized text]
3. [BENEFIT HEADER] — [optimized text]
4. [BENEFIT HEADER] — [optimized text]
5. [BENEFIT HEADER] — [optimized text]

## Description
[optimized description — copy this directly into Seller Central]

## Backend Search Terms
[comma-separated keywords to paste into Seller Central → Keywords → Search Terms]

---

# 📊 Audit Report: [ASIN]

**Product:** [title] | **Brand:** [brand]
**Price:** [price] | **Rating:** [stars] ([count] reviews)

## Score: [X/100] → [Y/100] (after optimization)

| Dimension | Before | After | Key Change |
|-----------|--------|-------|-----------|
| Title | /15 | /15 | [what changed] |
| Bullet Points | /15 | /15 | [what changed] |
| Images | /15 | — | [recommendation only] |
| A+ Content | /10 | — | [recommendation only] |
| Description | /10 | /10 | [what changed] |
| Pricing | /10 | — | [observation] |
| Reviews | /15 | — | [observation] |
| SEO Coverage | /10 | /10 | [what changed] |

## Keyword Coverage: [X]% → [Y]%

| Keyword | Before | After | Where Added |
|---------|--------|-------|-------------|
| [kw] | ❌ | ✅ | Title + Bullet 2 |
| [kw] | ✅ Title only | ✅ Title + Bullets | Bullet 4 |

## What Changed (Before → After)

**Title:**
> ❌ [original]
> ✅ [optimized]

**Bullets:**
> ❌ 1. [original]
> ✅ 1. [optimized — added: +[kw1], +[kw2]]

## 🔴 Issues Fixed
1. [what was wrong → how we fixed it]

## 🟡 Recommendations (requires seller action)
1. [image improvements, A+ content, pricing — things the skill can't rewrite]

## 🟢 What Was Already Working
1. [positive aspects preserved]
```

### Competitive Comparison (if requested)

```
| Dimension | Your Listing | Competitor 1 | Competitor 2 | Competitor 3 |
|-----------|-------------|-------------|-------------|-------------|
| Title score | /15 | /15 | /15 | /15 |
| Bullets score | /15 | /15 | /15 | /15 |
| Images | [count] | [count] | [count] | [count] |
| A+ Content | Yes/No | Yes/No | Yes/No | Yes/No |
| Keyword coverage | X% | X% | X% | X% |
| Price | — | — | — | — |
| Rating | — | — | — | — |
| **Total** | **/100** | **/100** | **/100** | **/100** |
```

### Key principles

1. The seller's workflow is: **copy the listing → paste into Seller Central → done.** The diagnostic section explains WHY those specific words were chosen, but the listing itself must stand alone as a complete, ready-to-use deliverable. Never output only a report without the actual listing copy.

2. **Output language must match the target marketplace.** Amazon US/UK/AU/CA/IN → English. Amazon DE → German. Amazon FR → French. Amazon JP → Japanese. Amazon ES/MX → Spanish. Amazon IT → Italian. Amazon BR → Portuguese. The entire output (listing copy AND diagnostic section) must be in the marketplace language, regardless of what language the user is speaking in the conversation.

## Integration with amazon-keyword-research

This skill works best when chained with [amazon-keyword-research](https://github.com/nexscope-ai/Amazon-Skills/tree/main/amazon-keyword-research):

```
Step 1: "Research keywords for portable blender on Amazon US"
   → amazon-keyword-research returns keyword list with volumes

Step 2: "Now create a listing using those keywords. Product: 380ml BPA-free blender, USB-C rechargeable. Tone: Friendly."
   → amazon-listing-optimization Mode A uses the keywords to generate optimized copy
```

## Limitations

This skill uses publicly available data from Amazon product pages. It cannot access backend search terms, exact search volumes, or PPC/conversion data. For deeper analytics, stay tuned for **[Nexscope](https://github.com/nexscope-ai)** — coming soon.

---

**Part of the [Nexscope](https://github.com/nexscope-ai) suite — AI-powered Amazon seller tools.**
