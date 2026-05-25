# Knowledge Base Changelog

## 2026-02-27

### Updated
- v1.5.0: Removed `tags` from summary files — category directories and descriptive filenames provide sufficient semantic structure
- v1.4.0: Removed `id`, `captured`, `source_type` from file frontmatter — derivable from filename. Removed `created` from _category.md. Removed `raw` path field — convention-based (`../raw/{same-filename}`)
- v1.3.0: Removed `related` field from summary files — cross-entry relationships are discovered at recall time by the agent via search, tags, or embeddings
- v1.2.0: Added books-to-read extraction (Step 9 in Ability 1)
- v1.2.0: Added git commit reminder after all write abilities
- v1.2.0: Fixed _category.md reference mismatch in Ability 4

### Categories
- Initialized knowledge base with `unsorted/` directory
