# deep-reading — Deep Reading for Zettelkasten

All-in-one deep reading skill: turn books, long articles, and reports into a connected knowledge network (structure notes, atomic notes, method notes, index). Uses Mortimer Adler for structure, Feynman for clarity, Luhmann for linking, plus Pragmatist and Critics. Enforces case fidelity and actionable extraction.

## When to Use

Use this skill when:

- You want to **deeply digest** a book, long article, research report, or paper and **build a knowledge network** (not just a summary).
- You need **structure notes** (reading order + argument tree), **atomic notes** (concepts), **method notes** (SOPs/checklists), and **index notes** (entry points).
- You say things like: “help me turn this book into a Zettelkasten,” “depth-first read this report,” “structure note + atomic notes for this article.”

## Quick Reference

| Phase   | Output                    | Key artifact                          |
|---------|---------------------------|----------------------------------------|
| 0       | Pre-game plan             | `YYYYMMDD_01_[title]_执行计划.md`     |
| 1       | Structure note            | `templates/structure_note_template.md`|
| 2       | Index note                | `templates/index_note_template.md`   |
| 2.5     | Index onboarding          | Mount to existing index; move to index dir |
| 3       | Atomic notes + Luhmann Scan | `references/luhmann_scan.md`       |
| 4       | Method notes              | `templates/method_note_template.md`   |
| 5       | Feynman review            | De-jargon, logic, topology            |
| 6       | Network review            | ≥2 links per note; multi-index mount  |
| 6.5     | Workflow audit (optional) | If `workflow-audit` skill is present  |

## Workflow at a Glance

1. **Phase 0**: Produce an execution plan (≥6 TODOs + context).
2. **Phase 1**: Create structure note (core thesis + logic chain). Uses `structure-note` if available.
3. **Phase 2**: Create index note (keywords + entry points). Uses `index-note` if available.
4. **Phase 2.5**: Mount the new index to an existing index; move index file into your index directory.
5. **Phase 3**: Create atomic notes from structure; run Luhmann Scan (dependencies, links, methods) per note.
6. **Phase 4**: Turn discovered methods into method notes (SOP/template/checklist).
7. **Phase 5**: Feynman review (clarity, metaphor, logic, surprise links).
8. **Phase 6**: Ensure ≥2 bidirectional links per note; complete index onboarding; multi-index mount check.
9. **Phase 6.5**: Optional workflow-audit pass if that skill is installed.

## Requirements

- **Paths**: The skill assumes an **index directory** (e.g. `03_索引/` or `Index/`) and a **daily/task directory** (e.g. `05_每日记录/YYYY/MM/DD` or `Daily/`). Adapt path names in the skill or your vault to match.
- **Optional companion skills**: For full automation, `structure-note`, `index-note`, `file-organize`, and `workflow-audit` can be used when available; the skill still works with manual steps if they are missing.
- **Language**: SKILL.md and templates are in Chinese; prompts and outputs follow your locale.

## Repo Layout

```
deep-reading/
├── README.md           # This file
├── SKILL.md            # Main skill instructions (required)
├── references/
│   ├── expert_personas.md
│   └── luhmann_scan.md
└── templates/
    ├── atomic_note_template.md
    ├── index_note_template.md
    ├── method_note_template.md
    └── structure_note_template.md
```

