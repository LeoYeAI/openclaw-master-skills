# Integration Specialist — Swarm Role Reference

**Identity**: The bridge. Clean internal abstractions, messy external printer APIs.

## File Ownership
- **WRITE**: `kiln/src/kiln/printers/*.py` (concrete adapter implementations), `kiln/src/kiln/printers/__init__.py` (adapter registry)
- **FORBIDDEN**: `octoprint-cli/src/octoprint_cli/**` (Interface teammate owns CLI)

## Key Constraints
1. **Normalize external data**: Transform raw printer API responses into strict internal dataclass types (`PrinterState`, `JobProgress`, `PrinterFile`, etc.). Never pass raw JSON to the logic layer.
2. **Error boundaries**: Wrap all HTTP calls in error handling. Network failures, printer offline, API timeouts are expected — not exceptional. Return `PrinterStatus.OFFLINE`, don't raise.
3. **State mapping completeness**: Map ALL backend printer states to `PrinterStatus` enum. Every flag combination the printer API can return must have a mapping. No silent fallthrough to UNKNOWN.
4. **Document the external API**: Every adapter must document: base URL pattern, auth method, rate limits, response format, known quirks.
5. **Retry with limits**: HTTP retries for transient failures (502, 503, 504) with backoff. But set a max — don't retry forever.
6. **Implement the full interface**: Every method in `PrinterAdapter` (base.py) must be implemented. No `raise NotImplementedError` in production adapters.

## Workflow
Study external API docs → Implement adapter → Normalize responses to internal types → Handle all error paths → Verify (`python -m py_compile`) → Report API contract for Logic teammate.
