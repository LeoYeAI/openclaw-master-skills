---
name: codex-skill
description: 'Use when user asks to leverage codex, gpt-5, or gpt-5.1 to implement something (usually implement a plan or feature designed by Claude). Provides non-interactive automation mode for hands-off task execution without approval prompts.'
---

# Codex Agent Skill

Operate Codex CLI as a **managed coding agent** — from worktree setup through PR merge.

## Prerequisites

```bash
codex --version  # Verify installed
# Install: npm i -g @openai/codex  or  brew install codex
tmux -V          # tmux required for full workflow
```

## CLI Quick Reference

| Flag | Effect |
|------|--------|
| `exec "prompt"` | Non-interactive one-shot, exits when done |
| `--full-auto` | Alias for `-s workspace-write` (auto-approve file edits) |
| `-s workspace-write` | Read + write files in workspace |
| `-s read-only` | Analysis only, no modifications (default for `exec`) |
| `-s danger-full-access` | Full access including network and system |
| `--dangerously-bypass-approvals-and-sandbox` | Skip all prompts + no sandbox (safe in containers/VMs) |
| `-m <model>` | Model selection — only use when user explicitly requests a model (e.g. `gpt-5.1-codex-max`). Omit to use Codex default. |
| `-c "model_reasoning_effort=high"` | Reasoning effort: `low`, `medium`, `high` |
| `--json` | Structured JSON Lines output |
| `-o <file>` | Write final output to file |
| `-C <dir>` / `--cd <dir>` | Set working directory |
| `--add-dir <dir>` | Allow writing to additional directories |
| `--skip-git-repo-check` | Run in non-git directories |
| `resume --last` | Resume last session with new prompt |

---

## Execution Modes

### Quick Mode — Small Tasks

For trivial fixes, one-file changes, or analysis. Use `exec` (non-interactive):

```bash
# Via OpenClaw exec — use background=true + pty=true, NO hard timeout
# pty=true ensures codex CLI flushes output properly (no buffering issues)
# (hard timeout kills the process; instead we poll and extend)
exec(command="codex exec --full-auto 'fix the typo in README.md'",
     workdir="/path/to/project", background=true, pty=true)

# With high reasoning
exec(command="codex exec -c 'model_reasoning_effort=high' --full-auto 'fix the auth bug'",
     workdir="/path/to/project", background=true, pty=true)
```

#### Adaptive Timeout (Poll-and-Extend)

**Do NOT use `timeout=` for codex tasks.** Instead, use background execution
with periodic polling. This prevents premature kills on long-running tasks:

1. Launch with `background=true` (no `timeout`)
2. Poll every ~5 min with `process(action="poll", sessionId=<id>, timeout=300000)`
3. If process is still running → it's making progress, keep waiting
4. If process exited → check logs, done
5. Safety net: if no new output for 12 hours, ask user before killing

```
Poll loop (agent behavior, not a script):

  poll_interval = 5 min (300000 ms)
  max_silent_rounds = 144  (= 12 hours with no new output → ask user)

  repeat:
    result = process(action="poll", sessionId=<id>, timeout=300000)
    if result.completed:
      → check exit code, read logs, report result
      → break
    else:
      new_output = process(action="log", sessionId=<id>, limit=20)
      if new_output changed since last check:
        silent_rounds = 0          # still producing output, keep going
      else:
        silent_rounds += 1
      if silent_rounds >= max_silent_rounds:
        → notify user: "Codex has been silent for 12 hours, kill or keep waiting?"
        → wait for user decision
```

This way tasks that need 5 min or several hours both work without premature kills.

**Quick Mode caveats:**
- Session output is held **in memory only** — lost on OpenClaw restart (no disk persistence).
  For truly critical tasks, prefer Full Mode (tmux + log file).
- In-memory output is capped by `PI_BASH_MAX_OUTPUT_CHARS`. Very verbose codex tasks may
  lose early output from `process log`. Use `process log offset:0 limit:50` to check if
  the beginning is still available; if not, the cap was hit.
- `process` is scoped per agent — you can only see sessions you started.

### Full Mode — Features, Bugfixes, Refactors

For non-trivial tasks, use the **full workflow** below. This gives you:
- **Isolated worktree** — no conflicts with other work
- **tmux session** — mid-task steering without killing the agent
- **Task tracking** — know what's running at all times
- **Quality gates** — Definition of Done checklist
- **Smart retries** — don't waste tokens on repeated failures

---

## Full Workflow: Task → Merged PR

### Step 1: Create Worktree

Isolate each task in its own worktree and branch:

```bash
TASK_ID="feat-custom-templates"
BRANCH="feat/$TASK_ID"
REPO_ROOT=$(git rev-parse --show-toplevel)
WORKTREE="/tmp/worktrees/$TASK_ID"

git worktree add -b "$BRANCH" "$WORKTREE" origin/main
cd "$WORKTREE"

# Install dependencies (adapt to your stack)
pnpm install   # or: npm install / go mod tidy / pip install -r requirements.txt
```

### Step 2: Launch Agent in tmux

Start Codex in **interactive mode** (no `exec`) so you can steer mid-task.
**Important:** Use `tmux pipe-pane` to log output — do NOT use `| tee` because it
turns stdout into a pipe, which breaks interactive mode (codex detects `!isatty(stdout)`
and may disable interactive features, breaking `send-keys` steering).

```bash
LOG_FILE="/tmp/worktrees/$TASK_ID/codex-output.log"

# 1. Create session (starts a shell — codex not launched yet)
tmux new-session -d -s "$TASK_ID" -c "$WORKTREE"

# 2. Attach logging BEFORE launching codex — prevents losing early output
#    stdbuf -oL = line-buffered writes, so tail -f shows progress in real time
#    (plain cat buffers when writing to a file, causing monitoring lag)
tmux pipe-pane -t "$TASK_ID" -o "stdbuf -oL cat >> $LOG_FILE"

# 3. Launch codex via send-keys — all output captured from the start
#    Exit code is appended to log on completion for reliable status detection
tmux send-keys -t "$TASK_ID" \
  'codex -c "model_reasoning_effort=high" \
   --dangerously-bypass-approvals-and-sandbox \
   '"'"'Your detailed prompt here.

When completely finished:
1. Commit all changes with descriptive messages
2. Push the branch: git push -u origin '"$BRANCH"'
3. Create PR: gh pr create --fill
4. Notify: openclaw system event --text "Done: '"$TASK_ID"'" --mode now'"'"' \
   ; echo "CODEX_EXIT=$?" >> '"$LOG_FILE" Enter
```

**Why this order (session → pipe-pane → send-keys)?**
- **No race condition** — if you pass the command directly to `tmux new-session`, output
  produced before `pipe-pane` attaches is lost from the log file
- **Exit code captured** — `echo "CODEX_EXIT=$?"` appends the exit code to the log,
  so you can distinguish success from crash (otherwise tmux discards it on session close)
- **Line-buffered logging** — `stdbuf -oL` ensures `tail -f $LOG_FILE` works in real time

**Why interactive mode (no `exec`)?**
- Allows mid-task steering via `tmux send-keys`
- Agent can be redirected without killing and restarting
- `--dangerously-bypass-approvals-and-sandbox` is safe in container/sandbox environments

### Step 3: Register Task

Track all active tasks in a JSON registry:

```bash
mkdir -p "$REPO_ROOT/.clawd"
TASKS_FILE="$REPO_ROOT/.clawd/active-tasks.json"

# Initialize if not exists
[ -f "$TASKS_FILE" ] || echo '{"tasks":[]}' > "$TASKS_FILE"

# Register
jq --arg id "$TASK_ID" --arg branch "$BRANCH" --arg wt "$WORKTREE" \
  '.tasks += [{
    "id": $id,
    "agent": "codex",
    "branch": $branch,
    "worktree": $wt,
    "tmuxSession": $id,
    "status": "running",
    "startedAt": (now|floor),
    "pr": null,
    "retries": 0,
    "checks": {}
  }]' "$TASKS_FILE" > /tmp/tasks.$$.json && mv /tmp/tasks.$$.json "$TASKS_FILE"
```

### Step 4: Monitor & Steer

```bash
# --- Status check ---

# Is the agent still running?
tmux has-session -t "$TASK_ID" 2>/dev/null && echo "running" || echo "done"

# Check exit code (if agent finished — written by the exit-code capture in Step 2)
grep "CODEX_EXIT=" "/tmp/worktrees/$TASK_ID/codex-output.log"

# --- Reading output ---

# Use the LOG FILE, not capture-pane, for long-running tasks.
# tmux capture-pane only holds ~2000 lines of scrollback — earlier output is silently
# dropped. The log file (via pipe-pane) retains everything.

# View recent output (clean — strips ANSI escape codes from colors/spinners)
sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' "/tmp/worktrees/$TASK_ID/codex-output.log" | tail -100

# Follow output in real time (works because of stdbuf -oL in Step 2)
tail -f "/tmp/worktrees/$TASK_ID/codex-output.log"

# Search for errors (strip ANSI first for clean grep results)
sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' "/tmp/worktrees/$TASK_ID/codex-output.log" \
  | grep -i "error\|fail\|panic"

# Quick glance via tmux pane (fine for short tasks, unreliable for long ones)
tmux capture-pane -t "$TASK_ID" -p -S -50

# --- Detecting stuck agents ---

# Check if codex is making file changes (no changes for a long time → may be stuck)
git -C "$WORKTREE" status --short

# Check if the same error appears repeatedly (loop detection)
sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' "/tmp/worktrees/$TASK_ID/codex-output.log" \
  | grep -i "error" | sort | uniq -c | sort -rn | head -5

# --- Mid-task steering (DON'T kill — redirect!) ---

# Agent going the wrong direction?
tmux send-keys -t "$TASK_ID" "Stop. Focus on the API layer first, not the UI." Enter

# Agent missing context?
tmux send-keys -t "$TASK_ID" "The schema is in src/types/template.ts. Use that." Enter

# Agent's context window filling up?
tmux send-keys -t "$TASK_ID" "Focus only on these 3 files: api.ts, handler.ts, types.ts" Enter

# Agent needs test guidance?
tmux send-keys -t "$TASK_ID" "Run 'npm test -- --grep auth' to verify your changes." Enter
```

**Monitoring cadence**: Check every 5–10 minutes, not every 30 seconds. Agents need time to work.

### Step 5: Definition of Done

A PR is **NOT ready for review** until all checks pass:

```
✅ PR created              → gh pr list --head "$BRANCH"
✅ No merge conflicts       → gh pr view $PR_NUM --json mergeable -q '.mergeable'
✅ CI passing               → gh pr checks $PR_NUM
✅ AI code review passed    → at least one cross-model review (see Step 6)
✅ UI screenshots included  → (if applicable) screenshot in PR description
```

Quick inline check:
```bash
PR_NUM=$(gh pr list --head "$BRANCH" --json number -q '.[0].number')
echo "PR: #$PR_NUM"
gh pr checks "$PR_NUM"
gh pr view "$PR_NUM" --json mergeable -q '.mergeable'
```

### Step 6: Multi-Model Code Review

Review with a **different model** than the one that wrote the code. Different models catch different issues:

```bash
DIFF=$(gh pr diff "$PR_NUM")

# Option A: Claude reviews Codex's code (best for security & overengineering checks)
echo "$DIFF" | claude -p \
  --append-system-prompt "You are a senior code reviewer. Be concise, flag only real issues." \
  "Review this PR diff. Focus on: bugs, edge cases, missing error handling,
   race conditions, security issues. Cite file and line numbers.
   Output: list of issues with severity (critical/warning/info)."

# Option B: Different Codex model reviews with analysis focus
echo "$DIFF" | codex exec -s read-only \
  "Review this PR diff for logic errors, performance issues, and missing tests."
```

Post review results to PR:
```bash
gh pr comment "$PR_NUM" --body "## AI Code Review

$REVIEW_OUTPUT"
```

Update task registry:
```bash
jq --arg id "$TASK_ID" \
  '(.tasks[] | select(.id == $id)).checks.codeReviewPassed = true' \
  "$TASKS_FILE" > /tmp/tasks.$$.json && mv /tmp/tasks.$$.json "$TASKS_FILE"
```

### Step 7: Notify

If you included the notify command in the agent prompt (Step 2), the agent self-notifies on completion.

Otherwise, notify after DoD passes:
```bash
openclaw system event --text "✅ PR #$PR_NUM ready for review: $TASK_ID — all checks passed" --mode now
```

Update task status:
```bash
jq --arg id "$TASK_ID" --argjson pr "$PR_NUM" \
  '(.tasks[] | select(.id == $id)) |= (.status = "done" | .pr = $pr | .completedAt = (now|floor))' \
  "$TASKS_FILE" > /tmp/tasks.$$.json && mv /tmp/tasks.$$.json "$TASKS_FILE"
```

### Step 8: Cleanup

After PR is merged:
```bash
git worktree remove "$WORKTREE" 2>/dev/null
git branch -d "$BRANCH" 2>/dev/null

# Remove from registry
jq --arg id "$TASK_ID" '.tasks = [.tasks[] | select(.id != $id)]' \
  "$TASKS_FILE" > /tmp/tasks.$$.json && mv /tmp/tasks.$$.json "$TASKS_FILE"
```

---

## Smart Retry Strategy

When an agent fails, **analyze the failure and adapt the prompt** — don't just re-run blindly.

| Failure Type | Symptom | Retry Strategy |
|---|---|---|
| Context overflow | Agent loops, produces garbage, or stops mid-task | Narrow scope: *"Focus only on files X, Y, Z"* |
| Wrong direction | Agent implements something unrelated to intent | Correct intent: *"Stop. Customer wanted X, not Y. Spec: ..."* |
| Missing info | Agent makes wrong assumptions about architecture | Add context: *"Auth uses JWT, see src/auth/jwt.ts"* |
| CI failure | Tests, lint, or typecheck fail after PR | Attach CI log: *"Fix these test failures: ..."* |
| Build failure | Dependencies missing or incompatible | Pre-install deps before retry |

**Max 3 retries.** After that, escalate to human.

```bash
RETRY=$((RETRY + 1))
if [ "$RETRY" -gt 3 ]; then
  openclaw system event --text "🚨 BLOCKED: $TASK_ID failed after 3 retries — needs human help" --mode now
  jq --arg id "$TASK_ID" '(.tasks[] | select(.id == $id)).status = "blocked"' \
    "$TASKS_FILE" > /tmp/tasks.$$.json && mv /tmp/tasks.$$.json "$TASKS_FILE"
  exit 1
fi

# Capture what went wrong — strip ANSI codes for clean error text
LOG_FILE="/tmp/worktrees/$TASK_ID/codex-output.log"
if [ -f "$LOG_FILE" ]; then
  FAILURE_LOG=$(sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' "$LOG_FILE" | tail -500)
else
  FAILURE_LOG=$(tmux capture-pane -t "$TASK_ID" -p -S -200)
fi
CI_LOG=$(gh pr checks "$PR_NUM" 2>/dev/null || echo "no PR yet")
tmux kill-session -t "$TASK_ID" 2>/dev/null

# Mark retry boundary in log (so retries don't blend together)
echo "=== RETRY $RETRY — $(date -Iseconds) ===" >> "$LOG_FILE"

# Respawn: session first, pipe-pane second, send-keys third (same pattern as Step 2)
tmux new-session -d -s "$TASK_ID" -c "$WORKTREE"
tmux pipe-pane -t "$TASK_ID" -o "stdbuf -oL cat >> $LOG_FILE"
tmux send-keys -t "$TASK_ID" \
  'codex -c "model_reasoning_effort=high" \
   --dangerously-bypass-approvals-and-sandbox \
   '"'"'Previous attempt failed. Error output:
'"$FAILURE_LOG"'

CI status: '"$CI_LOG"'

Fix the issues above and complete the original task.
[...your enriched instructions here...]

When done: commit, push, gh pr create --fill, then run:
openclaw system event --text "Done: '"$TASK_ID"' (retry '"$RETRY"')" --mode now'"'"' \
   ; echo "CODEX_EXIT=$?" >> '"$LOG_FILE" Enter

# Update registry
jq --arg id "$TASK_ID" --argjson r "$RETRY" \
  '(.tasks[] | select(.id == $id)) |= (.retries = $r | .status = "running")' \
  "$TASKS_FILE" > /tmp/tasks.$$.json && mv /tmp/tasks.$$.json "$TASKS_FILE"
```

---

## Parallel Execution

Run multiple agents simultaneously on different tasks:

```bash
# Helper: launch codex in tmux with proper logging (session → pipe-pane → send-keys)
launch_codex() {
  local TASK="$1" WORKDIR="$2" PROMPT="$3"
  local LOG="$WORKDIR/codex-output.log"
  tmux new-session -d -s "$TASK" -c "$WORKDIR"
  tmux pipe-pane -t "$TASK" -o "stdbuf -oL cat >> $LOG"
  tmux send-keys -t "$TASK" \
    "pnpm install && codex --dangerously-bypass-approvals-and-sandbox '$PROMPT'; echo \"CODEX_EXIT=\$?\" >> $LOG" Enter
}

# Task 1: Feature
git worktree add -b feat/auth /tmp/worktrees/feat-auth origin/main
launch_codex feat-auth /tmp/worktrees/feat-auth "Implement JWT auth..."

# Task 2: Bugfix
git worktree add -b fix/payments /tmp/worktrees/fix-payments origin/main
launch_codex fix-payments /tmp/worktrees/fix-payments "Fix payment webhook..."

# Dashboard: check all agents (use log files, not capture-pane, for reliable output)
tmux ls
for s in $(tmux ls -F '#{session_name}' 2>/dev/null); do
  LOG="/tmp/worktrees/$s/codex-output.log"
  echo "=== $s ==="
  if tmux has-session -t "$s" 2>/dev/null; then
    sed 's/\x1b\[[0-9;]*[a-zA-Z]//g' "$LOG" 2>/dev/null | tail -5 || echo "(no log yet)"
  else
    EXIT=$(grep "CODEX_EXIT=" "$LOG" 2>/dev/null | tail -1)
    echo "(exited) ${EXIT:-exit code unknown}"
  fi
done
```

---

## Codex-Specific Features

### Reasoning Effort

Control how much the model "thinks" before acting:

```bash
# High — for complex logic, multi-file refactors
codex -c "model_reasoning_effort=high" --full-auto "refactor auth module"

# Medium — balanced (default)
codex exec --full-auto "add input validation"

# Low — for trivial/mechanical changes
codex -c "model_reasoning_effort=low" --full-auto "rename all instances of foo to bar"
```

### Sandbox Modes

| Mode | Use Case |
|------|----------|
| `read-only` | Code review, analysis, documentation |
| `workspace-write` / `--full-auto` | Feature implementation, bug fixes, refactors |
| `danger-full-access` | Installing dependencies, network access needed |
| `--dangerously-bypass-approvals-and-sandbox` | Full auto in containers (recommended for tmux workflow) |

### JSON Output

```bash
# Structured output for programmatic processing
codex exec --full-auto --json "implement and test the feature"

# Save to file
codex exec --full-auto -o results.txt "run analysis"
```

### Resume Session

```bash
# Resume last session with a follow-up task
codex exec resume --last "now add tests for the feature you just built"
```

---

## Best Practices

### Prompt Quality
- **Include file paths**: *"The entry point is src/index.ts, config in src/config/"*
- **Include schemas/types**: Paste relevant type definitions into the prompt
- **Include test commands**: *"Verify with: npm test -- --grep auth"*
- **Include commit convention**: *"Use conventional commits: feat:, fix:, chore:"*
- **Include error logs**: When retrying, always attach the failure output

### Scope Management
- **One task per agent** — don't ask for "refactor everything"
- **Pre-install dependencies** before launching the agent
- **Be specific** — *"Add rate limiting to POST /api/users"* not *"improve the API"*
- **Use high reasoning effort** for complex tasks, low for mechanical ones

### When to Interrupt (Ask Human)
- Destructive operations (drop tables, force push main)
- Security decisions (expose credentials, change auth)
- Ambiguous requirements with significant trade-offs
- All other decisions: proceed autonomously
