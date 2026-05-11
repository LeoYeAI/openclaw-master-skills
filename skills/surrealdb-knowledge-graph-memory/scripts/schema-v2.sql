-- SurrealDB Knowledge Graph Memory Schema v2.0
-- Adds: Episodes, Working Memory support, Scoping, Outcome Calibration
-- 
-- MIGRATION: Run via Python for idempotent application:
--   python3 scripts/migrate-v2.py
-- 
-- Or manually per statement (DEFINE FIELD errors if exists, which is fine)

-- ============================================
-- NEW TABLE: Episodes (Task Histories)
-- ============================================

DEFINE TABLE episode SCHEMAFULL;
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
DEFINE FIELD metadata ON TABLE episode TYPE option<object>;
DEFINE FIELD session_key ON TABLE episode TYPE option<string>;
DEFINE FIELD agent_id ON TABLE episode TYPE string DEFAULT "main";

DEFINE INDEX episode_embedding_idx ON episode FIELDS embedding MTREE DIMENSION 1536 DIST COSINE;
DEFINE INDEX episode_outcome_idx ON episode FIELDS outcome;
DEFINE INDEX episode_agent_idx ON episode FIELDS agent_id;

-- ============================================
-- NEW TABLE: Working Memory Snapshots (optional DB backup)
-- ============================================

DEFINE TABLE working_memory SCHEMAFULL;
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
DEFINE FIELD metadata ON TABLE working_memory TYPE option<object>;

DEFINE INDEX wm_session_idx ON working_memory FIELDS session_key;
DEFINE INDEX wm_agent_idx ON working_memory FIELDS agent_id;

-- ============================================
-- UPGRADES TO EXISTING TABLES
-- ============================================

-- Add scope fields to facts (for multi-tenant support)
DEFINE FIELD scope ON TABLE fact TYPE string DEFAULT "agent";
DEFINE FIELD client_id ON TABLE fact TYPE option<string>;
DEFINE FIELD agent_id ON TABLE fact TYPE string DEFAULT "main";

-- Add outcome tracking to facts
DEFINE FIELD success_count ON TABLE fact TYPE int DEFAULT 0;
DEFINE FIELD failure_count ON TABLE fact TYPE int DEFAULT 0;
DEFINE FIELD last_outcome ON TABLE fact TYPE option<string>;

-- Indexes for scoped queries
DEFINE INDEX fact_scope_idx ON fact FIELDS scope;
DEFINE INDEX fact_agent_idx ON fact FIELDS agent_id;

-- Add scope to entities
DEFINE FIELD scope ON TABLE entity TYPE string DEFAULT "agent";
DEFINE FIELD client_id ON TABLE entity TYPE option<string>;
DEFINE FIELD agent_id ON TABLE entity TYPE string DEFAULT "main";

-- ============================================
-- FUNCTIONS: Outcome-Based Confidence
-- ============================================

-- Calculate confidence adjustment based on outcome history
DEFINE FUNCTION fn::outcome_adjustment($fact_id: record<fact>) {
  LET $fact = SELECT success_count, failure_count FROM $fact_id;
  LET $successes = $fact[0].success_count OR 0;
  LET $failures = $fact[0].failure_count OR 0;
  LET $total = $successes + $failures;
  
  IF $total = 0 THEN RETURN 0 END;
  
  LET $win_rate = $successes / $total;
  LET $adjustment = ($win_rate - 0.5) * 0.2;
  
  RETURN $adjustment;
};

-- Enhanced effective confidence with outcome calibration
DEFINE FUNCTION fn::effective_confidence_v2($fact_id: record<fact>) {
  LET $fact = SELECT confidence FROM $fact_id;
  LET $base = $fact[0].confidence OR 0;
  
  LET $boost = fn::inherited_boost($fact_id);
  LET $entity = fn::entity_boost($fact_id);
  LET $drain = fn::contradiction_drain($fact_id);
  LET $decay = fn::time_decay($fact_id);
  LET $outcome = fn::outcome_adjustment($fact_id);
  
  LET $effective = $base + $boost + $entity + $outcome - $drain - $decay;
  
  RETURN IF $effective > 1.0 THEN 1.0 
    ELSE IF $effective < 0.0 THEN 0.0 
    ELSE $effective END;
};

-- ============================================
-- FUNCTIONS: Scoped Search
-- ============================================

DEFINE FUNCTION fn::scoped_search($query_embedding: array<float>, $scope: string, $client_id: option<string>, $agent_id: string, $limit: int) {
  SELECT 
    *,
    vector::similarity::cosine(embedding, $query_embedding) AS similarity,
    fn::effective_confidence_v2(id) AS effective_confidence,
    IF scope = 'agent' AND agent_id = $agent_id THEN 
      vector::similarity::cosine(embedding, $query_embedding) * fn::effective_confidence_v2(id) * 1.3
    ELSE IF scope = 'client' AND client_id = $client_id THEN 
      vector::similarity::cosine(embedding, $query_embedding) * fn::effective_confidence_v2(id) * 1.1
    ELSE 
      vector::similarity::cosine(embedding, $query_embedding) * fn::effective_confidence_v2(id)
    END AS weighted_score
  FROM fact
  WHERE archived = false
    AND (scope = 'global' OR client_id = $client_id OR (scope = 'agent' AND agent_id = $agent_id))
  ORDER BY weighted_score DESC
  LIMIT $limit;
};

-- ============================================
-- FUNCTIONS: Episode Search
-- ============================================

DEFINE FUNCTION fn::search_episodes($query_embedding: array<float>, $agent_id: string, $limit: int) {
  SELECT 
    *,
    vector::similarity::cosine(embedding, $query_embedding) AS similarity
  FROM episode
  WHERE embedding IS NOT NONE
    AND agent_id = $agent_id
  ORDER BY similarity DESC
  LIMIT $limit;
};
