# Queue Schema Reference

Complete documentation for the task-runner persistent queue file format.

**File path:** `${TASK_RUNNER_DIR}/task-queue.json`
(default: `~/.openclaw/tasks/task-queue.json`)

This is a single file that accumulates all tasks over time. It is never reset — only tasks older
than `archiveDays` days with terminal statuses are moved to the archive directory.

---

## Top-Level Queue Object

```json
{
  "version": "1.0",
  "maxConcurrent": 2,
  "maxRetries": 3,
  "archiveDays": 7,
  "taskRunnerDir": "~/.openclaw/tasks/",
  "lastId": "T-05",
  "tasks": [ ...task objects... ]
}
```

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `version` | string | Schema version. Current: `"1.0"` |
| `maxConcurrent` | integer | Max tasks running simultaneously. Default: `2` |
| `maxRetries` | integer | Max retry attempts before marking blocked. Default: `3` |
| `archiveDays` | integer | Days to keep terminal tasks before archiving. Default: `7` |
| `taskRunnerDir` | string | Path to the task runner directory (may use `~`). Read from TOOLS.md |
| `lastId` | string | The ID of the most recently created task (e.g., `"T-05"`). `null` if no tasks yet |
| `tasks` | array | Array of task objects (see below). Active tasks only; archived tasks live in `archive/` |

---

## Task Object

```json
{
  "id": "T-01",
  "description": "original user text for this task",
  "goal": "parsed objective in one sentence",
  "type": "info-lookup",
  "status": "pending",
  "retries": 0,
  "maxRetries": 3,
  "subagent_session": null,
  "strategies_tried": [],
  "deliverable": null,
  "deliverable_path": null,
  "blocked_reason": null,
  "user_action_required": null,
  "added_at": "2026-02-17T09:00:00Z",
  "started_at": null,
  "completed_at": null
}
```

### Task Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique task identifier. Format: `T-NN` (e.g., `T-01`, `T-12`). Never reused |
| `description` | string | Yes | Original user text for this task, verbatim or lightly cleaned |
| `goal` | string | Yes | Parsed objective in one clear sentence. Set during INTAKE |
| `type` | string | Yes | Task type (see task_types below). Set during INTAKE or DISPATCHER |
| `status` | string | Yes | Current state (see statuses below) |
| `retries` | integer | Yes | Number of execution attempts so far. Starts at `0` |
| `maxRetries` | integer | Yes | Max attempts before blocking. Copied from queue-level config at intake time |
| `subagent_session` | string\|null | No | Session ID of the subagent executing this task. `null` when not running |
| `strategies_tried` | array | Yes | List of strategy attempt objects (see below). Empty array initially |
| `deliverable` | string\|null | No | Human-readable result summary (e.g., "Gold price: $2,312/oz"). Set when done |
| `deliverable_path` | string\|null | No | File path of output artifact, if any (e.g., `~/reports/gold-notes.md`) |
| `blocked_reason` | string\|null | No | Why the task is blocked. Plain English. Set when status = `"blocked"` |
| `user_action_required` | string\|null | No | Specific steps for user to unblock the task. Set when status = `"blocked"` |
| `added_at` | ISO 8601 | Yes | When the task was added to the queue |
| `started_at` | ISO 8601\|null | No | When the task first entered `"running"` state. `null` until dispatched |
| `completed_at` | ISO 8601\|null | No | When the task reached a terminal state. `null` until done/blocked/skipped |

---

## Task Statuses

| Status | Description | Next States |
|--------|-------------|-------------|
| `pending` | Waiting to be dispatched. Initial state | `running` (dispatcher picks up), `skipped` (user cancels) |
| `running` | Subagent spawned and executing | `done` (success), `pending` (retry), `blocked` (max retries) |
| `done` | Completed successfully | Archive after `archiveDays` days |
| `blocked` | Failed after `maxRetries` attempts; needs user action | `pending` (after user says "retry T-NN") |
| `skipped` | Skipped by user request | Archive after `archiveDays` days |

**Terminal states:** `done`, `blocked`, `skipped`

---

## Task Types

| Type | Description |
|------|-------------|
| `info-lookup` | Finding or retrieving information from the web |
| `file-creation` | Creating or editing files on disk |
| `code-execution` | Running scripts or shell commands |
| `agent-delegation` | Handing off complex work to a subagent |
| `reminder-scheduling` | Setting time-based triggers or cron jobs |
| `messaging` | Sending messages to channels or people |
| `unknown` | Unclassified; dispatcher will attempt to classify before executing |

---

## `strategies_tried` Array

Each element records one execution attempt:

```json
{
  "attempt": 1,
  "strategy": "web_search",
  "tool": "web_search",
  "attempted_at": "2026-02-17T09:05:00Z",
  "result": "returned 5 results but none contained the required data",
  "verification_failure": "key term not found in any result"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `attempt` | integer | Attempt number (1, 2, 3...) |
| `strategy` | string | Name of the strategy tried (e.g., `"web_search"`, `"web_fetch"`) |
| `tool` | string | Tool used for this attempt |
| `attempted_at` | ISO 8601 | When this attempt was made |
| `result` | string | Brief description of what happened |
| `verification_failure` | string\|null | If verification failed, what failed. `null` if execution itself failed |

---

## Full Example

```json
{
  "version": "1.0",
  "maxConcurrent": 2,
  "maxRetries": 3,
  "archiveDays": 7,
  "taskRunnerDir": "~/.openclaw/tasks/",
  "lastId": "T-03",
  "tasks": [
    {
      "id": "T-01",
      "description": "research the top 5 open-source LLM frameworks",
      "goal": "Find and summarize the top 5 open-source LLM inference frameworks with pros and cons",
      "type": "info-lookup",
      "status": "done",
      "retries": 0,
      "maxRetries": 3,
      "subagent_session": "agent:main:subagent:abc123",
      "strategies_tried": [
        {
          "attempt": 1,
          "strategy": "web_search",
          "tool": "web_search",
          "attempted_at": "2026-02-17T09:10:00Z",
          "result": "found 8 relevant results covering major frameworks",
          "verification_failure": null
        }
      ],
      "deliverable": "Top 5 frameworks: Ollama, LM Studio, llama.cpp, vLLM, Hugging Face TGI. Summary in T-02 input.",
      "deliverable_path": null,
      "blocked_reason": null,
      "user_action_required": null,
      "added_at": "2026-02-17T09:00:00Z",
      "started_at": "2026-02-17T09:10:00Z",
      "completed_at": "2026-02-17T09:15:00Z"
    },
    {
      "id": "T-02",
      "description": "create a markdown comparison table at ~/reports/llm-frameworks.md",
      "goal": "Create a markdown file with a comparison table of the 5 LLM frameworks from T-01",
      "type": "file-creation",
      "status": "done",
      "retries": 0,
      "maxRetries": 3,
      "subagent_session": "agent:main:subagent:def456",
      "strategies_tried": [
        {
          "attempt": 1,
          "strategy": "write",
          "tool": "write",
          "attempted_at": "2026-02-17T09:16:00Z",
          "result": "file written successfully",
          "verification_failure": null
        }
      ],
      "deliverable": "Comparison table created with 5 frameworks and 8 evaluation criteria",
      "deliverable_path": "~/reports/llm-frameworks.md",
      "blocked_reason": null,
      "user_action_required": null,
      "added_at": "2026-02-17T09:00:00Z",
      "started_at": "2026-02-17T09:16:00Z",
      "completed_at": "2026-02-17T09:18:00Z"
    },
    {
      "id": "T-03",
      "description": "post the LLM framework summary to #ai-team channel",
      "goal": "Post a summary of the LLM framework research to the #ai-team Slack/chat channel",
      "type": "messaging",
      "status": "blocked",
      "retries": 3,
      "maxRetries": 3,
      "subagent_session": null,
      "strategies_tried": [
        {
          "attempt": 1,
          "strategy": "message tool direct",
          "tool": "message",
          "attempted_at": "2026-02-18T10:00:00Z",
          "result": "channel #ai-team not found",
          "verification_failure": null
        },
        {
          "attempt": 2,
          "strategy": "search for channel by partial name",
          "tool": "message",
          "attempted_at": "2026-02-18T10:20:00Z",
          "result": "no match for ai-team",
          "verification_failure": null
        },
        {
          "attempt": 3,
          "strategy": "list all available channels",
          "tool": "message",
          "attempted_at": "2026-02-18T10:40:00Z",
          "result": "#ai-team does not exist in configured channels",
          "verification_failure": null
        }
      ],
      "deliverable": null,
      "deliverable_path": null,
      "blocked_reason": "Channel #ai-team does not exist in the configured messaging setup",
      "user_action_required": "1. Verify the correct channel name (e.g., #ai-research or #ai-discussion)\n2. Reply 'retry T-03 use channel #correct-channel-name'",
      "added_at": "2026-02-18T09:50:00Z",
      "started_at": "2026-02-18T10:00:00Z",
      "completed_at": "2026-02-18T10:40:00Z"
    }
  ]
}
```

---

## ID Numbering Rules

- IDs always use format `T-NN` (minimum 2 digits): `T-01`, `T-02`, ..., `T-99`
- When N exceeds 99, expand to 3 digits: `T-100`, `T-101`
- IDs always increment monotonically — never reuse, never reset
- `lastId` tracks the most recently assigned ID in the queue file
- On INTAKE: read `lastId`, parse the number, add 1 per new task, update `lastId`

---

## Archive Behavior

When the dispatcher runs and finds tasks with terminal status (`done`, `blocked`, `skipped`)
where `completed_at` is older than `archiveDays` days:

1. Move those task objects to `${TASK_RUNNER_DIR}/archive/YYYY-MM.json`
2. Archive file structure is identical to the main queue file (same fields)
3. Remove archived tasks from `tasks[]` in the main queue file
4. Do NOT change `lastId` (IDs from archived tasks remain "used")

Archive filenames use `YYYY-MM` format based on the task's `completed_at` date.
