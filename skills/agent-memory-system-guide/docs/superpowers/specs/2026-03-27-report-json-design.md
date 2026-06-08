# Report JSON Output Design

## Scope

This design adds a machine-readable `--json` mode to the `report` subcommand in `scripts/memory_capture.py`.

The change is intentionally narrow:

- Only `report` gains JSON stdout output.
- Existing human-readable stdout output remains the default.
- Existing Markdown file output through `--output` remains unchanged.

This iteration does not add `--json` to `bootstrap`, `export`, or `import`, and does not introduce `--dry-run`.

## Goals

- Make `report` easy to consume from automation, scripts, and other skills.
- Preserve current CLI behavior for existing users.
- Reuse the existing `ReportData` shape instead of inventing a second reporting model.

## Non-Goals

- Add JSON output to every subcommand.
- Replace Markdown report generation.
- Add dry-run planning or command tracing.
- Change report semantics or warning rules.

## Current Behavior

`report` currently:

1. Validates that the workspace exists.
2. Collects `ReportData`.
3. Prints a human-readable text report to stdout.
4. Optionally writes a Markdown report file through `--output`.

This works well for humans but is awkward for automation that needs stable field access.

## Options Considered

### Option 1: Add `report --json` and keep Markdown file output unchanged

Stdout becomes JSON only when `--json` is passed. `--output` still writes Markdown.

Pros:

- Smallest change with the highest immediate integration value.
- Backward compatible for existing human-oriented usage.
- Easy to test because it maps directly to `ReportData`.

Cons:

- Different output formats remain split between stdout and file output.

### Option 2: Make `--output` format-sensitive

Allow `--json` to affect both stdout and file output.

Pros:

- More uniform format behavior.

Cons:

- Expands scope and introduces ambiguity around whether `--output` should write JSON or Markdown.

### Option 3: Add a separate `report-json` subcommand

Pros:

- Explicit command naming.

Cons:

- Worse CLI ergonomics and unnecessary surface area.

## Recommended Design

Adopt Option 1.

### CLI

Add a new boolean flag to `report`:

- `--json`: print the report payload as JSON to stdout.

Behavior:

- `report` with no flag: current human-readable stdout output.
- `report --json`: JSON stdout.
- `report --output file.md`: current text stdout plus Markdown file.
- `report --json --output file.md`: JSON stdout plus Markdown file.

## Data Shape

The JSON payload should reflect `ReportData` closely:

```json
{
  "workspace": "/abs/path",
  "supported_files": {
    "MEMORY.md": true,
    "SESSION-STATE.md": false,
    "working-buffer.md": true,
    "memory-capture.md": true
  },
  "memory_note_count": 2,
  "attachments_count": 1,
  "latest_daily_note": "memory/2026-03-25.md",
  "warnings": [
    "Missing supported file: SESSION-STATE.md"
  ]
}
```

Field rules:

- `workspace`: absolute path string
- `supported_files`: filename to boolean presence map
- `memory_note_count`: integer
- `attachments_count`: integer
- `latest_daily_note`: relative path string or `null`
- `warnings`: list of strings

## Implementation Notes

- Add a serializer helper for `ReportData` rather than building JSON inline in `handle_report()`.
- Reuse the existing relative-path logic for `latest_daily_note`.
- Use `json.dumps(..., ensure_ascii=False, indent=2)` for readable machine output.
- Keep Markdown output logic unchanged.

## Testing Strategy

Add focused tests for:

1. `report --json` returns valid JSON with the expected fields.
2. `latest_daily_note` is serialized as a relative path or `null`.
3. `report --json --output file.md` still writes the Markdown report file.

Then run the full pytest suite to catch regressions.

## Files Expected To Change

- `scripts/memory_capture.py`
- `tests/test_memory_capture_script.py`

## Acceptance Criteria

- `report --json` prints valid JSON to stdout.
- The JSON fields match the existing report semantics.
- `--output` continues to write Markdown, even when `--json` is used.
- Human-readable `report` behavior remains unchanged by default.
- Full pytest suite passes.
