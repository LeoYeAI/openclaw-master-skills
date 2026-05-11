# Analytical Pitfalls — Detailed Examples

## Simpson's Paradox

**What it is:** A trend that appears in aggregated data reverses when you segment by a key variable.

**Example:** 
- Overall: Treatment A has 80% success, Treatment B has 85% → "B is better"
- But segmented by severity:
  - Mild cases: A=90%, B=85% → A is better
  - Severe cases: A=70%, B=65% → A is better
- Paradox: A is better in BOTH groups, but B looks better overall because B got more mild cases

**How to catch:** Always segment by obvious confounders (user type, time period, source, severity) before concluding.

---

## Survivorship Bias

**What it is:** Drawing conclusions only from "survivors" while ignoring those who dropped out.

**Example:**
- "Users who completed onboarding have 80% retention!" 
- Problem: You're only looking at users who already demonstrated commitment by completing onboarding
- The 60% who abandoned onboarding aren't in your "user" dataset

**How to catch:** Ask "Who is NOT in this dataset that should be?" Include churned users, failed attempts, non-converters.

---

## Comparing Unequal Periods

**What it is:** Comparing metrics across time periods of different lengths or characteristics.

**Examples:**
- February (28 days) vs January (31 days) revenue
- Holiday week vs normal week traffic
- Q4 (holiday season) vs Q1 for e-commerce

**How to catch:** 
- Normalize to per-day, per-user, or per-session
- Compare same period last year (YoY) not sequential months
- Flag seasonal factors explicitly

---

## p-Hacking (Multiple Comparisons)

**What it is:** Running many statistical tests until finding a "significant" result, then reporting only that one.

**Example:**
- Test 20 different user segments for conversion difference
- At p=0.05, expect 1 "significant" result by chance alone
- Report: "Segment X shows significant improvement!" (cherry-picked)

**How to catch:**
- Apply Bonferroni correction (divide α by number of tests)
- Pre-register hypotheses before looking at data
- Report ALL tests run, not just significant ones

---

## Spurious Correlation in Time Series

**What it is:** Two variables both trending over time appear correlated, but the relationship is meaningless.

**Example:**
- "Revenue and employee count are 95% correlated!"
- Both grew over time. Controlling for time, there's no relationship.
- Classic: "Ice cream sales correlate with drowning deaths" (both rise in summer)

**How to catch:**
- Detrend both series before correlating
- Check if relationship holds within time periods
- Ask: "Is there a causal mechanism, or just shared time trend?"

---

## Aggregating Percentages

**What it is:** Averaging percentages instead of recalculating from underlying totals.

**Example:**
- Store A: 10/100 = 10% conversion
- Store B: 5/10 = 50% conversion
- Wrong: "Average conversion is 30%"
- Right: 15/110 = 13.6% conversion

**How to catch:** Never average percentages. Sum numerators, sum denominators, recalculate.

---

## Selection Bias in A/B Tests

**What it is:** Treatment and control groups differ systematically before treatment is applied.

**Examples:**
- Users who opted into new feature vs those who didn't
- Early adopters (Monday signups) vs late week (Friday signups)
- Users who saw the experiment (loaded fast enough) vs those who didn't

**How to catch:**
- Verify pre-experiment metrics are balanced
- Use intention-to-treat analysis
- Check for differential attrition

---

## Confusing Causation

**What it is:** Assuming X causes Y when the relationship might be: Y causes X, Z causes both, or it's coincidental.

**Example:**
- "Power users have higher retention" 
- Did power usage cause retention? Or did retained users become power users over time? Or does a third factor (job role) drive both?

**How to catch:**
- Can you run an experiment? (randomize treatment)
- Is there a natural experiment? (policy change, feature rollout)
- At minimum: control for obvious confounders
