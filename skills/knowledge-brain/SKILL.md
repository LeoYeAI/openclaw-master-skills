---
name: knowledge
description: Capture, summarize, and organize knowledge from URLs, YouTube videos, documents, and files. Proactively recall stored knowledge when relevant.
---

# Knowledge: Capture, Summarize, and Organize

Manage a personal knowledge base that extracts content from artifacts, generates summaries, and organizes entries into fluid categories.

**When to activate this skill:**

1. **Explicit knowledge operations:** the user says "save this", "add to knowledge", "capture this article", "summarize this video", "sort knowledge", "organize categories", "import knowledge", etc.

2. **Proactive recall:** the user asks about ANY topic where the knowledge base might have relevant entries. This includes general questions like "what's a good workout routine", "how should I approach this design problem", "what do I know about sleep training", etc. When in doubt, check the knowledge base -- it is an extension of memory. Search it whenever the user's question touches a topic that could plausibly have been captured previously.

## Configuration

### Knowledge Base Path

The knowledge base path is not hardcoded. On first invocation:

1. **Check agent memory** for a previously stored knowledge base path.
2. **If no path is stored**, ask the user. Suggest `~/Documents/knowledge/` or a sensible default.
3. **Save the chosen path** to the agent's persistent memory so it persists across sessions.
4. **On subsequent invocations**, read the stored path. Do not ask again unless the path no longer exists.

### Knowledge Index in Agent Memory

The agent's persistent memory should contain a lightweight index of the knowledge base so that category awareness is always in context — even before this skill is activated. This is what makes proactive recall possible.

After any operation that changes the knowledge base structure (adding entries, sorting, creating/splitting/merging/renaming categories), update the index in agent memory. The index should look approximately like this:

```
## Knowledge Base
Path: ~/Documents/knowledge/
Categories:
- fitness: exercise routines, nutrition, recovery
- parenting: child development, sleep training, education approaches
- software-design: architecture patterns, API design, system modeling
- industrial-design: product design, materials, manufacturing
Unsorted: 3 entries
```

Keep the index under ~20 lines. Update it immediately after any structural change.

### Conventions

- **Date format:** YYYY-MM-DD (ISO 8601 date only)
- **Filename format:** `{descriptive-slug}--{YYYY-MM-DD}.md`
  - Slug: lowercase, hyphenated, 3-6 words describing the content
  - Raw and summary files for the same artifact share the same filename
- **Summary length:** 100-400 words

## Directory Structure

```
{knowledge-base-path}/
  README.md
  CHANGELOG.md
  unsorted/
    raw/
    summary/
  {category}/
    _category.md
    raw/
    summary/
```

Category directories are created on demand when knowledge is sorted into them.

### First-Run Initialization

On first invocation:
1. Resolve the knowledge base path (see Configuration above).
2. If `README.md` does not exist at the knowledge base path, create:
   - `README.md` (see README Template below)
   - `CHANGELOG.md` with an initial entry
   - `unsorted/raw/` and `unsorted/summary/` directories (use `mkdir -p` via Bash)
3. Save the resolved path to agent memory if not already stored.

### Version Control

If git is available and the knowledge base directory is not already a git repository, initialize one (`git init`). The knowledge base benefits from version control — it provides history for category reorganizations, a safety net for bulk imports, and makes it easy to sync across machines.

After meaningful operations (adding knowledge, sorting, reorganizing), commit the changes with a short descriptive message. Keep commits atomic: one commit per logical operation rather than batching unrelated changes. Do not push unless the user has configured a remote and asks to push.

---

## File Formats

### Raw File

```markdown
---
title: "{Human-readable title}"
source: "{URL, file path, or description of origin}"
---

{Full extracted content. Preserve original structure where possible.}
```

The filename carries the ID and date (`{slug}--{YYYY-MM-DD}.md`). No need to duplicate them in frontmatter.

Rules:
- Preserve content faithfully. Do not editorialize.
- For YouTube transcripts, clean auto-sub artifacts but keep `[HH:MM:SS]` timestamps at paragraph boundaries.
- For URLs, strip navigation, ads, and boilerplate. Keep the article body.

### Summary File

```markdown
---
title: "{Human-readable title}"
source: "{URL, file path, or description of origin}"
---

## Summary

{2-4 paragraphs capturing the main ideas, arguments, or content.
Write in plain, direct prose.}

## Key Points

- {Bullet point}

## Takeaways

{1-2 sentences on why this matters or how it connects to broader themes.}
```

The filename carries the ID and date. The corresponding raw file is always at `../raw/{same-filename}`. Category directories and descriptive filenames provide the semantic structure — no tags needed.

Rules:
- When generating, read the full raw content first. Capture the core argument, not surface details.
- Cross-entry relationships are discovered at recall time by the agent (via search, category context, or embeddings) rather than stored in individual files.

### _category.md

```markdown
---
category: {category-slug}
description: "{One-sentence scope definition}"
---

## {Category Name}

{1-3 sentences defining what belongs in this category and what does not.
Be specific enough to resolve ambiguity when sorting.}

## Notes

{Optional guidance on navigating this category, notable themes,
or conventions specific to this domain.}
```

### CHANGELOG.md Format

```markdown
# Knowledge Base Changelog

## YYYY-MM-DD

### Added
- [{id}] "{title}" from {source_type} -- placed in `{category}/`

### Moved
- [{id}] moved from `{old-category}/` to `{new-category}/`

### Categories
- Created `{category-name}`: {description}
- Renamed `{old-name}` to `{new-name}`
- Split `{old-name}` into `{new-name-1}` and `{new-name-2}`
- Merged `{name-1}` and `{name-2}` into `{new-name}`
```

Group entries under the current date heading. If today's heading exists, append to it.

---

## Core Abilities

### Ability 1: Create Knowledge from an Artifact

When the user provides a URL, YouTube link, file path, or content to capture:

**Step 1: Detect source type.**
- YouTube URL: contains `youtube.com/watch`, `youtu.be/`, or `youtube.com/shorts/`
- General URL: starts with `http://` or `https://`
- File path: exists on local filesystem
- Pasted text: inline content provided directly

**Step 2: Extract raw content.**

| Source | Method |
|--------|--------|
| URL | `WebFetch(url, "Extract the main article content of this page as plain text")` |
| YouTube | Bash: `yt-dlp --write-auto-sub --sub-lang "en" --skip-download --print title --print description -o "/tmp/yt-%(id)s" "{url}"` then Read the `.vtt` file and clean it (see transcript cleaning below) |
| Local file | `Read(filepath)` |
| Audio | Bash: `whisper "{path}" --output_format txt` if available; otherwise note as placeholder |
| Pasted text | Use directly |

**YouTube transcript cleaning:**
1. Remove VTT headers (`WEBVTT`, `Kind:`, `Language:`)
2. Remove timestamp lines (lines matching `XX:XX:XX.XXX --> XX:XX:XX.XXX`)
3. Remove duplicate consecutive lines
4. Collapse blank lines
5. Insert `[HH:MM:SS]` markers approximately every 60 seconds as paragraph breaks
6. Clean up via Bash pipeline, then read and format the result
7. Clean up temporary files in `/tmp/`

**Step 3: Generate descriptive slug.** Read the extracted content and produce a 3-6 word lowercase hyphenated slug. Examples:
- `deep-work-productivity-strategies--2026-02-27`
- `react-server-components-explained--2026-02-27`
- `infant-sleep-training-methods--2026-02-27`

**Step 4: Check for duplicates.** Grep across `**/raw/*.md` for the source URL in frontmatter. If found, warn the user and ask whether to overwrite or create a suffixed version.

**Step 5: Determine placement.** Consult the knowledge index in agent memory. If an existing category is an obvious fit for this content (e.g., a workout video clearly belongs in `fitness`), place it directly in that category. If the fit is ambiguous or no category matches, place it in `unsorted/`. When in doubt, use `unsorted/`.

**Step 6: Write the raw file** to `{target}/raw/{slug}--{date}.md` where `{target}` is either the chosen category or `unsorted`. Create the directory with `mkdir -p` if needed.

**Step 7: Generate the summary.** Read the full raw content. Produce a summary following the template above.

**Step 8: Write the summary file** to `{target}/summary/{slug}--{date}.md`.

**Step 9: Extract book references.** Scan the raw content and summary for mentions of books — titles, authors, "in his book...", "as described in...", ISBN references, etc. For each book found, append it to `books-to-read.md` at the knowledge base root (see Books to Read below). If the book is already listed, add this artifact's ID to its "Referenced By" column instead of creating a duplicate.

**Step 10: Update CHANGELOG.md.** Append an "Added" entry under today's date.

**Step 11: Update the knowledge index in agent memory.** If a new category was created or the unsorted count changed, update the index immediately.

**Step 12: Report to the user.** Display the title, source, summary key points, file locations, the category it was placed in (or note that it's in `unsorted/` and suggest sorting), and any books that were extracted.

### Ability 2: Sort Unsorted Knowledge

When the user asks to sort knowledge or after adding new knowledge:

1. **Enumerate unsorted entries.** Glob `unsorted/summary/*.md`. Read frontmatter for titles.

2. **Enumerate existing categories.** Glob `*/_category.md` (excluding `unsorted/`). Read each for scope.

3. **Propose categorization.** For each unsorted entry:
   - If an existing category fits, propose it.
   - If no category fits, propose creating a new one with a slug and description.
   - If the user specified a target, use that.

4. **Confirm with the user** via AskUserQuestion. Present proposed moves as a list. Wait for confirmation.

5. **Execute moves.** For each entry:
   a. Create target category directory structure if needed (`mkdir -p {category}/raw {category}/summary`).
   b. Write `_category.md` if this is a new category.
   c. Move raw file: Bash `mv unsorted/raw/{filename} {category}/raw/{filename}`.
   d. Move summary file: Bash `mv unsorted/summary/{filename} {category}/summary/{filename}`.

6. **Update CHANGELOG.md.** Record moves and new categories.

7. **Update the knowledge index in agent memory.** Reflect any new categories and the updated unsorted count.

8. **Report to the user.**

### Ability 3: Reorganize Categories

Always confirm with the user before executing any reorganization.

#### Split a Category

1. Read all summary files in the source category.
2. Propose which entries go to which new category. Confirm with user.
3. Create new category directories and `_category.md` files.
4. Move raw and summary files via Bash `mv`.
5. Delete the old empty category directory via Bash `rm -r` after confirming it is empty.
6. Update CHANGELOG.md.
7. Update the knowledge index in agent memory.

#### Merge Categories

1. Create the target category if it does not exist.
2. Move all raw and summary files from source categories to target.
3. Handle filename collisions: append `-2` suffix to both raw and summary filenames.
4. Write or update target `_category.md`.
5. Remove empty source directories.
6. Update CHANGELOG.md.
7. Update the knowledge index in agent memory.

#### Rename a Category

1. Rename directory via Bash `mv`.
2. Update `_category.md` frontmatter.
3. No changes needed in files — filenames are unchanged, raw/summary pairing holds.
4. Update CHANGELOG.md.
5. Update the knowledge index in agent memory.

### Ability 4: Recall Knowledge

When the user asks a question, references a topic, or requests context that the knowledge base may contain:

1. **Consult the knowledge index.** The memory index lists all categories with brief descriptions. Use it to identify which categories are likely relevant to the query. This narrows the search before touching any files.

2. **Locate relevant entries.** Using whatever search capabilities the agent has:
   - If the agent can search file contents (e.g., Grep, text search, embeddings), search within the identified categories' `summary/` directories for keywords related to the query.
   - If the agent can only read files, list the summary files in the relevant category directories and read their frontmatter (title) and content to find matches.
   - If neither works, read the `_category.md` files for the relevant categories and follow their notes.
   - Fall back to broader search across the full knowledge base only if category-scoped search yields nothing.

3. **Load into working context.** Read the relevant summary files fully. If deeper detail is needed, read the corresponding raw file at `../raw/{same-filename}`. The goal is to internalize the knowledge — absorb it into the current conversation context, embedding, or working memory so it informs subsequent responses.

4. **Synthesize across entries.** When multiple entries are relevant, connect them. Surface patterns, contradictions, or complementary perspectives across the loaded knowledge.

5. **Cite sources.** When drawing on loaded knowledge, reference the entry by title and ID so the user can trace back to the original artifact.

6. **Proactive recall.** When the knowledge index shows a relevant category exists, load and reference it without being asked. The knowledge base is an extension of memory — if relevant knowledge is there, use it.

### Ability 5: Import Existing Knowledge

When the user points to an existing directory, collection of files, or structured knowledge source to onboard into the knowledge base:

1. **Scan the source.** Use Glob and Read to inventory the source directory or file list. Identify:
   - File types present (markdown, text, PDF, HTML, etc.)
   - Any existing organizational structure (subdirectories, naming conventions, tags, metadata)
   - Total number of files and approximate scope

2. **Present a migration plan.** Before touching anything, report:
   - How many files were found and their types
   - Proposed category mapping (if the source has directories/folders, suggest mapping them to knowledge base categories)
   - Any files that can't be processed (binary formats, unsupported types)
   - Ask the user to confirm or adjust the plan

3. **Process each file.** For each importable file:
   a. Read the content.
   b. If the file already has structured metadata (YAML frontmatter, title, date), preserve and adapt it to the knowledge base format.
   c. If the file is unstructured, infer a title from the filename or first heading, and use the file's modification date as the captured date.
   d. Write the raw file using the standard template and naming convention.
   e. Generate a summary following the standard template.
   f. Place files according to the migration plan — either into a mapped category or into `unsorted/`.

4. **Preserve source structure as categories.** If the source has meaningful subdirectories:
   - Map each subdirectory to a knowledge base category.
   - Create `_category.md` files with descriptions inferred from the directory name and contents.
   - If the source structure is flat, place everything in `unsorted/` for manual sorting later.

5. **Verify placement.** After all files are imported, confirm entries are in appropriate categories.

6. **Update CHANGELOG.md.** Record the import as a batch operation:
   ```
   ### Imported
   - Imported {count} entries from `{source_path}`
   - Categories created: {list}
   - Entries placed in unsorted: {count}
   ```

7. **Update the knowledge index in agent memory.** Reflect all new categories and updated entry counts.

8. **Report to the user.** Summarize what was imported, where it landed, and flag anything that needs manual attention (duplicates, unprocessable files, ambiguous categorization).

Rules:
- Never modify or delete the source files. The import is a copy operation.
- If an entry with the same content or source already exists in the knowledge base, flag it as a duplicate and skip unless the user says otherwise.
- For large imports (50+ files), process in batches and report progress.
- If the source contains its own README, index, or table of contents, read it first to inform category mapping.

### After Any Ability

After completing any ability that writes or moves files (Abilities 1, 2, 3, 5), commit the changes to git if the knowledge base is a git repository. Use a short descriptive message. One commit per logical operation.

---

## Category Management Heuristics

Suggest but never execute without user confirmation.

- **Create a new category:** 3+ entries in `unsorted/` share a common theme not covered by existing categories.
- **Split a category:** 15-20+ entries with entries clearly clustering into 2+ distinct subtopics, or the `_category.md` description has become overly broad.
- **Merge categories:** Two categories with fewer than 3 entries each and significantly overlapping scopes.
- **Rename a category:** Name no longer reflects actual contents, or name is ambiguous.

After adding knowledge, briefly note if reorganization might be warranted. Example: "Note: `unsorted/` now has 5 entries about cooking. Consider creating a `cooking` category."

---

## Process Conventions

### Idempotency
Before creating a new raw file, check if a file with the same filename already exists anywhere (Glob `**/raw/{slug}--{date}.md`). If so, warn the user and ask whether to overwrite or suffix.

### Date Collisions
If two artifacts about similar topics are captured on the same day and produce the same slug, append a numeric suffix: `{slug}-2--{date}.md`.

### Empty Categories
When the last entry leaves a category, ask the user whether to delete the empty category or keep it for future use.

### Error Handling
- If WebFetch fails, report the error and ask the user to provide content another way.
- If yt-dlp fails (no subtitles available), note this in the raw file and ask if the user can provide a transcript.
- If a move operation fails, do not update CHANGELOG until the move succeeds.

### Writing Style in Summaries
- Plain, direct prose. No promotional language.
- Active voice. Specific facts over vague characterizations.

---

## Books to Read

A flat index file at the knowledge base root that automatically captures book references found in any processed artifact.

### File: `books-to-read.md`

```markdown
# Books to Read

| Title | Author | Referenced By | Date Added |
|-------|--------|---------------|------------|
| Deep Work | Cal Newport | deep-work-productivity--2026-02-27 | 2026-02-27 |
| Atomic Habits | James Clear | habit-stacking-overview--2026-02-27, morning-routine-video--2026-02-28 | 2026-02-28 |
```

### Rules

- Create this file on first use (when the first book reference is found), not during initialization.
- Each row is one book. The "Referenced By" column contains a comma-separated list of artifact IDs that mention this book.
- When a book is already in the table and a new artifact references it, append the new artifact ID to the existing row's "Referenced By" column. Do not add a duplicate row.
- Extract whatever is available: title is required, author is best-effort. If the author isn't mentioned, leave the column as `—`.
- Be conservative — only extract clear book references, not vague mentions of "a book about X".
- This file is not tracked in the memory index. It is accessed explicitly when the user asks for book recommendations or reading lists.

---

## README Template

On first-run, generate a brief `README.md` explaining the directory structure, file naming convention (`{slug}--{date}.md`), and basic usage (add, sort, reorganize, search, browse).
