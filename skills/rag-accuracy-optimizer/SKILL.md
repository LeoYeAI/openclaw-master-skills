---
name: rag-accuracy-optimizer
description: >
  Optimize accuracy for RAG (Retrieval-Augmented Generation) systems.
  Covers: DB schema design, chunking strategies, retrieval optimization,
  accuracy testing, and anti-hallucination safeguards. Use when: (1) designing
  or improving a RAG pipeline, (2) choosing the right chunking strategy, (3) optimizing
  retrieval accuracy (hybrid search, reranking, multi-query), (4) evaluating chunk
  quality or testing accuracy, (5) setting up monitoring & safeguards for RAG
  production, (6) choosing SQL vs Vector DB, (7) designing metadata schemas for
  domain-specific data (insurance, finance, healthcare, e-commerce).
---

# RAG Accuracy Optimizer

A skill for optimizing end-to-end accuracy in RAG systems.

## Workflow Overview

```
Data Design → Chunking → Indexing → Retrieval → Generation → Testing → Monitoring
```

Each step impacts accuracy. Optimize each step in order.

---

## 1. Structured Data Design

### SQL vs Vector DB — When to Use What?

| Criteria | SQL (PostgreSQL, MySQL) | Vector DB (Pinecone, Qdrant, Weaviate) |
|---|---|---|
| Exact facts (price, date, product code) | ✅ Optimal | ❌ Not suitable |
| Semantic search (query meaning) | ❌ Not supported | ✅ Optimal |
| Aggregation (SUM, COUNT, AVG) | ✅ Native | ❌ Not supported |
| Fuzzy matching ("similar to...") | ⚠️ Limited | ✅ Optimal |
| **Hybrid (recommended)** | pgvector for both | Vector DB + SQL metadata store |

**Principle:** Clearly structured data → SQL. Unstructured data requiring semantic understanding → Vector DB. Most production systems need **both**.

### Schema Design Patterns by Domain

**Insurance:**
```
policies(policy_id, product_type, effective_date)
clauses(clause_id, policy_id, clause_number, title, content)
exclusions(exclusion_id, clause_id, description)
-- Vector: embedding for clause.content + exclusion.description
```

**Finance:**
```
securities(ticker, name, sector, exchange)
reports(report_id, ticker, period, report_type)
sections(section_id, report_id, heading, content)
-- Vector: embedding for section.content, metadata: ticker + period
```

**Healthcare:**
```
drugs(drug_id, generic_name, brand_name, category)
guidelines(guideline_id, condition, recommendation, evidence_level)
interactions(drug_a_id, drug_b_id, severity, description)
-- Vector: embedding for guidelines.recommendation
```

**E-commerce:**
```
products(product_id, name, category, brand, price)
reviews(review_id, product_id, rating, content)
specs(product_id, attribute, value)
-- Vector: embedding for review.content + product description
```

### Metadata Tagging Strategy

Each chunk/document needs at minimum:

```python
metadata = {
    "source": "policy_doc_v2.pdf",       # Origin
    "source_type": "pdf",                 # File type
    "domain": "insurance",                # Domain
    "category": "life_insurance",          # Classification
    "entity_id": "POL-2024-001",          # Related entity ID
    "section": "exclusions",              # Section in doc
    "chunk_index": 3,                      # Chunk position
    "total_chunks": 12,                    # Total chunks in doc
    "created_at": "2024-01-15",           # Creation date
    "version": "2.0",                      # Version
    "language": "en"                       # Language
}
```

**Metadata principles:**
- Always include `source` for traceability and citation
- `entity_id` enables pre-filtering before search → reduces noise
- `chunk_index` + `total_chunks` enables fetching surrounding context
- Domain-specific fields (clause_number, ticker, drug_id) vary by use case

### Normalization vs Denormalization

| | Normalized | Denormalized |
|---|---|---|
| Pros | Less duplication, easy to update | Faster queries, fewer JOINs |
| Cons | Requires JOINs, slower | Duplication, harder to sync |
| **Use when** | Source of truth (SQL) | Vector store chunks |

**Recommendation:** Normalized for SQL source → Denormalized when creating chunks for Vector DB. Each chunk should contain sufficient context, no JOINs needed at retrieval time.

---

## 2. Chunking Strategies

> Detailed code examples: read `references/chunking-patterns.md`

### Choosing the Right Strategy

```
Data has clear structure (clauses, sections)?
  → Semantic chunking (by heading/section)

Long, continuous data (articles, transcripts)?
  → Fixed size + overlap (512 tokens, 10-20% overlap)

Need both overview + detail?
  → Hierarchical chunking (parent-child)

Domain-specific with its own logical units?
  → Domain-specific chunking
```

### Chunk Size Guidelines

| Size | Use case | Trade-off |
|---|---|---|
| 128-256 tokens | FAQ, short definitions | High precision, less context |
| 256-512 tokens | **Recommended default** | Good balance |
| 512-1024 tokens | Complex text, legal docs | More context, potential noise |
| >1024 tokens | Rarely used | Too much noise |

### Semantic Chunking

Split by meaning (section, topic) instead of fixed size:

```python
# Split by markdown headings
# Split by paragraph breaks (\n\n)
# Split by topic change (using NLP or LLM detection)
```

### Overlap Strategy

- **10-20% overlap** between adjacent chunks
- Ensures information at boundaries is not lost
- Chunk N ends with 1-2 opening sentences of chunk N+1

### Hierarchical Chunking (Parent-Child)

```
Document (summary)
  └── Section (heading + key points)
        └── Paragraph (details)
```

- Search at paragraph level (most detailed)
- When matched, pull parent section for additional context
- Keep `parent_id` in metadata

### Domain-Specific Chunking

- **Insurance:** 1 chunk = 1 clause
- **Finance:** 1 chunk = 1 report section, metadata = ticker + period
- **Healthcare:** 1 chunk = 1 guideline/recommendation
- **E-commerce:** 1 chunk = 1 review or 1 product description
- **Legal:** 1 chunk = 1 article/clause/section

### Metadata Enrichment Per Chunk

Each chunk should be enriched with:
- **Summary:** 1-2 sentence content summary (LLM-generated)
- **Keywords:** Key terms (supports BM25)
- **Questions:** 2-3 questions this chunk can answer (hypothetical questions)
- **Entities:** Named entities (product names, codes, dates)

---

## 3. Retrieval Optimization

> Detailed code examples: read `references/retrieval-patterns.md`

### Recommended Retrieval Pipeline

```
User Query
  → Query Rewriting (expand/reformulate)
  → Multi-Query Generation (3-5 variants)
  → Metadata Filtering (narrow scope)
  → Hybrid Search (Vector + BM25)
  → Merge & Deduplicate
  → Reranking (top 20 → top 5)
  → Contextual Compression
  → LLM Generation (with citations)
```

### Hybrid Search (Vector + BM25)

- **Vector search:** Find by meaning (semantic similarity)
- **BM25 (keyword):** Find by exact keywords (product names, codes)
- **Combined:** Weighted fusion or Reciprocal Rank Fusion (RRF)

```
final_score = α × vector_score + (1-α) × bm25_score
# α = 0.7 is a good starting point, tune per domain
```

### Query Rewriting

Use LLM to reformulate the user question for clarity:

```
User: "does insurance pay?"
→ Rewritten: "Under what circumstances does life insurance pay out benefits?"
```

### Multi-Query

From 1 question, generate 3-5 variants → search each variant → merge results:

```
Original: "Which bank has the highest savings rate?"
Query 1: "Compare savings interest rates across banks 2024"
Query 2: "Bank with highest deposit rate currently"
Query 3: "Top banks with best deposit interest rates"
```

### Reranking

After retrieval, use a reranking model to re-sort by relevance:

- **Cohere Rerank:** Simple API, highly effective
- **Cross-encoder:** More accurate than bi-encoder, but slower
- **GPT Rerank:** Use LLM to evaluate relevance (expensive but flexible)

Retrieve top 20 → rerank → take top 3-5 for generation.

### Contextual Compression

After reranking, compress each chunk: keep only the part relevant to the question.

```
Original chunk (500 tokens) → Compressed (150 tokens, relevant part only)
```

Reduces noise, saves context window, improves accuracy.

### Metadata Filtering

Narrow the search space BEFORE vector search:

```python
# Instead of searching all 1M chunks:
filter = {"domain": "insurance", "product_type": "life"}
# Only search within ~50K relevant chunks
results = vector_db.search(query, filter=filter, top_k=20)
```

---

## 4. Accuracy Testing & Monitoring

### Test Suite Design

Create ground truth Q&A pairs:

```json
{
    "test_cases": [
        {
            "question": "Does life insurance pay out for suicide?",
            "expected_answer": "No payout within the first 2 years",
            "expected_source": "clause_15_exclusions.pdf",
            "category": "exclusions",
            "difficulty": "medium"
        }
    ]
}
```

**Recommendation:** Minimum 50-100 test cases, evenly distributed across categories and difficulty levels.

### Metrics

| Metric | Meaning | Target |
|---|---|---|
| **Precision@K** | % relevant results in top K | >0.8 |
| **Recall@K** | % ground truth found in top K | >0.9 |
| **F1** | Harmonic mean of Precision and Recall | >0.85 |
| **MRR** | Mean Reciprocal Rank — average position of first correct result | >0.8 |
| **NDCG** | Normalized Discounted Cumulative Gain — ranking quality | >0.85 |
| **Answer Accuracy** | % correct answers (human eval or LLM judge) | >0.9 |

### A/B Testing

Compare strategies by running the same test suite:

```
Config A: chunk_size=256, overlap=10%, no_rerank
Config B: chunk_size=512, overlap=20%, cohere_rerank
→ Compare MRR, NDCG, Answer Accuracy
→ Choose the config with better metrics
```

### Error Analysis Framework

Classify errors to know where to optimize:

| Error Type | Cause | Solution |
|---|---|---|
| **Retrieval Miss** | Correct chunk not found | Improve chunking, add hypothetical Q |
| **Ranking Error** | Correct chunk found but ranked low | Add reranking |
| **Generation Error** | Correct chunk but LLM answers wrong | Improve prompt, add few-shot |
| **No Answer** | Information not in DB | Expand knowledge base |
| **Hallucination** | LLM fabricates information | Add citation enforcement |

### Production Monitoring

Log each query:

```python
log_entry = {
    "timestamp": "2024-01-15T10:30:00",
    "query": "...",
    "retrieved_chunks": [...],
    "reranked_chunks": [...],
    "answer": "...",
    "confidence": 0.85,
    "latency_ms": 450,
    "user_feedback": None  # thumbs up/down
}
```

**Alerts:**
- Continuous confidence < 0.5 → review chunking/retrieval
- Latency > 2s → optimize index or reduce top_k
- Negative feedback > 20% → audit error patterns

---

## 5. Safeguards

### Hallucination Prevention

Mandatory system prompt:

```
Answer ONLY based on the information provided in the context.
If you cannot find the information, respond: "I could not find this
information in the available data."
NEVER fabricate information.
```

### Citation Enforcement

Require source citations:

```
Every answer must include [Source: file_name, section/clause].
If a specific source cannot be cited, mark it as "unverified".
```

### Confidence Thresholds

```python
if max_relevance_score < 0.3:
    return "No relevant information found."
elif max_relevance_score < 0.6:
    return answer + "\n⚠️ Low confidence. Please verify."
else:
    return answer + f"\n📎 Source: {sources}"
```

### Answer Verification

Cross-check the answer with the DB:

1. Extract claims from the answer (using LLM)
2. Verify each claim against retrieved chunks
3. Flag claims without supporting evidence
4. Return only verified claims

---

## 6. Embedding Model Selection

> Detailed comparison: read `references/embedding-models.md`

### Quick Decision

| Scenario | Model | Reason |
|---|---|---|
| Production, budget OK | Cohere embed-v4 | Highest MTEB, input_type optimization |
| Production, low cost | OpenAI text-embedding-3-small | $0.02/1M tokens, good quality |
| Self-host, multilingual | **BGE-M3** ⭐ | Hybrid dense+sparse, 100+ languages, free |
| Self-host, Vietnamese | **BGE-M3** or **multilingual-e5-large** | Best for Vietnamese RAG |
| POC / Prototype | all-MiniLM-L6-v2 | 90MB, runs on CPU |

### Key Principles

- **Dimension reduction:** OpenAI embed-3 supports Matryoshka — reduce 3072→512 with only ~3% quality loss
- **Normalize embeddings:** Always `normalize_embeddings=True` when encoding for cosine similarity
- **Batch processing:** Encode in batches (256-2000 items) instead of one at a time
- **Consistency:** Use the SAME model for indexing and querying

---

## 7. Vector DB Comparison

> Detailed comparison + HNSW tuning: read `references/vector-db-comparison.md`

### Quick Decision

```
Already have PostgreSQL and <5M vectors? → pgvector
Just prototype/POC? → ChromaDB
Production, want zero-ops? → Pinecone
Need performance + HNSW control? → Qdrant
Need hybrid BM25+vector built-in? → Weaviate
```

### HNSW Tuning Quick Reference

| Param | Default | Accuracy-critical | Speed-critical |
|---|---|---|---|
| M | 16 | 48-64 | 8-16 |
| ef_construction | 200 | 400-500 | 100-200 |
| ef (search) | 100 | 200-256 | 50-100 |

**Trade-off:** Higher M and ef → better recall but more RAM and slower. Tune per SLA.

---

## 8. Advanced Techniques

> Detailed code examples: read `references/advanced-rag.md`

### Late Chunking

Embed the **entire document** first, then pool embeddings by chunk boundaries. Each chunk retains context from surrounding text.

```
Traditional: Doc → Chunk → Embed each (loses context)
Late Chunking: Doc → Embed full → Pool by boundaries (retains context)
```

**Use when:** Documents have many co-references ("it", "this", "the package"). Quality gain: +5-10%.

### RAPTOR (Recursive Abstractive Processing)

Build a multi-level summary tree: Level 0 (chunks) → Level 1 (summaries) → Level 2 (summary of summaries).

**Use when:** Need to answer both broad queries ("Compare all insurance packages") and narrow queries ("Clause X of Package Y"). Quality gain: +10-15%.

### GraphRAG (Microsoft)

Build a knowledge graph from documents → detect communities → summarize communities → query via map-reduce.

**Use when:** Multi-hop reasoning, synthesize across many documents. Quality gain: +15-25% for synthesis queries. **High overhead** (many LLM calls when building the graph).

### Combining Techniques (Production Stack)

```
1. Late Chunking → better embeddings
2. Hybrid Search (BM25 + vector) → high recall
3. Reranking (Cohere/Cross-encoder) → high precision
4. RAPTOR → multi-level retrieval (optional)
5. GraphRAG → synthesis queries (optional, high cost)
```

---

## 9. Performance Optimization

### Caching Layer

```python
# Cache embeddings (avoid re-computation)
import hashlib, json, redis

r = redis.Redis()

def cached_embed(text, model):
    key = f"emb:{hashlib.md5(text.encode()).hexdigest()}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    embedding = model.encode([text])[0].tolist()
    r.setex(key, 3600, json.dumps(embedding))  # TTL 1h
    return embedding

# Cache search results (avoid re-searching)
def cached_search(query, search_fn, ttl=300):
    key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    results = search_fn(query)
    r.setex(key, ttl, json.dumps(results))
    return results
```

### Async Retrieval

```python
import asyncio

async def parallel_retrieve(query, retrievers):
    """Run multiple retrievers in parallel."""
    tasks = [r.search(query) for r in retrievers]
    results = await asyncio.gather(*tasks)
    return merge_and_deduplicate(results)
```

### HNSW Index Tuning

See details in `references/vector-db-comparison.md` HNSW section. Key: tune `ef` (search) per latency SLA, tune `M` per recall target.

---

## 10. Vietnamese-Specific RAG

> Details: read `references/vietnam-nlp.md`

### Key Challenges

| Issue | Solution |
|---|---|
| Diacritics (with vs without) | Dual indexing: index both versions |
| Compound words ("bảo hiểm") | Word segmentation (underthesea) |
| Abbreviations (BHXH, TTCK, BLLĐ) | Abbreviation expansion dictionary |
| Vietnamese proper names | NER with underthesea/PhoBERT |
| Domain terms (finance, law, medical) | Domain-specific term enrichment |

### Embedding Models for Vietnamese

- **BGE-M3:** Best overall — hybrid dense+sparse, 100+ languages
- **multilingual-e5-large:** Good alternative — retrieval-optimized
- **PhoBERT-v2:** Best for NER/classification (needs fine-tuning for retrieval)

### Preprocessing Pipeline

```
Input text
  → Unicode normalize (NFC)
  → Expand abbreviations (BHXH → Social Insurance)
  → Domain term enrichment
  → Dual index: original + no-diacritics version
  → Extract entities → metadata
```

---

## 11. AI Orchestrator — Multi-Model Cost Optimization

> Detailed prompt templates, code examples: read `references/orchestrator-patterns.md`

### Query Classification Pipeline

Each user query is classified into 1 of 5 categories:

| Category | Description | Example | Model |
|---|---|---|---|
| **simple** | Greeting, FAQ, simple lookup | "Hello", "Opening hours?" | No LLM / Local |
| **rag** | Needs knowledge base search | "Does insurance cover cancer?" | Cheap (Gemini Flash) |
| **complex** | Multi-hop reasoning, comparison, analysis | "Compare 3 insurance packages for a family of 4" | Standard (GPT-4o-mini) / Premium (Claude Sonnet) |
| **action** | Needs tool/API execution (create form, calculate) | "Calculate insurance premium for me, age 30" | Standard + Tools |
| **unsafe** | Violation content, injection, jailbreak | "Ignore instructions..." | Block — No LLM |

### 2-Stage Classification (Minimize LLM Tokens)

```
User Query
  → Stage 1: Rule-based pre-classifier (regex, keywords, NO LLM)
    → confidence ≥ 0.8? → DONE (skip LLM)
    → confidence < 0.8? → Stage 2: LLM classifier (cheap model, ~50 tokens)
```

**Stage 1 blocks 60-80% of queries** without spending a single LLM token.

### Model Routing

```
Category → Model Selection:
  greeting/simple  → No LLM (rule-based response)
  rag (simple)     → Gemini Flash ($0.075/1M input) — cheap, fast
  rag (complex)    → GPT-4o-mini ($0.15/1M input) — balanced
  complex          → Claude Sonnet ($3/1M input) — premium quality
  action           → Gemini Flash + Tool calls
  unsafe           → Block response (no LLM cost)
```

### Cost Optimization Rules

1. **Rule-based first:** Greeting, FAQ, unsafe → DON'T call LLM
2. **Cheapest sufficient model:** Prefer Gemini Flash for RAG queries
3. **Escalate on failure:** Gemini Flash fail/low-confidence → GPT-4o-mini → Claude Sonnet
4. **Cache responses:** Identical queries → cached answer (TTL 5-30 min)
5. **Batch classify:** Multiple queries → 1 LLM call to classify all
6. **Token budget:** Set max_tokens per category (simple: 100, rag: 300, complex: 500)

### RAG Trigger Rules

| Condition | RAG On/Off |
|---|---|
| Query contains domain keywords | ✅ ON |
| Classification = "rag" or "complex" | ✅ ON |
| Greeting, simple lookup, unsafe | ❌ OFF |
| Confidence score > 0.9 from cache/FAQ | ❌ OFF (answer from cache) |

### Tool Trigger Rules

| Condition | Tools |
|---|---|
| Query requests calculation (fees, interest) | calculator tool |
| Query requests form creation/submission | form_builder tool |
| Query requests real-time lookup (price, exchange rate) | api_lookup tool |
| Classification ≠ "action" | No tools |

### JSON Output Format

```json
{
  "category": "rag",
  "confidence": 0.92,
  "risk_level": "low",
  "model": "gemini-flash",
  "rag_enabled": true,
  "tools": [],
  "max_tokens": 300,
  "reasoning": "User asks about insurance benefits — needs knowledge base search"
}
```

---

## Scripts

### eval_ragas.py

RAGAS evaluation pipeline. Run:

```bash
python3 scripts/eval_ragas.py --test-file eval_dataset.json --output results.json
python3 scripts/eval_ragas.py --test-file eval_dataset.json --metrics faithfulness,answer_relevancy
```

Input: JSON file with test cases (question, answer, contexts, ground_truth). Output: metrics report + threshold checks.
Requires: `pip install ragas langchain-openai datasets`

### embedding_benchmark.py

Benchmark embedding models on a Vietnamese dataset. Run:

```bash
python3 scripts/embedding_benchmark.py --models bge-m3,multilingual-e5 --dataset vi_pairs.json
python3 scripts/embedding_benchmark.py --models all --quick  # Use built-in test pairs
```

Input: JSON file with query-positive-negative pairs. Output: accuracy + latency comparison.
Requires: `pip install sentence-transformers numpy torch`

### chunk_optimizer.py

Evaluate chunk quality. Run:

```bash
python3 scripts/chunk_optimizer.py --input chunks.jsonl --output report.json
```

Input: JSONL file, each line is `{"text": "...", "metadata": {...}}`. Output: quality report with scores.

### accuracy_test.py

Test framework for RAG accuracy. Run:

```bash
python3 scripts/accuracy_test.py --test-file tests.json --results-dir ./results
```

Input: JSON file with test cases (question, expected_answer, expected_source). Output: metrics report.

---

## References

- `references/chunking-patterns.md` — Python code examples for chunking strategies
- `references/retrieval-patterns.md` — Code examples for hybrid search, reranking, multi-query
- `references/embedding-models.md` — Detailed embedding model comparison (OpenAI, Cohere, BGE-M3, PhoBERT...)
- `references/vector-db-comparison.md` — Vector DB comparison + HNSW tuning guide
- `references/advanced-rag.md` — Late Chunking, RAPTOR, GraphRAG with code examples
- `references/testing-frameworks.md` — RAGAS, LLM-as-Judge, Adversarial testing
- `references/vietnam-nlp.md` — Vietnamese NLP: diacritics, abbreviations, NER, domain terms
- `references/orchestrator-patterns.md` — Multi-model orchestrator: prompt templates, rule-based pre-classifier, cost comparison, fallback chain, monitoring
