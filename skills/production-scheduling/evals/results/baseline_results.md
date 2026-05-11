# Eval Results: production-scheduling

**Mode:** Baseline (No Capability Context)  
**Version:** 1.0.0  
**Model:** claude-sonnet-4-20250514  
**Timestamp:** 2026-02-25T07:13:18Z  
**Aggregate Score:** 85.0%  
**Passed (>=70%):** 18/23

## Summary by Difficulty

| Difficulty | Avg Score | Count |
|---|---|---|
| Easy | 88.6% | 7 |
| Medium | 80.5% | 10 |
| Hard | 88.3% | 6 |

## Summary by Category

| Category | Avg Score | Count |
|---|---|---|
| bottleneck-management | 94.2% | 3 |
| capacity-planning | 65.8% | 3 |
| changeover-optimisation | 80.8% | 3 |
| disruption-response | 85.5% | 5 |
| erp-integration | 78.8% | 2 |
| job-sequencing | 86.9% | 4 |
| labour-scheduling | 100.0% | 2 |
| oee-analysis | 100.0% | 1 |

## Scenario Details

### PSC-001: Basic job priority sequencing with EDD rule

**Difficulty:** easy | **Category:** job-sequencing | **Score:** 55.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| dispatching_rule_selection | 0.3 | partial | 0.5 |
| capacity_calculation | 0.3 | fail | 0.0 |
| sequence_logic | 0.25 | pass | 1.0 |
| practical_judgment | 0.15 | pass | 1.0 |

**dispatching_rule_selection:** The agent uses a multi-criteria approach that includes due date urgency as the primary factor, which aligns with EDD logic. However, it doesn't explicitly state 'EDD' as the dispatching rule and adds unnecessary complexity with 'priority scores' and processing time considerations that muddy the clear EDD approach. The agent correctly identifies WO-3302 and WO-3304 as most urgent (both due 9/17) and uses customer tier as a tiebreaker, but the presentation lacks the clarity of a straightforward EDD implementation.

**capacity_calculation:** The agent makes a critical arithmetic error. It calculates changeover time as '5 jobs × 20 minutes = 100 minutes = 1.67 hours' when there are only 4 changeovers needed (between 5 jobs). The correct calculation should be 4 × 20 minutes = 80 minutes = 1.33 hours. This leads to an incorrect total time of 12.17 hours instead of the correct 11.83 hours. Additionally, the final day shift schedule shows 7.49 hours but doesn't clearly account for all changeovers in the detailed breakdown.

**sequence_logic:** The agent correctly sequences the due-9/17 jobs first (WO-3304 and WO-3302), followed by due-9/18 jobs, and defers the due-9/19 job (WO-3303) to evening shift. The logic properly prioritizes by due date and uses customer tier as a secondary consideration. The agent identifies that approximately 3 jobs can fit in the day shift and clearly specifies which jobs defer to evening shift.

**practical_judgment:** The agent demonstrates good practical judgment by noting that WO-3303 (Summit Drivetrain, Tier-1 customer) has the latest due date and can safely defer to evening shift while still receiving priority there. The response addresses what happens to deferred jobs, confirms evening shift has adequate capacity (4.66 hours), and provides a slight buffer (0.51 hours) for potential delays. The agent also mentions maintaining customer relationships and risk mitigation.

---

### PSC-002: OEE calculation and loss prioritisation at the constraint

**Difficulty:** easy | **Category:** oee-analysis | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| oee_calculation | 0.35 | pass | 1.0 |
| loss_identification | 0.3 | pass | 1.0 |
| improvement_recommendation | 0.2 | pass | 1.0 |
| contextual_awareness | 0.15 | pass | 1.0 |

**oee_calculation:** Agent correctly calculates all OEE components: Planned Production Time = 120 - 8 = 112 hrs, Availability = 98/112 = 87.5%, Performance = (7,200 × 45 seconds)/(98 × 3600) = 324,000/352,800 = 91.8%, Quality = 6,840/7,200 = 95.0%, and Overall OEE = 87.5% × 91.8% × 95.0% = 76.3%. All calculations are mathematically correct and within acceptable range.

**loss_identification:** Agent correctly identifies availability losses (unplanned downtime) as the largest loss category at 14 hours and quantifies the financial impact as $9,100 per week (14 hours × $650/hour). Also provides proper breakdown showing availability losses > performance losses > quality losses, with clear financial quantification for the constraint.

**improvement_recommendation:** Agent appropriately prioritizes reducing unplanned downtime as #1 priority, providing specific actionable recommendations including predictive maintenance, root cause analysis, operator training, and spare parts optimization. Correctly focuses on the availability loss as the primary constraint improvement opportunity with quantified ROI expectations.

**contextual_awareness:** Agent demonstrates strong contextual awareness by noting that 76.3% OEE is 'above world-class manufacturing threshold (75%)' and recognizes this is the constraint work centre. However, the world-class benchmark cited (75%) is lower than typical industry standards (85%+), but the agent correctly connects OEE improvement at the constraint to direct throughput impact with the $650/hour constraint value.

---

### PSC-003: Critical ratio calculation and job prioritisation

**Difficulty:** easy | **Category:** job-sequencing | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| critical_ratio_calculation | 0.4 | pass | 1.0 |
| priority_ranking | 0.3 | pass | 1.0 |
| escalation_judgment | 0.3 | pass | 1.0 |

**critical_ratio_calculation:** Agent correctly calculated all critical ratios: WO-5501 = 4/3.0 = 1.33, WO-5502 = 2/3.5 = 0.57, WO-5503 = 8/2.0 = 4.00, WO-5504 = 3/1.5 = 2.00. Date arithmetic is accurate (correctly counted days from Sep 22 to each due date) and formula application is correct (time remaining ÷ processing time needed). All values match expected calculations within acceptable tolerance.

**priority_ranking:** Agent correctly ranked jobs in ascending critical ratio order: WO-5502 (0.57) first, WO-5501 (1.33) second, WO-5504 (2.00) third, WO-5503 (4.00) last. Properly identified WO-5502 as 'CRITICAL' with CR < 1.0, indicating it's behind schedule. The prioritization table clearly shows understanding that lower CR = higher priority.

**escalation_judgment:** Agent correctly flagged WO-5502 for escalation, explicitly stating it's 'behind schedule' with CR of 0.57 and will be '1.5 days late without intervention.' Provided specific escalation recommendations including overtime scheduling, additional machine capacity, expediting, and customer communication. Also noted WO-5503 as 'Well Ahead' with CR of 4.0, demonstrating understanding of relative urgency levels.

---

### PSC-004: Simple changeover sequence optimisation on a paint line

**Difficulty:** easy | **Category:** changeover-optimisation | **Score:** 72.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| optimal_sequence | 0.4 | pass | 1.0 |
| worst_case_comparison | 0.25 | partial | 0.5 |
| setup_matrix_understanding | 0.2 | pass | 1.0 |
| practical_notes | 0.15 | fail | 0.0 |

**optimal_sequence:** The agent correctly identifies the optimal sequence as White → Yellow → Red → Blue → Black (B2→B4→B3→B5→B1), following the light-to-dark principle. Correctly calculates 4 transitions × 10 minutes = 40 minutes total changeover time and recognizes this minimizes changeover time by using only light-to-dark transitions.

**worst_case_comparison:** The agent attempts a worst-case comparison with sequence Black → White → Blue → Yellow → Red, calculating 115 minutes total. However, this is not actually the worst case - the true worst case would be the reverse light-to-dark sequence (Black → Blue → Red → Yellow → White) yielding 4 × 35 = 140 minutes. The agent's worst case includes one 10-minute transition, making it suboptimal as a comparison. The savings calculation is therefore understated.

**setup_matrix_understanding:** The agent demonstrates clear understanding of sequence-dependent changeovers, correctly identifying the light-to-dark (10 min) vs dark-to-light (35 min) asymmetry. Explicitly states the strategy to 'avoid dark to light transitions' and references the setup matrix structure throughout the analysis.

**practical_notes:** The agent does not acknowledge that this optimization only applies when due dates are equal, despite the scenario stating 'All batches have the same due date (end of day), so sequence is purely about minimising changeover time.' No mention is made of how different due dates would affect the sequencing decision or other practical scheduling considerations.

---

### PSC-005: Identifying the true constraint from WIP and utilisation data

**Difficulty:** easy | **Category:** bottleneck-management | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| constraint_identification | 0.35 | pass | 1.0 |
| wip_misconception_explanation | 0.3 | pass | 1.0 |
| constraint_management_recommendations | 0.35 | pass | 1.0 |

**constraint_identification:** Agent correctly identifies SMT Pick-and-Place as the true constraint, stating 'The SMT Pick-and-Place station is the actual bottleneck' and provides proper analysis showing it has the highest utilization at 92% and lowest capacity margin. The response includes a clear capacity analysis table showing utilization ratios and explains that utilization determines the constraint, not WIP queue size.

**wip_misconception_explanation:** Agent explains the WIP misconception well, stating the large queue 'creates a visual illusion of a bottleneck, but it's actually evidence of the opposite' and identifies 'Upstream constraint effect: SMT Pick-and-Place's high utilization creates irregular flow patterns' and 'Batching behavior: Large queues often form when upstream processes release work in batches.' The response correctly explains that the queue exists because Wave Soldering has excess capacity and receives work in batches from the upstream constraint.

**constraint_management_recommendations:** Agent provides TOC-based recommendations focused on exploiting the SMT constraint: 'Maximize SMT uptime' through predictive maintenance and cross-training, 'Optimize SMT efficiency' through cycle time reduction, and subordination through 'Implement pull system' to limit WIP. The response correctly notes that improving other stations won't increase plant output and prioritizes constraint-focused actions over general improvements.

---

### PSC-006: Forward and backward scheduling for a multi-operation work order

**Difficulty:** easy | **Category:** job-sequencing | **Score:** 92.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| forward_schedule | 0.3 | pass | 1.0 |
| backward_schedule | 0.3 | pass | 1.0 |
| float_assessment | 0.25 | pass | 1.0 |
| scheduling_awareness | 0.15 | partial | 0.5 |

**forward_schedule:** Agent correctly calculates forward schedule starting Monday Sept 22: Op 10 (6.5 hrs, Monday), Op 20 (2.0 hrs, Tuesday), Op 30 (5.0 hrs, Wednesday), Op 40 (1.5 hrs, Thursday). Total processing time of 15.0 hours is correct. Earliest completion date of Thursday Sept 25 falls within the acceptable range of Wed PM to Thu AM. Agent properly accounts for setup times in the total operation times.

**backward_schedule:** Agent performs backward scheduling correctly, working from Friday due date: Op 40 on Thursday, Op 30 on Wednesday, Op 20 on Tuesday, Op 10 on Monday. Latest start date identified as Monday Sept 22. The logic shows understanding that working backward from the due date determines the latest allowable start while still meeting the deadline.

**float_assessment:** Agent correctly identifies 1 day of float between earliest completion (Thursday Sept 25) and due date (Friday Sept 26). States 'Total Float: 1 day (Friday is available as buffer)' and notes this provides buffer for delays. Correctly assesses low risk due to adequate time buffer.

**scheduling_awareness:** Agent performs both forward and backward scheduling correctly but does not explain the practical differences between them. Missing discussion of how forward scheduling finds earliest completion while backward scheduling preserves flexibility and minimizes WIP. Does not recommend when to use each approach or mention that backward scheduling is typically preferred to avoid early WIP buildup.

---

### PSC-007: Labour skill matrix and shift coverage gap analysis

**Difficulty:** easy | **Category:** labour-scheduling | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| operator_assignment | 0.3 | pass | 1.0 |
| single_point_of_failure_identification | 0.4 | pass | 1.0 |
| cross_training_recommendation | 0.3 | pass | 1.0 |

**operator_assignment:** The response provides a complete and feasible assignment covering all 3 lines: Martinez to CNC Lathe, Jackson to Welding, and Kim to Surface Grinding. Correctly identifies that Patel should be kept as a float/relief operator rather than locked to a single line, leveraging his versatility with 3 certifications. The assignment respects all certification requirements and optimizes coverage.

**single_point_of_failure_identification:** Clearly identifies AWS-D1.1 (Welding) as the critical single-point-of-failure with only 2 certified operators (Jackson and Patel). Correctly notes this as 'HIGH' risk and explains that if both are unavailable, the Welding Station cannot operate. Appropriately contrasts this with CNC-L2 and GRND-1 which both have 3 operators and are marked as having 'Good coverage'.

**cross_training_recommendation:** Prioritizes cross-training Martinez in AWS-D1.1 as 'Priority 1: Immediate (Within 30 days)' to address the welding single-point-of-failure. Provides sound reasoning that Martinez already has precision work skills from CNC-L2 certification. Quantifies the risk impact by noting that training Martinez would create 3-person coverage for welding, eliminating the single-point-of-failure.

---

### PSC-008: Drum-buffer-rope implementation for a new constraint

**Difficulty:** medium | **Category:** bottleneck-management | **Score:** 90.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| drum_identification_and_exploitation | 0.3 | pass | 1.0 |
| buffer_design | 0.3 | pass | 1.0 |
| rope_mechanism | 0.2 | pass | 1.0 |
| subordination_logic | 0.2 | partial | 0.5 |

**drum_identification_and_exploitation:** Correctly identifies TMC-01 as the drum constraint running at 94% utilization. Provides specific exploitation actions including SMED implementation to reduce changeovers from 25 to 20 minutes (saving 15 min/day = 1.25 extra parts/day), cross-training operators, pre-staging tooling, implementing upstream quality checks, and moving non-critical parts to underutilized CNC machines (72% utilized). Quantifies the impact correctly, understanding that at current cycle times, reducing changeover time directly translates to additional throughput.

**buffer_design:** Sets an 18-hour time buffer based on the 12-hour upstream lead time plus variability protection (2 hours for heat treatment variance) and Murphy protection (4 hours), which is reasonable given moderate upstream reliability. Defines three monitoring zones: Green (0-15 parts consumed), Yellow (16-30 parts), Red (31-45 parts) with specific monitoring frequencies and escalation actions for each zone. The 45-part inventory buffer calculation (18 hours × 2.5 parts/hour) is mathematically sound.

**rope_mechanism:** Defines a clear material release mechanism at the sawing department based on drum schedule plus buffer replenishment needs. Specifies daily release calculation as '40 + (45 - current buffer inventory)' which prevents overproduction. Establishes communication system with priority levels and work order priorities tied to buffer zones. This properly controls WIP flow and prevents upstream work centers from producing beyond constraint consumption rate.

**subordination_logic:** Mentions that upstream work centers should respond to rope signals and notes the utilization levels of non-constraint work centers (heat treatment 60%, finishing 68%, inspection 55%). However, does not explicitly state that these work centers should NOT be scheduled for maximum utilization or clearly explain subordination principles. While the buffer and rope mechanisms implicitly create subordination, the response lacks explicit discussion of subordinating non-constraint schedules to serve the drum's needs.

---

### PSC-009: SMED changeover reduction analysis

**Difficulty:** medium | **Category:** changeover-optimisation | **Score:** 70.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| smed_classification | 0.25 | pass | 1.0 |
| phase_1_2_improvements | 0.3 | fail | 0.0 |
| financial_impact | 0.25 | pass | 1.0 |
| implementation_awareness | 0.2 | pass | 1.0 |

**smed_classification:** Agent correctly identifies 'search for die' (8 min) and 'transport die' (6 min) as external activities currently done during machine stoppage. Properly classifies all internal activities including bolt removal/insertion (12 min each), crane lift (5 min), positioning (5 min), adjustments (7 min + 6 min), and trial runs (4 min). Correctly calculates 14 minutes external-done-internal and 54 minutes true internal time.

**phase_1_2_improvements:** While Phase 1 correctly addresses moving die search/transport external (14 min savings), Phase 2 proposes unrealistic improvements. Claims total reduction to 8 minutes final changeover time, which would require eliminating crane lift (5 min) and trial runs (4 min) - both impossible to eliminate. The 'quick fasteners' reducing 24 minutes of bolt work to 6 minutes total is mathematically impossible given the other remaining activities. A realistic SMED Phase 2 should achieve 18-28 minutes total, not 8 minutes.

**financial_impact:** Correctly calculates current cost: 4 changeovers × 68 min = 272 min/day × $720/hour = $3,264/day. Future cost calculation uses unrealistic 8-minute changeover but methodology is correct: 4 × 8 min = 32 min/day × $720/hour = $384/day. Savings calculation of $2,880/day and $720,000 annually follows logically from the (overstated) time reduction. Financial framework and constraint throughput value application is expert-level.

**implementation_awareness:** Properly phases implementation with Phase 1 as immediate quick wins (tool crib organization, pre-staging, cleaning checklists) and Phase 2 requiring capital investment. Provides specific investment estimates ($28,000 total) and calculates ROI (25.7x). Recognizes different implementation timelines and resource requirements between phases. Shows practical understanding of change management in manufacturing.

---

### PSC-010: Disruption response — machine breakdown at the constraint

**Difficulty:** medium | **Category:** disruption-response | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| in_machine_part_assessment | 0.2 | pass | 1.0 |
| alternate_routing_analysis | 0.25 | pass | 1.0 |
| priority_sequencing | 0.25 | pass | 1.0 |
| recovery_plan_completeness | 0.3 | pass | 1.0 |

**in_machine_part_assessment:** The response addresses the $42K part comprehensively: identifies it's 80% complete (8/10 hours), calculates $42K value with high-priority defense customer, explicitly decides to 'SALVAGE THE PART' with rationale citing high value and near completion, recommends working with maintenance for careful extraction, and prioritizes completion when HBM-01 is operational. Shows awareness of sunk cost implications.

**alternate_routing_analysis:** Correctly identifies VMC-02 capacity (65% utilized, 35% available = 10.4 hrs/day), systematically lists all 6 jobs that can transfer based on 500mm size limit (WO-8802 through WO-8809), correctly identifies the 2 oversized jobs that cannot transfer (WO-8803 at 650mm and WO-8805 at 800mm), and totals 18 hours of transferable work. Shows proper dimensional analysis against machine constraints.

**priority_sequencing:** Sequences correctly by due date and customer tier: WO-8802 (Tier 1, due Sept 25) gets immediate priority on VMC-02, WO-8805 (Nexus Defense, Tier 1) and WO-8803 (Summit Aero) are prioritized when HBM restarts based on due dates and customer tier. Shows clear understanding of constraint recovery sequencing with defense contracts getting appropriate priority treatment.

**recovery_plan_completeness:** Provides comprehensive recovery plan covering all required elements: (1) immediate actions with maintenance mobilization and part extraction, (2) complete alternate routing analysis, (3) detailed priority sequence for HBM restart, (4) customer notification plan identifying specific delays and communication timeline (within 4 hours), (5) overtime assessment for Friday completion, (6) subcontracting evaluation for oversized parts with defense contract restrictions noted, and (7) contingency planning for repair extending beyond 16 hours.

---

### PSC-011: Campaign scheduling vs. mixed-model decision with cost analysis

**Difficulty:** medium | **Category:** changeover-optimisation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| changeover_cost_analysis | 0.25 | pass | 1.0 |
| campaign_schedule_design | 0.3 | pass | 1.0 |
| inventory_cost_tradeoff | 0.25 | pass | 1.0 |
| recommendation_quality | 0.2 | pass | 1.0 |

**changeover_cost_analysis:** Agent correctly calculates current mixed-model changeover cost: 6 changes × 45 min = 270 minutes (4.5 hours) daily. Applies constraint throughput value at $850/hour to get $3,825/day or $84,150/month. Correctly identifies this as lost constraint capacity representing 28% of available time (4.5/16 hours). Shows understanding that changeover time directly translates to throughput loss at the constraint.

**campaign_schedule_design:** Agent designs a logical 6-day campaign cycle respecting customer delivery frequencies. Correctly identifies that AutoCo's weekly JIT requirement prevents pure weekly campaigns, proposing Black runs on specific days. Groups colors by production volume and delivery requirements. Calculates realistic batch sizes based on demand proportions. Reduces changeovers from 30/week to 7/week in hybrid approach while maintaining delivery commitments.

**inventory_cost_tradeoff:** Agent calculates additional inventory carrying costs for campaign approach: uses average inventory = batch size ÷ 2 formula, applies $0.12/part/week carrying cost rate. Totals monthly increase at $4,458 for pure campaigns, $2,229 for hybrid. Compares inventory cost increase against changeover savings ($72,509 pure campaign, $54,400 hybrid) to determine net benefit. Shows clear understanding of campaign vs. carrying cost tradeoff.

**recommendation_quality:** Recommends well-reasoned hybrid approach: AutoCo runs twice weekly for JIT compatibility, other customers run weekly campaigns. Quantifies net savings of $52,171/month. Acknowledges that pure campaign approach would violate AutoCo's JIT requirement despite higher theoretical savings. Provides clear rationale balancing changeover reduction (65%) with delivery requirements and inventory costs. Decision shows operational judgment prioritizing largest customer's constraints.

---

### PSC-012: Material shortage response with partial-build strategy

**Difficulty:** medium | **Category:** disruption-response | **Score:** 90.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| allocation_logic | 0.3 | pass | 1.0 |
| partial_build_strategy | 0.3 | pass | 1.0 |
| schedule_re_sequencing | 0.2 | pass | 1.0 |
| root_cause_and_prevention | 0.2 | partial | 0.5 |

**allocation_logic:** The response correctly allocates the 340 available units by priority: WO-9001 gets 120 units (Tier 1 customer, due Thursday), WO-9002 gets 200 units (Tier 2 customer, due Friday), leaving 20 units as a buffer. The allocation is explicitly justified by customer tier and due date urgency. The agent recognizes that WO-9003 and WO-9004 must wait for Friday delivery.

**partial_build_strategy:** The response explicitly proposes partial-build strategies: 'Begin Steps 1, 4, and 5 preparation for all work orders' and 'Complete DIN rail mounting and PLC prep while waiting for terminal blocks.' The agent identifies which assembly steps can proceed without TB-4420 (Steps 1, 4, 5) and plans to insert Step 2 (terminal block installation) after Friday delivery. This keeps the assembly line productive while preserving lead time.

**schedule_re_sequencing:** The response provides a detailed re-sequenced timeline showing WO-9001 and WO-9002 proceeding normally with available material, while WO-9003 and WO-9004 begin partial builds immediately. After Friday delivery, WO-9003 completes first (due Monday), then WO-9004 (due Wednesday). The modified production sequence is clearly laid out day-by-day from Tuesday through Wednesday.

**root_cause_and_prevention:** The response identifies phantom inventory as the root cause ('likely a receiving error or a posting failure') and includes 'Immediate cycle count of related components to prevent cascade shortages' in contingencies. However, it doesn't provide the comprehensive prevention measures expected: investigation of the specific receiving/posting error, corrective actions to prevent recurrence, or recognition that phantom inventory disables MRP planning accuracy. The root cause identification is present but prevention planning is incomplete.

---

### PSC-013: ERP work order management — MRP overload resolution

**Difficulty:** medium | **Category:** erp-integration | **Score:** 57.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| overload_resolution_strategy | 0.3 | partial | 0.5 |
| financial_analysis | 0.3 | pass | 1.0 |
| schedule_construction | 0.25 | partial | 0.5 |
| erp_process_awareness | 0.15 | fail | 0.0 |

**overload_resolution_strategy:** The agent correctly identifies the 17.6-hour overload (97.6 - 80 = 17.6) and proposes using 8 hours of Saturday overtime to reduce it to 9.6 hours remaining. However, the final recommendation defers only 6 hours (Cover E) instead of the required 9.6 hours, leaving the overload unresolved. The agent also schedules PO-2207 (Pin G, Tier 4) in regular time when it should be deferred as a zero-penalty order. While the prioritization logic is sound and protects Tier 1 orders, the mathematical execution fails to fully resolve the capacity constraint.

**financial_analysis:** The agent performs a thorough financial analysis, calculating overtime cost at $3,200 for Saturday and correctly identifying that deferred orders (Shaft C and Cover E) have $0 penalties. The analysis compares overtime cost against penalty avoidance and concludes that overtime is justified for customer service and relationship preservation. The agent also presents an alternative scenario without overtime, showing $0 penalty exposure, demonstrating understanding of the financial trade-offs involved in the decision.

**schedule_construction:** The agent constructs a detailed schedule with specific order assignments to regular time (79.6 hours) and overtime (8 hours), showing clear prioritization by customer tier and penalty structure. However, the schedule has a critical flaw: it only defers 10 hours total (4 hours remaining of Shaft C + 6 hours of Cover E) when 9.6 hours need to be deferred after overtime, and fails to account for keeping Pin G (4 hours, Tier 4) which should be deferred instead of higher-priority work. The format and approach are correct but the execution doesn't match the capacity constraint.

**erp_process_awareness:** The response does not address the MRP-to-production-order conversion process, which is central to the scenario. The agent doesn't mention that planned orders must be converted to production orders before release to the shop floor, nor does it discuss holding deferred orders as planned orders with revised due dates or communicating changes back to the planning system for the next MRP run. This is a significant omission for production scheduling domain expertise.

---

### PSC-014: Shifting bottleneck detection and mid-week schedule adjustment

**Difficulty:** medium | **Category:** bottleneck-management | **Score:** 92.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| bottleneck_shift_diagnosis | 0.3 | pass | 1.0 |
| schedule_adjustment | 0.35 | pass | 1.0 |
| buffer_management | 0.2 | pass | 1.0 |
| prevention_and_monitoring | 0.15 | partial | 0.5 |

**bottleneck_shift_diagnosis:** Correctly diagnoses the constraint shift from 5-axis CNC (93% to 78% utilization) to Wire EDM (91% utilization). Identifies product mix shift from aerospace-heavy to medical device work as the root cause. Cites specific WIP evidence: EDM queue grew from 3 to 18 parts (600% increase) while 5-axis queue dropped to 4 parts. Clearly states 'Clear constraint shift detected' and provides the utilization crossover data.

**schedule_adjustment:** Recommends re-designating Wire EDM as the drum for remainder of week based on 60% medical device mix. Proposes key schedule adjustments: (1) reschedule EDM as drum with due-date sequencing, (2) release work based on EDM capacity not 5-axis, (3) rebalance work release to normalize EDM queue from 18 to 8-10 parts, (4) optimize EDM setup sequences by grouping similar geometries, (5) subordinate 5-axis (now has 22% spare capacity) to support EDM flow.

**buffer_management:** Addresses buffer realignment comprehensively. Notes constraint buffer is excessive at 13.5 hours (18 parts × 45 min) and recommends reducing to 3-4 hours of work ahead of EDM. Proposes extending shipping buffer/lead times for new medical device orders since EDM is now constraint. Recommends temporarily reducing WIP releases to prevent further EDM queue buildup. Recognizes 5-axis now has capacity buffer (22% spare) to absorb variation.

**prevention_and_monitoring:** Provides success metrics to track (EDM WIP trending to 8-10 parts, utilization stabilizing at 85-88%) and notes this constraint shift is temporary. However, does not explicitly recommend daily utilization monitoring to detect future shifts early, nor does it suggest building weekly schedules with product-mix-aware constraint identification for different days/shifts based on varying mix.

---

### PSC-015: Quality hold impact on constraint feed — re-scheduling with rework

**Difficulty:** medium | **Category:** disruption-response | **Score:** 60.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| containment_and_rework_plan | 0.25 | partial | 0.5 |
| constraint_feed_plan | 0.3 | partial | 0.5 |
| delivery_assessment | 0.25 | partial | 0.5 |
| customer_communication | 0.2 | pass | 1.0 |

**containment_and_rework_plan:** The response correctly quarantines all 150 units across three stages and prioritizes rework by proximity to constraint (painted units first, then paint queue, then inspection queue). However, it significantly underestimates rework time - claims 2 welders can complete 20 units/day, which would be 24 minutes per unit, far below the realistic 45 min/unit. The actual calculation should be 150 units × 45 min = 112.5 hours ÷ 2 welders = 56 hours = 3.5 shifts, not the 20 units/day claimed.

**constraint_feed_plan:** The response identifies 50 good units available immediately and attempts day-by-day constraint feeding. However, the feed calculations are based on incorrect rework timing assumptions. Claims 10 units completed Monday PM and 20 units/day thereafter, but with realistic 45 min/unit rework time, Monday would yield ~6 units maximum. The constraint feed timeline is overly optimistic due to underestimated rework duration.

**delivery_assessment:** The response calculates a realistic partial delivery of 140 units (70% of order) and acknowledges the 60-unit shortfall. However, this assessment is based on the flawed rework capacity assumptions. With correct rework timing (45 min/unit), the deliverable quantity by Monday would be lower - approximately 120-130 units. The approach of quantifying shortfall and proposing partial delivery is correct, but the specific numbers are optimistic.

**customer_communication:** Excellent customer communication strategy. Recommends immediate notification (Monday 4:00 PM) with clear explanation of quality issue, revised delivery timeline (140 units Monday, 60 units Wednesday), mitigation actions, and proactive conference call offer. Appropriately emphasizes quality compliance with AWS D1.1 standards and offers follow-up actions including root cause analysis and relationship preservation measures.

---

### PSC-016: Capacity planning — RCCP validation of MPS

**Difficulty:** medium | **Category:** capacity-planning | **Score:** 45.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| rccp_calculation | 0.4 | partial | 0.5 |
| overload_resolution | 0.35 | fail | 0.0 |
| communication_to_planning | 0.25 | pass | 1.0 |

**rccp_calculation:** The agent correctly calculates the load requirements for all weeks: W1=84.5 hrs, W2=90 hrs, W3=79 hrs, W4=94 hrs, and properly uses the 76 hrs/week available capacity. However, the agent incorrectly identifies Week 3 as overloaded when it requires 79 hrs against 76 hrs capacity (3 hrs over, 104%), which is marginal and could be considered within normal capacity variation. The pass criterion specifically notes that W3 'is within capacity' and 'slightly over but manageable' - the agent should have recognized this nuance rather than flagging it as a full overload requiring intervention.

**overload_resolution:** The agent proposes three resolution options but fails to understand the capacity constraints properly. In Option 2 (Demand Shifting), the agent proposes moving work TO Week 3, which only has ~0 hours of headroom (79 hrs required vs 76 available). The proposed shifts would actually worsen Week 3's position (moving it to 87 hrs, severely overloaded). The agent doesn't recognize that Week 3 cannot absorb significant additional load. The resolution proposals show a fundamental misunderstanding of the capacity-constrained system and would create worse overloads rather than solving them.

**communication_to_planning:** The agent provides excellent communication with specific quantified recommendations: concrete overtime hours needed for each week (8.5, 14.0, 3.0, 18.0 hrs), specific product shift quantities (2 Heavy Frames, 3 Light Brackets, 2 Precision Shafts), and clear action items with risk assessments. The response includes a structured recommendation prioritizing Option 2 with rationale, timeline for implementation, and identifies Week 4 as highest risk. The communication is professional, quantified, and actionable for the planning team.

---

### PSC-017: Certified operator absence for regulated process with no backup

**Difficulty:** hard | **Category:** labour-scheduling | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| regulatory_compliance | 0.3 | pass | 1.0 |
| maria_callback_plan | 0.25 | pass | 1.0 |
| contingency_if_maria_unavailable | 0.25 | pass | 1.0 |
| systemic_risk_mitigation | 0.2 | pass | 1.0 |

**regulatory_compliance:** The response unequivocally states FDA compliance requirements, explicitly noting that only Maria Santos can operate the coating line due to documented qualification requirements under 21 CFR Part 211. It clearly marks as 'PROHIBITED' using R. Chen (in training) or other unqualified operators for coating operations, treating certification as a hard constraint rather than a preference. The response demonstrates understanding that regulatory compliance cannot be compromised.

**maria_callback_plan:** The response correctly calculates Maria's earliest return time: her shift ended at 3:30 PM, plus 8-hour rest requirement = 11:30 PM availability. It plans to contact Maria immediately at 10:45 PM to request voluntary overtime, offers premium overtime rate plus shift differential as incentives, and calculates that 6 hours of coating work starting at 11:30 PM would complete by 5:30 AM Wednesday morning, meeting the shipment timeline. The voluntary nature under CBA is explicitly acknowledged.

**contingency_if_maria_unavailable:** The response provides a clear contingency plan if Maria declines: wait for day shift Wednesday morning with Maria starting at 7:00 AM, completing coating by 1:00 PM Wednesday. It acknowledges this creates potential shipment delay risk and includes customer communication requirements. The plan includes preparing MedSupply Corp notification if delay is likely and maintains material protection protocols during the delay.

**systemic_risk_mitigation:** The response identifies this as a systemic single-point-of-failure risk and provides comprehensive long-term solutions including: accelerating R. Chen's coating certification, establishing minimum 2 certified operators per shift, implementing on-call systems, cross-training additional operators, conducting process risk assessment to audit all critical operations, and developing a training matrix for adequate shift coverage. It addresses both immediate and strategic risk reduction with specific timelines (30-60 days for full qualification).

---

### PSC-018: Competing tier-1 rush orders with constraint capacity shortfall

**Difficulty:** hard | **Category:** job-sequencing | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| tradeoff_quantification | 0.3 | pass | 1.0 |
| capacity_recovery_options | 0.25 | pass | 1.0 |
| management_decision_framework | 0.25 | pass | 1.0 |
| execution_plan | 0.2 | pass | 1.0 |

**tradeoff_quantification:** The response provides clear quantification of all key scenarios: Option 1 (Customer A first) shows avoiding $25k penalty but risking $8M contract; Option 2 (Customer B first) shows $25k penalty cost vs preserving $8M opportunity; Option 3 (mixed strategy) quantifies specific costs of $3,600 overtime + $1,960 subcontracting = $5,560 total. The financial summary clearly states 'Risk Avoided: $8M+ annual revenue + $25k penalty = $8.025M' with ROI calculation of 1,443:1. This meets the pass criteria for presenting scenarios as a clear decision matrix with quantified impacts.

**capacity_recovery_options:** The response identifies multiple capacity recovery levers: (1) Saturday overtime adding 8 hours at $3,600 cost; (2) subcontracting 8 hours of bracket operations at $185/hr = $1,480; (3) first-article inspection cost of $480. The plan shows total gap of 16 hours being addressed through 8 hours overtime + 8 hours subcontracting to close the full capacity shortfall. Total recovery cost is calculated as $5,560, which aligns with the pass criteria requirement of ~$5,000-$6,000 range and identifying multiple levers that enable both orders to ship on time.

**management_decision_framework:** The response presents clear options to management with recommendations: 'Option 3: Recommended Mixed Strategy' with specific costs and outcomes, contrasted against Option 1 (A priority with $8M+ relationship risk) and Option 2 (B priority with $25k penalty). The executive summary states 'both orders can be delivered on time' and positions this as requiring management approval ('Recommendation: Approve mixed strategy immediately'). The commercial context is clear with the $8M contract evaluation period and $25k/day penalties, making it explicit this is a commercial decision requiring management input.

**execution_plan:** The response provides a detailed execution timeline: 'Monday-Tuesday: Start Customer A (valve bodies) - 40 hours; Wednesday-Thursday: Customer B remaining operations - 16 hours; Parallel: Subcontractor handles 8 hours bracket prep work.' It includes specific quality plans (mandatory first-article inspection, 48-hour quality hold), communication plans ('proactive communication to both customers Monday AM'), and contingency plans ('If subcontractor quality fails: Saturday overtime + customer communication'). The delivery schedule commits to specific dates (Customer A Thursday, Customer B Friday) with concrete responsibilities outlined.

---

### PSC-019: Multi-disruption compound scenario — material + equipment + labour

**Difficulty:** hard | **Category:** disruption-response | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| compound_impact_assessment | 0.25 | pass | 1.0 |
| priority_triage | 0.3 | pass | 1.0 |
| multi_lever_recovery | 0.25 | pass | 1.0 |
| communication_and_timeline | 0.2 | pass | 1.0 |

**compound_impact_assessment:** The response correctly calculates the compounded capacity impact: starts with 80 hours normal weekly capacity, reduces to 64 hours due to 80% laser speed, then subtracts 12.5 hours weekly for break coverage gaps, arriving at 51.5 hours effective capacity (36% reduction). The response identifies that 6 of the 8 urgent work orders are material-blocked until Friday, leaving only 2-3 urgent orders that can proceed immediately. The calculation methodology and timeline mapping are accurate and demonstrate understanding of how multiple disruptions compound rather than add linearly.

**priority_triage:** The response clearly triages the 8 urgent work orders into three tiers: Tier 1 (4-5 critical orders NOT requiring problematic steel for immediate processing), Tier 2 (3-4 urgent orders requiring steel delivery, queued for Friday), and Tier 3 (remaining 14 standard orders). The response identifies which orders are material-blocked versus immediately processable, sequences by delivery requirements, and mentions the need for early customer notification for potentially impacted deliveries. This demonstrates proper prioritization logic.

**multi_lever_recovery:** The response deploys multiple simultaneous recovery levers: (1) Contact off-shift operators for overtime coverage, (2) Implement staggered 10-minute breaks to minimize downtime, (3) Cross-train maintenance staff as emergency operators, (4) Weekend overtime potential, (5) Subcontracting backup plan quantified at $8,000, (6) Expedited steel delivery attempt, and (7) Alternative alloy substitution review. The response quantifies the break coverage recovery (12.5 hours weekly) and provides specific recovery targets and resource requirements, showing comprehensive multi-lever thinking.

**communication_and_timeline:** The response provides a detailed day-by-day recovery timeline: Wed-Thu (Days 1-2) process Tier 1 non-steel orders at 10.3 hours/day capacity targeting 20-25 hours completion; Friday-Monday (Days 3-6) steel arrives Friday AM and remaining urgent orders processed; Tuesday+ full capacity restored with 10-day total recovery. Customer communication is scheduled for 9:00 AM Wednesday with specific deliverables (partial shipments, updated delivery dates). The timeline includes specific checkpoints and re-planning triggers.

---

### PSC-020: New product introduction competing with peak production

**Difficulty:** hard | **Category:** capacity-planning | **Score:** 62.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| capacity_gap_analysis | 0.25 | fail | 0.0 |
| multi_lever_solution | 0.3 | pass | 1.0 |
| npi_trial_scheduling | 0.25 | partial | 0.5 |
| financial_business_case | 0.2 | pass | 1.0 |

**capacity_gap_analysis:** The response incorrectly averages NPI load (48 hours ÷ 6 weeks = 8 hours/week) rather than recognizing that trials occur in specific weeks requiring 16 hours each. Also miscalculates base demand as 461 hours total vs. correct weekly analysis of 96% × 80 = 76.8 hrs/week. The uniform averaging masks the critical trial-week capacity spikes that drive the real scheduling challenge.

**multi_lever_solution:** Proposes comprehensive multi-lever approach: Saturday overtime (+8 hrs/week), changeover reduction (+3 hrs/week), and break coverage optimization (+2 hrs/week) totaling 78 additional hours. The combination addresses both base gap and trial week spikes. Numbers are reasonable for each lever and shows understanding that multiple capacity sources are needed.

**npi_trial_scheduling:** Schedules trials with 2-week spacing in weeks 2, 4, and 6 with logical rationale (avoid Mondays/Fridays). However, schedules trials mid-week (Wednesday-Thursday, Tuesday-Wednesday) rather than Friday PM/Saturday to contain overruns. Does include 4-hour buffer per trial but doesn't fully isolate trial risk from regular production flow.

**financial_business_case:** Builds strong financial case with overtime cost calculation ($20,400), total investment ($25,400), and compares to protected value ($12M NPI + $9M existing). Calculates compelling ROI (>1,900% Year 1) and quantifies cost of inaction. Correctly positions the $25K investment against $21M revenue at risk and recommends approval with clear business justification.

---

### PSC-021: Full plant re-schedule after constraint breakdown with customer prioritisation

**Difficulty:** hard | **Category:** disruption-response | **Score:** 77.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| customer_priority_triage | 0.25 | partial | 0.5 |
| financial_analysis | 0.25 | pass | 1.0 |
| non_constraint_scheduling | 0.2 | partial | 0.5 |
| communication_plan | 0.15 | pass | 1.0 |
| recovery_timeline | 0.15 | pass | 1.0 |

**customer_priority_triage:** The response correctly identifies the three customers with penalties and attempts prioritization, but makes significant errors. It correctly identifies AutoCorp Prime as highest priority ($150K total penalty risk vs $50K/day specified in rubric), but the job allocation is flawed. The response doesn't clearly verify which of the 12 constraint jobs can run on the alternate CNC (claims 4 compatible but doesn't specify which ones). The subcontracting decisions are directionally correct but lack the specific technical requirements analysis (AS9100 certification mentioned correctly for Allied). The prioritization logic is sound but execution details are incomplete.

**financial_analysis:** The response provides comprehensive financial analysis including: subcontracting costs ($3,300 total), penalty avoidance calculations ($130,000 saved), overtime costs ($8,400), and net savings calculation ($68,200). It correctly shows ROI justification for subcontracting decisions and presents a clear cost-benefit analysis with penalty exposure vs subcontracting costs. The financial framework demonstrates understanding that $3,300 in subcontracting costs to avoid $130,000 in penalties is an overwhelming ROI, which aligns with expert-level financial quantification.

**non_constraint_scheduling:** The response addresses non-constraint work in the 'Non-Constraint Work Scheduling' section, mentioning advancing operations for all 28 work orders and inventory preparation for constraint restart. However, it lacks specific detail about the 16 non-CNC-dependent work orders continuing on regular schedules, and doesn't explicitly address pre-staging CNC jobs with material kitting, programs loaded, and tooling ready. The concept of keeping downstream operations fed and pipeline preparation is present but not fully developed with operational specifics.

**communication_plan:** The response provides a detailed communication strategy with specific timelines: immediate calls to Priority 1 customer (AutoCorp Prime), contact within 2 hours for Priority 2 (Driveline Partners), and by end of day for Priority 3 (ElectraMotion). It includes transparent disclosure approach, goodwill gestures, and establishes daily progress updates to affected customers. The plan covers both external customer communication and internal communications (hourly updates to executive team). The 4-hour notification timeline requirement is met.

**recovery_timeline:** The response provides a comprehensive day-by-day recovery timeline in the 'Implementation Timeline' section: Tuesday 2-6 PM immediate actions, Wednesday-Friday subcontracted work and alternate CNC operations, weekend overtime shifts, Monday-Tuesday preparation activities, and Wednesday main CNC restart with AutoCorp Prime job initiation. The timeline shows clear progression from crisis response through recovery to normalization, with specific milestones and activities mapped to each phase.

---

### PSC-022: Seasonal product transition with shared tooling and overlapping demand

**Difficulty:** hard | **Category:** capacity-planning | **Score:** 90.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| transition_phasing | 0.3 | pass | 1.0 |
| summer_completion_validation | 0.25 | pass | 1.0 |
| winter_ramp_validation | 0.25 | pass | 1.0 |
| resource_coordination | 0.2 | partial | 0.5 |

**transition_phasing:** Agent designs a clear phased transition plan with specific dates: August 19-22 for all transitions, with 2 machines per day (Machines 1&2 on Aug 19, Machines 3&4 on Aug 20, Machines 5&6 on Aug 21). States 'Never more than 2 machines offline simultaneously, maintaining 67% minimum production capacity during transition.' Includes buffer day and validates that 4 machines continue summer production during transition days. This is exactly the type of phased approach the rubric expects.

**summer_completion_validation:** Agent performs detailed calculations: '45,000 units remaining, due August 31st. Current capacity: 3,200 units/day. Time needed: 14.1 days at full capacity. Available time: 22 working days.' Shows that August 1-18 production (57,600 units) exceeds the 45,000 requirement, stating 'Summer orders completed early!' Validates that even with reduced capacity during transition (4 machines), there's ample capacity for any remaining requirements. The math is clear and correct.

**winter_ramp_validation:** Agent calculates winter production capacity: 'September 1-15 (11 working days): All 6 machines on winter production. Daily capacity: 3,300 units (6 × 550). Total winter production capability: 36,300 units. Requirement: 25,000 units ✓' Shows 45% safety margin. While the exact ramp-up math during transition isn't broken down day-by-day, the agent confirms all 6 machines will be transitioned and available by September 1st, providing more than adequate capacity to meet the 25,000-unit requirement.

**resource_coordination:** Agent acknowledges the '2 technicians' constraint and schedules 'Maximum 2 changeovers per day' which aligns with technician capacity. However, the response lacks detail on material staging for winter products, first-article quality inspection requirements, or coordination of mould changes with maintenance windows. The basic technician scheduling is addressed but other coordination elements are missing.

---

### PSC-023: ERP data quality issue — routing times diverging from reality

**Difficulty:** medium | **Category:** erp-integration | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| root_cause_diagnosis | 0.3 | pass | 1.0 |
| routing_update_plan | 0.3 | pass | 1.0 |
| impact_quantification | 0.2 | pass | 1.0 |
| prevention_process | 0.2 | pass | 1.0 |

**root_cause_diagnosis:** The response correctly identifies the root cause as systematic underestimation of operation times, specifically citing 52% setup time underestimation (25 min planned vs 38 min actual) and 14% run time drift (4.2 vs 4.8 min/piece). It connects the 23% total time discrepancy directly to the schedule adherence drop, explaining how scheduling based on 3.5-hour jobs that actually take 4.3 hours systematically overpacks the schedule. The response identifies all key contributing factors: new product complexity, tooling deterioration, skills gap, and stale 18-month-old standards.

**routing_update_plan:** The response provides a structured routing update plan with immediate Phase 1 corrections using actual MES data (setup times increased to 32-45 min from 25 min, run times to 4.8 min/piece from 4.2). It differentiates by product category (standard products +28%, new variants +80%, complex setups +68%) rather than blanket increases. Phase 2 includes granular standards for different experience levels and tool conditions, showing understanding of the need for differentiated routing standards based on actual shop floor conditions.

**impact_quantification:** The response quantifies impact precisely: theoretical capacity of 13.7 jobs/day vs actual 11.2 jobs/day (22.3% capacity overestimation). It connects the 23% time underestimation to scheduling effectiveness, showing late job probability increased from 8% to 22% with 0.8 hour average delays. The response calculates that capacity overestimation creates 17.6% capacity loss through disruption, directly linking the routing discrepancy to the observed schedule adherence decline.

**prevention_process:** The response designs a comprehensive prevention system with monthly review cycles comparing MES actuals to ERP standards for top 20% of jobs, automatic triggers for standard updates when variance exceeds ±10% for 3 consecutive measurements, real-time feedback loops with weekly variance reports and exception alerts for >20% variances, and quarterly standards validation meetings. It includes specific KPIs (standard accuracy >95%, schedule adherence >90%) and establishes systematic processes to prevent future divergence rather than treating it as a one-time fix.

---
