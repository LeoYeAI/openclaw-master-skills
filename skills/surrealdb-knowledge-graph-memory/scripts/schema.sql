-- SurrealDB Knowledge Graph Memory Schema
-- Version: 1.0.1
-- Note: Uses OVERWRITE to make schema idempotent (safe to re-run)

-- ============================================
-- TABLES
-- ============================================

-- Facts: Individual pieces of knowledge
DEFINE TABLE fact SCHEMAFULL OVERWRITE;
DEFINE FIELD content ON fact TYPE string;
DEFINE FIELD embedding ON fact TYPE array<float>;
DEFINE FIELD source ON fact TYPE string DEFAULT "inferred";  -- explicit, inferred, migrated
DEFINE FIELD confidence ON fact TYPE float DEFAULT 0.6;
DEFINE FIELD created_at ON fact TYPE datetime DEFAULT time::now();
DEFINE FIELD last_confirmed ON fact TYPE datetime DEFAULT time::now();
DEFINE FIELD last_accessed ON fact TYPE datetime DEFAULT time::now();
DEFINE FIELD access_count ON fact TYPE int DEFAULT 0;
DEFINE FIELD tags ON fact TYPE array<string> DEFAULT [];
DEFINE FIELD archived ON fact TYPE bool DEFAULT false;
DEFINE FIELD metadata ON fact TYPE object DEFAULT {};

-- Entities: People, projects, concepts, places
DEFINE TABLE entity SCHEMAFULL OVERWRITE;
DEFINE FIELD name ON entity TYPE string;
DEFINE FIELD type ON entity TYPE string;  -- person, project, concept, place, organization
DEFINE FIELD aliases ON entity TYPE array<string> DEFAULT [];
DEFINE FIELD embedding ON entity TYPE array<float>;
DEFINE FIELD confidence ON entity TYPE float DEFAULT 0.5;
DEFINE FIELD created_at ON entity TYPE datetime DEFAULT time::now();
DEFINE FIELD metadata ON entity TYPE object DEFAULT {};

-- ============================================
-- EDGE TABLES (TYPE RELATION for graph edges)
-- ============================================

-- Relationships between facts
DEFINE TABLE relates_to TYPE RELATION SCHEMAFULL;
DEFINE FIELD relationship ON relates_to TYPE string;  -- supports, contradicts, updates, elaborates
DEFINE FIELD strength ON relates_to TYPE float DEFAULT 0.5;
DEFINE FIELD detected_at ON relates_to TYPE datetime DEFAULT time::now();
DEFINE FIELD detection_method ON relates_to TYPE string DEFAULT "similarity";  -- similarity, negation, llm, manual

-- Facts mention entities
DEFINE TABLE mentions TYPE RELATION SCHEMAFULL;
DEFINE FIELD role ON mentions TYPE string DEFAULT "subject";  -- subject, object, context
DEFINE FIELD created_at ON mentions TYPE datetime DEFAULT time::now();

-- ============================================
-- INDEXES
-- ============================================

-- Vector index for semantic search on facts
DEFINE INDEX fact_embedding_idx ON fact FIELDS embedding MTREE DIMENSION 1536 DIST COSINE;

-- Vector index for entity search
DEFINE INDEX entity_embedding_idx ON entity FIELDS embedding MTREE DIMENSION 1536 DIST COSINE;

-- Fast lookups
DEFINE INDEX fact_source_idx ON fact FIELDS source;
DEFINE INDEX fact_archived_idx ON fact FIELDS archived;
DEFINE INDEX fact_confidence_idx ON fact FIELDS confidence;
DEFINE INDEX entity_type_idx ON entity FIELDS type;
DEFINE INDEX entity_name_idx ON entity FIELDS name;

-- ============================================
-- FUNCTIONS: Confidence Calculations
-- ============================================

-- Inherited boost from supporting high-confidence facts
DEFINE FUNCTION fn::inherited_boost($fact_id: record<fact>) {
  LET $threshold = 0.7;
  LET $transfer_rate = 0.15;
  LET $max_boost = 0.2;
  
  LET $supporters = SELECT in.confidence AS conf, strength 
    FROM relates_to 
    WHERE out = $fact_id 
      AND relationship = "supports"
      AND in.confidence >= $threshold;
  
  LET $total = math::sum((SELECT (conf * strength * $transfer_rate) AS boost FROM $supporters).boost);
  
  RETURN IF $total > $max_boost THEN $max_boost ELSE $total END;
};

-- Confidence drain from contradicting high-confidence facts
DEFINE FUNCTION fn::contradiction_drain($fact_id: record<fact>) {
  LET $threshold = 0.7;
  LET $drain_rate = 0.20;
  
  LET $contradictors = SELECT in.confidence AS conf, strength 
    FROM relates_to 
    WHERE out = $fact_id 
      AND relationship = "contradicts"
      AND in.confidence >= $threshold;
  
  RETURN math::sum((SELECT (conf * strength * $drain_rate) AS drain FROM $contradictors).drain);
};

-- Entity-based boost (mentions well-established entities)
DEFINE FUNCTION fn::entity_boost($fact_id: record<fact>) {
  LET $boost_per_entity = 0.02;
  LET $entity_threshold = 0.8;
  
  LET $strong_entities = SELECT count() AS cnt 
    FROM mentions 
    WHERE in = $fact_id 
      AND out.confidence > $entity_threshold;
  
  RETURN ($strong_entities[0].cnt OR 0) * $boost_per_entity;
};

-- Time decay based on staleness
DEFINE FUNCTION fn::time_decay($fact_id: record<fact>) {
  LET $decay_rate = 0.05;
  LET $fact = SELECT last_confirmed FROM $fact_id;
  LET $days_stale = duration::days(time::now() - $fact[0].last_confirmed);
  LET $months_stale = $days_stale / 30;
  
  RETURN IF $months_stale > 0 THEN $months_stale * $decay_rate ELSE 0 END;
};

-- Final effective confidence
DEFINE FUNCTION fn::effective_confidence($fact_id: record<fact>) {
  LET $fact = SELECT confidence FROM $fact_id;
  LET $base = $fact[0].confidence OR 0;
  
  LET $boost = fn::inherited_boost($fact_id);
  LET $entity = fn::entity_boost($fact_id);
  LET $drain = fn::contradiction_drain($fact_id);
  LET $decay = fn::time_decay($fact_id);
  
  LET $effective = $base + $boost + $entity - $drain - $decay;
  
  RETURN IF $effective > 1.0 THEN 1.0 
    ELSE IF $effective < 0.0 THEN 0.0 
    ELSE $effective END;
};

-- ============================================
-- FUNCTIONS: Search & Retrieval
-- ============================================

-- Search facts with effective confidence weighting
DEFINE FUNCTION fn::search_facts($query_embedding: array<float>, $limit: int) {
  SELECT 
    *,
    vector::similarity::cosine(embedding, $query_embedding) AS similarity,
    fn::effective_confidence(id) AS effective_confidence,
    vector::similarity::cosine(embedding, $query_embedding) * fn::effective_confidence(id) AS weighted_score
  FROM fact
  WHERE archived = false
  ORDER BY weighted_score DESC
  LIMIT $limit;
};

-- Get fact with full context (related facts and entities)
DEFINE FUNCTION fn::get_fact_context($fact_id: record<fact>) {
  LET $fact = SELECT * FROM $fact_id;
  
  LET $supporting = SELECT 
      in.id AS fact_id,
      in.content AS content,
      in.confidence AS confidence,
      strength
    FROM relates_to 
    WHERE out = $fact_id AND relationship = "supports";
  
  LET $contradicting = SELECT 
      in.id AS fact_id,
      in.content AS content,
      in.confidence AS confidence,
      strength
    FROM relates_to 
    WHERE out = $fact_id AND relationship = "contradicts";
  
  LET $entities = SELECT 
      out.id AS entity_id,
      out.name AS name,
      out.type AS type,
      role
    FROM mentions 
    WHERE in = $fact_id;
  
  RETURN {
    fact: $fact[0],
    effective_confidence: fn::effective_confidence($fact_id),
    supporting: $supporting,
    contradicting: $contradicting,
    entities: $entities
  };
};

-- ============================================
-- EVENTS (optional - for real-time updates)
-- ============================================

-- Update last_accessed when fact is queried
DEFINE EVENT fact_accessed ON TABLE fact WHEN $event = "UPDATE" AND $after.access_count > $before.access_count THEN {
  UPDATE $after.id SET last_accessed = time::now();
};
