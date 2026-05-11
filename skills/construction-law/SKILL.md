---
name: construction-law
description: Construction law analysis covering FIDIC (2017 suite), PSSCOC, SIA Conditions, NEC4, and JCT. Use when (1) analysing contract clauses, risk allocation, or obligations; (2) preparing or reviewing claims (delay, disruption, prolongation, EOT, loss & expense); (3) comparing contract forms or advising on procurement strategy; (4) drafting or reviewing notices, correspondence, or contract documents; (5) building obligations registers or notice calendars; (6) discussing dispute resolution (DAB/DAAB, adjudication, arbitration, mediation, CAB); (7) Singapore-specific construction law (SOP Act, BCA, SIArb); (8) MDB procurement frameworks (ADB, World Bank). NOT for: non-construction commercial contracts, pure property/real-estate conveyancing, or insurance law. Also assists with QS measurement checking (BOQ review, quantity verification, rate analysis, unit consistency).
---

# Construction Law Skill

> ## 🔒 Security & Safety
>
> **All Python scripts in this skill are safe, read-only template generators.**
>
> - ✅ **No network access** — no API calls, no HTTP requests, no telemetry
> - ✅ **No subprocess execution** — no shell commands, no external programs
> - ✅ **No filesystem traversal** — only writes to the user-specified `--output` path
> - ✅ **Read-only static reference data** — contract clauses bundled with the skill
> - ✅ **Verified clean:** VirusTotal Benign • ClawScan Benign
>
> The "Static analysis: Review" flag is auto-triggered because `excel_register.py` uses Python's standard `importlib` to compose sibling scripts in the same `scripts/` folder — this is benign and intentional.
>
> **Safe to install and use.** 🛡️

---

Analysis and advisory for international construction contracts, claims, and dispute resolution.

## Quick Reference — Contract Forms

| Form | Type | Design By | Key Feature |
|------|------|-----------|-------------|
| FIDIC Red | Measure & Pay | Employer | Employer bears quantity risk |
| FIDIC Yellow | D&B | Contractor | Single-point design + build responsibility |
| FIDIC Silver | EPC/Turnkey | Contractor | Maximum risk on contractor |
| FIDIC Gold | DBO | Contractor | Includes O&M phase |
| FIDIC Emerald | Underground | Varies | Tunnelling-specific risk sharing |
| NEC4 Option A | Activity Schedule | Varies | Lump sum with early warning mechanism |
| NEC4 Option C | Target Cost | Varies | Pain/gain sharing, Clause 10.1 good faith |
| PSSCOC | Government | Employer | Singapore public sector standard |
| SIA | Private | Employer | Singapore private sector standard |
| JCT | Various | Varies | UK standard forms |

## Workflow

### 1. Identify the Contract Form
**ALWAYS ask which edition/year of the contract form.** Many SG projects still use PSSCOC 2017 (7th Ed) even for new awards — don't assume the latest edition. Same applies to FIDIC (1999 vs 2017), SIA, NEC, and JCT.

Determine which standard form (or bespoke) applies. Check for amendments, particular conditions, and any deleted/modified clauses.

Common editions in active use:
- PSSCOC: 2017 (7th Ed) ← still widely used | 2020 (8th Ed)
- PSSCOC D&B: 2014 (6th Ed) | 2020 (7th Ed)
- FIDIC: 1999 (still common internationally) | 2017 (current)
- SIA: 9th Ed (2010) | 11th Ed
- NEC: NEC3 (still active) | NEC4 (current)

### 2. Clause Analysis
For any clause question:
- Quote the relevant clause number and edition
- Identify the obligation, right, or risk it creates
- Note any time-bars or notice requirements
- Cross-reference with related clauses
- Flag amendments that change the standard position

### 3. Claims Analysis Framework
For delay/disruption/EOT claims, follow this structure:

**Step 1 — Entitlement**: Identify the contractual basis (which clause?)
**Step 2 — Causation**: Establish cause-and-effect (what event → what delay?)
**Step 3 — Notice**: Verify notice requirements met (time-bar compliance)
**Step 4 — Substantiation**: Evidence and records supporting the claim
**Step 5 — Quantification**: Calculate time/cost impact

### 4. Notice Calendar
When building notice calendars, capture:
- Clause reference
- Trigger event
- Notice period (days)
- Recipient
- Consequence of non-compliance (time-bar? loss of entitlement?)

### 5. Risk Allocation Analysis
Risk should be allocated to the party best able to:
1. Identify that risk
2. Control that risk
3. Mitigate that risk
4. Absorb that risk

Incorrect allocation → pricing inflation, claims escalation, disputes.

## Reference Files

For detailed clause-by-clause analysis, load the relevant reference:

- **FIDIC analysis**: See [references/fidic.md](references/fidic.md) — Red, Yellow, Silver, Gold, Emerald clause guides, time-bars, notice requirements, DAAB procedures
- **Singapore contracts**: See [references/singapore.md](references/singapore.md) — PSSCOC, SIA Conditions, SOP Act, BCA regulatory framework, SIArb
- **Claims & EOT**: See [references/claims.md](references/claims.md) — Delay analysis methods (as-planned vs as-built, impacted as-planned, collapsed as-built, time impact analysis), disruption, prolongation, global claims, concurrent delay
- **Dispute resolution**: See [references/disputes.md](references/disputes.md) — DAB/DAAB, adjudication, arbitration, mediation, CAB, enforcement
- **Procurement & tendering**: See [references/procurement.md](references/procurement.md) — MDB frameworks, procurement strategy, evaluation methods, collaborative contracting

## Scripts (Premium Features)

Three automated tools for contract administration:

### Notice Calendar Generator
Generates a complete notice/obligations calendar for any supported contract form.
```bash
python3 scripts/notice_calendar.py --form fidic-red --format md
python3 scripts/notice_calendar.py --form psscoc --format csv --output notices.csv
```
Supported forms: `fidic-red`, `fidic-yellow`, `psscoc`, `sia`, `nec4`

### Claims Template Generator
Produces structured claim notices, EOT applications, variation claims, and interim payment templates.
```bash
python3 scripts/claims_template.py --list
python3 scripts/claims_template.py --form fidic-red --type notice-of-claim --output notice.md
python3 scripts/claims_template.py --form psscoc --type eot-application --output eot.md
```
Templates include: clause references, section structure, placeholder fields, reservation of rights.

### Obligations Register Generator
Creates a trackable register of Contractor and/or Employer obligations with priorities and categories.
```bash
python3 scripts/obligations_register.py --form fidic-red --party both --format md
python3 scripts/obligations_register.py --form psscoc --party contractor --format csv --output obligations.csv
```
Supported forms: `fidic-red`, `psscoc`, `sia`

### SOP Act Payment Timeline Calculator
Calculates all statutory deadlines from a payment claim date under Singapore's SOP Act.
```bash
python3 scripts/sop_calculator.py --claim-date 2026-06-30
python3 scripts/sop_calculator.py --claim-date 2026-06-30 --response-period 14 --format csv --output timeline.csv
```
Outputs: full timeline with critical deadlines, smash-and-grab warnings, time-bar alerts.

### FIDIC Contract Comparator
Side-by-side comparison of FIDIC Red, Yellow, Silver, and Emerald Books across 6 topics.
```bash
python3 scripts/fidic_comparator.py --forms red,yellow,silver --topic risk
python3 scripts/fidic_comparator.py --forms red,silver --topic all --format csv --output comparison.csv
```
Topics: `overview`, `risk`, `claims`, `disputes`, `payment`, `termination`, `all`

### Delay Analysis Calculator
Input delay events and get critical path impact analysis with EOT entitlement and LD exposure.
```bash
python3 scripts/delay_calculator.py --baseline-start 2026-05-11 --baseline-end 2030-05-10 \
  --add "Late access|2026-06-01|2026-06-30|employer|critical" \
  --add "Weather|2026-07-15|2026-07-25|neutral|critical"
python3 scripts/delay_calculator.py --baseline-start 2026-05-11 --baseline-end 2030-05-10 --events events.json --format json
```
Outputs: delay summary, EOT entitlement, LD exposure, concurrent delay detection, recommendations.

### Excel Register Generator
Exports obligations registers and notice calendars to formatted .xlsx with colour-coded priorities.
```bash
python3 scripts/excel_register.py --form fidic-red --type both --output contract_admin.xlsx --commencement 2026-05-11
python3 scripts/excel_register.py --form psscoc --type obligations --output obligations.xlsx
```
Requires: `openpyxl` (`pip3 install openpyxl`)

## Key Principles (Always Apply)

1. **Read the contract first** — standard form positions mean nothing if amended
2. **Time-bars are fatal** — always check notice periods before anything else
3. **Concurrent delay** — different jurisdictions treat this differently; state the applicable approach
4. **Good faith** — no general duty in English/Singapore law unless express (NEC Clause 10.1); mandatory in French law (Art. 1104)
5. **Fitness for purpose vs reasonable skill & care** — contractor design (Yellow/Silver) vs consultant design (White Book)
6. **Prevention principle** — employer cannot benefit from their own act of prevention; may override liquidated damages if no EOT mechanism exists
