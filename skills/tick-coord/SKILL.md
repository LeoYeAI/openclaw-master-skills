---
name: tick-coord
description: "Multi-agent task coordination via Git-backed Markdown (tick-md). Use when coordinating work across avatars or agents, managing tasks, tracking dependencies, or running multi-agent workflows with TICK.md files."
license: MIT
---

# Tick Multi-Agent Coordination

Coordinate work across human and AI agents using structured Markdown files. Users interact naturally with you, and you maintain tasks transparently in TICK.md.

> **Source:** Built and linked from `~/clawd/projects/tick-md/cli`. To rebuild after changes: `cd ~/clawd/projects/tick-md/cli && npm run build`

## Installation

**Prerequisites**: The Tick CLI and MCP server should already be installed and configured by your environment.

**First time setup?** See `INSTALL.md` for editor-specific installation instructions.

**Quick Check**:
```bash
# Verify CLI is available
tick --version

# Check if TICK.md exists in project
ls TICK.md

# If not, initialize
tick init
```

## Core Concept

**Tick Protocol** = Git-based task coordination via TICK.md files
- **Human-readable**: Standard Markdown with YAML
- **Machine-parseable**: Structured for tools
- **Git-backed**: Full version control and audit trail
- **Local-first**: No cloud required

## Quick Start

### Check if Tick is initialized
```bash
ls TICK.md
```

### If not initialized
```bash
tick init
```

### Get current status
```bash
tick status
```

## Common Workflows

### 1. User Asks You to Do Something

**User**: "Can you refactor the authentication system?"

**Your Actions**:
```bash
# 1. Create task
tick add "Refactor authentication system" --priority high --tags backend,security

# 2. Register yourself (first time only)
tick agent register @your-name --type bot --roles "engineer,refactoring"

# 3. Claim the task
tick claim TASK-XXX @your-name

# 4. Work on it (do the actual work)

# 5. Add progress comments
tick comment TASK-XXX @your-name --note "Analyzing current auth flow"
tick comment TASK-XXX @your-name --note "Refactored to use JWT tokens"

# 6. Mark complete
tick done TASK-XXX @your-name
```

### 2. User Asks About Project Status

**User**: "What tasks are we working on?"

```bash
# Get comprehensive status
tick status

# Or filter and list tasks
tick list --status in_progress
tick list --claimed-by @bot-name
```

Summarize the output naturally for the user.

### 3. Coordination with Other Agents

**User**: "Have the other agents finished their tasks?"

```bash
# Check overall status
tick status

# List agents and their work
tick agent list --verbose

# Validate the project
tick validate
```

### 4. Breaking Down Complex Work

**User**: "Build a user dashboard with charts and data export"

**Your Actions**:
```bash
# Create parent task
tick add "Build user dashboard" --priority high --tags frontend

# Create subtasks with dependencies
tick add "Design dashboard layout" --priority high --tags frontend,design
tick add "Implement data charts" --priority medium --tags frontend,charts --depends-on TASK-XXX
tick add "Add CSV export" --priority low --tags frontend,export --depends-on TASK-XXX

# Visualize dependencies
tick graph
```

## Command Reference

### Project Management
```bash
tick init                          # Initialize new project
tick status                        # View project overview
tick list                          # List tasks with filters
tick graph                         # Visualize dependencies
tick watch                         # Monitor changes in real-time
tick validate                      # Check for errors
tick sync --push                   # Commit and push to git
```

### Task Operations
```bash
tick add "Task title" \
  --priority high \                # urgent|high|medium|low
  --tags backend,api \             # Comma-separated tags
  --assigned-to @agent \           # Assign to agent
  --depends-on TASK-001 \          # Dependencies
  --estimated-hours 4              # Time estimate

tick claim TASK-001 @agent         # Claim task (sets in_progress)
tick release TASK-001 @agent       # Release task (back to todo)
tick done TASK-001 @agent          # Complete task
tick reopen TASK-001 @agent        # Reopen completed task
tick delete TASK-001               # Delete a task
tick comment TASK-001 @agent \     # Add note
  --note "Progress update"
tick edit TASK-001 \               # Direct field edit
  --title "New title" \
  --priority high \
  --status in_progress
```

### Corrections & Recovery
```bash
tick reopen TASK-001 @agent        # Reopen completed task
tick reopen TASK-001 @agent \      # Reopen and re-block dependents
  --re-block

tick delete TASK-001               # Delete task, cleans up deps
tick delete TASK-001 --force       # Delete even if has dependents

tick edit TASK-001 --title "X"     # Change title
tick edit TASK-001 --priority high # Change priority
tick edit TASK-001 --status todo   # Change status directly
tick edit TASK-001 --tags a,b,c    # Replace tags
tick edit TASK-001 --add-tag new   # Add tag
tick edit TASK-001 --remove-tag old # Remove tag
tick edit TASK-001 \               # Edit dependencies
  --depends-on TASK-002,TASK-003

tick undo                          # Undo last tick operation
tick undo --dry-run                # Preview what would be undone
```

### Bulk Operations
```bash
tick import tasks.yaml             # Import tasks from YAML file
tick import - < tasks.yaml         # Import from stdin
tick import tasks.yaml --dry-run   # Preview import

tick batch start                   # Begin batch mode (no auto-commit)
tick batch status                  # Check batch status
tick batch commit                  # Commit all batched changes
tick batch abort                   # Discard batched changes
```

### Advanced Task Listing
```bash
tick list                          # All tasks, grouped by status
tick list --status blocked         # Only blocked tasks
tick list --priority urgent        # High-priority tasks
tick list --assigned-to @alice     # Tasks for specific agent
tick list --tag backend            # Tasks with tag
tick list --json                   # JSON output for scripts
```

### Dependency Visualization
```bash
tick graph                         # ASCII dependency tree
tick graph --format mermaid        # Mermaid flowchart
tick graph --show-done             # Include completed tasks
```

### Real-time Monitoring
```bash
tick watch                         # Watch for changes
tick watch --interval 10           # Custom polling interval
tick watch --filter in_progress    # Only show specific status
```

### Agent Management
```bash
tick agent register @name \        # Register new agent
  --type bot \                     # human|bot
  --roles "dev,qa" \               # Comma-separated roles
  --status idle                    # working|idle|offline

tick agent list                    # List all agents
tick agent list --verbose          # Detailed info
tick agent list --type bot         # Filter by type
tick agent list --status working   # Filter by status
```

## MCP Tools (Alternative to CLI)

If using Model Context Protocol, use these tools instead of CLI commands:

### Status and Inspection
- `tick_status` - Get project status (agents, tasks, progress)
- `tick_validate` - Validate TICK.md structure
- `tick_agent_list` - List agents with optional filters

### Task Management
- `tick_add` - Create new task
- `tick_claim` - Claim task for agent
- `tick_release` - Release claimed task
- `tick_done` - Complete task (auto-unblocks dependents)
- `tick_comment` - Add note to task

### Corrections & Recovery
- `tick_reopen` - Reopen completed task
- `tick_delete` - Delete a task
- `tick_edit` - Direct field edit (bypasses state machine)
- `tick_undo` - Undo last tick operation

### Agent Operations
- `tick_agent_register` - Register new agent

**MCP Example**:
```javascript
// Create task via MCP
await tick_add({
  title: "Refactor authentication",
  priority: "high",
  tags: ["backend", "security"],
  assignedTo: "@bot-name"
})

// Claim it
await tick_claim({
  taskId: "TASK-023",
  agent: "@bot-name"
})
```

## Best Practices

### 1. Natural Conversation First

✅ **Good**: User says "refactor the auth", you create task automatically
❌ **Bad**: Making user explicitly create tasks

### 2. Always Use Your Agent Name

Register once:
```bash
tick agent register @your-bot-name --type bot --roles "engineer"
```

Then use consistently:
```bash
tick claim TASK-001 @your-bot-name
tick done TASK-001 @your-bot-name
```

### 3. Provide Context in Comments

```bash
# ✅ Good - explains what and why
tick comment TASK-005 @bot --note "Switched from REST to GraphQL for better type safety and reduced over-fetching"

# ❌ Bad - too vague
tick comment TASK-005 @bot --note "Updated API"
```

### 4. Break Down Large Tasks

Create subtasks with dependencies:
```bash
tick add "Set up CI/CD pipeline" --priority high
tick add "Configure GitHub Actions" --depends-on TASK-010
tick add "Add deployment scripts" --depends-on TASK-011
tick add "Set up staging environment" --depends-on TASK-011
```

### 5. Check Status Before Claiming

```bash
# Make sure task exists and isn't claimed
tick status

# Then claim
tick claim TASK-XXX @your-name
```

## Understanding TICK.md Structure

The file has three sections:

1. **Frontmatter** (YAML): Project metadata
2. **Agents Table** (Markdown): Who's working on what
3. **Task Blocks** (YAML + Markdown): Individual tasks with history

**Example**:
```markdown
---
project: my-app
schema_version: "1.0"
next_id: 5
---

# Agents

| Name | Type | Roles | Status | Working On |
|------|------|-------|--------|------------|
| @alice | human | owner | working | TASK-003 |
| @bot | bot | engineer | idle | - |

# Tasks

\```yaml
id: TASK-001
title: Build authentication
status: done
priority: high
claimed_by: null
# ... more fields
history:
  - ts: 2026-02-07T10:00:00Z
    who: @bot
    action: created
  - ts: 2026-02-07T14:00:00Z
    who: @bot
    action: done
\```

Implemented JWT-based authentication with token refresh...
```

## Advanced Features

### Automatic Dependency Unblocking

When you complete a task, dependent tasks automatically unblock:
```bash
# TASK-002 depends on TASK-001
# TASK-002 status: blocked

tick done TASK-001 @bot
# TASK-002 automatically changes to: todo
```

### Circular Dependency Detection

Validation catches circular dependencies:
```bash
tick validate
# Error: Circular dependency detected: TASK-001 → TASK-002 → TASK-003 → TASK-001
```

### Smart Commit Messages

```bash
tick sync --push
# Automatically generates: "feat: complete TASK-001, TASK-002; update TASK-003"
```

### Reopening Completed Tasks

If a task was marked done prematurely:
```bash
tick reopen TASK-001 @bot
# Sets status back to in_progress, records in history

tick reopen TASK-001 @bot --re-block
# Also re-blocks any tasks that depend on this one
```

### Fixing Mistakes

```bash
# Undo the last tick operation
tick undo

# Preview what would be undone first
tick undo --dry-run

# Direct field edits (bypasses state machine)
tick edit TASK-001 --status todo --priority urgent
```

### Batch Operations

For multiple changes without individual commits:
```bash
tick batch start
# Now make multiple changes...
tick add "Task 1" --priority high
tick add "Task 2" --priority medium
tick claim TASK-001 @bot
# ...
tick batch commit   # Single commit for all changes
# Or: tick batch abort  # Discard all changes
```

### Real-time Monitoring

```bash
tick watch
# [10:23:45] ✓ Added: TASK-015 - Implement user search
# [10:24:12] 🔒 TASK-015 claimed by @bot
# [10:26:33] ⟳ TASK-015: in_progress → done
```

## Quick Reference Card

```
Workflow:      init → add → claim → work → comment → done → sync
Essential:     status | add | claim | done | list | graph
Corrections:   reopen | delete | edit | undo
Bulk:          import | batch start/commit/abort
Coordination:  agent register | agent list | validate | watch
Git:           sync --pull | sync --push
```

## Key Reminders

1. **Users interact with YOU, not with Tick directly**
2. **YOU maintain the TICK.md transparently**
3. **Dashboard is for inspection, not primary interaction**
4. **Always use your agent name consistently**
5. **Comment frequently to show progress**
6. **Validate before syncing**
7. **Check status before claiming**
8. **Break down complex work into subtasks**

## Project Board (Web Dashboard)

The tick-coord skill includes a built-in web dashboard for visualizing task state. It's an on-demand Astro + React app that reads from the Convex API, similar to how Prisma Studio or Drizzle Studio work. Spin it up when you need to inspect the board, stop it when you're done.

### Launch Project Board

When the user says **"launch project board"**, **"launch kanban"**, **"show me the board"**, **"open dashboard"**, or similar:

```bash
# SKILL_DIR should resolve to wherever tick-coord is installed
SKILL_DIR="<tick-coord-install-path>"

# Start the dashboard
bash "$SKILL_DIR/scripts/tick-board.sh" start

# Check if it's running
bash "$SKILL_DIR/scripts/tick-board.sh" status

# Stop when done
bash "$SKILL_DIR/scripts/tick-board.sh" stop
```

Default port is 3000. Override with `TICK_BOARD_PORT=8080`.

The board fetches live data from the Convex deployment and auto-refreshes every 30 seconds.

### Running the Dev Server (Important)

The dashboard dev server must run as a **detached background process** to avoid being killed by exec tool timeouts. The `tick-board.sh` script handles this automatically using `setsid` and a PID file, but if you need to start it manually:

```bash
# CORRECT — detached, survives exec timeout
cd "$SKILL_DIR/web"
setsid pnpm dev --port 3000 --host 0.0.0.0 </dev/null > /tmp/tick-board.log 2>&1 &
echo $! > /tmp/tick-board.pid

# WRONG — will be killed when exec times out
pnpm dev --port 3000 --host 0.0.0.0
```

Always use the script or the `setsid` pattern. Never run the dev server as a foreground exec command.

### Accessing the Dashboard

The dev server binds to `0.0.0.0`, making it available on all network interfaces:

| Access method | URL | When to use |
|--------------|-----|-------------|
| **Local** | `http://localhost:3000/` | Same machine |
| **LAN** | `http://<machine-ip>:3000/` | Devices on same network |
| **Tailscale** | `http://<tailscale-ip>:3000/` | Remote access via Tailnet |

To find available IPs, check the dev server output or run `hostname -I`.

**For Tailscale users:** Use the Tailscale IP (usually `100.x.x.x`) to access from any device on your Tailnet. Run `tailscale ip` to find it.

#### 🔒 Security Notice

The dev server is a **development tool** with no built-in authentication or encryption. When exposing it on a network:

- **LAN access** exposes the dashboard to anyone on your local network
- **Tailscale** is the recommended remote access method (encrypted, authenticated by default)
- **Do not expose the dev server to the public internet** (no port forwarding, no 0.0.0.0 on public-facing machines without a reverse proxy + auth)
- The dashboard is **read-only** (no write operations), but task data may contain sensitive project information
- For production/team use, deploy to Cloudflare Pages (or similar) with proper auth instead of running the dev server

This is a development inspection tool, not a production server. Use it like you'd use Prisma Studio: locally, temporarily, on trusted networks. We provide this as-is for convenience; securing your network and access is your responsibility.

### Syncing Tasks to the Dashboard

After adding/updating tasks in TICK.md, sync to Convex so the dashboard reflects current state:

```bash
CONVEX_SITE_URL=https://<your-convex-deployment>.convex.site \
TICK_SYNC_KEY=<your-sync-key> \
bash "$SKILL_DIR/scripts/tick-sync.sh"
```

### Dashboard Features
- Project list with task counts
- Kanban board with status columns (Backlog → Todo → In Progress → Review → Done)
- Task detail slide-out with full history timeline
- Priority and tag filters
- Regen/Dark/Light theme toggle
- Auto-refresh every 30s

## Resources

- **Source (local)**: `~/clawd/projects/tick-md`
- **GitHub (upstream)**: https://github.com/Purple-Horizons/tick-md
- **CLI npm**: https://npmjs.com/package/tick-md
- **MCP Server npm**: https://npmjs.com/package/tick-mcp-server

---

## Tag Conventions

For multi-agent setups, use structured tag conventions to enable domain ownership and project tracking:

- **Project tags:** `project:<name>` — group tickets under efforts
- **Category tags:** `category:<type>` — classify by domain (tech, product, marketing, sales, founder, community, ops)

See [`docs/tag-conventions.md`](docs/tag-conventions.md) for full details, usage examples, and migration guide.

---

## Multi-Avatar Coordination (OpenClaw)

This section covers patterns for multi-avatar deployments where one OpenClaw instance runs multiple agents (e.g., CEO + CTO) sharing task state via TICK.md.

### Agent Identity

Each avatar uses a consistent `@agent-name` for all tick operations. This is set per-avatar in their workspace:

- Register on first use: `tick agent register @your-name --type bot --roles "your,roles"`
- Use the same `@name` in every command: `tick claim TASK-XXX @your-name`
- Never use another avatar's name

If your workspace has `TICK_AGENT_ID` set in environment or defined in AGENTS.md, use that as your identity.

### TICK.md Location

Each project has its own TICK.md in its root directory. Before running tick commands, `cd` into the correct project:

```bash
cd ~/path/to/project && tick status
```

If TICK.md doesn't exist yet, initialize: `tick init`

### Handoff Protocol

When you complete a task that unblocks work for another avatar:

1. Complete your task with a descriptive comment:
   ```bash
   tick done TASK-001 @cto
   tick comment TASK-001 @cto --note "Auth system built with JWT. Endpoint: /api/auth. CTO handoff: ready for product review."
   ```

2. The completing agent's comment should include:
   - What was done (brief summary)
   - Any decisions made and why
   - What the next avatar needs to know to pick up dependent work

3. Dependent tasks auto-unblock when blockers complete. The next avatar checks:
   ```bash
   tick list --status todo --assigned-to @their-name
   ```

### Orchestrator Pattern (CEO → Specialist)

The main/CEO avatar delegates work by:

1. Creating tasks with assignments:
   ```bash
   tick add "Design database schema" --priority high --assigned-to @cto --tags engineering
   ```

2. Spawning the specialist via OpenClaw:
   ```
   sessions_spawn(agentId: "cto", task: "Check TICK.md for assigned tasks. Claim, complete, and comment on each.")
   ```

3. The specialist avatar:
   - Runs `tick list --assigned-to @cto` to find work
   - Claims each task before starting
   - Comments with progress on longer tasks
   - Marks done when complete
   - Its completion summary announces back to the orchestrator's session

4. The orchestrator checks results:
   ```bash
   tick status
   ```

### Conflict Prevention

- OpenClaw serializes agent sessions (`maxConcurrent` controls parallelism)
- tick-md uses file locking (`.tick/lock`) to prevent simultaneous writes
- If a lock conflict occurs, retry after a brief pause
- Use `tick validate` to check for structural issues after any unexpected state

### What NOT to Do

- Don't claim tasks assigned to other avatars without explicit delegation
- Don't modify another avatar's comments or history
- Don't run `tick init` in a project that already has TICK.md
- Don't skip the comment when completing — future context depends on it

## License

MIT
