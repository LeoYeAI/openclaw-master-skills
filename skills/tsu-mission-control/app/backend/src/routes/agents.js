import { Router } from "express";
import { getDb } from "../db.js";
import { broadcast } from "../services/events.js";
import { wrapRouter } from "../middleware.js";

const router = Router();

// ── LIST ──────────────────────────────────────────────
router.get("/", (req, res) => {
  const db = getDb();
  const agents = db.prepare("SELECT * FROM agents ORDER BY id").all();

  // Attach current task info
  for (const a of agents) {
    if (a.current_task_id) {
      a.current_task = db.prepare("SELECT id, title, pipeline_stage FROM tasks WHERE id = ?")
        .get(a.current_task_id);
    }
    a.active_tasks = db.prepare(
      "SELECT COUNT(*) as count FROM tasks WHERE assigned_agent = ? AND status IN ('assigned','in_progress')"
    ).get(a.id)?.count || 0;
  }

  res.json(agents);
});

// ── UPSERT (used by gateway sync + hooks) ─────────────
router.put("/:id", (req, res) => {
  const db = getDb();
  const { display_name, status, model, current_task_id, session_count, metadata } = req.body;

  const existing = db.prepare("SELECT * FROM agents WHERE id = ?").get(req.params.id);

  if (existing) {
    const updates = [];
    const values = [];
    if (display_name !== undefined) { updates.push("display_name = ?"); values.push(display_name); }
    if (status !== undefined)       { updates.push("status = ?"); values.push(status); }
    if (model !== undefined)        { updates.push("model = ?"); values.push(model); }
    if (current_task_id !== undefined) { updates.push("current_task_id = ?"); values.push(current_task_id); }
    if (session_count !== undefined) { updates.push("session_count = ?"); values.push(session_count); }
    if (metadata !== undefined)     { updates.push("metadata = ?"); values.push(JSON.stringify(metadata)); }

    updates.push("last_heartbeat = datetime('now')");
    values.push(req.params.id);

    if (updates.length > 1) {
      db.prepare(`UPDATE agents SET ${updates.join(", ")} WHERE id = ?`).run(...values);
    }

    // Log status changes
    if (status && status !== existing.status) {
      db.prepare(`
        INSERT INTO activity_log (entity_type, entity_id, action, old_value, new_value, actor, message)
        VALUES ('agent', ?, 'status_changed', ?, ?, 'system', ?)
      `).run(req.params.id, existing.status, status, `Agent ${req.params.id} → ${status}`);
    }
  } else {
    db.prepare(`
      INSERT INTO agents (id, display_name, status, model, current_task_id, session_count, last_heartbeat, metadata)
      VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
    `).run(
      req.params.id,
      display_name || req.params.id,
      status || "unknown",
      model || "",
      current_task_id || null,
      session_count || 0,
      JSON.stringify(metadata || {})
    );
  }

  const agent = db.prepare("SELECT * FROM agents WHERE id = ?").get(req.params.id);
  broadcast("agent:updated", agent);
  res.json(agent);
});

// ── HEARTBEAT ─────────────────────────────────────────
router.post("/:id/heartbeat", (req, res) => {
  const db = getDb();
  db.prepare("UPDATE agents SET last_heartbeat = datetime('now') WHERE id = ?")
    .run(req.params.id);

  if (req.body.status) {
    db.prepare("UPDATE agents SET status = ? WHERE id = ?")
      .run(req.body.status, req.params.id);
  }

  broadcast("agent:heartbeat", { id: req.params.id, at: new Date().toISOString() });
  res.json({ ok: true });
});

wrapRouter(router);
export default router;
