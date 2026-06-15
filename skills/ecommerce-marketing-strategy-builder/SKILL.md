---
name: ecommerce-marketing-strategy-builder
description: "Full-stack e-commerce marketing strategy builder. Analyzes your product, market, and competitors, then builds a complete omnichannel marketing plan covering paid ads, SEO, email/SMS, content marketing, social media, influencer partnerships, and referral programs. Includes target audience persona, competitive landscape, channel prioritization with budget allocation, content direction, and a 90-day action plan. Works for any e-commerce platform — Shopify, Amazon, Etsy, WooCommerce, TikTok Shop, and more. No API key required."
metadata:
  nexscope:
    emoji: 🎯
    category: ecommerce
---

# E-Commerce Marketing Strategy Builder 🎯

Build a complete omnichannel marketing strategy for your e-commerce business. Covers all major channels — paid ads, SEO, email, content, social media, influencers, and referral programs — with budget allocation, audience targeting, and a 90-day action plan.

## Installation

```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-marketing-strategy-builder -g
```

## Capabilities

- **Target audience persona**: Demographics, interests, pain points, buying motivations, and where they spend time online — built from product analysis and competitor research
- **Competitive landscape**: How competitors position, price, and market — and where the gaps are
- **Channel prioritization**: Which marketing channels to use and in what order, ranked by expected ROI for your specific product and stage
- **Budget allocation**: How to split your marketing budget across channels, with benchmarks
- **Email & SMS strategy**: Flows, sequences, and campaign types — the highest-ROI channel most sellers ignore
- **SEO & content plan**: Keyword themes, content types, and publishing cadence
- **Paid ads brief**: High-level ad strategy per platform (for detailed campaign setup, use [ecommerce-ppc-strategy-planner](https://github.com/nexscope-ai/eCommerce-Skills/tree/main/ecommerce-ppc-strategy-planner))
- **Social media plan**: Platform selection, content pillars, posting frequency
- **Influencer & affiliate direction**: Who to partner with, what to offer, how to structure deals
- **Referral & loyalty program**: How to turn existing customers into growth engines
- **Pricing positioning**: Where to price relative to competitors based on market analysis
- **90-day action plan**: Week-by-week roadmap with priorities and milestones

## Usage Examples

```
I'm launching a Shopify store selling premium dog treats, $24.99 per bag. Margin is 65%. 
Budget: $3,000/month for marketing. Target: US dog owners. Help me build a marketing strategy.
```

```
I sell handmade jewelry on Etsy and my own website. Price range $40-120. I have 2,000 
Instagram followers and 800 email subscribers. Monthly marketing budget is $1,500. 
I want to grow beyond Etsy. What's my strategy?
```

```
We're a new DTC skincare brand on Shopify. AOV $55, margin 70%. We have $10,000/month 
marketing budget and want to hit $100K revenue in 6 months. Build our marketing plan.
```

---

## How This Skill Collects Information

**Step 1: Extract from the prompt.** Parse product type, price, margin, budget, current channels, goals, stage, competitors mentioned.

**Step 2: Identify gaps.** Compare against what's needed:

Critical info:
| Info | Why It's Needed |
|------|----------------|
| Product type and price/AOV | Determines which channels and audiences fit |
| Profit margin | Calculates how much you can spend to acquire a customer |
| Monthly marketing budget | Allocates across channels |
| Business stage | New launch vs growing vs established — changes priority order |
| Marketing goal | Brand awareness vs direct sales vs both — changes channel mix |
| Sales channels | Shopify only? Amazon + Shopify? Etsy? Affects strategy |
| Existing assets | Email list, social following, content, reviews — what you already have to work with |

**Step 3: One follow-up.** Consolidate ALL missing questions into a single message. Use multiple-choice format to make it easy to answer quickly:

```
Example:
"Premium dog treats at $24.99, 65% margin, $3,000/month budget — great start! 
A few quick questions so I can build your strategy (just reply with the letters):

  1. Business stage?
     a) Pre-launch — haven't sold yet
     b) Early — selling, but under $10K/mo
     c) Growing — $10K-50K/mo
     d) Scaling — $50K+/mo

  2. Main goal?
     a) Brand awareness — get known
     b) Direct sales — revenue now
     c) Both
     d) Other: ___________

  3. Where do you sell?
     a) Shopify / own website only
     b) Amazon
     c) Etsy
     d) Multiple platforms (which ones?)

  4. Your target customer buys because of:
     a) Price / value
     b) Quality / premium
     c) Unique / can't find elsewhere
     d) Convenience
     e) Other: ___________

  5. What do you already have? (check all that apply)
     a) Email list — how many subscribers?
     b) Social media following — which platform, how many?
     c) Existing content (blog, videos, etc.)
     d) Customer reviews
     e) Nothing yet — starting from zero
     f) Other: ___________

  6. Any competitors you want me to analyze? (names or URLs, or skip)"
```

**Key rules:**
- **Never split into multiple follow-up rounds.** One message, all questions.
- **Use a/b/c/d choices** wherever possible — faster than open-ended questions.
- **Mix in 1-2 open-ended** only where choice format doesn't work (competitors, specific numbers).
- **If user gives short answers** like "1b 2c 3a 5e", that's enough — proceed with the strategy.

**Step 4: Use estimates when stuck.** Don't block on missing data — use category benchmarks, but:
- **Mark every estimate clearly** with ⚠️
- **Explain what better data would change**
- **List what to provide next time** at the end of the report

---

## Key Benchmarks (2025-2026)

### Channel ROI

| Channel | Average ROI | Best For | Source |
|---------|:----------:|----------|--------|
| Email marketing | $36-40 per $1 | Retention, repeat purchases, cart recovery | Omnisend 2026 Report |
| SMS marketing | $21-71 per $1 | Time-sensitive offers, cart abandonment | Omnisend 2026 Report |
| SEO / organic search | $7.48 per $1 | Long-term sustainable traffic | FirstPageSage |
| Google Ads (search) | $8 per $1 | High-intent buyers | Google Economic Impact Report |
| Paid social (Meta/TikTok) | $2.5 per $1 | Awareness + prospecting | FirstPageSage ROAS Statistics |
| Influencer marketing | Varies | Brand credibility, new audiences | — |
| Affiliate marketing | Performance-based | Low-risk expansion (pay per sale) | — |

### Marketing Budget Benchmarks

| Business Stage | Marketing as % of Revenue | Notes | Source |
|---------------|:------------------------:|-------|--------|
| New / pre-launch | 15-20% | Invest heavily to build awareness | Hostinger, WebFX |
| Early stage (<$500K/yr) | 10-15% | Build foundational channels | Hostinger |
| Growing ($500K-$5M/yr) | 7-12% | Optimize and scale what works | Gartner 2025 CMO Survey (avg 7.7%) |
| Established ($5M+/yr) | 5-8% | Efficiency + retention focus | Gartner |

### Budget Allocation Framework

| Channel | % of Budget | Priority |
|---------|:----------:|:--------:|
| Paid ads (Google, Meta, TikTok) | 25-35% | P1 — Immediate traffic |
| Content + SEO | 20-25% | P2 — Long-term compound growth |
| Email + SMS | 15-20% | P1 — Highest ROI, retention |
| Social media (organic) | 10-15% | P3 — Brand building |
| Influencer / affiliate | 10-15% | P2 — Credibility + reach |
| Testing / new channels | 5-10% | P3 — Discover next winner |

Recommended overall split: **60% owned/organic (SEO, email, content) + 40% paid channels (PPC, social ads, influencers)**

### Customer Retention Stats

- Repeat customers = 21% of customer base but drive 44% of revenue *(Omnisend)*
- After 1st purchase: 27% chance of buying again → 2nd: 49% → 3rd: 62% *(Smile.io)*
- Using 3+ marketing channels: 287% higher purchase rate *(Omnisend)*

---

## Workflow

### Step 1: Understand the Business

Collect and organize:
- Product, price, margin, business stage
- Marketing goal, budget, sales channels
- Existing assets (email list, social, content, reviews)
- Competitive landscape (who are the main competitors?)

### Step 2: Build Target Audience Persona

**Using info collected from the follow-up questions (stage, goal, buying motivation, existing assets), plus your own research:**

1. **If user provided customer data** → build persona from real data
2. **If user is pre-launch / no data** → infer from:
   - Product category → typical buyer profile (e.g., premium dog treats → dog owners 28-55, health-conscious pet parents)
   - Price point → income bracket (budget vs premium vs luxury)
   - Platform → audience skew (Etsy skews female 25-45, TikTok Shop skews 18-34)
3. **Research competitor audiences** — search for top brands in the category, check who follows them, what their reviews say
4. **Mark estimates** with ⚠️ when inferring instead of using real data

**Output the persona in this format:**

```
🎯 TARGET AUDIENCE PERSONA

Demographics:
  Age: [range]
  Gender: [split %]
  Location: [markets]
  Income: [range]
  Source: [user data / inferred from product type ⚠️ / competitor analysis]
  
Psychographics:
  Interests: [relevant interests]
  Values: [what they care about]
  Pain points: [problems your product solves]
  Buying motivation: [why they buy — convenience, quality, status, price]
  
Online behavior:
  Where they discover products: [Instagram, Google, TikTok, Amazon, etc.]
  Where they research: [reviews, YouTube, Reddit, blogs]
  What influences purchase: [price, reviews, brand, influencer recommendation]
  
Language they use:
  [Real phrases from reviews / social media — how they describe the problem 
  and solution in their own words. Use these in ad copy and content.]
  Source: [extracted from competitor reviews / user-provided / estimated ⚠️]
```

### Step 3: Competitive Landscape

**Using competitors from the follow-up (Q6), or find them yourself:**

- **If user provided competitors** → research those directly
- **If not** → search "[product category] best brands", check platform best sellers, look at who's running ads for the same keywords

**For each competitor, analyze:**
- **Pricing** — price range, budget/mid/premium positioning
- **Positioning** — tagline, USP, how they describe themselves
- **Strengths / Weaknesses** — from reviews (what people praise vs complain about)
- **Marketing channels** — where are they advertising? Social? Email? Content?

**Then identify:** market gaps, differentiation opportunities, and pricing recommendation.

**Output format:**

```
📊 COMPETITIVE LANDSCAPE

Market Price Range:  [$low — $high]
Your Position:       [where you sit and why]

Top Competitors:
  [Competitor 1]: 
    Price: $XX | Positioning: [how they position]
    Strengths: [from reviews/research]
    Weaknesses: [from reviews/research]
    Marketing: [channels they use]

  [Competitor 2]:
    [same structure]
  
Market Gaps:         [underserved segments, unmet needs, positioning opportunities]
Your Differentiation: [what makes you different — and how to communicate it]
Pricing Recommendation: [where to price and why]
```

### Step 4: Channel Prioritization

Based on business stage, budget, goals, and audience, rank channels.

**Where these percentages come from:**
- Omnisend 2026 Ecommerce Report: 60% owned/organic + 40% paid as optimal split
- Azarian Growth Agency 2025: 25-30% content/SEO, 20-25% paid search, 15-20% paid social, 10-15% email
- Gartner 2025 CMO Survey: marketing budgets at 7.7% of company revenue
- The stage-specific splits below are synthesized from these sources — adjust based on the user's actual data and goals

**For new launches (brand awareness + first sales):**
| Priority | Channel | Why | Budget % |
|:--------:|---------|-----|:--------:|
| P1 | Paid Ads (Meta/Google) | Immediate traffic when you have zero audience | 30-35% |
| P1 | Email setup (welcome flow, cart abandonment) | Capture and convert visitors from day 1 | 10-15% |
| P2 | Social media (organic) | Build brand, create content library | 10-15% |
| P2 | Influencer seeding | Get product in hands of micro-influencers | 15-20% |
| P3 | SEO / Content | Start building, won't pay off for 3-6 months | 10-15% |
| P3 | Testing | Try one new thing each month | 5-10% |

**For growing businesses (scale what works):**
| Priority | Channel | Why | Budget % |
|:--------:|---------|-----|:--------:|
| P1 | Email + SMS | Highest ROI, monetize existing customers | 15-20% |
| P1 | Paid Ads (scale winners) | Increase spend on proven channels | 25-30% |
| P2 | SEO / Content | Reduce CAC over time | 15-20% |
| P2 | Influencer / Affiliate | Expand reach cost-effectively | 10-15% |
| P3 | Social media | Maintain presence, repurpose content | 10% |
| P3 | Referral / Loyalty program | Turn customers into advocates | 5-10% |

**For established businesses (optimize + retain):**
| Priority | Channel | Why | Budget % |
|:--------:|---------|-----|:--------:|
| P1 | Email + SMS + Loyalty | Retention = highest-margin revenue | 20-25% |
| P1 | SEO / Content | Compound returns, reduce paid dependency | 20-25% |
| P2 | Paid Ads (efficient) | Maintain acquisition at target CAC | 20-25% |
| P2 | Affiliate program | Scale through partners | 10-15% |
| P3 | Social media | Brand + community | 10% |
| P3 | New market / channel | Expand to new platforms or geographies | 5-10% |

### Step 5: Channel-by-Channel Plan

For each prioritized channel, output:

**Email & SMS:**
- Key automated flows: Welcome series, abandoned cart, post-purchase, win-back
- Campaign types: New products, sales, content newsletters
- List building tactics: Pop-up offer, checkout opt-in, social media lead magnets
- Target metrics: Open rate >35%, click rate >3%, revenue per email >$0.10

**SEO & Content:**
- Keyword themes (not full keyword research — that's a separate skill)
- Content types: Blog posts, buying guides, comparison pages, FAQ
- Publishing cadence: X posts per week/month
- Technical SEO priorities if applicable

**Paid Ads:**
- Recommended platforms and why
- Budget split across platforms
- Campaign types (awareness vs conversion)
- Note: "For detailed campaign setup, use ecommerce-ppc-strategy-planner"

**Social Media:**
- Platform selection (based on where target audience is)
- Content pillars (3-4 themes to rotate)
- Posting frequency
- Engagement strategy

**Influencer / Affiliate:**
- Type of influencers (micro vs macro, niche)
- Outreach approach and what to offer
- Commission/payment structure
- How to measure ROI

**Referral / Loyalty:**
- Program structure (points, tiers, referral rewards)
- When to launch (need enough customers first)
- Expected impact

### Step 6: 90-Day Action Plan

Break the strategy into weekly actions:

```
📅 90-DAY ACTION PLAN

MONTH 1: Foundation
  Week 1: [Setup actions — accounts, tools, tracking]
  Week 2: [Launch first channel — usually paid ads + email flows]
  Week 3: [Content + social media kickoff]
  Week 4: [First review — what's working? Adjust]

MONTH 2: Optimize & Expand
  Week 5-6: [Optimize winning channels, cut losers]
  Week 7-8: [Launch second wave — influencer outreach, SEO content]

MONTH 3: Scale
  Week 9-10: [Scale winners with more budget]
  Week 11-12: [Launch referral/loyalty, review full strategy]

KEY MILESTONES:
  Day 30: [target metric]
  Day 60: [target metric]
  Day 90: [target metric]
```

### Step 7: KPIs & Measurement

Define success metrics:

| Metric | Benchmark | Your Target (how to set) | How to Track |
|--------|:---------:|:------------------------:|-------------|
| CAC | Varies | Must be < profit per order (AOV × margin) | Ad platforms + analytics |
| LTV | Varies | Aim for > 3× CAC (if LTV < 3× CAC, acquisition is too expensive) | Shopify/platform analytics |
| Email list growth | 5-10%/month | New stores: aim for 5%/mo. Growing: 8-10%/mo | Email platform |
| Email revenue share | 25-30% of total | Start with 15% target, grow to 25%+ over 6 months | Email platform |
| Organic traffic growth | 10-20%/month | SEO takes 3-6 months to kick in. Set 10%/mo after month 3 | Google Analytics |
| Social engagement rate | 1-3% | Below 1% = content problem. Target 2%+ | Platform analytics |
| Repeat purchase rate | 28% avg | New stores: 15-20%. Growing: 25%+. Established: 30%+ | Platform analytics |
| Blended ROAS | 2.5x+ | Calculate: 1 ÷ margin × 1.5 = your minimum target ROAS | All platforms combined |

---

## Output Format

```
# ✅ E-Commerce Marketing Strategy — Ready to Execute

## Business Snapshot
Product: [name] | Price: $XX | Margin: XX%
Stage: [new/growing/established] | Budget: $X,XXX/mo
Goal: [awareness / sales / both]
Channels: [where you sell]

## Target Audience Persona
[Full persona from Step A2]

## Competitive Landscape
[Analysis from Step A3]

## Channel Strategy (Prioritized)
[Full channel plan from Step A4-A5 with budget allocation]

## 90-Day Action Plan
[Weekly roadmap from Step A6]

## KPIs & Measurement
[Metrics table from Step A7]
```

---

## Other Skills

This skill builds the strategy. For execution on specific channels:

- **[ecommerce-ppc-strategy-planner](https://github.com/nexscope-ai/eCommerce-Skills/tree/main/ecommerce-ppc-strategy-planner)** — Detailed paid ads strategy for Google, Meta, and TikTok with ad copy + creative prompts

```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-ppc-strategy-planner -g
```

Selling on Amazon? See [nexscope-ai/Amazon-Skills](https://github.com/nexscope-ai/Amazon-Skills) for keyword research, listing optimization, and Amazon PPC.

More e-commerce skills: [nexscope-ai/eCommerce-Skills](https://github.com/nexscope-ai/eCommerce-Skills)

## Limitations

This skill provides strategic planning based on industry benchmarks, product analysis, and competitive research. It cannot access your actual analytics data, run A/B tests, create content, set up email flows, or manage ad accounts. For AI-powered marketing execution with live data, check out **[Nexscope](https://www.nexscope.ai/)** — your AI assistant for smarter e-commerce decisions.

---

**Built by [Nexscope](https://www.nexscope.ai/)** — research, validate, and act on e-commerce opportunities with AI.
