import { getDb } from "../db.js";
import { broadcast } from "./events.js";
import { onStallNudge } from "./dispatcher.js";
import { cleanupDeliveredDispatches } from "../routes/dispatch.js";

let interval = null;

export function startStallDetector() {
  // Run every 2 minutes
  interval = setInterval(checkStalls, 2 * 60 * 1000);
  // Also run once on startup after a short delay
  setTimeout(checkStalls, 10_000);
  console.log("[stall-detector] Started (every 2m)");
}

export function stopStallDetector() {
  if (interval) clearInterval(interval);
}

function checkStalls() {
  const db = getDb();

  const config = db.prepare("SELECT * FROM stall_config WHERE id = 'default'").get();
  if (!config) return;

  const { max_doing_mins, max_review_mins, heartbeat_stale_mins, auto_reassign } = config;
  const now = new Date();

  // ── 1. Tasks stuck in "doing" ─────────────────────
  const stalledDoing = db.prepare(`
    SELECT t.*, a.last_heartbeat, a.status as agent_status
    FROM tasks t
    LEFT JOIN agents a ON a.id = t.assigned_agent
    WHERE t.pipeline_stage = 'doing'
      AND t.updated_at < datetime('now', ?)
  `).all(`-${max_doing_mins} minutes`);

  for (const task of stalledDoing) {
    const alreadyFlagged = JSON.parse(task.metadata || "{}").stall_flagged;
    if (alreadyFlagged) continue;

    // Flag it
    db.prepare(`
      UPDATE tasks SET metadata = json_set(COALESCE(metadata, '{}'), '$.stall_flagged', 1, '$.stall_detected_at', ?)
      WHERE id = ?
    `).run(now.toISOString(), task.id);

    db.prepare(`
      INSERT INTO activity_log_v2 (entity_type, entity_id, action, old_value, new_value, actor, message)
      VALUES ('task', ?, 'stall_detected', 'doing', 'stalled', 'system', ?)
    `).run(task.id, `Task "${task.title}" has been in progress for ${max_doing_mins}+ minutes without updates`);

    // Create approval for attention
    db.prepare(`
      INSERT INTO approvals (type, entity_type, entity_id, title, description, urgency, requested_by, context)
      VALUES ('custom', 'task', ?, ?, ?, ?, 'system', ?)
    `).run(
      task.id,
      `Stalled: ${task.title}`,
      `This task has been in "doing" for over ${max_doing_mins} minutes. Agent: ${task.assigned_agent || "unassigned"}. Last update: ${task.updated_at}.`,
      "urgent",
      JSON.stringify({ reason: "stall", agent_status: task.agent_status, last_heartbeat: task.last_heartbeat })
    );

    // Auto-reassign if configured
    if (auto_reassign) {
      db.prepare(`
        UPDATE tasks SET pipeline_stage = 'todo', status = 'assigned',
          assigned_agent = NULL, updated_at = datetime('now'),
          metadata = json_set(COALESCE(metadata, '{}'), '$.auto_reassigned', 1, '$.previous_agent', ?)
        WHERE id = ?
      `).run(task.assigned_agent, task.id);

      db.prepare(`
        INSERT INTO activity_log_v2 (entity_type, entity_id, action, old_value, new_value, actor, message)
        VALUES ('task', ?, 'auto_reassigned', 'doing', 'todo', 'system', ?)
      `).run(task.id, `Task auto-moved back to todo after stalling (was assigned to ${task.assigned_agent})`);
    }

    broadcast("task:stalled", { task, config });

    // Nudge the agent to report status
    onStallNudge(task, max_doing_mins);
  }

  // ── 2. Tasks stuck in "review" ────────────────────
  const stalledReview = db.prepare(`
    SELECT * FROM tasks
    WHERE pipeline_stage = 'review'
      AND updated_at < datetime('now', ?)
      AND NOT EXISTS (
        SELECT 1 FROM approvals WHERE entity_type = 'task' AND entity_id = tasks.id AND status = 'pending'
      )
  `).all(`-${max_review_mins} minutes`);

  for (const task of stalledReview) {
    // Create a review approval
    db.prepare(`
      INSERT INTO approvals (type, entity_type, entity_id, title, description, urgency, requested_by)
      VALUES ('task_review', 'task', ?, ?, ?, 'normal', 'system')
    `).run(
      task.id,
      `Review needed: ${task.title}`,
      `This task has been waiting for review for ${max_review_mins}+ minutes.`
    );

    broadcast("approval:created", { type: "task_review", entity_id: task.id });
  }

  // ── 3. Stale agents (no heartbeat) ────────────────
  const staleAgents = db.prepare(`
    SELECT * FROM agents
    WHERE status IN ('online', 'busy')
      AND last_heartbeat < datetime('now', ?)
  `).all(`-${heartbeat_stale_mins} minutes`);

  for (const agent of staleAgents) {
    db.prepare("UPDATE agents SET status = 'offline' WHERE id = ?").run(agent.id);

    db.prepare(`
      INSERT INTO activity_log_v2 (entity_type, entity_id, action, old_value, new_value, actor, message)
      VALUES ('agent', ?, 'stale_detected', ?, 'offline', 'system', ?)
    `).run(agent.id, agent.status, `Agent ${agent.display_name || agent.id} marked offline (no heartbeat for ${heartbeat_stale_mins}+ min)`);

    broadcast("agent:stale", { id: agent.id, was: agent.status });
  }

  // ── 4. Expire old approvals ───────────────────────
  db.prepare(`
    UPDATE approvals SET status = 'expired'
    WHERE status = 'pending' AND expires_at IS NOT NULL AND expires_at < datetime('now')
  `).run();

  const stalledCount = stalledDoing.filter(t => !JSON.parse(t.metadata || "{}").stall_flagged).length;
  if (stalledCount > 0 || staleAgents.length > 0) {
    console.log(`[stall-detector] Found ${stalledCount} stalled tasks, ${staleAgents.length} stale agents`);
  }

  // ── 5. Cleanup old delivered dispatches ────────────
  cleanupDeliveredDispatches();
}
