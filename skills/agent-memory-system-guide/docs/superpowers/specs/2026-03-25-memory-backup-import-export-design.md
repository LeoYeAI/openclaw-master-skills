# Memory Backup Import Export Design

## Goal

Add a portable backup export and import workflow so a memory workspace can be moved to a new device and restored into nearly the same operational state.

The workflow should:
- export the current memory workspace into a single portable archive
- include enough metadata to validate and understand the backup
- restore files onto a new device by importing the archive
- protect existing target files by creating a pre-import backup before overwrite
- keep the existing bootstrap flow intact

## Non-Goals

- Do not add a remote sync service.
- Do not require a database or third-party storage provider.
- Do not attempt byte-for-byte machine cloning outside the memory workspace.
- Do not add encryption in this iteration.

## Proposed Design

### Archive format

Use a zip archive as the primary export format. The archive should contain:
- `manifest.json` with export metadata
- `MEMORY.md` when present
- `SESSION-STATE.md` when present
- `working-buffer.md` when present
- `memory-capture.md` when present
- `memory/` when present
- `attachments/` when present

Zip is the right default because it preserves directory structure, is easy to move between devices, and matches the user's goal of restoring a familiar workspace state rather than just copying one document.

### Manifest

`manifest.json` should describe:
- archive format version
- export timestamp
- source workspace path
- included relative paths

The manifest gives import enough structure to validate the archive before writing files.

### Export behavior

Export should scan a workspace for the supported memory files and optional directories, then create a timestamped zip archive in a chosen output directory or exact output path.

If none of the supported files exist, export should fail with a clear message instead of producing an empty archive.

### Import behavior

Import should first validate that:
- the zip exists
- `manifest.json` exists
- all archived paths are relative and safe

Before restoring files, import should create a timestamped backup archive of any existing target memory files in the destination workspace. After that safety backup succeeds, import should overwrite destination files with the archive contents.

### CLI shape

Extend the current script into subcommands:
- `bootstrap`
- `export`
- `import`

Keep `bootstrap` available so the repo does not regress for current users.

## Files to Update

- `scripts/memory_capture.py`
- `tests/test_memory_capture_script.py`
- `README.md`
- `README_CN.md`
- `README_EN.md`
- `SKILL.md`
- `manifest.toml`

## Testing Strategy

Add script tests that verify:
- export creates a zip archive with `manifest.json` and the expected files
- export fails when no memory files exist
- import restores files into a new workspace
- import creates a pre-import backup when target files already exist
- existing bootstrap behavior still works

## Success Criteria

- A user can export their memory workspace on one device and import it on another.
- Import preserves safety by backing up current destination memory files first.
- The repo documentation explains the migration workflow clearly.
- Automated tests cover the new CLI behaviors.
