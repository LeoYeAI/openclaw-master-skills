# Metadata And Bootstrap Safety Design

## Scope

This design covers two focused improvements:

1. Eliminate published version drift across repository entrypoints by treating `manifest.toml` as the source of truth for the current published skill version.
2. Make `scripts/memory_capture.py bootstrap` preserve an existing `memory-capture.md` by default instead of overwriting candidate memory.

The design explicitly does not change import/restore semantics, archive format, or broader README structure in this iteration.

## Goals

- Prevent users from seeing conflicting published versions in `manifest.toml`, `README*`, and `INSTALL.md`.
- Prevent accidental loss of in-progress candidate memory when bootstrap is re-run in an existing workspace.
- Keep the CLI and docs changes small enough to land safely in a repository with ongoing uncommitted work.

## Non-Goals

- Introduce a documentation generation pipeline for all README content.
- Redesign `import` to support destructive clean restores.
- Rewrite the broader bilingual documentation structure.

## Current Problems

### Metadata drift

The repository currently repeats release-facing metadata in multiple files. `manifest.toml` has the current version, while other entrypoints independently restate it. The result is a release process that depends on careful manual synchronization.

### Bootstrap overwrite risk

`create_bootstrap_files()` always rewrites `memory-capture.md`. That is safe for first-time workspace setup but unsafe for existing workspaces, because the file is meant to hold end-of-task candidate memory. Re-running bootstrap can erase work users have not yet distilled into `MEMORY.md`.

## Proposed Design

### 1. Version consistency contract

Keep `manifest.toml` as the source of truth for the published version number. In this iteration, enforce that contract with tests and by updating checked-in docs to match the manifest.

Implementation choices:

- Add a test that parses `manifest.toml` for `version`.
- Assert that `README.md`, `README_CN.md`, `README_EN.md`, and `INSTALL.md` all mention the same published version string.
- Update `INSTALL.md` and `manifest.toml` to match the already-published README version.

This deliberately avoids a generator script for now. The repository is small, and a hard consistency check gives most of the benefit without introducing a new maintenance tool.

### 2. Safe bootstrap semantics

Change bootstrap so it preserves an existing `memory-capture.md` by default.

Behavior:

- If `memory-capture.md` does not exist, bootstrap creates it with the generated timestamp header and template body.
- If `memory-capture.md` already exists, bootstrap leaves it untouched and reports `kept`.
- Add an explicit `--refresh-capture` flag for users who want to intentionally regenerate the file.

Why this design:

- Default-preserve behavior is the safest interpretation for a file that may contain unsaved candidate memory.
- An explicit refresh flag preserves the current ability to regenerate a clean capture sheet when desired.
- The flag keeps the command self-explanatory without changing archive or restore behavior.

## CLI Surface

`bootstrap` gains:

- `--refresh-capture`: overwrite `memory-capture.md` with regenerated content.

Default bootstrap output becomes status-based:

- `SESSION-STATE.md: created|kept`
- `working-buffer.md: created|kept`
- `memory-capture.md: created|kept|refreshed`

## Testing Strategy

### Metadata consistency

- Add a contract test that extracts `version` from `manifest.toml` and verifies all release-facing entrypoints mention that exact version.

### Bootstrap preservation

- Add a test proving bootstrap preserves an existing `memory-capture.md` by default.
- Add a test proving `bootstrap --refresh-capture` overwrites the file and emits the regenerated timestamped content.

Regression confidence comes from running the full existing pytest suite because many tests already lock the repository contracts around docs and CLI behavior.

## Risks And Mitigations

### Risk: Existing users expect bootstrap to refresh capture files

Mitigation: preserve that capability with `--refresh-capture` and document the safer default in the CLI help and docs.

### Risk: More metadata fields drift later

Mitigation: this iteration only solves version drift. If title, release link, or skill id drift become recurring problems, a later iteration can add a small metadata sync script driven by `manifest.toml`.

## Files Expected To Change

- `scripts/memory_capture.py`
- `INSTALL.md`
- `manifest.toml`
- `tests/test_release_manifest_contract.py`
- `tests/test_memory_capture_script.py`

## Acceptance Criteria

- `INSTALL.md` shows the same published version as `manifest.toml`.
- A test fails if any release-facing entrypoint drifts from the manifest version.
- Running `python3 scripts/memory_capture.py --workspace <dir>` preserves an existing `memory-capture.md`.
- Running `python3 scripts/memory_capture.py bootstrap --workspace <dir> --refresh-capture` regenerates `memory-capture.md`.
- The full pytest suite passes.
