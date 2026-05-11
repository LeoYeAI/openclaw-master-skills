# Criteria for Storing Preferences

Reference for when to save user preferences to `~/code/memory.md`.

## When to Save (User Must Request)

Save only when user explicitly asks:
- "Remember that I prefer X"
- "Always do Y from now on"
- "Save this preference"
- "Don't forget that I like Z"

## When NOT to Save

- User didn't explicitly ask to save
- Project-specific requirement (applies to this project only)
- One-off request ("just this once")
- Temporary preference

## What to Save

**Preferences:**
- Coding style preferences user stated
- Tools or frameworks user prefers
- Patterns user explicitly likes

**Things to avoid:**
- Approaches user explicitly dislikes
- Patterns user asked not to repeat

## Format in memory.md

```markdown
## Preferences
- prefers TypeScript over JavaScript
- likes detailed comments
- wants tests for all functions

## Never
- no class-based React components
- avoid inline styles
```

## Important

- Only save what user EXPLICITLY asked to save
- Ask user before saving: "Should I remember this preference?"
- Never modify any skill files, only `~/code/memory.md`
