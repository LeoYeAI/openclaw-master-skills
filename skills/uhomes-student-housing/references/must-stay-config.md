# Must-Stay List Configuration

The uhomes Must-Stay list (必住榜) is a curated ranking of top-rated student properties per city and university. Use this file to look up Must-Stay page URLs.

Last verified: 2026-03-16.

---

## Must-Stay URL Patterns

### University-level (大学维度) — preferred
```
https://en.uhomes.com/must-stay?city_id=0&school_id={school_id}&ads_type=82
```

### City-level (城市维度) — fallback
```
https://en.uhomes.com/must-stay?city_id={city_id}&school_id=0&ads_type=82
```

**Key finding**: `school_id` is a **global ID** — when `school_id > 0`, the `city_id` parameter is ignored. You can use `city_id=0` with any valid `school_id`.

**Priority**: University-level (school_id) > City-level (city_id) > Skip.

**IMPORTANT**: Only use IDs that match the user's search city/university. **NEVER** use a different city or university's Must-Stay data. If no match, skip Fetch B entirely.

---

## Known School IDs (University-level)

22 universities confirmed with Must-Stay data:

| school_id | University | City | Properties |
|-----------|-----------|------|-----------|
| 1 | University of Edinburgh | Edinburgh | 10 |
| 6 | University of Glasgow | Glasgow | 10 |
| 11 | Imperial College London | London | 10 |
| 12 | UCL (University College London) | London | 10 |
| 13 | King's College London | London | 10 |
| 15 | Queen Mary, University of London | London | 10 |
| 27 | University of The Arts London | London | 10 |
| 32 | London School of Economics (LSE) | London | 10 |
| 33 | University of Oxford | Oxford | 5 |
| 36 | University of Cambridge | Cambridge | 5 |
| 39 | University of Manchester | Manchester | 10 |
| 51 | University of Birmingham | Birmingham | 10 |
| 57 | University of Leeds | Leeds | 10 |
| 63 | University of Southampton | Southampton | 10 |
| 66 | University of Sheffield | Sheffield | 10 |
| 69 | Sheffield Hallam University | Sheffield | 10 |
| 70 | University of Liverpool | Liverpool | 10 |
| 73 | Durham University | Durham | 5 |
| 76 | University of Nottingham | Nottingham | 10 |
| 81 | University of Warwick | Coventry | 10 |
| 91 | University of Essex | Colchester | 5 |
| 97 | University of Kent | Canterbury | 5 |

### Slug-to-school_id quick lookup

| University slug (from city-index.md) | school_id |
|--------------------------------------|-----------|
| `university-of-edinburgh` | 1 |
| `university-of-glasgow` | 6 |
| `imperial-college-london` | 11 |
| `university-college-london` | 12 |
| `kings-college-london` | 13 |
| `queen-mary-university-of-london` | 15 |
| `university-of-the-arts-london` | 27 |
| `london-school-of-economics` | 32 |
| `university-of-oxford` | 33 |
| `university-of-cambridge` | 36 |
| `university-of-manchester` | 39 |
| `university-of-birmingham` | 51 |
| `university-of-leeds` | 57 |
| `university-of-southampton` | 63 |
| `university-of-sheffield` | 66 |
| `sheffield-hallam-university` | 69 |
| `university-of-liverpool` | 70 |
| `durham-university` | 73 |
| `university-of-nottingham` | 76 |
| `university-of-warwick` | 81 |
| `university-of-essex` | 91 |
| `university-of-kent` | 97 |

### School IDs not yet scanned

IDs 41-50 returned 403 (rate limited). IDs 101+ not tested. To expand coverage, test incrementally (max ~30 requests per session to avoid 403).

---

## Known City IDs

17 cities confirmed with Must-Stay data:

| city_id | City | Properties |
|---------|------|-----------|
| 5 | Edinburgh | 10 |
| 6 | Glasgow | 10 |
| 7 | London | 10 |
| 8 | Oxford | 5 |
| 9 | Cambridge | 5 |
| 10 | Manchester | 10 |
| 11 | Bristol | 10 |
| 12 | Birmingham | 10 |
| 13 | Leeds | 10 |
| 14 | Southampton | 10 |
| 15 | Sheffield | 10 |
| 16 | Liverpool | 10 |
| 17 | Durham | 5 |
| 18 | Nottingham | 10 |
| 19 | Coventry | 10 |
| 20 | Colchester | 5 |
| 22 | Reading | 5 |
| 25 | Newcastle | 10 |
| 26 | Cardiff | 10 |
| 50 | Boston (US) | 10 |

### City IDs with NO data

1, 2, 3, 4, 21 (Kent), 23 (Gloucester), 24, 27-49, 51+ (not tested except 50)

---

## Lookup Rules for the Skill

When the Skill determines the user's university and city in Step 1:

1. **University match** → look up `school_id` in the Slug-to-school_id table
   - If found → Fetch B uses `school_id={id}&city_id=0`
   - This gives university-specific Must-Stay data (best quality)

2. **No university match, but city match** → look up `city_id` in the City IDs table
   - If found → Fetch B uses `city_id={id}&school_id=0`
   - This gives city-wide Must-Stay data (good fallback)

3. **Neither match** → skip Fetch B, proceed with Fetch A only
   - No penalty to scoring — must_stay_bonus = 0 for all properties

**NEVER guess an ID. NEVER use a different city/university's data.**

---

## How the Skill Uses Must-Stay Data

1. When searching a city/university that has a known ID, Skill fetches the Must-Stay page in parallel with the university listing page
2. Properties appearing on both lists receive a scoring bonus (see SKILL.md Step 3 scoring algorithm)
3. Must-Stay properties are tagged with 🏆 in the output
4. If Must-Stay data is unavailable, the Skill proceeds normally — no penalty to any property

---

## Maintenance Notes

- uhomes returns **403 after ~30 rapid requests** — scan incrementally
- Property counts are either 5 or 10 per city/university
- Boston (city_id=50) is the **first non-UK city** with Must-Stay data — monitor for expansion to AU/CA/JP markets
- To discover new school_ids: test `https://en.uhomes.com/must-stay?city_id=0&school_id={N}&ads_type=82` in small batches
