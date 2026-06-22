-- BrainX V5 Phase 2 migration (production-safe, idempotent)
-- Scope: lifecycle governance, pattern/query observability tables, and indexes

-- 1) Extend existing memory table with V4 fields
ALTER TABLE brainx_memories ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending';
ALTER TABLE brainx_memories ADD COLUMN IF NOT EXISTS category TEXT;
ALTER TABLE brainx_memories ADD COLUMN IF NOT EXISTS pattern_key TEXT;
ALTER TABLE brainx_memories ADD COLUMN IF NOT EXISTS recurrence_count INTEGER DEFAULT 1;
ALTER TABLE brainx_memories ADD COLUMN IF NOT EXISTS first_seen TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE brainx_memories ADD COLUMN IF NOT EXISTS last_seen TIMESTAMPTZ DEFAULT NOW();
ALTER TABLE brainx_memories ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMPTZ;
ALTER TABLE brainx_memories ADD COLUMN IF NOT EXISTS promoted_to TEXT;
ALTER TABLE brainx_memories ADD COLUMN IF NOT EXISTS resolution_notes TEXT;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'brainx_memories_status_check'
  ) THEN
    ALTER TABLE brainx_memories
      ADD CONSTRAINT brainx_memories_status_check
      CHECK (status IN ('pending', 'in_progress', 'resolved', 'promoted', 'wont_fix'));
  END IF;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'brainx_memories_category_check'
  ) THEN
    ALTER TABLE brainx_memories
      ADD CONSTRAINT brainx_memories_category_check
      CHECK (category IS NULL OR category IN ('learning', 'error', 'feature_request', 'correction', 'knowledge_gap', 'best_practice'));
  END IF;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- 2) Pattern aggregation table
CREATE TABLE IF NOT EXISTS brainx_patterns (
  pattern_key TEXT PRIMARY KEY,
  recurrence_count INTEGER NOT NULL DEFAULT 1 CHECK (recurrence_count >= 1),
  first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  impact_score REAL DEFAULT 0,
  representative_memory_id TEXT REFERENCES brainx_memories(id),
  last_memory_id TEXT REFERENCES brainx_memories(id),
  last_category TEXT,
  last_status TEXT,
  promoted_to TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3) Query telemetry table (search/inject)
CREATE TABLE IF NOT EXISTS brainx_query_log (
  id BIGSERIAL PRIMARY KEY,
  query_hash TEXT NOT NULL,
  query_kind TEXT NOT NULL CHECK (query_kind IN ('search', 'inject')),
  duration_ms INTEGER,
  results_count INTEGER,
  avg_similarity REAL,
  top_similarity REAL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4) Indexes
CREATE INDEX IF NOT EXISTS idx_mem_status ON brainx_memories (status, last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_mem_category ON brainx_memories (category);
CREATE INDEX IF NOT EXISTS idx_mem_pattern_key ON brainx_memories (pattern_key);
CREATE INDEX IF NOT EXISTS idx_mem_pattern_recurrence ON brainx_memories (recurrence_count DESC, last_seen DESC);

CREATE INDEX IF NOT EXISTS idx_patterns_last_seen ON brainx_patterns (last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_patterns_recurrence ON brainx_patterns (recurrence_count DESC, impact_score DESC);

CREATE INDEX IF NOT EXISTS idx_query_log_created ON brainx_query_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_log_kind_created ON brainx_query_log (query_kind, created_at DESC);
