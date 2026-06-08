# Memory Positioning and Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clarify repository positioning in the documentation so users understand the local-first workflow, memory boundaries, and optional backend story.

**Architecture:** Update the README entry points and install wording only. Keep the script and template contract unchanged while making the documentation reflect stable profile, active context, and optional recall backend concepts.

**Tech Stack:** Markdown, repository contract tests, pytest

---

### Task 1: Document the intended product boundary

**Files:**
- Create: `docs/superpowers/specs/2026-03-27-memory-positioning-design.md`
- Modify: `README.md`
- Modify: `README_EN.md`
- Modify: `README_CN.md`
- Modify: `INSTALL.md`
- Test: `tests/test_readme_openviking_optional.py`
- Test: `tests/test_install_contract.py`

- [ ] **Step 1: Update README openings**

Add wording that this repository is a local-first Agent memory workflow rather than a hosted memory platform, while preserving the existing OpenViking-optional contract language.

- [ ] **Step 2: Add explicit boundary sections**

Document the roles of `SESSION-STATE.md`, `working-buffer.md`, `MEMORY.md`, `memory/`, and deeper archive or semantic recall layers.

- [ ] **Step 3: Add stable profile and project scope guidance**

Explain that `MEMORY.md` should bias toward durable profile information and that project references are optional conventions when one workspace spans multiple efforts.

- [ ] **Step 4: Update install wording**

Keep the OpenViking phrase required by tests, but broaden the wording to "optional enhancement/backend" rather than implying a single integration path.

### Task 2: Verify documentation contracts

**Files:**
- Modify: none
- Test: `tests/test_readme_openviking_optional.py`
- Test: `tests/test_install_contract.py`
- Test: full `tests/`

- [ ] **Step 1: Run targeted documentation contract tests**

Run: `pytest tests/test_readme_openviking_optional.py tests/test_install_contract.py -q`
Expected: PASS

- [ ] **Step 2: Run full regression suite**

Run: `pytest -q`
Expected: PASS

- [ ] **Step 3: Inspect diff**

Run: `git diff -- README.md README_EN.md README_CN.md INSTALL.md docs/superpowers/specs/2026-03-27-memory-positioning-design.md docs/superpowers/plans/2026-03-27-memory-positioning.md`
Expected: Documentation-only changes that align with the local-first positioning and optional backend wording.
