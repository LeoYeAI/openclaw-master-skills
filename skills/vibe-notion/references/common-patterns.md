# Common Patterns for Vibe Notion

This document outlines common workflows and patterns for interacting with Notion via the CLI.

## 1. Reading Page Content Recursively

To get the full content of a page, you need to retrieve the page object and then its child blocks. If those blocks have children (e.g., nested lists, columns), you may need to fetch those recursively.

```bash
# 1. Get page metadata
vibe-notion page get <page_id> --workspace-id <workspace_id>

# 2. List direct children
vibe-notion block children <page_id> --workspace-id <workspace_id>

# 3. For any block that has "has_children: true", fetch its children
vibe-notion block children <block_id> --workspace-id <workspace_id>
```

## 2. Querying a Database and Processing Results

Querying a database returns a list of page objects. You can filter, sort, and search results.

```bash
# Query a database with a search keyword
vibe-notion database query <database_id> --workspace-id <workspace_id> --search-query "keyword" --pretty

# Query with a limit
vibe-notion database query <database_id> --workspace-id <workspace_id> --limit 10 --pretty

# Query a specific view
vibe-notion database query <database_id> --workspace-id <workspace_id> --view-id <view_id> --pretty

# Query with timezone
vibe-notion database query <database_id> --workspace-id <workspace_id> --timezone "America/New_York" --pretty
```

> **Note**: The `--filter` and `--sort` options use property IDs from the database schema (retrieved via `database get`), not property names.

## 3. Creating a Page with Initial Content

Creating a page only sets the properties (like Title). To add content, you must append blocks to the newly created page.

```bash
# 1. Create the page and capture the ID
PAGE_ID=$(vibe-notion page create --workspace-id <workspace_id> --parent <parent_id> --title "New Document" | jq -r '.id')

# 2. Append content blocks
vibe-notion block append $PAGE_ID --workspace-id <workspace_id> --content '[
  {"type": "header", "properties": {"title": [["Introduction"]]}},
  {"type": "text", "properties": {"title": [["This is a new page created via CLI."]]}}
]'
```

## 4. Adding Content with Markdown

Use the `--markdown` flag to append or create pages with markdown content.

```bash
# Append markdown content to an existing page
vibe-notion block append <page_id> --workspace-id <workspace_id> --markdown '# Introduction

This is a new page created via CLI.'

# Create a page with markdown content from a file
vibe-notion page create --workspace-id <workspace_id> --parent <parent_id> --title "New Document" --markdown-file ./content.md

# Replace all content on a page with new markdown
vibe-notion page update <page_id> --workspace-id <workspace_id> --replace-content --markdown-file ./updated.md
```

## 5. Updating a Page

You can update a page's title, icon, or replace its entire content.

```bash
# Update title
vibe-notion page update <page_id> --workspace-id <workspace_id> --title "New Title" --pretty

# Update icon
vibe-notion page update <page_id> --workspace-id <workspace_id> --icon "🚀" --pretty

# Replace all content with new markdown
vibe-notion page update <page_id> --workspace-id <workspace_id> --replace-content --markdown '# New Content'

# Replace all content from a markdown file
vibe-notion page update <page_id> --workspace-id <workspace_id> --replace-content --markdown-file ./updated.md
```

## 6. Searching for Specific Content

Search is the best way to find objects when you don't have their IDs.

```bash
# Basic search
vibe-notion search "Inventory" --workspace-id <workspace_id> --pretty

# Search with a result limit
vibe-notion search "Meeting Notes" --workspace-id <workspace_id> --limit 10 --pretty

# Search sorted by last edited time
vibe-notion search "Meeting Notes" --workspace-id <workspace_id> --sort lastEdited --pretty

# Paginate through results using next_cursor from previous response
vibe-notion search "Notes" --workspace-id <workspace_id> --start-cursor 20 --pretty
```

## 7. Handling Pagination

Many list and query commands support pagination.

```bash
# Get the first 10 database results
vibe-notion database query <database_id> --workspace-id <workspace_id> --limit 10

# Block children use cursor-based pagination — pass next_cursor JSON from previous response
vibe-notion block children <block_id> --workspace-id <workspace_id> --start-cursor '<next_cursor_json>'

# Search uses offset-based pagination — pass next_cursor number from previous response
vibe-notion search "query" --workspace-id <workspace_id> --start-cursor 20
```

## 8. Batch Operations (Multiple Writes in One Call)

When you need to perform multiple write operations, use `batch` instead of calling the CLI once per action. This is especially useful for populating databases, setting up page structures, or making coordinated changes.

### Adding multiple rows to a database

```bash
vibe-notion batch --workspace-id <workspace_id> '[
  {"action": "database.add-row", "database_id": "<db_id>", "title": "Task 1", "properties": {"Status": "To Do", "Priority": "High"}},
  {"action": "database.add-row", "database_id": "<db_id>", "title": "Task 2", "properties": {"Status": "To Do", "Priority": "Medium"}},
  {"action": "database.add-row", "database_id": "<db_id>", "title": "Task 3", "properties": {"Status": "In Progress"}}
]'
```

### Creating a page and appending content in one call

```bash
vibe-notion batch --workspace-id <workspace_id> '[
  {"action": "page.create", "parent": "<parent_id>", "title": "Weekly Report"},
  {"action": "block.append", "parent_id": "<new_page_id>", "markdown": "# Summary\n\nAll tasks completed on time."}
]'
```

> **Note**: The second operation needs the page ID from the first. Since batch runs sequentially and you won't know the ID ahead of time, split this into two calls: one `page create` to get the ID, then a `batch` for the remaining operations. Batch is most useful when operations are independent or you already have all IDs.

### Updating multiple rows at once

```bash
vibe-notion batch --workspace-id <workspace_id> '[
  {"action": "database.update-row", "row_id": "<row_1>", "properties": {"Status": "Done"}},
  {"action": "database.update-row", "row_id": "<row_2>", "properties": {"Status": "Done"}},
  {"action": "database.update-row", "row_id": "<row_3>", "properties": {"Status": "Cancelled"}}
]'
```

### Using a file for large payloads

When the JSON is too large for a shell argument, write it to a file first:

```bash
# Write operations to a file, then pass it
vibe-notion batch --workspace-id <workspace_id> --file ./operations.json ''
```
