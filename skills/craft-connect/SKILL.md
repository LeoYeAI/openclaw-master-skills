---
name: craft
description: >
  Read and write Craft documents via the Craft Connect API. Use when the user
  asks to create, read, update, or search Craft documents, manage tasks, write
  daily notes, organize folders, work with collections (structured databases),
  or format rich content. Covers all block types including toggles, callouts,
  tables, code, highlights, math formulas, images, cards, and styled text.
  NOT for general note-taking to local files or unrelated document editors.
  Requires: CRAFT_API_URL (Craft Connect API base URL with embedded link token,
  stored in TOOLS.md). Uses curl for all HTTP requests.
---

# Craft Document Management

Operate on a Craft space via the Craft Connect REST API. Full CRUD on documents,
blocks, folders, tasks, collections, and comments.

## Requirements

- **curl** — used for all API requests
- **CRAFT_API_URL** — your Craft Connect API base URL (contains embedded link token for authentication)

## Setup

1. Create a Craft Connect link in your Craft space (Settings → Connect → Create Link)
2. Copy the API base URL and store it in TOOLS.md under a Craft section:

```
CRAFT_API_URL=https://connect.craft.do/links/<LINK_ID>/api/v1
```

3. Read TOOLS.md before making any calls to retrieve the URL.

All calls use `curl` with `-H "Content-Type: application/json"` for writes and
`-H "Accept: application/json"` for reads.

**Important:** URL-encode non-ASCII characters (e.g. Chinese) in query params.

---

## API Reference

### Connection Info

```bash
curl -s "$CRAFT_API_URL/connection"
```

Returns space ID, timezone, current time, and deep-link URL templates.

### Discovery

```bash
# List all folders and locations
curl -s "$CRAFT_API_URL/folders"

# List documents in a location (unsorted | trash | templates | daily_notes)
curl -s "$CRAFT_API_URL/documents?location=unsorted"

# List documents in a folder
curl -s "$CRAFT_API_URL/documents?folderId=<FOLDER_ID>"

# With metadata (creation/modification dates, deep links)
curl -s "$CRAFT_API_URL/documents?location=unsorted&fetchMetadata=true"

# Date filters (ISO YYYY-MM-DD or: today, yesterday, tomorrow)
curl -s "$CRAFT_API_URL/documents?createdDateGte=2025-01-01&lastModifiedDateLte=today"
```

### Search

```bash
# Search across ALL documents (URL-encode non-ASCII!)
curl -s "$CRAFT_API_URL/documents/search?include=<TERM>&fetchMetadata=true"

# Search within a specific document (with context blocks)
curl -s "$CRAFT_API_URL/blocks/search?blockId=<DOC_ID>&pattern=<REGEX>&beforeBlockCount=2&afterBlockCount=2"

# Filter search by folder or location
curl -s "$CRAFT_API_URL/documents/search?include=<TERM>&folderIds=<FOLDER_ID>"
curl -s "$CRAFT_API_URL/documents/search?include=<TERM>&location=daily_notes"
```

### Documents

```bash
# Create document (defaults to unsorted)
curl -s -X POST "$CRAFT_API_URL/documents" \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"title": "My Document"}]}'

# Create in a specific folder
curl -s -X POST "$CRAFT_API_URL/documents" \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"title": "Doc"}], "destination": {"folderId": "<ID>"}}'

# Create as template
curl -s -X POST "$CRAFT_API_URL/documents" \
  -H "Content-Type: application/json" \
  -d '{"documents": [{"title": "Template"}], "destination": {"destination": "templates"}}'

# Delete (soft-delete to trash, recoverable)
curl -s -X DELETE "$CRAFT_API_URL/documents" \
  -H "Content-Type: application/json" \
  -d '{"documentIds": ["<DOC_ID>"]}'

# Move between locations
curl -s -X PUT "$CRAFT_API_URL/documents/move" \
  -H "Content-Type: application/json" \
  -d '{"documentIds": ["<ID>"], "destination": {"folderId": "<FOLDER_ID>"}}'

# Restore from trash
curl -s -X PUT "$CRAFT_API_URL/documents/move" \
  -H "Content-Type: application/json" \
  -d '{"documentIds": ["<ID>"], "destination": {"destination": "unsorted"}}'
```

### Reading Content

```bash
# Get document content (JSON)
curl -s "$CRAFT_API_URL/blocks?id=<DOC_ID>" -H "Accept: application/json"

# Get daily note
curl -s "$CRAFT_API_URL/blocks?date=today" -H "Accept: application/json"

# Control depth (0=block only, 1=direct children, -1=all)
curl -s "$CRAFT_API_URL/blocks?id=<ID>&maxDepth=1"

# With metadata (comments, authors, timestamps)
curl -s "$CRAFT_API_URL/blocks?id=<ID>&fetchMetadata=true"
```

### Writing Content

Two methods: **markdown** (recommended) and **blocks JSON**.

#### Method 1: Markdown (Recommended)

Best for most content. Craft parses markdown and auto-generates correct block
types, indentation levels, and list styles.

```bash
curl -s -X POST "$CRAFT_API_URL/blocks" \
  -H "Content-Type: application/json" \
  -d '{
    "markdown": "## Heading\n\nParagraph\n\n- bullet 1\n- bullet 2",
    "position": {"position": "end", "pageId": "<DOC_ID>"}
  }'
```

#### Method 2: Blocks JSON

Use when you need explicit control over `color`, `font`, `textStyle`, or other
properties not expressible in plain markdown.

```bash
curl -s -X POST "$CRAFT_API_URL/blocks" \
  -H "Content-Type: application/json" \
  -d '{
    "blocks": [
      {"type": "text", "textStyle": "h2", "markdown": "## Title"},
      {"type": "text", "color": "#00A3CB", "markdown": "<callout>💡 Info</callout>"}
    ],
    "position": {"position": "end", "pageId": "<DOC_ID>"}
  }'
```

#### Position Options

| Position | Syntax |
|----------|--------|
| Append to document | `{"position": "end", "pageId": "<DOC_ID>"}` |
| Prepend to document | `{"position": "start", "pageId": "<DOC_ID>"}` |
| After a specific block | `{"position": "after", "siblingId": "<BLOCK_ID>"}` |
| Before a specific block | `{"position": "before", "siblingId": "<BLOCK_ID>"}` |
| Append to daily note | `{"position": "end", "date": "today"}` |

### Updating & Deleting Blocks

```bash
# Update (only provided fields change; others preserved)
curl -s -X PUT "$CRAFT_API_URL/blocks" \
  -H "Content-Type: application/json" \
  -d '{"blocks": [{"id": "<BLOCK_ID>", "markdown": "Updated", "font": "serif"}]}'

# Delete blocks (permanent!)
curl -s -X DELETE "$CRAFT_API_URL/blocks" \
  -H "Content-Type: application/json" \
  -d '{"blockIds": ["<ID1>", "<ID2>"]}'

# Move blocks between documents
curl -s -X PUT "$CRAFT_API_URL/blocks/move" \
  -H "Content-Type: application/json" \
  -d '{"blockIds": ["<ID>"], "position": {"position": "end", "pageId": "<DOC_ID>"}}'
```

### Tasks

```bash
# List tasks (scopes: inbox, active, upcoming, logbook, document)
curl -s "$CRAFT_API_URL/tasks?scope=active"
curl -s "$CRAFT_API_URL/tasks?scope=document&documentId=<DOC_ID>"

# Create task in inbox
curl -s -X POST "$CRAFT_API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{"tasks": [{"markdown": "Task text", "taskInfo": {"scheduleDate": "tomorrow"}, "location": {"type": "inbox"}}]}'

# Create task in daily note
curl -s -X POST "$CRAFT_API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{"tasks": [{"markdown": "Task", "taskInfo": {"scheduleDate": "2025-01-20", "deadlineDate": "2025-01-22"}, "location": {"type": "dailyNote", "date": "today"}}]}'

# Create task in a document
curl -s -X POST "$CRAFT_API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{"tasks": [{"markdown": "Task", "location": {"type": "document", "documentId": "<DOC_ID>"}}]}'

# Complete task
curl -s -X PUT "$CRAFT_API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{"tasksToUpdate": [{"id": "<TASK_ID>", "taskInfo": {"state": "done"}}]}'

# Delete task
curl -s -X DELETE "$CRAFT_API_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{"idsToDelete": ["<TASK_ID>"]}'
```

### Folders

```bash
# Create folder (root level)
curl -s -X POST "$CRAFT_API_URL/folders" \
  -H "Content-Type: application/json" \
  -d '{"folders": [{"name": "New Folder"}]}'

# Create nested folder
curl -s -X POST "$CRAFT_API_URL/folders" \
  -H "Content-Type: application/json" \
  -d '{"folders": [{"name": "Sub", "parentFolderId": "<PARENT_ID>"}]}'

# Delete folder (docs move to parent or Unsorted)
curl -s -X DELETE "$CRAFT_API_URL/folders" \
  -H "Content-Type: application/json" \
  -d '{"folderIds": ["<FOLDER_ID>"]}'

# Move folder
curl -s -X PUT "$CRAFT_API_URL/folders/move" \
  -H "Content-Type: application/json" \
  -d '{"folderIds": ["<ID>"], "destination": "root"}'
# or: "destination": {"parentFolderId": "<ID>"}
```

### Collections (Structured Databases)

Collections are like Notion databases — structured tables with typed columns.

```bash
# List all collections
curl -s "$CRAFT_API_URL/collections"

# Create collection in a document
curl -s -X POST "$CRAFT_API_URL/collections" \
  -H "Content-Type: application/json" \
  -d '{
    "schema": {
      "name": "Tasks",
      "contentPropDetails": {"name": "Title"},
      "properties": [
        {"name": "Status", "type": "singleSelect", "options": [{"name": "Todo"}, {"name": "In Progress"}, {"name": "Done"}]},
        {"name": "Priority", "type": "singleSelect", "options": [{"name": "High"}, {"name": "Medium"}, {"name": "Low"}]},
        {"name": "Due Date", "type": "date"}
      ]
    },
    "position": {"position": "end", "pageId": "<DOC_ID>"}
  }'

# Get schema (use json-schema-items format to learn the property keys!)
curl -s "$CRAFT_API_URL/collections/<COL_ID>/schema?format=json-schema-items"
# ⚠️ IMPORTANT: schema returns auto-generated keys like "", "_2", "_3", "_4"
# You MUST read the schema first to know the correct keys for items

# Get items
curl -s "$CRAFT_API_URL/collections/<COL_ID>/items"

# Add items (use schema keys, NOT "title"!)
# First GET the schema to find the contentProp key (e.g. "_4" for title)
curl -s -X POST "$CRAFT_API_URL/collections/<COL_ID>/items" \
  -H "Content-Type: application/json" \
  -d '{"items": [{"<CONTENT_KEY>": "Item Title", "properties": {"<STATUS_KEY>": "Todo", "<PRIORITY_KEY>": "High"}}]}'

# Update items
curl -s -X PUT "$CRAFT_API_URL/collections/<COL_ID>/items" \
  -H "Content-Type: application/json" \
  -d '{"itemsToUpdate": [{"id": "<ITEM_ID>", "properties": {"<STATUS_KEY>": "Done"}}]}'

# Delete items
curl -s -X DELETE "$CRAFT_API_URL/collections/<COL_ID>/items" \
  -H "Content-Type: application/json" \
  -d '{"idsToDelete": ["<ITEM_ID>"]}'

# Update schema (replaces entirely — include ALL fields you want to keep)
curl -s -X PUT "$CRAFT_API_URL/collections/<COL_ID>/schema" \
  -H "Content-Type: application/json" \
  -d '{"schema": { ... }}'
```

### Comments

```bash
curl -s -X POST "$CRAFT_API_URL/comments" \
  -H "Content-Type: application/json" \
  -d '{"comments": [{"blockId": "<BLOCK_ID>", "content": "Comment text"}]}'
```

### File Upload

```bash
curl -s -X POST "$CRAFT_API_URL/upload?position=end&pageId=<DOC_ID>" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @file.png
```

Position params: `position` (start|end|before|after) + `pageId`/`date`/`siblingId`.

---

## Block Types & Formatting

### Headings

```markdown
# H1 Title          → textStyle: "h1"
## H2 Subtitle      → textStyle: "h2"
### H3 Heading      → textStyle: "h3"
#### H4 Strong      → textStyle: "h4"
```

### Inline Styles

```markdown
**bold**, *italic*, ~strikethrough~, `inline code`
[link text](https://url)
$(a+b)^2$                    ← inline equation
```

### Highlights (9 solid + 5 gradient)

```markdown
<highlight color="COLOR">text</highlight>
```

Solid: `yellow`, `blue`, `red`, `green`, `purple`, `pink`, `mint`, `cyan`, `gray`
Gradient: `gradient-blue`, `gradient-purple`, `gradient-red`, `gradient-yellow`, `gradient-brown`

### Lists

```markdown
- bullet item           → listStyle: "bullet"
1. numbered item        → listStyle: "numbered"
- [ ] todo task         → listStyle: "task", taskInfo.state: "todo"
- [x] completed task    → listStyle: "task", taskInfo.state: "done"
+ toggle (collapsible)  → listStyle: "toggle"
```

### Toggle (Collapsible) Lists — CRITICAL

Children MUST be indented 2 spaces to nest inside a toggle:

```markdown
+ Parent toggle
  - Child 1 (hidden when collapsed)
  - Child 2
  + Nested toggle
    - Deep child
```

**Use markdown mode only.** `indentationLevel` in blocks JSON is silently
ignored on insert.

### Blockquote

```markdown
> Quoted text
```

Produces block with `decorations: ["quote"]`.

### Dividers / Lines

Blocks JSON with `lineStyle`:

```json
{"type": "line", "lineStyle": "extraLight", "markdown": "***"}
{"type": "line", "lineStyle": "light", "markdown": "****"}
{"type": "line", "lineStyle": "regular", "markdown": "*****"}
{"type": "line", "lineStyle": "strong", "markdown": "******"}
```

Markdown mode: `---` produces `extraLight` by default.

### Code Blocks

Markdown mode:

````markdown
```python
def hello():
    print("Hello")
```
````

Blocks JSON (requires `rawCode`!):

```json
{"type": "code", "language": "python", "rawCode": "def hello():\n    print('Hello')", "markdown": "```python\ndef hello():\n    print('Hello')\n```"}
```

### Math Formula (TeX)

```json
{"type": "code", "language": "math_formula", "rawCode": "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}", "markdown": "```math_formula\nx = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}\n```"}
```

Inline equation in markdown: `$(a+b)^2 = a^2 + 2ab + b^2$`

### Tables

Markdown mode:

```markdown
| Col A | Col B |
| --- | --- |
| val 1 | val 2 |
```

### Images

Blocks JSON:

```json
{"type": "image", "url": "https://example.com/photo.jpg", "markdown": "![Alt](https://example.com/photo.jpg)"}
```

Craft re-hosts the image and returns a `https://r.craft.do/` URL.

### Rich URL (Link Preview)

```json
{"type": "richUrl", "url": "https://www.youtube.com/watch?v=..."}
```

### Page / Card (Sub-pages)

```json
{"type": "page", "textStyle": "page", "markdown": "Sub-page Title"}
{"type": "page", "textStyle": "card", "markdown": "Card Title"}
```

Then insert content inside using the returned page ID as `pageId`.

### Callouts (Colored Blocks)

Require blocks JSON with `color`:

```json
{"type": "text", "color": "#00A3CB", "markdown": "<callout>💡 Info</callout>"}
```

Common colors: `#00A3CB` (blue/info), `#FF3B30` (red/warning), `#34C759`
(green/success), `#FF9500` (orange/caution), `#9862E8` (purple), `#003382`
(deep blue), `#006744` (deep green), `#864d00` (brown), `#ef052a` (bright red),
`#9ea4aa` (gray).

Callouts support inline styles inside:
`<callout>**bold** and <highlight color="yellow">highlight</highlight></callout>`

### Fonts

Set via `font` in blocks JSON: (default), `serif`, `mono`, `rounded`.

### Caption

```json
{"type": "text", "textStyle": "caption", "markdown": "<caption>Small annotation</caption>"}
```

### Task Blocks in Documents

```json
{"type": "text", "listStyle": "task", "taskInfo": {"state": "todo"}, "markdown": "- [ ] Task"}
```

States: `todo`, `done`, `canceled` — NOT "completed".

### Combination Example

```json
{
  "type": "text",
  "font": "rounded",
  "textStyle": "h3",
  "color": "#9862E8",
  "markdown": "<callout>### ✨ Purple rounded heading callout</callout>"
}
```

---

## Choosing Insert Method

| Need | Use | Why |
|------|-----|-----|
| Text, lists, headings | Markdown | Clean, auto-detects types |
| Toggle lists with children | Markdown | Only way to get indentation right |
| Code blocks, tables | Either | Markdown is simpler; JSON needs `rawCode` |
| Colored callouts | Blocks JSON | Need `color` property |
| Custom fonts | Blocks JSON | Need `font` property |
| Captions | Blocks JSON | Need `textStyle: "caption"` |
| Images, richUrl, pages | Blocks JSON | Need `type` field |
| Line styles | Blocks JSON | Need `lineStyle` |
| Math formulas | Blocks JSON | Need `language: "math_formula"` + `rawCode` |
| Mixed content | Split calls | Combine markdown + blocks JSON |

---

## Gotchas & Lessons Learned

1. **Toggle indentation**: markdown mode with 2-space indent is the only way.
   `indentationLevel` in blocks JSON is silently ignored on insert.

2. **Task state values**: `todo | done | canceled`. NOT `completed`.

3. **Position `after`/`before`**: use `siblingId` (not `blockId`).

4. **Position `end`/`start`**: use `pageId` or `date`.

5. **Code blocks in JSON mode**: require `rawCode` field. Without it you get
   a validation error.

6. **Collection item keys**: the API docs say `title` but the real field name
   is the auto-generated `contentProp` key from the schema (e.g. `_4`).
   Always `GET /collections/<id>/schema?format=json-schema-items` first
   to discover the correct keys.

7. **URL-encode search terms**: Chinese and special characters in query params
   must be URL-encoded or `curl` returns 400.

8. **Accept header**: use `application/json` for reads. `text/markdown` may 502.

9. **Document delete is soft**: goes to trash, restorable via move.
   Block delete is permanent.

10. **Large inserts**: one POST can insert many blocks. Prefer fewer larger
    writes to avoid rate limits.

11. **Image re-hosting**: Craft downloads external images and re-hosts them
    at `https://r.craft.do/`. Your original URL is replaced.

12. **Collections are experimental**: the API may change. Always read the
    schema before writing items.
