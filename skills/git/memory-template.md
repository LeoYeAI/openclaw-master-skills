# Memory Template — Git

Create `~/git/memory.md` only if user shares preferences:

```markdown
# Git Preferences

## Workflow
style: best-practices
merge-strategy: rebase
branch-naming: feature/x

## Commits
format: conventional
scope: optional

## Notes
<!-- Patterns observed from working together -->

---
*Updated: YYYY-MM-DD*
```

## When to Create Memory

- User explicitly shares a preference
- User corrects your suggestion ("I prefer merge over rebase")
- User has a team convention you should remember

## When NOT to Create Memory

- First interaction (just help them)
- User seems confused by options (use defaults)
- One-off exception (doesn't mean it's their preference)

## Default Behavior (No Memory)

Without memory file, apply best practices:
- Rebase feature branches
- Conventional commits
- feature/x branch naming
- Never force push main/master
