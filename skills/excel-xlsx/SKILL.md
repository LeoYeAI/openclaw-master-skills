---
name: Excel / XLSX
slug: excel-xlsx
version: 1.0.1
homepage: https://clawic.com/skills/excel-xlsx
description: Read, write, and generate Excel files with correct types, dates, formulas, and cross-platform compatibility.
changelog: Added Core Rules and modern skill structure
metadata: {"clawdbot":{"emoji":"📗","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines. Ask user preferences naturally during conversation.

## When to Use

User needs to read, write, or generate Excel files (.xlsx, .xls, .xlsm). Agent handles type coercion, date serialization, formula evaluation, and cross-platform quirks.

## Architecture

Memory lives in `~/excel-xlsx/`. See `memory-template.md` for structure.

```
~/excel-xlsx/
└── memory.md     # Preferences, tools, pain points
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup | `setup.md` |
| Memory template | `memory-template.md` |

## Core Rules

### 1. Dates Are Serial Numbers
Excel stores dates as days since 1900-01-01 (Windows) or 1904-01-01 (Mac legacy). Check workbook date system before converting. Time is fractional: 0.5 = noon, 0.25 = 6 AM.

### 2. The 1900 Leap Year Bug
Excel incorrectly treats 1900 as a leap year. Serial 60 represents Feb 29, 1900 (invalid date). Account for this when calculating dates before March 1, 1900.

### 3. 15-Digit Precision Limit
Numbers beyond 15 digits silently truncate. Use TEXT format for: phone numbers, IDs, credit cards, any long numeric identifiers. Leading zeros also require TEXT.

### 4. Formulas vs Cached Values
Cells may contain both formula and cached result. Some readers return formula string, others return cached value. Force recalculation if cached values might be stale.

### 5. Merged Cells Are Traps
Only the top-left cell of a merged range holds the value. Reading other cells in the merge returns empty. Hidden rows/columns still contain data.

### 6. Cross-Platform Testing Required
Windows vs Mac Excel can differ in date system. LibreOffice/Google Sheets may not support all features. Always test roundtrip compatibility when generating files for unknown consumers.

### 7. Use Streaming for Large Files
Loading large files fully into RAM causes memory issues. Use streaming readers (row-by-row) for files with 100K+ rows. Empty rows at end may be padded by some writers.

## Common Traps

- **Type inference on read** → Numbers stored as text stay text; explicit conversion needed
- **Column index confusion** → A=0 or A=1 varies by library; always verify convention
- **Newlines in cells** → `\n` works but cell needs "wrap text" format to display
- **External references** → `[Book.xlsx]Sheet!A1` breaks when source file moves
- **Password protection** → Trivial to break; not real security; encrypt file externally if needed
- **XLSM files** → Contain macros (security risk); XLSB is binary (faster but less compatible)
- **Shared strings** → Large files reuse text indices; libraries handle this, but be aware

## Format Limits

| Format | Rows | Columns | Notes |
|--------|------|---------|-------|
| XLSX | 1,048,576 | 16,384 (XFD) | Modern default |
| XLS | 65,536 | 256 | Legacy, avoid |
| CSV | Unlimited | Unlimited | No formatting |

## Security & Privacy

**Data that stays local:**
- All file processing happens locally
- User preferences stored in `~/excel-xlsx/memory.md` with consent
- No external services called

**This skill does NOT:**
- Send data to external endpoints
- Require network access

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `csv` — CSV parsing and generation
- `data` — Data processing patterns
- `data-analysis` — Analysis workflows

## Feedback

- If useful: `clawhub star excel-xlsx`
- Stay updated: `clawhub sync`
