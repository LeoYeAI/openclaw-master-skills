-- Mission Control Database Schema
-- This is the source of truth for all project/task state.
-- OpenClaw sessions can reset freely — this persists.

-- ============================================================
-- PROJECTS
-- ============================================================
CREATE TABLE IF NOT EXISTS projects (
  id            TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
  name          TEXT NOT NULL,
  description   TEXT DEFAULT '',
  status        TEXT NOT NULL DEFAULT 'draft'
                CHECK (status IN ('draft','approved','active','paused','completed','archived')),
  priority      TEXT NOT NULL DEFAULT 'medium'
                CHECK (priority IN ('critical','high','medium','low')),
  owner_agent   TEXT,                          -- agent ID responsible
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT NOT NULL DEFAULT (datetime('now')),
  completed_at  TEXT,
  metadata      TEXT DEFAULT '{}'              -- JSON blob for extensibility
);

CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_owner  ON projects(owner_agent);

-- ============================================================
-- TASKS
-- ============================================================
CREATE TABLE IF NOT EXISTS tasks (
  id            TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
  project_id    TEXT REFERENCES projects(id) ON DELETE CASCADE,
  title         TEXT NOT NULL,
  description   TEXT DEFAULT '',
  status        TEXT NOT NULL DEFAULT 'inbox'
                CHECK (status IN ('inbox','assigned','in_progress','review','done','blocked','cancelled')),
  priority      TEXT NOT NULL DEFAULT 'medium'
                CHECK (priority IN ('critical','high','medium','low')),
  assigned_agent TEXT,                         -- which agent is working on it
  pipeline_stage TEXT DEFAULT 'backlog'
                CHECK (pipeline_stage IN ('backlog','todo','doing','review','done')),
  sort_order    INTEGER DEFAULT 0,
  estimated_mins INTEGER,
  actual_mins   INTEGER,
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT NOT NULL DEFAULT (datetime('now')),
  started_at    TEXT,
  completed_at  TEXT,
  metadata      TEXT DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_tasks_project  ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_pipeline ON tasks(pipeline_stage);
CREATE INDEX IF NOT EXISTS idx_tasks_agent    ON tasks(assigned_agent);

-- ============================================================
-- AGENTS (locally tracked state, synced from gateway)
-- ============================================================
CREATE TABLE IF NOT EXISTS agents (
  id            TEXT PRIMARY KEY,              -- matches openclaw agent id
  display_name  TEXT NOT NULL DEFAULT '',
  status        TEXT NOT NULL DEFAULT 'unknown'
                CHECK (status IN ('online','busy','idle','offline','error','unknown')),
  model         TEXT DEFAULT '',
  last_heartbeat TEXT,
  current_task_id TEXT REFERENCES tasks(id) ON DELETE SET NULL,
  session_count INTEGER DEFAULT 0,
  metadata      TEXT DEFAULT '{}'
);

-- ============================================================
-- ACTIVITY LOG (audit trail for every state change)
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_log (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  entity_type   TEXT NOT NULL CHECK (entity_type IN ('project','task','agent','system')),
  entity_id     TEXT NOT NULL,
  action        TEXT NOT NULL,                 -- e.g. 'status_changed', 'assigned', 'created'
  old_value     TEXT,
  new_value     TEXT,
  actor         TEXT DEFAULT 'system',         -- 'user', agent id, or 'system'
  message       TEXT DEFAULT '',
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_activity_entity ON activity_log(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_activity_time   ON activity_log(created_at);

-- ============================================================
-- TAGS
-- ============================================================
CREATE TABLE IF NOT EXISTS tags (
  id    TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(4)))),
  name  TEXT NOT NULL UNIQUE,
  color TEXT DEFAULT '#6366f1'
);

CREATE TABLE IF NOT EXISTS task_tags (
  task_id TEXT REFERENCES tasks(id) ON DELETE CASCADE,
  tag_id  TEXT REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (task_id, tag_id)
);

-- ============================================================
-- SCHEDULED ITEMS (maps to openclaw cron jobs)
-- ============================================================
CREATE TABLE IF NOT EXISTS scheduled_items (
  id            TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
  name          TEXT NOT NULL,
  cron_expr     TEXT,                          -- cron expression
  next_run      TEXT,
  last_run      TEXT,
  status        TEXT DEFAULT 'active' CHECK (status IN ('active','paused','completed')),
  task_id       TEXT REFERENCES tasks(id) ON DELETE SET NULL,
  agent_id      TEXT REFERENCES agents(id) ON DELETE SET NULL,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
