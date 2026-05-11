# SurrealQL Query Examples

Quick reference for common knowledge graph queries.

## Basic CRUD

### Create Fact
```surql
CREATE fact CONTENT {
  content: "Charles prefers direct communication",
  embedding: [0.1, 0.2, ...],  -- 1536 dims
  source: "explicit",
  confidence: 0.9,
  tags: ["preference", "communication"]
};
```

### Read Fact
```surql
SELECT * FROM fact:abc123;

-- With effective confidence
SELECT *, fn::effective_confidence(id) AS eff_conf FROM fact:abc123;
```

### Update Fact
```surql
-- Boost confidence on confirmation
UPDATE fact:abc123 SET 
  confidence = math::min(1.0, confidence + 0.1),
  last_confirmed = time::now();

-- Add tag
UPDATE fact:abc123 SET tags += "important";
```

### Delete/Archive
```surql
-- Soft delete (archive)
UPDATE fact:abc123 SET archived = true;

-- Hard delete
DELETE fact:abc123;
```

## Relationships

### Create Support Edge
```surql
RELATE fact:supporter->relates_to->fact:supported SET 
  relationship = "supports",
  strength = 0.8,
  detection_method = "manual";
```

### Create Contradiction Edge
```surql
RELATE fact:new->relates_to->fact:old SET 
  relationship = "contradicts",
  strength = 0.7,
  detection_method = "pattern";
```

### Link Fact to Entity
```surql
RELATE fact:abc->mentions->entity:charles SET 
  role = "subject";
```

## Semantic Search

### Basic Vector Search
```surql
SELECT *,
  vector::similarity::cosine(embedding, $query_vec) AS similarity
FROM fact
WHERE archived = false
ORDER BY similarity DESC
LIMIT 10;
```

### Confidence-Weighted Search
```surql
SELECT *,
  vector::similarity::cosine(embedding, $query_vec) AS similarity,
  fn::effective_confidence(id) AS eff_conf,
  vector::similarity::cosine(embedding, $query_vec) * fn::effective_confidence(id) AS score
FROM fact
WHERE archived = false
  AND vector::similarity::cosine(embedding, $query_vec) > 0.5
ORDER BY score DESC
LIMIT 10;
```

### Search with Tag Filter
```surql
SELECT * FROM fact
WHERE archived = false
  AND "preference" IN tags
  AND vector::similarity::cosine(embedding, $query_vec) > 0.6
ORDER BY vector::similarity::cosine(embedding, $query_vec) DESC;
```

## Graph Traversal

### Get Supporting Facts
```surql
SELECT 
  in.content AS supporter_content,
  in.confidence AS supporter_conf,
  strength
FROM relates_to 
WHERE out = fact:target 
  AND relationship = "supports";
```

### Get Contradicting Facts
```surql
SELECT 
  in.content,
  in.confidence,
  strength,
  detected_at
FROM relates_to 
WHERE out = fact:target 
  AND relationship = "contradicts";
```

### Get All Related Facts (1 hop)
```surql
SELECT 
  <-relates_to<-fact AS supporters,
  ->relates_to->fact AS supported,
  ->mentions->entity AS entities
FROM fact:target;
```

### Find Facts About Entity
```surql
SELECT in.* FROM mentions WHERE out = entity:charles;
```

### Entity Co-occurrence
```surql
-- Find facts that mention both entities
SELECT * FROM fact WHERE 
  ->mentions->entity CONTAINS entity:charles
  AND ->mentions->entity CONTAINS entity:koda;
```

## Maintenance Queries

### Apply Time Decay
```surql
UPDATE fact SET 
  confidence = confidence * 0.95
WHERE last_accessed < time::now() - 30d
  AND archived = false;
```

### Find Pruning Candidates
```surql
SELECT id, content, fn::effective_confidence(id) AS eff_conf
FROM fact
WHERE fn::effective_confidence(id) < 0.3
  AND last_confirmed < time::now() - 30d
  AND archived = false;
```

### Prune Low-Confidence Facts
```surql
DELETE FROM fact 
WHERE fn::effective_confidence(id) < 0.2
  AND last_confirmed < time::now() - 30d;
```

### Find Near-Duplicates
```surql
-- For each fact, find others with >0.95 similarity
SELECT 
  id,
  content,
  (SELECT id, content, vector::similarity::cosine(embedding, $parent.embedding) AS sim
   FROM fact 
   WHERE id != $parent.id 
     AND vector::similarity::cosine(embedding, $parent.embedding) > 0.95
  ) AS duplicates
FROM fact
WHERE archived = false;
```

### Cleanup Orphans
```surql
-- Remove edges pointing to archived facts
DELETE FROM relates_to 
WHERE in.archived = true OR out.archived = true;

-- Remove mentions of archived facts
DELETE FROM mentions WHERE in.archived = true;

-- Remove entities with no mentions (after 30 days)
DELETE FROM entity 
WHERE count(<-mentions) = 0 
  AND created_at < time::now() - 30d;
```

## Statistics

### Basic Counts
```surql
SELECT 
  (SELECT count() FROM fact WHERE archived = false)[0].count AS facts,
  (SELECT count() FROM entity)[0].count AS entities,
  (SELECT count() FROM relates_to)[0].count AS relationships;
```

### Confidence Distribution
```surql
SELECT 
  count() AS total,
  math::mean(confidence) AS avg_conf,
  math::min(confidence) AS min_conf,
  math::max(confidence) AS max_conf
FROM fact
WHERE archived = false
GROUP ALL;
```

### Most Connected Entities
```surql
SELECT 
  name,
  type,
  count(<-mentions) AS mention_count
FROM entity
ORDER BY mention_count DESC
LIMIT 10;
```

### Facts by Source
```surql
SELECT source, count() AS count
FROM fact
WHERE archived = false
GROUP BY source;
```
