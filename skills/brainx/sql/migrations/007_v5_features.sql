-- BrainX V5 Features Migration
-- Advisory System, EIDOS Loop, Auto-Distillation
-- Idempotent: safe to run multiple times

-- ═══════════════════════════════════════════════════════
-- Feature 1: Advisory System
-- ═══════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS brainx_advisories (
  id TEXT PRIMARY KEY,
  agent TEXT,
  tool TEXT,
  action_context JSONB,
  advisory_text TEXT NOT NULL,
  source_memory_ids TEXT[],
  confidence REAL DEFAULT 0.5,
  was_followed BOOLEAN,
  outcome TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_advisories_agent_tool ON brainx_advisories (agent, tool, created_at DESC);

-- ═══════════════════════════════════════════════════════
-- Feature 2: EIDOS Loop
-- ═══════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS brainx_eidos_cycles (
  id TEXT PRIMARY KEY,
  agent TEXT,
  tool TEXT,
  project TEXT,
  context JSONB,
  prediction TEXT NOT NULL,
  predicted_outcome TEXT,
  actual_outcome TEXT,
  accuracy REAL,
  evaluation_notes TEXT,
  learning_memory_id TEXT REFERENCES brainx_memories(id),
  status TEXT DEFAULT 'predicted' CHECK (status IN ('predicted', 'evaluated', 'distilled')),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  evaluated_at TIMESTAMPTZ,
  distilled_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_eidos_agent ON brainx_eidos_cycles (agent, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_eidos_status ON brainx_eidos_cycles (status, created_at DESC);

-- ═══════════════════════════════════════════════════════
-- Feature 3: Auto-Distillation Log
-- ═══════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS brainx_distillation_log (
  id TEXT PRIMARY KEY,
  session_file TEXT NOT NULL UNIQUE,
  memories_created INTEGER DEFAULT 0,
  memories_skipped INTEGER DEFAULT 0,
  processed_at TIMESTAMPTZ DEFAULT NOW()
);
