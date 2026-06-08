# Hook Events Reference

All events are sent as HTTP POST to `/api/hooks/event` with the `X-Hook-Secret` header.

---

## Event Payload Format

```json
{
  "event": "event:name",
  "agentId": "agent-id",
  "taskId": "task-id-if-relevant",
  "data": { },
  "timestamp": "2026-03-21T12:00:00Z"
}
```

**Headers:**
```
Content-Type: application/json
X-Hook-Secret: YOUR_HOOK_SECRET
```

---

## Task Events

### task:started

Agent begins working on a task. Moves the task to "doing" stage.

```json
{
  "event": "task:started",
  "agentId": "main",
  "taskId": "t_abc123",
  "data": { "message": "Beginning implementation" }
}
```

### task:progress

Incremental progress update. Dashboard shows percentage.

```json
{
  "event": "task:progress",
  "agentId": "main",
  "taskId": "t_abc123",
  "data": { "progress": 65, "message": "Tests passing, writing docs" }
}
```

### task:review

Agent submits work for human review. Moves task to "review" stage and creates a review record in the Inbox.

```json
{
  "event": "task:review",
  "agentId": "main",
  "taskId": "t_abc123",
  "data": {
    "work_summary": "Implemented auth flow with JWT tokens. Added 12 tests.",
    "deliverables": [
      { "name": "auth.ts", "type": "code", "path": "/workspace/src/auth.ts", "summary": "Auth middleware" },
      { "name": "auth.test.ts", "type": "code", "path": "/workspace/tests/auth.test.ts", "summary": "12 test cases" }
    ],
    "checklist": [
      { "label": "Meets requirements", "checked": true },
      { "label": "Tests pass", "checked": true },
      { "label": "Documentation updated", "checked": false }
    ]
  }
}
```

### task:completed

Task is finished (typically after human approval).

```json
{
  "event": "task:completed",
  "agentId": "main",
  "taskId": "t_abc123",
  "data": { "message": "Completed successfully" }
}
```

### task:failed

Task failed. Includes reason for the failure.

```json
{
  "event": "task:failed",
  "agentId": "main",
  "taskId": "t_abc123",
  "data": { "reason": "API endpoint returns 403 — missing permissions" }
}
```

---

## Library Events

### library:publish

Agent publishes a new document to the Library.

```json
{
  "event": "library:publish",
  "agentId": "research",
  "data": {
    "title": "Competitor Pricing Analysis Q1 2026",
    "content": "# Full markdown content here...",
    "doc_type": "research",
    "format": "markdown",
    "collection_id": "col_research",
    "projectId": "p_abc123",
    "source_path": "/workspace/docs/pricing-analysis.md"
  }
}
```

**Document types**: `research`, `report`, `documentation`, `reference`, `template`, `note`, `analysis`, `brief`, `guide`, `other`

**Formats**: `markdown`, `html`, `code`, `json`, `text`, `csv`

**Default collection IDs**: `col_research`, `col_reports`, `col_docs`, `col_reference`, `col_templates`, `col_notes`

### library:update

Agent updates an existing document. Creates a new version.

```json
{
  "event": "library:update",
  "agentId": "research",
  "data": {
    "doc_id": "d_abc123",
    "content": "# Updated content...",
    "change_note": "Added Q2 data"
  }
}
```

---

## Approval Events

### approval:needed

Agent requests human approval before proceeding.

```json
{
  "event": "approval:needed",
  "agentId": "codex",
  "taskId": "t_abc123",
  "data": {
    "type": "workflow_gate",
    "title": "Deploy to production?",
    "description": "All tests pass. 3 files changed.",
    "urgency": "urgent",
    "entityType": "task",
    "entityId": "t_abc123",
    "resumeToken": "resume_deploy_abc"
  }
}
```

**Urgency**: `critical`, `urgent`, `normal`, `low`
**Types**: `workflow_gate`, `task_review`, `project_approval`, `custom`

---

## Request Events

### request:submit

Agent submits a new project request.

```json
{
  "event": "request:submit",
  "agentId": "main",
  "data": {
    "title": "Fix mobile image rotation bug",
    "description": "iOS Safari rotates images 90 degrees on upload",
    "category": "bug",
    "urgency": "urgent"
  }
}
```

**Categories**: `feature`, `bug`, `research`, `content`, `ops`, `automation`, `general`

---

## Session Events

### session:created

A new agent session started.

```json
{
  "event": "session:created",
  "agentId": "main",
  "data": { "sessionId": "sess_abc123" }
}
```

### session:ended

Agent session closed. Includes token usage and cost data.

```json
{
  "event": "session:ended",
  "agentId": "main",
  "data": {
    "tokens": {
      "model": "claude-sonnet-4-5",
      "provider": "anthropic",
      "input": 45000,
      "output": 12000,
      "cacheRead": 30000,
      "cacheWrite": 5000,
      "inputCost": 0.135,
      "outputCost": 0.60,
      "cacheCost": 0.03,
      "totalCost": 0.82
    }
  }
}
```

---

## Agent Events

### agent:idle

Agent has no more assigned work.

```json
{
  "event": "agent:idle",
  "agentId": "main",
  "data": { "message": "All tasks complete" }
}
```

### agent:error

Agent encountered a system-level error.

```json
{
  "event": "agent:error",
  "agentId": "main",
  "data": { "error": "Context window exceeded", "context": "Working on large file analysis" }
}
```

---

## Slash Command Shortcuts

If the agent's session supports slash commands:

```
/mc task:started <taskId>
/mc task:completed <taskId>
/mc task:failed <taskId> <reason>
/mc task:review <taskId>
/mc task:progress <taskId> <percentage> <message>
```

The lifecycle hook translates these into proper API calls.

---

## Outbound Events (Mission Control → Agents)

These events are dispatched from Mission Control to agents via the OpenClaw Gateway when a human makes a decision. They arrive in the agent's session as messages with `type: "mc:event"`.

### mc:review_approved

Sent when a human approves a review. The task moves to "done".

```json
{
  "type": "mc:event",
  "event": "mc:review_approved",
  "taskId": "t_abc123",
  "taskTitle": "Implement auth flow",
  "projectId": "p_xyz",
  "projectName": "Website Redesign",
  "round": 1,
  "qualityScore": 5,
  "notes": "Clean implementation",
  "nextAction": "check_for_next_task",
  "nextTaskHint": "Check /api/tasks?project_id=p_xyz&pipeline_stage=todo"
}
```

### mc:changes_requested

Review needs revisions. Task moves back to "doing".

```json
{
  "type": "mc:event",
  "event": "mc:changes_requested",
  "taskId": "t_abc123",
  "taskTitle": "API rate limit docs",
  "round": 1,
  "feedback": "Missing code examples and wrong header name",
  "nextAction": "revise_and_resubmit",
  "currentStage": "doing"
}
```

### mc:review_rejected

Work rejected. Task goes back to "todo".

```json
{
  "type": "mc:event",
  "event": "mc:review_rejected",
  "taskId": "t_abc123",
  "taskTitle": "Landing page copy",
  "round": 2,
  "reason": "Off-brand tone, doesn't match style guide",
  "nextAction": "task_returned_to_todo",
  "currentStage": "todo"
}
```

### mc:approval_granted

Workflow gate approved. Agent should resume.

```json
{
  "type": "mc:event",
  "event": "mc:approval_granted",
  "approvalId": "a_123",
  "approvalType": "workflow_gate",
  "title": "Deploy to production?",
  "resumeToken": "resume_deploy_abc",
  "entityType": "task",
  "entityId": "t_abc123",
  "notes": "Go ahead",
  "nextAction": "resume_workflow"
}
```

### mc:approval_denied

Workflow gate denied.

```json
{
  "type": "mc:event",
  "event": "mc:approval_denied",
  "approvalId": "a_123",
  "approvalType": "workflow_gate",
  "title": "Deploy to production?",
  "entityType": "task",
  "entityId": "t_abc123",
  "reason": "Not ready, needs more testing",
  "nextAction": "handle_denial"
}
```

### mc:project_kickoff

Request converted to project. Owner agent should plan and create tasks.

```json
{
  "type": "mc:event",
  "event": "mc:project_kickoff",
  "projectId": "p_new",
  "projectName": "Customer Onboarding Automation",
  "description": "Build automated onboarding flow",
  "priority": "high",
  "fromRequest": "r_123",
  "requestTitle": "Customer onboarding automation",
  "nextAction": "plan_and_create_tasks",
  "hint": "Create tasks via POST /api/tasks with project_id=p_new"
}
```

### mc:task_assigned

Task assigned or reassigned to agent.

```json
{
  "type": "mc:event",
  "event": "mc:task_assigned",
  "taskId": "t_abc123",
  "taskTitle": "Write auth docs",
  "projectId": "p_xyz",
  "priority": "high",
  "currentStage": "todo",
  "previousAgent": null,
  "nextAction": "start_when_ready"
}
```

### mc:task_resume

Task moved back to "doing" (e.g., after changes requested).

```json
{
  "type": "mc:event",
  "event": "mc:task_resume",
  "taskId": "t_abc123",
  "taskTitle": "API rate limit docs",
  "fromStage": "review",
  "toStage": "doing",
  "movedBy": "user",
  "nextAction": "continue_work"
}
```

### mc:task_queued

Task moved to "todo" — available for the agent to pick up.

```json
{
  "type": "mc:event",
  "event": "mc:task_queued",
  "taskId": "t_abc123",
  "taskTitle": "Hero section redesign",
  "fromStage": "backlog",
  "movedBy": "user",
  "nextAction": "awaiting_start"
}
```

### mc:project_activated / mc:project_paused / mc:project_completed

Project lifecycle changes.

```json
{
  "type": "mc:event",
  "event": "mc:project_activated",
  "projectId": "p_xyz",
  "projectName": "Website Redesign",
  "nextAction": "start_working",
  "hint": "Check /api/tasks?project_id=p_xyz&pipeline_stage=todo"
}
```

### mc:stall_nudge

Agent hasn't reported progress. Needs immediate status update.

```json
{
  "type": "mc:event",
  "event": "mc:stall_nudge",
  "taskId": "t_abc123",
  "taskTitle": "Implement auth flow",
  "stallMinutes": 120,
  "nextAction": "report_status",
  "hint": "Send a task:progress event, or task:failed if blocked."
}
```

---

## Complete Event Flow

```
Agent → Mission Control (inbound hooks):
  task:started, task:progress, task:review, task:completed, task:failed
  library:publish, library:update
  approval:needed, request:submit
  session:ended, agent:idle, agent:error

Mission Control → Agent (outbound dispatches):
  mc:review_approved, mc:changes_requested, mc:review_rejected
  mc:approval_granted, mc:approval_denied
  mc:project_kickoff, mc:project_activated, mc:project_paused, mc:project_completed
  mc:task_assigned, mc:task_resume, mc:task_queued
  mc:stall_nudge
```
