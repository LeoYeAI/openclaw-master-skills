# Output Format

## JSON (Default)

All commands output JSON by default for AI consumption:

```bash
# Search results
vibe-notion search "Roadmap" --workspace-id <workspace_id>
```
```json
{
  "results": [
    {
      "id": "305c0fcf-90b3-807a-bc1a-dc7cc18e0022",
      "title": "Getting Started",
      "score": 76.58
    }
  ],
  "has_more": true,
  "next_cursor": "20",
  "total": 100
}
```

```bash
# Database query — properties use human-readable field names from the collection schema
vibe-notion database query <database_id> --workspace-id <workspace_id>
```
```json
{
  "results": [
    {
      "id": "row-uuid",
      "properties": {
        "Name": "Acme Corp",
        "Status": "Active",
        "Type": "Enterprise"
      }
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

## Schema Hints (`$hints`)

`database get` and `database query` may include a `$hints` array when the database schema has issues. These are actionable warnings — follow the instructions in each hint to fix the problem.

```json
{
  "id": "collection-uuid",
  "name": "My Database",
  "schema": { "Name": "title", "Status": "select" },
  "$hints": [
    "Rollup 'Revenue Sum' depends on deleted relation 'Deals'. This rollup will return empty values. Fix: run `database delete-property <database_id> --workspace-id <workspace_id> --property \"Revenue Sum\"` to remove it."
  ]
}
```

**When `$hints` is present**: Read each hint carefully and execute the suggested fix commands. Broken properties can crash the Notion app for the user. Common issues detected:

- **Dead properties**: Soft-deleted but still in schema. Usually harmless but indicates past issues.
- **Broken rollups**: Reference deleted or missing relations. Will return empty values and may crash Notion.
- **Broken relations**: Missing target collection. May crash Notion.

If `$hints` is absent, the schema is clean — no action needed.

```bash
# Page get — returns page metadata with content blocks
vibe-notion page get <page_id> --workspace-id <workspace_id>
```
```json
{
  "id": "page-uuid",
  "title": "My Page",
  "blocks": [
    { "id": "block-1", "type": "text", "text": "Hello world" },
    { "id": "block-2", "type": "to_do", "text": "Task item" }
  ]
}
```

```bash
# With --backlinks: includes pages that link to this page/block
vibe-notion page get <page_id> --workspace-id <workspace_id> --backlinks
vibe-notion block get <block_id> --workspace-id <workspace_id> --backlinks
```
```json
{
  "id": "page-uuid",
  "title": "My Page",
  "blocks": [],
  "backlinks": [
    { "id": "linking-page-uuid", "title": "Page That Links Here" }
  ]
}
```

```bash
# Block get — collection_view blocks include collection_id and view_ids
vibe-notion block get <block_id> --workspace-id <workspace_id>
```
```json
{
  "id": "block-uuid",
  "type": "collection_view",
  "text": "",
  "parent_id": "parent-uuid",
  "collection_id": "collection-uuid",
  "view_ids": ["view-uuid"]
}
```

## Pretty (Human-Readable)

Use `--pretty` flag for formatted output on any command:

```bash
vibe-notion search "Roadmap" --workspace-id <workspace_id> --pretty
```
