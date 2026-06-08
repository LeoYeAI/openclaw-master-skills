import { Router } from "express";
import { getDb } from "../db.js";
import { broadcast } from "../services/events.js";
import { onReviewApproved, onReviewChangesRequested, onReviewRejected } from "../services/dispatcher.js";
import { wrapRouter, validate } from "../middleware.js";

const router = Router();

// ── LIST (Review Desk queue) ──────────────────────────
router.get("/", (req, res) => {
  const db = getDb();
  const { status, project_id, task_id } = req.query;
  const filterStatus = status || "pending";

  let sql = "SELECT r.*, t.title as task_title, t.priority as task_priority, t.assigned_agent, p.name as project_name FROM reviews r LEFT JOIN tasks t ON t.id = r.task_id LEFT JOIN projects p ON p.id = r.project_id WHERE 1=1";
  const params = [];
  if (filterStatus !== "all") { sql += " AND r.status = ?"; params.push(filterStatus); }
  if (project_id) { sql += " AND r.project_id = ?"; params.push(project_id); }
  if (task_id) { sql += " AND r.task_id = ?"; params.push(task_id); }
  sql += " ORDER BY CASE t.priority WHEN 'critical' THEN 0 WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, r.submitted_at DESC";

  res.json(db.prepare(sql).all(...params));
});

// ── GET ONE (full review with comments + task context) ─
router.get("/:id", (req, res) => {
  const db = getDb();
  const review = db.prepare(`
    SELECT r.*, t.title as task_title, t.description as task_description,
           t.priority as task_priority, t.assigned_agent, t.started_at, t.estimated_mins,
           p.name as project_name
    FROM reviews r
    LEFT JOIN tasks t ON t.id = r.task_id
    LEFT JOIN projects p ON p.id = r.project_id
    WHERE r.id = ?
  `).get(req.params.id);

  if (!review) return res.status(404).json({ error: "Review not found" });

  // Comments
  review.comments = db.prepare(
    "SELECT * FROM review_comments WHERE review_id = ? ORDER BY created_at ASC"
  ).all(req.params.id);

  // Previous rounds for context
  review.previous_rounds = db.prepare(
    "SELECT id, round, status, quality_score, decision_notes, reviewed_at FROM reviews WHERE task_id = ? AND id != ? ORDER BY round"
  ).all(review.task_id, req.params.id);

  // Task activity log
  review.task_activity = db.prepare(`
    SELECT * FROM activity_log WHERE entity_type = 'task' AND entity_id = ? ORDER BY created_at DESC LIMIT 20
  `).all(review.task_id);

  // Cost for this task
  review.task_cost = db.prepare(`
    SELECT COALESCE(SUM(total_cost_usd), 0) as cost, COALESCE(SUM(input_tokens + output_tokens), 0) as tokens
    FROM cost_entries WHERE task_id = ?
  `).get(review.task_id);

  res.json(review);
});

// ── CREATE (auto-called when task moves to review) ────
router.post("/", (req, res) => {
  const db = getDb();
  const { task_id, submitted_by, deliverables, work_summary, checklist } = req.body;

  if (!task_id) return res.status(400).json({ error: "task_id is required" });

  const task = db.prepare("SELECT * FROM tasks WHERE id = ?").get(task_id);
  if (!task) return res.status(404).json({ error: "Task not found" });

  // Determine round number
  const lastRound = db.prepare(
    "SELECT MAX(round) as r FROM reviews WHERE task_id = ?"
  ).get(task_id);
  const round = (lastRound?.r || 0) + 1;

  const stmt = db.prepare(`
    INSERT INTO reviews (task_id, project_id, round, submitted_by, deliverables, work_summary, checklist)
    VALUES (?, ?, ?, ?, ?, ?, ?)
  `);
  const info = stmt.run(
    task_id,
    task.project_id || null,
    round,
    submitted_by || task.assigned_agent || "agent",
    JSON.stringify(deliverables || []),
    work_summary || "",
    JSON.stringify(checklist || [])
  );

  const review = db.prepare("SELECT * FROM reviews WHERE rowid = ?").get(info.lastInsertRowid);

  db.prepare(`
    INSERT INTO activity_log_v2 (entity_type, entity_id, action, new_value, actor, message)
    VALUES ('review', ?, 'submitted', 'pending', ?, ?)
  `).run(review.id, submitted_by || "agent", `Review round ${round} submitted for "${task.title}"`);

  broadcast("review:submitted", { review, task_title: task.title });
  res.status(201).json(review);
});

// ── ADD COMMENT ───────────────────────────────────────
router.post("/:id/comment", (req, res) => {
  const db = getDb();
  const { content, author, deliverable_ref } = req.body;
  const review = db.prepare("SELECT * FROM reviews WHERE id = ?").get(req.params.id);

  if (!review) return res.status(404).json({ error: "Review not found" });
  if (!content?.trim()) return res.status(400).json({ error: "Content is required" });

  db.prepare(`
    INSERT INTO review_comments (review_id, author, content, deliverable_ref)
    VALUES (?, ?, ?, ?)
  `).run(req.params.id, author || "user", content.trim(), deliverable_ref || null);

  // Mark as in_review if still pending
  if (review.status === "pending") {
    db.prepare("UPDATE reviews SET status = 'in_review' WHERE id = ?").run(req.params.id);
  }

  const comments = db.prepare(
    "SELECT * FROM review_comments WHERE review_id = ? ORDER BY created_at ASC"
  ).all(req.params.id);

  broadcast("review:commented", { review_id: req.params.id, author: author || "user" });
  res.json(comments);
});

// ── DECIDE (approve / request changes / reject) ───────
router.post("/:id/decide", (req, res) => {
  const db = getDb();
  const { decision, notes, quality_score, reviewer, checklist } = req.body;
  const review = db.prepare("SELECT * FROM reviews WHERE id = ?").get(req.params.id);

  if (!review) return res.status(404).json({ error: "Review not found" });
  if (!["approved", "changes_requested", "rejected"].includes(decision)) {
    return res.status(400).json({ error: "Decision must be approved, changes_requested, or rejected" });
  }

  // Update review record
  const updates = ["status = ?", "decision_notes = ?", "reviewer = ?", "reviewed_at = datetime('now')"];
  const values = [decision, notes || "", reviewer || "user"];

  if (quality_score) {
    updates.push("quality_score = ?");
    values.push(quality_score);
  }
  if (checklist) {
    updates.push("checklist = ?");
    values.push(JSON.stringify(checklist));
  }

  values.push(req.params.id);
  db.prepare(`UPDATE reviews SET ${updates.join(", ")} WHERE id = ?`).run(...values);

  // Update the task based on decision
  const task = db.prepare("SELECT * FROM tasks WHERE id = ?").get(review.task_id);

  switch (decision) {
    case "approved": {
      db.prepare(`
        UPDATE tasks SET pipeline_stage = 'done', status = 'done',
          completed_at = datetime('now'), updated_at = datetime('now')
        WHERE id = ?
      `).run(review.task_id);

      db.prepare(`
        INSERT INTO activity_log (entity_type, entity_id, action, old_value, new_value, actor, message)
        VALUES ('task', ?, 'stage_changed', 'review', 'done', ?, ?)
      `).run(review.task_id, reviewer || "user", `Review approved: "${task?.title}" (round ${review.round}, score: ${quality_score || "—"})`);

      broadcast("task:moved", { taskId: review.task_id, from: "review", to: "done" });

      // Check project completion
      if (task?.project_id) {
        const remaining = db.prepare(`
          SELECT COUNT(*) as c FROM tasks WHERE project_id = ? AND pipeline_stage != 'done' AND status != 'cancelled'
        `).get(task.project_id);
        if (remaining.c === 0) {
          db.prepare("UPDATE projects SET status = 'completed', completed_at = datetime('now'), updated_at = datetime('now') WHERE id = ?").run(task.project_id);
          broadcast("project:completed", { id: task.project_id });
        }
      }
      break;
    }

    case "changes_requested": {
      db.prepare(`
        UPDATE tasks SET pipeline_stage = 'doing', status = 'in_progress',
          updated_at = datetime('now'),
          metadata = json_set(COALESCE(metadata, '{}'), '$.review_feedback', ?, '$.review_round', ?)
        WHERE id = ?
      `).run(notes || "Changes requested", review.round, review.task_id);

      db.prepare(`
        INSERT INTO activity_log (entity_type, entity_id, action, old_value, new_value, actor, message)
        VALUES ('task', ?, 'stage_changed', 'review', 'doing', ?, ?)
      `).run(review.task_id, reviewer || "user", `Changes requested on "${task?.title}": ${notes || "see review"}`);

      // Clear stall flag so stall detector doesn't immediately re-flag
      db.prepare(`
        UPDATE tasks SET metadata = json_remove(COALESCE(metadata, '{}'), '$.stall_flagged') WHERE id = ?
      `).run(review.task_id);

      broadcast("task:moved", { taskId: review.task_id, from: "review", to: "doing" });
      break;
    }

    case "rejected": {
      db.prepare(`
        UPDATE tasks SET pipeline_stage = 'todo', status = 'assigned',
          updated_at = datetime('now'),
          metadata = json_set(COALESCE(metadata, '{}'), '$.rejected_reason', ?)
        WHERE id = ?
      `).run(notes || "Rejected in review", review.task_id);

      db.prepare(`
        INSERT INTO activity_log (entity_type, entity_id, action, old_value, new_value, actor, message)
        VALUES ('task', ?, 'stage_changed', 'review', 'todo', ?, ?)
      `).run(review.task_id, reviewer || "user", `Review rejected: "${task?.title}" — ${notes || "no reason given"}`);

      broadcast("task:moved", { taskId: review.task_id, from: "review", to: "todo" });
      break;
    }
  }

  db.prepare(`
    INSERT INTO activity_log_v2 (entity_type, entity_id, action, old_value, new_value, actor, message)
    VALUES ('review', ?, ?, 'pending', ?, ?, ?)
  `).run(review.id, decision, decision, reviewer || "user",
    `Review ${decision} for "${task?.title}" (round ${review.round})`);

  const updated = db.prepare("SELECT * FROM reviews WHERE id = ?").get(req.params.id);
  const project = task?.project_id ? db.prepare("SELECT * FROM projects WHERE id = ?").get(task.project_id) : null;
  broadcast(`review:${decision}`, updated);

  // Dispatch outbound event to agent
  switch (decision) {
    case "approved":
      onReviewApproved(updated, task, project);
      break;
    case "changes_requested":
      onReviewChangesRequested(updated, task);
      break;
    case "rejected":
      onReviewRejected(updated, task);
      break;
  }

  res.json(updated);
});

// ── UPDATE CHECKLIST ──────────────────────────────────
router.patch("/:id/checklist", (req, res) => {
  const db = getDb();
  const { checklist } = req.body;
  db.prepare("UPDATE reviews SET checklist = ? WHERE id = ?").run(JSON.stringify(checklist || []), req.params.id);
  res.json({ ok: true });
});

// ── STATS ─────────────────────────────────────────────
router.get("/stats/summary", (req, res) => {
  const db = getDb();

  const pending = db.prepare("SELECT COUNT(*) as c FROM reviews WHERE status IN ('pending','in_review')").get().c;
  const approved = db.prepare("SELECT COUNT(*) as c FROM reviews WHERE status = 'approved'").get().c;
  const changesRequested = db.prepare("SELECT COUNT(*) as c FROM reviews WHERE status = 'changes_requested'").get().c;
  const avgScore = db.prepare("SELECT AVG(quality_score) as avg FROM reviews WHERE quality_score IS NOT NULL").get().avg;
  const avgRounds = db.prepare("SELECT AVG(round) as avg FROM reviews WHERE status = 'approved'").get().avg;

  res.json({ pending, approved, changesRequested, avgScore: avgScore ? +avgScore.toFixed(1) : null, avgRounds: avgRounds ? +avgRounds.toFixed(1) : null });
});

wrapRouter(router);
export default router;
