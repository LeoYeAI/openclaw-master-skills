# Deeplake Agent Skills

Agent skills for working with [Deeplake](https://deeplake.ai), the GPU database.

## Installation

```bash
npx skills add activeloopai/deeplake-skills
```

## Available Skills

| Skill                | Description                                                                                                                                         |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **deeplake-managed** | SDK for ingesting data into Deeplake managed tables (Python & Node.js/TypeScript). Use when users want to store, ingest, or query data in Deeplake. |

## Usage

Once installed, the skill is automatically available. The agent will use it when it detects tasks related to Deeplake data ingestion, querying, or management.

Example prompts:
- "Ingest these video files into Deeplake"
- "Create a Deeplake table with embeddings"
- "Query my Deeplake dataset for similar vectors"
- "Set up a PyTorch DataLoader from my Deeplake table"
- "Ingest COCO detection data into Deeplake using Node.js"

## Skill Structure

```
skills/
  deeplake-managed/
    SKILL.md        # Main agent instructions (Python + Node.js)
    reference.md    # pg_deeplake SQL reference (vector search, BM25, hybrid search)
    examples.md     # End-to-end workflow examples (Python + Node.js)
    formats.md      # Custom format classes for ingestion (Python + Node.js)
```

## License

MIT
