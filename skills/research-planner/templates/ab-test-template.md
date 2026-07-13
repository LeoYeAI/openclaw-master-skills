# A/B Test Template

Template for planning and documenting online controlled experiments (A/B tests) to evaluate changes in products or experiences.

## How to Use

- Use for **causal evaluation** of product changes where random assignment is feasible.
- Keep design simple; focus on one primary question per test.

## A/B Test Template

```markdown
# A/B Test – [Experiment Name]

Version: v[...]
Date: [...]
Owner: [...]

## 1. Objective and Hypothesis

- Business objective:
  - [...]
- Primary hypothesis (in testable form):
  - "If we [change X], then [metric Y] will [increase/decrease] for [population Z]."

## 2. Experimental Design

- Control:
  - Description of existing experience (Variant A).
- Treatment(s):
  - Description of change(s) in Variant B (and C, if multivariate).
- Unit of randomization:
  - [user / session / account / organization / etc.]
- Target population:
  - Eligibility criteria for inclusion in the experiment.

## 3. Metrics

- Primary metric(s):
  - [...]
- Guardrail / secondary metrics:
  - [e.g., overall revenue, error rate, performance metrics]
- Directionality and expectations:
  - [e.g., “Primary metric should increase; guardrails should not worsen beyond threshold X.”]

## 4. Sample Size and Duration

- Minimum sample size:
  - [...]
- Estimated test duration:
  - [...]
- Assumptions for power/precision (if known):
  - Baseline metric value:
  - Minimum detectable effect:

## 5. Implementation Notes

- Feature flags / experiment platform:
  - [...]
- Exclusions or special handling:
  - [e.g., internal traffic, bots, users under certain constraints]
- Rollout plan (if any):
  - [e.g., “start at 10% traffic, ramp to 50% after technical validation”]
```

## Key References for A/B Testing

- Ron Kohavi, Diane Tang, and Ya Xu, *Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing* – authoritative text on experimentation at scale.
- “Experimentation Platform” and related resources from Kohavi and colleagues (`https://experimentguide.com/` and academic papers such as “Controlled Experiments on the Web: Survey and Practical Guide”).


