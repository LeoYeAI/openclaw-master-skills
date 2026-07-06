---
name: anygen-storybook
homepage: https://www.anygen.io
description: "Create storybook-style visuals with AnyGen AI. Uses dialogue mode to understand narrative, style, and audience before generating. Supporting Nano Banana pro and Nano Banana 2. Triggers: storybook, visual narrative, creative storybook, visual story."
env:
  - ANYGEN_API_KEY
permissions:
  network:
    - "https://www.anygen.io"
  filesystem:
    read:
      - "~/.config/anygen/config.json"
    write:
      - "~/.config/anygen/config.json"
---

# AnyGen Storybook / Creative Generator

Create storybook-style visuals for narratives and slides using AnyGen OpenAPI. Powered by Nano Banana pro and Nano Banana 2. Output: online task URL for viewing.

## When to Use

- User needs to create a storybook, visual narrative, or creative visuals
- User has files to upload as reference material for storybook generation

## Security & Permissions

**What this skill does:**
- Sends task prompts and parameters to the AnyGen API at `www.anygen.io`
- Uploads user-provided reference files to `www.anygen.io` when `--file` is specified
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

## Communication Style

When interacting with the user, communicate naturally and professionally:

1. You may refer to AnyGen as the service powering the storybook generation when relevant.
2. Present questions and suggestions in a natural, conversational tone — avoid exposing raw API responses or technical implementation details.
3. Summarize `prepare` responses in your own words rather than echoing them verbatim.
4. Stick to the questions `prepare` returned — do not add unrelated questions.

### Examples

Less ideal (overly technical):
- "The prepare API returned the following JSON response with status=collecting..."

Better (natural and professional):
- "What story or narrative should the storybook depict?"
- "Based on what you've shared, here is the storybook plan: [summary]. Should I go ahead, or would you like to adjust anything?"

## Storybook Workflow (MUST Follow)

For storybooks, you MUST go through all 4 phases. A good storybook needs clear narrative, visual style, and audience. Users rarely provide all of these upfront.

### Phase 1: Understand Requirements

If the user provides files, you MUST handle them yourself before calling `prepare`:

1. **Read the file content yourself** using your own file reading capabilities. Extract key information (narrative, scenes, characters) that is relevant to creating the storybook.
2. **Check if the file was already uploaded** in this conversation. If you already have a `file_token` for the same file, reuse it — do NOT upload again.
3. **Inform the user and get consent** before uploading. Tell them the file will be uploaded to AnyGen's server for processing.
4. **Upload the file** to get a `file_token` for later use in task creation.
5. **Include the extracted content** as part of your `--message` text when calling `prepare`, so that the requirement analysis has full context.

The `prepare` API does NOT read files internally. You are responsible for providing all relevant file content as text in the conversation.

```bash
# Step 1: Tell the user you are uploading, then upload the file
python3 scripts/anygen.py upload --file ./script.pdf
# Output: File Token: tk_abc123

# Step 2: Call prepare with extracted file content included in the message
python3 scripts/anygen.py prepare \
  --message "I need a storybook for a product demo video. Here is the script: [your extracted summary/content here]" \
  --file-token tk_abc123 \
  --save ./conversation.json
```

Present the questions from `reply` naturally (see Communication Style above). Then continue the conversation with the user's answers:

```bash
python3 scripts/anygen.py prepare \
  --input ./conversation.json \
  --message "The visual style should be modern and clean, targeting tech-savvy users" \
  --save ./conversation.json
```

Repeat until `status="ready"` with `suggested_task_params`.

Special cases:
- If the user provides very complete requirements and `status="ready"` on the first call, proceed directly to Phase 2.
- If the user says "just create it, don't ask questions", skip prepare and go to Phase 3 with `create` directly.

### Phase 2: Confirm with User (MANDATORY)

When `status="ready"`, `prepare` returns `suggested_task_params` containing a detailed prompt. You MUST present this to the user for confirmation before creating the task.

How to present:
1. Summarize the key aspects of the suggested plan in natural language (narrative, visual style, frames, audience).
2. Ask the user to confirm or modify. For example: "Here is the storybook plan: [summary]. Should I go ahead, or would you like to adjust anything?"
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
  --operation storybook \
  --prompt "<prompt from suggested_task_params, with any user modifications>" \
  --file-token tk_abc123
# Output: Task ID: task_xxx, Task URL: https://...
```

**Immediately tell the user:**
1. Storybook is being generated (takes a few minutes).
2. Give them the **Task URL** so they can check progress online.

### Phase 4: Return Results

**No file download** for storybook. When the task completes, return the **Task URL** for online viewing.

```bash
python3 scripts/anygen.py poll --task-id task_xxx
```

**Tell the user:**
- **Task URL** — for viewing and editing the storybook online

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
python3 scripts/anygen.py create --operation storybook --prompt "..." [options]
```

| Parameter | Short | Description |
|-----------|-------|-------------|
| --operation | -o | **Must be `storybook`** |
| --prompt | -p | Storybook description |
| --file-token | | File token from upload (repeatable) |
| --language | -l | Language (zh-CN / en-US) |
| --style | -s | Style preference |

### upload

```bash
python3 scripts/anygen.py upload --file ./document.pdf
```

Returns a `file_token`. Max file size: 50MB. Tokens are persistent and reusable.

## Error Handling

| Error | Solution |
|-------|----------|
| invalid API key | Check API Key format (sk-xxx) |
| operation not allowed | Contact admin for permissions |
| prompt is required | Add --prompt parameter |
| file size exceeds 50MB limit | Reduce file size |

## Notes

- Max task execution time: 20 minutes
- Results are viewable online at the task URL
- Powered by Nano Banana pro and Nano Banana 2
- Poll interval: 3 seconds
