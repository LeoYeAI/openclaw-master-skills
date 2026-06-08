import { Router } from "express";
import { getDb } from "../db.js";
import { broadcast } from "../services/events.js";
import { onApprovalGranted, onApprovalDenied } from "../services/dispatcher.js";
import { wrapRouter, validate } from "../middleware.js";

const router = Router();

// ── LIST (default: pending only) ──────────────────────
router.get("/", (req, res) => {
  const db = getDb();
  const { status, type } = req.query;
  const filterStatus = status || "pending";

  let sql = "SELECT * FROM approvals WHERE 1=1";
  const params = [];
  if (filterStatus !== "all") { sql += " AND status = ?"; params.push(filterStatus); }
  if (type) { sql += " AND type = ?"; params.push(type); }
  sql += " ORDER BY CASE urgency WHEN 'critical' THEN 0 WHEN 'urgent' THEN 1 WHEN 'normal' THEN 2 ELSE 3 END, created_at DESC";

  const approvals = db.prepare(sql).all(...params);

  // Hydrate entity info
  for (const a of approvals) {
    if (a.entity_type === "task" && a.entity_id) {
      a.entity = db.prepare("SELECT id, title, pipeline_stage, assigned_agent FROM tasks WHERE id = ?").get(a.entity_id);
    } else if (a.entity_type === "project" && a.entity_id) {
      a.entity = db.prepare("SELECT id, name, status FROM projects WHERE id = ?").get(a.entity_id);
    } else if (a.entity_type === "request" && a.entity_id) {
      a.entity = db.prepare("SELECT id, title, status, urgency FROM project_requests WHERE id = ?").get(a.entity_id);
    }
  }

  res.json(approvals);
});

// ── GET ONE ───────────────────────────────────────────
router.get("/:id", (req, res) => {
  const db = getDb();
  const a = db.prepare("SELECT * FROM approvals WHERE id = ?").get(req.params.id);
  if (!a) return res.status(404).json({ error: "Approval not found" });
  res.json(a);
});

// ── CREATE (typically by hooks/system, but also manual) ─
router.post("/", (req, res) => {
  const db = getDb();
  const { type, entity_type, entity_id, title, description, urgency, requested_by, resume_token, expires_at, context } = req.body;

  if (!type || !title) return res.status(400).json({ error: "type and title are required" });

  const stmt = db.prepare(`
    INSERT INTO approvals (type, entity_type, entity_id, title, description, urgency, requested_by, resume_token, expires_at, context)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  const info = stmt.run(
    type, entity_type || null, entity_id || null,
    title, description || "", urgency || "normal",
    requested_by || "system", resume_token || null,
    expires_at || null, JSON.stringify(context || {})
  );

  const approval = db.prepare("SELECT * FROM approvals WHERE rowid = ?").get(info.lastInsertRowid);

  db.prepare(`
    INSERT INTO activity_log_v2 (entity_type, entity_id, action, new_value, actor, message)
    VALUES ('approval', ?, 'created', 'pending', ?, ?)
  `).run(approval.id, requested_by || "system", `Approval needed: ${title}`);

  broadcast("approval:created", approval);
  res.status(201).json(approval);
});

// ── DECIDE (approve or reject) ────────────────────────
router.post("/:id/decide", (req, res) => {
  const db = getDb();
  const { decision, notes, decided_by } = req.body;
  const approval = db.prepare("SELECT * FROM approvals WHERE id = ?").get(req.params.id);

  if (!approval) return res.status(404).json({ error: "Approval not found" });
  if (approval.status !== "pending") return res.status(422).json({ error: `Already ${approval.status}` });
  if (!["approved", "rejected"].includes(decision)) {
    return res.status(400).json({ error: "Decision must be 'approved' or 'rejected'" });
  }

  db.prepare(`
    UPDATE approvals SET status = ?, decided_by = ?, decision_notes = ?, decided_at = datetime('now')
    WHERE id = ?
  `).run(decision, decided_by || "user", notes || "", req.params.id);

  // Handle side effects based on type
  if (decision === "approved") {
    switch (approval.type) {
      case "task_review": {
        // Move the task to done
        if (approval.entity_id) {
          db.prepare(`
            UPDATE tasks SET pipeline_stage = 'done', status = 'done', completed_at = datetime('now'), updated_at = datetime('now')
            WHERE id = ?
          `).run(approval.entity_id);
          broadcast("task:moved", { taskId: approval.entity_id, from: "review", to: "done" });
        }
        break;
      }
      case "project_approval": {
        // Move project to active
        if (approval.entity_id) {
          db.prepare(`
            UPDATE projects SET status = 'active', updated_at = datetime('now')
            WHERE id = ?
          `).run(approval.entity_id);
          broadcast("project:updated", { id: approval.entity_id, status: "active" });
        }
        break;
      }
      case "request_triage": {
        // Mark request as approved
        if (approval.entity_id) {
          db.prepare(`
            UPDATE project_requests SET status = 'approved', reviewer = ?, updated_at = datetime('now')
            WHERE id = ?
          `).run(decided_by || "user", approval.entity_id);
          broadcast("request:triaged", { id: approval.entity_id, status: "approved" });
        }
        break;
      }
      case "workflow_gate": {
        // The frontend/agent should call the Lobster resume API with the token
        // We just record the decision here
        break;
      }
    }
  } else if (decision === "rejected") {
    switch (approval.type) {
      case "task_review": {
        // Send task back to doing
        if (approval.entity_id) {
          db.prepare(`
            UPDATE tasks SET pipeline_stage = 'doing', status = 'in_progress', updated_at = datetime('now')
            WHERE id = ?
          `).run(approval.entity_id);
          broadcast("task:moved", { taskId: approval.entity_id, from: "review", to: "doing" });
        }
        break;
      }
      case "request_triage": {
        if (approval.entity_id) {
          db.prepare(`
            UPDATE project_requests SET status = 'rejected', reviewer = ?, review_notes = ?, updated_at = datetime('now')
            WHERE id = ?
          `).run(decided_by || "user", notes || "", approval.entity_id);
        }
        break;
      }
    }
  }

  db.prepare(`
    INSERT INTO activity_log_v2 (entity_type, entity_id, action, old_value, new_value, actor, message)
    VALUES ('approval', ?, ?, 'pending', ?, ?, ?)
  `).run(req.params.id, decision, decision, decided_by || "user",
    `${approval.title} → ${decision}${notes ? ": " + notes : ""}`);

  const updated = db.prepare("SELECT * FROM approvals WHERE id = ?").get(req.params.id);
  broadcast(`approval:${decision}`, updated);

  // Dispatch outbound event to agent
  if (decision === "approved") {
    onApprovalGranted(updated);
  } else {
    onApprovalDenied(updated);
  }

  res.json(updated);
});

// ── PENDING COUNT (for badge) ─────────────────────────
router.get("/count/pending", (req, res) => {
  const db = getDb();
  const count = db.prepare("SELECT COUNT(*) as count FROM approvals WHERE status = 'pending'").get().count;
  res.json({ count });
});

wrapRouter(router);
export default router;
