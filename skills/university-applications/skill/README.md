# 🎓 Hong Kong Universities Master's Admissions Skill

> A pure Markdown-based prompt skill for collecting official master's program admissions information from all Hong Kong universities.

## Overview

This skill is a **prompt-based workflow** implemented entirely in Markdown files. It requires **no programming languages, no dependencies, and no installations**. It works by providing structured prompts that guide an LLM to collect, organize, and format official admissions data.

## How to Use (Natural Language)

Simply tell your AI assistant one of the following:

### Collect All Information
```
Please use the Hong Kong Universities Admissions Skill to collect master's program 
admissions information for all Hong Kong universities and output in all formats.
```

### Collect for a Specific University
```
Use the HK admissions skill to collect master's admissions info for HKU only, 
output as Markdown and HTML.
```

### Output in a Specific Format
```
Using the collected HK university data, generate an Excel-compatible output.
```

### Available Natural Language Commands

You can use **English or Chinese** to interact with this skill:

| English Command | Chinese Command | What It Does |
|----------------|----------------|-------------|
| "Collect all HK university master's admissions info" | "收集所有香港大学硕士招生信息" | Run full collection workflow, covering all 22 universities/institutions |
| "Collect admissions info for HKU only" | "只收集港大的硕士项目" | Single university collection (supports EN/CN name recognition) |
| "Output as Excel" | "输出为Excel格式" | Generate TSV file, directly importable to Excel/Google Sheets |
| "Output as HTML webpage" | "输出为HTML网页" | Generate interactive webpage (search, filter, dark mode) |
| "Output in all formats" | "输出所有格式" | Generate all 5 formats at once (Excel/Word/PDF/HTML/Markdown) |
| "Compare tuition across universities" | "比较各校学费" | Generate cross-university comparison table |
| "Output as [format]" | "输出为[格式]" | Generate specific format (Excel/Word/PDF/HTML/Markdown) |
| "Collect admissions info for [university]" | "收集[大学名]的硕士项目" | Collect for one specific university |
| "Compare [field] across universities" | "比较各校[字段]" | Compare tuition/deadlines/requirements/etc. |
| "Show programs for [faculty/field]" | "显示[学科领域]的项目" | Filter programs by academic field |

### University Name Recognition

The skill recognizes universities by multiple names:

| University | Recognized Names |
|-----------|-----------------|
| The University of Hong Kong | HKU, 港大, 香港大学 |
| The Chinese University of Hong Kong | CUHK, 中大, 香港中文大学 |
| HK University of Science & Technology | HKUST, UST, 科大, 香港科技大学 |
| The Hong Kong Polytechnic University | PolyU, 理工, 香港理工大学 |
| City University of Hong Kong | CityU, 城大, 香港城市大学 |
| Hong Kong Baptist University | HKBU, 浸大, 浸會, 香港浸会大学 |
| Lingnan University | LingU, 嶺南, 岭南大学 |
| The Education University of Hong Kong | EdUHK, 教大, 香港教育大学 |
| Hong Kong Metropolitan University | HKMU, 都會, 都会大学, 香港都会大学, OUHK, 公开大学 |
| Hong Kong Shue Yan University | HKSYU, 树仁, 仁大, 香港树仁大学 |
| The Hang Seng University of Hong Kong | HSUHK, 恒大, 恒生, 香港恒生大学 |
| Saint Francis University | SFU, 圣方济各, 珠海学院, 珠海 |
| HK Academy for Performing Arts | HKAPA, 演艺, 演艺学院 |
| Tung Wah College | TWC, 东华, 东华学院 |
| Hong Kong Nang Yan College | NYC, 能仁, 能仁专上学院 |
| Technological & Higher Education Inst. | THEi, 高科院 |
| Gratia Christian College | GCC, 宏恩 |
| Caritas Institute of Higher Education | CIHE, 明爱, 明爱专上学院 |
| Hong Kong College of Technology | HKCT, 港专, 港专学院 |
| UOW College Hong Kong | UOWCHK, 伍伦贡, 香港伍伦贡学院 |
| Vocational Training Council | VTC, 职训局 |

## Skill Structure

```
skill/
├── skill.md                           # ⭐ Skill entry point (all-in-one definition)
├── README.md                          # This file - Entry point & usage guide
├── README-CN.md                       # Chinese usage guide (中文版)
├── SKILL-SPEC.md                      # Skill specification & rules
├── DATA-SCHEMA.md                     # Data structure definition
├── COLLECTION-PROMPT.md               # Master prompt for data collection
├── universities/                      # Per-university collection prompts
│   ├── 01-hku.md                      # The University of Hong Kong
│   ├── 02-cuhk.md                     # Chinese University of Hong Kong
│   ├── 03-hkust.md                    # HK University of Science & Technology
│   ├── 04-polyu.md                    # Hong Kong Polytechnic University
│   ├── 05-cityu.md                    # City University of Hong Kong
│   ├── 06-hkbu.md                     # Hong Kong Baptist University
│   ├── 07-lingu.md                    # Lingnan University
│   ├── 08-eduhk.md                    # Education University of Hong Kong
│   ├── 09-hkmu.md                     # Hong Kong Metropolitan University
│   ├── 10-hksyu.md                    # Hong Kong Shue Yan University
│   ├── 11-hsuhk.md                    # Hang Seng University of Hong Kong
│   ├── 12-sfu.md                      # Saint Francis University (formerly Chu Hai)
│   ├── 13-hkapa.md                    # HK Academy for Performing Arts
│   ├── 14-twc.md                      # Tung Wah College
│   ├── 15-nyc.md                      # Hong Kong Nang Yan College
│   ├── 16-thei.md                     # Technological & Higher Education Inst.
│   ├── 17-chuhai-redirect.md          # Redirect → 12-sfu.md
│   ├── 18-ouhk-redirect.md            # Redirect → 09-hkmu.md
│   ├── 19-gcc.md                      # Gratia Christian College
│   ├── 20-cihe.md                     # Caritas Institute of Higher Education
│   ├── 21-hkct.md                     # Hong Kong College of Technology
│   ├── 22-uowchk.md                   # UOW College Hong Kong
│   └── 23-vtc.md                      # Vocational Training Council
├── output-templates/                  # Output format templates
│   ├── excel-template.md              # CSV/Excel output template
│   ├── word-template.md               # Word document output template
│   ├── pdf-template.md                # PDF output template
│   ├── html-template.md               # HTML webpage output template
│   └── markdown-template.md           # Markdown output template
├── workflows/                         # Workflow orchestration
│   ├── full-collection.md             # Full collection workflow
│   ├── single-university.md           # Single university workflow
│   └── format-conversion.md           # Format conversion workflow
└── examples/                          # Example outputs
    └── sample-output.md               # Sample of expected output
```

## Covered Universities & Institutions (22 Total)

### 🏛️ UGC-Funded Universities (8)

| # | University | Abbreviation | Official Admissions URL |
|---|-----------|--------------|------------------------|
| 1 | The University of Hong Kong | HKU | https://www.gradsch.hku.hk/gradsch/prospective-students/programmes-on-offer |
| 2 | The Chinese University of Hong Kong | CUHK | https://www.gs.cuhk.edu.hk/admissions/programme/taught |
| 3 | The Hong Kong University of Science and Technology | HKUST | https://pg.ust.hk/prospective-students/admissions/taught-postgraduate-admissions |
| 4 | The Hong Kong Polytechnic University | PolyU | https://www.polyu.edu.hk/study/pg/taught-postgraduate |
| 5 | City University of Hong Kong | CityU | https://www.cityu.edu.hk/pg/taught-postgraduate-programmes |
| 6 | Hong Kong Baptist University | HKBU | https://gs.hkbu.edu.hk/admission/taught-postgraduate-programmes |
| 7 | Lingnan University | LingU | https://www.ln.edu.hk/sgs/taught-postgraduate-programmes |
| 8 | The Education University of Hong Kong | EdUHK | https://www.eduhk.hk/gradsch/index.php/prospective-students/taught-postgraduate-programmes |

### 🏢 Self-Financing / Private Universities & Institutions (14)

| # | University / Institution | Abbreviation | Official Admissions URL |
|---|-------------------------|--------------|------------------------|
| 9 | Hong Kong Metropolitan University | HKMU | https://admissions.hkmu.edu.hk/tpg/ |
| 10 | Hong Kong Shue Yan University | HKSYU | https://gao.hksyu.edu/postgraduate-programmes/ |
| 11 | The Hang Seng University of Hong Kong | HSUHK | https://www.hsu.edu.hk/en/academic-programmes/postgraduate-programmes/ |
| 12 | Saint Francis University (formerly Chu Hai) | SFU | https://www.sfu.edu.hk/en/programmes/postgraduate/ |
| 13 | The Hong Kong Academy for Performing Arts | HKAPA | https://www.hkapa.edu/academic-programmes/postgraduate |
| 14 | Tung Wah College | TWC | https://www.twc.edu.hk/en/Programmes/postgraduate |
| 15 | Hong Kong Nang Yan College of Higher Education | NYC | https://www.ny.edu.hk/en/programmes |
| 16 | Technological & Higher Education Institute of HK | THEi | https://www.thei.edu.hk/programme/postgraduate |
| 17 | Gratia Christian College | GCC | https://www.gratia.edu.hk/programmes |
| 18 | Caritas Institute of Higher Education | CIHE | https://www.cihe.edu.hk/en/programmes |
| 19 | Hong Kong College of Technology | HKCT | https://www.hkct.edu.hk/en/programmes |
| 20 | UOW College Hong Kong | UOWCHK | https://www.uowchk.edu.hk/programmes |
| 21 | Vocational Training Council | VTC | https://www.vtc.edu.hk/admission/en/programme/ |

> ⚠️ **Note**: Some private institutions primarily offer undergraduate programmes. Their master's programme availability is verified during collection. Institutions without master's programmes will be noted in the output.

> 📌 **Renamed institutions**: Chu Hai College → Saint Francis University (2022); Open University of HK → HK Metropolitan University (2021)

## Data Fields Collected

For each master's program, the following fields are collected:

- **University Name** (English & Chinese)
- **Faculty / School / Department**
- **Program Name** (English & Chinese)
- **Degree Type** (MSc / MA / MBA / MEd / MFA / etc.)
- **Study Mode** (Full-time / Part-time / Mixed)
- **Duration**
- **Tuition Fee** (Total & Per Year, in HKD)
- **Application Open Date**
- **Application Deadline** (Main Round & Late Round if applicable)
- **English Language Requirements** (IELTS / TOEFL / CET-6 scores)
- **Other Entry Requirements**
- **Program Description**
- **Official Program URL**
- **Last Updated Date**

## Important Rules

1. ✅ **ONLY official university websites** are used as data sources
2. ❌ **NO third-party sources** (no agency sites, no forums, no ranking sites)
3. ✅ All URLs must point to `.hku.hk`, `.cuhk.edu.hk`, `.ust.hk`, `.polyu.edu.hk`, `.cityu.edu.hk`, `.hkbu.edu.hk`, `.ln.edu.hk`, `.eduhk.hk`, or `.hkmu.edu.hk` domains
4. ✅ Data must include the collection date for freshness tracking
5. ✅ If information is unavailable, mark as "Not Available - Check Official Site"

---

> 📖 中文版: [README-CN.md](README-CN.md)
