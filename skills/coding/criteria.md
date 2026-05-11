# Criteria for Code Preferences

Reference only — consult when deciding whether to update SKILL.md.

## When to Add

**Immediate (1 occurrence):**
- User explicitly says "always use X" or "never do Y"
- User corrects your choice → add their preference
- User rejects a suggestion → add to Never

**After repeated explicit feedback (2+ times):**
- User explicitly accepted your choice twice
- User stated same preference in multiple conversations
- User explicitly approved your approach multiple times

## When NOT to Add
- Project-specific requirement (not a general preference)
- User was just exploring options
- Contradicts existing confirmed preference (investigate first)

## How to Write Entries

**Ultra-compact format — 5 words max per entry:**

Stack examples:
- `mobile: Flutter`
- `web: Next.js`
- `db: Pocketbase for MVPs`
- `backend: avoid unless needed`

Style examples:
- `no Prettier`
- `minimal comments`
- `snake_case files`
- `TypeScript strict mode`

Structure examples:
- `feature-based folders`
- `tests colocated`
- `monorepo when related`

Never examples:
- `no Redux`
- `no excessive linting`
- `avoid ORMs`

## Context Qualifiers
When preference is context-dependent, prefix with context:
- `MVPs: skip tests`
- `Python: black formatter`
- `production: full types`

## Handling Changes
- User contradicts existing entry → remove old, add new
- User says "except for X" → add context qualifier
- Unclear if changed → move to mental note, observe more

## Maintenance
- Merge similar entries: "no Prettier" + "no ESLint" → "minimal tooling"
- Remove entries that never proved useful
- Keep total SKILL.md under 30 lines ideally
