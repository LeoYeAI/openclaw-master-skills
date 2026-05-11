---
name: linear
description: Query and manage Linear issues, projects, and team workflows.
homepage: https://linear.app
metadata: {"clawdis":{"emoji":"📊","requires":{"env":["LINEAR_API_KEY"]}}}
---

# Linear

Manage issues, check project status, and stay on top of your team's work.

## Setup

```bash
export LINEAR_API_KEY="your-api-key"
# Optional: default team key used when a command needs a team
export LINEAR_DEFAULT_TEAM="TEAM"
```

Discover team keys:

```bash
{baseDir}/scripts/linear.sh teams
```

If `LINEAR_DEFAULT_TEAM` is set, you can omit the team key in `team` and call:

```bash
{baseDir}/scripts/linear.sh create "Title" ["Description"]
```

## Quick Commands

```bash
# My stuff
{baseDir}/scripts/linear.sh my-issues          # Your assigned issues
{baseDir}/scripts/linear.sh my-todos           # Just your Todo items
{baseDir}/scripts/linear.sh urgent             # Urgent/High priority across team

# Browse
{baseDir}/scripts/linear.sh teams              # List available teams
{baseDir}/scripts/linear.sh team <TEAM_KEY>    # All issues for a team
{baseDir}/scripts/linear.sh project <name>     # Issues in a project
{baseDir}/scripts/linear.sh issue <TEAM-123>   # Get issue details
{baseDir}/scripts/linear.sh branch <TEAM-123>  # Get branch name for GitHub

# Actions
{baseDir}/scripts/linear.sh create <TEAM_KEY> "Title" ["Description"]
{baseDir}/scripts/linear.sh comment <TEAM-123> "Comment text"
{baseDir}/scripts/linear.sh status <TEAM-123> <todo|progress|review|done|blocked>
{baseDir}/scripts/linear.sh assign <TEAM-123> <userName>
{baseDir}/scripts/linear.sh priority <TEAM-123> <urgent|high|medium|low|none>

# Overview
{baseDir}/scripts/linear.sh standup            # Daily standup summary
{baseDir}/scripts/linear.sh projects           # All projects with progress
```

## Common Workflows

### Morning Standup
```bash
{baseDir}/scripts/linear.sh standup
```
Shows: your todos, blocked items across team, recently completed, what's in review.

### Quick Issue Creation (from chat)
```bash
{baseDir}/scripts/linear.sh create TEAM "Fix auth timeout bug" "Users getting logged out after 5 min"
```

### Triage Mode
```bash
{baseDir}/scripts/linear.sh urgent    # See what needs attention
```

## Git Workflow (Linear ↔ GitHub Integration)

**Always use Linear-derived branch names** to enable automatic issue status tracking.

### Getting the Branch Name
```bash
{baseDir}/scripts/linear.sh branch TEAM-212
# Returns: dev/team-212-fix-auth-timeout-bug
```

### Creating a Worktree for an Issue
```bash
# 1. Get the branch name from Linear
BRANCH=$({baseDir}/scripts/linear.sh branch TEAM-212)

# 2. Pull fresh main first (main should ALWAYS match origin)
cd /path/to/repo
git checkout main && git pull origin main

# 3. Create worktree with that branch (branching from fresh origin/main)
git worktree add .worktrees/team-212 -b "$BRANCH" origin/main
cd .worktrees/team-212

# 4. Do your work, commit, push
git push -u origin "$BRANCH"
```

**⚠️ Never modify files on main.** All changes happen in worktrees only.

### Why This Matters
- Linear's GitHub integration tracks PRs by branch name pattern
- When you create a PR from a Linear branch, the issue **automatically moves to "In Review"**
- When the PR merges, the issue **automatically moves to "Done"**
- Manual branch names break this automation
- Keeping main clean = no accidental pushes, easy worktree cleanup

### Quick Reference
```bash
# Full workflow example
ISSUE="TEAM-212"
BRANCH=$({baseDir}/scripts/linear.sh branch $ISSUE)

# Always start from fresh main
cd ~/workspace/your-repo
git checkout main && git pull origin main

# Create worktree (inside .worktrees/)
git worktree add .worktrees/${ISSUE,,} -b "$BRANCH" origin/main
cd .worktrees/${ISSUE,,}

# ... make changes ...
git add -A && git commit -m "fix: implement $ISSUE"
git push -u origin "$BRANCH"
gh pr create --title "$ISSUE: <title>" --body "Closes $ISSUE"
```

## Priority Levels

| Level | Value | Use for |
|-------|-------|---------|
| urgent | 1 | Production issues, blockers |
| high | 2 | This week, important |
| medium | 3 | This sprint/cycle |
| low | 4 | Nice to have |
| none | 0 | Backlog, someday |

## Teams (cached)

Team keys and IDs are discovered via the API and cached locally after the first lookup.
Use `linear.sh teams` to refresh and list available teams.

## Notes

- Uses GraphQL API (api.linear.app/graphql)
- Requires `LINEAR_API_KEY` env var
- Issue identifiers are like `TEAM-123`

## Attribution

Inspired by [schpet/linear-cli](https://github.com/schpet/linear-cli) by Peter Schilling (ISC License).
This is an independent bash implementation for Clawdbot integration.
