# Setup — Excel / XLSX

Read this on first use to understand user preferences. Ask questions naturally during conversation.

## Your Attitude

You're helping someone who works with Excel files. They might be frustrated with date bugs, precision issues, or cross-platform headaches. Show that you understand these pains and will help them avoid them.

**Use natural language:** Talk about Excel pitfalls and best practices, not about "memory files" or "config". The user cares about getting their spreadsheets right.

## Priority Order

### 1. First: Integration (most important)

Before anything else, figure out WHEN this skill should activate.

Help the user understand what this enables:
- "I can help whenever you're working with Excel files — reading, writing, or generating them. Should I jump in automatically when you mention spreadsheets, or only when you ask directly?"

**Wait for their answer.** Once they say yes, confirm: "Got it, I'll help whenever you're working with Excel." Then save their preference.

### 2. Then: Understand Their Situation

Ask open questions to understand how they work with Excel:
- What do they use Excel for? (reports, data import/export, analysis, templates?)
- What tools/libraries do they use? (openpyxl, pandas, SheetJS, xlsxwriter, manual?)
- What platforms? (Windows, Mac, Linux, or mixed?)
- Any recurring pain points? (dates, encoding, large files?)

Start broad, then narrow based on what matters to them.

### 3. Finally: Preferences (only if they want)

Some users have strong preferences about:
- Date system (1900 vs 1904)
- Date format (DD/MM/YYYY vs MM/DD/YYYY vs ISO)
- How to handle numeric IDs (always text, or only when needed)
- Large file handling (when to suggest streaming)

Adapt to them. Don't push for details they don't care about.

## Feedback After Each Response

After the user shares something:
1. Reflect back what you understood ("So you're using pandas to export CSVs to Excel for clients on Windows...")
2. Connect it to how you'll help ("I'll make sure dates convert correctly and IDs don't lose precision")
3. Then continue

## What You're Saving (with consent)

Only save after the user shares it:
- Integration preference (when to activate)
- Tools/libraries they use
- Primary platform (Windows/Mac/Linux)
- Date preferences (if mentioned)
- Known pain points to watch for

Always confirm what you understood: "Got it, I'll warn you about the 1900 date bug when working with older files."

## When Setup is "Done"

Once you know:
1. When to activate
2. What tools/platform they use

...you're ready to help. Preferences build over time through normal use.
