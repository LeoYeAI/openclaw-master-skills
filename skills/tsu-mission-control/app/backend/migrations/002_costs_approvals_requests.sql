-- Migration 002: Cost tracking, Approvals, Project Requests, Stall Detection
-- Run after 001_schema.sql

-- ============================================================
-- PROJECT REQUESTS (intake funnel — before a project exists)
-- ============================================================
-- Anyone (human or agent) can submit a request. It goes through
-- triage → approved → converted-to-project, or rejected.
-- This is the "front door" for new work.
CREATE TABLE IF NOT EXISTS project_requests (
  id            TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
  title         TEXT NOT NULL,
  description   TEXT DEFAULT '',
  requester     TEXT DEFAULT 'user',         -- who submitted: 'user', agent id, channel name
  category      TEXT DEFAULT 'general'
                CHECK (category IN ('feature','bug','research','content','ops','automation','general')),
  urgency       TEXT DEFAULT 'normal'
                CHECK (urgency IN ('critical','urgent','normal','low','wishlist')),
  status        TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','triaging','approved','rejected','converted','deferred')),
  reviewer      TEXT,                         -- who triaged it
  review_notes  TEXT DEFAULT '',
  converted_project_id TEXT REFERENCES projects(id) ON DELETE SET NULL,
  -- Context: where did this come from?
  source_channel TEXT,                        -- 'slack', 'web', 'telegram', 'cli', etc.
  source_ref    TEXT,                         -- message ID, thread URL, etc.
  attachments   TEXT DEFAULT '[]',            -- JSON array of {name, path, type}
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_requests_status ON project_requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_urgency ON project_requests(urgency);

-- ============================================================
-- COST TRACKING
-- ============================================================
-- Every agent session/task run records token usage and cost.
-- Populated by the lifecycle hook on session:ended events.
CREATE TABLE IF NOT EXISTS cost_entries (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  agent_id      TEXT NOT NULL,
  task_id       TEXT REFERENCES tasks(id) ON DELETE SET NULL,
  project_id    TEXT REFERENCES projects(id) ON DELETE SET NULL,
  session_key   TEXT,                         -- openclaw session key
  model         TEXT NOT NULL DEFAULT '',
  provider      TEXT DEFAULT '',              -- 'anthropic', 'openai', 'google', etc.
  -- Token counts
  input_tokens  INTEGER DEFAULT 0,
  output_tokens INTEGER DEFAULT 0,
  cache_read_tokens  INTEGER DEFAULT 0,
  cache_write_tokens INTEGER DEFAULT 0,
  -- Costs in USD (millicents for precision)
  input_cost_usd    REAL DEFAULT 0,
  output_cost_usd   REAL DEFAULT 0,
  cache_cost_usd    REAL DEFAULT 0,
  total_cost_usd    REAL DEFAULT 0,
  -- Timing
  duration_ms   INTEGER,                      -- how long the session/run lasted
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_costs_agent ON cost_entries(agent_id);
CREATE INDEX IF NOT EXISTS idx_costs_task ON cost_entries(task_id);
CREATE INDEX IF NOT EXISTS idx_costs_project ON cost_entries(project_id);
CREATE INDEX IF NOT EXISTS idx_costs_model ON cost_entries(model);
CREATE INDEX IF NOT EXISTS idx_costs_time ON cost_entries(created_at);

-- Daily aggregation view (materialized by the backend periodically)
CREATE TABLE IF NOT EXISTS cost_daily (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  date          TEXT NOT NULL,                -- YYYY-MM-DD
  agent_id      TEXT NOT NULL,
  model         TEXT NOT NULL DEFAULT '',
  project_id    TEXT NOT NULL DEFAULT '',
  total_input   INTEGER DEFAULT 0,
  total_output  INTEGER DEFAULT 0,
  total_cache   INTEGER DEFAULT 0,
  total_cost_usd REAL DEFAULT 0,
  run_count     INTEGER DEFAULT 0,
  UNIQUE (date, agent_id, model, project_id)
);

-- ============================================================
-- APPROVALS
-- ============================================================
-- Anything that needs human sign-off: task completion review,
-- project promotion, Lobster workflow gates, cost thresholds.
CREATE TABLE IF NOT EXISTS approvals (
  id            TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
  type          TEXT NOT NULL
                CHECK (type IN ('task_review','project_approval','workflow_gate',
                                'cost_alert','request_triage','custom')),
  entity_type   TEXT,                         -- 'task', 'project', 'request', 'workflow'
  entity_id     TEXT,                         -- ID of the thing needing approval
  title         TEXT NOT NULL,
  description   TEXT DEFAULT '',
  requested_by  TEXT DEFAULT 'system',        -- agent id or 'system'
  -- Approval state
  status        TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','approved','rejected','expired','cancelled')),
  decided_by    TEXT,                         -- who approved/rejected
  decision_notes TEXT DEFAULT '',
  decided_at    TEXT,
  -- For Lobster workflow gates
  resume_token  TEXT,                         -- token to resume paused workflow
  -- Urgency / expiry
  urgency       TEXT DEFAULT 'normal'
                CHECK (urgency IN ('critical','urgent','normal','low')),
  expires_at    TEXT,                         -- auto-expire if not acted on
  -- Context
  context       TEXT DEFAULT '{}',            -- JSON blob with extra info
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_approvals_status ON approvals(status);
CREATE INDEX IF NOT EXISTS idx_approvals_type ON approvals(type);
CREATE INDEX IF NOT EXISTS idx_approvals_entity ON approvals(entity_type, entity_id);

-- ============================================================
-- STALL DETECTION CONFIG
-- ============================================================
CREATE TABLE IF NOT EXISTS stall_config (
  id            TEXT PRIMARY KEY DEFAULT 'default',
  max_doing_mins     INTEGER DEFAULT 120,     -- task in "doing" with no update
  max_review_mins    INTEGER DEFAULT 480,     -- task in "review" with no decision
  heartbeat_stale_mins INTEGER DEFAULT 60,    -- agent heartbeat older than this = stale
  auto_reassign      INTEGER DEFAULT 0,       -- 1 = auto-move stalled tasks back to todo
  alert_channel      TEXT,                    -- channel to notify on stall
  updated_at         TEXT DEFAULT (datetime('now'))
);

-- Seed default config
INSERT OR IGNORE INTO stall_config (id) VALUES ('default');

-- ============================================================
-- UPDATE activity_log to support new entity types
-- ============================================================
-- SQLite doesn't support ALTER CHECK, so we drop and recreate
-- Actually, we can't drop CHECK constraints in SQLite. Instead,
-- we'll just allow the new types via the application layer and
-- document them. The existing CHECK on entity_type is:
--   CHECK (entity_type IN ('project','task','agent','system'))
-- We need to add: 'request', 'approval', 'cost'
-- Workaround: create a parallel table that accepts all types
CREATE TABLE IF NOT EXISTS activity_log_v2 (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type   TEXT NOT NULL,                -- no CHECK constraint, app validates
  entity_id     TEXT NOT NULL,
  action        TEXT NOT NULL,
  old_value     TEXT,
  new_value     TEXT,
  actor         TEXT DEFAULT 'system',
  message       TEXT DEFAULT '',
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_activity_v2_entity ON activity_log_v2(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_v2_time   ON activity_log_v2(created_at);
