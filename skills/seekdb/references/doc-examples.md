# seekdb Documentation Examples

Complete workflow examples for common seekdb documentation queries.

## Example 1: Keyword Search (Normal Flow)

**User Query**: "How do I use vector search in seekdb?"

**Process**:

1. **Resolve skill directory**
   ```
   Read SKILL.md → extract parent directory as <skill_dir>
   ```

2. **Search catalog**
   Search for lines containing "vector search" in `<skill_dir>references/seekdb-docs-catalog.jsonl`.

   Found matches:
   ```json
   {"path": "200.develop/600.search/300.vector-search/100.vector-search-intro.md",
    "description": "This document provides an overview of vector search in seekdb, covering core concepts, supported vector data types, indexing methods, and search operations.",
    "branch": "V1.1.0"}
   {"path": "200.develop/600.search/300.vector-search/300.vector-similarity-search.md",
    "description": "This document explains vector similarity search methods in seekdb...",
    "branch": "V1.1.0"}
   ```

3. **Fetch documents (remote)**
   - URL: `https://raw.githubusercontent.com/oceanbase/seekdb-doc/V1.1.0/en-US/200.develop/600.search/300.vector-search/100.vector-search-intro.md` (and other matched paths with their `branch`)
   - Use content to answer

---

## Example 2: Remote Fallback with Branch-Aware URL

**User Query**: "How to integrate seekdb with Claude Code?"

**Process**:

1. **Resolve skill directory** → `<skill_dir>`

2. **Search catalog**
   Search for lines containing "claude code" in `<skill_dir>references/seekdb-docs-catalog.jsonl`.

   Found:
   ```json
   {"path": "300.integrations/300.developer-tools/700.claude-code.md",
    "description": "This guide explains how to use the seekdb plugin with Claude Code...",
    "branch": "V1.0.0"}
   ```
   Note: `branch` is `V1.0.0` — this file only exists in the V1.0.0 branch (shared across versions via `showInAllVersions`).

3. **Fetch document (remote)**
   - URL: `https://raw.githubusercontent.com/oceanbase/seekdb-doc/V1.0.0/en-US/300.integrations/300.developer-tools/700.claude-code.md`

---

## Example 3: Multiple Matches

**User Query**: "Tell me about seekdb indexes"

**Process**:

1. **Resolve skill directory** → `<skill_dir>`

2. **Search catalog**
   Search for lines containing "index" in `<skill_dir>references/seekdb-docs-catalog.jsonl`.

   Found multiple matches:
   ```json
   {"path": "200.develop/600.search/300.vector-search/200.vector-index/100.vector-index-overview.md", "description": "...vector index types...", "branch": "V1.1.0"}
   {"path": "200.develop/200.design-database-schema/35.multi-model/300.char-and-text/300.full-text-index.md", "description": "...full-text indexes...", "branch": "V1.1.0"}
   {"path": "200.develop/200.design-database-schema/40.create-index-in-develop.md", "description": "...creating indexes...", "branch": "V1.1.0"}
   ```

3. **Fetch all relevant documents** from `https://raw.githubusercontent.com/oceanbase/seekdb-doc/[branch]/en-US/[path]` using each entry's `branch` and `path`.

4. **Provide comprehensive answer** covering vector indexes, full-text indexes, and index creation syntax.