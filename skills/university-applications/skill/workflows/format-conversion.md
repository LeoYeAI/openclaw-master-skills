# Format Conversion Workflow

## Overview

This workflow converts already-collected data into a specific output format.

## Trigger

Natural language commands like:

- "Convert the collected data to Excel format"
- "Output as HTML webpage"
- "Generate a PDF from the admissions data"
- "Give me the data in Word format"
- "Output in all formats"

## Format Mapping

| User Says | Format | Template File |
|-----------|--------|--------------|
| Excel, spreadsheet, CSV, TSV, 表格 | Excel/CSV | output-templates/excel-template.md |
| Word, document, doc, docx, 文档 | Word | output-templates/word-template.md |
| PDF, print, 打印 | PDF | output-templates/pdf-template.md |
| HTML, webpage, web, website, 网页 | HTML | output-templates/html-template.md |
| Markdown, MD, 文本 | Markdown | output-templates/markdown-template.md |
| All formats, all, everything, 所有格式 | All 5 | All templates |

## Workflow Steps

```
1. Identify which format(s) the user wants (use mapping table above)
2. Ensure data has already been collected (if not, run collection first)
3. Read the corresponding output template(s) from output-templates/
4. Apply the template to the collected data
5. Present the formatted output with usage instructions
```

## Multi-Format Output Order

When generating all formats, output in this order:
1. **Markdown** (quickest to review inline)
2. **Excel/CSV** (data analysis)
3. **HTML** (interactive browsing)
4. **Word** (formal document)
5. **PDF** (print/archive)

Each format should be clearly separated with a heading and usage instructions.
