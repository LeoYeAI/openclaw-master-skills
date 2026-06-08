import { Router } from "express";
import { getDb } from "../db.js";
import { broadcast } from "../services/events.js";
import { onProjectActivated, onProjectPaused, onProjectCompleted } from "../services/dispatcher.js";
import { wrapRouter, validate } from "../middleware.js";

const router = Router();

// ── LIST ──────────────────────────────────────────────
router.get("/", (req, res) => {
  const db = getDb();
  const { status, owner } = req.query;

  let sql = "SELECT * FROM projects WHERE 1=1";
  const params = [];
  if (status) { sql += " AND status = ?"; params.push(status); }
  if (owner) { sql += " AND owner_agent = ?"; params.push(owner); }
  sql += " ORDER BY updated_at DESC";

  const projects = db.prepare(sql).all(...params);

  // Attach task counts per project
  const countStmt = db.prepare(
    `SELECT pipeline_stage, COUNT(*) as count FROM tasks
     WHERE project_id = ? GROUP BY pipeline_stage`
  );
  for (const p of projects) {
    p.task_counts = countStmt.all(p.id).reduce((acc, r) => {
      acc[r.pipeline_stage] = r.count;
      return acc;
    }, {});
  }

  res.json(projects);
});

// ── GET ONE ───────────────────────────────────────────
router.get("/:id", (req, res) => {
  const db = getDb();
  const project = db.prepare("SELECT * FROM projects WHERE id = ?").get(req.params.id);
  if (!project) return res.status(404).json({ error: "Project not found" });

  // Include tasks
  project.tasks = db.prepare(
    "SELECT * FROM tasks WHERE project_id = ? ORDER BY sort_order, created_at"
  ).all(req.params.id);

  res.json(project);
});

// ── CREATE ────────────────────────────────────────────
router.post("/", (req, res) => {
  const db = getDb();
  const { name, description, priority, owner_agent, metadata } = req.body;

  if (!name) return res.status(400).json({ error: "Name is required" });

  const err = validate(req.body, {
    name: { required: true, type: "string", maxLength: 300 },
    description: { type: "string", maxLength: 10000 },
    priority: { type: "string", oneOf: ["critical", "high", "medium", "low"] },
    owner_agent: { type: "string", maxLength: 100 },
  });
  if (err) return res.status(400).json({ error: err });

  const stmt = db.prepare(`
    INSERT INTO projects (name, description, priority, owner_agent, metadata)
    VALUES (?, ?, ?, ?, ?)
  `);
  const info = stmt.run(
    name,
    description || "",
    priority || "medium",
    owner_agent || null,
    JSON.stringify(metadata || {})
  );

  const project = db.prepare("SELECT * FROM projects WHERE rowid = ?").get(info.lastInsertRowid);

  // Log activity
  db.prepare(`
    INSERT INTO activity_log (entity_type, entity_id, action, new_value, actor, message)
    VALUES ('project', ?, 'created', ?, 'user', ?)
  `).run(project.id, project.status, `Project "${name}" created`);

  broadcast("project:created", project);
  res.status(201).json(project);
});

// ── UPDATE ────────────────────────────────────────────
router.patch("/:id", (req, res) => {
  const db = getDb();
  const existing = db.prepare("SELECT * FROM projects WHERE id = ?").get(req.params.id);
  if (!existing) return res.status(404).json({ error: "Project not found" });

  const fields = ["name", "description", "status", "priority", "owner_agent", "metadata"];
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
  if (req.body.status === "completed") updates.push("completed_at = datetime('now')");

  values.push(req.params.id);
  db.prepare(`UPDATE projects SET ${updates.join(", ")} WHERE id = ?`).run(...values);

  // Log status changes
  if (req.body.status && req.body.status !== existing.status) {
    db.prepare(`
      INSERT INTO activity_log (entity_type, entity_id, action, old_value, new_value, actor, message)
      VALUES ('project', ?, 'status_changed', ?, ?, ?, ?)
    `).run(
      req.params.id, existing.status, req.body.status,
      req.body._actor || "user",
      `Project "${existing.name}" moved from ${existing.status} to ${req.body.status}`
    );

    // Dispatch project lifecycle events to owner agent
    const fresh = db.prepare("SELECT * FROM projects WHERE id = ?").get(req.params.id);
    if (req.body.status === "active" && existing.status !== "active") {
      onProjectActivated(fresh);
    } else if (req.body.status === "paused") {
      onProjectPaused(fresh);
    } else if (req.body.status === "completed") {
      onProjectCompleted(fresh);
    }
  }

  const updated = db.prepare("SELECT * FROM projects WHERE id = ?").get(req.params.id);
  broadcast("project:updated", updated);
  res.json(updated);
});

// ── DELETE ─────────────────────────────────────────────
router.delete("/:id", (req, res) => {
  const db = getDb();
  const existing = db.prepare("SELECT * FROM projects WHERE id = ?").get(req.params.id);
  if (!existing) return res.status(404).json({ error: "Project not found" });

  db.prepare("DELETE FROM projects WHERE id = ?").run(req.params.id);

  db.prepare(`
    INSERT INTO activity_log (entity_type, entity_id, action, old_value, actor, message)
    VALUES ('project', ?, 'deleted', ?, 'user', ?)
  `).run(req.params.id, existing.status, `Project "${existing.name}" deleted`);

  broadcast("project:deleted", { id: req.params.id });
  res.json({ ok: true });
});

wrapRouter(router);
export default router;
