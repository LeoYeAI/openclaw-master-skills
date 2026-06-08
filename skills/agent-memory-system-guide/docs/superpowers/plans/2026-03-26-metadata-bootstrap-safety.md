# Metadata And Bootstrap Safety Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove published-version drift across repository entrypoints and make bootstrap preserve existing `memory-capture.md` content by default.

**Architecture:** Keep `manifest.toml` as the single source of truth for published version checks, enforced by tests. Update the bootstrap CLI to preserve existing candidate memory unless the caller explicitly requests regeneration with `--refresh-capture`.

**Tech Stack:** Python 3, pytest, argparse, repository Markdown docs

---

### Task 1: Lock version consistency to the manifest

**Files:**
- Modify: `tests/test_release_manifest_contract.py`
- Modify: `manifest.toml`
- Modify: `INSTALL.md`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path
import re


def test_release_entrypoints_match_manifest_version():
    repo_root = Path(__file__).resolve().parents[1]
    manifest_text = (repo_root / 'manifest.toml').read_text(encoding='utf-8')
    match = re.search(r'^version = "([^"]+)"$', manifest_text, re.MULTILINE)
    assert match is not None
    version = match.group(1)

    for path in ['README.md', 'README_CN.md', 'README_EN.md', 'INSTALL.md']:
        text = (repo_root / path).read_text(encoding='utf-8')
        assert f'`{version}`' in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_release_manifest_contract.py::test_release_entrypoints_match_manifest_version -q`
Expected: FAIL because the manifest version does not yet match every release-facing entrypoint.

- [ ] **Step 3: Write minimal implementation**

Update the inconsistent metadata so `manifest.toml`, `INSTALL.md`, and the README entrypoints all expose the same current published version.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_release_manifest_contract.py::test_release_entrypoints_match_manifest_version -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_release_manifest_contract.py manifest.toml INSTALL.md
git commit -m "test: enforce published version consistency"
```

### Task 2: Preserve existing memory-capture content by default

**Files:**
- Modify: `tests/test_memory_capture_script.py`
- Modify: `scripts/memory_capture.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_bootstrap_preserves_existing_memory_capture_file(tmp_path: Path):
    capture_path = tmp_path / 'memory-capture.md'
    capture_path.write_text('# memory-capture.md\n\nkeep me\n', encoding='utf-8')

    result = run_script(tmp_path, '--generated-at', '2026-03-26T09:00:00+08:00')

    assert result.returncode == 0
    assert capture_path.read_text(encoding='utf-8') == '# memory-capture.md\n\nkeep me\n'
    assert 'memory-capture.md: kept' in result.stdout


def test_bootstrap_refresh_capture_overwrites_existing_memory_capture_file(tmp_path: Path):
    capture_path = tmp_path / 'memory-capture.md'
    capture_path.write_text('# memory-capture.md\n\nold content\n', encoding='utf-8')

    result = run_command(
        'bootstrap',
        '--workspace',
        str(tmp_path),
        '--generated-at',
        '2026-03-26T09:05:00+08:00',
        '--refresh-capture',
    )

    assert result.returncode == 0
    capture_text = capture_path.read_text(encoding='utf-8')
    assert 'Generated at: 2026-03-26T09:05:00+08:00' in capture_text
    assert '候选决策' in capture_text
    assert 'memory-capture.md: refreshed' in result.stdout
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_memory_capture_script.py -k "preserves_existing_memory_capture_file or refresh_capture_overwrites_existing_memory_capture_file" -q`
Expected: FAIL because bootstrap always rewrites `memory-capture.md` and the parser does not yet accept `--refresh-capture`.

- [ ] **Step 3: Write minimal implementation**

Update the CLI parser and bootstrap implementation to preserve existing capture files by default and refresh only when explicitly requested.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_memory_capture_script.py -k "preserves_existing_memory_capture_file or refresh_capture_overwrites_existing_memory_capture_file" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_memory_capture_script.py scripts/memory_capture.py
git commit -m "feat: preserve capture file during bootstrap"
```

### Task 3: Run regression verification

**Files:**
- Modify: none
- Test: `tests/test_release_manifest_contract.py`
- Test: `tests/test_memory_capture_script.py`
- Test: full `tests/`

- [ ] **Step 1: Run focused regression tests**

Run: `pytest tests/test_release_manifest_contract.py tests/test_memory_capture_script.py -q`
Expected: PASS

- [ ] **Step 2: Run full test suite**

Run: `pytest -q`
Expected: PASS with all repository contract tests green.

- [ ] **Step 3: Inspect git diff**

Run: `git diff -- scripts/memory_capture.py manifest.toml INSTALL.md tests/test_release_manifest_contract.py tests/test_memory_capture_script.py`
Expected: Only the scoped metadata, parser, bootstrap, and test changes appear.

- [ ] **Step 4: Commit**

```bash
git add scripts/memory_capture.py manifest.toml INSTALL.md tests/test_release_manifest_contract.py tests/test_memory_capture_script.py
git commit -m "feat: harden bootstrap and release metadata"
```
