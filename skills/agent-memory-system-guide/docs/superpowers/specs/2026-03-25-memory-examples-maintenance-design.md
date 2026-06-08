# Memory Examples and Maintenance Design

## Goal

Improve the repository in two ways:
- add more practical, copyable examples so users can apply the workflow without translating abstract guidance into their own format
- add lightweight maintenance automation that helps users inspect the health of a memory workspace and generate a maintenance report draft

## Non-Goals

- Do not turn the repository into a full memory management product.
- Do not add AI-based summarization, ranking, or automatic long-term memory distillation.
- Do not auto-edit `MEMORY.md`, daily notes, or Obsidian notes.
- Do not add a web UI, database, or background service.

## Proposed Design

### Documentation examples

Add concrete examples to the README files that show realistic usage patterns:
- first-time workspace bootstrap
- end-of-task `memory-capture.md` usage
- distilling a daily note into `MEMORY.md`
- cross-device export and import workflow
- maintenance report generation workflow

The examples should be short, runnable, and directly aligned with the existing file conventions in the repo.

### Maintenance automation

Extend `scripts/memory_capture.py` with a new `report` subcommand.

The command should:
- inspect the workspace for supported memory files and directories
- count daily notes and attachments
- identify the most recent daily note when possible
- emit actionable warnings for obvious maintenance gaps
- optionally write a Markdown maintenance report to a target path

The command should stay deterministic and rule-based. It should not infer memory importance or rewrite user files.

### Report contents

The generated report should include:
- generation timestamp
- file presence summary
- memory and attachment counts
- recent daily note information
- maintenance warnings
- suggested next actions

This makes the automation useful for regular check-ins while keeping the repository within its current scope.

## CLI Shape

The helper script will support:
- `bootstrap`
- `export`
- `import`
- `report`

`report` should accept:
- `--workspace`
- `--generated-at` optional override
- `--output` optional Markdown file path

If `--output` is omitted, it should print the report to stdout.

## Files to Update

- `scripts/memory_capture.py`
- `tests/test_memory_capture_script.py`
- `tests/test_memory_capture_contract.py`
- `README.md`
- `README_CN.md`
- `README_EN.md`
- `SKILL.md`

## Testing Strategy

Add tests that verify:
- `report` succeeds on a minimal workspace
- `report` emits warnings for missing expected files
- `report --output` writes a Markdown report
- documentation mentions the new examples and maintenance workflow

## Success Criteria

- A user can copy a concrete example for common workflows without guesswork.
- A user can run one command to understand the current maintenance state of the memory workspace.
- The automation remains lightweight, local, and non-destructive.
