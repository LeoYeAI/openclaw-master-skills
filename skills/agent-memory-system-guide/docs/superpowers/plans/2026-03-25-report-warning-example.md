# Report Warning Example Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a warning-state `report` example to the README files so users can see what the command looks like when files are missing.

**Architecture:** Keep the change documentation-only. Update the contract test first, then add a short warning example block to each README next to the existing normal-output example. The example must match the current CLI wording and section order.

**Tech Stack:** Markdown docs, plain `pytest`

---

### Task 1: Add contract coverage for the warning example

**Files:**
- Modify: `tests/test_memory_capture_contract.py`
- Test: `tests/test_memory_capture_contract.py`

- [ ] **Step 1: Write the failing contract assertions**

```python
assert 'Missing supported file: SESSION-STATE.md' in readme_text
assert 'Warnings:' in readme_text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_memory_capture_contract.py -v`
Expected: FAIL because the README files only contain the success example.

- [ ] **Step 3: Write minimal implementation**

Add one warning-state output example to:
- `README.md`
- `README_CN.md`
- `README_EN.md`

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_memory_capture_contract.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add README.md README_CN.md README_EN.md tests/test_memory_capture_contract.py
git commit -m "docs: add report warning output example"
```

### Task 2: Verify the repository

**Files:**
- No new files; verify the repo state

- [ ] **Step 1: Run full verification**

Run: `pytest -q`
Expected: all tests pass.

- [ ] **Step 2: Inspect repo state**

Run: `git status --short`
Expected: only intended modifications remain.
