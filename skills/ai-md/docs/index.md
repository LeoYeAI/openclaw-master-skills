---
layout: default
title: AI.MD
description: Convert CLAUDE.md to AI-native structured-label format
---

# AI.MD

**Your CLAUDE.md is read by AI every turn — write it in AI's language.**

AI.MD converts human-written `CLAUDE.md` into structured-label format.
Same rules. Fewer tokens. Higher compliance.

---

## Before / After

| Metric | Before (prose) | After (AI-native) | Change |
|--------|---------------|-------------------|--------|
| File size | 13,474 bytes | 6,332 bytes | **-53%** |
| Line count | 224 lines | 142 lines | **-37%** |
| Codex compliance | 6/8 | **8/8** | ✅ |
| Gemini compliance | 6.5/8 | **7/8** | ✅ |

Tested 2026-03, real production CLAUDE.md, 4 LLM models.

---

## 10 Techniques

| # | Technique | Why it works |
|---|-----------|-------------|
| 1 | One concept per line | 5 rules on 1 line → AI follows ~3. Split → follows all 5 |
| 2 | trigger/action/exception labels | AI executes directly, zero inference needed |
| 3 | Semantic anchors | Labels act as hashtags — lookup, not full-text search |
| 4 | State-machine gates | Each rule = if → then → else → priority |
| 5 | XML section isolation | `<gates>` `<rules>` `<rhythm>` prevent rule-bleed |
| 6 | Strip "why", keep "what" | AI doesn't need your explanations |
| 7 | Bilingual labels | English for AI parsing, native language for output |
| 8 | Cross-references | Write once, reference as `(GATE-5)` — no duplicates |
| 9 | Not-triggered lists | Tell AI when NOT to fire — prevents over-triggering |
| 10 | Conflict detection | Pair-check all rules, add priority/yields-to |

---

## Install (30 seconds)

```bash
mkdir -p ~/.claude/skills/ai-md
curl -o ~/.claude/skills/ai-md/SKILL.md \
  https://raw.githubusercontent.com/sstklen/ai-md/main/SKILL.md
```

Then tell Claude Code:

> **"AI.MD"** or **"distill my CLAUDE.md"** or **"蒸餾"**

---

## How It Works

| Phase | What happens |
|-------|-------------|
| 1. Understand | Read like a compiler — find triggers, actions, constraints |
| 2. Decompose | Break every `|`, `()`, "and/but" into atomic rules |
| 3. Label | Assign `trigger:` `action:` `exception:` `banned:` etc. |
| 4. Structure | Organize into `<gates>` → `<rules>` → `<rhythm>` → `<conn>` |
| 5. Resolve | Detect hidden conflicts, add priority/yields-to |
| 6. Test | Validate with 2+ models, 8 questions, same criteria |

---

## Key Insight

> More rules in prose = worse compliance.
> Same rules in structure = better compliance.
> **Structure > Prose. Always.**

---

[GitHub](https://github.com/sstklen/ai-md) · [Examples](https://github.com/sstklen/ai-md/tree/main/examples) · [SKILL.md](https://github.com/sstklen/ai-md/blob/main/SKILL.md) · MIT License
