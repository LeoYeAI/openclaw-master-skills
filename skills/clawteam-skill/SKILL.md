---
name: clawteam
description: "Multi-agent swarm coordination via the ClawTeam CLI. Use when the user wants to create agent teams, spawn multiple agents to work in parallel, coordinate tasks with dependencies, broadcast messages between agents, monitor progress via kanban board, or launch pre-built team templates (hedge-fund, code-review, research-paper). ClawTeam uses git worktree isolation + tmux + filesystem-based messaging. Trigger phrases: team, swarm, multi-agent, clawteam, spawn agents, parallel agents, agent team."
homepage: https://github.com/win4r/ClawTeam-OpenClaw
metadata:
  openclaw:
    requires:
      bins: ["clawteam"]
---

# ClawTeam — Multi-Agent Swarm Coordination

## Overview

ClawTeam is a CLI tool (`clawteam`) for orchestrating multiple AI agents as self-organizing swarms. It uses git worktree isolation, tmux windows, and filesystem-based messaging. OpenClaw is the default agent backend.
Source: https://github.com/win4r/ClawTeam-OpenClaw

## Optimization Notes

This skill is based on the upstream ClawTeam project and includes additional safety/approval optimizations for real-world operations:

- Channel-aware approval UX:
  - Feishu uses interactive approval cards with same-row `Approve/Reject` buttons.
  - Telegram uses inline keyboard approval buttons.
  - Other channels fall back to explicit text approval (`approve` / `reject`).
- Safer execution defaults:
  - No permission-bypass guidance.
  - No infinite unattended monitor loops.
  - Destructive operations require explicit approval checkpoints.

These changes are intentional enhancements, not a verbatim copy.

**CLI binary**: `clawteam` (must be preinstalled and available in `PATH`)

## Install & Verification

This skill is instruction-only. It does not install `clawteam` automatically.

Install from a trusted source and pin a version/tag when possible.

```bash
# Example only: verify upstream release/tag before install
pipx install "git+https://github.com/win4r/ClawTeam-OpenClaw.git@<trusted-tag>"

# Verify binary and version
which clawteam
clawteam --version
```

Recommended preflight before first real run:

```bash
# Use a disposable repo/worktree first
clawteam config health
clawteam team spawn-team dry-run -d "safety check" -n leader
clawteam team cleanup dry-run --force
```

## Quick Start

### One-Command Template Launch (Recommended)

```bash
# Launch a pre-built team from a template
clawteam launch hedge-fund --team fund1
clawteam launch code-review --team review1
clawteam launch research-paper --team paper1
```

### Manual Team Setup

```bash
# 1. Create team with leader
clawteam team spawn-team my-team -d "Build a web app" -n leader

# 2. Create tasks with dependencies
clawteam task create my-team "Design API schema" -o architect
# Returns task ID, e.g., abc123

clawteam task create my-team "Implement auth" -o backend --blocked-by abc123
clawteam task create my-team "Build frontend" -o frontend --blocked-by abc123
clawteam task create my-team "Write tests" -o tester

# 3. Spawn agents (each gets its own tmux window + git worktree)
clawteam spawn -t my-team -n architect --task "Design the API schema for a web app"
clawteam spawn -t my-team -n backend --task "Implement OAuth2 authentication"
clawteam spawn -t my-team -n frontend --task "Build React dashboard"

# 4. Monitor
clawteam board show my-team        # Kanban view
clawteam board attach my-team      # Tmux tiled view (all agents side-by-side)
clawteam board serve --port 8080   # Web dashboard
```

## Command Reference

### Team Management

| Command | Description |
|---------|-------------|
| `clawteam team spawn-team <name> -d "<desc>" -n <leader>` | Create team |
| `clawteam team discover` | List all teams |
| `clawteam team status <team>` | Show team members and info |
| `clawteam team cleanup <team> --force` | Delete team and all data |

### Task Management

| Command | Description |
|---------|-------------|
| `clawteam task create <team> "<subject>" -o <owner> [-d "<desc>"] [--blocked-by <id>]` | Create task |
| `clawteam task list <team> [--owner <name>]` | List tasks (filterable) |
| `clawteam task update <team> <id> --status <status>` | Update status |
| `clawteam task get <team> <id>` | Get single task |
| `clawteam task stats <team>` | Timing statistics |
| `clawteam task wait <team>` | Block until all tasks complete |

**Task statuses**: `pending`, `in_progress`, `completed`, `blocked`

**Dependency auto-resolution**: When a blocking task completes, dependent tasks automatically change from `blocked` to `pending`.

**Task locking**: When a task moves to `in_progress`, it is locked by the calling agent. Other agents cannot claim it unless they use `--force`. Stale locks from dead agents are automatically released.

### Agent Spawning

Use the default command (`openclaw`) unless the user explicitly requests another backend. Keep normal permission and trust prompts enabled.

```bash
# Default (RECOMMENDED): spawns openclaw tui in tmux with prompt
clawteam spawn -t <team> -n <name> --task "<task description>"

# Explicit backend (still uses openclaw by default)
clawteam spawn tmux -t <team> -n <name> --task "<task>"
clawteam spawn subprocess -t <team> -n <name> --task "<task>"

# With git worktree isolation
clawteam spawn -t <team> -n <name> --task "<task>" --workspace --repo /path/to/repo
```

High-impact note: `spawn subprocess` and custom backend modes can execute arbitrary code through delegated commands. Use only in trusted repositories/environments.

Each spawned agent gets:
- Its own tmux window (visible via `board attach`)
- Its own git worktree branch (`clawteam/{team}/{agent}`)
- An auto-injected coordination prompt (how to use clawteam CLI)
- Environment variables: `CLAWTEAM_AGENT_NAME`, `CLAWTEAM_TEAM_NAME`, etc.

**Spawn safety features:**
- Commands are pre-validated before launch — you get a clear error if the agent CLI is not installed
- If a spawn fails, the registered team member and worktree are automatically rolled back
- Workspace trust and permission prompts must be reviewed and confirmed by the user or operator

### Messaging

| Command | Description |
|---------|-------------|
| `clawteam inbox send <team> <to> "<msg>" --from <sender>` | Point-to-point message |
| `clawteam inbox broadcast <team> "<msg>" --from <sender>` | Broadcast to all |
| `clawteam inbox peek <team> -a <agent>` | Peek without consuming |
| `clawteam inbox receive <team>` | Consume messages |
| `clawteam inbox log <team>` | View message history |

### Monitoring

| Command | Description |
|---------|-------------|
| `clawteam board show <team>` | Kanban board (rich terminal) |
| `clawteam board overview` | All teams overview |
| `clawteam board live <team>` | Live-refreshing board |
| `clawteam board attach <team>` | Tmux tiled view |
| `clawteam board serve --port 8080` | Web dashboard |

### Cost Tracking

| Command | Description |
|---------|-------------|
| `clawteam cost report <team> --input-tokens <N> --output-tokens <N> --cost-cents <N>` | Report usage |
| `clawteam cost show <team>` | Show summary |
| `clawteam cost budget <team> <dollars>` | Set budget |

### Templates

| Command | Description |
|---------|-------------|
| `clawteam template list` | List available templates |
| `clawteam template show <name>` | Show template details |
| `clawteam launch <template> [--team-name <name>] [--goal "<goal>"]` | Launch from template |

**Built-in templates**: `hedge-fund`, `code-review`, `research-paper`

### Configuration

```bash
clawteam config show                           # Show all settings
clawteam config set transport file             # Set transport backend
clawteam config health                         # System health check
```

Do not enable permission-skipping settings in shared or production environments. Keep permission prompts enabled for auditability.

## Credentials & Channel Integration

This skill itself does not directly read or manage Feishu/Telegram tokens. Channel credentials are managed by the OpenClaw channel plugins/runtime.

- Feishu interactive approvals require a configured Feishu channel account in OpenClaw.
- Telegram interactive approvals require a configured Telegram bot/channel account in OpenClaw.
- Never paste bot tokens, app secrets, or webhook secrets into team tasks, git worktrees, or chat messages.

### Other Commands

| Command | Description |
|---------|-------------|
| `clawteam lifecycle idle <team> --agent <name>` | Report agent idle |
| `clawteam session save <team> --session-id <id>` | Save session for resume |
| `clawteam plan submit <team> "<plan>" --from <agent>` | Submit plan for approval (team-scoped storage) |
| `clawteam workspace list <team>` | List git worktrees |
| `clawteam workspace merge <team> --agent <name>` | Merge agent branch |

## JSON Output

Add `--json` before any subcommand for machine-readable output:

```bash
clawteam --json task list my-team
clawteam --json team status my-team
```

## Typical Workflow

1. **User says**: "Create a team to build a web app"
2. **You do**: `clawteam team spawn-team webapp -d "Build web app" -n leader`
3. **Create tasks**: Use `clawteam task create` with `--blocked-by` for dependencies
4. **Spawn agents**: Use `clawteam spawn` for each worker
5. **Monitor**: Use bounded polling with timeout/attempt limits
6. **Communicate**: Use `clawteam inbox broadcast` for team-wide updates
7. **Deliver**: Share progress and ask for confirmation before destructive actions
8. **Cleanup**: After confirmation, run `clawteam cost show`, `clawteam task stats`, merge worktrees, then `clawteam team cleanup webapp --force`

## Leader Orchestration Pattern

When YOU are the leader agent, follow this pattern to safely manage a swarm with user oversight:

### Phase 1: Analyze & Plan
```
1. Understand the user's goal
2. Break it into independent subtasks
3. Identify dependencies between tasks (what must finish before what)
4. Decide how many worker agents are needed
```

### Phase 2: Setup
```bash
# Create team
clawteam team spawn-team <team> -d "<goal description>" -n leader

# Create tasks with dependency chains
clawteam task create <team> "Design API" -o architect
# Save the returned task ID (e.g., abc123)
clawteam task create <team> "Build backend" -o backend --blocked-by abc123
clawteam task create <team> "Build frontend" -o frontend --blocked-by abc123
clawteam task create <team> "Integration tests" -o tester --blocked-by <backend-id>,<frontend-id>
```

### Phase 3: Spawn Workers
```bash
# Each spawn launches an openclaw tui in its own tmux window
clawteam spawn -t <team> -n architect --task "Design REST API schema for <goal>"
clawteam spawn -t <team> -n backend --task "Implement backend based on API schema"
clawteam spawn -t <team> -n frontend --task "Build React frontend"
clawteam spawn -t <team> -n tester --task "Write and run integration tests"
```

### Phase 4: Monitor Loop

Use a bounded monitor loop (for example, max 40 iterations with 30s interval = 20 minutes), then stop and report status.
1. **Push mid-progress updates** — when ~50% of tasks complete, send the user a brief status update (e.g. "4/7 agents done, 3 still working").
2. **Deliver final results** when all tasks complete.
3. **Escalate to user** if timeout is reached, instead of running indefinitely.

```bash
# Poll task status every 30-60 seconds with an upper bound
max_rounds=40
for ((round=1; round<=max_rounds; round++)); do
  clawteam --json task list <team> | python3 -c "
import sys, json
tasks = json.load(sys.stdin)
done = sum(1 for t in tasks if t['status'] == 'completed')
total = len(tasks)
print(f'{done}/{total} complete')
if done == total: print('ALL DONE'); sys.exit(0)
"
  # Check for messages from workers
  clawteam inbox receive <team>
  # Send a mid-progress update when roughly half the tasks are done
  sleep 30
done

# Timeout branch: ask user whether to continue monitoring
echo "Monitor timeout reached; request user confirmation to continue."
```

### Phase 5: Converge & Report

Before merge/cleanup, ask for user confirmation. Include the final output, a summary, and cost/timing stats.

```bash
# After all tasks complete — do ALL of these steps:
clawteam board show <team>           # Final status
clawteam cost show <team>            # Total cost — include in report to user
clawteam task stats <team>           # Timing stats — include in report to user
# Ask user for confirmation before merge and cleanup
# Merge each worker's branch back to main (after confirmation)
for agent in <agent1> <agent2> ...; do
  clawteam workspace merge <team> --agent $agent
done
clawteam team cleanup <team> --force  # Clean up after confirmation
# Then: send the final deliverables to the user
```

### Decision Rules for the Leader
- **Independent tasks** → spawn workers in parallel
- **Sequential tasks** → use `--blocked-by` to chain them; ClawTeam auto-unblocks
- **Worker asks for help** → check inbox, provide guidance via `inbox send`
- **Worker stuck** → check task status; if `in_progress` too long, send a nudge via `inbox send`
- **Worker done** → verify result via inbox message, then move to next phase
- **All done** → confirm with user, then merge worktrees and cleanup
- **Always** → prefer bounded monitoring and explicit user checkpoints for long-running actions

## Safety Guardrails

- Never bypass security, trust, or permission prompts.
- Never run infinite unattended loops; use bounded retries/timeouts.
- Ask for user confirmation before destructive actions (force cleanup, branch merge, mass task updates).
- If a command requests elevated privileges or modifies sensitive paths, pause and ask first.
- Keep an audit trail by reporting what was executed and why.
- Treat these as high-impact operations and confirm intent before running: `spawn subprocess`, `workspace merge`, `team cleanup --force`, `board serve`.

## Remote Approval Cards

Render approval UI based on the current message source (channel-aware behavior):

- `feishu` source: always use Feishu interactive card (`schema: "2.0"`) with `approval_decision` button callback.
- `telegram` source: use inline keyboard buttons (`Approve` / `Reject`) with callback payload carrying `approval_id` and `decision`.
- Other sources (cli/web/unknown): use a text approval prompt and require explicit reply `approve` or `reject`.
- Required fields for all channels:
  - `approval_id` (unique, one-time)
  - `action` (what will be executed)
  - `risk_level` (low/medium/high)
  - `scope` (files/commands/resources affected)
  - `deadline` (approval timeout)

Feishu template (same-row buttons, recommended):

```json
{
  "schema": "2.0",
  "config": { "wide_screen_mode": true },
  "header": {
    "title": { "tag": "plain_text", "content": "Remote Approval" },
    "template": "orange"
  },
  "body": {
    "elements": [
      {
        "tag": "markdown",
        "content": "**approval_id**: `<id>`\n**action**: <action>\n**risk_level**: <level>\n**scope**: <scope>\n**deadline**: <time>"
      },
      { "tag": "hr" },
      {
        "tag": "column_set",
        "flex_mode": "none",
        "horizontal_align": "left",
        "columns": [
          {
            "tag": "column",
            "width": "auto",
            "elements": [
              {
                "tag": "button",
                "text": { "tag": "plain_text", "content": "Approve" },
                "type": "primary",
                "value": { "action": "approval_decision", "approval_id": "<id>", "decision": "approve" }
              }
            ]
          },
          {
            "tag": "column",
            "width": "auto",
            "elements": [
              {
                "tag": "button",
                "text": { "tag": "plain_text", "content": "Reject" },
                "type": "default",
                "value": { "action": "approval_decision", "approval_id": "<id>", "decision": "reject" }
              }
            ]
          }
        ]
      }
    ]
  }
}
```

Source detection hint:

- Prefer runtime channel metadata (for example, `channel=feishu` or `channel=telegram`).
- If unavailable, infer from session key patterns:
  - `agent:*:feishu:*` -> Feishu mode
  - `agent:*:telegram:*` -> Telegram mode

## Data Location

All state stored in `~/.clawteam/`:
- Teams: `~/.clawteam/teams/<team>/config.json`
- Tasks: `~/.clawteam/tasks/<team>/task-<id>.json` (with `fcntl` file locking for concurrent safety)
- Plans: `~/.clawteam/plans/<team>/<agent>-<plan_id>.md` (team-scoped, isolated per team)
- Messages: `~/.clawteam/teams/<team>/inboxes/<agent>/msg-*.json`
- Costs: `~/.clawteam/costs/<team>/`
