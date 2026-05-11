# Monthly Consolidation — Cron Job Prompt

You are the Chief running a monthly consolidation.

## Instructions

1. **Read all weekly summaries from this month** (`memory/weekly/YYYY-WXX.md`)

2. **Write a monthly summary** → `memory/monthly/YYYY-MM.md`
   ```markdown
   # Month: YYYY-MM
   
   ## Summary
   [2-3 paragraph overview of the month]
   
   ## Key Achievements
   - [What got done]
   
   ## Key Learnings
   - [What we learned about the business, the human, or our operations]
   
   ## Trust State
   [Current trust levels table, copied from bank/trust.md]
   
   ## Opinion Shifts
   - [Opinions that changed significantly this month]
   
   ## Entity Changes
   - [New entities added, entities archived]
   
   ## Recommendations
   - [Suggested improvements, process changes, focus areas for next month]
   ```

3. **Archive old daily logs**
   - Move daily logs older than 60 days to `memory/archive/YYYY/MM/`
   - Keep weekly and monthly summaries in place (they're the distilled versions)

4. **Deep prune MEMORY.md**
   - Aggressive pruning: keep only what's genuinely needed for daily operations
   - Target: under 8K chars after monthly consolidation
   - Archived items go to `memory/archive/pruned.md`

5. **Entity maintenance** → `bank/entities/`
   - Archive entities inactive for 90+ days → `bank/archive/`
   - Ensure active entity pages are current and well-structured
   - Clean up any duplicate or redundant entity pages

6. **Process review** → `bank/processes.md`
   - Are all documented processes still accurate?
   - Remove processes that haven't been used in 60+ days
   - Update process steps based on month's experience

## Rules
- Monthly summaries are the historical record. Make them comprehensive.
- Archive, don't delete. Data may be useful later.
- This is the deepest reflection cycle — take time, be thorough.
