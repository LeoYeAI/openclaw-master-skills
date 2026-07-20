---
title: Quick Start
description: Get your first pipeline running in 60 seconds
---

## 1. Initialize

Navigate to your project and run:

```bash
cd /path/to/your/project
shiploop init
```

Ship Loop auto-detects your framework (Node.js, Python, Rust, Go), deploy provider (Vercel, Netlify), and creates a `SHIPLOOP.yml` with sensible defaults.

You'll be prompted for:
- **Project name** (defaults to directory name)
- **Site URL** (your production deployment URL)
- **Agent** (pick a preset or enter a custom command)

## 2. Define Segments

Edit `SHIPLOOP.yml` and replace the example segment with your features:

```yaml
segments:
  - name: "dark-mode"
    prompt: |
      Add dark mode support using CSS custom properties.
      Add a toggle button in the header.
      Persist the user's preference in localStorage.

  - name: "search"
    prompt: |
      Add a search bar to the homepage.
      Search should filter the existing content list.
      Include keyboard shortcut: Cmd+K / Ctrl+K.
    depends_on: [dark-mode]
```

Each segment has:
- `name`: identifier (used in git tags and learnings)
- `prompt`: what the coding agent should build
- `depends_on`: (optional) segments that must ship first

## 3. Run

```bash
shiploop run
```

Ship Loop will:
1. Pick the first eligible segment (dependencies met)
2. Send the prompt to your coding agent
3. Run preflight checks (build, lint, test)
4. If preflight fails, enter the repair loop
5. If repair stalls, enter the meta loop with experiments
6. On success: commit, push, verify deployment, tag
7. Move to the next segment

## 4. Monitor

While running, you'll see live output:

```
🚢 Ship Loop: My App (2 segments)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔄 Segment 1/2: dark-mode
   🤖 coding... → ✅ completed in 180s
   🛫 preflight... → ✅ passed
   📦 Committed: a1b2c3d
   ✅ Deploy verified
✅ dark-mode — shipped [$0.38]
```

Check status anytime:

```bash
shiploop status
```

Check costs:

```bash
shiploop budget
```

## 5. Recover from Crashes

State is checkpointed after every transition. If the process dies:

```bash
shiploop run   # Picks up where it left off
```

Failed segments are detected and marked. Reset them to retry:

```bash
shiploop reset dark-mode
shiploop run
```

## Next Steps

- [Architecture](/ship-loop/concepts/architecture/) to understand the three loops
- [Configuration](/ship-loop/reference/configuration/) for the full SHIPLOOP.yml reference
- [Agent Presets](/ship-loop/guides/agent-presets/) to set up your coding agent
