-- Migration 004: Library System
-- A curated document store with collections, tags, versions, and search.

-- ============================================================
-- COLLECTIONS (folders / categories for organizing docs)
-- ============================================================
-- Hierarchical: a collection can have a parent_id for nesting.
-- Examples: "Research", "Research > Competitors", "Reports > Weekly",
--           "API Docs", "Templates", "Meeting Notes"
CREATE TABLE IF NOT EXISTS collections (
  id            TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
  name          TEXT NOT NULL,
  slug          TEXT NOT NULL UNIQUE,           -- url-safe name
  description   TEXT DEFAULT '',
  icon          TEXT DEFAULT '📁',              -- emoji or icon identifier
  color         TEXT DEFAULT '#6366f1',
  parent_id     TEXT REFERENCES collections(id) ON DELETE SET NULL,
  sort_order    INTEGER DEFAULT 0,
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_collections_parent ON collections(parent_id);
CREATE INDEX IF NOT EXISTS idx_collections_slug ON collections(slug);

-- Seed some default collections
INSERT OR IGNORE INTO collections (id, name, slug, icon, color, sort_order) VALUES
  ('col_research',  'Research',       'research',       '🔬', '#3b82f6', 0),
  ('col_reports',   'Reports',        'reports',        '📊', '#10b981', 1),
  ('col_docs',      'Documentation',  'documentation',  '📖', '#a855f7', 2),
  ('col_reference', 'Reference',      'reference',      '📚', '#f59e0b', 3),
  ('col_templates', 'Templates',      'templates',      '📋', '#6366f1', 4),
  ('col_notes',     'Notes',          'notes',          '📝', '#64748b', 5);

-- ============================================================
-- DOCUMENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS documents (
  id            TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(8)))),
  title         TEXT NOT NULL,
  slug          TEXT NOT NULL,                  -- url-safe title
  -- Classification
  doc_type      TEXT NOT NULL DEFAULT 'document'
                CHECK (doc_type IN ('research','report','documentation','reference',
                                     'template','note','analysis','brief','guide','other')),
  format        TEXT NOT NULL DEFAULT 'markdown'
                CHECK (format IN ('markdown','html','code','json','text','csv')),
  collection_id TEXT REFERENCES collections(id) ON DELETE SET NULL,
  -- Content
  content       TEXT NOT NULL DEFAULT '',       -- the actual document body
  excerpt       TEXT DEFAULT '',                -- first ~200 chars or manual summary
  word_count    INTEGER DEFAULT 0,
  -- Provenance
  author_agent  TEXT,                           -- which agent created this
  project_id    TEXT REFERENCES projects(id) ON DELETE SET NULL,
  task_id       TEXT REFERENCES tasks(id) ON DELETE SET NULL,
  source_path   TEXT,                           -- original workspace file path if any
  -- Status
  status        TEXT NOT NULL DEFAULT 'published'
                CHECK (status IN ('draft','published','archived')),
  pinned        INTEGER DEFAULT 0,             -- 1 = pinned to top
  -- Versioning
  version       INTEGER NOT NULL DEFAULT 1,
  -- Timestamps
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT NOT NULL DEFAULT (datetime('now')),
  published_at  TEXT
);

CREATE INDEX IF NOT EXISTS idx_docs_collection ON documents(collection_id);
CREATE INDEX IF NOT EXISTS idx_docs_type ON documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_docs_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_docs_project ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_docs_agent ON documents(author_agent);
CREATE INDEX IF NOT EXISTS idx_docs_slug ON documents(slug);

-- ============================================================
-- DOCUMENT TAGS (many-to-many)
-- ============================================================
CREATE TABLE IF NOT EXISTS doc_tags (
  doc_id  TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  tag_id  TEXT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (doc_id, tag_id)
);

-- ============================================================
-- DOCUMENT VERSIONS (full history of edits)
-- ============================================================
CREATE TABLE IF NOT EXISTS document_versions (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  doc_id        TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  version       INTEGER NOT NULL,
  content       TEXT NOT NULL,
  change_note   TEXT DEFAULT '',
  changed_by    TEXT DEFAULT 'system',         -- agent id or 'user'
  created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_doc_versions_doc ON document_versions(doc_id);

-- ============================================================
-- FULL-TEXT SEARCH (SQLite FTS5)
-- ============================================================
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
  title, content, excerpt, doc_type,
  content='documents',
  content_rowid='rowid'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS docs_fts_insert AFTER INSERT ON documents BEGIN
  INSERT INTO documents_fts(rowid, title, content, excerpt, doc_type)
  VALUES (new.rowid, new.title, new.content, new.excerpt, new.doc_type);
END;

CREATE TRIGGER IF NOT EXISTS docs_fts_delete BEFORE DELETE ON documents BEGIN
  INSERT INTO documents_fts(documents_fts, rowid, title, content, excerpt, doc_type)
  VALUES ('delete', old.rowid, old.title, old.content, old.excerpt, old.doc_type);
END;

CREATE TRIGGER IF NOT EXISTS docs_fts_update AFTER UPDATE ON documents BEGIN
  INSERT INTO documents_fts(documents_fts, rowid, title, content, excerpt, doc_type)
  VALUES ('delete', old.rowid, old.title, old.content, old.excerpt, old.doc_type);
  INSERT INTO documents_fts(rowid, title, content, excerpt, doc_type)
  VALUES (new.rowid, new.title, new.content, new.excerpt, new.doc_type);
END;
