---
name: self-improving-agent-skill
version: 0.2.0
description: 基于对经验的持续学习，不断优化 Agent 能力。适用于完成重要任务后、出现错误时、会话结束时，或用户输入“自我进化”“总结经验”“从经验中学习”等指令时触发。
---

# Self-Improving Agent

> "An AI agent that learns from every interaction, accumulating patterns and insights to continuously improve its own capabilities." — Based on 2025 lifelong learning research

## Overview

This is a **universal self-improvement system** that learns from ALL task experiences. It implements a complete feedback loop:

- **Multi-Memory Architecture**: Semantic (patterns/rules) + Episodic (experiences) + Working (session context)
- **Self-Correction**: Detects and fixes guidance errors
- **Self-Validation**: Periodically verifies skill accuracy
- **Evolution Markers**: Traceable changes with source attribution
- **Confidence Tracking**: Measures pattern reliability over time
- **User Confirmation Gate**: All skill file modifications require explicit user approval before applying
- **Human-in-the-Loop**: Collects feedback to validate improvements

## Research-Based Design

| Research | Key Insight | Application |
|----------|-------------|-------------|
| [SimpleMem](https://arxiv.org/html/2601.02553v1) | Efficient lifelong memory | Pattern accumulation system |
| [Multi-Memory Survey](https://dl.acm.org/doi/10.1145/3748302) | Semantic + Episodic memory | World knowledge + experiences |
| [Lifelong Learning](https://arxiv.org/html/2501.07278v1) | Continuous task stream learning | Learn from every task |
| [Evo-Memory](https://shothota.medium.com/evo-memory-deepminds-new-benchmark) | Test-time lifelong learning | Real-time adaptation |

## The Self-Improvement Loop

```
┌──────────────────────────────────────────────────────────────┐
│                  UNIVERSAL SELF-IMPROVEMENT                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Task Event → Extract Experience → Abstract Pattern → Update │
│       │               │                 │              │     │
│       ▼               ▼                 ▼              ▼     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              MULTI-MEMORY SYSTEM                       │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ Semantic Memory  │ Episodic Memory  │ Working Memory   │  │
│  │ (Patterns/Rules) │ (Experiences)    │ (Current)        │  │
│  │ memory/self-improving/semantic/ │ memory/self-improving/episodic/ │ memory/self-improving/working/  │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │              FEEDBACK LOOP                             │  │
│  │ User Feedback → Confidence Update → Pattern Adapt      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

## When This Activates

### Automatic Triggers

| Event | Action |
|-------|--------|
| Any significant task completes | Extract patterns, propose skill updates (requires user confirmation) |
| An error or failure occurs | Capture error context, trigger self-correction (requires user confirmation before applying fixes) |
| Session ends | Consolidate working memory into long-term memory |

### Manual Triggers

- User says "自我进化", "self-improve", "从经验中学习"
- User says "分析今天的经验", "总结教训", "总结经验"
- User asks to improve a specific skill or workflow

## Memory Storage

### Workspace Discovery

Before accessing any memory files, the agent MUST first determine the workspace root path:

1. **Check environment** — Use the workspace path provided by the IDE/environment context
2. **Verify structure** — Confirm the workspace root by checking for project markers (e.g., `.git/`, `package.json`, `pom.xml`, etc.)
3. **All paths below are relative to the workspace root** — e.g., `{workspace}/memory/self-improving/`

### Relationship with Agent Memory

The Self-Improving Agent's memory lives **inside** the Agent's `memory/` directory as a dedicated subdirectory. This design ensures:

- **No confusion**: Agent's own memory (`MEMORY.md`, `memory/YYYY-MM-DD.md`) and Self-Improving Agent's memory (`memory/self-improving/`) are clearly separated by directory structure
- **Discoverability**: The Agent can browse `memory/` and naturally find self-improving insights
- **Supplement, not replace**: Self-Improving Agent can **append** high-confidence patterns to Agent's memory files (with user confirmation), enriching the Agent's knowledge

```
{workspace}/
├── MEMORY.md                          # Agent core memory (Self-Improving Agent can append)
├── memory/
│   ├── YYYY-MM-DD.md                  # Agent daily memory (Self-Improving Agent can append)
│   └── self-improving/                # Self-Improving Agent dedicated memory space
│       ├── semantic/
│       │   └── patterns.json          # Abstract patterns and rules
│       ├── episodic/
│       │   └── YYYY/
│       │       └── YYYY-MM-DD-{task}.json  # Specific experiences
│       ├── working/
│       │   ├── current_session.json   # Active session data
│       │   ├── last_error.json        # Error context for self-correction
│       │   └── session_end.json       # Session end marker for consolidation
│       └── index.json                 # Memory index and metrics
```

### Memory Interaction Rules

| Action | Target | Condition |
|--------|--------|-----------|
| Read | `MEMORY.md` | Always — to understand Agent's accumulated knowledge |
| Read | `memory/YYYY-MM-DD.md` | Always — to understand today's context |
| Append to | `MEMORY.md` | Only high-confidence patterns (>= 0.9), requires user confirmation |
| Append to | `memory/YYYY-MM-DD.md` | Session summary and key learnings, requires user confirmation |
| Full CRUD | `memory/self-improving/*` | Self-Improving Agent's own memory space, free to manage |

## Evolution Priority Matrix

Trigger evolution when new reusable knowledge appears:

| Trigger | Priority | Action |
|---------|----------|--------|
| New workflow pattern discovered | High | Add to relevant skill guidance |
| Architecture/design tradeoff clarified | High | Add to decision patterns |
| Debugging fix or anti-pattern found | High | Add to troubleshooting patterns |
| Security or performance insight | High | Add to best practice patterns |
| Code pattern or idiom learned | Medium | Add to coding patterns |
| Test strategy improvement | Medium | Update testing approach |
| Tool usage optimization | Medium | Update tool usage patterns |
| Documentation structure insight | Low | Update documentation templates |

## Multi-Memory Architecture

### 1. Semantic Memory (`memory/self-improving/semantic/patterns.json`)

Stores **abstract patterns and rules** reusable across contexts:

```json
{
  "patterns": {
    "pat-2025-01-11-001": {
      "id": "pat-2025-01-11-001",
      "name": "Pattern Name",
      "source": "user_feedback|implementation_review|retrospective",
      "confidence": 0.95,
      "applications": 5,
      "created": "2025-01-11",
      "last_applied": "2025-01-15",
      "category": "coding_patterns|architecture|debugging|workflow|...",
      "pattern": "One-line summary",
      "problem": "What problem does this solve?",
      "solution": "How to apply this pattern",
      "quality_rules": ["Rule 1", "Rule 2"],
      "target_skills": ["skill-name-1", "skill-name-2"]
    }
  }
}
```

### 2. Episodic Memory (`memory/self-improving/episodic/`)

Stores **specific experiences and what happened**:

```json
{
  "id": "ep-2025-01-11-001",
  "timestamp": "2025-01-11T10:30:00Z",
  "skill": "debugger|coding-assistant|reviewer|...",
  "task_type": "debugging|coding|review|design|...",
  "situation": "What the user was trying to do",
  "solution": "How the issue was resolved",
  "outcome": "success|partial|failure",
  "root_cause": "Underlying issue if applicable",
  "lesson": "Key takeaway from this experience",
  "related_pattern": "pattern_id if linked",
  "user_feedback": {
    "rating": 8,
    "comments": "User's feedback on the experience"
  }
}
```

### 3. Working Memory (`memory/self-improving/working/`)

Stores **current session context** — ephemeral data that gets consolidated at session end:

```json
{
  "session_id": "session-2025-01-11-001",
  "started": "2025-01-11T10:00:00Z",
  "tasks_completed": [],
  "errors_encountered": [],
  "patterns_applied": [],
  "pending_extractions": []
}
```

## Self-Improvement Process

### Phase 1: Experience Extraction

After any significant task completes, extract:

```yaml
What happened:
  task_type: {what kind of task}
  task: {what was being done}
  outcome: {success|partial|failure}

Key Insights:
  what_went_well: [what worked]
  what_went_wrong: [what didn't work]
  root_cause: {underlying issue if applicable}

User Feedback:
  rating: {1-10 if provided}
  comments: {specific feedback}
```

### Phase 2: Pattern Abstraction

Convert experiences to reusable patterns. The goal is to go from concrete to abstract — patterns should be general enough to apply across different tasks but specific enough to be actionable.

| Concrete Experience | Abstract Pattern |
|--------------------|------------------|
| "User forgot to save intermediate work" | "Always persist intermediate results to files" |
| "Code review missed SQL injection" | "Add security checklist to review process" |
| "Callback was empty, causing silent failure" | "Verify all callbacks have implementations" |
| "Ambiguous UI spec caused rework" | "UI specs need exact layout specifications" |

**Abstraction Rules:**

```yaml
If experience_repeats 3+ times:
  pattern_level: critical
  action: Add to "Critical Mistakes" or "Anti-Patterns" section

If solution_was_effective:
  pattern_level: best_practice
  action: Add to "Best Practices" section

If user_rating >= 7:
  pattern_level: strength
  action: Reinforce this approach in relevant skills

If user_rating <= 4:
  pattern_level: weakness
  action: Add to "What to Avoid" section
```

### Phase 3: Skill Updates

**IMPORTANT: User Confirmation Required** — Before writing any changes to skill files, you MUST:

1. **Present proposed changes** — Show the user a clear summary of what will be modified:
   - Which skill file(s) will be updated
   - What content will be added, modified, or removed
   - The rationale behind each change (source episode, pattern, confidence level)
2. **Wait for explicit approval** — Do NOT proceed until the user confirms. Acceptable confirmations include explicit affirmative responses (e.g., "确认", "好的", "proceed", "yes").
3. **Apply changes only after approval** — Once confirmed, apply the changes with evolution markers for traceability.

If the user rejects or requests modifications, adjust the proposed changes accordingly and re-present for confirmation.

**Proposed Change Summary Format:**

```markdown
## Proposed Skill Update

**Target**: `{skill-file-path}`
**Action**: {Add new pattern | Correct existing guidance | Update checklist}
**Source**: {episode_id or trigger}
**Confidence**: {X.XX}

### Changes Preview
{Show the exact content that will be added/modified, using diff-style or before/after format}

### Rationale
{Why this change is recommended}

---
Confirm this update? (yes/no/modify)
```

Once confirmed, update skill files with **evolution markers** for traceability:

```markdown
<!-- Evolution: 2025-01-12 | source: ep-2025-01-12-001 | task: debugging -->

## Pattern Added (2025-01-12)

**Pattern**: Always verify callbacks are not empty functions

**Source**: Episode ep-2025-01-12-001

**Confidence**: 0.95

### Updated Checklist
- [ ] Verify all callbacks have implementations
- [ ] Test callback execution paths
```

**Correction Markers** (when fixing wrong guidance):

```markdown
<!-- Correction: 2025-01-12 | was: "Use callback chain" | reason: caused stale state -->

## Corrected Guidance

Use direct state monitoring instead of callback chains for reactive updates.
```

Use the templates in `templates/` for consistent formatting. See `references/appendix.md` for the full template structures.

### Phase 4: Memory Consolidation

1. **Update semantic memory** — add or update patterns in `memory/self-improving/semantic/patterns.json`
2. **Store episodic memory** — write episode to `memory/self-improving/episodic/YYYY/YYYY-MM-DD-{task}.json`
3. **Update pattern confidence** — increase confidence for patterns that were successfully applied, decrease for those that led to errors
4. **Prune outdated patterns** — lower confidence for patterns with no recent applications; archive patterns below 0.3 confidence
5. **Supplement Agent memory** — propose additions to Agent's own memory files. **User confirmation is REQUIRED** before any write to `MEMORY.md` or `memory/YYYY-MM-DD.md`. Follow the same confirmation protocol as Phase 3:

   **What to propose:**
   - High-confidence patterns (>= 0.9) as concise entries → `MEMORY.md`
   - Today's session summary and key learnings → `memory/YYYY-MM-DD.md`

   **Confirmation format:**

   ```markdown
   ## Proposed Agent Memory Update

   ### → MEMORY.md (append)
   {Exact content to be appended, preview here}

   ### → memory/YYYY-MM-DD.md (append)
   {Exact content to be appended, preview here}

   **Source patterns**: {pattern IDs and confidence levels}

   ---
   Confirm this memory update? (yes/no/modify)
   ```

   **After approval:**
   - Append confirmed content with `<!-- Source: self-improving-agent | date: YYYY-MM-DD -->` markers for traceability
   - Do NOT overwrite existing content — always append at the end

## Self-Correction

Triggered when:
- A command or operation returns an error
- Tests fail after following skill guidance
- User reports the guidance produced incorrect results

**Process:**

1. **Detect Error**
   - Capture error context into `memory/self-improving/working/last_error.json`
   - Identify which guidance was followed

2. **Verify Root Cause**
   - Was the guidance incorrect?
   - Was the guidance misinterpreted?
   - Was the guidance incomplete?

3. **Propose Correction**
   - Draft the corrected guidance with correction markers
   - Present proposed changes to user for review (follow Phase 3 confirmation format)
   - **Wait for user confirmation before applying any changes**

4. **Apply Correction** (after user approval)
   - Update relevant skill/document with corrected guidance
   - Add correction marker with reason
   - Update related patterns in semantic memory

5. **Validate Fix**
   - Test the corrected guidance if possible
   - Ask user to verify the fix

## Self-Validation

Periodically (or when triggered manually), verify that stored patterns and skill guidance are still accurate:

1. Check that examples still work
2. Verify checklists match current conventions
3. Confirm external references are still valid
4. Detect duplicated or conflicting guidance

Use the validation template in `templates/validation-template.md` for structured reviews.

## Human-in-the-Loop Feedback

After each self-improvement cycle, present a summary to the user:

```markdown
## Self-Improvement Summary

I've learned from our session and updated:

### Patterns Extracted
1. **pattern_name**: Description (confidence: X.XX)

### Skills/Documents Updated
- `skill-name`: What was updated

### Confidence Levels
- New patterns: ~0.85 (needs more validation)
- Reinforced patterns: ~0.95 (well-established)

### Your Feedback
- Were these updates helpful?
- Should I apply any pattern more broadly?
- Any corrections needed?
```

Integrate feedback into confidence scoring:

| Feedback | Action |
|----------|--------|
| Positive (rating >= 7) | Increase confidence, consider expanding to related skills |
| Neutral (rating 4-6) | Keep pattern, gather more data before expanding |
| Negative (rating <= 3) | Decrease confidence, revise or archive pattern |

## Best Practices

### DO

- Learn from EVERY significant task interaction
- Extract patterns at the right abstraction level — general enough to reuse, specific enough to be actionable
- **Always present proposed changes to the user and wait for explicit confirmation** before writing to skill files OR Agent memory (`MEMORY.md`, `memory/YYYY-MM-DD.md`)
- Update multiple related skills when a pattern applies broadly
- Track confidence and application counts for all patterns
- Ask for user feedback on improvements
- Use evolution/correction markers for full traceability
- Validate guidance before applying broadly
- Read `MEMORY.md` and today's `memory/YYYY-MM-DD.md` at the start of each self-improvement cycle for context

### DON'T

- **NEVER modify skill files or Agent memory files without user confirmation** — this is a hard rule with no exceptions
- **NEVER overwrite** Agent memory content — always append at the end
- Over-generalize from a single experience — wait for 2-3 occurrences before creating a pattern
- Update skills without confidence tracking
- Ignore negative feedback — it's the most valuable signal
- Make changes that break existing, working functionality
- Create contradictory patterns — resolve conflicts explicitly
- Apply untested patterns at high confidence

## Quick Start

After any significant task completes, this agent:

1. **Analyzes** what happened during the task
2. **Extracts** reusable patterns and insights
3. **Proposes** skill updates and presents them to the user for review
4. **Waits** for explicit user confirmation before applying any skill modifications
5. **Updates** approved changes to skill files with evolution markers
6. **Logs** to memory (semantic + episodic) for future reference
7. **Reports** summary to user and collects feedback

## References

For detailed memory structures, validation templates, metrics, and workflow diagrams, read `references/appendix.md`.

For pattern/correction/validation templates, see the `templates/` directory:
- `templates/pattern-template.md` — Adding new patterns
- `templates/correction-template.md` — Fixing incorrect guidance
- `templates/validation-template.md` — Validating skill accuracy

### Research Papers

- [SimpleMem: Efficient Lifelong Memory for LLM Agents](https://arxiv.org/html/2601.02553v1)
- [A Survey on the Memory Mechanism of Large Language Model Agents](https://dl.acm.org/doi/10.1145/3748302)
- [Lifelong Learning of LLM based Agents](https://arxiv.org/html/2501.07278v1)
- [Evo-Memory: DeepMind's Benchmark](https://shothota.medium.com/evo-memory-deepminds-new-benchmark)

