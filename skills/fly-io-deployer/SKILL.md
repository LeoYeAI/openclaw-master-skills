---
name: fly-io-deployer
description: Deploy and operate Node, Python, Go, Rust, Elixir, and Docker apps on Fly.io with production-grade fly.toml authoring, Machines API orchestration, region selection (latency vs sovereignty vs egress), Fly Postgres clustering, LiteFS for SQLite replication, Upstash Redis bindings, Tigris object storage, persistent volumes, WireGuard private networking with 6PN, secrets via flyctl, blue/green deploys via auto-stopping machines, scale-to-zero strategies, scheduled scaling, preview deploys per PR, multi-region replicas, hot-config reload, machine SSH, log shipping to Better Stack/Axiom/Datadog/Logtail, and aggressive cost tuning. Triggers on "fly.io", "flyctl", "fly machines", "fly.toml", "fly postgres", "litefs", "tigris", "upstash on fly", "fly deploy", "migrate from heroku", "migrate from render", "migrate from railway", "scale to zero", "fly regions", "fly volumes", "fly wireguard", "6pn", "fly secrets".
metadata:
  tags: ["fly-io", "deployment", "paas", "devops", "edge", "containers", "postgres", "migration", "litefs", "tigris", "machines"]
---

# Fly.io Deployer

Plan, ship, and operate apps on Fly.io's Machines platform with the discipline of a senior platform engineer who has migrated production stacks off Heroku, Render, Railway, and AWS. Produces a deployable `fly.toml`, a region plan, a stateful-services plan (Postgres / LiteFS / Redis / Tigris), a CI/CD pipeline, and a cost model — all sized for the actual traffic shape, not the marketing demo.

## Usage

Invoke when starting a new Fly app, migrating onto Fly, debugging a sick deploy, planning multi-region rollout, or cutting the bill. Equally useful for greenfield ("we want to ship a Rust API to fly") and rescue work ("our Render bill tripled, get us off in 2 weeks").

**Basic invocation:**
> Deploy this Node + Postgres app to Fly.io
> Migrate our Heroku stack (web + worker + Postgres + Redis) onto Fly
> Cut our $1,400/mo Fly bill in half without dropping regions

**With context:**
> Here's the Dockerfile and the Heroku Procfile — produce fly.toml + a migration runbook
> We need EU + US Postgres replicas with read-your-writes from web nodes
> Auto-stop machines but keep p95 cold-start under 800ms for the web app

The agent emits a `fly.toml`, optional `Dockerfile`, `litefs.yml`, `flyctl` migration scripts, GitHub Actions for deploys + preview environments, secret rotation script, and a one-page cost model.

## Inputs Required

- **App shape** — runtime (Node/Python/Go/Rust/Elixir/Bun/Deno/Docker), framework (Next.js/Rails/Django/FastAPI/Phoenix/Actix), entrypoint
- **Stateful needs** — Postgres? Redis? S3-compatible object storage? File system? SQLite?
- **Traffic profile** — req/s peak, geographic distribution, p95 latency target, daily/weekly seasonality
- **Compliance constraints** — data residency (EU-only? US-only? FRA mandatory?), HIPAA/PCI scope
- **Origin platform** (if migrating) — Heroku / Render / Railway / Vercel / AWS / DigitalOcean
- **Budget ceiling** — monthly USD cap matters when picking machine sizes and replica counts

## Workflow

1. Read the app and classify it: stateless web, stateful web (sessions on disk), worker, scheduled job, ws server, RPC, or full-stack monolith
2. Pick primary region from latency to majority of users + sovereignty (`fly platform regions` enumerates current set)
3. Decide replicas: single-region multi-machine vs multi-region active-active vs primary+read-replicas
4. Choose stateful services: Fly Postgres cluster, LiteFS+SQLite, external Supabase/Neon, Upstash Redis, Tigris/R2/S3
5. Author `fly.toml` (anatomy section below); generate `Dockerfile` if missing
6. Wire secrets via `flyctl secrets set` (never bake into image)
7. Create the app + provision volumes + provision Postgres + attach
8. First deploy with `--strategy=immediate` to a single machine; verify health
9. Scale to target shape with `fly scale count` + `fly machine clone --region`
10. Wire CI (deploy on main, preview app per PR)
11. Wire log shipping (Vector → Better Stack/Axiom/Datadog) and metrics (Fly Prometheus + Grafana)
12. Configure auto-stop / auto-start for cost; tune min_machines_running
13. Document rollback (`fly releases list` + `fly deploy --image <prev-sha>`)

## fly.toml Anatomy

Every field, what it does, and the most common mistake.

```toml
app = "myapp-prod"                       # globally unique; -prod / -staging / -pr-<n>
primary_region = "fra"                   # closest to majority users; influences PG primary
kill_signal = "SIGINT"                   # SIGTERM default; SIGINT for Node/Python graceful
kill_timeout = "30s"                     # must exceed your slowest in-flight request
swap_size_mb = 512                       # ENABLE — saves OOM kills on tight machines

[build]
  dockerfile = "Dockerfile"              # explicit > auto-detect; nixpacks/buildpacks fragile
  # build_target = "runtime"             # multi-stage final stage
  # build_args = { NODE_ENV = "production" }

[deploy]
  strategy = "rolling"                   # rolling | bluegreen | canary | immediate
  max_unavailable = 0.33                 # rolling: fraction down at once
  release_command = "npm run db:migrate" # one-shot machine before traffic shifts
  wait_timeout = "5m"                    # hard ceiling on deploy duration

[env]
  PORT = "8080"                          # match internal_port below
  NODE_ENV = "production"
  LOG_FORMAT = "json"                    # required for proper log shipping
  # Never put secrets here — use `flyctl secrets set`

[experimental]
  auto_rollback = true                   # roll back on health-check failure

[[mounts]]
  source = "data"                        # name a volume created via `fly volumes create`
  destination = "/data"
  initial_size = "10gb"
  auto_extend_size_threshold = 80        # %, auto-extends volume
  auto_extend_size_increment = "5gb"
  auto_extend_size_limit = "100gb"
  snapshot_retention = 7                 # days; default is 5

[[services]]
  internal_port = 8080
  protocol = "tcp"
  auto_stop_machines = "stop"            # stop | suspend | off; suspend = warm pause
  auto_start_machines = true
  min_machines_running = 1               # 0 only if cold start is acceptable
  processes = ["app"]                    # gates which process group serves this port

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
    [services.ports.tls_options]
      alpn = ["h2", "http/1.1"]
      versions = ["TLSv1.2", "TLSv1.3"]

  [services.concurrency]
    type = "connections"                 # or "requests" for HTTP-aware
    soft_limit = 200                     # start scaling up
    hard_limit = 250                     # refuse new conns

  [[services.tcp_checks]]
    interval = "15s"
    timeout = "2s"
    grace_period = "10s"                 # extends to first-deploy boot

  [[services.http_checks]]
    interval = "10s"
    timeout = "2s"
    grace_period = "30s"
    method = "GET"
    path = "/healthz"
    protocol = "http"
    tls_skip_verify = false
    [services.http_checks.headers]
      X-Health = "fly"

[[vm]]
  size = "shared-cpu-1x"                 # smallest; fine for low-traffic
  memory = "512mb"
  cpus = 1
  cpu_kind = "shared"                    # shared | performance
  # gpu_kind = "a10"                     # only if doing GPU inference
  processes = ["app"]

[processes]
  app    = "node server.js"
  worker = "node worker.js"
  cron   = "node cron.js"

[[statics]]
  guest_path = "/app/public"             # served from machine, off-CPU
  url_prefix = "/static/"

[metrics]
  port = 9091
  path = "/metrics"                      # Fly's Prometheus scrapes this
```

**Common mistakes:**
- `internal_port` does not match `PORT` env → connection refused, healthchecks 502
- `min_machines_running = 0` on a stateful service → first user gets a 30s cold start
- No `release_command` → migrations race the rolling deploy and break readers
- `kill_timeout` shorter than slowest request → 502s on every deploy
- `auto_stop_machines = "stop"` with attached volume but stateful in-RAM cache → cache cold every wake
- `processes` declared but no `[[services]] processes = [...]` filter → worker exposes HTTP

## Region Strategy

Fly has 35+ regions. Picking three is harder than picking one.

**Tiers by latency to global users** (rough p50 from CDN telemetry):

| Tier | Regions | Use case |
|------|---------|----------|
| 1 | `fra` (Frankfurt), `iad` (Ashburn), `sjc` (San Jose), `nrt` (Tokyo), `syd` (Sydney), `gru` (São Paulo) | Most apps land 80% of traffic in 3 of these |
| 2 | `lhr` (London), `cdg` (Paris), `ams` (Amsterdam), `ord` (Chicago), `dfw` (Dallas), `lax` (LA), `sea` (Seattle), `hkg` (Hong Kong), `sin` (Singapore), `bom` (Mumbai) | Fill p95 gaps |
| 3 | `arn` (Stockholm), `mad` (Madrid), `waw` (Warsaw), `otp` (Bucharest), `jnb` (Johannesburg), `eze` (Buenos Aires), `scl` (Santiago), `qro` (Querétaro), `gdl` (Guadalajara), `bog` (Bogotá), `den` (Denver), `mia` (Miami), `yyz` (Toronto), `yul` (Montréal), `phx` (Phoenix) | Niche or compliance-driven |

**Decision rules:**

- **Single region**: pick `fra` for EU-heavy, `iad` for US-east-heavy, `sjc` for US-west, `gru` for LATAM. Add a second region only when p95 from a continent exceeds your SLO.
- **Two regions**: `iad` + `fra` covers 70% of global SaaS traffic with sub-150ms p95. `iad` + `sjc` if you're US-only but coast-spread.
- **Three regions**: add `nrt` or `syd` when APAC > 10% of users. `gru` when LATAM > 10%.
- **Compliance**: GDPR-strict ⇒ EU-only set `[fra, ams, cdg]`; UK data ⇒ `lhr`; data must stay in Germany ⇒ `fra` only and verify Fly's host-country docs.
- **Postgres primary**: place where writes originate or where the largest user group lives. Read replicas absorb global reads.
- **Egress cost**: cross-region traffic on 6PN is free between Fly machines but billed for outbound to internet — keep DB and app in the *same* region whenever possible.

## Postgres Cluster Recipe

`fly pg create` provisions a Stolon-managed Postgres cluster on Fly Machines. It is **not** a managed database — you operate it.

**Provision:**

```bash
fly pg create \
  --name myapp-db \
  --region fra \
  --vm-size shared-cpu-2x \
  --volume-size 40 \
  --initial-cluster-size 3 \
  --password "$(openssl rand -hex 24)"

fly pg attach --app myapp-prod myapp-db
# This sets DATABASE_URL secret on the app
```

**Cluster anatomy:**
- 1 leader (writes), N replicas (reads)
- Stolon manages failover; ~30s window during leader change
- Each member is a Machine with its own volume; volumes don't replicate — Stolon does
- Connection string is a `flycast` (`.flycast`) anycast over 6PN — auto-routes to leader

**Read replicas in other regions:**

```bash
fly machine clone <leader-id> --app myapp-db --region iad
fly machine clone <leader-id> --app myapp-db --region nrt
```

App code routes reads via the read-only port:

```js
const writer = new Pool({ connectionString: process.env.DATABASE_URL });
const reader = new Pool({ connectionString: process.env.DATABASE_URL.replace(":5432", ":5433") });
```

`5433` returns the *closest* replica via 6PN routing.

**Backups:**
- Volume snapshots: daily, 5-day retention default; bump with `--snapshot-retention`
- Logical: `fly pg ssh` then `pg_dump` to Tigris bucket nightly via `fly machine run --schedule`
- Restore: snapshot restore via `fly volumes restore`; or fork a fresh cluster from a snapshot

**Sizing rules:**
- Start at `shared-cpu-2x` + 4 GB RAM. Move to `performance-2x` when p99 query > 50ms.
- Volume size = working set × 3. Postgres needs free space for WAL, vacuum, and temp.
- `effective_cache_size` = 75% of memory. `shared_buffers` = 25%. Tune via `fly pg config update`.

**When to use external Postgres instead:**
- Need point-in-time recovery (PITR) — Fly PG doesn't ship it
- Need multi-AZ guarantees beyond Stolon's 30s failover
- Already on Supabase / Neon / Crunchy — they're managed; Fly PG is unmanaged

**LiteFS — when SQLite beats Postgres:**

LiteFS replicates a SQLite DB across Machines via FUSE-intercepted writes. Single-writer, many-readers.

```yaml
# litefs.yml
fuse:
  dir: "/litefs"
data:
  dir: "/var/lib/litefs"
exec:
  - cmd: "node server.js"
lease:
  type: "consul"
  hostname: "myapp-prod.internal"
  advertise-url: "http://${HOSTNAME}.vm.myapp-prod.internal:20202"
  consul:
    url: "${FLY_CONSUL_URL}"
    key: "litefs/myapp"
```

Use LiteFS when:
- Working set fits in RAM (sub-10GB)
- Writes are <1k/sec
- You want zero ops on the DB
- Read replicas in every region without query rewriting

Don't use LiteFS when: high write throughput, complex transactions, you need PITR, or you need multiple writers.

## Migration from Heroku / Render / Railway

Per-source playbooks. The common ground is: build a Dockerfile from the implicit one, port the Procfile to `[processes]`, port add-ons to Fly equivalents, swap secrets, cut DNS.

### From Heroku

| Heroku concept | Fly equivalent |
|----------------|----------------|
| Procfile `web:` | `[processes] app = "..."` + `[[services]]` |
| Procfile `worker:`, `release:` | `[processes] worker = "..."`; `[deploy] release_command = "..."` |
| `heroku-postgresql` | `fly pg create` (or external Supabase/Neon) |
| `heroku-redis` | Upstash Redis on Fly (`fly ext redis create`) |
| `heroku config:set` | `flyctl secrets set` |
| Heroku Scheduler | `fly machine run --schedule "0 * * * *"` |
| `heroku ps:scale web=3` | `fly scale count app=3` |
| Review apps | Preview apps via GitHub Actions (recipe below) |
| Buildpacks | Generate Dockerfile (`fly launch` does this; verify it) |

**Cutover steps:**
1. `fly launch --no-deploy` — generates fly.toml + Dockerfile from your repo
2. Provision Postgres on Fly; `pg_dump` from Heroku → restore into Fly PG
3. Set all secrets: `heroku config | awk -F= '{print $1"="$2}' | xargs flyctl secrets set`
4. Deploy: `fly deploy`
5. Sanity-check at `myapp-prod.fly.dev`
6. Add custom domain: `fly certs add example.com`; create CNAME `example.com → myapp-prod.fly.dev`
7. Final cutover: `pg_dump` once more during a maintenance window; flip DNS TTL down 24h before
8. Decommission Heroku after 7-day soak

### From Render

Render's `render.yaml` maps cleanly. Web service → `[[services]]`; cron → `fly machine run --schedule`; private services → use 6PN `*.internal`. Render Postgres → Fly PG (or stay on Render PG short-term and connect over public TLS if migration window is tight).

Watch out: Render's free instances spin down — emulate with `auto_stop_machines` and `min_machines_running = 0`.

### From Railway

Railway's templates are Docker-based; the Dockerfile transfers. Railway's plugins (Postgres, Redis) → Fly PG / Upstash. Railway uses TCP proxies on a public hostname; Fly uses `*.internal` private DNS — refactor service-to-service URLs.

### From Vercel (server functions)

Vercel functions don't move 1:1 — they're stateless serverless. On Fly, run the framework as a regular long-lived process (e.g. Next.js standalone, SvelteKit Node adapter). Multi-region via clones; ISR via durable storage (Tigris) or Fly Volumes.

## Volumes vs Object Storage (Tigris)

| Need | Use |
|------|-----|
| Postgres / LiteFS data | Volume |
| User uploads (images, videos, attachments) | Tigris bucket |
| Build artifacts, cache | Volume (or Tigris if shared across machines) |
| Session store | Redis (Upstash on Fly), not volume |
| Static assets bundled with app | `[[statics]]` (no volume needed) |

Tigris is S3-API-compatible; provisioned via `fly storage create`. Free egress between Tigris and Fly machines in the same region. Use it for anything you'd put on S3 — except you don't pay AWS egress.

Volumes are local NVMe attached to a single machine. **Volumes do NOT replicate.** Two machines on two volumes = two independent disks; pick LiteFS or Postgres replication if you need durability across machines.

## Private Networking via WireGuard / 6PN

Every Fly app gets a private IPv6 (`*.internal`) and 6PN mesh. Cross-app calls inside an org go over the mesh, not the internet.

```bash
# from inside any machine in the org
curl http://myapp-db.internal:5432         # Postgres flycast
curl http://worker.process.myapp-prod.internal:9000   # specific process group
curl http://top1.nearest.of.myapp-prod.internal      # closest healthy machine
```

DNS patterns:
- `<app>.internal` — round-robin across all machines
- `<region>.<app>.internal` — machines in a region
- `<process>.process.<app>.internal` — only that process group
- `<machine-id>.vm.<app>.internal` — exact machine
- `top<n>.nearest.of.<app>.internal` — N closest machines

**WireGuard for laptop access:**
```bash
fly wireguard create personal fra my-laptop
# wg-quick up the generated config
# now ssh root@<machine>.vm.<app>.internal works from your laptop
```

Use cases: dev DB access without a public Postgres port; private service-to-service without a load balancer; VPC-style isolation.

## Secrets Management

```bash
fly secrets set DATABASE_URL=... STRIPE_KEY=...     # batch set, one restart
fly secrets set --stage DATABASE_URL=...            # stage; deploy applies
fly secrets list
fly secrets unset OLD_KEY
fly secrets import < .env.production                # bulk
```

Rules:
- Secrets are encrypted at rest, mounted as env vars at boot
- Setting a secret triggers a deploy unless `--stage`
- Secrets are not in fly.toml; never commit them
- Rotate by setting the new value; the next deploy picks it up
- Use `--stage` when rotating multiple coupled secrets (DB password + connection string)

## Blue/Green via Auto-Stopping Machines

Fly's `bluegreen` deploy strategy: new machines created alongside old, healthchecks must pass, then traffic switches, old destroyed. Use when:

- Schema migrations are incompatible (run release_command on a separate ephemeral machine first)
- Long-lived ws connections must drain
- Deploy size is small (>50 machines makes bluegreen expensive)

```toml
[deploy]
  strategy = "bluegreen"
  max_unavailable = 0
  wait_timeout = "10m"
```

For sites that can tolerate a 30-second window: `rolling` is cheaper.

## Scaling: Auto vs Scheduled

**Auto (concurrency-based):**
- Set `soft_limit` and `hard_limit` per service
- Fly's autoscaler adds machines when soft_limit is exceeded sustained
- Scales down on idle if `auto_stop_machines = "stop"`

**Scheduled (cron-based):**
```bash
# scale up before peak
fly machine run --schedule "0 8 * * 1-5" --command "fly scale count app=10"
# back down after
fly machine run --schedule "0 20 * * 1-5" --command "fly scale count app=2"
```

**Scale-to-zero:**
- `min_machines_running = 0` + `auto_stop_machines = "suspend"` → wakes in <500ms (RAM checkpointed)
- `auto_stop_machines = "stop"` → 5-15s cold start (full reboot)
- Suspend doesn't work with all kernels; verify on your image

## Preview Deploys per PR

```yaml
# .github/workflows/fly-preview.yml
name: Fly Preview
on: [pull_request]
jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: |
          APP="myapp-pr-${{ github.event.number }}"
          flyctl apps create $APP --org personal || true
          flyctl deploy --app $APP --remote-only --strategy=immediate \
            --build-arg COMMIT_SHA=${{ github.sha }}
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Tear down on PR close:

```yaml
on:
  pull_request:
    types: [closed]
jobs:
  destroy:
    runs-on: ubuntu-latest
    steps:
      - run: flyctl apps destroy myapp-pr-${{ github.event.number }} --yes
        env: { FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }} }
```

Use a separate `--org` for previews if budget is a concern; cap with billing alerts.

## SSH and Debugging

```bash
fly ssh console                                       # nearest machine
fly ssh console -s                                    # pick from list
fly ssh console --machine <id>                        # specific
fly ssh sftp shell                                    # file ops
fly logs                                              # all machines, tail
fly logs --machine <id>                               # one machine
fly status --all                                      # cluster state
fly machine status <id>                               # one machine
fly releases                                          # deploy history
fly deploy --image registry.fly.io/myapp:deployment-prev   # roll back
```

When healthchecks flap: `fly machine status <id> --display-checks`. When a machine won't boot: `fly logs --machine <id> | grep -i panic`. When 6PN is broken: `fly ssh console -C 'getent hosts myapp-db.internal'`.

## Log Shipping

Fly's built-in logs are tail-only and 24h-retained. For production, ship to an external store.

**Vector sidecar (most flexible):**

```toml
[[services]]
  internal_port = 8686
  protocol = "tcp"
  processes = ["vector"]

[processes]
  app    = "node server.js"
  vector = "vector --config /etc/vector/vector.toml"
```

Vector reads from `nats://[fdaa::3]:4223` (Fly's internal log NATS) and pushes to Better Stack, Axiom, Datadog, Logtail, S3, etc.

**Better Stack (cheapest pretty UI):** $0.13/GB ingest, 30-day retention default; their Fly-native integration is one click.

**Axiom (best for high-volume):** Apache Parquet under the hood; flat $0.50/GB then $0.04/GB stored. Use for >100 GB/mo.

**Datadog:** Use only if the org is already paying — Datadog ingest is 5-10× pricier than alternatives but logs+APM+infra in one pane.

**Logtail (Better Stack legacy):** still works; same vendor.

## Cost Tuning

The Fly bill has four levers. Pull each before complaining about the price.

1. **Machine size** — `shared-cpu-1x` is $1.94/mo; `performance-2x` is $62/mo. Right-size per process. The `app` machine doesn't need the same VM as the `worker`.
2. **Min running** — `min_machines_running = 0` for non-critical services with cold-start tolerance saves the entire idle bill.
3. **Volumes** — billed per provisioned GB, not used. Audit with `fly volumes list` and shrink unused ones (note: shrink requires recreation).
4. **Egress** — outbound to internet is $0.02/GB after 100 GB/mo free tier. Big offenders: video, large API responses, debug logs to external services. Mitigate with image compression at edge, gzip, log sampling.

**Per-resource cost cheat sheet:**

| Resource | Approx /mo |
|----------|-----------|
| `shared-cpu-1x` 256MB | $1.94 |
| `shared-cpu-1x` 512MB | $2.94 |
| `shared-cpu-2x` 2GB | $13 |
| `performance-1x` 2GB | $36 |
| `performance-2x` 4GB | $62 |
| `a10` GPU machine | $1.50/hr running |
| Volume | $0.15/GB/mo |
| Bandwidth (after free tier) | $0.02/GB |
| Tigris storage | $0.02/GB/mo |
| Tigris egress to Fly machines | $0 |
| Static IPv4 | $2/mo |

Rule of thumb: a 3-machine global SaaS web tier on `shared-cpu-2x` with Postgres replicas in 3 regions, Tigris at 50GB, and modest traffic (5TB/mo egress) lands at $250-400/mo all-in.

## Anti-patterns

- **Baking secrets into the Docker image** — `flyctl secrets set` is the only correct path
- **Using `fly deploy` from local during incidents** — version drift; always use the commit SHA pipeline
- **Single-machine "production" app** — Fly machines reboot for maintenance; `min_machines_running >= 2` for anything paid
- **Cross-region writes against a primary** — write latency dominates; route writes back to the primary's region
- **Running cron via app process** — use `fly machine run --schedule` so cron failures don't affect the web fleet
- **Auto-stop on a stateful in-memory cache** — every wake re-warms; either pin `min_machines_running = 1` or move cache to Redis
- **Storing user uploads on volumes** — volumes are per-machine; uploads vanish when a machine retires. Use Tigris.
- **Skipping `[deploy] release_command`** — schema migrations race traffic on rolling deploys
- **No `swap_size_mb`** — Node and Python apps OOM on small machines without swap
- **Healthcheck path that hits the database** — DB blip kills all machines simultaneously; healthcheck should be process-local
- **One Fly app for staging + prod** — use separate apps. They're free to create.

## Exit Criteria

A Fly deployment is done when:

- `fly status` shows all machines `started` and healthy across all configured regions
- `fly logs` is silent of errors for 30 minutes post-deploy
- DNS is cut over and TLS issued (`fly certs check example.com` shows `Ready`)
- Postgres has its first scheduled volume snapshot and a logical backup in Tigris
- CI pushes to main auto-deploy and PRs spin up preview apps
- Logs ship to the external store and dashboards exist for p50/p95/p99 + error rate
- A documented rollback runbook lives in the repo (`fly deploy --image registry.fly.io/<app>:<prev-sha>`)
- Cost model is published and matches the first invoice ±15%
- Secrets are rotated off the migration source (Heroku/Render/Railway) and that account is closed
