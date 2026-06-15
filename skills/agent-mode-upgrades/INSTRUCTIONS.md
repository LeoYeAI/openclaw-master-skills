# Enhanced Agentic Loop - Integration Instructions

This document provides instructions for integrating the Enhanced Agentic Loop into OpenClaw.

## For Users

### Installation

1. **Install the skill**:
   ```bash
   openclaw skill install agentic-loop-upgrade
   ```
   Or manually clone to `~/.openclaw/skills/agentic-loop-upgrade`

2. **Restart OpenClaw** to load the skill:
   ```bash
   openclaw gateway restart
   ```

3. **Enable Enhanced Loop**:
   - Open OpenClaw Dashboard (http://localhost:18789)
   - Navigate to **Agent** → **Mode** in the sidebar
   - Click the **Enhanced Loop** card
   - Click **Save Configuration**

### Using the Mode Dashboard

The Mode page provides a visual interface for configuring the enhanced loop:

**Sections:**

1. **Active Mode** - Toggle between Core Loop and Enhanced Loop
2. **Orchestrator Model** - Select any model from the OpenClaw model catalog for planning/reflection calls (smaller models reduce cost)
3. **Planning & Reflection** - Configure goal decomposition and progress tracking
4. **Execution** - Parallel tools and confidence gates
5. **Context Management** - Proactive summarization settings
6. **Error Recovery** - Semantic diagnosis and recovery attempts
7. **State Machine** - Observable state tracking and metrics

### Plan Visualization

When the enhanced loop is active, you'll see plan progress in agent responses:

```
:::plan
{
  "goal": "Build a website for a landscaping company",
  "completed": 3,
  "total": 5,
  "steps": [
    {"id": "step_1", "title": "Initialize project", "status": "done"},
    {"id": "step_2", "title": "Create layout", "status": "done"},
    {"id": "step_3", "title": "Build pages", "status": "done"},
    {"id": "step_4", "title": "Add images", "status": "active"},
    {"id": "step_5", "title": "Launch server", "status": "pending"}
  ]
}
:::
```

---

## For Agents (Koda/AI Assistants)

When the Enhanced Agentic Loop is enabled, you have access to advanced capabilities.

### Plan State

Plans persist across conversation turns. When you receive a complex task:

1. **Plan Detection**: The orchestrator detects planning intent and generates a plan
2. **Step Tracking**: As you complete tool calls, steps are automatically tracked
3. **Progress Display**: Show plan progress using the `:::plan` format block

### Showing Plan Progress

Include this at the START of responses when working on multi-step tasks:

```markdown
:::plan
{
  "goal": "Description of the overall goal",
  "completed": 2,
  "total": 5,
  "steps": [
    {"id": "step_1", "title": "First step", "status": "done"},
    {"id": "step_2", "title": "Second step", "status": "done"},
    {"id": "step_3", "title": "Third step", "status": "active"},
    {"id": "step_4", "title": "Fourth step", "status": "pending"},
    {"id": "step_5", "title": "Fifth step", "status": "pending"}
  ]
}
:::
```

Status values: `done`, `active`, `pending`, `failed`

### Parallel Execution

When you identify independent tools, call them in the same function_calls block. The orchestrator will execute them concurrently:

- Reading multiple files simultaneously
- Searching while fetching data
- Independent API calls

### Confidence Gates

For risky operations, the system may pause and ask for approval. Risk levels:

- **low**: Read operations (auto-approved)
- **medium**: Write/edit, safe exec
- **high**: Messages, browser actions, git push
- **critical**: Deletions, database operations

### Error Recovery

When a tool fails, don't just retry blindly. The semantic recovery system will:

1. Diagnose the error type (permission, network, not_found, etc.)
2. Suggest alternative approaches
3. Retry with modifications

### Checkpointing

Long-running tasks are automatically checkpointed. If a session is interrupted, you can resume from the last checkpoint.

---

## Configuration Reference

### Enhanced Loop Config File

Location: `~/.openclaw/agents/main/agent/enhanced-loop-config.json`

```json
{
  "enabled": true,
  "orchestratorProvider": "anthropic",
  "orchestratorModel": "<selected from OpenClaw model catalog>",
  "planning": {
    "enabled": true,
    "reflectionAfterTools": true,
    "maxPlanSteps": 10
  },
  "execution": {
    "parallelTools": true,
    "maxConcurrentTools": 5,
    "confidenceGates": true,
    "confidenceThreshold": 0.7
  },
  "context": {
    "proactiveManagement": true,
    "summarizeAfterIterations": 5,
    "contextThreshold": 0.7
  },
  "errorRecovery": {
    "enabled": true,
    "maxAttempts": 3,
    "learnFromErrors": true
  },
  "stateMachine": {
    "enabled": true,
    "logging": true,
    "metrics": false
  },
  "memory": {
    "autoInject": true,
    "maxFacts": 8,
    "maxEpisodes": 3,
    "episodeConfidenceThreshold": 0.9,
    "includeRelations": true
  }
}
```

### Disabling

To disable the enhanced loop:

1. **Via Dashboard**: Mode → Click Core Loop → Save
2. **Via File**: Delete `~/.openclaw/agents/main/agent/enhanced-loop-config.json`
3. **Via Config**: Set `"enabled": false` in the config file

---

## Troubleshooting

### Plan not showing?
- Ensure Enhanced Loop is enabled in Mode dashboard
- Check that the task is complex enough to trigger planning

### Too many tokens?
- Select a smaller/cheaper orchestrator model via the Mode dashboard (the dropdown lists all models from the OpenClaw catalog)
- Reduce maxPlanSteps
- Disable reflectionAfterTools for simpler tasks

### Want to revert?
- One click: Mode → Core Loop → Save
- All state is preserved; you can switch back anytime

---

## Version

v2.1.0 - Enhanced agentic loop with memory auto-injection and channel-aware plan rendering
