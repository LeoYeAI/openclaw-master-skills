# Eval Results: customs-trade-compliance

**Version:** 1.0.0  
**Model:** claude-sonnet-4-20250514  
**Timestamp:** 2026-02-24T11:52:44Z  
**Aggregate Score:** 90.4%  
**Passed (>=70%):** 25/28

## Summary by Difficulty

| Difficulty | Avg Score | Count |
|---|---|---|
| Easy | 95.9% | 8 |
| Medium | 89.2% | 10 |
| Hard | 87.2% | 10 |

## Summary by Category

| Category | Avg Score | Count |
|---|---|---|
| documentation | 88.8% | 4 |
| duty-optimisation | 74.4% | 4 |
| fta-qualification | 100.0% | 3 |
| incoterms | 100.0% | 2 |
| penalties | 100.0% | 4 |
| restricted-party-screening | 81.9% | 4 |
| tariff-classification | 92.5% | 4 |
| valuation | 94.2% | 3 |

## Scenario Details

### CTC-001: Standard tariff classification of a consumer electronics product

**Difficulty:** easy | **Category:** tariff-classification | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| correct_classification | 0.35 | pass | 1.0 |
| duty_rate_and_additional_duties | 0.3 | pass | 1.0 |
| classification_rationale | 0.35 | pass | 1.0 |

**correct_classification:** Agent correctly classifies under HTS 8518.22.0000 (loudspeakers, multiple loudspeakers mounted in same enclosure). Properly applies GRI 1, explaining that heading 8518 specifically covers loudspeakers and that Bluetooth connectivity is ancillary to the primary sound reproduction function. Correctly excludes other headings (8517, 8521, 8527, 8471) with specific reasoning, including noting that it fails the Note 5 test for ADP machines under 8471.

**duty_rate_and_additional_duties:** Agent correctly identifies the MFN duty rate as Free (0%) for HTS 8518.22.0000. Properly identifies Section 301 List 3 additional duty of 25% applicable to Chinese-origin speakers. Provides detailed calculation showing FOB value ($18.50) plus freight ($1.50) = CIF value ($20.00), with Section 301 duty of $5.00 per unit, totaling $25,000 for the shipment. Correctly notes that duty applies to customs value including freight.

**classification_rationale:** Agent provides systematic GRI 1 analysis, checking Chapter 85 Notes (specifically Note 3 on loudspeakers in enclosures). Properly explains that Bluetooth connectivity and built-in amplifier are ancillary features that don't change the fundamental classification as a loudspeaker. Addresses why the lithium battery doesn't create classification issues. Distinguishes between single vs. multiple drivers for subheading determination. However, does not specifically mention checking CBP CROSS database, but the overall rationale is comprehensive and methodical.

---

### CTC-002: Selecting the correct Incoterm for a containerised ocean shipment

**Difficulty:** easy | **Category:** incoterms | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| incoterm_analysis | 0.4 | pass | 1.0 |
| customs_valuation | 0.35 | pass | 1.0 |
| practical_recommendation | 0.25 | pass | 1.0 |

**incoterm_analysis:** The response correctly identifies that FOB Hamburg is 'technically incorrect' for containerised ocean freight and provides the proper explanation: 'FOB (Free on Board) is designed for conventional break-bulk cargo where goods cross the ship's rail. In containerised shipping: Risk transfers at the container yard/terminal, not at the ship's rail.' The agent properly recommends FCA Hamburg as the appropriate alternative, explaining that it provides 'Clear risk transfer: At the container terminal when goods are handed to your nominated carrier.' This demonstrates understanding of Incoterms 2020 guidance and the practical differences between FOB and FCA for container cargo.

**customs_valuation:** The response correctly calculates US customs value on a CIF-equivalent basis. Starting with €85,000 = $92,650, it properly adds ocean freight (+$3,200) and marine insurance (+$425) to reach $96,275 customs value. The duty calculation is accurate: $96,275 × 2.0% = $1,925.50. The response explicitly states 'US customs values imports on a CIF basis (Cost + Insurance + Freight to US port). Under FOB terms, we must ADD the ocean freight and insurance to reach the customs value.' This demonstrates proper understanding of 19 CFR § 152.103 valuation requirements.

**practical_recommendation:** The response provides practical business-focused recommendations beyond just technical compliance. It suggests FCA Hamburg as the primary alternative and also presents CIP Hamburg as a second option, explaining the business advantages: 'Supplier arranges freight/insurance (may get better rates through volume contracts), Invoice value = customs value (no additions required), Cleaner customs filing.' The response includes a comparative cost analysis showing $85.29 savings under CIP structure and provides specific action items for the logistics team including immediate steps and documentation requirements. This shows practical consideration of who should arrange freight and the operational implications of each Incoterm choice.

---

### CTC-003: Basic import documentation checklist for a first-time importer

**Difficulty:** easy | **Category:** documentation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| document_list | 0.35 | pass | 1.0 |
| isf_requirements | 0.3 | pass | 1.0 |
| pga_requirements | 0.35 | pass | 1.0 |

**document_list:** The response provides a comprehensive list of required documents including commercial invoice (with specific 19 CFR § 141.86 requirements like country of origin, complete addresses, terms of sale), packing list (with carton-by-carton contents, weights, dimensions, marks/numbers), ocean bill of lading (noting original or properly endorsed copy), customs bond (mentions broker will handle bond coverage), and implicitly covers power of attorney by discussing broker relationship. The response goes beyond minimum requirements by providing specific formatting requirements for each document.

**isf_requirements:** Correctly explains ISF must be filed 24 hours before vessel loading at Chinese port (not arrival), properly identifies the urgency with 48-72 hour deadline given 10-day ETA. Lists all 10 required importer data elements (manufacturer, seller, buyer, ship-to, country of origin, HS classification, container stuffing location, consolidator, IOR number, consignee number) plus the 2 carrier elements. Accurately cites $5,000 penalty for violations and emphasizes the critical timeline with 'URGENT' warnings.

**pga_requirements:** Correctly identifies FDA as the relevant PGA for ceramic dinnerware as food contact surfaces under FDA jurisdiction. Accurately references 21 CFR 109.16 lead limits (3 ppm for flatware, 2 ppm for hollowware), mentions FDA Prior Notice requirement (2-8 hours before arrival), and notes risk of detention without compliance certificates. Also appropriately mentions CPSC requirements for children's products and General Certificate of Conformity. Provides specific lead content limits and emphasizes compliance certificate requirements from manufacturer.

---

### CTC-004: Straightforward restricted party screening false positive adjudication

**Difficulty:** easy | **Category:** restricted-party-screening | **Score:** 85.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| adjudication_analysis | 0.4 | pass | 1.0 |
| documentation_and_process | 0.3 | pass | 1.0 |
| risk_awareness | 0.3 | partial | 0.5 |

**adjudication_analysis:** The response correctly identifies this as a false positive based on multiple distinguishing factors: (1) entity type mismatch - company vs individual person, (2) geographic separation - Jordan vs Syria with no correlation, (3) surname-only match at 78% with recognition that 'Al-Hassan' is a common Levantine surname, (4) verified Jordanian commercial registration, and (5) clean transaction history from 2021 and 2023. The analysis systematically documents each factor in a structured table format and properly notes that 78% match reflects only surname similarity without additional correlating factors.

**documentation_and_process:** The response provides comprehensive documentation including: screening tool details, transaction reference, hit details in tabular format, systematic analysis of all distinguishing factors, clear conclusion (false positive), adjudicator identification fields, and explicit notation of 5-year record retention requirement per OFAC compliance. The memorandum format includes approval signature lines and notes that supporting documentation will be retained, demonstrating proper process adherence.

**risk_awareness:** The response correctly concludes false positive and confirms EAR99 classification means no export control restrictions for Jordan. However, it does not adequately address residual risk factors that should be monitored: fails to note Jordan's geographic proximity to Syria as a factor worth monitoring, and while it mentions the product is 'dual-use risk minimal,' it doesn't recommend verifying end use/end user for the water filtration equipment or note that trading companies can potentially serve as intermediaries for diversion.

---

### CTC-005: Calculating FTA duty savings under USMCA for an automotive component

**Difficulty:** easy | **Category:** fta-qualification | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| rule_of_origin_identification | 0.3 | pass | 1.0 |
| qualification_analysis | 0.4 | pass | 1.0 |
| savings_and_recommendation | 0.3 | pass | 1.0 |

**rule_of_origin_identification:** The response correctly identifies the USMCA product-specific rule for HTS 8708.70 from Annex 4-B, quoting the exact rule: 'A change to heading 8708 from any other chapter; or No required change in tariff classification, provided there is a regional value content of not less than 75 percent under the net cost method.' It properly recognizes both the tariff shift and RVC pathways as alternatives, demonstrating understanding of the specific automotive parts rules under USMCA.

**qualification_analysis:** The response performs comprehensive analysis of both qualification pathways. For tariff shift: correctly identifies that all non-originating materials (Russian/Canadian aluminium from Ch. 76, Japanese machining inserts from Ch. 82, Chinese valve stems from Ch. 84, US paint from Ch. 32) satisfy the chapter change requirement. For RVC: properly calculates VNM as $23.00 (excluding Canadian aluminium due to USMCA cumulation), computes RVC as 75.79% using net cost method, and correctly concludes qualification under both pathways. The analysis properly applies USMCA cumulation rules by treating Canadian materials as originating.

**savings_and_recommendation:** Accurately calculates annual duty savings: $11,400,000 × 2.5% = $285,000. Provides clear recommendation to proceed with USMCA claims. Addresses certification requirements by listing the nine required data elements per Article 5.2, notes importer can self-certify, specifies 5-year documentation retention requirement, and mentions customs broker instructions. Also addresses verification risk and provides practical implementation guidance including supporting documentation requirements and monitoring considerations.

---

### CTC-006: Handling a CBP CF-28 Request for Information on a routine entry

**Difficulty:** easy | **Category:** documentation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| cf28_response_quality | 0.35 | pass | 1.0 |
| significance_analysis | 0.35 | pass | 1.0 |
| risk_identification | 0.3 | pass | 1.0 |

**cf28_response_quality:** The response provides a comprehensive, professional CF-28 draft that addresses all four CBP requests with specificity: (1) complete manufacturer details including IndoSteel's name, address, GST number, and relationship disclosure, (2) detailed product specifications including 18-gauge 304 stainless steel, specific dimensions, undermount mounting type, and manufacturing process, (3) thorough country of origin documentation explicitly stating steel was melted and poured at Tata Steel Jamshedpur with detailed steelmaking process description, and (4) robust related-party valuation support including CUP analysis showing $42 price falls within $38-$48 market range, cost breakdown, and circumstances of sale test. The response is factual and professional, not defensive.

**significance_analysis:** The response correctly explains what each CF-28 request signals: manufacturer information request indicates AD/CVD screening, product specifications suggest classification verification (HTS 7324.10.0000), the melted-and-poured question probes for steel circumvention of AD/CVD orders, and related-party documentation targets transfer pricing audit. The analysis correctly identifies this as a 'multiple red flags' scenario indicating CBP scrutiny and potential focused assessment. The response demonstrates understanding that CF-28 is informational but can lead to CF-29 adverse action if inadequately addressed.

**risk_identification:** The response identifies key compliance risks: (1) potential circumvention investigation if steel origin cannot be verified (EAPA risk), (2) focused assessment incoming based on the CF-28 pattern, (3) related-party audit expansion to other entries, and (4) classification challenges. Recommends proactive steps including filing within 25 days, alerting parent company, conducting internal audit of related-party entries, and considering prior disclosure if discrepancies found. The post-CF-28 strategy section provides comprehensive risk mitigation recommendations including preparation for escalation.

---

### CTC-007: Simple customs valuation with assists provided to foreign manufacturer

**Difficulty:** easy | **Category:** valuation | **Score:** 82.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| assist_identification | 0.3 | pass | 1.0 |
| correct_calculation | 0.35 | pass | 1.0 |
| corrective_action | 0.35 | partial | 0.5 |

**assist_identification:** The response correctly identifies both the engineering drawings and custom mould as dutiable assists under 19 CFR § 152.103(d). It properly categorizes the engineering drawings as 'engineering, development, and design work' per 19 CFR § 152.103(d)(1)(i) and the mould as 'tool/die/mould provided free of charge' per 19 CFR § 152.103(d)(1)(iii). The response correctly notes that both must be added to the transaction value and does not incorrectly apply any EU exemptions for assists produced in the importing country.

**correct_calculation:** The calculation is mathematically correct: Engineering drawings $15,000 ÷ 500,000 units = $0.03 per unit; Custom mould $45,000 ÷ 500,000 units = $0.09 per unit; Total assist addition = $0.12 per unit. Corrected dutiable value = $2.80 + $0.12 = $2.92. Annual duty underpayment = ($1,460,000 - $1,400,000) × 3.4% = $2,040. The response correctly prorates both assists across the total production volume of 500,000 units rather than adding the full amount to individual shipments.

**corrective_action:** The response recommends appropriate corrective actions including halting current filing practices, conducting entry review, and implementing long-term assist management protocols. However, it focuses primarily on prior disclosure rather than the more direct remedy of Post Summary Corrections (PSCs) for unliquidated entries. While prior disclosure is mentioned as advisable, the response doesn't clearly distinguish between PSCs for recent entries within the liquidation period versus prior disclosure for older entries. The future entry procedures and internal controls recommendations are comprehensive and appropriate.

---

### CTC-008: Incoterms DDP with circular duty valuation problem

**Difficulty:** easy | **Category:** incoterms | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| circular_valuation_problem | 0.4 | pass | 1.0 |
| correct_methodology | 0.35 | pass | 1.0 |
| practical_guidance | 0.25 | pass | 1.0 |

**circular_valuation_problem:** The response clearly identifies the circular valuation problem: 'Using the DDP price of $250,000 as the customs value creates a circular valuation problem that violates customs valuation methodology. Under DDP terms, the supplier's price includes the very duties we're trying to calculate. This creates mathematical impossibility: we cannot use a price that includes duties to calculate those same duties.' The agent correctly cites 19 CFR § 152.103(a)(2) that import duties are excluded from transaction value and provides the proper regulatory framework.

**correct_methodology:** The response provides the correct algebraic methodology to solve for the CIF value: 'DDP Price = X + $4,500 + $375 + (X × 3.2%) + Fees' and works through the calculation to arrive at X = $236,209. The agent correctly accounts for freight, insurance, duty percentage, MPF, and HMF in the formula: 'X = ($250,000 - $5,450) ÷ 1.035464' and validates the components with a detailed breakdown showing how all elements sum back to the $250,000 DDP price.

**practical_guidance:** The response provides comprehensive practical guidance including specific broker instructions: 'Use $236,209 as the transaction value (CIF basis)' and 'Invoice annotation required: The commercial invoice should show: DDP price $250,000 includes estimated duties and fees. Dutiable value for customs purposes: $236,209 CIF New York.' The agent recommends requesting supplier documentation breakdown and suggests alternative approaches including changing to CIP incoterms to eliminate valuation complexity entirely.

---

### CTC-009: Multi-function device classification requiring GRI 3(b) essential character analysis

**Difficulty:** medium | **Category:** tariff-classification | **Score:** 70.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| gri_application | 0.35 | partial | 0.5 |
| essential_character_analysis | 0.4 | pass | 1.0 |
| duty_impact_and_risk | 0.25 | partial | 0.5 |

**gri_application:** The response correctly applies GRIs in order (GRI 1 first, then GRI 3) and identifies multiple candidate headings. However, it completely omits Section XVI Note 3 for composite machines, which is critical for this multi-function device. The response jumps directly to GRI 3(b) essential character without first considering whether Section XVI Note 3's 'principal function' test applies. It does check some headings against Chapter notes (correctly excludes 8471 using Section XVI Note 5 ADP criteria) but misses the most relevant note for composite machines.

**essential_character_analysis:** Excellent GRI 3(b) analysis examining all four essential character factors: value (40% smart home controller vs 35% camera), function (smart home management as primary differentiating capability), role in use (centralized control with integrated security), and consumer perception (marketed as smart home hub). Reaches reasoned conclusion that smart home controller gives essential character. Acknowledges classification ambiguity and recommends binding ruling for imports over $2M annually. The analysis is thorough and demonstrates proper understanding of essential character determination.

**duty_impact_and_risk:** Response identifies Section 301 exposure and calculates potential additional duty impact ($170,000 on 25% rate). Recommends binding ruling for high-volume imports and notes CBP could argue for camera classification. However, it does not clearly identify the duty rate difference between the candidate headings (8525 vs 8517) or calculate the specific duty differential between classifications. The Section 301 analysis is present but incomplete - states potential coverage without definitively checking List 3 status.

---

### CTC-010: USMCA qualification failure due to non-originating material from outside the zone

**Difficulty:** medium | **Category:** fta-qualification | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| qualification_analysis | 0.35 | pass | 1.0 |
| exposure_calculation | 0.3 | pass | 1.0 |
| corrective_action | 0.35 | pass | 1.0 |

**qualification_analysis:** The response correctly determines that the handbags do NOT qualify for USMCA. It accurately identifies the product-specific rule: 'A change to heading 4202 from any other heading except from heading 4104-4107 (tanned leather)' and correctly recognizes that the Italian-tanned cowhide leather (HS 4107.12, 55% of material cost) falls within the excluded range 4104-4107. The response explicitly states this creates a 'Fatal Flaw' because 'No tariff shift occurs for the primary material component' and explains that 'The rule is designed to prevent simple assembly operations using pre-tanned leather from conferring USMCA origin.' This demonstrates proper understanding of the exceptions list in the product-specific rule.

**exposure_calculation:** The response provides a comprehensive exposure calculation: $170,000 in unpaid duties (8.0% × $2,125,000), $8,500 in estimated interest (5% × $170,000), negligence penalty exposure of $340,000 (2× lost revenue), and gross negligence exposure of $680,000 (4× lost revenue). It correctly identifies that prior disclosure caps penalty at interest only ($8,500 vs potential $340,000+) and mentions approximately 35 entries affected. The calculation methodology is sound and includes both the duty owed and penalty exposure under 19 USC § 1592.

**corrective_action:** The response recommends all key corrective actions: (1) immediately halt all USMCA claims and file future entries at MFN rate, (2) file prior disclosure within 5 business days before CBP discovers the issue, (3) tender $178,500 in unpaid duties plus interest. It provides detailed prior disclosure key points including nature of violation, affected entries, circumstances, corrective actions, and tender amount. The response also analyzes go-forward options including continuing Mexico sourcing at MFN rate vs. supply chain restructuring to source USMCA-qualifying leather. It includes comprehensive compliance program enhancements and emphasizes timeline criticality with specific ROI analysis ($8,500 vs $340,000+ penalty exposure).

---

### CTC-011: Related-party customs valuation with transfer pricing conflict

**Difficulty:** medium | **Category:** valuation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| valuation_analysis | 0.35 | pass | 1.0 |
| eapa_response | 0.3 | pass | 1.0 |
| strategic_recommendation | 0.35 | pass | 1.0 |

**valuation_analysis:** The response correctly identifies the core issue: the $180/kg transfer price is 18-25% below market ($220-$240/kg), creating a strong presumption that the related-party relationship influenced the price. It properly applies the 'circumstances of sale' test, noting that the significant discount to market undermines the argument that the relationship didn't influence price. The response recognizes that while TNMM is acceptable for tax purposes, CBP requires that related-party prices approximate 'test values' - specifically transaction values of identical/similar goods sold to unrelated parties. It correctly states the transfer price is 'likely NOT defensible as transaction value' and provides the proper regulatory framework analysis.

**eapa_response:** The response demonstrates understanding that while EAPA is typically for AD/CVD evasion, CBP can investigate undervaluation as duty evasion. It recommends immediate retention of trade counsel, notes CBP has 300 days to investigate with potential interim measures within 90 days, and correctly identifies the evidence standard ('reasonably suggests' evasion). The response advocates proactive engagement rather than waiting for CBP contact, and specifically recommends considering prior disclosure 'before CBP commences a formal investigation.' It provides a comprehensive timeline and strategic approach for responding to the allegation.

**strategic_recommendation:** The response provides a multi-track approach with clear phases: immediate damage assessment, valuation defense preparation, and strategic decision point. It correctly calculates penalty exposure scenarios: prior disclosure caps exposure at ~$482K (duty + interest) vs. defense scenario at ~$1.3M (duty + negligence penalties). It recommends immediate adjustment of transfer price to market levels ($230/kg) for future entries, filing prior disclosure within 10 days, and long-term coordination between tax and trade functions. The ROI calculation ($833K in avoided penalties) demonstrates quantitative analysis. The response addresses both immediate EAPA threat and structural tax-customs valuation conflict through recommended process improvements.

---

### CTC-012: Restricted party screening true positive — Entity List match

**Difficulty:** medium | **Category:** restricted-party-screening | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| hit_adjudication | 0.25 | pass | 1.0 |
| compliance_actions | 0.4 | pass | 1.0 |
| fdpr_analysis | 0.35 | pass | 1.0 |

**hit_adjudication:** Response correctly identifies this as a TRUE POSITIVE with clear evidence: '99% (exact match)', 'Perfect match (Guiyang, China)', and 'This is definitively the same entity listed on the BIS Entity List'. Immediately blocks the transaction with 'FULL STOP — This transaction is prohibited and must be blocked immediately.' No attempt to find reasons to clear the hit or proceed while investigating.

**compliance_actions:** Response comprehensively covers required actions: (1) Blocks transaction immediately ('Do not process the purchase order', 'Do not provide technical specifications'), (2) Correctly identifies ECCN 3B001 requires licence and Entity List adds separate layer for all EAR items, (3) Notes presumption of denial policy means 'BIS will almost certainly deny any licence application', (4) Instructs to 'Notify sales team that this customer is prohibited' and cease all engagement, (5) Addresses deemed export risk by prohibiting sharing of 'technical specifications' and 'technical discussions', (6) Includes comprehensive FDPR analysis as required.

**fdpr_analysis:** Provides thorough FDPR analysis explaining: (1) 'Direct products of US technology/software' and 'Direct products of plants/facilities' are controlled, (2) 'Worldwide application — applies regardless of the country of manufacture', (3) Notes 'Even if your company were non-US, any equipment incorporating US-origin components, technology, or software would be subject to US export controls', (4) Specifically mentions Entity List FDPR implications, (5) Correctly concludes that even non-US manufactured equipment cannot be shipped without BIS licence. Demonstrates clear understanding that FDPR extends US jurisdiction to foreign-made products.

---

### CTC-013: Prior disclosure decision after discovering systematic classification error

**Difficulty:** medium | **Category:** penalties | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| disclosure_decision | 0.3 | pass | 1.0 |
| exposure_calculation | 0.35 | pass | 1.0 |
| filing_steps | 0.35 | pass | 1.0 |

**disclosure_decision:** The response correctly recommends filing prior disclosure immediately with strong rationale. It identifies this as a 'textbook prior disclosure scenario' with material duty shortfall of $214,400 across 85 entries over 14 months. The agent correctly notes no CBP investigation has commenced (internal audit discovery), calculates substantial financial benefit ($631,400 savings), and recognizes the systematic nature could support gross negligence characterization. The recommendation is supported by proper legal analysis of 19 CFR § 162.74 requirements.

**exposure_calculation:** The response provides comprehensive financial exposure calculations for both scenarios. WITHOUT disclosure: correctly calculates negligence penalty as 2× lost revenue ($428,800) OR 20% dutiable value ($640,000), applies the higher amount per CBP practice, totaling $854,400 with duties. WITH disclosure: properly applies 19 CFR § 162.74 penalty cap at interest only for negligence ($8,600) plus duties ($214,400) = $223,000 total. Net savings calculation of $631,400 is accurate. The analysis correctly distinguishes between duty owed (always payable) and penalty exposure.

**filing_steps:** The response provides detailed, sequenced filing steps including: (1) retaining trade counsel, (2) assembling complete entry documentation with spreadsheet of all 85 entries, (3) preparing proper tender of $214,400 duties plus interest via certified check, (4) drafting disclosure letter with required elements (nature of violation, circumstances, corrective measures), (5) filing with appropriate CBP office via certified mail. Also includes immediate corrective actions (halt current classification, verify no CBP investigation) and post-filing compliance measures (independent classification verification SOP). The 16-day timeline and specific documentation requirements demonstrate operational knowledge of the prior disclosure process.

---

### CTC-014: Evaluating an FTZ admission strategy for inverted tariff relief

**Difficulty:** medium | **Category:** duty-optimisation | **Score:** 80.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| ftz_benefit_analysis | 0.4 | partial | 0.5 |
| operational_requirements | 0.3 | pass | 1.0 |
| risk_assessment | 0.3 | pass | 1.0 |

**ftz_benefit_analysis:** The response correctly identifies inverted tariff relief as the primary benefit and calculates $720,000 in savings from the 2.0% component duty differential on domestic shipments. It also identifies scrap duty relief ($27,000) and mentions export benefits. However, it significantly undercalculates the total opportunity. The response calculates savings only on domestic shipments (80%) rather than recognizing that ALL component duties are eliminated through the inverted tariff structure - the full $899,000 in component duties. It also miscalculates export savings by stating they're 'already captured' when they should be separate. The methodology is sound but the quantification misses the full scope of FTZ benefits.

**operational_requirements:** The response comprehensively covers operational requirements: Form 214 application for production authority (4-6 months), zone designation timeline (6-9 months), detailed documentation requirements including production plan and security procedures. It correctly identifies privileged foreign status (PFS) inventory tracking, weekly inventory reconciliation per 19 CFR § 146.23, consumption entries for domestic sales, and FTZ-compliant inventory management systems. The response includes specific regulatory citations and addresses manufacturing restrictions, yield requirements, and system integration needs. Setup and operating cost estimates are reasonable and detailed.

**risk_assessment:** The response identifies key risks including production authority scope limitations, mixed-status goods complexity with specific examples, regulatory changes (Section 301 extension to finished tablets), enhanced CBP scrutiny, and zone-to-zone transfer limitations. It correctly notes that if finished goods become dutiable, the inverted tariff benefit disappears. The response includes appropriate mitigation strategies for each risk. However, it could have mentioned AD/CVD limitations and been more explicit about Section 301 applicability to current components, but the overall risk framework is comprehensive and operationally sound.

---

### CTC-015: EU-UK TCA origin determination for manufactured goods post-Brexit

**Difficulty:** medium | **Category:** fta-qualification | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| tca_rule_application | 0.4 | pass | 1.0 |
| insufficient_processing_check | 0.3 | pass | 1.0 |
| declaration_and_documentation | 0.3 | pass | 1.0 |

**tca_rule_application:** The response correctly identifies and applies the TCA product-specific rule for HS 8711.60, requiring 'value of all non-originating materials used does not exceed 45% of the ex-works price.' It properly applies bilateral cumulation by counting the German frame (15%) as originating EU content, reducing non-originating content from 70% to 55%. The calculation correctly identifies Chinese battery (35%) + Taiwanese motor (20%) + Japanese controller (15%) = 70% non-originating content, which exceeds the 45% threshold. The response also properly considers the tolerance rule (10%) but concludes it doesn't rescue qualification since 55% still exceeds 50% (45% + 10%).

**insufficient_processing_check:** The response explicitly addresses TCA Article ORIG.7 'Operations Not Conferring Origin' and evaluates whether the Birmingham assembly operations constitute insufficient processing. It notes that 'simple assembly of parts to constitute a complete product' is listed as insufficient processing but analyzes that bicycle assembly involves 'significant technical integration (electrical system integration, mechanical fitting, calibration, safety testing)' which likely constitutes 'sufficient processing.' The response correctly notes this is independently irrelevant since the 45% value rule failure is disqualifying.

**declaration_and_documentation:** The response correctly explains TCA origin declaration requirements: consignments ≤ €6,000 can use any exporter declaration, while consignments > €6,000 require REX registration. It provides the specific REX registration process through HMRC Online Services and includes the exact prescribed declaration text with REX number format. The response correctly identifies that at the unit values involved, REX registration would be required. It also addresses compliance documentation requirements including retaining bill of materials and supplier origin certifications for audit purposes.

---

### CTC-016: Duty drawback claim for re-exported imported components

**Difficulty:** medium | **Category:** duty-optimisation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| drawback_type_identification | 0.3 | pass | 1.0 |
| recovery_calculation | 0.35 | pass | 1.0 |
| filing_requirements | 0.35 | pass | 1.0 |

**drawback_type_identification:** The response correctly identifies manufacturing drawback under 19 USC § 1313(a) as the applicable type. It clearly states the statutory requirements are met: imported bearings are used as materials in manufacturing, the gearboxes are a different article with new character/use, and they're exported within 5 years. The response correctly notes this is NOT substitution drawback because bearings are physically incorporated. It also correctly identifies the 99% recovery rate per 19 USC § 1313(r). The response demonstrates understanding of TFTEA simplifications eliminating specific entry-to-entry matching requirements.

**recovery_calculation:** The response provides accurate calculations: Annual recovery of $320,760 ($1,080,000 × 30% × 99%) and 3-year recovery of $962,280. It correctly applies the 30% export ratio to determine the portion eligible for drawback and uses the proper 99% drawback rate. The response also notes the important caveat that calculations must be 'adjusted for consumed quantities' if bearing consumption varies by gearbox model, showing awareness that the blanket 30% ratio may need refinement based on actual manufacturing records. It mentions the 5-year filing deadline constraint.

**filing_requirements:** The response comprehensively outlines filing requirements: CBP Form 7539 filed annually, CBP Form 7531 for manufacturer registration, detailed documentation requirements including import records (Form 7501, invoices, duty payment proof), manufacturing records (BOMs, production records, inventory accounting), and export documentation (AES filings, commercial invoices, bills of lading). It correctly references 19 CFR § 191.26 record-keeping standards requiring identity, quantity, location, and disposition tracking. The response acknowledges TFTEA simplifications eliminating entry-to-entry matching while maintaining manufacturing documentation requirements, and recommends specialized drawback counsel for the complex filing process.

---

### CTC-017: Dual-use goods classification — EAR jurisdiction and ECCN determination

**Difficulty:** medium | **Category:** restricted-party-screening | **Score:** 42.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| eccn_classification | 0.4 | fail | 0.0 |
| licence_determination | 0.35 | partial | 0.5 |
| due_diligence | 0.25 | pass | 1.0 |

**eccn_classification:** The agent initially classifies the camera under 6A003.b.4.b but then contradicts itself by concluding it doesn't meet either 6A003.b.4.a or 6A003.b.4.b criteria, and switches to 6A993.a. This fundamental confusion about the classification thresholds is incorrect. The camera with 640×480 resolution (307,200 pixels) and 0.03°C NETD clearly meets the 6A003.b.4.b threshold of NETD ≤0.05K at 300K and >111,000 elements. The agent also incorrectly states that 6A003.b.4.a requires 'more than 4 × 10⁶ active pixels' when the actual threshold is much lower. The final classification of 6A993.a is wrong - this high-performance camera belongs in 6A003.

**licence_determination:** The agent correctly identifies that a license is required for the UAE under AT controls for 6A993, but this is based on the incorrect classification. Under the correct 6A003 classification, the analysis should focus on NS/RS controls rather than AT controls. The agent shows awareness of the Commerce Country Chart and license exception concepts, and correctly concludes a license is needed, but the regulatory pathway analysis is flawed due to the misclassification. The discussion of processing times and approval likelihood shows practical knowledge.

**due_diligence:** The agent provides comprehensive due diligence analysis including: (1) restricted party screening against BIS Entity List, DPL, and other lists, (2) verification of the customer's business legitimacy through UAE business license and D&B reports, (3) questioning the 50-unit order size and requesting customer information, (4) addressing re-export/diversion risks specific to UAE free trade zones and proximity to Iran, (5) requiring written end-use certifications with specific restrictions, and (6) implementing post-export monitoring. The analysis demonstrates understanding of dual-use technology risks and appropriate risk mitigation measures.

---

### CTC-018: Handling a CBP penalty assessment for negligent misclassification

**Difficulty:** medium | **Category:** penalties | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| classification_evaluation | 0.3 | pass | 1.0 |
| response_strategy | 0.4 | pass | 1.0 |
| response_drafting | 0.3 | pass | 1.0 |

**classification_evaluation:** The agent correctly recognizes the unusual situation where CBP's reclassification results in a LOWER duty rate (2.6% vs 3.9%) and that the company actually OVERPAID duties by $35,100. Crucially, the agent understands that penalties can still be assessed despite no revenue loss, stating 'The government cannot assess penalties for lost revenue when no revenue was lost' but still analyzing the classification dispute on its merits. The agent provides a detailed GRI analysis supporting both headings, examines Chapter 94 Note 2 that includes 'luminaires,' and notes that Chapter 85 Note 1(k) excludes luminaires covered by Chapter 94. The agent recognizes this is a genuine classification dispute in the LED lighting area and recommends independent analysis rather than automatically conceding.

**response_strategy:** The agent develops a sophisticated multi-track strategy. Phase 1 prioritizes challenging the penalty calculation error (noting the statutory maximum should be $0 when no revenue was lost). Phase 2 addresses the classification dispute as a separate but secondary issue. Phase 3 includes mitigation arguments. The strategy recognizes the 30-day deadline and includes both immediate and long-term action items. The agent properly identifies that even if some penalty were appropriate, the circumstances (clean compliance history, reasonable basis for classification, broker involvement, industry standards) support mitigation. The response strategy addresses both the mathematical error in penalty calculation and the substantive classification dispute.

**response_drafting:** The agent drafts a comprehensive formal response with proper structure: case number reference, detailed penalty calculation challenge showing statutory maximum should be $0, thorough classification analysis using GRI 1 with specific references to Chapter notes, circumstances supporting negligence defense including reasonable care factors, and specific requested relief (cancel penalty, confirm correct calculation, issue refund). The draft includes supporting documentation requirements and addresses the strongest mitigation factor (no revenue loss). The response is professionally structured for submission to CBP's Fines, Penalties and Forfeitures Officer and includes the mathematical calculations demonstrating the penalty assessment error.

---

### CTC-019: Transshipment circumvention — AD/CVD evasion investigation on steel products

**Difficulty:** hard | **Category:** penalties | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| eapa_process_knowledge | 0.25 | pass | 1.0 |
| substantial_transformation_analysis | 0.35 | pass | 1.0 |
| operational_and_financial_actions | 0.4 | pass | 1.0 |

**eapa_process_knowledge:** The response demonstrates detailed EAPA process knowledge including: (1) 30-day deadline for interim measures challenge, (2) interim measures requiring cash deposits of 265.79%, (3) retroactive application if upheld ('Retroactive AD/CVD assessment on 2 years of imports'), (4) 300-day final determination timeline implied in medium-term planning, and (5) high stakes nature with accurate financial calculations. The response correctly identifies this as enforcement action requiring specialized trade counsel and shows understanding of CBP's authority to impose interim measures pending investigation.

**substantial_transformation_analysis:** The response provides sophisticated substantial transformation analysis specific to steel processing: (1) correctly identifies the core legal question as whether cold-rolling constitutes substantial transformation, (2) analyses processing complexity including thickness reduction (15-40%), improved surface finish, altered metallurgical properties, (3) applies the 'name, character, use' test specifically to HRC vs CRC, (4) identifies critical thresholds (>35% Vietnamese value-added, <70% Chinese input cost), (5) recognizes CBP's skeptical position on minimal processing operations, and (6) notes suspicious pricing ($680/MT below legitimate Vietnamese production costs). The analysis goes beyond generic substantial transformation concepts to steel-specific EAPA context.

**operational_and_financial_actions:** The response comprehensively addresses operational and financial actions: (1) immediate halt of new orders and cash preservation strategy, (2) accurate cash impact calculation ($1.8M per shipment, $14.4M annually), (3) retention of specialized EAPA counsel with specific firm recommendations, (4) 30-day timeline for interim measures challenge, (5) detailed evidence collection from Vietnamese supplier including production records and origin documentation, (6) immediate supply chain diversification with specific alternatives (US domestic, USMCA-qualifying Mexican, Korean/Japanese sources), (7) financial risk scenarios ranging from $500K legal costs to $30-60M total exposure, and (8) structured timeline for immediate, medium-term, and long-term actions. The response treats this as the high-stakes compliance emergency it represents.

---

### CTC-020: Complex classification of a multi-material composite product crossing chapter boundaries

**Difficulty:** hard | **Category:** tariff-classification | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| systematic_gri_application | 0.35 | pass | 1.0 |
| essential_character_determination | 0.4 | pass | 1.0 |
| binding_ruling_recommendation | 0.25 | pass | 1.0 |

**systematic_gri_application:** The response systematically applies GRIs in strict order. GRI 1: Correctly identifies and analyzes Chapter 95 Note 1 as creating specific inclusion for sports equipment that overrides exclusions in Chapters 40, 84, and 85. Reviews heading 9506.91 and finds the product prima facie described. Properly analyzes competing headings (4016, 8471, 8543, 6307) and explains why they fail under GRI 1. States 'GRI 2 Analysis: Not applicable - this is a complete, finished article' and 'GRI 3 Analysis: Not reached - GRI 1 provides a single, unambiguous classification.' The methodology is correct - when GRI 1 provides clear classification, subsequent GRIs are not applied.

**essential_character_determination:** The response provides comprehensive essential character analysis using all four factors: (1) Function - analyzes both yoga practice surface function and electronic feedback function, concluding electronics enhance core function rather than change it; (2) Value - acknowledges electronics represent 58% of FOB cost but doesn't let this override other factors; (3) Physical structure - notes 70% rubber base provides structural foundation; (4) Consumer perception/marketing - emphasizes product is sold and used as yoga/fitness equipment. Concludes electronics are 'integrated accessories' that enhance traditional yoga mat function. While the response concludes GRI 1 resolves the classification, the essential character analysis is thorough and supports the conclusion.

**binding_ruling_recommendation:** Strongly recommends seeking a binding ruling with detailed rationale: (1) Financial impact of $1.8M annual imports with potential 8.3% duty differential; (2) Precedent value for similar smart fitness products; (3) Audit protection against future CBP challenges; (4) Market expansion certainty. Provides specific ruling request strategy including emphasis on Chapter 95 Note 1, technical specifications, marketing materials, and addressing potential 8471 arguments. Acknowledges 'Medium Risk Factors' including high electronics value and novel product category. Calculates total duty impact and notes limited downside risk, making strategic case for ruling request.

---

### CTC-021: First sale valuation challenge with related-party middleman

**Difficulty:** hard | **Category:** valuation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| first_sale_validity | 0.4 | pass | 1.0 |
| exposure_assessment | 0.3 | pass | 1.0 |
| recommended_action | 0.3 | pass | 1.0 |

**first_sale_validity:** The response correctly identifies all fatal flaws: (1) Related party transaction - 'HK subsidiary is wholly-owned by your parent company, making this a related-party transaction throughout the supply chain'; (2) Lack of commercial substance - 'No inventory risk: Goods never physically enter Hong Kong, No market risk: Captive customer'; (3) Assists bypass middleman - 'You provide product designs and specifications directly to the Chinese factory, bypassing the HK subsidiary'; (4) Systematic analysis using Nissho Iwai requirements showing failure on all three tests. Concludes programme is 'indefensible' with multiple fatal flaws.

**exposure_assessment:** Accurately calculates financial exposure: '$612,000 in underpaid duties over 3 years, negligence penalty: $612,000 (1× lost revenue), gross negligence penalty: $1,224,000 (2× lost revenue), fraud penalty: Up to $5.7M'. Correctly identifies assists as separate violation: 'Assuming $5-8/unit in design assists, the effective first sale value becomes $70-73/unit'. Quantifies prior disclosure benefit: 'With prior disclosure: $612,000 (duties) + interest ≈ $650,000 total exposure vs Without prior disclosure: $1.2M - $2.4M+ penalty risk'.

**recommended_action:** Provides comprehensive action plan: (1) 'Cease claiming first sale treatment immediately on all new entries'; (2) 'File a prior disclosure within 60 days' with detailed reasoning; (3) Structural fixes including 'Direct Chinese factory sales to US' or 'HK entity takes title and inventory risk: Minimum 30-day inventory holding'; (4) 'Implement robust valuation controls' including assist tracking. Correctly warns this is 'not a borderline case' and recommends immediate cessation of the programme.

---

### CTC-022: UFLPA detention — tracing cotton supply chain through multiple tiers

**Difficulty:** hard | **Category:** documentation | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| evidence_requirements | 0.35 | pass | 1.0 |
| supply_chain_tracing | 0.35 | pass | 1.0 |
| contingency_planning | 0.3 | pass | 1.0 |

**evidence_requirements:** The response correctly identifies the 'clear and convincing evidence' standard and details comprehensive evidence requirements: complete supply chain mapping from cotton farm through yarn spinner, fabric mill, to garment manufacturer; lot-level traceability linking specific cotton purchases to yarn lots to fabric batches to finished garments; third-party audit reports on labor conditions; isotopic testing from recognized labs (Oritain, Applied DNA Sciences); and production records correlating dates across all tiers. Explicitly notes that self-certifications are insufficient and requires independent verification, demonstrating understanding that CBP has rejected supplier declarations alone.

**supply_chain_tracing:** Provides systematic timeline-based methodology: Days 1-3 immediate supplier engagement with Dhaka Garments for specific lot numbers; Days 4-14 tier-by-tier excavation from fabric mills to yarn spinners to cotton origins; parallel isotopic testing deployment; and structured evidence compilation by Day 28. Correctly identifies that traceability must link the detained 24,000 units to specific fabric lots, then to specific yarn purchases, then to cotton origin. Acknowledges that broken chain at any tier defeats the rebuttable presumption. Timeline accounts for 30-day CBP deadline with extension request strategy.

**contingency_planning:** Addresses multiple contingencies with specific actions: Scenario A/B/C analysis with probability assessments; re-export to Canada/EU markets if Xinjiang cotton confirmed; isotopic testing + legal challenge if documentation incomplete; commercial mitigation calculating reduced revenue impact ($1.2M to $400K); destruction/abandonment as final option; cost-benefit analysis of each strategy; and recommendation for long-term UFLPA compliance program. Addresses client's 45-day deadline constraint and provides expected value calculations for decision-making. Includes immediate re-export negotiations as parallel track to documentation efforts.

---

### CTC-023: Optimising duty exposure across multiple FTAs for a multi-origin product

**Difficulty:** hard | **Category:** duty-optimisation | **Score:** 37.5%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| multi_fta_analysis | 0.4 | partial | 0.5 |
| supply_chain_optimisation | 0.35 | partial | 0.5 |
| financial_impact_assessment | 0.25 | fail | 0.0 |

**multi_fta_analysis:** The response correctly identifies RCEP qualification for Japan and notes UK's CPTPP status, but contains several errors: (1) States Japan MFN is 0% when it's actually 2.5%, undermining the RCEP benefit calculation; (2) Incorrectly states UK is 'negotiating' CPTPP accession when UK already acceded in 2023; (3) For RCEP calculation, includes 'Japanese servo motors under cumulation (26.2%)' but the BOM shows Japanese motors at 26.2% - this double-counting inflates the RVC to 52.4%; (4) Does not properly analyze which specific components are originating vs non-originating under each FTA's cumulation rules; (5) EU and US analysis is correct (no applicable FTAs) but overstates potential savings by not noting the low MFN rates make FTA benefits modest.

**supply_chain_optimisation:** The response identifies some restructuring opportunities but with significant issues: (1) Correctly suggests Vietnam operations for EU market access via EU-Vietnam FTA; (2) Proposes Mexico operations for USMCA qualification, but incorrectly states German gears would qualify as North American content through 'EU-Mexico FTA bilateral cumulation' - this is not how USMCA cumulation works; (3) Suggests sourcing from RCEP partners to improve qualification, which is directionally correct; (4) However, misses the most obvious optimization: replacing Chinese aluminum housing (7.6% non-originating) with RCEP/CPTPP member sourcing would be the easiest swap to improve qualification margins; (5) Does not analyze the specific impact of Taiwanese PCB controllers (9% non-originating under both RCEP and CPTPP).

**financial_impact_assessment:** The financial analysis contains multiple calculation errors and unrealistic projections: (1) Claims Japan annual savings of $0 but states MFN is 0% when it's actually 2.5%, missing $210,000 in potential RCEP savings; (2) UK calculation uses wrong volume (shows $84K vs $3.36M sales when BOM shows 800 units); (3) Payback calculations are fundamentally flawed - shows 19-year payback for EU ($2M investment for $107K savings) and 14-year for US ($3M for $210K), yet concludes 'combined payback of 12.8 years'; (4) Does not properly weigh restructuring costs against duty savings - the analysis shows negative ROI for most strategies yet still recommends implementation; (5) Overstates total addressable savings at $401K when several markets have low MFN rates that may not justify program costs.

---

### CTC-024: Responding to a retroactive Section 301 exclusion expiration

**Difficulty:** hard | **Category:** duty-optimisation | **Score:** 80.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| immediate_actions | 0.3 | pass | 1.0 |
| medium_term_strategies | 0.4 | partial | 0.5 |
| strategic_framework | 0.3 | pass | 1.0 |

**immediate_actions:** The response identifies key immediate actions within the 60-day window: (1) Accelerated stockpiling of 150% normal quarterly demand over 45 days with detailed financial analysis showing $787,500 in duty savings versus $47K carrying cost for net benefit of $740,500. (2) Logistics acceleration including shift to air freight for final 30 days. (3) Detailed execution requirements including supplier engagement, customs broker coordination, and ISF filing. The response provides comprehensive financial calculations and practical implementation steps, though it doesn't specifically mention filing a new exclusion request with USTR or government affairs advocacy.

**medium_term_strategies:** The response evaluates multiple strategies including FTZ, Vietnam manufacturing transition, and component analysis. However, it makes a critical error regarding FTZ benefits for Section 301 tariffs - it suggests FTZ provides 'duty deferral benefit' and 'inverted tariff opportunity' when Section 301 tariffs actually apply when goods enter US commerce from the FTZ, providing no relief. The Vietnam transition analysis is sound with 15-20% cost premium versus 25% tariff elimination. The component analysis for inverted tariff is detailed but based on the incorrect premise that FTZ helps with Section 301. Missing comparative financial analysis of alternative sourcing locations like Germany or Israel.

**strategic_framework:** Presents a comprehensive four-phase strategic framework: Phase 1 immediate stockpiling, Phase 2 FTZ strategy, Phase 3 supply chain restructuring to Vietnam, Phase 4 US assembly with substantial transformation. Includes detailed financial impact analysis showing total cost reduction from $2.1M to $850K (60% mitigation). Provides specific timelines, investment requirements, ROI calculations, and risk assessments. Addresses customer pricing considerations and includes contingency planning. The framework gives the CEO multiple strategic options with clear financial modeling and implementation roadmaps.

---

### CTC-025: Complex prior disclosure involving multiple violation types across related entities

**Difficulty:** hard | **Category:** penalties | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| prior_disclosure_strategy | 0.35 | pass | 1.0 |
| penalty_exposure_analysis | 0.3 | pass | 1.0 |
| compliance_programme_implementation | 0.35 | pass | 1.0 |

**prior_disclosure_strategy:** The response recommends filing three separate but simultaneous prior disclosures covering ALL violations, which is strategically sound. It correctly identifies the urgency created by the competitor's Focused Assessment, stating 'File within 72 hours' due to 'industry FA activity and the magnitude of exposure create imminent investigation risk.' The response properly structures each filing with penalty calculations, rationale for separate filings, and supporting documentation requirements. It correctly notes that prior disclosure is an admission ('Never admit fraud — position all violations as negligent oversights') and addresses filing logistics including the $921K total tender amount with interest calculations. The strategy demonstrates understanding that systematic compliance failures warrant comprehensive disclosure rather than piecemeal remediation.

**penalty_exposure_analysis:** The response provides accurate penalty calculations for both scenarios. WITHOUT prior disclosure: correctly applies 2× lost revenue formula resulting in $1.772M total exposure across all violations. WITH prior disclosure: correctly calculates principal plus interest totaling $921K. The table clearly shows savings of $851K from prior disclosure. The response correctly applies 19 USC § 1592 penalty formulas and recognizes that 'the absence of any compliance infrastructure' increases culpability characterization. It properly calculates interest on each violation separately ($18K, $6K, $11K) and provides the total tender calculation. The analysis demonstrates understanding that each violation may be assessed independently and that systematic failures could elevate the penalty characterization.

**compliance_programme_implementation:** The response provides a comprehensive compliance programme addressing all three violation types with specific controls: (1) Classification: 'licensed customs broker for independent classification,' 'mandatory ruling request process,' and 'classification database with GRI analysis documentation'; (2) Assists: 'assist identification checklist for procurement team' and 'quarterly reconciliation review for all related-party transactions'; (3) FTA: 'supplier certification requirements' and 'qualification matrix for all Mexico-sourced products with BOM traceability.' The programme includes organizational structure (trade compliance reporting to General Counsel), technology implementation, training programmes for all relevant functions, and ongoing monitoring with specific metrics ('>98% entry accuracy rate'). The timeline is realistic with Phase 1 (0-30 days) for immediate controls and Phase 2 (30-90 days) for systematic infrastructure. References to CBP's enforcement framework and industry best practices demonstrate domain expertise.

---

### CTC-026: Multi-jurisdictional origin dispute with conflicting classification across EU, UK, and US

**Difficulty:** hard | **Category:** tariff-classification | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| classification_analysis | 0.35 | pass | 1.0 |
| uk_harmonisation_strategy | 0.4 | pass | 1.0 |
| cross_jurisdictional_awareness | 0.25 | pass | 1.0 |

**classification_analysis:** The response provides thorough analysis of all three classifications: (1) Correctly identifies EU 9027.80 as covering 'instruments for physical or chemical analysis' and notes the device performs spectroscopic analysis, which is fundamentally physical/chemical analysis. Cites Chapter 90 Note 3 supporting instruments remaining in Chapter 90 regardless of application. (2) Properly characterizes US 9018.19 as focusing on clinical application vs analytical function. (3) Correctly identifies UK 8543.70 as a residual heading for electrical apparatus 'not elsewhere specified' and argues 9027 is more specific. Applies GRI 3(a) analysis stating '9027 is more specific than 8543.' Concludes EU classification is most defensible with proper essential character analysis under GRI 3(b), identifying spectroscopy as the essential character-giving component based on function, value, and technical complexity.

**uk_harmonisation_strategy:** Develops comprehensive UK strategy: (1) Correctly identifies that 'HMRC advice letter is non-binding' and recommends filing 'a BTI request with HMRC' for formal ruling. (2) Provides specific technical arguments including that 'heading 8543.70 is a residual heading for electrical apparatus not elsewhere specified - but 9027 IS more specific' and applies GRI 3(a). (3) Recommends 'EU BTI ruling as persuasive authority' in supporting evidence package. (4) Includes detailed supporting evidence package with technical specifications, manufacturing cost breakdown, and comparison products. (5) Notes proper timeline (120 days for BTI decision) and interim procedure (continue paying 2.2% but note dispute). Calculates annual exposure at £82,500 and mentions appeal options if BTI denied.

**cross_jurisdictional_awareness:** Demonstrates strong cross-jurisdictional awareness: (1) Recognizes different regulatory implications beyond duty rates, noting '9027 classification may simplify future regulatory pathways for analytical variants' and 'eliminates confusion with purely medical device import requirements.' (2) Recommends coordinated timing strategy to 'avoid jurisdictions citing each other's adverse decisions' showing awareness of precedential effects. (3) Notes 'Post-Brexit, UK tariff schedule substantially mirrors EU TARIC structure' and uses EU BTI as persuasive authority. (4) Emphasizes 'Global classification consistency: reduces audit risk' and notes benefits of harmonized positioning. (5) Provides risk mitigation for parallel proceedings and considers broader compliance implications including audit probability.

---

### CTC-027: Voluntary self-disclosure for potential ITAR violation involving deemed exports

**Difficulty:** hard | **Category:** restricted-party-screening | **Score:** 100.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| violation_assessment | 0.3 | pass | 1.0 |
| vsd_analysis | 0.35 | pass | 1.0 |
| remediation_plan | 0.35 | pass | 1.0 |

**violation_assessment:** The response correctly identifies this as a deemed export violation under ITAR § 120.17 (defining export to include disclosure to foreign nationals within the US) and § 127.1 (civil penalties). It properly recognizes that Chinese national access to USML Category XI technical data constitutes an export to China without required authorization, notes the 8-month duration as significant, and correctly states this is a strict liability violation regardless of the engineer's intent or connections. The response demonstrates understanding that no physical export is required for ITAR violations.

**vsd_analysis:** The response strongly recommends filing a VSD immediately with solid rationale: (1) cites DDTC Policy Memo stating they 'generally will not seek civil penalties when violations are voluntarily disclosed,' (2) notes presumption against criminal referral for VSDs, (3) identifies massive penalty exposure ($1.3M per violation potentially totaling over $300M theoretically), (4) recognizes China-related deemed exports are under 'intense scrutiny,' and (5) notes internal discovery means DDTC is not yet aware. The response correctly outlines VSD requirements under ITAR § 127.12 and provides realistic timeline expectations for DDTC response.

**remediation_plan:** The response provides comprehensive remediation including: (1) immediate access revocation while preserving records, (2) comprehensive audit of all 35 foreign nationals' access, (3) detailed Technology Control Plan with IT system flags, automated monitoring, and FSO quarterly reviews, (4) enhanced training programs including Foreign Person Training, (5) systematic improvements like digital rights management and HR/IT system integration, (6) engagement of specialized ITAR counsel, and (7) proper documentation for the VSD. The plan addresses both immediate containment and long-term structural improvements to prevent recurrence.

---

### CTC-028: Post-Brexit Northern Ireland Protocol goods classification and dual status

**Difficulty:** hard | **Category:** documentation | **Score:** 55.0%

| Criterion | Weight | Rating | Score |
|---|---|---|---|
| windsor_framework_application | 0.4 | pass | 1.0 |
| documentation_requirements | 0.3 | partial | 0.5 |
| marking_and_regulatory | 0.3 | fail | 0.0 |

**windsor_framework_application:** The response correctly identifies this as a Green Lane movement under the Windsor Framework based on three key factors: end-use in Northern Ireland, UKIMS registration requirement, and standard B2B transaction. It explicitly states 'No customs declarations required' and 'No customs broker needed' which correctly reflects green lane treatment. The response demonstrates understanding that UKIMS registration is the critical prerequisite and references the 'not at risk' concept by emphasizing goods are for 'exclusive use in Belfast facility with no onward movement to Ireland/EU'. The analysis correctly identifies this as a UK internal movement with zero customs duty.

**documentation_requirements:** The response correctly identifies minimal documentation requirements for Green Lane including commercial invoice, delivery note, and customer's UKIMS registration number. It correctly states no customs declarations or transit documents are required. However, it fails to mention the Trader Support Service (TSS) which is the mandatory system for GB-NI movements, even for green lane goods. The response provides good practical documentation templates and references the correct HS code 8438.80, but the omission of TSS is a significant gap in the green lane procedure requirements.

**marking_and_regulatory:** The response incorrectly states that UKCA marking 'creates a compliance gap for Northern Ireland placement' and that 'Industrial food processing equipment requires CE marking for Northern Ireland placement'. This is wrong - under the Windsor Framework, UKCA marking IS accepted in Northern Ireland for goods from Great Britain. The response recommends expensive CE marking certification (£5,000-15,000) and advises 'do not ship until CE marking is complete', which is unnecessary for a green lane GB-NI movement. While the response shows knowledge of EU machinery requirements, it fundamentally misapplies them to Northern Ireland's dual regulatory status under the Windsor Framework.

---
