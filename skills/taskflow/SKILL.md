---
name: taskflow
description: Structured project/task management for OpenClaw agents — markdown-first authoring, SQLite-backed querying, bidirectional sync, CLI, Apple Notes integration.
metadata:
  {
    "openclaw":
      {
        "emoji": "📋",
        "os": ["darwin", "linux"],
        "requires": { "bins": ["node"], "env": ["OPENCLAW_WORKSPACE"] },
      },
  }
---

# TaskFlow — Agent Skill Reference

TaskFlow gives any OpenClaw agent a **structured project/task/plan system** with markdown-first authoring, SQLite-backed querying, and bidirectional sync.

**Principle:** Markdown is canonical. Edit `tasks/*.md` directly. The SQLite DB is a derived index, not the source of truth.

---

## Security

### OPENCLAW_WORKSPACE Trust Boundary

`OPENCLAW_WORKSPACE` is a **high-trust value**. All TaskFlow scripts resolve file paths from it, and the CLI and sync daemon use it to locate the SQLite database, markdown task files, and log directory.

**Rules for safe use:**

1. **Set it only from trusted, controlled sources.** The value must come from:
   - Your own shell profile (`.zshrc`, `.bashrc`, `/etc/environment`)
   - The systemd user unit `Environment=` directive in a template you control
   - The macOS LaunchAgent `EnvironmentVariables` dictionary you installed

   **Never** accept `OPENCLAW_WORKSPACE` from:
   - User-supplied CLI arguments or HTTP request parameters
   - Untrusted config files read at runtime
   - Any external input that has not been explicitly validated

2. **Validate the path exists before use.** Any script that reads `OPENCLAW_WORKSPACE` should confirm the directory exists before proceeding:

   ```js
   import { existsSync } from 'node:fs'
   import path from 'node:path'

   const workspace = process.env.OPENCLAW_WORKSPACE
   if (!workspace) {
     console.error('OPENCLAW_WORKSPACE is not set. Aborting.')
     process.exit(1)
   }
   if (!existsSync(workspace)) {
     console.error(`OPENCLAW_WORKSPACE path does not exist: ${workspace}`)
     process.exit(1)
   }
   // Resolve to absolute path to neutralize any relative-path tricks
   const safeWorkspace = path.resolve(workspace)
   ```

3. **Do not construct paths from untrusted input.** Even with a valid `OPENCLAW_WORKSPACE`, never concatenate unvalidated user input onto it (e.g. `path.join(workspace, userSlug, '../../../etc/passwd')`). Use `path.resolve()` and check that the resolved path starts with the workspace root:

   ```js
   function safeJoin(base, ...parts) {
     const resolved = path.resolve(base, ...parts)
     if (!resolved.startsWith(path.resolve(base) + path.sep)) {
       throw new Error(`Path traversal attempt detected: ${resolved}`)
     }
     return resolved
   }
   ```

4. **Treat `OPENCLAW_WORKSPACE` as a local system path only.** It must point to a directory on the local filesystem. Remote paths (NFS mounts, network shares) may work but are outside the tested configuration and could introduce TOCTOU (time-of-check/time-of-use) race conditions.

---

## Setup

### 1. Set environment variable

Add to your shell profile (`.zshrc`, `.bashrc`, etc.):

```bash
export OPENCLAW_WORKSPACE="/path/to/your/.openclaw/workspace"
```

All TaskFlow scripts and the CLI resolve paths from this variable. Without it, they fall back to `process.cwd()`, which is almost never what you want.

> **See also:** [OPENCLAW_WORKSPACE Trust Boundary](#openclaw_workspace-trust-boundary) above for security requirements.

### 2. Link the CLI

```bash
ln -sf {baseDir}/scripts/taskflow-cli.mjs /opt/homebrew/bin/taskflow  # macOS (Apple Silicon)
# or: ln -sf {baseDir}/scripts/taskflow-cli.mjs /usr/local/bin/taskflow
```

### 3. Run the setup wizard

```bash
taskflow setup
```

The wizard handles the rest: creates workspace directories, walks you through adding your first project(s), initializes the database, syncs, and optionally installs the macOS LaunchAgent for periodic sync.

**Alternative — manual setup:**

<details>
<summary>Manual steps (if you prefer explicit control)</summary>

```bash
# Create workspace dirs
mkdir -p "$OPENCLAW_WORKSPACE/tasks" "$OPENCLAW_WORKSPACE/plans" "$OPENCLAW_WORKSPACE/memory" "$OPENCLAW_WORKSPACE/logs"

# Bootstrap the DB schema
taskflow init

# Create PROJECTS.md and tasks/<slug>-tasks.md manually (see templates/)

# Sync markdown → DB
taskflow sync files-to-db

# Verify
taskflow status
```

</details>

---

## First Run

### For agents (OpenClaw / AI)

When a user asks you to set up TaskFlow or you detect it has not been initialized:

1. **Detect state.** Check for `$OPENCLAW_WORKSPACE/PROJECTS.md` and `$OPENCLAW_WORKSPACE/memory/taskflow.sqlite`.
2. **If clean slate:** Ask the user for their first project name and description, then run:
   ```bash
   taskflow setup --name "Project Name" --desc "One-liner description"
   ```
   Follow up by running `taskflow status` to confirm.
3. **If PROJECTS.md exists but no DB:** Run `taskflow setup` (it detects the state automatically and offers to init + sync).
4. **If both exist:** Run `taskflow status` — already set up.
5. After setup, update `AGENTS.md` with the new project slug so future sessions discover it via `cat PROJECTS.md`.

### For humans (CLI)

```bash
taskflow setup
```

The interactive wizard will:
- Detect your existing workspace state
- Walk you through naming your first project(s)
- Create `PROJECTS.md` and `tasks/<slug>-tasks.md` from templates
- Initialize the SQLite database and sync
- Offer to install the periodic-sync daemon (LaunchAgent on macOS, systemd timer on Linux) for automatic 60s sync

**Non-interactive (scripted installs):**

```bash
taskflow setup --name "My Project" --desc "What it does"
```

Passing `--name` skips all interactive prompts (daemon install is also skipped in non-interactive mode).

---

## Directory Layout

```
<workspace>/
├── PROJECTS.md                      # Project registry (one ## block per project)
├── tasks/<slug>-tasks.md            # Task list per project
├── plans/<slug>-plan.md             # Optional: architecture/design doc per project
└── taskflow/
    ├── SKILL.md                     # This file
    ├── scripts/
    │   ├── taskflow-cli.mjs         # CLI entry point (symlink target)
    │   ├── task-sync.mjs            # Bidirectional markdown ↔ SQLite sync
    │   ├── init-db.mjs              # Bootstrap SQLite schema (idempotent)
    │   ├── export-projects-overview.mjs  # JSON export of project/task state
    │   └── apple-notes-export.mjs   # Optional: project state → Apple Notes (macOS only)
    ├── templates/                   # Starter files for new projects
    ├── schema/
    │   └── taskflow.sql             # Full DDL
    └── system/
        ├── com.taskflow.sync.plist.xml  # Periodic sync (macOS LaunchAgent)
        ├── taskflow-sync.service        # Periodic sync (Linux systemd user unit)
        └── taskflow-sync.timer          # Systemd timer (60s interval)
<workspace>/
└── taskflow.config.json                 # Apple Notes config (auto-created on first notes run)
```

---

## Creating a Project

Follow this full checklist when creating a new project:

### 1. Add a block to `PROJECTS.md`

```markdown
## <slug>
- Name: <Human-Readable Name>
- Status: active
- Description: One-sentence description of the project.
```

- `slug` is lowercase, hyphenated (e.g., `my-project`). It becomes the canonical project ID everywhere.
- Valid status values: `active`, `paused`, `done`.

### 2. Create the task file

Copy `taskflow/templates/tasks-template.md` → `tasks/<slug>-tasks.md` and update the project name in the heading.

The file **must** contain these five section headers in this order:

```markdown
# <Project Name> — Tasks

## In Progress
## Pending Validation
## Backlog
## Blocked
## Done
```

### 3. Optionally create a plan file

Copy `taskflow/templates/plan-template.md` → `plans/<slug>-plan.md` for architecture docs, design decisions, and phased roadmaps. Plan files are **not** synced to SQLite — they are reference-only for the agent.

### 4. DB row (auto-created on first sync)

You do **not** need to manually insert into the `projects` table. The sync engine auto-creates the project row from `PROJECTS.md` on the next `files-to-db` run. If you want to be explicit via Node.js, use a parameterized statement:

```js
// Safe: parameterized insert — no string interpolation in the SQL
db.prepare(`INSERT INTO projects (id, name, description, status)
            VALUES (:id, :name, :description, 'active')`)
  .run({ id: slug, name: projectName, description: projectDesc })
```

---

## Task Line Format

Every task line follows this exact format:

```
- [x| ] (task:<id>) [<priority>] [<owner>] <title>
```

| Field | Details |
|---|---|
| `[ ]` / `[x]` | Open / completed. Sync drives status from section header, not this checkbox. |
| `(task:<id>)` | Task ID. Format: `<slug>-NNN` (zero-padded 3-digit). Sequential per project. |
| `[<priority>]` | **Required. Must come before owner tag.** See priority table below. |
| `[<owner>]` | Optional. Agent/model tag (e.g., `codex`, `sonnet`, `claude`). |
| `<title>` | Human-readable task title. |

### ⚠️ Tag Order Rule

**Priority tag MUST come before owner tag.** The sync parser is positional — it reads the first `[Px]` bracket as priority, and the next `[tag]` as owner. Swapping them will misparse the task.

### ⚠️ Title Sanitization Rules

Task titles must be **plain text only**. Before writing any user-supplied string as a task title, apply the following rules:

1. **Reject lines that look like section headers.** A title may not start with one or more `#` characters followed by a space (e.g. `# My heading`, `## Done`). These would corrupt the sync parser's section detection.

2. **Reject the exact section header strings** even without leading whitespace:
   - `In Progress`, `Pending Validation`, `Backlog`, `Blocked`, `Done`
   - Comparison must be case-insensitive.

3. **Escape or strip markdown special characters** that have structural meaning in the task file:

   | Character | Risk | Safe action |
   |-----------|------|-------------|
   | `#`       | Looks like a header | Strip or reject |
   | `- ` (dash + space at line start) | Looks like a list item / task | Strip leading `- ` |
   | `[ ]` / `[x]` | Looks like a checkbox | Escape brackets: `\[` `\]` |
   | `]` / `[` alone | Can corrupt `(task:id)` parse | Escape: `\[` `\]` |
   | Newlines (`\n`, `\r`) | Creates multi-line titles | Strip / reject |

4. **Maximum length.** Titles should be ≤ 200 characters. Truncate or reject longer strings.

**Example sanitization (Node.js):**

```js
// Safe: sanitize a user-supplied task title before writing to markdown
function sanitizeTitle(raw) {
  if (typeof raw !== 'string') throw new TypeError('title must be a string')

  // Strip newlines
  let title = raw.replace(/[\r\n]+/g, ' ').trim()

  // Reject lines that look like section headers (# Heading or bare header words)
  if (/^#{1,6}\s/.test(title)) {
    throw new Error('Title may not start with a markdown heading (#)')
  }
  const BANNED_HEADERS = /^(in progress|pending validation|backlog|blocked|done)$/i
  if (BANNED_HEADERS.test(title)) {
    throw new Error('Title may not be a reserved section header name')
  }

  // Escape structural markdown characters
  title = title
    .replace(/\[/g, '\\[')
    .replace(/\]/g, '\\]')

  // Enforce length limit
  if (title.length > 200) {
    throw new Error('Title exceeds 200 character limit')
  }

  return title
}
```

These rules apply whenever a task title comes from **any external or user-supplied source** (CLI args, API payloads, file imports). Titles hard-coded by agents in their own sessions are low-risk but should still avoid structural characters.

✅ Correct: `- [ ] (task:myproject-007) [P1] [codex] Implement search`
❌ Wrong:   `- [ ] (task:myproject-007) [codex] [P1] Implement search`

### Priority Levels (Configurable)

| Tag | Default Meaning |
|---|---|
| `P0` | Critical — must do now, blocks everything |
| `P1` | High — important, do soon |
| `P2` | Normal — standard priority (default) |
| `P3` | Low — nice to have |
| `P9` | Someday — no urgency, parking lot |

Priorities are configurable per-installation but the tags themselves (`P0`–`P3`, `P9`) are what the sync engine validates.

### Optional Note Lines

A note can follow a task line as an indented `- note:` line:

```markdown
- [ ] (task:myproject-003) [P1] [codex] Implement auth flow
  - note: blocked on API key from vendor
```

> **Known limitation (v1):** Notes are one-way. Removing or editing a note in markdown does not propagate to the DB. This is tracked for a post-MVP fix.

### Example Task File Section

```markdown
## In Progress
- [ ] (task:myproject-001) [P1] [codex] Wire up OAuth login
  - note: PR open, needs review

## Backlog
- [ ] (task:myproject-002) [P2] Add rate limiting middleware
- [ ] (task:myproject-003) [P3] Write integration tests
```

---

## Adding a New Task

1. **Determine the next ID.** Scan the task file for the highest existing `<slug>-NNN` and increment by 1. Or query SQLite using a **parameterized statement** (never interpolate the slug into SQL strings):

   ```js
   // Node.js — safe, parameterized
   const db = new DatabaseSync(dbPath)
   const row = db
     .prepare(`SELECT MAX(CAST(SUBSTR(id, LENGTH(:slug) + 2) AS INTEGER)) AS max_seq
               FROM tasks_v2
               WHERE project_id = :slug`)
     .get({ slug: projectSlug })
   const nextSeq = (row.max_seq ?? 0) + 1
   const nextId  = `${projectSlug}-${String(nextSeq).padStart(3, '0')}`
   ```

   > ⚠️ **Never construct SQL by string interpolation.** Use `db.prepare()` with named or positional parameters (`?` or `:name`) for all values that come from external input. This applies even for read-only queries.

2. **Append the task line** to the correct section (`## Backlog` for new work, `## In Progress` if starting immediately).

3. **Format the line** using the exact format above. No trailing spaces. Priority tag before owner tag.

---

## Updating Task Status

**Move the task line** from its current section to the target section in the markdown file.

| Target State | Move to Section |
|---|---|
| Started / picked up | `## In Progress` |
| Needs human review | `## Pending Validation` |
| Not started yet | `## Backlog` |
| Waiting on dependency | `## Blocked` |
| Finished | `## Done` |

Also flip the checkbox: `[ ]` for active states, `[x]` for `Done` (and optionally `Pending Validation`).

The periodic sync (60s) will pick up the change and update SQLite automatically. To force an immediate sync:

```bash
node taskflow/scripts/task-sync.mjs files-to-db
```

---

## Querying Tasks

### Simple: Read the markdown file directly

```bash
cat tasks/<slug>-tasks.md
```

For a quick in-session view, just read the relevant section.

### Advanced: Query SQLite

> ⚠️ **SQL Safety Rule:** Any query that incorporates a variable value (project slug, task ID, status string, etc.) **must** use parameterized statements — not string interpolation. The `sqlite3` CLI examples below use only **static, hardcoded literal values** and are shown as diagnostic/inspection tools only. For programmatic use, always use the Node.js `db.prepare()` API with bound parameters.

#### sqlite3 CLI (static queries — for manual inspection only)

```bash
# All in-progress tasks across all projects (by priority)
# Safe: 'in_progress' is a static literal, not a variable
sqlite3 "$OPENCLAW_WORKSPACE/memory/taskflow.sqlite" \
  "SELECT id, project_id, priority, title
   FROM tasks_v2
   WHERE status = 'in_progress'
   ORDER BY priority, project_id;"

# Task count by status per project (no variables — safe for CLI)
sqlite3 "$OPENCLAW_WORKSPACE/memory/taskflow.sqlite" \
  "SELECT project_id, status, COUNT(*) AS count
   FROM tasks_v2
   GROUP BY project_id, status
   ORDER BY project_id, status;"
```

> Do **not** embed shell variables directly in the SQL string (e.g. `WHERE project_id = '$SLUG'`). That pattern is SQL injection waiting to happen. Use the Node.js API with parameters instead.

#### Node.js API — parameterized queries (required for programmatic use)

```js
import { DatabaseSync } from 'node:sqlite'
import path from 'node:path'

const dbPath = path.join(process.env.OPENCLAW_WORKSPACE, 'memory', 'taskflow.sqlite')
const db = new DatabaseSync(dbPath)
db.exec('PRAGMA foreign_keys = ON')

// ── Backlog for a specific project ─────────────────────────────
// :slug is a named parameter — never interpolated into the SQL string
const backlog = db
  .prepare(`SELECT id, priority, title
            FROM tasks_v2
            WHERE project_id = :slug AND status = 'backlog'
            ORDER BY priority`)
  .all({ slug: 'my-project' })  // value bound at runtime, never in SQL string

// ── Audit trail for a specific task ────────────────────────────
const transitions = db
  .prepare(`SELECT from_status, to_status, actor, at
            FROM task_transitions_v2
            WHERE task_id = ?
            ORDER BY at`)
  .all('my-project-007')  // positional parameter — also safe

// ── Write: update task status ───────────────────────────────────
// NEVER: db.exec(`UPDATE tasks_v2 SET status='${newStatus}' WHERE id='${id}'`)
// ALWAYS:
db.prepare(`UPDATE tasks_v2 SET status = :status, updated_at = datetime('now')
            WHERE id = :id`)
  .run({ status: 'done', id: 'my-project-007' })
```

### CLI Quick Reference

```bash
# Terminal summary: all projects + task counts by status
taskflow status

# Add a task in markdown with automatic next ID
taskflow add taskflow "Implement quick add command" --priority P1 --owner codex

# List current tasks for a project (excludes done by default)
taskflow list taskflow
taskflow list --project "TaskFlow" --all
taskflow list task --status backlog,pending_validation --json

# JSON export of full project/task state (for dashboards, integrations)
node taskflow/scripts/export-projects-overview.mjs

# Detect drift between markdown and DB (exit 1 if mismatch)
node taskflow/scripts/task-sync.mjs check

# Sync markdown → DB (normal direction; run after editing task files)
node taskflow/scripts/task-sync.mjs files-to-db

# Sync DB → markdown (run after programmatic DB updates)
node taskflow/scripts/task-sync.mjs db-to-files
```

### Apple Notes Export (Optional — macOS Only)

TaskFlow can maintain a live Apple Note with your current project status. The note is rendered as rich HTML and written via AppleScript.

```bash
# Push current status to Apple Notes (creates note on first run)
taskflow notes
```

On first run (or during `taskflow setup`), a new note is created in the configured folder and its Core Data ID is saved to:

```
$OPENCLAW_WORKSPACE/taskflow.config.json
```

Config schema:

```json
{
  "appleNotesId":     "x-coredata://...",
  "appleNotesFolder": "Notes",
  "appleNotesTitle":  "TaskFlow - Project Status"
}
```

**Important — never delete the shared note.** The note is always edited in-place. Deleting and recreating it generates a new Core Data ID and breaks any existing share links. If the note is accidentally deleted, `taskflow notes` will create a new one and update the config automatically.

For hourly auto-refresh, add a cron entry:

```bash
# Run: crontab -e
0 * * * * OPENCLAW_WORKSPACE=/path/to/workspace /path/to/node /path/to/taskflow/scripts/apple-notes-export.mjs
```

Or install a dedicated LaunchAgent (macOS) targeting `apple-notes-export.mjs` with an hourly `StartInterval` of `3600`.

This feature is entirely optional and macOS-specific. On other platforms, `taskflow notes` exits gracefully with a message.

---

## Memory Integration Rules

These rules keep daily memory logs clean and prevent duplication.

### ✅ Do

- Reference task IDs in daily memory logs when you complete or advance work:
  ```
  Completed `myproject-007` (OAuth login). Moved `myproject-008` to In Progress.
  ```
- Keep memory entries narrative — what happened, what you decided, what's next.

### ❌ Do Not

- **Never duplicate the backlog in daily memory files.** `tasks/<slug>-tasks.md` is the single source of truth for all pending work. Memory files should not list what's left to do.
- Do not track task state changes in memory (e.g., "Task 007 is now in progress"). Only note meaningful progress events or decisions.
- Do not create new tasks in memory files. Add them to the task file directly.

### Pattern: Loading Project Context

At the start of a session involving a project:

1. `cat PROJECTS.md` — identify the project slug and status
2. `cat tasks/<slug>-tasks.md` — load current task state
3. `cat plans/<slug>-plan.md` — load architecture context (if it exists)
4. Begin work. Record task ID references in memory at session end.

---

## Periodic Sync Daemon

The sync daemon runs `task-sync.mjs files-to-db` every **60 seconds** in the background. This means markdown edits are automatically reflected in SQLite within a minute.

- Logs: `logs/taskflow-sync.stdout.log` and `logs/taskflow-sync.stderr.log` (relative to workspace)
- Lock: Advisory TTL lock in `sync_state` table prevents concurrent syncs
- Conflict resolution: Last-write-wins per sync direction

### Quickest install (auto-detects OS)

```bash
taskflow install-daemon
```

This detects your platform and installs the appropriate unit. On macOS it installs and loads the LaunchAgent; on Linux it writes systemd user units and enables the timer.

### macOS — LaunchAgent (manual steps)

Templates: `taskflow/system/com.taskflow.sync.plist.xml`

1. Copy `taskflow/system/com.taskflow.sync.plist.xml` → `~/Library/LaunchAgents/com.taskflow.sync.plist`
2. Replace `{{workspace}}` with the absolute path to your workspace (no trailing slash)
3. Replace `{{node}}` with the path to your `node` binary (`which node`)
4. Load: `launchctl load ~/Library/LaunchAgents/com.taskflow.sync.plist`
5. Verify: `launchctl list | grep taskflow`

Uninstall:
```bash
launchctl unload ~/Library/LaunchAgents/com.taskflow.sync.plist
rm ~/Library/LaunchAgents/com.taskflow.sync.plist
```

### Linux — systemd user timer (manual steps)

Templates: `taskflow/system/taskflow-sync.service` and `taskflow/system/taskflow-sync.timer`

```bash
# Create the user unit directory
mkdir -p ~/.config/systemd/user

# Copy templates, replacing placeholders
sed -e "s|{{workspace}}|$OPENCLAW_WORKSPACE|g" \
    -e "s|{{node}}|$(which node)|g" \
    taskflow/system/taskflow-sync.service > ~/.config/systemd/user/taskflow-sync.service

sed -e "s|{{workspace}}|$OPENCLAW_WORKSPACE|g" \
    -e "s|{{node}}|$(which node)|g" \
    taskflow/system/taskflow-sync.timer  > ~/.config/systemd/user/taskflow-sync.timer

# Enable and start
systemctl --user daemon-reload
systemctl --user enable --now taskflow-sync.timer
```

Verify:
```bash
systemctl --user status taskflow-sync.timer
journalctl --user -u taskflow-sync.service
```

Uninstall:
```bash
systemctl --user disable --now taskflow-sync.timer
rm ~/.config/systemd/user/taskflow-sync.{service,timer}
systemctl --user daemon-reload
```

> **Note:** systemd user units require a login session. To run them without an interactive session (e.g. on a server), enable lingering: `loginctl enable-linger $USER`

---

## Section Header → DB Status Map

| Markdown Header | DB `status` value |
|---|---|
| `## In Progress` | `in_progress` |
| `## Pending Validation` | `pending_validation` |
| `## Backlog` | `backlog` |
| `## Blocked` | `blocked` |
| `## Done` | `done` |

**Section headers are fixed.** Do not rename them. The sync parser maps these exact strings.

---

## Known Quirks

Things that work but might trip you up:

- **`MAX(id)` is lexicographic.** Task IDs are text, so `SELECT MAX(id)` works only because IDs are zero-padded (`-001`, `-002`). If you create `-1` instead of `-001`, sequencing breaks. Always zero-pad to 3 digits.
- **Checkbox state is decorative.** Status comes from which `##` section a task lives under, not whether it's `[x]` or `[ ]`. The sync engine ignores the checkbox on read. On write-back, `done` tasks get `[x]`, everything else gets `[ ]`.
- **Notes survive deletion.** If you remove a `- note:` line from markdown, the old note stays in the DB (COALESCE preserves it). This is intentional for v1 -- notes are one-way display. To truly clear a note, update the DB directly.
- **Lock TTL is 60 seconds.** If a sync crashes without releasing the lock, the next run will be blocked for up to 60s. The SIGTERM/SIGINT handlers try to clean up, but a `kill -9` won't. The lock auto-expires.
- **Auto-project creation derives names from slugs.** If sync encounters a task file with no matching `projects` row, it creates one with a name like "My Project" from slug "my-project". The name might not be what you want -- fix it in PROJECTS.md and re-sync.
- **Tag order is strict.** `[P1] [codex]` works. `[codex] [P1]` silently assigns `codex` as... nothing useful. Priority tag must come first.

---

## Known Limitations (v1)

- Notes are one-way (markdown → DB). Removing a note in markdown does not clear it in DB.
- `db-to-files` rewrites all project task files, even unchanged ones.
- One task file per project (1:1 mapping). Multiple files per project is post-MVP.
- Periodic sync daemon: macOS (LaunchAgent) and Linux (systemd user timer) are supported. Run `taskflow install-daemon` to install.
- Node.js 22.5+ required (`node:sqlite`). No Python fallback in v1.

---

## Quick Cheat Sheet

```
New project:   PROJECTS.md block + tasks/<slug>-tasks.md + optional plans/<slug>-plan.md
New task:      taskflow add <project> "title" (or append manually to section)
Update status: Move line to correct ## section, flip checkbox if needed
Query simple:  cat tasks/<slug>-tasks.md
Query complex: Use db.prepare('SELECT ... WHERE id = ?').all(id) — never interpolate variables into SQL
CLI status:    taskflow status
CLI add:       taskflow add dashboard "Fix cron panel" --priority P1 --owner codex
Force sync:    node taskflow/scripts/task-sync.mjs files-to-db
Memory rule:   Reference IDs in logs; never copy backlog into memory
```
