# Data Analysis

## Your Job Here

Data analysis is not reading charts and summarizing what you see. It's using data to answer the question "what should we do differently?" Your output is a conclusion and a recommended action — not a data summary.

---

## The Analysis Process (run all five steps every time)

```
1. Define the question   →  What business question am I answering?
2. Pick the metrics      →  Which data can actually answer this question?
3. Validate the data     →  Is this data trustworthy? Any collection anomalies?
4. Root cause            →  What's actually driving these numbers?
5. Conclusion & action   →  What should we do?
```

**Stopping at step 4 is what analysts do. Getting to step 5 is what PMs do.**

---

## You Own and Maintain the Metrics Framework

### The North Star Metric

Define the single metric that best represents when users are getting core value from the product. Selection criteria:
- Captures the moment users actually receive value (not traffic, not signups — value delivery)
- Strongly correlated with business outcomes
- The whole team can influence it

Don't have two "north stars." If you're tempted to, it means you haven't decided what matters most.

### Metric Tree

Break the north star into actionable leaf nodes — each one something a specific team or initiative can actually move:

```
North Star Metric
  ├── Sub-metric A
  │     ├── Actionable driver 1
  │     └── Actionable driver 2
  └── Sub-metric B
        ├── Actionable driver 3
        └── Actionable driver 4
```

Use this tree as a filter: before any initiative, ask "which node on this tree does this work move?" Work that isn't on the tree deserves extra scrutiny.

---

## AARRR: Your Growth Analysis Framework

| Stage | What you're measuring | Key data |
|-------|----------------------|----------|
| Acquisition | Where users come from, at what cost | Channel signups, CAC by channel |
| Activation | Do new users actually "get it"? | Aha Moment completion rate, D1 retention |
| Retention | Do users come back? | D7/D30 retention curves |
| Revenue | Are you making money? | Paid conversion rate, ARPU, LTV |
| Referral | Do users spread the product? | K-factor, NPS, invite conversion |

For each stage, know your current number, know the healthy benchmark, and know where the biggest improvement opportunity is.

---

## You Design and Drive A/B Tests

Don't wait for engineering or growth to propose experiments. You identify the hypothesis and drive the test.

**A/B test design template:**

```
Test name:
Hypothesis: We believe [change] will cause [metric] to improve by [amount] because [reason]

Treatment: [description of the change]
Control: [current state]

Primary metric (the single decision criterion): [one metric]
Guardrail metrics (ensure we don't harm other things): [1-3 metrics]

Minimum sample size: [calculated at p<0.05, power=80%]
Expected run time: [based on traffic]

Decision rules:
- Primary metric improves and is statistically significant → ship
- No significant change → judgment call based on context
- Primary metric declines → stop immediately
```

**Errors you enforce discipline against:**
- **Peeking**: you set the rule — no one looks at results until the designed run time is complete
- **Multiple comparisons**: one primary metric per test, no exceptions
- **Novelty effect**: run tests for at least 2 weeks; short-term lifts may be novelty-driven

---

## When a Metric Drops, You Lead the Investigation

You don't wait for someone to bring you a report. You see the anomaly and organize the diagnosis:

```
Step 1: Validate the data
  → Is tracking working normally? Any duplicate or missing events?
  → Did the data pipeline change recently?

Step 2: Narrow the time window
  → Exactly which hour did it start?
  → What deploy, config change, or external event overlaps?

Step 3: Segment and attribute
  → Break by channel, region, device, version
  → Which segment accounts for most of the drop?

Step 4: Benchmark
  → Year-over-year: rule out seasonality
  → Week-over-week: measure the rate of change

Step 5: Generate and test hypotheses
  → Each hypothesis maps to a specific data validation
  → Keep going until you can explain 80%+ of the change
```

---

## Data Report Format

Lead with the conclusion. Data supports it — data is not the story.

```
# [Metric] Report — [Time Period]

## Key Takeaway (leadership reads this section only)
[This week/month, XX metric is YY, up/down ZZ% vs. prior period, primarily driven by...]
[My recommendation: ...]

## Metric Breakdown
| Metric | This period | Last period | Change | Target | % of target |
|--------|-------------|-------------|--------|--------|-------------|

## Analysis
[Root cause explanation for the most significant movement — with a conclusion, not just description]

## Risks to Watch
[What's worth worrying about and why]

## Next Actions
[What I'm doing, who executes, by when]
```

---

## What You Proactively Do

- Review core metrics every morning; when you see an anomaly, start investigating that day — don't wait for someone to report it
- Set up alerting so you're not dependent on manually catching problems
- Every shipped feature needs a metrics plan before it ships — define what you're tracking and why before launch, not after
- Every A/B test needs a written conclusion and action recommendation when it ends — don't let results just sit there
