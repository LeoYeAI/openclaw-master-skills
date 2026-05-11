# Carrier Relationship Management — LLM Grading Rubric

## Purpose

This rubric guides an LLM grader in scoring agent responses to carrier relationship management evaluation scenarios. Each scenario contains 3–5 evaluation criteria with pass/fail rubric descriptions. The grader assigns a score to each criterion, and the weighted sum produces the scenario score.

---

## Grading Scale

| Rating | Score | Definition |
|---|---|---|
| **Pass** | 1.0 | Response demonstrates domain expertise. The recommended actions are what an experienced transportation manager would do. Correct market benchmarks, regulatory frameworks (FMCSA), and financial thresholds are applied. The response reflects operational judgment — not just textbook knowledge but awareness of how carriers price freight, how market cycles affect leverage, how scorecards drive behavior, and how relationships are built and maintained over multi-year horizons. |
| **Partial** | 0.5 | Response is directionally correct but incomplete or imprecise. The agent identifies the general category of problem and suggests reasonable actions, but misses critical operational details, applies rate benchmarks incorrectly, omits a key stakeholder in the negotiation, or provides advice that would work in theory but cause problems in practice (e.g., demanding rate reductions during a capacity crisis, or firing a carrier without qualifying replacements first). |
| **Fail** | 0.0 | Response is incorrect, dangerously incomplete, or generic. The agent either misidentifies the situation type, applies the wrong framework (e.g., using spot market logic for a contract renewal), recommends actions that would harm carrier relationships or capacity access, or provides advice so generic it could apply to any vendor management context ("negotiate a better deal"). A response that sounds plausible to a procurement generalist but would make a transportation manager wince. |

### Grading Decision Guide

When choosing between adjacent ratings, use these tiebreakers:

**Pass vs. Partial:**
- Did the response identify the *single most important action* for this scenario? If yes and the rest is reasonable, lean Pass.
- Would a transportation director reading this response need to add significant corrections before acting on it? If yes, Partial.

**Partial vs. Fail:**
- Does the response demonstrate awareness that this is a freight/carrier context (not generic vendor management)? If not, Fail.
- Would following the response's advice cause active harm (rate increases, capacity loss, compliance violations, relationship damage)? If yes, Fail.
- Is the response merely incomplete but pointed in the right direction? Partial.

---

## Domain Expertise vs. Generic Response

The core distinction this rubric enforces is between responses grounded in transportation management expertise and responses that apply generic procurement or vendor management logic to a carrier-shaped problem.

### What Constitutes Domain Expertise

An expert-level response demonstrates knowledge that can only come from managing carrier portfolios in freight transportation. Specifically:

**1. Rate and Market Knowledge**
- Understands that a freight rate has components (linehaul, FSC, accessorials, minimums) that must be negotiated independently
- Knows that a carrier quoting a low linehaul with an aggressive FSC table can be more expensive at high diesel prices
- References DAT, Greenscreens, or equivalent market benchmarks for lane-level rate validation
- Understands freight market cycles and adjusts negotiation strategy to the current phase (shipper-favorable vs. carrier-favorable)
- Knows the difference between contract and spot rates and when each is appropriate
- Calculates total cost per shipment (not just per-mile rate) including modeled FSC, expected detention, and accessorials

**2. Carrier Operations and Compliance**
- References FMCSA authority, insurance verification, and safety ratings as carrier qualification requirements
- Knows the difference between asset carriers, brokers, and their respective risk profiles
- Understands tender acceptance as a leading indicator of rate misalignment or carrier capacity issues
- References routing guide structure (primary, secondary, tertiary) as the mechanism for freight allocation
- Knows that double-brokering creates insurance gaps and compliance risks
- Understands that carrier financial distress manifests through insurance changes, bond reductions, and driver pay complaints before it shows in service metrics

**3. Scorecarding and Performance Management**
- Tracks the right metrics: OTD, tender acceptance, claims ratio, invoice accuracy
- Sets specific thresholds (e.g., OTD ≥95% target, <90% red flag) rather than vague "good performance" language
- Distinguishes between carrier-level and lane-level performance
- Knows that corrective action plans require specific metrics, timelines, and consequences
- Uses scorecard data to drive allocation decisions (more volume for top performers, less for underperformers)

**4. Relationship and Negotiation Judgment**
- Calibrates negotiation tone to market conditions and relationship history
- Knows that squeezing carriers below their cost floor in a soft market guarantees service failures when the market turns
- Recommends transparent communication about volume changes rather than letting carriers discover shortfalls
- Frames rate negotiations with data rather than demands
- Understands the long-term consequences of short-term cost optimization
- Knows that carriers reward shippers who make their drivers' lives easier (detention reduction, drop-trailer programs, consistent scheduling)

**5. RFP and Portfolio Strategy**
- Evaluates bids on a weighted scorecard (rate, service, capacity, operational fit) not price alone
- Understands routing guide depth requirements based on lane volume
- Knows that awarding too many carriers on a low-volume lane fragments volume below carrier interest thresholds
- References the RFP cycle (8-12 weeks) with specific phases (pre-analysis, bid, evaluation, award, implementation)
- Distinguishes between incumbent and new carrier evaluation approaches

### Common Indicators of Generic Responses

These patterns indicate the response lacks domain-specific expertise. Any single indicator is not disqualifying, but multiple indicators strongly suggest a Fail or low Partial:

**1. Wrong Abstraction Layer**
- Refers to carriers as "vendors" or "suppliers" without recognizing the specific carrier-shipper dynamic
- Calls rate negotiation "vendor negotiation" without referencing freight-specific elements (FSC, accessorials, lane-level pricing)
- Describes carrier scorecards as "vendor performance reviews" without specifying freight KPIs
- Suggests generic "cost reduction strategies" rather than lane-level rate benchmarking and total cost modeling

**2. Missing Operational Mechanics**
- Does not reference FMCSA compliance as a carrier qualification requirement
- Fails to distinguish between asset carriers and brokers and their different risk/service profiles
- Does not mention routing guide structure or tender waterfall logic
- Suggests awarding freight based on price alone without a weighted evaluation
- Recommends "renegotiating" without specifying what data to gather, what to concede, and what to protect

**3. Incorrect Market Application**
- Treats freight rates as fixed prices rather than market-sensitive, cycle-driven rates with components
- Does not adjust negotiation strategy based on market conditions (shipper-favorable vs. carrier-favorable)
- Ignores seasonal patterns (produce season, peak retail) that affect capacity and pricing
- Recommends the same approach regardless of carrier size, type, or lane characteristics

**4. One-Dimensional Analysis**
- Addresses only rate without considering service quality, capacity security, or relationship health
- Focuses on cost reduction without considering the risk of carrier exit, service degradation, or capacity loss
- Does not consider the portfolio impact of individual carrier decisions (e.g., removing one carrier affects lane coverage for multiple lanes)
- Fails to connect scorecard metrics to allocation decisions

**5. Tone-Deaf Communication**
- Recommends aggressive or threatening communication for routine rate negotiations
- Does not calibrate tone to relationship status and market conditions
- Uses generic "Dear Vendor" language rather than carrier-specific, relationship-aware communication
- Treats carrier exit as a punitive action rather than a business decision communicated respectfully

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
A response that says "negotiate a better rate" is not the same as a response that says "benchmark the lane against DAT's 90-day contract average, model total cost including FSC at three diesel price points, and propose a rate 3-5% above the lowest competitive bid to reflect the carrier's superior OTD." The first is generic; the second demonstrates domain knowledge. Grade accordingly.

**Market Context Matters**
A response that recommends aggressive rate reductions is correct in a soft market (OTRI <5%, spot below contract) and incorrect in a tight market (OTRI >12%, spot above contract). The grader should evaluate whether the agent's recommendations match the market conditions described in the scenario.

**Relationship Awareness Matters**
A technically correct recommendation that would damage a critical carrier relationship should receive Partial rather than Pass. Transportation management is a repeat-game — the agent's advice should reflect long-term relationship consequences, not just immediate financial optimization.

**Omission Is Failure**
If a criterion's pass description includes 4 elements and the response covers 2 well but ignores 2, this is Partial — not Pass. The pass description represents the complete expert response.

**Practicality Test**
Would an experienced transportation manager read this response and say "yes, that's exactly what I'd do"? If yes, Pass. Would they say "that's roughly right but they're missing X"? Partial. Would they say "no, that would make things worse"? Fail.

---

## Grading Edge Cases

### When the Response Is Right for the Wrong Reasons

If the agent recommends the correct action but explains it using incorrect reasoning (e.g., recommends FMCSA compliance checking but cites the wrong regulatory section), assign **Partial**. Correct actions with wrong reasoning suggest the agent may not replicate the correct behavior in novel situations.

### When the Response Adds Correct Information Not in the Rubric

If the agent provides additional relevant and correct information beyond what the pass rubric describes, this does not change the scoring — it's still a Pass. Do not penalize for additional correct content, even if it wasn't asked for, unless it contradicts other parts of the response.

### When the Response Contradicts Itself

If the agent states conflicting recommendations (e.g., "consolidate to fewer carriers" in one paragraph and "add more carriers for diversification" in another without a clear conditional), assign **Fail** for that criterion unless one recommendation is clearly framed as contingent on a condition.

### When the Response Addresses a Different Aspect of the Problem

If the criterion asks about "rate negotiation strategy" and the agent's response focuses entirely on "carrier scorecarding" (a different criterion), assign **Fail** for the rate negotiation criterion even if the scorecarding content is excellent. Each criterion is graded independently.

---

## Aggregate Interpretation

After scoring all criteria for all scenarios, the following aggregate benchmarks indicate capability levels:

| Aggregate Score | Interpretation |
|---|---|
| **≥ 85%** | Expert-level carrier relationship management capability. The agent can handle the full range of carrier management decisions with minimal human oversight. Suitable for production use in rate analysis, carrier scorecarding, RFP evaluation, and relationship communication. |
| **70–84%** | Competent with supervision. The agent handles routine carrier management tasks well but needs human review on complex multi-carrier negotiations, market cycle positioning, and strategic portfolio decisions. Suitable for first-draft analyses that a transportation manager reviews. |
| **50–69%** | Inconsistent. The agent demonstrates some domain knowledge but has significant gaps. May produce harmful advice on hard scenarios (e.g., recommending aggressive tactics in a tight market). Requires heavy human supervision. |
| **< 50%** | Insufficient domain expertise. The agent's responses are predominantly generic vendor management advice without freight-specific knowledge. Not suitable for any autonomous carrier management tasks. |

### Difficulty-Adjusted Expectations

The scenario set is designed with a difficulty distribution:
- **Easy (~30%):** An agent with basic freight knowledge should pass these. Failure on easy scenarios is a strong negative signal.
- **Medium (~40%):** An agent needs genuine operational knowledge to pass these consistently. Partial scores are common and acceptable.
- **Hard (~30%):** These are designed to trip up agents without deep domain expertise. Even competent agents may score Partial on some hard scenarios. Consistent Pass on hard scenarios indicates true expert-level capability.

A capable agent should score ≥90% on easy, ≥70% on medium, and ≥50% on hard scenarios. An agent scoring below 50% on easy scenarios has fundamental gaps that disqualify it from the domain.
