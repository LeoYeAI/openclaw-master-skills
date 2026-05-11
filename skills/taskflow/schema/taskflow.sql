-- TaskFlow SQLite Schema
-- All statements use IF NOT EXISTS so this file is safe to re-run (idempotent).
-- Generated: 2026-02-20
-- Node requirement: >=22.5 (node:sqlite / DatabaseSync)

-- ---------------------------------------------------------------------------
-- PRAGMA tweaks (run once at connection time, not schema objects)
-- ---------------------------------------------------------------------------
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- projects
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS projects (
  id          TEXT PRIMARY KEY,                       -- slug, e.g. "dashboard"
  name        TEXT NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  status      TEXT NOT NULL DEFAULT 'active'
                CHECK (status IN ('active', 'paused', 'done')),
  source_file TEXT NOT NULL DEFAULT 'PROJECTS.md',
  updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

-- ---------------------------------------------------------------------------
-- tasks_v2
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tasks_v2 (
  id          TEXT PRIMARY KEY,                       -- <slug>-NNN, e.g. "dashboard-001"
  project_id  TEXT NOT NULL,
  title       TEXT NOT NULL,
  status      TEXT NOT NULL
                CHECK (status IN (
                  'backlog',
                  'in_progress',
                  'pending_validation',
                  'done',
                  'blocked'
                )),
  priority    TEXT NOT NULL DEFAULT 'P2'
                CHECK (priority IN ('P0', 'P1', 'P2', 'P3', 'P9')),
  owner_model TEXT,                                   -- agent/model tag (optional)
  notes       TEXT,
  source_file TEXT NOT NULL,
  legacy_key  TEXT,                                   -- for migrations from older systems
  created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  updated_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  FOREIGN KEY (project_id) REFERENCES projects(id)
    ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_tasks_v2_project_status
  ON tasks_v2 (project_id, status, priority);

-- ---------------------------------------------------------------------------
-- task_transitions_v2  (audit log — every status change is recorded here)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS task_transitions_v2 (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id     TEXT NOT NULL,
  from_status TEXT,                                   -- NULL on first insertion
  to_status   TEXT NOT NULL,
  reason      TEXT,
  actor       TEXT,                                   -- 'sync', 'agent', 'human', etc.
  actor_model TEXT,                                   -- which model made the change
  at          TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
  FOREIGN KEY (task_id) REFERENCES tasks_v2(id)
    ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_transitions_task_id
  ON task_transitions_v2 (task_id, at DESC);

CREATE INDEX IF NOT EXISTS idx_transitions_at
  ON task_transitions_v2 (at DESC);

-- ---------------------------------------------------------------------------
-- sync_state  (singleton row — id must be 1)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sync_state (
  id          INTEGER PRIMARY KEY CHECK (id = 1),
  files_hash  TEXT,                                   -- hash of all task file contents
  db_hash     TEXT,                                   -- hash of serialized DB task state
  last_sync_at TEXT,
  lock_owner  TEXT,                                   -- process/session that holds the lock
  lock_until  TEXT,                                   -- TTL-based lock expiry (ISO8601, 60s TTL)
  last_result TEXT                                    -- 'ok' | 'error: ...'
);

-- Ensure the singleton row exists (safe to run multiple times).
INSERT OR IGNORE INTO sync_state (id) VALUES (1);

-- ---------------------------------------------------------------------------
-- legacy_key_map  (migration bridge — maps old task keys to new tasks_v2 ids)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS legacy_key_map (
  legacy_key TEXT PRIMARY KEY,
  new_id     TEXT NOT NULL,
  FOREIGN KEY (new_id) REFERENCES tasks_v2(id)
);

CREATE INDEX IF NOT EXISTS idx_legacy_key_map_new_id
  ON legacy_key_map (new_id);
