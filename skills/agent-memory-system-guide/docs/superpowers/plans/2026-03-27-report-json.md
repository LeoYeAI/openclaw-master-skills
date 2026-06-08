# Report JSON Output Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a machine-readable `--json` mode to `scripts/memory_capture.py report` while preserving the current default report behavior.

**Architecture:** Extend only the `report` subcommand with a `--json` flag, serialize the existing `ReportData` model into JSON for stdout, and leave Markdown file output through `--output` unchanged.

**Tech Stack:** Python 3, argparse, dataclasses, json, pytest

---

### Task 1: Lock report JSON behavior with failing tests

**Files:**
- Modify: `tests/test_memory_capture_script.py`
- Test: `tests/test_memory_capture_script.py`

- [ ] **Step 1: Write the failing tests**

```python
import json
```

```python
def test_report_prints_json_summary(tmp_path: Path):
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    (workspace / 'MEMORY.md').write_text('# MEMORY\n', encoding='utf-8')
    (workspace / 'working-buffer.md').write_text('# BUFFER\n', encoding='utf-8')
    (workspace / 'memory-capture.md').write_text('# CAPTURE\n', encoding='utf-8')
    memory_dir = workspace / 'memory'
    memory_dir.mkdir()
    (memory_dir / '2026-03-25.md').write_text('# day 2\n', encoding='utf-8')
    attachments_dir = workspace / 'attachments'
    attachments_dir.mkdir()
    (attachments_dir / 'proof.txt').write_text('data\n', encoding='utf-8')

    result = run_command('report', '--workspace', str(workspace), '--json')

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload['workspace'] == str(workspace.resolve())
    assert payload['supported_files']['SESSION-STATE.md'] is False
    assert payload['memory_note_count'] == 1
    assert payload['attachments_count'] == 1
    assert payload['latest_daily_note'] == 'memory/2026-03-25.md'
    assert 'Missing supported file: SESSION-STATE.md' in payload['warnings']
```

```python
def test_report_json_can_write_markdown_output_file(tmp_path: Path):
    workspace = tmp_path / 'workspace'
    workspace.mkdir()
    (workspace / 'MEMORY.md').write_text('# MEMORY\n', encoding='utf-8')
    (workspace / 'SESSION-STATE.md').write_text('# SESSION\n', encoding='utf-8')
    (workspace / 'working-buffer.md').write_text('# BUFFER\n', encoding='utf-8')
    (workspace / 'memory-capture.md').write_text('# CAPTURE\n', encoding='utf-8')
    memory_dir = workspace / 'memory'
    memory_dir.mkdir()
    (memory_dir / '2026-03-25.md').write_text('# day 1\n', encoding='utf-8')
    attachments_dir = workspace / 'attachments'
    attachments_dir.mkdir()
    (attachments_dir / 'proof.txt').write_text('good\n', encoding='utf-8')
    report_path = tmp_path / 'workspace-report.md'

    result = run_command(
        'report',
        '--workspace',
        str(workspace),
        '--json',
        '--output',
        str(report_path),
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload['latest_daily_note'] == 'memory/2026-03-25.md'
    assert report_path.exists()
    markdown = report_path.read_text(encoding='utf-8')
    assert '# Memory workspace report' in markdown
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_memory_capture_script.py -k "prints_json_summary or json_can_write_markdown_output_file" -q`
Expected: FAIL because `report` does not yet accept `--json`.

- [ ] **Step 3: Write minimal implementation**

Add the flag and serializer in `scripts/memory_capture.py`:

```python
report_parser.add_argument(
    "--json",
    action="store_true",
    help="Print the report payload as JSON to stdout.",
)
```

```python
def report_payload(data: ReportData) -> dict[str, object]:
    return {
        "workspace": str(data.workspace),
        "supported_files": data.supported_files,
        "memory_note_count": data.memory_note_count,
        "attachments_count": data.attachments_count,
        "latest_daily_note": (
            data.latest_daily_note.relative_to(data.workspace).as_posix()
            if data.latest_daily_note
            else None
        ),
        "warnings": data.warnings,
    }
```

```python
if args.json:
    print(json.dumps(report_payload(report_data), ensure_ascii=False, indent=2))
else:
    print(format_report_text(report_data))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_memory_capture_script.py -k "prints_json_summary or json_can_write_markdown_output_file" -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_memory_capture_script.py scripts/memory_capture.py
git commit -m "feat: add json output for report"
```

### Task 2: Run regression verification

**Files:**
- Modify: none
- Test: `tests/test_memory_capture_script.py`
- Test: full `tests/`

- [ ] **Step 1: Run focused regression tests**

Run: `pytest tests/test_memory_capture_script.py -q`
Expected: PASS

- [ ] **Step 2: Run full test suite**

Run: `pytest -q`
Expected: PASS with all repository contract tests green.

- [ ] **Step 3: Inspect scoped diff**

Run: `git diff -- scripts/memory_capture.py tests/test_memory_capture_script.py`
Expected: Only `report --json` CLI and test changes appear.

- [ ] **Step 4: Commit**

```bash
git add scripts/memory_capture.py tests/test_memory_capture_script.py docs/superpowers/specs/2026-03-27-report-json-design.md docs/superpowers/plans/2026-03-27-report-json.md
git commit -m "docs: specify report json output"
```
