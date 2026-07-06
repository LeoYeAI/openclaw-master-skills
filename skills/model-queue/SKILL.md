---
name: task-queue-by-model-source
description: >
  Multi-queue task orchestration system. Tasks are routed to queues by model source,
  with support for task dependencies, context passing, and failure handling.
  Each model source has its own FIFO queue, executing one task at a time.
metadata:
  author: openclaw
  version: 1.0.0
  tier: general
---

# Model Queue Skill

A multi-queue task orchestration system where tasks are routed to queues based on their target model source. Supports task dependencies, context passing between tasks, and configurable failure handling.

---

## Core Concepts

### Model Source Mapping

Models are grouped by their underlying source (e.g., local Ollama, remote Ollama, cloud API). All tasks targeting models on the same source share a single queue.

**Configuration in TOOLS.md:**
```
MODEL_SOURCE_OLLAMA_LOCAL=ollama/llama3,ollama/qwen2.5,ollama/mistral
MODEL_SOURCE_OLLAMA_REMOTE=ollama-remote/qwen3.5:27b,ollama-remote/llama3:70b
MODEL_SOURCE_CLOUD_NVIDIA=nvidia/z-ai/glm5,nvidia/llama3
```

### Queue Isolation

Each model source has its own queue file:
- `${MODEL_QUEUES_DIR}/ollama-local.json`
- `${MODEL_QUEUES_DIR}/ollama-remote.json`

Queues are independent — a blocked task in one queue doesn't affect other queues.

---

## Task Object Schema

```json
{
  "id": "T-001",
  "queue": "ollama-local",
  "model": "ollama/qwen2.5",
  "description": "Analyze the sales data",
  "goal": "Generate a summary of Q1 sales performance",
  "status": "pending",
  "priority": 0,
  "depends_on": null,
  "on_depends_fail": "block",
  "context_input": null,
  "result": null,
  "result_status": null,
  "result_summary": null,
  "retries": 0,
  "maxRetries": 3,
  "subagent_session": null,
  "added_at": "2026-03-04T16:51:00Z",
  "started_at": null,
  "completed_at": null
}
```

---

## Task Statuses

| Status | Description |
|--------|-------------|
| `pending` | Ready to be dispatched (no dependencies or resolved) |
| `waiting` | Has dependency, waiting for it to complete |
| `running` | Currently executing via subagent |
| `done` | Completed successfully |
| `failed` | Failed after max retries |
| `blocked` | Dependency failed, waiting for user action |
| `skipped` | Skipped by user or due to dependency failure |

---

## Two Operating Modes

| Mode | Trigger | Purpose |
|------|---------|---------|
| **INTAKE** | User message containing task intent | Parse message → route to queue → confirm → **immediately run DISPATCHER** |
| **DISPATCHER** | After INTAKE (primary) · Heartbeat/cron (backup) | Check queues → dispatch pending tasks → report completions |

---

## A1 — Triggers

### Model Source Configuration

**REQUIRED: Configure model sources in TOOLS.md before first use.**

Add to your `TOOLS.md`:
```markdown
## Model Queue Configuration

MODEL_QUEUES_DIR=~/.openclaw/model-queues/
MODEL_QUEUE_MAX_RETRIES=3
MODEL_QUEUE_ARCHIVE_DAYS=7

# Model Source Mappings (REQUIRED)
# Format: MODEL_SOURCE_{NAME}=model1,model2,model3
MODEL_SOURCE_OLLAMA_LOCAL=ollama/llama3,ollama/qwen2.5,ollama/mistral
MODEL_SOURCE_OLLAMA_REMOTE=ollama-remote/qwen3.5:27b,ollama-remote/llama3:70b
MODEL_SOURCE_CLOUD_NVIDIA=nvidia/z-ai/glm5,nvidia/llama3

# Default model source when not specified (optional)
DEFAULT_MODEL_SOURCE=ollama-remote
```

### How Model Source is Determined

1. **Explicit model**: User says "用 qwen2.5 分析..." → find qwen2.5's source
2. **Explicit source**: User says "send to remote..." → use default model for that source
3. **No specification**: Use DEFAULT_MODEL_SOURCE, or ask user

### INTAKE Triggers

Activate INTAKE mode when user message matches:

| Pattern | Examples |
|---------|----------|
| Explicit task | "add task", "new task", "queue this" |
| Delegation | "do this for me", "handle this" |
| Model-specific | "用 qwen3.5 分析这个", "用远程模型处理" |
| Dependency | "然后", "after that", "next" |
| Status check | "task status", "show queue", "队列状态" |
| Control | "cancel T-001", "retry T-002", "skip T-003" |

**Do NOT activate INTAKE for:**
- Simple one-sentence questions
- Pure scheduling requests without tasks
- Single web searches

### DISPATCHER Triggers

- **Immediately after INTAKE** (primary path)
- HEARTBEAT.md check during heartbeat poll (backup)
- systemEvent: `"MODEL_QUEUE_DISPATCH: check queues and run pending tasks"` (backup)

---

## Mode 1: INTAKE — Step-by-Step

### Step 0 — First Run Setup

**Run this check before anything else, every INTAKE invocation:**

```
CHECK whether ${MODEL_QUEUES_DIR}/ exists and has queue files
IF no queue files exist:
  → This is the first run. Auto-configure.
  
  [1] Create directory:
      exec: mkdir -p ${MODEL_QUEUES_DIR}
  
  [2] For each MODEL_SOURCE_* in TOOLS.md:
      CREATE ${MODEL_QUEUES_DIR}/{source_name}.json:
      {
        "version": "1.0",
        "source": "{source_name}",
        "models": [list of models],
        "maxConcurrent": 1,
        "maxRetries": ${MODEL_QUEUE_MAX_RETRIES},
        "lastId": null,
        "tasks": []
      }
  
  [3] Register heartbeat entry:
      READ HEARTBEAT.md
      IF "Model Queue Dispatcher" NOT in file:
        APPEND:
        ## Model Queue Dispatcher
        Every heartbeat: check ${MODEL_QUEUES_DIR} for pending/running tasks
        - If tasks exist → run DISPATCHER mode
        - If nothing pending → HEARTBEAT_OK
  
  [4] Register backup cron job:
      CALL cron tool:
        action: "add"
        job:
          name: "Model Queue Dispatcher"
          schedule: { kind: "every", everyMs: 900000 }
          payload: { kind: "systemEvent", text: "MODEL_QUEUE_DISPATCH: check queues and run pending tasks" }
          sessionTarget: "main"
          enabled: true
  
  [5] Notify user:
      "⚙️ Model Queue initialized. N queues ready."
  
  → THEN continue with normal INTAKE steps.

IF queue files already exist:
  → Skip Step 0. Proceed to Step 1.
```

### Step 1 — Parse User Message

Parse the message to extract:

1. **Tasks**: Split by numbered lists, bullets, "然后", "and then", "next"
2. **Model/Source**: Look for model names or source keywords
3. **Dependencies**: "然后", "after that", "based on that" implies dependency on previous task
4. **Control commands**: "cancel T-XXX", "retry T-XXX", "show status"

### Step 2 — Handle Control Commands

| Command | Action |
|---------|--------|
| `cancel T-XXX` | Set status = "skipped", save, confirm |
| `retry T-XXX` | Reset status = "pending", retries = 0, save, confirm |
| `skip T-XXX` | Set status = "skipped", save, confirm |
| `show status` / `task status` | Render queue status table (see Output Templates) |
| `show queue {source}` | Show specific queue details |

### Step 3 — Determine Model Source

For each task:

```
IF user specified model explicitly (e.g., "用 qwen2.5"):
  FIND model in MODEL_SOURCE_* configs
  SET task.model = specified model
  SET task.queue = source containing that model

ELSE IF user specified source (e.g., "用远程", "send to remote"):
  FIND matching MODEL_SOURCE_*
  SET task.queue = that source
  SET task.model = first model in that source (or ask)

ELSE:
  IF DEFAULT_MODEL_SOURCE configured:
    SET task.queue = DEFAULT_MODEL_SOURCE
    SET task.model = first model in that source
  ELSE:
    ASK user: "Which model/source should handle this task?"
```

### Step 4 — Determine Dependencies

```
IF task contains dependency indicators ("然后", "after that", "based on that"):
  IF previous task in same message:
    SET task.depends_on = previous_task.id
    SET task.on_depends_fail = "block" (default)
  ELSE:
    ASK user: "This task depends on which previous task?"

IF user explicitly specified dependency ("depends on T-XXX"):
  SET task.depends_on = specified_id
```

### Step 5 — Assign Task ID

```
READ queue file for task.queue
IF queue.lastId is null:
  task.id = "T-001"
ELSE:
  PARSE number from queue.lastId (e.g., "T-005" → 5)
  INCREMENT number
  FORMAT as T-NNN (e.g., 6 → "T-006")
  task.id = formatted ID
```

### Step 6 — Build Task Object

Create task object with:
- `id`, `queue`, `model`, `description`, `goal`
- `status`: "pending" if no dependency, "waiting" if has dependency
- `priority`: 0 (default) or user-specified
- `depends_on`, `on_depends_fail`
- `retries`: 0, `maxRetries`: from config
- `added_at`: current timestamp
- All other fields: null

### Step 7 — Append to Queue

```
READ queue file for task.queue
APPEND task to queue.tasks[]
UPDATE queue.lastId = task.id
WRITE queue file
```

### Step 8 — Confirm to User

Single task:
```
📋 Added T-001 to queue [ollama-local]
Model: ollama/qwen2.5
Task: Analyze the sales data
Queue position: 1
```

Multiple tasks:
```
📋 Added 3 tasks to queue [ollama-local]:
• T-001: Analyze the sales data
• T-002: Generate report (depends on T-001)
• T-003: Send to team (depends on T-002)

Starting dispatcher now...
```

### Step 9 — Run DISPATCHER

**Immediately after confirming, run DISPATCHER mode (see below).**

Do not exit and wait for heartbeat. Tasks must start executing immediately.

---

## Mode 2: DISPATCHER — Step-by-Step

### Step 1 — Scan All Queue Files

```
LIST all *.json files in ${MODEL_QUEUES_DIR}/
FOR EACH queue file:
  READ queue data
```

### Step 2 — Check Running Tasks

For each queue:

```
running_tasks = tasks where status = "running"

FOR EACH running_task:
  IF running_task.subagent_session is set:
    CALL subagents(action="list") to check session status
    
    IF session is DONE:
      READ result from session
      SET running_task.status = "done"
      SET running_task.result = full result
      SET running_task.result_summary = extract summary
      SET running_task.completed_at = now()
      NOTIFY user: "✅ {running_task.id} done — {summary}"
    
    ELSE IF session is FAILED or ERROR:
      IF running_task.retries < running_task.maxRetries:
        INCREMENT running_task.retries
        SET running_task.status = "pending"
        LOG: "Retrying {running_task.id} (attempt {retries+1})"
      ELSE:
        SET running_task.status = "failed"
        SET running_task.completed_at = now()
        NOTIFY user: "❌ {running_task.id} failed after {retries} attempts"
    
    ELSE IF session is STILL RUNNING:
      LEAVE as-is (check again next heartbeat)
```

### Step 3 — Check Waiting Tasks

For each task with `status = "waiting"`:

```
IF task.depends_on is set:
  FIND dependency task in ANY queue (cross-queue lookup allowed)
  
  IF dependency.status == "done":
    SET task.status = "pending"
    SET task.context_input = {
      "source_task": dependency.id,
      "result_summary": dependency.result_summary,
      "result_status": dependency.result_status,
      "included_at": now()
    }
    LOG: "{task.id} dependency satisfied, ready to run"
  
  ELSE IF dependency.status in ["failed", "blocked"]:
    SWITCH task.on_depends_fail:
      CASE "block":
        SET task.status = "blocked"
        SET task.blocked_reason = "Dependency {dependency.id} failed"
        NOTIFY user: "⚠️ {task.id} blocked — dependency {dependency.id} failed"
      
      CASE "skip":
        SET task.status = "skipped"
        SET task.skipped_reason = "Dependency {dependency.id} failed"
        NOTIFY user: "⏭️ {task.id} skipped — dependency {dependency.id} failed"
      
      CASE "continue":
        SET task.status = "pending"
        SET task.context_input = {
          "warning": "Dependency {dependency.id} failed",
          "included_at": now()
        }
        LOG: "{task.id} continuing despite failed dependency"
  
  ELSE IF dependency.status in ["pending", "waiting", "running"]:
    LEAVE task.status = "waiting"
```

### Step 4 — Dispatch Pending Tasks

For each queue:

```
pending_tasks = tasks where status = "pending"
running_count = count of tasks where status = "running"

IF running_count >= queue.maxConcurrent:
  SKIP this queue (no slots available)

ELSE:
  slots_available = queue.maxConcurrent - running_count
  
  SORT pending_tasks by:
    1. priority (DESC)
    2. added_at (ASC)
  
  FOR EACH pending_task, up to slots_available:
    DISPATCH task:
      [1] BUILD subagent prompt:
          "You are executing task {task.id} for model-queue.
          
          Target Model: {task.model}
          Task: {task.description}
          Goal: {task.goal}
          
          {% if task.context_input %}
          Context from previous task {task.context_input.source_task}:
          {task.context_input.result_summary}
          {% endif %}
          
          Execute this task. When complete, report:
          1. The result (full output)
          2. A brief summary (1-2 sentences)  
          3. Status: success, partial, or failed
          4. If failed, explain why and suggest what might help
          
          Focus only on this task. Do not start other tasks."
      
      [2] CALL sessions_spawn:
          task: subagent prompt
          model: task.model (or default for queue)
          mode: "run"
          timeoutSeconds: appropriate timeout
      
      [3] UPDATE task:
          SET task.status = "running"
          SET task.subagent_session = spawned session ID
          SET task.started_at = now()
```

### Step 5 — Save All Queues

```
FOR EACH modified queue file:
  WRITE queue data to disk
```

### Step 6 — Return Appropriate Response

```
IF any notifications were sent (done/failed/blocked):
  RETURN the notifications (active heartbeat response)

ELSE IF tasks were dispatched:
  RETURN "Dispatched N tasks across M queues."

ELSE IF nothing to do (no pending, no running):
  RETURN "HEARTBEAT_OK"
```

---

## Output Templates

### Task Added
```
📋 Added {task.id} to queue [{queue}]
Model: {task.model}
{task.description}
{% if task.depends_on %}
Depends on: {task.depends_on} (block on failure)
{% endif %}
Queue position: {position}
```

### Task Completed
```
✅ {task.id} done — {task.result_summary}
Queue: {task.queue} | Duration: {duration}
```

### Task Failed
```
❌ {task.id} failed after {task.retries} attempts
Queue: {task.queue}
Error: {task.error_message}

To retry: "retry {task.id}"
```

### Queue Status
```
📊 Queue Status

[{source-1}] {pending} pending, {running} running, {done} done
  {T-XXX} 🔄 running: {description} (started {time} ago)
  {T-XXX} ⏳ pending: {description}
  {T-XXX} ⏳ waiting: {description} (depends on {T-YYY})
  {T-XXX} 🚫 blocked: {description} — {blocked_reason}

[{source-2}] {pending} pending, {running} running, {done} done
  (empty)
```

---

## A5 — Configuration Reference

### TOOLS.md Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL_QUEUES_DIR` | `~/.openclaw/model-queues/` | Directory for queue files |
| `MODEL_QUEUE_MAX_RETRIES` | `3` | Max retry attempts per task |
| `MODEL_QUEUE_ARCHIVE_DAYS` | `7` | Days before archiving completed tasks |
| `MODEL_SOURCE_*` | (required) | Model source mappings |
| `DEFAULT_MODEL_SOURCE` | (optional) | Default source when not specified |

### Queue File Structure

```json
{
  "version": "1.0",
  "source": "ollama-local",
  "models": ["ollama/llama3", "ollama/qwen2.5"],
  "maxConcurrent": 1,
  "maxRetries": 3,
  "lastId": "T-005",
  "tasks": [...]
}
```

---

## A6 — Heartbeat Integration

Heartbeat and cron setup is **automatic**. Step 0 of INTAKE mode handles this.

### HEARTBEAT.md Entry (auto-injected)

```markdown
## Model Queue Dispatcher

Every heartbeat: check ${MODEL_QUEUES_DIR} for pending/running tasks
- If tasks exist → run DISPATCHER mode (model-queue skill)
- If nothing pending → HEARTBEAT_OK
```

### Backup Cron Job (auto-registered)

```
every 15 min → systemEvent: "MODEL_QUEUE_DISPATCH: check queues and run pending tasks"
sessionTarget: main
```

---

## A7 — Edge Cases

| Situation | Behavior |
|-----------|----------|
| Model not in any MODEL_SOURCE_* | Ask user to specify source |
| Dependency cycle detected | Reject task with error message |
| Dependency in different queue | Allow (cross-queue dependencies supported) |
| Multiple dependencies | Not supported in v1 (single dependency only) |
| Task times out (subagent) | Mark as failed, trigger retry logic |
| Queue file corrupt/invalid JSON | Alert user, do not overwrite; ask to inspect |
| All tasks blocked | Notify user with suggestions |
| 20+ tasks added at once | Process in order, dispatch one at a time |
| Subagent session ID lost | Mark task as pending, re-dispatch |

---

## A8 — File Organization

```
${MODEL_QUEUES_DIR}/
  ollama-local.json
  ollama-remote.json
  cloud-nvidia.json
  archive/
    ollama-local/
      2026-03.json
    ollama-remote/
      2026-03.json
```

---

## Future Enhancements (v2)

- [ ] Multiple dependencies per task
- [ ] Task groups (batch operations)
- [ ] Priority boost for urgent tasks
- [ ] Queue pause/resume
- [ ] Task result caching
- [ ] Cross-queue result sharing
- [ ] Scheduled task execution (run at specific time)
- [ ] Task templates (reusable task definitions)
