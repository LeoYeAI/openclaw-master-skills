# Bug Records — Project-Specific Bug Documentation

> **Purpose**: Record all bugs fixed in the current project with root cause and fix details.
> **Update Rule**: MANDATORY update after every bug fix. If previous fix was incomplete, update the record.

---

## Record Template

```markdown
### [BUG-XXX] Brief Description
**Date**: YYYY-MM-DD
**Severity**: P0/P1/P2

**Root Cause**:
[1-2 sentences explaining WHY the bug occurred]

**Fix Method**:
[Concise description of HOW the bug was fixed]

**Files Modified**:
- `path/to/file1.ts`
- `path/to/file2.ts`

**Environment Impact**:
- [ ] Development
- [ ] Staging
- [ ] Production
```

---

## Bug Records

<!-- Add new records below this line, newest first -->

### [BUG-001] Simulated tool call parser fails for multi-arg file write calls
**Date**: 2026-03-05
**Severity**: P1

**Root Cause**:
`tool_call_parser.py` only supported single-argument tool calls. When the LLM output
`write_file("path.md", """content""")`, the parser produced `{"input": "garbled"}` instead
of `{"file_path": "path.md", "text": "content"}`. Additionally, `llm_node.py` had an
independent duplicate implementation of `parse_simulated_tool_calls` with the same bug.
After fixing, the server was not restarted, so old bytecode was still in use.

**Fix Method**:
1. Added AST-based parser (`_try_ast_parse_call`) for multi-arg calls in `tool_call_parser.py`
2. Added regex fallback for `tool_name("path", """content""")` pattern
3. Added word boundary `(?<![a-zA-Z0-9_])` to all regex patterns to prevent substring matches
4. Made `llm_node.py` delegate to `tool_call_parser.py` instead of its own broken parser
5. Cleared `__pycache__` and restarted backend

**Files Modified**:
- `backend/app/services/tool_call_parser.py` (AST parser + regex fallback + word boundaries)
- `backend/app/core/graph/nodes/llm_node.py` (delegate to tool_call_parser)

**Lessons Learned**:
- Must scan for duplicate implementations before declaring fix complete (Rule 17)
- Must verify fix is loaded by running system after code change (Rule 18)
- Must add word boundaries to regex patterns that match tool/function names (Rule 19)

**Environment Impact**:
- [x] Development

---

## Quick Reference: Common Root Causes

| Category | Root Cause Pattern | Prevention |
|----------|-------------------|------------|
| **Environment** | Config only in one env file | Check ALL env files |
| **Import** | Wrong import path/syntax | Verify module resolution |
| **State** | Race condition/stale state | Add proper synchronization |
| **Type** | Type mismatch/null check | Enable strict typing |
| **API** | Contract mismatch | Verify request/response schema |
| **Dependency** | Version incompatibility | Lock versions, test upgrades |

---

## Statistics

| Month | Total | P0 | P1 | P2 | Most Common Category |
|-------|-------|----|----|----|--------------------|
| YYYY-MM | 0 | 0 | 0 | 0 | — |

---

## Update Checklist

After fixing a bug:
- [ ] New record added with root cause and fix method
- [ ] Previous incomplete records updated if applicable
- [ ] Environment impact correctly marked
- [ ] `bug-patterns.md` updated if this is a new pattern
