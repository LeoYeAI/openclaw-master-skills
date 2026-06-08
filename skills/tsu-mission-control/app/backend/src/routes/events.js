import { Router } from "express";
import { getDb } from "../db.js";
import { addListener } from "../services/events.js";
import { wrapRouter } from "../middleware.js";

const router = Router();

// ── ACTIVITY LOG (merged from both tables) ────────────
router.get("/activity", (req, res) => {
  const db = getDb();
  const { entity_type, entity_id, limit, offset } = req.query;
  const lim = parseInt(limit) || 50;
  const off = parseInt(offset) || 0;

  // Pull from both activity_log and activity_log_v2, union and sort
  let sql1 = "SELECT id, entity_type, entity_id, action, old_value, new_value, actor, message, created_at FROM activity_log WHERE 1=1";
  let sql2 = "SELECT id + 1000000 as id, entity_type, entity_id, action, old_value, new_value, actor, message, created_at FROM activity_log_v2 WHERE 1=1";
  const params1 = [], params2 = [];

  if (entity_type) {
    sql1 += " AND entity_type = ?"; params1.push(entity_type);
    sql2 += " AND entity_type = ?"; params2.push(entity_type);
  }
  if (entity_id) {
    sql1 += " AND entity_id = ?"; params1.push(entity_id);
    sql2 += " AND entity_id = ?"; params2.push(entity_id);
  }

  // Fetch slightly more than needed to handle offset across the union
  const fetchLimit = lim + off + 1;
  const rows1 = db.prepare(sql1 + " ORDER BY created_at DESC LIMIT ?").all(...params1, fetchLimit);
  const rows2 = db.prepare(sql2 + " ORDER BY created_at DESC LIMIT ?").all(...params2, fetchLimit);

  const merged = [...rows1, ...rows2]
    .sort((a, b) => b.created_at.localeCompare(a.created_at))
    .slice(off, off + lim);
  res.json(merged);
});

// ── SSE STREAM ────────────────────────────────────────
// Clients connect here to receive real-time updates.
// Every broadcast() call in the backend pushes to all connected SSE clients.
router.get("/stream", (req, res) => {
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
    "Access-Control-Allow-Origin": "*",
  });
  res.write(`event: connected\ndata: ${JSON.stringify({ ts: Date.now() })}\n\n`);

  addListener(res);

  // Keep-alive ping every 30s
  const keepAlive = setInterval(() => {
    res.write(`: keepalive ${Date.now()}\n\n`);
  }, 30000);

  req.on("close", () => clearInterval(keepAlive));
});

// ── DASHBOARD STATS ───────────────────────────────────
router.get("/stats", (req, res) => {
  const db = getDb();

  const projects = db.prepare(`
    SELECT status, COUNT(*) as count FROM projects GROUP BY status
  `).all().reduce((a, r) => { a[r.status] = r.count; return a; }, {});

  const tasks = db.prepare(`
    SELECT pipeline_stage, COUNT(*) as count FROM tasks GROUP BY pipeline_stage
  `).all().reduce((a, r) => { a[r.pipeline_stage] = r.count; return a; }, {});

  const agents = db.prepare(`
    SELECT status, COUNT(*) as count FROM agents GROUP BY status
  `).all().reduce((a, r) => { a[r.status] = r.count; return a; }, {});

  const recentActivity = db.prepare(`
    SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 20
  `).all();

  const tasksByPriority = db.prepare(`
    SELECT priority, COUNT(*) as count FROM tasks
    WHERE status NOT IN ('done','cancelled') GROUP BY priority
  `).all().reduce((a, r) => { a[r.priority] = r.count; return a; }, {});

  const blockedTasks = db.prepare(`
    SELECT * FROM tasks WHERE pipeline_stage = 'blocked' OR status = 'blocked'
  `).all();

  // Stalled tasks (flagged by stall detector)
  const stalledTasks = db.prepare(`
    SELECT * FROM tasks WHERE json_extract(metadata, '$.stall_flagged') = 1 AND pipeline_stage = 'doing'
  `).all();

  // Request & approval counts
  const pendingRequests = db.prepare(
    "SELECT COUNT(*) as c FROM project_requests WHERE status IN ('pending','triaging')"
  ).get().c;

  const pendingApprovals = db.prepare(
    "SELECT COUNT(*) as c FROM approvals WHERE status = 'pending'"
  ).get().c;

  // Today's cost
  const todayCost = db.prepare(
    "SELECT COALESCE(SUM(total_cost_usd), 0) as cost FROM cost_entries WHERE date(created_at) = date('now')"
  ).get().cost;

  res.json({
    projects,
    tasks,
    agents,
    tasksByPriority,
    blockedTasks,
    stalledTasks,
    recentActivity,
    pendingRequests,
    pendingApprovals,
    todayCost,
    totalProjects: Object.values(projects).reduce((s, n) => s + n, 0),
    totalTasks: Object.values(tasks).reduce((s, n) => s + n, 0),
    totalAgents: Object.values(agents).reduce((s, n) => s + n, 0),
  });
});

wrapRouter(router);
export default router;
