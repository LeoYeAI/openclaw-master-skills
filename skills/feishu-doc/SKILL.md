---
name: feishu-doc
description: Fetch content from Feishu (Lark) Wiki, Docs, Sheets, and Bitable. Automatically resolves Wiki URLs to real entities and converts content to Markdown.
tags: [feishu, lark, wiki, doc, sheet, document, reader, writer]
---

# Feishu Doc Skill

Fetch content from Feishu (Lark) Wiki, Docs, Sheets, and Bitable. Write and update documents.

## Prerequisites

- Install `feishu-common` first.
- This skill depends on `../feishu-common/index.js` for token and API auth.

## Capabilities

- **Read**: Fetch content from Docs, Sheets, Bitable, and Wiki.
- **Create**: Create new blank documents.
- **Write**: Overwrite document content with Markdown.
- **Append**: Append Markdown content to the end of a document.
- **Blocks**: List, get, update, and delete specific blocks.

## Long Document Handling (Unlimited Length)

To generate long documents (exceeding LLM output limits of ~2000-4000 tokens):
1. **Create** the document first to get a `doc_token`.
2. **Chunk** the content into logical sections (e.g., Introduction, Chapter 1, Chapter 2).
3. **Append** each chunk sequentially using `feishu_doc_append`.
4. Do NOT try to write the entire document in one `feishu_doc_write` call if it is very long; use the append loop pattern.

## Usage

```bash
# Read
node index.js --action read --token <doc_token>

# Create
node index.js --action create --title "My Doc"

# Write (Overwrite)
node index.js --action write --token <doc_token> --content "# Title\nHello world"

# Append
node index.js --action append --token <doc_token> --content "## Section 2\nMore text"
```

## Configuration

Create a `config.json` file in the root of the skill or set environment variables:

```json
{
  "app_id": "YOUR_APP_ID",
  "app_secret": "YOUR_APP_SECRET"
}
```

Environment variables:
- `FEISHU_APP_ID`
- `FEISHU_APP_SECRET`
