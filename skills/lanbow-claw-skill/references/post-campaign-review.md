---
name: post-campaign-review
description: |
  Post-campaign performance review and optimization diagnosis for Meta Ads.
  Analyzes campaign delivery data to identify performance issues, diagnose root causes,
  and generate actionable optimization recommendations for the next iteration cycle.
  Use when:
  (1) Reviewing campaign performance after delivery
  (2) Diagnosing why a campaign underperformed (high CPC, low CTR, audience fatigue, etc.)
  (3) Planning optimization actions for the next round of ads
  (4) Comparing performance across ad sets, creatives, or time periods
  (5) Deciding budget reallocation, targeting adjustments, or creative refreshes
  Triggers: "review campaign", "post-campaign", "campaign diagnosis", "optimize ads",
  "ad performance review", "投后分析", "投后诊断", "复盘", "优化建议"
---

# Post-Campaign Review & Optimization Diagnosis

Analyze Meta Ads campaign delivery data, diagnose performance issues, and generate structured optimization recommendations for the next iteration cycle.

## Prerequisites

- lanbow-ads CLI installed and authenticated (`lanbow-ads auth status`)
- At least one campaign with delivery data available
- Access to `lanbow-ads insights get` command for data retrieval

## Core Workflow

```
Step 1: Data Collection
    | Fetch performance data via lanbow-ads CLI
Step 2: Metric Health Check
    | Evaluate key metrics against benchmarks
Step 3: Root Cause Diagnosis
    | Identify patterns and diagnose issues
Step 4: Optimization Plan
    | Generate actionable next-round recommendations
Step 5: Output Report
    | Structured diagnosis with prioritized actions
```

## Step 1: Data Collection

Gather performance data using `lanbow-ads insights get`. Collect multiple perspectives:

```bash
# Overall campaign performance (last 7 days)
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_7d --json

# Daily breakdown for trend analysis
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_7d --time-increment 1 --json

# Ad set level comparison
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_7d --level adset --json

# Ad level comparison
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_7d --level ad --json

# Audience breakdowns
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_7d --breakdowns age gender --json
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_7d --breakdowns country --json
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_7d --breakdowns publisher_platform --json

# Device breakdown
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_7d --breakdowns device_platform --json
```

**Extended date ranges for trend comparison:**

```bash
# Compare current vs previous period
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_14d --time-increment 7 --json
lanbow-ads insights get --campaign CAMPAIGN_ID --date-preset last_30d --time-increment 7 --json
```

**Always request JSON output** (`--json`) for structured analysis.

### Data Points to Collect

| Category | Metrics | Source |
|----------|---------|--------|
| **Delivery** | impressions, reach, frequency | campaign-level |
| **Engagement** | clicks, CTR, CPC | campaign + ad level |
| **Cost** | spend, CPM, CPC, cost_per_action | campaign + ad set level |
| **Conversion** | actions, conversions, ROAS, cost_per_conversion | campaign-level |
| **Quality** | quality_ranking, engagement_rate_ranking, conversion_rate_ranking | ad-level |
| **Audience** | age/gender/geo/device performance splits | breakdown queries |

## Step 2: Metric Health Check

Evaluate each metric against industry benchmarks and internal thresholds.

### Benchmark Reference Table

| Metric | Healthy Range | Warning | Critical |
|--------|--------------|---------|----------|
| **CTR (Link)** | > 1.0% | 0.5% - 1.0% | < 0.5% |
| **CPC (Link)** | < $1.50 | $1.50 - $3.00 | > $3.00 |
| **CPM** | < $15 | $15 - $30 | > $30 |
| **Frequency** | 1.0 - 3.0 | 3.0 - 5.0 | > 5.0 |
| **CTR (All)** | > 2.0% | 1.0% - 2.0% | < 1.0% |
| **Conversion Rate** | > 2.0% | 1.0% - 2.0% | < 1.0% |
| **ROAS** | > 3.0x | 1.5x - 3.0x | < 1.5x |
| **Cost per Lead** | Varies by vertical | — | — |

> **Note:** Benchmarks vary significantly by industry, region, and objective. Adjust thresholds based on the advertiser's vertical and historical performance. Always prefer internal historical benchmarks when available.

### Health Check Matrix

For each metric, assign a status:

```
🟢 Healthy  — performing within or above benchmark
🟡 Warning  — approaching threshold, monitor closely
🔴 Critical — underperforming, requires immediate action
```

## Step 3: Root Cause Diagnosis

Analyze patterns across dimensions to identify root causes.

### Diagnostic Framework

#### 3.1 Creative Fatigue Signals
- **Frequency > 3.0** with declining CTR over time → audience seeing ads too often
- **CTR dropping day-over-day** while impressions remain stable → creative losing effectiveness
- **One ad significantly outperforming others** → winner/loser gap widening

#### 3.2 Audience Saturation Signals
- **Reach plateau** — daily reach growth flattening
- **CPM increasing** while CTR decreasing → audience pool exhausted
- **Frequency climbing** without proportional reach growth

#### 3.3 Targeting Mismatch Signals
- **High impressions + low CTR** → reaching wrong audience
- **Age/gender breakdown showing extreme variance** → some segments irrelevant
- **Geographic performance gaps** → some regions underperforming

#### 3.4 Budget & Bidding Issues
- **Limited spending** — not using allocated budget → audience too narrow or bid too low
- **Cost spikes at scale** → diminishing returns at current budget level
- **Inconsistent daily spend** → learning phase instability

#### 3.5 Landing Page / Conversion Issues
- **High CTR + low conversion rate** → post-click experience problem
- **High bounce rate signals** (inferred from high CPC but low conversions)
- **Mobile vs desktop conversion gap** → mobile experience issues

### Diagnosis Output Format

For each identified issue:

```markdown
### Issue: [Issue Name]

- **Severity:** 🔴 Critical / 🟡 Warning
- **Evidence:** [Specific data points supporting the diagnosis]
- **Root Cause:** [Why this is happening]
- **Impact:** [How this affects campaign performance]
- **Recommended Action:** [What to do about it]
```

## Step 4: Optimization Plan

Generate prioritized optimization recommendations organized by effort and impact.

### Optimization Categories

#### A. Immediate Fixes (0-48 hours)
Quick wins that can be implemented right away:

- **Pause underperforming ads** — ads with CTR < 50% of ad set average
- **Budget reallocation** — shift budget from low-ROAS to high-ROAS ad sets
- **Frequency cap adjustment** — if frequency > 5, reduce or refresh creatives
- **Bid adjustment** — if underspending, increase bid; if overspending, add bid cap

#### B. Creative Optimization (3-7 days)
Creative refreshes and iterations:

- **New creative angles** — based on top-performing ad analysis
- **Copy variations** — test new headlines, primary text, CTAs
- **Format changes** — try video if only using static, or vice versa
- **Audience-specific creatives** — tailor messaging per high-performing segment

#### C. Targeting Refinement (1-2 weeks)
Audience and targeting adjustments:

- **Narrow targeting** — exclude underperforming segments (age, gender, geo)
- **Expand lookalikes** — if current audience is saturated
- **Interest layering** — add or remove interest targets based on performance
- **Exclusion lists** — exclude converted users, low-quality segments

#### D. Strategic Changes (2-4 weeks)
Structural campaign modifications:

- **Campaign restructure** — consolidate or split ad sets
- **Objective change** — if current objective not aligned with actual goal
- **Funnel stage shift** — move budget between awareness/consideration/conversion
- **Testing framework** — set up structured A/B tests for next cycle

### Priority Matrix

| Action | Impact | Effort | Priority |
|--------|--------|--------|----------|
| Pause low performers | High | Low | P0 — Do Now |
| Budget reallocation | High | Low | P0 — Do Now |
| Creative refresh | High | Medium | P1 — This Week |
| Targeting refinement | Medium | Medium | P2 — Next Week |
| Campaign restructure | High | High | P3 — Plan & Execute |

## Step 5: Output Report

### Report Structure

```markdown
# Post-Campaign Review: [Campaign Name]

## 1. Performance Summary
- Period: [date range]
- Total Spend: $X
- Key Results: [impressions, clicks, conversions]

## 2. Metric Health Check
[Health check matrix with status indicators]

## 3. Performance by Dimension
### By Ad Set
[Table comparing ad set performance]
### By Ad / Creative
[Table comparing ad-level performance]
### By Audience Segment
[Age, gender, geo, device breakdowns]
### By Time (Trend)
[Daily/weekly trend analysis]

## 4. Diagnosis
[Root cause analysis for each identified issue]

## 5. Optimization Recommendations
### P0 — Immediate Actions (0-48h)
[Prioritized list with specific instructions]
### P1 — Creative Optimization (3-7 days)
[Creative refresh recommendations]
### P2 — Targeting & Audience (1-2 weeks)
[Targeting adjustment recommendations]
### P3 — Strategic Changes (2-4 weeks)
[Structural recommendations]

## 6. Next Cycle KPI Targets
[Proposed targets for next iteration based on current data]

## 7. Appendix
- Raw data tables
- Benchmark sources
- Methodology notes
```

## Key Principles

1. **Data-first diagnosis** — every recommendation must be backed by specific data points from the insights output
2. **Actionable specificity** — don't say "improve targeting," say "exclude age 18-24 in US which has 0.3% CTR vs 1.8% average"
3. **Prioritized actions** — always rank by impact × effort; surface quick wins first
4. **Iteration mindset** — frame recommendations as hypotheses to test, not absolute truths
5. **Historical context** — when available, compare current performance to previous periods to identify trends

## Example Diagnosis Flow

```
Input: lanbow-ads insights get --campaign 123456 --date-preset last_7d --json

Data shows:
  - CTR: 0.4% (Critical)
  - CPM: $22 (Warning)
  - Frequency: 4.2 (Warning)
  - Spend: $350 of $500 budget (underspending)

Diagnosis:
  1. Creative fatigue (frequency 4.2 + declining CTR)
  2. Audience may be too narrow (underspending budget)

Recommendations:
  P0: Pause bottom 2 ads, keep top performer running
  P1: Generate 3 new creative angles using creative_gen skill
  P2: Expand targeting to lookalike 3% (currently 1%)
  P3: Test ABO structure with segment-specific creatives
```

## Integration with Other Skills

This skill is designed to work in a cycle with the other lanbow-ads ads skills:

- **ads-strategy-researcher** → provides the initial strategy that this skill validates against results
- **creative_gen** → generates new creatives based on this skill's creative refresh recommendations
- **lanbow-ads** → executes the optimization actions (pause ads, adjust budgets, update targeting)

The post-campaign review closes the feedback loop:

```
Strategy → Creative → Launch → Review → Optimize → (repeat)
```
