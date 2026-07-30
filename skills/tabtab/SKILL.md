---
name: tabtab
description: |
  Use TabTab to run AI-powered tasks in a sandboxed multi-agent environment. Supported capabilities:
  - General agent: open-ended tasks, writing, research, summarisation
  - Data analysis: upload CSV / Excel files, run analytics, generate insights
  - Data collection: web scraping and browser automation to collect structured data
  - Chart generation: produce charts and visualisations from data
  - Deep research: long-form research with web search and synthesised reports
  - Database Q&A: natural-language to SQL queries against connected databases
  - Slide generation: create PowerPoint presentations
  - Web / HTML generation: produce web pages or UI prototypes

  Interact via REST API: create tasks, poll status, stream event logs, terminate tasks, and download sandbox output.
metadata:
  category: integration,automation,api,data-analysis,research,scraping
  required_env: TABTAB_API_KEY
  optional_env: TABTAB_BASE_URL
  dependencies: curl,jq,stat
---

# TabTab Skill

## Overview

The TabTab OpenPlatform exposes REST endpoints under `/open/apis/v1/` that let you drive TabTab's multi-agent platform programmatically. Every request must carry an API Key in the `Authorization` header.

```
Authorization: Bearer sk-<32-hex-chars>
```

The API Key is obtained from the **KMS** page(https://tabtabai.com/api-key) in TabTab settings and stored as environment variable `TABTAB_API_KEY`.

---

## Configuration — Set environment variables

### Recommended: write to `scripts/env` (persists across sessions, not in shell history)

```bash
cat > "$(dirname "$0")/scripts/env" <<'EOF'
TABTAB_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
TABTAB_BASE_URL="https://tabtabai.com"   # optional
EOF
chmod 600 "$(dirname "$0")/scripts/env"
```

All scripts automatically source `scripts/env` on startup if the file exists — no further setup needed.

> **Security:** `chmod 600` ensures only you can read the file. Add `scripts/env` to `.gitignore` to prevent accidental commits:
> ```bash
> echo "skills/tabtab/scripts/env" >> .gitignore
> ```

### Alternative: export in shell session (lost on terminal close)

```bash
export TABTAB_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
export TABTAB_BASE_URL="https://tabtabai.com"  # optional
```

> **Warning:** Commands typed with the key inline (e.g. `export TABTAB_API_KEY="sk-..."`) are saved to shell history (`.bash_history` / `.zsh_history`). Prefer the `scripts/env` file approach above, or set the key via a password manager / secrets tool that avoids writing to history.

### Verify configuration

```bash
echo "BASE_URL : ${TABTAB_BASE_URL:-https://tabtabai.com}"
echo "API_KEY  : ${TABTAB_API_KEY:0:8}…"  # print only first 8 chars for safety

# Verify API key is valid before proceeding — stop if this fails
bash scripts/hello.sh
```

| Variable          | Required | Description                                               |
| ----------------- | -------- | --------------------------------------------------------- |
| `TABTAB_API_KEY`  | ✅        | API Key in `sk-…` format obtained from KMS page           |
| `TABTAB_BASE_URL` | ❌        | Base URL of TabTab instance (default: `https://tabtabai.com`) |

If `TABTAB_API_KEY` is empty, all scripts will immediately exit with an error.

### Required tools

The scripts depend on the following tools — confirm they are installed from trusted packages:

| Tool   | Purpose                                                             |
| ------ | ------------------------------------------------------------------- |
| `curl` | HTTP requests to the API                                            |
| `jq`   | JSON parsing and transformation                                     |
| `stat` | File size check before upload (`upload-files.sh`) |

---

---

## Step 0 — Verify connectivity

Check API Key validity before proceeding:

```bash
bash scripts/hello.sh
```

Expected (200):

```json
{
  "message": "Hello from TabTab OpenPlatform!",
  "timestamp": "2026-03-09T10:00:00+00:00",
  "user_id": "<internal-user-id>"
}
```

If response is `401`, the key is missing, revoked, or expired — stop and report error to user.

---

## Step 1 — Upload files (optional)

If your task requires file inputs (e.g., analyzing a spreadsheet, processing a PDF, or extracting data from images), upload them first:

### Upload multiple files (batch)

```bash
FILES_INFO=$(TABTAB_FILES="file1.pdf file2.png data.xlsx" bash scripts/upload-files.sh)
echo "$FILES_INFO"
```

### File restrictions

| Restriction        | Value                                                                                                                                                                                                   |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Max file size      | 50MB per file                                                                                                                                                                                           |
| Max files per task | 20 files                                                                                                                                                                                                |
| Supported types    | PDF, Word (.doc, .docx), Excel (.xls, .xlsx), PowerPoint (.ppt, .pptx), Text (.txt, .md), Images (.jpg, .jpeg, .png, .gif, .webp, .bmp, .svg, .tiff, .tif, .ico), Archives (.zip, .rar, .7z, .tar, .gz) |

**Note:** MIME type validation is lenient. The primary validation is based on file extension. This accommodates variations in MIME type reporting across different browsers and systems.

---

## Step 2 — Create a task

Submit a new task and get back a `task_id` immediately. The task is queued for agent execution; you will poll for its result in the next step.

### Create task with files (using scripts)

```bash
# First upload files
FILES_INFO=$(TABTAB_FILES="report.pdf chart.png" bash scripts/upload-files.sh)
FILES_JSON=$(echo "$FILES_INFO" | jq -c '.files')

# Then create task with files
TASK_ID=$(TABTAB_MESSAGE="Analyze the attached documents" \
  TABTAB_MODE="data_analysis" \
  TABTAB_FILES="$FILES_JSON" \
  bash scripts/create-task.sh)
```

### Create task without files

```bash
TASK_ID=$(TABTAB_MESSAGE="Research quantum computing trends" \
  TABTAB_MODE="deep_research" \
  bash scripts/create-task.sh)
```

### Request fields

| Field      | Type   | Required | Description                                             |
| ---------- | ------ | -------- | ------------------------------------------------------- |
| `message`  | string | ✅       | Initial user prompt — task goal                         |
| `mode`     | string | ✅       | Execution strategy (see table below)                    |
| `run_mode` | string | ❌       | `agent` (default) or `chat`                             |
| `params`   | object | ❌       | Extra parameters, e.g. `{"output": "report"}`           |
| `files`    | array  | ❌       | List of uploaded files (only effective in `agent` mode) |

### `mode` values

| Mode            | When to use                           |
| --------------- | ------------------------------------- |
| `general`       | Open-ended tasks, research, writing   |
| `data_analysis` | CSV / Excel / database analytics      |
| `deep_research` | Long-form research with web search    |
| `data_collect`  | Structured data scraping / collection |
| `html`          | Web page / UI generation              |
| `ppt`           | Slide deck generation                 |
| `charts`        | Chart / visualisation generation      |
| `chat_db`       | Natural language to SQL               |
| `flash`         | Fast single-step tasks                |

### Expected response (201)

```json
{
  "status": "pending",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## Step 3 — Poll task status

Poll until `status` leaves `pending` / `running`:

```bash
STATUS=$(TABTAB_TASK_ID="$TASK_ID" bash scripts/poll-task.sh)
echo "Final status: $STATUS"
```

For manual polling:

```bash
while true; do
  STATUS=$(TABTAB_TASK_ID="$TASK_ID" bash scripts/get-status.sh)
  echo "status: $STATUS"

  case "$STATUS" in
    completed | failed | cancelled) break ;;
    hitl)
      echo "Task is waiting for human input — check the TabTab UI."
      break
      ;;
  esac

  sleep 5
done
```

### Status lifecycle

```
pending → running → completed
                  ↘ failed
                  ↘ cancelled
                  ↘ hitl  (waiting for user action in UI)
```

### Response fields

| Field            | Description                                   |
| ---------------- | --------------------------------------------- |
| `status`         | Current task status                           |
| `status_message` | Human-readable detail (non-empty on `failed`) |

---

## Step 4 — Retrieve event log

Fetch all events for a completed (or still-running) task to inspect what the agent did:

```bash
# Get all events — stdout is the saved file path
EVENTS_FILE=$(TABTAB_TASK_ID="$TASK_ID" bash scripts/get-events.sh)
jq '.events[].event_type' "$EVENTS_FILE"

# Custom output path
EVENTS_FILE=$(TABTAB_TASK_ID="$TASK_ID" \
  TABTAB_EVENTS_FILE=/tmp/my-events.json \
  bash scripts/get-events.sh)

# Get incremental events (streaming-style)
LAST_EVENT_ID=""
while true; do
  EVENTS_FILE=$(TABTAB_TASK_ID="$TASK_ID" \
    TABTAB_FROM_EVENT_ID="$LAST_EVENT_ID" \
    bash scripts/get-events.sh)

  # Update cursor — read from the saved file
  NEW_LAST=$(jq -r '.events[-1].event_id // empty' "$EVENTS_FILE")
  [ -n "$NEW_LAST" ] && LAST_EVENT_ID="$NEW_LAST"

  # Stop when task is done
  STATUS=$(TABTAB_TASK_ID="$TASK_ID" bash scripts/get-status.sh | jq -r '.status')
  case "$STATUS" in completed | failed | cancelled) break ;; esac

  sleep 3
done
```

### Key event types

| `event_type`          | Meaning                                              |
| --------------------- | ---------------------------------------------------- |
| `user_input`          | Original user prompt                                 |
| `agent_state_change`  | Agent phase transition (planning → executing → done) |
| `tool_call_item`      | A complete tool call with input + output             |
| `message_output_item` | Agent text output / final answer                     |
| `think_output_item`   | Agent internal reasoning (if thinking mode enabled)  |
| `token_usage`         | LLM token consumption for one step                   |
| `task_final_usage`    | Aggregate token + tool usage for the whole task      |
| `hitl_operation`      | Human-in-the-loop pause/resume event                 |

---

## Step 5 — Download sandbox output

Download the working directory of a task as a ZIP file:

```bash
# Download entire sandbox
OUT=$(TABTAB_TASK_ID="$TASK_ID" bash scripts/download.sh)
echo "Saved to: $OUT"

# Download a specific sub-directory only
OUT=$(TABTAB_TASK_ID="$TASK_ID" TABTAB_DIR="output" \
  TABTAB_OUT="/workspace/result.zip" \
  bash scripts/download.sh)
echo "Saved to: $OUT"
```

The response is a `Content-Type: application/zip` streaming file.

---

## Step 6 — Terminate a running task (optional)

Send a stop signal to cancel a running task:

```bash
TABTAB_TASK_ID="$TASK_ID" bash scripts/terminate-task.sh
```

The signal is **asynchronous** — poll `status` until it becomes `cancelled`.

---

## Helper scripts

The skill ships ready-to-use shell scripts under `scripts/`. Use these scripts for most operations — they handle authentication, JSON parsing, and error handling automatically.

### Quick reference

| Script              | Purpose                               |
| ------------------- | ------------------------------------- |
| `hello.sh`          | Test API connectivity                 |
| `upload-files.sh`   | Upload multiple files in batch        |
| `create-task.sh`    | Create a new task                     |
| `list-tasks.sh`     | List all tasks with pagination        |
| `get-status.sh`     | Get current status of a task          |
| `get-events.sh`     | Get event log for a task              |
| `poll-task.sh`      | Poll until task finishes (blocking)   |
| `download.sh`       | Download sandbox output as ZIP        |
| `terminate-task.sh` | Cancel a running task                 |

---

## Complete end-to-end example (reference)

This example shows the complete flow using both scripts and direct curl commands (for reference). For actual usage, prefer the scripts shown above.

```bash
# ── Config ─────────────────────────────────────────────
# Set these in your shell session before running (never store secrets in a file):
# export TABTAB_API_KEY="sk-..."
# export TABTAB_BASE_URL="https://tabtabai.com"  # optional
BASE="${TABTAB_BASE_URL:-https://tabtabai.com}"
KEY="$TABTAB_API_KEY"

# ── 0. Verify ──────────────────────────────────────────
bash scripts/hello.sh

# ── 1. Upload files ───────────────────────────────────
FILES_INFO=$(TABTAB_FILES="report.pdf chart.png" bash scripts/upload-files.sh)
FILES_JSON=$(echo "$FILES_INFO" | jq -c '.files')

# ── 2. Create task with files ───────────────────────
TASK_ID=$(TABTAB_MESSAGE="Analyze the sales data in attachments and generate trend report" \
  TABTAB_MODE="data_analysis" \
  TABTAB_FILES="$FILES_JSON" \
  bash scripts/create-task.sh)
echo "Created task: $TASK_ID"

# ── 3. Poll ────────────────────────────────────────────
STATUS=$(TABTAB_TASK_ID="$TASK_ID" bash scripts/poll-task.sh)

# ── 4. Download output ─────────────────────────────────
[ "$STATUS" = "completed" ] \
  && TABTAB_TASK_ID="$TASK_ID" bash scripts/download.sh > /dev/null 2>&1 \
  && echo "Download complete"
```

---

## Error handling

All endpoints return a consistent error body on failure:

```json
{
  "code": 401,
  "err_code": "30001",
  "message": "unauthorized. 30001",
  "status": "error"
}
```

| HTTP  | `err_code` | Meaning                                          |
| ----- | ---------- | ------------------------------------------------ |
| `400` | `400`      | Invalid file type or size exceeds limit          |
| `401` | `30000`    | API Key missing or invalid format                |
| `401` | `30001`    | API Key revoked                                  |
| `401` | `30002`    | API Key expired                                  |
| `403` | `403`      | Task belongs to a different user                 |
| `404` | `404`      | Task not found                                   |
| `500` | `50000`    | Internal server error — retry or contact support |

Always check the HTTP status code and `err_code` before proceeding. Do **not** retry `401`/`403`/`404` errors automatically — they require user action.

---

## Best Practices

1. **Always use scripts**: They handle authentication, JSON parsing, and error handling automatically
2. **Verify connectivity first**: Run `bash scripts/hello.sh` after setting credentials — if it fails, stop and fix the key before proceeding
3. **Export env vars in your shell session**: Set `TABTAB_API_KEY` (and optionally `TABTAB_BASE_URL`) via `export` before using any script. Never store secrets in plain-text files inside the skill directory.
4. **Check response codes**: Scripts return proper exit codes; check `$?` after each call
5. **Capture stderr for progress**: Scripts write progress to stderr, output to stdout for capture
6. **Use poll-task.sh for blocking**: It waits until completion, simpler than manual polling loops
