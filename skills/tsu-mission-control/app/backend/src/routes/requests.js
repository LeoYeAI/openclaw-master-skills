import { Router } from "express";
import { getDb } from "../db.js";
import { broadcast } from "../services/events.js";
import { onProjectKickoff } from "../services/dispatcher.js";
import { wrapRouter, validate } from "../middleware.js";

const router = Router();

// ── LIST ──────────────────────────────────────────────
router.get("/", (req, res) => {
  const db = getDb();
  const { status, category, urgency } = req.query;

  let sql = "SELECT * FROM project_requests WHERE 1=1";
  const params = [];
  if (status)   { sql += " AND status = ?";   params.push(status); }
  if (category) { sql += " AND category = ?"; params.push(category); }
  if (urgency)  { sql += " AND urgency = ?";  params.push(urgency); }
  sql += " ORDER BY CASE urgency WHEN 'critical' THEN 0 WHEN 'urgent' THEN 1 WHEN 'normal' THEN 2 WHEN 'low' THEN 3 ELSE 4 END, created_at DESC";

  res.json(db.prepare(sql).all(...params));
});

// ── GET ONE ───────────────────────────────────────────
router.get("/:id", (req, res) => {
  const db = getDb();
  const r = db.prepare("SELECT * FROM project_requests WHERE id = ?").get(req.params.id);
  if (!r) return res.status(404).json({ error: "Request not found" });

  // Include related activity
  r.activity = db.prepare(
    "SELECT * FROM activity_log_v2 WHERE entity_type = 'request' AND entity_id = ? ORDER BY created_at DESC LIMIT 30"
  ).all(req.params.id);

  res.json(r);
});

// ── SUBMIT NEW REQUEST ────────────────────────────────
router.post("/", (req, res) => {
  const db = getDb();
  const {
    title, description, requester, category, urgency,
    source_channel, source_ref, attachments
  } = req.body;

  if (!title?.trim()) return res.status(400).json({ error: "Title is required" });

  const err = validate(req.body, {
    title: { required: true, type: "string", maxLength: 500 },
    description: { type: "string", maxLength: 10000 },
    category: { type: "string", oneOf: ["feature", "bug", "research", "content", "ops", "automation", "general"] },
    urgency: { type: "string", oneOf: ["critical", "urgent", "normal", "low", "wishlist"] },
    requester: { type: "string", maxLength: 100 },
  });
  if (err) return res.status(400).json({ error: err });

  const stmt = db.prepare(`
    INSERT INTO project_requests (title, description, requester, category, urgency,
                                   source_channel, source_ref, attachments)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);
  const info = stmt.run(
    title.trim(),
    description || "",
    requester || "user",
    category || "general",
    urgency || "normal",
    source_channel || "web",
    source_ref || null,
    JSON.stringify(attachments || [])
  );

  const request = db.prepare("SELECT * FROM project_requests WHERE rowid = ?").get(info.lastInsertRowid);

  db.prepare(`
    INSERT INTO activity_log_v2 (entity_type, entity_id, action, new_value, actor, message)
    VALUES ('request', ?, 'submitted', ?, ?, ?)
  `).run(request.id, request.status, requester || "user", `New request: "${title.trim()}"`);

  // If urgency is critical, auto-create an approval item
  if (urgency === "critical") {
    db.prepare(`
      INSERT INTO approvals (type, entity_type, entity_id, title, description, urgency, requested_by)
      VALUES ('request_triage', 'request', ?, ?, ?, 'critical', ?)
    `).run(request.id, `Triage: ${title.trim()}`, description || "", requester || "system");
  }

  broadcast("request:submitted", request);
  res.status(201).json(request);
});

// ── TRIAGE (review a request) ─────────────────────────
router.post("/:id/triage", (req, res) => {
  const db = getDb();
  const { status, review_notes, reviewer } = req.body;
  const existing = db.prepare("SELECT * FROM project_requests WHERE id = ?").get(req.params.id);
  if (!existing) return res.status(404).json({ error: "Request not found" });

  const allowed = ["triaging", "approved", "rejected", "deferred"];
  if (!allowed.includes(status)) {
    return res.status(422).json({ error: `Status must be one of: ${allowed.join(", ")}` });
  }

  db.prepare(`
    UPDATE project_requests SET status = ?, review_notes = ?, reviewer = ?, updated_at = datetime('now')
    WHERE id = ?
  `).run(status, review_notes || "", reviewer || "user", req.params.id);

  db.prepare(`
    INSERT INTO activity_log_v2 (entity_type, entity_id, action, old_value, new_value, actor, message)
    VALUES ('request', ?, 'triaged', ?, ?, ?, ?)
  `).run(req.params.id, existing.status, status, reviewer || "user",
    `Request "${existing.title}" → ${status}${review_notes ? ": " + review_notes : ""}`);

  const updated = db.prepare("SELECT * FROM project_requests WHERE id = ?").get(req.params.id);
  broadcast("request:triaged", updated);
  res.json(updated);
});

// ── CONVERT TO PROJECT ────────────────────────────────
router.post("/:id/convert", (req, res) => {
  const db = getDb();
  const existing = db.prepare("SELECT * FROM project_requests WHERE id = ?").get(req.params.id);
  if (!existing) return res.status(404).json({ error: "Request not found" });
  if (existing.status === "converted") return res.status(422).json({ error: "Already converted" });

  const { priority, owner_agent, extra_tasks } = req.body;

  // Create the project
  const priorityMap = { critical: "critical", urgent: "high", normal: "medium", low: "low", wishlist: "low" };
  const projInfo = db.prepare(`
    INSERT INTO projects (name, description, priority, owner_agent, status, metadata)
    VALUES (?, ?, ?, ?, 'active', ?)
  `).run(
    existing.title,
    existing.description,
    priority || priorityMap[existing.urgency] || "medium",
    owner_agent || null,
    JSON.stringify({ source_request_id: existing.id, category: existing.category })
  );

  const project = db.prepare("SELECT * FROM projects WHERE rowid = ?").get(projInfo.lastInsertRowid);

  // Link the request back
  db.prepare(`
    UPDATE project_requests SET status = 'converted', converted_project_id = ?, updated_at = datetime('now')
    WHERE id = ?
  `).run(project.id, existing.id);

  // If extra tasks were provided (e.g. from AI decomposition), create them
  if (Array.isArray(extra_tasks)) {
    const taskStmt = db.prepare(`
      INSERT INTO tasks (project_id, title, description, priority, pipeline_stage, status, sort_order)
      VALUES (?, ?, ?, ?, 'backlog', 'inbox', ?)
    `);
    extra_tasks.forEach((t, i) => {
      taskStmt.run(project.id, t.title, t.description || "", t.priority || "medium", i);
    });
  }

  db.prepare(`
    INSERT INTO activity_log_v2 (entity_type, entity_id, action, new_value, actor, message)
    VALUES ('request', ?, 'converted', ?, 'user', ?)
  `).run(existing.id, project.id, `Request converted to project "${existing.title}"`);

  db.prepare(`
    INSERT INTO activity_log (entity_type, entity_id, action, new_value, actor, message)
    VALUES ('project', ?, 'created', 'active', 'user', ?)
  `).run(project.id, `Project created from request: "${existing.title}"`);

  broadcast("request:converted", { request: existing, project });
  broadcast("project:created", project);

  // Dispatch kickoff to the owner agent
  onProjectKickoff(project, existing);

  res.json({ request: { ...existing, status: "converted", converted_project_id: project.id }, project });
});

// ── DELETE ─────────────────────────────────────────────
router.delete("/:id", (req, res) => {
  const db = getDb();
  db.prepare("DELETE FROM project_requests WHERE id = ?").run(req.params.id);
  broadcast("request:deleted", { id: req.params.id });
  res.json({ ok: true });
});

// ── STATS ─────────────────────────────────────────────
router.get("/stats/summary", (req, res) => {
  const db = getDb();
  const byStatus = db.prepare(
    "SELECT status, COUNT(*) as count FROM project_requests GROUP BY status"
  ).all().reduce((a, r) => { a[r.status] = r.count; return a; }, {});

  const byCategory = db.prepare(
    "SELECT category, COUNT(*) as count FROM project_requests WHERE status NOT IN ('converted','rejected') GROUP BY category"
  ).all().reduce((a, r) => { a[r.category] = r.count; return a; }, {});

  const pending = db.prepare(
    "SELECT COUNT(*) as count FROM project_requests WHERE status IN ('pending','triaging')"
  ).get().count;

  res.json({ byStatus, byCategory, pending });
});

wrapRouter(router);
export default router;
