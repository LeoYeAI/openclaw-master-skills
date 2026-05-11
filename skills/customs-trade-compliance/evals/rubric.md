# Customs & Trade Compliance — LLM Grading Rubric

## Purpose

This rubric guides an LLM grader in scoring agent responses to customs and trade compliance evaluation scenarios. Each scenario contains 3–4 evaluation criteria with pass/fail rubric descriptions. The grader assigns a score to each criterion, and the weighted sum produces the scenario score.

---

## Grading Scale

| Rating | Score | Definition |
|---|---|---|
| **Pass** | 1.0 | Response demonstrates trade compliance expertise. The classification, valuation, and regulatory analysis are what an experienced customs specialist would provide. Correct legal and regulatory frameworks are cited. GRI application, FTA qualification analysis, penalty calculations, and screening adjudications are performed accurately. The response reflects operational judgment — not just regulatory knowledge but awareness of how customs authorities actually enforce, how brokers operate, and how trade compliance interacts with tax, procurement, and supply chain functions. |
| **Partial** | 0.5 | Response is directionally correct but incomplete or imprecise. The agent identifies the general category of trade compliance issue and suggests reasonable approaches, but misses critical regulatory details, applies thresholds or formulas incorrectly, omits a key step in the decision framework, or provides advice that is technically correct but would create problems in practice (e.g., filing a first sale claim without verifying the middleman's commercial role, or claiming USMCA preference without checking the exceptions list in the product-specific rule). |
| **Fail** | 0.0 | Response is incorrect, dangerously incomplete, or generic. The agent either misapplies the GRIs, applies the wrong legal framework (e.g., USMCA rules to an EU-UK TCA analysis), recommends actions that would increase penalty exposure or trigger regulatory violations, or provides advice so generic it could apply to any business function ("consult with legal and ensure compliance with applicable regulations"). A response that sounds plausible to a layperson but would make a trade compliance specialist wince. |

### Grading Decision Guide

When choosing between adjacent ratings, use these tiebreakers:

**Pass vs. Partial:**
- Did the response correctly identify the *single most important regulatory risk* in the scenario? If yes and the rest is reasonable, lean Pass.
- Would a trade compliance director reviewing this response need to add significant corrections before acting on it? If yes, Partial.

**Partial vs. Fail:**
- Does the response demonstrate awareness that this is a customs/trade compliance context (not generic procurement or logistics)? If not, Fail.
- Would following the response's advice create additional regulatory exposure (penalty, seizure, debarment, criminal referral)? If yes, Fail.
- Is the response merely incomplete but pointed in the correct regulatory direction? Partial.

---

## Domain Expertise vs. Generic Response

The core distinction this rubric enforces is between responses grounded in customs and trade compliance expertise and responses that apply generic business or legal logic to a trade-compliance-shaped problem.

### What Constitutes Domain Expertise

An expert-level response demonstrates knowledge that can only come from working in customs and trade compliance. Specifically:

**1. Classification Methodology**
- Applies the GRIs in strict sequential order — never invokes GRI 3 before exhausting GRI 1, never invokes GRI 4 before exhausting GRI 1-3
- Checks Section and Chapter notes before the heading text — notes override headings
- Knows the difference between "parts" and "accessories" under Section XVI Note 2
- Understands that essential character under GRI 3(b) requires multi-factor analysis (function, value, bulk, consumer perception) — not just the highest-value component
- Knows that "sets put up for retail sale" must meet three specific conditions under GRI 3(b)
- Recognises when a classification is genuinely ambiguous and recommends a binding ruling instead of guessing

**2. Valuation Knowledge**
- Applies the WTO valuation methods in hierarchical order — transaction value (Method 1) first, others only when Method 1 fails
- Correctly identifies assists, royalties, and post-importation costs as additions/deductions to transaction value
- Knows the US values on a CIF-equivalent basis (adding international freight and insurance) while the EU values on a CIF basis and the UK on a CIF basis
- Understands the "circumstances of sale" test for related-party valuations and the four "test values"
- Recognises the conflict between transfer pricing (tax) and customs valuation objectives
- Knows the DDP circular valuation problem and the methodology to resolve it

**3. FTA Qualification Analysis**
- Checks the product-specific rule of origin in the relevant FTA annex — does not apply generic "substantial transformation" when specific rules exist
- Correctly applies cumulation rules (bilateral, diagonal, full) for the specific FTA
- Performs the RVC calculation using the correct method (transaction value vs net cost for USMCA, build-up vs build-down for RCEP)
- Checks the exceptions list in tariff shift rules — knows that "a change from any heading EXCEPT headings X-Y" means those specific headings are excluded
- Knows the documentation requirements for each FTA's certification of origin (USMCA nine elements, EU-UK TCA REX registration, RCEP Form RCEP)
- Understands the insufficient processing rules under the EU-UK TCA

**4. Penalty and Enforcement Knowledge**
- Correctly applies the 19 USC § 1592 penalty framework (negligence, gross negligence, fraud) with accurate maximum amounts
- Knows the prior disclosure requirements (19 CFR § 162.74) and the penalty caps it creates
- Understands that prior disclosure is an admission of violation — not a casual filing
- Knows the EAPA process, timelines, and interim measures for AD/CVD evasion investigations
- Understands that 19 USC § 1592 penalties can be assessed even when the government LOST revenue (e.g., misclassification resulting in higher duty payment)
- Knows the difference between a CF-28 (request for information — not adversarial) and a CF-29 (notice of action — CBP is changing something)

**5. Restricted Party Screening and Export Controls**
- Correctly classifies items under the EAR (ECCN) and knows how to check the Commerce Country Chart
- Understands the ITAR "deemed export" concept — disclosure to foreign nationals in the US is treated as an export
- Correctly adjudicates screening hits by analysing name match quality, address correlation, entity type, and country nexus
- Knows the difference between SDN (OFAC — blocked), Entity List (BIS — licence required), and Denied Persons List (BIS — absolute prohibition)
- Understands the Foreign Direct Product Rule and its application to Entity List entities
- Knows that ~95% of screening hits are false positives and that systematic documentation of adjudications is mandatory

### Common Indicators of Generic Responses

These patterns indicate the response lacks domain-specific expertise. Any single indicator is not disqualifying, but multiple indicators strongly suggest a Fail or low Partial:

**1. Wrong Abstraction Layer**
- Refers to customs entries as "shipments" or "orders" without using the correct terminology
- Calls the HTS a "product code" or "tariff number" without specifying the system
- Describes classification as "looking up the product code" rather than applying the GRIs
- Suggests "checking if the FTA applies" rather than performing the specific qualification analysis
- Uses "import tax" instead of "customs duty" or conflates duties with taxes

**2. Missing Regulatory Mechanics**
- Does not apply the GRIs in order — jumps to GRI 3 or 4 without exhausting GRI 1
- Does not check Section or Chapter notes when classifying
- Does not adjust the customs value for Incoterm-specific additions (freight, insurance under FOB/FCA)
- Does not add assists to the transaction value
- Files an FTA claim without verifying the product-specific rule of origin
- Accepts a screening hit at face value without adjudication analysis
- Does not distinguish between negligence, gross negligence, and fraud in penalty assessments

**3. Incorrect Legal Application**
- Applies USMCA rules to non-USMCA trade (e.g., EU-UK)
- Uses the wrong penalty statute (e.g., cites 19 USC § 1592 for an export control violation)
- Applies the "substantial transformation" test when a specific FTA rule of origin exists
- Does not know that ITAR is strict liability for deemed exports
- Confuses the EAR (Commerce) with the ITAR (State) jurisdiction
- Applies US customs valuation rules (FOB+ basis) to EU imports (CIF basis) or vice versa

**4. One-Dimensional Analysis**
- Addresses only classification without considering valuation, duty rate, and additional duties (Section 301, AD/CVD)
- Recommends FTA utilisation without performing the qualification analysis
- Calculates duties without considering assists or related-party valuation adjustments
- Screens the buyer but not the consignee, end user, or freight forwarder
- Files a prior disclosure without calculating the penalty savings vs non-disclosure

**5. Tone-Deaf Communication**
- Drafts aggressive communications with CBP for routine information requests (CF-28)
- Admits fraud in a penalty response when the facts support negligence
- Provides highly technical regulatory analysis to internal business stakeholders without translating to business impact
- Recommends voluntarily sharing more information with CBP than the situation requires

---

## Scoring Individual Criteria

For each criterion within a scenario, the grader should:

1. **Read the scenario context and task** to understand what the agent was asked to do.
2. **Read the criterion's pass and fail rubric descriptions** — these are specific to the scenario, not generic.
3. **Evaluate the agent's response** against both the pass and fail descriptions.
4. **Assign a rating:**
   - **Pass (1.0):** The response matches the pass description substantively. Minor wording differences are fine — the grader is evaluating whether the agent demonstrated the same trade compliance judgment, not whether it used identical phrasing.
   - **Partial (0.5):** The response falls between the pass and fail descriptions. It captures some elements of the pass description but misses others, or gets the regulatory direction right but the specific details wrong.
   - **Fail (0.0):** The response matches the fail description, or is worse than the fail description, or does not address the criterion at all.

### Important Scoring Nuances

**Specificity Matters**
A response that says "check if the goods qualify for the FTA" is not the same as a response that says "look up the product-specific rule for heading 4202 in USMCA Annex 4-B, verify the tariff shift from heading 4107 is excluded, and calculate the RVC using the transaction value method." The first is generic; the second demonstrates process knowledge. Grade accordingly.

**Regulatory Precision Matters**
Citing the correct statute, regulation, or treaty article signals expertise. Saying "there might be penalties" is different from saying "19 USC § 1592(c) provides for penalties up to 2× lost revenue for negligence, with prior disclosure under 19 CFR § 162.74 capping the penalty at interest." Imprecise regulatory references earn Partial at best.

**Calculation Accuracy Matters**
Customs and trade compliance is quantitative. An agent that identifies the correct framework but makes mathematical errors (wrong duty amount, wrong RVC percentage, wrong penalty calculation) should receive Partial rather than Pass. Customs authorities will hold the importer to the correct numbers.

**Omission Is Failure**
If a criterion's pass description includes 4 elements and the response covers 2 well but ignores 2, this is Partial — not Pass. The pass description represents the complete expert response.

**Over-Compliance Is as Wrong as Under-Compliance**
A response that treats a routine CF-28 as a seizure event is as incorrect as one that ignores a true positive screening hit. Correct risk calibration is fundamental to domain expertise.

**Practicality Test**
Would an experienced trade compliance specialist read this response and say "yes, that's exactly what I'd do"? If yes, Pass. Would they say "that's roughly right but they're missing X"? Partial. Would they say "no, that would make things worse"? Fail.

---

## Grading Edge Cases

### When the Response Is Right for the Wrong Reasons

If the agent recommends the correct action but explains it using incorrect reasoning (e.g., recommends prior disclosure but cites the wrong statute), assign **Partial**. Correct actions with wrong reasoning suggest the agent may not replicate the correct behaviour in novel situations.

### When the Response Adds Correct Information Not in the Rubric

If the agent provides additional relevant and correct information beyond what the pass rubric describes, this does not change the scoring — it's still a Pass. Do not penalise for additional correct content, even if it wasn't asked for, unless it contradicts other parts of the response.

### When the Response Contradicts Itself

If the agent states conflicting recommendations (e.g., "file a prior disclosure" in one paragraph and "do not admit the violation" in another), assign **Fail** for that criterion unless one recommendation is clearly framed as contingent on a condition.

### When the Regulatory Framework Has Changed

Trade compliance regulations change frequently (tariff rates, Section 301 lists, sanctions designations, FTA amendments). If the agent references a legitimate regulatory change that alters the expected response, the grader should give the benefit of the doubt and assign **Partial** at minimum, then flag the scenario for rubric review.

### When the Response Addresses a Different Aspect of the Problem

If the criterion asks about "classification analysis" and the agent's response focuses entirely on "penalty exposure" (a different criterion), assign **Fail** for the classification criterion even if the penalty content is excellent. Each criterion is graded independently.

---

## Terminology Weighting

Domain-specific terminology usage is a signal, not a score. The grader should use terminology as follows:

**Terminology that signals expertise (positive signal, supports higher scores):**
- Correct use of: HTS, HTSUS, TARIC, GRI, Section XVI Note 2, heading vs subheading, CBP CROSS database, BTI, FTZ, TIB, ATA Carnet, ISF 10+2, CF-28, CF-29, CF-7501, prior disclosure, FP&F, CEE, C-TPAT, AEO, ECCN, EAR99, USML, deemed export, FDPR, SDN, Entity List, DPL, EAPA, AD/CVD, Section 301, Section 232, UFLPA, WRO, RVC, CTH, CTSH, CTC, assists, transaction value, related-party circumstances of sale, reconciliation entry, PSC, liquidation, protest
- Correct differentiation between: MFN rate vs preferential rate, classification vs valuation, parts vs accessories, sets vs assortments, tariff shift vs RVC, transaction value vs net cost, negligence vs gross negligence vs fraud, CF-28 vs CF-29, prior disclosure vs voluntary self-disclosure, EAR vs ITAR

**Terminology that signals generic knowledge (neutral — neither helps nor hurts):**
- Standard business terms used correctly: compliance, due diligence, risk assessment, audit, mitigation
- General trade terms: import, export, customs, tariff, duty, free trade agreement

**Terminology that signals misunderstanding (negative signal, supports lower scores):**
- Misuse of trade terms (e.g., "customs tax" instead of "customs duty," "tariff code" when the context requires "ECCN")
- Using generic terms where specific terms exist (e.g., "trade rules" instead of "USMCA Annex 4-B product-specific rule of origin")
- Applying the wrong regime's terminology (e.g., "embargo" when the issue is an Entity List licence requirement, "ban" when the restriction is a licence requirement with presumption of denial)

**Important:** Terminology alone does not determine the score. An agent that uses all the right words but recommends the wrong actions should still fail. An agent that uses plain language but recommends the correct actions with proper regulatory judgment should still pass. Terminology is a supporting signal for borderline cases.

---

## Aggregate Interpretation

After scoring all criteria for all scenarios, the following aggregate benchmarks indicate capability levels:

| Aggregate Score | Interpretation |
|---|---|
| **≥ 85%** | Expert-level trade compliance capability. The agent can handle the full range of customs and trade compliance scenarios with minimal human oversight. Suitable for production use in classification analysis, FTA qualification, entry instructions, and routine compliance advisory. |
| **70–84%** | Competent with supervision. The agent handles routine compliance scenarios well but needs human review on complex multi-jurisdictional issues, related-party valuation, export control classification, and penalty proceedings. Suitable for first-draft analysis that a compliance specialist reviews. |
| **50–69%** | Inconsistent. The agent demonstrates some domain knowledge but has significant gaps. May produce advice that increases regulatory exposure on hard scenarios. Requires heavy human supervision and should not be used for regulatory filings or penalty responses without thorough review. |
| **< 50%** | Insufficient domain expertise. The agent's responses are predominantly generic and would not be useful to a trade compliance professional. Not suitable for any autonomous compliance tasks. |

### Difficulty-Adjusted Expectations

The scenario set is designed with a difficulty distribution:
- **Easy (~30%):** An agent with basic trade compliance training should pass these. Failure on easy scenarios is a strong negative signal.
- **Medium (~35%):** An agent needs genuine operational knowledge to pass these consistently. Partial scores are common and acceptable.
- **Hard (~35%):** These are designed to trip up agents without deep domain expertise. Even competent agents may score Partial on some hard scenarios. Consistent Pass on hard scenarios indicates true expert-level capability.

A capable agent should score ≥90% on easy, ≥70% on medium, and ≥50% on hard scenarios. An agent scoring below 50% on easy scenarios has fundamental gaps that disqualify it from the domain.
