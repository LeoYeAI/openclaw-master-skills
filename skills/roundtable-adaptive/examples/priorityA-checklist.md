# Roundtable Priority A — Checklist

## 1) Dedup check (thread reuse)
- [ ] Trigger same topic twice in `#roundtable`
- [ ] First trigger creates thread
- [ ] Second trigger reuses same thread (no new orchestrator spawn)
- [ ] Reuse message posted: `♻️ Duplicate topic detected — reusing existing thread.`

## 2) `--quick` mode
- [ ] Run: `roundtable --quick [topic]`
- [ ] Confirm meta-panel is skipped
- [ ] Confirm only 1 round is executed
- [ ] Confirm final synthesis generated

## 3) Meta-panel path
- [ ] Run: `roundtable [topic]` (without `--quick` and `--panel`)
- [ ] Confirm 4 meta analysts run
- [ ] Confirm workflow decision logged (parallel/sequential/hybrid)
- [ ] Confirm panel + synthesis model come from meta recommendations

## 4) Quality scorecard logging
Per run log these fields:
- topic
- mode
- workflow_type
- elapsed_time_sec
- consensus_pct
- validated (yes/no/partial)
- panel_degraded (true/false)

Suggested location:
`{workspace}/memory/roundtables/scorecard.jsonl`

JSONL line example:
```json
{"ts":"2026-02-26T20:00:00+01:00","topic":"Should we ship X?","mode":"vote","workflow_type":"parallel_debate","elapsed_time_sec":184,"consensus_pct":67.5,"validated":"yes","panel_degraded":false}
```
