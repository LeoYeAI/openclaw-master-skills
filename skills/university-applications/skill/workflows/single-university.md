# Single University Workflow

## Overview

This workflow collects data for a single specified university.

## Trigger

Natural language commands like:

- "Collect master's admissions info for HKU only"
- "Get CUHK master's programs"
- "Show me HKUST taught postgraduate programmes"

## University Mapping

| User Says | Maps To | File |
|-----------|---------|------|
| HKU, Hong Kong University, 港大 | The University of Hong Kong | universities/01-hku.md |
| CUHK, Chinese University, 中大 | The Chinese University of Hong Kong | universities/02-cuhk.md |
| HKUST, UST, Science & Tech, 科大 | HK University of Science & Technology | universities/03-hkust.md |
| PolyU, Poly, Polytechnic, 理工 | The Hong Kong Polytechnic University | universities/04-polyu.md |
| CityU, City University, 城大 | City University of Hong Kong | universities/05-cityu.md |
| HKBU, Baptist, 浸會, 浸大 | Hong Kong Baptist University | universities/06-hkbu.md |
| LingU, Lingnan, 嶺南 | Lingnan University | universities/07-lingu.md |
| EdUHK, Education University, 教大 | The Education University of Hong Kong | universities/08-eduhk.md |
| HKMU, Metropolitan, 都會, OUHK | Hong Kong Metropolitan University | universities/09-hkmu.md |

## Workflow Steps

```
1. Identify which university the user is asking about (use mapping table above)
2. Read SKILL-SPEC.md for rules
3. Read DATA-SCHEMA.md for data structure
4. Read the corresponding universities/XX-xxx.md file
5. Collect all master's programs for that university
6. Validate data
7. Generate summary statistics (for this university only)
8. Output in requested format(s) using the appropriate template(s)
```

## Output

If no specific format is requested, default to **Markdown** format.
If the user requests a specific format, use only that format template.
