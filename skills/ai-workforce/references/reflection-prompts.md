# Reflection Cycle Prompts

Use these as cron job prompts (payload.kind: "agentTurn", sessionTarget: "isolated").

## Daily Reflection

Schedule: end of each working day

```
Run daily reflection. Today's date: use current date.

1. Read today's daily log (memory/YYYY-MM-DD.md). If none exists, exit.
2. Extract key learnings → append to bank/experience.md (2-3 bullets max)
3. Update bank/opinions.md — confirm/contradict existing opinions, adjust confidence
4. Update bank/trust.md — log task outcomes, promote if 3+ consecutive successes
5. Update bank/entities/*.md — new people/projects? Update existing? Update bank/index.md
6. Prune MEMORY.md if over 12K chars → move pruned items to memory/archive/pruned.md
7. Append ## Reflection section to today's daily log (3-5 sentences)

Rules: Don't fabricate events. Don't change trust without evidence. Be honest about mistakes.
```

## Weekly Reflection

Schedule: end of each week

```
Run weekly reflection.

1. Read past 7 days of daily logs (memory/YYYY-MM-DD.md)
2. Write weekly summary → memory/weekly/YYYY-WXX.md
   Include: Highlights, Wins, Misses, Trust Changes, Patterns Noticed, Next Week Focus
3. Review trust progression in bank/trust.md — promote/demote based on full week evidence
4. Review bank/opinions.md — adjust confidence, remove stale low-confidence items
5. Check entity staleness in bank/entities/ — flag items not referenced in 30+ days
6. Review bank/processes.md — new SOPs from repeated tasks? Existing ones need updating?

Rules: Weekly summaries must be standalone. Be brutally honest about misses.
```

## Monthly Consolidation

Schedule: 1st of each month

```
Run monthly consolidation.

1. Read all weekly summaries from this month
2. Write monthly summary → memory/monthly/YYYY-MM.md
   Include: Summary (2-3 paragraphs), Key Achievements, Key Learnings, Trust State, Opinion Shifts, Entity Changes, Recommendations
3. Archive daily logs older than 60 days → memory/archive/YYYY/MM/
4. Deep prune MEMORY.md to under 8K chars → archive pruned items
5. Archive entities inactive 90+ days → bank/archive/
6. Review bank/processes.md — remove unused processes (60+ days)

Rules: Monthly summaries are historical record — be comprehensive. Archive, never delete.
```

## Capability Audit (Monthly, after consolidation)

```
Run monthly capability audit.

1. Read bank/capabilities.md
2. List all currently available tools (check what you can call)
3. List all installed skills
4. For each tool/skill, ask: "How could this help the business given what I know from bank/world.md?"
5. Update the Available table with any new entries
6. Review Gaps — any now solvable with current tools?
7. Review Proposed — any approved but not implemented? Set them up.
8. Add 1-2 Expansion Ideas based on recent work patterns from bank/experience.md
9. Propose new capability uses to the human (max 2 per month — don't overwhelm)
```
