# Knowledge Base

Personal knowledge base managed by the `knowledge` skill.

## Structure

- `unsorted/` -- Newly captured knowledge awaiting categorization
- `{category}/` -- Categorized knowledge (e.g., `fitness/`, `parenting/`, `design/`)

Each directory contains:
- `raw/` -- Full extracted content from source artifacts
- `summary/` -- Concise summaries with key points and takeaways

Category directories also contain `_category.md` defining their scope.

## File Naming

`{descriptive-slug}--{YYYY-MM-DD}.md`

Raw and summary files for the same artifact share the same filename.

## Usage

- **Add knowledge:** Provide a URL, YouTube link, file path, or text
- **Sort knowledge:** Sort entries from `unsorted/` into categories
- **Reorganize:** Split, merge, or rename categories
- **Search:** Grep across summaries or raw content
- **Browse:** Read `_category.md` files for scope, then individual summaries

## Changelog

See `CHANGELOG.md` for all additions and structural changes.
