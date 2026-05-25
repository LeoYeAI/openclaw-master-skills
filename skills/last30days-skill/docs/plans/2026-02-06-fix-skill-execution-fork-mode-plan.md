---
title: "fix: Skill execution broken - fork mode subagent ignores bash and text instructions"
type: fix
date: 2026-02-06
---

# fix: Skill Execution Broken in Fork Mode

## Overview

The last30days v2 skill stopped running its Python script and stopped showing acknowledgment text. The agent jumps straight to WebSearch, ignoring all instructions to run bash first or output text. Five attempted fixes all failed.

## Root Cause (Confirmed via Research)

**The old v1 skill worked by accident.** GitHub Issue #17283 documented that `context: fork` and `agent: Explore` were **silently ignored** in older Claude Code versions. The skill ran **inline** in the main conversation — not in a forked subagent. That's why:
- The user saw acknowledgment text (output inline to conversation)
- The bash script ran (main model followed instructions inline)
- Progress was visible (tool calls shown normally)

**Claude Code 2.1+ fixed the bug** and now properly honors `context: fork`. The skill now truly runs in an isolated subagent where:
- The model decides tool ordering independently
- Text output instructions are deprioritized vs tool calls
- "RUN THIS FIRST" instructions are **suggestions**, not commands
- There is **no mechanism** to force tool ordering in a forked subagent

**This is why every SKILL.md rewrite failed** — the problem isn't the instructions, it's `context: fork` itself.

## Evidence

| Attempt | What we tried | Result |
|---------|--------------|--------|
| 1 | "YOUR FIRST ACTION: Run this command. EXECUTE." | Agent ran script sometimes, never showed ack text |
| 2 | "YOUR FIRST OUTPUT — before ANY tool calls" + progress block | Agent ignored text, jumped to WebSearch |
| 3 | Moved progress block to very first section | Agent ignored it entirely |
| 4 | "DO NOT skip this. DO NOT jump to tool calls first." | Agent still jumped to WebSearch |
| 5 | Embedded echo in bash block + "Do NOT start with WebSearch" | Agent still jumped to WebSearch, never ran bash |

## Proposed Fix

### Option A: Remove `context: fork` (Recommended)

**Remove `context: fork` from frontmatter.** The skill runs inline in the main conversation, exactly like the old v1 skill accidentally did.

**Why this works:**
- Inline execution follows instructions sequentially
- Text output appears directly to the user
- Bash commands run when instructed
- This is how the "working" v1 skill actually operated

**File:** `SKILL.md` frontmatter

**Change from:**
```yaml
---
name: last30days
description: Research a topic from the last 30 days on Reddit + X + Web...
argument-hint: '"[topic] for [tool]" or "[topic]"'
context: fork
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch
---
```

**Change to:**
```yaml
---
name: last30days
description: Research a topic from the last 30 days on Reddit + X + Web...
argument-hint: '"[topic] for [tool]" or "[topic]"'
allowed-tools: Bash, Read, Write, AskUserQuestion, WebSearch
---
```

That's it. Remove the one line.

**Then restore the old v1 instruction flow:**
1. "Parse User Intent" section FIRST (generates acknowledgment text)
2. "Research Execution" with bash command
3. "Do WebSearch" while script runs
4. Synthesize and present

### Option B: Keep `context: fork` + Use `!`command`` Preprocessing

Use shell preprocessing syntax (`!`command``) to run the script **before** the model even sees the prompt:

```markdown
## Research data (auto-fetched)
!`python3 ~/.claude/skills/last30days/scripts/last30days.py "$ARGUMENTS" --emit=compact 2>&1`
```

**Risk:** Not confirmed that `$ARGUMENTS` works in `!`command`` context. More complex. The user still won't see progress text during preprocessing.

### Recommendation: Option A

Remove `context: fork`. It's one line. The old skill worked inline. The v2 skill should too. Option B is a backup if inline mode causes context window issues.

## Implementation

### Step 1: Remove `context: fork` from frontmatter

Single line removal in `SKILL.md`.

### Step 2: Restore v1-style instruction flow

The SKILL.md opening should match the public v1 pattern:

```markdown
# last30days: Research Any Topic from the Last 30 Days

Research ANY topic across Reddit, X, and the web. Surface what people are actually discussing, recommending, and debating right now.

## CRITICAL: Parse User Intent

Before doing anything, parse the user's input for:
[... topic/tool/query type parsing ...]

Store these variables:
- TOPIC = ...
- TARGET_TOOL = ...
- QUERY_TYPE = ...

---

## Research Execution

**Step 1: Run the research script**
```bash
python3 ~/.claude/skills/last30days/scripts/last30days.py "$ARGUMENTS" --emit=compact 2>&1
```

**Step 2: Do WebSearch** (while script runs)
[... websearch queries based on QUERY_TYPE ...]

**Step 3: Wait for script to complete**
[... synthesis instructions ...]
```

The key structural elements from v1 that need to return:
1. Descriptive intro paragraph
2. "Parse User Intent" BEFORE any tool calls
3. Script execution as a clearly labeled step
4. WebSearch as step 2 (not step 1)

### Step 3: Keep all v2 improvements

The v2-specific improvements (citation rules, stats template, Reddit fallback, scoring changes) stay. Only the frontmatter and instruction flow change.

### Step 4: Sync and test

Copy to `~/.claude/skills/last30days/SKILL.md`, test in new session.

## Acceptance Criteria

- [ ] `context: fork` removed from SKILL.md frontmatter
- [ ] Agent outputs acknowledgment text before running tools
- [ ] Python script actually executes (Reddit + X results appear)
- [ ] WebSearch supplements, doesn't replace, script results
- [ ] Stats emoji tree format renders correctly
- [ ] Citations are sparse (1 per insight, not 3-5)

## Test Plan

Run in a NEW Claude Code session:
1. `/last30days kanye west` — should see ack text, script runs, Reddit results
2. `/last30days open claw` — should see ack text, X results via Bird

## Files to Modify

| File | Change |
|------|--------|
| `SKILL.md` | Remove `context: fork`, restore v1 instruction flow |

## References

- GitHub Issue #17283: `context: fork` was silently ignored (the bug that made v1 work)
- Claude Code Skills docs: `!`command`` preprocessing syntax
- Claude Code Subagents docs: `agent: Explore` uses Haiku, read-only tools
- Public v1 SKILL.md: `github.com/mvanhorn/last30days-skill`
