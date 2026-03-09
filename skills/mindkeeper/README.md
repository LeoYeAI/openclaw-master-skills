# Mindkeeper Skill

Time Machine for Your AI's Brain — version control for agent context files. This skill teaches your AI to use mindkeeper tools for history, diff, rollback, and snapshots.

**Setup:** Add this skill alone. When you first ask for mindkeeper capability, the AI will ask for your confirmation before installing the mindkeeper-openclaw plugin and restarting the Gateway. You can also install the plugin manually (see Requirements).

## What It Does

- **Browse history** — See what changed in SOUL.md, AGENTS.md, or any tracked file
- **Compare versions** — Full unified diff between any two commits
- **Rollback** — Restore any file to a previous version (with preview + confirmation)
- **Named snapshots** — Create checkpoints before risky changes

## Requirements

- Node.js ≥ 22
- OpenClaw with Gateway running

The mindkeeper-openclaw plugin provides the mind_* tools. The AI will ask for your confirmation before running `openclaw plugins install mindkeeper-openclaw` and restarting the Gateway on first use. Alternatively, install it yourself:

```bash
openclaw plugins install mindkeeper-openclaw
# Then restart your Gateway
```

## Permissions & Why They Are Needed

| Action | Purpose |
|--------|---------|
| `openclaw plugins install mindkeeper-openclaw` | Fetches the official plugin from npm to add mind_status, mind_history, mind_diff, mind_rollback, mind_snapshot tools |
| Gateway restart | Loads the newly installed plugin into the running Gateway |

**User consent:** The AI will not run these commands until you explicitly confirm. This ensures you control when plugins are installed and when the Gateway restarts.

## How to Use

1. Install this skill: `clawhub install mindkeeper`
2. Ask your AI in natural language. On first use, the AI will ask for confirmation before installing the plugin and restarting the Gateway:
   - "What changed in SOUL.md recently?"
   - "Compare my current AGENTS.md to last week's version"
   - "Roll back SOUL.md to yesterday"
   - "Save a checkpoint called 'perfect-personality' before I experiment"

## Examples

| User says | AI action |
|-----------|------------|
| "What changed in SOUL.md?" | `mind_history` with file filter |
| "Show me the diff from last week" | `mind_history` → find commit → `mind_diff` |
| "Undo that change" | `mind_rollback` (preview first, then execute) |
| "Save a checkpoint before I experiment" | `mind_snapshot` with descriptive name |

## Troubleshooting

- **History is empty** — Call `mind_status` to check if mindkeeper is initialized. Make a small edit to a tracked file to trigger the first snapshot.
- **Tools not found** — Ensure the mindkeeper-openclaw plugin is installed and Gateway has been restarted.
- **Rollback not applying** — After rollback, tell the user to run `/new` to reload the session with the restored file.

## Links

- [mindkeeper on GitHub](https://github.com/seekcontext/mindkeeper)
- [mindkeeper-openclaw on npm](https://www.npmjs.com/package/mindkeeper-openclaw)
