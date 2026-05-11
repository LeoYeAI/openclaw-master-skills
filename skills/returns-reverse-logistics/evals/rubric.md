# Returns & Reverse Logistics — LLM Grading Rubric

## Purpose

This rubric guides an LLM grader in scoring agent responses to returns and reverse logistics evaluation scenarios. Each scenario contains 3–5 evaluation criteria with pass/fail rubric descriptions. The grader assigns a score to each criterion, and the weighted sum produces the scenario score.

---

## Grading Scale

| Rating | Score | Definition |
|---|---|---|
| **Pass** | 1.0 | Response demonstrates domain expertise. The recommended actions are what an experienced returns operations manager would do. Correct policy frameworks, disposition economics, fraud indicators, and vendor recovery procedures are applied accurately. The response reflects operational judgment — not just textbook knowledge but awareness of how returns actually flow through receiving, grading, disposition, and financial reconciliation. |
| **Partial** | 0.5 | Response is directionally correct but incomplete or imprecise. The agent identifies the general category of situation and suggests reasonable actions, but misses critical operational details, applies grading criteria incorrectly, omits a key stakeholder, or provides advice that would work in theory but cause problems in practice (e.g., restocking an opened health/beauty product, applying a restocking fee to a defective return, or flagging a high-LTV bracket shopper as fraud). |
| **Fail** | 0.0 | Response is incorrect, dangerously incomplete, or generic. The agent either misidentifies the return type, applies the wrong disposition logic, recommends actions that would harm margin recovery or customer relationships, or provides advice so generic it could apply to any industry ("process the return and issue a refund"). A response that sounds plausible to a layperson but would make a returns operations manager wince. |

### Grading Decision Guide

When choosing between adjacent ratings, use these tiebreakers:

**Pass vs. Partial:**
- Did the response identify the *single most critical action* for this scenario? If yes and the rest is reasonable, lean Pass.
- Would a returns operations manager reading this response need to add significant corrections before acting on it? If yes, Partial.

**Partial vs. Fail:**
- Does the response demonstrate awareness that this is a returns/reverse-logistics context (not generic customer service)? If not, Fail.
- Would following the response's advice cause active harm (financial loss, regulatory violation, relationship damage, fraud exposure)? If yes, Fail.
- Is the response merely incomplete but pointed in the right direction? Partial.

---

## Domain Expertise vs. Generic Response

The core distinction this rubric enforces is between responses grounded in returns operations expertise and responses that apply generic customer service logic to a returns-shaped problem.

### What Constitutes Domain Expertise

An expert-level response demonstrates knowledge that can only come from working in returns operations. Specifically:

**1. Grading and Disposition Knowledge**
- Knows the Grade A/B/C/D framework and what drives the grading decision for different product categories
- Understands that disposition routing is an economics decision: restock > open box > refurbish > liquidate > donate > destroy, and the thresholds that drive routing between tiers
- Recognises that restocking an item as "new" when it has been materially used (even if it looks clean) creates downstream customer quality issues
- Knows that opened health/beauty/cosmetics cannot be restocked regardless of apparent condition
- Understands that liquidation recovery varies by channel and that manifested, category-sorted pallets recover 20-40% more than mixed pallets

**2. Fraud Detection Competence**
- Distinguishes between wardrobing (wear and return), swap fraud (return a different item), receipt fraud, bracketing, and serial returning — each has different indicators and different responses
- Knows that serial number verification is the single most reliable swap-fraud indicator for electronics
- Understands that a high return rate alone is not fraud — it must be contextualised with net LTV, return condition, and behaviour consistency
- Knows the fraud scoring threshold model: flag at 65, hold at 80, and specific point values for specific signals
- Recognises that false positives on fraud detection destroy customer relationships and must be managed as aggressively as fraud itself

**3. Policy and Legal Framework Application**
- Correctly distinguishes between a return (customer's right to reverse purchase within policy window) and a warranty claim (manufacturer's obligation to address defects within warranty period)
- Knows that the Magnuson-Moss Warranty Act prevents manufacturers from voiding warranties based on third-party parts unless the part caused the defect
- Understands FTC enforcement around "sold as new" when restocking used products
- Knows that recalled products follow the recall programme, not the returns programme
- Applies duty drawback rules correctly for cross-border returns

**4. Financial and Disposition Economics**
- Calculates refurbishment ROI (refurb cost vs. refurbished selling price vs. alternative disposition value)
- Understands vendor recovery economics: when to pursue RTV, when to batch, when to write off
- Knows the internal cost of returns processing (~$7-8 per return) and factors it into eat-the-cost decisions
- Correctly applies restocking fee logic: when fees apply, when they're waived (defective, fulfilment error), and when waiving for goodwill is the right economic decision
- Understands that return shipping costs for bulky items often exceed product value, making "returnless refund" the better option

**5. Communication and Relationship Judgment**
- Never uses the word "fraud" or "investigation" in customer-facing communications
- Calibrates tone to situation: warm for standard returns, empathetic for denials, neutral for holds, transparent for restocking fees
- Always provides alternatives when denying a return (warranty claim, exchange, store credit, escalation to supervisor)
- In vendor communications, leads with data (defect rates, return volumes, photos) not complaints
- Does not blame the customer, even when the customer is clearly at fault (e.g., wardrobing) — addresses the behaviour through policy, not confrontation

### Common Indicators of Generic Responses

These patterns indicate the response lacks domain-specific expertise. Any single indicator is not disqualifying, but multiple indicators strongly suggest a Fail or low Partial:

**1. Wrong Abstraction Layer**
- Refers to returns processing as "handling the complaint"
- Calls the grading assessment a "quality check" without referencing the A/B/C/D framework or category-specific criteria
- Describes fraud detection as "checking if it looks suspicious" without referencing specific signals or scoring
- Suggests "contacting the manufacturer" for a return policy question (confusing returns with warranty)
- Treats disposition as a binary "restock or refund" without considering the full disposition hierarchy

**2. Missing Operational Mechanics**
- Does not verify serial numbers on electronics returns (the single most important swap-fraud check)
- Suggests restocking an opened cosmetics or health product
- Does not distinguish between return window policy and warranty coverage period
- Recommends issuing a refund before physical inspection is complete
- Does not segregate recalled products from the standard returns stream
- Applies restocking fees to defective products

**3. One-Dimensional Analysis**
- Addresses only the refund without considering disposition of the returned product
- Focuses on customer satisfaction without considering fraud risk, margin impact, or precedent
- Suggests a single course of action without contingency planning
- Does not consider the customer's history (LTV, return rate, prior flags) when making exception decisions
- Treats all returns identically regardless of product category, value, or customer profile

**4. Incorrect Financial Logic**
- Over-invests in recovering low-value claims (pursuing a $50 vendor claim that costs $75 to process)
- Under-invests in high-value recovery (not pursuing a $5,000 vendor defect claim because "it's not worth the hassle")
- Does not calculate returnless refund threshold (when return shipping cost exceeds product recovery value)
- Applies blanket restocking fees without category or condition differentiation
- Treats all liquidation channels as equivalent without considering recovery rate differences

**5. Tone-Deaf Communication**
- Uses the word "fraud" or "suspicious" in customer communications
- Provides no alternative when denying a return
- Sends a form letter for a high-value or complex situation
- Does not calibrate urgency to the financial or regulatory exposure
- Blames the customer for a process failure (e.g., hazmat return packaging)

---

## Scoring Individual Criteria

For each criterion within a scenario, the grader should:

1. **Read the scenario context and task** to understand what the agent was asked to do.
2. **Read the criterion's pass and fail rubric descriptions** — these are specific to the scenario, not generic.
3. **Evaluate the agent's response** against both the pass and fail descriptions.
4. **Assign a rating:**
   - **Pass (1.0):** The response matches the pass description substantively. Minor wording differences are fine — the grader is evaluating whether the agent demonstrated the same operational judgment, not whether it used identical phrasing.
   - **Partial (0.5):** The response falls between the pass and fail descriptions. It captures some elements of the pass description but misses others, or gets the direction right but the details wrong.
   - **Fail (0.0):** The response matches the fail description, or is worse than the fail description, or does not address the criterion at all.

### Important Scoring Nuances

**Specificity Matters**
A response that says "inspect the return and decide what to do with it" is not the same as a response that says "grade the return as B based on the missing original packaging and minor cosmetic wear, route to open-box resale channel at 70% of retail, and repackage with new inner packaging." The first is generic; the second demonstrates disposition knowledge. Grade accordingly.

**Sequence Matters**
In returns operations, the order of actions often matters as much as the actions themselves. A response that recommends issuing a refund before completing inspection (giving up leverage on condition disputes), or processing a recalled product through the standard returns stream, should receive Partial rather than Pass.

**Omission Is Failure**
If a criterion's pass description includes 4 elements and the response covers 2 well but ignores 2, this is Partial — not Pass. The pass description represents the complete expert response.

**Over-Escalation Is as Wrong as Under-Escalation**
A response that triggers a fraud investigation and LP notification for a $35 apparel return with tags still on is as incorrect as one that processes a $750 electronics return with a mismatched serial number without review. Correct calibration of response to risk is fundamental to domain expertise.

**Practicality Test**
Would an experienced returns operations manager read this response and say "yes, that's exactly what I'd do"? If yes, Pass. Would they say "that's roughly right but they're missing X"? Partial. Would they say "no, that would cause problems"? Fail.

---

## Grading Edge Cases

### When the Response Is Right for the Wrong Reasons

If the agent recommends the correct action but explains it using incorrect reasoning (e.g., recommends accepting a return outside the window but cites the wrong justification), assign **Partial**. Correct actions with wrong reasoning suggest the agent may not replicate the correct behaviour in novel situations.

### When the Response Adds Correct Information Not in the Rubric

If the agent provides additional relevant and correct information beyond what the pass rubric describes, this does not change the scoring — it's still a Pass. Do not penalise for additional correct content, even if it wasn't asked for, unless it contradicts other parts of the response.

### When the Response Contradicts Itself

If the agent states conflicting recommendations (e.g., "accept the return" in one paragraph and "deny per policy" in another), assign **Fail** for that criterion unless one recommendation is clearly framed as contingent on a condition.

### When the Scenario Has Evolved Since the Rubric Was Written

The rubric pass/fail descriptions reflect the expected best practice at the time of writing. If the agent references a legitimate recent change in regulations, industry practices, or technology that alters the expected response, the grader should give the benefit of the doubt and assign **Partial** at minimum, then flag the scenario for rubric review.

### When the Response Addresses a Different Aspect of the Problem

If the criterion asks about "disposition routing" and the agent's response focuses entirely on "customer communication" (a different criterion), assign **Fail** for the disposition criterion even if the customer communication content is excellent. Each criterion is graded independently.

---

## Terminology Weighting

Domain-specific terminology usage is a signal, not a score. The grader should use terminology as follows:

**Terminology that signals expertise (positive signal, supports higher scores):**
- Correct use of: RMA, Grade A/B/C/D, disposition, restock, open box, returnless refund, restocking fee, RTV, defect rate, wardrobing, swap fraud, bracketing, serial returner, BORIS (buy online return in store), duty drawback, Magnuson-Moss, CPSC recall, liquidation manifest, net recovery rate, cost per return
- Correct differentiation between: return vs warranty claim, restock vs open box vs refurbish vs liquidate, customer-fault vs defective vs fulfilment-error returns, manufacturer warranty vs extended warranty vs return policy

**Terminology that signals generic knowledge (neutral — neither helps nor hurts):**
- Standard business terms used correctly: escalation, customer satisfaction, policy exception, refund, credit
- General retail terms: customer service, quality check, return label, tracking number

**Terminology that signals misunderstanding (negative signal, supports lower scores):**
- Misuse of industry terms (e.g., calling RTV a "vendor return," confusing a return with a warranty claim)
- Using generic terms where specific terms exist (e.g., "check it out" instead of "grade and disposition")
- Applying the wrong framework (e.g., freight claims language for a product return)

**Important:** Terminology alone does not determine the score. An agent that uses all the right words but recommends the wrong actions should still fail. An agent that uses plain language but recommends the correct actions with proper operational judgment should still pass. Terminology is a supporting signal for borderline cases.

---

## Aggregate Interpretation

After scoring all criteria for all scenarios, the following aggregate benchmarks indicate capability levels:

| Aggregate Score | Interpretation |
|---|---|
| **≥ 85%** | Expert-level returns and reverse logistics capability. The agent can handle the full range of return scenarios with minimal human oversight. Suitable for production use in return authorisation, disposition routing, and fraud triage. |
| **70–84%** | Competent with supervision. The agent handles routine returns well but needs human review on complex fraud cases, policy exceptions, and vendor disputes. Suitable for first-draft responses that a human analyst reviews. |
| **50–69%** | Inconsistent. The agent demonstrates some domain knowledge but has significant gaps. May produce harmful advice on hard scenarios. Requires heavy human supervision and should not be used for customer-facing communications without review. |
| **< 50%** | Insufficient domain expertise. The agent's responses are predominantly generic and would not be useful to a returns operations professional. Not suitable for any autonomous returns management tasks. |

### Difficulty-Adjusted Expectations

The scenario set is designed with a difficulty distribution:
- **Easy (~30%):** An agent with basic returns training should pass these. Failure on easy scenarios is a strong negative signal.
- **Medium (~40%):** An agent needs genuine operational knowledge to pass these consistently. Partial scores are common and acceptable.
- **Hard (~27%):** These are designed to trip up agents without deep domain expertise. Even competent agents may score Partial on some hard scenarios. Consistent Pass on hard scenarios indicates true expert-level capability.

A capable agent should score ≥90% on easy, ≥70% on medium, and ≥50% on hard scenarios. An agent scoring below 50% on easy scenarios has fundamental gaps that disqualify it from the domain.
