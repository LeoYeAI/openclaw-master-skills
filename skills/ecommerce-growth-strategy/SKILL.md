---
name: ecommerce-growth-strategy
description: "E-commerce growth strategy advisor. Diagnoses current business health using unit economics (CAC, LTV, AOV, contribution margin), identifies the highest-impact growth opportunities across 5 levers (traffic, conversion, AOV, retention, expansion), and builds a prioritized 90-day growth roadmap. Uses the Ansoff Matrix adapted for e-commerce to evaluate market penetration, channel expansion, product expansion, and new market entry. Includes multichannel readiness assessment (Amazon, Walmart, TikTok Shop, Etsy, DTC/Shopify/Shopify) and product line expansion analysis. No API key required. Use when: (1) planning next phase of e-commerce growth, (2) deciding whether to expand to new channels or products, (3) diagnosing why growth has stalled, (4) prioritizing what to fix or build next."
metadata:
  nexscope:
    emoji: "🚀"
    category: ecommerce
---

# E-Commerce Growth Strategy 🚀

Your strategic growth advisor for e-commerce. This skill diagnoses where your business stands today, identifies the highest-impact growth opportunities, and builds a prioritized roadmap to get you to the next stage — whether that's your first $10K month or scaling past $1M.

This is the strategy layer above marketing execution. It tells you **what to do next and why**, then connects you to specialized skills like [ecommerce-marketing-strategy-builder](https://github.com/nexscope-ai/eCommerce-Skills/tree/main/ecommerce-marketing-strategy-builder) for **how to do it**.

```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-marketing-strategy-builder -g
```

**Supported platforms:** Shopify, WooCommerce, Amazon, Walmart, TikTok Shop, Etsy, eBay, BigCommerce, and multi-channel sellers.

Built by [Nexscope](https://www.nexscope.ai/) — your AI assistant for smarter e-commerce decisions.

## Install

```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-growth-strategy -g
```

## Usage

```
I sell pet clothes on Shopify, doing about $8K/month. Margin is 65%. I want to hit 
$20K/month in 6 months. What should I focus on?
```

```
We're an Amazon seller doing $50K/month in kitchen gadgets. Should we expand to 
Walmart or TikTok Shop? Or launch new products first?
```

```
My Etsy jewelry shop makes $3K/month but growth has stalled. I have 2,000 email 
subscribers and 5K Instagram followers. What's my best path to $10K/month?
```

## Capabilities

- Business health diagnosis using unit economics (CAC, LTV, LTV:CAC ratio, contribution margin, payback period, AOV)
- Growth opportunity identification across 5 levers: traffic, conversion, AOV, retention, expansion
- Ansoff Matrix adapted for e-commerce — evaluates 4 growth paths: penetrate, expand channels, expand products, enter new markets
- Growth Opportunity Matrix — maps each opportunity by impact vs effort for prioritization
- Multichannel readiness assessment — when and where to expand (Amazon, Walmart, TikTok Shop, Etsy, DTC/Shopify/Shopify)
- Product line expansion analysis — adjacent categories, timing, launch strategy
- Retention and LTV growth strategies — RFM segmentation, repeat purchase drivers, loyalty tactics
- Conversion rate optimization priorities — identifies biggest conversion leaks
- Prioritized 90-day growth roadmap with specific milestones and KPIs
- Cross-skill linking to specialized execution skills (PPC, email, marketing strategy, content)

---

## How This Skill Works

**Step 1: Collect information.** Extract from the user's initial message:
- Product / category
- Current sales platform(s)
- Current monthly revenue (or stage)
- Growth goal or target
- Any specific context (problems, constraints, opportunities mentioned)

**Step 2: Ask one follow-up with all remaining questions.** Use multiple-choice format:

```
Great — [acknowledge what they told you]. To build your growth strategy I need a few more details:

1. Business stage?
   a) Pre-launch — haven't sold yet
   b) Early — under $10K/mo
   c) Growing — $10K-50K/mo
   d) Scaling — $50K-200K/mo
   e) Established — $200K+/mo

2. Your main growth bottleneck right now?
   a) Not enough traffic / visitors
   b) Traffic but low conversion (people visit but don't buy)
   c) One-time buyers — they buy once and never come back
   d) Low average order value — they buy but spend little
   e) Maxed out on current platform — need to expand
   f) Not sure — diagnose for me
   g) Other: ___________

3. Current marketing channels? (check all that apply)
   a) Paid ads (Google, Meta, TikTok)
   b) Organic social media
   c) SEO / organic search
   d) Email marketing
   e) Influencer / affiliate
   f) None — haven't started marketing
   g) Other: ___________

4. Growth direction preference?
   a) Optimize what I have (squeeze more from current setup)
   b) Expand to new sales channels (Amazon, Walmart, TikTok Shop, etc.)
   c) Launch new products / expand product line
   d) Enter new markets / countries
   e) All of the above — tell me what's best
   f) Other: ___________

5. Monthly marketing budget?
   a) Under $500
   b) $500-2,000
   c) $2,000-10,000
   d) $10,000+
   e) Prefer not to say

6. Key numbers (share what you know — skip what you don't):
   - Average order value (AOV): $___
   - Product cost / margin: ___%
   - Repeat purchase rate: ___%
   - Email list size: ___
   - Monthly website visitors: ___
   - Current conversion rate: ___%

7. Competitors? (names or URLs, or skip)

Reply like: "1c 2f 3abd 4e 5c 6 AOV $35, margin 60%, repeat 15%, list 2000, visitors 8000, conv 2.5% 7 skip"
```

**Step 3: Diagnose current state.** Using the numbers provided (or estimating with ⚠️ where missing):

Calculate and present:
- **Unit Economics Health Check:**
  - CAC (if calculable from budget + new customers)
  - LTV = AOV × Purchase Frequency × Customer Lifespan × Gross Margin
  - LTV:CAC Ratio — compare against benchmarks (see below)
  - Contribution Margin = Revenue - COGS - Shipping - Processing - Packaging - Returns
  - Payback Period = CAC ÷ (AOV × Margin)

- **The Growth Equation:**
  Revenue = Traffic × Conversion Rate × AOV × Purchase Frequency
  
  Show which variable has the biggest room for improvement based on their numbers vs benchmarks. A 20% improvement in conversion is often worth more than a 20% increase in traffic.

**Step 4: Map growth opportunities.** Using the E-Commerce Ansoff Matrix:

| | Existing Products | New Products |
|---|---|---|
| **Existing Markets** | 🟢 **Penetrate** (optimize conversion, increase AOV, improve retention) | 🟡 **Product Expansion** (adjacent categories, bundles, subscriptions) |
| **New Markets** | 🟡 **Channel Expansion** (new platforms, new countries) | 🔴 **Diversification** (new products in new markets — highest risk) |

For each quadrant, identify 2-3 specific opportunities based on their business. Then rank every opportunity on a **Growth Opportunity Matrix**:

| Opportunity | Impact (1-5) | Effort (1-5) | Priority |
|-------------|:---:|:---:|:---:|
| e.g., Add email abandoned cart flow | 5 | 2 | 🔴 High |
| e.g., Expand to Amazon | 4 | 4 | 🟡 Medium |
| e.g., Launch subscription model | 3 | 5 | 🟢 Low |

Priority = High Impact + Low Effort first. Always.

**Step 5: Analyze each priority opportunity in detail.**

For each High and Medium priority opportunity, provide:
- What it is and why it matters for this business
- Specific tactics to execute
- Expected impact (revenue, conversion, AOV improvement)
- Timeline and resources needed
- Risks and how to mitigate them
- Link to relevant Nexscope skill for detailed execution

**Step 6: Build the 90-day growth roadmap.**

Break into 3 phases:
- **Days 1-30: Foundation** — fix what's broken, capture quick wins
- **Days 31-60: Build** — implement medium-effort, high-impact initiatives  
- **Days 61-90: Scale** — double down on what's working, launch expansion experiments

Each phase has:
- Specific actions with deadlines
- Milestones to hit
- KPIs to track
- Decision points ("If X happens, do Y. If not, do Z.")

**Step 7: Set KPIs and tracking plan.**

Define targets for each key metric based on their current baseline + realistic improvement rates.

---

## The 5 Growth Levers

Every e-commerce business grows through the same 5 levers. The question is which lever gives you the biggest return right now.

### Lever 1: Traffic / Acquisition
**What:** Get more potential buyers to your store
**When to prioritize:** Conversion rate is already decent (>2%) but visitor count is low
**Tactics:**
- SEO / content marketing (highest ROI long-term, 3-6 months to see results)
- Paid ads — Google Shopping, Meta, TikTok (immediate but costs money)
- Influencer/affiliate partnerships
- Social media organic
- Marketplace expansion (Amazon, Walmart = built-in traffic)

**Key metric:** Cost per visitor, CAC by channel
**Benchmark:** Average ecommerce CAC varies by category — beauty $20-60, apparel $30-80, food $15-50, supplements $40-100, home goods $30-70 *(Finsi.ai 2026)*

### Lever 2: Conversion Rate Optimization (CRO)
**What:** Turn more visitors into buyers
**When to prioritize:** Getting traffic but conversion is below benchmark
**Tactics:**
- Fix mobile experience (60%+ of traffic is mobile)
- Simplify checkout (guest checkout, fewer steps)
- Add social proof (reviews, UGC, trust badges)
- Improve product pages (better photos, clearer descriptions, size guides)
- Reduce friction (free shipping threshold, clear return policy)
- Exit-intent offers

**Key metric:** Conversion rate (sessions to orders)
**Benchmarks:** Average ecommerce conversion rate ~1.5-3% depending on source. By device: desktop ~2.8%, mobile ~2.8%. By traffic source: email 5.3%, organic search 2.8%, paid search 1.9%, social <1% *(Red Stag Fulfillment 2026, Smart Insights 2025)*

### Lever 3: Average Order Value (AOV)
**What:** Get each buyer to spend more per transaction
**When to prioritize:** Good traffic + good conversion, but revenue feels low relative to order volume
**Tactics:**
- Bundling and kits
- Free shipping threshold (set 20-30% above current AOV)
- Upsells and cross-sells (on product page, in cart, post-purchase)
- Tiered pricing (buy 2 get 10% off, buy 3 get 20% off)
- Premium product tier

**Key metric:** AOV
**Impact:** A 15% increase in AOV with same traffic = 15% more revenue at zero acquisition cost

### Lever 4: Retention / Purchase Frequency
**What:** Get existing customers to buy again (and again)
**When to prioritize:** You're acquiring customers but they buy once and disappear
**Tactics:**
- Email marketing automation (welcome, post-purchase, win-back flows)
- Loyalty/rewards program
- Subscription model (for consumables)
- SMS marketing
- Personalized product recommendations
- Community building (social, UGC, exclusive groups)

**Key metrics:** Repeat purchase rate, purchase frequency, customer lifespan
**Benchmarks:** 
- Acquiring a new customer costs 5-25× more than retaining one *(Harvard Business Review)*
- 5% increase in retention → 25-95% more profit *(HBR)*
- Existing customers are 50% more likely to try new products, spend 31% more *(Forbes)*
- Average ecommerce repeat purchase rate: ~28% *(Omnisend)*

### Lever 5: Expansion (Channels, Products, Markets)
**What:** Grow beyond current boundaries
**When to prioritize:** Current channel/product is profitable and operationally stable. Don't expand from a broken base
**Types:**
- **Channel expansion:** Shopify → Amazon, Amazon → Walmart, any → TikTok Shop
- **Product expansion:** Adjacent categories, variations, bundles, subscriptions
- **Market expansion:** US → EU, US → UK, domestic → international

**Key metric:** Revenue from new channel/product as % of total, without cannibalizing existing

---

## Multichannel Readiness Assessment

When a user asks about expanding to a new channel, evaluate readiness:

### Readiness Checklist (must be YES on all before expanding)
- [ ] Current channel is profitable (positive contribution margin)
- [ ] Operations can handle +30% order volume without breaking
- [ ] Have systems for inventory sync across channels
- [ ] Have bandwidth (team or budget) to manage another channel
- [ ] Understand the new channel's fee structure and its impact on margins

### Channel-Specific Assessment

| Channel | Best For | Audience | Fees | Key Requirement |
|---------|---------|---------|------|-----------------|
| **Amazon** | Established products with search demand | Broadest reach, high purchase intent | 15% referral + FBA fees | Competitive pricing, strong reviews |
| **Walmart** | Brands already on Amazon, price-competitive | Growing, value-conscious | 6-20% referral | Brand registry, competitive pricing |
| **TikTok Shop** | Visual, demonstrable products targeting 18-34 | Young, impulse buyers | 5% + shipping | Video content capability, trend-aware |
| **Etsy** | Handmade, vintage, unique, customizable | Niche buyers willing to pay premium | 6.5% transaction + listing | Unique/artisan positioning |
| **Own Website (DTC/Shopify)** | Brand control, customer data ownership | Your audience | Platform fees only (~2-3%) | Marketing capability to drive traffic |
| **eBay** | Clearance, refurbished, collectibles, niche | Bargain hunters, collectors | ~13% final value | Competitive pricing, good seller rating |

### Expansion Priority by Current Platform

**If currently on Shopify/DTC:**
1. Amazon (if product has search demand) — instant access to high-intent traffic
2. TikTok Shop (if product is visual) — low fees, organic viral potential
3. Etsy (if product is unique/handmade) — niche premium audience
4. Walmart — growing marketplace, less competition than Amazon
5. eBay — good for clearance, niche, or collectible products

**If currently on Amazon:**
1. Own website (DTC/Shopify) — own your customer data and email list
2. Walmart — similar catalog, growing marketplace, lower competition
3. TikTok Shop — diversify beyond search-based channels
4. eBay — clearance channel for slow-moving inventory
5. Etsy — only if product is unique/handmade/customizable

**If currently on Etsy:**
1. Own website (DTC/Shopify) — capture email, build brand outside Etsy
2. Amazon Handmade — if product fits, much larger audience
3. TikTok Shop — visual/handmade products do well organically
4. eBay — vintage/collectible crossover audience
5. Walmart — only if you can scale production for mass market

**If currently on Walmart:**
1. Amazon — if not already there, much larger traffic
2. Own website (DTC/Shopify) — build brand, own customer data
3. TikTok Shop — younger audience, viral potential
4. eBay — secondary sales channel for clearance
5. Etsy — only if product has handmade/unique angle

**If currently on TikTok Shop:**
1. Own website (DTC/Shopify) — capture email from viral traffic
2. Amazon — convert TikTok awareness into search-based sales
3. Walmart — price-conscious audience overlap
4. Etsy — if product is unique/trendy
5. eBay — clearance or bundle deals

**If currently on eBay:**
1. Own website (DTC/Shopify) — build brand beyond marketplace
2. Amazon — much larger audience for established products
3. Walmart — growing alternative marketplace
4. TikTok Shop — if product is demonstrable/visual
5. Etsy — only if product has handmade/vintage angle

---

## Product Line Expansion Framework

### When to Expand
- Current products are profitable and reviews are strong (4+ stars)
- You're seeing repeat customers ask for related products
- Competitors offer adjacent products you don't
- You've identified gaps from customer reviews/feedback

### How to Identify Adjacent Products
1. **Customer review mining** — what do customers wish your product included? What do they buy alongside it?
2. **Competitor catalog analysis** — what else do similar brands sell?
3. **Search demand** — are people searching for products adjacent to yours?
4. **Cross-sell data** — what products are frequently bought together in your category?

### Product Launch Strategy (3 Phases)
1. **Phase 1: Owned audience** — launch to email list and existing customers first. Low CAC, real feedback
2. **Phase 2: Paid + social** — expand via ads, influencer partnerships, social media
3. **Phase 3: Marketplace** — list on Amazon/Walmart once you have reviews and momentum

*(ConvertCart 2025)*

### Expansion Risk Assessment
| Type | Risk Level | Example |
|------|:---------:|---------|
| Variation of existing product | 🟢 Low | New color/size of best-seller |
| Complementary accessory | 🟢 Low | Leash brand adds collars |
| Adjacent category (same audience) | 🟡 Medium | Dog treats brand adds dog toys |
| New category (different audience) | 🔴 High | Dog treats brand adds cat food |
| Subscription model | 🟡 Medium | One-time purchase → recurring |

---

## Unit Economics Reference

When calculating unit economics, use these formulas and benchmarks:

### Formulas
- **CAC** = Total Acquisition Spend ÷ New Customers Acquired (include ad spend, creative, tools, discounts)
- **LTV** = AOV × Purchase Frequency × Customer Lifespan × Gross Margin
- **LTV:CAC Ratio** = LTV ÷ CAC
- **Contribution Margin** = Revenue - COGS - Shipping - Processing (3%) - Packaging - Returns provision (5%)
- **Payback Period** = CAC ÷ (AOV × Contribution Margin %)

### LTV:CAC Benchmarks *(Finsi.ai 2026)*
| Ratio | Meaning |
|:-----:|---------|
| < 1:1 | Losing money on every customer. Business model broken |
| 1:1 - 2:1 | Marginal. Profitable only with very low overhead |
| 2:1 - 3:1 | Functional. Room for improvement — focus on retention (raise LTV) or efficiency (lower CAC) |
| 3:1 - 5:1 | Healthy. Target range for growth-stage brands |
| > 5:1 | Under-investing in growth. Could afford to spend more on acquisition |

### Growth Equation
```
Revenue = Traffic × Conversion Rate × AOV × Purchase Frequency
```
Show the user which variable has the most room to improve. A 20% lift in conversion often beats a 20% increase in traffic — and costs less.

---

## Growth Priorities by Business Stage

### Pre-launch ($0/mo)
**Focus:** Validate product-market fit before spending on growth
- Build email list (landing page + lead magnet)
- Launch to small audience, get 50+ honest reviews
- Prove unit economics work (positive contribution margin)
- **Don't:** Scale ads, expand channels, launch multiple products

### Early Stage (<$10K/mo)
**Focus:** Find profitable acquisition channel + build retention foundation
- Priority lever: Traffic (find 1 channel that works profitably)
- Set up basic email flows (welcome, cart abandon, post-purchase)
- Optimize product pages for conversion
- **Don't:** Expand to new channels, launch new products, over-invest in brand

### Growing ($10K-50K/mo)
**Focus:** Optimize unit economics + diversify traffic + build retention
- Priority lever: Retention + CRO (highest ROI at this stage)
- Expand to 2-3 marketing channels
- Begin product line planning (adjacent products)
- Test channel expansion (one new marketplace)
- **Don't:** Scale what isn't profitable, expand too fast operationally

### Scaling ($50K-200K/mo)
**Focus:** Systemize, delegate, expand
- Priority lever: Expansion + AOV
- Launch on 2nd/3rd sales channels
- Expand product line (adjacent categories)
- Build team or outsource operations
- Invest in brand building
- **Don't:** Neglect retention while chasing acquisition, ignore operations

### Established ($200K+/mo)
**Focus:** Defensibility, efficiency, diversification
- Priority lever: All 5 — systematic optimization
- International expansion
- Subscription/recurring revenue
- Loyalty and community programs
- Consider vertical integration (manufacturing, fulfillment)

---

## Output Format

```
# 🚀 Growth Strategy — [Brand/Product Name]

## Business Snapshot
Product | Platform | Revenue | Stage | AOV | Margin | Repeat Rate

## Unit Economics Health Check
| Metric | Your Number | Benchmark | Status |
| CAC | $X | $X-X (category avg) | 🟢/🟡/🔴 |
| LTV | $X | — | — |
| LTV:CAC | X:1 | 3:1-5:1 target | 🟢/🟡/🔴 |
| Contribution Margin | X% | 40-60% target | 🟢/🟡/🔴 |
| Conversion Rate | X% | X% (benchmark) | 🟢/🟡/🔴 |
| Repeat Purchase Rate | X% | 28% avg | 🟢/🟡/🔴 |

## Growth Equation Diagnosis
Revenue = Traffic × Conversion × AOV × Frequency
[Which variable has the most room to improve?]

## E-Commerce Ansoff Matrix (Your Opportunities)
[4-quadrant analysis with specific opportunities per quadrant]

## Growth Opportunity Matrix
| Opportunity | Impact | Effort | Priority | Details |
[Ranked list of all opportunities]

## Top 3 Growth Priorities (Detailed)
### Priority 1: [Name]
[What, why, how, expected impact, timeline, risks]
→ Execution skill: [link to relevant Nexscope skill]

### Priority 2: [Name]
...

### Priority 3: [Name]
...

## Channel Expansion Assessment (if applicable)
[Readiness checklist + specific channel recommendation]

## Product Expansion Assessment (if applicable)
[Adjacent products + launch strategy]

## 90-Day Growth Roadmap
### Days 1-30: Foundation
[Actions + milestones + KPIs]
### Days 31-60: Build
[Actions + milestones + KPIs]
### Days 61-90: Scale
[Actions + milestones + KPIs]

## KPIs & Tracking
| Metric | Current | 30-Day Target | 60-Day | 90-Day |
[Specific targets for each key metric]

## Next Steps
[Immediate action items — what to do THIS WEEK]
```

---

## Other Skills

For detailed execution of specific growth initiatives:

**Paid advertising:**
```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-ppc-strategy-planner -g
```

**Email marketing system:**
```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-email-marketing-builder -g
```

**Full marketing strategy:**
```bash
npx skills add nexscope-ai/eCommerce-Skills --skill ecommerce-marketing-strategy-builder -g
```

**Product descriptions:**
```bash
npx skills add nexscope-ai/eCommerce-Skills --skill product-description-generator -g
```

More e-commerce skills: [nexscope-ai/eCommerce-Skills](https://github.com/nexscope-ai/eCommerce-Skills)

Built by [Nexscope](https://www.nexscope.ai/) — your AI assistant for smarter e-commerce decisions.
