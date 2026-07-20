---
name: task-runner
description: >
  Persistent task queue system. Users add tasks at any time via natural language; tasks are stored
  in a single persistent queue file and executed asynchronously via subagents. A heartbeat/cron
  dispatcher wakes periodically to check pending tasks, spawn workers, and report completions.
  The system never "finishes" — it always remains ready for the next task.
metadata:
  author: skill-engineer
  version: 2.1.0
  owner: main agent (any agent with access to the full tool suite)
  tier: general
---

# Task Runner Skill

A persistent, daemon-style task queue. Users add tasks at any time. A dispatcher runs on every
heartbeat to check the queue and execute pending work via subagents. Tasks accumulate, complete,
and are archived — the queue itself never closes.

---

## Two Operating Modes

This skill has **two distinct modes** with different triggers and behaviors:

| Mode | Trigger | Purpose |
|------|---------|---------|
| **INTAKE** | User message containing task intent | Parse message → add tasks to queue → confirm → **immediately run DISPATCHER** |
| **DISPATCHER** | After INTAKE (primary) · Heartbeat/cron (backup) | Read queue → dispatch pending tasks → report completions |

Both modes read and write the **same persistent queue file**.

---

## A1 — Triggers

### Mode 1: INTAKE (user message)

Activate INTAKE mode when the user's message matches any of the following patterns:

| Pattern | Examples |
|---------|---------|
| Explicit task add | "add task", "add these tasks", "task:", "new task" |
| Delegation | "do this for me", "do these for me", "handle these", "can you do X" |
| Framing | "I need you to", "help me with", "I need", "I want you to" |
| List framing | "task list", "my tasks", "queue these", "work on these" |
| Control commands | "skip T-03", "retry T-02", "mark T-01 done", "cancel T-04" |
| Status check | "show tasks", "task status", "what's in the queue", "what are my pending tasks" |
| Compound ask | Any message with 2+ distinct action items (bullets, numbers, "and also", "then") |

**Do NOT activate INTAKE for:**
- Pure single-question lookups answered in one sentence ("what time is it?")
- Scheduling-only requests with no actual task ("remind me in 20 min")
- Single web search requests ("google X")
- The heartbeat systemEvent (that's DISPATCHER mode)

### Mode 2: DISPATCHER (inline after INTAKE, heartbeat, or cron)

Activate DISPATCHER mode when triggered by:
- **Immediately after INTAKE** — runs in the same turn, right after tasks are queued (primary path)
- `HEARTBEAT.md` check during a heartbeat poll (backup: catches retries and completions)
- systemEvent: `"TASK_RUNNER_DISPATCH: check queue and run pending tasks"` (backup)
- Any scheduled/cron trigger registered for task-runner (backup)

---

## Configuration

| Variable | Location | Default | Description |
|----------|----------|---------|-------------|
| `TASK_RUNNER_DIR` | TOOLS.md | `~/.openclaw/tasks/` | Directory for queue file and deliverables |
| `TASK_RUNNER_MAX_CONCURRENT` | TOOLS.md | `2` | Max tasks running simultaneously |
| `TASK_RUNNER_MAX_RETRIES` | TOOLS.md or env | `3` | Max retry attempts before marking blocked |
| `TASK_RUNNER_ARCHIVE_DAYS` | TOOLS.md | `7` | Days after which done/blocked tasks are archived |

**How to configure** — add to `TOOLS.md`:
```
## Task Runner
TASK_RUNNER_DIR=~/.openclaw/tasks/
TASK_RUNNER_MAX_CONCURRENT=2
TASK_RUNNER_MAX_RETRIES=3
TASK_RUNNER_ARCHIVE_DAYS=7
```

**Queue file path:** `${TASK_RUNNER_DIR}/task-queue.json`
(single persistent file, NOT dated — accumulates all tasks over time)

---

## A3 — Outputs

| Output | Path / Channel | Description |
|--------|---------------|-------------|
| Queue file | `${TASK_RUNNER_DIR}/task-queue.json` | Single persistent queue; all tasks |
| Per-task completion message | Chat notification | Sent immediately when a task finishes (done or blocked) |
| Deliverable files | Task-specific paths | Files produced by tasks (when applicable) |
| INTAKE confirmation | Chat | Sent after adding tasks to queue |

---

## Mode 1: INTAKE — Step-by-Step

**Goal:** Convert user message into structured task objects, append to queue, confirm.

### Step 0 — First Run Setup (auto-configure on first use)

**Run this check before anything else, every INTAKE invocation:**

```
CHECK whether ${TASK_RUNNER_DIR}/task-queue.json exists
IF file does NOT exist:
  → This is the first run. Auto-configure everything silently before proceeding.

  [1] Create directory:
      exec: mkdir -p ${TASK_RUNNER_DIR}

  [2] Initialize queue file:
      WRITE ${TASK_RUNNER_DIR}/task-queue.json with default structure:
      { "lastId": null, "tasks": [], "archivedCount": 0 }

  [3] Register heartbeat entry:
      READ HEARTBEAT.md (create it if missing)
      IF "Task Runner Dispatcher" is NOT already in the file:
        APPEND the following block (with a blank line before it):

        ## Task Runner Dispatcher
        Every heartbeat: check ${TASK_RUNNER_DIR}/task-queue.json
        - If pending or running tasks exist → run DISPATCHER mode (task-runner skill)
        - If nothing pending → HEARTBEAT_OK (skip)

      WRITE the updated HEARTBEAT.md

  [4] Register backup cron job:
      CALL cron tool with:
        action: "add"
        job:
          name: "Task Runner Dispatcher"
          schedule: { kind: "every", everyMs: 900000 }
          payload: { kind: "systemEvent", text: "TASK_RUNNER_DISPATCH: check queue and run pending tasks" }
          sessionTarget: "main"
          enabled: true

  [5] Notify user:
      "⚙️ Task Runner initialized.
       Heartbeat dispatcher registered in HEARTBEAT.md.
       Backup cron job registered (runs every 15 minutes).
       Your tasks will execute automatically."

  → THEN continue with normal INTAKE steps below.

IF file already exists:
  → Skip Step 0 entirely. Proceed directly to Step 1.
```

**Idempotency rule:** Step 0 only fires on true first run (queue file absent).
It will never double-register the heartbeat entry or create duplicate cron jobs.

---

### Step 1 — Load queue

```
READ ${TASK_RUNNER_DIR}/task-queue.json
IF file does not exist:
  Initialize with default structure (see references/queue-schema.md)
  Set lastId = null
```

### Step 2 — Parse tasks from message

Split user message into individual tasks using these cues:
- Numbered lists (1., 2., 3.)
- Bulleted lists (-, *, •)
- Explicit separators ("first", "also", "and then", "next")
- Compound sentences with multiple imperatives
- Single task: entire message is one task

### Step 3 — Assign IDs

Continue from `lastId` in the queue file:
- If `lastId = "T-05"`, next task is `T-06`
- If `lastId = null`, start at `T-01`
- Format: `T-NN` (zero-padded, minimum 2 digits; expand to 3 when N > 99)

### Step 4 — Build task objects

For each parsed task, create a JSON object (schema in `references/queue-schema.md`):
- Set `id`, `description`, `goal`, `status = "pending"`, `added_at`
- Set `retries = 0`, `maxRetries` from config
- Leave execution fields null

### Step 5 — Append to queue and save

```
APPEND new task objects to queue.tasks[]
UPDATE queue.lastId to the last assigned ID
WRITE updated queue file to disk
```

### Step 6 — Confirm to user

```
Added T-06: [description]. Starting now...
```

For multiple tasks:
```
📋 Added 3 tasks to queue:
• T-06: [description]
• T-07: [description]
• T-08: [description]
Starting dispatcher now...
```

**Then immediately run DISPATCHER mode (Steps 1–5 below) in the same turn.**
Do not exit and wait for the next heartbeat. Tasks must start executing immediately.
The heartbeat/cron dispatcher is a backup for retries and completion checks — not the primary execution path.

### Step 7 — Handle control commands

| Command | Action |
|---------|--------|
| `skip T-NN` | Set status = "skipped"; save; confirm |
| `retry T-NN` | Reset status = "pending", retries = 0; save; confirm |
| `cancel T-NN` | Set status = "skipped", blocked_reason = "cancelled by user"; save; confirm |
| `mark T-NN done` | Set status = "done", completed_at = now; save; confirm |
| `show tasks` / `task status` | Read queue; render status table (see A5 templates) |

---

## Mode 2: DISPATCHER — Step-by-Step

**Goal:** Check queue, dispatch pending tasks, track running tasks, report completions.

### Step 1 — Load queue

```
READ ${TASK_RUNNER_DIR}/task-queue.json
IF file does not exist OR tasks array is empty:
  → HEARTBEAT_OK (silent, nothing to do)
  → EXIT
```

### Step 2 — Check for work

```
pending_tasks = tasks where status = "pending"
running_tasks = tasks where status = "running"

IF pending_tasks is empty AND running_tasks is empty:
  → HEARTBEAT_OK (silent)
  → EXIT
```

### Step 3 — Check running tasks for completion

For each task with `status = "running"`:

```
IF subagent_session is set:
  CHECK subagent session status

  IF session is DONE:
    READ deliverable from session output
    RUN verification (see references/verification-guide.md)
    IF verification passes:
      SET status = "done"
      SET deliverable, deliverable_path, completed_at
      NOTIFY user: ✅ T-NN done — [summary]
    ELSE (verification failed):
      TREAT as failure (see retry logic below)

  IF session is FAILED or ERROR:
    IF retries < maxRetries:
      INCREMENT retries
      ADD to strategies_tried
      SET status = "pending"  ← will be re-dispatched this cycle
    ELSE:
      SET status = "blocked"
      SET blocked_reason, user_action_required, completed_at
      NOTIFY user: 🚫 T-NN blocked — [reason + unblock steps]

  IF session is STILL RUNNING:
    Leave as-is (will check again next heartbeat)
```

### Step 4 — Dispatch pending tasks

```
currently_running = count of tasks with status = "running"
slots_available = maxConcurrent - currently_running

FOR EACH pending task (in order of added_at), up to slots_available:
  PICK execution strategy (see references/task-types.md)
  SPAWN subagent with task description and strategy
  SET status = "running"
  SET subagent_session = spawned session ID
  SET started_at = now
```

**Subagent instructions template:**
```
You are executing task [T-NN] for the task-runner skill.

Task: [description]
Goal: [goal]
Type: [task_type]
Strategy: [selected strategy from task-types.md]

Execute the task. When complete:
1. Report the result clearly
2. Note any deliverable file path if a file was created
3. If blocked, explain exactly why and what the user needs to do

Do not start any other tasks. Focus only on this one.
```

### Step 5 — Save and exit

```
WRITE updated queue file (status changes, subagent_session IDs)
```

If any notifications were sent (done/blocked), this is an active heartbeat response.
If only silent dispatching occurred, this is still a heartbeat response (not HEARTBEAT_OK).
Only return HEARTBEAT_OK when there was truly nothing to do (no pending, no running tasks).

---

## A5 — Output Format Templates

### INTAKE confirmation (single task)

```
Added T-06: [description]. Queue now has N pending tasks.
```

### INTAKE confirmation (multiple tasks)

```
📋 Added N tasks to queue:
• T-06: [description]
• T-07: [description]

Starting now...
```

### Task status table (on demand)

```
📋 Task Queue — [N total, N pending, N running, N done, N blocked]

ID    Status      Description
T-01  ✅ done      [description] → [deliverable summary]
T-02  🔄 running   [description] (started [time ago])
T-03  ⏳ pending   [description]
T-04  🚫 blocked   [description] — [blocked_reason short]
T-05  ⏭️ skipped   [description]
```

### Task done notification

```
✅ T-NN done — [one-sentence summary of what was accomplished]
[deliverable: link or file path, if applicable]
```

### Task blocked notification

```
🚫 T-NN blocked after [N] attempts

What was tried:
- [Strategy 1]: [result]
- [Strategy 2]: [result]

Why it's blocked:
[Clear plain-English explanation]

To unblock:
1. [Concrete step #1]
2. [Concrete step #2 if needed]

Reply "retry T-NN" once ready.
```

### Task skipped

```
⏭️ T-NN skipped — as requested.
```

---

## A6 — Heartbeat Integration

Heartbeat and cron setup is **automatic**. Step 0 of INTAKE mode handles this on first use —
no manual configuration required.

### Role of heartbeat/cron (backup only)

Tasks are dispatched **immediately** after INTAKE — heartbeat and cron are backups only.

The backup dispatcher handles:
- **Retry dispatch**: tasks that failed and were reset to pending
- **Completion checks**: polling running subagent sessions for done/blocked status
- **Recovery**: tasks that were pending when no user message triggered INTAKE

Users should never need to wait for a heartbeat for a freshly added task.

### What gets configured automatically

**HEARTBEAT.md entry** (injected on first INTAKE):
```markdown
## Task Runner Dispatcher
Every heartbeat: check ${TASK_RUNNER_DIR}/task-queue.json
- If pending or running tasks exist → run DISPATCHER mode (task-runner skill)
- If nothing pending → HEARTBEAT_OK (skip)
```

**Backup cron job** (registered on first INTAKE):
```
every 15 min → systemEvent: "TASK_RUNNER_DISPATCH: check queue and run pending tasks"
sessionTarget: main
```

### Manual setup (if needed)

If for any reason auto-setup did not run (e.g., queue file was pre-created externally),
delete `${TASK_RUNNER_DIR}/task-queue.json` and send any task — Step 0 will fire.

---

## A7 — Success Criteria

### INTAKE mode succeeds when:

1. All tasks from user message parsed and assigned IDs
2. Tasks appended to queue file (file saved to disk)
3. Confirmation sent to user with task IDs and count
4. DISPATCHER mode triggered immediately in the same turn
5. Subagents spawned for pending tasks before INTAKE turn ends

### DISPATCHER mode succeeds when:

1. Queue file read without error
2. All running tasks checked for completion (done/blocked notifications sent as needed)
3. Pending tasks dispatched up to `maxConcurrent` slots
4. Queue file saved with updated states
5. User notified for every task that reached a terminal state this cycle

### Ongoing system health:

- Queue file is never corrupted (always valid JSON)
- Tasks older than `archiveDays` days with terminal status are archived/removed
- `lastId` always increments (no ID reuse)
- `maxRetries` respected before any task is marked blocked

---

## Edge Cases

| Situation | Behavior |
|-----------|---------|
| Queue file missing (first run) | Run Step 0 auto-setup: create dir, init queue, register heartbeat + cron; notify user |
| Queue file missing (manually deleted) | Step 0 re-fires: re-initializes queue; does NOT re-register heartbeat/cron (idempotent check) |
| Queue file corrupt/invalid JSON | Log error, notify user, do not overwrite; ask user to inspect |
| Task description is ambiguous | Assign `unknown` type; dispatcher will attempt classification + fallback |
| `maxConcurrent` already reached | Dispatcher skips dispatching; checks again next heartbeat |
| User adds task while dispatcher is running | Race-safe: dispatcher reads, processes, writes atomically per cycle |
| Task depends on another task's output | Set `blocked_reason = "depends on T-NN-1 which is pending/blocked"` |
| User says "retry T-NN" | Reset to pending, retries = 0, strategies_tried = [] |
| All tasks blocked | Notify user: "All tasks are blocked. Review unblock instructions above." |
| 20+ tasks added at once | Dispatcher dispatches in batches of `maxConcurrent`; all tasks eventually run |
| Subagent session ID lost | Mark task as pending again; will re-dispatch next cycle |
| Archive: done tasks > archiveDays old | Move to `${TASK_RUNNER_DIR}/archive/YYYY-MM.json`; remove from main queue |

---

## A8 — File Organization

```
${TASK_RUNNER_DIR}/
  task-queue.json          ← single persistent queue (all active tasks)
  archive/
    2026-01.json           ← archived tasks (done/blocked, older than archiveDays)
    2026-02.json
```

Queue file schema is documented in `references/queue-schema.md`.

---

## References

- `references/queue-schema.md` — Queue JSON format (complete field reference)
- `references/task-types.md` — Task type catalog and strategy selection
- `references/verification-guide.md` — Verification logic per task type
- `tests/test-triggers.json` — Trigger test cases (positive and negative)
