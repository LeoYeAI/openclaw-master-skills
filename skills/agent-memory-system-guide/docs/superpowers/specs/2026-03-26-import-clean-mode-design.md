# Import Clean Mode Design

## Scope

This design adds an explicit clean-restore mode to `scripts/memory_capture.py import` while preserving the current default import behavior.

The change is intentionally narrow:

- Keep default `import` semantics compatible with the current release.
- Add `--clean` as an opt-in mode for deterministic restore behavior.
- Update tests and docs so the distinction between the two modes is explicit.

This iteration does not redesign archive format, backup naming, or export behavior.

## Goals

- Remove ambiguity around what `import` actually does today.
- Provide a deterministic restore mode for users who want the target workspace to exactly match the archive contents within the supported memory scope.
- Avoid breaking existing users who rely on the current overwrite-style behavior.

## Non-Goals

- Change default `import` into a destructive clean restore.
- Add selective restore by path.
- Change archive manifest structure.
- Add interactive confirmation prompts.

## Current Behavior

The current `import` flow:

1. Validates the archive manifest.
2. Creates a pre-import backup of the target workspace's supported files and directories.
3. Restores archive members by writing them into the target workspace.

This means imported files overwrite matching files, but extra files already present in the target workspace remain untouched. In practice this is an overwrite/merge style restore, not a clean restore.

## Problem

The docs use restore-oriented language, which can reasonably lead users to expect the target workspace to match the archive after import. That expectation is not always true when the target workspace contains extra daily notes, attachments, or supported files not present in the archive.

## Options Considered

### Option 1: Add explicit `--clean` and preserve current default

Default `import` remains backward compatible. `import --clean` first removes supported files and directories from the target workspace, then restores archive contents.

Pros:

- Preserves current behavior for existing users and scripts.
- Adds a deterministic restore path for users who need it.
- Keeps CLI intent explicit and easy to document.

Cons:

- Two restore modes must be documented and tested.

### Option 2: Change default `import` into clean restore

Pros:

- Simplest mental model.

Cons:

- Backward incompatible.
- Higher risk of surprising data deletion in existing workflows.

### Option 3: Documentation-only clarification

Pros:

- Lowest implementation cost.

Cons:

- Does not solve the need for deterministic restore behavior.

## Recommended Design

Adopt Option 1.

### CLI

Add a new flag to the `import` subcommand:

- `--clean`: remove supported target memory files and directories before archive restore.

### Supported clean scope

The clean operation only touches the existing supported import/export scope:

- Files: `MEMORY.md`, `SESSION-STATE.md`, `working-buffer.md`, `memory-capture.md`
- Directories: `memory/`, `attachments/`

No other files or directories in the workspace are removed.

### Import behavior

#### Default `import`

- Validate archive.
- Create pre-import backup of supported target content when present.
- Restore archive members by overwrite.
- Leave extra supported files not present in the archive untouched.

#### `import --clean`

- Validate archive.
- Create pre-import backup of supported target content when present.
- Remove existing supported files and directories from the target workspace.
- Restore archive members from the archive.

This guarantees that the supported restore surface matches the archive contents after import.

## Implementation Notes

- Add a helper that removes supported files and directories under the target workspace.
- Run the clean helper only after archive validation and backup creation succeed.
- Keep path handling restricted to the current supported scope to avoid expanding the blast radius.
- Preserve current success messages and add a clear line when clean mode runs, for example `Import mode: clean`.

## Testing Strategy

Add focused tests for both semantics:

1. Default import keeps extra target files that are outside the archive contents but inside the supported scope.
2. `import --clean` removes extra target files in the supported scope before restore.
3. `import --clean` still creates a pre-import backup before deletion.

Run the full pytest suite afterward to confirm no regression to bootstrap, export, report, or doc contracts.

## Documentation Updates

Update `README.md`, `README_CN.md`, `README_EN.md`, and `SKILL.md` to say:

- Default import is conservative: pre-import backup plus overwrite-style restore.
- Use `--clean` when the goal is a deterministic clean restore of the supported memory surface.

## Risks And Mitigations

### Risk: Users misunderstand `--clean` as deleting the whole workspace

Mitigation: document the exact supported scope and keep deletion limited to supported files and directories.

### Risk: Clean mode deletes content unexpectedly

Mitigation: keep pre-import backup mandatory before clean removal and preserve default mode for non-destructive compatibility.

## Files Expected To Change

- `scripts/memory_capture.py`
- `tests/test_memory_capture_script.py`
- `README.md`
- `README_CN.md`
- `README_EN.md`
- `SKILL.md`

## Acceptance Criteria

- `import` without `--clean` retains extra supported files not present in the archive.
- `import --clean` removes extra supported files and directories before restore.
- Both modes still create a pre-import backup when target supported content exists.
- Docs clearly distinguish conservative import from clean restore.
- Full pytest suite passes.
