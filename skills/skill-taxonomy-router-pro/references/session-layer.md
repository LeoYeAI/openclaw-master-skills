# Session layer

Use this as the lightweight conversational layer for `skill-router`.

## Keep in active chat memory
- Route to the most specific relevant skill first.
- Prefer the lowest sufficient risk.
- Do not trust newly downloaded skills by default.
- New-skill risk operations require explicit user approval.
- If a skill has risk or conflict, ask the user before using that risky/conflicting path.
- Prefer canonical skills over overlapping variants.
- Start from summarized pool/index views before drilling into individual skills.
- Use scripts to query indexes/reports instead of reading large files or scanning many titles into chat.
- Do not invoke the full skill-router workflow by default on every task; use it only when task complexity, ambiguity, risk, or overlap makes routing help materially valuable.
- Report progress as small deltas, not repeated full summaries.

## Push to scripts/off-chat processing
- Full skill index scans
- Backlog prioritization details
- Overlap family expansion
- Source-risk review details
- Intake state bookkeeping
- Bulk download state and registry diffs
