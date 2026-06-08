import { Router } from "express";
import { getDb } from "../db.js";
import { broadcast } from "../services/events.js";
import { onTaskStageChanged, onTaskAssigned } from "../services/dispatcher.js";
import { wrapRouter, validate } from "../middleware.js";

const router = Router();

// Valid pipeline transitions (enforce state machine)
const VALID_TRANSITIONS = {
  backlog: ["todo"],
  todo: ["doing", "backlog"],
  doing: ["review", "todo", "blocked"],
  review: ["done", "doing"],
  done: [],                        // terminal
  blocked: ["todo", "doing"],
};

// ── LIST ──────────────────────────────────────────────
router.get("/", (req, res) => {
  const db = getDb();
  const { project_id, status, pipeline_stage, assigned_agent } = req.query;

  let sql = "SELECT * FROM tasks WHERE 1=1";
  const params = [];
  if (project_id)      { sql += " AND project_id = ?";      params.push(project_id); }
  if (status)          { sql += " AND status = ?";           params.push(status); }
  if (pipeline_stage)  { sql += " AND pipeline_stage = ?";   params.push(pipeline_stage); }
  if (assigned_agent)  { sql += " AND assigned_agent = ?";   params.push(assigned_agent); }
  sql += " ORDER BY sort_order, created_at DESC";

  const tasks = db.prepare(sql).all(...params);
  res.json(tasks);
});

// ── GET ONE ───────────────────────────────────────────
router.get("/:id", (req, res) => {
  const db = getDb();
  const task = db.prepare("SELECT * FROM tasks WHERE id = ?").get(req.params.id);
  if (!task) return res.status(404).json({ error: "Task not found" });

  // Include activity
  task.activity = db.prepare(
    "SELECT * FROM activity_log WHERE entity_type = 'task' AND entity_id = ? ORDER BY created_at DESC LIMIT 50"
  ).all(req.params.id);

  // Include tags
  task.tags = db.prepare(`
    SELECT t.* FROM tags t
    JOIN task_tags tt ON tt.tag_id = t.id
    WHERE tt.task_id = ?
  `).all(req.params.id);

  res.json(task);
});

// ── CREATE ────────────────────────────────────────────
router.post("/", (req, res) => {
  const db = getDb();
  const {
    project_id, title, description, priority,
    assigned_agent, pipeline_stage, estimated_mins, metadata
  } = req.body;

  if (!title) return res.status(400).json({ error: "Title is required" });

  const err = validate(req.body, {
    title: { required: true, type: "string", maxLength: 500 },
    description: { type: "string", maxLength: 10000 },
    priority: { type: "string", oneOf: ["critical", "high", "medium", "low"] },
    pipeline_stage: { type: "string", oneOf: ["backlog", "todo", "doing", "review", "done"] },
    assigned_agent: { type: "string", maxLength: 100 },
  });
  if (err) return res.status(400).json({ error: err });

  // Auto-set status based on pipeline stage
  const stage = pipeline_stage || "backlog";
  const statusMap = {
    backlog: "inbox", todo: "assigned", doing: "in_progress",
    review: "review", done: "done"
  };

  const stmt = db.prepare(`
    INSERT INTO tasks (project_id, title, description, priority, assigned_agent,
                       pipeline_stage, status, estimated_mins, metadata)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  const info = stmt.run(
    project_id || null,
    title,
    description || "",
    priority || "medium",
    assigned_agent || null,
    stage,
    statusMap[stage] || "inbox",
    estimated_mins || null,
    JSON.stringify(metadata || {})
  );

  const task = db.prepare("SELECT * FROM tasks WHERE rowid = ?").get(info.lastInsertRowid);

  db.prepare(`
    INSERT INTO activity_log (entity_type, entity_id, action, new_value, actor, message)
    VALUES ('task', ?, 'created', ?, 'user', ?)
  `).run(task.id, task.pipeline_stage, `Task "${title}" created`);

  broadcast("task:created", task);
  res.status(201).json(task);
});

// ── MOVE (pipeline stage transition) ──────────────────
router.post("/:id/move", (req, res) => {
  const db = getDb();
  const { to_stage, actor } = req.body;
  const task = db.prepare("SELECT * FROM tasks WHERE id = ?").get(req.params.id);

  if (!task) return res.status(404).json({ error: "Task not found" });
  if (!to_stage) return res.status(400).json({ error: "to_stage is required" });

  // Validate transition
  const allowed = VALID_TRANSITIONS[task.pipeline_stage];
  if (!allowed || !allowed.includes(to_stage)) {
    return res.status(422).json({
      error: `Cannot move from "${task.pipeline_stage}" to "${to_stage}"`,
      allowed_transitions: allowed || []
    });
  }

  const statusMap = {
    backlog: "inbox", todo: "assigned", doing: "in_progress",
    review: "review", done: "done", blocked: "blocked"
  };

  const updates = [
    "pipeline_stage = ?", "status = ?", "updated_at = datetime('now')"
  ];
  const values = [to_stage, statusMap[to_stage]];

  if (to_stage === "doing" && !task.started_at) {
    updates.push("started_at = datetime('now')");
  }
  if (to_stage === "done") {
    updates.push("completed_at = datetime('now')");
  }

  values.push(req.params.id);
  db.prepare(`UPDATE tasks SET ${updates.join(", ")} WHERE id = ?`).run(...values);

  db.prepare(`
    INSERT INTO activity_log (entity_type, entity_id, action, old_value, new_value, actor, message)
    VALUES ('task', ?, 'stage_changed', ?, ?, ?, ?)
  `).run(
    req.params.id, task.pipeline_stage, to_stage,
    actor || "user",
    `Task "${task.title}" moved from ${task.pipeline_stage} → ${to_stage}`
  );

  const updated = db.prepare("SELECT * FROM tasks WHERE id = ?").get(req.params.id);
  broadcast("task:moved", { task: updated, from: task.pipeline_stage, to: to_stage });

  // Dispatch outbound event to assigned agent
  onTaskStageChanged(updated, task.pipeline_stage, to_stage, actor);

  res.json(updated);
});

// ── UPDATE ────────────────────────────────────────────
router.patch("/:id", (req, res) => {
  const db = getDb();
  const existing = db.prepare("SELECT * FROM tasks WHERE id = ?").get(req.params.id);
  if (!existing) return res.status(404).json({ error: "Task not found" });

  const fields = [
    "title", "description", "priority", "assigned_agent",
    "sort_order", "estimated_mins", "actual_mins", "metadata"
  ];
  const updates = [];
  const values = [];

  for (const f of fields) {
    if (req.body[f] !== undefined) {
      updates.push(`${f} = ?`);
      values.push(f === "metadata" ? JSON.stringify(req.body[f]) : req.body[f]);
    }
  }

  if (updates.length === 0) return res.status(400).json({ error: "No fields to update" });
  updates.push("updated_at = datetime('now')");

  values.push(req.params.id);
  db.prepare(`UPDATE tasks SET ${updates.join(", ")} WHERE id = ?`).run(...values);

  if (req.body.assigned_agent && req.body.assigned_agent !== existing.assigned_agent) {
    db.prepare(`
      INSERT INTO activity_log (entity_type, entity_id, action, old_value, new_value, actor, message)
      VALUES ('task', ?, 'assigned', ?, ?, ?, ?)
    `).run(
      req.params.id, existing.assigned_agent || "none", req.body.assigned_agent,
      req.body._actor || "user",
      `Task "${existing.title}" assigned to ${req.body.assigned_agent}`
    );

    // Dispatch assignment to the new agent
    onTaskAssigned(updated, existing.assigned_agent);
  }

  const updated = db.prepare("SELECT * FROM tasks WHERE id = ?").get(req.params.id);
  broadcast("task:updated", updated);
  res.json(updated);
});

// ── DELETE ─────────────────────────────────────────────
router.delete("/:id", (req, res) => {
  const db = getDb();
  const existing = db.prepare("SELECT * FROM tasks WHERE id = ?").get(req.params.id);
  if (!existing) return res.status(404).json({ error: "Task not found" });

  db.prepare("DELETE FROM tasks WHERE id = ?").run(req.params.id);
  broadcast("task:deleted", { id: req.params.id });
  res.json({ ok: true });
});

// ── PIPELINE OVERVIEW ──────────────────────────────────
router.get("/pipeline/overview", (req, res) => {
  const db = getDb();
  const { project_id } = req.query;

  let where = "";
  const params = [];
  if (project_id) { where = " WHERE project_id = ?"; params.push(project_id); }

  const stages = ["backlog", "todo", "doing", "review", "done"];
  const pipeline = {};

  for (const stage of stages) {
    pipeline[stage] = db.prepare(
      `SELECT * FROM tasks${where ? where + " AND" : " WHERE"} pipeline_stage = ?
       ORDER BY sort_order, priority DESC, created_at`
    ).all(...params, stage);
  }

  res.json(pipeline);
});

wrapRouter(router);
export default router;
