# Skill Types and Templates

> Merged guide: first determine the skill's cognitive operation type, then
> choose a structural template.

---

## Table of Contents

- [1. Skill Type Taxonomy](#1-skill-type-taxonomy)
- [2. Quick Type Identification](#2-quick-type-identification)
- [3. Type to Output Contract Mapping](#3-type-to-output-contract-mapping)
- [4. Template Index](#4-template-index)
- [5. Template 1: Minimal Skill](#5-template-1-minimal-skill)
- [6. Template 2: Read-Only Skill](#6-template-2-read-only-skill)
- [7. Template 3: Script-Driven Skill](#7-template-3-script-driven-skill)
- [8. Template 4: Knowledge-Intensive Skill](#8-template-4-knowledge-intensive-skill)
- [9. Template 5: Plugin Skill](#9-template-5-plugin-skill)
- [10. Selection Guide](#10-selection-guide)

---

## 1. Skill Type Taxonomy

Determine the core cognitive operation before choosing structure:

| Type | Core Operation | Input -> Output | Common Triggers |
|------|---------------|-----------------|-----------------|
| Summary | Compress with coverage | Many items -> few items (no loss) | "summarize, extract key points, meeting notes" |
| Insight | Extract key explanations | Many signals -> few key causes | "what's the key issue, why is this happening" |
| Generation | Create within constraints | Constraints -> new content | "write, draft, generate, give me a version" |
| Decision | Weigh trade-offs and commit | Options + criteria -> choice + rationale | "which one, recommend, how to decide" |
| Evaluation | Score against standards | Artifact -> score/gaps/improvements | "review, audit, check quality, grade" |
| Diagnosis | Trace root cause and fix | Symptoms -> root cause + fix path | "not working, error, why did it fail" |
| Persuasion | Bridge positions to action | My goal + audience mindset -> acceptable action | "convince boss, write pitch, negotiation" |
| Planning | Decompose into executable path | Goal -> milestones/deps/steps | "plan, roadmap, break down task" |
| Research | Discover and structure knowledge | Question -> structured answer + sources | "research, compare, gather data" |
| Facilitation | Elicit implicit information | Implicit knowledge -> explicit answers | "interview guide, facilitate discussion" |
| Transformation | Map format/structure | Format A -> Format B | "convert to, transform, extract fields" |

## 2. Quick Type Identification

Ask one question to determine ~80%:

```
Which best describes what you need?
1) Comprehensive coverage "summary" (compress without losing info)
2) Key-only "insight/diagnosis" (find the most important causes)
3) Produce "new content" (generate/plan/transform)
4) Reach a "conclusion" (decide/evaluate)
```

Confirm with: "This sounds like a [Type] skill: the goal is [operation]. Correct?"

## 3. Type to Output Contract Mapping

| Type | Recommended Output Structure |
|------|------------------------------|
| Summary | Coverage checklist + structured points + uncertainty notes |
| Insight | Top 3-5 insights (with evidence) + why (mechanism) + actionable advice |
| Generation | Strict template + variable placeholders + style options + self-check |
| Decision | Single recommendation + trade-off table + risks + next steps |
| Evaluation | Score/grade + gap list + actionable fix per gap + verification steps |
| Diagnosis | Repro steps + root cause + minimal fix + regression test |
| Persuasion | Audience profile + argument structure + script/draft + CTA |
| Planning | Milestones + dependencies/critical path + risks + deliverables |
| Research | Question list + source table (URL+date) + conclusions (with confidence) |
| Facilitation | Goal + question sequence + follow-up strategy + summary template |
| Transformation | Input/output schema + mapping rules + error handling + example I/O |

### Common Confusions to Clarify

- **Summary vs Insight**: "Cover everything" vs "Only the decisive signals"
- **Research vs Insight**: "Find data" vs "Explain what data means"
- **Evaluation vs Decision**: "Score an artifact" vs "Choose among options"
- **Diagnosis vs Evaluation**: "Find gaps" vs "Trace root cause and fix"

---

## 4. Template Index

| Template | Use Case | Complexity | Files |
|----------|----------|-----------|-------|
| Minimal | Quick prototype, simple task | Low | 1 |
| Read-Only | Code review, analysis | Low | 1 |
| Script-Driven | Automation tasks | Medium | 3+ |
| Knowledge-Intensive | Expert domain | High | 5+ |
| Plugin | Claude Code plugin | Medium | 4+ |

**Recommended flow**: Determine type (Section 1) -> Choose template (below)
-> Write output contract (Section 3).

---

## 5. Template 1: Minimal Skill

Best for: quick prototypes, simple prompts, personal preferences.

```
my-skill/
└── SKILL.md
```

```yaml
---
name: my-skill
description: >
  Brief description of what this skill does. Use when [scenario 1],
  [scenario 2], or [scenario 3].
---

# My Skill

## Quick Start
[Simplest usage]

## Instructions
1. Step one
2. Step two

## Output Format
[Expected output example]
```

## 6. Template 2: Read-Only Skill

Best for: code review, analysis, auditing (no file modifications).

```
my-reviewer/
├── SKILL.md
└── references/
    └── checklist.md
```

```yaml
---
name: my-reviewer
description: >
  Reviews [target] for [criteria]. Use when performing [type] reviews,
  auditing [target], or checking [quality aspect].
---

# My Reviewer

## Decision Tree
- Full review -> Follow complete checklist
- Quick review -> Focus on critical items only

## Workflow
1. Analyze target
2. Apply checklist (references/checklist.md)
3. Generate findings report

## Output Contract
[Structured report template with severity levels]
```

## 7. Template 3: Script-Driven Skill

Best for: automation, file processing, validation tasks.

```
my-processor/
├── SKILL.md
├── scripts/
│   ├── process.py
│   └── validate.py
└── references/
    └── format-spec.md
```

```yaml
---
name: my-processor
description: >
  Processes [input type] into [output type] using automated scripts.
  Use when converting [format A] to [format B], validating [target],
  or batch processing [items].
---

# My Processor

## Quick Start
python scripts/process.py input.ext output.ext

## Workflow
1. Validate input: `python scripts/validate.py input.ext`
2. Process: `python scripts/process.py input.ext output.ext`
3. Verify output

## Error Handling
[Common errors and fixes]
```

## 8. Template 4: Knowledge-Intensive Skill

Best for: expert domains requiring deep background knowledge.

```
my-expert-skill/
├── SKILL.md
├── scripts/
│   └── validate.py
└── references/
    ├── knowledge-base.md
    ├── checklist.md
    ├── patterns.md
    └── edge-cases.md
```

```yaml
---
name: my-expert-skill
description: >
  Expert-level [domain] analysis with structured evaluation.
  Use when reviewing [target] for [criteria], designing [artifact],
  or auditing [system] against [standards].
---

# My Expert Skill

## Decision Tree
- New [target] -> Design workflow
- Existing [target] -> Review workflow

## Workflow
1. Gather context
2. Apply domain knowledge (references/knowledge-base.md)
3. Evaluate against checklist (references/checklist.md)
4. Generate structured report

## Output Contract
[Scoring rubric + structured report template]

## References
| File | Purpose | When to read |
|------|---------|-------------|
| knowledge-base.md | Domain knowledge | During analysis |
| checklist.md | Evaluation criteria | During review |
| patterns.md | Common patterns | When designing |
| edge-cases.md | Edge cases | When troubleshooting |
```

## 9. Template 5: Plugin Skill

Best for: Claude Code plugins with multiple related skills.

```
my-plugin/
├── SKILL.md
├── scripts/
│   ├── init.py
│   └── validate.py
├── references/
│   └── api-docs.md
└── assets/
    └── templates/
```

## 10. Selection Guide

**Choose Minimal** when:
- Task is deterministic (input -> process -> output)
- No complex decisions needed
- User just needs "one-click execution"

**Choose Read-Only** when:
- Task produces analysis/review without modifying files
- Structured checklist drives the workflow

**Choose Script-Driven** when:
- Same code would be rewritten repeatedly
- Deterministic reliability is critical
- Processing can be automated

**Choose Knowledge-Intensive** when:
- Deep domain knowledge is required
- Judgment criteria come from industry best practices
- Large background knowledge base needed
- Expert-level output quality expected

**General rule**: Start with the simplest template that fits. Add complexity
only when needed. Over-engineering increases maintenance cost.
