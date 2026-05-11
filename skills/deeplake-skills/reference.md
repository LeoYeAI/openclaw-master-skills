# Deeplake Managed Service -- Reference

## pg_deeplake SQL Reference

Once data is ingested, use these SQL features:

### Vector Similarity Search (Cosine)

The `<#>` operator is overloaded by pg_deeplake -- it performs **vector cosine similarity** when applied to embedding columns and **BM25 text similarity** when applied to text columns. In both cases, higher scores = more similar, so use `ORDER BY ... DESC`.

**Note:** Unlike pgvector's `<=>` (distance, lower = closer), pg_deeplake's `<#>` returns **similarity** (higher = more similar). Always use `ORDER BY ... DESC`.

```sql
-- <#> on embedding column: cosine similarity (higher = more similar)
SELECT id, text, embedding <#> $query_embedding AS similarity
FROM documents
ORDER BY similarity DESC
LIMIT 10;
```

**Python example:**
```python
import numpy as np

query_embedding = model.encode("search query").tolist()  # Must be list, not numpy array

results = client.query("""
    SELECT id, text, embedding <#> $1 AS similarity
    FROM embeddings
    ORDER BY similarity DESC
    LIMIT 10
""", (query_embedding,))

for row in results:
    print(f"{row['similarity']:.3f}: {row['text']}")
```

### BM25 Text Search

> **Important:** Use the `<#>` operator for BM25 search. The `BM25_SIMILARITY()` function form is **not supported** on the managed query endpoint and will return a 400 error.

```sql
-- <#> on text column: BM25 text similarity (higher = more relevant)
SELECT id, text, text <#> 'search query' AS score
FROM documents
ORDER BY score DESC
LIMIT 10;
```

**Python example:**
```python
results = client.query("""
    SELECT id, text, text <#> $1 AS score
    FROM documents
    ORDER BY score DESC
    LIMIT 10
""", ("machine learning",))
```

### Full-Text Contains

```sql
-- Check if text contains keyword
SELECT * FROM documents
WHERE text @> 'important keyword';
```

### Hybrid Search (Vector + Text)

```sql
-- Combine vector and text search with weights
-- deeplake_hybrid_record(embedding, text, vector_weight, text_weight)
-- Weights: 0.7 = 70% vector similarity, 0.3 = 30% BM25 text similarity
SELECT id,
       (embedding, text)::deeplake_hybrid_record <#>
       deeplake_hybrid_record($query_embedding, 'search text', 0.7, 0.3) AS score
FROM documents
ORDER BY score DESC
LIMIT 10;
```

**Python example:**
```python
query_emb = model.encode("neural networks").tolist()
results = client.query("""
    SELECT id, text,
           (embedding, text)::deeplake_hybrid_record <#>
           deeplake_hybrid_record($1, $2, 0.7, 0.3) AS score
    FROM documents
    ORDER BY score DESC
    LIMIT 10
""", (query_emb, "neural networks"))
```

### Create Indexes for Performance

```sql
-- Vector index (speeds up similarity search)
CREATE INDEX ON documents USING deeplake_index (embedding);

-- Text index (speeds up BM25 search)
CREATE INDEX ON documents USING deeplake_index (text);
```

**Via SDK (recommended):**

```python
# Python — standalone
client.create_index("documents", "embedding")
client.create_index("documents", "text")

# Python — during ingestion
client.ingest("documents", data, index=["embedding", "text"])
```

```typescript
// Node.js — standalone
await client.createIndex("documents", "embedding");
await client.createIndex("documents", "text");

// Node.js — during ingestion
await client.ingest("documents", data, { index: ["embedding", "text"] });
```

### Raw SQL: Inserting Image Bytes

When inserting image data via raw SQL (not `client.ingest()`), use `decode()` with the `IMAGE` cast:

```sql
INSERT INTO images (id, img)
VALUES ('img_1', decode('89504e470d0a1a0a...', 'hex')::IMAGE);
```

```python
image_hex = image_bytes.hex()
client.query(
    "INSERT INTO images (id, img) VALUES ($1, decode($2, 'hex')::IMAGE)",
    ("img_1", image_hex)
)
```

### Raw SQL: Vector Literals

When using vector values as SQL literals (e.g. for benchmarking without parameterized queries):

```sql
SELECT id, text, embedding <#> ARRAY[0.1, 0.2, 0.3]::FLOAT4[] AS score
FROM documents
ORDER BY score DESC
LIMIT 10;
```

> **Tip:** For production use, prefer parameterized queries (`$1`) over literals.

---

## Data Types Reference

| Schema Type    | Python Type | JS/TS Type        | Postgres Type             | Example                 |
| -------------- | ----------- | ----------------- | ------------------------- | ----------------------- |
| `TEXT`         | str         | string            | text                      | `"hello"`               |
| `INT32`        | int         | number            | integer                   | `42`                    |
| `INT64`        | int         | number            | bigint                    | `9999999999`            |
| `FLOAT32`      | float       | number            | real                      | `3.14`                  |
| `FLOAT64`      | float       | number            | double precision          | `3.14159265359`         |
| `BOOL`         | bool        | boolean           | boolean                   | `True`                  |
| `BINARY`       | bytes       | Buffer/Uint8Array | bytea                     | `b"\x00\x01"`           |
| `IMAGE`        | bytes       | Buffer/Uint8Array | IMAGE (bytea)             | Image binary data       |
| `VIDEO`        | bytes       | Buffer/Uint8Array | bytea                     | Video binary data       |
| `EMBEDDING`    | list[float] | number[]          | float4[]                  | `[0.1, 0.2, 0.3]`       |
| `SEGMENT_MASK` | bytes       | Buffer/Uint8Array | SEGMENT_MASK (bytea)      | Segmentation mask data  |
| `BINARY_MASK`  | bytes       | Buffer/Uint8Array | BINARY_MASK (bytea)       | Binary mask data        |
| `BOUNDING_BOX` | list[float] | number[]          | BOUNDING_BOX (float4[])   | `[x, y, w, h]`          |
| `CLASS_LABEL`  | int         | number            | CLASS_LABEL (int4)        | Label index             |
| `POLYGON`      | bytes       | Buffer/Uint8Array | DEEPLAKE_POLYGON (bytea)  | Polygon coordinates     |
| `POINT`        | list[float] | number[]          | DEEPLAKE_POINT (float4[]) | `[1.0, 2.0]`            |
| `MESH`         | bytes       | Buffer/Uint8Array | MESH (bytea)              | 3D mesh data (PLY, STL) |
| `MEDICAL`      | bytes       | Buffer/Uint8Array | MEDICAL (bytea)           | Medical imaging (DICOM) |
| `FILE`         | str (path)  | string (path)     | N/A (processed)           | `"/path/to/file.mp4"`   |

> **Note:** `EMBEDDING` is a Deeplake schema type that maps to `float4[]` in PostgreSQL. pg_deeplake treats these columns specially for vector similarity search via the `<#>` operator and `deeplake_index`.
>
> **Note:** `FILE` is a schema directive, not a storage type. Columns marked as `FILE` are treated as file paths during ingestion -- the files are processed (chunked, etc.) and the resulting data is stored in generated columns. The `FILE` column itself is not stored in the dataset.
>
> **Note:** Domain types like `IMAGE`, `SEGMENT_MASK`, `BINARY_MASK`, `BOUNDING_BOX`, `CLASS_LABEL`, `DEEPLAKE_POLYGON`, `DEEPLAKE_POINT`, `MESH`, and `MEDICAL` are PostgreSQL domain types defined by pg_deeplake. They behave like their base types (bytea, float4[], int4) but carry semantic meaning for visualization, search, and type-aware processing.
>
> **Important -- IMAGE columns for UI display:** To display images correctly in the UI, explicitly set `schema={"image_col": "IMAGE"}` during ingestion. Without this, bytes columns are stored as generic `BINARY` and the UI will not render them as images.
>
> **Important -- IMAGE query results:** IMAGE columns returned via `client.query()` may come back as **base64-encoded strings** rather than raw bytes, depending on the backend serialization. Always handle both types:
> ```python
> import base64
> val = row["image"]
> if isinstance(val, str):
>     image_bytes = base64.b64decode(val)
> else:
>     image_bytes = val
> ```

**Schema inference:**
- `bool` / `boolean` -> BOOL
- `int` / `number` (integer) -> INT64
- `float` / `number` (decimal) -> FLOAT64
- `bytes` / `Buffer` -> BINARY
- `str` / `string` -> TEXT
- `list[float]` / `number[]` -> EMBEDDING (size auto-detected)

---

## Thumbnail Table Schema

When a format declares `image_columns()`, the SDK auto-generates a shared `thumbnails` dataset at `{root_path}/thumbnails` with this schema:

| Column        | Type   | Description                                  |
| ------------- | ------ | -------------------------------------------- |
| `file_id`     | TEXT   | UUID of the source row (`_id` column value)  |
| `column_name` | TEXT   | Name of the IMAGE column (e.g. `"image"`)    |
| `dimension`   | TEXT   | Thumbnail size (e.g. `"32x32"`, `"256x256"`) |
| `content`     | BINARY | JPEG thumbnail bytes (quality 85)            |

**Sizes generated:** 32x32, 64x64, 128x128, 256x256 (aspect-preserving via `Image.thumbnail()` in Python, `sharp.resize({ fit: 'inside' })` in Node.js).

---

## Limits

| Resource                     | Limit           |
| ---------------------------- | --------------- |
| Video chunk duration         | 10 seconds      |
| Text chunk size (default)    | 1000 characters |
| Text chunk overlap (default) | 200 characters  |
| PDF rendering resolution     | 150 DPI (configurable via `pdf_dpi`) |
| Batch size (data ingest)     | 1000 rows       |
| Write buffer (flush_every)   | 200 rows        |
| Commit interval              | 2000 rows       |
| File normalization workers   | 4 threads       |
| Storage I/O concurrency      | 32 operations   |

---

## Performance Tuning

The SDK uses several optimizations to handle large-scale ingestion efficiently:

**Buffered writes:** Instead of calling `ds.append()` for each small batch (e.g., one image or text chunk), rows are accumulated in a memory buffer and flushed in larger batches. This reduces Python-to-C++ FFI overhead (or JS-to-WASM overhead in Node.js).

```python
# Default: flush every 200 rows, commit every 2000 rows
client.ingest("table", files)

# These are fixed internal defaults (not configurable via ingest()):
# flush_every=200   -- rows buffered before ds.append()
# commit_every=2000 -- rows between ds.commit() calls
```

**Periodic commits:** `ds.commit()` is called every 2000 rows (default) to:
- Free C++ memory buffers
- Enable crash recovery (partial progress is persisted)
- Bound peak memory usage for very large ingestions

A final `ds.commit()` is always called after all rows are written.

**Parallel file normalization (Python only):** When ingesting multiple files, normalization (ffmpeg for video, PyMuPDF for PDFs, file I/O for images/text) runs in a thread pool (up to 4 workers). Since these operations release the GIL, threads provide real parallelism.

**Storage concurrency (Python only):** The SDK sets `deeplake.storage.set_concurrency(32)` during ingestion to parallelize S3/GCS chunk uploads, significantly improving throughput for large datasets.

| Parameter             | Default | Description                        |
| --------------------- | ------- | ---------------------------------- |
| `flush_every`         | 200     | Rows buffered before `ds.append()` |
| `commit_every`        | 2000    | Rows between `ds.commit()` calls   |
| Normalization workers | 4       | Max threads for file processing    |
| Storage concurrency   | 32      | Parallel storage I/O operations    |

---

## Troubleshooting

**"Token required" error:**
```bash
# Set the DEEPLAKE_API_KEY env var, or pass token= to Client()
export DEEPLAKE_API_KEY="dl_xxx"
```

**"Token does not contain org_id" error:**
```python
# Ensure your token contains an OrgID claim, or that the API /me endpoint
# is accessible to fall back on. All tokens should contain OrgID in their JWT payload.
```

**"ffmpeg not found" for video processing:**
```bash
# Install ffmpeg
sudo apt-get install ffmpeg
```

**"fitz not found" for PDF processing (Python):**
```bash
# Install PyMuPDF
pip install pymupdf
```

**Thumbnail generation skipped (Python):**
```bash
# Install Pillow
pip install Pillow
```

**Thumbnail generation skipped (Node.js):**
```bash
# Install sharp
npm install sharp
```

**Connection refused to API:**
```bash
# Check API server is running
curl https://api.deeplake.ai/health
```

**"workspace ID is required" when creating a workspace (HTTP 400):**
```
# POST /workspaces requires the "id" field in the request body.
# The "id" is used in API paths and al:// URLs.
# Example: { "id": "my-workspace", "name": "My Workspace" }
```

**"Not found: /workspaces/.../tables" during ingest:**
```
# The workspace must exist before calling ingest().
# Create it via the API or UI first, then ingest.
```

**Tables created via raw SQL not visible to ingest():**
```
# Tables created with raw SQL (CREATE TABLE ... USING deeplake) are not
# registered with the managed API. The SDK expects tables created via
# POST /workspaces/{id}/tables, which registers the al:// path.
# Use client.ingest() to create tables, or use client.query() for raw SQL
# operations on manually-created tables.
```

**Query timeout on large datasets:**
```python
# Python: increase timeout (default 60s)
results = client.query("SELECT COUNT(*) FROM big_table", timeout=300)
```
```typescript
// Node.js: increase timeout (default 60s)
const rows = await client.query("SELECT COUNT(*) FROM big", undefined, { timeoutMs: 300_000 });
```

**Note:** All database operations (query, list_tables, drop_table, create_table) go through the REST API. No direct PostgreSQL connection is needed from the Python or Node.js client.
