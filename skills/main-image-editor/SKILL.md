---
name: main-image-editor
description: "Orchestrate screenshot + Chinese instruction into PSD batch edits with transaction rollback by reusing psd-automator."
command-dispatch: tool
command-tool: main_image_editor
command-arg-mode: raw
metadata:
  openclaw:
    userInvocable: true
    commandDispatch: tool
    commandTool: main_image_editor
    commandArgMode: raw
---

# main-image-editor

Orchestration layer for "main image modification" workflows:

1. Parse screenshot + Chinese instruction into structured edit tasks.
2. Convert tasks into `psd-automator` task JSON.
3. Execute serially with transaction rollback (rollback all on any failure).
4. Reuse `psd-automator` export + bundle output.

## Usage

```bash
node skills/main-image-editor/scripts/run-main-image-editor.js \
  --request skills/main-image-editor/examples/request.sample.json \
  --index ~/.openclaw/psd-index.json
```

Dry-run or force execute:

```bash
node skills/main-image-editor/scripts/run-main-image-editor.js \
  --request skills/main-image-editor/examples/request.sample.json \
  --dry-run
```

```bash
node skills/main-image-editor/scripts/run-main-image-editor.js \
  --request skills/main-image-editor/examples/request.sample.json \
  --force
```

## Request payload

`request` JSON supports:

- `text`: Chinese requirement text
- `screenshotPath`: screenshot path (used for match + audit)
- `confidenceThreshold`: optional (default `0.8`)
- `tasks`: optional pre-parsed tasks (skip regex parsing when provided)
- `execution`: optional runtime controls (`indexPath`, `dryRun`, `force`)

When `fileHint` is missing, parser will try to extract `.psd/.psb` filename from:

1. request `text`
2. OCR text from `screenshotPath` (local `tesseract` command or macOS Vision OCR fallback)

## Failure policy

- Default policy is `rollback_all`.
- Any single PSD failure restores all touched PSD files from transaction backups.
- Temporary outputs generated in the failed run are cleaned up before returning.
