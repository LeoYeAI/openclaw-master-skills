# Coding Behavior Fallback

Use this only when `coding-lead` is not loaded.

## Scope
This file defines the minimum fallback behavior for `fullstack-dev` and generated team templates. If `coding-lead` is available, it overrides this file.

## Task Routing
- Simple: direct in current session
- Medium: prefer Claude ACP `run` or direct acpx
- Complex: continue in the existing fullstack-dev session with context files
- Do not rely on IM-bound ACP session persistence
- ACP unavailable: fall back to direct execution, do not block

## Context Hygiene
- Keep active context files under `<project>/.openclaw/`
- Reuse the same context file for the same code chain when possible
- Naming pattern: `context-<task-slug>.md`
- Active context file cap per project: 60
- Context-file lifecycle window per project: 100 total files across active + archive
- Completed or stale context files should be deleted or archived under `.openclaw/archive/`

## Safety & Completion
- Verify against task + acceptance criteria before declaring done
- Confirm the target working directory before writing or spawning
- Read relevant product knowledge files before touching project code
- Reuse over reinvention; ask product-lead when boundaries are unclear
