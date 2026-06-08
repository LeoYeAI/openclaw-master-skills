---
name: afrexai-competitive-intel
description: Complete competitive intelligence system — market mapping, product teardowns, pricing intel, win/loss analysis, battlecards, and strategic monitoring. Goes far beyond SEO to cover the full business landscape.
---

# Competitive Intelligence Engine

A complete system for understanding, tracking, and outmaneuvering competitors. Covers market mapping, product analysis, pricing intelligence, sales battlecards, win/loss analysis, and ongoing monitoring.

## When to Use

- Entering a new market or launching a product
- Losing deals to competitors and need to understand why
- Quarterly strategy reviews
- Pricing decisions (new product or adjustment)
- Sales team needs competitive talking points
- M&A due diligence on a target or acquirer
- Investor pitch prep (show you understand the landscape)
- Content strategy informed by competitor gaps

---

## Phase 1: Market Mapping

### 1.1 Competitor Identification

Classify every competitor into one of four tiers:

| Tier | Definition | Example | Monitoring Frequency |
|------|-----------|---------|---------------------|
| **Direct** | Same product, same buyer | Your closest rivals | Weekly |
| **Adjacent** | Different product, overlapping buyer | Platform expanding into your space | Bi-weekly |
| **Indirect** | Different solution to same problem | Spreadsheets replacing your SaaS | Monthly |
| **Emerging** | Early-stage, same vision | YC startups in your category | Monthly |

### Discovery Methods

Search these sources systematically:

1. **Google**: "[your category] software/tool/service" — note top 10 organic + ads
2. **G2/Capterra/TrustRadius**: Your category page — note top 10 by reviews
3. **Product Hunt**: Search your keywords — sort by votes
4. **Crunchbase**: Search your category — filter funded companies
5. **LinkedIn**: "[competitor name]" company pages — note employee count trends
6. **Reddit/HN**: "alternative to [leader]" or "[category] recommendations"
7. **Customer interviews**: "Who else did you evaluate?"
8. **Lost deal notes**: Who did you lose to and why?

### Market Map YAML

```yaml
market_map:
  category: "[Your Category]"
  date: "YYYY-MM-DD"
  total_addressable_market: "$XB"
  
  competitors:
    - name: "Competitor A"
      tier: "direct"
      website: "https://..."
      founded: 2019
      funding: "$50M Series B"
      estimated_revenue: "$10-20M ARR"
      employee_count: 150
      employee_trend: "growing"  # growing | stable | shrinking
      hq: "San Francisco, CA"
      key_customers: ["Customer 1", "Customer 2"]
      primary_market: "mid-market"  # smb | mid-market | enterprise
      positioning: "All-in-one platform for X"
      strengths: ["Feature A", "Strong brand"]
      weaknesses: ["Expensive", "Slow support"]
      threat_level: "high"  # low | medium | high | critical
      notes: ""
```

---

## Phase 2: Product Teardown

### 2.1 Feature Matrix

For each direct competitor, build a feature comparison:

```yaml
feature_matrix:
  last_updated: "YYYY-MM-DD"
  
  categories:
    - name: "Core Features"
      features:
        - name: "Feature X"
          us: "full"       # none | partial | full | superior
          competitor_a: "full"
          competitor_b: "partial"
          weight: 5        # 1-5 importance to buyer
          notes: "We have deeper customization"
          
        - name: "Feature Y"
          us: "none"
          competitor_a: "full"
          competitor_b: "full"
          weight: 3
          notes: "On our roadmap for Q3"
    
    - name: "Integrations"
      features:
        - name: "Salesforce"
          us: "full"
          competitor_a: "partial"
          weight: 4
```

### 2.2 Product Teardown Template

For each major competitor, conduct a structured teardown:

```markdown
## [Competitor Name] Product Teardown
**Date:** YYYY-MM-DD
**Analyst:** [name]

### First Impressions (0-5 min)
- Homepage messaging: What problem do they lead with?
- Sign-up friction: How many steps? What info required?
- Time to value: How fast can you DO something?
- Design quality: Modern, dated, cluttered, clean?

### Onboarding (5-30 min)
- Guided tour? Checklist? Video? Nothing?
- Sample data provided? Sandbox mode?
- How quickly did you feel competent?
- What confused you?

### Core Workflow
- Complete their primary use case end-to-end
- Note: steps required, clicks per task, speed, error handling
- Screenshot key screens

### Differentiators
- What can they do that we can't? (be honest)
- What's their "magic moment"?
- What do their happiest customers praise? (check G2 reviews)

### Weaknesses
- Where did you get stuck?
- What felt missing or half-baked?
- What do their angriest customers complain about? (check G2 1-2 star reviews)

### Pricing vs Value
- What plan would a typical customer need?
- Price per user/month at that tier?
- Any hidden costs (implementation, support, integrations)?
- Free trial? Freemium? Money-back guarantee?

### Technical Assessment
- Stack: (check Wappalyzer, BuiltWith, job postings)
- API: Public? REST/GraphQL? Rate limits? Docs quality?
- Mobile: Native app? Responsive web? PWA?
- Performance: Page load speed, UI responsiveness
- Uptime: Status page? Historical incidents?
```

### 2.3 UX Scoring Rubric

Score each competitor's product (0-10 per dimension):

| Dimension | What to Evaluate | Weight |
|-----------|-----------------|--------|
| **Ease of Setup** | Time to first value, onboarding friction | 15% |
| **Core UX** | Primary workflow efficiency, intuitiveness | 25% |
| **Feature Depth** | Covers edge cases, power user needs | 20% |
| **Reliability** | Uptime, bugs encountered, error handling | 15% |
| **Integrations** | Ecosystem breadth, API quality | 10% |
| **Support** | Response time, quality, self-serve resources | 10% |
| **Mobile** | Native quality, feature parity | 5% |

**Total = weighted sum. Compare across competitors.**

---

## Phase 3: Pricing Intelligence

### 3.1 Pricing Comparison Table

```yaml
pricing_intel:
  date: "YYYY-MM-DD"
  
  competitors:
    - name: "Us"
      model: "per-seat"  # per-seat | usage | flat | hybrid | freemium
      entry_price: "$29/user/mo"
      mid_price: "$79/user/mo"
      enterprise_price: "Custom"
      free_tier: true
      free_limits: "5 users, 1000 records"
      annual_discount: "20%"
      contract_required: false
      implementation_fee: "$0"
      hidden_costs: []
      
    - name: "Competitor A"
      model: "per-seat"
      entry_price: "$49/user/mo"
      mid_price: "$99/user/mo"
      enterprise_price: "Custom ($150+/user)"
      free_tier: false
      annual_discount: "15%"
      contract_required: true  # annual minimum
      implementation_fee: "$5,000"
      hidden_costs: ["API access on enterprise only", "SSO $50/user extra"]
```

### 3.2 Price Positioning Analysis

Answer these questions:

1. **Where do we sit?** Map all competitors on a 2x2: Price (low→high) vs Feature depth (basic→advanced)
2. **Who's cheapest?** At 10 users? 50 users? 200 users? (pricing often crosses over at scale)
3. **Total Cost of Ownership**: Include implementation, training, migration, hidden fees
4. **Value ratio**: Features-per-dollar compared to each competitor
5. **Pricing trend**: Are competitors raising prices? (check Wayback Machine on /pricing)
6. **Discount behavior**: Do they discount aggressively in deals? (ask sales team, check G2 reviews mentioning price)

### 3.3 Pricing Strategy Recommendations

Based on analysis, recommend one of:

| Strategy | When to Use | Risk |
|----------|------------|------|
| **Premium** | Clearly superior product + brand | Losing price-sensitive deals |
| **Parity** | Similar product, compete on other axes | Race to bottom |
| **Penetration** | New entrant, need market share fast | Perception of low quality |
| **Value** | Better product at lower price | Margin pressure if costs rise |
| **Niche** | Specialized for segment competitors ignore | Small TAM |

---

## Phase 4: Sales Battlecards

### 4.1 Battlecard Template

Create one per direct competitor:

```markdown
# 🏆 Battlecard: Us vs [Competitor]
**Last Updated:** YYYY-MM-DD | **Confidence:** High/Medium/Low

## Quick Stats
| Metric | Us | Them |
|--------|-----|------|
| Founded | | |
| Funding | | |
| Est. Revenue | | |
| Employees | | |
| G2 Rating | | |
| Gartner Position | | |

## Their Pitch (in their words)
"[Their homepage headline or elevator pitch]"

## Why Customers Choose Us Over Them
1. **[Reason 1]**: [Specific proof point — customer quote, metric, demo moment]
2. **[Reason 2]**: [Specific proof point]
3. **[Reason 3]**: [Specific proof point]

## Why Customers Choose Them Over Us (be honest)
1. **[Reason 1]**: [And how to counter it]
2. **[Reason 2]**: [And how to counter it]

## Landmines to Plant 🧨
Questions to ask the prospect that expose competitor weaknesses:
1. "Ask them how they handle [weakness area] — you'll find it requires [workaround]"
2. "Request a demo of [specific feature] — it's not as deep as it looks"
3. "Ask about [hidden cost] — it's not on the pricing page"

## Objection Handling

**"[Competitor] is cheaper"**
> Response: "At first glance, yes. But when you factor in [hidden cost 1], [hidden cost 2], and [limitation requiring workaround], the total cost is actually [higher/comparable]. Plus, [our unique value] saves you [X hours/dollars] per [period]."

**"[Competitor] has [feature we lack]"**
> Response: "[Acknowledge honestly]. Here's why our customers find that [our approach] actually works better for [their use case]: [specific reasoning]. [Customer name] evaluated both and chose us specifically because [reason]."

**"We're already using [Competitor]"**
> Response: "That makes sense — they're solid at [genuine strength]. The customers who switch to us typically hit a wall with [specific limitation]. Are you experiencing [common pain point with that competitor]?"

## Trap Plays (When to Walk Away)
- If prospect needs [specific capability we truly lack], acknowledge it honestly
- If they're deeply embedded in [competitor ecosystem], switching cost may be too high
- If deal size is below $[X], cost of competing isn't worth it

## Win Stories
- **[Customer A]**: Switched from [Competitor] because [reason]. Result: [metric improvement]
- **[Customer B]**: Evaluated both, chose us because [reason]. Quote: "[testimonial]"

## Recent Intel
- [Date]: [Competitor] announced [product change/funding/hire]
- [Date]: [Customer feedback about competitor]
```

### 4.2 Quick Objection Matrix

For the sales team's daily use:

| Objection | Short Response | Proof Point |
|-----------|---------------|-------------|
| "Too expensive" | [Value reframe] | [ROI stat or customer quote] |
| "Never heard of you" | [Social proof] | [Customer logos, G2 rank] |
| "Missing [feature]" | [Alternative or roadmap] | [Workaround or timeline] |
| "Happy with current tool" | [Trigger question] | [Common pain with incumbent] |
| "Need enterprise features" | [What we have] | [Enterprise customer reference] |

---

## Phase 5: Win/Loss Analysis

### 5.1 Win/Loss Interview Framework

After every significant deal (won or lost), capture:

```yaml
win_loss:
  deal: "[Company Name]"
  date: "YYYY-MM-DD"
  outcome: "won"  # won | lost | no-decision
  deal_size: "$X ARR"
  sales_cycle_days: 45
  competitors_evaluated: ["Competitor A", "Competitor B"]
  
  decision_factors:
    - factor: "Ease of use"
      importance: 5  # 1-5
      our_score: 4   # 1-5
      winner_score: 3
      notes: "Demo experience was decisive"
      
    - factor: "Price"
      importance: 4
      our_score: 3
      winner_score: 4
      notes: "We were 20% more expensive but justified by ROI"
      
    - factor: "Integration with Salesforce"
      importance: 5
      our_score: 5
      winner_score: 2
      notes: "They required middleware; we're native"
  
  champion: "VP of Sales"
  decision_maker: "CRO"
  buying_trigger: "Previous tool couldn't scale past 50 users"
  
  key_quote: "Your Salesforce integration sealed the deal"
  
  lessons:
    - "Lead with integration story for Salesforce-heavy orgs"
    - "ROI calculator was critical for justifying premium price"
```

### 5.2 Win/Loss Trend Dashboard

Track quarterly:

```markdown
## Q[X] Win/Loss Summary

### Win Rate by Competitor
| Competitor | Wins | Losses | Win Rate | Trend |
|-----------|------|--------|----------|-------|
| Competitor A | 12 | 8 | 60% | ↑ (was 50%) |
| Competitor B | 5 | 15 | 25% | ↓ (was 35%) |
| No competition | 20 | 3 | 87% | → |

### Top Win Reasons (ranked by frequency)
1. Ease of use (mentioned in 65% of wins)
2. Integration depth (55%)
3. Customer support (40%)

### Top Loss Reasons (ranked by frequency)
1. Price (mentioned in 70% of losses)
2. Missing [specific feature] (45%)
3. Incumbent relationship (30%)

### Action Items from This Quarter's Losses
1. [Feature gap] → Product team building for Q[X+1]
2. [Price objection] → New ROI calculator + case study
3. [Competitor strength] → Invest in [counter-strategy]
```

---

## Phase 6: Ongoing Monitoring

### 6.1 Competitor Signal Tracking

Set up monitoring for each direct competitor:

| Signal | Source | Frequency | What to Look For |
|--------|--------|-----------|-----------------|
| **Product changes** | Their changelog/blog | Weekly | New features, deprecations |
| **Pricing changes** | /pricing page + Wayback | Monthly | Price increases, new tiers, model changes |
| **Hiring** | LinkedIn Jobs | Bi-weekly | Engineering surge = new product. Sales surge = growth push |
| **Funding** | Crunchbase, TechCrunch | As it happens | New round = aggressive expansion coming |
| **Leadership** | LinkedIn, press | As it happens | New CEO/CRO = strategy shift likely |
| **Reviews** | G2, Capterra | Monthly | Sentiment shifts, recurring complaints |
| **Content** | Their blog, social | Weekly | Messaging changes, new positioning |
| **Customers** | Press releases, case studies | Monthly | Logos gained, industries targeted |
| **Community** | Reddit, HN, Twitter | Weekly | Complaints, praise, feature requests |

### 6.2 Weekly Intel Brief Template

```markdown
## Competitive Intel Brief — Week of [Date]

### 🔴 Critical (action needed)
- [Competitor X] launched [feature] that directly competes with our [feature]
  - Impact: [assessment]
  - Recommended response: [action]

### 🟡 Notable (monitor)
- [Competitor Y] raised Series C ($40M) — expect aggressive hiring/marketing
- [Competitor Z] changed pricing model from per-seat to usage-based

### 🟢 Informational
- [Competitor X] published blog post about [topic]
- [Competitor Y] hiring 3 new enterprise AEs in EMEA

### Win/Loss This Week
- Won [Deal] vs [Competitor] — reason: [X]
- Lost [Deal] to [Competitor] — reason: [X]
```

### 6.3 Quarterly Competitive Review Agenda

1. **Market map update** (15 min): Any new entrants? Any exits? Tier changes?
2. **Feature gap review** (20 min): What did competitors ship? What should we respond to?
3. **Win/loss trends** (15 min): Are we gaining or losing ground? Against whom?
4. **Pricing check** (10 min): Any pricing changes? Is our positioning still right?
5. **Battlecard refresh** (15 min): Update all active battlecards
6. **Strategic decisions** (15 min): Based on all intel, what should we invest in / deprioritize?

---

## Phase 7: Strategic Frameworks

### 7.1 Competitive Moat Assessment

Rate your moat and each competitor's (1-5):

| Moat Type | Description | Us | Comp A | Comp B |
|-----------|------------|-----|--------|--------|
| **Network Effects** | Product gets better with more users | | | |
| **Switching Costs** | Pain of leaving increases over time | | | |
| **Data Advantage** | Proprietary data that improves product | | | |
| **Brand** | Trust, recognition, preference | | | |
| **Scale Economies** | Cost advantages from size | | | |
| **Regulatory** | Licenses, certifications, compliance | | | |
| **Technology** | Patents, proprietary tech, speed | | | |
| **Ecosystem** | Integrations, partnerships, marketplace | | | |

**Total moat score = sum. Higher = harder to displace.**

### 7.2 Competitor Response Prediction

For each major competitor move, predict their likely response to YOUR moves:

```markdown
**If we [action]...**
- Competitor A will likely: [response] because [reasoning]
- Competitor B will likely: [response] because [reasoning]
- Timeline: [how fast they'll respond]
- Our counter-move: [what we do next]
```

### 7.3 Blue Ocean Opportunities

After mapping all competitors, look for:

1. **Underserved segments**: Customer types everyone ignores (too small? too niche? too complex?)
2. **Unmet needs**: Features/capabilities no one offers that customers actually want
3. **Experience gaps**: The workflow everyone does poorly
4. **Business model innovation**: Could you win by charging differently? (usage vs seat vs outcome-based)
5. **Channel gaps**: Where are customers NOT being reached? (vertical communities, specific geographies, languages)

---

## Edge Cases & Advanced Techniques

### Stealth Competitors
- Monitor patent filings in your space (Google Patents)
- Watch YC/Techstars demo days for category entrants
- Track job postings at big tech for [your category] keywords — could signal internal build

### International Competitors
- Search in target language for your category
- Check local review sites (Capterra has country-specific)
- Different markets have different leaders — map per region

### Platform Risk
- If you build on a platform (Salesforce, Shopify, etc.), monitor the platform itself
- Platforms often build features that commoditize plugins
- Track platform's acquisition history in your space

### Competitor Intelligence Ethics
- ✅ Public information (websites, press, job postings, reviews, patents)
- ✅ Customer feedback about competitors (win/loss interviews)
- ✅ Product trials and demos (sign up normally)
- ❌ Fake identities to access gated content
- ❌ Poaching employees for intel
- ❌ Accessing confidential documents
- ❌ Reverse engineering protected code

---

## Natural Language Commands

| Command | What It Does |
|---------|-------------|
| "Map my competitive landscape" | Full Phase 1 market mapping |
| "Tear down [competitor]" | Product teardown (Phase 2) |
| "Compare pricing with [competitors]" | Pricing intelligence (Phase 3) |
| "Build battlecard for [competitor]" | Sales battlecard (Phase 4) |
| "Analyze our win/loss data" | Win/loss patterns (Phase 5) |
| "Weekly competitive brief" | Monitoring summary (Phase 6) |
| "Assess our competitive moat" | Strategic analysis (Phase 7) |
| "Find blue ocean opportunities" | Gap analysis (Phase 7.3) |
| "How should we respond to [competitor move]?" | Response prediction (Phase 7.2) |
| "Full competitive review" | All phases, comprehensive output |
