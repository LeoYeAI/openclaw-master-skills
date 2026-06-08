# Agent Memory System Guide Obsidian Design

## Goal

Turn the skill into an Obsidian-native memory workflow that uses Obsidian features as first-class primitives, not just as an archive target.

The workflow should:
- preserve recovery state in `SESSION-STATE.md` and `working-buffer.md`
- store durable memory in `MEMORY.md`
- keep daily notes as raw history
- expose structured metadata for Obsidian queries
- preserve note relationships through wikilinks and backlinks
- keep attachments and embedded evidence usable inside Obsidian

OpenViking remains optional. The core workflow must still work without it.

## Non-Goals

- Do not turn OpenViking into a required dependency.
- Do not introduce a new database or external storage layer.
- Do not replace the existing memory hierarchy with a new framework.
- Do not add automation that depends on plugins being installed in every vault.

## Proposed Design

### 1. Obsidian-first note shape

Every durable note produced by the skill should follow the same structure:
- YAML frontmatter with stable metadata
- short summary
- key points
- evidence or source references
- related notes using wikilinks
- attachments or embeds when available

The default frontmatter fields should be:
- `title`
- `aliases`
- `tags`
- `type`
- `status`
- `source`
- `source_url`
- `created`
- `updated`
- `related`

This makes the output immediately usable by Obsidian search, backlinks, and Dataview.

### 2. Dataview-friendly metadata

The skill should document a fixed metadata contract that Obsidian users can query consistently.

Recommended conventions:
- `type` describes the note kind, such as `memory`, `daily`, `decision`, `task`, or `source`
- `status` describes the lifecycle, such as `draft`, `active`, `stable`, or `archived`
- `tags` contains a small curated set of topical labels
- `aliases` contains alternate names and phrases that the user may search for later
- `related` stores note slugs or links that should be surfaced together

The documentation should show one or two Dataview examples so users understand how to query the resulting notes.

### 3. Wikilink and backlink strategy

The workflow should prefer wikilinks for all internal references:
- daily note references should use `[[YYYY-MM-DD]]` style links when possible
- related memory notes should use `[[note title]]`
- the same concept should be linked consistently across summaries, decisions, and source notes

This gives Obsidian backlinks enough signal to build a useful graph without requiring extra plugins.

### 4. Embeds and attachments

The skill should preserve evidence in a way that Obsidian can render directly:
- keep local images as embeddable resources
- keep remote images as markdown image links
- preserve quoted evidence in block quotes or block embeds
- avoid stripping attachment references during note generation

Attachment handling should be described as an Obsidian convention rather than a hard dependency on a specific plugin.

### 5. Template-driven recovery

`SESSION-STATE.md` and `working-buffer.md` should remain the recovery primitives.

Template behavior:
- `SESSION-STATE.md` is the authoritative current-task snapshot
- `working-buffer.md` is the short-lived scratchpad for the active session
- both files should be easy to copy into a vault and edit manually
- the README should show that these templates are part of the recommended Obsidian setup

### 6. Optional OpenViking integration

OpenViking should remain an enhancement layer, not a core requirement.

When available:
- it can enrich recall with semantic search
- it can help summarize older notes and source material
- it should never override `SESSION-STATE.md` as the source of truth for the active task

When unavailable:
- the workflow should still function using local files only
- the user should still be able to recover work from `SESSION-STATE.md`, `working-buffer.md`, and daily notes

## Files to Update

- `SKILL.md`
- `README.md`
- `README_EN.md`
- `README_CN.md`
- `INSTALL.md` if the installation prompt needs a short Obsidian-specific note
- `tests/` for contract coverage

## Testing Strategy

Add contract tests that verify:
- `SKILL.md` mentions `frontmatter`, `wikilink`, `backlinks`, `Dataview`, `embeds`, and attachments behavior
- the README explains that OpenViking is optional
- the recovery templates remain part of the recommended setup
- the installation prompt still treats OpenViking as optional

Use small text-based assertions rather than snapshot-heavy tests so the docs can evolve without brittle failures.

## Rollout Plan

1. Update `SKILL.md` with the Obsidian-native contract.
2. Update the three README files to describe the Obsidian workflow more explicitly.
3. Update `INSTALL.md` only if needed for the new wording.
4. Add or update contract tests.
5. Run `pytest -q`.
6. Commit and push the updated repository.

## Success Criteria

- A user can read the README and understand how the skill fits into Obsidian.
- A user can copy the templates and immediately start using them in a vault.
- Obsidian notes produced by the skill are queryable and linkable without extra cleanup.
- OpenViking is clearly documented as optional.
- The repository tests pass after the doc updates.
