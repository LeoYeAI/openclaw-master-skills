---
name: cloudflare-workers-architect
description: Design Cloudflare Workers solutions end-to-end — pick the right runtime tier (Workers vs Pages vs Durable Objects vs Workers AI), the right storage (KV vs D1 vs R2 vs Durable Object Storage vs Hyperdrive), the right state pattern (singleton DOs, sharded DOs, hibernating WebSockets, RPC-bound services), and the right limits (CPU time, wall time, subrequest count, request size). Covers R2 multipart uploads, Queues-backed pipelines, Cron Triggers, Tail Workers, Smart Placement, Workers AI model selection, Vectorize embeddings, Hyperdrive for legacy Postgres/MySQL, and migration playbooks from Lambda@Edge, Vercel Edge, Deno Deploy, and AWS API Gateway. Triggers on "cloudflare workers", "cloudflare pages", "durable objects", "workers kv", "d1 database", "r2 storage", "cloudflare queues", "vectorize", "workers ai", "hyperdrive", "smart placement", "tail worker", "cron triggers", "rpc bindings", "wrangler", "service bindings", "edge function", "lambda@edge migration", "vercel edge migration", "deno deploy migration".
metadata:
  tags: ["cloudflare", "cloudflare-workers", "edge", "serverless", "durable-objects", "r2", "d1", "kv", "vectorize", "workers-ai", "hyperdrive"]
---

# Cloudflare Workers Architect

Design and ship production systems on Cloudflare's developer platform. Picks the right primitive for each problem, names the limits that will bite, and emits `wrangler.toml`, bindings, deploy scripts, and a cost model. Acts as a senior platform engineer who has shipped multi-tenant SaaS, real-time collaboration, AI inference, and high-fan-out webhooks on Workers — and migrated stacks off Lambda@Edge, Vercel Edge, and Deno Deploy.

## Usage

Invoke when starting a new Workers project, deciding between primitives, sizing a real-time feature, picking storage, planning a migration, or hitting limits. Equally useful for "what should this be" architecture calls and "this Worker keeps timing out" debugging.

**Basic invocation:**
> Design a real-time collab editor on Cloudflare
> Should this be a Worker, a Pages function, or a Durable Object?
> Migrate our 80 Lambda@Edge handlers to Workers

**With context:**
> Here's the API surface — pick storage and write the wrangler.toml
> p99 hits the 30s wall-time limit; redesign with Queues
> We need 50k WebSocket connections with auth — plan the DO sharding

The agent emits a primitive choice, `wrangler.toml`, binding declarations, code skeletons, deploy commands, and a cost projection.

## Inputs Required

- **Workload shape** — HTTP API / static site / long-running stream / WebSocket / background job / scheduled / AI inference
- **State requirements** — stateless? per-user? per-room? global? eventual or strong?
- **Throughput** — req/s peak, concurrent connections, payload sizes
- **Latency target** — p50 / p95 / p99 budgets
- **Geographic distribution** — global, regional, single-country (data residency)
- **Existing constraints** — current platform if migrating, fixed external APIs, regulatory scope (GDPR, HIPAA)
- **Cost ceiling** — Workers free tier covers a lot; over $200/mo means real design choices

## Workflow

1. Classify the workload against the Decision Tree (below)
2. Pick storage from the Selection Matrix; declare bindings in `wrangler.toml`
3. Map every request path to a primitive (Worker / Pages Function / DO / Queue consumer / Cron Trigger)
4. Identify the limit that will bite first; design around it before code
5. Author `wrangler.toml` with all bindings, routes, and compatibility flags
6. Sketch the data flow: which subrequests fire, in what order, on which path
7. Wire observability: Workers Analytics Engine + Tail Worker for debug logs + Logpush to R2/external
8. Implement and test locally with `wrangler dev --remote` (real bindings)
9. Deploy via `wrangler deploy`; canary via gradual deploys
10. Document rollback (`wrangler rollback` to a known version ID)

## Decision Tree: Pages vs Workers vs Durable Objects vs Workers AI

```
START
 ├── Is the request path a static asset (HTML/JS/CSS/image)?
 │     └── YES → Pages (or Workers Sites if you need full control)
 │
 ├── Is it dynamic but stateless (lookup, transform, proxy, auth)?
 │     └── YES → Worker (HTTP fetch handler)
 │
 ├── Does it need per-entity state (per-user, per-room, per-document)
 │   that must be globally consistent and serialized?
 │     └── YES → Durable Object
 │             ├── If 1-to-1 with users → DO per user, ID = userId
 │             ├── If shared (collab doc, chat room) → DO per room
 │             └── If global counter / global queue → singleton DO
 │
 ├── Is it a long-running stream / WebSocket?
 │     └── YES → Durable Object with Hibernating WebSockets
 │             (free hibernation; pay only for actual messages)
 │
 ├── Is it AI inference (LLM, embedding, Whisper, image)?
 │     └── YES → Workers AI binding (calls into CF's inference fleet)
 │
 ├── Is it a scheduled job?
 │     └── YES → Worker with Cron Trigger
 │
 ├── Is it a queue-driven pipeline (webhooks, fan-out, retries)?
 │     └── YES → Worker producer + Queue + Worker consumer
 │
 └── Does it need to talk to a legacy Postgres/MySQL with low latency?
       └── YES → Hyperdrive binding (connection pool + region pinning)
```

**Pages vs Workers nuance:** Pages = static + opt-in `functions/`. Use Pages when the site is mostly static and you have a few API routes. Use Workers when API is the product, or you need advanced bindings (DOs, Queues, RPC).

**Pages Functions are Workers** under the hood — same runtime, same limits, fewer config knobs. Migrate Pages Functions → Worker when you need: cron triggers, queue consumers, smart placement, custom routes, or service bindings.

## Storage Selection Matrix

| Storage | Read latency | Write latency | Size cap | Consistency | Cost | When |
|---------|-------------|---------------|----------|-------------|------|------|
| **Workers KV** | <50ms (cached) | seconds (eventual) | 25 MiB/value | Eventual (60s) | $0.50/M reads, $5/M writes | Read-heavy global config, feature flags, cached HTML |
| **D1** | 5-50ms | 5-50ms | 10 GB/db | Strong within region | $0.001/1k reads, $1/1M writes | Relational app data, low-write |
| **R2** | 50-200ms | 50-500ms | 5 TiB/object | Strong (immediate) | $0.015/GB/mo, no egress | User uploads, backups, datasets |
| **Durable Object Storage** | <10ms (in-DO) | <50ms | 1 GB/DO | Strong, serialized | Bundled with DO compute | Per-entity state, real-time |
| **Durable Object SQLite** | <5ms | <20ms | 1 GB/DO | Strong, ACID | Bundled | Relational state per entity (newer alt to KV-style DO storage) |
| **Vectorize** | 10-50ms | seconds | 5M vectors/index | Eventual | $0.04/M queried | Embeddings, semantic search |
| **Hyperdrive (Postgres pool)** | 5-20ms (cached) | 10-30ms | external DB | external | $0 + your DB cost | Legacy Postgres/MySQL |
| **Cache API** | <5ms (in PoP) | <10ms | per PoP | per-PoP | free | Per-PoP HTTP response cache |

**Decision rules:**
- **Reads >> writes, global, eventual ok** → KV
- **Relational queries, joins, transactions, low-write** → D1
- **Files, blobs, datasets, images** → R2
- **Per-entity state with strong serialization** → DO Storage (use SQLite variant for relational shape)
- **Embeddings / semantic search** → Vectorize
- **Existing Postgres/MySQL you can't replace** → Hyperdrive
- **Per-PoP HTTP cache (idempotent GET)** → Cache API

**Anti-pattern alert:**
- Don't use KV as a write-heavy store — eventual consistency + write rate limits will burn you
- Don't use D1 for >100 writes/sec sustained — split into per-tenant DOs with SQLite
- Don't use R2 for tiny key-value records — KV is cheaper at small sizes
- Don't use a singleton DO for global state with >1k req/s — that DO's CPU is the bottleneck; shard

## Edge State Patterns

**Pattern 1: Singleton DO** — one DO globally, ID = constant string.
- Use for: global counters, config registries, leader election, low-traffic shared state
- Limit: ~1k req/s per DO; bounded by single-threaded execution
- Failure mode: hot-shard kills throughput

**Pattern 2: DO per entity** — `idFromName(userId)`, `idFromName(roomId)`.
- Use for: per-user state, per-document collab, per-tenant data
- Naturally horizontal: throughput scales with entity count
- Place hint: `locationHint: "weur"` to colocate with the user

**Pattern 3: Sharded DOs** — `idFromName(\`shard-${hash(key) % N}\`)`.
- Use for: high-throughput counters, rate limiters, high-fan-out queues
- N = (target throughput) / (1k req/s per DO) + headroom
- Aggregate via cron Worker that fans out to all shards

**Pattern 4: Hibernating WebSocket DO**
- DO accepts WebSocket via `state.acceptWebSocket(ws)` (NOT `ws.accept()`)
- DO can be evicted from memory between messages — only billed when active
- State persists in DO Storage, not in JS variables
- Up to ~32k connections per DO before throughput pressure

```js
// hibernating WS pattern
export class ChatRoom {
  constructor(state, env) { this.state = state; }
  async fetch(req) {
    const pair = new WebSocketPair();
    this.state.acceptWebSocket(pair[1]);              // hibernation-aware
    return new Response(null, { status: 101, webSocket: pair[0] });
  }
  async webSocketMessage(ws, msg) {                    // called even after hibernation
    const peers = this.state.getWebSockets();
    for (const p of peers) if (p !== ws) p.send(msg);
  }
  async webSocketClose(ws, code, reason, wasClean) { /* cleanup */ }
}
```

**Pattern 5: RPC bindings between Workers** (modern alternative to service bindings)
- Worker A exposes a class extending `WorkerEntrypoint` with methods
- Worker B binds to A and calls `env.A.someMethod(args)` directly
- Type-safe, no JSON marshalling, no internal HTTP

```js
// worker-a (service)
export class AuthAPI extends WorkerEntrypoint {
  async verify(token) { return await this.env.KV.get(`session:${token}`); }
}
// worker-b (consumer) — wrangler.toml: services = [{ binding = "AUTH", service = "worker-a", entrypoint = "AuthAPI" }]
const session = await env.AUTH.verify(token);
```

## Request Lifecycle and Limits

**Free plan:**
- 100k req/day
- 10ms CPU time per request
- No paid bindings (DO, R2, D1 etc) — use Workers Paid

**Workers Paid ($5/mo) and Bundled:**
- 10M req/mo included; $0.30/M after
- 30s CPU time max (most usage)
- 50ms CPU time / request bundled (Bundled mode)
- Unbundled mode: 10ms / req but $0.50/M req over the included cap

**Hard limits — design around these:**
| Limit | Value | Notes |
|-------|-------|-------|
| CPU time per request | 30s (Paid Bundled), 50ms (Bundled), 10ms (free) | CPU not wall — fetch waiting doesn't count |
| Wall time per request | unlimited (in practice) | But TCP timeouts and client behavior limit |
| Subrequests per request | 50 (free) / 1000 (paid) | Includes fetches to your own services |
| Request body | 100 MB (paid) / 1 MB (KV bodies) | Use R2 multipart for larger |
| Response body | unlimited streaming | Buffered up to memory |
| Worker memory | 128 MB | Hard ceiling; large parses fail |
| Script size | 10 MB compressed | After bundling |
| DO concurrent requests | 1k+ but serialized within a DO | Single-threaded execution |
| WebSocket messages/sec/DO | ~1k | Above this, shard |

**Subrequest budget tactics:**
- Batch external calls (one fetch with multiple keys vs N fetches)
- Use `waitUntil(ctx, promise)` for fire-and-forget logging — it doesn't count against the request's user-visible latency but still counts against subrequest budget
- Stream-pipe rather than buffer-then-forward when proxying

**CPU time tactics:**
- Heavy crypto, ZIP, image manipulation → push to Queues consumer (separate budget)
- LLM calls → use Workers AI binding (compute happens in CF inference fleet, doesn't count against your CPU)
- JSON parses of >5 MB blobs → stream-parse with `JSONparser`

## R2 Multipart Uploads

R2 multipart is required for objects > 5 GB and recommended for objects > 100 MB.

```js
// 1. Initiate upload
const upload = await env.MY_BUCKET.createMultipartUpload(key);
// 2. Upload parts (5 MB - 5 GB each, max 10k parts)
const parts = [];
for (let i = 0; i < chunks.length; i++) {
  const part = await upload.uploadPart(i + 1, chunks[i]);
  parts.push(part);  // { partNumber, etag }
}
// 3. Complete
await upload.complete(parts);
```

**Patterns:**
- **Browser direct upload**: Worker generates a presigned URL per part; client uploads directly to R2; Worker completes when client confirms all parts done. Saves Worker bandwidth.
- **Resumable**: Persist `{uploadId, partsCompleted}` in DO Storage; client resumes from last completed part on reconnect.
- **Server-side stream**: When proxying a large stream, pipe it through a `TransformStream` that buffers 5 MB chunks and uploads each as a part.

## Smart Placement

Smart Placement re-runs your Worker close to your **origin** (your DB, third-party API) instead of the **user**, when that yields lower total latency.

When to enable: Worker makes 3+ subrequests to a single origin per request and the origin is far from a meaningful share of users.

```toml
[placement]
mode = "smart"
```

**Don't use Smart Placement when:**
- The Worker is a CDN-style cache (you want it close to user)
- Subrequests are to globally-distributed services already (KV, R2, D1)
- The origin is in a single region but users are concentrated nearby

## Cron Triggers and Tail Workers

**Cron triggers:** declare in `wrangler.toml`:
```toml
[triggers]
crons = ["0 */6 * * *", "0 0 * * 0"]
```
Implement `scheduled` handler in the Worker. Limit: 30s CPU time per cron.

**Tail Workers:** a Worker that consumes the runtime traces of another Worker.
```toml
tail_consumers = [{ service = "log-processor" }]
```
Use for: structured log shipping to external stores (BetterStack, Datadog, S3, custom DB), per-request audit trails, real-time error dashboards, sampling for debug. Cheaper than turning Logpush on for low-volume.

## wrangler.toml Anatomy

```toml
name = "myapp-api"
main = "src/index.ts"
compatibility_date = "2026-04-01"           # pin behavior; bump deliberately
compatibility_flags = ["nodejs_compat"]     # opt into Node APIs

workers_dev = false                         # disable .workers.dev preview in prod
routes = [{ pattern = "api.example.com/*", zone_name = "example.com" }]

[placement]
mode = "smart"                              # only if origin-bound

[observability]
enabled = true                              # built-in logs/metrics

[[durable_objects.bindings]]
name = "ROOMS"
class_name = "ChatRoom"

[[migrations]]
tag = "v1"
new_sqlite_classes = ["ChatRoom"]            # SQLite-backed DO; use new_classes for legacy KV-DOs

[[kv_namespaces]]
binding = "CACHE"
id = "abc123..."
preview_id = "def456..."

[[d1_databases]]
binding = "DB"
database_name = "myapp-prod"
database_id = "..."

[[r2_buckets]]
binding = "UPLOADS"
bucket_name = "myapp-uploads"

[[queues.producers]]
binding = "WEBHOOKS"
queue = "webhooks"

[[queues.consumers]]
queue = "webhooks"
max_batch_size = 100
max_batch_timeout = 30
max_retries = 5
dead_letter_queue = "webhooks-dlq"

[[services]]
binding = "AUTH"
service = "auth-worker"
entrypoint = "AuthAPI"                      # RPC entrypoint

[[hyperdrive]]
binding = "PG"
id = "..."

[ai]
binding = "AI"

[[vectorize]]
binding = "VECTORS"
index_name = "embeddings"

[vars]
ENVIRONMENT = "production"
# secrets via `wrangler secret put`

[triggers]
crons = ["0 */6 * * *"]

tail_consumers = [{ service = "log-processor" }]

[limits]
cpu_ms = 50                                 # bundled; 30000 for paid

[env.staging]
name = "myapp-api-staging"
routes = [{ pattern = "staging-api.example.com/*", zone_name = "example.com" }]
```

## Workers AI Model Selection

Workers AI runs CF-hosted models. You pay per neuron (CF's normalized inference unit).

| Task | Model | Cost (rough) | Latency |
|------|-------|-------------|---------|
| Chat (general) | `@cf/meta/llama-3.1-8b-instruct` | $0.011/1M tokens | 200-800ms first token |
| Chat (high quality) | `@cf/meta/llama-3.1-70b-instruct` | $0.59/1M | 500ms-2s |
| Code completion | `@cf/qwen/qwen2.5-coder-32b-instruct` | $0.10/1M | 300ms-1s |
| Embeddings (small, fast) | `@cf/baai/bge-base-en-v1.5` | $0.012/1M | 50-150ms |
| Embeddings (multilingual) | `@cf/baai/bge-m3` | $0.012/1M | 80-200ms |
| Speech-to-text | `@cf/openai/whisper` | $0.005/min | 1-3s/min audio |
| Image generation | `@cf/black-forest-labs/flux-1-schnell` | per-image | 1-3s |
| Image classification | `@cf/microsoft/resnet-50` | $0.005/req | 50ms |

```js
const result = await env.AI.run("@cf/meta/llama-3.1-8b-instruct", {
  messages: [{ role: "user", content: "..." }],
  max_tokens: 256,
  stream: true   // returns ReadableStream — pipe direct to client
});
```

**Decision rules:**
- **RAG retrieval embeddings**: bge-base-en or bge-m3 (multilingual)
- **Chat in-product**: llama-8b for cost; 70b only when quality matters
- **Code-focused**: qwen-coder-32b
- **Realtime classification**: resnet-50 + bge-base
- **Heavyweight reasoning**: bridge to OpenAI/Anthropic via Worker fetch — not on Workers AI yet

## Vectorize for Embeddings

```js
// index
await env.VECTORS.upsert([
  { id: "doc-1", values: embedding, metadata: { tenant: "acme", url: "..." } }
]);
// query
const results = await env.VECTORS.query(queryEmbedding, {
  topK: 10,
  filter: { tenant: "acme" },        // metadata filter
  returnMetadata: "all"
});
```

Limits: 5M vectors/index, 1536 dims/vector typical, metadata filter expressions are limited boolean. For >5M vectors, shard by tenant; for richer filters use D1 first then re-rank with Vectorize.

## Hyperdrive for Legacy DBs

Hyperdrive = connection pool + query cache + region pinning for external Postgres/MySQL. Replaces "Worker → public DB" with "Worker → Hyperdrive → DB" and cuts latency 2-10× for SaaS apps with a single primary DB.

```toml
[[hyperdrive]]
binding = "PG"
id = "..."
```

```js
import postgres from "postgres";
const sql = postgres(env.PG.connectionString);
const rows = await sql`SELECT * FROM users WHERE id = ${id}`;
```

**When Hyperdrive helps:**
- DB is in single region, users are global
- Many short-lived queries per request (connection cost dominates)
- Read-heavy with cacheable patterns

**When it doesn't:**
- DB is already in multiple regions
- Per-request workload is one big query (connection cost is amortized)
- Heavy write traffic (cache miss every time)

## Migration Playbooks

### From AWS Lambda@Edge

| Lambda@Edge | Workers |
|------------|---------|
| Viewer Request → header rewrite | Worker `fetch` handler |
| Origin Request → cache key manipulation | Worker + `cf` request properties |
| Viewer Response | Worker mutates `Response` before return |
| Origin Response | Same — Worker between origin fetch and response |
| CloudFront cache | Cloudflare cache (default) + Cache API for explicit |
| Lambda@Edge limits (5s/1MB) | Workers limits (30s/100MB) |

Migration steps: (1) rewrite each Lambda handler as a `fetch` handler, (2) move origin from S3 to R2 if egress matters, (3) keep CloudFront temporarily and cut DNS to Cloudflare last.

### From Vercel Edge Functions

Vercel Edge runs the same V8 isolate model — most code ports directly. Differences:
- No `next/server` runtime helpers — replace with Web standard `Request`/`Response`
- ISR/SSG → Cloudflare Pages (or Workers with Cache API + R2 for fallback)
- Vercel `geo` headers → CF `request.cf.country` etc
- Vercel KV → Workers KV (similar API; bulk migrate via dual-write window)

### From Deno Deploy

Closest analogue. Deno's `Deno.serve` → Workers `fetch` handler. Deno KV → Workers KV (same eventual consistency profile). Deno Cron → Cron Triggers. Most adapters port; check NPM compat (`compatibility_flags = ["nodejs_compat"]` if needed).

### From AWS API Gateway + Lambda

Largest savings come from killing API Gateway (its bill alone often exceeds the Lambda one). Replace:
- API Gateway routes → `routes` in `wrangler.toml`
- Lambda handlers → Worker `fetch` handler with router (Hono / itty-router)
- DynamoDB → KV (small) or D1 (relational) or DO Storage (per-entity)
- S3 → R2
- SQS → Queues
- EventBridge → Cron Triggers + Queues

Migration risk: cold start on Lambda (~500ms-2s) vs Workers (5-50ms) usually a win, but watch for API Gateway custom authorizers — you'll re-implement auth in the Worker.

## Anti-patterns

- **Storing per-user data in KV with `kv.put(\`user:${id}\`, json)`** — eventual consistency means logout/permission changes can lag 60s. Use D1 or DO Storage.
- **Singleton DO for a global rate limiter** — works at low scale, falls over at >1k req/s. Shard by hash(userId) % N.
- **Calling `crypto.randomUUID()` and storing in KV expecting uniqueness checks** — eventual consistency; two concurrent writers can both succeed. Use D1 unique constraint or DO transactional storage.
- **Buffering large R2 objects in memory** — 128 MB Worker cap. Stream via `body` ReadableStream.
- **Not pinning `compatibility_date`** — runtime upgrades can break `Date` parsing, `crypto.subtle` defaults, etc.
- **Putting secrets in `[vars]`** — they appear in dashboards and Wrangler output. Use `wrangler secret put`.
- **Using a Worker to proxy a Postgres query without Hyperdrive** — TCP setup eats your latency budget.
- **Forgetting `waitUntil` on background work** — promises die when the response returns.
- **One DO for an entire chat application** — single-threaded; thousands of users one room is fine, all rooms one DO is not.
- **Treating Pages as a separate runtime from Workers** — they're the same; if you outgrow Pages config, just move to Workers.
- **Counting on cache hit ratios with personalized responses** — Cache API needs a stable cache key; auth headers usually break it. Use vary or omit caching for personalized paths.
- **Running `node:fs` operations** — there is no filesystem. Map paths to R2 or KV.

## Exit Criteria

A Workers system is production-ready when:

- Each path has a documented primitive choice with the limit it lives within
- `wrangler.toml` declares every binding and the `compatibility_date` is current within 90 days
- Secrets are set via `wrangler secret put`, not committed
- DO classes are SQLite-backed where appropriate (new projects after Apr 2025)
- Observability: Workers Analytics dashboard reviewed weekly; Tail Worker or Logpush wired to long-term store
- Errors visible: Sentry / Honeybadger or equivalent SDK loaded in the Worker
- Load test sustains target req/s with p95 within budget
- Rollback rehearsed: `wrangler rollback <version-id>` known to work
- Cost projection within 20% of first invoice
- Migration source (Lambda@Edge / Vercel / Deno) decommissioned with a 7-day overlap window
