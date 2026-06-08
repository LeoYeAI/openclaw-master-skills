# agent-memory-system-guide

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

GitHub repository: [cjke84/agent-memory-system-guide](https://github.com/cjke84/agent-memory-system-guide)

English overview: This repository provides a practical local-first Agent long-term memory workflow for OpenClaw and Codex. It combines a compact `MEMORY.md`, daily notes, session recovery files, and Obsidian archiving, with OpenViking as an optional enhancement rather than a hard dependency.

Canonical OpenClaw skill id: `memory-system`

## Start Here

- [English README](README_EN.md)
- [中文介绍](README_CN.md)
- [Install Skill for Agent](INSTALL.md)
- GitHub release archive: [v0.1.0](https://github.com/cjke84/agent-memory-system-guide/releases/tag/v0.1.0)
- Current published skill version: `1.1.5`

## What it is

An Agent long-term memory guide for OpenClaw and Obsidian workflows.
It is a local-first workflow and file contract, not a hosted memory platform.
OpenViking is an optional enhancement for semantic recall and summary support.
It is not required for the core workflow.
Treat OpenViking, `memory_search`, or future memory services as optional recall backends that sit behind the local recovery layer instead of replacing it.

Best fit:
- Agents that need persistent memory
- Agents that should keep daily notes and distill stable facts
- Users who want Obsidian as the long-term archive

## Quick start

1. Install the skill.
2. Copy `templates/SESSION-STATE.md` and `templates/working-buffer.md`, then use them together with `MEMORY.md` and daily notes.
3. Distill stable facts into long-term memory and keep raw notes in daily files.
4. Archive stable knowledge into Obsidian.

## File boundaries

- `SESSION-STATE.md` uses the compact repository template only; do not expand it with a second detailed schema such as `Task`, `Status`, `Owner`, `Last Updated`, or `Cleanup Rule`
- If an external workflow already emits those fields, merge them back into the compact sections instead of adding new headings
- `working-buffer.md` is the only short-term scratchpad / WAL file for rough notes
- `MEMORY.md` is for startup-time quick reference
- `memory/` is for daily notes and deeper archive material
- Overlap between `MEMORY.md` and `memory/` is acceptable, but their retrieval roles are different
- Lookup order: `SESSION-STATE.md` first, then recent daily notes, then `MEMORY.md` or `memory_search`, and only then Obsidian or deeper archives

## Memory layers

- `SESSION-STATE.md`: the active recovery layer for the interrupted task
- `working-buffer.md`: rough notes, temporary decisions, and pre-distillation scratch space
- `MEMORY.md`: distilled long-term memory for stable preferences, conventions, decisions, and recurring pitfalls
- `memory/`: daily notes and project-scoped raw history
- Obsidian, `memory_search`, OpenViking, or another external tool: deeper archive or optional recall layer

Practical boundary:
- Use memory for durable profile and collaboration facts.
- Use daily notes for volatile execution history.
- Use archive or semantic search only after the local recovery files stop being enough.

## Stable profile and project scope

- Bias `MEMORY.md` toward stable profile: preferences, naming conventions, architecture decisions, recurring pitfalls, and facts that should survive startup.
- Keep fast-changing execution detail in `SESSION-STATE.md`, `working-buffer.md`, and recent daily notes.
- If one workspace serves multiple projects, include a date, repo, or project tag when distilling notes into `MEMORY.md` so later lookup stays scoped without introducing a new required schema.

## Memory capture

- Use `templates/memory-capture.md` as a low-friction end-of-task capture sheet.
- During the task, write rough notes into `working-buffer.md` under `临时决策`, `新坑`, and `待蒸馏`.
- After the task, spend 30 seconds turning those rough notes into candidate memory instead of forcing a full `MEMORY.md` rewrite.
- To bootstrap those files in a real workspace, run `python3 scripts/memory_capture.py --workspace /path/to/workspace` or `python3 scripts/memory_capture.py bootstrap --workspace /path/to/workspace`.

## Practical Examples

### Workflow examples

### First-time workspace bootstrap

First-time workspace bootstrap is about creating the recovery-layer files with a single command. Copy the templates for `SESSION-STATE.md`, `working-buffer.md`, and `memory-capture.md`, then run `python3 scripts/memory_capture.py bootstrap --workspace /path/to/workspace` (or omit `bootstrap` for the default bootstrap path) so the helper creates `SESSION-STATE.md`, `working-buffer.md`, and a refreshed `memory-capture.md` in one go. Keep `MEMORY.md` as a deliberate, user-maintained file.

### End-of-task memory capture

End-of-task memory capture keeps the workflow light. Fill `working-buffer.md` while the task is running, then spend 30 seconds after the task wrapping up by pasting the best bits into `memory-capture.md` under `候选决策`, `候选踩坑`, and `候选长期记忆`. The template keeps the handoff to `MEMORY.md` or a weekly distillation note explicit without overloading the long-term file.

### Distill a daily note into `MEMORY.md`

Daily note distillation closes the loop. Pick the notes you wrote in the latest `memory/YYYY-MM-DD.md`, pull the key decisions and learnings into your `MEMORY.md`, and tag the source with a date or project reference. Keep the daily note for reference, and copy only the distilled insights that other agents or future sessions actually need on startup.

### Memory is not generic RAG

This workflow treats memory as a layered system rather than a single retrieval bucket. `MEMORY.md` is for stable profile and durable collaboration facts; `memory/` keeps raw execution history; Obsidian and optional semantic tools help with deep recall when needed. That keeps the local workflow auditable and portable without turning the repository into a memory API product.

### Report examples

### Maintenance report command

`python3 scripts/memory_capture.py report --workspace /path/to/workspace` collects the current workspace picture and helps you keep it honest. The report command always exits 0 when it can read the workspace; it only returns a non-zero status if the directory does not exist or cannot be read. Its stdout and Markdown outputs share four sections: **Supported files**, **Directories**, **Latest daily note**, and **Warnings**. Supported files are `MEMORY.md`, `SESSION-STATE.md`, `working-buffer.md`, and `memory-capture.md`; the scanned directories are `memory/` and `attachments/`. The report counts every file inside `attachments/` recursively and only date-named daily notes like `YYYY-MM-DD.md` under `memory/`, then identifies the lexicographically latest matching daily-note path as the latest daily note. Non-daily Markdown files in `memory/` are ignored so index or reference notes do not skew the maintenance summary.

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

- Export a portable backup zip with `python3 scripts/memory_capture.py export --workspace /path/to/workspace --output /path/to/memory-backup.zip`.
- Move that zip to a new device, then restore with `python3 scripts/memory_capture.py import --workspace /path/to/new-workspace --input /path/to/memory-backup.zip`.
- Default import is conservative: it creates a pre-import backup of the destination memory files, then performs an overwrite-style restore without deleting extra supported files that are already present.
- Use `python3 scripts/memory_capture.py import --clean --workspace /path/to/new-workspace --input /path/to/memory-backup.zip` when you want a clean restore of the supported memory surface.
- The backup archive includes `MEMORY.md`, `SESSION-STATE.md`, `working-buffer.md`, `memory-capture.md`, `memory/`, and `attachments/` when present.

## Obsidian setup guide

Use one vault folder to keep the memory workspace predictable. A practical layout is:

```text
vault/
  MEMORY.md
  SESSION-STATE.md
  working-buffer.md
  memory-capture.md
  memory/
  attachments/
```

Recommended configuration:
- Keep daily notes under `memory/` so the CLI report and Obsidian browsing agree on the same location.
- Keep media and pasted files under `attachments/` so embeds and backup archives stay portable.
- Use `templates/OBSIDIAN-NOTE.md` for long-lived notes that need frontmatter, backlinks, and embeds.
- Enable `Calendar` if you want date-based browsing for daily notes.
- Enable `Dataview` if you want to query notes by `type`, `status`, `tags`, and `related`.
- Enable `Templater` only for note scaffolding; keep the memory workflow readable without plugin lock-in.

Minimal Dataview query example:

```text
TABLE type, status, tags, related
FROM "memory"
WHERE status != "archived"
SORT updated desc
```

Sync guidance:
- Sync the vault or the subset containing `MEMORY.md`, `memory/`, and `attachments/`.
- Avoid mixing sync rules with generated cache folders from unrelated plugins.
- Keep Obsidian sync optional; the local file workflow should still work without it.

## Scheduled maintenance examples

Use automation for reporting and backup, not for directly rewriting long-term memory.

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

- `Obsidian Sync`: best when you already live inside Obsidian and want the smoothest multi-device vault sync with fewer manual rules.
- `iCloud` or other consumer cloud drives: fine for personal vaults, but be careful with conflict copies and delayed sync on large attachment sets.
- `git`: good for versioned text history and reviewable note changes, but less comfortable for binary attachments and non-technical users.
- `Syncthing`: good for peer-to-peer sync and local control, but requires a bit more setup discipline across devices.

Recommendation:
- Use one primary sync path for the vault to avoid duplicated conflict resolution.
- Keep export/import as the conservative recovery path even if sync is enabled.
- If you use `git`, treat it as versioning for text files, not a replacement for attachment-aware backup.

## Files

- `SKILL.md`: skill contract and workflow
- `manifest.toml`: publish metadata for OpenClaw / ClawHub style release workflows
- `INSTALL.md`: a copy-paste installation prompt for agents
- `README_EN.md` / `README_CN.md`: bilingual introductions
- `templates/SESSION-STATE.md` and `templates/working-buffer.md`: recovery templates
- `templates/memory-capture.md`: end-of-task candidate-memory template
- `templates/OBSIDIAN-NOTE.md`: Obsidian note template (frontmatter, links, embeds)
- `scripts/memory_capture.py`: bootstrap, export backup, import restore, and maintenance report helper

Publish note: `manifest.toml` is the source of truth for skill versioning and the Xiaping skill id used for updates.
