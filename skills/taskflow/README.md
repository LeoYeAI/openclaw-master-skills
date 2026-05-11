# TaskFlow

Structured project and task management for OpenClaw agents — markdown-first, SQLite-backed, zero dependencies.

---

![TaskFlow dashboard](examples/dashboard-screenshot.png)

---

## Quick Start

```bash
# 1. Set workspace (add to your shell profile)
export OPENCLAW_WORKSPACE="/path/to/your/.openclaw/workspace"

# 2. Link the CLI
ln -sf "$(pwd)/scripts/taskflow-cli.mjs" /opt/homebrew/bin/taskflow   # macOS
# ln -sf "$(pwd)/scripts/taskflow-cli.mjs" /usr/local/bin/taskflow    # Linux

# 3. Run setup
taskflow setup
```

The setup wizard creates your workspace structure, walks you through your first project, initializes the SQLite database, syncs your markdown files, and optionally installs a macOS LaunchAgent for automatic 60-second sync.

**Non-interactive (scripted installs):**

```bash
taskflow setup --name "My Project" --desc "What it does"
```

---

## Features

- **Markdown-first** — `PROJECTS.md` and `tasks/<slug>-tasks.md` are the source of truth; edit them directly in any editor or agent session
- **SQLite-backed** — bidirectional sync keeps a derived index for fast querying, dashboards, and exports
- **Bidirectional sync** — `files-to-db` and `db-to-files` modes; check for drift with `sync check`
- **CLI** — `taskflow status`, `taskflow add`, `taskflow list`, `taskflow export`, `taskflow sync`, `taskflow setup`
- **JSON export** — full project/task snapshot to stdout, ready for dashboards and integrations
- **LaunchAgent (macOS)** — automatic 60s background sync via `launchctl`; Linux cron instructions included
- **Zero dependencies** — pure Node.js, uses the built-in `node:sqlite` module (no npm install)

---

## CLI

![taskflow status](examples/cli-status.png)

```
taskflow setup               Interactive first-run onboarding
taskflow status              All projects with task counts and progress bars
taskflow sync files-to-db    Sync markdown → SQLite (markdown is authoritative)
taskflow sync db-to-files    Regenerate markdown from DB state
taskflow sync check          Detect drift (exit 1 if mismatch — good for CI)
taskflow export              JSON snapshot to stdout
taskflow init                Bootstrap or re-bootstrap the SQLite schema
taskflow add <project> ...   Add a task with automatic next ID assignment
taskflow list <project>      List current tasks for a project (supports --project and fuzzy name)
taskflow help                Full reference
```

![taskflow help](examples/cli-help.png)


---

## Requirements

- **Node.js 22.5+** (uses `node:sqlite` / `DatabaseSync`)
- macOS or Linux

---

## How It Works

```
<workspace>/
├── PROJECTS.md                  # Project registry (one ## block per project)
├── tasks/<slug>-tasks.md        # Task list per project (five fixed sections)
├── plans/<slug>-plan.md         # Optional: architecture / design docs
└── memory/
    └── taskflow.sqlite          # Derived index — never edit directly
```

Tasks live in five fixed sections: `## In Progress`, `## Pending Validation`, `## Backlog`, `## Blocked`, `## Done`. A task line looks like:

```
- [ ] (task:myproject-007) [P1] [codex] Implement search endpoint
```

The sync engine reads section headers (not checkboxes) to determine task status. Move a line between sections to change status; the LaunchAgent or a manual sync picks it up within 60 seconds.

---

## Agent Integration

TaskFlow is designed to be used by OpenClaw agents as a skill. The agent reads `PROJECTS.md` to discover projects, reads `tasks/<slug>-tasks.md` for current task state, and edits those files directly — no special API needed.

See [SKILL.md](SKILL.md) for the full agent contract: task line format, sync rules, memory integration policy, SQLite query patterns, and known quirks.

---

## Apple Notes Sync (macOS)

`taskflow notes` pushes a live project status summary to Apple Notes -- share it with your team or just keep it on your phone.

![Apple Notes sync](examples/apple-notes-screenshot.png)

---

## Disclaimer

Use at your own risk. We are not liable for any issues you encounter. This is a tool we built for ourselves and found genuinely useful -- sharing it in case other ADHD nerds juggling 10 projects at once get something out of it too. PRs and feedback welcome.

---

## Credits

Built by [Aux](https://github.com/auxclawdbot) (an [OpenClaw](https://openclaw.ai) agent) and [@sm0ls](https://github.com/sm0ls).

## License

MIT
