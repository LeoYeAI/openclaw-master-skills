# Production Scheduling — LLM Grading Rubric

## Purpose

This rubric guides an LLM grader in scoring agent responses to production scheduling evaluation scenarios. Each scenario contains 3–5 evaluation criteria with pass/fail rubric descriptions. The grader assigns a score to each criterion, and the weighted sum produces the scenario score.

---

## Grading Scale

| Rating | Score | Definition |
|---|---|---|
| **Pass** | 1.0 | Response demonstrates production scheduling domain expertise. Calculations are correct or within acceptable rounding tolerances. The recommended actions are what an experienced production scheduler managing discrete/batch manufacturing with 15+ years of experience would do. Scheduling decisions reflect awareness of the constraint, sequence-dependent setups, labour qualification requirements, and the tension between throughput, delivery, and changeover cost. The response shows operational judgment — not textbook recitation but awareness of how scheduling actually works on a shop floor. |
| **Partial** | 0.5 | Response is directionally correct but incomplete or imprecise. The agent identifies the general type of scheduling problem and suggests reasonable approaches, but misses critical details: ignores sequence-dependent setup times, omits the constraint from the analysis, applies a dispatching rule without explaining why it fits the situation, does not distinguish between forward and backward scheduling when both are relevant, or provides advice that works in theory but ignores shop floor realities (union rules, operator certifications, changeover matrices, queue time at downstream work centres). |
| **Fail** | 0.0 | Response is incorrect, dangerously incomplete, or generic. The agent misidentifies the constraint, applies the wrong dispatching rule, gets capacity calculations fundamentally wrong, recommends actions that would starve the constraint or create excessive WIP, violates regulatory or union constraints, or provides advice so generic it could apply to any manufacturing context ("optimise your schedule and communicate with the team"). A response that sounds reasonable to a layperson but would make an experienced production scheduler wince. |

### Grading Decision Guide

When choosing between adjacent ratings, use these tiebreakers:

**Pass vs. Partial:**
- Did the response correctly identify and protect the constraint? If yes and the logic is sound, lean Pass.
- Would a production manager reading this response need to add significant corrections before acting on it? If yes, Partial.
- Did the response quantify the financial impact of scheduling decisions (changeover cost, overtime cost vs. penalty exposure, throughput value per hour)? If yes, lean Pass. Financial quantification is a hallmark of experienced scheduling.

**Partial vs. Fail:**
- Does the response demonstrate awareness that this is a production scheduling context (not generic project management or supply chain management)? If not, Fail.
- Would following the response's advice cause active harm (constraint starvation, regulatory violation, uncontrolled WIP growth, customer penalty exposure without acknowledgment)? If yes, Fail.
- Is the response merely incomplete but pointed in the right direction? Partial.

---

## Domain Expertise vs. Generic Response

The core distinction this rubric enforces is between responses grounded in production scheduling expertise and responses that apply generic operations or project management logic to a manufacturing-shaped problem.

### What Constitutes Domain Expertise

An expert-level response demonstrates knowledge that can only come from working in production scheduling at a discrete or batch manufacturing facility. Specifically:

**1. Constraint Awareness (Theory of Constraints)**
- Identifies the constraint work centre from utilisation data (highest load-to-capacity ratio, not highest WIP queue)
- Understands that a minute lost at the constraint is a minute lost for the entire plant
- Applies subordination — schedules non-constraint work centres to serve the constraint's needs, not to maximise their own utilisation
- Knows the difference between a true constraint and a temporary WIP queue caused by upstream batch-dumping
- Implements buffer management (time buffers, not inventory buffers) with green/yellow/red zones
- Recognises shifting bottlenecks driven by product mix changes and adjusts the scheduling logic accordingly

**2. Scheduling Mechanics**
- Correctly applies dispatching rules (SPT, EDD, CR, WSJF) and can explain when each is appropriate
- Understands sequence-dependent setup times and uses setup matrices to optimise changeover sequences
- Performs forward and backward scheduling and understands the practical difference (backward preserves flexibility and minimises WIP)
- Calculates Critical Ratio and interprets values correctly (CR < 1.0 = behind schedule)
- Distinguishes finite from infinite capacity planning and knows that MRP output is not a feasible schedule
- Respects frozen/slushy/liquid planning horizons and the cost of schedule changes

**3. Disruption Response**
- Immediately assesses whether the disruption affects the constraint — this determines response priority
- Checks buffer penetration before deciding on action (green = monitor, yellow = expedite, red = escalate)
- Identifies alternate routings, subcontracting options, and partial-build strategies
- Communicates revised schedules within 30 minutes of a significant disruption
- Sets a stability lock after re-sequencing to prevent cascading changes
- Quantifies the financial impact of disruption to justify overtime, subcontracting, or customer negotiations

**4. Changeover Optimisation**
- Applies SMED methodology: separates internal and external setup elements
- Understands that external work done during machine stoppage is recoverable time
- Knows the campaign-vs-mixed-model tradeoff and can calculate the economic crossover point
- Uses setup matrices for sequence-dependent changeovers (e.g., light-to-dark colour sequencing)
- Connects changeover reduction to throughput gain at the constraint (and knows that changeover reduction at non-constraints has zero throughput impact)

**5. Labour and Regulatory Awareness**
- Maintains and uses a skill/certification matrix for operator assignment
- Identifies single-point-of-failure certifications and recommends cross-training
- Respects union rules on overtime, seniority, mandatory rest periods, and shift assignment
- In regulated environments (pharma, food, aerospace), treats operator certification as a hard constraint — never suggests workarounds that compromise compliance
- Factors fatigue into scheduling decisions (no complex changeovers in the last 2 hours of a 12-hour shift)

**6. OEE and Performance Analysis**
- Correctly calculates OEE components (Availability × Performance × Quality)
- Excludes planned downtime from the Availability denominator when using standard OEE (includes it for TEEP)
- Identifies the largest loss category and prioritises improvement at the constraint
- Understands that OEE improvement at a non-constraint does not increase plant output
- Connects OEE to throughput value per hour for financial impact quantification

**7. ERP/MES Integration**
- Understands the MRP-to-production-order-to-shop-floor flow
- Knows that MRP runs infinite-capacity logic and the scheduler must resolve overloads before releasing orders
- Uses MES actual data to validate and update scheduling parameters (setup times, run rates, yield factors)
- Recognises the plan-vs-reality gap and implements a rolling re-plan cadence
- Detects phantom demand from BOM errors and phantom inventory from posting errors

### Common Indicators of Generic Responses

These patterns indicate the response lacks production scheduling expertise. Any single indicator is not disqualifying, but multiple indicators strongly suggest a Fail or low Partial:

**1. Wrong Abstraction Layer**
- Uses project management language ("critical path method," "Gantt chart") instead of production scheduling language (dispatching rules, finite capacity, constraint, work centre)
- Refers to "tasks" instead of "operations" or "jobs"
- Treats the factory as a single resource rather than a network of work centres with different capacities
- Suggests "analysing the data" or "looking at the schedule" without specifying what analysis or which scheduling technique

**2. Missing Constraint Awareness**
- Does not identify the constraint or identifies the wrong work centre as the constraint
- Recommends maximising utilisation at all work centres (creates excess WIP at non-constraints)
- Treats all work centres as equally important for disruption response
- Does not establish or reference buffer management at the constraint
- Confuses WIP accumulation with a bottleneck (WIP piles up BEFORE the bottleneck, not AT it)

**3. Incorrect Scheduling Logic**
- Applies the wrong dispatching rule without justification (e.g., FIFO when due dates are critical)
- Ignores sequence-dependent setup times in changeover optimisation
- Does not calculate total changeover time when sequencing jobs (treating changeover as zero or fixed)
- Treats forward and backward scheduling as identical
- Ignores the finite capacity of the constraint when loading work

**4. Regulatory and Labour Blind Spots**
- Suggests running a regulated process with an unqualified operator
- Ignores union rules on overtime or shift assignment
- Does not check the skill matrix before assigning operators to work centres
- Treats labour as infinitely flexible (any operator can run any machine)

**5. Dangerous Advice**
- Recommends starving the constraint to work on non-constraint improvements
- Suggests ignoring buffer penetration and relying on "the schedule"
- Proposes re-sequencing the schedule every hour (schedule instability is worse than suboptimal sequencing)
- Ignores the in-machine part during a breakdown (risking a $40K scrap)
- Splits capacity equally between competing rush orders instead of identifying the optimal allocation

---

## Scoring Individual Criteria

For each criterion within a scenario, the grader should:

1. **Read the scenario context and task** to understand what the agent was asked to do.
2. **Read the criterion's pass and fail rubric descriptions** — these are specific to the scenario, not generic.
3. **Evaluate the agent's response** against both the pass and fail descriptions.
4. **Assign a rating:**
   - **Pass (1.0):** The response matches the pass description substantively. Minor calculation rounding differences are acceptable (within ±10%). The grader is evaluating whether the agent demonstrated the same scheduling judgment, not whether it used identical numbers.
   - **Partial (0.5):** The response falls between the pass and fail descriptions. It captures some elements of the pass description but misses others, or gets the direction right but the numbers wrong.
   - **Fail (0.0):** The response matches the fail description, or is worse than the fail description, or does not address the criterion at all.

### Important Scoring Nuances

**Calculations Matter**
In production scheduling, the numbers matter. A response that correctly identifies "use EDD" but gets the capacity calculation wrong by 30% should receive Partial for the dispatching rule criterion but Fail for the capacity calculation criterion. Domain expertise is demonstrated through correct quantitative analysis, not just correct concept identification.

**Constraint Centrality**
Every scheduling decision should be evaluated through the lens of: does this protect or harm the constraint? A response that makes correct decisions about non-constraint operations but ignores the constraint's needs should be Partial at best. Conversely, a response that correctly manages the constraint but is vague about non-constraint operations can still Pass if the constraint logic is sound.

**Financial Quantification**
Responses that quantify scheduling decisions in financial terms (throughput loss per hour of constraint downtime, overtime cost vs. penalty exposure, changeover cost vs. carrying cost) receive credit even when other aspects are weaker. Responses that ignore the financial dimension are capped at Partial regardless of analytical quality.

**Regulatory Hard Constraints**
In scenarios involving regulated processes (pharma, food safety, aerospace), any response that suggests violating a regulatory requirement (running with an unqualified operator, skipping required inspections, mixing lots without proper traceability) is an automatic Fail for that criterion regardless of other content.

**Omission Is Failure**
If a criterion's pass description includes 4 elements and the response covers 2 well but ignores 2, this is Partial — not Pass. The pass description represents the complete expert response.

**Over-Reaction Is as Wrong as Under-Reaction**
Re-sequencing the entire plant schedule because a non-constraint machine is down for 30 minutes is as wrong as ignoring a constraint breakdown. Correct calibration of response to impact severity is fundamental to scheduling expertise.

---

## Grading Edge Cases

### When the Response Is Right for the Wrong Reasons

If the agent recommends the correct scheduling action but explains it using incorrect reasoning (e.g., recommends reducing changeovers at the constraint "to improve OEE" rather than "to recover constraint capacity"), assign **Partial**. Correct actions with wrong reasoning suggest the agent may not replicate the correct behavior in novel situations.

### When the Response Adds Correct Information Not in the Rubric

If the agent provides additional relevant and correct information beyond what the pass rubric describes (e.g., mentions TPM daily checks when the rubric only asks about buffer management), this does not change the scoring — it's still a Pass. Do not penalise for additional correct content.

### When the Response Contradicts Itself

If the agent states conflicting recommendations (e.g., "maximise utilisation at all work centres" in one paragraph and "subordinate non-constraints to the drum's pace" in another without resolving the tension), assign **Fail** for that criterion.

### When Calculation Rounding Differs

Accept any answer within ±10% of the expected value as correct. For OEE calculations, accept answers within ±2 percentage points. For capacity calculations, accept ±1 hour for shifts up to 16 hours.

---

## Terminology Weighting

Domain-specific terminology usage is a signal, not a score. The grader should use terminology as follows:

**Terminology that signals expertise (positive signal):**
- Correct use of: constraint, drum-buffer-rope, subordination, buffer penetration, exploitation, finite capacity, infinite capacity, dispatching rule, SPT, EDD, critical ratio, WSJF, setup matrix, sequence-dependent setup, SMED, internal/external setup, OEE (availability/performance/quality), TEEP, takt time, heijunka, work centre, routing, BOM, MRP planned order, production order, frozen zone, plan adherence, WIP turns, make span, transfer batch, campaign scheduling, mixed-model, run rate, cycle time, changeover
- Correct differentiation between: constraint vs. non-constraint, buffer time vs. buffer inventory, forward vs. backward scheduling, finite vs. infinite capacity, planned vs. unplanned downtime, setup time vs. run time

**Terminology that signals misunderstanding (negative signal):**
- Calling any work centre with WIP in front of it a "bottleneck" without checking utilisation
- Using "buffer stock" when the context calls for "time buffer" (DBR)
- Confusing "schedule adherence" with "on-time delivery" (they measure different things)
- Using "capacity" interchangeably with "utilisation"

---

## Aggregate Interpretation

| Aggregate Score | Interpretation |
|---|---|
| **≥ 85%** | Expert-level production scheduling capability. The agent can handle the full range of job sequencing, bottleneck management, disruption response, and changeover optimisation with minimal human oversight. Suitable for generating draft schedules, disruption response plans, and capacity analyses that a scheduler reviews. |
| **70–84%** | Competent with supervision. The agent handles routine scheduling well but needs human review on complex multi-disruption scenarios, constraint shift detection, and regulatory-constrained scheduling. Suitable for first-draft analysis and recommendations. |
| **50–69%** | Inconsistent. The agent demonstrates some scheduling knowledge but has significant gaps in constraint management, financial quantification, or regulatory awareness. May produce harmful advice on hard scenarios (e.g., recommending regulatory workarounds, ignoring constraint starvation). Requires heavy human supervision. |
| **< 50%** | Insufficient domain expertise. The agent's responses are predominantly generic operations advice without production-scheduling-specific calculations or judgment. Not suitable for any autonomous scheduling tasks. |

### Difficulty-Adjusted Expectations

- **Easy (~30%):** An agent with basic scheduling training should pass these. These test fundamental calculations (OEE, critical ratio, simple sequencing, colour changeover). Failure on easy scenarios is a strong negative signal.
- **Medium (~43%):** An agent needs genuine operational knowledge to pass these consistently. These involve SMED analysis, DBR implementation, disruption response with alternate routing, and campaign scheduling tradeoffs. Partial scores are common and acceptable.
- **Hard (~26%):** These are designed to test deep expertise: multi-disruption compounds, competing rush orders with commercial tradeoffs, regulatory-constrained labour scheduling, and full plant re-schedules. Even competent agents may score Partial on some hard scenarios.

A capable agent should score ≥90% on easy, ≥70% on medium, and ≥50% on hard scenarios.
