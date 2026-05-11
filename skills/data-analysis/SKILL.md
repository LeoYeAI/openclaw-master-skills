---
name: Data Analysis
description: Turn raw data into decisions with statistical rigor, proper methodology, and awareness of analytical pitfalls.
---

## When to Load

User asks about: analyzing data, finding patterns, understanding metrics, testing hypotheses, cohort analysis, A/B testing, churn analysis, statistical significance.

## Core Principle

Analysis without a decision is just arithmetic. Always clarify: **What would change if this analysis shows X vs Y?**

## Methodology First

Before touching data:
1. **What decision** is this analysis supporting?
2. **What would change your mind?** (the real question)
3. **What data do you actually have** vs what you wish you had?
4. **What timeframe** is relevant?

## Statistical Rigor Checklist

- [ ] Sample size sufficient? (small N = wide confidence intervals)
- [ ] Comparison groups fair? (same time period, similar conditions)
- [ ] Multiple comparisons? (20 tests = 1 "significant" by chance)
- [ ] Effect size meaningful? (statistically significant ≠ practically important)
- [ ] Uncertainty quantified? ("12-18% lift" not just "15% lift")

## Analytical Pitfalls to Catch

| Pitfall | What it looks like | How to avoid |
|---------|-------------------|--------------|
| Simpson's Paradox | Trend reverses when you segment | Always check by key dimensions |
| Survivorship bias | Only analyzing current users | Include churned/failed in dataset |
| Comparing unequal periods | Feb (28d) vs March (31d) | Normalize to per-day or same-length windows |
| p-hacking | Testing until something is "significant" | Pre-register hypotheses or adjust for multiple comparisons |
| Correlation in time series | Both went up = "related" | Check if controlling for time removes relationship |
| Aggregating percentages | Averaging percentages directly | Re-calculate from underlying totals |

For detailed examples of each pitfall, see `pitfalls.md`.

## Approach Selection

| Question type | Approach | Key output |
|---------------|----------|------------|
| "Is X different from Y?" | Hypothesis test | p-value + effect size + CI |
| "What predicts Z?" | Regression/correlation | Coefficients + R² + residual check |
| "How do users behave over time?" | Cohort analysis | Retention curves by cohort |
| "Are these groups different?" | Segmentation | Profiles + statistical comparison |
| "What's unusual?" | Anomaly detection | Flagged points + context |

For technique details and when to use each, see `techniques.md`.

## Output Standards

1. **Lead with the insight**, not the methodology
2. **Quantify uncertainty** — ranges, not point estimates
3. **State limitations** — what this analysis can't tell you
4. **Recommend next steps** — what would strengthen the conclusion

## Red Flags to Escalate

- User wants to "prove" a predetermined conclusion
- Sample size too small for reliable inference
- Data quality issues that invalidate analysis
- Confounders that can't be controlled for
