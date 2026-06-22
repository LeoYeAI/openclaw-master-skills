# Sales Analytics & Revenue Intelligence

## Revenue Metrics Architecture

### The Metrics Hierarchy
```
LEVEL 1 — BOARD METRICS (Monthly/Quarterly)
├── ARR / MRR (Annual/Monthly Recurring Revenue)
├── Net Revenue Retention (NRR)
├── Gross Revenue Retention (GRR)
├── CAC Payback Period
├── LTV:CAC Ratio
└── Rule of 40 (Revenue Growth % + Profit Margin %)

LEVEL 2 — EXECUTIVE METRICS (Weekly/Monthly)
├── Pipeline Coverage Ratio
├── Win Rate (by segment, source, rep)
├── Average Deal Size (ACV)
├── Sales Cycle Length
├── Sales Velocity
├── Quota Attainment Distribution
└── Forecast Accuracy

LEVEL 3 — OPERATIONAL METRICS (Daily/Weekly)
├── Activities per Rep (calls, emails, meetings)
├── Stage Conversion Rates
├── Lead Response Time
├── SQL-to-Opportunity Conversion
├── Meetings Booked / Held Ratio
├── Proposal-to-Close Rate
├── Pipeline Created (new, pulled-forward, pushed)
└── Churned Pipeline (lost, slipped, disqualified)

LEVEL 4 — DIAGNOSTIC METRICS (As-Needed)
├── Discount Rate by Rep/Segment
├── Multi-Thread Rate
├── Champion Contact Frequency
├── Competitive Win/Loss by Competitor
├── Time-in-Stage Analysis
├── Deal Slip Rate by Stage
├── Content Engagement in Deal Cycle
└── Feature/Use-Case Win Correlation
```

### Core Revenue Metrics — Definitions & Formulas

**MRR (Monthly Recurring Revenue)**
```
MRR = Sum of all active monthly subscription values

Components:
- New MRR: From new customers this month
- Expansion MRR: Upgrades, add-ons, seat additions
- Contraction MRR: Downgrades, seat removals
- Churn MRR: Lost customers

Net New MRR = New MRR + Expansion MRR - Contraction MRR - Churn MRR
ARR = MRR × 12
```

**Net Revenue Retention (NRR)**
```
NRR = (Starting MRR + Expansion - Contraction - Churn) / Starting MRR × 100

Benchmarks:
- Below 90%: Critical — churn is destroying growth
- 90–100%: Mediocre — treading water
- 100–110%: Good — mild organic growth
- 110–130%: Excellent — strong expansion
- 130%+: Elite — world-class (e.g., Snowflake, Twilio at peak)
```

**Gross Revenue Retention (GRR)**
```
GRR = (Starting MRR - Contraction - Churn) / Starting MRR × 100
(Never exceeds 100% — excludes expansion)

Benchmarks:
- Below 80%: Severe retention problem
- 80–90%: Below average
- 90–95%: Good
- 95%+: Excellent
```

**Customer Acquisition Cost (CAC)**
```
CAC = (Total Sales & Marketing Spend) / (New Customers Acquired)

Blended CAC: All spend / all new customers
Paid CAC: Paid channel spend / paid-channel customers
Organic CAC: Non-paid spend / organic customers
Fully Loaded CAC: Include overhead, tools, management
```

**LTV (Lifetime Value)**
```
Simple LTV = ARPA × Gross Margin % × Average Customer Lifespan

LTV via churn:
LTV = (ARPA × Gross Margin %) / Monthly Churn Rate

Cohort-based LTV (most accurate):
Track actual revenue per cohort over time, project remaining lifetime
```

**LTV:CAC Ratio**
```
LTV:CAC = Customer Lifetime Value / Customer Acquisition Cost

Benchmarks:
- Below 1:1: Losing money on every customer
- 1:1–3:1: Unsustainable or very early stage
- 3:1–5:1: Healthy and efficient
- 5:1+: Under-investing in growth (or exceptional efficiency)
```

**CAC Payback Period**
```
CAC Payback = CAC / (ARPA × Gross Margin %)
(Expressed in months)

Benchmarks:
- Under 6 months: Excellent
- 6–12 months: Good
- 12–18 months: Acceptable for enterprise
- 18–24 months: Concerning
- 24+ months: Unsustainable without significant capital
```

**Sales Velocity**
```
Sales Velocity = (# Opportunities × Win Rate × Avg Deal Size) / Sales Cycle Length

Units: Revenue per day (or per period)

Improvement levers:
1. Increase number of qualified opportunities
2. Improve win rate
3. Increase average deal size
4. Decrease sales cycle length

Even small improvements across all four compound dramatically.
```

**Magic Number (Sales Efficiency)**
```
Magic Number = Net New ARR (Quarter) / Sales & Marketing Spend (Prior Quarter)

Benchmarks:
- Below 0.5: Inefficient — fix GTM before scaling
- 0.5–0.75: Acceptable — optimize while growing
- 0.75–1.0: Efficient — invest more
- 1.0+: Highly efficient — accelerate spending
```

**Burn Multiple**
```
Burn Multiple = Net Burn / Net New ARR

Benchmarks:
- Below 1x: Best-in-class
- 1x–1.5x: Good
- 1.5x–2x: Concerning
- 2x+: Inefficient — need to improve unit economics
```

---

## Funnel Analytics

### Full-Funnel Metrics Map

| Stage | Key Metrics | Conversion Benchmark (B2B SaaS) |
|-------|------------|--------------------------------|
| Visitor | Unique visitors, traffic sources, bounce rate | — |
| Lead | MQLs, lead volume by source, cost per lead | 2–5% visitor-to-lead |
| MQL | MQL volume, MQL-to-SQL rate, time to qualify | 15–30% lead-to-MQL |
| SQL | SQL volume, SQL-to-Opportunity rate | 40–60% MQL-to-SQL |
| Opportunity | Pipeline created, avg deal size | 50–70% SQL-to-Opp |
| Proposal | Proposals sent, proposal-to-close rate | 60–80% Opp-to-Proposal |
| Closed Won | Deals closed, revenue, win rate | 20–30% overall win rate |

### Stage Conversion Analysis

**Waterfall Analysis**
```
Track volume at each stage month-over-month:
- Jan: 1000 leads → 300 MQLs → 150 SQLs → 90 Opps → 27 Closed
- Feb: 1200 leads → 340 MQLs → 160 SQLs → 85 Opps → 30 Closed

Calculate stage-to-stage conversion rates:
- Lead-to-MQL: Jan 30%, Feb 28.3% (declining — investigate lead quality)
- SQL-to-Opp: Jan 60%, Feb 53.1% (declining — investigate qualification)
- Opp-to-Close: Jan 30%, Feb 35.3% (improving — positive signal)
```

**Conversion Rate Decomposition**
```
When a conversion rate changes, decompose by:
1. Source/Channel: Which channels improved/declined?
2. Segment: SMB vs. Mid-Market vs. Enterprise?
3. Rep: Top performers vs. bottom performers?
4. Lead Score: High-score vs. low-score leads?
5. Time Period: Weekday vs. weekend? Beginning vs. end of month?
6. Content/Campaign: Which campaigns drive best conversion?
```

**Funnel Velocity Analysis**
```
Track median time between stages:
- Lead → MQL: 3 days (target: <7 days)
- MQL → SQL: 5 days (target: <5 days)
- SQL → Opp: 2 days (target: <3 days)
- Opp → Proposal: 14 days (target: <14 days)
- Proposal → Close: 21 days (target: <21 days)
- Total cycle: 45 days

Flag: Any deal 2x+ median at any stage needs intervention
```

### Funnel Diagnostics Framework

**The Leaky Bucket Audit**
```
For each funnel stage, calculate:
1. Volume In (entering stage)
2. Volume Out — Won (advancing to next stage)
3. Volume Out — Lost (disqualified, lost, ghosted)
4. Volume Stuck (no activity for >X days)
5. Leak Rate = (Lost + Stuck) / Volume In

Priority: Fix the stage with the highest leak rate first
(Fixing bottom-of-funnel leaks has highest revenue impact per fix)
```

**Revenue Attribution by Funnel Stage**
```
Influenced Revenue by Stage:
- What % of closed-won revenue touched each stage?
- What's the conversion rate from each stage?
- What's the average value of deals at each stage?

This reveals where revenue is actually created vs. where effort is spent.
```

---

## Cohort Analysis

### Revenue Cohort Analysis

**Monthly Cohort Retention Table**
```
              Month 0  Month 1  Month 2  Month 3  Month 6  Month 12
Jan Cohort    100%     92%      88%      85%      78%      65%
Feb Cohort    100%     94%      91%      88%      82%      —
Mar Cohort    100%     91%      86%      —        —        —
Apr Cohort    100%     95%      —        —        —        —

Read: Of customers acquired in January, 65% are still paying after 12 months.
Insight: February cohort retains better — investigate what changed (onboarding? ICP? pricing?).
```

**Revenue Cohort (Dollar Retention)**
```
              Month 0  Month 1  Month 2  Month 3  Month 6  Month 12
Jan Cohort    $100K    $95K     $93K     $92K     $98K     $112K
Feb Cohort    $120K    $116K    $115K    $118K    $130K    —

Read: January cohort's revenue exceeds starting value by month 12 (NRR > 100%).
Dollar retention often improves even as logo retention declines due to expansion.
```

### Cohort Segmentation Dimensions

```
Segment cohorts by:
1. Acquisition Channel: Organic vs. paid vs. referral vs. outbound
2. Plan/Tier: Free trial vs. paid; SMB vs. Enterprise
3. ICP Fit Score: High-fit vs. low-fit
4. Onboarding Completion: Full onboarding vs. partial vs. none
5. First Value Milestone: Reached activation vs. didn't
6. Sales Rep: Rep A vs. Rep B (for coaching insights)
7. Use Case: Primary use case at signup
8. Geography: Region-based retention patterns
9. Company Size: 1–10, 11–50, 51–200, 201–1000, 1000+
10. Deal Size: Quartile-based (bottom 25% ACV vs. top 25%)
```

### Cohort Analysis Best Practices

1. **Always use cohorts, never averages** — averages hide trends
2. **Compare cohorts to find inflection points** — when did retention improve? What changed?
3. **Calculate payback by cohort** — some channels have fast payback but low LTV
4. **Track both logo and dollar retention** — dollar retention masks logo churn
5. **Use cohorts for forecasting** — project future revenue using cohort curves
6. **Minimum cohort size: 30+** — smaller cohorts produce unreliable data
7. **Compare retention curves, not just endpoints** — the shape of the curve matters

---

## Unit Economics Deep Dive

### LTV Calculation Methods

**Method 1: Simple (Average-Based)**
```
LTV = ARPA × Gross Margin % × (1 / Monthly Churn Rate)

Example: $500 ARPA × 80% margin × (1/0.02) = $500 × 0.8 × 50 = $20,000
Weakness: Assumes constant churn rate (rarely true).
```

**Method 2: Cohort-Based (Empirical)**
```
Track actual cumulative revenue per cohort over time.
Plot the curve. Project remaining lifetime using curve fitting.

Best method. Accounts for non-linear retention curves.
Requires 12+ months of cohort data.
```

**Method 3: DCF-Adjusted**
```
LTV = Σ (Revenue_t × Gross Margin %) / (1 + discount_rate)^t

Use 10% annual discount rate for SaaS.
More accurate for long-lifetime customers where time value of money matters.
```

**Method 4: Segment-Specific**
```
Calculate LTV separately for each segment:
- SMB LTV: $8,000 (high churn, low ACV)
- Mid-Market LTV: $45,000 (moderate churn, moderate ACV)
- Enterprise LTV: $250,000 (low churn, high ACV, expansion)

Blended LTV hides segment economics. Always disaggregate.
```

### CAC Analysis

**CAC by Channel**
```
Channel          Spend    Customers  CAC      LTV:CAC  Payback
Google Ads       $50K     25         $2,000   4.0x     8 mo
LinkedIn Ads     $40K     10         $4,000   3.0x     16 mo
Content/SEO      $30K     40         $750     10.7x    3 mo
Outbound SDR     $80K     20         $4,000   5.0x     12 mo
Referral         $10K     15         $667     12.0x    2.5 mo
Events           $60K     12         $5,000   3.6x     15 mo

Insight: Content/SEO and referral have best unit economics.
Events have worst CAC but may influence enterprise deals not captured here.
```

**Fully-Loaded CAC Components**
```
Include in CAC calculation:
- Direct ad spend
- Marketing team salaries (allocated %)
- Sales team salaries + commissions (for new business)
- Tools & technology (CRM, marketing automation, etc.)
- Content production costs
- Event costs
- Agency fees
- Overhead allocation

Exclude:
- Customer success costs (belongs in retention/LTV calculation)
- Product development (belongs in R&D)
- General admin overhead
```

### Unit Economics Health Check

```
Metric                  Red Flag        Healthy         Best-in-Class
LTV:CAC                 <3:1            3:1–5:1         >5:1
CAC Payback             >18 months      12–18 months    <12 months
Gross Margin            <60%            70–80%          >80%
Net Revenue Retention   <90%            100–120%        >130%
Gross Revenue Retention <80%            90–95%          >95%
Burn Multiple           >2x             1–1.5x          <1x
Magic Number            <0.5            0.75–1.0        >1.0
Rule of 40              <20             30–40           >40
```

---

## Attribution Modeling

### Attribution Models

**Single-Touch Models**
```
First Touch: 100% credit to first interaction
- Use case: Understanding which channels drive awareness
- Weakness: Ignores nurture and closing activities

Last Touch: 100% credit to last interaction before conversion
- Use case: Understanding which channels close deals
- Weakness: Ignores awareness and nurture activities

Last Non-Direct Touch: 100% credit to last non-direct-visit interaction
- Use case: Better last-touch when direct visits are high
```

**Multi-Touch Models**
```
Linear: Equal credit to all touchpoints
- Use case: When all touchpoints are equally valued
- Example: 5 touchpoints = 20% credit each

Time Decay: More credit to touchpoints closer to conversion
- Use case: When recent touches are more influential
- Example: Last touch 40%, second-to-last 25%, third 15%, fourth 12%, fifth 8%

U-Shaped (Position-Based): 40% first touch, 40% last touch, 20% split among middle
- Use case: When discovery and closing are most important
- Best for lead generation analysis

W-Shaped: 30% first touch, 30% lead creation, 30% opportunity creation, 10% remaining
- Use case: B2B with clear funnel stages
- Best for full-funnel B2B analysis

Custom/Algorithmic: Machine learning assigns weights based on actual conversion data
- Use case: When you have sufficient data volume (1000+ conversions)
- Most accurate but requires data infrastructure
```

### Attribution Implementation

**Tracking Infrastructure**
```
Required tracking:
1. UTM Parameters: source, medium, campaign, content, term on all links
2. First-Touch Cookie: Capture and store first UTM parameters
3. Multi-Touch Session Tracking: Log all sessions with UTMs
4. CRM Integration: Pass attribution data to opportunity records
5. Offline Event Tracking: Match event attendees to CRM records
6. Self-Reported Attribution: "How did you hear about us?" field

UTM Convention:
utm_source=linkedin
utm_medium=paid_social
utm_campaign=q1_2025_enterprise_awareness
utm_content=ceo_testimonial_video
utm_term=enterprise_saas
```

**Attribution Data Model**
```
Touchpoint Record:
- Contact ID
- Timestamp
- Channel (source/medium)
- Campaign
- Content/Asset
- Page/URL
- Touchpoint Type (impression, click, form fill, demo, etc.)
- Conversion Event (lead, MQL, SQL, Opportunity, Closed Won)
- Revenue Attributed (based on model)

Enable: Joining touchpoints to pipeline and revenue for ROI analysis.
```

### Channel ROI Analysis

```
For each channel, calculate:
1. Total Investment: All costs (spend, people, tools)
2. Pipeline Generated: Total pipeline $ influenced
3. Revenue Generated: Closed-won $ attributed
4. CAC by Channel: Investment / customers acquired
5. ROI: (Revenue - Investment) / Investment × 100
6. Payback: Months to recover channel CAC
7. Efficiency Ratio: Revenue / Investment

Compare across channels using consistent attribution model.
Report with both first-touch and multi-touch for complete picture.
```

---

## Pipeline Forecasting

### Forecasting Methods

**Method 1: Bottom-Up (Rep Commit)**
```
Process:
1. Each rep reviews their pipeline
2. Categorizes deals: Commit / Best Case / Upside
3. Manager reviews and adjusts
4. Roll up to org-level forecast

Accuracy: 60–75% (bias-prone, optimism inflation)
Best for: Mid-market/enterprise with experienced reps
```

**Method 2: Historical Stage-Based**
```
Process:
1. Calculate historical conversion rate at each stage
2. Multiply current pipeline value at each stage by conversion rate
3. Sum weighted pipeline for forecast

Example:
Stage         Pipeline Value  Historical Win Rate  Weighted Forecast
Discovery     $500K           15%                  $75K
Demo          $800K           30%                  $240K
Proposal      $600K           55%                  $330K
Negotiation   $400K           75%                  $300K
Verbal        $200K           90%                  $180K
                                         TOTAL:    $1,125K

Accuracy: 70–80%
Best for: High-volume, repeatable sales motions
```

**Method 3: Weighted Pipeline with Aging**
```
Apply decay factor based on time-in-stage vs. historical average:

Adjusted Win Rate = Base Win Rate × Aging Factor

Aging Factor:
- Under median time: 1.0 (on track)
- 1–1.5x median: 0.8 (slowing)
- 1.5–2x median: 0.5 (at risk)
- Over 2x median: 0.2 (likely lost)

This penalizes stuck deals that inflate forecasts.
```

**Method 4: AI/ML Predictive**
```
Inputs:
- Deal attributes (size, segment, source, product)
- Activity data (emails, calls, meetings, stakeholders engaged)
- Temporal patterns (time in stage, velocity changes)
- Rep characteristics (historical performance, experience)
- External signals (company news, hiring, funding)

Output: Probability-weighted forecast per deal
Accuracy: 80–90% with sufficient training data
Requires: 500+ historical closed deals, clean CRM data
```

### Forecast Categories

```
Category    Definition                                         Weight
Commit      Rep stakes their reputation. 90%+ confident.       95%
Best Case   Strong signal, 1–2 things must go right.           60–70%
Pipeline    Qualified, engaged, but multiple unknowns.         20–40%
Upside      Early stage, speculative. Not in formal forecast.  5–10%
```

### Forecast Accuracy Measurement

```
Forecast Accuracy = 1 - |Actual - Forecast| / Actual × 100

Track by:
- Period (weekly, monthly, quarterly)
- Category (commit accuracy, best case accuracy)
- Rep (identify consistent over/under-forecasters)
- Segment (enterprise vs. SMB)

Targets:
- Commit accuracy: >90%
- Best case accuracy: >70%
- Overall quarterly accuracy: >85%
```

---

## Win/Loss Analysis

### Win/Loss Analysis Framework

**Data Collection**
```
For every closed deal (won or lost), capture:

Quantitative:
- Deal size (original vs. final)
- Sales cycle length
- Number of stakeholders involved
- Number of meetings/demos
- Discount applied
- Competitive situation (vs. whom)
- Lead source
- ICP fit score

Qualitative (from interviews or debrief forms):
- Primary reason won/lost (single most important factor)
- Secondary factors
- Decision criteria and their weights
- Competitive strengths/weaknesses cited
- Objections encountered and how handled
- Champion strength (1–5)
- Procurement experience
- Content/assets that influenced decision
```

**Win/Loss Interview Process**
```
Timing: 2–4 weeks after decision (while memory is fresh)
Method: 20-minute phone/video interview with decision-maker

Interview Guide:
1. Walk me through your evaluation process from beginning to end.
2. Who was involved in the decision, and what did each person care about?
3. What were your top 3 decision criteria, and how did you weight them?
4. How did we compare to alternatives on each criterion?
5. What was the single most important factor in your decision?
6. Was there a moment where you felt the decision shifted? What happened?
7. What could we have done differently?
8. How would you rate the experience of working with our team? (1–10)

Best practice: Use a neutral third party for interviews (reduces bias).
```

### Win/Loss Analysis Outputs

**Win Rate by Dimension**
```
Dimension           Segment A    Segment B    Segment C
By Source:          Inbound 35%  Outbound 22% Partner 40%
By Competitor:      vs. X 45%   vs. Y 30%    vs. Z 55%
By Deal Size:       <$25K 38%   $25–100K 28% >$100K 22%
By Segment:         SMB 35%     Mid-Mkt 25%  Enterprise 18%
By Rep:             Rep A 40%   Rep B 25%    Rep C 32%
By Product:         Core 35%    Premium 28%  Platform 20%
By Use Case:        Use A 42%   Use B 30%    Use C 18%
```

**Loss Reason Taxonomy**
```
Category            Sub-Reason                    Frequency  Trend
Price               Too expensive (absolute)      25%        Stable
Price               Poor ROI perception            8%        ↑ Rising
Competition         Feature gap vs. [Competitor]  18%        ↑ Rising
Competition         Incumbent advantage           10%        Stable
Timing              No budget this cycle           12%        Seasonal
Timing              Project deprioritized          7%        ↑ Rising
Product             Missing critical feature       8%        ↓ Declining
Product             Integration gap                5%        Stable
Process             Couldn't reach decision-maker  4%        Stable
Process             Procurement blocked            3%        Stable
```

**Competitive Intelligence from Win/Loss**
```
Track per competitor:
- Head-to-head win rate (trend over time)
- Primary reasons we win against them
- Primary reasons we lose against them
- Their perceived strengths (from buyer interviews)
- Their perceived weaknesses
- Common displacement strategies that work
- Common objections they raise about us
- Deals where they weren't considered (and why — positioning insight)
```

---

## Sales Velocity & Efficiency Metrics

### Sales Velocity Formula & Levers

```
Velocity = (Opportunities × Win Rate × Avg Deal Size) / Cycle Length

Lever           Current   Target    Impact on Velocity
Opportunities   100       120       +20%
Win Rate        25%       30%       +20%
Avg Deal Size   $50K      $60K      +20%
Cycle Length     60 days   50 days   +20%

Combined impact: 1.2 × 1.2 × 1.2 × 1.2 = 2.07x velocity (107% improvement)
Small improvements across all four levers compound dramatically.
```

### Efficiency Metrics

**Revenue per Rep**
```
Revenue per Rep = Total New Business Revenue / Number of Quota-Carrying Reps

Benchmarks (B2B SaaS):
- SMB motion: $400K–$700K ARR per rep
- Mid-Market: $700K–$1.2M ARR per rep
- Enterprise: $1M–$3M ARR per rep

Track trend: Declining revenue per rep = GTM efficiency problem
```

**Quota Attainment Distribution**
```
Track distribution, not just average:
- % of reps at 0–50% attainment
- % of reps at 50–75% attainment
- % of reps at 75–100% attainment
- % of reps at 100–150% attainment
- % of reps at 150%+ attainment

Healthy distribution: 60–70% of reps at or above quota
Warning sign: More than 30% of reps below 50% (quota setting or enablement problem)
Warning sign: Top 20% of reps produce 80%+ of revenue (dependency risk)
```

**Ramp Time & Productivity**
```
Track by tenure cohort:
- Month 1–3: Expected at 0–25% of full quota
- Month 4–6: Expected at 25–50% of full quota
- Month 7–9: Expected at 50–75% of full quota
- Month 10–12: Expected at 75–100% of full quota

Fully ramped: 12+ months (varies by complexity)
Measure: Time to first deal, time to full productivity
```

---

## Financial Projections & Board Reporting

### Revenue Projection Models

**Bottom-Up Revenue Model**
```
Inputs:
- Current ARR: $5M
- New business ARR per quarter (from pipeline + bookings forecast)
- Expansion rate (from NRR historical)
- Churn rate (from GRR historical)
- Seasonality adjustments

Quarterly Projection:
Q1 Starting ARR: $5.0M
+ New Business: $800K
+ Expansion: $250K (5% of starting)
- Contraction: $100K (2% of starting)
- Churn: $150K (3% of starting)
= Q1 Ending ARR: $5.8M

Repeat for Q2, Q3, Q4 with growth assumptions.
```

**Capacity-Based Revenue Model**
```
Revenue Capacity = Number of Ramped Reps × Quota × Expected Attainment %

Example:
- 10 ramped reps × $1M quota × 70% attainment = $7M new ARR capacity
- 5 ramping reps × $1M quota × 35% attainment = $1.75M
- Total new ARR capacity: $8.75M

Hiring plan drives revenue plan:
- Hire dates → ramp timelines → productive capacity → revenue
```

### Board-Level Sales Metrics Dashboard

**Monthly Board Package — Sales Section**
```
Page 1: Revenue Summary
- ARR waterfall (start → new → expansion → contraction → churn → end)
- ARR vs. plan (chart with gap analysis)
- MRR trend (12-month trailing)
- Revenue composition (new vs. expansion vs. existing)

Page 2: GTM Efficiency
- CAC by channel (trend)
- LTV:CAC ratio (trend)
- CAC payback period (trend)
- Magic number (trend)
- Sales efficiency ratio (new ARR / S&M spend)

Page 3: Pipeline & Forecast
- Pipeline coverage ratio (3x+ = healthy)
- Pipeline waterfall (created, advanced, won, lost)
- Forecast vs. actual (trailing 4 quarters for accuracy trend)
- Win rate trend (overall and by segment)

Page 4: Team Performance
- Quota attainment distribution
- Revenue per rep
- Ramp progress for new hires
- Headcount vs. plan

Page 5: Leading Indicators
- Pipeline created this month vs. prior months
- MQL/SQL volume trends
- Activity metrics (meetings, demos) trends
- NRR and expansion trends
```

### Investor / Board Narrative

```
Structure every board narrative around:

1. The Number: Did we hit plan? By how much?
2. The Why: What drove the result? (1–2 key factors)
3. The Trend: Is performance improving or declining?
4. The Risks: What could derail next quarter?
5. The Plan: What are we doing about the risks?
6. The Ask: What decisions do we need from the board?

Keep it to 1 page of narrative per section. Let data tell the story.
```

---

## Sales Reporting Best Practices

### Dashboard Design Principles

1. **One metric per question** — Each dashboard answers a single question
2. **Comparison is insight** — Always show vs. target, vs. prior period, vs. benchmark
3. **Trend over snapshot** — Show trailing 6–12 months, not just current month
4. **Segment always** — Every metric should be drillable by segment, rep, source, product
5. **Leading over lagging** — Prioritize metrics you can act on now
6. **Automate delivery** — Weekly email with key metrics; don't require login
7. **Red/Yellow/Green** — Make status immediately visible
8. **Define every metric** — Include calculation methodology in dashboard documentation

### Reporting Cadence

```
Daily:
- Activity metrics (calls, emails, meetings)
- Pipeline changes (new, advanced, lost)
- Deal alerts (at risk, closing soon, stalled)

Weekly:
- Pipeline review (stage-by-stage)
- Forecast update
- Win/loss summary
- Leading indicators dashboard

Monthly:
- Full funnel review
- Channel performance
- Rep performance
- Unit economics update

Quarterly:
- Board package
- Win/loss analysis deep dive
- Cohort analysis
- Competitive landscape update
- Territory and quota review
- GTM strategy review
```

### Common Analytics Mistakes

1. **Vanity metrics** — Tracking impressions, page views, or MQLs without connecting to revenue
2. **Blended averages** — Averaging across segments hides critical segment-level problems
3. **Point-in-time snapshots** — Looking at current month without trend context
4. **Attribution bias** — Over-crediting last touch, ignoring multi-touch influence
5. **Survivorship bias** — Analyzing only won deals, not lost deals
6. **Small sample conclusions** — Making strategic changes based on 10 data points
7. **Lagging indicator focus** — Reacting to revenue misses instead of monitoring leading indicators
8. **Inconsistent definitions** — Different teams defining "MQL" or "pipeline" differently
9. **Ignoring cohorts** — Treating all customers as one population
10. **Activity vs. outcome confusion** — Measuring effort (calls made) not impact (meetings booked)
