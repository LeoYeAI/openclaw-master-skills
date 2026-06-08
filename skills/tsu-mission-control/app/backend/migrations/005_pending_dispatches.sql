-- ============================================================
-- PENDING DISPATCHES — outbound event queue for agent polling
-- ============================================================
-- Events dispatched from Mission Control to agents are queued here
-- as a guaranteed delivery floor. If HTTP/WS delivery succeeds,
-- the record is deleted. If both fail, agents poll this table
-- via GET /api/dispatch/pending/:agentId

CREATE TABLE IF NOT EXISTS pending_dispatches (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_id    TEXT NOT NULL,
  event       TEXT NOT NULL,
  payload     TEXT NOT NULL DEFAULT '{}',
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  delivered   INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_pending_agent ON pending_dispatches(agent_id, delivered);
CREATE INDEX IF NOT EXISTS idx_pending_created ON pending_dispatches(created_at);
