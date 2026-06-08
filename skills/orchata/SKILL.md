---
name: orchata-rag
description: Knowledge management and RAG platform with tree-based document indexing. Use this skill to search, browse, and manage Orchata knowledge bases via MCP tools.
metadata:
  version: 1.0.0
  author: Orchata AI
---

# Orchata Skills

This document describes how to effectively use Orchata, a RAG (Retrieval-Augmented Generation) platform with tree-based document indexing. Load this into your context to interact with Orchata knowledge bases.

## What is Orchata?

Orchata is a knowledge management platform that:

- **Organizes documents into Spaces** - Logical containers for related content
- **Uses tree-based indexing** - Documents are parsed into hierarchical structures with sections, summaries, and page ranges
- **Provides semantic search** - Find relevant content using natural language queries
- **Exposes MCP tools** - AI assistants can directly manage and query knowledge bases

## Core Concepts

### Spaces

A **Space** is a container for related documents. Think of it as a folder with semantic search capabilities.

- Each space has a `name`, `description`, and optional `icon`
- Descriptions are used by `smart_query` to recommend relevant spaces
- Spaces can be archived (soft-deleted)

### Documents

A **Document** is content within a space. Supported formats include:

- PDF (text-based and scanned with OCR)
- Word documents (.docx)
- Excel spreadsheets (.xlsx)
- PowerPoint presentations (.pptx)
- Markdown files (.md)
- Plain text files (.txt)
- Images (PNG, JPG, etc.)

**Document Status:**

| Status | Description |
| ------ | ----------- |
| `PENDING` | Uploaded, waiting for processing |
| `PROCESSING` | Being parsed and indexed |
| `COMPLETED` | Ready for queries |
| `FAILED` | Processing error occurred |

**Important:** Only query documents with `status: "COMPLETED"`. Other statuses won't return results.

### Document Trees

Documents are indexed into **hierarchical tree structures**:

- Each tree has nodes representing sections/chapters
- Nodes contain: `title`, `summary`, `startPage`, `endPage`, `textContent`
- Trees enable precise navigation of large documents

### Queries

Two types of queries are available:

1. **`query_spaces`** - Search document content using tree-based reasoning
2. **`smart_query`** - Discover which spaces are relevant for a query

---

## MCP Tools Reference

### Space Management

#### list_spaces

List all knowledge spaces in the organization.

```text
list_spaces
list_spaces with status="active"
list_spaces with page=1 pageSize=20
```

**Parameters:**

- `page` (number, optional): Page number (default: 1)
- `pageSize` (number, optional): Items per page (default: 10)
- `status` (string, optional): Filter by `active`, `archived`, or `all`

---

#### manage_space

Create, get, update, or delete a space.

```text
manage_space with action="create" name="Product Docs" description="Technical documentation"
manage_space with action="create" name="Legal" description="Case files" icon="briefcase"
manage_space with action="get" id="space_abc123"
manage_space with action="update" id="space_abc123" description="Updated description"
manage_space with action="delete" id="space_abc123"
```

**Parameters:**

- `action` (string, required): `create`, `get`, `update`, or `delete`
- `id` (string): Space ID (required for get/update/delete)
- `name` (string): Space name (required for create)
- `description` (string, optional): Space description
- `icon` (string, optional): Icon name. Defaults to "folder"
- `slug` (string, optional): URL-friendly identifier
- `isArchived` (boolean, optional): Archive status (for update)

**Valid Icons:**
`folder`, `book`, `file-text`, `database`, `package`, `archive`, `briefcase`, `inbox`, `layers`, `box`

If an invalid icon is provided, the tool returns an error with the list of valid options.

---

### Document Management

#### list_documents

List documents in a space.

```text
list_documents with spaceId="space_abc123"
list_documents with spaceId="space_abc123" status="completed"
list_documents with spaceId="space_abc123" status="all"
```

**Parameters:**

- `spaceId` (string, required): Space ID
- `page` (number, optional): Page number
- `pageSize` (number, optional): Items per page (max: 100)
- `status` (string, optional): Filter by status. Values: `pending`, `processing`, `completed`, `failed`, or `all`. Omitting returns all documents.

**Note:** Status values are case-insensitive (`completed` and `COMPLETED` both work).

---

#### save_document

Upload or upsert documents (single or batch).

**Single document:**

```text
save_document with spaceId="space_abc123" filename="guide.md" content="# Guide\n\nContent here..."
```

**Batch upload:**

```text
save_document with spaceId="space_abc123" documents=[{"filename": "doc1.md", "content": "..."}, {"filename": "doc2.md", "content": "..."}]
```

**Parameters:**

- `spaceId` (string, required): Space ID
- `filename` (string): Filename (required for single)
- `content` (string): Content (required for single)
- `documents` (array, optional): Array of `{filename, content, metadata}` for batch
- `metadata` (object, optional): Custom key-value pairs

---

#### get_document

Get document content by ID or filename. Returns processed markdown text.

```text
get_document with spaceId="space_abc123" id="doc_xyz789"
get_document with spaceId="space_abc123" filename="guide.md"
get_document with spaceId="*" filename="guide.md"
```

**Parameters:**

- `spaceId` (string, required): Space ID, or `*` to search all spaces (requires filename)
- `id` (string, optional): Document ID
- `filename` (string, optional): Filename

**Notes:**

- Either `id` or `filename` is required
- Use `spaceId="*"` to search all spaces when you know the filename but not the space
- For completed documents, returns the extracted markdown text (not raw PDF binary)
- When using `*`, the response includes the `spaceId` where the document was found

---

#### update_document

Update document content or metadata.

```text
update_document with spaceId="space_abc123" id="doc_xyz789" content="New content..."
update_document with spaceId="space_abc123" id="doc_xyz789" append=true content="Additional content"
```

**Parameters:**

- `spaceId` (string, required): Space ID
- `id` (string, required): Document ID
- `content` (string, optional): New content
- `metadata` (object, optional): New metadata
- `append` (boolean, optional): Append instead of replace
- `separator` (string, optional): Separator for append mode

---

#### delete_document

Permanently delete a document.

```text
delete_document with spaceId="space_abc123" id="doc_xyz789"
```

**Parameters:**

- `spaceId` (string, required): Space ID
- `id` (string, required): Document ID

---

### Query Tools

#### query_spaces

Search documents across one or more spaces using tree-based reasoning.

```text
query_spaces with query="How do I authenticate API requests?"
query_spaces with query="installation guide" spaceIds="space_abc123"
query_spaces with query="error handling" spaceIds=["space_abc", "space_def"] topK=10
```

**Parameters:**

- `query` (string, required): Natural language search query
- `spaceIds` (string or array, optional): Space ID(s) to search. Omit or use `*` for all spaces
- `topK` (number, optional): Maximum results (default: 10)
- `compact` (boolean, optional): Use compact format (default: false). See **When to Use Compact** below.

**When to Use Compact:**

| Mode | When to use | What you get |
| ---- | ----------- | ------------ |
| `compact=false` (default) | **Most queries.** Any time you need actual data, facts, numbers, dates, or details from documents. | Full results with document metadata, tree context, page ranges, and complete content. |
| `compact=true` | Broad discovery queries where you only need to know *which* documents are relevant, not their content. | Minimal results: just content snippet, source filename, and score. |

**Rule of thumb:** Default to `compact=false`. Only use `compact=true` when you're browsing/surveying and don't need the actual content yet.

**Response (compact=true format):**

```json
{
  "results": [
    {
      "content": "Relevant text content...",
      "source": "filename.pdf",
      "score": 0.95
    }
  ],
  "total": 5
}
```

---

#### smart_query

Discover which spaces are relevant for a query using LLM reasoning.

```text
smart_query with query="How do I install the SDK?"
smart_query with query="billing questions" maxSpaces=3
```

**Parameters:**

- `query` (string, required): Query to find relevant spaces for
- `maxSpaces` (number, optional): Maximum spaces to return (default: 5)

**Response:**

```json
{
  "query": "How do I install the SDK?",
  "relevantSpaces": [
    {"spaceId": "space_abc123", "relevance": "Contains SDK installation guides"},
    {"spaceId": "space_def456", "relevance": "Has developer tutorials"}
  ],
  "totalFound": 2
}
```

**Use case:** When you don't know which space to search, use `smart_query` first to discover relevant spaces, then use `query_spaces` with those space IDs.

---

### Tree Visibility Tools

These tools let you explore the hierarchical structure of indexed documents.

#### get_document_tree

Get the tree structure of a document showing sections, summaries, and page ranges.

```text
get_document_tree with spaceId="space_abc123" documentId="doc_xyz789"
```

**Parameters:**

- `spaceId` (string, required): Space ID
- `documentId` (string, required): Document ID

**Response:**

```json
{
  "documentId": "doc_xyz789",
  "totalPages": 45,
  "totalNodes": 12,
  "nodes": [
    {
      "nodeId": "0001",
      "title": "Introduction",
      "summary": "Overview of the system architecture...",
      "pages": "1-5",
      "depth": 0
    },
    {
      "nodeId": "0002",
      "title": "Installation",
      "summary": "Step-by-step installation guide...",
      "pages": "6-12",
      "depth": 0
    }
  ]
}
```

**Use case:** Use this to understand a document's structure before drilling into specific sections.

---

#### get_tree_node

Get the full text content of a specific tree node/section.

```text
get_tree_node with documentId="doc_xyz789" nodeId="0002"
```

**Parameters:**

- `documentId` (string, required): Document ID
- `nodeId` (string, required): Node ID from the tree structure

**Response:**

```json
{
  "documentId": "doc_xyz789",
  "filename": "manual.pdf",
  "nodeId": "0002",
  "title": "Installation",
  "summary": "Step-by-step installation guide...",
  "pages": "6-12",
  "depth": 0,
  "content": "## Installation\n\nTo install the software, follow these steps:\n\n1. Download the installer...\n\n..."
}
```

**Use case:** After viewing the tree structure, use this to read the full content of a specific section.

---

## Workflow Patterns

### Pattern 1: Search for Information (Default Approach)

**For most questions, a single `query_spaces` call is all you need.** Start here before trying multi-step workflows.

```text
query_spaces with query="your question"
```

This searches all spaces with full details (compact=false by default). One call, done.

**If you want to narrow to specific spaces:**

```text
query_spaces with query="your question" spaceIds="known_space_id"
```

**If you truly don't know which spaces exist:**

```text
smart_query with query="your question"
# Then use the returned spaceIds:
query_spaces with query="your question" spaceIds=["returned_space_id"]
```

> **Avoid over-searching.** The multi-step workflow (`smart_query` -> `query_spaces` -> `get_document_tree` -> `get_tree_node`) is rarely necessary. For most questions, a single `query_spaces` call returns the answer directly. Only escalate to tree browsing if results are insufficient.

### Pattern 2: Look Up Specific Data

When looking for specific facts, numbers, dates, names, or details:

**Just query directly -- one call:**

```text
query_spaces with query="total amount on invoice #1234"
```

The default `compact=false` returns full content with document metadata, so you get the actual data you need in one step. Do **not** use `compact=true` for data lookups -- it strips the detail you need.

### Pattern 3: Browse a Large Document

When you need to navigate a large document's structure:

1. **Get the document structure:**

   ```text
   get_document_tree with spaceId="space_id" documentId="doc_id"
   ```

2. **Identify relevant sections** from the node titles and summaries

3. **Read specific sections:**

   ```text
   get_tree_node with documentId="doc_id" nodeId="relevant_node_id"
   ```

### Pattern 4: Add New Content

When adding documents to a knowledge base:

1. **Find or create the appropriate space:**

   ```text
   list_spaces
   # or
   manage_space with action="create" name="New Space" description="..."
   ```

2. **Upload the content:**

   ```text
   save_document with spaceId="space_id" filename="document.md" content="..."
   ```

3. **Wait for processing** (status will change from PENDING -> PROCESSING -> COMPLETED)

4. **Verify it's ready:**

   ```text
   list_documents with spaceId="space_id" status="COMPLETED"
   ```

---

## manage_space - Valid Icons

When creating or updating a space, use one of these icon values:

- `folder` (default)
- `book`
- `file-text`
- `database`
- `package`
- `archive`
- `briefcase`
- `inbox`
- `layers`
- `box`

Invalid icons will return a helpful error message with the list of valid options.

---

## list_documents - Status Parameter

The `status` parameter accepts the following values (case-insensitive):

- `"all"` - Returns documents in any status (COMPLETED, FAILED, PENDING, PROCESSING)
- `"completed"` - Returns only successfully processed documents
- `"failed"` - Returns only documents that failed processing (includes `errorMessage` field)
- `"pending"` - Returns documents waiting to be processed
- `"processing"` - Returns documents currently being processed

Documents with `status="FAILED"` will include an `errorMessage` field explaining what went wrong during processing.

---

## save_document - Processing Workflow

Documents are processed asynchronously:

1. `save_document` returns immediately with `status="PROCESSING"`
2. Background job generates embeddings and indexes the document (typically 1-3 seconds)
3. Status changes to `"COMPLETED"` when ready
4. Document becomes searchable via `query_spaces`

**To check completion status:**

- Use `get_document` to check a specific document's status
- Use `list_documents` with `status="processing"` to see all processing documents
- Use `list_documents` with `status="failed"` to see any failures

**Example:**

```javascript
// Save document
const result = await save_document({...});
// result.document.status === "PROCESSING"

// Check status after a moment
const doc = await get_document({id: result.document.id});
// doc.status === "COMPLETED" (when ready)
```

---

## get_tree_node - Content Availability

`get_tree_node` may return `"(No text content cached for this node)"` for certain nodes. This occurs for:

- Structural/organizational nodes without associated text content
- Nodes that serve as section headers in the tree hierarchy

**This is expected behavior.**

**To read actual document content:**

- Use `get_document` to retrieve the full processed markdown
- Use `query_spaces` to search and retrieve relevant content chunks

The tree structure (via `get_document_tree`) is always available and shows document organization, summaries, and page ranges.

---

## Best Practices

### DO

- **Start with a single `query_spaces` call** - it usually has the answer in one step
- **Use `compact=false` (the default) for most queries** - you get full content and context
- **Check document status** before querying - only `COMPLETED` documents are searchable
- **Use descriptive queries** - natural language works best
- **Use tree tools for large documents** - navigate structure instead of reading everything
- **Write good space descriptions** - they're used by `smart_query` for discovery

### DON'T

- **Don't over-search** - avoid multi-step workflows (`smart_query` -> `query_spaces` -> `get_document_tree` -> `get_tree_node`) when a single `query_spaces` call suffices
- **Don't use `compact=true` for data lookups** - it strips the content you need; only use it for broad discovery
- **Don't query PENDING/PROCESSING documents** - they won't return results
- **Don't use very short queries** - more context = better results
- **Don't forget to check processing status** after uploading new documents

---

## Error Handling

Common errors and solutions:

| Error | Cause | Solution |
| ----- | ----- | -------- |
| "Document not found" | Wrong ID or no access | Verify the document ID with `list_documents` |
| "Space not found" | Wrong ID or archived | Use `list_spaces` to find valid space IDs |
| Empty search results | Document not COMPLETED or no matches | Check document status; try broader query |
| "Tree not found" | Document uses vector indexing or not processed | Check if document status is COMPLETED |
| "Invalid icon" | Icon name not in allowed list | Use one of: folder, book, file-text, database, package, archive, briefcase, inbox, layers, box |
| "No text content cached" | Tree node content not cached | This is normal for structural nodes; use `get_document` for full content |

### Troubleshooting Tips

**If `save_document` fails:**

1. Verify the space exists with `manage_space with action="get" id="..."`
2. Ensure content is valid text/markdown
3. Check that the space is not archived

**If `list_documents` returns 0 results:**

1. Try `status="all"` or omit the status parameter entirely
2. Verify the spaceId is correct with `list_spaces`
3. Check if documents are still processing (status="processing")

**If `get_tree_node` returns no content:**

- Some nodes are structural and don't have cached text content
- Use `get_document` to get the full processed document text instead
- Or use `query_spaces` to search for specific content

---

## Quick Reference

| Task | Tool | Example |
| ---- | ---- | ------- |
| List all spaces | `list_spaces` | `list_spaces with status="active"` |
| Create a space | `manage_space` | `manage_space with action="create" name="Docs"` |
| List documents | `list_documents` | `list_documents with spaceId="..."` |
| Upload content | `save_document` | `save_document with spaceId="..." content="..."` |
| Get document text | `get_document` | `get_document with spaceId="..." id="..."` |
| Search content | `query_spaces` | `query_spaces with query="..."` |
| Find relevant spaces | `smart_query` | `smart_query with query="..."` |
| View doc structure | `get_document_tree` | `get_document_tree with spaceId="..." documentId="..."` |
| Read a section | `get_tree_node` | `get_tree_node with documentId="..." nodeId="..."` |
