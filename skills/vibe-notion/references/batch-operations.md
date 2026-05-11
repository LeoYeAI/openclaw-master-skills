# Batch Operations

Run multiple write operations in a single CLI call. Use this instead of calling the CLI repeatedly when you need to create, update, or delete multiple things at once. Saves tokens and reduces round-trips.

```bash
# Inline JSON
vibe-notion batch --workspace-id <workspace_id> '<operations_json>'

# From file (for large payloads)
vibe-notion batch --workspace-id <workspace_id> --file ./operations.json '[]'
```

**Supported actions** (14 total):

| Action | Description |
|--------|-------------|
| `page.create` | Create a page |
| `page.update` | Update page title, icon, or content |
| `page.archive` | Archive a page |
| `block.append` | Append blocks to a parent |
| `block.update` | Update a block |
| `block.delete` | Delete a block |
| `block.move` | Move a block to a new position |
| `comment.create` | Create a comment |
| `database.create` | Create a database |
| `database.update` | Update database title or schema |
| `database.delete-property` | Delete a database property |
| `database.add-row` | Add a row to a database |
| `database.update-row` | Update properties on a database row |
| `block.upload` | Upload a file as an image or file block |

**Operation format**: Each operation is an object with `action` plus the same fields you'd pass to the individual command handler. Example with mixed actions:

```json
[
  {"action": "database.add-row", "database_id": "<db_id>", "title": "Task A", "properties": {"Status": "To Do"}},
  {"action": "database.add-row", "database_id": "<db_id>", "title": "Task B", "properties": {"Status": "In Progress"}},
  {"action": "page.update", "page_id": "<page_id>", "title": "Updated Summary"}
]
```

**Output format**:

```json
{
  "results": [
    {"index": 0, "action": "database.add-row", "success": true, "data": {"id": "row-uuid-1", "...": "..."}},
    {"index": 1, "action": "database.add-row", "success": true, "data": {"id": "row-uuid-2", "...": "..."}},
    {"index": 2, "action": "page.update", "success": true, "data": {"id": "page-uuid", "...": "..."}}
  ],
  "total": 3,
  "succeeded": 3,
  "failed": 0
}
```

**Fail-fast behavior**: Operations run sequentially. If any operation fails, execution stops immediately. The output will contain results for all completed operations plus the failed one. The process exits with code 1 on failure, 0 on success.

```json
{
  "results": [
    {"index": 0, "action": "database.add-row", "success": true, "data": {"...": "..."}},
    {"index": 1, "action": "page.update", "success": false, "error": "Page not found"}
  ],
  "total": 3,
  "succeeded": 1,
  "failed": 1
}
```

## Bulk Operations Strategy

For large operations (tens or hundreds of items), use `--file` to avoid shell argument limits and keep things manageable.

**Step 1**: Write the operations JSON to a file, then run batch with `--file`:

```bash
# Write operations to a file (using your Write tool), then:
vibe-notion batch --workspace-id <workspace_id> --file ./operations.json '[]'
```

**Multi-pass pattern** — when new rows need to reference each other (e.g., relation properties linking row A -> row B, where both are new):

1. **Pass 1 — Create all rows** (without cross-references): Write a batch JSON file with all `database.add-row` operations, omitting relation properties that point to other new rows. Run it. Collect the returned IDs from the output.
2. **Pass 2 — Set cross-references**: Write a second batch JSON file with `database.update-row` operations that set the relation properties using the IDs from Pass 1. Run it.

```
Pass 1: Create rows A, B, C (no cross-refs) -> get IDs for A, B, C
Pass 2: Update A.predecessor=B, C.related=A (using real IDs from Pass 1)
```

This is the same result as a script, but without writing any code. Just two batch calls.

## Rate Limits

Notion enforces rate limits on its API. Batch operations run sequentially, so a large batch (30+ operations) can trigger **429 Too Many Requests** errors. To avoid this:

 **Split large batches into chunks of ~25-30 operations** per batch call
 If a batch fails mid-way with a 429, re-run with only the remaining (unprocessed) operations
 The `batch` output shows which operations succeeded before the failure — use the `index` field to determine where to resume
