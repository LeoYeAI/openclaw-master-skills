import { Router } from "express";
import { getDb } from "../db.js";
import { wrapRouter } from "../middleware.js";

const router = Router();

/**
 * GET /api/dispatch/pending/:agentId
 *
 * Agents poll this to pick up events that weren't delivered via
 * HTTP/WS. Returns undelivered events, marks them as delivered.
 * This is the guaranteed delivery path — events are always queued
 * here even if push delivery succeeds.
 *
 * Query params:
 *   ?limit=10 — max events to return (default 10)
 *   ?peek=true — return events without marking delivered
 */
router.get("/pending/:agentId", (req, res) => {
  const db = getDb();
  const { agentId } = req.params;
  const limit = parseInt(req.query.limit) || 10;
  const peek = req.query.peek === "true";

  const events = db.prepare(`
    SELECT id, agent_id, event, payload, created_at
    FROM pending_dispatches
    WHERE agent_id = ? AND delivered = 0
    ORDER BY created_at ASC
    LIMIT ?
  `).all(agentId, limit);

  // Parse payload JSON
  const parsed = events.map(e => ({
    ...e,
    payload: (() => { try { return JSON.parse(e.payload); } catch { return e.payload; } })(),
  }));

  // Mark as delivered unless peeking
  if (!peek && events.length > 0) {
    const ids = events.map(e => e.id);
    db.prepare(`UPDATE pending_dispatches SET delivered = 1 WHERE id IN (${ids.map(() => "?").join(",")})`).run(...ids);
  }

  res.json({ events: parsed, count: parsed.length });
});

/**
 * POST /api/dispatch/ack
 *
 * Agent explicitly acknowledges receipt of specific events.
 * Body: { ids: [1, 2, 3] }
 */
router.post("/ack", (req, res) => {
  const db = getDb();
  const { ids } = req.body;
  if (!Array.isArray(ids) || ids.length === 0) {
    return res.status(400).json({ error: "ids array required" });
  }

  db.prepare(`DELETE FROM pending_dispatches WHERE id IN (${ids.map(() => "?").join(",")})`).run(...ids);
  res.json({ ok: true, deleted: ids.length });
});

/**
 * GET /api/dispatch/pending/:agentId/count
 *
 * Quick count check — agents use this to decide whether to poll.
 */
router.get("/pending/:agentId/count", (req, res) => {
  const db = getDb();
  const count = db.prepare("SELECT COUNT(*) as c FROM pending_dispatches WHERE agent_id = ? AND delivered = 0").get(req.params.agentId).c;
  res.json({ count });
});

/**
 * Cleanup: delete old delivered dispatches (older than 24h)
 * Called by the stall detector on its periodic sweep.
 */
export function cleanupDeliveredDispatches() {
  try {
    const db = getDb();
    db.prepare("DELETE FROM pending_dispatches WHERE delivered = 1 AND created_at < datetime('now', '-24 hours')").run();
    db.prepare("DELETE FROM pending_dispatches WHERE created_at < datetime('now', '-72 hours')").run(); // Hard TTL
  } catch (e) {
    console.error("[dispatch] cleanup failed:", e.message);
  }
}

wrapRouter(router);
export default router;
