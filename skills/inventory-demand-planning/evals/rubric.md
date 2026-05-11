# Inventory Demand Planning — LLM Grading Rubric

## Purpose

This rubric guides an LLM grader in scoring agent responses to inventory demand planning evaluation scenarios. Each scenario contains 3–5 evaluation criteria with pass/fail rubric descriptions. The grader assigns a score to each criterion, and the weighted sum produces the scenario score.

---

## Grading Scale

| Rating | Score | Definition |
|---|---|---|
| **Pass** | 1.0 | Response demonstrates demand planning domain expertise. Calculations are correct or within acceptable rounding tolerances. The recommended actions are what an experienced demand planner managing hundreds of SKUs at a multi-location retailer would do. Forecasting methods are matched to demand patterns correctly. Safety stock formulas include the appropriate variables (review period, lead time variability). Financial thresholds, markdown timing, and vendor negotiation tactics reflect operational judgment — not textbook recitation but awareness of how retail planning actually works. |
| **Partial** | 0.5 | Response is directionally correct but incomplete or imprecise. The agent identifies the general type of planning problem and suggests reasonable approaches, but misses critical details: omits the review period from safety stock, uses MAPE instead of WMAPE on low-volume items, applies a flat lift estimate without adjusting for promotional mechanism, recommends a forecasting method without specifying parameters, or provides advice that works in theory but ignores real-world constraints (vendor MOQs, case pack rounding, shelf life, perishability). |
| **Fail** | 0.0 | Response is incorrect, dangerously incomplete, or generic. The agent misidentifies the demand pattern, applies the wrong forecasting method, gets safety stock calculations fundamentally wrong (e.g., omits lead time entirely), recommends actions that would create significant excess inventory or stockouts, or provides advice so generic it could apply to any supply chain context ("monitor demand and adjust accordingly"). A response that sounds reasonable to a layperson but would make a demand planner wince. |

### Grading Decision Guide

When choosing between adjacent ratings, use these tiebreakers:

**Pass vs. Partial:**
- Did the response get the calculation right (within ±10% of the expected value)? If yes and the logic is sound, lean Pass.
- Would a planning manager reading this response need to add significant corrections before acting on it? If yes, Partial.

**Partial vs. Fail:**
- Does the response demonstrate awareness that this is a demand planning context (not generic supply chain management)? If not, Fail.
- Would following the response's advice cause active harm (significant excess inventory, avoidable stockouts, wasted perishable product, vendor relationship damage)? If yes, Fail.
- Is the response merely incomplete but pointed in the right direction? Partial.

---

## Domain Expertise vs. Generic Response

The core distinction this rubric enforces is between responses grounded in retail demand planning expertise and responses that apply generic supply chain or business logic to an inventory-shaped problem.

### What Constitutes Domain Expertise

An expert-level response demonstrates knowledge that can only come from working in demand planning at a multi-location retailer. Specifically:

**1. Forecasting Method Selection and Application**
- Matches forecasting methods to demand patterns (Holt-Winters for seasonal, Croston's for intermittent, etc.)
- Knows that a simple moving average cannot track trending demand — it lags by half the window length
- Understands the difference between additive and multiplicative seasonality and when each applies
- Specifies model parameters (alpha, beta, gamma) within reasonable ranges and explains why
- Uses tracking signal as a model health metric with ±4 as the intervention threshold
- Knows that exponential smoothing with low alpha (0.10–0.15) adapts slowly and may need a level reset after a demand regime change

**2. Safety Stock and Inventory Math**
- Includes the review period in safety stock calculations for periodic review systems (not just lead time)
- Uses the combined demand + lead time variability formula when lead times are uncertain
- Knows that normal-distribution safety stock fails for intermittent demand (CV > 1.0, high zero-demand ratio)
- Computes inventory position as on-hand + on-order − backorders − committed (not just on-hand)
- Rounds order quantities to case pack multiples and vendor MOQs
- Understands the exponential cost of increasing service level from 95% to 99% (nearly doubles safety stock)

**3. Promotional Planning Knowledge**
- Separates baseline from promotional demand — never lets promotional volume contaminate the baseline model
- Knows that lift varies by promotional mechanism (TPR-only vs. TPR + display + circular) and that these are not additive
- Estimates post-promo dip and connects it to forward-buy behavior and product shelf life
- Models cannibalization effects across substitutable SKUs within a category
- Understands that BOGO creates heavy forward-buying on shelf-stable goods but minimal forward-buying on perishables

**4. ABC/XYZ Segmentation Judgment**
- Classifies on margin contribution (not revenue or units)
- Computes XYZ on de-seasonalized, de-promoted demand to avoid penalizing seasonal items
- Assigns differentiated policies per segment — not one-size-fits-all
- Flags CZ items as discontinuation candidates without waiting for explicit direction
- Knows that new items should be temporarily elevated one class until they have sufficient history

**5. Operational and Financial Awareness**
- Converts forecasts into purchase orders that respect vendor MOQs, case packs, and lead times
- Considers shelf life and spoilage risk when sizing orders for perishable products
- Computes the carrying cost of excess inventory and compares it to the cost of stockouts
- Manages seasonal buy decisions with an open-to-buy reserve (60–70% initial commit, 30–40% reserve)
- Knows that markdown timing matters more than markdown depth — every week of delay costs margin
- Understands the self-reinforcing nature of phantom inventory (wrong on-hand → no reorder trigger → stockout)

### Common Indicators of Generic Responses

These patterns indicate the response lacks demand-planning-specific expertise. Any single indicator is not disqualifying, but multiple indicators strongly suggest a Fail or low Partial:

**1. Wrong Abstraction Layer**
- Refers to the vendor as "the supplier" and uses procurement language rather than demand planning language
- Calls the forecast a "prediction" or "estimate" without referencing the specific method
- Describes safety stock as "buffer stock" or "extra inventory" without referencing the statistical calculation
- Suggests "analyzing the data" or "looking at historical trends" without specifying what to look at

**2. Missing Planning Mechanics**
- Omits the review period from safety stock (this is the single most common error)
- Uses on-hand inventory instead of inventory position for reorder decisions
- Does not round order quantities to case packs or vendor minimums
- Recommends a forecasting method without parameters or validation approach
- Does not separate baseline from promotional demand
- Applies a single safety stock formula to all demand patterns (normal distribution everywhere)

**3. Incorrect Calculations**
- Safety stock off by more than 30% from the expected value
- Reorder point that ignores lead time demand
- Lift estimate that doesn't match the promotional mechanism type
- Weeks-of-supply calculation that divides by trailing demand instead of forward forecast
- ABC classification based on revenue instead of margin

**4. One-Dimensional Analysis**
- Addresses the forecast without considering the inventory and ordering implications
- Focuses on accuracy metrics without connecting to service levels or financial impact
- Recommends a markdown without computing the margin recovery under different depth scenarios
- Proposes a promotion without modeling the post-promo dip and cannibalization

**5. Dangerous Advice**
- Recommends chasing viral demand with a large order at 8-week ocean lead time
- Accepts an S&OP override at face value on perishable product without probability weighting
- Orders for peak promotional demand on a perishable product, ignoring spoilage risk
- Applies normal-distribution safety stock to an intermittent demand item with CV > 1.5
- Does not flag phantom inventory when the system shows stock but sales are zero

---

## Scoring Individual Criteria

For each criterion within a scenario, the grader should:

1. **Read the scenario context and task** to understand what the agent was asked to do.
2. **Read the criterion's pass and fail rubric descriptions** — these are specific to the scenario, not generic.
3. **Evaluate the agent's response** against both the pass and fail descriptions.
4. **Assign a rating:**
   - **Pass (1.0):** The response matches the pass description substantively. Minor calculation rounding differences are acceptable (within ±10%). The grader is evaluating whether the agent demonstrated the same planning judgment, not whether it used identical formulas.
   - **Partial (0.5):** The response falls between the pass and fail descriptions. It captures some elements of the pass description but misses others, or gets the direction right but the numbers wrong.
   - **Fail (0.0):** The response matches the fail description, or is worse than the fail description, or does not address the criterion at all.

### Important Scoring Nuances

**Calculations Matter**
In demand planning, the numbers matter. A response that correctly identifies "use Holt-Winters" but gets the safety stock calculation wrong by 50% should receive Partial for the method criterion but Fail for the safety stock criterion. Domain expertise is demonstrated through correct quantitative analysis, not just correct concept identification.

**Formulas Must Match the Situation**
Using the right formula family but omitting a critical variable (e.g., leaving out the review period from safety stock, or not including lead time variability when the scenario provides variable lead times) is Partial at best. The formula selection signals knowledge; the correct application demonstrates expertise.

**Context Sensitivity Matters**
A response that applies the right formula to shelf-stable goods but also applies the same formula to a 21-day perishable yogurt without adjusting for spoilage risk should receive Partial. Expert-level planning always considers the physical characteristics of the product.

**Omission Is Failure**
If a criterion's pass description includes 4 elements and the response covers 2 well but ignores 2, this is Partial — not Pass. The pass description represents the complete expert response.

**Over-Reaction Is as Wrong as Under-Reaction**
A response that triggers a vendor performance review over a single late PO is as wrong as one that ignores a vendor trending from 96% to 84% OTD over three quarters. Correct calibration of response to severity is fundamental to planning expertise.

**Financial Judgment**
Demand planning is ultimately about capital allocation. Responses that demonstrate financial awareness — computing carrying costs, comparing markdown scenarios, quantifying the cost of a service level increase — receive credit even when other aspects are weaker. Responses that ignore the financial dimension of planning decisions are capped at Partial regardless of analytical quality.

---

## Grading Edge Cases

### When the Response Is Right for the Wrong Reasons

If the agent recommends the correct action but explains it using incorrect reasoning (e.g., recommends Holt-Winters but says it's because the demand is intermittent), assign **Partial**. Correct actions with wrong reasoning suggest the agent may not replicate the correct behavior in novel situations.

### When the Response Adds Correct Information Not in the Rubric

If the agent provides additional relevant and correct information beyond what the pass rubric describes, this does not change the scoring — it's still a Pass. Do not penalize for additional correct content, even if it wasn't asked for, unless it contradicts other parts of the response.

### When the Response Contradicts Itself

If the agent states conflicting recommendations (e.g., "order aggressively" in one paragraph and "order conservatively due to perishability risk" in another without resolving the tension), assign **Fail** for that criterion unless one recommendation is clearly framed as contingent on a condition.

### When Calculation Rounding Differs

Many of the scenarios involve calculations where reasonable rounding choices produce slightly different results. Accept any answer within ±10% of the expected value as correct. For example, if the expected safety stock is 205 units, any answer between 185 and 225 is acceptable for a Pass.

### When the Response Addresses a Different Aspect of the Problem

If the criterion asks about "safety stock calculation" and the agent's response focuses entirely on "forecasting method selection" (a different criterion), assign **Fail** for the safety stock criterion even if the forecasting content is excellent. Each criterion is graded independently.

---

## Terminology Weighting

Domain-specific terminology usage is a signal, not a score. The grader should use terminology as follows:

**Terminology that signals expertise (positive signal, supports higher scores):**
- Correct use of: WMAPE, bias, tracking signal, MAD, Holt-Winters, Croston's, SBA, exponential smoothing, alpha/beta/gamma, seasonal indices, multiplicative vs. additive seasonality, de-seasonalized, de-promoted, CV, ADI, inventory position, ROP, EOQ, order-up-to level, periodic review, continuous review, safety stock, service level, z-score, ABC/XYZ, GMROI, open-to-buy, weeks of supply, sell-through rate, lift ratio, cannibalization, forward-buy, post-promo dip, demand signal, phantom inventory, cycle count, vendor scorecard, MOQ, case pack
- Correct differentiation between: baseline vs. promotional demand, on-hand vs. inventory position, MAPE vs. WMAPE, additive vs. multiplicative seasonality, continuous vs. periodic review, demand variability vs. lead time variability

**Terminology that signals generic knowledge (neutral):**
- Standard business terms: forecast, inventory, supply chain, vendor, KPI, optimization
- General statistical terms: mean, standard deviation, variance, normal distribution

**Terminology that signals misunderstanding (negative signal):**
- Using "safety stock" and "buffer stock" interchangeably without the statistical calculation
- Calling the tracking signal a "KPI" rather than a model diagnostic
- Confusing MAPE with WMAPE when dealing with low-volume items
- Using "reorder point" in a periodic review system (should be "order-up-to level")

**Important:** Terminology alone does not determine the score. An agent that uses all the right words but recommends ordering 10,000 units of a C-item based on a viral spike should still fail. An agent that uses plain language but correctly identifies the demand pattern, computes safety stock, and sizes the order appropriately should still pass. Terminology is a supporting signal for borderline cases.

---

## Aggregate Interpretation

After scoring all criteria for all scenarios, the following aggregate benchmarks indicate capability levels:

| Aggregate Score | Interpretation |
|---|---|
| **≥ 85%** | Expert-level demand planning capability. The agent can handle the full range of forecasting, safety stock, promotional, and replenishment decisions with minimal human oversight. Suitable for production use in forecast generation, replenishment recommendations, and promotional planning support. |
| **70–84%** | Competent with supervision. The agent handles routine planning well but needs human review on complex promotional lift estimation, seasonal transitions, and multi-factor optimization. Suitable for first-draft forecasts and recommendations that a planner reviews. |
| **50–69%** | Inconsistent. The agent demonstrates some demand planning knowledge but has significant gaps in calculation accuracy or operational awareness. May produce harmful advice on hard scenarios (e.g., chasing viral demand, over-committing on perishables). Requires heavy human supervision. |
| **< 50%** | Insufficient domain expertise. The agent's responses are predominantly generic supply chain advice without demand-planning-specific calculations or judgment. Not suitable for any autonomous planning tasks. |

### Difficulty-Adjusted Expectations

The scenario set is designed with a difficulty distribution:
- **Easy (~38%):** An agent with basic demand planning training should pass these. These test fundamental calculations (safety stock, ROP, ABC classification) and straightforward method selection. Failure on easy scenarios is a strong negative signal.
- **Medium (~38%):** An agent needs genuine operational knowledge to pass these consistently. These involve promotional planning, vendor management, seasonal transitions, and multi-factor decisions. Partial scores are common and acceptable.
- **Hard (~25%):** These are designed to test deep expertise: viral spikes, regime changes, supply crises, S&OP conflicts, and multi-stakeholder optimization. Even competent agents may score Partial on some hard scenarios. Consistent Pass on hard scenarios indicates true expert-level capability.

A capable agent should score ≥90% on easy, ≥70% on medium, and ≥50% on hard scenarios. An agent scoring below 50% on easy scenarios has fundamental gaps that disqualify it from the domain.
