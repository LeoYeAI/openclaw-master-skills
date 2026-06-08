# Memory Examples and Maintenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add practical documentation examples and a lightweight maintenance report command for memory workspaces.

**Architecture:** Keep the repo as a guide plus helper CLI. Documentation changes add copyable examples in the README files and skill text. The Python helper gains a deterministic `report` subcommand that scans supported files, emits warnings, and optionally writes a Markdown maintenance report without modifying user memory content.

**Tech Stack:** Markdown docs, Python 3, `argparse`, `pathlib`, plain `pytest`

---

### Task 1: Add failing tests for the maintenance report command

**Files:**
- Modify: `tests/test_memory_capture_script.py`
- Test: `tests/test_memory_capture_script.py`

- [ ] **Step 1: Write the failing tests**

```python
def test_report_prints_workspace_summary(tmp_path: Path):
    ...

def test_report_writes_markdown_output_file(tmp_path: Path):
    ...
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_memory_capture_script.py -k report -v`
Expected: FAIL because the `report` subcommand does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Add `report` support to `scripts/memory_capture.py` with stdout and file output modes.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_memory_capture_script.py -k report -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_memory_capture_script.py scripts/memory_capture.py
git commit -m "feat: add memory maintenance report command"
```

### Task 2: Document examples and maintenance workflow

**Files:**
- Modify: `README.md`
- Modify: `README_CN.md`
- Modify: `README_EN.md`
- Modify: `SKILL.md`
- Modify: `tests/test_memory_capture_contract.py`

- [ ] **Step 1: Write the failing contract assertions**

Add assertions for:
- practical examples in the README files
- maintenance report command documentation

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_memory_capture_contract.py -v`
Expected: FAIL until the docs mention the new examples and report flow.

- [ ] **Step 3: Write minimal implementation**

Document:
- bootstrap example
- task-end capture example
- distillation example
- maintenance report example

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_memory_capture_contract.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md README_CN.md README_EN.md SKILL.md tests/test_memory_capture_contract.py
git commit -m "docs: add memory workflow examples and maintenance guide"
```

### Task 3: Verify the repository

**Files:**
- No new files; verify the repo state

- [ ] **Step 1: Run targeted verification**

Run: `pytest tests/test_memory_capture_script.py tests/test_memory_capture_contract.py -v`
Expected: PASS

- [ ] **Step 2: Run full verification**

Run: `pytest -q`
Expected: all tests pass.

- [ ] **Step 3: Inspect repo state**

Run: `git status --short`
Expected: only intended modifications remain.
