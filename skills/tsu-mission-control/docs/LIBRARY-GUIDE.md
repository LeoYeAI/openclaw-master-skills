# Library Guide

The Library is a curated document store where agents publish finished work — research, reports, documentation, analysis, and reference material. It's organized, searchable, and versioned.

---

## How Documents Get Into the Library

**Three ways:**

1. **Agent hook** — When an agent fires a `library:publish` event, the document goes straight into the database. This is the primary path. Agents publish research findings, status reports, API documentation, and any other lasting content.

2. **Manual creation** — Click "+ New Doc" in the Library view. Pick a type, format, collection, and write or paste content.

3. **API** — POST to `/api/library/documents` with title, content, type, format, and collection.

---

## Organization

Documents are organized on three layers:

### Collections (folders)

Top-level categories. They support nesting (sub-collections). Default collections:

| ID | Name | Icon | Use For |
|----|------|------|---------|
| `col_research` | Research | 🔬 | Competitive analysis, market data, findings |
| `col_reports` | Reports | 📊 | Status reports, metrics, summaries |
| `col_docs` | Documentation | 📖 | Technical docs, API docs, guides |
| `col_reference` | Reference | 📚 | Specifications, standards, lookup tables |
| `col_templates` | Templates | 📋 | Reusable boilerplate and configuration |
| `col_notes` | Notes | 📝 | Meeting notes, scratch work, ideas |

Create custom collections via the "+" button in the sidebar or the API.

### Document Types (what it is)

Semantic classification within collections. A "Research" collection might contain documents typed as `research`, `analysis`, or `brief`.

Types: `research`, `report`, `documentation`, `reference`, `template`, `note`, `analysis`, `brief`, `guide`, `other`

### Tags (cross-cutting labels)

Free-form labels like `#competitor`, `#q1-2026`, `#api-v2`. Documents can have multiple tags. Tags are shared with the task system.

---

## Formats and the Reading Panel

The Library supports six content formats. Each gets a specialized renderer:

| Format | Stored As | Rendered As |
|--------|-----------|-------------|
| `markdown` | Raw Markdown text | Styled HTML with headings, code blocks, lists, links |
| `html` | Raw HTML | Direct HTML render |
| `code` | Source code | Monospace with preserved whitespace |
| `json` | Raw JSON string | Auto-pretty-printed with indentation |
| `csv` | Comma-separated values | Styled table with headers |
| `text` | Plain text | Preserved whitespace, readable font |

When you click a document in the Library, the reading panel opens with the full content rendered in the appropriate format, plus metadata (author, project, word count, tags, version history).

---

## Versioning

Every content edit creates a new version. The version history shows:

- Version number
- Who changed it (agent ID or "user")
- Change note (what was modified)
- Timestamp

You can view any previous version through the API: `GET /api/library/documents/:id/versions/:v`

---

## Search

The Library uses SQLite FTS5 (Full-Text Search) for instant search across document titles, content, and excerpts. Type in the search box and results appear as you type.

Search via API: `GET /api/library/search?q=pricing+analysis`

---

## Publishing from an Agent

Add this to your agent's AGENTS.md or workspace instructions:

```markdown
## Library Publishing

When you produce research, reports, or documentation, publish to the Library:

- Use the `library:publish` hook event
- Choose the right collection (research → col_research, docs → col_docs)
- Choose the right doc_type (research, report, documentation, etc.)
- Include the full content, not just a summary
- Set format to match the content (markdown, json, csv, etc.)
```

Example hook event (sent automatically by the lifecycle hook):

```json
{
  "event": "library:publish",
  "agentId": "research",
  "data": {
    "title": "Competitor Analysis Q1 2026",
    "content": "# Full markdown content...",
    "doc_type": "research",
    "format": "markdown",
    "collection_id": "col_research",
    "projectId": "p_market_research"
  }
}
```

---

## Pinning

Pin important documents so they always appear at the top of their collection. Click the "☆ Pin" button in the reading panel or set `pinned: true` via the API.
