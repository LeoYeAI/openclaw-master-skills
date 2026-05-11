# Full Collection Workflow

## Overview

This workflow orchestrates the complete data collection process for all 22 Hong Kong universities/institutions and generates output in all 5 formats.

## Trigger

Any of these natural language commands:

- "Collect all HK university master's admissions info"
- "Run the full collection workflow"
- "Get all Hong Kong university master's program data"
- "Use the HK admissions skill to collect everything"

## Workflow Steps

### Phase 1: Preparation

```
1. Read SKILL-SPEC.md → Understand the rules and constraints
2. Read DATA-SCHEMA.md → Understand the data structure
3. Note the current date for data freshness tracking
```

### Phase 2: Data Collection (Per University)

Execute these in order. For each university, read the corresponding file in `universities/` and collect data per the template:

**UGC-Funded Universities (8):**
```
Step 2.1:  Read universities/01-hku.md    → Collect all HKU master's programs
Step 2.2:  Read universities/02-cuhk.md   → Collect all CUHK master's programs
Step 2.3:  Read universities/03-hkust.md  → Collect all HKUST master's programs
Step 2.4:  Read universities/04-polyu.md  → Collect all PolyU master's programs
Step 2.5:  Read universities/05-cityu.md  → Collect all CityU master's programs
Step 2.6:  Read universities/06-hkbu.md   → Collect all HKBU master's programs
Step 2.7:  Read universities/07-lingu.md  → Collect all LingU master's programs
Step 2.8:  Read universities/08-eduhk.md  → Collect all EdUHK master's programs
```

**Self-Financing / Private Institutions (14):**
```
Step 2.9:  Read universities/09-hkmu.md   → Collect all HKMU master's programs
Step 2.10: Read universities/10-hksyu.md  → Collect all HKSYU master's programs
Step 2.11: Read universities/11-hsuhk.md  → Collect all HSUHK master's programs
Step 2.12: Read universities/12-sfu.md    → Collect all SFU master's programs
Step 2.13: Read universities/13-hkapa.md  → Collect all HKAPA master's programs
Step 2.14: Read universities/14-twc.md    → Collect all TWC master's programs
Step 2.15: Read universities/15-nyc.md    → Collect all NYC master's programs (if any)
Step 2.16: Read universities/16-thei.md   → Collect all THEi master's programs
Step 2.17: Read universities/19-gcc.md    → Collect all GCC master's programs (if any)
Step 2.18: Read universities/20-cihe.md   → Collect all CIHE master's programs (if any)
Step 2.19: Read universities/21-hkct.md   → Collect all HKCT master's programs (if any)
Step 2.20: Read universities/22-uowchk.md → Collect all UOWCHK master's programs (if any)
Step 2.21: Read universities/23-vtc.md    → Collect all VTC master's programs (if any)
```

> Note: Some smaller institutions may not offer master's programmes. If none found, record "No master's programmes currently offered" for that institution.

### Phase 3: Validation

```
For each collected program:
✅ Verify all required fields are filled
✅ Verify all URLs are from official domains
✅ Verify tuition fees are in HKD format
✅ Verify dates use correct format
✅ Verify IELTS/TOEFL scores are within valid ranges
✅ Flag any uncertain or potentially outdated data
```

### Phase 4: Summary Statistics

```
Calculate:
- Total program count
- Programs per university
- Programs per degree type
- Tuition fee min/max/average/median
- Average tuition per university
- Deadline distribution by month
- English requirement summary
- Study mode distribution
```

### Phase 5: Output Generation

Generate ALL 5 formats:

```
Step 5.1: Read output-templates/excel-template.md → Generate TSV/CSV output
Step 5.2: Read output-templates/word-template.md → Generate Word-compatible HTML
Step 5.3: Read output-templates/pdf-template.md → Generate print-ready HTML for PDF
Step 5.4: Read output-templates/html-template.md → Generate interactive webpage
Step 5.5: Read output-templates/markdown-template.md → Generate Markdown document
```

### Phase 6: Delivery

Present all outputs to the user with clear instructions for each format:

```
📊 Excel/CSV → Save as .tsv, open in Excel/Sheets
📄 Word → Save as .html, open in Word, save as .docx
📕 PDF → Save as .html, open in browser, Print → Save as PDF
🌐 HTML → Save as .html, open in browser (interactive features)
📝 Markdown → Save as .md, view in any Markdown renderer
```

## Error Handling

- If a university's data cannot be fully collected, include what is available and mark gaps
- If a URL is uncertain, provide the main admissions page URL as fallback
- If tuition fee information is not available, mark as "Check official site" with URL
- Always complete the workflow even if some data points are missing

## Quality Assurance

Before final delivery, verify:

- [ ] All 22 universities/institutions are represented (or noted if no master's programmes)
- [ ] Summary statistics are accurate
- [ ] All output formats are generated
- [ ] All links point to official domains
- [ ] Disclaimer is included in every format
- [ ] Data collection date is noted
