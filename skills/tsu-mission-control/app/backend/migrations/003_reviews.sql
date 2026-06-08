-- Migration 003: Review Desk
-- A dedicated review workflow for inspecting agent deliverables before sign-off.

-- ============================================================
-- REVIEWS (one per task submission to review stage)
-- ============================================================
-- Each time a task enters "review", a review record is created.
-- If it bounces back and returns, a new review record is created.
-- This gives you a full history of review rounds per task.
CREATE TABLE IF NOT EXISTS reviews (
  id            TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
  task_id       TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  project_id    TEXT REFERENCES projects(id) ON DELETE SET NULL,
  round         INTEGER NOT NULL DEFAULT 1,    -- review round (1st, 2nd, etc.)
  -- Who submitted and who reviews
  submitted_by  TEXT,                          -- agent id that submitted for review
  reviewer      TEXT,                          -- human or agent who reviewed
  -- Status
  status        TEXT NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','in_review','approved','changes_requested','rejected')),
  -- Quality assessment
  quality_score INTEGER                        -- 1-5 optional rating
                CHECK (quality_score IS NULL OR (quality_score >= 1 AND quality_score <= 5)),
  -- Checklist (JSON array of {label, checked} items)
  checklist     TEXT DEFAULT '[]',
  -- Deliverables the agent produced (JSON array of {name, type, path, summary})
  deliverables  TEXT DEFAULT '[]',
  -- Summary of what the agent did
  work_summary  TEXT DEFAULT '',
  -- Review decision
  decision_notes TEXT DEFAULT '',
  -- Timestamps
  submitted_at  TEXT NOT NULL DEFAULT (datetime('now')),
  reviewed_at   TEXT,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_reviews_task ON reviews(task_id);
CREATE INDEX IF NOT EXISTS idx_reviews_status ON reviews(status);
CREATE INDEX IF NOT EXISTS idx_reviews_project ON reviews(project_id);

-- ============================================================
-- REVIEW COMMENTS (threaded discussion on a review)
-- ============================================================
CREATE TABLE IF NOT EXISTS review_comments (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  review_id     TEXT NOT NULL REFERENCES reviews(id) ON DELETE CASCADE,
  author        TEXT NOT NULL DEFAULT 'user',   -- 'user', agent id, 'system'
  content       TEXT NOT NULL,
  -- Optional: reference to a specific deliverable
  deliverable_ref TEXT,                         -- deliverable name/path this comment is about
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_review_comments_review ON review_comments(review_id);
