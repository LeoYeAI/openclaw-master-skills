# Memory Template — Excel / XLSX

Create `~/excel-xlsx/memory.md` with this structure:

```markdown
# Excel / XLSX Memory

## Status
status: ongoing
last: YYYY-MM-DD
integration: pending | done | declined

## Environment
platform: windows | mac | linux | mixed
libraries: [openpyxl, pandas, xlsxwriter, SheetJS, etc.]

## Preferences
date_system: 1900 | 1904 | auto
date_format: DD/MM/YYYY | MM/DD/YYYY | YYYY-MM-DD | none
numeric_ids: always_text | when_needed | none
large_files: suggest_streaming | handle_normally

## Pain Points
<!-- Things they've mentioned struggling with -->
- [e.g., "dates always break when opening on Mac"]
- [e.g., "phone numbers lose leading zeros"]

## Common Tasks
<!-- What they typically do with Excel -->
- [e.g., "export reports for finance team"]
- [e.g., "import CSVs from legacy system"]

## Notes
<!-- Other observations -->

---
*Updated: YYYY-MM-DD*
```

## Status Values

| Value | Meaning | Behavior |
|-------|---------|----------|
| `ongoing` | Still learning | Gather context as they work |
| `complete` | Has enough context | Work normally |
| `paused` | User said "not now" | Don't ask, work with what you have |

## Preference Defaults

If no preference specified, use these sensible defaults:
- **date_system:** auto (detect from workbook)
- **date_format:** ISO (YYYY-MM-DD) when generating, preserve when reading
- **numeric_ids:** when_needed (warn for >15 digits or leading zeros)
- **large_files:** suggest_streaming (mention for 100K+ rows)

## What to Track Over Time

As you help them:
- Note which warnings actually helped vs annoyed them
- Remember which libraries they use
- Track recurring issues (same mistake = add to pain points)
- Update preferences when they express them

## Integration Note

After user confirms their preferences:
- Save when to activate this skill
- Save key preferences for future sessions
