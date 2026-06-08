# Agent Memory System Guide Obsidian Native Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the skill explicitly Obsidian-native by adding structured note templates, Dataview-friendly metadata, wikilink/backlink guidance, and attachment/embed conventions.

**Architecture:** Keep the existing memory hierarchy intact and layer Obsidian-specific conventions on top of it. The repo should remain documentation-first, but now it should also ship a reusable note template and contract tests that pin the Obsidian workflow.

**Tech Stack:** Markdown, YAML frontmatter conventions, plain-text contract tests with `pytest`

---

### Task 1: Add an Obsidian note template

**Files:**
- Create: `templates/OBSIDIAN-NOTE.md`
- Modify: `SKILL.md:1-200`
- Modify: `README.md:1-80`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_obsidian_template_exists():
    repo_root = Path('/Users/jingkechen/Documents/agent-memory-system-guide')
    assert (repo_root / 'templates' / 'OBSIDIAN-NOTE.md').exists()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_obsidian_template_contract.py -v`
Expected: FAIL because the template file does not exist yet.

- [ ] **Step 3: Write minimal implementation**

Create `templates/OBSIDIAN-NOTE.md` with:
- YAML frontmatter fields for `title`, `aliases`, `tags`, `type`, `status`, `source`, `source_url`, `created`, `updated`, `related`
- a summary section
- key points
- evidence
- related notes
- attachment/embed guidance

Update `SKILL.md` and `README.md` so the template is presented as part of the recommended Obsidian setup.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_obsidian_template_contract.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add templates/OBSIDIAN-NOTE.md SKILL.md README.md tests/test_obsidian_template_contract.py
git commit -m "docs: add obsidian note template"
```

### Task 2: Make the documentation Obsidian-native

**Files:**
- Modify: `SKILL.md:1-200`
- Modify: `README_EN.md:1-80`
- Modify: `README_CN.md:1-80`
- Modify: `INSTALL.md:1-40`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_skill_mentions_obsidian_primitives():
    repo_root = Path('/Users/jingkechen/Documents/agent-memory-system-guide')
    skill_text = (repo_root / 'SKILL.md').read_text(encoding='utf-8')
    for token in ['frontmatter', 'Dataview', 'wikilink', 'backlinks', 'embeds', 'attachments']:
        assert token in skill_text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_obsidian_contract.py -v`
Expected: FAIL because the Obsidian-specific contract text is not yet fully written.

- [ ] **Step 3: Write minimal implementation**

Update the docs to explain:
- how frontmatter fields are used
- how Dataview can query `type`, `status`, `tags`, and `related`
- how internal references should use wikilinks
- how backlinks help the graph stay connected
- how images, block quotes, and attachment references should be preserved
- how OpenViking stays optional while still supporting the workflow

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_obsidian_contract.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add SKILL.md README_EN.md README_CN.md INSTALL.md tests/test_obsidian_contract.py
git commit -m "docs: document obsidian-native workflow"
```

### Task 3: Add contract coverage for recovery and optional OpenViking

**Files:**
- Modify: `tests/test_memory_recovery_contract.py`
- Modify: `tests/test_openviking_optional_contract.py`
- Modify: `tests/test_install_contract.py`
- Modify: `tests/test_readme_openviking_optional.py`

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_readme_mentions_obsidian_template_and_optional_openviking():
    repo_root = Path('/Users/jingkechen/Documents/agent-memory-system-guide')
    text = (repo_root / 'README.md').read_text(encoding='utf-8')
    assert 'templates/OBSIDIAN-NOTE.md' in text
    assert 'OpenViking is an optional enhancement' in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_readme_openviking_optional.py tests/test_install_contract.py -v`
Expected: FAIL until the new README wording and template link are in place.

- [ ] **Step 3: Write minimal implementation**

Tighten the tests to check for:
- recovery templates
- Obsidian note template
- OpenViking optional wording
- installation prompt boundaries

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest -q`
Expected: all contract tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_memory_recovery_contract.py tests/test_openviking_optional_contract.py tests/test_install_contract.py tests/test_readme_openviking_optional.py
git commit -m "test: cover obsidian and openviking contracts"
```

### Task 4: Verify and publish

**Files:**
- No new files; verify the repo state

- [ ] **Step 1: Run full verification**

Run: `pytest -q`
Expected: all tests pass.

- [ ] **Step 2: Check the diff**

Run: `git status --short`
Expected: clean working tree after commits.

- [ ] **Step 3: Push to GitHub**

```bash
git push
```

Expected: remote `main` updated with the Obsidian-native workflow.
