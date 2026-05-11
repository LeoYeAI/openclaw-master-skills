---
name: deeplake-managed
description: SDK for ingesting data into Deeplake managed tables. Use when users want to store, ingest, or query data in Deeplake.
allowed-tools: Bash, Read, Write, Edit, Glob, Grep, WebFetch
metadata:
  openclaw:
    requires:
      env:
        - DEEPLAKE_API_KEY
    primaryEnv: DEEPLAKE_API_KEY
    homepage: https://github.com/activeloopai/deeplake-skills
---

# Deeplake Managed Service SDK

> Agent-friendly SDK for ingesting data into Deeplake managed tables.
> Use this skill when users want to store, ingest, or query data in Deeplake.
> Available in both **Python** and **Node.js/TypeScript**.

---

## Quick Reference

### Python

```bash
pip install deeplake # uv add deeplake 
```

**Python import (primary):**
```python
from deeplake import Client

# Async variant (requires aiohttp: pip install aiohttp):
from deeplake.managed import AsyncClient
```


```python
from deeplake import Client

# Initialize -- token from DEEPLAKE_API_KEY env var, workspace defaults to "default"
client = Client()
client = Client(token="dl_xxx", workspace_id="my-workspace")

# Ingest files (FILE schema)
client.ingest("videos", {"path": ["video1.mp4", "video2.mp4"]}, schema={"path": "FILE"})

# Ingest structured data with indexes for search
client.ingest("embeddings", {
    "text": ["doc1", "doc2", "doc3"],
    "embedding": [[0.1, 0.2, ...], [0.3, 0.4, ...], [0.5, 0.6, ...]],
}, index=["embedding", "text"])

# Ingest from HuggingFace
client.ingest("cifar", {"_huggingface": "cifar10"})

# Ingest with format object (see formats.md for CocoPanoptic, Coco, LeRobot, custom)
client.ingest("table", format=my_format)

# Fluent query
results = client.table("videos").select("id", "text").where("file_id = $1", "abc").limit(10)()

# Raw SQL
results = client.query("SELECT * FROM videos LIMIT 10")

# Vector similarity search
results = client.query("""
    SELECT id, text, embedding <#> $1 AS similarity
    FROM embeddings ORDER BY similarity DESC LIMIT 10
""", (query_embedding,))

# Table management
client.list_tables()
client.drop_table("old_table")
client.create_index("embeddings", "embedding")
```

### Node.js / TypeScript

```
npm install deeplake
```

**TypeScript import:**
```typescript
import { ManagedClient, initializeWasm } from 'deeplake';
```

**WASM initialization (required before any operations):**
```typescript
await initializeWasm();
```
Call `initializeWasm()` once at startup before any `ManagedClient` operations (ingest, query, etc.). It initializes the underlying WASM module.


```typescript
import { ManagedClient, initializeWasm } from 'deeplake';

await initializeWasm();

const client = new ManagedClient({ token: 'dl_xxx', workspaceId: 'my-workspace' });

// Ingest files (FILE schema)
await client.ingest("videos", { path: ["video1.mp4"] }, { schema: { path: "FILE" } });

// Ingest structured data
await client.ingest("embeddings", {
    text: ["doc1", "doc2"],
    embedding: [[0.1, 0.2], [0.3, 0.4]],
});

// Ingest with format object (see formats.md)
await client.ingest("table", null, { format: myFormat });

// Fluent query (use .execute())
const results = await client.table("videos")
    .select("id", "text").where("file_id = $1", "abc").limit(10).execute();

// Raw SQL
const rows = await client.query("SELECT * FROM videos LIMIT 10");

// Table management
await client.listTables();
await client.dropTable("old_table");
await client.createIndex("embeddings", "embedding");
```

---

## Dependancies and Prerequisite

**Required services:**
- Deeplake API server running (default: `https://api.deeplake.ai`)

**Optional python dependencies (per file type):**
- Video ingestion: `ffmpeg` (`sudo apt-get install ffmpeg`)
- PDF ingestion: `pymupdf` (`pip install pymupdf`)
- Thumbnail generation: `Pillow` (`pip install Pillow`)
- COCO detection format: `pycocotools`, `Pillow`, `numpy` (`pip install pycocotools Pillow numpy`)
- LeRobot frames format: `pandas`, `numpy` (`pip install pandas numpy`)

**Optional typescript dependencies (per file type):**
- Video ingestion: `ffmpeg` (system binary)
- PDF ingestion: `pdfjs-dist` (`npm install pdfjs-dist`)
- Thumbnail generation: `sharp` (`npm install sharp`)
- COCO detection format: no external deps (pure JS mask rendering)

## Architecture

```
Python:  Client(token, workspace_id)
Node.js: ManagedClient({ token, workspaceId })
  |-- .ingest(table, data)       -> creates PG table via API, opens al://{ws}/{table}
  |                                 via deeplake SDK (auto credential rotation)
  |-- .query(sql)                -> POST /workspaces/{id}/tables/query -> list[dict] / QueryRow[]
  |-- .table(table)...           -> fluent SQL builder -> list[dict] / QueryRow[]
  |-- .create_index(table, col)  -> CREATE INDEX USING deeplake_index (for search)
  |-- .open_table(table)         -> deeplake.open("al://{ws}/{table}") with auto creds
  |-- .list_tables()             -> GET /workspaces/{id}/tables -> list[str] / string[]
  `-- .drop_table(table)         -> DELETE /workspaces/{id}/tables/{name}
                    |
                    v
              REST API -> PostgreSQL + pg_deeplake
  - All DB operations go through the REST API (no direct PG connection)
  - Dataset access uses al:// paths with automatic credential resolution
  - Creds endpoint: GET /api/org/{workspace}/ds/{table}/creds
  - Vector similarity: embedding <#> query_vec
  - BM25 text search:  text <#> 'search query'
  - Hybrid search:     (embedding, text)::deeplake_hybrid_record
```

---

## Client Initialization

### Python

```python
from deeplake import Client

client = Client(
    token: str = None,           # API token (falls back to DEEPLAKE_API_KEY env var)
    workspace_id: str = "default",  # Target workspace (default: "default")
    api_url: str = None,         # API URL (default: https://api.deeplake.ai)
)
```

### Node.js / TypeScript

```typescript
import { ManagedClient, initializeWasm } from 'deeplake';

await initializeWasm();

const client = new ManagedClient({
    token: string,               // API token (required)
    workspaceId?: string,        // Target workspace (default: "default")
    apiUrl?: string,             // API URL (default: https://api.deeplake.ai)
});
```

**Token:** Create API tokens from the Deeplake platform at `https://app.deeplake.ai/<org_name>/workspace/<workspace>/apitoken`. The token is a JWT with `org_id` embedded. Falls back to the `DEEPLAKE_API_KEY` environment variable (Python only).

**Backend endpoint:** The client sets the C++ backend endpoint to `api_url` before each dataset open (not on initialization) so that `al://` path resolution (credential fetching) goes through deeplake-api instead of the legacy controlplane. This avoids global state clobbering when multiple clients use different API URLs. Python: `deeplake.client.endpoint = api_url`. Node.js: `deeplakeSetEndpoint(apiUrl)`.

**Connection lifecycle:**
```python
# Python: just create and use -- no connection to manage
client = Client()
client.ingest("table", {"path": ["file.txt"]}, schema={"path": "FILE"})
# No close() method -- client is stateless (REST API calls only)
```

---

## Ingestion

### Python: client.ingest()

```python
result = client.ingest(
    table_name: str,                    # Table name to create (must not already exist)
    data: dict[str, list] = None,       # Data dict (required unless format= is set).
                                        #   {"_huggingface": "name"} -> HuggingFace dataset
                                        #   schema has "FILE" cols -> file paths processed
                                        #   otherwise -> column data {col: [values]}
    *,
    format: Format = None,              # Format object (subclass of Format) with
                                        #   normalize() method. When set, data is ignored.
                                        #   e.g. CocoPanoptic(images_dir=..., ...)
    schema: dict[str, str] = None,      # Schema override {col: type}
                                        #   Use "FILE" for columns containing file paths
                                        #   See reference.md for all type names
    index: list[str] = None,            # Columns to create deeplake_index on after ingestion.
                                        #   Use for EMBEDDING (vector search) and TEXT (BM25) columns.
    on_progress: Callable = None,       # Progress callback(rows_written, total)
    chunk_size: int = 1000,             # Text chunk size (chars)
    chunk_overlap: int = 200,           # Text chunk overlap (chars)
    pdf_dpi: int = 150,                 # PDF render DPI (higher = sharper but slower)
) -> dict
```

### Node.js: client.ingest()

```typescript
const result = await client.ingest(
    tableName: string,                              // Table name
    data?: Record<string, unknown[]> | null,        // Data dict (or null when using format)
    options?: {
        format?: Format,                            // Format object with normalize()
        schema?: Record<string, string>,            // Schema override
        index?: string[],                           // Columns to create deeplake_index on
        onProgress?: (processed, total) => void,    // Progress callback
        chunkSize?: number,                         // Text chunk size (default 1000)
        chunkOverlap?: number,                      // Text chunk overlap (default 200)
    },
): Promise<IngestResult>
```

**Table existence:** If `table_name` already exists, `ingest()` appends data to the existing table — it does NOT drop and recreate it. To replace an existing table, call `client.drop_table(table_name)` first. The PG table schema must be compatible with the new data being appended.

**Returns:** `{"table_name": "videos", "row_count": 150, "dataset_path": "al://workspace_id/videos"}`

**Both `data` and `format`:** If both are provided, `format` takes precedence and `data` is ignored. If neither is provided, an `IngestError` is raised.

**Thumbnails:** When a format object declares `image_columns()` (columns with pg_schema type `"IMAGE"`), thumbnails are auto-generated at 4 sizes (32x32, 64x64, 128x128, 256x256) and stored in a shared `thumbnails` dataset at `{root_path}/thumbnails`. Requires Pillow (Python) or sharp (Node.js).

### Chunking Strategy by File Type

| File Type | Extensions                           | Strategy                        | Columns Created                                                             |
| --------- | ------------------------------------ | ------------------------------- | --------------------------------------------------------------------------- |
| **Video** | .mp4, .mov, .avi, .mkv, .webm        | 10-second segments + thumbnails | id, file_id, chunk_index, start_time, end_time, video_data, thumbnail, text |
| **Image** | .jpg, .jpeg, .png, .gif, .bmp, .webp | Single chunk                    | id, file_id, image, filename, text                                          |
| **PDF**   | .pdf                                 | Page-by-page at 150 DPI (configurable via `pdf_dpi`) | id, file_id, page_index, image, text                                        |
| **Text**  | .txt, .md, .csv, .json, .xml, .html  | 1000 char chunks, 200 overlap   | id, file_id, chunk_index, text                                              |
| **Other** | *                                    | Single binary chunk             | id, file_id, data, filename                                                 |

### Key Examples

```python
# Ingest files (FILE schema)
client.ingest("videos", {"path": ["cam1.mp4", "cam2.mp4"]}, schema={"path": "FILE"})
client.ingest("photos", {"path": ["img1.jpg"]}, schema={"path": "FILE"})
client.ingest("manuals", {"path": ["manual.pdf"]}, schema={"path": "FILE"})

# Ingest structured data (dict = column data, schema inferred)
client.ingest("vectors", {
    "text": ["Hello", "Goodbye"],
    "embedding": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
})

# Ingest with explicit schema
client.ingest("data", {"name": ["Alice", "Bob"], "age": [30, 25]},
              schema={"name": "TEXT", "age": "INT64"})

# Ingest from HuggingFace
client.ingest("mnist", {"_huggingface": "mnist"})

# Ingest with a format object (see formats.md for CocoPanoptic, Coco, LeRobot, custom)
client.ingest("table", format=my_format)

# Ingest with progress callback
def progress(rows_written, total):
    print(f"Written {rows_written} rows...")
client.ingest("docs", {"path": pdf_files}, schema={"path": "FILE"}, on_progress=progress)
```

> For custom format classes, see [formats.md](formats.md).
> For more ingestion examples, see [examples.md](examples.md).

---

## Training / Streaming

### client.open_table()

Open a managed table as a `deeplake.Dataset` for direct access -- bypasses PostgreSQL and returns the native dataset object with built-in ML framework integration.

```python
ds = client.open_table(table_name: str) -> deeplake.Dataset
```

**When to use:** Training loops, batch iteration, PyTorch/TensorFlow DataLoaders, async prefetch.

```python
# Batch iteration
ds = client.open_table("videos")
for batch in ds.batches(32):
    train(batch)

# PyTorch DataLoader
from torch.utils.data import DataLoader
ds = client.open_table("training_data")
loader = DataLoader(ds.pytorch(), batch_size=32, shuffle=True, num_workers=4)

# TensorFlow tf.data.Dataset
ds = client.open_table("training_data")
tf_ds = ds.tensorflow().batch(32).prefetch(tf.data.AUTOTUNE)
```

---

## Querying

### Fluent Query API (Recommended)

`client.table(table)` returns a chainable `ManagedQueryBuilder`:

```python
# Python: supports both .execute() and () to run the query
results = (
    client.table("videos")
        .select("id", "text", "start_time")
        .where("file_id = $1", "abc123")
        .where("start_time > $2", 60)
        .order_by("start_time ASC")
        .limit(10)
        .offset(0)
)()  # or .execute()
```

```typescript
// Node.js: use .execute() only (no () shorthand)
// (assumes initializeWasm() already called at startup)
const results = await client.table("videos")
    .select("id", "text", "start_time")
    .where("file_id = $1", "abc123")
    .where("start_time > $2", 60)
    .orderBy("start_time ASC")
    .limit(10)
    .offset(0)
    .execute();
```

| Method                  | Python                | Node.js               | Description                |
| ----------------------- | --------------------- | --------------------- | -------------------------- |
| `.select(*cols)`        | `.select("id", "t")`  | `.select("id", "t")`  | Set columns (default `*`)  |
| `.where(cond, *params)` | `.where("id=$1","x")` | `.where("id=$1","x")` | Add WHERE (multiple = AND) |
| `.order_by(clause)`     | `.order_by("col")`    | `.orderBy("col")`     | Add ORDER BY               |
| `.limit(n)`             | `.limit(10)`          | `.limit(10)`          | Set LIMIT                  |
| `.offset(n)`            | `.offset(20)`         | `.offset(20)`         | Set OFFSET                 |
| Run query               | `.execute()` or `()`  | `.execute()`          | Execute, return results    |

**How `.where()` parameters work:** Each `.where("col = $N", value)` call adds an AND condition. The `$1`, `$2`, etc. placeholders are filled by the extra arguments, numbering across all `.where()` calls sequentially.

### Raw SQL: client.query()

```python
# Python
rows = client.query(
    sql: str,
    params: tuple = None,
    timeout: int = 60,       # HTTP timeout in seconds (increase for slow queries)
) -> list[dict]

# Examples
rows = client.query("SELECT * FROM videos LIMIT 10")
rows = client.query("SELECT * FROM documents WHERE file_id = $1", ("abc123",))
rows = client.query("SELECT COUNT(*) FROM big_table", timeout=300)  # 5-minute timeout
```

```typescript
// Node.js
const rows = await client.query(
    sql: string,
    params?: unknown[],
    options?: { timeoutMs?: number },  // default 60000 (60s)
) -> Promise<QueryRow[]>

// Examples
const rows = await client.query("SELECT * FROM videos LIMIT 10");
const rows = await client.query("SELECT * FROM documents WHERE file_id = $1", ["abc123"]);
const rows = await client.query("SELECT COUNT(*) FROM big", undefined, { timeoutMs: 300_000 });
```

Queries are sent to the API via `POST /workspaces/{id}/tables/query`. Use `$1`, `$2`, ... for parameterized queries.

> **Timeout:** The default query timeout is 60 seconds. For long-running queries (large aggregations, index builds), increase it via the `timeout` / `timeoutMs` parameter. Non-default timeouts are forwarded to the backend as `timeout_ms` so the server can also apply a deadline.

> For pg_deeplake SQL features (vector search, BM25, hybrid search, indexes), see [reference.md](reference.md).

---

## Table Management

```python
# Python
tables = client.list_tables() -> list[str]
client.drop_table(table_name: str, if_exists: bool = True) -> None
client.create_index(table_name: str, column: str) -> None
```

```typescript
// Node.js
const tables = await client.listTables();
await client.dropTable(tableName: string, ifExists?: boolean); // default true
await client.createIndex(tableName: string, column: string);
```

### Index Creation

`create_index()` / `createIndex()` creates a `deeplake_index` on a column. Use it for:
- **EMBEDDING columns** — enables vector cosine similarity search via `<#>`
- **TEXT columns** — enables BM25 text search via `<#>`

The method executes `CREATE INDEX IF NOT EXISTS ... USING deeplake_index (column)` and is a no-op if the index already exists.

```python
# Python — standalone
client.create_index("embeddings", "embedding")  # vector index
client.create_index("documents", "text")         # text index

# Python — during ingestion (creates indexes after data is committed)
client.ingest("search_index", {
    "text": documents,
    "embedding": embeddings,
}, index=["embedding", "text"])
```

```typescript
// Node.js — standalone
await client.createIndex("embeddings", "embedding");
await client.createIndex("documents", "text");

// Node.js — during ingestion
await client.ingest("search_index", {
    text: documents,
    embedding: embeddings,
}, { index: ["embedding", "text"] });
```

---

## Workspace Management

Workspaces are created via the REST API. The SDK clients don't have a built-in `createWorkspace()` method — use `apiRequest` directly.

**Important:** The `id` field is **required** when creating a workspace. Omitting it returns an error.

```typescript
// Node.js — create workspace via API
import { apiRequest, extractOrgId } from 'deeplake';

const orgId = extractOrgId(token);
await apiRequest(apiUrl, token, orgId, {
    method: 'POST',
    path: '/workspaces',
    body: { id: 'my-workspace', name: 'My Workspace' },
    timeoutMs: 30_000,
});
```

```python
# Python — create workspace via API
import requests

resp = requests.post(
    f"{api_url}/workspaces",
    headers={"Authorization": f"Bearer {token}"},
    json={"id": "my-workspace", "name": "My Workspace"},
)
resp.raise_for_status()
```

**List workspaces:**

```typescript
// Node.js
const resp = await apiRequest(apiUrl, token, orgId, {
    method: 'GET',
    path: '/workspaces',
});
// resp.data = [{ id, org_id, name, type, created_at }, ...]
```

| Field    | Required | Description                                       |
| -------- | -------- | ------------------------------------------------- |
| `id`     | **Yes**  | Workspace identifier (used in API paths and `al://` URLs) |
| `name`   | No       | Display name (defaults to `id` if omitted)        |

> **Note:** Omitting `id` returns HTTP 400 Bad Request with the message "workspace ID is required".

---

## Error Handling

Both Python and Node.js share the same error hierarchy:

```
ManagedServiceError          # Base class for all errors
├── AuthError                # Token invalid/expired
│   └── TokenError           # Token parsing failed
├── CredentialsError         # DB credentials fetch failed
├── IngestError              # File ingestion failed
├── TableError               # Table operation failed
└── WorkspaceError           # Workspace not found or inaccessible
```

```python
# Python imports
from deeplake.managed import (
    ManagedServiceError, AuthError, CredentialsError,
    IngestError, TableError, TokenError, WorkspaceError,
)
```

```typescript
// Node.js imports
import {
    ManagedServiceError, AuthError, CredentialsError,
    IngestError, TableError, TokenError, WorkspaceError,
} from 'deeplake';
```

| Error                                      | Cause                     | Solution                                                    |
| ------------------------------------------ | ------------------------- | ----------------------------------------------------------- |
| `AuthError: Token required`                | No token provided         | Pass `token=` to Client() or set `DEEPLAKE_API_KEY` env var |
| `AuthError: Token does not contain org_id` | Token missing OrgID claim | Ensure token has OrgID claim or API `/me` is accessible     |
| `IngestError: File not found`              | Invalid file path         | Check file exists at given path                             |
| `TableError: table creation failed`        | API table creation failed | Check API server is running and workspace is accessible     |
| `WorkspaceError: No storage path`          | API returned no path      | Check workspace exists and has storage configured           |

> For troubleshooting details, see [reference.md](reference.md).

---

## Agent Decision Trees

### Decision: How to Initialize Client

```
Need to create a Client
|
|-- Python?
|   |-- DEEPLAKE_API_KEY env var is set?
|   |   `-- client = Client()                          # defaults: token from env, workspace="default"
|   |-- Have explicit token?
|   |   `-- client = Client(token="dl_xxx")            # workspace defaults to "default"
|   |-- Need specific workspace?
|   |   `-- client = Client(workspace_id="my-ws")      # token from env
|   `-- Need custom API URL?
|       `-- client = Client(api_url="http://custom:8080")
|
`-- Node.js?
    `-- import { ManagedClient, initializeWasm } from 'deeplake';
        await initializeWasm();
        const client = new ManagedClient({
           token: process.env.DEEPLAKE_API_KEY!,
           workspaceId: "my-ws",        // optional, default "default"
           apiUrl: "http://custom:8080", // optional
        });
```

### Decision: How to Ingest Data

```
User wants to ingest data
|
|-- Is it local files? -> use FILE schema
|   |-- Python:
|   |   `-- client.ingest("table", {"path": ["f1.mp4", "f2.mp4"]},
|   |          schema={"path": "FILE"})
|   `-- Node.js:
|       `-- await client.ingest("table", { path: ["f1.mp4"] },
|              { schema: { path: "FILE" } })
|
|-- Is it structured data (dict/lists)? -> pass a dict directly
|   |-- Python:
|   |   `-- client.ingest("table", {"col1": [...], "col2": [...]})
|   `-- Node.js:
|       `-- await client.ingest("table", { col1: [...], col2: [...] })
|
|-- Is it a HuggingFace dataset? -> use _huggingface key
|   `-- client.ingest("table", {"_huggingface": "dataset_name"})
|
|-- Is it a LeRobot robotics dataset? -> 3-table design (tasks + frames + episodes)
|   |-- from deeplake.managed.formats import LeRobotTasks, LeRobotFrames, LeRobotEpisodes
|   |-- client.ingest("tasks", format=LeRobotTasks(dataset_dir))
|   |-- client.ingest("frames", format=LeRobotFrames(dataset_dir, chunk_start=0, chunk_end=3))
|   `-- client.ingest("episodes", format=LeRobotEpisodes(dataset_dir, chunk_start=0, chunk_end=3))
|   Note: chunk_end is inclusive. Episodes requires git lfs. See examples.md Workflow 7.
|
|-- Is it a domain-specific format (COCO, etc.)? -> use format object
|   |-- Python:  client.ingest("table", format=my_format)
|   `-- Node.js: await client.ingest("table", null, { format: myFormat })
|   See formats.md for built-in formats: CocoPanoptic, Coco, LeRobot, custom
|
|-- Need custom chunking for text?
|   `-- client.ingest("table", {"path": ["doc.txt"]},
|          schema={"path": "FILE"},
|          chunk_size=500, chunk_overlap=100)
|
`-- Need explicit schema?
|   `-- client.ingest("table", {...}, schema={
|          "name": "TEXT",
|          "count": "INT64",
|          "vector": "EMBEDDING",
|      })
|
`-- Need indexes for search performance?
    `-- client.ingest("table", {...}, index=["embedding", "text"])
       Or standalone: client.create_index("table", "embedding")
```

### Decision: How to Query Data

```
User wants to query data
|
|-- Simple SELECT (small result)?
|   |-- Python fluent: client.table("table").select("id", "text").limit(100)()
|   |-- Python raw:    client.query("SELECT * FROM table LIMIT 100")
|   |-- Node fluent:   await client.table("table").select("id", "text").limit(100).execute()
|   `-- Node raw:      await client.query("SELECT * FROM table LIMIT 100")
|
|-- Large result set (streaming)?
|   `-- Use client.open_table("table") for direct dataset access
|      with batch iteration, PyTorch/TF DataLoaders, etc.
|
|-- Need semantic/vector search?
|   `-- client.query("""
|          SELECT *, embedding <#> $1 AS score
|          FROM table ORDER BY score DESC LIMIT 10
|      """, (query_embedding,))
|
|-- Need text search?
|   `-- client.query("""
|          SELECT * FROM table
|          WHERE text @> $1
|      """, ("keyword",))
|
`-- Need hybrid search (vector + text)?
    `-- client.query("""
           SELECT *, (embedding, text)::deeplake_hybrid_record <#>
           deeplake_hybrid_record($1, $2, 0.7, 0.3) AS score
           FROM table ORDER BY score DESC LIMIT 10
       """, (query_emb, "search text"))
```

### Decision: User Wants to Train on Data

```
User wants to train / iterate over data
|
|-- Fast native batch iteration (RECOMMENDED for large datasets)?
|   |-- ds = client.open_table("table")
|   |   for batch in ds.batches(256):  # dict of numpy arrays
|   |       states = torch.tensor(np.stack([batch[c] for c in cols], axis=1))
|   |-- For column subsets, use query first:
|   |   view = ds.query("SELECT col1, col2 WHERE episode_index < 100")
|   `   for batch in view.batches(256): ...
|
|-- Need PyTorch DataLoader (small datasets or need shuffle)?
|   `-- ds = client.open_table("table")
|      loader = DataLoader(ds.pytorch(), batch_size=32, shuffle=True)
|      NOTE: Slower on large remote datasets — prefer ds.batches() above
|
|-- Need TensorFlow tf.data?
|   `-- ds = client.open_table("table")
|      tf_ds = ds.tensorflow().batch(32).prefetch(AUTOTUNE)
|
`-- Training on LeRobot data?
    |-- Behavior cloning (state->action):
    |   ds = client.open_table("droid_frames")
    |   view = ds.query("SELECT state_x, ..., action_x, ... WHERE episode_index < 100")
    |   for batch in view.batches(256):
    |       states = torch.tensor(np.stack([batch[c] for c in STATE_COLS], axis=1))
    |       actions = torch.tensor(np.stack([batch[c] for c in ACTION_COLS], axis=1))
    |       # train(model, states, actions)
    |
    `-- Video-conditioned training:
        ds = client.open_table("droid_episodes")
        # Access video bytes via ds[i]["exterior_1_video"], etc.
```

### Decision: Error Recovery

```
Operation failed with error
|
|-- AuthError?
|   |-- "Token required" -> Set DEEPLAKE_API_KEY env var or pass token= to Client()
|   |-- "Token does not contain org_id" -> Ensure token has OrgID claim
|   `-- "Token expired" -> Get new token
|
|-- IngestError?
|   |-- "data must be a dict" -> Pass a dict, not list/str/int
|   |-- "data must not be empty" -> Dict must have at least one key
|   |-- "File not found" -> Check file path exists
|   |-- "ffmpeg not found" -> Install ffmpeg for video processing
|   `-- "fitz not found" / "pdfjs-dist not found" -> Install pymupdf (Python) or pdfjs-dist (Node.js)
|
|-- TableError?
|   |-- "create_deeplake_table failed" -> Check pg_deeplake extension
|   |-- "Table already exists" -> Use drop_table() first or different name
|   |-- "Index creation failed" -> Check column exists and is EMBEDDING or TEXT type
|   `-- "Query timed out" -> Increase timeout: client.query(sql, timeout=300)
|
|-- WorkspaceError / "workspace ID is required"?
|   `-- POST /workspaces requires the "id" field in the request body.
|      Use: { id: "my-ws", name: "My Workspace" }
|
|-- "Not found: /workspaces/.../tables"?
|   `-- Workspace must exist before ingest(). Create it via the API or UI first.
|
|-- Tables created via raw SQL not visible to ingest()?
|   `-- Raw SQL tables (CREATE TABLE ... USING deeplake) are not registered with
|      the managed API. Use client.ingest() to create tables. Use client.query()
|      for raw SQL operations on manually-created tables.
|
|-- Thumbnail generation failed? (logged as warning, non-fatal)
|   |-- Python: Install Pillow (`pip install Pillow`)
|   `-- Node.js: Install sharp (`npm install sharp`)
|
`-- ManagedServiceError?
    `-- Check API server is running at the configured api_url
```

---

## Supporting Files

- **[reference.md](reference.md)** -- pg_deeplake SQL reference (vector search, BM25, hybrid search, indexes), data types, limits, performance tuning, troubleshooting
- **[examples.md](examples.md)** -- Complete end-to-end workflow examples and detailed ingestion examples
- **[formats.md](formats.md)** -- Format base class, custom format classes, normalize()/schema()/image_columns() rules
