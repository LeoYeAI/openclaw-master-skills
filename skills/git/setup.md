# Setup — Git

## Default Mode (No Setup Needed)

Most users don't need to configure anything. The skill uses industry best practices by default:

- Feature branches for new work
- Rebase before push to keep history clean
- Conventional commits when appropriate
- Never force push shared branches

**Just start using Git normally.** The skill helps when you need it.

## For Non-Technical Users

Git tracks versions of your files — like "undo history" for your entire project. Every software project uses it.

**The basics you need:**
- `git status` — see what changed
- `git add .` — prepare changes
- `git commit -m "message"` — save a checkpoint
- `git push` — upload to the team

That's it. The skill handles the rest.

## Optional: Custom Preferences

If you want to customize (most users skip this), just tell me:

- **Merge vs rebase?** — How to combine branches (default: rebase)
- **Commit style?** — Conventional commits, simple, etc. (default: conventional)
- **Branch naming?** — feature/x, feat-x, etc. (default: feature/x)

Only configure if you have strong preferences. Otherwise, best practices are applied automatically.

## What Gets Saved

If you share preferences, they go to `~/git/memory.md`:
- Your preferred workflow style
- Commit conventions you use
- Any project-specific patterns

The skill learns from working with you — no quiz required.
