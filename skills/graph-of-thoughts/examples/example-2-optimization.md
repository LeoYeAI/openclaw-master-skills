# Example: Algorithm Optimization with Graph of Thoughts

## Problem

Optimize a search function for a large dataset (10M+ records).

**Current State**:
- Linear search through array
- O(n) complexity
- 500ms average response time
- Growing dataset causing slowdowns

**Requirements**:
- <50ms response time
- Support prefix matching
- Handle typos/fuzzy matching
- Memory efficient (<2GB)

---

## Phase 1: Generate Paths (N=5)

### Path A: Inverted Index
```
Approach: Build inverted index of terms
- Map terms to document IDs
- Fast exact matching
- Well-understood

Key Features:
- Term → [doc_ids] mapping
- Boolean query support
- Ranked results

Score: 8.2/10
```

### Path B: Trie Structure
```
Approach: Prefix tree for fast lookups
- O(k) where k = key length
- Perfect for prefix matching
- Memory efficient for common prefixes

Key Features:
- Character-by-character traversal
- Autocomplete support
- Space sharing for prefixes

Score: 7.5/10
```

### Path C: Vector Embeddings
```
Approach: Semantic search with embeddings
- Dense vector representations
- Similarity search
- Handles typos via semantics

Key Features:
- Word2Vec/BERT embeddings
- Cosine similarity
- Semantic understanding

Score: 7.8/10
```

### Path D: Simple Caching
```
Approach: Cache popular queries
- LRU cache for results
- Fast for repeated queries
- Minimal code changes

Key Features:
- In-memory cache
- TTL for freshness
- Transparent to caller

Score: 6.5/10
```

### Path E: Distributed Search
```
Approach: Shard data across nodes
- Parallel search
- Horizontal scaling
- Fault tolerance

Key Features:
- Consistent hashing
- Replica sets
- Query distribution

Score: 7.0/10
```

---

## Phase 2: Evaluate Paths

| Path | Feasibility | Quality | Novelty | Coverage | Efficiency | **Score** |
|------|-------------|---------|---------|----------|------------|-----------|
| A | 9 | 8 | 6 | 8 | 8 | **8.2** |
| B | 8 | 7 | 6 | 7 | 8 | **7.5** |
| C | 7 | 9 | 8 | 9 | 5 | **7.8** |
| D | 10 | 5 | 4 | 4 | 9 | **6.5** |
| E | 6 | 8 | 7 | 9 | 6 | **7.0** |

**Analysis**:
- A (Inverted Index): Best for exact matching, proven
- B (Trie): Good for prefix, limited fuzzy
- C (Embeddings): Best fuzzy, high memory
- D (Caching): Fast but limited coverage
- E (Distributed): Complex, overkill for single-node

---

## Phase 3: Identify Synergies

### Synergy Matrix

| Pair | Type | Score | Combination Potential |
|------|------|-------|----------------------|
| A + C | Complementary | **0.85** | Exact + Semantic |
| A + B | Enhancing | 0.78 | Index + Prefix |
| A + D | Enhancing | 0.72 | Index + Cache |
| B + C | Partial | 0.65 | Prefix + Semantic |
| C + D | Limited | 0.45 | Different paradigms |

### Top Synergy: A + C (Index + Embeddings)

```
Why they work together:
- A provides fast exact matching
- C provides fuzzy/semantic matching
- Combined: best of both worlds

Combination Strategy:
1. Try exact match first (A)
2. Fall back to semantic search (C)
3. Combine and rank results
```

---

## Phase 4: Combine Thoughts

### Combination: Hybrid Search (A + C)

```python
class HybridSearch:
    def __init__(self):
        self.inverted_index = InvertedIndex()  # From A
        self.embeddings = VectorIndex()         # From C
        self.cache = LRUCache()                 # From D (bonus)
    
    def search(self, query, top_k=10):
        # Check cache first
        if query in self.cache:
            return self.cache[query]
        
        # Phase 1: Exact match (fast)
        exact_results = self.inverted_index.search(query)
        
        # Phase 2: Semantic search (fuzzy)
        semantic_results = self.embeddings.search(query, top_k * 2)
        
        # Phase 3: Combine and rank
        combined = self.combine_results(
            exact_results, 
            semantic_results
        )
        
        # Cache results
        self.cache[query] = combined[:top_k]
        
        return combined[:top_k]
    
    def combine_results(self, exact, semantic):
        # Exact matches get priority
        # Semantic fills in gaps
        # Rerank by combined score
        ...
```

**Score**: 8.8/10 (+0.6 from best individual)

---

## Phase 5: Iterate with Feedback

### Iteration 1

**Critique**: "Vector search is slow for 10M documents"

**Improvement**: Use Approximate Nearest Neighbor (ANN)
```python
# Replace exact vector search with ANN
self.embeddings = AnnoyIndex()  # or HNSW
# Trades ~5% accuracy for 10x speed
```

**New Score**: 9.2/10

### Iteration 2

**Critique**: "Memory usage high with both indexes"

**Improvement**: Quantize embeddings
```python
# Reduce embedding size
# 512 float32 → 64 int8
# 8x memory reduction
self.embeddings = QuantizedIndex(
    dimensions=512,
    quantized=True
)
```

**New Score**: 9.3/10

### Iteration 3

**Critique**: "Prefix matching still slow"

**Improvement**: Add trie for autocomplete
```python
# Hybrid now has 3 indexes:
# 1. Inverted (exact)
# 2. ANN (semantic)
# 3. Trie (prefix) - from B
```

**New Score**: 9.4/10

### Convergence Check

| Iteration | Improvement | Cumulative |
|-----------|-------------|------------|
| 1 | +0.4 | 9.2 |
| 2 | +0.1 | 9.3 |
| 3 | +0.1 | 9.4 |
| 4 (projected) | +0.02 | 9.42 |

**Decision**: Stop at iteration 3 (diminishing returns)

---

## Phase 6: Aggregate Final Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HYBRID SEARCH ENGINE                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Query Entry Point:                                         │
│  ┌──────────────────────────────────────────┐              │
│  │  search(query) → [results]               │              │
│  └───────────────────┬──────────────────────┘              │
│                      │                                      │
│                      ▼                                      │
│  ┌──────────────────────────────────────────┐              │
│  │         Query Preprocessor               │              │
│  │  - Normalize                             │              │
│  │  - Tokenize                              │              │
│  │  - Spell check (optional)                │              │
│  └───────────────────┬──────────────────────┘              │
│                      │                                      │
│         ┌────────────┼────────────┐                        │
│         │            │            │                        │
│         ▼            ▼            ▼                        │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐               │
│  │   LRU     │ │  Exact    │ │  Semantic │               │
│  │   Cache   │ │  Match    │ │  Search   │               │
│  │           │ │           │ │  (ANN)    │               │
│  │  10K      │ │  Inverted │ │  HNSW     │               │
│  │  queries  │ │  Index    │ │  Index    │               │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘               │
│        │             │             │                      │
│        │      ┌──────┴──────┐      │                      │
│        │      │             │      │                      │
│        │      ▼             ▼      │                      │
│        │ ┌─────────────────────┐   │                      │
│        │ │   Prefix Autocomplete │  │                      │
│        │ │   (Trie)            │   │                      │
│        │ └──────────┬──────────┘   │                      │
│        │            │              │                      │
│        └────────────┼──────────────┘                      │
│                     │                                      │
│                     ▼                                      │
│  ┌──────────────────────────────────────────┐              │
│  │         Result Combiner                  │              │
│  │  - Merge results                         │              │
│  │  - Deduplicate                           │              │
│  │  - Rank by combined score                │              │
│  └───────────────────┬──────────────────────┘              │
│                      │                                      │
│                      ▼                                      │
│  ┌──────────────────────────────────────────┐              │
│  │         Ranked Results                   │              │
│  │  [doc1: 0.95, doc2: 0.87, ...]          │              │
│  └──────────────────────────────────────────┘              │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Memory Usage:
- Inverted Index: ~200MB
- ANN Index (quantized): ~500MB
- Trie: ~100MB
- Cache: ~50MB
- Total: ~850MB (within 2GB limit ✓)
```

### Component Details

```python
class HybridSearchEngine:
    """Final synthesized search solution."""
    
    def __init__(self, config):
        # From Path A: Inverted Index
        self.exact_index = InvertedIndex(
            tokenizer=Tokenizer(normalize=True),
            stemmer=PorterStemmer()
        )
        
        # From Path C: Semantic Search (with improvements)
        self.semantic_index = HNSWIndex(
            metric='cosine',
            dimension=64,  # Quantized from 512
            quantized=True
        )
        
        # From Path B: Prefix Trie
        self.prefix_trie = TrieIndex()
        
        # From Path D: Caching
        self.cache = LRUCache(max_size=10000)
        
        # Ranking weights
        self.weights = {
            'exact': 0.4,
            'semantic': 0.35,
            'prefix': 0.25
        }
    
    def search(self, query: str, top_k: int = 10) -> List[Result]:
        """Search across all indexes and combine."""
        
        # Check cache
        cache_key = self._cache_key(query)
        if cached := self.cache.get(cache_key):
            return cached
        
        # Parallel search across indexes
        with ThreadPoolExecutor() as executor:
            exact_future = executor.submit(
                self.exact_index.search, query
            )
            semantic_future = executor.submit(
                self.semantic_index.search, query, top_k * 2
            )
            prefix_future = executor.submit(
                self.prefix_trie.search, query, top_k
            )
            
            exact_results = exact_future.result()
            semantic_results = semantic_future.result()
            prefix_results = prefix_future.result()
        
        # Combine results
        combined = self._combine_results(
            exact_results,
            semantic_results,
            prefix_results
        )
        
        # Cache and return
        self.cache.set(cache_key, combined[:top_k])
        return combined[:top_k]
    
    def _combine_results(self, exact, semantic, prefix):
        """Combine and rank results from all indexes."""
        scores = defaultdict(float)
        
        # Exact matches (highest weight)
        for doc_id, score in exact:
            scores[doc_id] += score * self.weights['exact']
        
        # Semantic matches
        for doc_id, score in semantic:
            scores[doc_id] += score * self.weights['semantic']
        
        # Prefix matches
        for doc_id, score in prefix:
            scores[doc_id] += score * self.weights['prefix']
        
        # Sort by combined score
        ranked = sorted(
            scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return [Result(doc_id, score) for doc_id, score in ranked]
```

---

## Performance Benchmarks

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Avg Response Time | 500ms | 35ms | **14x faster** |
| P99 Response Time | 2000ms | 80ms | **25x faster** |
| Memory Usage | 1.5GB | 850MB | **43% reduction** |
| Index Size | N/A | 800MB | Within limits ✓ |
| Exact Match Accuracy | 100% | 100% | Maintained ✓ |
| Fuzzy Match Accuracy | 0% | 92% | **Enabled** ✓ |
| Prefix Match Speed | 500ms | 5ms | **100x faster** ✓ |

---

## Verification

### Requirements Check

| Requirement | Target | Achieved | Status |
|-------------|--------|----------|--------|
| Response Time | <50ms | 35ms | ✅ |
| Prefix Matching | Yes | Yes | ✅ |
| Fuzzy Matching | Yes | Yes | ✅ |
| Memory Usage | <2GB | 850MB | ✅ |

### Test Cases

```python
# Test 1: Exact match
results = engine.search("machine learning")
assert results[0].doc_id == "ml_tutorial"
assert len(results) == 10

# Test 2: Typo handling
results = engine.search("machne lerning")
assert "ml_tutorial" in [r.doc_id for r in results]

# Test 3: Prefix matching
results = engine.search("mach")
assert len(results) > 0

# Test 4: Performance
import time
start = time.time()
for _ in range(1000):
    engine.search("test query")
avg_time = (time.time() - start) / 1000
assert avg_time < 0.05  # <50ms
```

---

## Summary

| Metric | Value |
|--------|-------|
| Paths Generated | 5 |
| Combinations Created | 1 (major) |
| Feedback Iterations | 3 |
| Final Score | 9.4/10 |
| Confidence | 90% |
| Improvement over best individual | +1.2 points |

**Selected Solution**: Hybrid search engine combining inverted index, semantic search (ANN), and prefix trie with intelligent caching.

**Key Innovations**:
1. Three-index hybrid approach
2. Quantized embeddings for memory efficiency
3. Parallel search execution
4. Combined ranking algorithm

**Why This Solution**:
- Meets all performance requirements
- Memory efficient
- Handles exact, fuzzy, and prefix queries
- Proven components with novel combination
