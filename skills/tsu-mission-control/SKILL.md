---
name: mission-control
description: Integrate with Mission Control dashboard to report task progress, publish documents to the Library, request approvals, and submit project requests. Use this skill whenever you start, complete, or fail a task, need human approval, want to publish research/reports/documentation, or need to submit a new project request. This skill provides the HTTP endpoints and event formats for communicating with the Mission Control backend.
metadata:
  {
    "openclaw":
      {
        "emoji": "🎛️",
        "requires": { "bins": ["node", "npm"] },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "mission-control-skill",
              "bins": [],
              "label": "Install Mission Control skill",
            },
          ],
        "env":
          {
            "MISSION_CONTROL_URL": "http://localhost:8000",
            "MISSION_CONTROL_HOOK_SECRET": "",
          },
      },
  }
---

# Mission Control Integration Skill

You are connected to a Mission Control dashboard that tracks your work, manages projects and tasks, handles approvals, and stores documents in a Library. This skill tells you how to communicate with it.

## Overview

Mission Control is a database-backed dashboard running at `$MISSION_CONTROL_URL` (default: `http://localhost:8000`). It provides:

- **Pipeline**: Tasks flow through stages: backlog → todo → doing → review → done
- **Inbox**: A unified queue where humans review requests, approve work, and handle workflow gates
- **Library**: A curated document store for research, reports, documentation, and reference material
- **Costs**: Token spend tracking per session
- **Activity**: A chronological feed of all events

Your job is to report your progress so the dashboard stays accurate.

---

## Reporting Task Progress

When you are assigned a task (you'll see a task ID like `t_abc123`), report your progress at each stage by sending HTTP POST requests to the hooks endpoint.

### Endpoint

```
POST $MISSION_CONTROL_URL/api/hooks/event
Content-Type: application/json
X-Hook-Secret: $MISSION_CONTROL_HOOK_SECRET
```

### When Starting a Task

```json
{
  "event": "task:started",
  "agentId": "YOUR_AGENT_ID",
  "taskId": "TASK_ID",
  "data": { "message": "Beginning work on [description]" }
}
```

### When Making Progress

```json
{
  "event": "task:progress",
  "agentId": "YOUR_AGENT_ID",
  "taskId": "TASK_ID",
  "data": { "progress": 50, "message": "Completed first draft" }
}
```

### When Submitting for Review

Use this when your work is done and ready for human review. This automatically creates a review record in the Inbox with your deliverables and checklist.

```json
{
  "event": "task:review",
  "agentId": "YOUR_AGENT_ID",
  "taskId": "TASK_ID",
  "data": {
    "work_summary": "Describe what you did and what the human should look at",
    "deliverables": [
      { "name": "report.md", "type": "doc", "path": "/workspace/docs/report.md", "summary": "The main report" },
      { "name": "data.json", "type": "file", "path": "/workspace/data/output.json", "summary": "Raw analysis data" }
    ],
    "checklist": [
      { "label": "Meets requirements", "checked": true },
      { "label": "No errors", "checked": true },
      { "label": "Well documented", "checked": false }
    ]
  }
}
```

### When a Task is Complete (after human approval)

```json
{
  "event": "task:completed",
  "agentId": "YOUR_AGENT_ID",
  "taskId": "TASK_ID",
  "data": { "message": "Task completed successfully" }
}
```

### When a Task Fails

```json
{
  "event": "task:failed",
  "agentId": "YOUR_AGENT_ID",
  "taskId": "TASK_ID",
  "data": { "reason": "Explain what went wrong and why" }
}
```

---

## Publishing to the Library

When you produce research, reports, documentation, analysis, or any reference material, publish it to the Library so it's organized and searchable.

### Publishing a New Document

```json
{
  "event": "library:publish",
  "agentId": "YOUR_AGENT_ID",
  "data": {
    "title": "Document Title",
    "content": "Full document content in markdown, JSON, or plain text",
    "doc_type": "research",
    "format": "markdown",
    "collection_id": "col_research",
    "projectId": "PROJECT_ID_IF_RELEVANT",
    "source_path": "/workspace/docs/my-report.md"
  }
}
```

**Document types**: `research`, `report`, `documentation`, `reference`, `template`, `note`, `analysis`, `brief`, `guide`, `other`

**Formats**: `markdown`, `html`, `code`, `json`, `text`, `csv`

**Default collections** (use these IDs):
- `col_research` — Research findings, competitive analysis, market data
- `col_reports` — Status reports, weekly summaries, metrics
- `col_docs` — Technical documentation, API docs, guides
- `col_reference` — Reference material, specifications, standards
- `col_templates` — Reusable templates and boilerplate
- `col_notes` — Meeting notes, scratch work, ideas

### Updating an Existing Document

```json
{
  "event": "library:update",
  "agentId": "YOUR_AGENT_ID",
  "data": {
    "doc_id": "DOCUMENT_ID",
    "content": "Updated content",
    "change_note": "What changed and why"
  }
}
```

---

## Requesting Approvals

When you need human approval before proceeding (deploying to production, making purchases, deleting data, etc.), create a workflow gate:

```json
{
  "event": "approval:needed",
  "agentId": "YOUR_AGENT_ID",
  "data": {
    "type": "workflow_gate",
    "title": "Deploy to production?",
    "description": "All tests pass. 3 files changed. Ready to deploy.",
    "urgency": "urgent",
    "entityType": "task",
    "entityId": "TASK_ID",
    "resumeToken": "UNIQUE_TOKEN_TO_RESUME"
  }
}
```

The human will see this in their Inbox and can approve or reject. If you provided a `resumeToken`, the backend stores it so you can check whether approval was granted.

**Urgency levels**: `critical`, `urgent`, `normal`, `low`

---

## Submitting Project Requests

When you identify new work that should be done (a bug you found, an improvement idea, research that's needed), submit a project request:

```json
{
  "event": "request:submit",
  "agentId": "YOUR_AGENT_ID",
  "data": {
    "title": "Request title",
    "description": "Detailed description of what's needed and why",
    "category": "bug",
    "urgency": "urgent"
  }
}
```

**Categories**: `feature`, `bug`, `research`, `content`, `ops`, `automation`, `general`

---

## Reporting Session Lifecycle

### When a Session Starts

Report session creation so Mission Control tracks active sessions:

```json
{
  "event": "session:created",
  "agentId": "YOUR_AGENT_ID",
  "data": { "sessionId": "sess_abc123" }
}
```

### When a Session Ends (Reporting Costs)

When your session ends, report token usage so the Costs dashboard stays accurate:

```json
{
  "event": "session:ended",
  "agentId": "YOUR_AGENT_ID",
  "data": {
    "tokens": {
      "model": "claude-sonnet-4-5",
      "provider": "anthropic",
      "input": 45000,
      "output": 12000,
      "cacheRead": 30000,
      "totalCost": 0.82
    }
  }
}
```

---

## Reporting Agent Status

### When Idle (no more tasks)

```json
{
  "event": "agent:idle",
  "agentId": "YOUR_AGENT_ID",
  "data": { "message": "All assigned tasks complete" }
}
```

### When an Error Occurs

```json
{
  "event": "agent:error",
  "agentId": "YOUR_AGENT_ID",
  "data": { "error": "Description of the error", "context": "What you were trying to do" }
}
```

---

## Using the /mc Shorthand

If your session supports slash commands, you can use these shortcuts instead of crafting full HTTP requests:

```
/mc task:started <taskId>
/mc task:completed <taskId>
/mc task:failed <taskId> <reason>
/mc task:review <taskId>
/mc task:progress <taskId> <percentage> <message>
```

The lifecycle hook translates these into the proper API calls automatically.

---

## Polling for Pending Events

Mission Control pushes events to you via the gateway, but delivery isn't guaranteed (gateway might be down, session might have restarted). At the start of each session, check if any events are waiting for you:

```
GET $MISSION_CONTROL_URL/api/dispatch/pending/YOUR_AGENT_ID
```

Response:
```json
{
  "events": [
    {
      "id": 1,
      "event": "mc:project_kickoff",
      "payload": { "type": "mc:event", "event": "mc:project_kickoff", "projectId": "abc", "projectName": "New Feature", "..." },
      "created_at": "2026-03-21T20:00:00Z"
    }
  ],
  "count": 1
}
```

Calling this endpoint marks the events as delivered. Process each one according to the event type (see the outbound events section below).

To check without consuming: `GET /api/dispatch/pending/YOUR_AGENT_ID?peek=true`

To explicitly acknowledge after processing: `POST /api/dispatch/ack` with `{ "ids": [1, 2, 3] }`

**Best practice**: Check for pending events at session start and after each heartbeat.

---

## Best Practices

1. **Always report task:started** when you begin work — this moves the task to "In Progress" on the dashboard
2. **Use task:review** when work is done — don't use task:completed directly. Let the human review first.
3. **Include deliverables** in your review submission — list every file you created or modified
4. **Publish to the Library** when you create lasting content — reports, research, documentation
5. **Pick the right collection** — don't dump everything in "Notes". Research goes in Research, docs go in Documentation.
6. **Request approval for risky actions** — deployments, deletions, purchases, external API calls with side effects
7. **Report failures honestly** — include what went wrong and what you tried. The human needs context to help.
8. **Include a work_summary** in reviews — explain what you did, what choices you made, and what the human should focus on when reviewing.

---

## Quick Reference

| Event | When to Use |
|-------|-------------|
| `task:started` | You begin working on an assigned task |
| `task:progress` | You want to report incremental progress (0-100%) |
| `task:review` | Work is done, ready for human review |
| `task:completed` | Task is approved and fully done |
| `task:failed` | Something went wrong, task can't be completed |
| `library:publish` | You produced a document worth keeping |
| `library:update` | You revised an existing Library document |
| `approval:needed` | You need human permission before proceeding |
| `request:submit` | You identified new work that should be done |
| `session:created` | Your session just started |
| `session:ended` | Your session is closing, report token usage |
| `agent:idle` | You have no more tasks |
| `agent:error` | You hit a system-level error |

---

## Events You Will RECEIVE from Mission Control

Mission Control sends events back to you when a human makes a decision. These arrive as messages in your session with `type: "mc:event"`. When you receive one, act on it.

### mc:review_approved

Your work was approved. The task is now "done". Look for the next task.

**Fields**: `taskId`, `taskTitle`, `projectId`, `projectName`, `round`, `qualityScore`, `notes`, `nextAction`

**What to do**: Check if the project has more tasks in "todo" stage. If so, pick the next one and start it.

### mc:changes_requested

Your work needs revisions. The task has been moved back to "doing". Read the feedback and fix the issues.

**Fields**: `taskId`, `taskTitle`, `round`, `feedback`, `currentStage`

**What to do**: Read the `feedback` field carefully. It contains the human's specific concerns. Revise your work, then resubmit with `task:review`.

### mc:review_rejected

Your work was rejected. The task is back in "todo" and may be reassigned.

**Fields**: `taskId`, `taskTitle`, `round`, `reason`, `currentStage`

**What to do**: Read the `reason`. If you can address it, pick the task back up. If not, move on to other work.

### mc:approval_granted

A workflow gate you requested was approved. Resume your paused work.

**Fields**: `approvalId`, `approvalType`, `title`, `resumeToken`, `entityType`, `entityId`, `notes`, `nextAction`

**What to do**: If `resumeToken` is present, use it to resume the paused workflow. If `nextAction` is "resume_workflow", continue from where you stopped.

### mc:approval_denied

A workflow gate you requested was denied.

**Fields**: `approvalId`, `approvalType`, `title`, `entityType`, `entityId`, `reason`, `nextAction`

**What to do**: Read the `reason`. You may need to take a different approach or abandon the action.

### mc:project_kickoff

A new project was created (from an approved request or directly). You are the owner agent. Start planning.

**Fields**: `projectId`, `projectName`, `description`, `priority`, `fromRequest`, `requestTitle`, `hint`

**What to do**: Break the project down into tasks. Create them via `POST /api/tasks` with `project_id` set. Put tasks in "backlog" or "todo" stage. Then start working on the highest-priority one.

### mc:task_assigned

A task was assigned to you.

**Fields**: `taskId`, `taskTitle`, `projectId`, `priority`, `currentStage`, `previousAgent`, `nextAction`

**What to do**: If `currentStage` is "todo", start when ready. If "doing", continue work immediately.

### mc:task_resume

A task you own was moved back to "doing" (e.g., after changes requested).

**Fields**: `taskId`, `taskTitle`, `fromStage`, `toStage`, `movedBy`, `nextAction`

**What to do**: Resume work on this task. Check if there's review feedback in the task metadata.

### mc:task_queued

A task you own was moved to "todo" — it's queued and ready for you to pick up.

**Fields**: `taskId`, `taskTitle`, `fromStage`, `movedBy`, `nextAction`

**What to do**: This task is available for you to start. When you're ready, send `task:started` and begin work.

### mc:project_activated

A project you own was activated. Start working on its tasks.

**Fields**: `projectId`, `projectName`, `hint`

**What to do**: Check the `hint` field for the API endpoint to find available tasks. Start with the highest priority one.

### mc:project_paused

A project you own was paused. Stop work on its tasks.

**Fields**: `projectId`, `projectName`, `reason`

**What to do**: Stop working on tasks from this project. Focus on other projects or report idle.

### mc:project_completed

All tasks in a project are done.

**Fields**: `projectId`, `projectName`

**What to do**: Acknowledge completion. Consider publishing a summary to the Library.

### mc:stall_nudge

You haven't reported progress in a while. Mission Control wants a status update.

**Fields**: `taskId`, `taskTitle`, `stallMinutes`, `hint`

**What to do**: Send a `task:progress` event immediately with your current status. If you're stuck, send `task:failed` with the reason.

---

## Outbound Events Quick Reference

| Event | Meaning | Your Action |
|-------|---------|-------------|
| `mc:review_approved` | Work accepted | Find next task |
| `mc:changes_requested` | Revisions needed | Read feedback, fix, resubmit |
| `mc:review_rejected` | Work rejected | Read reason, task back to todo |
| `mc:approval_granted` | Gate cleared | Resume paused workflow |
| `mc:approval_denied` | Gate denied | Handle denial, try alternative |
| `mc:project_kickoff` | New project, you're owner | Plan tasks, break down work |
| `mc:task_assigned` | Task assigned to you | Start or continue work |
| `mc:task_resume` | Task moved back to doing | Resume work |
| `mc:task_queued` | Task moved to todo | Pick up when ready |
| `mc:project_activated` | Project is now active | Start working on tasks |
| `mc:project_paused` | Project paused | Stop work on its tasks |
| `mc:project_completed` | All tasks done | Acknowledge, maybe publish summary |
| `mc:stall_nudge` | No progress reported | Send status update immediately |

---

## Trigger Contracts — What Happens When a Human Decides

These are the complete end-to-end chains from a human decision in the dashboard to the expected agent response. If you receive one of these events, you MUST act on it — the human is waiting.

### Request Approved → Project Kickoff

**Human action**: Approves a request in the Inbox, or clicks "Convert to Project" on a request.

**What Mission Control does**:
1. Creates a new project in the database (status: `active`)
2. Links it to the original request
3. Dispatches `mc:project_kickoff` to the owner agent

**Event you receive**: `mc:project_kickoff`

**Your required response**:
1. Read the `description` and `priority` fields
2. Break the project into tasks — send `POST $MISSION_CONTROL_URL/api/tasks` for each one:
   ```json
   {
     "project_id": "PROJECT_ID_FROM_EVENT",
     "title": "Task name",
     "description": "What to do",
     "priority": "high",
     "pipeline_stage": "todo",
     "assigned_agent": "YOUR_AGENT_ID"
   }
   ```
3. Pick the highest-priority task and send `task:started` to begin work
4. If you can't plan the project (unclear requirements), send a `request:submit` event asking for clarification

**If you don't respond**: The project sits empty with zero tasks. The human sees it on the dashboard with 0% progress and no activity.

### Project Activated → Start Working

**Human action**: Sets a project's status to "active" (either via the Projects page or by approving a request).

**What Mission Control does**:
1. Updates the project status in the database
2. Dispatches `mc:project_activated` to the owner agent

**Event you receive**: `mc:project_activated`

**Your required response**:
1. Query available tasks: `GET $MISSION_CONTROL_URL/api/tasks?project_id=PROJECT_ID&pipeline_stage=todo`
2. If tasks exist, pick the highest-priority one and send `task:started`
3. If no tasks exist, create them first (same as kickoff flow above)

**If you don't respond**: The project shows as "active" but with no tasks moving. The stall detector will eventually flag it.

### Review Approved → Next Task

**Human action**: Approves a review in the Inbox.

**What Mission Control does**:
1. Moves the task to "done" stage
2. Checks if all project tasks are done (if so, completes the project)
3. Dispatches `mc:review_approved` to the agent who submitted the review

**Event you receive**: `mc:review_approved`

**Your required response**:
1. Check the `nextTaskHint` field — it contains the API URL to find the next todo task
2. If there's a next task, send `task:started` and begin work
3. If no more tasks in the project, send `agent:idle`
4. Consider publishing a progress report to the Library

**If you don't respond**: The completed task shows as done, but the next task in the project stays in "todo" with nobody working on it.

### Changes Requested → Revise and Resubmit

**Human action**: Requests changes on a review.

**What Mission Control does**:
1. Moves the task back to "doing" stage
2. Stores the feedback in the task metadata
3. Dispatches `mc:changes_requested` to the agent

**Event you receive**: `mc:changes_requested`

**Your required response**:
1. Read the `feedback` field — it contains the human's specific concerns
2. Revise your work to address each point
3. Resubmit with `task:review` including updated deliverables and a new `work_summary` that explains what you changed

**If you don't respond**: The task sits in "doing" with review feedback that nobody acts on. The stall detector will flag it.
