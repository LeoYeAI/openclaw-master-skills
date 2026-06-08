# SDK / CLI API Reference

Quick reference for `scripts/stitch.mjs`.

## Commands

| Command | Args | Flags | Description |
|---|---|---|---|
| `projects` | — | — | List all projects |
| `create` | `"title"` | — | Create new project |
| `info` | `<project-id>` | — | Project details + screen list |
| `generate` | `<project-id> "prompt"` | `--device --model` | Generate new screen |
| `edit` | `<screen-id> "prompt"` | `--project --device --model` | Edit existing screen |
| `variants` | `<screen-id> "prompt"` | `--project --count --range --aspects --device --model` | Generate variants |
| `html` | `<screen-id>` | `--project` | Download HTML |
| `image` | `<screen-id>` | `--project` | Download screenshot |
| `export` | `<screen-id>` | `--project` | Download HTML + screenshot |

## Flags

| Flag | Values | Default |
|---|---|---|
| `--device` | `desktop` `mobile` `tablet` `agnostic` | SDK default |
| `--model` | `pro` (GEMINI_3_PRO) `flash` (GEMINI_3_FLASH) | SDK default |
| `--project` | project ID | from `latest-screen.json` |
| `--count` | `1`–`5` | `3` |
| `--range` | `refine` `explore` `reimagine` | `explore` |
| `--aspects` | `layout,color_scheme,images,text_font,text_content` (comma-sep) | all |

## Output (stdout)

All commands output JSON:
```json
{ "ok": true, "projectId": "...", "screenId": "...", "runDir": "...", "artifacts": [...] }
```

Errors exit with code 1 and print to stderr.

## Artifacts

Saved to `runs/<YYYYMMDD-HHmmss>-<operation>-<slug>/`:
- `screen.html` — Full HTML/CSS
- `screen.png` — Screenshot
- `variant-N.html` / `variant-N.png` — For variants
- `result.json` — Metadata

## State File

`latest-screen.json` (skill root):
```json
{ "projectId": "...", "screenId": "...", "operation": "generate", "timestamp": "..." }
```

Automatically updated by `generate`, `edit`, `variants`. Read by `edit`, `variants`, `html`, `image`, `export` when `--project` not given.

## SDK Background

The CLI uses `@google/stitch-sdk` v0.0.3 via raw `stitch.callTool()` calls.
Backend: `stitch.googleapis.com/mcp` (JSON-RPC over HTTP).
Auth: `STITCH_API_KEY` → `X-Goog-Api-Key` header.

MCP Tools called directly:
- `list_projects`, `create_project`, `get_project`
- `generate_screen_from_text` → response: `outputComponents[0].design.screens[0]`
- `edit_screens`, `generate_variants` → same response structure
- `list_screens`, `get_screen`
- `htmlCode` and `screenshot` fields are `{downloadUrl, mimeType, name}` objects
