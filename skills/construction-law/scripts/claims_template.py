#!/usr/bin/env python3
"""
Claims Letter / Notice Template Generator
Generates structured claim notices, EOT applications, and response letters
based on contract form and claim type.

Usage:
    python3 claims_template.py --form fidic-red --type notice-of-claim --output notice.md
    python3 claims_template.py --form psscoc --type eot-application --output eot.md
    python3 claims_template.py --form sia --type variation-claim --output vo_claim.md
    python3 claims_template.py --form fidic-red --type interim-claim --output interim.md
    python3 claims_template.py --list
"""

import argparse
import sys
from datetime import datetime

TEMPLATES = {
    "notice-of-claim": {
        "title": "Notice of Claim",
        "description": "Initial notice to preserve entitlement (time-bar compliance)",
        "forms": {
            "fidic-red": {
                "clause": "20.2.1",
                "period": "28 days from awareness",
                "template": """# NOTICE OF CLAIM
## Under Clause 20.2.1 of the Conditions of Contract

**Contract:** [Contract Title]
**Contract No.:** [Contract Number]
**Employer:** [Employer Name]
**Contractor:** [Contractor Name]
**Engineer:** [Engineer Name]
**Date:** {date}
**Ref:** [Reference Number]

---

**Dear [Engineer/Engineer's Representative],**

**RE: NOTICE OF CLAIM UNDER CLAUSE 20.2.1 — [Brief Description of Claim]**

We refer to the above-captioned Contract and hereby give notice pursuant to **Sub-Clause 20.2.1** of the Conditions of Contract (FIDIC Red Book 2017 Edition).

### 1. EVENT OR CIRCUMSTANCE GIVING RISE TO THE CLAIM

[Describe the event or circumstance. Be specific about what happened, when it happened, and where.]

The Contractor became aware of this event/circumstance on **[date of awareness]**.

This Notice is given within **28 days** of the date on which the Contractor became aware of the event or circumstance, in compliance with Sub-Clause 20.2.1.

### 2. CONTRACTUAL BASIS

The Contractor considers that it is entitled to:

- [ ] Extension of Time under Sub-Clause [8.4 / 8.5 / other]
- [ ] Additional Payment (Cost) under Sub-Clause [___]
- [ ] Additional Payment (Cost + Profit) under Sub-Clause [___]

The relevant Sub-Clauses giving rise to this entitlement are:
- **Sub-Clause [___]**: [Brief description of entitlement basis]

### 3. PRELIMINARY ESTIMATE OF IMPACT

**Time impact:** [Estimated delay in days/weeks — if known at this stage]
**Cost impact:** [Preliminary estimate — if quantifiable at this stage]

*Note: These are preliminary estimates only. A fully detailed claim will be submitted in accordance with Sub-Clause 20.2.4 within 84 days of this Notice.*

### 4. SUPPORTING RECORDS

The Contractor is maintaining contemporary records in accordance with Sub-Clause 20.2.3, including:
- Daily site records
- Progress photographs
- Correspondence
- Programme updates
- Resource records
- [Other relevant records]

### 5. RESERVATION OF RIGHTS

The Contractor reserves all rights under the Contract and at law, including but not limited to the right to submit further claims and to update the particulars and quantum of this claim.

This Notice is given **without prejudice** to any other rights or remedies available to the Contractor.

Yours faithfully,

**[Contractor Name]**
[Authorised Signatory]
[Name and Title]

---
*cc: [Employer] / [Other parties as required]*
"""
            },
            "psscoc": {
                "clause": "23(1)",
                "period": "28 days from commencement of delay event",
                "template": """# APPLICATION FOR EXTENSION OF TIME
## Under Clause 23(1) of PSSCOC

**Contract:** [Contract Title]
**Contract No.:** [Contract Number]
**Employer:** [Government Agency]
**Contractor:** [Contractor Name]
**Superintending Officer:** [SO Name]
**Date:** {date}
**Ref:** [Reference Number]

---

**Dear [Superintending Officer],**

**RE: APPLICATION FOR EXTENSION OF TIME UNDER CLAUSE 23(1) — [Brief Description]**

We refer to the above Contract and hereby apply for an Extension of Time pursuant to **Clause 23(1)** of the Public Sector Standard Conditions of Contract.

### 1. CAUSE OF DELAY

[Describe the delay event in detail — what happened, when, how it affects the works]

The delay event commenced on **[date]**.

This application is made within **28 days** from the commencement of the delay event, in compliance with Clause 23(1).

### 2. GROUNDS FOR EOT

The Contractor applies for EOT on the following grounds under Clause 23:
- [ ] Variation Orders
- [ ] Exceptionally adverse weather conditions
- [ ] Delay caused by the Employer or SO
- [ ] Civil commotion, strikes, lockouts
- [ ] Force majeure
- [ ] Other: [specify]

### 3. IMPACT ON PROGRAMME

**Current Completion Date:** [date]
**Estimated delay:** [number] days
**Requested Revised Completion Date:** [date]

**Critical path impact:** [Describe how the delay event affects the critical path]

### 4. MITIGATION MEASURES

The Contractor has taken / is taking the following steps to mitigate delay:
- [Measure 1]
- [Measure 2]
- [Measure 3]

### 5. SUPPORTING DOCUMENTS

Enclosed:
- [ ] Updated programme showing delay impact
- [ ] Site diary / daily records for affected period
- [ ] Relevant correspondence
- [ ] Photographs
- [ ] Weather records (if applicable)
- [ ] Resource records

### 6. RESERVATION OF RIGHTS

The Contractor reserves all rights under the Contract including any entitlement to costs arising from the delay.

Yours faithfully,

**[Contractor Name]**
[Authorised Signatory]
"""
            },
            "sia": {
                "clause": "23",
                "period": "Written notice required",
                "template": """# APPLICATION FOR EXTENSION OF TIME
## Under Clause 23 of the SIA Conditions

**Contract:** [Contract Title]
**Employer:** [Employer Name]
**Contractor:** [Contractor Name]
**Architect:** [Architect Name]
**Date:** {date}
**Ref:** [Reference Number]

---

**Dear [Architect],**

**RE: APPLICATION FOR EXTENSION OF TIME — [Brief Description]**

We refer to the above Contract and hereby apply for an Extension of Time pursuant to **Clause 23** of the SIA Conditions of Building Contract (9th Edition).

### 1. DELAY EVENT
[Description of event causing delay]

### 2. CONTRACTUAL BASIS
[Relevant sub-clause of Clause 23]

### 3. IMPACT
**Current Completion Date:** [date]
**Delay period:** [number] days
**Requested Revised Completion Date:** [date]

### 4. MITIGATION
[Steps taken to minimise delay]

### 5. SUPPORTING DOCUMENTS
[List of enclosed documents]

### 6. RESERVATION OF RIGHTS
The Contractor reserves all rights under the Contract.

Yours faithfully,

**[Contractor Name]**
[Authorised Signatory]
"""
            }
        }
    },
    "eot-application": {
        "title": "EOT Application (Detailed)",
        "description": "Detailed extension of time application with delay analysis",
        "forms": {
            "fidic-red": {
                "clause": "20.2.4",
                "period": "84 days from Notice of Claim",
                "template": """# FULLY DETAILED CLAIM — EXTENSION OF TIME
## Under Sub-Clause 20.2.4 of the Conditions of Contract

**Contract:** [Contract Title]
**Contract No.:** [Contract Number]
**Employer:** [Employer Name]
**Contractor:** [Contractor Name]
**Engineer:** [Engineer Name]
**Date:** {date}
**Ref:** [Reference Number]

**Notice of Claim Ref:** [Reference to original 20.2.1 notice]
**Notice of Claim Date:** [Date of original notice]

---

### 1. EXECUTIVE SUMMARY

This fully detailed claim is submitted pursuant to Sub-Clause 20.2.4, within 84 days of the Notice of Claim dated [date].

**Summary of claim:**
- Extension of Time: [number] days
- Additional Cost: $[amount]
- Profit (if applicable): $[amount]

### 2. FACTUAL BACKGROUND

#### 2.1 Contract Overview
- Contract Sum: $[amount]
- Original Completion Date: [date]
- Current Completion Date: [date] (as extended)
- Commencement Date: [date]

#### 2.2 Chronology of Events
| Date | Event | Reference |
|------|-------|-----------|
| [date] | [Event description] | [Letter/drawing/instruction ref] |
| [date] | [Event description] | [Reference] |

### 3. CONTRACTUAL ENTITLEMENT

#### 3.1 Relevant Contract Provisions
[Quote relevant clauses verbatim]

#### 3.2 Analysis of Entitlement
[Demonstrate how the facts satisfy each element of the clause]

#### 3.3 Notice Compliance
- Date of awareness: [date]
- Notice given: [date]
- Period: [X] days (within 28-day requirement)

### 4. CAUSATION — DELAY ANALYSIS

#### 4.1 Methodology
[State the delay analysis method used: TIA / Impacted As-Planned / Collapsed As-Built / Windows]

#### 4.2 Baseline Programme
[Reference the approved programme used as baseline]

#### 4.3 Delay Events
| Event | Start | End | Duration | Critical? |
|-------|-------|-----|----------|-----------|
| [Description] | [date] | [date] | [X] days | Yes/No |

#### 4.4 Critical Path Impact
[Demonstrate how delay events affected the critical path]

#### 4.5 Conclusion on Time
**Total delay to critical path: [X] days**
**EOT requested: [X] days**
**Revised Completion Date: [date]**

### 5. QUANTIFICATION — COSTS

#### 5.1 Prolongation Costs
| Item | Monthly Rate | Period | Amount |
|------|-------------|--------|--------|
| Site staff | $[amount] | [X] months | $[amount] |
| Site facilities | $[amount] | [X] months | $[amount] |
| Plant & equipment | $[amount] | [X] months | $[amount] |
| Insurance | $[amount] | [X] months | $[amount] |
| Bonds | $[amount] | [X] months | $[amount] |
| **Subtotal** | | | **$[amount]** |

#### 5.2 Head Office Overhead (Emden Formula)
```
HO Overhead = (Contract Sum / Contract Period) × (HO% / 100) × Delay Period
            = ($[amount] / [X] months) × ([X]% / 100) × [X] months
            = $[amount]
```

#### 5.3 Additional Direct Costs
[Itemise any additional costs directly caused by the delay event]

#### 5.4 Finance Charges
[Interest on delayed payments, if applicable]

#### 5.5 Profit (if entitled)
[Calculate profit element if Sub-Clause provides for Cost + Profit]

#### 5.6 Summary of Costs
| Head | Amount |
|------|--------|
| Prolongation costs | $[amount] |
| HO overhead | $[amount] |
| Additional direct costs | $[amount] |
| Finance charges | $[amount] |
| Profit | $[amount] |
| **TOTAL CLAIM** | **$[amount]** |

### 6. SUPPORTING DOCUMENTS

| Document | Reference |
|----------|-----------|
| Approved baseline programme | [ref] |
| Updated/as-built programme | [ref] |
| Daily site records | [ref] |
| Correspondence | [ref] |
| Photographs | [ref] |
| Cost records / invoices | [ref] |
| Weather records | [ref] |
| Resource records | [ref] |

### 7. RESERVATION OF RIGHTS

The Contractor reserves all rights under the Contract and at law. This claim may be updated as further information becomes available.

Yours faithfully,

**[Contractor Name]**
[Authorised Signatory]
"""
            }
        }
    },
    "variation-claim": {
        "title": "Variation Valuation Claim",
        "description": "Claim for valuation of instructed variation",
        "forms": {
            "fidic-red": {
                "clause": "13.3",
                "period": "Per Engineer's instruction",
                "template": """# VARIATION VALUATION
## Under Sub-Clause 13.3 of the Conditions of Contract

**Contract:** [Contract Title]
**Contract No.:** [Contract Number]
**Variation Instruction Ref:** [Reference]
**Variation Instruction Date:** [Date]
**Date:** {date}
**Ref:** [Reference Number]

---

### 1. VARIATION INSTRUCTION

On [date], the Engineer issued [Instruction/Direction] Ref: [reference] instructing the following variation:

[Describe the variation — what work is added/omitted/changed]

### 2. VALUATION BASIS

The Contractor proposes the following valuation in accordance with Sub-Clause 13.3:

#### 2.1 Applicable Rates
- [ ] Contract rates (applicable to similar work)
- [ ] New rates (no similar work in BOQ)
- [ ] Daywork rates

#### 2.2 Breakdown

| Item | Description | Qty | Unit | Rate | Amount |
|------|-------------|-----|------|------|--------|
| 1 | [Description] | [qty] | [unit] | $[rate] | $[amount] |
| 2 | [Description] | [qty] | [unit] | $[rate] | $[amount] |
| | **Subtotal** | | | | **$[amount]** |
| | Profit & Overhead [X]% | | | | $[amount] |
| | **TOTAL** | | | | **$[amount]** |

### 3. TIME IMPACT

**Does this variation affect the programme?**
- [ ] Yes — EOT claim to follow under Clause 20.2
- [ ] No — variation can be absorbed within current programme

### 4. SUPPORTING DOCUMENTS

- [ ] Engineer's variation instruction
- [ ] Drawings / specifications
- [ ] Quotations from suppliers/subcontractors
- [ ] Rate build-up / cost breakdown
- [ ] Programme showing impact (if applicable)

Yours faithfully,

**[Contractor Name]**
[Authorised Signatory]
"""
            }
        }
    },
    "interim-claim": {
        "title": "Interim Claim Statement",
        "description": "Progress claim / interim payment application",
        "forms": {
            "fidic-red": {
                "clause": "14.3",
                "period": "Monthly",
                "template": """# INTERIM PAYMENT APPLICATION No. [X]
## Under Sub-Clause 14.3 of the Conditions of Contract

**Contract:** [Contract Title]
**Contract No.:** [Contract Number]
**Period:** [Start Date] to [End Date]
**Date:** {date}
**Ref:** [Reference Number]

---

### SUMMARY

| Item | Amount |
|------|--------|
| A. Work done to date | $[amount] |
| B. Materials on site | $[amount] |
| C. Approved variations | $[amount] |
| D. Claims (assessed) | $[amount] |
| E. Price adjustments | $[amount] |
| **F. Gross valuation (A+B+C+D+E)** | **$[amount]** |
| G. Less retention [X]% | ($[amount]) |
| **H. Net valuation** | **$[amount]** |
| I. Less previous certifications | ($[amount]) |
| **J. Amount due this certificate** | **$[amount]** |

### BREAKDOWN OF WORK DONE

| BOQ Ref | Description | Contract Qty | Completed Qty | Rate | Amount |
|---------|-------------|-------------|---------------|------|--------|
| [ref] | [description] | [qty] | [qty] | $[rate] | $[amount] |

### VARIATIONS INCLUDED

| VO No. | Description | Amount |
|--------|-------------|--------|
| VO-[X] | [Description] | $[amount] |

### CLAIMS INCLUDED

| Claim No. | Description | Amount |
|-----------|-------------|--------|
| CLM-[X] | [Description] | $[amount] |

Yours faithfully,

**[Contractor Name]**
[Authorised Signatory]
"""
            }
        }
    }
}

def list_templates():
    print("Available templates:\n")
    for key, tmpl in TEMPLATES.items():
        forms = ", ".join(tmpl["forms"].keys())
        print(f"  --type {key}")
        print(f"    {tmpl['title']}: {tmpl['description']}")
        print(f"    Available for: {forms}")
        print()

def generate_template(form, claim_type, output=None):
    if claim_type not in TEMPLATES:
        print(f"Error: Unknown type '{claim_type}'. Use --list to see available templates.")
        sys.exit(1)

    tmpl = TEMPLATES[claim_type]
    if form not in tmpl["forms"]:
        available = ", ".join(tmpl["forms"].keys())
        print(f"Error: Template '{claim_type}' not available for '{form}'. Available forms: {available}")
        sys.exit(1)

    form_tmpl = tmpl["forms"][form]
    content = form_tmpl["template"].format(date=datetime.now().strftime("%d %B %Y"))

    header = f"<!-- Template: {tmpl['title']} | Form: {form} | Clause: {form_tmpl['clause']} | Period: {form_tmpl['period']} -->\n"
    result = header + content

    if output:
        with open(output, 'w') as f:
            f.write(result)
        print(f"Template written to {output}")
    else:
        print(result)

def main():
    parser = argparse.ArgumentParser(description="Generate construction claims/notice templates")
    parser.add_argument("--form", choices=["fidic-red", "fidic-yellow", "psscoc", "sia", "nec4"],
                       help="Contract form")
    parser.add_argument("--type", dest="claim_type",
                       choices=list(TEMPLATES.keys()),
                       help="Template type")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--list", action="store_true", help="List available templates")
    args = parser.parse_args()

    if args.list:
        list_templates()
        return

    if not args.form or not args.claim_type:
        parser.error("--form and --type are required (or use --list)")

    generate_template(args.form, args.claim_type, args.output)

if __name__ == "__main__":
    main()
