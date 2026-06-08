# AI.MD

**Your CLAUDE.md is read by AI every single turn, not by you — so write it in AI's language.**

AI.MD converts human-written `CLAUDE.md` into AI-native structured-label format.
Not "compressed" — **restructured** so LLMs actually follow your rules better.

## The Problem

```
You type "hi" → AI reads your CLAUDE.md → responds
50 turns later → AI has re-read it 50 times
```

Claude Code re-reads `CLAUDE.md` on **every conversation turn**. Most CLAUDE.md files are written in human prose — paragraphs, parenthetical explanations, long sentences with multiple rules crammed together.

This wastes tokens AND reduces compliance. We proved it.

## Battle-Tested Results

Tested 2026-03 with real CLAUDE.md (washinmura.jp), 5 rounds, 4 models:

| Format | Codex (GPT-5.3) | Gemini 2.5 Pro | Claude Opus 4.6 |
|--------|-----------------|----------------|-----------------|
| Human prose (many rules) | 6/8 | 6.5/8 | 8/8 |
| AI-native structured | **8/8** | **7/8** | **8/8** |

**Same rules. Different format. Higher compliance across all models.**

The uncomfortable finding: Adding more rules in prose **decreased** compliance (8/8 → 6/8).
Converting to structured format **restored and exceeded** it (6/8 → 8/8).

### Size Reduction

Same real-world CLAUDE.md, before and after conversion:

| Metric | Before (prose) | After (AI-native) | Change |
|--------|---------------|-------------------|--------|
| File size | 13,474 bytes | 6,332 bytes | **-53%** |
| Line count | 224 lines | 142 lines | **-37%** |

Claude Code officially recommends keeping CLAUDE.md **under 200 lines** (re-read every turn).
The original was **over the limit** (224). After AI.MD conversion: **well within** (142).

Less tokens burned per turn × every turn × every session = compounding savings.

## What Makes It Work

Three mechanisms explain why structured-label format outperforms prose:

### 1. One Concept Per Line = Focused Attention

LLMs don't "read" — they **attend**. When rules share a line, attention splits.
When each rule has its own line, each gets full attention weight.

```
# BAD: 5 rules, 1 line — AI follows ~3
EVIDENCE: no-fabricate no-guess | banned:應該是 | Read/Grep→行號 | "好像"→self-test | guess=shame-wall

# GOOD: 5 rules, 5 lines — AI follows all 5
EVIDENCE:
  core: no-fabricate | no-guess | unsure=say-so
  banned: 應該是/可能是 → 先拿數據
  proof: all-claims-need(data/line#/source)
  hear-doubt: "好像"/"覺得" → self-test → 禁反問user
  violation: guess → shame-wall
```

### 2. Explicit Labels = Zero Inference

Labels declare meaning. Prose requires the model to infer it.

```
# BAD: AI must infer what (防搞混) means
GATE-1: 收到任務→先用一句話複述(防搞混)

# GOOD: Labels tell AI exactly what each part does
GATE-1 複述:
  trigger: new-task
  action: first-sentence="你要我做的是___"
  exception: signal=處理一下 → skip
```

### 3. Semantic Anchoring = Direct Matching

Labels act as matchable tags. When user says "add an API", the model matches it to `new-api:` directly — like a hash lookup instead of full-text search.

```
MOAT:
  new-api: must check health-check.py coverage (GATE-5)
```

This specific technique fixed a test case that failed 5 consecutive times across all models.

## Install

```bash
mkdir -p ~/.claude/skills/ai-md
curl -o ~/.claude/skills/ai-md/SKILL.md \
  https://raw.githubusercontent.com/sstklen/ai-md/main/SKILL.md
```

## Usage

In Claude Code, say any of:
- `AI.MD` or `distill my CLAUDE.md`
- `rewrite my MD for AI`
- `蒸餾`

The skill runs in two stages:
1. **Preview** — measures your current token burn, shows before/after examples
2. **Distill** — converts with backup, tests with multiple models, reports scores

## The Conversion Process

The full methodology is in [`SKILL.md`](SKILL.md), but here's the summary:

| Phase | What Happens |
|-------|-------------|
| **1. Understand** | Read like a compiler — identify triggers, actions, constraints, metadata, and deletable human explanations |
| **2. Decompose** | Break every `\|` separator, `()` parenthetical, and "and/but" conjunction into atomic rules |
| **3. Label** | Assign function labels: `trigger:` `action:` `exception:` `banned:` `policy:` etc. |
| **4. Structure** | Organize into hierarchy: `<gates>` → `<rules>` → `<rhythm>` → `<conn>` → `<ref>` |
| **5. Resolve** | Detect and resolve hidden conflicts between rules (priority, yields-to, not-triggered) |
| **6. Test** | Validate with 2+ LLM models, 8 test questions, same pass/fail criteria |

## Special Techniques

| Technique | What It Does |
|-----------|-------------|
| **Bilingual labels** | English labels (shorter, universal) + native language output strings |
| **State machine gates** | Each gate has trigger → action → exception → priority. Clear execution model. |
| **XML section tags** | `<gates>` `<rules>` `<rhythm>` create hard boundaries, prevent rule-bleed |
| **Cross-reference** | Single source of truth + `(GATE-5)` references instead of duplicates |
| **"What Not Why"** | Delete all explanations of WHY a rule exists. AI needs WHAT, not WHY. |
| **Not-triggered lists** | Explicit examples of when a rule should NOT fire. Prevents over-triggering. |
| **Conflict detection** | Check every pair of gates for hidden conflicts. Add priority/yields-to. |

## Template

```xml
# PROJECT-NAME | lang:xx | for-AI-parsing

<user>
identity, tone, signals, decision-style
</user>

<gates label="priority: gates>rules>rhythm">
GATE-1 name:
  trigger: ...
  action: ...
  exception: ...
</gates>

<rules>
RULE-NAME:
  core: ...
  banned: ...
  violation: ...
</rules>

<rhythm>
workflow patterns as key: value
</rhythm>

<conn>
connection strings (never compress facts)
</conn>
```

## Examples

See [`examples/before.md`](examples/before.md) and [`examples/after.md`](examples/after.md) for a real conversion.

## Key Insight

> **More rules in prose = worse compliance.**
> **Same rules in structure = better compliance.**
>
> Your beautifully written CLAUDE.md might be hurting your AI's performance.
> Structure > Prose. Always.

## License

MIT
