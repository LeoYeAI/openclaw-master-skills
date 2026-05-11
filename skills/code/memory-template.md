# Memory Setup - Code

## Initial Setup

Create directory on first use:
```bash
mkdir -p ~/code
touch ~/code/memory.md
```

## memory.md Template

Copy to `~/code/memory.md`:

```markdown
# Code Memory

## Preferences
<!-- User's coding workflow preferences. Format: "preference" -->
<!-- Examples: always run tests, prefer TypeScript, commit after each feature -->

## Never
<!-- Things that don't work for this user. Format: "thing to avoid" -->
<!-- Examples: inline styles, console.log debugging, large PRs -->

## Patterns
<!-- Approaches that work well. Format: "pattern: context" -->
<!-- Examples: TDD: for complex logic, screenshots: for UI work -->

---
Last updated: YYYY-MM-DD
```

## Notes

- Check `criteria.md` for additional user-specific criteria
- Use `planning.md` for breaking down complex requests
- Verify with tests and screenshots per `verification.md`
