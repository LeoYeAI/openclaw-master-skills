---
name: anygen-slide
description: "Generate an editable PowerPoint (PPTX)/Slide deck from a prompt with AnyGen. Choose styles, page count, ratio, and auto-download the PPTX file. Triggers: make PPT, create slides, slide deck, presentation, quarterly review deck."
---

# PowerPoint/Slides Generator (PPTX) - AnyGen

Generate professional slide decks from natural language prompts. Supports multiple styles, page counts, and aspect ratios. Output: auto-downloaded PPTX file + online task URL.

## When to use

| Scenario | Example Prompts |
|----------|----------------|
| Product presentation | "make a product roadmap PPT" |
| Business review | "make a quarterly review slide deck" |
| Pitch deck | "create a startup pitch deck" |
| Training material | "make a training presentation on cloud security" |

## Prerequisites

- Python3 and `requests`: `pip3 install requests`
- AnyGen API Key (`sk-xxx`) — [Get one](https://www.anygen.io/home) → Setting → Integration
- Configure once: `python3 scripts/anygen.py config set api_key "sk-xxx"`

> All `scripts/` paths below are relative to this skill's installation directory.

## Invocation Flow

### Step 1: Collect Required Information

**Required:**
1. **API Key** — `sk-xxx` format (skip if already configured)
2. **Prompt** — What the slides should cover

**Slide-specific options (ask the user):**
- **Style** — business / minimalist / tech / academic / creative / data-driven / nature / dark
- **Page count** — Brief 5-8 / Standard 10-15 / Detailed 15-25 (default: AI decides)
- **Aspect ratio** — 16:9 (projection) or 4:3 (printing)

**Optional:**
- Reference files (PDF, PNG, JPG, DOCX, PPTX, TXT) via `--file`
- Language: `zh-CN` (default) or `en-US`

### Step 2: Create task

```bash
python3 scripts/anygen.py create \
  --operation slide \
  --prompt "A presentation about the history of artificial intelligence" \
  --style "business" \
  --slide-count 12 \
  --ratio "16:9"
# → Task ID: task_abc123xyz
```

| Parameter | Short | Description |
|-----------|-------|-------------|
| --operation | -o | **Must be `slide`** |
| --prompt | -p | Content description |
| --api-key | -k | API Key (omit if configured) |
| --style | -s | Style preference |
| --slide-count | -c | Number of pages |
| --ratio | -r | 16:9 / 4:3 |
| --template | -t | PPT template |
| --language | -l | zh-CN / en-US |
| --file | | Attachment file path (repeatable) |

### Step 3: Check progress

`status` is a **non-blocking single query** — call it, get the result, return immediately.

```bash
python3 scripts/anygen.py status \
  --task-id task_abc123xyz
# → [STATUS] task_id=task_abc123xyz status=processing progress=60
```

**Progress reporting rules — you MUST follow:**

1. Call `status` every **10 seconds** to poll internally
2. Only notify the user at **milestone progress points**: 25%, 50%, 75%, 90%, and completion. Do NOT report every small change — this is a long-running task (up to 15 min)
3. Example user-facing messages at milestones:
   - 25% → "AnyGen is generating slide outline..."
   - 50% → "Content generated, now designing layout..."
   - 75% → "Styling and polishing slides..."
   - 90% → "Almost done, finalizing..."
4. **Progress may stay at the same percentage for several minutes.** This is normal — AnyGen performs deep generation (content research, layout design, style rendering) at certain stages. Do NOT assume the task is stuck. Only treat `status=failed` as an error.

### Step 4: Download file

```bash
python3 scripts/anygen.py download \
  --task-id task_abc123xyz --output ./output/
```

### Step 5: Return results to user

**Tell the user:**
- **Local file path** — from `[RESULT] Local file:` line
- **Task URL** — from `[RESULT] Task URL:` line, for online viewing/editing

**Do NOT** return `file_url` to the user. The script auto-downloads the file.

## Advanced: IM File Delivery (MEDIA: Protocol)

When running in an **IM context** (e.g., Feishu/Lark bot with OpenClaw), add `--media` to `download`:

```bash
python3 scripts/anygen.py download \
  --task-id task_abc123xyz --media
```

Send the output `MEDIA:/absolute/path/to/file` as a **separate short message** so the framework delivers the file.

## Error Handling

| Error | Solution |
|-------|----------|
| invalid API key | Check if API Key is correct |
| operation not allowed | Contact admin for permissions |
| prompt is required | Add --prompt parameter |
| task not found | Check if task_id is correct |
| Generation timeout | Recreate the task |

## Notes

- Maximum execution time per task is 15 minutes (customizable via `--max-time`)
- Download link is valid for 24 hours
- Single attachment file should not exceed 10MB
