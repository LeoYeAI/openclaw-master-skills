# Screenshot Preparation Guideline for ClawHub

This guide walks you through preparing the environment and demo data before taking screenshots for the mindkeeper skill listing on ClawHub.

See [CLAWHUB_PUBLISH.md](../../../../CLAWHUB_PUBLISH.md) for the full publishing workflow.

## Prerequisites

- **Node.js** ≥ 22
- **OpenClaw** installed and configured
- **Gateway** running (e.g. `openclaw start` or desktop app)
- A **workspace** with agent context files (SOUL.md, AGENTS.md, etc.)

---

## Phase 1: Environment Setup

### 1.1 Install mindkeeper plugin

```bash
openclaw plugins install mindkeeper-openclaw
```

Restart the Gateway so the plugin loads and the mind_* tools become available.

### 1.2 Identify your workspace

mindkeeper tracks files in your OpenClaw workspace. Typical locations:

- `~/.openclaw/workspace/` (default)
- Or the workspace configured in `~/.openclaw/openclaw.json`

Ensure the workspace contains at least:

- `SOUL.md`
- `AGENTS.md` (optional but helpful)

If these files don't exist, create minimal placeholder content:

```bash
# Example: create SOUL.md
echo "# Agent Personality" > ~/.openclaw/workspace/SOUL.md
echo "You are a helpful assistant." >> ~/.openclaw/workspace/SOUL.md
```

### 1.3 Verify mindkeeper is running

```bash
openclaw mind status
```

You should see workspace path, pending changes count, and named snapshots. The plugin uses your configured OpenClaw workspace automatically.

---

## Phase 2: Build Demo History

mindkeeper auto-snapshots after changes with a **30-second debounce**. Plan edits with gaps or wait ~30s between edits.

### 2.1 Create initial history (Day 1 simulation)

**Edit 1** — Add content to SOUL.md:

```markdown
# Agent Personality

You are a helpful assistant. You prefer concise answers.
```

Save and wait **≥30 seconds** for the auto-snapshot to run (mindkeeper debounces changes).

**Edit 2** — Change SOUL.md:

```markdown
# Agent Personality

You are a helpful assistant. You prefer concise answers and use markdown when useful.
```

Save and wait **≥30 seconds**.

**Edit 3** — Add more:

```markdown
# Agent Personality

You are a helpful assistant. You prefer concise answers and use markdown when useful.
You avoid being overly verbose.
```

Save and wait **≥30 seconds**.

### 2.2 Create a named snapshot (for Screenshot 3)

```bash
openclaw mind snapshot before-experiment
```

Or ask the AI: "Save a checkpoint called 'before-experiment' before I make changes."

### 2.3 Verify history exists

```bash
openclaw mind history SOUL.md
```

You should see at least 3–4 commits with short hashes (e.g. `a1b2c3d4`). Note one or two hashes for the diff example.

---

## Phase 3: Screenshot Checklist

Before taking screenshots, confirm:

- [ ] Gateway is running
- [ ] mindkeeper plugin is installed and loaded
- [ ] `openclaw mind status` shows workspace and tracked info
- [ ] `openclaw mind history SOUL.md` shows at least 3 commits
- [ ] You have a named snapshot (e.g. `before-experiment`)
- [ ] Screen resolution is 1920×1080 or 1280×720
- [ ] UI is clean (close unnecessary panels, hide clutter)

---

## Phase 4: Screenshot Order

Take screenshots in this order so the conversation state stays consistent:

| # | Screenshot | User prompt | What to capture |
|---|------------|-------------|-----------------|
| 1 | Hero | "What changed in SOUL.md recently?" | User question + AI response with history list |
| 2 | Diff | "Compare my current SOUL.md to the previous version" or "Show me the diff between SOUL.md now and [paste a hash from history]" | AI response with diff output |
| 3 | Snapshot | "Save a checkpoint called 'demo-checkpoint'" | AI success message confirming snapshot |
| 4 | Rollback | "Roll back SOUL.md to the previous version" | AI preview diff + confirmation prompt |
| 5 | Status | "Is mindkeeper tracking my files?" | AI response with `mind_status` output |

---

## Phase 5: Save & Name

Save screenshots as PNG in:

```
packages/openclaw/skills/mindkeeper/screenshots/
```

Suggested filenames:

- `01-hero-history.png`
- `02-diff.png`
- `03-snapshot.png`
- `04-rollback-preview.png`
- `05-status.png`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `mind_status` / tools not found | Restart Gateway after plugin install |
| History is empty | Make edits, wait 30s between each, or run `openclaw mind snapshot <name>` |
| "No commits" in diff | Ensure you have at least 2 commits; use `mind_history` to get valid hashes |
| Diff shows nothing | Use `from` and `to` hashes from `mind_history`; omit `to` to compare to current |
| Rollback fails | Ensure the target commit exists; use `mind_history` to verify hashes |

---

## Quick Reference

```bash
# Check status
openclaw mind status

# View history (get commit hashes for diff/rollback)
openclaw mind history SOUL.md

# Create named snapshot
openclaw mind snapshot <name>
```

Note: `openclaw mind` only exposes status, history, and snapshot. For diff and rollback, use the AI (mind_diff, mind_rollback tools) or the standalone `mindkeeper` CLI if installed.
