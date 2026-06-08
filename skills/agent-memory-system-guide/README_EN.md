# agent-memory-system-guide

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

GitHub repository: [cjke84/agent-memory-system-guide](https://github.com/cjke84/agent-memory-system-guide)

Canonical OpenClaw skill id: `memory-system`

An Agent long-term memory guide for OpenClaw, Codex, and Obsidian workflows.

It helps you build a durable local-first memory stack with a compact `MEMORY.md`, daily notes, session recovery files, and Obsidian archiving. OpenViking is included as an optional enhancement for semantic recall and summary support, not as a hard dependency.

GitHub release archive: [v0.1.0](https://github.com/cjke84/agent-memory-system-guide/releases/tag/v0.1.0)

Current published skill version: `1.1.5`

## What it is

This skill explains how to build a durable memory stack for agents: a compact `MEMORY.md`, daily notes, memory distillation, and Obsidian backups.
It is a local-first workflow and file contract, not a hosted memory platform.
OpenViking is an optional enhancement for semantic recall and summary support.
Treat OpenViking, `memory_search`, or future memory services as optional recall backends rather than replacements for the local recovery layer.

Best fit:
- Agents that need persistent memory
- Agents that should keep daily notes and distill stable facts
- Users who want Obsidian as the long-term archive

## How to use

1. Install the skill.
2. Copy `templates/SESSION-STATE.md` and `templates/working-buffer.md`, then use them with `MEMORY.md` and daily notes.
3. Distill stable facts into long-term memory and keep raw notes in daily files.
4. Archive stable knowledge into Obsidian.

## File boundaries

- `SESSION-STATE.md` uses the compact repository template: `当前任务`, `已完成`, `卡点`, `下一步`, and `恢复信息`
- Do not expand it into a second detailed schema such as `Task`, `Status`, `Owner`, `Last Updated`, or `Cleanup Rule`
- If another workflow already emits those fields, merge them back into the compact sections instead of creating new headings
- `working-buffer.md` is the only short-term scratchpad; if another skill has a working buffer or WAL concept, it should reuse this file
- `MEMORY.md` is for startup-time quick reference
- `memory/` is for daily notes and deeper archive material
- Overlap between `MEMORY.md` and `memory/` is acceptable, but their retrieval roles are different
- Lookup order: `SESSION-STATE.md` first, then recent daily notes, then `MEMORY.md` or `memory_search`, and only then Obsidian or deeper archives

## Memory layers

- `SESSION-STATE.md`: active recovery state for the interrupted task
- `working-buffer.md`: rough notes, temporary decisions, and pre-distillation scratch space
- `MEMORY.md`: distilled long-term memory for stable preferences, conventions, decisions, and recurring pitfalls
- `memory/`: daily notes and project-scoped raw history
- Obsidian, `memory_search`, OpenViking, or another external tool: deeper archive or optional recall layer

Practical boundary:
- Use memory for durable profile and collaboration facts.
- Use daily notes for volatile execution history.
- Reach for archive or semantic recall only after the local recovery files stop being enough.

## Stable profile and project scope

- Bias `MEMORY.md` toward stable profile: preferences, naming conventions, architecture decisions, recurring pitfalls, and facts that should survive startup.
- Keep fast-changing execution detail in `SESSION-STATE.md`, `working-buffer.md`, and recent daily notes.
- If one workspace spans multiple projects, include a date, repo, or project tag when distilling notes into `MEMORY.md` so later retrieval stays scoped without introducing a new required schema.

## Memory capture

- Use `templates/memory-capture.md` as a low-friction end-of-task capture sheet.
- During the task, write rough notes into `working-buffer.md` under `临时决策`, `新坑`, and `待蒸馏`.
- After the task, spend 30 seconds generating candidate memory before deciding what belongs in `MEMORY.md`.
- To bootstrap those files in a real workspace, run `python3 scripts/memory_capture.py --workspace /path/to/workspace` or `python3 scripts/memory_capture.py bootstrap --workspace /path/to/workspace`.

## Practical Examples

### Workflow examples

### First-time workspace bootstrap

A first-time workspace bootstrap should start with copying the template files, then running `python3 scripts/memory_capture.py bootstrap --workspace /path/to/workspace` so your workspace immediately contains `SESSION-STATE.md`, `working-buffer.md`, and a refreshed `memory-capture.md`. Keep `MEMORY.md` as an intentional file you create and maintain yourself.

### End-of-task memory capture

The end-of-task memory capture rhythm comes down to converting the rough notes in `working-buffer.md` into candidate memories in `templates/memory-capture.md` while things are still fresh. `memory-capture.md` keeps entries like `候选决策` and `候选踩坑` tidy so the actual `MEMORY.md` edits stay concise and intentional.

### Daily note distillation

Daily note distillation is how you keep long-term memory lean. After closing out the day, review the most recent Markdown in `memory/`, pick the facts that other agents should recall, and weave them into `MEMORY.md`. Keep the original daily note for context, and rely on the distilled summary for quick lookups. This daily note distillation step keeps the long-term file small without losing the raw source.

### Memory is not generic RAG

This workflow treats memory as a layered system rather than a single retrieval bucket. `MEMORY.md` holds stable profile and durable collaboration facts, `memory/` keeps raw execution history, and Obsidian or optional semantic tools support deeper recall when needed. That keeps the workflow auditable and portable without turning this repository into a memory API product.

### Report examples

### Maintenance report command

The maintenance report command documents your workspace state without touching the memories themselves. Run `python3 scripts/memory_capture.py report --workspace /path/to/workspace` to print sections for Supported files, Directories, Latest daily note, and Warnings. The command scans the supported files (`MEMORY.md`, `SESSION-STATE.md`, `working-buffer.md`, `memory-capture.md`), walks the `memory/` and `attachments/` directories recursively, counts every file under `attachments/`, and counts only date-named daily notes such as `YYYY-MM-DD.md` under `memory/`. It identifies the lexicographically latest matching daily-note path under `memory/` as the latest daily note, so index or reference Markdown files do not skew the result. It exits 0 if the workspace is readable and only returns a non-zero status when the workspace directory is missing or cannot be opened, but it still prints the warning section whenever a problem occurs.

Example stdout:

```text
Memory workspace report for /path/to/workspace

Supported files:
  MEMORY.md: present
  SESSION-STATE.md: present
  working-buffer.md: present
  memory-capture.md: present

Directories:
  memory: 2 daily note(s)
  attachments: 1 attachment(s)

Latest daily note: memory/2026-03-25.md

Warnings: none
```

Example warning-state stdout:

```text
Memory workspace report for /path/to/workspace

Supported files:
  MEMORY.md: present
  SESSION-STATE.md: missing
  working-buffer.md: present
  memory-capture.md: present

Directories:
  memory: 0 daily note(s)
  attachments: 0 attachment(s)

Latest daily note: none

Warnings:
  - Missing supported file: SESSION-STATE.md
  - memory directory has no daily notes
  - attachments directory is empty
```

Example Markdown report output:

Generate the file with:

```text
python3 scripts/memory_capture.py report --workspace /path/to/workspace --output /path/to/workspace-report.md
```

The generated `/path/to/workspace-report.md` will look like:

```markdown
# Memory workspace report

- Workspace: /path/to/workspace

## Supported files
- `MEMORY.md`: present
- `SESSION-STATE.md`: present
- `working-buffer.md`: present
- `memory-capture.md`: present

## Directories
- `memory`: 2 daily note(s)
- `attachments`: 1 attachment(s)

## Latest daily note
- memory/2026-03-25.md

## Warnings
- none
```

## Cross-device Backup and Restore

- Export a portable backup zip on the old device with `python3 scripts/memory_capture.py export --workspace /path/to/workspace --output /path/to/memory-backup.zip`.
- Move the archive to a new device and restore with `python3 scripts/memory_capture.py import --workspace /path/to/new-workspace --input /path/to/memory-backup.zip`.
- Default import is conservative: it always creates a pre-import backup, then performs an overwrite-style restore without deleting extra supported files already present in the target workspace.
- Use `python3 scripts/memory_capture.py import --clean --workspace /path/to/new-workspace --input /path/to/memory-backup.zip` when you want a deterministic clean restore of the supported memory surface.
- The archive includes `MEMORY.md`, `SESSION-STATE.md`, `working-buffer.md`, `memory-capture.md`, `memory/`, and `attachments/` when they exist.

## Obsidian setup guide

Keep the memory workflow inside one predictable vault layout:

```text
vault/
  MEMORY.md
  SESSION-STATE.md
  working-buffer.md
  memory-capture.md
  memory/
  attachments/
```

Recommended setup:
- Put daily notes in `memory/` so the CLI report and Obsidian navigation use the same path.
- Put pasted files, screenshots, and evidence in `attachments/` so embeds and backup exports stay portable.
- Use `templates/OBSIDIAN-NOTE.md` for durable notes that need frontmatter, backlinks, and embeds.
- Enable `Calendar` for date-based daily note browsing.
- Enable `Dataview` for querying `type`, `status`, `tags`, and `related`.
- Enable `Templater` for note scaffolding only; avoid making the core memory workflow depend on plugin automation.

Minimal Dataview query example:

```text
TABLE type, status, tags, related
FROM "memory"
WHERE status != "archived"
SORT updated desc
```

Sync guidance:
- Sync the whole vault, or at least the subset containing `MEMORY.md`, `memory/`, and `attachments/`.
- Keep unrelated plugin cache folders out of your sync rules.
- Obsidian sync remains optional; the local file workflow should still work on its own.

## Scheduled maintenance examples

Automate reporting and backup, not direct long-term-memory rewrites.

Daily report example with `crontab`:

```text
0 9 * * * cd /path/to/repo && python3 scripts/memory_capture.py report --workspace /path/to/workspace --output /path/to/workspace-report.md
```

Weekly backup example with `crontab`:

```text
0 18 * * 5 cd /path/to/repo && python3 scripts/memory_capture.py export --workspace /path/to/workspace --output /path/to/backups/
```

Practical rule:
- Schedule checks, reports, and backups automatically.
- Do not automatically write distilled content into `MEMORY.md`; keep that review step manual.

## Sync options and trade-offs

- `Obsidian Sync`: best if Obsidian is your main interface and you want the smoothest multi-device vault sync.
- `iCloud` or other consumer cloud drives: workable for personal vaults, but watch for conflict copies and slower large-attachment sync.
- `git`: useful for versioned text history and reviewable note changes, but awkward for binary attachments and less technical collaborators.
- `Syncthing`: strong for peer-to-peer sync and local control, but it needs more disciplined setup across devices.

Recommendation:
- Pick one primary sync path for the vault to reduce conflict handling.
- Keep export/import as the conservative recovery path even when sync is enabled.
- If you use `git`, treat it as text-file versioning rather than a full attachment backup system.

## Obsidian-native notes

- Use `templates/OBSIDIAN-NOTE.md` for durable notes: YAML frontmatter, wikilinks, embeds, and attachment conventions.
- With Dataview, you can query your notes by `type`, `status`, `tags`, and `related`.

## Included files

- `SKILL.md`: skill contract and workflow
- `manifest.toml`: publish metadata for OpenClaw / ClawHub style release workflows
- `INSTALL.md`: a copy-paste installation prompt for agents
- `templates/SESSION-STATE.md` and `templates/working-buffer.md`: recovery templates
- `templates/memory-capture.md`: end-of-task candidate-memory template
- `scripts/memory_capture.py`: bootstrap, export backup, import restore, and maintenance report helper

Publish note: `manifest.toml` is the source of truth for skill versioning and the Xiaping skill id used for updates.
