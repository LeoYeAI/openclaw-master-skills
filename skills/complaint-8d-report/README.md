# Customer Complaint 8D Report (complaint-8d-report)

Generates or completes **8D reports** (Eight Disciplines) from complaint data, with a standard template and D1–D8 fill-in guidance.

## When to use

- Customer complaints requiring an 8D or CAR (Corrective Action Report)
- Quality deviations and systematic defect recurrence prevention
- Standard-format complaint reports and closure documentation

## How to use

In an OpenClaw session, state what you need, for example:

- "Write an 8D report"
- "8D for product XXX, customer found surface scratches…"
- "Create 8D for case CC-2025-001"

The agent will follow the workflow in `SKILL.md`: gather information, generate the report skeleton, and guide you through each discipline.

## Contents

| File / folder | Description |
|---------------|-------------|
| `SKILL.md` | Main skill: workflow, report template, hints per D, multi-customer format handling |
| `reference.md` | 8D methodology, tools, multi-customer formats |
| `formats/` | Optional: one file per customer format (section order and headings); see `formats/README.md` |
| `formats/automotive-oem-example.md` | Example customer-specific format |
| `examples/sample-8d-snippet.md` | D2/D4/D5 example snippets (format reference) |
| `clawhub.json` | ClawHub publish metadata |

## Install (from ClawHub)

```bash
clawhub install complaint-8d-report
```

Takes effect in a new session.
