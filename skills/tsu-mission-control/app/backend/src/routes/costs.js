import { Router } from "express";
import { getDb } from "../db.js";
import { broadcast } from "../services/events.js";
import { wrapRouter } from "../middleware.js";

const router = Router();

// ── RECORD COST ENTRY (called by hook) ────────────────
router.post("/", (req, res) => {
  const db = getDb();
  const {
    agent_id, task_id, project_id, session_key, model, provider,
    input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
    input_cost_usd, output_cost_usd, cache_cost_usd, total_cost_usd,
    duration_ms
  } = req.body;

  if (!agent_id) return res.status(400).json({ error: "agent_id is required" });

  // Auto-resolve project_id from task if not provided
  let resolvedProjectId = project_id;
  if (!resolvedProjectId && task_id) {
    const task = db.prepare("SELECT project_id FROM tasks WHERE id = ?").get(task_id);
    resolvedProjectId = task?.project_id || null;
  }

  const stmt = db.prepare(`
    INSERT INTO cost_entries (agent_id, task_id, project_id, session_key, model, provider,
      input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
      input_cost_usd, output_cost_usd, cache_cost_usd, total_cost_usd, duration_ms)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(
    agent_id, task_id || null, resolvedProjectId || null, session_key || null,
    model || "unknown", provider || "",
    input_tokens || 0, output_tokens || 0, cache_read_tokens || 0, cache_write_tokens || 0,
    input_cost_usd || 0, output_cost_usd || 0, cache_cost_usd || 0, total_cost_usd || 0,
    duration_ms || null
  );

  // Update daily aggregate
  const date = new Date().toISOString().slice(0, 10);
  db.prepare(`
    INSERT INTO cost_daily (date, agent_id, model, project_id, total_input, total_output, total_cache, total_cost_usd, run_count)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
    ON CONFLICT(date, agent_id, model, project_id)
    DO UPDATE SET
      total_input = total_input + excluded.total_input,
      total_output = total_output + excluded.total_output,
      total_cache = total_cache + excluded.total_cache,
      total_cost_usd = total_cost_usd + excluded.total_cost_usd,
      run_count = run_count + 1
  `).run(date, agent_id, model || "unknown", resolvedProjectId || "",
    input_tokens || 0, output_tokens || 0, (cache_read_tokens || 0) + (cache_write_tokens || 0),
    total_cost_usd || 0);

  broadcast("cost:recorded", { agent_id, model, total_cost_usd, task_id });
  res.status(201).json({ ok: true });
});

// ── DASHBOARD SUMMARY ─────────────────────────────────
router.get("/summary", (req, res) => {
  const db = getDb();
  const { days } = req.query;
  const lookback = parseInt(days) || 30;

  // Total spend
  const total = db.prepare(`
    SELECT COALESCE(SUM(total_cost_usd), 0) as total_cost,
           COALESCE(SUM(input_tokens), 0) as total_input,
           COALESCE(SUM(output_tokens), 0) as total_output,
           COUNT(*) as run_count
    FROM cost_entries
    WHERE created_at >= datetime('now', ?)
  `).get(`-${lookback} days`);

  // Today's spend
  const today = db.prepare(`
    SELECT COALESCE(SUM(total_cost_usd), 0) as cost,
           COUNT(*) as runs
    FROM cost_entries WHERE date(created_at) = date('now')
  `).get();

  // By agent
  const byAgent = db.prepare(`
    SELECT agent_id, SUM(total_cost_usd) as cost, SUM(input_tokens + output_tokens) as tokens, COUNT(*) as runs
    FROM cost_entries WHERE created_at >= datetime('now', ?)
    GROUP BY agent_id ORDER BY cost DESC
  `).all(`-${lookback} days`);

  // By model
  const byModel = db.prepare(`
    SELECT model, SUM(total_cost_usd) as cost, SUM(input_tokens + output_tokens) as tokens, COUNT(*) as runs
    FROM cost_entries WHERE created_at >= datetime('now', ?)
    GROUP BY model ORDER BY cost DESC
  `).all(`-${lookback} days`);

  // By project
  const byProject = db.prepare(`
    SELECT c.project_id, p.name as project_name,
           SUM(c.total_cost_usd) as cost, COUNT(*) as runs
    FROM cost_entries c
    LEFT JOIN projects p ON p.id = c.project_id
    WHERE c.created_at >= datetime('now', ?) AND c.project_id IS NOT NULL
    GROUP BY c.project_id ORDER BY cost DESC
  `).all(`-${lookback} days`);

  // Daily trend (last N days)
  const daily = db.prepare(`
    SELECT date, SUM(total_cost_usd) as cost, SUM(run_count) as runs
    FROM cost_daily
    WHERE date >= date('now', ?)
    GROUP BY date ORDER BY date
  `).all(`-${lookback} days`);

  // Most expensive tasks
  const topTasks = db.prepare(`
    SELECT c.task_id, t.title, SUM(c.total_cost_usd) as cost,
           SUM(c.input_tokens + c.output_tokens) as tokens
    FROM cost_entries c
    JOIN tasks t ON t.id = c.task_id
    WHERE c.created_at >= datetime('now', ?)
    GROUP BY c.task_id ORDER BY cost DESC LIMIT 10
  `).all(`-${lookback} days`);

  res.json({
    period_days: lookback,
    total,
    today,
    byAgent,
    byModel,
    byProject,
    daily,
    topTasks,
  });
});

// ── RAW ENTRIES (for detail drill-down) ───────────────
router.get("/entries", (req, res) => {
  const db = getDb();
  const { agent_id, task_id, project_id, model, limit } = req.query;

  let sql = "SELECT * FROM cost_entries WHERE 1=1";
  const params = [];
  if (agent_id)   { sql += " AND agent_id = ?";   params.push(agent_id); }
  if (task_id)    { sql += " AND task_id = ?";     params.push(task_id); }
  if (project_id) { sql += " AND project_id = ?";  params.push(project_id); }
  if (model)      { sql += " AND model = ?";       params.push(model); }
  sql += " ORDER BY created_at DESC LIMIT ?";
  params.push(parseInt(limit) || 100);

  res.json(db.prepare(sql).all(...params));
});

wrapRouter(router);
export default router;
