# SHIFT — BRIDGE
# Context Bridge: passes context between master and sub-identities.
# Three-layer system ensures sub-identities always have the context they need.

## Session Folder Structure

```
~/.openclaw/workspace/.shift/
├── sessions/
│   └── <runId>/
│       ├── INBOUND.json      ← master writes before spawning
│       ├── CONTEXT.md        ← master writes (project memory, files)
│       ├── OUTBOUND.md       ← sub-identity writes when done
│       ├── CONSULT-OUTBOUND.md  ← child sub-identity writes (consultation)
│       └── ESCALATE.md       ← Runner writes if task too complex
└── cost-tracking.json       ← rolling hourly delegation cost
```

`<runId>` is a unique ID for each delegation (e.g., `run-20260318-1542-codex-001`).

## Layer 1: INBOUND.json

Written by: Master, before spawning sub-agent.
Read by: Sub-identity, as its first action.

```json
{
  "runId": "run-20260318-1542-codex-001",
  "timestamp": "2026-03-18T15:42:00Z",
  "persona": "codex",
  "userMessage": "implement a binary search tree in Python",
  "masterConversationHistory": [
    {"role": "user", "content": "can you help with a sorting algorithm"},
    {"role": "assistant", "content": "Sure, what language?"},
    {"role": "user", "content": "python please"}
  ],
  "activeFiles": ["src/sorter.py"],
  "masterSummary": "the user is working through sorting algorithms in Python. Last discussed: basic list sorting."
}
```

`masterConversationHistory` contains the last N turns from the master session (configurable: `contextBridge.historyTurns`).

## Layer 2: CONTEXT.md

Written by: Master, before spawning sub-agent.
Read by: Sub-identity, after reading INBOUND.json.

Contains pulled content from:
- Relevant sections of `MEMORY.md` (project context)
- Active files being discussed (pulled content)
- Sub-identity-specific context needs (defined in persona)

```markdown
# Context for Codex

## Project: sorting-algos
- Language: Python
- Files in scope: src/sorter.py, src/bst.py
- Recent decisions: using classes, type hints required

## Memory (relevant)
- the user prefers clean, readable code over clever one-liners
- Unit tests required for all implementations

## Active File Content: src/sorter.py
```python
class Sorter:
    def quick_sort(self, arr):
        # TODO: implement
        pass
```

## Sub-identity Persona Context Needs (for Codex)
- Programming language: Python ✓ (from INBOUND)
- Active file paths: src/sorter.py ✓
- Error messages: none
- Decisions made: using classes + type hints ✓
```

## Layer 3: OUTBOUND.md

Written by: Sub-identity, when task is complete.
Read by: Master, after sub-agent finishes.

```markdown
# OUTBOUND — Codex

## Status: complete | error | escalation | needs_consultation

## Result
(write the actual response content here — code, analysis, or answer)

## Status: needs_consultation
(when sub-identity needs another sub-identity's context before continuing)
## PartialResult
(what Codex has done/understood so far)

## ConsultationLog
- consulted: researcher
- question: "best approach for BST balancing?"
- answer_summary: "use red-black tree or AVL for self-balancing"
- status: pending | complete

## Cost
- inputTokens: 1234
- outputTokens: 567
- estimatedCost: 0.023

## Notes
(any warnings, caveats, or follow-up suggestions)
```

## ESCALATE.md (Runner only)

Written by: Runner, when task is detected as too complex.
Read by: Master, as replacement for OUTBOUND.md.

```markdown
# ESCALATE — Runner

## Reason
task_too_complex | ambiguous | requires_deep_knowledge

## Summary
Runner's brief understanding of what was asked.

## PartialAnswer
(any partial work Runner did, or null)

## Recommendation
Which persona Runner suggests for this task: codex | researcher
```

## Cost Tracking

`cost-tracking.json` (updated after each delegation):

```json
{
  "hourStart": "2026-03-18T15:00:00Z",
  "totalSpend": 0.87,
  "delegations": [
    {
      "runId": "run-20260318-1542-codex-001",
      "persona": "codex",
      "inputTokens": 1234,
      "outputTokens": 567,
      "estimatedCost": 0.023,
      "timestamp": "2026-03-18T15:42:00Z"
    }
  ]
}
```

Master checks `hourStart` on each request. If current time is in a new hour, resets `totalSpend` to 0.

## Context File Lifecycle

```
Master writes INBOUND.json + CONTEXT.md
        ↓
Sub-identity spawned (files attached or path passed)
        ↓
Sub-identity reads context, executes task
        ↓
Sub-identity writes OUTBOUND.md (or ESCALATE.md)
        ↓
Master reads OUTBOUND.md
        ↓
Master synthesizes response
        ↓
Session files archived after contextBridge.archiveAfterMinutes
```

## Error Handling

| Error | Behavior |
|---|---|
| INBOUND.json missing | Sub-identity starts fresh (not catastrophic) |
| CONTEXT.md missing | Sub-identity uses only INBOUND.json |
| OUTBOUND.md missing | Master logs error, falls back to sub-identity's stream (if any) |
| ESCALATE.md present | Master takes over (ignores OUTBOUND.md) |
| Session folder missing | Created automatically by master before spawning |
