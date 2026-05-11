---
name: amazon-ppc-campaign
description: "Amazon PPC campaign builder and optimizer for sellers. Two modes: (A) Build — design a complete campaign structure from scratch with keyword groupings, bid calculations, and negative keyword lists, (B) Optimize — audit existing campaigns using search term reports, identify keyword funnel opportunities, calculate bid adjustments, and generate a week-by-week action plan. Integrates with amazon-keyword-research for keyword input. No API key required. Use when: (1) setting up Amazon PPC campaigns for a new product, (2) auditing existing campaign performance and ACoS, (3) optimizing keyword bids and negative keywords, (4) building Auto/Manual/Exact campaign structures, (5) analyzing search term reports for opportunities, (6) calculating break-even ACoS and target ACoS, (7) scaling profitable campaigns to Sponsored Brands or Display."
metadata: {"nexscope":{"emoji":"📢","category":"amazon"}}
---

# Amazon PPC Campaign Optimization 📢

Build profitable PPC campaign structures from scratch, or audit and optimize existing campaigns with data-driven bid adjustments. No API key — works out of the box.

## Installation

```bash
npx skills add nexscope-ai/Amazon-Skills --skill amazon-ppc -g
```

## Two Modes

| Mode | When to Use | Input | Output |
|------|-------------|-------|--------|
| **A — Build** | Launching PPC for a new product | Product info + keywords + margins | Complete campaign blueprint + keyword groupings + initial bids |
| **B — Optimize** | Improving existing campaigns | Campaign data + search term reports + current ACoS | Optimization plan + bid adjustments + negative keyword list |

## Capabilities

- **ACoS financial framework**: Calculate break-even ACoS, target ACoS, and Max CPC from product margins — the foundation for every bid decision
- **Campaign architecture design**: Build a structured Auto → Broad → Exact funnel with proper negative keyword isolation between campaigns
- **Keyword grouping**: Organize keywords into campaign buckets with match types and initial bids based on confidence level
- **Bid optimization**: Apply ACoS-based bid adjustment rules using industry-standard formulas (cut/increase by percentage based on ACoS range)
- **Keyword funnel analysis**: Identify migration opportunities (Auto→Broad→Exact) and wasted spend (high-click zero-sale terms)
- **Negative keyword management**: Generate seed lists (cross-campaign, irrelevant terms, generic waste modifiers) and ongoing additions from search term data
- **Search term report analysis**: Parse user-provided campaign data to find profitable terms, wasteful terms, and optimization gaps
- **Competitor ASIN targeting**: Build product targeting campaigns aimed at competitor product pages
- **Integration chain**: Works with [amazon-keyword-research](https://github.com/nexscope-ai/Amazon-Skills/tree/main/amazon-keyword-research) for keyword input and [amazon-listing-optimization](https://github.com/nexscope-ai/Amazon-Skills/tree/main/amazon-listing-optimization) for pre-launch listing quality checks

## Usage Examples

### Mode A — Build New Campaigns

```
I'm launching a portable blender on Amazon US. Price: $39.99. Product cost: $8, shipping: $3, Amazon fees: $7.50. Here are my keywords: portable blender, personal blender, smoothie maker. Build me a PPC campaign structure.
```

```
Use amazon-keyword-research to find keywords for "bamboo cutting board", then build a PPC campaign structure. Product costs $6, sells for $29.99. Brand new product launch.
```

```
I want to advertise my dog t-shirt (ASIN B0D72TSM62, price $5.99, cost $2). Look at competitors B0CMD17929 and B0B76519ZG, extract their keywords, and build my PPC campaigns.
```

### Mode B — Optimize Existing Campaigns

```
My PPC ACoS is 58% and my target is 30%. I have 3 campaigns: Auto ($800/month, ACoS 67%), Manual Broad ($1,100, ACoS 48%), Manual Exact ($500, ACoS 33%). Product margin is 54%. Help me optimize.
```

```
Here's my search term report [paste CSV data]. Break-even ACoS is 40%. Find wasted spend, tell me what to negate and what to migrate.
```

```
Weekly PPC check: here are this week's search terms with clicks and sales [data]. Add negatives for 10+ clicks with no sales, move 2+ orders to Exact.
```

### Short Prompts Work Too

```
Help me set up PPC for my product B0D72TSM62
```
```
My ACoS is too high, help me fix it
```
```
I want to start advertising on Amazon
```

---

## How This Skill Collects Information

Users rarely provide everything upfront — and they don't need to. This skill follows a **progressive information gathering** approach:

**Step 1: Extract from the prompt.** Parse whatever the user already provided — ASIN, price, ACoS numbers, campaign names, keywords, etc.

**Step 2: Auto-discover.** If an ASIN is given, run the bundled `scripts/fetch-competitor.sh <ASIN>` to get price, category, BSR, and competitor context. This script handles Amazon's anti-bot protections. If the user mentions a product type without an ASIN, use `web_search` to understand the market.

**Step 3: Identify gaps.** Compare what you have against what's needed (see the Required Information tables in Mode A Step A1 and Mode B Step B1 below). Focus on what's **critical** to proceed:
- Mode A critical: **product costs** (to calculate ACoS) + **monthly ad budget** (to size campaigns) + **keywords or competitor ASINs** (to build campaigns)
- Mode B critical: **current ACoS** + **profit margin** (to know the gap and set targets)

**Step 4: One consolidated follow-up.** Ask only for missing critical items — in one conversational message, not a questionnaire:

```
Mode A example:
"I found your product — Paiaite Dog T-Shirt, $5.99 on Amazon. To build your
campaigns, I need three things:
  1. Your product cost per unit (so I can calculate your break-even ACoS)
  2. Your monthly ad budget (so I can size the campaigns right)
  3. Any target keywords or competitor ASINs? (Or I can research for you)"

Mode B example:
"Got it — ACoS is too high. To give you specific actions, can you share:
  1. Your profit margin (or product cost, I'll calculate it)
  2. Which campaigns are running and their rough ACoS?
Search term report data is a bonus but not required to start."
```

**Step 5: Use estimates when stuck.** If the user can't provide something (e.g., doesn't know exact fees), use reasonable category-based estimates and clearly note the assumption. Never block progress waiting for perfect data.

---

## Key Concepts

Three formulas drive every recommendation in this skill. They're introduced here and applied in Step A2 (for Mode A) and Step B2 (for Mode B).

**Break-even ACoS** = Profit margin before ad spend. If your product sells for $40 with $15 in costs after Amazon fees, your margin is $25/$40 = 62.5%. At 62.5% ACoS you spend all profit on ads — break even.

**Target ACoS** = Break-even ACoS − Desired profit margin. Want 25% profit after ads? Target ACoS = 62.5% − 25% = 37.5%.

**Keyword Funnel** = The core PPC optimization loop, applied in Steps A4/A6 (building) and B3 (optimizing):
```
Auto Campaign (discover new terms)
    ↓ terms with 2+ orders
Manual Broad (test at broader match)
    ↓ terms with 2+ sales
Manual Exact (scale winners with precision)

At each step: add the migrated term as NEGATIVE in the source campaign to prevent duplicate spend.
```

---

## Mode A Workflow — Build Campaign Structure

### Step A1: Collect Product Info

The following details are needed. Many can be extracted automatically (see "How This Skill Collects Information" above) — only ask for what's truly missing.

| Detail | How to Get It | Critical? |
|--------|--------------|:---------:|
| ASIN | From user's prompt | Helpful |
| Product name and category | Fetch from ASIN or ask | Helpful |
| Selling price | Fetch from ASIN or ask | ✅ Yes |
| Product cost (landed) | Must ask user | ✅ Yes |
| Monthly ad budget | Must ask user | ✅ Yes |
| Amazon fees (referral + FBA) | Estimate ~15% referral + FBA by size | Can estimate |
| Launch vs mature product | Ask or infer from context | Helpful |

### Step A2: Calculate ACoS Targets

Using the formulas from Key Concepts, compute the financial framework that governs all bid decisions:

```
📊 PPC FINANCIAL FRAMEWORK

Selling Price:           $39.99
Total Costs:             $18.50 (product $8 + shipping $3 + Amazon fees $7.50)
Profit Before Ads:       $21.49
Profit Margin:           53.7%

Break-even ACoS:         53.7% (spending ALL profit on ads)
Target ACoS (Mature):    30.0% (keeps ~24% profit margin)
Target ACoS (Launch):    50.0% (aggressive — acceptable for first 4-8 weeks)

Max CPC at Target ACoS:  $1.20 (at 10% conversion rate)
Formula: Max CPC = Selling Price × Target ACoS × Conversion Rate
```

If user doesn't know their conversion rate, use category benchmarks: 10-15% is average.

### Step A3: Collect Keywords

Keywords can come from three sources (use one or combine):

1. **From [amazon-keyword-research](https://github.com/nexscope-ai/Amazon-Skills/tree/main/amazon-keyword-research) skill** (recommended): Run keyword research first, then feed the ranked keyword list into this skill.
2. **From competitor ASINs**: User provides 1-3 competitor ASINs → run `scripts/fetch-competitor.sh <ASIN>` for each → extract keywords from their titles and bullet points. The script returns title, brand, bullets, price, category, BSR, and review count.
3. **From user's list**: User provides their own keywords (e.g., from Helium 10, search term reports, or manual research).

Additionally, expand keywords using Amazon autocomplete: `curl -s "https://completion.amazon.com/api/2017/suggestions?mid=ATVPDKIKX0DER&alias=aps&prefix=<URL-ENCODED-KEYWORD>" | python3 -c "import sys,json; [print(s['value']) for s in json.load(sys.stdin).get('suggestions',[])]"`

### Step A4: Build Campaign Structure and Group Keywords

**Default: 4 campaigns.** This is the standard structure for a new product launch:

| Priority | Campaign | What It Does | Always Include? |
|:--------:|----------|--------------|:---------------:|
| 1 | **Auto Discovery** | Amazon auto-matches your ad to search terms — collects data on what shoppers actually search | ✅ Yes |
| 2 | **Manual Exact** | Your top 10-15 proven keywords with exact match — highest control, lowest ACoS | ✅ Yes |
| 3 | **Manual Broad** | All research keywords with broad match — discovers variations and long-tail terms | ✅ Yes |
| 4 | **Product Targeting** | Shows your ad on competitor product pages — steals their traffic | ✅ If competitor ASINs available |

**If budget is tight:** Launch Priority 1+2 first (Auto + Exact). Add Priority 3 after one week of data. Add Priority 4 when you have competitor ASINs identified.

Organize keywords into these campaign buckets:

See the **Mode A Output** template below for the exact format of keyword groupings per campaign.

### Step A5: Set Initial Bids

**Max CPC (from Step A2) is your profitability ceiling** — not your actual bid. Actual competitive bids depend on the category and keyword competition.

**How to recommend bids:**
1. Calculate Max CPC as the financial guardrail (what you can afford)
2. For actual starting bids, tell the user to check Amazon's **suggested bid range** when creating the campaign in Seller Central — this reflects real auction data
3. If Amazon's suggested bid > Max CPC, flag the gap and explain: either accept a loss (ranking launch), raise product price, or skip that keyword

**When you don't have suggested bid data**, use these category-relative starting points:
| Campaign Type | Starting Bid | Adjust After |
|--------------|-------------|-------------|
| Manual Exact | Amazon suggested bid or Max CPC (whichever is lower) | 7 days with 20+ clicks |
| Manual Broad | 70-80% of Exact bid | 7 days |
| Auto | 50-70% of Exact bid | 7 days |
| Product Targeting | 50-70% of Exact bid | 7 days |

**Important:** These are starting points. The real optimization happens after 1-2 weeks of data — adjust based on actual ACoS per keyword.

### Step A6: Build Negative Keyword Seed List

Generate an initial negative keyword list before launch. Three types:

1. **Cross-campaign negatives**: Add all Exact campaign keywords as negatives in Broad and Auto campaigns (prevents internal competition — this is the Keyword Funnel isolation from Key Concepts).
2. **Irrelevant term negatives**: Terms that share words with your product but are wrong category/intent. Example for "bamboo cutting board":
   - Wrong material: "plastic cutting board", "glass cutting board"
   - Wrong product: "cutting board oil", "cutting board stand"
   - Wrong intent: "how to clean cutting board", "cutting board DIY"
3. **Generic waste negatives**: Common low-intent modifiers: "free", "cheap", "used", "DIY", "review", "reddit", "how to"

### Step A7: Generate Campaign Blueprint

Compile everything from Steps A1-A6 into the final deliverable. Follow the **Mode A Output** template in the Output Formats section below.

---

## Mode B Workflow — Optimize Existing Campaigns

### Step B1: Collect Campaign Data

The following details are needed. Follow the same progressive gathering approach — extract from the user's prompt first, then ask for missing critical items in one follow-up (see "How This Skill Collects Information" above).

| Detail | Critical? | Notes |
|--------|:---------:|-------|
| Campaign names and types | ✅ Yes | Auto/Manual/Broad/Exact |
| Overall ACoS | ✅ Yes | And per-campaign if available |
| Monthly ad spend and ad sales | ✅ Yes | For budget efficiency analysis |
| Product profit margin | ✅ Yes | To calculate break-even ACoS |
| Top spending keywords + their ACoS | Helpful | Enables specific bid adjustments |
| Search term report (CSV) | Bonus | Enables keyword funnel analysis |
| CTR and conversion rates | Bonus | Deeper performance insights |

### Step B2: Performance Audit

Using the ACoS formulas from Key Concepts, analyze across five dimensions: (1) Financial Health — break-even vs current ACoS, monthly profit/loss; (2) Campaign Efficiency — per-campaign ACoS with 🔴🟡🟢 status; (3) Keyword Performance — group keywords by profitable/marginal/unprofitable/zero-sales; (4) Budget Allocation — is spend proportional to revenue? recommend shifts; (5) Missed Opportunities — converting terms not in Manual, high-spend zero-sale terms without negatives, underfunded winners.

### Step B3: Keyword Funnel Analysis

Apply the Keyword Funnel from Key Concepts to the user's actual data. Three actions:
- **Migrate up** (2+ orders): Auto → Exact or Broad → Exact. Add as negative in source campaign.
- **Add negatives** (10+ clicks, 0 sales): Add as negative exact or phrase in the source campaign.
- **Watch list** (<20 clicks): Not enough data yet — flag for next review cycle.

### Step B4: Bid Adjustments

Apply ACoS-based bid adjustments to keywords with 20+ clicks (minimum for statistical significance):
- ACoS > 200%: cut bid 30-50%
- ACoS 100-199%: cut bid 20%
- ACoS target+10% to 99%: cut bid 10-15%
- ACoS at target (±10%): no change
- ACoS below target: increase bid 10-20%
- 10+ clicks with 0 sales: pause keyword

Output a table: Keyword | Current Bid | Current ACoS | New Bid | Reason

### Step B5: Generate Optimization Action Plan

Compile everything from Steps B1-B4 into a prioritized action plan. Follow the **Mode B Output** template in the Output Formats section below.

---

## Output Formats

The primary deliverable is always an **actionable campaign plan** the seller can implement directly in Seller Central.

### Mode A Output — New Campaign Blueprint

```
# ✅ PPC Campaign Blueprint — Ready to Implement

## Financial Framework
Selling Price: $XX.XX | Profit Before Ads: $XX.XX | Break-even ACoS: XX%
Target ACoS (Launch): XX% | Target ACoS (Mature): XX%
Max CPC: $X.XX (at XX% conversion rate)

## How These Campaigns Work Together

Standard: 4 campaigns. If budget is tight, start P1+P2, add the rest later.

  Auto (P1) → finds new search terms        ↓ terms with 2+ orders
  Broad (P3) → tests keywords at wider match ↓ terms with 2+ sales
  Exact (P2) → best keywords, lowest ACoS
  Product Targeting (P4) → ads on competitor pages

Separate campaigns prevent internal competition (bidding against yourself).

## Campaign Setup — Follow This in Seller Central

For each campaign below, create it in Seller Central with these exact settings.
Bids marked "use suggested" mean: use Amazon's suggested bid shown during setup.
If suggested bid > your Max CPC, that keyword may not be profitable — see the
⚠️ flag in the Financial Framework for guidance.

### Campaign 1: [Product] - Auto Discovery (Priority 1)
CAMPAIGN SETTINGS:
  Campaign Name:    [Product] - Auto
  Daily Budget:     $XX
  Start Date:       [today]
  End Date:         No end date
  Bid Strategy:     Dynamic Bids - Down Only

AD GROUP:
  Ad Group Name:    Auto - Discovery
  Default Bid:      $X.XX (use suggested bid × 0.5-0.7)
  ASIN:             [your ASIN]

KEYWORDS:           None — Amazon auto-selects based on your listing

NEGATIVE KEYWORDS:
  [keyword] | Negative Exact
  [keyword] | Negative Exact
  (add all Exact campaign keywords here — prevents Auto from
   competing with Exact on the same terms)

### Campaign 2: [Product] - Manual Exact (Priority 2)
CAMPAIGN SETTINGS:
  Campaign Name:    [Product] - Exact
  Daily Budget:     $XX
  Start Date:       [today]
  End Date:         No end date
  Bid Strategy:     Fixed Bids

AD GROUP:
  Ad Group Name:    Exact - Primary
  Default Bid:      $X.XX (use suggested bid, or Max CPC if lower)
  ASIN:             [your ASIN]

KEYWORDS:
  [keyword] | Exact | $X.XX (use suggested bid)
  [keyword] | Exact | $X.XX
  [10-15 keywords, each with match type and bid]

NEGATIVE KEYWORDS:  None needed (exact match is already precise)

### Campaign 3: [Product] - Manual Broad (Priority 3)
CAMPAIGN SETTINGS:
  Campaign Name:    [Product] - Broad
  Daily Budget:     $XX
  Start Date:       [today or Week 2]
  End Date:         No end date
  Bid Strategy:     Dynamic Bids - Down Only

AD GROUP:
  Ad Group Name:    Broad - Discovery
  Default Bid:      $X.XX (use suggested bid × 0.7-0.8)
  ASIN:             [your ASIN]

KEYWORDS:
  [keyword] | Broad | $X.XX
  [keyword] | Broad | $X.XX
  [15-20 keywords]

NEGATIVE KEYWORDS:
  [keyword] | Negative Exact
  (add all Exact campaign keywords — prevents Broad from competing)

### Campaign 4: [Product] - Product Targeting (Priority 4)
CAMPAIGN SETTINGS:
  Campaign Name:    [Product] - ASIN Targeting
  Daily Budget:     $XX
  Start Date:       [today or Week 2]
  End Date:         No end date
  Bid Strategy:     Fixed Bids

AD GROUP:
  Ad Group Name:    Competitor ASINs
  Default Bid:      $X.XX (use suggested bid × 0.5-0.7)
  ASIN:             [your ASIN]

TARGETS:
  B0XXXXXXXX | [competitor name, price, reviews] | $X.XX
  B0XXXXXXXX | [competitor name, price, reviews] | $X.XX

NEGATIVE KEYWORDS:
  [your own ASIN] | Negative Exact (prevent ads on your own page)

## Negative Keyword Master List (apply to Auto + Broad + Product Targeting)
  [term] | Negative Exact     (irrelevant terms)
  [term] | Negative Phrase     (waste modifiers: free, cheap, used, DIY, etc.)

## Budget Summary
| Campaign | Priority | Daily | Monthly | Role |
|----------|:--------:|-------|---------|------|
| Auto     | P1 | $XX | $XXX | Discover search terms |
| Exact    | P2 | $XX | $XXX | Scale best keywords |
| Broad    | P3 | $XX | $XXX | Test variations |
| Product  | P4 | $XX | $XXX | Competitor pages |
| TOTAL    |    | $XX | $XXX | |

## Launch Schedule
Day 1:  Create P1 (Auto) + P2 (Exact). Check that ads are active.
Day 3:  Check impressions. If very low, your bids are below competitive
        range — increase toward Amazon's suggested bid.
Day 7:  Add P3 (Broad) + P4 (Product Targeting). Review Auto search
        terms — add obvious negatives.
Day 14: Full analysis — migrate winners (2+ orders) from Auto/Broad → Exact.
Day 21: Bid optimization — adjust bids for keywords with 20+ clicks.

---

# 📊 Campaign Design Rationale

## Keyword Sources
[How keywords were discovered — fetch-competitor.sh, autocomplete, etc.]

## Bid Notes
Max CPC (profitability ceiling): $X.XX
Amazon suggested bids for this category typically range $X.XX - $X.XX.
[Flag any keywords where suggested bid > Max CPC and explain the tradeoff]
```

### Mode B Output — Optimization Report

```
# ✅ PPC Optimization Actions — Ready to Implement

## Priority 1: Immediate Negative Keywords (Do Today)
Add these as Negative Exact in their respective campaigns:
  Campaign "[name]": "term1", "term2", "term3"
  Campaign "[name]": "term4", "term5"
Expected savings: $XXX/month

## Priority 2: Keyword Migrations (This Week)
Move to Manual Exact (and add as negative in source):
  "[keyword]" from Auto → Exact, bid: $X.XX
  "[keyword]" from Broad → Exact, bid: $X.XX

## Priority 3: Bid Adjustments (This Week)
  "[keyword]": $X.XX → $X.XX (ACoS XX% → target XX%)
  "[keyword]": $X.XX → $X.XX (increase — profitable at XX%)
  "[keyword]": PAUSE (XX clicks, 0 sales)

## Priority 4: Budget Reallocation (Next Week)
  Auto: $XX/day → $XX/day (reduce — low efficiency)
  Exact: $XX/day → $XX/day (increase — best ACoS)

---

# 📊 Full Audit Report

## Performance Summary
| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Overall ACoS | XX% | XX% | 🔴🟡🟢 |
| TACoS | XX% | <XX% | 🔴🟡🟢 |
| Monthly Ad Profit | $XXX | $XXX | 🔴🟡🟢 |
| Budget Utilization | XX% | >90% | 🔴🟡🟢 |

## Keyword Funnel Analysis
[Full table from Step B3]

## Bid Adjustment Details  
[Full table from Step B4]

## Week-by-Week Action Plan
Week 1: [specific tasks with expected outcomes]
Week 2: [specific tasks]
Week 3: [specific tasks]
Week 4: [review and next cycle planning]

## Expected Results After 4 Weeks
ACoS: XX% → XX%
Monthly savings: $XXX
Sales increase: +XX% (from better targeting)
```

---

## Ongoing Management & Integration

After setup, offer weekly reminders (cron/heartbeat): search term analysis + bid adjustments + monthly full audit. Recommended skill chain: [amazon-keyword-research](https://github.com/nexscope-ai/Amazon-Skills/tree/main/amazon-keyword-research) → [amazon-listing-optimization](https://github.com/nexscope-ai/Amazon-Skills/tree/main/amazon-listing-optimization) → amazon-ppc. Always check listing quality before spending on ads. More skills: [Amazon-Skills](https://github.com/nexscope-ai/Amazon-Skills) | [eCommerce-Skills](https://github.com/nexscope-ai/eCommerce-Skills)

## Limitations

This skill uses publicly available data and user-provided campaign reports. It cannot access Seller Central directly, pull real-time bid landscapes, or automate campaign changes via API. For deeper PPC analytics with automated bid management, check out **[Nexscope](https://www.nexscope.ai/)** — Your AI Assistant for smarter E-commerce decisions.

---

**Built by [Nexscope](https://www.nexscope.ai/)** — research, validate, and act on e-commerce opportunities with AI.