---
name: specclaw
description: "Spec-driven development framework for OpenClaw. Propose features, generate specs, spawn coding agents, validate implementations."
metadata:
  openclaw:
    emoji: "🦞"
    requires:
      tools: ["exec", "sessions_spawn", "message"]
allowed-tools: ["exec", "read", "write", "edit", "sessions_spawn", "sessions_yield", "subagents", "message", "memory_search"]
---

# SpecClaw — Spec-Driven Development

## Overview

SpecClaw brings structured, spec-driven development to OpenClaw agents. It manages the full lifecycle: propose → plan → build → verify → archive.

## Directory Structure

When initialized (`.specclaw/` exists in project root):

```
.specclaw/
├── config.yaml          # Project configuration
├── STATUS.md            # Project dashboard (auto-generated)
├── patterns.md          # Recurring pattern registry (cross-change)
└── changes/
    ├── <change-name>/
    │   ├── proposal.md  # Problem + solution + scope
    │   ├── spec.md      # Requirements + acceptance criteria
    │   ├── design.md    # Technical approach + file map
    │   ├── tasks.md     # Ordered tasks with status markers
    │   ├── status.md    # Progress tracking
    │   ├── errors.md    # Build error journal (auto-generated on failures)
    │   └── learnings.md # Build learnings (spec gaps, patterns, insights)
    └── archive/         # Completed changes
```

## Commands

The user triggers commands conversationally. Recognize these patterns:

### `specclaw init`
**Trigger:** "specclaw init", "initialize specclaw", "set up spec-driven development"

1. Create `.specclaw/` directory structure
2. Generate `config.yaml` from template (see `templates/config.yaml`)
3. Ask user for project name/description
4. Create initial `STATUS.md`
5. Add `.specclaw/` tracking to git

### `specclaw propose "<idea>"`
**Trigger:** "specclaw propose", "propose a change", "new feature proposal"

1. Create `.specclaw/changes/<slugified-name>/`
2. Generate `proposal.md` from template
3. Include: problem statement, proposed solution, scope, impact, open questions
4. Present proposal to user for review
5. Update `STATUS.md`

### `specclaw plan <change>`
**Trigger:** "specclaw plan", "plan the feature", "generate spec for"

1. Read the proposal
2. Analyze existing codebase (file structure, patterns, dependencies)
3. Generate:
   - `spec.md` — functional requirements, acceptance criteria, edge cases
   - `design.md` — technical approach, architecture, file changes map
   - `tasks.md` — ordered implementation tasks with dependencies
4. Present plan summary to user
5. Update status

### `specclaw build <change>`
**Trigger:** "specclaw build", "implement the feature", "start building"

**This is where OpenClaw shines.** Follow this execution flow exactly:

#### Step 1 — Setup

Run the setup script to parse config, create a git branch, and get build configuration:

```bash
bash skill/scripts/build.sh setup .specclaw <change_name>
```

This returns JSON config including `parallel_tasks`, `models.coding`, `git.strategy`, and `notifications.channel`. Capture this output — you'll need `parallel_tasks` and `model` values throughout the build.

Send a **build started** notification:

```
🦞 **Build Started**
**Change:** <change_name>
**Branch:** specclaw/<change_name>
**Tasks:** <total_count> across <wave_count> waves
```

#### Step 2 — Parse Tasks

Get all actionable tasks:

```bash
bash skill/scripts/parse-tasks.sh --status pending .specclaw/changes/<change>/tasks.md
```

This outputs JSON: `[{"id": "T1", "title": "...", "wave": 1, "depends": [], "files": [...], "estimate": "small"}, ...]`

**For retries** (re-running build on a change with prior failures):

```bash
bash skill/scripts/parse-tasks.sh --status failed .specclaw/changes/<change>/tasks.md
```

Reset failed tasks to pending before re-executing:

```bash
bash skill/scripts/update-task-status.sh .specclaw/changes/<change>/tasks.md <TASK_ID> pending
```

Then re-parse with `--status pending` and continue from the appropriate wave.

#### Step 3 — Wave Loop

Execute tasks wave-by-wave. For each wave number (1, 2, 3...):

**a. Filter tasks for this wave:**

```bash
bash skill/scripts/parse-tasks.sh --wave N --status pending .specclaw/changes/<change>/tasks.md
```

If no tasks returned for this wave, the build is complete — skip to Step 4.

**Skip waves with blocked tasks:** If a task's dependency failed in a prior wave, skip it and mark it failed:

```bash
bash skill/scripts/update-task-status.sh .specclaw/changes/<change>/tasks.md <TASK_ID> failed
```

**b. For each task in the wave** (up to `parallel_tasks` from config):

1. **Mark in-progress:**
   ```bash
   bash skill/scripts/update-task-status.sh .specclaw/changes/<change>/tasks.md <TASK_ID> in_progress
   ```

2. **Build context payload:**
   ```bash
   bash skill/scripts/build-context.sh .specclaw <change> <TASK_ID>
   ```
   This outputs a complete context string containing: spec sections, design sections, task details, relevant source file contents, and constraints. Use this output directly as the agent's task.

3. **Spawn coding agent:**
   ```
   sessions_spawn(
     task: <output from build-context.sh>,
     label: "specclaw-<change>-<task_id>",
     mode: "run",
     model: <models.coding from config>
   )
   ```

**c. Yield and wait:**

After spawning all tasks in the wave batch, call `sessions_yield` to wait for agent completions. Results auto-announce back to you.

**d. Process completed agents:**

For each agent that **succeeded**:

1. Mark complete:
   ```bash
   bash skill/scripts/update-task-status.sh .specclaw/changes/<change>/tasks.md <TASK_ID> complete
   ```

   If this task previously failed (was `[!]` before): Run `bash skill/scripts/log-error.sh .specclaw <change> --resolve <task_id>`

2. Git commit the changes:
   ```bash
   bash skill/scripts/build.sh commit .specclaw <change> <TASK_ID> "<task_title>" <files...>
   ```

3. Send a **task complete** notification:
   ```
   ✅ **Task Complete:** <TASK_ID> — <task_title>
   **Change:** <change_name> | **Wave:** <N>/<total_waves>
   ```

**e. Process failed agents:**

For each agent that **failed**:

1. Mark failed:
   ```bash
   bash skill/scripts/update-task-status.sh .specclaw/changes/<change>/tasks.md <TASK_ID> failed
   ```

2. **Log error:** Run `bash skill/scripts/log-error.sh .specclaw <change> <task_id> <wave> <agent_label> "<failure summary>"` — pipe agent error output if available

3. Log the error in `status.md` with the failure reason

4. Send a **task failed** notification:
   ```
   ❌ **Task Failed:** <TASK_ID> — <task_title>
   **Change:** <change_name> | **Wave:** <N>/<total_waves>
   **Error:** <brief failure reason>
   ```

5. Mark all dependent tasks in later waves as **skipped/failed** — they cannot proceed

**f. Repeat** for the next wave number until no pending tasks remain.

#### Step 4 — Finalize

Run the finalize script to execute tests and merge the branch:

```bash
bash skill/scripts/build.sh finalize .specclaw <change_name>
```

This runs the configured `test_command` (if any) and merges the branch per `git.strategy`.

#### Step 5 — Post-Build Review

If `automation.post_build_review` is `true` in config, run an automated review before updating the dashboard:

**a. Scope deviation check:**

Compare files actually changed against files declared in tasks:

```bash
# Get files changed since pre-build commit (branch point)
git diff --name-only main...HEAD
```

Cross-reference with files listed in each task in `tasks.md`. Flag any files changed but not declared in any task's `Files:` field.

**b. Review prompt:**

Evaluate the build and auto-log findings (~150 words max):

```
🦞 Post-Build Review — <change-name>
Results: X/Y tasks passed, Z failed

Evaluate:
1. Were any spec requirements ambiguous or incomplete?
2. Did the design need adjustment during implementation?
3. Were any files modified outside declared task scope?
4. Did any agents struggle with context or instructions?
5. Any reusable patterns discovered?

For each finding, log with:
  bash skill/scripts/log-learning.sh .specclaw <change> <category> <priority> "<detail>" "<action>"
```

**c. Auto-log scope deviations:**

For any files changed outside declared task scope, automatically log as `design_gap`:

```bash
bash skill/scripts/log-learning.sh .specclaw <change> design_gap medium "File <path> modified but not declared in any task" "Review task file declarations for completeness"
```

**d. Pattern scan:** Run `bash skill/scripts/detect-patterns.sh .specclaw scan <change>` to check for recurring patterns across changes.

**e.** If any patterns have recurrence >= 3, alert the user: "⚠️ Pattern PAT-XXX has N occurrences — consider promoting its prevention rule to agent context."

#### Step 6 — Update Dashboard

Regenerate the project status dashboard:

```bash
bash skill/scripts/update-status.sh .specclaw
```

#### Step 7 — Notify

Send the **build summary** via the `message` tool to the configured notification channel:

```
🦞 **Build Complete**
**Change:** <change_name>
**Status:** <succeeded|partial|failed>
**Tasks:** <completed>/<total> complete, <failed> failed, <skipped> skipped
**Branch:** specclaw/<change_name> → merged to <target_branch>
**Duration:** <elapsed time>
```

If any tasks failed, include a remediation section:

```
⚠️ **Failed Tasks:**
- <TASK_ID>: <brief error> — re-run with `specclaw build <change>` to retry
```

#### Retry Flow

When `specclaw build` is called on a change that has failed tasks:

1. Parse failed tasks: `parse-tasks.sh --status failed`
2. Reset each to pending: `update-task-status.sh ... pending`
3. Re-parse pending tasks and determine which waves need re-execution
4. Execute only the waves containing reset tasks (and their dependents)
   - Retried tasks automatically get previous error context via `build-context.sh`
5. Finalize and notify as normal

#### Key Principles

- **Fresh context always** — each agent gets ONLY what it needs via `build-context.sh`. No stale context from prior tasks. This is critical for quality.
- **Parallel within waves** — tasks in the same wave with no cross-dependencies spawn simultaneously, up to `parallel_tasks` limit.
- **Sequential across waves** — wave N+1 starts only after wave N completes.
- **Fail-fast on dependencies** — if a task fails, all tasks depending on it are immediately marked failed.

### `specclaw learn <change> "<insight>"`
**Trigger:** "specclaw learn", "log a learning", "what did we learn", "capture insight"

Capture build learnings — spec gaps, design misses, and patterns discovered during implementation.

**Log a learning:**
```bash
bash skill/scripts/log-learning.sh .specclaw <change> <category> <priority> "<detail>" ["<action>"]
```

Categories: `spec_gap` | `design_gap` | `pattern` | `best_practice` | `agent_issue`
Priorities: `low` | `medium` | `high`

**List learnings for a change:**
```bash
bash skill/scripts/log-learning.sh .specclaw <change> --list
```

**Promote a learning** (mark for elevation to agent prompts/SKILL.md):
```bash
bash skill/scripts/log-learning.sh .specclaw <change> --promote <id>
```

**When to log:**
- After a build reveals a spec gap (requirements were unclear or missing)
- When a design decision needed mid-build adjustment
- When agents discovered a useful pattern worth reusing
- When parallel tasks created conflicts (duplicate code, shared dependencies)
- When an agent struggled with the context or instructions

Learnings are stored in `.specclaw/changes/<change>/learnings.md` and feed into the pattern detection system for cross-change analysis.

### `specclaw patterns`
**Trigger:** "specclaw patterns", "check patterns", "recurring issues", "what keeps happening"

Track recurring patterns across changes — errors and learnings that repeat become prevention rules.

**Scan a change for patterns:**
```bash
bash skill/scripts/detect-patterns.sh .specclaw scan <change>
```
Reads errors.md and learnings.md, matches against existing patterns, creates new or increments existing.

**List all patterns:**
```bash
bash skill/scripts/detect-patterns.sh .specclaw list [--min-recurrence N]
```

**Promote a pattern** (mark for elevation to agent prompts):
```bash
bash skill/scripts/detect-patterns.sh .specclaw promote <pat-id>
```

**Auto-promotion:** Patterns with 3+ occurrences are flagged ⚠️ — their prevention rules should be added to agent context templates or SKILL.md build instructions.

Pattern registry lives at `.specclaw/patterns.md` (global, not per-change).

### `specclaw verify <change>`
**Trigger:** "specclaw verify", "validate implementation", "check against spec"

1. Read `spec.md` acceptance criteria
2. Check each criterion against the implementation
3. Run tests if configured (`config.yaml test_command`)
4. Generate verification report
5. Update `status.md` with pass/fail per criterion
6. If failures: suggest remediation tasks

### `specclaw status`
**Trigger:** "specclaw status", "project status", "what's the progress"

1. Read all changes in `.specclaw/changes/`
2. Compile dashboard showing:
   - Active changes with progress %
   - Pending proposals
   - Recently archived
   - Overall project health
3. Update `STATUS.md`

### `specclaw archive <change>`
**Trigger:** "specclaw archive", "mark as done", "archive the change"

1. Verify change is complete (all tasks done, verification passed)
2. Move to `.specclaw/changes/archive/YYYY-MM-DD-<change-name>/`
3. Update `STATUS.md`
4. Optionally create git tag

### `specclaw auto`
**Trigger:** "specclaw auto", "autonomous mode", "auto-build"

1. Check `STATUS.md` for next actionable item
2. If proposal exists without plan → generate plan
3. If plan exists without implementation → build
4. If built without verification → verify
5. Respect `config.yaml` limits (max_tasks_per_run)
6. Notify user of results

## Task Format in tasks.md

```markdown
## Tasks

### Wave 1 (no dependencies)
- [ ] `T1` — Create theme context provider
  - Files: `src/contexts/ThemeContext.tsx`
  - Estimate: small
- [ ] `T2` — Add CSS custom properties
  - Files: `src/styles/variables.css`
  - Estimate: small

### Wave 2 (depends on Wave 1)
- [ ] `T3` — Create toggle component
  - Files: `src/components/ThemeToggle.tsx`
  - Depends: T1
  - Estimate: small

### Wave 3 (depends on Wave 2)
- [ ] `T4` — Integration tests
  - Files: `tests/theme.test.ts`
  - Depends: T1, T2, T3
  - Estimate: medium
```

Status markers:
- `[ ]` — pending
- `[~]` — in progress
- `[x]` — complete
- `[!]` — failed (needs remediation)

## Agent Context Preparation

Context construction is handled by the `build-context.sh` script:

```bash
bash skill/scripts/build-context.sh .specclaw <change> <TASK_ID>
```

The script automatically assembles a complete context payload containing:

1. **Task header** — task ID, title, and estimate
2. **Spec context** — relevant sections from `spec.md` (requirements, acceptance criteria)
3. **Design context** — relevant sections from `design.md` (architecture, approach)
4. **Task details** — full task description, file list, and dependencies from `tasks.md`
5. **Source files** — current contents of files listed in the task's `Files:` field
6. **Constraints** — standard rules (follow patterns, write tests, stay in scope)

The output is a single string ready to pass directly as the `task` parameter to `sessions_spawn`. Do not manually construct context — always use the script to ensure consistency and freshness.

## Configuration Reference

See `templates/config.yaml` for the full config schema.

Key settings:
- `models.planning` — model for proposals, specs, design (default: opus)
- `models.coding` — model for implementation (default: codex)
- `models.review` — model for verification (default: sonnet)
- `git.strategy` — "branch-per-change" or "direct"
- `notifications.channel` — where to send updates
- `automation.max_tasks_per_run` — limit for auto mode

## Best Practices

1. **Keep proposals focused** — one change per proposal, small scope
2. **Review specs before building** — garbage in, garbage out
3. **Wave-based execution** — group independent tasks, respect dependencies
4. **Fresh context always** — never let agents accumulate stale context
5. **Verify early** — run verification after each wave, not just at the end
