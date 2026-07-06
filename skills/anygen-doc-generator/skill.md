---
name: anygen-doc
homepage: https://www.anygen.io
description: "Generate structured documents with AnyGen AI. Uses dialogue mode to understand audience, purpose, and content before generating. Background-polls progress and auto-delivers the downloaded DOCX file without blocking the conversation."
env:
  - ANYGEN_API_KEY
requires:
  - sessions_spawn
permissions:
  network:
    - "https://www.anygen.io"
  filesystem:
    read:
      - "~/.config/anygen/config.json"
    write:
      - "~/.config/anygen/config.json"
---

# AI Document Generator - AnyGen

Create professional structured documents using AnyGen OpenAPI.

## When to Use

- User needs to create documents (specs, proposals, summaries, reports)
- User has files to upload as reference material for document generation

## Security & Permissions

**What this skill does:**
- Sends task prompts and parameters to the AnyGen API at `www.anygen.io`
- Uploads user-provided reference files to `www.anygen.io` when `--file` is specified
- Downloads generated documents (DOCX) to local disk
- Reads/writes API key config at `~/.config/anygen/config.json`

**What this skill does NOT do:**
- Does not upload files unless the user explicitly provides them via `--file`
- Does not send your API key to any endpoint other than `www.anygen.io`
- Does not modify system configuration beyond `~/.config/anygen/config.json`
- Does not run background processes or install additional software

**Bundled scripts:** `scripts/anygen.py` (Python — uses `requests`)

Review the bundled scripts before first use to verify behavior.

## Prerequisites

- Python3 and `requests`: `pip3 install requests`
- AnyGen API Key (`sk-xxx`) — [Get one](https://www.anygen.io/home) → Setting → Integration
- Configure once: `python3 scripts/anygen.py config set api_key "sk-xxx"`

> All `scripts/` paths below are relative to this skill's installation directory.

## CRITICAL: Background Poll — NEVER Block the Conversation

After creating a task, you MUST start a **background** poll process to auto-download the result, then continue the conversation normally. NEVER call `poll` in the foreground — it blocks for 3-20 minutes.

Rules:
1. Use `create` to start the task → get `task_id` and `task_url`.
2. Give the user the `task_url` for immediate online preview.
3. Launch `poll` as a **background process** to auto-download the file when ready (see Phase 4).
4. Continue the conversation normally — do NOT wait.
5. After the conversation naturally ends or the user asks about the result, check if the background poll has completed and deliver the file.

## Communication Style

When interacting with the user, communicate naturally and professionally:

1. You may refer to AnyGen as the service powering the document generation when relevant.
2. Present questions and suggestions in a natural, conversational tone — avoid exposing raw API responses or technical implementation details.
3. Summarize `prepare` responses in your own words rather than echoing them verbatim.
4. Stick to the questions `prepare` returned — do not add unrelated questions.

### Examples

Less ideal (overly technical):
- "The prepare API returned the following JSON response with status=collecting..."
- "The system's internal tool asks: who is your target audience?"

Better (natural and professional):
- "Who is the target audience for this document?"
- "Based on what you've shared, here is the plan for your document: [summary]. Should I go ahead, or would you like to adjust anything?"

## Document Workflow (MUST Follow)

For documents, you MUST go through all 4 phases. A good document needs audience, purpose, structure, scope, and content details. Users rarely provide all of these upfront.

### Phase 1: Understand Requirements

If the user provides files, you MUST handle them yourself before calling `prepare`:

1. **Read the file content yourself** using your own file reading capabilities. Extract key information (topic, data, structure) that is relevant to creating the document.
2. **Check if the file was already uploaded** in this conversation. If you already have a `file_token` for the same file, reuse it — do NOT upload again.
3. **Inform the user and get consent** before uploading. Tell them the file will be uploaded to AnyGen's server for processing. For example: "I'll upload your file to AnyGen so it can be used as reference material for the document. This may take a moment..."
4. **Upload the file** to get a `file_token` for later use in task creation.
5. **Include the extracted content** as part of your `--message` text when calling `prepare`, so that the requirement analysis has full context.

The `prepare` API does NOT read files internally. You are responsible for providing all relevant file content as text in the conversation.

```bash
# Step 1: Tell the user you are uploading, then upload the file
python3 scripts/anygen.py upload --file ./report.pdf
# Output: File Token: tk_abc123

# Step 2: Call prepare with extracted file content included in the message
python3 scripts/anygen.py prepare \
  --message "I need a technical design document based on this report. Here is the key content: [your extracted summary/content here]" \
  --file-token tk_abc123 \
  --save ./conversation.json
```

The `--file-token` parameter in `prepare` attaches the file reference to the conversation, but it does NOT extract or read the file content. You must include the relevant content as text in `--message`.

Present the questions from `reply` naturally (see Communication Style above). Then continue the conversation with the user's answers:

```bash
python3 scripts/anygen.py prepare \
  --input ./conversation.json \
  --message "The audience is engineering managers, goal is to document the auth system architecture" \
  --save ./conversation.json
```

Repeat until `status="ready"` with `suggested_task_params`.

Special cases:
- If the user provides very complete requirements and `status="ready"` on the first call, proceed directly to Phase 2.
- If the user says "just create it, don't ask questions", skip prepare and go to Phase 3 with `create` directly.
- For template/style reference files (e.g., "use this as a template"), do NOT extract content. Just upload and pass the `file_token`.

### Phase 2: Confirm with User (MANDATORY)

When `status="ready"`, `prepare` returns `suggested_task_params` containing a detailed prompt. You MUST present this to the user for confirmation before creating the task.

How to present:
1. Summarize the key aspects of the suggested plan in natural language (audience, structure, content highlights, style).
2. Ask the user to confirm or modify. For example: "Here is what I plan to create: [summary]. Should I go ahead, or would you like to change anything?"
3. NEVER auto-create the task without the user's explicit approval.

When the user requests adjustments:
1. Call `prepare` again with the user's modification as a new message, loading the existing conversation history:

```bash
python3 scripts/anygen.py prepare \
  --input ./conversation.json \
  --message "<the user's modification request>" \
  --save ./conversation.json
```

2. `prepare` will return an updated suggestion that incorporates the user's changes.
3. Present the updated suggestion to the user again for confirmation (repeat from step 1 above).
4. Repeat this confirm-adjust loop until the user explicitly approves. Do NOT skip confirmation after an adjustment.

### Phase 3: Create Task

Once the user confirms:

```bash
python3 scripts/anygen.py create \
  --operation doc \
  --prompt "<prompt from suggested_task_params, with any user modifications>" \
  --file-token tk_abc123 \
  --export-format docx
# Output: Task ID: task_xxx, Task URL: https://...
```

**Immediately tell the user:**
1. Document is being generated (takes a few minutes).
2. Give them the **Task URL** so they can preview progress online right now.
3. Tell them you will deliver the downloaded file once it's ready.

### Phase 4: Monitor and Deliver Result

> **Requires `sessions_spawn`.** If sub-agent is not available, skip to the **Fallback** section below.

#### With Sub-Agent (preferred)

Spawn a sub-agent to monitor the task in the background. Use `sessions_spawn` with the following instructions.

**Information to pass to the sub-agent** (it has NO context from this conversation):
- `task_id` — from Phase 3 output
- `task_url` — the Task URL returned by `create`
- `script_path` — absolute path to `scripts/anygen.py`

**Sub-agent instructions** (pass this as the task prompt):

```
You are a background monitor for an AnyGen document generation task.

Task ID: {task_id}
Task URL: {task_url}
Script: {script_path}

Your job:
1. Run the poll command to wait for completion and auto-download:
   python3 {script_path} poll --task-id {task_id} --output ~/.openclaw/workspace/ --media
   This will poll every 3 seconds, and automatically download the file when completed.
2. The script will output a MEDIA: line (with non-ASCII filenames automatically handled). Deliver it to the user:
   a. Send a SHORT message containing ONLY the MEDIA: line exactly as output by the script.
      This message MUST be sent as a separate message by itself — do NOT combine it with other text.
      The MEDIA: protocol will deliver the actual file to the user in their IM client.
   b. Then send a second message to the user with:
      - The Task URL ({task_url}) for online viewing/editing
      - If there is a [RESULT] Thumbnail URL: line, download the thumbnail image to a local file and show it to the user as a preview
3. If status="failed", tell the user the generation failed and provide the Task URL for reference.
4. Timeout after 20 minutes — if still not completed, tell the user the task is taking longer than expected and provide the Task URL for them to check manually.
```

Then continue the conversation normally. Do NOT wait for the sub-agent.

#### Fallback (no sub-agent)

If `sessions_spawn` is not available, tell the user something like: "I've started the generation for you. Unfortunately I'm not able to track the progress automatically in this environment — please check the link above in a few minutes to view and download your document."

## Command Reference

### prepare

```bash
python3 scripts/anygen.py prepare --message "..." [--file-token tk_xxx] [--input conv.json] [--save conv.json]
```

| Parameter | Description |
|-----------|-------------|
| --message, -m | User message text |
| --file | File path to auto-upload and attach (repeatable) |
| --file-token | File token from prior upload (repeatable) |
| --input | Load conversation from JSON file |
| --save | Save conversation state to JSON file |
| --stdin | Read message from stdin |

### create

```bash
python3 scripts/anygen.py create --operation doc --prompt "..." [options]
```

| Parameter | Short | Description |
|-----------|-------|-------------|
| --operation | -o | **Must be `doc`** |
| --prompt | -p | Content description |
| --file-token | | File token from upload (repeatable) |
| --export-format | -f | `docx` (default) / `image` |
| --language | -l | Language (zh-CN / en-US) |
| --style | -s | Style preference |

### upload

```bash
python3 scripts/anygen.py upload --file ./document.pdf
```

Returns a `file_token`. Max file size: 50MB. Tokens are persistent and reusable.

### poll

Blocks until task completes, auto-downloads the file, and prints `[RESULT]` lines.

```bash
python3 scripts/anygen.py poll --task-id task_xxx --output ./output/
```

| Parameter | Description |
|-----------|-------------|
| --task-id | Task ID from `create` |
| --output | Output directory for auto-download (default: current directory) |

### download (manual, if needed)

```bash
python3 scripts/anygen.py download --task-id task_xxx --output ./output/
```

## Error Handling

| Error | Solution |
|-------|----------|
| invalid API key | Check API Key format (sk-xxx) |
| operation not allowed | Contact admin for permissions |
| prompt is required | Add --prompt parameter |
| file size exceeds 50MB limit | Reduce file size |

## Notes

- Max task execution time: 20 minutes
- Download link valid for 24 hours
- Poll interval: 3 seconds

## Files

```
doc-generator/
├── SKILL.md              # This document
└── scripts/
    └── anygen.py         # CLI client
```
