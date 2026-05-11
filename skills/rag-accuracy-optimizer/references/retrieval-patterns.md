# Retrieval Patterns — Python Code Examples

## Table of Contents

1. [Hybrid Search (Vector + BM25)](#1-hybrid-search-vector--bm25)
2. [Query Rewriting](#2-query-rewriting)
3. [Multi-Query Generation](#3-multi-query-generation)
4. [Reranking](#4-reranking)
5. [Contextual Compression](#5-contextual-compression)
6. [Metadata Filtering](#6-metadata-filtering)
7. [Full RAG Retrieval Pipeline](#7-full-rag-retrieval-pipeline)

---

## 1. Hybrid Search (Vector + BM25)

### Reciprocal Rank Fusion (RRF)

```python
def reciprocal_rank_fusion(
    results_lists: list[list[dict]],
    k: int = 60
) -> list[dict]:
    """
    Merge multiple ranked lists using RRF.
    Each result dict needs 'id' và 'text'.
    """
    scores = {}
    docs = {}

    for results in results_lists:
        for rank, doc in enumerate(results):
            doc_id = doc["id"]
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
            docs[doc_id] = doc

    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)
    return [
        {**docs[doc_id], "rrf_score": scores[doc_id]}
        for doc_id in sorted_ids
    ]
```

### Hybrid Search với Qdrant + BM25

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from rank_bm25 import BM25Okapi
import numpy as np

class HybridSearcher:
    def __init__(self, qdrant_url: str, collection: str, documents: list[dict]):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.collection = collection
        self.documents = documents

        # Build BM25 index
        tokenized = [doc["text"].lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)
        self.doc_ids = [doc["id"] for doc in documents]

    def search(
        self,
        query: str,
        query_vector: list[float],
        top_k: int = 20,
        alpha: float = 0.7,
        metadata_filter: dict | None = None,
    ) -> list[dict]:
        """
        Hybrid search: α × vector + (1-α) × BM25.
        alpha=0.7 → prioritize semantic, alpha=0.3 → prioritize keyword.
        """
        # Vector search
        qdrant_filter = None
        if metadata_filter:
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in metadata_filter.items()
            ]
            qdrant_filter = Filter(must=conditions)

        vector_results = self.qdrant.search(
            collection_name=self.collection,
            query_vector=query_vector,
            limit=top_k * 2,
            query_filter=qdrant_filter,
        )

        # BM25 search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        bm25_top = np.argsort(bm25_scores)[::-1][:top_k * 2]

        # Normalize scores
        vec_scores = {r.id: r.score for r in vector_results}
        max_vec = max(vec_scores.values()) if vec_scores else 1
        vec_scores = {k: v / max_vec for k, v in vec_scores.items()}

        bm25_norm = {}
        max_bm25 = bm25_scores[bm25_top[0]] if len(bm25_top) > 0 else 1
        for idx in bm25_top:
            doc_id = self.doc_ids[idx]
            bm25_norm[doc_id] = bm25_scores[idx] / max_bm25 if max_bm25 > 0 else 0

        # Combine
        all_ids = set(vec_scores.keys()) | set(bm25_norm.keys())
        combined = []
        for doc_id in all_ids:
            score = alpha * vec_scores.get(doc_id, 0) + (1 - alpha) * bm25_norm.get(doc_id, 0)
            combined.append({"id": doc_id, "score": score})

        combined.sort(key=lambda x: x["score"], reverse=True)
        return combined[:top_k]
```

### Hybrid Search với PostgreSQL + pgvector

```python
import psycopg2

def hybrid_search_pgvector(
    conn,
    query_text: str,
    query_embedding: list[float],
    top_k: int = 20,
    alpha: float = 0.7,
    domain_filter: str | None = None,
) -> list[dict]:
    """Hybrid search using pgvector + ts_rank (PostgreSQL full-text search)."""
    filter_clause = ""
    params = [query_embedding, query_text, query_text, top_k]

    if domain_filter:
        filter_clause = "WHERE domain = %s"
        params = [query_embedding, query_text, query_text, domain_filter, top_k]

    sql = f"""
    WITH vector_search AS (
        SELECT id, text, metadata,
               1 - (embedding <=> %s::vector) AS vec_score
        FROM chunks {filter_clause.replace('WHERE', 'WHERE' if not filter_clause else 'WHERE') or ''}
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    ),
    keyword_search AS (
        SELECT id, text, metadata,
               ts_rank(to_tsvector('simple', text), plainto_tsquery('simple', %s)) AS kw_score
        FROM chunks {filter_clause}
        WHERE to_tsvector('simple', text) @@ plainto_tsquery('simple', %s)
        LIMIT %s
    )
    SELECT COALESCE(v.id, k.id) AS id,
           COALESCE(v.text, k.text) AS text,
           ({alpha} * COALESCE(v.vec_score, 0) +
            {1-alpha} * COALESCE(k.kw_score, 0)) AS combined_score
    FROM vector_search v
    FULL OUTER JOIN keyword_search k ON v.id = k.id
    ORDER BY combined_score DESC
    LIMIT {top_k};
    """

    # Simplified — adapt SQL params to your setup
    cur = conn.cursor()
    cur.execute(sql, params)
    return [{"id": r[0], "text": r[1], "score": r[2]} for r in cur.fetchall()]
```

---

## 2. Query Rewriting

```python
from openai import OpenAI

client = OpenAI()

def rewrite_query(query: str, context: str = "") -> str:
    """Rewrite user query for clarity and completeness."""
    prompt = f"""Rewrite the following question for clarity and completeness to enable effective search.
Preserve the original meaning. Return ONLY the rewritten question, no explanation.

{"Context: " + context if context else ""}
Original question: {query}
Rewritten question:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()

# Example
# "bh có trả ko?" → "Bảo hiểm nhân thọ có chi trả quyền lợi trong trường hợp nào?"
```

---

## 3. Multi-Query Generation

```python
def generate_multi_queries(query: str, n: int = 4) -> list[str]:
    """Generate n question variants to expand search coverage."""
    prompt = f"""Generate {n} different questions with the same meaning as the original question.
Each should use different wording and perspectives.
Return each question on a new line, no numbering.

Original question: {query}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )

    queries = [q.strip() for q in response.choices[0].message.content.strip().split("\n") if q.strip()]
    return [query] + queries[:n]  # Include original

# Example:
# "Lãi suất ngân hàng nào cao nhất?"
# → ["Lãi suất ngân hàng nào cao nhất?",
#     "So sánh lãi suất tiết kiệm các ngân hàng 2024",
#     "Ngân hàng nào có lãi suất huy động tốt nhất",
#     "Top ngân hàng lãi suất tiền gửi cao hiện nay",
#     "Bảng xếp hạng lãi suất ngân hàng mới nhất"]
```

---

## 4. Reranking

### Cohere Rerank

```python
import cohere

co = cohere.Client("YOUR_COHERE_API_KEY")

def cohere_rerank(query: str, documents: list[dict], top_n: int = 5) -> list[dict]:
    """Rerank documents using Cohere Rerank API."""
    texts = [doc["text"] for doc in documents]

    response = co.rerank(
        model="rerank-multilingual-v3.0",
        query=query,
        documents=texts,
        top_n=top_n,
    )

    reranked = []
    for result in response.results:
        doc = documents[result.index].copy()
        doc["rerank_score"] = result.relevance_score
        reranked.append(doc)

    return reranked
```

### Cross-Encoder Rerank (sentence-transformers)

```python
from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-12-v2")

def cross_encoder_rerank(query: str, documents: list[dict], top_n: int = 5) -> list[dict]:
    """Rerank using cross-encoder model (local, no API needed)."""
    pairs = [(query, doc["text"]) for doc in documents]
    scores = model.predict(pairs)

    scored_docs = list(zip(documents, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)

    reranked = []
    for doc, score in scored_docs[:top_n]:
        doc_copy = doc.copy()
        doc_copy["rerank_score"] = float(score)
        reranked.append(doc_copy)

    return reranked
```

### GPT Rerank

```python
import json

def gpt_rerank(query: str, documents: list[dict], top_n: int = 5) -> list[dict]:
    """Rerank using GPT — expensive but flexible, supports reasoning."""
    docs_text = "\n\n".join(
        f"[Doc {i}]: {doc['text'][:500]}"
        for i, doc in enumerate(documents)
    )

    prompt = f"""Evaluate the relevance of each document to the question.
Return a JSON array of document indices, sorted from most to least relevant.
Keep only top {top_n} documents.

Question: {query}

Documents:
{docs_text}

Trả về JSON: {{"ranked_indices": [...]}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )

    result = json.loads(response.choices[0].message.content)
    indices = result.get("ranked_indices", [])[:top_n]

    return [documents[i] for i in indices if i < len(documents)]
```

---

## 5. Contextual Compression

```python
def compress_chunk(query: str, chunk_text: str) -> str:
    """Compress chunk: keep only the part relevant to the question."""
    prompt = f"""Extract ONLY the information from the following passage that is relevant to the question.
Keep the original content, do not add new information.
If no relevant information is found, return "NOT_RELEVANT".

Question: {query}

Passage:
{chunk_text}

Relevant information:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=500,
    )

    result = response.choices[0].message.content.strip()
    if result == "NOT_RELEVANT":
        return ""
    return result


def compress_chunks(query: str, chunks: list[dict]) -> list[dict]:
    """Compress all chunks, remove irrelevant ones."""
    compressed = []
    for chunk in chunks:
        compressed_text = compress_chunk(query, chunk["text"])
        if compressed_text:
            chunk_copy = chunk.copy()
            chunk_copy["original_text"] = chunk["text"]
            chunk_copy["text"] = compressed_text
            chunk_copy["compressed"] = True
            compressed.append(chunk_copy)
    return compressed
```

---

## 6. Metadata Filtering

```python
def extract_metadata_filters(query: str, available_filters: dict) -> dict:
    """Use LLM to extract metadata filters from the question."""
    prompt = f"""From the following question, extract applicable filters.
Available filters: {json.dumps(available_filters, ensure_ascii=False)}

Question: {query}

Return JSON with matching filters. Only include a filter when CERTAIN from the question.
Ví dụ: {{"domain": "insurance", "product_type": "life"}}
If nothing can be extracted, return {{}}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
    )

    return json.loads(response.choices[0].message.content)

# Example
available = {
    "domain": ["insurance", "finance", "healthcare", "ecommerce"],
    "product_type": ["life", "health", "auto", "home"],
    "language": ["vi", "en"],
}
filters = extract_metadata_filters("Bảo hiểm nhân thọ có chi trả khi nào?", available)
# → {"domain": "insurance", "product_type": "life", "language": "vi"}
```

---

## 7. Full RAG Retrieval Pipeline

Combine all patterns into a complete pipeline.

```python
class RAGPipeline:
    """Full retrieval pipeline: rewrite → multi-query → filter → hybrid search → rerank → compress."""

    def __init__(self, searcher: HybridSearcher, embedding_fn, available_filters: dict):
        self.searcher = searcher
        self.embed = embedding_fn
        self.available_filters = available_filters

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        use_rewrite: bool = True,
        use_multi_query: bool = True,
        use_rerank: bool = True,
        use_compression: bool = True,
        alpha: float = 0.7,
    ) -> list[dict]:
        # Step 1: Query rewriting
        search_query = rewrite_query(query) if use_rewrite else query

        # Step 2: Multi-query
        queries = generate_multi_queries(search_query, n=4) if use_multi_query else [search_query]

        # Step 3: Metadata filtering
        filters = extract_metadata_filters(query, self.available_filters)

        # Step 4: Hybrid search for each query
        all_results = []
        for q in queries:
            q_vector = self.embed(q)
            results = self.searcher.search(
                query=q,
                query_vector=q_vector,
                top_k=20,
                alpha=alpha,
                metadata_filter=filters if filters else None,
            )
            all_results.append(results)

        # Step 5: Merge & deduplicate (RRF)
        merged = reciprocal_rank_fusion(all_results)[:20]

        # Step 6: Rerank
        if use_rerank and merged:
            merged = cohere_rerank(query, merged, top_n=top_k * 2)

        # Step 7: Contextual compression
        if use_compression:
            merged = compress_chunks(query, merged[:top_k * 2])

        return merged[:top_k]


# Sử dụng
pipeline = RAGPipeline(
    searcher=hybrid_searcher,
    embedding_fn=get_embedding,
    available_filters={"domain": ["insurance", "finance"]},
)

results = pipeline.retrieve("Bảo hiểm nhân thọ có chi trả khi tự tử không?")
for r in results:
    print(f"Score: {r.get('rrf_score', 'N/A')}")
    print(f"Text: {r['text'][:200]}...")
    print("---")
```
