# Team Projects — Walkthrough

A practical example: using multi-agent teams to build a marketing website.

## Step 1: Configure Agents

Add agents to `openclaw.json` (see `example-config.json`). Each agent needs:
- A unique `id`
- A `name` (for display)
- Tool access appropriate to their role
- Optional `workspace` for file isolation

Enable inter-agent messaging:
```json
{
  "tools": {
    "agentToAgent": { "enabled": true, "allow": ["*"] },
    "sessions": { "visibility": "all" }
  }
}
```

## Step 2: Create a Project

Tell the coordinator agent (Koda):

> "Create a team project to build a marketing website for Acme Corp. We need research, design, copy, and development. Use @researcher for market research, @writer for copy, and @coder for development."

The coordinator will:
1. Create the project with phases
2. Break down into tasks
3. Assign to agents

## Step 3: The Coordinator Dispatches

Behind the scenes, the coordinator uses:

```bash
# Create project
node scripts/project-store.js create-project \
  --name "Acme Corp Website" \
  --coordinator main \
  --agents "researcher,writer,coder"

# Add phases
node scripts/project-store.js add-phase --project proj_abc --name "Research"
node scripts/project-store.js add-phase --project proj_abc --name "Content"
node scripts/project-store.js add-phase --project proj_abc --name "Development"

# Add tasks
node scripts/project-store.js add-task \
  --project proj_abc --phase phase_111 \
  --title "Competitor analysis" \
  --assignee researcher --priority high

node scripts/project-store.js add-task \
  --project proj_abc --phase phase_222 \
  --title "Write homepage copy" \
  --assignee writer --priority high \
  --dependsOn task_aaa

node scripts/project-store.js add-task \
  --project proj_abc --phase phase_333 \
  --title "Build React website" \
  --assignee coder --priority high \
  --dependsOn task_bbb
```

Then dispatches using OpenClaw's native tools:
```
sessions_spawn(agentId: "researcher", task: "Research competitors for Acme Corp...")
```

## Step 4: Agents Work & Report Back

Each agent:
1. Receives their task via `sessions_spawn`
2. Does the work using their allowed tools
3. Reports completion with `TASK_COMPLETE: #task_abc`

The coordinator receives completion events (push-based, no polling) and:
1. Updates task status to "done"
2. Checks if the phase is complete
3. Dispatches next batch of tasks whose dependencies are met

## Step 5: Inter-Agent Communication

If the writer needs info from the researcher:
```
@researcher What did you find about Acme's main competitor pricing?
```

This gets routed via `sessions_send` to the researcher's session.

## Step 6: Project Completion

When all phases complete:
```bash
node scripts/orchestrator.js advance proj_abc
# → { advancedPhases: ["phase_333"], projectComplete: true }
```

The coordinator announces completion to the user.

## Key Architecture Points

1. **No polling** — Sub-agent completions use push-based announcement
2. **Dependency gates** — Tasks with `dependsOn` only dispatch after deps are done
3. **Tool isolation** — Each agent only has access to tools appropriate for their role
4. **Workspace isolation** — Each agent works in their own directory
5. **Persistent state** — Project board persists across sessions in JSON
6. **Scalable** — Works with 2 agents or 20
