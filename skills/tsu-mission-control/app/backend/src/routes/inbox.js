import { Router } from "express";
import { getDb } from "../db.js";
import { wrapRouter } from "../middleware.js";

const router = Router();

// ── UNIFIED INBOX ─────────────────────────────────────
// Merges pending requests, reviews, and approvals into one
// priority-sorted queue. Each item gets a normalized shape:
//   { inbox_type, id, title, subtitle, description, urgency,
//     submitted_by, status, entity_type, entity_id, created_at, ...extras }

router.get("/", (req, res) => {
  const db = getDb();
  const { type, status } = req.query;
  const filterStatus = status || "pending";

  const items = [];

  // ── Requests ────────────────────────────────────
  if (!type || type === "request") {
    const reqStatuses = filterStatus === "pending" ? ["pending", "triaging"]
      : filterStatus === "decided" ? ["approved", "rejected", "deferred", "converted"]
      : filterStatus === "all" ? null
      : [filterStatus];

    let sql = "SELECT * FROM project_requests";
    const params = [];
    if (reqStatuses) {
      sql += ` WHERE status IN (${reqStatuses.map(() => "?").join(",")})`;
      params.push(...reqStatuses);
    }
    sql += " ORDER BY created_at DESC";

    const reqs = db.prepare(sql).all(...params);
    for (const r of reqs) {
      items.push({
        inbox_type: "request",
        id: r.id,
        title: r.title,
        subtitle: r.category,
        description: r.description,
        urgency: r.urgency === "critical" ? "critical" : r.urgency === "urgent" ? "urgent" : r.urgency === "low" || r.urgency === "wishlist" ? "low" : "normal",
        submitted_by: r.requester,
        status: r.status === "pending" || r.status === "triaging" ? "pending" : r.status,
        raw_status: r.status,
        created_at: r.created_at,
        decided_notes: r.review_notes,
        decided_by: r.reviewer,
        // Extras for request-specific actions
        category: r.category,
        source_channel: r.source_channel,
        converted_project_id: r.converted_project_id,
      });
    }
  }

  // ── Reviews ─────────────────────────────────────
  if (!type || type === "review") {
    const revStatuses = filterStatus === "pending" ? ["pending", "in_review"]
      : filterStatus === "decided" ? ["approved", "changes_requested", "rejected"]
      : filterStatus === "all" ? null
      : [filterStatus];

    let sql = `SELECT r.*, t.title as task_title, t.priority as task_priority,
               t.assigned_agent, p.name as project_name
               FROM reviews r
               LEFT JOIN tasks t ON t.id = r.task_id
               LEFT JOIN projects p ON p.id = r.project_id`;
    const params = [];
    if (revStatuses) {
      sql += ` WHERE r.status IN (${revStatuses.map(() => "?").join(",")})`;
      params.push(...revStatuses);
    }
    sql += " ORDER BY r.submitted_at DESC";

    const revs = db.prepare(sql).all(...params);
    for (const r of revs) {
      const deliverables = JSON.parse(r.deliverables || "[]");
      items.push({
        inbox_type: "review",
        id: r.id,
        title: r.task_title || "Untitled task",
        subtitle: r.project_name ? `${r.project_name} · Round ${r.round}` : `Round ${r.round}`,
        description: r.work_summary,
        urgency: r.task_priority === "critical" ? "critical" : r.task_priority === "high" ? "urgent" : "normal",
        submitted_by: r.submitted_by || r.assigned_agent,
        status: r.status === "pending" || r.status === "in_review" ? "pending" : r.status === "changes_requested" ? "changes_requested" : r.status,
        raw_status: r.status,
        created_at: r.submitted_at || r.created_at,
        decided_notes: r.decision_notes,
        decided_by: r.reviewer,
        // Review-specific extras
        task_id: r.task_id,
        project_id: r.project_id,
        round: r.round,
        quality_score: r.quality_score,
        deliverable_count: deliverables.length,
        checklist: r.checklist,
        deliverables: r.deliverables,
        work_summary: r.work_summary,
        task_priority: r.task_priority,
        task_description: r.task_description,
        project_name: r.project_name,
        assigned_agent: r.assigned_agent,
      });
    }
  }

  // ── Approvals ───────────────────────────────────
  if (!type || type === "approval") {
    const aprStatuses = filterStatus === "pending" ? ["pending"]
      : filterStatus === "decided" ? ["approved", "rejected", "expired", "cancelled"]
      : filterStatus === "all" ? null
      : [filterStatus];

    let sql = "SELECT * FROM approvals";
    const params = [];
    if (aprStatuses) {
      sql += ` WHERE status IN (${aprStatuses.map(() => "?").join(",")})`;
      params.push(...aprStatuses);
    }
    sql += " ORDER BY created_at DESC";

    const aprs = db.prepare(sql).all(...params);
    for (const a of aprs) {
      // Hydrate entity
      let entityName = "";
      if (a.entity_type === "task" && a.entity_id) {
        const t = db.prepare("SELECT title FROM tasks WHERE id = ?").get(a.entity_id);
        entityName = t?.title || "";
      }

      items.push({
        inbox_type: "approval",
        id: a.id,
        title: a.title,
        subtitle: a.type.replace(/_/g, " "),
        description: a.description,
        urgency: a.urgency,
        submitted_by: a.requested_by,
        status: a.status,
        raw_status: a.status,
        created_at: a.created_at,
        decided_notes: a.decision_notes,
        decided_by: a.decided_by,
        decided_at: a.decided_at,
        // Approval-specific extras
        approval_type: a.type,
        entity_type: a.entity_type,
        entity_id: a.entity_id,
        entity_name: entityName,
        resume_token: a.resume_token,
      });
    }
  }

  // ── Sort by urgency then date ───────────────────
  const urgencyOrder = { critical: 0, urgent: 1, normal: 2, low: 3 };
  items.sort((a, b) => {
    // Pending first
    const aPending = a.status === "pending" ? 0 : 1;
    const bPending = b.status === "pending" ? 0 : 1;
    if (aPending !== bPending) return aPending - bPending;
    // Then by urgency
    const au = urgencyOrder[a.urgency] ?? 2;
    const bu = urgencyOrder[b.urgency] ?? 2;
    if (au !== bu) return au - bu;
    // Then newest first
    return b.created_at.localeCompare(a.created_at);
  });

  res.json(items);
});

// ── COUNTS (for sidebar badge) ────────────────────────
router.get("/counts", (req, res) => {
  const db = getDb();
  const requests = db.prepare("SELECT COUNT(*) as c FROM project_requests WHERE status IN ('pending','triaging')").get().c;
  const reviews = db.prepare("SELECT COUNT(*) as c FROM reviews WHERE status IN ('pending','in_review')").get().c;
  const approvals = db.prepare("SELECT COUNT(*) as c FROM approvals WHERE status = 'pending'").get().c;
  res.json({ requests, reviews, approvals, total: requests + reviews + approvals });
});

wrapRouter(router);
export default router;
