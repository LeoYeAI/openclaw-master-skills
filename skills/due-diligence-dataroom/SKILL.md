---
name: due-diligence-dataroom
description: >
  Organize, audit, and generate investor or acquirer due diligence data rooms for startups and SMBs.
  Maps required documents by category (financial, legal, HR, technical, commercial), identifies gaps,
  generates checklists, drafts document summaries, and produces a readiness score. Supports both
  fundraising DD (Series A/B, SAFE rounds) and M&A DD (sell-side, buy-side). Outputs structured
  folder structure, gap report, and investor-ready index.
  NOT for: tax filing, bookkeeping, smart contract audits, or legal advice on documents flagged as risky
  (escalate those to counsel). Do not use for public-company SEC filings.
version: 1.0.0
author: PrecisionLedger
tags:
  - finance
  - startups
  - due-diligence
  - investors
  - m-and-a
  - legal
  - fundraising
---

# Due Diligence Data Room Skill

Build investor-ready and acquirer-ready data rooms for fundraising (SAFE, priced rounds, Series A/B) and M&A (sell-side or buy-side). This skill guides Sam Ledger through organizing DD documents, identifying gaps, scoring readiness, and producing a clean data room index.

---

## When to Use This Skill

**Trigger phrases:**
- "Set up a data room"
- "What do investors need for due diligence?"
- "Prepare for Series A DD"
- "What documents do we need for the M&A process?"
- "Audit our data room"
- "Create a DD checklist"
- "We're getting acquired — what do they need?"
- "Rate our due diligence readiness"

**NOT for:**
- Tax filing or accounting — use QBO/compliance workflows
- Smart contract security audits — use `solidity-audit-precheck`
- Legal advice on specific clauses — refer to counsel
- Ongoing contract management — use `contract-review-agent`
- Cap table creation from scratch — use `cap-table-manager`
- Financial model building — use `startup-financial-model`

---

## Data Room Structure

Standard folder taxonomy used by institutional investors and M&A advisors:

```
/DataRoom
├── 01_Corporate
│   ├── Certificate of Incorporation (current + all amendments)
│   ├── Bylaws / Operating Agreement
│   ├── Board Resolutions (key actions last 3 years)
│   ├── Organizational Chart
│   └── Subsidiaries & Foreign Qualifications
│
├── 02_Financial
│   ├── Financial Statements (3 years audited or reviewed)
│   ├── Management Accounts (latest 12 months, monthly)
│   ├── Financial Model (base/bear/bull scenarios)
│   ├── Tax Returns (3 years federal + state)
│   ├── Accounts Receivable Aging
│   ├── Accounts Payable Aging
│   └── Bank Statements (6–12 months)
│
├── 03_Cap_Table
│   ├── Cap Table (fully diluted, current)
│   ├── Stock Option Plan (ISO/NSO plan document)
│   ├── Option Grants (individual grant summaries)
│   ├── SAFE Agreements (all outstanding)
│   ├── Convertible Notes (all outstanding)
│   ├── Investor Rights Agreement
│   ├── Right of First Refusal Agreement
│   └── 409A Valuation (most recent)
│
├── 04_Contracts_Commercial
│   ├── Customer Contracts (top 10 by revenue)
│   ├── Vendor/Supplier Agreements (key dependencies)
│   ├── Partnership Agreements
│   ├── Distribution Agreements
│   └── LOIs / MOUs (current)
│
├── 05_Intellectual_Property
│   ├── Patent Applications & Grants
│   ├── Trademark Registrations
│   ├── Copyright Registrations
│   ├── Trade Secret Policy
│   ├── IP Assignment Agreements (founders + employees)
│   └── Open Source Policy + License Inventory
│
├── 06_HR_People
│   ├── Employee List (names, titles, start dates, salaries)
│   ├── Offer Letters (key hires / executives)
│   ├── Employment Agreements (exec NDAs, non-competes)
│   ├── Contractor/1099 List + Agreements
│   ├── Benefits Summary Plan Document
│   ├── PEO/Payroll Provider Agreement
│   └── Org Chart (people version)
│
├── 07_Legal_Compliance
│   ├── Litigation History (pending, settled, threatened)
│   ├── Regulatory Licenses / Permits
│   ├── Privacy Policy + Terms of Service
│   ├── GDPR / CCPA Compliance Documentation
│   ├── Data Processing Agreements (key vendors)
│   └── Insurance Policies (D&O, E&O, Cyber, General Liability)
│
├── 08_Technical
│   ├── Architecture Diagram (system overview)
│   ├── Tech Stack Summary
│   ├── Security Audit Reports (penetration tests, SOC 2)
│   ├── Uptime / SLA History
│   ├── Disaster Recovery Plan
│   └── Data Handling / Privacy Architecture
│
└── 09_Business_Overview
    ├── Pitch Deck (current investor version)
    ├── Executive Summary / One-Pager
    ├── Product Roadmap
    ├── Customer References (top clients)
    └── Market Research / Competitive Analysis
```

---

## DD Readiness Scoring

Score each category 0–100 based on document completeness:

| Category | Weight | Scoring Logic |
|---|---|---|
| Corporate | 10% | All formation docs present, current, signed |
| Financial | 25% | 3yr statements + monthly actuals + model + bank stmts |
| Cap Table | 20% | Fully diluted table + all agreements + 409A current |
| Commercial | 15% | Top 10 customer contracts + key vendor agreements |
| IP | 15% | Assignments from all founders/employees + IP inventory |
| HR/People | 10% | Employee list + exec agreements + benefits docs |
| Legal | 10% | Litigation disclosure + licenses + insurance |
| Technical | 5% | Architecture + security + SLA history |

**Overall Readiness Score:**
```
Score = Σ (Category Score × Category Weight)

Interpretation:
  90–100: Investor-ready. Proceed.
  75–89:  1–2 week gap closure. Flag gaps to founder.
  50–74:  2–4 weeks work. Significant gaps present.
  <50:    Not ready. Build foundational documents first.
```

---

## Gap Analysis Output

When auditing an existing data room, produce a gap report in this format:

```
DUE DILIGENCE READINESS REPORT
Company: [Name]
Date: [Date]
Assessed by: Sam Ledger / PrecisionLedger

OVERALL SCORE: 72/100 — Needs 2–3 Weeks of Work

CATEGORY BREAKDOWN:
┌─────────────────────┬───────┬────────────────────────────────────────────────┐
│ Category            │ Score │ Missing / At Risk                              │
├─────────────────────┼───────┼────────────────────────────────────────────────┤
│ Corporate           │ 90%   │ Missing: Foreign qualification (Delaware co)   │
│ Financial           │ 65%   │ Missing: Audited statements, 409A outdated     │
│ Cap Table           │ 80%   │ Missing: 2 SAFE agreements not countersigned   │
│ Commercial          │ 70%   │ Missing: Contracts for 3 of top 10 customers   │
│ IP                  │ 55%   │ Missing: IP assignment from 1 co-founder       │
│ HR/People           │ 85%   │ Minor: Outdated offer letters for 2 eng hires  │
│ Legal               │ 90%   │ OK                                             │
│ Technical           │ 60%   │ Missing: Pen test report, no SLA documentation │
└─────────────────────┴───────┴────────────────────────────────────────────────┘

CRITICAL GAPS (will stall deal):
1. IP Assignment from co-founder [Name] — get signed before outreach
2. 409A valuation — expired 18+ months ago, investor will flag
3. Audited financials — Series A investors typically require 1 year audit minimum

HIGH PRIORITY (2-week fix):
4. SAFE countersignatures — pull originals, chase signatories
5. Missing customer contracts — get NDAs or MSAs on file

MEDIUM PRIORITY (can fix in parallel):
6. Foreign qualification certificate from Delaware
7. Pen test report — schedule if not done
8. Offer letter refresh for recent eng hires

RECOMMENDED NEXT STEPS:
Week 1: Resolve Critical Gaps (IP assignment, 409A, audited financials)
Week 2: High Priority items
Week 3: Full review + data room QA pass
```

---

## Document Checklist by Round Type

### SAFE / Pre-Seed Round (Minimal DD)
```
□ Certificate of Incorporation
□ Cap table (current, all SAFEs included)
□ Financial model or pitch deck financials
□ SAFE template to be signed
□ Founders' IP assignments
□ Bank statements (3 months)
```

### Series A (Full Institutional DD)
All folders above, plus:
```
□ Audited financials (1 year minimum, 2 preferred)
□ Monthly management accounts (last 12 months)
□ 409A valuation (< 12 months old)
□ Board minutes for all major decisions
□ Fully diluted cap table (with option pool)
□ All outstanding convertible instruments (SAFEs, notes)
□ Customer contracts (top 10 by revenue)
□ IP assignments (all founders, key employees, contractors)
□ Employment agreements (all executives)
```

### M&A Sell-Side
All Series A above, plus:
```
□ 3 years tax returns (federal + state)
□ Historical financial statements (3–5 years)
□ All material contracts (customer, vendor, partnership)
□ Litigation history (last 5 years, including settled)
□ Environmental compliance (if applicable)
□ Real property leases
□ Insurance policies with coverage limits
□ Employee benefit plan documents (401k, health)
□ Change of control provisions in key contracts
□ Government contracts or regulated agreements
```

---

## Step-by-Step Workflow

### Step 1: Scope the DD Type
Determine:
- **Type:** Fundraising (which stage?) or M&A (sell-side or buy-side)?
- **Timeline:** When is the investor/acquirer expecting access?
- **Audience:** Who is reviewing? (VC, PE, strategic acquirer, family office?)

### Step 2: Intake Audit
Ask the founder/CFO to share:
- Existing data room link or folder structure
- List of what's been prepared vs. not started
- Any known legal issues (pending litigation, IP disputes)
- Outstanding cap table instruments (unconverted SAFEs, notes)

### Step 3: Build Gap Report
Map what exists against the master checklist above.
Score each category.
Flag critical gaps (deal-stoppers) vs. nice-to-haves.

### Step 4: Prioritize
Sequence by:
1. Deal-stoppers first (IP assignments, 409A, audited financials)
2. Investor-specific asks (some VCs have custom checklists — get theirs)
3. Everything else in parallel

### Step 5: Draft Document Summaries
For key documents, produce a 3-line summary:
- What it is
- What it says (key terms)
- Any red flags or notes for investor

### Step 6: Build the Data Room Index
Produce a master index document:
```
DATA ROOM INDEX — [Company Name]
Last Updated: [Date]

Section 1: Corporate
  1.1 Certificate of Incorporation (Delaware, 2022) ✓
  1.2 Certificate of Amendment — Series Seed (2024) ✓
  1.3 Bylaws (as amended 2024) ✓
  1.4 Board Resolutions — [Summary] ✓
  1.5 Foreign Qualification — California [MISSING]

Section 2: Financial
  2.1 2023 Audited Financial Statements ✓
  2.2 2024 Management Accounts (Jan–Dec) ✓
  2.3 2025 YTD Management Accounts ✓
  2.4 Financial Model (Base/Bear/Bull, 36 months) ✓
  2.5 2022–2024 Federal Tax Returns ✓
  2.6 AR Aging Report (as of [Date]) ✓
...
```

### Step 7: Final QA Pass
Before opening data room access:
- [ ] All files named consistently (no "final_FINAL_v3.pdf")
- [ ] No personal employee info visible to all viewers (use sub-folders with tiered permissions)
- [ ] Sensitive items (bank statements, SSNs) restricted to appropriate viewers
- [ ] Index document is current and matches folder contents
- [ ] Watermarks on sensitive docs if required

---

## Example Interaction

**User:** "Our Series A investor wants data room access in 2 weeks. We've never set one up. Where do we start?"

**Sam's response:**
```
Two weeks is tight but doable if we move fast. Here's the triage plan:

FIRST 48 HOURS — Stop everything else, get these:

1. IP Assignments — every founder and early contractor must sign.
   This is the #1 deal-killer. I'll need: names of all founders,
   date company was incorporated, names of any early freelancers
   who touched the product.

2. Cap Table — send me whatever you have (spreadsheet, Carta export).
   I'll audit it and identify any missing countersignatures.

3. Financial Statements — do you have a CPA? If yes, request
   management-reviewed or compiled statements for 2023 + 2024.
   Full audit takes weeks — we'll flag the gap and provide reviewed.

THIS WEEK — Collect in parallel:
   □ All customer contracts (even just the signed MSAs/SOWs)
   □ Certificate of Incorporation + any amendments
   □ Board minutes (any major funding, equity, or officer decisions)
   □ Existing insurance policies (D&O is the critical one)

NEXT WEEK — Build + QA:
   □ I'll build the data room index and folder structure
   □ Financial model review and clean-up
   □ Full gap report for investor

What platform are you using for the data room? (Notion, Google Drive,
Carta Data Room, Caplinked, DocSend?) I'll tailor the structure.
```

---

## Platform-Specific Notes

| Platform | Best For | Notes |
|---|---|---|
| Google Drive | Early-stage, SAFE rounds | Easy setup, permission by folder, familiar |
| Carta Data Room | Series A+ with Carta cap table | Native integration, investor-friendly |
| Notion | Small rounds, internal prep | Good for checklists, not ideal for investor DD |
| DocSend | Tracking investor engagement | Analytics on who views what, for hours |
| Caplinked / Intralinks | M&A, larger rounds | Watermarking, NDA-gating, enterprise features |
| Box / SharePoint | Acquirer-preferred in M&A | Enterprise IT often requires these |

---

## Red Flags to Surface to Counsel

When auditing documents, flag these immediately — do not attempt to resolve without legal:

```
⚠️  Missing IP assignment from any co-founder or early employee
⚠️  Pending or threatened litigation not previously disclosed
⚠️  Customer contract with change-of-control clause (may block M&A)
⚠️  Government contract with anti-assignment provision
⚠️  Open-source license with copyleft (GPL) in commercial product
⚠️  Options granted below 409A fair market value (IRS issue)
⚠️  SAFE or note with full-ratchet anti-dilution (rare, toxic)
⚠️  Non-compete clauses in jurisdictions where they're unenforceable
⚠️  Data breach history not yet disclosed
⚠️  Expired regulatory license or lapsed compliance certification
```

---

## Integration Points

- **`startup-financial-model`** — generate or audit the financial model included in Section 02
- **`cap-table-manager`** — build or reconcile the fully-diluted cap table for Section 03
- **`contract-review-agent`** — summarize and flag key customer/vendor contracts for Section 04
- **`kpi-alert-system`** — once funded, monitor key metrics investors will track post-close
- **`report-generator`** — format the gap report into an investor-ready PDF memo

---

## Reference: Series A Investor DD Checklist (Condensed)

```
FINANCIAL
□ 3 years financial statements (audited preferred, reviewed acceptable)
□ YTD management accounts (monthly, current)
□ 36-month financial model with assumptions
□ AR aging + top 10 customer concentration
□ Tax returns (2 years minimum)

LEGAL / CORPORATE
□ Certificate of Incorporation + all amendments
□ Bylaws (as amended)
□ Board minutes (major resolutions)
□ All equity/instrument agreements (SAFEs, notes, stock plan)
□ Fully diluted cap table
□ 409A valuation (< 12 months)

COMMERCIAL
□ Top 10 customer contracts
□ Key vendor/dependency agreements
□ Any exclusivity, MFN, or anti-assignment clauses flagged

PEOPLE
□ Employee census (name, title, start date, salary, equity)
□ Executive offer letters and employment agreements
□ Option grant ledger
□ Independent contractor agreements (key ones)

IP
□ IP assignment agreements (all founders, employees, contractors)
□ Patent / trademark filings
□ Open-source license inventory
□ Trade secret policy

TECHNICAL / SECURITY
□ System architecture overview
□ Security audit or pen test (< 18 months)
□ SOC 2 / ISO 27001 (if applicable)
□ Uptime / incident history
```
