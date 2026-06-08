# Memory Backup Import Export Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add zip-based memory workspace export and import so users can move their memory state to a new device and restore it safely.

**Architecture:** Extend the existing Python helper into a small subcommand CLI. `export` will package supported memory files plus a manifest into a zip archive, and `import` will validate the archive, create a pre-import safety backup of the destination state, then restore the archived files into the target workspace.

**Tech Stack:** Python 3, `argparse`, `json`, `zipfile`, plain `pytest` script tests

---

### Task 1: Add failing tests for export and import

**Files:**
- Modify: `tests/test_memory_capture_script.py`
- Test: `tests/test_memory_capture_script.py`

- [ ] **Step 1: Write the failing test**

```python
def test_export_creates_archive_with_manifest(tmp_path: Path):
    ...

def test_import_restores_files_and_backs_up_existing_state(tmp_path: Path):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_memory_capture_script.py -v`
Expected: FAIL because export and import commands do not exist yet.

- [ ] **Step 3: Write minimal implementation**

Add subcommands and archive helpers in `scripts/memory_capture.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_memory_capture_script.py -v`
Expected: PASS for the new cases.

- [ ] **Step 5: Commit**

```bash
git add tests/test_memory_capture_script.py scripts/memory_capture.py
git commit -m "feat: add memory export and import commands"
```

### Task 2: Preserve bootstrap behavior while extending the CLI

**Files:**
- Modify: `scripts/memory_capture.py`
- Test: `tests/test_memory_capture_script.py`

- [ ] **Step 1: Write the failing test**

```python
def test_bootstrap_subcommand_creates_missing_memory_files(tmp_path: Path):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_memory_capture_script.py::test_bootstrap_subcommand_creates_missing_memory_files -v`
Expected: FAIL until the script supports explicit `bootstrap`.

- [ ] **Step 3: Write minimal implementation**

Support both the new subcommand form and the legacy invocation pattern for compatibility.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_memory_capture_script.py -v`
Expected: PASS without regressing the existing bootstrap tests.

- [ ] **Step 5: Commit**

```bash
git add tests/test_memory_capture_script.py scripts/memory_capture.py
git commit -m "refactor: keep bootstrap compatible with new CLI"
```

### Task 3: Document migration workflow

**Files:**
- Modify: `README.md`
- Modify: `README_CN.md`
- Modify: `README_EN.md`
- Modify: `SKILL.md`
- Modify: `manifest.toml`

- [ ] **Step 1: Write the failing test**

Use existing text-contract style assertions in a new or updated test if needed.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_memory_capture_contract.py -v`
Expected: FAIL until the new migration flow is documented.

- [ ] **Step 3: Write minimal implementation**

Describe:
- export command
- import command
- cross-device migration goal
- pre-import backup behavior

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_memory_capture_contract.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md README_CN.md README_EN.md SKILL.md manifest.toml tests/test_memory_capture_contract.py
git commit -m "docs: document memory migration backup workflow"
```

### Task 4: Verify the repository

**Files:**
- No new files; verify the repo state

- [ ] **Step 1: Run full verification**

Run: `pytest -q`
Expected: all tests pass.

- [ ] **Step 2: Inspect repo state**

Run: `git status --short`
Expected: only intended modifications remain.
