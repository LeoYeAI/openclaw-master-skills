---
name: team-projects
description: "Multi-agent project management with task boards, @-mention routing, WBS, and orchestrated team collaboration. Includes a Control UI plugin tab with project dashboard and a right-edge Team Chat drawer for live activity. Enables a coordinator agent to plan projects, break down work into phases and tasks, assign to specialist agents, dispatch via sessions_spawn, and track progress to completion. Use when: (1) managing work across multiple OpenClaw agents, (2) creating project plans with work breakdown structures, (3) assigning and tracking tasks across agents, (4) coordinating multi-agent workflows with dependencies, (5) running team-based projects with progress tracking."
metadata:
  {
    "openclaw": {
      "emoji": "📋",
      "requires": {
        "config": {
          "tools.agentToAgent.enabled": true,
          "agents.list": "at least 2 agents configured"
        }
      }
    }
  }
---

# Team Projects 📋

Multi-agent project management for OpenClaw. Run agent teams that plan, assign, execute, and track work together. Includes a **Control UI plugin tab** for visual project tracking and a **right-edge Team Chat drawer** for live agent activity.

## Overview

This skill enables a **coordinator agent** to manage projects across multiple specialist agents:

```
User → Coordinator (Koda) → dispatches tasks via sessions_spawn
                            ├── @researcher → web research, data analysis
                            ├── @coder → writing code, building features
                            ├── @writer → copy, documentation, content
                            └── ... any configured agent
```

Each agent works independently with their own tools and workspace. The coordinator tracks progress, manages dependencies, and advances the project.

## UI Components

### 1. Projects Tab (sidebar)
A full project dashboard registered as a plugin tab in the Control sidebar under the "Control" group. Shows project cards, task boards with phase sections, team overview, and progress stats.

### 2. Team Chat Drawer (right edge)
A slide-out panel accessible from a vertical "Team" tab fixed to the right edge of the screen. Shows:
- Live agent activity feed (sub-agent sessions, messages)
- Project progress bar
- Task overview (collapsible)
- Quick message input to send commands

## Installation

### Step 1: Config Prerequisites

Add to `openclaw.json`:

```json
{
  "tools": {
    "agentToAgent": {
      "enabled": true,
      "allow": ["*"]
    }
  }
}
```

Add `subagents.allowAgents` to the **coordinator agent's list entry** (NOT on `agents.defaults`):

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "name": "Koda",
        "subagents": {
          "allowAgents": ["*"]
        }
      }
    ]
  }
}
```

> ⚠️ **Critical:** `allowAgents` must be on the agent's own entry in `agents.list`. Setting it on `agents.defaults.subagents` does NOT work. The code reads `resolveAgentConfig(cfg, requesterAgentId)?.subagents?.allowAgents` which resolves the per-agent config, not defaults.

### Step 2: Gateway Plugin Installation (for Projects tab)

The Projects tab requires installing a gateway plugin. This involves 4 registration points in the OpenClaw source:

#### 2a. Plugin SDK entry

Create `src/plugin-sdk/team-projects.ts`:

```typescript
export { emptyPluginConfigSchema } from "../plugins/config-schema.js";
export type {
  OpenClawPluginApi,
  PluginViewRegistration,
} from "../plugins/types.js";
```

#### 2b. Plugin extension

Create `extensions/team-projects/openclaw.plugin.json`:

```json
{
  "id": "team-projects",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

Create `extensions/team-projects/index.ts` — see `gateway-plugin/index.ts`.

#### 2c. Register in build pipeline (4 files)

**`tsdown.config.ts`** — Add `"team-projects"` to the `pluginSdkEntrypoints` array.

**`src/plugins/loader.ts`** — Add to the `pluginSdkScopedAliasEntries` array:
```typescript
{
  subpath: "team-projects",
  srcFile: "team-projects.ts",
  distFile: "team-projects.js",
},
```

**`scripts/write-plugin-sdk-entry-dts.ts`** — Add `"team-projects"` to the entrypoints array.

**`package.json`** — Add to the exports map:
```json
"./plugin-sdk/team-projects": {
  "types": "./dist/plugin-sdk/team-projects.d.ts",
  "default": "./dist/plugin-sdk/team-projects.js"
},
```

#### 2d. Enable in config

```json
{
  "plugins": {
    "allow": ["telegram", "discord", "team-projects"],
    "entries": {
      "team-projects": {
        "enabled": true
      }
    }
  }
}
```

### Step 3: UI View Installation

#### 3a. Team Projects view

Copy `gateway-plugin/team-projects-view.ts` to `ui/src/ui/views/team-projects.ts`.

#### 3b. Team Chat Drawer

Copy `gateway-plugin/team-chat-drawer.ts` to `ui/src/ui/views/team-chat-drawer.ts`.

> ⚠️ **Critical: No Shadow DOM** — The OpenClaw app uses `createRenderRoot() { return this; }`, so Lit `css` tagged templates are NOT applied. All styles must be embedded as inline `<style>` tags in the rendered HTML. The team-chat-drawer uses an inline `<style>` block inside `renderTeamChatEdgeTab()` so styles are present even when the drawer is closed.

#### 3c. Wire into app-render.ts

See `gateway-plugin/app-render-patch.ts` for the integration points:

1. Import `renderTeamChatDrawer` and `renderTeamChatEdgeTab` from `./views/team-chat-drawer.ts`
2. Before `</main>`, add `${renderPluginTabContent(state)}`
3. After `</main>`, add the edge tab and drawer renders
4. Add the `renderPluginTabContent()` function

#### 3d. Wire into app-gateway.ts

See `gateway-plugin/app-gateway-patch.ts` for the integration points:

1. Import `uiPluginRegistry` from `./plugins/registry.ts`
2. Import `renderTeamProjects` from `./views/team-projects.ts`
3. In `onHello`, after `applySnapshot()`, call `registerTeamProjectsPlugin()`
4. Add the `registerTeamProjectsPlugin()` function

#### 3e. Add view state fields

In `ui/src/ui/app-view-state.ts`, add to `AppViewState`:

```typescript
teamChatOpen: boolean;
teamChatProject: unknown;
teamChatSessions: unknown[];
teamChatActivity: unknown[];
teamChatLoading: boolean;
teamChatInput: string;
teamChatTasksCollapsed: boolean;
```

In `ui/src/ui/app-settings.ts`, add `teamChatOpen?: boolean` to `SettingsHost` type, and add defensive cleanup in `applyTabSelection()`:

```typescript
} else if (host.teamChatOpen) {
  host.teamChatOpen = false;
}
```

### Step 4: Build & Restart

```bash
cd ~/openclaw
pnpm build        # Backend (gateway + plugin SDK)
pnpm ui:build     # Control UI
openclaw gateway restart
```

Hard-refresh the browser (Ctrl+Shift+R) to load the new UI assets.

## Usage

### Creating a Project

Tell the coordinator agent what you want to build. It will:
1. Create the project with appropriate phases
2. Break down work into tasks
3. Assign tasks to agents based on capabilities
4. Dispatch ready tasks

**Example prompt:**
> "Create a team project to redesign our company website. @researcher should analyze competitors, @writer should draft copy, and @coder should build it in React. Priority: launch in 2 weeks."

### The Coordinator's Workflow

The coordinator uses CLI tools to manage the project board:

```bash
# Create a project
node {{SKILL_DIR}}/scripts/project-store.js create-project \
  --name "Website Redesign" \
  --description "Full redesign of company website" \
  --coordinator main \
  --agents "researcher,writer,coder"

# Add phases (ordered)
node {{SKILL_DIR}}/scripts/project-store.js add-phase \
  --project PROJECT_ID --name "Research" --description "Competitive analysis"

# Add tasks with assignments and dependencies
node {{SKILL_DIR}}/scripts/project-store.js add-task \
  --project PROJECT_ID --phase PHASE_ID \
  --title "Analyze top 5 competitors" \
  --description "Research competitor websites..." \
  --assignee researcher --priority high

node {{SKILL_DIR}}/scripts/project-store.js add-task \
  --project PROJECT_ID --phase PHASE_ID \
  --title "Write homepage hero copy" \
  --assignee writer --priority high \
  --dependsOn "task_abc123"
```

### Dispatching Tasks

The orchestrator identifies ready tasks (dependencies met, not yet dispatched):

```bash
# See what's ready to dispatch
node {{SKILL_DIR}}/scripts/orchestrator.js plan PROJECT_ID
```

Then dispatch via OpenClaw's native `sessions_spawn`:

```
sessions_spawn(
  agentId: "researcher",
  task: "Research the top 5 competitors in the AI SaaS space...",
  label: "task_abc123"
)
```

### Agent Communication

Agents can communicate using @-mentions:

- **@agentId** — Direct message to an agent (routed via `sessions_send`)
- **@all** / **@team** — Broadcast to all project agents
- **#task_id** — Reference a task
- **TASK_COMPLETE: #task_id** — Signal task completion
- **TASK_BLOCKED: #task_id** — Signal a blocker

### Tracking Progress

```bash
# View project stats
node {{SKILL_DIR}}/scripts/project-store.js stats --id PROJECT_ID

# View work breakdown structure
node {{SKILL_DIR}}/scripts/project-store.js wbs --id PROJECT_ID

# Check and advance completed phases
node {{SKILL_DIR}}/scripts/orchestrator.js advance PROJECT_ID
```

### Updating Tasks

```bash
# Mark task in progress
node {{SKILL_DIR}}/scripts/project-store.js update-task \
  --project PROJECT_ID --id TASK_ID --status in_progress

# Mark task done
node {{SKILL_DIR}}/scripts/project-store.js update-task \
  --project PROJECT_ID --id TASK_ID --status done

# Add a comment
node {{SKILL_DIR}}/scripts/project-store.js add-comment \
  --project PROJECT_ID --task TASK_ID \
  --author main --text "Looks good, merging now"
```

## Data Model

### Project
```
project
├── id, name, slug, description
├── status: planning | active | paused | completed | archived
├── coordinator: agentId
├── agents: [agentId, ...]
└── phases[]
    ├── id, name, description, order
    ├── status: pending | active | completed
    └── tasks[]
        ├── id, title, description
        ├── assignee: agentId
        ├── priority: critical | high | medium | low
        ├── status: todo | in_progress | blocked | review | done
        ├── dependsOn: [taskId, ...]
        ├── sessionKey: (set when dispatched)
        ├── artifacts: [paths/URLs]
        └── comments[]
```

### Storage
- **Projects:** `~/.openclaw/workspace/team-projects/projects.json`
- **Chat logs:** `~/.openclaw/workspace/team-projects/chat_PROJECT_ID.jsonl`
- **Orchestrator state:** `~/.openclaw/workspace/team-projects/orchestrator-state.json`

## Architecture

### How It Works

```
┌─────────────┐     sessions_spawn      ┌──────────────┐
│ Coordinator  │ ──────────────────────→ │  Worker Agent │
│   (Koda)     │                         │  (researcher) │
│              │ ←── push completion ──── │              │
│  project-    │                         └──────────────┘
│  store.js    │     sessions_spawn      ┌──────────────┐
│              │ ──────────────────────→ │  Worker Agent │
│  orchestr-   │                         │   (coder)     │
│  ator.js     │ ←── push completion ──── │              │
│              │                         └──────────────┘
│  UI plugin   │     sessions_send       ┌──────────────┐
│  tab         │ ←────────────────────── │  Worker Agent │
└─────────────┘     (inter-agent msg)    │   (writer)    │
                                         └──────────────┘
```

### Key Design Decisions

1. **Push-based completion** — No polling. OpenClaw's `subagent-announce` system delivers completion events automatically.
2. **Dependency gates** — The orchestrator only dispatches tasks whose `dependsOn` are all `done`.
3. **Tool isolation** — Each agent gets only the tools they need. A researcher can't exec arbitrary code; a coder can't send messages to external channels.
4. **File-based persistence** — Simple JSON storage. No database required. Works on any OpenClaw instance.
5. **CLI-first** — All operations available via CLI. The UI is optional.
6. **Agent-native** — Uses OpenClaw's existing `sessions_spawn`, `sessions_send`, and `agents_list` tools. No custom transport.
7. **Plugin architecture** — Projects tab registered via OpenClaw's `uiPluginRegistry` (client-side). Team Chat drawer uses inline `<style>` tags for CSS (no Shadow DOM).
8. **Client-side plugin registration** — Since the gateway plugin view registration pipeline isn't fully wired end-to-end, the Projects tab is registered client-side in `app-gateway.ts` during `onHello`. This is reliable and avoids depending on gateway-side plugin infrastructure.

### Plugin Registration Points (4 required for gateway plugin)

When adding a new gateway plugin to OpenClaw, you must register it in 4 places:

| File | What to add |
|------|-------------|
| `src/plugin-sdk/<id>.ts` | SDK type entry (exports `OpenClawPluginApi` etc.) |
| `src/plugins/loader.ts` → `pluginSdkScopedAliasEntries` | Jiti alias so runtime can resolve `openclaw/plugin-sdk/<id>` |
| `tsdown.config.ts` → `pluginSdkEntrypoints` | Build entry so `dist/plugin-sdk/<id>.js` gets generated |
| `scripts/write-plugin-sdk-entry-dts.ts` | DTS entry generator |
| `package.json` → exports → `./plugin-sdk/<id>` | Package subpath export |

Missing any one of these causes `Cannot find module` errors at runtime.

### CSS Gotcha: No Shadow DOM

OpenClaw's `OpenClawApp` uses `createRenderRoot() { return this; }` — it renders directly to the DOM without Shadow DOM. This means:

- Lit `css` tagged templates (used with `static styles`) are **never applied**
- All styles must be embedded as `<style>` tags in the HTML returned by render functions
- The `teamChatDrawerStyles` export was originally dead code until fixed to use inline styles

## Coordinator Prompt Template

The coordinator agent should include `templates/coordinator-prompt.md` in its system prompt (or SOUL.md). This gives it the commands and workflow for managing projects.

Worker agents should include `templates/worker-prompt.md` for task completion protocols.

## Known Issues & Gotchas

### `allowAgents` must be per-agent
Setting `agents.defaults.subagents.allowAgents: ["*"]` does NOT work. The code at `agents-list-tool.ts:49` reads:
```typescript
const allowAgents = resolveAgentConfig(cfg, requesterAgentId)?.subagents?.allowAgents ?? [];
```
This resolves the per-agent config entry, not defaults. You must add it to the agent's entry in `agents.list`.

### `dependsOn` normalization
The CLI passes `--dependsOn task_abc` as a string, not an array. The project store and orchestrator both normalize with `Array.isArray()` checks. If you create tasks programmatically, always pass an array.

### UI requires hard refresh
After rebuilding the UI (`pnpm ui:build`) and restarting the gateway, browsers may cache the old JS bundle. Always hard-refresh (Ctrl+Shift+R) after UI changes.

### Icon availability
The icon used for the Projects tab must exist in `ui/src/ui/icons.ts`. Available icons include: `fileText`, `folder`, `barChart`, `zap`, `brain`, `settings`, `plug`, etc. Custom icon names like `clipboard-list` won't work — use `fileText` instead.

## Limitations

- **No real-time UI sync** — The UI reads from JSON files; updates appear on refresh, not live push.
- **No native gateway RPC** — The project board is managed via CLI tools, not gateway RPC methods (yet).
- **Single coordinator** — One agent coordinates per project (though you could have different coordinators for different projects).
- **No cost tracking** — Task cost/token tracking depends on OpenClaw's session usage system.
- **Client-side plugin registration** — The gateway-side plugin view registration pipeline (`registerView` → hello snapshot → `loadFromGateway`) is scaffolded but not fully wired. Plugin tabs are registered client-side instead.

## Future Enhancements

- [ ] Gateway RPC plugin for live UI updates via WebSocket
- [ ] Kanban drag-and-drop in the sidebar
- [ ] Gantt chart / timeline view
- [ ] Automated task creation from GitHub issues
- [ ] Cost/token budget per task
- [ ] Agent capability auto-detection from tools config
- [ ] Cron-based project health checks
- [ ] Gateway-side plugin view registration (when pipeline is complete)

## Files

```
team-projects/
├── SKILL.md                              # This file
├── scripts/
│   ├── project-store.js                  # CRUD for projects, phases, tasks, comments
│   ├── orchestrator.js                   # Dispatch planning, dependency gates, phase advancement
│   ├── task-router.js                    # @-mention parsing and dispatch planning
│   └── gateway-handlers.js              # HTTP API adapter (optional)
├── ui/
│   ├── project-sidebar.js               # Sidebar panel component (standalone)
│   └── team-chat.js                     # Multi-agent chat component (standalone)
├── gateway-plugin/
│   ├── index.ts                         # Gateway plugin source (extensions/team-projects/)
│   ├── openclaw.plugin.json             # Plugin manifest
│   ├── plugin-sdk-entry.ts              # SDK type entry (src/plugin-sdk/team-projects.ts)
│   ├── team-projects-view.ts            # UI view renderer (ui/src/ui/views/team-projects.ts)
│   ├── team-chat-drawer.ts              # Team Chat drawer + edge tab (ui/src/ui/views/team-chat-drawer.ts)
│   ├── app-render-patch.ts              # Patch for app-render.ts (plugin tab catch-all + drawer)
│   ├── app-gateway-patch.ts             # Patch for app-gateway.ts (renderer registration)
│   └── BUILD_REGISTRATION.md            # Build pipeline registration checklist
├── templates/
│   ├── coordinator-prompt.md            # System prompt for coordinator agent
│   └── worker-prompt.md                 # System prompt fragment for worker agents
└── references/
    ├── example-config.json              # Example openclaw.json for team setup
    └── walkthrough.md                   # Step-by-step usage guide
```
