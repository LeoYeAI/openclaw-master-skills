# Scoring methodology

## How scores are calculated

Base score: **10 points**. Each checklist failure deducts points based on severity.

| Severity | Deduction per issue | Cap |
|----------|-------------------|-----|
| HIGH | -1.5 | No cap (3 HIGHs = 5.5, effectively a rewrite) |
| MEDIUM | -0.5 | -3 total (even 10 MEDIUMs cap at -3) |
| LOW | -0.2 | -1 total (even 10 LOWs cap at -1) |

**Formula:** `Score = max(0, 10 - (HIGH_count × 1.5) - min(MEDIUM_count × 0.5, 3) - min(LOW_count × 0.2, 1))`

## Score interpretation

| Score | Rating | Action |
|-------|--------|--------|
| 9-10 | Excellent | Ship it. Minor polish only. |
| 7-8 | Good | PASS threshold. Fix MEDIUMs when convenient. |
| 5-6 | Needs work | Fix all HIGHs before using in production. |
| 3-4 | Poor | Significant restructuring needed. |
| 0-2 | Major rewrite | Start from template, salvage what you can. |

## Example calculations

### Example 1: Clean skill
```text
HIGHs: 0  = -0.0
MEDIUMs: 2 = -1.0
LOWs: 3   = -0.6

Score = 10 - 0 - 1.0 - 0.6 = 8.4/10 (Good)
```

### Example 2: Typical first draft
```text
HIGHs: 2  = -3.0
MEDIUMs: 4 = -2.0
LOWs: 1   = -0.2

Score = 10 - 3.0 - 2.0 - 0.2 = 4.8/10 (Poor)
```

### Example 3: Monolithic skill
```text
HIGHs: 5  = -7.5
MEDIUMs: 6 = -3.0 (capped)
LOWs: 4   = -0.8

Score = 10 - 7.5 - 3.0 - 0.8 = 0/10 (floor) (Major rewrite)
```

## PASS/FAIL threshold

A skill **PASSES** when:
- Score is 7 or higher, AND
- Zero HIGH severity issues

A skill with score 8 but one HIGH issue still **NEEDS WORK** because HIGHs indicate spec violations or LLM confusion risks.

## Batch scan ratings

In batch mode (`--scan-all`), skills are grouped:

| Group | Criteria |
|-------|----------|
| PASS | Score 7+ AND 0 HIGHs |
| NEEDS WORK | Score 5-6 OR any HIGHs |
| REWRITE | Score below 5 |
