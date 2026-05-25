---
name: conduxt
description: >
  Orchestrate full-duplex coding agent sessions via ACPX (preferred) or tmux
  (fallback), composing OpenClaw native tools and community Skills.
  Handles any coding task: requirements, bug fixes, refactoring, investigations.
  Use when: "implement feature X", "fix this bug", "refactor the API layer",
  "start agent", "open a session", "code this", "fix issue #N".
user-invocable: true
homepage: https://github.com/xuezhouyang/conduxt
metadata: {"openclaw": {"emoji": "🎛️", "requires": {"bins": ["git", "jq"], "anyBins": ["acpx", "tmux"]}, "os": ["darwin", "linux"]}}
---

# CLI Coding Orchestrator

> You are the orchestrator. Drive coding agents via ACPX (protocol-level) or
> tmux (terminal scraping), composing community Skills to complete end-to-end
> coding tasks — feature implementation, bug fixes, investigations, refactoring.

---

## 1. Your Role

You are the OpenClaw Main model. You have a full toolchain — use it directly
to orchestrate tasks, not by calling pre-made bash scripts. Scripts in the
`scripts/` directory exist only as optional helpers.

## 2. Dual-Backend Architecture: ACPX vs tmux

This Skill supports two agent communication backends. **Prefer ACPX**, use tmux as fallback.

### Why ACPX First

| Dimension | ACPX (Protocol) | tmux (Terminal Scraping) |
|-----------|-----------------|------------------------|
| Communication | Full-duplex JSON-RPC over stdio | Half-duplex PTY scraping |
| Output | Typed ndjson (tool_call/text/done) | Raw ANSI text (burns 30-40% Context) |
| Mid-task instructions | Prompt queue: submit anytime, queued | send-keys: timing issues, may be treated as user input |
| Completion detection | Native `[done]` signal | Regex matching or Callback injection |
| Cancellation | Cooperative `session/cancel` (preserves state) | `C-c` (unreliable, may corrupt state) |
| Crash recovery | Auto-restart + load serialized session | Session survives but agent death goes unnoticed |
| Permissions | `--approve-all` / `--deny-all` policy-based | Interactive TTY popups (block unattended flows) |
| Visual monitoring | ndjson pipe to external tools | tmux split-pane (advantage) |

**ACPX is strictly superior for communication, observation, and mid-task instructions. tmux only wins on maturity and visual monitoring.**

### When to Use Which

| Scenario | Backend |
|----------|---------|
| Default / new tasks | **ACPX** |
| ACPX unavailable or unstable | tmux (fallback) |
| Need visual split-pane monitoring | tmux (or ACPX + external dashboard) |
| Agent doesn't support ACP | tmux |

---

## 3. Toolbox

### Native Tools

| Tool | Purpose | Key Usage |
|------|---------|-----------|
| `exec` | Run shell commands | `acpx prompt`, `tmux send-keys`, `git worktree`, `gh` |
| `exec pty:true` | Interactive terminal | Simple one-off tasks (do NOT nest tmux inside PTY) |
| `process` | Background processes | `background:true` for long tasks, `process action:log limit:20` |
| `read`/`write`/`edit` | File operations | MEMORY.md, active-tasks.json |
| `gh` | GitHub CLI | `gh issue view`, `gh pr create` |
| `git` | Version control | `git worktree add/remove`, `git branch`, `git push` |

### ACPX Commands

| Command | Purpose |
|---------|---------|
| `acpx prompt -s <session> "<instruction>"` | Send prompt (creates session if new, appends if existing) |
| `acpx prompt -s <session> --no-wait "<msg>"` | Fire-and-forget (returns immediately) |
| `acpx prompt -s <session> --format json "<msg>"` | Structured ndjson output |
| `acpx sessions list` | List all active sessions |
| `acpx sessions show -s <session>` | Show session details |
| `acpx cancel -s <session>` | Cooperative cancel of current task |
| `acpx prompt -s <session> --approve-all "<msg>"` | Auto-approve all permission requests |

### Community Skills (Composable)

| Skill | When to Use | Core Capability |
|-------|-------------|-----------------|
| `coding-agent` | Agent lifecycle management (tmux backend) | tmux session + Callback wakeup + worktree |
| `tmux` | Low-level tmux operations | Socket management, send-keys, wait-for-text |
| `tmux-agents` | Multi-agent types (tmux backend) | Codex, Gemini, local models |
| `gemini` | Gemini CLI coding | Long-context tasks |
| `resilient-coding-agent` | Gateway restart recovery | tmux session persistence |

> **Composition principle**: Use Skills when available (they encapsulate best practices).
> Fall back to native tools when Skills don't cover your needs.
> coding-agent / tmux-agents use tmux backend — if using ACPX backend, use `acpx` commands directly.

---

## 4. Full-Duplex Communication Model

### ACPX Path (Preferred)

```
User ←→ You (Main) ←→ acpx ←→ ACP Adapter ←→ Coding Agent
          ↕              ↕
       MEMORY.md    ndjson stream (typed events: thinking/tool_call/text/done)
                    prompt queue (submit anytime, protocol-level isolation)
                    session persistence (~/.acpx/sessions/*.json)
```

- **User → Agent**: `acpx prompt -s <session> "<instruction>"` enters the prompt queue
- **Agent → User**: `[done]` event in ndjson stream → you are woken up → notify user
- **True full-duplex**: Submit new instructions while previous task is running, queued without timing issues

### tmux Path (Fallback)

```
User ←→ You (Main) ←→ tmux session ←→ Coding Agent
          ↕                ↕
       MEMORY.md      send-keys (inject instructions)
                      capture-pane (read output)
                      Callback event (completion notification)
```

- **User → Agent**: `tmux send-keys -t <session> "<text>" Enter`
- **Agent → User**: Callback JSON or capture-pane polling
- **Timing caveat**: When agent is busy, send-keys may be treated as user input. Send `Escape` first and wait for idle.

---

## 5. Scenario Playbook

Each scenario provides both ACPX (preferred) and tmux (fallback) paths.

### Scenario A: Execute Coding Task

**Triggers** (task source is flexible):
- "Implement pagination for the users API"
- "Investigate this performance issue"
- "Refactor the API layer to RESTful"
- "Fix issue #78" (optional, low priority)

```
1. Understand the Task
   Task sources are diverse — handle flexibly:
   • User describes requirement → use description text as prompt directly
   • Link to external doc/wiki → fetch content and extract requirements
   • GitHub issue → exec: gh issue view <N> --json title,body
   • Code review comments → extract action items

2. Generate task_id and branch name
   Create semantic IDs from task content, e.g.:
   • "add pagination" → task_id: add-pagination, branch: feat/add-pagination
   • "perf issue"     → task_id: perf-analysis,  branch: fix/perf-analysis
   • issue #78        → task_id: issue-78,        branch: fix/issue-78

3. Create isolated workspace
   → exec: git worktree add ../worktrees/<task_id> -b <branch> main

4. Start Coding Agent

   ┌─ ACPX path (preferred) ────────────────────────────────────┐
   │ exec: cd ../worktrees/<task_id> && acpx prompt \           │
   │   -s <task_id> \                                           │
   │   --approve-all \                                          │
   │   --no-wait \                                              │
   │   "<task description + callback instructions (see §6)>"   │
   │                                                            │
   │ • --no-wait: returns immediately, doesn't block you        │
   │ • --approve-all: auto-approve permissions for unattended   │
   │ • session auto-persisted to ~/.acpx/sessions/<task_id>.json│
   └────────────────────────────────────────────────────────────┘

   ┌─ tmux path (fallback) ─────────────────────────────────────┐
   │ a) Use coding-agent Skill (recommended)                    │
   │ b) Use tmux-agents Skill (for Gemini/Codex)                │
   │ c) Direct exec:                                            │
   │    tmux new-session -d -s <task_id> -c ../worktrees/<id>  │
   │    tmux send-keys -t <task_id> "claude" Enter              │
   │    tmux send-keys -t <task_id> "<prompt + callback>" Enter │
   └────────────────────────────────────────────────────────────┘

5. Write MEMORY.md task entry (see §7)

6. Inform user
   → "Session <task_id> started, agent is working. Will notify on completion."

7. Wait for completion
   ACPX: [done] in ndjson stream → read result → route
   tmux: Callback arrives or 30min timeout → capture-pane → notify
```

**Parallel tasks**: Repeat the above for each task. ACPX natively supports named parallel sessions.
Before creating PRs, check for file conflicts between branches with `git diff --name-only`.

### Scenario B: Interactive Session (Human-in-the-Loop)

**Trigger**: "Start a session for API refactoring"

```
ACPX:
  exec: acpx prompt -s api-refactor "You are my coding assistant, await instructions."
  → Creates named session, agent enters wait state

tmux:
  exec: tmux new-session -d -s api-refactor -c /path/to/repo
  exec: tmux send-keys -t api-refactor "claude" Enter

Report to user:
  "Session api-refactor started. You can:
   • 'Tell api-refactor to start with interface definitions'
   • 'How is api-refactor doing?'
   • 'Stop api-refactor'"
```

### Scenario C: Mid-Task Intervention (Full-Duplex Core)

**Trigger**: "Tell <session> to do Y" / "Change <session>'s direction"

```
ACPX (no timing issues, protocol-level isolation):
  Append instruction:  acpx prompt -s <session> --no-wait "Focus on interface definitions, skip DB layer"
  Cancel current:      acpx cancel -s <session>

tmux (watch for timing):
  Append instruction:  tmux send-keys -t <session> "Focus on interface definitions" Enter
  Interrupt current:   tmux send-keys -t <session> Escape
  Force stop:          tmux send-keys -t <session> C-c
```

### Scenario D: Check Progress

**Trigger**: "How is <session> doing?" / "status"

```
ACPX:
  exec: acpx sessions show -s <session>
  → Structured session state, no ANSI stripping needed
  → Or use --format json for recent ndjson events

tmux:
  exec: tmux capture-pane -p -t <session> -S -20
  → Strip ANSI: sed 's/\x1b\[[0-9;]*[a-zA-Z]//g'
  → Summarize for user (don't paste raw terminal output)

List all sessions:
  ACPX: acpx sessions list
  tmux: tmux list-sessions
```

### Scenario E: Agent Selection

| Condition | Recommended Agent | ACPX Launch | tmux Launch |
|-----------|------------------|-------------|-------------|
| Default / best coding | Claude Code | `acpx prompt -s X --agent claude` | `coding-agent` Skill |
| Long context needed | Gemini CLI | `acpx prompt -s X --agent gemini` | `gemini` Skill |
| Need Codex | Codex CLI | `acpx prompt -s X --agent codex` | `tmux-agents` Skill |
| Simple one-off | Direct exec | No session needed | `exec pty:true` |

ACPX-supported agent adapters:
- Claude Code: `npx @zed-industries/claude-agent-acp` (adapter)
- Codex CLI: `npx @zed-industries/codex-acp` (adapter)
- Gemini CLI: `gemini --experimental-acp` (native support)

### Scenario F: PR Creation

**Trigger**: [done] signal or Callback shows completed + tests pass

```
1. Independently verify tests (don't trust agent's self-report)
   → cd <worktree> && <auto-detect test runner>

2. Push branch
   → git push -u origin <branch>

3. Create PR
   → gh pr create --title "fix: <title>" --body "..." --base main --head <branch>

4. Update MEMORY.md: status=completed, add PR link

5. Notify user
```

### Scenario G: Cleanup

```
ACPX:
  End session (history preserved in ~/.acpx/sessions/)
  → No need to kill processes, ACPX manages lifecycle

tmux:
  tmux kill-session -t <session>

Common:
  git worktree remove <dir> --force
  git branch -d <branch> (optional)
  Edit MEMORY.md: status → abandoned or completed
```

---

## 6. Structured Callback Protocol

### ACPX Path

ACPX ndjson stream natively provides `[done]` signals, but we still inject the
Callback JSON instruction for unified processing logic. The JSON can be extracted
directly from the ndjson stream — **no regex matching against terminal output**.

### tmux Path

Requires injection and detection of `callback-json` keyword via capture-pane.

### Injection Content (Shared by Both Paths)

Append to the end of the agent prompt:

```
When you complete this task, you MUST output the following JSON block
wrapped in triple backticks with language tag "callback-json":

{
  "task_id": "<task_id>",
  "status": "completed|failed|need_clarification",
  "branch": "<branch>",
  "files_changed": ["file1.go", "file2_test.go"],
  "test_results": { "passed": 42, "failed": 0, "skipped": 1 },
  "duration_minutes": 12,
  "summary": "Brief description of what was done"
}

Commit your code and run tests BEFORE outputting this JSON. This is mandatory.
```

### Routing Rules

| Condition | Your Action |
|-----------|-------------|
| `completed` + `failed=0` | Independently verify tests → create PR → notify user |
| `completed` + `failed>0` | Append instruction: "N tests failing, please fix and re-output callback" |
| `failed` | Update MEMORY.md → notify user of failure reason |
| `need_clarification` | Forward `summary` to user, wait for reply, then send to agent |

Pure if/else — no LLM interpretation of natural language needed.

### Completion Detection Comparison

| Method | ACPX | tmux |
|--------|------|------|
| Primary | ndjson `[done]` signal | `coding-agent` Skill built-in Callback |
| Fallback | Extract callback-json from ndjson | `capture-pane` regex matching |
| Background | N/A (stream is continuous) | `scripts/watchdog.sh` |

---

## 7. State Persistence

### MEMORY.md Task Entry

```markdown
## In-Flight Tasks

### add-pagination: Implement pagination for /api/users
- **Status**: in-progress
- **Branch**: feat/add-pagination
- **Session**: add-pagination
- **Backend**: ACPX | tmux
- **Agent**: Claude Code | Gemini CLI
- **Started**: 2026-03-10T14:30:00Z
- **Latest Milestone**: 14:42 - Running tests
- **Callback**: pending
```

### When to Write

| Event | Action |
|-------|--------|
| Task created | Add entry, status=pending |
| Agent started | status → in-progress, record backend type |
| User asks for progress | Update Latest Milestone |
| Completion signal received | status → completed/failed |
| PR created | Add PR link |
| Cleanup | status → completed/abandoned |

> **MEMORY.md must be written under any backend** — it is the only shared state
> across sessions and agents. ACPX session history is per-agent and does not
> share across sessions.

---

## 8. Crash Detection

### ACPX Path

ACPX has built-in crash recovery — auto-restarts agent and loads serialized session.
You only need to check if the session is still active:

```bash
acpx sessions list              # check if session exists
acpx sessions show -s <session> # check detailed status
```

If session disappeared (ACPX itself crashed), recover context from MEMORY.md and recreate.

### tmux Path

tmux session survives but agent may have died:

```bash
tmux has-session -t <session> 2>/dev/null  # is session alive
tmux capture-pane -p -t <session> -S -1    # any output
```

Optional: `scripts/watchdog.sh` background loop (zero token).

---

## 9. Optional Helper Scripts

Three scripts in `scripts/` with dual-backend support. You **can use them but don't have to**:

| Script | Purpose |
|--------|---------|
| `setup.sh <task_id> <branch> <worktree_dir> [task_desc] [backend]` | Create branch + worktree + initialize MEMORY.md |
| `launch.sh <task_id> <worktree_dir> <prompt_file> [backend] [agent]` | ACPX-first agent launch with auto tmux fallback |
| `watchdog.sh [task_id]` | Background zero-token monitoring (ACPX/tmux aware) |

Parameters:
- `backend`: `acpx` (default if available) | `tmux` | `auto`
- `agent`: `claude` | `gemini` | `codex` | `aider` | `auto`

---

## 10. Command Reference

### ACPX Commands

| Action | Command |
|--------|---------|
| Send prompt | `acpx prompt -s <name> "<text>"` |
| Fire-and-forget | `acpx prompt -s <name> --no-wait "<text>"` |
| Structured output | `acpx prompt -s <name> --format json "<text>"` |
| Auto-approve perms | `acpx prompt -s <name> --approve-all "<text>"` |
| List sessions | `acpx sessions list` |
| Show session | `acpx sessions show -s <name>` |
| Cancel task | `acpx cancel -s <name>` |

### tmux Commands

| Action | Command |
|--------|---------|
| Create session | `tmux new-session -d -s <name> -c <dir>` |
| Send instruction | `tmux send-keys -t <name> "<text>" Enter` |
| Read output | `tmux capture-pane -p -t <name> -S -30` |
| List sessions | `tmux list-sessions` |
| Send interrupt | `tmux send-keys -t <name> C-c` |
| Kill session | `tmux kill-session -t <name>` |

### Common Commands

| Action | Command |
|--------|---------|
| Fetch issue | `gh issue view <N> --json title,body,labels` |
| Create worktree | `git worktree add <dir> -b <branch> main` |
| Remove worktree | `git worktree remove <dir>` |
| Push branch | `git push -u origin <branch>` |
| Create PR | `gh pr create --title "..." --body "..." --base main --head <branch>` |

---

## 11. Relationship with Existing Skills

| Skill | Backend | Your Usage |
|-------|---------|------------|
| `coding-agent` | tmux | Preferred agent launch for tmux fallback |
| `tmux` | tmux | Low-level operations (custom socket, wait-for-text) |
| `tmux-agents` | tmux | Multi-agent types (Codex, Gemini, local models) |
| `gemini` | tmux | Gemini CLI for long-context tasks |
| `resilient-coding-agent` | tmux | Gateway restart recovery |

> When using ACPX backend, these tmux-based Skills don't apply. Use `acpx` commands directly.
> When ACPX is unavailable, fall back to these Skills.

---

## 12. Evolution Roadmap

```
Phase 1 (Current): ACPX and tmux in parallel
  • New tasks prefer ACPX
  • ACPX instability → tmux fallback
  • Validate ACPX session persistence and crash recovery

Phase 2: High-value migration
  • Migrate half-duplex and context-pollution-heavy scenarios to ACPX
  • tmux demoted to visual monitoring only

Phase 3 (End state): ACPX as primary path
  • tmux optional (visual only)
  • ACPX becomes the standard interface for all agent communication
```

---

## 13. Important Notes

1. **ACPX stability**: ACPX is still early-stage and may have breaking changes. Fall back to tmux immediately on issues.
2. **No PTY nesting**: Do NOT start tmux inside `exec pty:true` (double PTY allocation)
3. **tmux send-keys timing**: When agent is busy, send `Escape` first and wait for idle before appending
4. **Don't pull full logs**: Use capture-pane `-S -20`, ACPX use `--format json` pipe
5. **Security**: Never pass API keys or secrets via send-keys or acpx prompt
6. **ACPX permissions**: Use `--approve-all` for unattended; `--approve-reads` when security matters
7. **Context pollution**: ACPX ndjson can pipe to external monitoring without entering Context; tmux capture-pane is zero-token

---

## 14. User Command Mapping

| User Says | What You Do |
|-----------|-------------|
| "Implement feature X for project Y" | Scenario A: understand requirement → create task → start agent |
| "Investigate this performance issue" | Scenario A: analyze problem → create investigation task |
| "Do these three tasks in parallel" | Scenario A × N (parallel named sessions) |
| "Fix issue #78" (optional) | Scenario A: fetch issue description |
| "Start a session for X" | Scenario B: interactive |
| "Tell <session> to do Y" | Scenario C: acpx prompt / tmux send-keys |
| "How is <session> doing?" | Scenario D: acpx sessions show / capture-pane |
| "Use Gemini for this task" | Scenario E: acpx --agent gemini / gemini Skill |
| "Create PR" | Scenario F |
| "Stop <session>" / "cleanup" | Scenario G |
| "status" | List all sessions + MEMORY.md in-flight tasks |
| "retry <task>" | Scenario G cleanup + Scenario A restart |
