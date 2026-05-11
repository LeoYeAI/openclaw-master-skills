# ADR-009: Document Ingestion for RAG

## Status
Accepted

## Context
Agents need to search not just their own memories but also external documents — PDFs, web pages, text files, Markdown. This is the foundation for Retrieval-Augmented Generation (RAG) within Palaia.

## Decision

### Core Principle: RAG as Additive Extension
Document ingestion reuses the existing Store, entry format, and search infrastructure. Ingested documents are stored as regular Palaia entries with additional frontmatter for source attribution. No breaking changes to existing functionality.

### Chunking Strategy
- **Sliding window** with configurable `chunk_size` (words) and `chunk_overlap` (words).
- **Sentence boundary respecting**: chunks split at sentence boundaries rather than mid-sentence.
- **Minimum chunk size**: chunks shorter than 10 words are skipped (too short to be useful).

### Entry Frontmatter for Ingested Chunks
```yaml
---
scope: private
project: company-docs
tags: [rag, ingested]
source: document.pdf
source_page: 3
chunk_index: 0
chunk_total: 12
ingested_at: 2026-03-11T23:00:00Z
---
[chunk text]
```

Fields `source`, `chunk_index`, `chunk_total`, and `ingested_at` are added to the standard entry format. `source_page` is only present for PDFs.

### Supported Formats
- `.txt`, `.md` — read directly (stdlib)
- `.html`, `.htm` — parsed with `html.parser` (stdlib)
- URLs — fetched with `urllib` (stdlib), then parsed as HTML or plain text
- `.pdf` — requires `pdfplumber` (optional dependency)
- Directories — recursively process all supported files

### Optional Dependencies
PDF support via `pdfplumber` is optional. When not installed, attempting to ingest a PDF gives a clear error message with install instructions. All other formats use stdlib only.

```toml
[project.optional-dependencies]
pdf = ["pdfplumber>=0.7"]
```

### Scope and Project Isolation
Ingested documents follow the same scope/project system as regular entries:
- `--scope` controls visibility (default: `private`)
- `--project` assigns to a Palaia project for isolated search
- All standard scope rules apply

### RAG Query Output
`palaia query --rag` outputs a formatted context block with source attribution, suitable for direct injection into LLM prompts. Without `--rag`, query output is unchanged.

## Consequences
- No new storage format or index — everything goes through the existing Store
- Ingested entries appear in normal `palaia query` and `palaia list` results
- Source attribution via frontmatter enables tracing back to original documents
- PDF support is gracefully optional — no hard dependency added
- Deduplication works normally (content hash prevents re-ingesting same text)
