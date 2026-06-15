---
name: "milvus"
version: "1.0.0"
description: "Operate Milvus vector database with pymilvus — collections, vector search, hybrid search, indexes, RBAC, partitions, and more via Python code."
tags: ["milvus", "vector-database", "pymilvus", "semantic-search", "rag", "embeddings"]
metadata:
  openclaw:
    emoji: "\U0001F9E0"
    homepage: "https://github.com/milvus-io/pymilvus"
    primaryEnv: "MILVUS_URI"
    requires:
      bins:
        - python3
      os:
        - darwin
        - linux
    install:
      - kind: uv
        package: pymilvus
        bins: []
---

# Milvus Vector Database Skill

Operate [Milvus](https://milvus.io/) vector databases directly through Python code using the `pymilvus` SDK. This skill covers the full lifecycle — connecting, schema design, collection management, vector CRUD, search, hybrid search, indexing, partitions, databases, and RBAC.

## When to Use

Use this skill when the user wants to:
- Connect to a Milvus instance (local, standalone, cluster, or Milvus Lite)
- Create collections with custom schemas
- Insert, upsert, search, query, get, or delete vectors
- Perform hybrid search with reranking
- Manage indexes, partitions, databases
- Set up users, roles, and access control (RBAC)
- Build RAG pipelines, semantic search, or recommendation systems with Milvus

## Requirements

- Python 3.8+
- `pymilvus` (`pip install pymilvus`)
- A running Milvus instance, or use Milvus Lite (embedded, file-based) for development

## Capabilities Overview

| Area | What You Can Do |
|------|----------------|
| **Connection** | Connect to Milvus Lite, Standalone, Cluster, or Zilliz Cloud |
| **Collections** | Create (quick or custom schema), list, describe, drop, rename, load, release |
| **Vectors** | Insert, upsert, search, hybrid search, query, get, delete |
| **Indexes** | Create (AUTOINDEX, HNSW, IVF_FLAT, etc.), list, describe, drop |
| **Partitions** | Create, list, load, release, drop |
| **Databases** | Create, list, switch, drop |
| **RBAC** | Users, roles, privileges management |

---

# Connection

```python
from pymilvus import MilvusClient

# Milvus Lite (embedded, file-based — great for dev/test)
client = MilvusClient(uri="./milvus_demo.db")

# Standalone / Cluster Milvus
client = MilvusClient(uri="http://localhost:19530", token="root:Milvus")

# Zilliz Cloud
client = MilvusClient(
    uri="https://in03-xxxx.api.gcp-us-west1.zillizcloud.com:19530",
    token="your_api_key"
)
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `uri` | str | `"./file.db"` for Milvus Lite, `"http://host:19530"` for server |
| `token` | str | API key or `"username:password"` |
| `user` | str | Username (alternative to token) |
| `password` | str | Password (alternative to token) |
| `db_name` | str | Target database (default: `"default"`) |
| `timeout` | float | Operation timeout in seconds |

### Async Client

```python
from pymilvus import AsyncMilvusClient

async with AsyncMilvusClient(uri="http://localhost:19530") as client:
    results = await client.search(...)
```

---

# Collection Management

## Quick Create (auto schema + auto index + auto load)

```python
client.create_collection(
    collection_name="my_collection",
    dimension=768,
    metric_type="COSINE"  # Optional: "COSINE" (default), "L2", "IP"
)
```

This automatically creates:
- `id` field (INT64, primary key, auto_id)
- `vector` field (FLOAT_VECTOR, dim=dimension)
- AUTOINDEX on vector field
- Collection is auto-loaded

## Custom Schema Create

```python
from pymilvus import DataType

# Step 1: Define schema
schema = client.create_schema(auto_id=False, enable_dynamic_field=True)
schema.add_field("id", DataType.INT64, is_primary=True)
schema.add_field("text", DataType.VARCHAR, max_length=512)
schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=768)

# Step 2: Define index
index_params = client.prepare_index_params()
index_params.add_index(
    field_name="embedding",
    index_type="AUTOINDEX",
    metric_type="COSINE"
)

# Step 3: Create collection
client.create_collection(
    collection_name="my_collection",
    schema=schema,
    index_params=index_params
)
```

### Supported Data Types

**Scalar types:**

| DataType | Notes |
|----------|-------|
| `DataType.BOOL` | Boolean |
| `DataType.INT8` / `INT16` / `INT32` / `INT64` | Integers |
| `DataType.FLOAT` / `DOUBLE` | Floating point |
| `DataType.VARCHAR` | String (requires `max_length`) |
| `DataType.JSON` | JSON object |
| `DataType.ARRAY` | Array (requires `element_type`, `max_capacity`) |

**Vector types:**

| DataType | Notes |
|----------|-------|
| `DataType.FLOAT_VECTOR` | Float32 vector (requires `dim`) |
| `DataType.FLOAT16_VECTOR` | Float16 vector (requires `dim`) |
| `DataType.BFLOAT16_VECTOR` | BFloat16 vector (requires `dim`) |
| `DataType.BINARY_VECTOR` | Binary vector (requires `dim`) |
| `DataType.SPARSE_FLOAT_VECTOR` | Sparse vector (no `dim` needed) |

### add_field Parameters

```python
schema.add_field(
    field_name="my_field",
    datatype=DataType.VARCHAR,
    is_primary=False,
    auto_id=False,
    max_length=256,          # Required for VARCHAR
    dim=768,                 # Required for vector types (except sparse)
    element_type=DataType.INT64,  # Required for ARRAY
    max_capacity=100,        # Required for ARRAY
    nullable=False,
    default_value=None,
    is_partition_key=False,
    description=""
)
```

## Other Collection Operations

```python
# List all collections
collections = client.list_collections()

# Describe a collection
info = client.describe_collection(collection_name="my_collection")

# Check if collection exists
exists = client.has_collection(collection_name="my_collection")

# Rename a collection
client.rename_collection(old_name="old_name", new_name="new_name")

# Drop a collection
client.drop_collection(collection_name="my_collection")

# Load collection into memory (required before search/query)
client.load_collection(collection_name="my_collection")

# Release collection from memory
client.release_collection(collection_name="my_collection")

# Get load state
state = client.get_load_state(collection_name="my_collection")

# Get collection statistics
stats = client.get_collection_stats(collection_name="my_collection")
```

### Collection Guidance

- Quick create is best for prototyping; use custom schema for production.
- A collection must be **loaded** before search or query operations.
- Before dropping a collection, confirm with the user — this deletes all data.
- Use `enable_dynamic_field=True` to allow inserting fields not defined in the schema.

---

# Vector Operations

Target collection must exist and be loaded.

## Insert

```python
data = [
    {"id": 1, "text": "AI advances", "embedding": [0.1, 0.2, ...]},
    {"id": 2, "text": "ML basics", "embedding": [0.3, 0.4, ...]},
]
res = client.insert(collection_name="my_collection", data=data)
# Returns: {"insert_count": 2, "ids": [1, 2]}
```

## Upsert (insert or update if PK exists)

```python
res = client.upsert(collection_name="my_collection", data=data)
# Returns: {"upsert_count": 2}
```

## Search (vector similarity)

```python
results = client.search(
    collection_name="my_collection",
    data=[[0.1, 0.2, ...]],           # List of query vectors
    anns_field="embedding",             # Vector field name
    limit=10,                           # Top-K
    output_fields=["text", "id"],       # Fields to return
    filter='age > 20 and status == "active"',  # Optional scalar filter
    search_params={
        "metric_type": "COSINE",
        "params": {"nprobe": 10}        # Index-specific params
    }
)
# Returns: List[List[dict]]
# Each hit: {"id": ..., "distance": ..., "entity": {"text": ...}}
```

## Hybrid Search (multi-vector with reranking)

```python
from pymilvus import AnnSearchRequest, RRFRanker, WeightedRanker

req1 = AnnSearchRequest(
    data=[[0.1, 0.2, ...]],
    anns_field="dense_embedding",
    param={"metric_type": "COSINE", "params": {"nprobe": 10}},
    limit=10
)
req2 = AnnSearchRequest(
    data=[{1: 0.5, 100: 0.3}],          # Sparse vector
    anns_field="sparse_embedding",
    param={"metric_type": "IP"},
    limit=10
)

# RRF reranking
results = client.hybrid_search(
    collection_name="my_collection",
    reqs=[req1, req2],
    ranker=RRFRanker(k=60),
    limit=10,
    output_fields=["text"]
)

# Or weighted reranking
results = client.hybrid_search(
    collection_name="my_collection",
    reqs=[req1, req2],
    ranker=WeightedRanker(0.7, 0.3),
    limit=10
)
```

## Query (filter-based retrieval)

```python
results = client.query(
    collection_name="my_collection",
    filter='id in [1, 2, 3]',
    output_fields=["text", "embedding"],
    limit=100
)
```

## Get (by primary key)

```python
results = client.get(
    collection_name="my_collection",
    ids=[1, 2, 3],
    output_fields=["text"]
)
```

## Delete

```python
# By primary keys
client.delete(collection_name="my_collection", ids=[1, 2, 3])

# By filter expression
client.delete(collection_name="my_collection", filter='status == "obsolete"')
```

## Filter Expression Syntax

| Expression | Example |
|---|---|
| Comparison | `age > 20` |
| Equality | `status == "active"` |
| IN list | `id in [1, 2, 3]` |
| AND/OR | `age > 20 and status == "active"` |
| String match | `text like "hello%"` |
| Array contains | `ARRAY_CONTAINS(tags, "ml")` |
| JSON field | `json_field["key"] > 100` |
| Match all | `id > 0` |

### Vector Guidance

- The `data` parameter in search must match the collection's vector dimension exactly.
- For text-to-vector search, convert text to vectors using an embedding model first.
- For large inserts, batch data into chunks (e.g., 1000 rows per batch).
- Always specify `output_fields` to control which fields are returned.

---

# Index Management

## Create Index

```python
index_params = client.prepare_index_params()

# Vector index
index_params.add_index(
    field_name="embedding",
    index_type="HNSW",               # See index types table below
    metric_type="COSINE",            # "COSINE", "L2", "IP"
    params={"M": 16, "efConstruction": 256}
)

# Optional: scalar index
index_params.add_index(
    field_name="text",
    index_type=""                    # Auto-select for scalars
)

client.create_index(
    collection_name="my_collection",
    index_params=index_params
)
```

### Common Index Types

| Index Type | For | Key Params | Notes |
|------------|-----|------------|-------|
| `AUTOINDEX` | Dense vectors | Auto-tuned | Recommended for most cases |
| `FLAT` | Dense vectors | None | Brute force, 100% recall |
| `IVF_FLAT` | Dense vectors | `nlist` | Good balance |
| `IVF_SQ8` | Dense vectors | `nlist` | Compressed, less memory |
| `HNSW` | Dense vectors | `M`, `efConstruction` | High recall, more memory |
| `DISKANN` | Dense vectors | None | Disk-based, large datasets |
| `SPARSE_INVERTED_INDEX` | Sparse vectors | `drop_ratio_build` | For sparse vectors |
| `SPARSE_WAND` | Sparse vectors | `drop_ratio_build` | Faster sparse search |

### Metric Types

| Metric | Description | Use With |
|--------|-------------|----------|
| `"COSINE"` | Cosine similarity (larger = more similar) | Dense vectors |
| `"L2"` | Euclidean distance (smaller = more similar) | Dense vectors |
| `"IP"` | Inner product (larger = more similar) | Dense & Sparse vectors |

## Other Index Operations

```python
# List indexes
indexes = client.list_indexes(collection_name="my_collection")

# Describe an index
info = client.describe_index(collection_name="my_collection", index_name="my_index")

# Drop an index
client.drop_index(collection_name="my_collection", index_name="my_index")
```

### Index Guidance

- `AUTOINDEX` is recommended for most use cases.
- An index is required before loading a collection.
- After creating an index, load the collection before searching.
- Sparse vectors only support `"IP"` metric type.

---

# Partition Management

```python
# Create a partition
client.create_partition(collection_name="my_collection", partition_name="partition_A")

# List partitions
partitions = client.list_partitions(collection_name="my_collection")
# Returns: ["_default", "partition_A"]

# Check if partition exists
exists = client.has_partition(collection_name="my_collection", partition_name="partition_A")

# Load specific partitions
client.load_partitions(collection_name="my_collection", partition_names=["partition_A"])

# Release specific partitions
client.release_partitions(collection_name="my_collection", partition_names=["partition_A"])

# Drop a partition
client.drop_partition(collection_name="my_collection", partition_name="partition_A")
```

### Partition Guidance

- Every collection has a `_default` partition.
- Use `is_partition_key=True` on a field to enable automatic partitioning by field value.
- A partition must be loaded before search.
- Before dropping a partition, confirm with the user — all data in it will be deleted.

---

# Database Management

```python
# Create a database
client.create_database(db_name="my_database")

# List all databases
databases = client.list_databases()
# Returns: ["default", "my_database"]

# Switch to a database
client.using_database(db_name="my_database")

# Drop a database (must drop all collections first)
client.drop_database(db_name="my_database")

# Or connect to a specific database at init
client = MilvusClient(uri="http://localhost:19530", db_name="my_database")
```

### Database Guidance

- Every Milvus instance has a `"default"` database.
- Before dropping a database, all collections in it must be dropped first.

---

# User & Role Management (RBAC)

## User Operations

```python
# Create a user
client.create_user(user_name="analyst", password="SecureP@ss123")

# List users
users = client.list_users()

# Describe a user (shows assigned roles)
info = client.describe_user(user_name="analyst")

# Update password
client.update_password(user_name="analyst", old_password="SecureP@ss123", new_password="NewP@ss456")

# Grant role to user
client.grant_role(user_name="analyst", role_name="read_only")

# Revoke role from user
client.revoke_role(user_name="analyst", role_name="read_only")

# Drop a user
client.drop_user(user_name="analyst")
```

## Role Operations

```python
# Create a role
client.create_role(role_name="read_only")

# List roles
roles = client.list_roles()

# Grant privilege (v2 API — recommended)
client.grant_privilege_v2(
    role_name="read_only",
    privilege="Search",                 # e.g., "Search", "Insert", "Query", "Delete"
    collection_name="my_collection",    # Use "*" for all collections
    db_name="default"                   # Use "*" for all databases
)

# Built-in privilege groups
client.grant_privilege_v2(
    role_name="admin_role",
    privilege="ClusterAdmin",           # See privilege groups below
    collection_name="*",
    db_name="*"
)

# Revoke privilege
client.revoke_privilege_v2(
    role_name="read_only",
    privilege="Search",
    collection_name="my_collection",
    db_name="default"
)

# Describe role (see granted privileges)
info = client.describe_role(role_name="read_only")

# Drop a role
client.drop_role(role_name="read_only")
```

### Built-in Privilege Groups

| Group | Scope |
|-------|-------|
| `ClusterAdmin` | Full cluster access |
| `ClusterReadOnly` | Read-only cluster access |
| `ClusterReadWrite` | Read-write cluster access |
| `DatabaseAdmin` | Full database access |
| `DatabaseReadOnly` | Read-only database access |
| `DatabaseReadWrite` | Read-write database access |
| `CollectionAdmin` | Full collection access |
| `CollectionReadOnly` | Read-only collection access |
| `CollectionReadWrite` | Read-write collection access |

### Common Individual Privileges

`Search`, `Query`, `Insert`, `Delete`, `Upsert`, `CreateIndex`, `DropIndex`, `CreateCollection`, `DropCollection`, `Load`, `Release`, `CreatePartition`, `DropPartition`

### RBAC Guidance

- Recommended workflow: create role → grant privileges → create user → assign role.
- Use `"*"` for collection_name/db_name to grant on all resources.
- Before dropping a user or role, confirm with the user.

---

# Common Patterns

## RAG Pipeline Pattern

```python
from pymilvus import MilvusClient, DataType

# 1. Connect
client = MilvusClient(uri="http://localhost:19530")

# 2. Create collection
schema = client.create_schema(auto_id=True, enable_dynamic_field=True)
schema.add_field("id", DataType.INT64, is_primary=True)
schema.add_field("text", DataType.VARCHAR, max_length=2048)
schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=768)
schema.add_field("source", DataType.VARCHAR, max_length=256)

index_params = client.prepare_index_params()
index_params.add_index(field_name="embedding", index_type="AUTOINDEX", metric_type="COSINE")

client.create_collection(collection_name="knowledge_base", schema=schema, index_params=index_params)

# 3. Insert documents (after embedding with your model)
client.insert("knowledge_base", data=[
    {"text": "chunk text...", "embedding": [...], "source": "doc1.pdf"},
])

# 4. Retrieve relevant context
results = client.search(
    collection_name="knowledge_base",
    data=[query_embedding],
    limit=5,
    output_fields=["text", "source"],
    search_params={"metric_type": "COSINE"}
)
```

## Quick Semantic Search Pattern

```python
# Simplest possible setup
client = MilvusClient(uri="./search.db")
client.create_collection(collection_name="docs", dimension=768)
client.insert("docs", data=[{"id": i, "vector": emb, "text": txt} for i, (emb, txt) in enumerate(zip(embeddings, texts))])
results = client.search("docs", data=[query_vector], limit=10, output_fields=["text"])
```

---

# General Guidance

- Always check if pymilvus is installed: `pip install pymilvus`.
- For quick prototyping, use **Milvus Lite** (`uri="./file.db"`) — no server needed.
- A collection must be **loaded into memory** before search/query.
- The vector dimension in search data must **exactly match** the collection schema.
- For text queries, users need an **embedding model** to convert text to vectors first. Suggest `pymilvus[model]` for built-in embedding support.
- Before any destructive operation (drop collection, drop database, delete vectors), always confirm with the user.
- Use `enable_dynamic_field=True` when the schema may evolve.
- For large-scale inserts, batch data into chunks of ~1000 rows.
- Prefer `AUTOINDEX` unless the user has specific performance requirements.
