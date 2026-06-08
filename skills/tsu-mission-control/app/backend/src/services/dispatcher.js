/**
 * Outbound Dispatcher — sends events FROM Mission Control TO agents
 *
 * THREE delivery paths (tried in priority order):
 *   1. HTTP POST to gateway /hooks/agent — triggers a real agent turn (most reliable)
 *   2. WebSocket "agent" method — if WS is connected
 *   3. Pending queue in SQLite — agents can poll GET /api/dispatch/pending
 *
 * The pending queue is ALWAYS written first as a guaranteed delivery floor.
 * If HTTP or WS delivery succeeds, the pending record is cleaned up.
 * If both fail, the agent picks it up on next heartbeat/poll.
 */

import { getDb } from "../db.js";
import { broadcast } from "./events.js";

let gatewaySend = null;

export function setGatewaySender(sendFn) {
  gatewaySend = sendFn;
}

// ══════════════════════════════════════════════════════
// CORE DISPATCH
// ══════════════════════════════════════════════════════

function dispatch(agentId, event, payload) {
  try {
    const db = getDb();
    const targetAgent = agentId || "main";
    const eventPayload = { type: "mc:event", event, ...payload, timestamp: new Date().toISOString() };

    // Log to activity
    try {
      db.prepare(`
        INSERT INTO activity_log_v2 (entity_type, entity_id, action, new_value, actor, message)
        VALUES ('dispatch', ?, ?, ?, 'mission-control', ?)
      `).run(targetAgent, event, JSON.stringify(payload), `Dispatched ${event} to ${targetAgent}`);
    } catch (e) { console.error(`[dispatcher] log failed:`, e.message); }

    // Always queue for polling (guaranteed floor)
    let pendingId = null;
    try {
      const info = db.prepare(`INSERT INTO pending_dispatches (agent_id, event, payload) VALUES (?, ?, ?)`).run(
        targetAgent, event, JSON.stringify(eventPayload)
      );
      pendingId = info.lastInsertRowid;
    } catch (e) { console.error(`[dispatcher] queue failed:`, e.message); }

    // Path 1: HTTP POST to gateway /hooks/agent
    const gwUrl = process.env.OPENCLAW_GATEWAY_URL || "";
    const gwToken = process.env.OPENCLAW_GATEWAY_TOKEN || "";
    const agentMessage = formatAgentMessage(event, payload);

    if (gwUrl) {
      const httpBase = gwUrl.replace(/^ws(s?):\/\//, "http$1://");
      const hookUrl = `${httpBase}/hooks/agent`;

      fetch(hookUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(gwToken ? { "x-openclaw-token": gwToken } : {}),
        },
        body: JSON.stringify({
          message: agentMessage,
          name: `MC: ${event}`,
          agent: targetAgent,
        }),
      }).then(res => {
        if (res.ok) {
          console.log(`[dispatcher] ${event} → ${targetAgent} via /hooks/agent (${res.status})`);
          if (pendingId) try { db.prepare("DELETE FROM pending_dispatches WHERE id = ?").run(pendingId); } catch {}
        } else {
          console.warn(`[dispatcher] /hooks/agent ${res.status} for ${event} — falling back to WS`);
          trySendViaWS(targetAgent, agentMessage, event);
        }
      }).catch(err => {
        console.warn(`[dispatcher] /hooks/agent failed: ${err.message} — falling back to WS`);
        trySendViaWS(targetAgent, agentMessage, event);
      });
    } else {
      trySendViaWS(targetAgent, agentMessage, event);
    }

    // SSE broadcast for frontend
    broadcast(`dispatch:${event}`, { agentId: targetAgent, ...payload });

  } catch (err) {
    console.error(`[dispatcher] CRITICAL: ${event} failed entirely:`, err.message);
  }
}

function trySendViaWS(agentId, message, event) {
  if (!gatewaySend) return;
  try {
    gatewaySend("agent", {
      agent: agentId,
      message,
      idempotencyKey: `mc-${event}-${Date.now()}`,
    });
    console.log(`[dispatcher] ${event} → ${agentId} via WS agent method`);
  } catch (e) {
    console.warn(`[dispatcher] WS failed for ${event}: ${e.message} — event queued for polling`);
  }
}

// ══════════════════════════════════════════════════════
// AGENT MESSAGE FORMATTING
// ══════════════════════════════════════════════════════

function formatAgentMessage(event, p) {
  switch (event) {
    case "mc:project_kickoff":
      return [
        `[Mission Control] New project "${p.projectName}" has been approved and needs task planning.`,
        `Project ID: ${p.projectId}`,
        `Priority: ${p.priority || "medium"}`,
        p.description ? `Description: ${p.description}` : null,
        ``,
        `ACTION REQUIRED: Break this project into tasks.`,
        `For each task, POST to /api/tasks with:`,
        `  { "project_id": "${p.projectId}", "title": "...", "priority": "high|medium|low", "pipeline_stage": "todo", "assigned_agent": "YOUR_ID" }`,
        `Then send task:started on the highest-priority task.`,
      ].filter(Boolean).join("\n");

    case "mc:project_activated":
      return [
        `[Mission Control] Project "${p.projectName}" is now active. Project ID: ${p.projectId}`,
        `ACTION REQUIRED: Check for tasks at GET /api/tasks?project_id=${p.projectId}&pipeline_stage=todo`,
        `Start the highest-priority one.`,
      ].join("\n");

    case "mc:review_approved":
      return [
        `[Mission Control] Review APPROVED for "${p.taskTitle}"${p.qualityScore ? ` (score: ${p.qualityScore}/5)` : ""}.`,
        p.notes ? `Notes: ${p.notes}` : null,
        `ACTION REQUIRED: Find the next todo task in this project and start it.`,
        p.nextTaskHint ? `Hint: ${p.nextTaskHint}` : null,
      ].filter(Boolean).join("\n");

    case "mc:changes_requested":
      return [
        `[Mission Control] CHANGES REQUESTED on "${p.taskTitle}" (round ${p.round}).`,
        `Feedback: ${p.feedback || "See review comments."}`,
        `ACTION REQUIRED: Revise your work based on the feedback above, then resubmit with task:review.`,
      ].join("\n");

    case "mc:review_rejected":
      return [
        `[Mission Control] Review REJECTED for "${p.taskTitle}".`,
        `Reason: ${p.reason || "No reason given."}`,
        `Task returned to "todo". Read the reason and decide whether to retry.`,
      ].join("\n");

    case "mc:approval_granted":
      return [
        `[Mission Control] APPROVAL GRANTED: "${p.title}".`,
        p.notes ? `Notes: ${p.notes}` : null,
        p.resumeToken ? `Resume token: ${p.resumeToken}` : null,
        `ACTION REQUIRED: Proceed with the approved action.`,
      ].filter(Boolean).join("\n");

    case "mc:approval_denied":
      return [
        `[Mission Control] APPROVAL DENIED: "${p.title}".`,
        `Reason: ${p.reason || "No reason given."}`,
        `Do NOT proceed. Consider an alternative approach.`,
      ].join("\n");

    case "mc:task_assigned":
      return [
        `[Mission Control] Task assigned to you: "${p.taskTitle}" (${p.priority || "medium"} priority).`,
        `Task ID: ${p.taskId}, Stage: ${p.currentStage}`,
        p.currentStage === "todo" ? `ACTION REQUIRED: Start when ready (send task:started).` : `Resume work on this task.`,
      ].join("\n");

    case "mc:task_resume":
      return [
        `[Mission Control] Task "${p.taskTitle}" moved back to "doing" by ${p.movedBy || "user"}.`,
        `ACTION REQUIRED: Resume work. Check task metadata for review feedback.`,
      ].join("\n");

    case "mc:stall_nudge":
      return [
        `[Mission Control] STALL ALERT: "${p.taskTitle}" has had no updates for ${p.stallMinutes}+ minutes.`,
        `ACTION REQUIRED: Report status NOW via task:progress, or task:failed if blocked.`,
      ].join("\n");

    case "mc:project_paused":
      return `[Mission Control] Project "${p.projectName}" PAUSED. Stop working on its tasks.`;

    case "mc:project_completed":
      return `[Mission Control] Project "${p.projectName}" COMPLETED. All tasks done. Consider publishing a summary.`;

    case "mc:task_queued":
      return `[Mission Control] Task "${p.taskTitle}" is now in "todo" and available to start.`;

    default:
      return `[Mission Control] ${event}: ${JSON.stringify(p)}`;
  }
}

// ══════════════════════════════════════════════════════
// REVIEW DECISIONS
// ══════════════════════════════════════════════════════

/**
 * Review was approved. Agent should know the work was accepted
 * and look for the next task in the project.
 */
export function onReviewApproved(review, task, project) {
  dispatch(review.submitted_by || task?.assigned_agent, "mc:review_approved", {
    taskId: review.task_id,
    taskTitle: task?.title,
    projectId: review.project_id,
    projectName: project?.name,
    round: review.round,
    qualityScore: review.quality_score,
    notes: review.decision_notes,
    // Help the agent find the next task
    nextAction: "check_for_next_task",
    nextTaskHint: project ? `Check /api/tasks?project_id=${review.project_id}&pipeline_stage=todo` : null,
  });
}

/**
 * Review needs changes. Agent should revise based on feedback.
 */
export function onReviewChangesRequested(review, task) {
  dispatch(review.submitted_by || task?.assigned_agent, "mc:changes_requested", {
    taskId: review.task_id,
    taskTitle: task?.title,
    round: review.round,
    feedback: review.decision_notes,
    nextAction: "revise_and_resubmit",
    // Task has been moved back to "doing" — agent should resume work
    currentStage: "doing",
  });
}

/**
 * Review was rejected. Task goes back to todo for reassignment.
 */
export function onReviewRejected(review, task) {
  dispatch(review.submitted_by || task?.assigned_agent, "mc:review_rejected", {
    taskId: review.task_id,
    taskTitle: task?.title,
    round: review.round,
    reason: review.decision_notes,
    nextAction: "task_returned_to_todo",
    currentStage: "todo",
  });
}

// ══════════════════════════════════════════════════════
// APPROVAL DECISIONS
// ══════════════════════════════════════════════════════

/**
 * Approval granted. If it has a resume token, the agent's
 * paused workflow should continue.
 */
export function onApprovalGranted(approval) {
  dispatch(approval.requested_by, "mc:approval_granted", {
    approvalId: approval.id,
    approvalType: approval.type,
    title: approval.title,
    resumeToken: approval.resume_token,
    entityType: approval.entity_type,
    entityId: approval.entity_id,
    notes: approval.decision_notes,
    nextAction: approval.resume_token ? "resume_workflow" : "proceed",
  });
}

/**
 * Approval denied. Agent needs to handle the rejection.
 */
export function onApprovalDenied(approval) {
  dispatch(approval.requested_by, "mc:approval_denied", {
    approvalId: approval.id,
    approvalType: approval.type,
    title: approval.title,
    entityType: approval.entity_type,
    entityId: approval.entity_id,
    reason: approval.decision_notes,
    nextAction: "handle_denial",
  });
}

// ══════════════════════════════════════════════════════
// REQUEST → PROJECT CONVERSION
// ══════════════════════════════════════════════════════

/**
 * A request was approved and converted into a project.
 * The owner agent should start planning work.
 */
export function onProjectKickoff(project, request) {
  dispatch(project.owner_agent, "mc:project_kickoff", {
    projectId: project.id,
    projectName: project.name,
    description: project.description,
    priority: project.priority,
    fromRequest: request?.id,
    requestTitle: request?.title,
    nextAction: "plan_and_create_tasks",
    // Agent should break the project into tasks and add them to the pipeline
    hint: `Create tasks via POST /api/tasks with project_id=${project.id}. Set pipeline_stage to "backlog" or "todo".`,
  });
}

// ══════════════════════════════════════════════════════
// TASK LIFECYCLE
// ══════════════════════════════════════════════════════

/**
 * A task was assigned to an agent (or reassigned).
 */
export function onTaskAssigned(task, previousAgent) {
  dispatch(task.assigned_agent, "mc:task_assigned", {
    taskId: task.id,
    taskTitle: task.title,
    projectId: task.project_id,
    priority: task.priority,
    currentStage: task.pipeline_stage,
    previousAgent: previousAgent || null,
    nextAction: task.pipeline_stage === "todo" ? "start_when_ready" : "continue_work",
  });
}

/**
 * A task was moved to a stage where an agent should act.
 * Covers: moved to "todo" (available for pickup), moved to "doing"
 * after changes requested, unblocked, etc.
 */
export function onTaskStageChanged(task, fromStage, toStage, actor) {
  // Only dispatch to agents for actionable transitions
  if (toStage === "doing" && task.assigned_agent) {
    dispatch(task.assigned_agent, "mc:task_resume", {
      taskId: task.id,
      taskTitle: task.title,
      fromStage,
      toStage,
      movedBy: actor,
      nextAction: "continue_work",
    });
  }

  if (toStage === "todo" && task.assigned_agent) {
    dispatch(task.assigned_agent, "mc:task_queued", {
      taskId: task.id,
      taskTitle: task.title,
      fromStage,
      movedBy: actor,
      nextAction: "awaiting_start",
    });
  }
}

// ══════════════════════════════════════════════════════
// PROJECT LIFECYCLE
// ══════════════════════════════════════════════════════

/**
 * Project was activated (status → active). Owner agent should
 * start working on backlog/todo tasks.
 */
export function onProjectActivated(project) {
  dispatch(project.owner_agent, "mc:project_activated", {
    projectId: project.id,
    projectName: project.name,
    nextAction: "start_working",
    hint: `Check /api/tasks?project_id=${project.id}&pipeline_stage=todo for available tasks.`,
  });
}

/**
 * All tasks in a project are done.
 */
export function onProjectCompleted(project) {
  dispatch(project.owner_agent, "mc:project_completed", {
    projectId: project.id,
    projectName: project.name,
    nextAction: "project_finished",
  });
}

/**
 * Project was paused. Agents should stop working on its tasks.
 */
export function onProjectPaused(project) {
  dispatch(project.owner_agent, "mc:project_paused", {
    projectId: project.id,
    projectName: project.name,
    nextAction: "stop_work",
    reason: "Project paused by user",
  });
}

// ══════════════════════════════════════════════════════
// STALL RECOVERY
// ══════════════════════════════════════════════════════

/**
 * Stall detector flagged a task. Nudge the agent to report status.
 */
export function onStallNudge(task, stallMinutes) {
  dispatch(task.assigned_agent, "mc:stall_nudge", {
    taskId: task.id,
    taskTitle: task.title,
    stallMinutes,
    nextAction: "report_status",
    hint: "Send a task:progress event with your current status, or task:failed if blocked.",
  });
}
