# Eval Results: production-scheduling

**Version:** 1.0.0  
**Model:** claude-sonnet-4-20250514  
**Timestamp:** 2026-02-24T14:38:37Z  
**Aggregate Score:** 92.4%  
**Passed (>=70%):** 21/23

## Summary by Difficulty

| Difficulty | Avg Score | Count |
|---|---|---|
| Easy | 78.9% | 7 |
| Medium | 97.2% | 10 |
| Hard | 100.0% | 6 |

## Summary by Category

| Category | Avg Score | Count |
|---|---|---|
| bottleneck-management | 100.0% | 3 |
| capacity-planning | 100.0% | 3 |
| changeover-optimisation | 95.8% | 3 |
| disruption-response | 97.5% | 5 |
| erp-integration | 92.5% | 2 |
| job-sequencing | 66.2% | 4 |
| labour-scheduling | 100.0% | 2 |
| oee-analysis | 100.0% | 1 |

## Scenario Details

### PSC-001: Basic job priority sequencing with EDD rule

**Difficulty:** easy | **Category:** job-sequencing | **Score:** 37.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| dispatching_rule_selection | 0.3 | fail | 0.0 |
| capacity_calculation | 0.3 | pass | 1.0 |
| sequence_logic | 0.25 | fail | 0.0 |
| practical_judgment | 0.15 | partial | 0.5 |

**dispatching_rule_selection:** The agent does not select EDD (Earliest Due Date) as the primary dispatching rule despite the clear due date urgency in the scenario. Instead, it uses a complex 'hybrid dispatching approach' that prioritizes customer tier first, then due dates. This leads to putting WO-3303 (due 9/19) first despite being the least urgent, and ranking WO-3302 (due 9/17, critically behind with CR=0.29) last. The agent explicitly states 'WO-3303 takes absolute priority' regardless of due date, which contradicts proper EDD sequencing for meeting delivery commitments.

**capacity_calculation:** The agent correctly calculates total processing time as 10.5 hours, changeover time as 4 × 20 min = 80 min = 1.33 hours, for a total of 11.83 hours required vs 8 hours available. The shortfall of 3.83 hours is accurately calculated. The agent correctly identifies that not all jobs can fit in the day shift and specifies that WO-3302 must defer to evening shift.

**sequence_logic:** The agent does not sequence by due date priority as required. It puts WO-3303 (due 9/19) first despite being the least urgent, and places WO-3302 (due 9/17) last despite being most urgent. The sequence WO-3303 → WO-3305 → WO-3301 → WO-3304 does not prioritize the 9/17 due dates (WO-3302, WO-3304) first as proper EDD logic would require. The agent's customer-tier-first approach contradicts due-date-driven sequencing.

**practical_judgment:** The agent demonstrates some practical awareness by noting customer tier considerations and checking that deferred jobs can complete by due date ('NO DELIVERY MISS'). However, it makes a questionable judgment by prioritizing the Tier-1 customer's non-urgent job (due 9/19) over critically behind Tier-3 jobs (due 9/17). While customer relationships matter, deferring a critically late job (CR=0.29) to prioritize a comfortable job (CR=2.0) shows poor scheduling judgment that could damage overall customer relationships through delivery failures.

---

### PSC-002: OEE calculation and loss prioritisation at the constraint

**Difficulty:** easy | **Category:** oee-analysis | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| oee_calculation | 0.35 | pass | 1.0 |
| loss_identification | 0.3 | pass | 1.0 |
| improvement_recommendation | 0.2 | pass | 1.0 |
| contextual_awareness | 0.15 | pass | 1.0 |

**oee_calculation:** Agent correctly calculated all OEE components: Planned Production Time = 120-8 = 112 hrs, Availability = (112-14)/112 = 87.5%, Performance = 7,200/7,840 = 91.8%, Quality = 6,840/7,200 = 95.0%, and Overall OEE = 87.5% × 91.8% × 95.0% = 76.3%. The calculations are accurate and within the acceptable range of 74-78%.

**loss_identification:** Agent correctly identified availability loss (14 hours unplanned downtime) as the largest loss category at 52% of total losses, quantified as $9,100/week. Also properly calculated performance loss as $5,330 and quality loss as $2,990, showing availability is indeed the primary concern with proper financial quantification using $650/hr constraint throughput value.

**improvement_recommendation:** Agent recommended prioritizing unplanned downtime reduction with specific actionable items: daily operator checks, weekly PM enhancement, and monthly deep maintenance. Correctly noted this is the constraint and provided ROI analysis showing $3,750/week net gain. Demonstrated understanding that constraint improvement directly translates to throughput gain.

**contextual_awareness:** Agent demonstrated strong contextual awareness by noting 76.3% OEE 'vs. world-class 85%+' and quantified the annual opportunity cost at nearly $1M. Explicitly stated 'This constraint is underperforming significantly' and connected OEE improvement to plant throughput, showing understanding that this is the constraint work center where improvements matter most.

---

### PSC-003: Critical ratio calculation and job prioritisation

**Difficulty:** easy | **Category:** job-sequencing | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| critical_ratio_calculation | 0.4 | pass | 1.0 |
| priority_ranking | 0.3 | pass | 1.0 |
| escalation_judgment | 0.3 | pass | 1.0 |

**critical_ratio_calculation:** The agent correctly calculated all critical ratios: WO-5502: (Sep 24 - Sep 22)/3.5 = 2/3.5 = 0.57, WO-5504: (Sep 25 - Sep 22)/1.5 = 3/1.5 = 2.00, WO-5501: (Sep 26 - Sep 22)/3.0 = 4/3.0 = 1.33, WO-5503: (Sep 30 - Sep 22)/2.0 = 8/2.0 = 4.00. All calculations match the expected values within acceptable rounding tolerance. The agent also clearly showed the formula used: CR = (Due Date - Current Date) / Remaining Processing Time.

**priority_ranking:** The agent correctly ranked jobs by ascending critical ratio (lowest CR = highest priority): WO-5502 (0.57) as Priority 1, WO-5501 (1.33) as Priority 2, WO-5504 (2.00) as Priority 3, and WO-5503 (4.00) as Priority 4. The agent also correctly identified WO-5502 as 'CRITICAL - Behind schedule' with CR < 1.0 and flagged it for immediate processing.

**escalation_judgment:** The agent correctly identified WO-5502 as requiring immediate escalation due to CR = 0.57 < 1.0, noting it needs 3.5 days of work but only has 2 days until due date (1.5 days short). Provided comprehensive escalation actions including notifying production manager, contacting customer about potential delay, evaluating overtime/weekend work, checking alternate routing, and assessing parallel processing. Also noted that WO-5503 with CR = 4.0 has significant slack and can be deferred if needed.

---

### PSC-004: Simple changeover sequence optimisation on a paint line

**Difficulty:** easy | **Category:** changeover-optimisation | **Score:** 87.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| optimal_sequence | 0.4 | pass | 1.0 |
| worst_case_comparison | 0.25 | partial | 0.5 |
| setup_matrix_understanding | 0.2 | pass | 1.0 |
| practical_notes | 0.15 | pass | 1.0 |

**optimal_sequence:** The agent correctly identifies the optimal light-to-dark sequence (White → Yellow → Red → Blue → Black) and accurately calculates the total changeover time as 40 minutes (4 transitions × 10 minutes each). The response demonstrates clear understanding of the light-to-dark sequencing principle and provides the correct minimum achievable changeover time.

**worst_case_comparison:** The agent attempts to identify a worst-case scenario but calculates it as 90 minutes instead of the correct 140 minutes (4 transitions × 35 minutes for pure dark-to-light sequence). While they do quantify savings (50 minutes vs. the correct 100 minutes), the comparison is based on an incorrect worst-case calculation. They do recognize the concept of comparing optimal vs. worst case.

**setup_matrix_understanding:** The agent demonstrates excellent understanding of sequence-dependent changeover times by constructing a complete setup matrix and clearly explaining the light-to-dark (10 min) vs. dark-to-light (35 min) cost asymmetry. They explicitly state the principle: 'never go backward in the light-to-dark spectrum' and recognize the '4× time penalty for dark-to-light transitions.'

**practical_notes:** The agent provides relevant practical implementation notes including pre-staging batches, color verification, first-piece inspection, and operator discipline. They also note that the ending with Black 'positions the line for a dark start the next day.' While they don't explicitly state the due date assumption, their analysis is contextually appropriate for equal due dates as specified in the scenario.

---

### PSC-005: Identifying the true constraint from WIP and utilisation data

**Difficulty:** easy | **Category:** bottleneck-management | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| constraint_identification | 0.35 | pass | 1.0 |
| wip_misconception_explanation | 0.3 | pass | 1.0 |
| constraint_management_recommendations | 0.35 | pass | 1.0 |

**constraint_identification:** The response correctly identifies SMT Pick-and-Place as the true constraint based on its 92% utilisation being the highest among all work centres. It explicitly states 'SMT utilisation: 92% (highest across all work centres)' and explains that this work centre 'has the least protective capacity cushion.' The response demonstrates understanding that utilisation ratio determines the constraint, not WIP queue size, by calculating theoretical minimum utilisation (84.4%) and explaining why 92% actual utilisation indicates near-constraint status.

**wip_misconception_explanation:** The response thoroughly explains why the WIP pile at wave soldering is misleading. It identifies the root cause as 'batch-dumping from upstream' where 'SMT likely processes boards in batches and releases them all at once to wave soldering, creating artificial queue spikes.' It correctly notes that wave soldering has 'excess capacity (22% protective capacity) but appears overloaded due to poor upstream release timing' and calculates that the 340-unit queue represents 1.06 days of queue time. The explanation clearly establishes that the WIP is a symptom of upstream batching from the constraint, not evidence that soldering is overloaded.

**constraint_management_recommendations:** The response provides comprehensive TOC-based constraint management actions. For exploitation: 'Eliminate SMT idle time,' 'Reduce SMT changeovers,' 'Run SMT through breaks,' and assigns best technician to prevent setup errors. For subordination: implements 'controlled release' from SMT to wave soldering, establishes proper buffer sizing (80-120 units vs current 340), and makes wave soldering process work in SMT's release sequence. It establishes buffer management with green/yellow/red zones and validates that downstream work centres won't constrain SMT output. The recommendations correctly focus all improvement efforts on the constraint while subordinating other work centres.

---

### PSC-006: Forward and backward scheduling for a multi-operation work order

**Difficulty:** easy | **Category:** job-sequencing | **Score:** 27.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| forward_schedule | 0.3 | fail | 0.0 |
| backward_schedule | 0.3 | fail | 0.0 |
| float_assessment | 0.25 | partial | 0.5 |
| scheduling_awareness | 0.15 | pass | 1.0 |

**forward_schedule:** The agent calculated Op 10 (6.5 hrs) finishing Monday at 14:30, then Op 20 (2.0 hrs) starting immediately at 14:30 and finishing Tuesday at 08:30. This is impossible - a 2-hour operation cannot span from Monday 14:30 to Tuesday 08:30 (18 hours later). The agent fundamentally misunderstands shift boundaries and inter-day scheduling logic. The correct forward schedule should show Op 20 starting Tuesday at 08:00 and finishing at 10:00, not spanning overnight.

**backward_schedule:** The backward schedule shows the same fundamental error in reverse. Op 20 is shown as 2.0 hours running from Thursday 14:00 to 16:00 (correct), but then Op 10 (6.5 hours) is shown running Thursday 08:00 to 14:30 (6.5 hours, correct duration). However, the agent fails to account for the queue time between operations and does not properly work backward through shift boundaries. The latest start should be earlier than Thursday given the 15 total hours of processing time.

**float_assessment:** The agent correctly identifies that there is significant float (claims 2.5 working days or 20 hours) and concludes the job is feasible with low risk. However, this float calculation is based on the incorrect forward/backward schedules. The directional assessment is right - there is substantial slack - but the quantification is wrong due to the scheduling errors.

**scheduling_awareness:** The agent demonstrates good understanding of the practical differences between forward and backward scheduling: 'Use backward scheduling...This preserves maximum scheduling flexibility for higher-priority or tighter-deadline work orders earlier in the week.' Also notes 'backward scheduling with the latest start date...preserves maximum scheduling flexibility' and suggests forward scheduling only 'If CNC Milling is the plant constraint.' Shows clear awareness of when to apply each approach and their strategic implications.

---

### PSC-007: Labour skill matrix and shift coverage gap analysis

**Difficulty:** easy | **Category:** labour-scheduling | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| operator_assignment | 0.3 | pass | 1.0 |
| single_point_of_failure_identification | 0.4 | pass | 1.0 |
| cross_training_recommendation | 0.3 | pass | 1.0 |

**operator_assignment:** The response provides a feasible assignment covering all 3 lines: Martinez → CNC Lathe (CNC-L2), Jackson → Welding (AWS-D1.1), Kim → Surface Grinding (GRND-1). Correctly identifies C. Patel as a float operator who 'holds all three certifications' rather than locking them to a single line. Also provides backup coverage plan with Thompson as CNC backup only.

**single_point_of_failure_identification:** Correctly identifies AWS-D1.1 (welding) as the critical single-point-of-failure with only 2 qualified operators (B. Jackson, C. Patel) marked as 'HIGH' risk. States 'If B. Jackson calls in sick, C. Patel becomes the single point of failure for welding operations.' Properly contrasts this with CNC-L2 (3 operators, 'Low' risk) and GRND-1 (3 operators, 'Low' risk). Clearly identifies welding as the highest-risk gap.

**cross_training_recommendation:** Recommends E. Thompson for AWS-D1.1 training as 'URGENT (Complete within 30 days)' to create '3rd welding-qualified operator, eliminating single-point-of-failure.' Provides specific business case and quantifies training time (40 hours). Also recommends D. Kim for CNC training and A. Martinez for AWS training as secondary priorities. Correctly prioritizes welding certification training due to the identified single-point-of-failure risk.

---

### PSC-008: Drum-buffer-rope implementation for a new constraint

**Difficulty:** medium | **Category:** bottleneck-management | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| drum_identification_and_exploitation | 0.3 | pass | 1.0 |
| buffer_design | 0.3 | pass | 1.0 |
| rope_mechanism | 0.2 | pass | 1.0 |
| subordination_logic | 0.2 | pass | 1.0 |

**drum_identification_and_exploitation:** Correctly identifies TMC-01 as the drum/constraint. Provides specific exploitation actions: reduces changeovers from 3 to 2 per day through part family grouping, recovering 25 min/day = 2.1 additional parts; eliminates micro-stops from 3% to 1% = 19 minutes/day = 1.6 parts; implements external setup during machine runtime; assigns dedicated experienced operator; adds quality gates before constraint to improve yield from 98% to 99.5%. Quantifies each improvement in parts/day terms, showing understanding that constraint time equals plant throughput.

**buffer_design:** Sets buffer duration at 6 hours (50% of 12-hour upstream lead time) with appropriate buffer factor of 0.5. Defines clear buffer zones: Green (11-15 parts, 67-100%), Yellow (6-10 parts, 33-66%), Red (1-5 parts, 1-33%), Black (0 parts). Specifies monitoring frequency (every 2 hours) and escalation actions for each zone, including quantified throughput loss ($32/minute in black zone). Buffer size of 15 parts correctly calculated from 6 hours × 2.5 parts/hour constraint consumption rate.

**rope_mechanism:** Defines rope as release control mechanism: releases 6-part batches from sawing when buffer drops to 12 parts, maintaining 3 releases per day every 8 hours. Establishes maximum WIP discipline with 33 parts total (15 buffer + 18 upstream WIP). Explicitly states 'Never release more than the constraint can consume + buffer replenishment, regardless of upstream capacity availability' - this demonstrates proper rope understanding that prevents WIP accumulation.

**subordination_logic:** Explicitly subordinates non-constraints: Heat treatment (60% util) should 'deliberately plan 40% idle time to absorb upstream variability'; CNC rough machining must maintain 28% protective capacity and 'do not optimize rough machining independently'; Sawing reduced from 85% to 75% utilization through rope control. States upstream operations should process batches 'to feed TMC-01 schedule, not to maximize heat treatment efficiency.' Clearly understands subordination principle that non-constraints serve the drum's needs.

---

### PSC-009: SMED changeover reduction analysis

**Difficulty:** medium | **Category:** changeover-optimisation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| smed_classification | 0.25 | pass | 1.0 |
| phase_1_2_improvements | 0.3 | pass | 1.0 |
| financial_impact | 0.25 | pass | 1.0 |
| implementation_awareness | 0.2 | pass | 1.0 |

**smed_classification:** The agent correctly identified 'Search for next die' (8 min) and 'Transport die to press' (6 min) as external activities incorrectly performed during machine stoppage, totaling 14 minutes of external-done-internal time. The classification table properly shows these as 'External' activities that were being done internal. The agent also correctly classified the remaining activities as internal: die removal/fastening (24 min total), positioning (5 min), adjustments (7+6 min), trial runs (4 min), totaling 54 minutes of true internal time. The classification demonstrates clear understanding of SMED principles.

**phase_1_2_improvements:** Phase 1 properly identifies moving die search and transport to pre-changeover external preparation, saving 14 minutes immediately. Phase 2 correctly proposes quick-release clamps to replace the 24-minute bolt system (12+12 min) with a faster clamping cycle, standardized die heights to eliminate shut height adjustment (7 min), and alignment systems to reduce positioning time. The agent estimates total Phase 2 reduction of 40 minutes, bringing final changeover time to 11 minutes, which aligns with the expected 18-28 minute range. The response demonstrates understanding of both external/internal separation and internal streamlining phases.

**financial_impact:** The agent correctly calculates current cost: 68 min × 4 changeovers/day × $720/hr ÷ 60 min = $3,264/day, and annual impact of $816,000 (using 250 production days). Post-improvement calculation shows 11 min changeovers resulting in $528/day cost and $684,000 annual savings. The calculation methodology is correct, properly accounting for constraint throughput loss per minute and daily changeover frequency. The ROI calculation shows 13-day payback with 2,750% first-year return, demonstrating strong financial justification.

**implementation_awareness:** The agent provides a clear phased implementation approach: Phase 1 (weeks 1-2) requires no capital investment and implements external preparation immediately. Phase 2 is properly sequenced over weeks 3-12 with specific capital investments ($24,000 total). The response includes risk mitigation for crane and forklift availability, standardized procedures, operator training requirements, and success metrics. The implementation roadmap shows understanding of the practical constraints and sequencing needed for successful SMED deployment.

---

### PSC-010: Disruption response — machine breakdown at the constraint

**Difficulty:** medium | **Category:** disruption-response | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| in_machine_part_assessment | 0.2 | pass | 1.0 |
| alternate_routing_analysis | 0.25 | pass | 1.0 |
| priority_sequencing | 0.25 | pass | 1.0 |
| recovery_plan_completeness | 0.3 | pass | 1.0 |

**in_machine_part_assessment:** The response thoroughly addresses the $42K part: identifies it as 80% complete (8 of 10 hours), assesses that spindle bearing failure typically doesn't affect workpiece fixture datums, recommends leaving part in machine fixture for resumption when repaired, accounts for tool re-qualification risk (+1 hour), and calculates total completion time (3 hours). Explicitly notes the high value at risk and treats it as priority recovery.

**alternate_routing_analysis:** Correctly identifies VMC-02's 500mm size limit and systematically evaluates all queued jobs. Properly categorizes 6 jobs as eligible (WO-8802 through WO-8809, all ≤500mm, totaling 18 hours) and 2 jobs requiring HBM-01 (WO-8803 at 650mm and WO-8805 at 800mm). Calculates VMC-02 available capacity as 5.6 hours/day (35% headroom × 16 hrs) and plans multi-day utilization strategy.

**priority_sequencing:** Applies correct priority logic: WO-8802 (Tier 1, due 9/25) gets immediate priority on VMC-02. For HBM restart, sequences WO-8805 (Tier 1) first, then WO-8803 (Tier 2). Uses both customer tier and due date appropriately. VMC-02 backfill jobs are sequenced by due date considering customer tier (ValveTech Tier 2 jobs scheduled appropriately).

**recovery_plan_completeness:** Provides comprehensive recovery plan covering all required elements: (1) immediate actions with specific timeline, (2) complete alternate routing analysis, (3) detailed recovery schedule with scenarios, (4) customer impact analysis identifying exactly which orders will be late, (5) overtime assessment with cost-benefit analysis ($1,200 vs $47K at-risk orders), (6) subcontracting option for backup, (7) structured customer communications with specific timelines, and (8) clear management decision points with business justification.

---

### PSC-011: Campaign scheduling vs. mixed-model decision with cost analysis

**Difficulty:** medium | **Category:** changeover-optimisation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| changeover_cost_analysis | 0.25 | pass | 1.0 |
| campaign_schedule_design | 0.3 | pass | 1.0 |
| inventory_cost_tradeoff | 0.25 | pass | 1.0 |
| recommendation_quality | 0.2 | pass | 1.0 |

**changeover_cost_analysis:** The agent correctly calculates current mixed-model changeover cost: 6 changes/day × 45 min = 270 minutes = 4.5 hours/day. Correctly values this at $850/hr constraint rate = $3,825/day or $956,250 annually. Properly identifies this represents 28% of constraint time (4.5/16 hours) consumed by changeovers. Shows clear understanding that changeover time is lost throughput at the constraint.

**campaign_schedule_design:** Designs a logical weekly campaign schedule that respects customer delivery frequencies. Correctly identifies that AutoCo needs weekly JIT (Monday-Tuesday Black production), BuildCo needs weekly delivery (Wednesday Grey), and groups lower-volume monthly customers (White, Red on Friday). Reduces changeovers from 30/week to 6/week while maintaining delivery requirements. Shows understanding of constraint between campaign efficiency and customer delivery windows.

**inventory_cost_tradeoff:** Performs detailed inventory analysis calculating cycle stock for each customer under campaign vs. mixed-model. Calculates total additional carrying cost at $31,600/year and compares to $765,000 changeover savings. Includes safety stock analysis for AutoCo ($3,120/year) and occasional mini-campaign costs ($9,560/year). Net benefit calculation of $720,720 demonstrates proper tradeoff quantification.

**recommendation_quality:** Recommends a sophisticated hybrid approach: base campaign schedule with JIT exceptions for AutoCo. Provides clear implementation plan, risk mitigation strategies, and success metrics. Quantifies net annual benefit of $720K with supporting rationale. Addresses quality risks, equipment risks, and demand variability. Shows expert-level understanding of practical implementation challenges in campaign scheduling.

---

### PSC-012: Material shortage response with partial-build strategy

**Difficulty:** medium | **Category:** disruption-response | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| allocation_logic | 0.3 | pass | 1.0 |
| partial_build_strategy | 0.3 | pass | 1.0 |
| schedule_re_sequencing | 0.2 | pass | 1.0 |
| root_cause_and_prevention | 0.2 | pass | 1.0 |

**allocation_logic:** Agent correctly allocates the 340 available units by priority: WO-9001 gets 120 units (Tier 1, due Thursday), WO-9002 gets 200 units (Tier 2, due Friday), WO-9003 gets only 20 units (partial allocation), and WO-9004 gets 0 units. The allocation table clearly shows customer tiers and justifies protecting Tier 1 completely and highest Tier 2 customer with remaining inventory. This matches the pass criteria exactly.

**partial_build_strategy:** Agent proposes a clear partial-build strategy: 'All four work orders proceed through Step 1: Mount DIN rails and wire ducts, Install enclosures and mechanical components, Complete all work that doesn't require TB-4420.' The response identifies which steps can proceed without the terminal blocks and explains that terminal blocks are installed at Step 2, allowing Steps 1, 3-5 to proceed. This preserves lead time and keeps assembly teams productive while waiting for material arrival.

**schedule_re_sequencing:** Agent provides a detailed revised schedule showing re-sequencing: WO-9001 completes Thursday as planned, WO-9002 completes Friday as planned, WO-9003 gets partial build Tuesday-Thursday then completes Friday PM-Saturday when material arrives, and WO-9004 shifts to Monday completion. The schedule table shows clear day-by-day activities and material usage, demonstrating proper re-sequencing to work around the constraint.

**root_cause_and_prevention:** Agent correctly identifies phantom inventory as the root cause: 'MRP shows 800 units on-hand, but a physical count reveals only 340 units. The gap of 460 units is phantom inventory (likely a receiving error or a posting failure).' Recommends immediate actions including second count verification, root cause investigation of receipts/postings, MRP correction, and prevention measures like daily cycle counting on TB-4420 and review of other high-value components for similar discrepancies.

---

### PSC-013: ERP work order management — MRP overload resolution

**Difficulty:** medium | **Category:** erp-integration | **Score:** 85.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| overload_resolution_strategy | 0.3 | partial | 0.5 |
| financial_analysis | 0.3 | pass | 1.0 |
| schedule_construction | 0.25 | pass | 1.0 |
| erp_process_awareness | 0.15 | pass | 1.0 |

**overload_resolution_strategy:** The agent correctly identifies the 17.6 hour overload and proposes using Saturday overtime (8 hours), leaving 9.6 hours to resolve. However, there's a critical error in the priority analysis - PO-2207 (Pin G) is classified as Tier 4 with no penalty, but the agent schedules it first in regular capacity instead of deferring it. The agent defers PO-2209 (7.6 hrs) and partially defers PO-2205 (2 hrs remaining), totaling 9.6 hours deferred, which mathematically resolves the overload. While the math works out, the strategy contains logical inconsistencies in applying the priority matrix they created.

**financial_analysis:** The agent provides comprehensive financial analysis: calculates overtime cost at $3,200 for Saturday, compares alternative scenarios, and quantifies penalty exposure. The analysis shows $6,000 in penalties without overtime versus $3,200 overtime cost plus $5,000 penalties with overtime, demonstrating $2,800 net savings. The ROI calculation (87.5%) and cost-benefit reasoning clearly justifies the overtime decision. The agent properly weighs overtime cost against penalty structure across customer tiers.

**schedule_construction:** The agent constructs a detailed, concrete schedule showing exactly which orders run in regular capacity (80 hours), Saturday overtime (8 hours), and what gets deferred. The schedule includes specific hour allocations per order, handling of split orders (PO-2203 and PO-2205), and proper sequencing by priority. The mathematical verification shows 80 + 8 = 88 hours available capacity accommodates the selected orders, with 9.6 hours properly deferred to resolve the overload.

**erp_process_awareness:** The agent demonstrates clear understanding of the MRP-to-production-order process, explicitly stating 'Convert priority orders PO-2207 through PO-2208 to production orders' while recommending to 'Hold PO-2209 as planned order.' The response recognizes that MRP generates planned orders that must be selectively converted to production orders based on capacity reality. The agent also addresses the need to communicate deferrals and reschedule deferred orders appropriately in the system.

---

### PSC-014: Shifting bottleneck detection and mid-week schedule adjustment

**Difficulty:** medium | **Category:** bottleneck-management | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| bottleneck_shift_diagnosis | 0.3 | pass | 1.0 |
| schedule_adjustment | 0.35 | pass | 1.0 |
| buffer_management | 0.2 | pass | 1.0 |
| prevention_and_monitoring | 0.15 | pass | 1.0 |

**bottleneck_shift_diagnosis:** The response correctly diagnoses a product-mix-driven bottleneck shift from aerospace-heavy (5-axis-intensive) to medical-device-heavy (EDM-intensive) work. It cites specific evidence: EDM utilisation jumped from 71% to 91% (+20 percentage points), 5-axis dropped from 93% to 78% (-15 percentage points), EDM WIP queue exploded from 3 to 18 parts (+500%), and 5-axis WIP dropped from 12 to 4 parts (-67%). The response also validates the shift with the correct constraint test: 'Adding 1 hour to EDM capacity would increase plant output; adding 1 hour to 5-axis would not.'

**schedule_adjustment:** The response correctly re-designates Wire EDM as the constraint for the remainder of the week, citing the 60% medical device mix. It proposes all key subordination actions: (1) slowing 5-axis release rate to match EDM's consumption rate (1.33 parts/hour), (2) establishing a 4-hour time buffer protecting the EDM, (3) optimizing EDM setup sequences to minimize changeover time, (4) continuing 5-axis at full rate on aerospace work that bypasses EDM, and (5) pre-staging materials and assigning the best EDM operator to eliminate delays.

**buffer_management:** The response correctly identifies buffer misalignment: 'Convert 5-axis buffer time to productive capacity for aerospace work' since it no longer needs constraint protection, and establishes proper EDM buffer zones (Green: 0-4 parts, Yellow: 5-8 parts, Red: >8 parts). It acknowledges the current 18-part queue is excessive and targets 6-8 parts maximum. The response also notes this is a temporary adjustment for the week's product mix, not a permanent change.

**prevention_and_monitoring:** The response recommends ongoing monitoring through established buffer zones with clear triggers for action (Green/Yellow/Red zones) and extends the frozen zone to 72 hours for the EDM queue to prevent schedule instability. It includes success metrics for monitoring: EDM utilisation >90%, queue reduction to 6-8 parts by Thursday, and system flow metrics. While it doesn't explicitly mention weekly product-mix analysis, it demonstrates awareness that constraint shifts require ongoing attention through the buffer management system.

---

### PSC-015: Quality hold impact on constraint feed — re-scheduling with rework

**Difficulty:** medium | **Category:** disruption-response | **Score:** 87.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| containment_and_rework_plan | 0.25 | pass | 1.0 |
| constraint_feed_plan | 0.3 | pass | 1.0 |
| delivery_assessment | 0.25 | partial | 0.5 |
| customer_communication | 0.2 | pass | 1.0 |

**containment_and_rework_plan:** Response immediately quarantines all 150 defective sub-frames across all three locations with proper segregation and documentation per AWS D1.1. Correctly prioritizes rework sequence: 20 painted units first (closest to constraint), then 40 at paint queue, then 90 at weld inspection. Accurately calculates rework capacity: 150 units × 45 min/unit = 112.5 hours, requiring 3.5 welders working full-time over 4 days, and plans appropriate resource scaling from 2 to 3 welders.

**constraint_feed_plan:** Identifies 50 good sub-frames available immediately for Tuesday assembly start. Maps detailed day-by-day constraint feed: Tuesday uses good stock (30 units), Wednesday adds 20 Priority 1 rework units, Thursday adds 40 Priority 2 units, continuing through Monday. Correctly sequences rework to maintain constraint feed without starvation, showing 1.67 days of buffer from good stock while rework mobilizes. Plans weekend overtime shifts to maintain constraint throughput.

**delivery_assessment:** Provides detailed day-by-day delivery calculation showing cumulative assembly progress: 30 (Tue) + 30 (Wed) + 30 (Thu) + 30 (Fri) + 30 (Sat OT) + 30 (Sun OT) + 20+ (Mon) = 200 delivered by Monday. However, this calculation is overly optimistic as it doesn't fully account for paint throughput delays for the reworked units and assumes perfect execution without any schedule slippage. A more realistic assessment would acknowledge higher delivery risk.

**customer_communication:** Recommends immediate customer notification (Monday 3:00 PM) with comprehensive communication including: (1) full disclosure of quality issue and quarantine actions, (2) commitment to AWS D1.1 compliance with certified welders, (3) assurance that delivery remains on track through weekend overtime, (4) daily progress updates, and (5) backup planning disclosure. Communication appropriately emphasizes structural safety as non-negotiable and provides direct contact for questions.

---

### PSC-016: Capacity planning — RCCP validation of MPS

**Difficulty:** medium | **Category:** capacity-planning | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| rccp_calculation | 0.4 | pass | 1.0 |
| overload_resolution | 0.35 | pass | 1.0 |
| communication_to_planning | 0.25 | pass | 1.0 |

**rccp_calculation:** The agent correctly calculates the weekly loads: W1 = 84.5 hrs (30+32+22.5), W2 = 90.0 hrs (35+28+27), W3 = 79.0 hrs (25+36+18), W4 = 94.0 hrs (40+24+30). All arithmetic is accurate. Correctly identifies available capacity as 76 hrs/week (accounting for maintenance window). Properly identifies overloaded weeks: W1 (8.5 hrs over, 111.2%), W2 (14.0 hrs over, 118.4%), W4 (18.0 hrs over, 123.7%). Correctly notes W3 is at 104.0% utilization but manageable. Calculations are within acceptable rounding tolerance.

**overload_resolution:** The agent proposes a comprehensive multi-lever resolution strategy: (1) Demand shifting - moves 6 Light Brackets from W2 to W3 (4.8 hrs) and 4 Heavy Frames from W4 to W5 (10.0 hrs), correctly recognizing W3's limited absorption capacity; (2) Saturday overtime authorization for 8 hrs/week to address remaining overloads; (3) Daily overtime for W2's residual 1.2 hours; (4) MPS revision as last resort with specific candidates (Light Brackets due to lower margin). The solution addresses the interaction between weeks and provides quantified impact of each action. Shows understanding that constraint capacity cannot be compromised.

**communication_to_planning:** The agent presents clear, actionable communication with specific quantified recommendations: identifies exact overload hours per week, proposes concrete actions (move 6 Light Brackets W2→W3, 4 Heavy Frames W4→W5), specifies overtime requirements and costs ($13,175 total), identifies escalation needs (Production Manager approval for OT, Sales coordination for customer negotiations), and provides implementation timeline. Uses concrete numbers throughout rather than vague statements. Includes cost-benefit analysis and justification for overtime authorization.

---

### PSC-017: Certified operator absence for regulated process with no backup

**Difficulty:** hard | **Category:** labour-scheduling | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| regulatory_compliance | 0.3 | pass | 1.0 |
| maria_callback_plan | 0.25 | pass | 1.0 |
| contingency_if_maria_unavailable | 0.25 | pass | 1.0 |
| systemic_risk_mitigation | 0.2 | pass | 1.0 |

**regulatory_compliance:** The response unequivocally states that no other night-shift operator can legally run the coating line under FDA regulations and that using R. Chen would be a GMP violation regardless of skill level. It explicitly says to 'stop the coating line' if Maria is unavailable and documents the decision for FDA compliance. The response correctly prioritizes regulatory compliance as non-negotiable and notes the potential FDA citation penalty of $15,000+.

**maria_callback_plan:** The response correctly calculates Maria's earliest return time: 3:30 PM + 8 hours = 11:30 PM (8-hour rest satisfied). It provides a detailed contact plan with a script explaining the situation, voluntary overtime at time-and-a-half rate, and notes that coating would finish by 5:30 AM Wednesday. The response correctly identifies this as voluntary overtime under the CBA and provides timeline for completion.

**contingency_if_maria_unavailable:** The response provides a clear contingency plan if Maria is unavailable: stop the coating line and re-sequence night shift work to other productive operations (tableting, granulation prep, packaging). It plans for Maria to run coating during her regular day shift (6:00 AM - 2:30 PM) with coating completing by 12:00 PM, quality testing by 2:00 PM, and packaging by 5:00 PM Wednesday - still meeting the Wednesday delivery commitment.

**systemic_risk_mitigation:** The response identifies this as a systemic single-point-of-failure risk and recommends specific actions: (1) cross-train 2 additional operators on tablet coating, (2) accelerate R. Chen's qualification from 2 weeks to 1 week, (3) review weekend/holiday coverage, and (4) submit a CAPA (Corrective and Preventive Action) request. It also recommends a broader operator matrix analysis for all FDA-regulated operations to identify similar vulnerabilities.

---

### PSC-018: Competing tier-1 rush orders with constraint capacity shortfall

**Difficulty:** hard | **Category:** job-sequencing | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| tradeoff_quantification | 0.3 | pass | 1.0 |
| capacity_recovery_options | 0.25 | pass | 1.0 |
| management_decision_framework | 0.25 | pass | 1.0 |
| execution_plan | 0.2 | pass | 1.0 |

**tradeoff_quantification:** The response provides comprehensive quantification of all scenarios with clear financial impact: Priority A first (B 5 days late, $8M contract at extreme risk), Priority B first (A 2 days late, $50K penalty), Split capacity (A 1 day late $25K penalty, B 3 days late high contract risk). The risk-adjusted analysis quantifies Customer B late delivery as 60% probability of $8M loss = $4.8M expected value at risk vs Customer A $50K penalty, showing 96× higher exposure. Presents clear decision matrix with costs and outcomes.

**capacity_recovery_options:** Identifies multiple recovery levers: (1) Saturday overtime 8 hours at $3,600, (2) Partial subcontracting of Customer B 3-axis operations for $1,880, (3) Hybrid approach combining both for $2,620. Calculates specific costs and shows how each option closes the 16-hour capacity gap. Technical assessment correctly identifies that 8 of 24 hours for Customer B can be subcontracted as 3-axis operations while complex geometries must remain internal.

**management_decision_framework:** Presents clear options matrix with three distinct paths: Overtime Only ($3,600, medium risk), Subcontract Only ($1,880, recommended), and Do Nothing (unacceptable extreme risk). Explicitly frames this as requiring 'Management Decision' with specific authorization checkboxes. Quantifies expected ROI of 2,553:1 return ratio for the $1,880 investment to protect $4.8M expected value. Makes recommendation but leaves final commercial decision to management.

**execution_plan:** Provides detailed implementation timeline from Monday 10:00 AM through Friday 2:00 PM with specific milestones, including subcontractor contact, material expediting, quality inspections, and shipping schedules. Includes risk mitigation with first-article inspection protocol, QA engineer assignment, and 4-hour schedule buffer. Sets clear decision deadline (Monday 2:00 PM) and provides specific customer communication scripts. Authorization requirements clearly specified with costs.

---

### PSC-019: Multi-disruption compound scenario — material + equipment + labour

**Difficulty:** hard | **Category:** disruption-response | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| compound_impact_assessment | 0.25 | pass | 1.0 |
| priority_triage | 0.3 | pass | 1.0 |
| multi_lever_recovery | 0.25 | pass | 1.0 |
| communication_and_timeline | 0.2 | pass | 1.0 |

**compound_impact_assessment:** The response correctly calculates the compounded capacity impact: Normal 80 hrs/week → 80% laser speed = 64 hrs base, then accounts for break coverage loss (16 hrs - 30 min breaks = 15.5 hrs/day) giving 12.4 hrs/day or 62 hrs/week effective capacity. Identifies 48 hours of steel-dependent work blocked until Friday, leaving only 24.8 hours available Wed-Thu for non-steel orders. Quantifies the total impact as '32% reduction from normal' and maps the precise timeline constraints.

**priority_triage:** The response systematically triages work orders into steel-dependent vs non-steel categories, then further segments the 8 urgent orders by material dependency. Establishes clear sequencing rules: 'Urgent orders due Thursday/Friday first' then 'shortest processing time first' within urgent categories. Allocates 100% of Wed-Thu capacity (24.8 hours) to urgent non-steel orders and establishes Friday priority sequence for steel-dependent orders by due date and margin.

**multi_lever_recovery:** Deploys multiple simultaneous recovery levers: (1) Cross-trained operator activation and night shift overtime for break coverage, (2) Extended shifts 6 AM-8 PM both Wed-Thu adding capacity, (3) Staggered micro-breaks to keep laser running continuously, (4) Weekend overtime authorization as backup, (5) Subcontracting assessment for high-risk steel orders, (6) Material pre-staging during downtime. Quantifies each lever's capacity contribution and combines them systematically.

**communication_and_timeline:** Provides detailed day-by-day timeline: Phase 1 Wed-Thu (24.8 hrs for urgent non-steel), Phase 2 Friday steel receipt and processing start, Phase 3 weekend decision point. Includes specific checkpoints (Wednesday 6 PM, Thursday 6 PM, Friday noon) with measurable targets. Drafts customer communications differentiating steel-dependent vs non-steel orders with specific messaging and timing ('before 10:00 AM'). Sets clear escalation triggers and resource authorization thresholds.

---

### PSC-020: New product introduction competing with peak production

**Difficulty:** hard | **Category:** capacity-planning | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| capacity_gap_analysis | 0.25 | pass | 1.0 |
| multi_lever_solution | 0.3 | pass | 1.0 |
| npi_trial_scheduling | 0.25 | pass | 1.0 |
| financial_business_case | 0.2 | pass | 1.0 |

**capacity_gap_analysis:** Agent correctly calculates base demand at 96% utilisation: 76.8 hrs/week × 6 weeks = 460.8 hours. Properly accounts for NPI trials as concentrated load (not averaged): 16 hrs × 3 trials = 48 hours initially, then risk-adjusts to 50 hours total (20+16+14). Presents week-by-week load profile showing trial weeks exceed 100% utilisation (110%, 105%, 103%) while non-trial weeks stay at 96%. Identifies the non-uniform gap correctly - trial weeks create significant spikes beyond the base 4.8 hr/week shortage.

**multi_lever_solution:** Implements comprehensive multi-lever approach: (1) Saturday overtime all 6 weeks = 48 hours capacity, (2) Changeover optimization via SMED = 18 hours recovered, (3) Break coverage optimization = 12 hours recovered. Total capacity increase: 78 hours vs. 47.2 hours needed after risk adjustment. Specifically addresses trial-week spikes by scheduling trials Friday PM/Saturday to contain overruns. Also identifies subcontracting contingency (MetalForm Industries) as backup lever. This demonstrates understanding that single-lever solutions are insufficient for this scenario.

**npi_trial_scheduling:** Schedules NPI trials strategically: Week 2, 4, 6 on Friday PM/Saturday to contain overruns without displacing Monday commitments. Risk-adjusts trial durations: Trial 1 = 20 hours (includes 8-hour contingency for first-time tooling), Trial 2 = 16 hours, Trial 3 = 14 hours. Explicitly notes that trials are unpredictable and builds overrun protection into the schedule structure. Does not displace any existing customer orders - trials run in overtime slots and weekend capacity.

**financial_business_case:** Presents complete financial justification: Investment = $22,900 (Saturday OT $20,400 + changeover optimization $2,500). Revenue at risk = $13.35M/year ($12M NPI + $1.35M existing customer increases). ROI calculation shows 58,300% return. Quantifies downside risk: $12.9M-$13.8M total exposure from contract loss and customer relationship damage. Cost-to-revenue ratio of 0.17% strongly supports approval. Includes subcontracting contingency cost ($8,500 for 30 hours) as backup option.

---

### PSC-021: Full plant re-schedule after constraint breakdown with customer prioritisation

**Difficulty:** hard | **Category:** disruption-response | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| customer_priority_triage | 0.25 | pass | 1.0 |
| financial_analysis | 0.25 | pass | 1.0 |
| non_constraint_scheduling | 0.2 | pass | 1.0 |
| communication_plan | 0.15 | pass | 1.0 |
| recovery_timeline | 0.15 | pass | 1.0 |

**customer_priority_triage:** The response correctly triages by penalty exposure: WO-1101 (AutoCorp, $50K/day penalty) gets highest priority with Allied subcontracting at $3,910; WO-1105 (Driveline, $15K/day) assigned to internal small CNC; WO-1108 (ElectraMotion, $8K/day) scheduled for main CNC restart Wednesday. The 5 remaining non-penalty jobs are appropriately scheduled for post-repair processing. The agent correctly identifies that only 4 of 12 jobs can run on the smaller CNC and uses subcontracting strategically for the highest-penalty work.

**financial_analysis:** Strong financial analysis throughout: WO-1101 subcontract cost of $3,910 vs $50K/day penalty avoidance; total recovery cost of $11,910 vs $123,000 penalty exposure avoided; clear ROI calculations showing 6:1 benefit-cost ratio. The response includes detailed cost breakdowns for Allied Machining ($195/hr), transport costs ($400), and compares subcontractor options (Allied vs Metro Precision) with cost-benefit rationale. Weekend overtime estimates and total program costs are quantified.

**non_constraint_scheduling:** Excellent non-constraint management: explicitly addresses the 16 non-CNC work orders continuing normal operations, pre-staging materials for constraint recovery, preventive maintenance during capacity surplus, cross-training operators from idled machining to assembly, and material preparation campaigns. The response recognizes downstream material shortages by Thursday and plans productive work reallocation. Plans for 15-minute constraint restart capability and addresses the full production pipeline.

**communication_plan:** Comprehensive communication plan with immediate customer notifications by Tuesday 4:00 PM, specific messaging for each penalty customer explaining recovery actions, daily check-ins with subcontractor, weekly status updates, and clear escalation procedures. Includes actual customer communication templates and establishes a cadence through recovery completion. Internal communication covers shift supervisors, quality team, and maintenance coordination.

**recovery_timeline:** Detailed day-by-day recovery plan: Tuesday 2:30 PM immediate actions and customer notifications; Wednesday-Friday subcontract execution and alternate routing; following Monday-Wednesday main CNC restart with WO-1108 as first job; complete timeline through full recovery. Includes specific daily checkpoints, success metrics, and contingency plans with probability assessments. Timeline accounts for Allied's 2-day lead time, 6-day main CNC repair, and post-repair ramp-up.

---

### PSC-022: Seasonal product transition with shared tooling and overlapping demand

**Difficulty:** hard | **Category:** capacity-planning | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| transition_phasing | 0.3 | pass | 1.0 |
| summer_completion_validation | 0.25 | pass | 1.0 |
| winter_ramp_validation | 0.25 | pass | 1.0 |
| resource_coordination | 0.2 | pass | 1.0 |

**transition_phasing:** The response designs a clear 4-phase transition plan: Phase 1 (Aug 1-18) all 6 machines on summer, Phase 2 (Aug 19-25) transitions machines #5,#6 to winter (4 summer + 2 winter), Phase 3 (Aug 26-Sep 1) transitions machines #3,#4 (2 summer + 4 winter), Phase 4 (Sep 2-15) transitions final machines #1,#2 to all winter. This is exactly the phased approach required rather than simultaneous transition. The plan shows reduced summer capacity during transition (3,200 → 2,133 → 1,067 units/day) and validates feasibility at each phase.

**summer_completion_validation:** The response provides clear mathematical validation: Phase 1 produces 57,600 units (18 days × 3,200/day), which exceeds the 45,000 remaining requirement and creates a 12,600 safety buffer. By end of Phase 3, total summer production reaches 73,600 units, which is 164% of the backlog requirement. The math is shown step-by-step and confirms summer orders can be completed with substantial margin.

**winter_ramp_validation:** The response calculates winter production systematically: Phase 2 produces 5,500 units (5 days × 1,100/day), Phase 3 produces 11,000 units (5 days × 2,200/day), Phase 4 produces 33,000 units (10 days × 3,300/day). Total winter inventory by Sep 15: 49,500 units, which exceeds the 25,000 requirement by 98%. The math is clearly shown and confirms the winter ramp-up target is achieved with substantial buffer.

**resource_coordination:** The response thoroughly addresses resource coordination: schedules mould changes on Friday afternoons with specific timeline (4:00 PM start, 9:00 PM completion), assigns both technicians to work in parallel on 2 machines simultaneously (reducing 10-hour sequential work to 5-hour parallel work), includes first-piece qualification protocol with dimensional and quality verification, and mentions pre-staging winter moulds and raw materials. The detailed mould change schedule table shows specific dates, downtime windows, and technician assignments.

---

### PSC-023: ERP data quality issue — routing times diverging from reality

**Difficulty:** medium | **Category:** erp-integration | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| root_cause_diagnosis | 0.3 | pass | 1.0 |
| routing_update_plan | 0.3 | pass | 1.0 |
| impact_quantification | 0.2 | pass | 1.0 |
| prevention_process | 0.2 | pass | 1.0 |

**root_cause_diagnosis:** The response correctly identifies ERP routing times lagging behind actual shop floor reality as the root cause. It cites the 52% setup time discrepancy (25 min vs 38 min actual) and 14% run time variance as primary drivers. The response connects multiple contributing factors: new product complexity driving setup variances, tooling degradation affecting cycle times, and loss of experienced setup technicians. It directly links the 23% total job time discrepancy to the schedule adherence drop, explaining how scheduling based on 3.5-hour jobs that actually take 4.3 hours systematically overpacks the schedule and creates the observed 14-percentage-point adherence decline.

**routing_update_plan:** The response provides a comprehensive structured routing update plan: (1) Immediate corrections using actual MES data (38 min setup, 4.8 min/piece run time), (2) Segmented correction by job complexity with specific time standards for simple/standard/complex jobs, (3) Differentiation by product family and material type rather than single averages, (4) Addition of setup-skill factors reflecting current workforce capabilities vs. retired experts, and (5) Implementation phases from emergency blanket updates to precision calibration. The plan directly uses the MES actual data rather than arbitrary percentage increases.

**impact_quantification:** The response quantifies the impact precisely: 23% time underestimate means scheduling 102 hours/week when actually needing 125 hours/week, creating a 23-hour capacity gap. It explains how every job overruns by an average of 48 minutes, causing cascading delays. The response connects this to the observed schedule adherence drop and quantifies lost constraint capacity at 23 hours/week. It also explains how overscheduling the constraint erodes downstream buffers and makes the system fragile to additional disruptions.

**prevention_process:** The response designs a comprehensive prevention process: (1) Weekly MES variance reporting with automated flagging of >15% deviations, (2) Monthly routing updates based on rolling 4-week actuals, (3) New Product Introduction protocol with provisional routing times and validation before standard scheduling, (4) Tool life integration linking wear to cycle time degradation, and (5) Engineering change control requiring routing validation. The process includes specific thresholds, responsibilities, and systematic monitoring to prevent future divergence.

---
