-- SurrealDB Knowledge Graph Memory Schema v2.0 - Additive Migration
-- Only adds NEW tables and indexes; modifies existing fields safely
-- Run with: surreal import --conn http://localhost:8000 --ns openclaw --db memory schema-v2-additive.surql

-- ============================================
-- NEW TABLE: Episodes (Task Histories)
-- ============================================

DEFINE TABLE IF NOT EXISTS episode SCHEMAFULL;
DEFINE FIELD task ON TABLE episode TYPE string;
DEFINE FIELD goal ON TABLE episode TYPE string;
DEFINE FIELD started_at ON TABLE episode TYPE option<datetime>;
DEFINE FIELD completed_at ON TABLE episode TYPE option<datetime>;
DEFINE FIELD outcome ON TABLE episode TYPE string DEFAULT "in_progress";
DEFINE FIELD duration_hours ON TABLE episode TYPE option<float>;
DEFINE FIELD steps_taken ON TABLE episode TYPE int DEFAULT 0;
DEFINE FIELD decisions ON TABLE episode TYPE array DEFAULT [];
DEFINE FIELD problems ON TABLE episode TYPE array DEFAULT [];
DEFINE FIELD solutions ON TABLE episode TYPE array DEFAULT [];
DEFINE FIELD key_learnings ON TABLE episode TYPE array DEFAULT [];
DEFINE FIELD facts_used ON TABLE episode TYPE array DEFAULT [];
DEFINE FIELD facts_created ON TABLE episode TYPE array DEFAULT [];
DEFINE FIELD embedding ON TABLE episode TYPE option<array<float>>;
DEFINE FIELD metadata ON TABLE episode TYPE object DEFAULT {};
DEFINE FIELD session_key ON TABLE episode TYPE option<string>;
DEFINE FIELD agent_id ON TABLE episode TYPE string DEFAULT "main";

DEFINE INDEX IF NOT EXISTS episode_embedding_idx ON episode FIELDS embedding MTREE DIMENSION 1536 DIST COSINE;
DEFINE INDEX IF NOT EXISTS episode_outcome_idx ON episode FIELDS outcome;
DEFINE INDEX IF NOT EXISTS episode_agent_idx ON episode FIELDS agent_id;

-- ============================================
-- NEW TABLE: Working Memory Snapshots
-- ============================================

DEFINE TABLE IF NOT EXISTS working_memory SCHEMAFULL;
DEFINE FIELD session_key ON TABLE working_memory TYPE string;
DEFINE FIELD agent_id ON TABLE working_memory TYPE string DEFAULT "main";
DEFINE FIELD goal ON TABLE working_memory TYPE string;
DEFINE FIELD plan ON TABLE working_memory TYPE array DEFAULT [];
DEFINE FIELD decisions_made ON TABLE working_memory TYPE array DEFAULT [];
DEFINE FIELD blocked_on ON TABLE working_memory TYPE option<string>;
DEFINE FIELD confidence ON TABLE working_memory TYPE float DEFAULT 0.5;
DEFINE FIELD iteration ON TABLE working_memory TYPE int DEFAULT 0;
DEFINE FIELD created_at ON TABLE working_memory TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON TABLE working_memory TYPE datetime DEFAULT time::now();
DEFINE FIELD metadata ON TABLE working_memory TYPE object DEFAULT {};

DEFINE INDEX IF NOT EXISTS wm_session_idx ON working_memory FIELDS session_key;
DEFINE INDEX IF NOT EXISTS wm_agent_idx ON working_memory FIELDS agent_id;
