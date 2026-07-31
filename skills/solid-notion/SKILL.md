---
name: solid-notion
description: "Read, edit, and write Notion pages as Markdown using the solid-notion CLI. Use when pulling Notion content, editing pages, managing changesets, submitting edits, restoring changes, or setting up Notion API authentication. Keywords: solid-notion, Notion, Notion API, markdown, pull, edit, write, submit, restore, changeset, notion page, notion block."
metadata:
  author: DZ Chen
  version: "0.1"
---

# solid-notion CLI Guide

`solid-notion` is a CLI for reading, editing, and writing Notion pages as Markdown with local reversible changesets.

---

## 0. Installation

For normal usage (published package):

```bash
npm install -g solid-notion
solid-notion --version
```

For local development from source:

```bash
pnpm install
pnpm build
```

---

## 1. Authentication Setup

Before using any command that talks to Notion, a token must be configured.

### Getting a Notion Token

Create a Notion integration to get an API token:

1. Visit [https://www.notion.so/profile/integrations/internal](https://www.notion.so/profile/integrations/internal)
2. Click "New integration" and give it a name
3. Copy the "Internal Integration Token"
4. Share your pages with this integration (via page "Share" settings)

### Check current auth status

```bash
solid-notion auth status --json
```

Returns:

```json
{
  "ok": true,
  "profile": "default",
  "config_path": "...",
  "token_present": true,
  "token_fingerprint": "a1b2c3d4",
  "token_valid": null
}
```

If `token_present` is `false`, run init first.

### Save a token (agent-recommended method)

```bash
printf "%s" "$NOTION_TOKEN" | solid-notion init --token-stdin --json
```

Returns on success:

```json
{
  "ok": true,
  "action": "init",
  "profile": "default",
  "config_path": "...",
  "token_saved": true,
  "overwritten": false,
  "ignored_inputs": [],
  "dry_run": false
}
```

Other token input methods (in precedence order):

| Method | Flag | Notes |
|--------|------|-------|
| Direct | `--token <value>` | Visible in `ps` / shell history |
| Stdin | `--token-stdin` | **Recommended** for agents |
| JSON | `--input-json '{"token":"..."}'` | Useful for structured protocols |

Additional flags:

| Flag | Effect |
|------|--------|
| `--json` | Machine-readable JSON output only |
| `--dry-run` | Preview without writing |
| `--force` | Overwrite existing token |
| `--profile <name>` | Use a named profile (default: `"default"`) |

### Remove a token

```bash
solid-notion auth logout --json
```

---

## 2. Command Reference

### 2.1 Browse

#### List locally pulled pages

```bash
solid-notion ls
solid-notion ls --json
```

Lists all pages that have been pulled to `$SOLID_NOTION_HOME/`. Does **not** call the Notion API.

Default output: tab-separated `<pulled_at>\t<page_id>\t<title>`, sorted newest first.

JSON output (`--json`): array of objects with `page_id`, `title`, `pulled_at`, `path`.

#### List all pages (remote)

```bash
solid-notion pages
```

Output: tab-separated lines of `<last_edited>\t<page_id>\t<title>`.

#### Search pages

```bash
solid-notion search <query>
```

Output: same tab-separated format as `pages`.

### 2.2 Read

#### Show a page (non-recursive, stdout)

```bash
solid-notion show page <page_id_or_name> --format markdown
solid-notion show page <page_id_or_name> --format json
```

`<page_id_or_name>` can be a UUID or a page title. Default format: `markdown`.

#### Show a block (JSON only)

```bash
solid-notion show block <block_id> --format json
```

#### Pull a page to local files

```bash
solid-notion pull page <page_id_or_name> --format markdown --outdir ./output
```

Options:

| Flag | Default | Description |
|------|---------|-------------|
| `--format <format>` | `json` | `json` or `markdown` |
| `--outdir <dir>` | `$SOLID_NOTION_HOME/<page_id>` | Output directory |
| `--no-local-images` | (images downloaded) | Skip downloading images |
| `--no-local-videos` | (videos downloaded) | Skip downloading videos |
| `--no-recursive` | (recursive) | Only first-level blocks |

Outputs the path of the written file.

If the page was already pulled locally, running `pull page` again fetches the latest content from Notion and overwrites local output files in that directory.

#### Pull a block to local file

```bash
solid-notion pull block <block_id> --outdir ./output
```

Options: `--outdir <dir>`, `--no-recursive`

### 2.3 Edit and Write

All edit/write/submit commands require a **strict Notion page ID** (UUID format like `aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee`). Page names are NOT accepted.

#### Apply a JSON patch

Pipe a JSON patch object to stdin:

```bash
echo '{"ops": [...]}' | solid-notion edit <page_id>
```

Also accepts a markdown file path (`notion-page-<uuid>.md`) to resolve the page ID.

**CRITICAL: Valid Patch Schema**

The patch object must have exactly these keys: `ops` (array) and `notes` (string). No other keys allowed.

```json
{
  "ops": [
    { "op": "replace_block_text", "block_id": "...", "new_markdown": "...", "reason": "..." },
    { "op": "append_blocks", "parent_block_id": "...", "blocks": [...], "reason": "..." },
    { "op": "set_props", "page_id": "...", "set": {...}, "reason": "..." }
  ],
  "notes": "optional notes"
}
```

**Three allowed operation types:**

##### `replace_block_text`

Replaces rich_text content of a block. Supported block types:

`paragraph`, `heading_1`, `heading_2`, `heading_3`, `bulleted_list_item`, `numbered_list_item`, `to_do`, `quote`, `callout`

```json
{
  "op": "replace_block_text",
  "block_id": "block-uuid",
  "new_markdown": "## New heading",
  "reason": "Clarified section title"
}
```

##### `append_blocks`

Appends new blocks under a parent block.

- Most block types need `type` + `rich_text_md`
- `divider` needs only `type`
- `code` supports optional `language` (defaults to `plain text`)

```json
{
  "op": "append_blocks",
  "parent_block_id": "parent-uuid",
  "blocks": [
    { "type": "paragraph", "rich_text_md": "New paragraph content" },
    { "type": "heading_2", "rich_text_md": "New section" }
  ],
  "reason": "Added conclusion section"
}
```

Allowed block types:

- `paragraph`, `heading_1`, `heading_2`, `heading_3`
- `bulleted_list_item`, `numbered_list_item`, `to_do`, `quote`, `callout`
- `code`, `divider`

##### `set_props`

Updates page properties (title, rich_text, number, checkbox, select, multi_select, date).

```json
{
  "op": "set_props",
  "page_id": "page-uuid",
  "set": {
    "Status": { "type": "select", "name": "Done" },
    "Priority": { "type": "number", "value": 3 },
    "Done": { "type": "checkbox", "value": true },
    "Tags": { "type": "multi_select", "names": ["urgent", "important"] },
    "Due Date": { "type": "date", "start": "2026-03-02", "end": null },
    "Title": { "type": "title", "md": "New page title" },
    "Notes": { "type": "rich_text", "md": "Some notes" }
  },
  "reason": "Updated status to Done"
}
```

**Property value types:**

| Type | Shape | Example |
|------|-------|---------|
| `number` | `{ "type": "number", "value": 42 }` | - |
| `checkbox` | `{ "type": "checkbox", "value": true }` | - |
| `select` | `{ "type": "select", "name": "Option" }` | - |
| `multi_select` | `{ "type": "multi_select", "names": ["A", "B"] }` | - |
| `date` | `{ "type": "date", "start": "2026-03-02", "end": null }` | end optional |
| `title` | `{ "type": "title", "md": "markdown" }` | - |
| `rich_text` | `{ "type": "rich_text", "md": "markdown" }` | - |

#### Write workspace changes back to Notion

```bash
solid-notion write <page_id>
```

Reads the workspace files (`page.md`, `.original.md`), replaces the page content in Notion, creates a changeset, and cleans up the workspace.

#### Submit pending edits with rollback

```bash
solid-notion submit <page_id> -m "description of changes"
```

**CRITICAL: How submit works**

`submit` consumes **pending edit logs** (created by previous `edit` commands) and applies them to Notion with transaction-like semantics:

1. **Phase 0: Load** — Reads all edit log files from `edit-logs/<page_id>/` that don't have `.submitted` markers
2. **Phase 1: Prepare** — Fetches before-snapshots (current block content, property values) so rollback is possible
3. **Phase 2: Apply** — Applies ops sequentially to Notion
4. **Phase 3: Finalize** — On success, saves commit to `versions/`. On failure, rolls back already-applied ops using before-snapshots.

**Exit statuses:**

| `status` | Meaning | `ok` |
|----------|---------|------|
| `pushed` | All ops applied successfully | `true` |
| `nothing_to_submit` | No pending edits found | `false` |
| `rolled_back` | Apply failed but rollback succeeded | `false` |
| `failed_needs_reconcile` | Apply failed AND rollback partially failed | `false` |

**Submit result format:**

```json
{
  "ok": true,
  "commit_id": "cmt_20260302_143022",
  "notion_id": "3d1b-...",
  "status": "pushed",
  "applied_ops": 3,
  "included_edits": 2
}
```

**Best practices:**
- Always run `submit` after `edit` operations to publish changes
- If submit returns `rolled_back`, the page is back to original state — no manual cleanup needed
- If submit returns `failed_needs_reconcile`, manual intervention may be required
- The `-m` (message) flag is **required**

### 2.4 Create New Pages

**CRITICAL: Use the `new` command to create Notion pages programmatically**

The `new` command creates a new page under a parent (page or database) with **metadata only** (title, icon, cover, props) via stdin as JSON. After creation, the page is **automatically pulled** locally as markdown. To add content (blocks), use the existing `edit` + `submit` workflow.

#### Create a new page

```bash
echo '{"title":"My New Page","notes":""}' | solid-notion new --parent <parent_id> -m "Create page" --json
```

**Required flags:**
- `--parent <parent_id>` — Parent page or database ID
- `-m, --message <message>` — Commit message

**Optional flags:**
- `--database` — Parent is a database (creates as database entry)
- `--json` — Output JSON only
- `--dry-run` — Validate without creating

**CRITICAL: Valid Payload Schema**

The JSON payload via stdin must have exactly these keys:

```json
{
  "title": "Page Title",
  "icon": { "type": "emoji", "emoji": "📝" },
  "cover": { "type": "external", "url": "https://..." },
  "props": {
    "Status": { "type": "select", "name": "In Progress" }
  },
  "notes": "optional notes about this creation"
}
```

**Required fields:**
- `title` (string, non-empty)
- `notes` (string, can be empty)

**Optional fields:**
- `icon` — `{ "type": "emoji", "emoji": "🎉" }` or `{ "type": "external", "url": "..." }`
- `cover` — `{ "type": "external", "url": "..." }`
- `props` — Page properties (database entries), same types as `set_props` plus `url`, `email`, `phone_number`

**No `blocks` field.** Content is added via `edit` + `submit` after creation.

**Property types for `props` (database entries):**

All types from `set_props` plus:
- `url`: `{ "type": "url", "value": "https://..." }`
- `email`: `{ "type": "email", "value": "user@example.com" }`
- `phone_number`: `{ "type": "phone_number", "value": "+1234567890" }`

**CRITICAL rules:**
- Payload must have exactly `title`, `notes`, and optional fields — no extra keys
- For database pages, `props` must match the database schema
- After creation, the page is auto-pulled locally as markdown

**Transaction semantics:**

`new` follows the same 4-phase pipeline as `submit`:

1. **Phase 0: Parse** — Read and validate JSON from stdin
2. **Phase 1: Prepare** — Verify parent exists, derive internal ops, create commit draft
3. **Phase 2: Apply** — Create page on Notion (metadata only)
4. **Phase 3: Finalize** — Persist version record, auto-pull page. On failure, rollback (archive page).

Rollback for `new`:
- Archives the created page (soft-delete)

**Success output (JSON mode):**

```json
{
  "ok": true,
  "commit_id": "parent-id-20260304T120000Z",
  "action": "new",
  "status": "pushed",
  "created_page_id": "abc123-def456",
  "page_url": "https://notion.so/abc123def456",
  "title": "My New Page",
  "parent_id": "parent-id",
  "parent_type": "page",
  "pulled_to": "/path/to/notion-page-abc123-def456.md"
}
```

**Dry run output:**

```json
{
  "ok": true,
  "action": "new",
  "status": "dry_run",
  "dry_run": true,
  "validation": "passed",
  "title": "My New Page",
  "parent_id": "parent-id"
}
```

### 2.5 History and Restore

#### View history

```bash
solid-notion history <page_id>
```

Output: tab-separated `<id>\t<created_at>\t<type>`.

Types:
- `changeset` — Created by `write` or `restore`
- `new` — Created by `new` command
- `submit` — Created by `submit` command

#### Restore to a previous changeset or version

```bash
solid-notion restore <page_id> <changeset_or_commit_id>
solid-notion restore <changeset_or_commit_id>
```

**Behavior depends on type:**
- **Changeset** (from `write`/`restore`): Restores page to that changeset's state
- **Version (`submit` or `new`)**: Restore to the target hash by undoing only the later `submit` versions, then writes a new changeset

Hash-only lookup is supported. If the hash exists in multiple pages, CLI asks you to disambiguate with page ID.

After restore-to-version, local version files after the target hash are deleted.

Outputs the new changeset ID created by restore.

---

## 3. Agent Workflows

### Workflow: Read a page as Markdown

```bash
solid-notion pull page <page_id_or_name> --format markdown --outdir /tmp/notion-work
```

Then read the output file path printed to stdout.

### Workflow: Full edit cycle (Markdown mode)

1. **Pull** the page to a workspace:
   ```bash
   solid-notion pull page <page_id> --format markdown --outdir ~/.local/share/solid-notion-cli/<page_id>
   ```

2. **Edit** the local `page.md` file as needed.

3. **Write** changes back:
   ```bash
   solid-notion write <page_id>
   ```

4. **Submit** with a message:
   ```bash
   solid-notion submit <page_id> -m "Updated section headings"
   ```

### Workflow: Edit via JSON patch (Programmatic mode)

Use this workflow when making precise, targeted edits without pulling full markdown.

1. **Get the target block IDs** (you may need to pull JSON first):
   ```bash
   solid-notion pull page <page_id> --format json --outdir /tmp
   # or inspect specific block:
   solid-notion show block <block_id> --format json
   ```

2. **Construct a valid patch** with `ops` array and `notes`:
   ```json
   {
     "ops": [
       {
         "op": "replace_block_text",
         "block_id": "block-uuid-here",
         "new_markdown": "Updated content here",
         "reason": "Clarified the explanation"
       },
       {
         "op": "set_props",
         "page_id": "page-uuid-here",
         "set": {
           "Status": { "type": "select", "name": "In Progress" }
         },
         "reason": "Moving to next phase"
       }
     ],
     "notes": "Batch update from review session"
   }
   ```

3. **Apply the patch** via stdin:
   ```bash
   cat patch.json | solid-notion edit <page_id>
   ```

4. **Submit** the pending edits:
   ```bash
   solid-notion submit <page_id> -m "Applied review feedback"
   ```

**CRITICAL rules for JSON patch editing:**
- The patch must have exactly `ops` and `notes` — no extra keys
- Each op must have `op`, `reason`, and type-specific fields
- `block_id` in `replace_block_text` must be a valid Notion block ID
- `page_id` in `set_props` must be the target page UUID
- `append_blocks` creates new blocks — the `created_block_ids` are recorded in edit logs for rollback

### Workflow: Batch multiple edits before submit

You can run multiple `edit` commands before a single `submit`. All pending edits are aggregated:

```bash
# First edit
echo '{"ops":[...],"notes":"First change"}' | solid-notion edit <page_id>

# Second edit  
echo '{"ops":[...],"notes":"Second change"}' | solid-notion edit <page_id>

# Third edit
echo '{"ops":[...],"notes":"Third change"}' | solid-notion edit <page_id>

# Submit all at once
solid-notion submit <page_id> -m "Batch: three related updates"
```

Submit reads all edit logs from `edit-logs/<page_id>/`, marks them `.submitted` on success, and creates a single commit record.

### Workflow: Restore a change

1. **List** changesets:
   ```bash
   solid-notion history <page_id>
   ```

2. **Restore** to a specific hash:
   ```bash
   solid-notion restore <page_id> <changeset_or_commit_id>
   # or hash-only when unique:
   solid-notion restore <changeset_or_commit_id>
   ```

---

## 4. Storage Concepts & Layout

All data is stored under `$SOLID_NOTION_HOME` (default: `~/.local/share/solid-notion-cli`).

### Storage Concepts Explained

**Workspace files** (`<page_id>/`) — Created by `pull`, used by `write`:
- `page.md` — The markdown you edit
- `.original.md` — Snapshot before editing (for diff/comparison)
- `page.meta.md` — Page metadata (properties, etc.)
- **Lifecycle**: Created on `pull`, deleted on successful `write`

**Edit logs** (`edit-logs/<page_id>/`) — Created by `edit`, consumed by `submit`:
- JSONL files recording each patch operation with before/after snapshots
- **Purpose**: Enable rollback if submit fails
- **Format**: Each line is a JSON object with `op`, `block_id`/`page_id`, `reason`, and before/after values
- **Lifecycle**: Created on `edit`, marked `.submitted` on successful `submit`

**Versions** (`<page_id>/versions/`) — Created by `submit`:
- Commit records with full operation history and snapshots
- **Purpose**: Immutable history of what was published to Notion
- **Format**: JSON with `commitId`, `status`, `ops`, `beforeSnapshots`, `applyState`
- **Lifecycle**: Created on every `submit` attempt (even failures)

**Changesets** (`changesets/<page_id>/`) — Created by `write` and `restore`:
- Reversible markdown diffs for the "write -> restore" workflow
- **Purpose**: Track full page content changes for `history` and `restore`
- **Format**: Markdown files with YAML frontmatter containing before/after content
- **Lifecycle**: Created on `write`, referenced by `history` and `restore`

### Directory Layout

```
$SOLID_NOTION_HOME/
  config.json                          # Auth tokens (mode 0600)
  
  # Workspace (markdown editing workflow)
  <page_id>/
    page.md                            # Edited markdown
    page.meta.md                       # Page metadata
    .original.md                       # Original for diff
    versions/                          # Submit commits (JSON)
  
  # Edit logs (JSON patch workflow)
  edit-logs/<page_id>/
    <page_id>-<timestamp>.jsonl        # Pending edits (before submit)
    <page_id>-<timestamp>.jsonl.submitted  # Marker file (after submit)
  
  # Changesets (restorable full-page versions)
  changesets/<page_id>/
    <page_id>-<timestamp>.md           # Changeset with YAML frontmatter
```

Override the base directory with `SOLID_NOTION_HOME` environment variable.

---

## 5. Global Flags

| Flag | Effect |
|------|--------|
| `-v, --verbose` | Print debug logs to stderr |
| `-V, --version` | Print version |

---

## 6. Error Handling

### init command error codes

| Exit code | Error | Meaning |
|-----------|-------|---------|
| 2 | `missing_arguments` | No token provided |
| 3 | `invalid_token` | Token is empty or invalid |
| 4 | `token_already_exists` | Token exists, use `--force` |
| 5 | `write_failed` | Could not write config file |

### General errors

All other commands exit `1` on failure and print diagnostics to stderr including error name, message, metadata (status, code, errno, syscall, hostname), cause chain, and stack trace.

---

## 7. Anti-Patterns

### Authentication
- **Do NOT** use `--token <value>` in automated flows. Use `--token-stdin` to avoid leaking tokens in process lists.
- **Do NOT** skip `solid-notion auth status --json` before running commands. If there is no token, all Notion API calls will fail.

### Page IDs
- **Do NOT** pass page names to `edit`, `write`, `submit`, `history`, or `restore`. These commands require strict page UUIDs.

### Output parsing
- **Do NOT** forget `--json` when you need to parse command output programmatically.

### Submit command
- **Do NOT** call `submit` without `-m`. The message flag is **required**.
- **Do NOT** assume `submit` takes stdin — it reads from local `edit-logs/`, not from stdin.
- **Do NOT** ignore `status: "rolled_back"` — this means Notion writes failed but were undone.
- **Do NOT** ignore `status: "failed_needs_reconcile"` — this means both apply AND rollback failed.

### Edit patch schema
- **Do NOT** include extra keys in the patch object (only `ops` and `notes` allowed).
- **Do NOT** forget the `reason` field in each op — it is required.
- **Do NOT** use unsupported block types in `replace_block_text` or `append_blocks`.
- **Do NOT** use `set_props` on properties with unsupported types (only: number, checkbox, select, multi_select, date, title, rich_text).
- **Do NOT** pass Notion block objects as `new_markdown` — pass simple Markdown text (e.g., "## Heading" or "Paragraph with **bold**").
