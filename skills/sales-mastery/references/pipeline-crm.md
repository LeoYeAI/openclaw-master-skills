# Pipeline Management & CRM — Reference Guide

Complete framework for designing, building, and optimizing sales pipelines, CRM workflows, forecasting systems, and revenue operations infrastructure.

---

## TABLE OF CONTENTS
1. Pipeline Architecture Design
2. Stage Definitions & Exit Criteria
3. Lead Scoring Models
4. Deal Scoring & Prioritization
5. Sales Forecasting Frameworks
6. CRM Workflow Automation
7. Pipeline Metrics & Health Indicators
8. Territory & Quota Design
9. Sales Capacity Planning
10. Reporting & Dashboards

---

## 1. PIPELINE ARCHITECTURE DESIGN

### Pipeline Stage Design Principles
- Stages should be based on BUYER actions, not seller actions
- Each stage must have clear, observable entry criteria (no subjective stages)
- 5-7 stages is optimal — fewer is too vague, more creates friction
- Stage names should be universally understood by the team
- Every stage must have a defined set of required activities and exit criteria

### Standard B2B SaaS Pipeline

**Stage 1 — Lead/MQL**: Marketing-qualified lead that fits ICP criteria. Entry: meets scoring threshold.
Exit: SDR has qualified via conversation.

**Stage 2 — SQL/Discovery**: Sales-qualified, discovery call completed. Entry: confirmed fit on BANT/MEDDIC
criteria. Exit: discovery complete, mutual interest confirmed.

**Stage 3 — Demo/Evaluation**: Product demonstration completed. Entry: scheduled and attended demo.
Exit: positive evaluation, stakeholders engaged.

**Stage 4 — Proposal/Negotiation**: Proposal sent, pricing discussed. Entry: proposal delivered.
Exit: verbal agreement on terms.

**Stage 5 — Contract/Legal**: Contract sent for review. Entry: contract in prospect's hands.
Exit: signed contract.

**Stage 6 — Closed Won**: Deal signed and booked. Entry: signature received.

**Stage 0 — Closed Lost**: Deal lost. Entry: prospect declined. Required: loss reason captured.

### Win Probability by Stage (benchmarks)
- Lead/MQL: 5-10%
- SQL/Discovery: 15-25%
- Demo/Evaluation: 30-50%
- Proposal: 50-70%
- Contract: 75-90%
- Closed Won: 100%

Adjust based on historical data. These are starting points.

---

## 2. STAGE DEFINITIONS & EXIT CRITERIA

### For each pipeline stage, document:

**Entry Criteria**: What MUST be true for a deal to enter this stage?
- Example: "Discovery stage requires: confirmed decision-maker engaged, budget range discussed,
  timeline identified, specific pain articulated"

**Required Activities**: What must the seller DO in this stage?
- Example: "Demo stage requires: personalized demo delivered, technical questions answered,
  next steps agreed, champion identified"

**Exit Criteria**: What must be TRUE to advance to the next stage?
- Example: "Proposal stage exit requires: pricing presented, procurement process mapped,
  written confirmation of intent to proceed"

**Required Fields in CRM**: What data must be captured at this stage?
- Example: "At SQL stage: decision-maker name, budget range, timeline, competitive alternatives,
  compelling event, champion name"

**Stage Duration Benchmark**: How long should deals spend here?
- Track median and mean. Deals significantly exceeding the benchmark need inspection.

---

## 3. LEAD SCORING MODELS

### Demographic/Firmographic Scoring (Fit Score)
Score based on how well the lead matches your ICP:

| Factor | Criteria | Points |
|--------|----------|--------|
| Company Size | Ideal range (e.g., 100-1000 employees) | +20 |
| Company Size | Adjacent range | +10 |
| Company Size | Outside range | -10 |
| Industry | Target industry | +15 |
| Role/Title | Decision-maker | +25 |
| Role/Title | Influencer | +15 |
| Role/Title | End user | +5 |
| Geography | Target region | +10 |
| Technology | Uses complementary tech | +10 |
| Revenue | In target range | +15 |

### Behavioral Scoring (Intent Score)
Score based on engagement and buying signals:

| Action | Points | Decay |
|--------|--------|-------|
| Visited pricing page | +25 | 14 days |
| Requested demo | +50 | 30 days |
| Downloaded case study | +15 | 21 days |
| Attended webinar | +20 | 21 days |
| Opened 3+ emails | +10 | 7 days |
| Visited site 3+ times | +15 | 14 days |
| Engaged on LinkedIn | +5 | 7 days |
| Downloaded whitepaper | +10 | 21 days |
| Used free tool/calculator | +20 | 14 days |
| Watched product video | +15 | 14 days |

### Score Thresholds
- **MQL threshold**: Fit score > 40 AND Intent score > 30
- **SQL threshold**: MQL + successful qualification call
- **Hot lead alert**: Intent score > 80 (immediate SDR follow-up)

### Score Decay
Apply time-based decay to behavioral scores. A lead who visited your pricing page 6 months ago is not
the same as one who visited yesterday. Standard decay: 50% reduction after the decay period.

---

## 4. DEAL SCORING & PRIORITIZATION

### Deal Health Score (0-100)

Calculate based on weighted factors:

| Factor | Weight | Criteria |
|--------|--------|----------|
| Champion Identified | 20% | Named champion with access to decision-maker |
| Economic Buyer Engaged | 20% | Direct contact with budget holder |
| Compelling Event | 15% | Time-bound reason to buy (contract expiry, mandate, etc.) |
| Decision Process Mapped | 15% | Known timeline, criteria, and stakeholders |
| Budget Confirmed | 15% | Explicit budget range confirmed |
| Next Steps Clear | 10% | Specific next action with date committed |
| Competition Known | 5% | Competitive landscape understood |

### Priority Matrix

**Priority 1 (work now)**: Health score > 70, closing this quarter, > $50K ACV
**Priority 2 (work this week)**: Health score > 50, closing within 2 quarters
**Priority 3 (nurture)**: Health score < 50, long timeline, or sub-threshold ACV
**Deprioritize**: Health score < 30 AND no compelling event AND no champion

---

## 5. SALES FORECASTING FRAMEWORKS

### Forecast Categories

**Commit**: Deal will close this period. Sales rep would "bet their paycheck" on it. Must have: signed contract
in hand, or verbal commitment with contract in transit. Historical accuracy target: 90%+.

**Best Case**: High probability of closing this period. Must have: champion confirmed, pricing agreed, timeline
aligned, no known blockers. Historical accuracy target: 50-70%.

**Pipeline**: Active deal with potential to close this period. Must have: active engagement, discovery complete,
demo delivered. Historical accuracy target: 20-40%.

**Upside**: Deal could pull in but significant uncertainty remains. Tracking for awareness.

### Forecasting Methods

**Bottom-Up (rep-level)**: Each rep forecasts their deals, manager validates. Most common. Prone to optimism
bias and sandbagging.

**Historical Conversion**: Apply historical stage-to-close conversion rates to current pipeline.
Example: If 30% of Proposal-stage deals close, and you have $1M in Proposal, forecast $300K.

**Weighted Pipeline**: Sum of (deal value × win probability) for all deals in pipeline. Simple but useful
as a cross-check.

**Trend-Based**: Use trailing 3-6 month conversion rates, deal sizes, and cycle lengths to project forward.
Accounts for seasonal patterns.

**AI/ML-Based**: Use historical data to build predictive models. Best for large sales teams with significant
data. Factor in: stage, time in stage, activity level, stakeholder engagement, deal size vs. average.

### Forecasting Cadence
- **Weekly**: Pipeline review, deal inspection, forecast update
- **Monthly**: Forecast vs. actual analysis, coverage ratio check, pipeline quality review
- **Quarterly**: Deep pipeline analysis, capacity assessment, territory review, forecast accuracy audit

---

## 6. CRM WORKFLOW AUTOMATION

### Essential Automations

**Lead Routing**: Auto-assign leads based on territory, round-robin, or scoring. Route hot leads immediately.
Re-assign if no contact within SLA (typically 5 minutes for inbound, 24 hours for MQL).

**Task Creation**: Auto-create follow-up tasks when deals change stages, when no activity occurs for X days,
or when specific events trigger (e.g., contract viewed, pricing page visited).

**Email Sequences**: Trigger automated email sequences based on stage, behavior, or time. Pause when rep
takes manual action.

**Notifications**: Alert reps when: hot lead enters their territory, deal has no activity for 7+ days,
contract is viewed, competitor is mentioned, key stakeholder visits the website.

**Stage Advancement**: Auto-advance stages when criteria are met (e.g., meeting completed → Discovery,
proposal viewed → Negotiation). Require manual confirmation for later stages.

**Data Hygiene**: Flag deals with missing required fields, deals stuck in stage beyond benchmark,
deals without next steps, and opportunities without recent activity.

### CRM Data Quality Rules
- Every deal must have: close date, amount, stage, next step, and owner
- Close dates in the past must be updated or deals closed-lost
- Deals without activity for 30+ days should be reviewed (stale pipeline)
- Required fields must be enforced at each stage transition
- Contact roles (champion, decision-maker, etc.) must be mapped for deals > $25K

---

## 7. PIPELINE METRICS & HEALTH INDICATORS

### Core Pipeline Metrics

**Pipeline Coverage Ratio**: Total pipeline value ÷ quota. Healthy = 3-4x. Below 3x = pipeline problem.
Above 5x = deal quality problem (or sandbag culture).

**Pipeline Velocity**: (Number of deals × Average deal size × Win rate) ÷ Average sales cycle length.
The single best holistic pipeline metric. Improving any of the four components increases velocity.

**Win Rate**: Deals won ÷ Total deals resolved (won + lost). Track by stage, by rep, by segment, and by
source. Overall win rate benchmarks: 15-25% from SQL, 40-60% from Proposal stage.

**Average Deal Size**: Track trends over time. Increasing = good (moving upmarket or packaging better).
Decreasing = investigate (discounting, wrong-fit deals, competition).

**Sales Cycle Length**: Median days from SQL to Closed Won. Track by segment, deal size, and source.
Shortening = operational improvement. Lengthening = investigate.

**Stage Conversion Rates**: Percentage of deals that advance from each stage to the next. Drop-offs at
specific stages indicate systemic issues.

### Pipeline Health Dashboard Elements
1. Pipeline value by stage (waterfall or funnel chart)
2. Coverage ratio vs. target
3. Pipeline velocity trend (month over month)
4. Win rate trend
5. Average deal size trend
6. Sales cycle length trend
7. Stage conversion rates
8. Pipeline created this period vs. pipeline needed
9. Deals at risk (stale, no next step, slipped close date)
10. Rep performance vs. quota (pipeline and closed)

---

## 8. TERRITORY & QUOTA DESIGN

### Territory Design Principles
- Equal opportunity: each territory should have roughly equal revenue potential
- Clear boundaries: no overlap, no confusion about ownership
- Account fit: match rep strengths to territory characteristics
- Growth potential: balance current revenue with future potential

### Territory Segmentation Approaches
- **Geographic**: By region, state, or metro area
- **Industry/Vertical**: By market segment
- **Company size**: By employee count or revenue
- **Named accounts**: Specific accounts assigned (enterprise)
- **Hybrid**: Combination of the above

### Quota Setting Framework
- **Top-down**: Company target ÷ number of reps × coverage factor
- **Bottom-up**: Historical performance × growth expectation + new market opportunity
- **Balanced**: Average of top-down and bottom-up approaches
- **Quota should be achievable by 60-70% of reps** — if fewer achieve, quota is too high; if more, too low
- **Ramp quotas for new hires**: 0% month 1, 25% month 2, 50% month 3, 75% month 4, 100% month 5+

---

## 9. SALES CAPACITY PLANNING

### The Capacity Model
For each rep: (Available selling days × Daily capacity) × Historical conversion rates = Expected output

**Variables to model**:
- Number of quota-carrying reps (current and planned hires)
- Ramp time for new hires (typically 3-6 months to full productivity)
- Average deals per rep per quarter (by segment)
- Average deal size (by segment)
- Win rate (by segment and rep tenure)
- Non-selling time (training, admin, vacation, meetings)

### Hiring Plan from Revenue Target
Work backward from revenue target:
1. Annual target = $10M
2. Average deal size = $50K → need 200 deals
3. Win rate = 25% → need 800 opportunities
4. Deals per rep per year (fully ramped) = 80 opportunities
5. Need 10 fully-ramped reps → hire 12 to account for ramp and attrition

---

## 10. REPORTING & DASHBOARDS

### Executive Revenue Dashboard
1. Revenue vs. target (current period and YTD)
2. Pipeline coverage for current and next quarter
3. Forecast by category (commit, best case, pipeline)
4. Win rate trend
5. New business vs. expansion revenue split
6. Top 10 deals with status

### Sales Manager Dashboard
1. Team pipeline by stage
2. Individual rep performance vs. quota
3. Activity metrics (calls, emails, meetings, demos)
4. Deal inspection: stale deals, slipped close dates, missing data
5. Conversion rates by stage and rep
6. Forecast accuracy trend

### SDR/BDR Dashboard
1. Meetings booked vs. target
2. Activity metrics (emails sent, calls made, LinkedIn touches)
3. Response rates by channel and sequence
4. Lead-to-meeting conversion rate
5. Meeting-to-opportunity conversion rate (quality metric)
6. Pipeline value generated
