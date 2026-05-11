# Sample Output - Skill Execution Example

> This file demonstrates what the output looks like when the skill is executed.
> Below is a sample with 3 programs to illustrate the data format.

---

## Sample Markdown Output (Excerpt)

### Executive Summary

| Metric | Value |
|--------|-------|
| Total Universities | 9 |
| Total Programs | 3 (sample) |
| Tuition Range | HKD 120,000 - HKD 588,000 |
| Average Tuition | HKD 302,667 |

---

### The University of Hong Kong (HKU)

> 🌐 Official Admissions: https://www.gradsch.hku.hk/gradsch/prospective-students/programmes-on-offer

#### Master of Science in Computer Science

| Field | Details |
|-------|---------|
| Degree | MSc |
| Faculty | Faculty of Engineering |
| Mode | Full-time |
| Duration | 1 year |
| Tuition (Total) | HKD 200,000 |
| Application Opens | 2 October 2025 |
| **Main Deadline** | **13 January 2026** |
| Late Deadline | N/A |
| IELTS | Overall 6.0, no sub-score below 5.5 |
| TOEFL | iBT 80 |
| Other English | N/A |
| Requirements | Bachelor's degree in Computer Science, Computer Engineering, or related discipline |
| 🔗 Official Page | [https://admissions.hku.hk/tpg/programme/master-of-science-in-computer-science](https://admissions.hku.hk/tpg/programme/master-of-science-in-computer-science) |
| ⚠️ Freshness | Verify at official site - data based on 2025/26 intake cycle |

---

### The Chinese University of Hong Kong (CUHK)

> 🌐 Official Admissions: https://www.gs.cuhk.edu.hk/admissions/programme/taught

#### Master of Business Administration (MBA)

| Field | Details |
|-------|---------|
| Degree | MBA |
| Faculty | CUHK Business School |
| Mode | Full-time |
| Duration | 16 months |
| Tuition (Total) | HKD 588,000 |
| Application Opens | 1 September 2025 |
| **Main Deadline (R1)** | **31 October 2025** |
| Late Deadline (R3) | 31 March 2026 |
| IELTS | Overall 6.5 |
| TOEFL | iBT 79 |
| Other English | GMAT/GRE recommended |
| Requirements | Bachelor's degree, minimum 3 years work experience |
| 🔗 Official Page | [https://mba.cuhk.edu.hk](https://mba.cuhk.edu.hk) |
| ⚠️ Freshness | Verify at official site |

---

### Hong Kong Baptist University (HKBU)

> 🌐 Official Admissions: https://gs.hkbu.edu.hk/admission/taught-postgraduate-programmes

#### Master of Arts in Translation and Bilingual Communication

| Field | Details |
|-------|---------|
| Degree | MA |
| Faculty | Faculty of Arts |
| Mode | Full-time & Part-time |
| Duration | 1 year (FT) / 2 years (PT) |
| Tuition (Total) | HKD 120,000 |
| Application Opens | 1 November 2025 |
| **Main Deadline** | **1 March 2026** |
| Late Deadline | 30 April 2026 |
| IELTS | Overall 6.5 |
| TOEFL | iBT 79 |
| Other English | CET-6: 450 |
| Requirements | Bachelor's degree in any discipline, strong bilingual ability |
| 🔗 Official Page | [https://gs.hkbu.edu.hk/programmes/master-of-arts-ma-in-translation-and-bilingual-communication](https://gs.hkbu.edu.hk/programmes/master-of-arts-ma-in-translation-and-bilingual-communication) |
| ⚠️ Freshness | Verify at official site |

---

## Sample Excel/CSV Output (Excerpt)

```tsv
University	Faculty	Program (EN)	Degree	Mode	Duration	Tuition Total (HKD)	Application Opens	Main Deadline	Late Deadline	IELTS	TOEFL	Official URL
HKU	Faculty of Engineering	MSc in Computer Science	MSc	Full-time	1 year	200,000	2 Oct 2025	13 Jan 2026	N/A	6.0 (sub 5.5)	80	https://admissions.hku.hk/tpg/programme/master-of-science-in-computer-science
CUHK	CUHK Business School	MBA	MBA	Full-time	16 months	588,000	1 Sep 2025	31 Oct 2025	31 Mar 2026	6.5	79	https://mba.cuhk.edu.hk
HKBU	Faculty of Arts	MA in Translation and Bilingual Communication	MA	FT & PT	1yr FT / 2yr PT	120,000	1 Nov 2025	1 Mar 2026	30 Apr 2026	6.5	79	https://gs.hkbu.edu.hk/programmes/master-of-arts-ma-in-translation-and-bilingual-communication
```

---

## How This Sample Was Generated

1. The skill read `SKILL-SPEC.md` for rules
2. Read `DATA-SCHEMA.md` for structure
3. Read `universities/01-hku.md`, `universities/02-cuhk.md`, `universities/06-hkbu.md`
4. Collected 1 program from each (for demo purposes)
5. Validated all URLs point to official domains
6. Applied `output-templates/markdown-template.md` and `output-templates/excel-template.md`

In a real execution, ALL programs from ALL 9 universities would be collected.

---

> ⚠️ **Note**: This is a SAMPLE with illustrative data. When running the actual skill,
> real data from official university websites will be collected and may differ from these examples.
