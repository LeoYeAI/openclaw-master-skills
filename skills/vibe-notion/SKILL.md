---
name: vibe-notion
description: Interact with Notion using the unofficial private API - pages, databases, blocks, search, users, comments
version: 1.4.0
allowed-tools: Bash(vibe-notion:*)
metadata:
  openclaw:
    requires:
      bins:
        - vibe-notion
    install:
      - kind: node
        package: vibe-notion
        bins: [vibe-notion]
---

# Vibe Notion

A TypeScript CLI tool that enables AI agents and humans to interact with Notion workspaces through the unofficial private API. Supports full CRUD operations on pages, databases, blocks, search, and user management.

> **Note**: This skill uses Notion's internal/private API (`/api/v3/`), which is separate from the official public API. For official API access, use `vibe-notionbot`.


## Which CLI to Use

This package ships two CLIs. Pick the right one based on your situation:

| | `vibe-notion` (this CLI) | `vibe-notionbot` |
|---|---|---|
| API | Unofficial private API | Official Notion API |
| Auth | `token_v2` auto-extracted from Notion desktop app | `NOTION_TOKEN` env var (Integration token) |
| Identity | Acts as the user | Acts as a bot |
| Setup | Zero — credentials extracted automatically | Manual — create Integration at notion.so/my-integrations |
| Database rows | `add-row`, `update-row` | Create via `page create --database` |
| View management | `view-get`, `view-update`, `view-list`, `view-add`, `view-delete` | Not supported |
| Workspace listing | Supported | Not supported |
| Stability | Private API — may break on Notion changes | Official versioned API — stable |

**Decision flow:**

1. If the Notion desktop app is installed → use `vibe-notion` (this CLI)
2. If `NOTION_TOKEN` is set but no desktop app → use `vibe-notionbot`
3. If both are available → prefer `vibe-notion` (broader capabilities, zero setup)
4. If neither → ask the user to set up one of the two

## Important: CLI Only

**Never call Notion's internal API directly.** Always use the `vibe-notion` CLI commands described in this skill. Do not make raw HTTP requests to `notion.so/api/v3/` or use any Notion client library. Direct API calls risk exposing credentials and may trigger Notion's abuse detection, getting the user's account blocked.

If a feature you need is not supported by `vibe-notion`, let the user know and offer to file a feature request at [devxoul/vibe-notion](https://github.com/devxoul/vibe-notion/issues) on their behalf. Before submitting, strip out any real user data — IDs, names, emails, tokens, page content, or anything else that could identify the user or their workspace. Use generic placeholders instead and keep the issue focused on describing the missing capability.

## Important: Never Write Scripts

**Never write scripts (Python, TypeScript, Bash, etc.) to automate Notion operations.** The `batch` command already handles bulk operations of any size. Writing a script to loop through API calls is always wrong — use `batch` with `--file` instead.

This applies even when:
- You need to create 100+ rows
- You need cross-references between newly created rows (use multi-pass batch — see [references/batch-operations.md](references/batch-operations.md#bulk-operations-strategy))
- The operation feels "too big" for a single command

If you catch yourself thinking "I should write a script for this," stop and use `batch`.

## Quick Start

```bash
# 1. Find your workspace ID
vibe-notion workspace list --pretty

# 2. Search for a page
vibe-notion search "Roadmap" --workspace-id <workspace-id> --pretty

# 3. Get page content
vibe-notion page get <page-id> --workspace-id <workspace-id> --pretty

# 4. Query a database
vibe-notion database query <collection-id> --workspace-id <workspace-id> --pretty
```

Credentials are auto-extracted from the Notion desktop app on first use. No manual setup needed.

> **Important**: `--workspace-id` is required for ALL commands that operate within a specific workspace. Use `vibe-notion workspace list` to find your workspace ID.

## Authentication

Credentials (`token_v2`) are auto-extracted from the Notion desktop app when you run any command. No API keys, OAuth, or manual extraction needed.

On macOS, your system may prompt for Keychain access on first use — this is normal and required to decrypt the cookie.

The extracted `token_v2` is stored at `~/.config/vibe-notion/credentials.json` with `0600` permissions.

## Memory

The agent maintains a `~/.config/vibe-notion/MEMORY.md` file as persistent memory across sessions. This is agent-managed — the CLI does not read or write this file. Use the `Read` and `Write` tools to manage your memory file.

### Reading Memory

At the **start of every task**, read `~/.config/vibe-notion/MEMORY.md` using the `Read` tool to load any previously discovered workspace IDs, page IDs, database IDs, and user preferences.

- If the file doesn't exist yet, that's fine — proceed without it and create it when you first have useful information to store.
- If the file can't be read (permissions, missing directory), proceed without memory — don't error out.

### Writing Memory

After discovering useful information, update `~/.config/vibe-notion/MEMORY.md` using the `Write` tool. Write triggers include:

- After discovering workspace IDs (from `workspace list`)
- After discovering useful page IDs, database IDs, collection IDs (from `search`, `page list`, `page get`, `database list`, etc.)
- After the user gives you an alias or preference ("call this the Tasks DB", "my main workspace is X")
- After discovering page/database structure (parent-child relationships, what databases live under which pages)

When writing, include the **complete file content** — the `Write` tool overwrites the entire file.

### What to Store

- Workspace IDs with names
- Page IDs with titles and parent context
- Database/collection IDs with titles and parent context
- User-given aliases ("Tasks DB", "Main workspace")
- Commonly used view IDs
- Parent-child relationships (which databases are under which pages)
- Any user preference expressed during interaction

### What NOT to Store

Never store `token_v2`, credentials, API keys, or any sensitive data. Never store full page content (just IDs and titles). Never store block-level IDs unless they're persistent references (like database blocks).

### Handling Stale Data

If a memorized ID returns an error (page not found, access denied), remove it from `MEMORY.md`. Don't blindly trust memorized data — verify when something seems off. Prefer re-searching over using a memorized ID that might be stale.

### Format / Example

Here's a concrete example of how to structure your `MEMORY.md`:

```markdown
# Vibe Notion Memory

## Workspaces

- `abc123-...` — Acme Corp (default)

## Pages (Acme Corp)

- `page-id-1` — Product Roadmap (top-level)
- `page-id-2` — Q1 Planning (under Product Roadmap)

## Databases (Acme Corp)

- `coll-id-1` — Tasks (under Product Roadmap, views: `view-1`)
- `coll-id-2` — Contacts (top-level)

## Aliases

- "roadmap" → `page-id-1` (Product Roadmap)
- "tasks" → `coll-id-1` (Tasks database)

## Notes

- User prefers --pretty output for search results
- Main workspace is "Acme Corp"
```

> Memory lets you skip repeated `search` and `workspace list` calls. When you already know an ID from a previous session, use it directly.

## Commands

### Auth Commands

```bash
vibe-notion auth status     # Check authentication status
vibe-notion auth logout     # Remove stored token_v2
vibe-notion auth extract    # Manually re-extract token_v2 (for troubleshooting)
```

### Page Commands

```bash
# List pages in a space (top-level only)
vibe-notion page list --workspace-id <workspace_id> --pretty
vibe-notion page list --workspace-id <workspace_id> --depth 2 --pretty

# Get a page and all its content blocks
vibe-notion page get <page_id> --workspace-id <workspace_id> --pretty
vibe-notion page get <page_id> --workspace-id <workspace_id> --limit 50
vibe-notion page get <page_id> --workspace-id <workspace_id> --backlinks --pretty

# Create a new page (--parent is optional; omit to create at workspace root)
vibe-notion page create --workspace-id <workspace_id> --parent <parent_id> --title "My Page" --pretty
vibe-notion page create --workspace-id <workspace_id> --title "New Root Page" --pretty


# Create a page with markdown content
vibe-notion page create --workspace-id <workspace_id> --parent <parent_id> --title "My Doc" --markdown '# Hello\n\nThis is **bold** text.'

# Create a page with markdown from a file
vibe-notion page create --workspace-id <workspace_id> --parent <parent_id> --title "My Doc" --markdown-file ./content.md

# Create a page with markdown containing local images (auto-uploaded to Notion)
vibe-notion page create --workspace-id <workspace_id> --parent <parent_id> --title "My Doc" --markdown-file ./doc-with-images.md

# Replace all content on a page with new markdown
vibe-notion page update <page_id> --workspace-id <workspace_id> --replace-content --markdown '# New Content'
vibe-notion page update <page_id> --workspace-id <workspace_id> --replace-content --markdown-file ./updated.md

# Update page title or icon
vibe-notion page update <page_id> --workspace-id <workspace_id> --title "New Title" --pretty
vibe-notion page update <page_id> --workspace-id <workspace_id> --icon "🚀" --pretty

# Archive a page
vibe-notion page archive <page_id> --workspace-id <workspace_id> --pretty

# Get page or database row properties (without content blocks — lightweight alternative to page get)
vibe-notion page properties <page_id> --workspace-id <workspace_id> --pretty
```

### Database Commands

```bash
# Get database schema
vibe-notion database get <database_id> --workspace-id <workspace_id> --pretty

# Query a database (auto-resolves default view)
vibe-notion database query <database_id> --workspace-id <workspace_id> --pretty
vibe-notion database query <database_id> --workspace-id <workspace_id> --limit 10 --pretty
vibe-notion database query <database_id> --workspace-id <workspace_id> --view-id <view_id> --pretty
vibe-notion database query <database_id> --workspace-id <workspace_id> --search-query "keyword" --pretty
vibe-notion database query <database_id> --workspace-id <workspace_id> --timezone "America/New_York" --pretty

# Query with filter and sort (uses property IDs from database get schema)
vibe-notion database query <database_id> --workspace-id <workspace_id> --filter '<filter_json>' --pretty
vibe-notion database query <database_id> --workspace-id <workspace_id> --sort '<sort_json>' --pretty

# List all databases in workspace
vibe-notion database list --workspace-id <workspace_id> --pretty

# Create a database
vibe-notion database create --workspace-id <workspace_id> --parent <page_id> --title "Tasks" --pretty
vibe-notion database create --workspace-id <workspace_id> --parent <page_id> --title "Tasks" --properties '{"status":{"name":"Status","type":"select"}}' --pretty

# Update database title or schema
vibe-notion database update <database_id> --workspace-id <workspace_id> --title "New Name" --pretty
vibe-notion database update <database_id> --workspace-id <workspace_id> --properties '{"status":{"name":"Status","type":"select"}}' --pretty
vibe-notion database update <database_id> --workspace-id <workspace_id> --title "New Name" --properties '{"status":{"name":"Status","type":"select"}}' --pretty

# Add a row to a database
vibe-notion database add-row <database_id> --workspace-id <workspace_id> --title "Row title" --pretty
vibe-notion database add-row <database_id> --workspace-id <workspace_id> --title "Row title" --properties '{"Status":"In Progress","Due":{"start":"2025-03-01"}}' --pretty

# Add row with date range
vibe-notion database add-row <database_id> --workspace-id <workspace_id> --title "Event" --properties '{"Due":{"start":"2026-01-01","end":"2026-01-15"}}' --pretty

# Update properties on an existing database row (row_id from database query)
vibe-notion database update-row <row_id> --workspace-id <workspace_id> --properties '{"Status":"Done"}' --pretty
vibe-notion database update-row <row_id> --workspace-id <workspace_id> --properties '{"Priority":"High","Tags":["backend","infra"]}' --pretty
vibe-notion database update-row <row_id> --workspace-id <workspace_id> --properties '{"Due":{"start":"2026-06-01"},"Status":"In Progress"}' --pretty
vibe-notion database update-row <row_id> --workspace-id <workspace_id> --properties '{"Due":{"start":"2026-01-01","end":"2026-01-15"}}' --pretty
vibe-notion database update-row <row_id> --workspace-id <workspace_id> --properties '{"Related":["<target_row_id>"]}' --pretty

# Delete a property from a database (cannot delete the title property)
vibe-notion database delete-property <database_id> --workspace-id <workspace_id> --property "Status" --pretty

# Get view configuration and property visibility
vibe-notion database view-get <view_id> --workspace-id <workspace_id> --pretty

# Show or hide properties on a view (comma-separated names)
vibe-notion database view-update <view_id> --workspace-id <workspace_id> --show "ID,Due" --pretty
vibe-notion database view-update <view_id> --workspace-id <workspace_id> --hide "Assignee" --pretty
vibe-notion database view-update <view_id> --workspace-id <workspace_id> --show "Status" --hide "Due" --pretty

# Reorder columns (comma-separated names in desired order; unmentioned columns appended)
vibe-notion database view-update <view_id> --workspace-id <workspace_id> --reorder "Name,Status,Priority,Date" --pretty
vibe-notion database view-update <view_id> --workspace-id <workspace_id> --reorder "Name,Status" --show "Status" --pretty

# Resize columns (JSON mapping property names to pixel widths)
vibe-notion database view-update <view_id> --workspace-id <workspace_id> --resize '{"Name":200,"Status":150}' --pretty

# List all views for a database
vibe-notion database view-list <database_id> --workspace-id <workspace_id> --pretty

# Add a new view to a database (default type: table)
vibe-notion database view-add <database_id> --workspace-id <workspace_id> --pretty
vibe-notion database view-add <database_id> --workspace-id <workspace_id> --type board --name "Board View" --pretty

# Delete a view from a database (cannot delete the last view)
vibe-notion database view-delete <view_id> --workspace-id <workspace_id> --pretty
```

### Table Commands

Simple tables (non-database) — lightweight tables embedded in pages.

```bash
# Create a simple table with headers and optional rows
vibe-notion table create <parent_id> --workspace-id <workspace_id> --headers "Name,Role,Score" --pretty
vibe-notion table create <parent_id> --workspace-id <workspace_id> --headers "Name,Role,Score" --rows '[["Alice","Dev","95"],["Bob","PM","88"]]' --pretty
vibe-notion table create <parent_id> --workspace-id <workspace_id> --headers "A,B" --after <block_id> --pretty
vibe-notion table create <parent_id> --workspace-id <workspace_id> --headers "A,B" --before <block_id> --pretty

# Add a row to a simple table
vibe-notion table add-row <table_id> --workspace-id <workspace_id> --cells "Charlie,QA,92" --pretty

# Update a single cell (row and col are 0-indexed, excluding header row)
vibe-notion table update-cell <table_id> --workspace-id <workspace_id> --row 0 --col 1 --value "Lead" --pretty

# Delete a row (0-indexed, excluding header row)
vibe-notion table delete-row <table_id> --workspace-id <workspace_id> --row 0 --pretty
```

> **Simple tables vs databases**: Simple tables are inline, lightweight grids with no schema, filters, or views. Use `database` commands for structured data with typed properties, filtering, and sorting.

### Block Commands

```bash
# Get a specific block
vibe-notion block get <block_id> --workspace-id <workspace_id> --pretty
vibe-notion block get <block_id> --workspace-id <workspace_id> --backlinks --pretty

# List child blocks
vibe-notion block children <block_id> --workspace-id <workspace_id> --pretty
vibe-notion block children <block_id> --workspace-id <workspace_id> --limit 50 --pretty
vibe-notion block children <block_id> --workspace-id <workspace_id> --start-cursor '<next_cursor_json>' --pretty

# Append child blocks
vibe-notion block append <parent_id> --workspace-id <workspace_id> --content '[{"type":"text","properties":{"title":[["Hello world"]]}}]' --pretty

# Append markdown content as blocks
vibe-notion block append <parent_id> --workspace-id <workspace_id> --markdown '# Hello\n\nThis is **bold** text.'

# Append markdown from a file
vibe-notion block append <parent_id> --workspace-id <workspace_id> --markdown-file ./content.md

# Append markdown with local images (auto-uploaded to Notion)
vibe-notion block append <parent_id> --workspace-id <workspace_id> --markdown-file ./doc-with-images.md

# Append nested markdown (indented lists become nested children blocks)
vibe-notion block append <parent_id> --workspace-id <workspace_id> --markdown '- Parent item\n  - Child item\n    - Grandchild item'

# Append blocks after a specific block (positional insertion)
vibe-notion block append <parent_id> --workspace-id <workspace_id> --after <block_id> --markdown '# Inserted after specific block'
vibe-notion block append <parent_id> --workspace-id <workspace_id> --after <block_id> --content '[{"type":"text","properties":{"title":[["Inserted after"]]}}]'

# Append blocks before a specific block
vibe-notion block append <parent_id> --workspace-id <workspace_id> --before <block_id> --markdown '# Inserted before specific block'

# Update a block
vibe-notion block update <block_id> --workspace-id <workspace_id> --content '{"properties":{"title":[["Updated text"]]}}' --pretty

# Delete a block
vibe-notion block delete <block_id> --workspace-id <workspace_id> --pretty

# Upload a file as a block (image or file block)
vibe-notion block upload <parent_id> --workspace-id <workspace_id> --file ./image.png --pretty
vibe-notion block upload <parent_id> --workspace-id <workspace_id> --file ./document.pdf --pretty
vibe-notion block upload <parent_id> --workspace-id <workspace_id> --file ./image.png --after <block_id> --pretty
vibe-notion block upload <parent_id> --workspace-id <workspace_id> --file ./image.png --before <block_id> --pretty

# Move a block to a new position
vibe-notion block move <block_id> --workspace-id <workspace_id> --parent <parent_id> --pretty
vibe-notion block move <block_id> --workspace-id <workspace_id> --parent <parent_id> --after <sibling_id> --pretty
vibe-notion block move <block_id> --workspace-id <workspace_id> --parent <parent_id> --before <sibling_id> --pretty
```

### Block Types & Rich Text Reference

For block type JSON format (headings, text, lists, to-do, code, quote, divider) and rich text formatting codes, see [references/block-types.md](references/block-types.md).

### Comment Commands

```bash
# List comments on a page
vibe-notion comment list --page <page_id> --workspace-id <workspace_id> --pretty

# List inline comments on a specific block
vibe-notion comment list --page <page_id> --block <block_id> --workspace-id <workspace_id> --pretty

# Create a comment on a page (starts a new discussion)
vibe-notion comment create "This is a comment" --page <page_id> --workspace-id <workspace_id> --pretty

# Reply to an existing discussion thread
vibe-notion comment create "Replying to thread" --discussion <discussion_id> --workspace-id <workspace_id> --pretty

# Get a specific comment by ID
vibe-notion comment get <comment_id> --workspace-id <workspace_id> --pretty
```

## Batch Operations

For batch command format, supported actions (14 total), operation JSON structure, output format, fail-fast behavior, bulk operations strategy (multi-pass pattern), and rate limit handling, see [references/batch-operations.md](references/batch-operations.md).

**Quick usage:**

```bash
# Inline JSON
vibe-notion batch --workspace-id <workspace_id> '<operations_json>'

# From file (for large payloads)
vibe-notion batch --workspace-id <workspace_id> --file ./operations.json '[]'
```

### Search Command

```bash
# Search across workspace (--workspace-id is required)
vibe-notion search "query" --workspace-id <workspace_id> --pretty
vibe-notion search "query" --workspace-id <workspace_id> --limit 10 --pretty
vibe-notion search "query" --workspace-id <workspace_id> --start-cursor <offset> --pretty
vibe-notion search "query" --workspace-id <workspace_id> --sort lastEdited --pretty
```

### User Commands

```bash
# Get current user info
vibe-notion user me --pretty

# Get a specific user
vibe-notion user get <user_id> --workspace-id <workspace_id> --pretty

# List users in a workspace
vibe-notion user list --workspace-id <workspace_id> --pretty
```

## Output Format

All commands output JSON by default. Use `--pretty` for human-readable output.

For JSON response shapes (search, database query, page get, block get, backlinks), `$hints` schema warnings, and detailed examples, see [references/output-format.md](references/output-format.md).

## When to Use `--backlinks`

Backlinks reveal which pages/databases **link to** a given page. This is critical for efficient navigation.

**Use `--backlinks` when:**
- **Tracing relations**: A search result looks like a select option, enum value, or relation target (e.g., a plan name or category). Backlinks instantly reveal all rows/pages that reference it via relation properties — no need to hunt for the parent database.
- **Finding references**: You found a page and want to know what other pages mention or link to it.
- **Reverse lookups**: Instead of querying every database to find rows pointing to a page, use backlinks on the target page to get them directly.

**Example — finding who uses a specific plan:**
```bash
# BAD: 15 API calls — search, open empty pages, trace parents, find database, query
vibe-notion search "Enterprise Plan" ...
vibe-notion page get <plan-page-id> ...  # empty
vibe-notion block get <plan-page-id> ...  # find parent
# ... many more calls to discover the database

# GOOD: 2-3 API calls — search, then backlinks on the target
vibe-notion search "Enterprise Plan" ...
vibe-notion page get <plan-page-id> --backlinks --pretty
# → backlinks immediately show all people/rows linked to this plan
```

## Pagination

Commands that return lists support pagination via `has_more`, `next_cursor` fields:

- **`block children`**: Cursor-based. Pass `next_cursor` value from previous response as `--start-cursor`.
- **`search`**: Offset-based. Pass `next_cursor` value (a number) as `--start-cursor`.
- **`database query`**: Use `--limit` to control page size. `has_more` indicates more results exist, but the private API does not support cursor-based pagination — increase `--limit` to fetch more rows.

## Troubleshooting

### Authentication failures

If auto-extraction fails (e.g., Notion desktop app is not installed or not logged in), run the extract command manually for debug output:

```bash
vibe-notion auth extract --debug
```

This shows the Notion directory path and extraction steps to help diagnose the issue.

### Database locked during extraction

If `auth extract` fails with:

```json
{"error":"No token_v2 found. Make sure Notion desktop app is installed and logged in."}
```

And the Notion desktop app **is** installed and logged in, the cookie database may be locked by the running Notion app. Tell the user to quit the Notion desktop app completely, then retry the command. Once credentials are extracted, the user can reopen Notion.

### `vibe-notion: command not found`

The `vibe-notion` package is not installed. Run it directly using a package runner. Ask the user which one to use:

```bash
npx -y vibe-notion ...
bunx vibe-notion ...
pnpm dlx vibe-notion ...
```

If you already know the user's preferred package runner, use it directly instead of asking.

## Limitations

- Auto-extraction supports macOS and Linux. Windows DPAPI decryption is not yet supported.
- `token_v2` uses the unofficial internal API and may break if Notion changes it.
- This is a private/unofficial API and is not supported by Notion.
