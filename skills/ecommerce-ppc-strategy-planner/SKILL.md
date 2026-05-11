---
name: ecommerce-ppc-strategy-planner
description: "Cross-platform PPC strategy planner for ecommerce businesses. Analyzes your product and margins, recommends the right advertising platforms (Google Ads, Meta Ads, TikTok Ads), calculates ROAS targets, allocates budget across channels, and generates platform-specific campaign briefs with ad copy and creative direction. Two modes: (A) Build — design a multi-platform ad strategy from scratch, (B) Optimize — audit existing cross-platform campaigns and reallocate budget. Works for Shopify, WooCommerce, standalone stores, and marketplace sellers expanding to external traffic. No API key required."
metadata: {"nexscope":{"emoji":"📊","category":"ecommerce"}}
---

# E-Commerce PPC Strategy Planner 📊

Plan your cross-platform advertising strategy: which platforms to use, how much to spend on each, and what campaigns to run. Generates actionable briefs for Google Ads, Meta Ads, and TikTok Ads — with ad copy and creative direction included.

## Installation

```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-ppc-strategy-planner -g
```

## Two Modes

| Mode | When to Use | Input | Output |
|------|-------------|-------|--------|
| **A — Build** | Starting ads for the first time | Product info + budget + margins | Platform recommendation + budget split + campaign briefs + ad copy |
| **B — Optimize** | Running ads but want better results | Per-platform ROAS/CPA data | Cross-platform audit + budget reallocation + optimization actions |

## Capabilities

- **ROAS financial framework**: Calculate break-even ROAS, target ROAS, and max CPA from product margins — the foundation for all platform decisions
- **Platform recommendation**: Match your product type to the right ad channels (search-intent → Google, visual/impulse → Meta, demo/novelty → TikTok)
- **Cross-platform budget allocation**: Split budget across channels based on expected ROAS and funnel stage
- **Google Ads brief**: Shopping, Search, and Performance Max campaign structures with keyword direction
- **Meta Ads brief**: Audience targeting, ad set structure, and creative hooks for Facebook + Instagram
- **TikTok Ads brief**: Video hook concepts, Spark Ads strategy, and audience targeting
- **Ad copy generation**: Headlines, descriptions, and CTAs for each platform
- **Creative brief**: Image/video specs, style direction, hook angles (not actual image/video creation)
- **Cross-platform audit**: Compare ROAS/CPA across channels and identify where to shift budget

## Usage Examples

### Mode A — Build New Strategy

```
I sell handmade candles on Shopify. Price $34, cost $8. Monthly ad budget $2,000. Help me plan which platforms to advertise on.
```

```
I'm launching a fitness resistance band set, $29.99, 60% margin. $5,000/month budget. Where should I advertise and how much on each platform?
```

```
I have a Shopify store selling pet accessories. Best sellers are dog bandanas ($15) and cat toys ($12). $1,000/month to start. What's my ad strategy?
```

### Mode B — Optimize Existing

```
Running Google Shopping (ROAS 3.2x, $3,000/mo) and Facebook ($1,800/mo, ROAS 1.4x). Margin is 45%. Should I shift budget?
```

```
My TikTok ads get tons of views but barely convert. Google Shopping is profitable. Total budget $4,000/month. Help me optimize.
```

---

## How This Skill Collects Information

**Step 1: Extract from the prompt.** Parse product type, price, margins, budget, platforms mentioned, ROAS data, store type.

**Step 2: Identify gaps.** Compare against what's needed:

Mode A critical info:
| Info | Why It's Needed |
|------|----------------|
| Product price + cost/margin | Calculate break-even ROAS and Max CPA |
| Monthly ad budget | Allocate across platforms |
| **Buyer behavior type** | Determines which platform is primary (see below) |
| Existing website traffic / email list | Determines if retargeting is viable |

Mode B critical info:
| Info | Why It's Needed |
|------|----------------|
| Per-platform spend + ROAS/CPA | Audit each platform's performance |
| Profit margin | Calculate break-even ROAS |
| Campaign duration | New campaigns need 2-4 weeks before optimization |

**Step 3: One follow-up.** Ask only for missing critical items. Always include the buyer behavior question for Mode A:

```
Mode A example:
"Nice — handmade candles at $34 with $2,000/month budget. To plan your 
strategy, I need a few things:

  1. Your product cost per unit (to calculate break-even ROAS)
  2. How do customers typically find products like yours?
     a) They search for it (e.g., 'soy candles') — they know what they want
     b) They discover it visually — they see it and want it (lifestyle, fashion, decor)
     c) They need to see it in action — demo/video is what sells it
     d) Not sure — I'll analyze and recommend
  3. Do you have existing website traffic or an email list?
     (This affects whether retargeting is viable from day one)"

Mode B example:
"Got it — Google and Facebook running. To audit properly:
  1. Your product margin (or cost + price, I'll calculate)
  2. How long have these campaigns been running? (New campaigns 
     need 2-4 weeks before optimization)"
```

The buyer behavior answer directly determines platform selection:
- **a) Search** → Google Shopping / Search is primary
- **b) Visual** → Meta Ads (Facebook / Instagram) is primary
- **c) Demo** → TikTok Ads is primary
- **d) Not sure** → Infer from product type, mark as ⚠️ estimated

**Step 4: Use estimates when stuck.** Don't block on missing data — use category benchmarks, but:
- **Mark every estimate clearly** in the output with ⚠️ (e.g., "⚠️ Estimated: conversion rate 2.5% based on home decor category average")
- **Explain what better data would change** (e.g., "If you can share your actual Shopify conversion rate, I can recalculate the ROAS target and budget split more accurately")
- **List what to provide next time** at the end of the report for more precise results

---

## Key Concepts

### ROAS (Return on Ad Spend)
The universal metric across all platforms. ROAS = Revenue ÷ Ad Spend. A 4:1 ROAS means $4 revenue for every $1 spent.

### Break-even ROAS
The minimum ROAS needed to not lose money: **Break-even ROAS = 1 ÷ Profit Margin**

| Profit Margin | Break-even ROAS | Meaning |
|:-------------:|:---------------:|---------|
| 25% | 4.0x | Need $4 revenue per $1 ad spend just to break even |
| 33% | 3.0x | |
| 50% | 2.0x | |
| 60% | 1.67x | |
| 75% | 1.33x | Higher margin = more room for ad spend |

### Target ROAS
Break-even ROAS + profit buffer. Typically 1.5-2x the break-even ROAS for sustainable growth.

### Platform ROAS Benchmarks (2025-2026)

| Platform | Average ROAS | Top Quartile | Best For |
|----------|:-----------:|:------------:|----------|
| Google Ads (Shopping) | 4.5x | 6x+ | High-intent buyers (they're already searching) |
| Meta Ads (FB/IG) | 2.2x | 4-5x | Visual products, impulse buys, retargeting (3.6x) |
| TikTok Ads | 1.4x | 2x+ | Product discovery, demo-driven, younger audiences |

Industry-wide ecommerce average: 2.87x

### Max CPA (Cost per Acquisition)
Maximum you can pay to acquire one customer: **Max CPA = Average Order Value × Profit Margin**. Example: $34 product × 50% margin = $17 max CPA.

---

## Mode A Workflow — Build Strategy

### Step A1: Collect Product Info

| Detail | How to Get It | Critical? |
|--------|--------------|:---------:|
| Product type and description | From user's prompt | ✅ Yes |
| Selling price (or AOV) | Ask or infer | ✅ Yes |
| Product cost / profit margin | Must ask user | ✅ Yes |
| Monthly ad budget | Must ask user | ✅ Yes |
| Buyer behavior type | Asked in follow-up (see "How This Skill Collects Information") | ✅ Yes |
| Store platform (Shopify, WooCommerce, etc.) | Ask or infer | Helpful |
| Existing website traffic / email list | Asked in follow-up | Helpful |
| Target market / geography | Ask or infer | Helpful |

### Step A2: Calculate ROAS Framework

```
📊 CROSS-PLATFORM FINANCIAL FRAMEWORK

Product Price (AOV):     $34.00
Product Cost:            $8.00
Profit Margin:           76.5%

Break-even ROAS:         1.31x ($1 ad spend must generate $1.31 revenue)
Target ROAS:             2.5x (maintains ~36% profit after ads)
Max CPA:                 $26.01 (max cost to acquire one sale)

Monthly Ad Budget:       $2,000
At Target ROAS (2.5x):   $5,000 expected monthly ad revenue
At Break-even (1.31x):   $2,620 minimum monthly ad revenue
```

### Step A3: Recommend Platform Mix

Match the product to the right platforms based on product characteristics:

| Product Type | Primary Platform | Secondary | Why |
|-------------|-----------------|-----------|-----|
| Commodities (people search for them) | Google Shopping | Meta retargeting | Capture existing demand |
| Visual / lifestyle products | Meta Ads | Google Shopping | Create demand through imagery |
| Novel / demo-driven products | TikTok Ads | Meta Ads | "Wow" factor drives discovery |
| High-ticket / considered purchases | Google Search | Meta retargeting | Research-heavy buyer journey |
| Repeat consumables | Meta + Email | Google Brand | Build loyalty, retarget buyers |

**Platform selection logic (based on buyer behavior answer from follow-up):**
1. User answered **a) Search** → Google Shopping is primary
2. User answered **b) Visual** → Meta is primary
3. User answered **c) Demo** → TikTok is primary
4. User answered **d) Not sure** → infer from product type using the table above (mark as ⚠️ estimated, explain reasoning)
5. Always include retargeting (Meta or Google Display) if budget > $1,000/mo AND user has existing website traffic or email list
6. If budget < $1,000/mo → pick ONE primary platform only, don't spread thin

### Step A4: Allocate Budget Across Platforms

Use this framework, adjusted for product type:

**For search-intent products (Google primary):**
| Channel | % of Budget | Purpose |
|---------|:-----------:|---------|
| Google Shopping / PMax | 50-60% | Capture high-intent buyers |
| Meta Ads (prospecting) | 20-25% | Create demand + build audiences |
| Meta/Google retargeting | 10-15% | Convert visitors who didn't buy |
| Testing (TikTok / new) | 5-10% | Discover new channels |

**For visual/impulse products (Meta primary):**
| Channel | % of Budget | Purpose |
|---------|:-----------:|---------|
| Meta Ads (prospecting) | 45-55% | Primary demand creation |
| Google Shopping | 20-25% | Capture search spillover |
| Meta/Google retargeting | 15-20% | Highest ROAS channel |
| TikTok Ads | 5-10% | Discovery + younger audience |

**For demo/novelty products (TikTok primary):**
| Channel | % of Budget | Purpose |
|---------|:-----------:|---------|
| TikTok Ads | 40-50% | Product discovery via video |
| Meta Ads | 20-30% | Broader audience + retargeting |
| Google Shopping | 10-20% | Capture search from viral interest |
| Retargeting | 10-15% | Convert viewers who didn't buy |

### Step A5: Generate Platform Briefs

For each recommended platform, output a campaign brief:

**Google Ads Brief:**
- Campaign type recommendation (Shopping, Search, Performance Max)
- Keyword themes (not full keyword list — that's for google-ads-ecommerce skill)
- Bidding strategy recommendation (Target ROAS, Maximize Conversions)
- Daily budget
- Key settings (location targeting, device bids, scheduling)

**Meta Ads Brief:**
- Campaign objective (Sales, Traffic, Engagement)
- Audience targeting: demographics, interests, behaviors, lookalikes
- Ad set structure (how many ad sets, what audiences)
- Placement recommendations (Feed, Stories, Reels)
- Daily budget per ad set

**TikTok Ads Brief:**
- Campaign objective (Conversions, Traffic)
- Targeting: demographics, interests, behaviors
- Spark Ads vs In-Feed vs TopView recommendation
- Content style recommendation (UGC, product demo, before/after)
- Daily budget

### Step A6: Generate Ad Copy and Creative Direction

For each platform, generate 3 ad copy variations AND a creative brief using these specs:

#### Google Ads Copy Specs

| Element | Max Length | Notes |
|---------|:---------:|-------|
| Headline | **30 characters** | Write 3-5 headlines; Google rotates them |
| Long headline | **90 characters** | For Performance Max / Display |
| Description | **90 characters** | Write 2-4 descriptions |
| Display path | **15 characters × 2** | e.g., /soy-candles/shop |

CTA: Chosen from Google's preset list (Shop Now, Learn More, Get Offer, Sign Up).

**Example:**
```
Headline 1: Handmade Soy Candles – $34    (30 chars)
Headline 2: 60+ Hour Clean Burn            (22 chars)
Headline 3: Free Shipping Over $50         (25 chars)
Description 1: Hand-poured soy candles with natural essential oils. Clean burn, long-lasting fragrance. Shop now.  (90 chars)
Description 2: Eco-friendly candles perfect for gifts or self-care. Made in small batches with premium soy wax.    (90 chars)
```

#### Meta Ads (Facebook / Instagram) Copy Specs

| Element | Recommended | Max | Notes |
|---------|:----------:|:---:|-------|
| Primary text | **125 chars** | 2,200 | First 125 visible before "See more" |
| Headline | **40 chars** | 255 | Below the image/video |
| Description | **30 chars** | — | Shows in some placements only |
| Image | **1080×1080** | — | Square for Feed |
| Stories/Reels | **1080×1920** | — | Vertical 9:16 |
| Video length | **15-60s** | 240 min | 15-30s performs best |

CTA: Shop Now, Learn More, Get Offer, Sign Up, Order Now.

**Example:**
```
Primary text: Your evening ritual, upgraded. Hand-poured soy candles that fill your space with natural fragrance for 60+ hours. 🕯️
Headline: Shop Handmade Soy Candles
Description: From $34 · Free Shipping
CTA: Shop Now
```

#### TikTok Ads Copy Specs

| Element | Max Length | Notes |
|---------|:---------:|-------|
| Ad text / caption | **100 characters** | Keep short — users scroll fast |
| Display name | **40 characters** | Your brand name |
| Video | **9:16 vertical** | 720×1280 minimum |
| Video length | **9-15 seconds** | Sweet spot; max 60s |
| Spark Ads | N/A | Boost existing organic posts — no separate copy needed |

CTA: Shop Now, Learn More, Download, Contact Us.

**Hook rule:** First 2-3 seconds must grab attention. Start with motion, a question, or a surprising visual — never a logo or slow intro.

**Example:**
```
Hook (0-3s): [Close-up of match striking, candle being lit in cozy room]
Caption: The only candle that lasts 60+ hours 🕯️ #soycandle #cozyvibes
CTA: Shop Now
```

#### Creative Brief (all platforms)

For each platform, also provide:
- **Visual style direction**: lifestyle, product-only, UGC, comparison, or before/after
- **Video hook concept**: What happens in the first 3 seconds (the make-or-break moment)
- **Key messages**: 2-3 bullet points the creative must communicate
- **What NOT to do**: Common mistakes for this product type (e.g., "Don't use stock photos for a handmade product")

#### Creative Asset Prompts

Generate ready-to-use prompts that users can take directly to a designer or AI image tool (Midjourney, DALL-E, Flux, etc.):

**For each recommended platform, provide 2-3 image prompts:**

```
📸 AI Image Prompt (Product Shot):
"[Product] on [surface/background], [lighting style], [camera angle], 
[mood/aesthetic], commercial product photography, [aspect ratio]"

📸 AI Image Prompt (Lifestyle):
"[Scene description with product in context], [lighting], [color palette], 
[mood], editorial photography style, [aspect ratio]"

📸 AI Image Prompt (Ad Creative):
"[Scene] with space for text overlay on [top/bottom/left], 
[style], [dimensions for platform]"
```

**For video ads, provide a shot list:**
```
🎬 Video Shot List (15s):
0-3s: [Hook — what grabs attention]
3-8s: [Product showcase — key features/benefits]
8-12s: [Social proof or lifestyle context]
12-15s: [CTA — clear next step + end card]
```

**For designer briefs, include:**
- Deliverables: exact sizes and quantities needed per platform
- Reference mood/style (e.g., "Aesop-style minimalist" or "Glossier-style friendly")
- Brand colors and fonts (if user provides them)
- What assets the designer should deliver (PSD, PNG, video files)

This section ensures the user can immediately act on the strategy — either by generating visuals with AI tools or briefing a designer/photographer.

### Step A7: Generate Complete Strategy

Compile Steps A1-A6 into the Mode A Output template below.

---

## Mode B Workflow — Optimize Existing

### Step B1: Collect Platform Data

| Detail | Critical? | Notes |
|--------|:---------:|-------|
| Platforms running | ✅ Yes | Google, Meta, TikTok, etc. |
| Per-platform spend | ✅ Yes | Monthly or daily |
| Per-platform ROAS or CPA | ✅ Yes | The core metric |
| Product profit margin | ✅ Yes | To calculate break-even |
| Campaign duration | Helpful | New campaigns need 2-4 weeks before optimization |
| CTR and conversion rates | Bonus | Deeper performance analysis |
| Best/worst performing audiences | Bonus | For audience optimization |

### Step B2: Cross-Platform Audit

Compare each platform against break-even and target ROAS:

| Platform | Spend | ROAS | vs Break-even | vs Target | Status | Action |
|----------|------:|:----:|:-------------:|:---------:|:------:|--------|
| Google Shopping | $3,000 | 4.5x | ✅ +3.2x | ✅ +2.0x | 🟢 | Scale budget |
| Meta Prospecting | $1,200 | 1.8x | ✅ +0.5x | ❌ -0.7x | 🟡 | Optimize audiences |
| Meta Retargeting | $600 | 5.2x | ✅ +3.9x | ✅ +2.7x | 🟢 | Scale budget |
| TikTok | $800 | 0.9x | ❌ -0.4x | ❌ -1.6x | 🔴 | Cut or restructure |

### Step B3: Budget Reallocation

Shift money from underperformers to winners:
- 🟢 Platforms beating target ROAS → increase budget 20-30%
- 🟡 Platforms between break-even and target → optimize before scaling
- 🔴 Platforms below break-even → cut budget 50% or pause

### Step B4: Per-Platform Optimization

For each underperforming platform, provide specific actions:
- **Google:** keyword negative list, bidding strategy change, campaign type switch
- **Meta:** audience refinement, creative refresh, placement optimization, lookalike expansion
- **TikTok:** creative hook changes, targeting adjustments, Spark Ads pivot

### Step B5: Generate Optimization Plan

Compile into the Mode B Output template below with prioritized actions and timeline.

---

## Output Formats

### Mode A Output — Multi-Platform Strategy

```
# ✅ E-Commerce PPC Strategy — Ready to Implement

## Financial Framework
Product: [name] | Price: $XX | Margin: XX%
Break-even ROAS: X.Xx | Target ROAS: X.Xx | Max CPA: $XX
Monthly Budget: $X,XXX

## Platform Mix
[Visual showing recommended platforms and % allocation]

## Platform 1: [Google Ads / Meta / TikTok]
  Budget: $XXX/month (XX%)
  Campaign Type: [type]
  Targeting: [audiences / keywords]
  Bidding: [strategy]

  Ad Copy (3 variations):
    V1: [headline] | [description] | [CTA]
    V2: ...
    V3: ...

  Creative Brief:
    Format: [dimensions + type]
    Style: [lifestyle / UGC / product demo / comparison]
    Hook: [first 3 seconds concept for video, or key visual for static]
    Key Messages: [2-3 bullet points]

  Creative Asset Prompts:
    📸 Product Shot: "[AI image prompt ready to paste into Midjourney/DALL-E]"
    📸 Lifestyle: "[AI image prompt for lifestyle scene]"
    📸 Ad Creative: "[AI image prompt with text overlay space]"
    🎬 Video (15s):
      0-3s: [Hook]
      3-8s: [Product showcase]
      8-12s: [Social proof / lifestyle]
      12-15s: [CTA + end card]

## Platform 2: [...]
  [same structure]

## Budget Summary
| Platform | Monthly | Daily | % | Expected ROAS | Expected Revenue |
|----------|---------|-------|---|:-------------:|-----------------:|
| [name]   | $XXX    | $XX   | XX% | X.Xx       | $X,XXX           |

## 30-Day Test Plan
Week 1: [launch actions]
Week 2: [check metrics, early optimizations]
Week 3: [scale winners, cut losers]
Week 4: [full review, reallocate]
```

### Mode B Output — Cross-Platform Optimization

```
# ✅ PPC Optimization Actions — Ready to Implement

## Priority 1: Budget Shifts (Do Today)
  [Platform]: $XX/mo → $XX/mo (reason)
  [Platform]: $XX/mo → $XX/mo (reason)

## Priority 2: Platform-Specific Fixes (This Week)
  [Platform]: [specific actions — audience changes, creative refresh, etc.]

## Priority 3: Testing (Next Week)
  [New audience / creative / platform to test]

## Cross-Platform Audit
[Full comparison table from Step B2]

## Expected Results (4 Weeks)
| Metric | Current | Target | Impact |
|--------|---------|--------|--------|
| Blended ROAS | X.Xx | X.Xx | +XX% |
| Monthly Revenue | $X,XXX | $X,XXX | +$X,XXX |
```

---

## Other Skills

This skill covers cross-platform strategy. For platform-specific execution, check out these dedicated skills:

- **google-ads-ecommerce** — Google Shopping, Search, and Performance Max campaign setup (coming soon)
- **meta-ads-ecommerce** — Facebook and Instagram ad campaign setup (coming soon)
- **tiktok-ads-ecommerce** — TikTok ad campaign setup (coming soon)

More e-commerce skills: [nexscope-ai/eCommerce-Skills](https://github.com/nexscope-ai/eCommerce-Skills)

### Selling on Amazon?

**[amazon-ppc-campaign](https://github.com/nexscope-ai/Amazon-Skills/tree/main/amazon-ppc-campaign)** — Build and optimize Amazon Sponsored Products / Brands / Display campaigns. Calculates ACoS targets, groups keywords by campaign type, sets bid strategies based on Amazon's suggested ranges. Output follows Seller Central hierarchy — ready to implement.

```bash
npx skills add nexscope-ai/Amazon-Skills --skill amazon-ppc-campaign -g
```

See all Amazon seller skills: [nexscope-ai/Amazon-Skills](https://github.com/nexscope-ai/Amazon-Skills)

## Limitations

This skill provides strategic planning and creative direction based on industry benchmarks and product analysis. It cannot access live ad platform data, create actual images/videos, set up tracking pixels, or manage ad accounts directly. For deeper optimization with live data, check out **[Nexscope](https://www.nexscope.ai/)** — Your AI Assistant for smarter E-commerce decisions.

---

**Built by [Nexscope](https://www.nexscope.ai/)** — research, validate, and act on e-commerce opportunities with AI.
