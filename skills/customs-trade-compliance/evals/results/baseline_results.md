# Eval Results: customs-trade-compliance

**Mode:** Baseline (No Capability Context)  
**Version:** 1.0.0  
**Model:** claude-sonnet-4-20250514  
**Timestamp:** 2026-02-25T05:53:47Z  
**Aggregate Score:** 74.6%  
**Passed (>=70%):** 18/28

## Summary by Difficulty

| Difficulty | Avg Score | Count |
|---|---|---|
| Easy | 67.8% | 8 |
| Medium | 80.5% | 10 |
| Hard | 74.2% | 10 |

## Summary by Category

| Category | Avg Score | Count |
|---|---|---|
| documentation | 69.4% | 4 |
| duty-optimisation | 57.5% | 4 |
| fta-qualification | 61.7% | 3 |
| incoterms | 85.0% | 2 |
| penalties | 92.5% | 4 |
| restricted-party-screening | 88.1% | 4 |
| tariff-classification | 55.6% | 4 |
| valuation | 94.2% | 3 |

## Scenario Details

### CTC-001: Standard tariff classification of a consumer electronics product

**Difficulty:** easy | **Category:** tariff-classification | **Score:** 32.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| correct_classification | 0.35 | fail | 0.0 |
| duty_rate_and_additional_duties | 0.3 | partial | 0.5 |
| classification_rationale | 0.35 | partial | 0.5 |

**correct_classification:** Agent classified the product under 8518.30.2000 ('Other loudspeakers') which is incorrect. The correct classification should be under 8518.22 (multiple loudspeakers mounted in same enclosure) or 8518.29 (other loudspeakers), not 8518.30 which covers headphones/earphones and microphone sets. The agent incorrectly placed it in the headphones/earphones subheading despite clearly stating it's a loudspeaker. Additionally, the agent failed to check Section XVI Note 5(A) regarding ADP machines, which is critical for distinguishing Bluetooth speakers from data processing equipment.

**duty_rate_and_additional_duties:** Agent correctly identified the Section 301 additional duties apply to Chinese-origin goods and provided a duty rate calculation. However, the agent stated Section 301 rate as 7.5% under 'List 4A' when the pass criterion specifies Chinese goods under heading 8518 are subject to Section 301 List 3 at 25%. The agent also correctly noted the need to adjust FOB value for customs purposes but used the wrong Section 301 rate, resulting in an incorrect total effective duty calculation.

**classification_rationale:** Agent provided some GRI 1 analysis by identifying Chapter 85 and heading 8518 correctly, and noted the single-function nature of the device. However, the response failed to systematically check Section XVI notes, particularly Note 3 for composite machines and Note 5(A) for ADP machine criteria, which are critical for proper classification. The agent also did not mention checking CBP CROSS database for prior rulings on Bluetooth speakers, and the subheading analysis was flawed by placing a loudspeaker under the headphones/earphones category.

---

### CTC-002: Selecting the correct Incoterm for a containerised ocean shipment

**Difficulty:** easy | **Category:** incoterms | **Score:** 87.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| incoterm_analysis | 0.4 | pass | 1.0 |
| customs_valuation | 0.35 | pass | 1.0 |
| practical_recommendation | 0.25 | partial | 0.5 |

**incoterm_analysis:** The response correctly identifies that FOB Hamburg is inappropriate for containerized cargo, specifically noting that FOB is 'designed for conventional break-bulk cargo' and that 'risk transfer occurs over the ship's rail - a concept that doesn't apply to container operations.' It properly recommends FCA Hamburg as the alternative, explaining that risk transfers when goods are delivered to the carrier at the container terminal. This demonstrates understanding of Incoterms 2020 guidance for containerized shipments.

**customs_valuation:** The response correctly calculates US customs value by converting the invoice value (€85,000 × 1.09 = $92,650) and adding ocean freight ($3,200) and marine insurance ($425) to arrive at $96,275 customs value. It properly applies the 2.0% duty rate to calculate $1,925.50 in duties. The response correctly excludes inland freight from Houston to warehouse from the customs value, showing understanding that US customs values on a CIF-equivalent basis under 19 CFR § 152.103.

**practical_recommendation:** The response provides a clear recommendation to negotiate FCA Hamburg instead of FOB Hamburg and explains the benefits (eliminate ambiguity, align with container practices). However, it lacks deeper business context analysis such as who has better freight rates, logistics capabilities, or consideration of CIP Houston as an alternative where the seller arranges freight. It also doesn't discuss the insurance coverage differences between Incoterms (ICC A vs ICC C requirements) that could impact the business decision.

---

### CTC-003: Basic import documentation checklist for a first-time importer

**Difficulty:** easy | **Category:** documentation | **Score:** 52.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| document_list | 0.35 | partial | 0.5 |
| isf_requirements | 0.3 | fail | 0.0 |
| pga_requirements | 0.35 | pass | 1.0 |

**document_list:** The response lists most required documents including commercial invoice, packing list, bill of lading, entry summary (Form 7501), and power of attorney. However, it fails to mention the customs bond requirement, which is critical for first-time importers who typically need a single-entry bond. The response also includes some non-required documents like 'factory inspection certificate' and 'certificate of origin' as required rather than optional. The commercial invoice requirements are mentioned but not specifically referenced to 19 CFR § 141.86.

**isf_requirements:** The response incorrectly states that ISF must be filed '24 hours before vessel departure from China' when the correct requirement is 24 hours before vessel LOADING at the foreign port. While it lists some ISF elements, it provides an incomplete list and uses incorrect terminology (e.g., 'Harmonized Tariff Schedule Number' instead of the required HS-6 commodity code). The response does mention the $5,000 penalty and urgency, but the fundamental timing error regarding vessel departure vs. loading is a critical mistake that could lead to violations.

**pga_requirements:** The response correctly identifies FDA as the relevant PGA for ceramic dinnerware as food contact surfaces and accurately states the lead and cadmium release limits (3.0 µg/ml for flatware, 2.0 µg/ml for small hollowware, 1.0 µg/ml for large hollowware for lead; 0.5 µg/ml for flatware, 0.25 µg/ml for hollowware for cadmium). It also mentions CPSC requirements and demonstrates understanding that ceramic tableware falls under FDA jurisdiction for food contact compliance. The response shows awareness of the regulatory framework governing ceramic imports from China.

---

### CTC-004: Straightforward restricted party screening false positive adjudication

**Difficulty:** easy | **Category:** restricted-party-screening | **Score:** 70.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| adjudication_analysis | 0.4 | pass | 1.0 |
| documentation_and_process | 0.3 | partial | 0.5 |
| risk_awareness | 0.3 | partial | 0.5 |

**adjudication_analysis:** The response correctly identifies this as a false positive and systematically documents multiple distinguishing factors: (1) entity type mismatch (company vs individual), (2) geographic separation (Jordan vs Syria), (3) established business profile with Jordanian registration since 2004, (4) clean transaction history with two prior orders, and (5) recognition that 'Al-Hassan' is a common Arabic surname with only 78% match. The analysis properly notes that 78% is based on surname similarity alone and lacks given names or business identifiers. All key differentiating factors are identified and analyzed systematically.

**documentation_and_process:** The response provides good documentation of the screening hit details, analysis factors, and clear disposition. However, it lacks several critical process elements: no mention of the specific date of adjudication, no identification of the adjudicator by name, no mention of the 5-year record retention requirement, and no requirement for supervisory approval of the false positive determination. The documentation is substantive but missing key procedural safeguards.

**risk_awareness:** The response demonstrates good risk assessment by categorizing product risk as LOW for EAR99 equipment and customer risk as LOW for established business. However, it fails to acknowledge important residual risk factors: Jordan's geographic proximity to Syria as a potential concern, the fact that trading companies can serve as intermediaries for diversion, and the need to verify end use/end user even for EAR99 products. The response confirms EAR99 status but doesn't fully address the geographic and business model risk factors that should be monitored.

---

### CTC-005: Calculating FTA duty savings under USMCA for an automotive component

**Difficulty:** easy | **Category:** fta-qualification | **Score:** 50.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| rule_of_origin_identification | 0.3 | fail | 0.0 |
| qualification_analysis | 0.4 | partial | 0.5 |
| savings_and_recommendation | 0.3 | pass | 1.0 |

**rule_of_origin_identification:** The agent incorrectly identifies the USMCA rule for HTS 8708.70 as requiring 62.5% RVC, when automotive parts under heading 8708 typically require 70-75% RVC under USMCA. The agent also fails to check the actual USMCA Annex 4-B product-specific rule and instead provides generic tariff shift language ('change to subheading 8708.70 from any other heading') without verifying the specific USMCA requirements for automotive parts.

**qualification_analysis:** The agent performs both tariff shift and RVC analyses, correctly identifies that Canadian aluminium is originating under USMCA cumulation, and properly excludes it from non-originating materials. However, there are significant errors: (1) uses wrong RVC threshold (62.5% vs actual 70-75%), (2) includes profit margin in the net cost calculation incorrectly by subtracting it rather than using proper net cost methodology, (3) calculates 73.9% RVC when the correct calculation should be approximately 75.8% using transaction value method: ((95-23)/95) × 100.

**savings_and_recommendation:** Agent correctly calculates annual duty savings at $285,000 ($11,400,000 × 2.5%) and per-unit savings of $2.38. Provides sound recommendations including claiming USMCA preferential treatment, maintaining detailed records, obtaining Certificate of Origin from Mexican manufacturer, and monitoring supply chain changes. Addresses documentation requirements and the need for ongoing compliance monitoring.

---

### CTC-006: Handling a CBP CF-28 Request for Information on a routine entry

**Difficulty:** easy | **Category:** documentation | **Score:** 85.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| cf28_response_quality | 0.35 | pass | 1.0 |
| significance_analysis | 0.35 | pass | 1.0 |
| risk_identification | 0.3 | partial | 0.5 |

**cf28_response_quality:** The response provides a complete, professional CF-28 response addressing all four CBP requests with appropriate specificity: (1) manufacturer name and full address for IndoSteel Home Products Pvt. Ltd., (2) detailed product specifications including 18-gauge Type 304 stainless steel, single bowl undermount design with specific dimensions, (3) country of origin as India with explicit confirmation that steel was melted and poured in India at Tata Steel Jamshedpur facility, and (4) comprehensive related-party valuation documentation including CUP analysis showing $42 price within $38-$48 market range, transfer pricing study, and supporting financial documents. The tone is factual and cooperative rather than defensive.

**significance_analysis:** The response correctly explains the significance of each CBP request: manufacturer information for trade remedy verification and potential manufacturer-specific duty rates, detailed product description for HTS classification verification and trade remedy scope determination, steel origin verification for Buy American compliance and Section 232 implications, and related-party valuation scrutiny for revenue protection and transfer pricing compliance. The response demonstrates understanding that CBP is conducting verification for potential AD/CVD exposure and related-party pricing audit triggers, though it could have been more explicit about the CF-29 consequence of inadequate response.

**risk_identification:** The response identifies several key risks including transfer pricing scrutiny as the primary audit trigger, potential for additional duties if valuation is questioned, and classification verification concerns. It recommends immediate actions like comprehensive response submission and engaging transfer pricing experts. However, it misses the critical risk that if steel was NOT actually melted and poured in India, this could affect country of origin determination for AD/CVD and Section 232 purposes. The response also doesn't mention that this CF-28 could be part of a broader Focused Assessment or recommend reviewing other entries for consistency.

---

### CTC-007: Simple customs valuation with assists provided to foreign manufacturer

**Difficulty:** easy | **Category:** valuation | **Score:** 82.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| assist_identification | 0.3 | pass | 1.0 |
| correct_calculation | 0.35 | pass | 1.0 |
| corrective_action | 0.35 | partial | 0.5 |

**assist_identification:** Agent correctly identifies both engineering drawings ($15,000) and custom mould ($45,000) as assists under 19 CFR 152.102(d)(1). Properly categorizes engineering drawings as 'engineering and design work undertaken elsewhere and provided to the producer free of charge' and mould as 'tools, dies, and moulds provided to the producer free of charge.' Correctly states that both must be added to transaction value under 19 USC 1401a. Does not make the EU/US confusion error about domestic engineering work exemption.

**correct_calculation:** Agent correctly calculates: Total assists = $60,000, prorated across 500,000 units = $0.12 per unit, adjusted unit value = $2.80 + $0.12 = $2.92, total correct dutiable value = $1,460,000. Correctly calculates duty underpayment as $2,040 annually using the 3.4% duty rate. Properly prorates assists across the full production volume rather than incorrectly adding full amount to first shipment. Mathematical calculations are accurate throughout.

**corrective_action:** Agent recommends filing prior disclosure under 19 CFR 162.74 and updating broker procedures, which are appropriate. However, the response suggests filing 'CF-28 requests for duty rate corrections' rather than the correct mechanism of Post Summary Corrections (PSCs) for adding assist values to liquidated entries. CF-28s are CBP information requests, not correction mechanisms. Missing recommendation for internal SOP requiring trade compliance review of tooling/engineering provided to suppliers. Does address the key corrective actions but uses incorrect procedural mechanism.

---

### CTC-008: Incoterms DDP with circular duty valuation problem

**Difficulty:** easy | **Category:** incoterms | **Score:** 82.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| circular_valuation_problem | 0.4 | pass | 1.0 |
| correct_methodology | 0.35 | partial | 0.5 |
| practical_guidance | 0.25 | pass | 1.0 |

**circular_valuation_problem:** The agent correctly identifies the circular valuation problem, stating 'Using the full DDP price of $250,000 as the customs value would result in double taxation of duties and fees' and explains that 'the $250,000 already includes U.S. import duties (3.2% × customs value)' while 'CBP will calculate duties on this inflated amount, meaning you'll pay duties twice.' The agent recognizes that duties are built into the DDP price and using that price as customs value creates circular taxation.

**correct_methodology:** The agent demonstrates understanding of the need to work backwards from DDP price and lists the correct components to subtract (duties, fees, freight, insurance). However, the response does not provide the algebraic methodology to solve the circular equation. The calculation shown is incomplete with '*These are estimates requiring iteration' without showing how to actually solve for the CIF value where duty depends on the value itself. The agent mentions the concept but doesn't provide the mathematical framework: CIF = X, therefore $250,000 = X + 0.032X + fees, solve for X.

**practical_guidance:** The agent provides comprehensive practical guidance including: 'Request FOB breakdown from supplier' with specific details needed, 'Use Transaction Value method - The FOB price will be your customs value under 19 USC 1401a(b)(1)', coordination with broker instructions, and specific broker guidance to 'Declare the FOB value as customs value, NOT the DDP price.' The response also suggests working backwards if supplier cannot provide breakdown and advises being prepared with documentation for CBP questions.

---

### CTC-009: Multi-function device classification requiring GRI 3(b) essential character analysis

**Difficulty:** medium | **Category:** tariff-classification | **Score:** 57.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| gri_application | 0.35 | partial | 0.5 |
| essential_character_analysis | 0.4 | pass | 1.0 |
| duty_impact_and_risk | 0.25 | fail | 0.0 |

**gri_application:** The response attempts GRI analysis but has significant gaps. It correctly starts with GRI 1 and identifies multiple candidate headings (8525, 8517, 8471, 8528). However, it completely omits Section XVI Note 3, which is critical for composite machines performing multiple functions like this device. The response jumps to 'GRI 2(b): Essential Character Analysis' which doesn't exist - GRI 2 deals with incomplete/unfinished goods, not essential character. Essential character analysis belongs under GRI 3(b). The agent shows awareness of the need for systematic GRI application but misapplies the framework.

**essential_character_analysis:** The response provides a thorough essential character analysis examining cost/value (camera 35% + storage 5% = 40% vs smart home controller 40%), functional analysis, marketing/intended use, and technical integration. It correctly identifies this as a close case between headings 8525 and 8517, weighs factors for each heading, and reaches a reasoned conclusion that the smart home controller represents essential character based on highest single component cost (40%), broader system functionality, and integrated platform approach. The analysis demonstrates understanding that both functions are substantial but makes a defensible determination.

**duty_impact_and_risk:** The response mentions 'Section 301 List 3: 25% additional tariff applies' and references 'Standard HTS duty rate for 8517.62.0090' but fails to address key duty impact elements. It does not identify the actual duty rate difference between candidate headings 8525 and 8517, does not calculate total duty exposure, and most critically, does not recommend requesting a CBP binding ruling despite acknowledging this is a 'close case' with classification ambiguity. For a $680,000 import program with ambiguous classification, failing to recommend a binding ruling before first shipment is a significant oversight.

---

### CTC-010: USMCA qualification failure due to non-originating material from outside the zone

**Difficulty:** medium | **Category:** fta-qualification | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| qualification_analysis | 0.35 | pass | 1.0 |
| exposure_calculation | 0.3 | pass | 1.0 |
| corrective_action | 0.35 | pass | 1.0 |

**qualification_analysis:** The agent correctly determines the handbags do NOT qualify for USMCA. Accurately identifies the product-specific rule for HTS 4202: 'A change to heading 4202 from any other heading except from heading 4104-4107.' Correctly recognizes that Italian leather classified under HS 4107.12 falls within the prohibited range 4104-4107, making this the 'Fatal Issue.' Understands that the leather does not undergo sufficient tariff shift to qualify, and correctly concludes the USMCA claim is invalid due to this specific exclusion.

**exposure_calculation:** Agent calculates specific duty exposure: $127,500 in unpaid duties over 8 months across approximately 35 entries. Provides detailed breakdown showing annual impact of $170,000 and monthly exposure of $14,167. While the response doesn't explicitly detail the penalty calculation under 19 USC § 1592 or mention interest calculations, it clearly identifies the $127,500 duty liability and recognizes this as 'significant duty exposure' warranting corrective action.

**corrective_action:** Agent recommends comprehensive corrective action: (1) immediately stop claiming USMCA preference, (2) file voluntary prior disclosure under 19 CFR 162.74 to minimize penalties, (3) conduct comprehensive entry review of all affected entries, (4) payment of $127,500 in unpaid duties. Provides detailed prior disclosure key points including nature of violation, scope, circumstances, and proposed resolution. Recommends long-term supply chain solutions including sourcing USMCA-originating leather and enhanced compliance procedures. Timeline of 30 days is appropriate for maximizing penalty mitigation benefits.

---

### CTC-011: Related-party customs valuation with transfer pricing conflict

**Difficulty:** medium | **Category:** valuation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| valuation_analysis | 0.35 | pass | 1.0 |
| eapa_response | 0.3 | pass | 1.0 |
| strategic_recommendation | 0.35 | pass | 1.0 |

**valuation_analysis:** The agent correctly identifies the core issue: the $180/kg transfer price is 22-33% below market range ($220-$240/kg) and fails the 'circumstances of sale' test under 19 USC 1401a(b)(2)(B). The response properly distinguishes that TNMM may be appropriate for tax purposes but 'does not satisfy customs valuation requirements' when it significantly differs from unrelated party prices. The agent applies 19 CFR 152.103(l) requiring related party values to approximate arm's length prices and correctly concludes the variance 'exceeds reasonable approximation threshold.' This demonstrates understanding of the conflict between transfer pricing methodology and customs valuation requirements.

**eapa_response:** The agent recognizes the EAPA allegation creates immediate compliance risk and recommends proactive engagement rather than waiting passively. Specifically recommends: (1) 'Conduct Prior Disclosure' filing CBP Form 28 'before CBP contacts you,' (2) demonstrates understanding that prior disclosure provides 'reduced penalties' and 'demonstrates good faith compliance,' (3) recommends immediate revaluation of methodology to market-based pricing. The response shows understanding that the significant price disparity gives the competitor 'formal grounds for the allegation' and that CBP will 'likely investigate and compare declared values to market prices.'

**strategic_recommendation:** The agent provides a comprehensive multi-track approach: (1) Short-term: immediate prior disclosure and revaluation to $220-$230/kg range, (2) Medium-term: addresses structural issue by recommending 'Establish Dual Pricing System' maintaining $180/kg for tax purposes while using market-based pricing for customs, (3) Long-term: ongoing compliance through quarterly price reviews and documentation. Correctly calculates penalty exposure ($117K-$175K duty shortfall) and demonstrates understanding that prior disclosure caps penalties while non-disclosure creates 2x penalty risk. The recommendation to 'maintain contemporaneous documentation' and establish audit trails shows practical compliance expertise.

---

### CTC-012: Restricted party screening true positive — Entity List match

**Difficulty:** medium | **Category:** restricted-party-screening | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| hit_adjudication | 0.25 | pass | 1.0 |
| compliance_actions | 0.4 | pass | 1.0 |
| fdpr_analysis | 0.35 | pass | 1.0 |

**hit_adjudication:** The agent correctly identifies this as a 'CONFIRMED HIT - TRANSACTION PROHIBITED' and explicitly states the transaction must be denied immediately. The response properly analyzes the 99% match score as 'virtual certainty' and confirms both company name and geographic location (Guiyang) align precisely with the Entity List entry. The agent unambiguously blocks the transaction with no suggestion of proceeding while investigating further.

**compliance_actions:** The response comprehensively addresses required actions: (1) explicitly states 'STOP all transaction activities - Do not process, ship, or provide any services', (2) correctly identifies ECCN 3B001 as EAR-controlled and notes Entity List restrictions apply to 'all EAR-controlled items', (3) acknowledges the 'presumption of denial' policy making license approval extremely unlikely, (4) requires notifying internal stakeholders and flagging the customer in systems, (5) includes customer communication template, and (6) addresses the FDPR extensively. The response properly treats this as an immediate block rather than a license application strategy.

**fdpr_analysis:** The agent provides detailed FDPR analysis explaining both 'Direct Products Covered' (foreign-manufactured items that are direct products of US technology/software) and 'Plant/Major Component Products' (items produced by plants that are direct products of US technology). The response correctly notes that 'even non-U.S. manufactured competing equipment may require BIS authorization' and explains the comprehensive technology denial regime. The analysis demonstrates understanding that FDPR extends US jurisdiction to non-US manufactured items, particularly relevant for semiconductor manufacturing equipment with pervasive US technology components.

---

### CTC-013: Prior disclosure decision after discovering systematic classification error

**Difficulty:** medium | **Category:** penalties | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| disclosure_decision | 0.3 | pass | 1.0 |
| exposure_calculation | 0.35 | pass | 1.0 |
| filing_steps | 0.35 | pass | 1.0 |

**disclosure_decision:** Agent clearly recommends filing a prior disclosure immediately with strong rationale. Correctly identifies the $214,400 duty shortfall as material and calculates potential savings of $400,000-430,000. Notes the systematic nature across 85 entries over 14 months could be viewed as gross negligence, making disclosure even more critical. Identifies that error was discovered internally (not by CBP), making prior disclosure available. Explicitly states this eliminates penalty exposure versus full penalty risk if CBP discovers independently.

**exposure_calculation:** Agent correctly calculates both scenarios. Without disclosure: identifies negligent violation penalty up to $214,400 (100% of duty shortfall) and gross negligent up to $428,800 (200%), plus duty owed $214,400 and interest, for maximum exposure up to $668,200. With disclosure: eliminates penalties entirely with proper disclosure, leaving only duty owed $214,400 plus interest ~$15,000-25,000, totaling ~$229,400-239,400. Correctly calculates net savings of $400,000-430,000. Properly distinguishes between duty owed (always payable) and penalty amounts.

**filing_steps:** Agent provides comprehensive filing steps: (1) engages qualified customs attorney, (2) prepares entry-by-entry analysis of all 85 affected entries with detailed calculations, (3) documents discovery process and timeline, (4) prepares complete disclosure package including cover letter, supporting documentation, and legal analysis, (5) pays duties and estimated interest with filing, (6) files with appropriate port director. Also recommends immediate cessation of incorrect classification, corrective action plan, and enhanced procedures. Includes proper sequencing and timeline (30-day process).

---

### CTC-014: Evaluating an FTZ admission strategy for inverted tariff relief

**Difficulty:** medium | **Category:** duty-optimisation | **Score:** 65.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| ftz_benefit_analysis | 0.4 | partial | 0.5 |
| operational_requirements | 0.3 | pass | 1.0 |
| risk_assessment | 0.3 | partial | 0.5 |

**ftz_benefit_analysis:** The response correctly identifies inverted tariff relief with accurate calculation ($899,000 total component duties eliminated), export savings (20% × $899,000 = $179,800), and scrap savings (3% × $899,000 = $26,970). However, it miscalculates the total potential savings as $899,000 instead of $1,105,770 by double-counting. The response states 'Total Annual Duty Savings: $899,000' in the summary but shows the individual components correctly. It demonstrates understanding of the three FTZ benefits but fails to properly aggregate them, showing $899,000 as both the baseline duties AND the total savings, which is mathematically inconsistent.

**operational_requirements:** The response comprehensively addresses operational requirements: FTZ Board application process (12-18 months timeline, $50,000-100,000 costs), infrastructure modifications ($200,000-500,000), perpetual inventory system with weekly reconciliation, separate tracking for components by origin and finished goods by destination, CBP oversight with regular inspections, documentation requirements including daily transaction reports and monthly inventory reports, annual reconciliation, and staff training. It correctly identifies the need to work through a zone operator and covers both setup and ongoing operational costs.

**risk_assessment:** The response identifies some key risks including regulatory compliance burden, inventory management complexity, and CBP audit exposure. However, it misses critical FTZ-specific risks: (1) does not mention that FTZ Board may deny manufacturing authority, (2) does not consider that tariff changes could eliminate benefits, (3) does not address Section 301 tariff limitations (which apply even in FTZ unless goods are exported), and (4) does not mention AD/CVD duty limitations. The risk assessment is too optimistic, categorizing most risks as 'medium' or 'low' without acknowledging regulatory approval uncertainty or trade policy risks.

---

### CTC-015: EU-UK TCA origin determination for manufactured goods post-Brexit

**Difficulty:** medium | **Category:** fta-qualification | **Score:** 35.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| tca_rule_application | 0.4 | partial | 0.5 |
| insufficient_processing_check | 0.3 | partial | 0.5 |
| declaration_and_documentation | 0.3 | fail | 0.0 |

**tca_rule_application:** The response identifies there are two potential qualification routes (tariff shift OR value threshold of 45%) and correctly applies bilateral cumulation by treating the German frame as EU-originating. However, it fails to reference the specific TCA Annex ORIG-2 product-specific rule for heading 8711, instead providing what appears to be a generic rule structure. The response also doesn't account for UK value-added from assembly operations when calculating the originating content percentage, only counting component values. While it concludes qualification under the tariff shift rule, it lacks the precision of looking up the actual TCA rule text and properly calculating all originating content including UK manufacturing value-add.

**insufficient_processing_check:** The response acknowledges the need to check sufficient processing and lists specific manufacturing operations (integration of battery packs, motor installation, assembly with mechanical components, testing). It correctly identifies that simple packaging, sorting, or labeling would be insufficient. However, it does not reference TCA Article ORIG.7 or the specific insufficient processing list in the agreement. The analysis of whether the described operations exceed 'simple assembly' is reasonable but lacks the regulatory precision of citing the actual TCA provisions that define insufficient processing operations.

**declaration_and_documentation:** The response fails to mention the REX (Registered Exporter) system, which is required for consignments above €6,000 under the TCA. At the described volumes and values, REX registration would be mandatory. It provides only generic guidance about 'statement on origin' without referencing the specific prescribed text requirements in TCA Annex ORIG-4. The response also doesn't mention the 4-year document retention requirement or the verification procedures that EU customs can initiate. The documentation requirements listed are reasonable but lack the TCA-specific regulatory framework.

---

### CTC-016: Duty drawback claim for re-exported imported components

**Difficulty:** medium | **Category:** duty-optimisation | **Score:** 47.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| drawback_type_identification | 0.3 | pass | 1.0 |
| recovery_calculation | 0.35 | fail | 0.0 |
| filing_requirements | 0.35 | partial | 0.5 |

**drawback_type_identification:** Correctly identifies Manufacturing Drawback under 19 USC § 1313(a)(1)(B) with proper justification that imported bearings are consumed in manufacturing of exported gearboxes. Demonstrates understanding that bearings maintain essential character when incorporated (same condition requirement). However, does not mention the 99% recovery rate or discuss potential substitution drawback under § 1313(b) post-TFTEA, but the core identification is accurate.

**recovery_calculation:** Calculates annual recovery as $324,000 (30% × $1,080,000) but fails to apply the 99% drawback rate, overstating recovery by approximately $3,240 annually. The correct calculation should be $1,080,000 × 30% × 99% = $320,760. Also states retroactive recovery of $972,000 without accounting for the 99% rate. Does mention the 5-year filing deadline but the core mathematical error is significant.

**filing_requirements:** Provides comprehensive filing requirements including CBP Form 7501 (though this should be 7551 for drawback entries), detailed documentation needs, and implementation roadmap. Correctly emphasizes traceability requirements and production records linking imports to exports. However, misses key TFTEA simplifications allowing substitution for commercially interchangeable bearings, does not mention the relative value calculation, and incorrectly references Form 7501 instead of 7551. Does recommend specialized expertise which is appropriate.

---

### CTC-017: Dual-use goods classification — EAR jurisdiction and ECCN determination

**Difficulty:** medium | **Category:** restricted-party-screening | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| eccn_classification | 0.4 | pass | 1.0 |
| licence_determination | 0.35 | pass | 1.0 |
| due_diligence | 0.25 | pass | 1.0 |

**eccn_classification:** The agent correctly classified the thermal imaging camera under ECCN 6A003.b.4, properly analyzing the key controlled parameters: NETD ≤ 0.05°C (camera has 0.03°C), spectral range 8-14 micrometers (exact match), and resolution >480 pixels (640×480 = 307,200 pixels exceeds threshold). The agent explicitly noted this classification takes precedence over less restrictive categories like 6A993 or EAR99, demonstrating understanding of the hierarchical nature of ECCN controls and the specific performance thresholds that distinguish controlled from less-controlled items.

**licence_determination:** The agent correctly determined that a BIS export license is required, properly identifying that ECCN 6A003.b.4 is controlled for National Security (NS) and Regional Stability (RS) reasons with Column 1 controls requiring licenses for all destinations except Country Group A:1. The agent accurately noted that UAE is in Country Group B (not A:1), therefore requiring a license. The analysis demonstrates proper understanding of the Commerce Country Chart structure and control reasons.

**due_diligence:** The agent identified comprehensive due diligence requirements including: (1) screening against denied persons lists (BIS, OFAC), (2) recognizing dual-use concerns for thermal imaging technology with potential military/surveillance applications despite stated commercial use, (3) identifying the need for end-user statements and verification of the distributor's customer base given the 50-unit quantity, (4) recognizing regional diversion risks in the Middle East requiring re-export restrictions, and (5) recommending enhanced customer verification for the high-value transaction. The response addresses all key due diligence elements for controlled dual-use technology exports.

---

### CTC-018: Handling a CBP penalty assessment for negligent misclassification

**Difficulty:** medium | **Category:** penalties | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| classification_evaluation | 0.3 | pass | 1.0 |
| response_strategy | 0.4 | pass | 1.0 |
| response_drafting | 0.3 | pass | 1.0 |

**classification_evaluation:** The response correctly recognizes the unusual situation where CBP's reclassification results in a lower duty rate (2.6% vs 3.9%) and that the company overpaid duties by $35,100. It explicitly states 'No Loss to Revenue: The company overpaid duties by $35,100, meaning the government suffered no loss' and 'Excessive Penalty: $180,000 penalty for a classification dispute where duties were overpaid is unreasonable.' The response properly evaluates CBP's proposed classification on the merits, arguing that HTS 9405.42 is correct for LED light fixtures and that 8543.70 is inappropriate, citing that 'Chapter 94 (furnishings, lamps, lighting fittings) has priority over Chapter 85 (electrical machinery) for complete lighting fixtures.' It demonstrates understanding that penalties can be assessed regardless of revenue loss.

**response_strategy:** The response develops a comprehensive two-track strategy. Track 1 contests the reclassification with detailed arguments supporting HTS 9405.42, including GRI analysis and precedential support. Track 2 addresses penalty mitigation even if the classification is wrong, emphasizing the overpayment situation ('No Loss to Government: Actual overpayment of $35,100 in duties'), clean compliance history ('12 years of clean compliance history'), and good faith interpretation. The response recognizes the 30-day deadline ('Within 30 Days') and provides specific mitigation factors including the ambiguous nature of LED lighting classification. It requests both complete penalty cancellation and alternative mitigation options.

**response_drafting:** The response provides comprehensive draft elements including: (1) executive summary acknowledging the dispute, (2) detailed classification defense with legal framework and merchandise description, (3) strong penalty mitigation arguments addressing no negligence, no loss to government, and mitigating factors, (4) specific requests for classification ruling and penalty relief, and (5) procedural considerations. The draft emphasizes the key mitigation argument that 'Government received more revenue than legally owed' and 'Penalty serves no remedial purpose.' It recommends engaging customs counsel and includes tactical considerations for follow-up actions. The response provides substantive, actionable draft content rather than generic advice.

---

### CTC-019: Transshipment circumvention — AD/CVD evasion investigation on steel products

**Difficulty:** hard | **Category:** penalties | **Score:** 70.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| eapa_process_knowledge | 0.25 | partial | 0.5 |
| substantial_transformation_analysis | 0.35 | partial | 0.5 |
| operational_and_financial_actions | 0.4 | pass | 1.0 |

**eapa_process_knowledge:** The response demonstrates some EAPA process knowledge including the 30-day response period for interim measures and 300-day investigation timeline. However, it lacks critical details: doesn't mention CBP's 90-day deadline for interim determination, omits that CBP has subpoena authority to compel Vietnamese mill records, doesn't note the high affirmative rate (~70%+) of EAPA investigations, and while it mentions retroactive liability from 'interim measures date,' it doesn't clearly explain that affirmative final determinations result in AD/CVD duties applying retroactively to all entries during the investigation period.

**substantial_transformation_analysis:** The response provides a reasonable framework for substantial transformation analysis, asking relevant questions about gauge reduction, processing complexity, and value addition. However, it fails to demonstrate deep knowledge of CBP's evolving position on steel processing in EAPA cases, particularly the narrower view taken in recent Southeast Asian steel cases. The response doesn't analyze the suspicious $680/MT pricing (below legitimate Vietnamese production costs) or consider that this suggests minimal Vietnamese processing margins with cheap Chinese input steel. It treats substantial transformation as a winnable argument without acknowledging CBP's recent skepticism toward steel cold-rolling as sufficient transformation.

**operational_and_financial_actions:** The response provides comprehensive operational and financial guidance: correctly calculates cash deposit impact ($1.8M per shipment, $14.47M annual exposure), recommends immediate trade counsel retention, advises challenging interim measures within 30 days, includes detailed supply chain diversification with specific country alternatives and pricing, recommends Vietnamese mill audit and documentation, suggests establishing credit facilities for deposits, and provides cost estimates for legal defense ($275K-425K). The response addresses both immediate cash flow impact and medium/long-term supply chain strategy, demonstrating practical understanding of the financial and operational challenges.

---

### CTC-020: Complex classification of a multi-material composite product crossing chapter boundaries

**Difficulty:** hard | **Category:** tariff-classification | **Score:** 82.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| systematic_gri_application | 0.35 | partial | 0.5 |
| essential_character_determination | 0.4 | pass | 1.0 |
| binding_ruling_recommendation | 0.25 | pass | 1.0 |

**systematic_gri_application:** The response attempts to apply GRIs systematically but makes critical errors. It incorrectly states 'GRI 1 - Headings vs. Subheadings Not applicable - we're determining the appropriate heading first' - this misunderstands GRI 1, which applies when goods are prima facie classifiable in one heading only. The agent should have first determined if the product fits clearly in 9506, 4016, or 8543 before moving to GRI 2(b). It correctly identifies this as a composite good under GRI 2(b) and properly analyzes candidate headings (9506, 8543, 4016), but the initial GRI 1 error and failure to systematically eliminate headings shows incomplete methodology.

**essential_character_determination:** The response provides a comprehensive essential character analysis considering all relevant factors: physical composition by weight (70% rubber), value composition (62.5% electronics), functional analysis (smart functionality as differentiating feature), and commercial reality (premium pricing for electronic functionality). It weighs these factors systematically and reaches a reasoned conclusion that electronics impart essential character through value dominance, functional differentiation, and marketing positioning. The analysis acknowledges the genuine tension between physical composition and value composition, demonstrating proper application of the essential character test.

**binding_ruling_recommendation:** The response strongly recommends seeking a binding ruling with solid rationale: high import value ($1.8M), novel product category with limited precedents, potential for CBP disagreement (could argue for 9506 based on physical characteristics), audit protection benefits, and business planning certainty. It provides specific ruling strategy recommendations including submitting technical specifications and marketing materials. The response correctly identifies this as a genuinely ambiguous classification requiring CBP guidance, which is exactly the type of situation where binding rulings are most valuable.

---

### CTC-021: First sale valuation challenge with related-party middleman

**Difficulty:** hard | **Category:** valuation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| first_sale_validity | 0.4 | pass | 1.0 |
| exposure_assessment | 0.3 | pass | 1.0 |
| recommended_action | 0.3 | pass | 1.0 |

**first_sale_validity:** The response correctly identifies all fatal problems with the first sale programme: (1) Related party relationship between HK subsidiary and US importer through common parent ownership, citing 19 CFR 152.103(l). (2) Insufficient economic substance of HK subsidiary with minimal activities (basic invoicing, quarterly visits, no physical handling) failing the 'bona fide middleman' test. (3) Payment flows through 'intercompany transfers' rather than arm's length commercial payments undermining the separate sale argument. (4) Assists (product designs/specifications) flow directly from US to Chinese factory, bypassing HK subsidiary entirely. Correctly concludes the programme is not defensible due to these structural issues.

**exposure_assessment:** Response accurately calculates multi-year exposure: $204K annually × 3 years = $612K in underpaid duties. Identifies penalty exposure with proper statutory framework. Separately identifies the assists valuation issue as an independent violation (technical assists should be included per 19 CFR 152.103(d)(1)(iii)). Quantifies potential penalty mitigation through prior disclosure. Provides structured risk assessment table with HIGH/MEDIUM risk categorization and specific exposure amounts.

**recommended_action:** Provides comprehensive action plan: (1) Immediate suspension of current programme and reversion to $95/unit for new entries. (2) Strongly recommends prior disclosure to mitigate penalties given $612K+ exposure. (3) Recommends engaging trade counsel for legal advice. (4) Addresses structural supply chain restructuring options including direct purchasing from Chinese factory or demonstrating genuine value-add by HK subsidiary. (5) Addresses the assists valuation issue for future compliance. Action plan is properly sequenced with realistic timelines and recognizes operational complexity of restructuring.

---

### CTC-022: UFLPA detention — tracing cotton supply chain through multiple tiers

**Difficulty:** hard | **Category:** documentation | **Score:** 85.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| evidence_requirements | 0.35 | pass | 1.0 |
| supply_chain_tracing | 0.35 | pass | 1.0 |
| contingency_planning | 0.3 | partial | 0.5 |

**evidence_requirements:** The response correctly identifies the key evidence requirements for overcoming the UFLPA rebuttable presumption: complete supply chain mapping from garment factory through fabric mills, yarn spinners to cotton suppliers; tier-by-tier documentation including contracts, purchase orders, and invoices; batch traceability linking specific cotton to specific garments; third-party audit reports; and crucially, isotopic testing from accredited laboratories (specifically mentioning Oritain and Applied DNA Sciences). The response demonstrates understanding that self-certifications are insufficient and emphasizes the 'clear and convincing evidence' standard through its comprehensive evidence structure.

**supply_chain_tracing:** The response provides a systematic tracing methodology with clear phases and timelines: Phase 1 (Days 1-7) focuses on direct supplier engagement with Dhaka Garments to obtain fabric cutting records and batch tracking; Phase 2 (Days 5-12) involves document authentication and cross-referencing; Phase 3 (Days 10-15) includes independent verification and on-site audits. The response includes isotopic testing as a parallel track (5-7 day turnaround) and maps the complete supply chain from garment manufacturer to cotton suppliers. The timeline respects the 30-day CBP deadline with submission planned for days 25-30.

**contingency_planning:** The response provides three scenarios with probability assessments and addresses some key contingencies including requesting CBP extensions, negotiating partial releases, and air-freighting replacement inventory. However, it fails to explicitly address the critical scenario where Xinjiang cotton is discovered in the supply chain (requiring re-export or destruction), and doesn't sufficiently emphasize that any Xinjiang cotton link makes the goods inadmissible regardless of other evidence. While it mentions long-term supply chain overhaul, it lacks specific recommendations for implementing ongoing UFLPA compliance programs with pre-clearance protocols.

---

### CTC-023: Optimising duty exposure across multiple FTAs for a multi-origin product

**Difficulty:** hard | **Category:** duty-optimisation | **Score:** 37.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| multi_fta_analysis | 0.4 | partial | 0.5 |
| supply_chain_optimisation | 0.35 | partial | 0.5 |
| financial_impact_assessment | 0.25 | fail | 0.0 |

**multi_fta_analysis:** The response analyzes each market systematically but contains several significant errors and omissions. For the US market, correctly identifies no direct FTA but misses consideration of FTZ or drawback strategies. For the UK market, correctly identifies CPTPP membership and accession but incorrectly calculates CPTPP content as only 36.1% (combining Malaysia 19.9% and Japan 16.2%) when it should include Japan 26.2% + Malaysia 30.3% = 56.5% under diagonal cumulation. For the EU market, correctly identifies no current FTA but then pivots to Vietnam strategy without proper analysis of current Malaysian qualification requirements. The response demonstrates awareness of FTA frameworks but applies cumulation rules incorrectly and doesn't properly analyze which components qualify under each agreement.

**supply_chain_optimisation:** The response identifies some restructuring opportunities but focuses primarily on establishing new facilities rather than optimizing the current BOM. It correctly suggests sourcing Japanese sensors and gears to improve CPTPP content, and proposes Vietnam assembly for EU benefits. However, it misses the most straightforward optimization: replacing the 7.6% Chinese aluminum housing with Malaysian/ASEAN content to improve both RCEP and CPTPP margins. The response also doesn't address the 9% Taiwanese PCB controllers which are non-originating under both agreements. While it proposes facility relocations, it doesn't systematically evaluate which specific component substitutions would be most cost-effective.

**financial_impact_assessment:** The response provides financial calculations but they are fundamentally flawed. It calculates UK duty savings as $84,000 annually (800 units × unclear methodology), but the correct calculation should be 800 units × $4,200 × 2.5% = $84,000. More critically, it assumes qualification under CPTPP when its own analysis shows only 36.1% content (below the likely 40% threshold). The response proposes massive facility investments ($200-500k) for markets with minimal duty savings (EU at 1.7% MFN, UK at 2.5%) without demonstrating positive ROI. It inflates potential savings to $401,100 without showing the calculation methodology, and doesn't compare restructuring costs to actual achievable savings.

---

### CTC-024: Responding to a retroactive Section 301 exclusion expiration

**Difficulty:** hard | **Category:** duty-optimisation | **Score:** 80.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| immediate_actions | 0.3 | pass | 1.0 |
| medium_term_strategies | 0.4 | partial | 0.5 |
| strategic_framework | 0.3 | pass | 1.0 |

**immediate_actions:** The response identifies key immediate actions within the 60-day window: (1) Strategic stockpiling - importing 3 months of inventory ($2.1M worth) before exclusion expires, with calculated savings of $525K in avoided tariffs and costs of $50K in expedited shipping + $15K carrying costs for net benefit of $460K. (2) Immediate purchase orders and accelerated shipping implementation. (3) Week 1-4 timeline with specific actions including engaging customs attorney and initiating supplier discussions. The response provides detailed financial calculations comparing carrying costs against tariff savings, which demonstrates the required cost-benefit analysis.

**medium_term_strategies:** The response evaluates multiple medium-term strategies including supplier diversification with financial analysis: Israeli supplier at 28% premium ($940K additional cost vs $840K tariff savings = net $100K), German supplier with calculated impacts, and graduated transition plan. However, it has critical gaps: (1) Incorrectly suggests FTZ could provide benefits without clearly stating that Section 301 tariffs apply IN the FTZ when goods enter commerce, (2) Does not evaluate duty drawback for any re-exported units, (3) The tariff engineering analysis is superficial and doesn't adequately address whether component importation with domestic assembly would actually change Section 301 applicability, (4) Missing analysis of whether supplier diversification could trigger EAPA circumvention risk.

**strategic_framework:** Presents a comprehensive strategic framework with three distinct phases: Phase 1 (0-60 days) for crisis mitigation, Phase 2 (3-12 months) for transition with specific supplier diversification targets, and Phase 3 (12+ months) for long-term optimization. Provides detailed financial modeling showing reduction from $2.1M annual exposure to $600K-800K within 18 months. Includes integrated implementation timeline with weekly milestones, risk mitigation strategies, success metrics (85%+ customer retention, 70% non-China sourcing), and addresses customer pricing strategy with 12% price increase capturing $840K additional revenue. The framework considers supply chain resilience, working capital impacts, and provides contingency planning for high-priority risks.

---

### CTC-025: Complex prior disclosure involving multiple violation types across related entities

**Difficulty:** hard | **Category:** penalties | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| prior_disclosure_strategy | 0.35 | pass | 1.0 |
| penalty_exposure_analysis | 0.3 | pass | 1.0 |
| compliance_programme_implementation | 0.35 | pass | 1.0 |

**prior_disclosure_strategy:** Response correctly recommends filing a single comprehensive prior disclosure covering all three violations simultaneously. Provides strong strategic rationale including industry scrutiny from competitor's Focused Assessment, systemic compliance failures across multiple violation types, and timing urgency. Addresses key filing logistics including consolidated CF-28 approach, emphasis on new CCO context, and comprehensive remediation narrative. Correctly notes that filing is an admission and recommends engaging specialized customs counsel. Recognizes the detection risk particularly for classification errors through CBP data analytics.

**penalty_exposure_analysis:** Response provides comprehensive penalty exposure analysis for both scenarios. Calculates maximum pre-disclosure exposure at $10.48M (40% of domestic value across all three violations). Post-disclosure analysis shows expected penalty range of $88,600-$442,000 (10-50% of duty shortfall). Correctly applies 19 USC 1592 penalty framework and recognizes that prior disclosure caps penalties significantly. Identifies mitigation arguments including voluntary disclosure timing, no prior violations, and remedial measures. Shows clear understanding that this is a multi-million dollar decision with savings potential of $1-2M+.

**compliance_programme_implementation:** Response provides comprehensive compliance programme addressing all three violation types with specific controls: (1) Classification - automated HTS validation, dual approval, annual expert review; (2) Valuation - assist identification checklist, procurement liaison, quarterly reconciliation; (3) FTA - origin determination procedures, supplier certifications, BOM analysis. Includes organizational structure with dedicated compliance roles, technology solutions, training programmes, internal audit cycles, and performance metrics. Provides detailed timeline with 30-day disclosure target, 90-day immediate changes, and 180-day full implementation. References industry best practices and positions for C-TPAT consideration.

---

### CTC-026: Multi-jurisdictional origin dispute with conflicting classification across EU, UK, and US

**Difficulty:** hard | **Category:** tariff-classification | **Score:** 50.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| classification_analysis | 0.35 | partial | 0.5 |
| uk_harmonisation_strategy | 0.4 | partial | 0.5 |
| cross_jurisdictional_awareness | 0.25 | partial | 0.5 |

**classification_analysis:** The response identifies that heading 8543 is inappropriate as a residual heading and correctly concludes that the EU classification under 9027.80 is most defensible based on the spectroscopy function. However, it fails to properly analyze heading 9018 versus 9027 distinction - it doesn't explain that 9018 covers instruments used ON/WITH patients while 9027 covers laboratory analytical instruments. The response mentions 'hierarchical logic' and 'primary function test' but doesn't apply the actual GRI framework or cite relevant Chapter notes. It correctly identifies spectroscopy as physical/chemical analysis but lacks the depth of technical classification analysis expected.

**uk_harmonisation_strategy:** The response proposes filing an 'eCTI application' which appears to be incorrect terminology - the correct process would be applying for a Binding Tariff Information (BTI) ruling from HMRC. It correctly identifies that the current UK classification can be challenged and calculates the financial impact (£82,500 annually). However, it doesn't mention that the HMRC advice letter is non-binding, doesn't properly cite the EU BTI as persuasive authority, and doesn't outline the full appeal process (reconsideration, then First-tier Tribunal). The strategy is directionally correct but lacks precision in the procedural details.

**cross_jurisdictional_awareness:** The response demonstrates some awareness of cross-jurisdictional issues by noting the need for 'consistent regulatory pathway' and mentions that different classifications may affect 'medical device compliance pathways.' It recognizes the EU BTI as 'supporting precedent' for the UK application. However, it fails to explain the specific regulatory implications (e.g., FDA procedures for heading 9018 vs 9027, MHRA pathways). It doesn't reference WCO classification opinions, HS Explanatory Notes, or the broader WCO framework that underlies all three jurisdictions' classification systems.

---

### CTC-027: Voluntary self-disclosure for potential ITAR violation involving deemed exports

**Difficulty:** hard | **Category:** restricted-party-screening | **Score:** 82.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| violation_assessment | 0.3 | pass | 1.0 |
| vsd_analysis | 0.35 | pass | 1.0 |
| remediation_plan | 0.35 | partial | 0.5 |

**violation_assessment:** The response correctly identifies this as a 'Deemed Export Violation under ITAR §120.17' and explains that deemed exports involve 'disclosure of controlled technical data to foreign persons in the US.' It recognizes that ITAR §123.9 requires DDTC license for deemed exports of USML items. The response notes the 'Chinese national involvement' creates 'Heightened DDTC sensitivity given current geopolitical climate,' indicating awareness of China as a proscribed destination. It correctly characterizes this as a 'Significant violation scope' due to '8 months of unauthorized access to Category XI technical data,' demonstrating understanding that duration matters for violation severity.

**vsd_analysis:** The response strongly recommends proceeding with VSD, providing solid rationale: 'Proactive disclosure likely results in reduced penalties vs. potential government discovery,' 'No prior violations strengthens VSD case,' and notes the 'Internal discovery' demonstrates functional compliance systems. It correctly cites '22 CFR §127.12 provides voluntary self-disclosure procedures' and recommends filing 'within 30 days of discovery per best practices.' The response anticipates DDTC's likely response including 'civil penalty' and 'compliance agreement with enhanced monitoring,' showing understanding of the VSD process and outcomes.

**remediation_plan:** The response provides comprehensive remediation including immediate steps (revoke access, preserve evidence, engage counsel), enhanced security measures, and compliance program improvements. However, it fails to address key elements: (1) does not mention applying for retroactive DDTC license, (2) recommends revoking access but doesn't address reassignment to non-ITAR projects to avoid appearance of witness tampering, (3) mentions auditing 'all foreign national access' but doesn't specify the broader compliance audit needed, (4) doesn't explicitly mention implementing a Technology Control Plan (TCP) as required terminology. The plan is directionally correct but misses specific ITAR remediation requirements.

---

### CTC-028: Post-Brexit Northern Ireland Protocol goods classification and dual status

**Difficulty:** hard | **Category:** documentation | **Score:** 55.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| windsor_framework_application | 0.4 | pass | 1.0 |
| documentation_requirements | 0.3 | partial | 0.5 |
| marking_and_regulatory | 0.3 | fail | 0.0 |

**windsor_framework_application:** The response correctly identifies that the shipment qualifies for the Green Lane because the customer is registered in UKIMS, goods are destined exclusively for Northern Ireland with no onward movement to Republic of Ireland/EU, and demonstrates understanding of the 'not at risk' concept. It correctly notes that Green Lane status provides simplified procedures and mentions the need for UKIMS registration as a key prerequisite. The response shows solid grasp of the Windsor Framework's green/red lane system and the conditions for qualification.

**documentation_requirements:** The response identifies many correct documents including commercial invoice, UKIMS registration number, and Green Lane Declaration. However, it fails to mention the Trader Support Service (TSS) which is mandatory for GB-NI movements and provides the simplified declaration process. It also doesn't clearly state that no customs duty is payable on green lane goods, and includes some unnecessary documentation like 'UK Supplier Declaration' that isn't specifically required for green lane movements under the Windsor Framework.

**marking_and_regulatory:** The response incorrectly states that 'DUAL MARKING REQUIRED' and that goods placed on the NI market 'generally need CE marking.' This is wrong - under the Windsor Framework, UKCA marking IS accepted in Northern Ireland for goods from Great Britain. The response fails to understand that Northern Ireland has dual market access where UKCA-marked goods from GB can be placed on the NI market without requiring CE marking. It incorrectly applies EU Machinery Directive requirements to an internal UK movement to Northern Ireland.

---
