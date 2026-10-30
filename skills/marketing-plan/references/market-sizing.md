# Market Sizing

Adapted from a contribution by @imMamdouhaboammar (PR #418).

Use this reference when the market-quality gate raises the question "is this market big enough to plan around?" or when the user asks directly how big a market is. The goal is a defensible range that supports a decision (enter, narrow, validate, or avoid). A precise-looking number with no visible math does more harm than an honest range.

## Define the market first

Sizing a vague category ("healthcare," "SaaS") produces a meaningless number. Before estimating anything, write a one-sentence market definition covering geography, buyer, use case, and price model.

> AI note-taking tools for sales teams at English-speaking B2B SaaS companies with 20-500 employees, sold per seat.

State what is out of scope too (adjacent segments, other geographies, enterprise).

## TAM, SAM, SOM in plain terms

| Layer | Plain meaning | Narrowed by |
|---|---|---|
| **TAM** (total addressable market) | Annual spend if every possible buyer of this category bought | Category definition only |
| **SAM** (serviceable addressable market) | The slice you could actually serve with your product as it exists | Geography, segment, use case, language, price band, integrations |
| **SOM** (serviceable obtainable market) | What you can realistically win in the next 1-3 years | Channels, budget, sales capacity, conversion rates, competition |

SOM is the number that matters for a marketing plan. TAM mostly matters for fundraising narratives, and a large TAM proves nothing about demand. Size TAM only when someone needs it.

## The four sizing methods

The mini-examples below use one made-up product (an AI note-taker for sales teams) with illustrative numbers, to show the math. They aren't real market data.


No single method is reliable alone. Run at least two, then compare.

### 1. Bottom-up

`reachable buyers × expected annual spend × realistic capture rate`

Best for local services, B2B niches, agencies, and marketplaces where buyers can be counted.

**Mini-example** (sales note-taker, SAM):
- ~18,000 B2B SaaS companies in range (LinkedIn company filter, Crunchbase export)
- Average 8 sales seats each, $25/seat/month = $2,400/year per account
- SAM ≈ 18,000 × $2,400 = **~$43M/year**
- SOM at 1-2% capture by end of Year 1 = **$0.4M-$0.9M ARR**

Weak points: the seat count and capture rate are assumptions. Label them as such.

### 2. Search-led

Estimate demand from high-intent keyword clusters, then apply click and conversion assumptions.

**Mini-example:**
- High-intent cluster ("AI meeting notes for sales," "Gong alternative," "sales call summary tool"): ~9,000 searches/month across 40 terms
- Achievable click share at page-one rankings: 10-20% → 900-1,800 visits/month
- Visit-to-trial 4%, trial-to-paid 20% → 7-14 new accounts/month
- At $2,400/year per account: **~$0.2M-$0.4M new ARR/year** from search alone

Search volume is an intent proxy. It measures people actively looking, which undercounts latent demand and categories buyers don't search for by name. CPC levels and competitor ad density show how much others will pay for that intent.

### 3. Competitor-led

Infer market size and maturity from what competitors visibly earn.

**Mini-example:**
- 6 direct competitors; 2 report ARR publicly or via press (~$15M and ~$8M), the other 4 estimated from headcount (~40-80 staff each at ~$150K revenue per employee → ~$6M-$12M each)
- Combined visible revenue: **~$47M-$71M**
- Cross-check: review counts on G2 and Capterra, pricing pages, hiring pace, ad activity

If the combined revenue of competitors is larger than your SAM estimate, your SAM is probably too narrow (or competitors serve segments you excluded). In this example, $47M-$71M exceeds the $43M bottom-up SAM, which suggests competitors also sell to enterprise or non-sales teams. If combined revenue is tiny, the category may be early or the demand may be weaker than it looks.

### 4. Channel-led

Size the market you can reach through specific channels with the current budget. This is often the most useful number for an early-stage plan because it bakes in execution limits.

**Mini-example** (Seed stage, $10K/month paid budget):
- LinkedIn: target audience of ~60,000 sales leaders in segment; $10K/month at ~$80 CPL → ~125 leads/month → 10% to paid → ~12 accounts/month
- Outbound: 1 SDR, 1,000 accounts/month, 1.5% meeting rate, 25% close → ~4 accounts/month
- Combined: ~16 accounts/month ≈ **~$0.45M new ARR/year**, capped by budget and headcount

### Triangulate and cross-check

Put each method's result side by side for the same layer (usually SOM or SAM):

| Method | SOM estimate (Year 1) | Key assumption | Confidence |
|---|---|---|---|
| Bottom-up | $0.4M-$0.9M | 1-2% capture | Medium |
| Search-led | $0.2M-$0.4M (search channel only) | 10-20% click share | Medium |
| Channel-led | ~$0.45M | $80 CPL holds at scale | Low |

How to read the comparison:
- **Compare like with like.** The search-led figure covers one channel, so it's a floor for SOM rather than a competing estimate. Here, bottom-up and channel-led agree around $0.4M-$0.5M, and search alone gets about halfway there, which is consistent.
- **Estimates overlap** → the overlap is your working range.
- **Estimates differ by more than ~3×** → one assumption is broken. Find it before presenting any number.
- **Bottom-up far exceeds channel-led** → demand exists but the plan can't reach it yet. That points to a budget or channel constraint, which belongs in Section 10 (funding-stage unlocks).
- **Channel-led far exceeds bottom-up** → the reachable-buyer count is probably too low, or the channel assumptions are optimistic.

Top-down analyst reports can serve as a sanity check on TAM. Don't use them as the primary method for a local or niche market, because global category figures rarely translate.

## Evidence and confidence

Label every estimate and every major input.

| Label | Use when |
|---|---|
| **High** | Two or more independent evidence types agree, or first-party data (CRM, conversion data, paid search terms) supports it |
| **Medium** | Credible but incomplete evidence, e.g. competitors are active but their revenue is estimated |
| **Low** | Plausible inference with thin support, e.g. a global trend with unknown local adoption |
| **Unknown** | Missing or contradictory data. Turn it into a validation task |

Rank evidence by how close it sits to real buyer behavior:
1. First-party commercial data (sales notes, CRM, conversion rates, churn reasons)
2. Observed market behavior (competitor ads, pricing pages, review volume, job posts)
3. Search and demand proxies (keyword volume, CPC, autocomplete)
4. Third-party reports (analyst, government, platform data)
5. Expert opinion (founder interviews, practitioner posts)
6. Weak proxies (uncited market-size claims, trend articles, AI summaries)

### The presentation rule

Never present a single precise market number without sources. Always show:
- A **range**, not a point estimate
- The **assumptions** behind it, listed separately from observed facts
- The **method(s)** used and whether they agree
- A **confidence label**
- The **one assumption** that would most change the answer, and how to test it

Bad: "The market is $4.27B."
Good: "SAM is roughly $35M-$50M/year (medium confidence), based on bottom-up seat math and competitor revenue. The biggest swing factor is average seats per account; 10 customer calls would tighten it."

## Market attractiveness scorecard

Size alone doesn't make a market worth entering. Score each factor 1-5 and total out of 50.

| Factor | 1 | 3 | 5 |
|---|---|---|---|
| Demand clarity | Pain is unclear | Pain exists, intent is mixed | Clear repeated buying or search behavior |
| Budget availability | No clear payer | Payer exists, value uncertain | Clear budget owner and spend precedent |
| Competitive weakness | Strong incumbents everywhere | Some gaps | Obvious gaps buyers care about |
| Reachability | Hard to target | Reachable with work | Easy to reach through known channels |
| Channel feasibility | Channels expensive or unclear | Some testable channels | Clear low-risk validation path |
| Urgency | Nice-to-have | Periodic need | Triggered, painful, time-sensitive |
| Proof availability | Hard to prove results | Some proof can be built | Strong proof is easy to show |
| Execution risk | Heavy regulatory or operational risk | Manageable constraints | Low risk |
| Speed to signal | Months to learn | 2-6 weeks | 7-14 days |
| Strategic fit | Weak fit with team and assets | Partial fit | Strong fit |

| Total | Read | Plan implication |
|---|---|---|
| 40-50 | Enter now | Plan around the full SOM range |
| 30-39 | Enter narrowly | Pick one segment or wedge; size SOM for that wedge only |
| 20-29 | Validate first | Make the first 90 days a validation sprint with kill criteria |
| Below 20 | Avoid for now | Flag in Section 13 open decisions unless the team has a unique advantage |

Use the scorecard alongside the problem size × frequency gate. A large SOM in the weak quadrant (small, infrequent problem) still constrains CAC and channel mix.

## Where this feeds the plan

- **Section 2 (Strategic frame)**: market definition, quadrant, attractiveness score
- **Section 8 (Revenue)** and **Section 10 (12-month outlook)**: SOM range as the ceiling for revenue targets
- **Section 13 (Open decisions)**: low-confidence or unknown inputs, each with a validation task

## Common mistakes

- Treating TAM as proof of demand
- Using a global report for a local-market decision
- Reading search volume as market size
- Presenting one method's output without a cross-check
- Ignoring substitutes and the status quo (spreadsheets, agencies, doing nothing), which compete for the same budget
