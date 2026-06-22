-- BrainX V5 schema (production-synced)
-- Requires: CREATE EXTENSION vector;

CREATE TABLE IF NOT EXISTS brainx_memories (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL CHECK (type IN ('decision', 'action', 'learning', 'gotcha', 'note', 'feature_request', 'fact')),
  content TEXT NOT NULL,
  context TEXT,
  tier TEXT DEFAULT 'warm' CHECK (tier IN ('hot', 'warm', 'cold', 'archive')),
  agent TEXT,
  importance INTEGER DEFAULT 5 CHECK (importance BETWEEN 1 AND 10),
  embedding vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  last_accessed TIMESTAMPTZ DEFAULT NOW(),
  access_count INTEGER DEFAULT 0,
  source_session TEXT,
  superseded_by TEXT REFERENCES brainx_memories(id),
  tags TEXT[] DEFAULT '{}',
  status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'resolved', 'promoted', 'wont_fix')),
  category TEXT CHECK (category IN (
    'learning', 'error', 'feature_request', 'correction', 'knowledge_gap', 'best_practice',
    'infrastructure', 'project_registry', 'personal', 'financial', 'contact', 'preference',
    'goal', 'relationship', 'health', 'business', 'client', 'deadline', 'routine', 'context'
  )),
  pattern_key TEXT,
  recurrence_count INTEGER DEFAULT 1 CHECK (recurrence_count >= 1),
  first_seen TIMESTAMPTZ DEFAULT NOW(),
  last_seen TIMESTAMPTZ DEFAULT NOW(),
  resolved_at TIMESTAMPTZ,
  promoted_to TEXT,
  resolution_notes TEXT
);

-- V4 lifecycle/pattern fields (idempotent for existing V3 installs)
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
    SELECT 1 FROM pg_constraint
    WHERE conname = 'brainx_memories_status_check'
  ) THEN
    ALTER TABLE brainx_memories
      ADD CONSTRAINT brainx_memories_status_check
      CHECK (status IN ('pending', 'in_progress', 'resolved', 'promoted', 'wont_fix'));
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'brainx_memories_category_check'
  ) THEN
    ALTER TABLE brainx_memories
      ADD CONSTRAINT brainx_memories_category_check
      CHECK (category IS NULL OR category IN (
        'learning', 'error', 'feature_request', 'correction', 'knowledge_gap', 'best_practice',
        'infrastructure', 'project_registry', 'personal', 'financial', 'contact', 'preference',
        'goal', 'relationship', 'health', 'business', 'client', 'deadline', 'routine', 'context'
      ));
  END IF;
EXCEPTION WHEN duplicate_object THEN
  NULL;
END $$;

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

CREATE TABLE IF NOT EXISTS brainx_learning_details (
  memory_id TEXT PRIMARY KEY REFERENCES brainx_memories(id),
  category TEXT,
  what_was_wrong TEXT,
  what_is_correct TEXT,
  source TEXT,
  error_message TEXT,
  command_attempted TEXT,
  stack_trace TEXT,
  reproducible TEXT CHECK (reproducible IN ('yes', 'no', 'unknown')),
  suggested_fix TEXT,
  environment TEXT,
  related_files TEXT[],
  requested_capability TEXT,
  user_context TEXT,
  complexity TEXT CHECK (complexity IN ('simple', 'medium', 'complex')),
  suggested_implementation TEXT,
  frequency TEXT CHECK (frequency IN ('first_time', 'recurring')),
  promotion_status TEXT DEFAULT 'pending',
  promoted_to TEXT,
  promoted_at TIMESTAMPTZ,
  see_also TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS brainx_trajectories (
  id TEXT PRIMARY KEY,
  context TEXT,
  problem TEXT NOT NULL,
  steps JSONB,
  solution TEXT,
  outcome TEXT CHECK (outcome IN ('success', 'partial', 'failed')),
  agent TEXT,
  embedding vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  times_used INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS brainx_context_packs (
  id TEXT PRIMARY KEY,
  data JSONB NOT NULL,
  embedding vector(1536),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS brainx_session_snapshots (
  id TEXT PRIMARY KEY,
  project TEXT NOT NULL,
  agent TEXT,
  summary TEXT NOT NULL,
  status TEXT CHECK (status IN ('in_progress', 'completed', 'blocked', 'paused')),
  pending_items JSONB DEFAULT '[]',
  blockers JSONB DEFAULT '[]',
  last_file_touched TEXT,
  last_error TEXT,
  key_urls JSONB DEFAULT '[]',
  embedding vector(1536),
  session_start TIMESTAMPTZ,
  session_end TIMESTAMPTZ DEFAULT NOW(),
  turn_count INTEGER
);

CREATE TABLE IF NOT EXISTS brainx_pilot_log (
  id SERIAL PRIMARY KEY,
  agent VARCHAR(50),
  own_memories INTEGER DEFAULT 0,
  team_memories INTEGER DEFAULT 0,
  total_chars INTEGER DEFAULT 0,
  injected_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_mem_embedding ON brainx_memories USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX IF NOT EXISTS idx_mem_tier ON brainx_memories (tier, importance DESC);
CREATE INDEX IF NOT EXISTS idx_mem_context ON brainx_memories (context);
CREATE INDEX IF NOT EXISTS idx_mem_tags ON brainx_memories USING gin (tags);
CREATE INDEX IF NOT EXISTS idx_mem_status ON brainx_memories (status, last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_mem_category ON brainx_memories (category);
CREATE INDEX IF NOT EXISTS idx_mem_pattern_key ON brainx_memories (pattern_key);
CREATE INDEX IF NOT EXISTS idx_mem_pattern_recurrence ON brainx_memories (recurrence_count DESC, last_seen DESC);

CREATE INDEX IF NOT EXISTS idx_traj_embedding ON brainx_trajectories USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
CREATE INDEX IF NOT EXISTS idx_pack_embedding ON brainx_context_packs USING ivfflat (embedding vector_cosine_ops) WITH (lists = 5);

CREATE INDEX IF NOT EXISTS idx_snapshots_project ON brainx_session_snapshots (project, session_end DESC);
CREATE INDEX IF NOT EXISTS idx_snapshots_embedding ON brainx_session_snapshots USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
CREATE INDEX IF NOT EXISTS idx_patterns_last_seen ON brainx_patterns (last_seen DESC);
CREATE INDEX IF NOT EXISTS idx_patterns_recurrence ON brainx_patterns (recurrence_count DESC, impact_score DESC);
CREATE INDEX IF NOT EXISTS idx_query_log_created ON brainx_query_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_query_log_kind_created ON brainx_query_log (query_kind, created_at DESC);

-- Schema version tracking
CREATE TABLE IF NOT EXISTS brainx_schema_version (
  version INTEGER PRIMARY KEY,
  description TEXT,
  applied_at TIMESTAMPTZ DEFAULT NOW()
);
INSERT INTO brainx_schema_version (version, description) VALUES (5, 'V5: HNSW index, advisory, eidos, distillation, quality gate')
ON CONFLICT (version) DO NOTHING;
