# Ralph Agent Prompt

Copy this to `CLAUDE.md` in project root for Ralph execution.

---

# Ralph Agent Instructions

You are an autonomous coding agent working on a SvelteKit PWA project.

## Your Task

1. Read the PRD at `prd.json`
2. Read the progress log at `progress.txt` (check Codebase Patterns section first)
3. Check you're on the correct branch from PRD `branchName`. If not, check it out or create from main.
4. Pick the **highest priority** user story where `passes: false`
5. Implement that single user story
6. Run quality checks: `npm run check && npm run test`
7. Update CLAUDE.md files if you discover reusable patterns (see below)
8. If checks pass, commit ALL changes with message: `feat: [Story ID] - [Story Title]`
9. Update the PRD to set `passes: true` for the completed story
10. Append your progress to `progress.txt`

## Progress Report Format

APPEND to progress.txt (never replace, always append):
```
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered (e.g., "this codebase uses X for Y")
  - Gotchas encountered (e.g., "don't forget to update Z when changing W")
  - Useful context (e.g., "the component X is in lib/components/")
---
```

The learnings section is critical - it helps future iterations avoid repeating mistakes.

## Consolidate Patterns

If you discover a **reusable pattern** that future iterations should know, add it to the `## Codebase Patterns` section at the TOP of progress.txt (create it if it doesn't exist):

```
## Codebase Patterns
- Use `$derived` for computed state, not `$:` (Svelte 5 runes)
- Stores must be `.svelte.ts` files to use `$state` rune
- Server-only code goes in `+page.server.ts` or `lib/server/`
- Always add `data-testid` attributes for Playwright selectors
```

Only add patterns that are **general and reusable**, not story-specific details.

## SvelteKit-Specific Rules

### File Conventions
- Routes: `src/routes/[path]/+page.svelte`
- Server data: `src/routes/[path]/+page.server.ts`
- Components: `src/lib/components/ComponentName.svelte`
- Stores: `src/lib/stores/storeName.svelte.ts` (for runes)
- Server utilities: `src/lib/server/` (never imported client-side)

### Svelte 5 Runes
- Use `$state()` for reactive state
- Use `$derived()` for computed values
- Use `$effect()` for side effects
- Use `$props()` for component props
- Do NOT use `$:` reactive statements (Svelte 4 syntax)

### TypeScript
- All files must typecheck (`npm run check`)
- Export types from `src/lib/types/`
- Use strict mode

## Quality Requirements

- ALL commits must pass: `npm run check && npm run test`
- Do NOT commit broken code
- Keep changes focused and minimal
- Follow existing code patterns in the codebase

## Browser Testing

For any story that changes UI:

1. Run the dev server: `npm run dev`
2. Navigate to the relevant page
3. Verify the UI changes work as expected
4. Check responsive behavior (mobile/desktop)

Note in progress.txt if you verified in browser.

## Stop Condition

After completing a user story, check if ALL stories have `passes: true`.

If ALL stories are complete and passing, reply with:
<promise>COMPLETE</promise>

If there are still stories with `passes: false`, end your response normally (another iteration will pick up the next story).

## Important

- Work on ONE story per iteration
- Commit after each completed story
- Keep CI green
- Read the Codebase Patterns section in progress.txt before starting
- Small, focused changes are better than large refactors
