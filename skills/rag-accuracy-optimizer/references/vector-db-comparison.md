# Vector Database — Detailed Comparison

## Overview

Choosing a vector DB depends on: **scale** (how many vectors), **deployment** (cloud vs self-host), **features** (hybrid search, filtering), and **budget**.

---

## Vector DB Comparison

### Pinecone

| Attribute | Value |
|---|---|
| Type | Managed cloud only |
| Max dimensions | 20,000 |
| Index type | Proprietary (dựa trên graph-based ANN) |
| Hybrid search | ✅ Sparse-dense vectors |
| Metadata filtering | ✅ Mạnh (số, text, list, boolean) |
| Namespaces | ✅ Partition data trong cùng index |
| Pricing | Free tier: 2GB, 100K vectors. Starter: $70/mo |
| Latency | ~50-100ms (p50) |
| Throughput | ~200 QPS (standard pod) |

**Pros:** Zero-ops, scale tự động, API đơn giản, metadata filtering mạnh, sparse-dense hybrid native.
**Cons:** Vendor lock-in, không self-host, đắt khi scale, không có full-text search.

```python
from pinecone import Pinecone

pc = Pinecone(api_key="xxx")
index = pc.Index("my-index")

# Upsert
index.upsert(vectors=[
    {"id": "doc1", "values": [0.1, 0.2, ...], "metadata": {"domain": "insurance"}}
])

# Query with metadata filter
results = index.query(
    vector=[0.1, 0.2, ...],
    top_k=10,
    filter={"domain": {"$eq": "insurance"}},
    include_metadata=True
)
```

### Qdrant

| Attribute | Value |
|---|---|
| Type | Self-host (Rust) + Qdrant Cloud |
| Max dimensions | 65,536 |
| Index type | HNSW (tunable) |
| Hybrid search | ✅ Sparse vectors + dense |
| Metadata filtering | ✅ Rất mạnh (nested, geo, datetime) |
| Multi-vector | ✅ Named vectors |
| Pricing | Self-host: Free. Cloud: từ $25/mo |
| Latency | ~10-50ms (self-host) |
| Throughput | ~500-1000 QPS (tuned) |

**Pros:** Rust performance, HNSW tuning chi tiết, multi-vector (nhiều embedding cho 1 point), filtering mạnh, self-host miễn phí, active community.
**Cons:** Cần ops nếu self-host, cloud pricing tăng nhanh theo storage.

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient(host="localhost", port=6333)

# Create collection với HNSW tuning
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1024,
        distance=Distance.COSINE,
        hnsw_config={
            "m": 16,             # Connections per node
            "ef_construct": 200,  # Construction quality
        }
    )
)

# Search với HNSW ef tuning
results = client.search(
    collection_name="documents",
    query_vector=[0.1, 0.2, ...],
    limit=10,
    search_params={"hnsw_ef": 128}  # Runtime search quality
)
```

### Weaviate

| Attribute | Value |
|---|---|
| Type | Self-host (Go) + Weaviate Cloud |
| Index type | HNSW (default), Flat, Dynamic |
| Hybrid search | ✅ BM25 + vector native |
| Modules | Vectorizer, reranker, generative built-in |
| GraphQL API | ✅ |
| Multi-tenancy | ✅ |
| Pricing | Self-host: Free. Cloud: từ $25/mo |
| Latency | ~20-80ms |

**Pros:** Built-in hybrid search (BM25 + vector), module ecosystem (auto-vectorize, auto-rerank), GraphQL API, multi-tenancy cho SaaS.
**Cons:** Go performance < Rust (Qdrant), module system phức tạp, memory usage cao.

```python
import weaviate

client = weaviate.connect_to_local()

# Hybrid search (BM25 + vector tự động)
collection = client.collections.get("Document")
response = collection.query.hybrid(
    query="bảo hiểm nhân thọ chi trả",
    alpha=0.7,  # 0=pure BM25, 1=pure vector
    limit=10,
    return_metadata=["score", "explain_score"]
)
```

### pgvector (PostgreSQL Extension)

| Attribute | Value |
|---|---|
| Type | PostgreSQL extension |
| Index type | IVFFlat, HNSW |
| Max dimensions | 2,000 |
| Hybrid search | ✅ (kết hợp với pg full-text search) |
| SQL queries | ✅ Full PostgreSQL |
| Pricing | Free (part of PostgreSQL) |
| Latency | ~20-100ms (tuned HNSW) |

**Pros:** Dùng luôn PostgreSQL hiện có, SQL đầy đủ, JOIN với business data, transaction support, không cần thêm infra.
**Cons:** Scale hạn chế (OK đến ~5M vectors), max 2000 dimensions, performance kém hơn DB chuyên dụng ở scale lớn.

```sql
-- Enable extension
CREATE EXTENSION vector;

-- Create table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    metadata JSONB,
    embedding vector(1024)
);

-- Create HNSW index
CREATE INDEX ON documents USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 200);

-- Search
SELECT id, content, metadata,
       1 - (embedding <=> '[0.1, 0.2, ...]'::vector) AS similarity
FROM documents
WHERE metadata->>'domain' = 'insurance'
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;

-- Hybrid: vector + full-text search
SELECT id, content,
       ts_rank(to_tsvector('simple', content), plainto_tsquery('simple', 'bảo hiểm')) AS bm25_score,
       1 - (embedding <=> query_embedding) AS vector_score
FROM documents
ORDER BY 0.7 * (1 - (embedding <=> query_embedding)) + 0.3 * ts_rank(...) DESC
LIMIT 10;
```

### ChromaDB

| Attribute | Value |
|---|---|
| Type | Embedded (Python) + Client-Server |
| Index type | HNSW (hnswlib) |
| Hybrid search | ❌ (chỉ vector + metadata filter) |
| Persistent storage | ✅ SQLite + Parquet |
| Pricing | Free & open-source |
| Latency | ~10-30ms (embedded) |

**Pros:** Đơn giản nhất, `pip install chromadb` là chạy, tốt cho prototype/POC, embedding tự động (tích hợp sentence-transformers).
**Cons:** Không có BM25/hybrid search, scale hạn chế (~1M vectors), không production-grade cho workload lớn.

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:M": 16, "hnsw:construction_ef": 200}
)

# Add (auto-embed nếu có embedding function)
collection.add(
    documents=["Bảo hiểm nhân thọ chi trả..."],
    metadatas=[{"domain": "insurance"}],
    ids=["doc1"]
)

# Query
results = collection.query(
    query_texts=["bảo hiểm chi trả khi nào?"],
    n_results=10,
    where={"domain": "insurance"}
)
```

---

## Summary Comparison Table

| Feature | Pinecone | Qdrant | Weaviate | pgvector | ChromaDB |
|---|---|---|---|---|---|
| Self-host | ❌ | ✅ | ✅ | ✅ | ✅ |
| Cloud managed | ✅ | ✅ | ✅ | ✅ (RDS) | ❌ |
| Hybrid search | Sparse-dense | Sparse-dense | BM25+vector | FTS+vector | ❌ |
| Max scale | Billions | Billions | Billions | ~5-10M | ~1M |
| HNSW tuning | ❌ | ✅ Full | ✅ Partial | ✅ Partial | ✅ Basic |
| Multi-vector | ❌ | ✅ | ❌ | ❌ | ❌ |
| Multi-tenancy | Namespaces | ✅ | ✅ | Schemas | Collections |
| SQL/JOIN | ❌ | ❌ | ❌ | ✅ Full | ❌ |
| Learning curve | Thấp | Trung bình | Cao | Thấp (nếu biết SQL) | Rất thấp |
| **Best for** | Production SaaS | Performance-critical | Feature-rich apps | Existing PG stack | POC/Prototype |

---

## HNSW Index Tuning

HNSW (Hierarchical Navigable Small World) is the most popular indexing algorithm. 3 main params:

### Parameters

| Param | Meaning | Default | Range | Trade-off |
|---|---|---|---|---|
| **M** | Connections per node | 16 | 4-64 | Higher → better recall, more RAM |
| **ef_construction** | Search width when building index | 200 | 100-500 | Higher → better index quality, slower build |
| **ef** (search) | Search width when querying | 100 | 50-500 | Higher → better recall, slower queries |

### Tuning Guidelines

```
Scale nhỏ (<100K vectors):
  M=16, ef_construction=200, ef=100 (defaults OK)

Scale trung bình (100K-10M vectors):
  M=32, ef_construction=256, ef=128

Scale lớn (>10M vectors):
  M=48, ef_construction=400, ef=200
  → Test recall@10 vs latency, tune ef theo SLA

Accuracy-critical (y tế, pháp lý):
  M=64, ef_construction=500, ef=256
  → Chấp nhận latency cao hơn để recall >99%
```

### Benchmark Example

```
Dataset: 1M vectors, dim=1024
Hardware: 32GB RAM, 8 cores

| Config | Build time | RAM | Recall@10 | Latency (p50) |
|--------|-----------|------|-----------|---------------|
| M=16, ef_c=200 | 45 min | 4.2 GB | 95.3% | 12ms |
| M=32, ef_c=256 | 72 min | 6.8 GB | 97.8% | 18ms |
| M=48, ef_c=400 | 120 min | 9.5 GB | 99.1% | 28ms |
```

### RAM Estimation

```
RAM per vector ≈ dim × 4 bytes (float32) + M × 8 bytes (connections) + metadata
Example: 1M vectors × 1024 dim × M=32
  = 1M × (4096 + 256 + ~200) bytes
  ≈ 4.3 GB
```

---

## Vector DB Selection Guide

### Decision Tree

```
Đã có PostgreSQL và <5M vectors?
├── Có → pgvector (ít infra nhất)
└── Không
    ├── Chỉ prototype/POC? → ChromaDB
    ├── Production, muốn zero-ops? → Pinecone
    ├── Cần performance + control? → Qdrant
    └── Cần hybrid search + modules? → Weaviate
```

### Common Migration Path

```
POC: ChromaDB (đơn giản nhất)
  → MVP: pgvector (thêm SQL queries)
  → Scale: Qdrant/Pinecone (performance)
```

### Cost Comparison (1M vectors, 1024 dim)

| DB | Monthly Cost | Notes |
|---|---|---|
| ChromaDB | $0 (local) | Compute cost only |
| pgvector | $0-50 | Depends on PG hosting |
| Qdrant (self-host) | $0-30 | Depends on VM size |
| Qdrant Cloud | ~$50-100 | Managed |
| Weaviate Cloud | ~$50-100 | Managed |
| Pinecone | ~$70-140 | Managed, pod-based |
