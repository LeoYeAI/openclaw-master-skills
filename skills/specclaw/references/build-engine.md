# Build Engine — Architecture & Reference

This document describes the SpecClaw build pipeline internals for developers maintaining the system. For agent instructions, see SKILL.md.

---

## Build Command Flow

When the agent runs `specclaw build <change>`, the pipeline executes:

```
1. build.sh setup .specclaw <change>              → config JSON (branch created if needed)
2. parse-tasks.sh --status pending tasks.md        → JSON task array
3. For each wave (sequential):
   a. parse-tasks.sh --wave N --status pending     → tasks in this wave
   b. For each task (parallel up to parallel_tasks limit):
      - build-context.sh .specclaw <change> <task_id>  → context payload (stdout)
      - update-task-status.sh tasks.md T1 in_progress
      - sessions_spawn with context payload
      - On completion:
        - update-task-status.sh tasks.md T1 complete|failed
        - build.sh commit .specclaw <change> T1 "title" files...
4. build.sh finalize .specclaw <change>            → summary JSON (tests, lint, merge)
5. update-status.sh .specclaw                      → regenerate STATUS.md dashboard
```

---

## Script APIs

All scripts live in `skill/scripts/` and require only bash, coreutils, and git. `jq` is optional (grep fallbacks exist).

### `build.sh` — Setup, Commit, Finalize

```
build.sh <subcommand> [args]
```

| Subcommand | Arguments | Description |
|---|---|---|
| `setup` | `<specclaw_dir> <change_name>` | Parse config.yaml, create/switch git branch (if branch-per-change), output config JSON |
| `commit` | `<specclaw_dir> <change_name> <task_id> "<title>" [files...]` | Stage listed files and commit with specclaw prefix. No-ops if nothing to commit |
| `finalize` | `<specclaw_dir> <change_name>` | Run test/lint/build commands, merge branch if branch-per-change, output summary JSON |

**`setup` reads from config.yaml:**
- `project.name`, `git.strategy`, `git.branch_prefix`, `git.auto_commit`, `git.commit_prefix`
- `build.test_command`, `build.lint_command`, `build.build_command`
- `build.parallel_tasks`, `build.timeout_seconds`, `models.coding`

**`commit` behavior:**
- Stages specified files with `git add`
- Skips commit if `git diff --cached` is clean (warns, exits 0)
- Skips commit if `auto_commit: false` (stages only)
- Commit message format: `<commit_prefix>(<change>): <task_id> — <title>`

**`finalize` behavior:**
- Runs test/lint/build commands (all optional, each reported independently)
- For `branch-per-change`: checks out main/master, runs `git merge --no-ff`
- On merge conflict: aborts merge, returns to feature branch, reports error
- Cleans up feature branch on successful merge

### `parse-tasks.sh` — Task Parser

```
parse-tasks.sh [OPTIONS] <tasks.md>
```

| Flag | Description |
|---|---|
| `--wave N` | Only output tasks from wave N |
| `--status STATUS` | Filter by status: `pending`, `in_progress`, `complete`, `failed` |
| `--validate` | Check JSON validity only (exit 0/1, no output). Requires `jq` |
| `-h, --help` | Show usage |

**Output:** JSON array to stdout. Each task object:

```json
{
  "id": "T1",
  "title": "Create parser module",
  "status": "pending",
  "wave": 1,
  "files": "src/parser.ts, src/parser.test.ts",
  "depends": "",
  "estimate": "~30 min"
}
```

**Parsing rules:**
- Waves detected by `### Wave N` headers (auto-incremented)
- Task lines must match `- [x] \`T<N>\` — Title` format
- Status markers: `[ ]` pending, `[~]` in_progress, `[x]` complete, `[!]` failed
- Sub-fields (`Files:`, `Depends:`, `Estimate:`, `Notes:`) parsed from indented lines
- Malformed tasks (no backtick ID) are skipped with a stderr warning
- Validates output with `jq` if available; errors on invalid JSON

### `build-context.sh` — Context Payload Builder

```
build-context.sh <specclaw_dir> <change_name> <task_id>
```

**Reads:**
- `.specclaw/config.yaml` — project name, commit prefix
- `.specclaw/changes/<change>/spec.md` — full specification
- `.specclaw/changes/<change>/design.md` — full design document
- `.specclaw/changes/<change>/tasks.md` — parsed via `parse-tasks.sh` internally
- Existing file contents for all files listed in the task

**Outputs to stdout:** A complete coding agent prompt containing:
1. Task title and notes
2. File list to modify
3. Full spec and design context
4. Current contents of each listed file (truncated at **500 lines** per file)
5. Constraints (file scope, code style, test requirements)
6. Commit message format

**File handling:**
- Files that don't exist yet are marked `*New file — to be created*`
- Files exceeding 500 lines show first 500 with a truncation notice
- File paths are resolved relative to the project root (parent of `.specclaw`)

**Fallback behavior:**
- Missing `jq`: uses grep-based JSON field extraction (with stderr warning)
- Missing `spec.md` or `design.md`: inserts placeholder text (with stderr warning)

### `update-task-status.sh` — Status Updater

```
update-task-status.sh [OPTIONS] <tasks.md> <task_id> <new_status>
update-task-status.sh [OPTIONS] <tasks.md> --batch T1:complete T2:failed ...
```

| Flag | Description |
|---|---|
| `--batch` | Accept multiple `TASK_ID:STATUS` pairs |
| `--quiet` | Suppress stdout (errors still go to stderr) |
| `--log` | Append transitions to a `## Status Log` section in tasks.md |
| `-h, --help` | Show usage |

**Valid statuses:** `pending`, `in_progress`, `complete`, `failed`

**Marker mapping:**
| Status | Marker |
|---|---|
| `pending` | `[ ]` |
| `in_progress` | `[~]` |
| `complete` | `[x]` |
| `failed` | `[!]` |

**Behavior:**
- Updates markers in-place via `sed -i`
- Detects previous status for transition logging
- Outputs `OK: T1: pending → in_progress` (unless `--quiet`)
- Always writes `[timestamp] T1: old → new` to stderr
- With `--log`: creates `## Status Log` section if missing, appends timestamped transitions
- Exits 1 if any task ID not found or status invalid (partial batch may have succeeded)

### `update-status.sh` — Dashboard Generator

```
update-status.sh <specclaw_dir>
```

**Reads:**
- `.specclaw/config.yaml` — project name
- `.specclaw/changes/*/tasks.md` — task counts per change
- `.specclaw/changes/archive/*/` — completed changes

**Writes:** `.specclaw/STATUS.md` with:
- Active changes with progress (`done/total tasks (pct%)`) and failure counts
- Pending proposals (directories with `proposal.md` but no `tasks.md`)
- Archived/completed changes
- Summary stats (total, active, completed)

**Status emojis:** 🔨 active, ⚠️ has failures, ✅ all complete, 📋 proposal only

---

## JSON Schemas

### `build.sh setup` Output

```json
{
  "project_name": "my-project",
  "git_strategy": "branch-per-change",
  "branch_prefix": "specclaw/",
  "branch_name": "specclaw/my-feature",
  "branch_existed": false,
  "auto_commit": true,
  "commit_prefix": "specclaw",
  "test_command": "npm test",
  "lint_command": "npm run lint",
  "build_command": "npm run build",
  "parallel_tasks": 3,
  "timeout_seconds": 300,
  "coding_model": "anthropic/claude-sonnet-4-20250514"
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `project_name` | string | — | From `config.yaml` |
| `git_strategy` | string | `"branch-per-change"` | `branch-per-change` or `direct` |
| `branch_prefix` | string | `"specclaw/"` | Prefix for feature branches |
| `branch_name` | string | — | Full branch name (prefix + change) |
| `branch_existed` | bool | `false` | `true` if resuming an existing branch |
| `auto_commit` | bool | `true` | Whether `commit` subcommand actually commits |
| `commit_prefix` | string | `"specclaw"` | Used in commit message format |
| `test_command` | string | `""` | Empty = skip tests |
| `lint_command` | string | `""` | Empty = skip lint |
| `build_command` | string | `""` | Empty = skip build |
| `parallel_tasks` | int | `3` | Max concurrent agents per wave |
| `timeout_seconds` | int | `300` | Agent timeout |
| `coding_model` | string | `""` | Model for coding agents |

### `parse-tasks.sh` Output

```json
[
  {"id":"T1","title":"Create parser module","status":"pending","wave":1,"files":"src/parser.ts","depends":"","estimate":"~30 min"},
  {"id":"T2","title":"Add validation","status":"complete","wave":1,"files":"src/validate.ts","depends":"","estimate":"~20 min"},
  {"id":"T3","title":"Integration tests","status":"failed","wave":2,"files":"tests/integration.ts","depends":"T1, T2","estimate":"~45 min"}
]
```

### `build.sh finalize` Output

```json
{
  "tests_passed": true,
  "lint_passed": true,
  "build_passed": true,
  "merged": true,
  "errors": []
}
```

| Field | Type | Description |
|---|---|---|
| `tests_passed` | bool | `false` if test command exited non-zero |
| `lint_passed` | bool | `false` if lint command exited non-zero |
| `build_passed` | bool | `false` if build command exited non-zero |
| `merged` | bool | `true` if branch was merged to main (branch-per-change only) |
| `errors` | string[] | Human-readable error descriptions |

**Possible error strings:**
- `"Test command failed: <cmd>"`
- `"Lint command failed: <cmd>"`
- `"Build command failed: <cmd>"`
- `"Merge conflict merging <branch> into <main> — manual resolution required"`
- `"Failed to checkout <main> for merge"`
- `"Not on expected feature branch; skipping merge"`

---

## Parallel Execution Strategy

### Wave-Based Parallelism

Tasks are grouped into waves. Within a wave, tasks are independent and can run in parallel. Waves execute sequentially — all tasks in wave N must complete before wave N+1 starts.

```
Wave 1: [T1, T2, T3]  ← spawn all 3 simultaneously
         ↓ wait all
Wave 2: [T4, T5]       ← spawn both (they depend on wave 1)
         ↓ wait all
Wave 3: [T6]           ← final integration/testing task
```

### Concurrency Control & Batching

The `parallel_tasks` config value (default: 3) limits concurrent agents. If a wave has more tasks than the limit, they are batched:

```
Wave 1 has 5 tasks, parallel_tasks = 3:
  Batch A: [T1, T2, T3] → sessions_spawn all 3 → sessions_yield → wait
  Batch B: [T4, T5]     → sessions_spawn both  → sessions_yield → wait
  → Wave 2...
```

The agent reads `parallel_tasks` from the setup JSON and chunks tasks accordingly.

### Conflict Prevention

- Each task declares its files explicitly in tasks.md
- Tasks in the same wave MUST NOT touch the same files
- File overlap within a wave indicates a planning error (should be caught during `specclaw plan`)
- The build engine does not validate this at runtime — it's enforced at planning time

---

## Fresh Context Principle

Each coding agent gets ONLY:
1. The specific task it's working on
2. The full spec and design documents
3. Current content of files it needs to modify (capped at 500 lines each)
4. Constraints and commit format

NO accumulated context from previous tasks. This prevents:
- Context window pollution across tasks
- Conflicting instructions from earlier tasks
- Agents "remembering" wrong approaches

The `build-context.sh` script enforces this by building each payload independently from source files on disk.

---

## Error Handling

### Task Failure

When a coding agent fails or times out:

1. `update-task-status.sh` marks the task as `[!] failed`
2. The error is logged (use `--log` flag for persistent log in tasks.md)
3. Dependent tasks (in later waves) are skipped
4. Independent tasks in the same wave continue unaffected
5. After all possible tasks complete, failures are reported to the user

### Recovery & Resume

The build engine supports resumption natively:

```bash
# Re-run build — automatically picks up pending and failed tasks
specclaw build <change>
# Complete tasks ([x]) are skipped. In-progress ([~]) and failed ([!]) are retried.

# build.sh setup detects existing branch:
# "Branch 'specclaw/my-feature' already exists — resuming"
# branch_existed: true in setup JSON
```

### Batch Status Updates

For efficiency when multiple tasks complete simultaneously:

```bash
update-task-status.sh --batch --log tasks.md T1:complete T2:failed T3:complete
```

---

## Git Integration

### branch-per-change Strategy (default)

```
build.sh setup   → git checkout -b specclaw/<change>  (or switch if exists)
build.sh commit  → git add <files> && git commit -m "specclaw(<change>): T1 — title"
  ... repeat per task ...
build.sh finalize → git checkout main && git merge --no-ff specclaw/<change>
                  → git branch -d specclaw/<change>  (cleanup on success)
```

On merge conflict, `finalize` runs `git merge --abort`, switches back to the feature branch, and reports the error in the summary JSON. Manual resolution is required.

### direct Strategy

```
build.sh setup   → no branch operations
build.sh commit  → git add <files> && git commit (on current branch)
build.sh finalize → run checks only, no merge step
```

---

## Notification Payloads

### Build Started
```
🦞 **SpecClaw Build Started**
**Change:** <change-name>
**Tasks:** <count> across <waves> waves
**Model:** <coding model>
```

### Task Complete
```
✅ `<task-id>` — <task-title> (wave <n>)
```

### Task Failed
```
❌ `<task-id>` — <task-title>
Error: <error summary>
```

### Build Complete
```
🦞 **SpecClaw Build Complete**
**Change:** <change-name>
**Result:** <passed>/<total> tasks | <failed> failed
**Duration:** <time>
**Next:** Run `specclaw verify <change>` to validate
```

---

## Troubleshooting

### Build hangs

**Symptom:** Build seems stuck, no progress.

**Check:**
1. Look for `[~]` (in_progress) tasks in `tasks.md` — these are the active ones
2. Check if the spawned agent sessions are still running
3. Verify `timeout_seconds` in config.yaml (default: 300s / 5 min)

**Fix:** Kill stuck agent sessions, then re-run `specclaw build <change>`. In-progress tasks will be retried.

### JSON parse errors

**Symptom:** `parse-tasks.sh` outputs invalid JSON or the build engine can't read task data.

**Check:**
```bash
parse-tasks.sh --validate tasks.md
# Exit 0 = valid, Exit 1 = invalid
```

**Common causes:**
- Missing backtick-wrapped task IDs (e.g. `T1` not `` `T1` ``)
- Malformed wave headers (must be `### Wave N`)
- Broken indentation on `- Files:` / `- Depends:` sub-fields
- Non-UTF8 characters in task titles

### Merge conflicts

**Symptom:** `build.sh finalize` reports merge conflict error.

**What happens:** The script runs `git merge --abort` automatically and switches back to the feature branch. No data is lost.

**Fix:**
1. Manually resolve conflicts: `git checkout main && git merge specclaw/<change>`
2. Or rebase the feature branch: `git rebase main` from the feature branch

### Task context too large

**Symptom:** Coding agent gets truncated context or hits token limits.

**Cause:** `build-context.sh` includes full `spec.md` and `design.md` plus file contents.

**Mitigations:**
- File contents are capped at **500 lines** per file (configurable via `MAX_FILE_LINES` in script)
- Keep spec and design documents focused
- Split large tasks into smaller ones with fewer files

### Resuming interrupted builds

**Symptom:** Build was interrupted (crash, timeout, manual stop).

**Fix:** Simply re-run `specclaw build <change>`.

**What happens:**
- `build.sh setup` detects the existing branch and switches to it (`branch_existed: true`)
- `parse-tasks.sh --status pending` returns only incomplete tasks
- Completed tasks (`[x]`) are skipped entirely
- Failed tasks (`[!]`) and in-progress tasks (`[~]`) are picked up for retry
- Git commits from completed tasks are preserved on the branch
