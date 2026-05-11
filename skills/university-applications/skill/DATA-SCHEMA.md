# Data Schema: HK University Master's Admissions

## Overview

This document defines the exact data structure for collecting and storing master's program admissions information. All data fields, types, and validation rules are specified here.

## University Record Schema

Each university has one record with the following fields:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| university_name_en | String | ✅ | Official English name |
| university_name_zh | String | ✅ | Official Chinese name |
| abbreviation | String | ✅ | Common abbreviation (e.g., HKU) |
| official_website | URL | ✅ | Main university website |
| admissions_url | URL | ✅ | Graduate admissions page |
| ugc_funded | Boolean | ✅ | Whether UGC-funded |

## Program Record Schema

Each master's program has one record with the following fields:

| # | Field | Type | Required | Example | Validation |
|---|-------|------|----------|---------|------------|
| 1 | university_abbr | String | ✅ | "HKU" | Must match a university record |
| 2 | faculty | String | ✅ | "Faculty of Engineering" | Official faculty name |
| 3 | program_name_en | String | ✅ | "Master of Science in Computer Science" | Full official name |
| 4 | program_name_zh | String | ⬚ | "計算機科學理學碩士" | Chinese name if available |
| 5 | degree_type | Enum | ✅ | "MSc" | One of: MSc/MA/MBA/MEd/MFA/MSW/LLM/MChinMed/MPH/MArch/Other |
| 6 | study_mode | Enum | ✅ | "Full-time" | One of: Full-time/Part-time/Full-time & Part-time |
| 7 | duration | String | ✅ | "1 year (FT) / 2 years (PT)" | Include both modes if applicable |
| 8 | tuition_fee_total | String | ✅ | "HKD 180,000" | Total program fee in HKD |
| 9 | tuition_fee_annual | String | ⬚ | "HKD 90,000/year" | Annual fee if paid yearly |
| 10 | application_open_date | String | ✅ | "1 September 2025" | When applications open |
| 11 | application_deadline_main | String | ✅ | "30 November 2025" | Main round deadline |
| 12 | application_deadline_late | String | ⬚ | "30 April 2026" | Late round deadline if exists |
| 13 | english_req_ielts | String | ✅ | "Overall 6.5, no sub-score < 5.5" | IELTS requirement |
| 14 | english_req_toefl | String | ✅ | "IBT 80" | TOEFL requirement |
| 15 | english_req_other | String | ⬚ | "CET-6: 430" | Other English tests accepted |
| 16 | other_requirements | String | ⬚ | "Bachelor's in related field" | Additional entry requirements |
| 17 | program_description | String | ⬚ | "This program aims to..." | Brief program description |
| 18 | official_url | URL | ✅ | "https://www.msc-cs.hku.hk" | Direct link to program page |
| 19 | data_collected_date | Date | ✅ | "2025-10-01" | When this data was collected |
| 20 | data_freshness_note | String | ⬚ | "⚠️ Verify at official site" | Freshness warning if needed |

## Field Format Standards

### Currency
- Always in HKD (Hong Kong Dollars)
- Format: `HKD XXX,XXX`
- If fee varies, show range: `HKD 120,000 - 180,000`

### Dates
- Format: `DD Month YYYY` (e.g., "30 November 2025")
- If exact date unknown: "Around [Month] [Year]"
- If rolling admissions: "Rolling (until places filled)"

### English Requirements
- IELTS: `Overall X.X, no sub-score below X.X`
- TOEFL iBT: `Total XX`
- TOEFL pBT: `Total XXX`
- CET-6: `XXX`
- If program has special requirements, note them

### URLs
- Must be full URLs starting with `https://`
- Must be from official university domains only
- Must link directly to the program page when possible

## Data Template (Markdown Table Row)

When collecting data, use this format for each program:

```markdown
### [Program Full Name]

| Field | Value |
|-------|-------|
| University | [University Name] ([Abbreviation]) |
| Faculty | [Faculty/School Name] |
| Program (EN) | [Full English Name] |
| Program (ZH) | [Chinese Name or N/A] |
| Degree Type | [MSc/MA/MBA/etc.] |
| Study Mode | [Full-time/Part-time/Both] |
| Duration | [X year(s) FT / X year(s) PT] |
| Tuition (Total) | HKD [Amount] |
| Tuition (Annual) | HKD [Amount]/year |
| Application Opens | [Date] |
| Main Deadline | [Date] |
| Late Deadline | [Date or N/A] |
| IELTS | [Requirement] |
| TOEFL | [Requirement] |
| Other English | [Other tests or N/A] |
| Other Requirements | [Requirements or N/A] |
| Description | [Brief description] |
| Official URL | [URL] |
| Collected Date | [Date] |
| Freshness Note | [Note or ✅ Verified] |
```

## Summary Statistics Schema

After collecting all programs, generate these summary statistics:

| Statistic | Description |
|-----------|-------------|
| Total Programs | Count of all programs collected |
| Programs per University | Breakdown by university |
| Programs per Degree Type | Count by MSc/MA/MBA/etc. |
| Tuition Fee Range | Min, Max, Average across all programs |
| Tuition Fee by University | Average fee per university |
| Deadline Distribution | Programs by deadline month |
| IELTS Range | Min and Max IELTS requirements |
| Study Mode Distribution | Full-time vs Part-time vs Both |
