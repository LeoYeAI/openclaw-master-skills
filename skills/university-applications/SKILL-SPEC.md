# Skill Specification: HK University Master's Admissions Collector

## Skill Identity

- **Name**: hk-university-admissions
- **Version**: 1.0.0
- **Type**: Prompt-based Data Collection & Formatting Skill
- **Implementation**: Pure Markdown (No code, no dependencies)
- **Interface**: Natural Language

## Purpose

Collect, organize, and format official master's degree program admissions information from all recognized universities in Hong Kong SAR, China.

## Scope

### In Scope
- All taught master's programs (MSc, MA, MBA, MEd, MFA, MPhil, LLM, etc.)
- Information from all recognized degree-granting universities and institutions in Hong Kong (22 total)
- Both UGC-funded and self-financing/private institutions
- Current academic year admissions cycle data
- Official English and Chinese program names
- Tuition fees in HKD
- Application timeline (open date, deadline, late deadline)
- English language proficiency requirements
- Program official webpage links

### Out of Scope
- Research-based doctoral programs (PhD)
- Undergraduate programs
- Exchange programs
- Short courses and certificates
- Non-degree programs

## Data Source Rules

### MANDATORY: Official Sources Only

Every piece of data collected MUST come from official university domains:

```
✅ ALLOWED domains:
   *.hku.hk              - The University of Hong Kong
   *.cuhk.edu.hk         - The Chinese University of Hong Kong
   *.ust.hk              - HK University of Science and Technology
   *.polyu.edu.hk        - The Hong Kong Polytechnic University
   *.cityu.edu.hk        - City University of Hong Kong
   *.hkbu.edu.hk         - Hong Kong Baptist University
   *.ln.edu.hk           - Lingnan University
   *.eduhk.hk            - The Education University of Hong Kong
   *.hkmu.edu.hk         - Hong Kong Metropolitan University
   *.hksyu.edu            - Hong Kong Shue Yan University
   *.hsu.edu.hk          - The Hang Seng University of Hong Kong
   *.sfu.edu.hk          - Saint Francis University
   *.hkapa.edu           - The Hong Kong Academy for Performing Arts
   *.twc.edu.hk          - Tung Wah College
   *.ny.edu.hk           - Hong Kong Nang Yan College of Higher Education
   *.thei.edu.hk         - Technological & Higher Education Institute of HK
   *.gratia.edu.hk       - Gratia Christian College
   *.cihe.edu.hk         - Caritas Institute of Higher Education
   *.hkct.edu.hk         - Hong Kong College of Technology
   *.uowchk.edu.hk       - UOW College Hong Kong
   *.vtc.edu.hk          - Vocational Training Council

❌ BLOCKED sources (must NEVER use):
   - Education agency websites
   - Student forums or review sites
   - Third-party ranking websites
   - Social media platforms
   - News articles
   - Any non-official domain
```

### Data Freshness
- Always note the date of data collection
- If the LLM's training data may be outdated, clearly mark with: "⚠️ Verify at official site - data may have been updated"
- Always provide the official URL for users to verify

## Quality Rules

1. **Accuracy**: Only state what is confirmed from official sources
2. **Completeness**: Collect ALL available fields; mark missing ones as "N/A - Check Official Site"
3. **Consistency**: Use the same format across all universities
4. **Currency**: HKD for all monetary values
5. **Bilingual**: Include both English and Chinese names when available
6. **Linking**: Every program must have its official URL
7. **Transparency**: Clearly state when information could not be confirmed

## Output Format Requirements

The skill supports 5 output formats:

| Format | Description | Use Case |
|--------|-------------|----------|
| **Excel** | CSV with headers, tab-separated, Excel-compatible | Data analysis, sorting, filtering |
| **Word** | Structured document with headings and tables | Formal reports, printing |
| **PDF** | Print-ready formatted document | Sharing, archiving |
| **HTML** | Responsive webpage with search and filter | Online browsing, interactive use |
| **Markdown** | Structured MD with tables and links | Documentation, version control |

## Workflow Steps

```
Step 1: COLLECT    → Gather data from each university's official site
Step 2: VALIDATE   → Cross-check data fields, flag uncertainties
Step 3: ORGANIZE   → Structure data per skill/DATA-SCHEMA.md
Step 4: FORMAT     → Apply output template(s) as requested
Step 5: DELIVER    → Present formatted output to user
```
