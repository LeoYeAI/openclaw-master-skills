---
name: Legal Docs Pro
description: >
  Your landlord just sent a 12-page lease renewal and you have no idea what half the clauses mean. Or you need an NDA for a freelancer by tomorrow and LegalZoom wants $59 for a template that doesn't know your business. Legal Docs Pro handles both sides: generate NDAs, contracts, privacy policies, and demand letters through natural conversation, or upload a contract you received and get every risky clause flagged with a plain-English explanation of what it actually means. It remembers your business details across sessions — company name, address, standard terms — so generating your next document takes seconds, not form fields.
---

# Legal Docs Pro — Agent Skill

> **⚖️ Legal Docs Pro** generates, reviews, and explains legal documents for freelancers, solopreneurs, and small businesses. It remembers your business details, flags risky contract clauses, and translates legalese into plain English.

> ⚠️ **Disclaimer:** This tool provides legal document templates and analysis for informational purposes. It is not a substitute for professional legal advice. Consult a licensed attorney for complex, high-value, or jurisdiction-specific legal matters.

## Description

Legal Docs Pro is an AI-powered legal document toolkit. Use when the user asks to:
- Draft or generate any legal document (NDA, contractor agreement, privacy policy, etc.)
- Review, analyze, or explain an existing contract
- Look up or explain a legal term or clause
- Manage their business profile for document auto-fill
- Export a generated document
- Scan a contract file for risks

NOT for: e-signatures, business formation/incorporation, estate planning (wills/trusts), litigation strategy, or tax advice.

## Setup

The user must run `setup.sh` before first use. This creates the data directory and business profile:

```bash
chmod 700 scripts/setup.sh && bash scripts/setup.sh
```

Business profile is stored in `config/settings.json`. The agent reads this file at the start of every document generation or review session.

---

## 1. Business Profile System

### Loading the Profile

At the start of every document-related task, read `config/settings.json` to retrieve the user's stored business details. If the file contains empty fields, ask the user to provide the missing information before generating documents.

### Profile Fields

The `config/settings.json` file stores:

| Field | Purpose | Example |
|-------|---------|---------|
| `business_name` | Legal entity name | "Bright Pixel LLC" |
| `business_type` | Entity type | "LLC", "Sole Proprietor", "S-Corp" |
| `address` | Principal business address | "123 Main St, Suite 4, Denver, CO 80202" |
| `state_of_formation` | State where entity was formed | "Colorado" |
| `ein` | Employer Identification Number | "12-3456789" |
| `default_jurisdiction` | Governing law for contracts | "State of Colorado" |
| `owner_name` | Primary owner / signatory | "Jordan Rivera" |
| `owner_title` | Title of signatory | "Managing Member" |
| `owner_email` | Contact email | "jordan@brightpixel.io" |
| `phone` | Business phone | "303-555-0142" |
| `payment_terms` | Default net terms | "Net 30" |
| `late_fee_rate` | Late payment penalty | "1.5% per month" |
| `preferred_ip_assignment` | IP ownership preference | "All work product assigned to Company" |
| `standard_non_compete` | Default non-compete scope | "12 months, 50-mile radius" |
| `contacts` | Key contacts array | Names, roles, emails |

### Updating the Profile

When the user says "update my business profile" or provides new business details in conversation, update the relevant fields in `config/settings.json`. Confirm changes back to the user.

### Auto-Population

Every generated document MUST pull from the business profile. Never ask the user to re-enter information that exists in their profile. If a field is needed but missing, ask once, save it to the profile, and use it going forward.

---

## 2. Document Generation

### Supported Document Types

| Document | Variants | Typical Use Case |
|----------|----------|-----------------|
| **NDA** | Mutual, Unilateral | Before sharing confidential info with a partner, vendor, or hire |
| **Freelance/Contractor Agreement** | Fixed-price, Hourly, Retainer | Hiring freelancers or contractors |
| **Consulting Agreement** | Time-based, Project-based | Engaging consultants for advisory work |
| **Privacy Policy** | Website, App, SaaS | Any business collecting user data |
| **Terms of Service** | Website, App, SaaS | Any business with a public-facing product |
| **Partnership Agreement** | Simple 50/50, Custom split | Two or more parties starting a venture |
| **Demand Letter** | Late payment, Breach of contract, Property damage | Collecting money or enforcing obligations |
| **Cease and Desist** | Trademark, Copyright, Defamation | Stopping unauthorized use of IP or harmful activity |

### Generation Workflow

Follow this exact sequence for every document:

**Step 1 — Understand the Deal**
Ask the user to describe the situation in plain language. Examples:
- "I need an NDA for a freelance designer who'll see our product mockups"
- "I'm hiring a contractor to build my website for $5,000"
- "Someone owes me $3,200 and won't pay"

**Step 2 — Clarifying Questions**
Ask ONLY the questions needed to customize the document. Pull everything you can from the business profile first. Typical clarifying questions by document type:

*NDA:*
- Mutual or one-way? (Who's sharing confidential info?)
- What type of information is being protected?
- How long should confidentiality last? (Default: 2 years)
- Name and details of the other party?

*Freelance/Contractor Agreement:*
- Scope of work — what exactly will they do?
- Payment amount, structure (fixed/hourly/retainer), and schedule?
- Timeline / deadlines?
- Who owns the work product? (Default: pull from profile `preferred_ip_assignment`)
- Will they need access to confidential information? (If yes, embed NDA clause)

*Demand Letter:*
- Who owes what?
- Original agreement or basis for the claim?
- Amount owed and any accrued interest/fees?
- What resolution are you seeking?
- Deadline for response?

**Step 3 — Generate the Document**
Generate the complete document with all sections filled in. Use the business profile for your entity's details. Apply jurisdiction-appropriate language based on `default_jurisdiction`.

**Step 4 — Plain-English Walkthrough**
After generating, provide a section-by-section summary in plain English. For each major clause, include a "What this means" explanation. Example:

> **Section 4 — Indemnification**
> *What this means:* If the contractor's work causes someone to sue your business, the contractor agrees to cover your legal costs. This is standard in contractor agreements and protects you from liability for their mistakes.

**Step 5 — Document Footer**
Every generated document MUST end with this disclaimer:

```
---
DISCLAIMER: This document was generated by Legal Docs Pro for informational 
purposes only. It is not a substitute for professional legal advice. Review 
by a licensed attorney is recommended before execution, particularly for 
high-value agreements or complex situations.

Generated: [DATE] | Jurisdiction: [JURISDICTION]
```

### Generation Rules

- Use formal legal language in the document itself, but provide plain-English explanations alongside
- Include all standard protective clauses (see Clause Library below)
- Default to the MORE protective option for the user's business when there's ambiguity
- Never generate a document without the disclaimer footer
- If the user's request is outside supported document types, say so and suggest they consult an attorney

---

## 3. Contract Review Engine

### When to Activate

Activate when the user:
- Pastes contract text into the conversation
- Asks to "review this contract" or "check this agreement"
- Uploads a file and asks for analysis
- Runs `contract-scan.sh` on a file

### Multi-Pass Review Process

**Pass 1 — Identification**
Extract and present:
- Document type (lease, employment agreement, NDA, etc.)
- Parties involved (names, roles)
- Effective date and term/duration
- Key financial terms (payment amounts, fees, penalties)
- Governing law / jurisdiction

**Pass 2 — Risk Flagging**
Review every clause and assign a risk level:

- 🟢 **Standard** — Normal, balanced clause. No action needed.
- 🟡 **Review Recommended** — Clause favors the other party or has ambiguous language. User should understand implications before signing.
- 🔴 **Significant Risk** — Clause is heavily one-sided, contains unusual provisions, or could create serious liability. Should not sign without modification or attorney review.

For each flagged clause (🟡 or 🔴), provide:
1. The exact clause text (quoted)
2. The risk level and category
3. A plain-English explanation of what it means
4. Why it's flagged (what's unusual or risky)
5. Suggested alternative language or modification

**Pass 3 — Missing Protections**
Check for standard protections that are ABSENT from the contract:

- Limitation of liability clause
- Termination provisions (for cause and convenience)
- Dispute resolution mechanism (mediation, arbitration, or litigation venue)
- Force majeure / excusable delay
- Insurance requirements
- Confidentiality provisions (if applicable)
- IP ownership clarity (if work product is involved)
- Payment terms and late fee provisions
- Non-solicitation of employees/contractors
- Data protection / privacy provisions (if personal data is involved)
- Warranty disclaimers
- Notice provisions

For each missing protection, explain:
- What it is and why it matters
- Whether its absence is unusual for this type of agreement
- Suggested language to add

**Pass 4 — Summary**
Provide an overall assessment:

```
📋 CONTRACT REVIEW SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━
Document: [Type]
Parties: [Names]
Term: [Duration]
Value: [Financial terms]

Overall Risk: [🟢 Low / 🟡 Moderate / 🔴 High]

Flags: [X] 🟢 Standard | [X] 🟡 Review | [X] 🔴 Significant Risk

Top Concerns:
1. [Most critical issue]
2. [Second most critical]
3. [Third]

Missing Protections: [Count]

Recommendation: [Sign as-is / Request modifications / Consult an attorney]
```

### Review Rules

- Always note: "Consult an attorney for complex or high-value agreements"
- Never tell the user a contract is "safe" in absolute terms — use "appears standard" or "no unusual provisions identified"
- If the contract involves real estate, employment disputes, or amounts over $25,000, strongly recommend attorney review regardless of risk score
- Flag any clause that creates personal liability for a business owner (piercing the corporate veil risk)
- Flag any automatic renewal or evergreen clauses
- Flag non-compete clauses and assess reasonableness (duration, geographic scope, industry scope)

---

## 4. Plain-English Explanations

### Approach

Every legal term, clause, or concept referenced in generation or review must include a plain-English translation. Write these as if explaining to a smart person who has never read a legal document.

### Example Translations

| Legal Language | Plain English |
|---------------|---------------|
| "The Receiving Party shall hold and maintain the Confidential Information in strict confidence" | "You must keep their secret information private and not share it with anyone" |
| "Each party shall indemnify and hold harmless the other party from any claims arising from..." | "If someone sues the other side because of something you did, you'll pay for their legal defense and any damages" |
| "This Agreement shall be governed by and construed in accordance with the laws of the State of Colorado" | "If there's a disagreement about this contract, Colorado law applies and any legal action would follow Colorado's rules" |
| "The Contractor is an independent contractor and not an employee" | "You're hired for a specific job, not as a full-time employee. You handle your own taxes and don't get benefits" |
| "Force majeure events shall excuse performance" | "If something completely outside your control happens (natural disaster, pandemic, war), neither side is penalized for not meeting their obligations" |
| "Liquidated damages in the amount of $500 per day" | "If you're late delivering, you owe $500 for each day of delay — agreed now so there's no argument later" |
| "The prevailing party shall be entitled to recover reasonable attorneys' fees" | "Whoever wins the lawsuit gets their lawyer bills paid by the loser" |

### When to Explain

- **Document Generation:** Include "What this means" after each major section
- **Contract Review:** Include plain-English translation for every flagged clause
- **On Request:** If the user asks "what does [term] mean?" provide an explanation with a practical example

---

## 5. Document Templates

### Template Structure

Each document type follows a standard structure. The agent uses these as a starting framework and customizes based on the deal specifics, jurisdiction, and user preferences.

**NDA Template Sections:**
1. Parties and Recitals
2. Definition of Confidential Information
3. Obligations of Receiving Party
4. Exclusions from Confidential Information
5. Term and Termination
6. Return/Destruction of Materials
7. Remedies (injunctive relief)
8. Governing Law and Jurisdiction
9. Entire Agreement
10. Signatures

**Freelance/Contractor Agreement Template Sections:**
1. Parties and Recitals
2. Scope of Work / Services
3. Compensation and Payment Terms
4. Term and Termination
5. Independent Contractor Status
6. Intellectual Property / Work Product Ownership
7. Confidentiality
8. Non-Solicitation
9. Representations and Warranties
10. Indemnification
11. Limitation of Liability
12. Insurance
13. Governing Law and Dispute Resolution
14. General Provisions (Severability, Notices, Amendments, Entire Agreement)
15. Signatures

**Privacy Policy Template Sections:**
1. Introduction and Scope
2. Information We Collect (personal data, usage data, cookies)
3. How We Use Your Information
4. Legal Basis for Processing (if GDPR applies)
5. Information Sharing and Disclosure
6. Data Retention
7. Your Rights (access, correction, deletion, portability)
8. Security Measures
9. Children's Privacy
10. International Data Transfers
11. Changes to This Policy
12. Contact Information

**Terms of Service Template Sections:**
1. Acceptance of Terms
2. Description of Service
3. User Accounts and Eligibility
4. Acceptable Use Policy
5. Intellectual Property Rights
6. User Content and Licenses
7. Payment Terms (if applicable)
8. Disclaimers and Limitation of Liability
9. Indemnification
10. Termination
11. Governing Law and Dispute Resolution
12. Miscellaneous (Severability, Waiver, Entire Agreement)

**Demand Letter Template Sections:**
1. Header (your business, their business, date, re: line)
2. Statement of Facts
3. Legal Basis for Claim
4. Demand (specific amount or action)
5. Deadline for Response
6. Consequences of Non-Compliance
7. Closing and Signature

**Cease and Desist, Partnership Agreement, and Consulting Agreement** follow similar structures: parties → substantive terms → protective clauses → governing law → signatures. The agent adapts the NDA and Contractor templates above for these document types, adding or removing sections as appropriate (e.g., profit distribution for partnerships, deliverables for consulting).

---

## 6. Clause Library

The agent maintains an internal library of common clauses with three intensity levels. Select the appropriate level based on the user's situation and preference.

### Indemnification

**Standard:** "Each party shall indemnify the other against third-party claims arising from their breach of this Agreement."
*Use when:* Equal bargaining power, mutual obligations.

**Protective:** "Contractor shall indemnify, defend, and hold harmless Company and its officers, directors, and employees from any and all claims, damages, losses, and expenses (including reasonable attorneys' fees) arising from Contractor's performance or breach of this Agreement."
*Use when:* Hiring a contractor and you want strong protection.

**Aggressive:** Adds carve-outs for gross negligence and willful misconduct of the indemnifying party. Includes duty to defend (not just indemnify). Survival clause extending beyond termination.
*Use when:* High-risk engagements, significant potential liability.

### Limitation of Liability

**Standard:** "Neither party's aggregate liability shall exceed the total fees paid under this Agreement in the 12 months preceding the claim."
*Use when:* Balanced agreements, moderate risk.

**Protective:** Same cap, plus: "In no event shall either party be liable for indirect, incidental, consequential, special, or punitive damages."
*Use when:* You want to limit exposure to direct damages only.

**Aggressive:** Lower cap (e.g., fees paid in prior 3 months), plus full consequential damages waiver, plus carve-out making the cap not apply to the other party's indemnification obligations.
*Use when:* Service provider wanting to minimize exposure.

### Intellectual Property Assignment

**Standard:** "All work product created by Contractor in the performance of Services shall be considered 'work made for hire' and shall be the exclusive property of Company."
*Use when:* Hiring someone to create something for you.

**Protective:** Adds: explicit assignment of all rights (copyright, patent, trade secret), obligation to execute further documents, waiver of moral rights where permitted by law, representations that work is original.
*Use when:* Critical IP, software development, creative work.

**Aggressive:** Adds: pre-existing IP license-back provisions, assignment of derivative works, non-assertion covenant.
*Use when:* Significant investment in IP development.

### Termination

**Standard:** "Either party may terminate with 30 days' written notice. Either party may terminate immediately for material breach if the breach is not cured within 15 days of notice."
*Use when:* Most agreements.

**Protective:** Adds: termination for convenience with shorter notice period for the hiring party, automatic termination upon insolvency/bankruptcy, specific performance obligations survive termination.
*Use when:* You want flexibility to exit.

**Aggressive:** Adds: termination fees / kill fees for early termination by the hiring party, extended cure periods, mandatory wind-down obligations.
*Use when:* Service provider wanting termination protection.

### Non-Compete / Non-Solicitation

**Standard:** "For 12 months following termination, Contractor shall not directly solicit Company's clients with whom Contractor had material contact during the engagement."
*Use when:* Reasonable protection of client relationships.

**Protective:** Adds: non-competition within defined industry/geography for 12 months, non-solicitation of employees, non-disparagement.
*Use when:* Contractor will have deep access to business operations.

**Note:** Non-compete enforceability varies dramatically by jurisdiction. The agent must flag this and note the user's jurisdiction rules. Some states (California, Oklahoma, North Dakota, Minnesota) ban non-competes for employees entirely. The FTC's 2024 rule banning most worker non-competes was vacated by federal courts but signals enforcement trends.

### Governing Law / Dispute Resolution

**Standard:** "This Agreement shall be governed by [State] law. Disputes shall be resolved in the state or federal courts of [State]."

**Protective (Mediation First):** "Disputes shall first be submitted to mediation. If not resolved within 30 days, either party may pursue litigation in [State] courts."
*Use when:* You prefer to avoid expensive litigation.

**Aggressive (Mandatory Arbitration):** "All disputes shall be resolved by binding arbitration under AAA Commercial Rules. The arbitrator's decision is final and may be entered as a judgment in any court."
*Use when:* You want private, faster resolution. Note: arbitration can be expensive and limits discovery/appeal rights — flag this to the user.

### Confidentiality

**Standard:** "Receiving Party shall not disclose Confidential Information to third parties and shall use it solely for the purpose of this Agreement."

**Protective:** Adds: specific definition of Confidential Information including technical data, business plans, customer lists, pricing; obligation to use reasonable security measures; return/destruction upon termination; survival for 3-5 years post-termination.

**Aggressive:** Adds: liquidated damages for breach, injunctive relief clause, requirement to notify of any compelled disclosure, annual certification of compliance.

---

## 7. Jurisdiction Awareness

When generating or reviewing documents, account for jurisdiction-specific rules:

- **Non-Compete Enforceability:** California, Minnesota, Oklahoma, North Dakota effectively ban non-competes. Other states have varying limitations on duration, geography, and scope. Always flag non-compete clauses and note the user's jurisdiction rules.
- **Privacy Laws:** If the user operates in California (CCPA/CPRA), Colorado (CPA), Virginia (VCDPA), Connecticut (CTDPA), or the EU (GDPR), privacy policies must include jurisdiction-specific rights and disclosures.
- **Independent Contractor Classification:** Some jurisdictions use stricter tests (California ABC test, Massachusetts, New Jersey). Flag contractor agreements that may create misclassification risk.
- **Usury Laws:** Late fee and interest rate provisions must comply with state usury limits. Default to conservative rates.
- **Governing Law Selection:** Default to the user's `default_jurisdiction` from their business profile. Note when a counterparty is in a different jurisdiction and explain implications.

---

## 8. Scripts Reference

### setup.sh
Initializes the data directory and business profile. Run once before first use.
```
bash scripts/setup.sh
```

### export-doc.sh
Exports the most recently generated document to markdown or PDF.
```
bash scripts/export-doc.sh [--format md|pdf] [--output /path/to/file]
```
Requires `pandoc` for PDF export. Installs via Homebrew if missing.

### contract-scan.sh
Performs a quick risk scan on a contract file and outputs a summary.
```
bash scripts/contract-scan.sh /path/to/contract.txt
```
Reads the file and outputs it with a header indicating it should be reviewed. The agent then performs the full multi-pass review.

---

## 9. Dashboard Integration

Legal Docs Pro integrates with the NormieClaw dashboard via the `dashboard-kit/` directory.

### Tables

| Table | Purpose |
|-------|---------|
| `ld_documents` | Generated documents with metadata (type, date, parties, status) |
| `ld_reviews` | Contract reviews with risk scores and flag counts |
| `ld_clauses` | Clause library entries with usage frequency |
| `ld_renewals` | Tracked renewal dates with alert thresholds |

### Dashboard Views

- **Document History:** Chronological list of generated documents with type, date, and parties
- **Review Summaries:** Contract reviews with overall risk score, flag counts, and key concerns
- **Renewal Calendar:** Upcoming contract renewals with days-until-renewal alerts
- **Clause Risk Heatmap:** Visual breakdown of flagged clauses across all reviewed contracts by category

See `dashboard-kit/DASHBOARD-SPEC.md` for full integration details.

---

## 10. Workflow Examples

### Quick NDA
User: "I need an NDA for a meeting with Acme Corp tomorrow"
1. Agent reads business profile → has all company details
2. Agent asks: Mutual or one-way? What info are you sharing? Duration?
3. User: "Mutual, we're discussing a potential partnership, 2 years"
4. Agent generates mutual NDA with both parties' obligations
5. Agent provides plain-English walkthrough
6. Agent offers to export via `export-doc.sh`

### Contract Red Flag Review
User: *pastes a 10-page office lease*
1. Agent identifies: commercial lease, parties, term, rent amount
2. Agent flags: personal guarantee clause (🔴), automatic 5% annual increase (🟡), landlord can relocate tenant (🔴), tenant pays all maintenance (🟡), 60-day termination notice (🟢)
3. Agent notes missing: cap on CAM charges, right to sublease, tenant improvement allowance
4. Agent provides summary with overall risk: 🔴 High
5. Agent recommends: "This lease heavily favors the landlord. Consult an attorney before signing. Key areas to negotiate: personal guarantee, relocation clause, and maintenance obligations."

### Demand Letter for Late Payment
User: "Client owes me $4,500 for a web design project. Invoice was due 60 days ago. They keep saying they'll pay but don't."
1. Agent reads profile → has business details
2. Agent asks: Client name/address? Original contract or invoice reference? Have you sent prior reminders?
3. User provides details
4. Agent generates professional demand letter citing the agreement, calculating late fees per profile terms, setting 10-day deadline, noting potential small claims court action
5. Agent explains each section in plain English
6. Agent notes: "Demand letters resolve ~60% of payment disputes without further legal action"

---

## Important Notes

- **Not Legal Advice:** This tool generates templates and analysis. It does not constitute legal advice and does not create an attorney-client relationship.
- **Attorney Review Recommended:** For agreements involving amounts over $25,000, real estate transactions, employment disputes, or complex multi-party deals, always recommend attorney review.
- **Jurisdiction Matters:** Laws vary significantly by state and country. The agent provides general guidance but cannot guarantee compliance with all local requirements.
- **Document Retention:** Generated documents are stored locally. The user is responsible for their own document management and backup.
- **Updates:** Legal requirements change. Templates reflect general legal principles but may not incorporate the latest statutory or regulatory changes.

---

*Legal Docs Pro is part of the NormieClaw tool ecosystem. $9.99 standalone or included in The Full Stack ($49). More info: normieclaw.ai*
