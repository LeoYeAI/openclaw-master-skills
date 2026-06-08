# Import Clean Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explicit `import --clean` mode that performs a deterministic clean restore of the supported memory surface while preserving the current default import behavior.

**Architecture:** Keep the current import path as the default overwrite-style restore. Extend the import CLI with `--clean`, back it with a helper that removes only supported files and directories after backup creation, and update docs to distinguish conservative import from clean restore.

**Tech Stack:** Python 3, argparse, pathlib, zipfile, pytest, Markdown docs

---

### Task 1: Lock the two import semantics with failing tests

**Files:**
- Modify: `tests/test_memory_capture_script.py`
- Test: `tests/test_memory_capture_script.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_import_preserves_extra_supported_files_by_default(tmp_path: Path):
    source_workspace = tmp_path / 'source'
    source_memory_dir = source_workspace / 'memory'
    source_memory_dir.mkdir(parents=True)
    (source_workspace / 'MEMORY.md').write_text('# MEMORY\n\nrestored\n', encoding='utf-8')
    (source_memory_dir / '2026-03-25.md').write_text('# daily restored\n', encoding='utf-8')
    archive_path = tmp_path / 'memory-backup.zip'

    export_result = run_command(
        'export',
        '--workspace',
        str(source_workspace),
        '--output',
        str(archive_path),
        '--generated-at',
        '2026-03-26T10:00:00+08:00',
    )
    assert export_result.returncode == 0

    target_workspace = tmp_path / 'target'
    target_memory_dir = target_workspace / 'memory'
    target_memory_dir.mkdir(parents=True)
    (target_workspace / 'MEMORY.md').write_text('# MEMORY\n\nexisting\n', encoding='utf-8')
    extra_note = target_memory_dir / '2026-03-20.md'
    extra_note.write_text('# extra daily note\n', encoding='utf-8')

    result = run_command(
        'import',
        '--workspace',
        str(target_workspace),
        '--input',
        str(archive_path),
        '--generated-at',
        '2026-03-26T10:05:00+08:00',
    )

    assert result.returncode == 0
    assert extra_note.exists()
    assert 'Import mode: conservative' in result.stdout


def test_import_clean_removes_extra_supported_files_before_restore(tmp_path: Path):
    source_workspace = tmp_path / 'source'
    source_memory_dir = source_workspace / 'memory'
    source_memory_dir.mkdir(parents=True)
    (source_workspace / 'MEMORY.md').write_text('# MEMORY\n\nrestored\n', encoding='utf-8')
    (source_memory_dir / '2026-03-25.md').write_text('# daily restored\n', encoding='utf-8')
    archive_path = tmp_path / 'memory-backup.zip'

    export_result = run_command(
        'export',
        '--workspace',
        str(source_workspace),
        '--output',
        str(archive_path),
        '--generated-at',
        '2026-03-26T10:10:00+08:00',
    )
    assert export_result.returncode == 0

    target_workspace = tmp_path / 'target'
    target_memory_dir = target_workspace / 'memory'
    attachments_dir = target_workspace / 'attachments'
    target_memory_dir.mkdir(parents=True)
    attachments_dir.mkdir()
    (target_workspace / 'MEMORY.md').write_text('# MEMORY\n\nexisting\n', encoding='utf-8')
    extra_note = target_memory_dir / '2026-03-20.md'
    extra_note.write_text('# extra daily note\n', encoding='utf-8')
    extra_attachment = attachments_dir / 'old.txt'
    extra_attachment.write_text('old\n', encoding='utf-8')

    result = run_command(
        'import',
        '--workspace',
        str(target_workspace),
        '--input',
        str(archive_path),
        '--generated-at',
        '2026-03-26T10:15:00+08:00',
        '--clean',
    )

    assert result.returncode == 0
    assert not extra_note.exists()
    assert not extra_attachment.exists()
    assert (target_workspace / 'memory' / '2026-03-25.md').exists()
    assert 'Import mode: clean' in result.stdout

    backups = sorted(target_workspace.glob('memory-import-backup-*.zip'))
    assert backups
    with zipfile.ZipFile(backups[0]) as archive:
        assert archive.read('memory/2026-03-20.md').decode('utf-8') == '# extra daily note\n'
        assert archive.read('attachments/old.txt').decode('utf-8') == 'old\n'
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_memory_capture_script.py -k "preserves_extra_supported_files_by_default or clean_removes_extra_supported_files_before_restore" -q`
Expected: FAIL because the CLI does not accept `--clean`, does not emit mode lines, and current behavior does not explicitly guarantee the new semantics.

- [ ] **Step 3: Write minimal implementation**

Add the `--clean` flag and deletion helper in `scripts/memory_capture.py`:

```python
import shutil
```

```python
import_parser.add_argument(
    "--clean",
    action="store_true",
    help="Remove supported memory files and directories before restoring the archive.",
)
```

```python
def clear_supported_workspace_state(workspace: Path) -> None:
    for name in SUPPORTED_FILES:
        candidate = workspace / name
        if candidate.exists():
            candidate.unlink()
    for directory_name in SUPPORTED_DIRECTORIES:
        directory = workspace / directory_name
        if directory.exists():
            shutil.rmtree(directory)
```

```python
with zipfile.ZipFile(archive_path) as archive:
    members = safe_members_from_manifest(archive)
    backup_path = backup_existing_workspace_state(workspace, generated_at)
    if args.clean:
        clear_supported_workspace_state(workspace)
    restore_archive(archive, workspace, members)

print(f"Import mode: {'clean' if args.clean else 'conservative'}")
```

Keep equivalent final code if helper names differ, but preserve the same behavior and scope.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_memory_capture_script.py -k "preserves_extra_supported_files_by_default or clean_removes_extra_supported_files_before_restore" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_memory_capture_script.py scripts/memory_capture.py
git commit -m "feat: add clean import mode"
```

### Task 2: Update user-facing import semantics in docs

**Files:**
- Modify: `README.md`
- Modify: `README_CN.md`
- Modify: `README_EN.md`
- Modify: `SKILL.md`

- [ ] **Step 1: Write the failing contract test**

Add assertions to an existing contract test in `tests/test_memory_capture_contract.py`:

```python
assert '--clean' in readme_text
assert 'conservative' in readme_en_text
assert 'overwrite-style restore' in readme_en_text
assert '保守' in readme_cn_text
assert '--clean' in skill_text
assert 'clean restore' in skill_text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_memory_capture_contract.py -q`
Expected: FAIL because the docs do not yet mention `--clean` or the distinction between conservative import and clean restore.

- [ ] **Step 3: Write minimal documentation updates**

Update the import sections in:

- `README.md`
- `README_CN.md`
- `README_EN.md`
- `SKILL.md`

Required wording to introduce:

- Default import is conservative and overwrite-style.
- `--clean` removes supported memory files/directories before restore.
- Pre-import backup still runs in both modes.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_memory_capture_contract.py -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md README_CN.md README_EN.md SKILL.md tests/test_memory_capture_contract.py
git commit -m "docs: clarify import restore modes"
```

### Task 3: Run regression verification

**Files:**
- Modify: none
- Test: `tests/test_memory_capture_script.py`
- Test: `tests/test_memory_capture_contract.py`
- Test: full `tests/`

- [ ] **Step 1: Run focused regression tests**

Run: `pytest tests/test_memory_capture_script.py tests/test_memory_capture_contract.py -q`
Expected: PASS

- [ ] **Step 2: Run full test suite**

Run: `pytest -q`
Expected: PASS with all repository contract tests green.

- [ ] **Step 3: Inspect scoped diff**

Run: `git diff -- scripts/memory_capture.py tests/test_memory_capture_script.py tests/test_memory_capture_contract.py README.md README_CN.md README_EN.md SKILL.md`
Expected: Only import-clean implementation, tests, and doc wording changes appear.

- [ ] **Step 4: Commit**

```bash
git add scripts/memory_capture.py tests/test_memory_capture_script.py tests/test_memory_capture_contract.py README.md README_CN.md README_EN.md SKILL.md
git commit -m "feat: document deterministic clean restore"
```
