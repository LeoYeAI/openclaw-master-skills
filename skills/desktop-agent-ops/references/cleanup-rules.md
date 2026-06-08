# Cleanup Rules

Cleanup is mandatory.

## Clean when

Run cleanup when a task is:

- completed
- failed and terminated
- cancelled
- clearly replaced by a new unrelated task

## Clean these items

At minimum clear:

- temporary screenshots
- region captures
- temporary OCR outputs if created later
- recent target / anchor state
- focus hints
- retry counters
- task-local metadata that should not leak into unrelated work

## Keep these items only if useful

You may keep lightweight audit artifacts only when they help future debugging, but do not let them behave as active task context.

Examples of safe retained items:

- a final result summary
- a final success screenshot if intentionally preserved
- a short log for debugging

## Context isolation rule

If a task is finished and a later request is unrelated, do not reuse:

- last screenshot
- last target name
- last focused app assumption
- last fallback path

Create a new task context instead.

## Suggested rule of thumb

If the previous task is done and enough time has passed that the new request is functionally unrelated, start fresh rather than trying to resume old context.

## Script usage

Use `scripts/cleanup_task.py` to perform actual cleanup and return a structured result.
