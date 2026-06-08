---
name: render
description: Deploy and operate apps on Render (Blueprint + one-click Dashboard deeplink, same flow as Codex render-deploy). Use when the user wants to deploy, host, or publish an app; create or edit render.yaml; add web, static, workers, cron, Postgres, or Key Value; get the Blueprint deeplink to deploy; trigger or verify deploys via API when RENDER_API_KEY is set; connect Render MCP via mcporter for direct service creation; or configure env vars, health checks, scaling, previews, and projects.
metadata:
  { "openclaw": { "emoji": "☁️", "homepage": "https://render.com/docs", "version": "1.0.0" } }
---

# Render Skill

Deploy and manage applications on Render using Blueprints (`render.yaml`), the Dashboard, or the API. This skill mirrors the **Codex render-deploy** flow: analyze codebase → generate/validate Blueprint → commit & push → one-click Dashboard deeplink → optional API/mcporter verify or re-deploy.

## When to Use This Skill

Activate when the user wants to:
- Deploy, host, or publish an application on Render
- Create or edit a `render.yaml` Blueprint (new or existing repo)
- Add web, static site, private, worker, or cron services; Postgres; or Key Value
- Configure env vars, health checks, scaling, disks, or regions
- Set up preview environments or projects
- Validate a Blueprint or get Dashboard/API links

## Deployment Method Selection

1. **If `RENDER_API_KEY` is set** → Prefer REST API or MCP (fastest; no user click). Use `references/rest-api-deployment.md` for request bodies, or mcporter if configured (see `references/mcp-integration.md`).
2. **If no API key** → Use Blueprint + deeplink (user commits, pushes, then clicks the deeplink to deploy).

Check for API key:

```bash
[ -n "$RENDER_API_KEY" ] && echo "RENDER_API_KEY is set" || echo "RENDER_API_KEY is not set"
```

## Happy Path (New Users)

Before deep analysis, use this short sequence to reduce friction:
1. Ask whether they want to deploy from a **Git repo** (required for Blueprint and deeplink) or only get guidance. If no Git remote, they must create/push one first.
2. Ask whether the app needs a database, workers, cron, or other services so you can choose the right Blueprint shape.

Then follow **Deploy to Render** below (Blueprint → push → deeplink → verify).

## Prerequisites Check

1. **Git remote** – Required for Blueprint deploy. Run `git remote -v`; if none, ask the user to create a repo on GitHub/GitLab/Bitbucket, add `origin`, and push.
2. **Render CLI (optional)** – For local validation: `render blueprints validate render.yaml`. Install: `brew install render` or [Render CLI](https://github.com/render-oss/cli).
3. **API key (optional)** – For verifying deploys or triggering re-deploys: [Dashboard → API Keys](https://dashboard.render.com/u/*/settings#api-keys). Set `RENDER_API_KEY` in the environment.

## Security Notes

- **Never commit secrets to render.yaml** — always use `sync: false` for API keys, passwords, and tokens; the user fills them in the Dashboard.
- **Validate before suggesting deployment** — run `render blueprints validate render.yaml` or use the Validate Blueprint API so invalid YAML is never pushed.
- **Validate user-provided values** — when writing env vars or service names from user input into YAML, sanitize or quote as needed to avoid injection.

## References

- `references/codebase-analysis.md` (detect runtime, build/start commands, env vars)
- `references/blueprint-spec.md` (root keys, service types, env vars, validation)
- `references/rest-api-deployment.md` (direct API create service: ownerId, request bodies, type mapping)
- `references/mcp-integration.md` (Render MCP tools, mcporter usage, supported runtimes/plans/regions)
- `references/post-deploy-checks.md` (verify deploy status and health via API)
- `references/troubleshooting-basics.md` (build/startup/runtime failures)
- `assets/` (example Blueprints: node-express.yaml, python-web.yaml, static-site.yaml, web-with-postgres.yaml)

## Blueprint Basics

- **File:** `render.yaml` at the **root** of the Git repository (required).
- **Root-level keys (official spec):** `services`, `databases`, `envVarGroups`, `projects`, `ungrouped`, `previews.generation`, `previews.expireAfterDays`.
- **Spec:** [Blueprint YAML Reference](https://render.com/docs/blueprint-spec). JSON Schema for IDE validation: https://render.com/schema/render.yaml.json (e.g. YAML extension by Red Hat in VS Code/Cursor).

**Validation:** `render blueprints validate render.yaml` (Render CLI v2.7.0+), or the [Validate Blueprint API](https://api-docs.render.com/reference/validate-blueprint) endpoint.

## Service Types

| type       | Purpose |
|------------|--------|
| `web`      | Public HTTP app or static site (use `runtime: static` for static) |
| `pserv`    | Private service (internal hostname only, no public URL) |
| `worker`   | Background worker (runs continuously, e.g. job queues) |
| `cron`     | Scheduled job (cron expression; runs and exits) |
| `keyvalue` | Render Key Value instance (Redis/Valkey-compatible; **defined in `services`**) |

**Note:** Private services use `pserv`, not `private`. Key Value is a service with `type: keyvalue`; do not use a separate root key for it in new Blueprints (some older blueprints use `keyValueStores` and `fromKeyValueStore`—prefer the official format).

## Runtimes

Use **`runtime`** (preferred; `env` is deprecated): `node`, `python`, `elixir`, `go`, `ruby`, `rust`, `docker`, `image`, `static`. For static sites: `type: web`, `runtime: static`, and **`staticPublishPath`** (e.g. `./build` or `./dist`) required.

## Minimal Web Service

```yaml
services:
  - type: web
    name: my-app
    runtime: node
    buildCommand: npm install
    startCommand: npm start
    envVars:
      - key: NODE_ENV
        value: production
```

Python example: `runtime: python`, `buildCommand: pip install -r requirements.txt`, `startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT` (or gunicorn). Set `PYTHON_VERSION` / `NODE_VERSION` in envVars when needed.

## Static Site

```yaml
- type: web
  name: my-blog
  runtime: static
  buildCommand: yarn build
  staticPublishPath: ./build
```

Optional: `headers`, `routes` (redirects/rewrites). See [Static Sites](https://render.com/docs/static-sites).

## Environment Variables

- **Literal:** `key` + `value` (never hardcode secrets).
- **From Postgres:** `fromDatabase.name` + `fromDatabase.property` (e.g. `connectionString`).
- **From Key Value or other service:** `fromService.type` + `fromService.name` + `fromService.property` (e.g. `connectionString`, `host`, `port`, `hostport`) or `fromService.envVarKey` for another service’s env var.
- **Secret / user-set:** `sync: false` (user is prompted in Dashboard on first create; add new secrets manually later). **Cannot be used inside env var groups.**
- **Generated:** `generateValue: true` (base64 256-bit value).
- **Shared:** `fromGroup: <envVarGroups[].name>` to attach an env var group.

Env groups **cannot** reference other services (no `fromDatabase`/`fromService` in groups) and **cannot** use `sync: false`. Put secrets and DB/KV references in **service-level** `envVars`, or reference a group and add service-specific vars alongside.

## Databases (Render Postgres)

```yaml
databases:
  - name: my-db
    plan: basic-256mb
    databaseName: my_app
    user: my_user
    region: oregon
    postgresMajorVersion: "18"
```

**Plans (current):** `free`, `basic-256mb`, `basic-1gb`, `basic-4gb`, `pro-*`, `accelerated-*`. Legacy: `starter`, `standard`, `pro`, `pro plus` (no new DBs on legacy). Optional: `diskSizeGB`, `ipAllowList`, `readReplicas`, `highAvailability.enabled`. Reference in services: `fromDatabase.name`, `property: connectionString`.

## Key Value (Redis/Valkey)

Key Value instances are **services** with `type: keyvalue` (or deprecated `redis`). **`ipAllowList` is required:** use `[]` for internal-only, or `- source: 0.0.0.0/0` to allow external.

```yaml
services:
  - type: keyvalue
    name: my-cache
    ipAllowList:
      - source: 0.0.0.0/0
        description: everywhere
    plan: free
    maxmemoryPolicy: allkeys-lru
```

Reference in another service: `fromService.type: keyvalue`, `fromService.name: my-cache`, `property: connectionString`. Policies: `allkeys-lru` (caching), `noeviction` (job queues), etc. See [Key Value](https://render.com/docs/key-value).

**Note:** Some repos use root-level `keyValueStores` and `fromKeyValueStore`; the official spec uses `services` + `fromService`. Prefer the official form for new Blueprints.

## Cron Jobs

```yaml
- type: cron
  name: my-cron
  runtime: python
  schedule: "0 * * * *"
  buildCommand: "true"
  startCommand: python scripts/daily.py
  envVars: []
```

`schedule` is a cron expression (minute hour day month weekday). `buildCommand` is required (use `"true"` if no build). Free plan not available for cron/worker/pserv.

## Env Var Groups

Share vars across services. No `fromDatabase`/`fromService`/`sync: false` inside groups—only literal values or `generateValue: true`.

```yaml
envVarGroups:
  - name: app-env
    envVars:
      - key: CONCURRENCY
        value: "2"
      - key: APP_SECRET
        generateValue: true

services:
  - type: web
    name: api
    envVars:
      - fromGroup: app-env
      - key: DATABASE_URL
        fromDatabase:
          name: my-db
          property: connectionString
```

## Health Check, Region, Pre-deploy

- **Web only:** `healthCheckPath: /health` for zero-downtime deploys.
- **Region:** `region: oregon` (default), `ohio`, `virginia`, `frankfurt`, `singapore` (set at create; cannot change later).
- **Pre-deploy:** `preDeployCommand` runs after build, before start (e.g. migrations).

## Scaling

- **Manual:** `numInstances: 2`.
- **Autoscaling** (Professional workspace): `scaling.minInstances`, `scaling.maxInstances`, `scaling.targetCPUPercent` or `scaling.targetMemoryPercent`. Not available with persistent disks.

## Disks, Monorepos, Docker

- **Persistent disk:** `disk.name`, `disk.mountPath`, `disk.sizeGB` (web, pserv, worker).
- **Monorepo:** `rootDir`, `buildFilter.paths` / `buildFilter.ignoredPaths`, `dockerfilePath` / `dockerContext`.
- **Docker:** `runtime: docker` (build from Dockerfile) or `runtime: image` (pull from registry). Use `dockerCommand` instead of `startCommand` when needed.

## Preview Environments & Projects

- **Preview environments:** Root-level `previews.generation: off | manual | automatic`, optional `previews.expireAfterDays`. Per-service `previews.generation`, `previews.numInstances`, `previews.plan`.
- **Projects/environments:** Root-level `projects` with `environments` (each lists `services`, `databases`, `envVarGroups`). Use for staging/production. Optional `ungrouped` for resources not in any environment.

## Common Deployment Patterns

### Full stack (web + Postgres + Key Value)

Web service with `fromDatabase` for Postgres and `fromService` for Key Value. Add one `databases` entry and one `type: keyvalue` service; reference both from the web service `envVars`. See `assets/web-with-postgres.yaml` for Postgres; add a keyvalue service and `fromService` for Redis URL.

### Microservices (API + worker + cron)

Multiple services in one Blueprint: `type: web` for the API, `type: worker` for a background processor, `type: cron` for scheduled jobs. Share `envVarGroups` or repeat env vars; use `fromDatabase`/`fromService` for shared DB/Redis. All use the same `branch` and `buildCommand`/`startCommand` as appropriate per runtime.

### Preview environments for PRs

Set root-level `previews.generation: automatic` (or `manual`). Optionally `previews.expireAfterDays: 7`. Each PR gets a preview URL; per-service overrides with `previews.generation`, `previews.numInstances`, or `previews.plan` when needed.

## Plans (Services)

`plan: free | starter | standard | pro | pro plus` (and for web/pserv/worker: `pro max`, `pro ultra`). Omit to keep existing or default to `starter` for new. Free not available for pserv, worker, cron.

## Dashboard & API

- **Dashboard:** https://dashboard.render.com — New → Blueprint, connect repo, select `render.yaml`.
- **Key Value:** https://dashboard.render.com/new/redis

## API Access

To use the Render API from the agent (verify deploys, trigger deploys, list services/logs):

1. **Get an API key:** Dashboard → Account Settings → [API Keys](https://dashboard.render.com/u/*/settings#api-keys).
2. **Store as env var:** Set `RENDER_API_KEY` in the environment (e.g. `skills.entries.render.env` or process env).
3. **Authentication:** Use Bearer token: `Authorization: Bearer $RENDER_API_KEY` on all requests.
4. **API docs:** https://api-docs.render.com — services, deploys, logs, validate Blueprint, etc.

---

# Deploy to Render (same flow as Codex render-deploy skill)

Goal: get the app deployed by generating a Blueprint, then **one-click via Dashboard deeplink**; optionally **trigger or verify via API** when the user has `RENDER_API_KEY`.

## Step 1: Analyze codebase and create render.yaml

- Use `references/codebase-analysis.md` to determine runtime, build/start commands, env vars, and datastores.
- Add or update `render.yaml` at repo root (see Blueprint sections above and `references/blueprint-spec.md`). Use `sync: false` for secrets. See `assets/` for examples.
- **Validate** before asking the user to push:
  - CLI: `render blueprints validate render.yaml` (install: `brew install render` or [Render CLI install](https://github.com/render-oss/cli)).
  - Or API: POST to [Validate Blueprint](https://api-docs.render.com/reference/validate-blueprint) with the YAML body.
- Fix any validation errors before proceeding.

## Step 2: Commit and push (required)

Render reads the Blueprint from the **Git remote**. The file must be committed and pushed.

```bash
git add render.yaml
git commit -m "Add Render deployment configuration"
git push origin main
```

If there is no Git remote, stop and ask the user to create a repo on GitHub/GitLab/Bitbucket, add it as `origin`, and push. Without a pushed repo, the Dashboard deeplink will not work.

## Step 3: Dashboard deeplink (one-click deploy)

Get the repo URL and build the Blueprint deeplink:

```bash
git remote get-url origin
```

If the URL is **SSH**, convert to **HTTPS** (Render needs HTTPS for the deeplink):

| SSH | HTTPS |
|-----|--------|
| `git@github.com:user/repo.git` | `https://github.com/user/repo` |
| `git@gitlab.com:user/repo.git` | `https://gitlab.com/user/repo` |
| `git@bitbucket.org:user/repo.git` | `https://bitbucket.org/user/repo` |

Pattern: replace `git@<host>:` with `https://<host>/`, remove `.git` suffix.

**Deeplink format:**
```
https://dashboard.render.com/blueprint/new?repo=<REPO_HTTPS_URL>
```

Example: `https://dashboard.render.com/blueprint/new?repo=https://github.com/username/my-app`

Give the user this checklist:

1. Confirm `render.yaml` is in the repo at the root (they just pushed it).
2. **Click the deeplink** to open Render Dashboard.
3. Complete Git provider OAuth if prompted.
4. Name the Blueprint (or accept default).
5. **Fill in secret env vars** (those with `sync: false`).
6. Review services/databases, then click **Apply** to deploy.

Deployment starts automatically. User can monitor in the Dashboard.

## Step 4: Verify deployment (optional, needs API key)

If the user has set `RENDER_API_KEY` (e.g. in `skills.entries.render.env` or process env), the agent can verify after the user has applied the Blueprint:

- **List services:** `GET https://api.render.com/v1/services` — Header: `Authorization: Bearer $RENDER_API_KEY`. Find the service by name.
- **List deploys:** `GET https://api.render.com/v1/services/{serviceId}/deploys?limit=1` — Check for `status: "live"` to confirm success.
- **Logs (if needed):** Render API or Dashboard → service → Logs.

Example (exec tool or curl):
```bash
curl -s -H "Authorization: Bearer $RENDER_API_KEY" "https://api.render.com/v1/services" | head -100
curl -s -H "Authorization: Bearer $RENDER_API_KEY" "https://api.render.com/v1/services/{serviceId}/deploys?limit=1"
```

For a short checklist and common fixes, use `references/post-deploy-checks.md` and `references/troubleshooting-basics.md`.

## Triggering deploys (re-deploy without push)

- **After repo is connected:** Pushes to the linked branch trigger automatic deploys when auto-deploy is on.
- **Trigger via API:** With `RENDER_API_KEY`, trigger a new deploy:
  - **POST** `https://api.render.com/v1/services/{serviceId}/deploys`
  - Header: `Authorization: Bearer $RENDER_API_KEY`
  - Optional body: `{ "clearCache": "do_not_clear" }` or `"clear"`
- **Deploy hook (no API key):** Dashboard → service → Settings → Deploy Hook. User can set that URL as an env var (e.g. `RENDER_DEPLOY_HOOK_URL`); then the agent can run `curl -X POST "$RENDER_DEPLOY_HOOK_URL"` to trigger a deploy.

So: **OpenClaw can deploy** by (1) creating `render.yaml`, (2) having the user push and click the Blueprint deeplink (one-click), and optionally (3) triggering or verifying deploys via API or deploy hook when credentials are available.

## Render from OpenClaw (no native MCP)

OpenClaw does not load MCP servers from config. Use one of:

### Option A: REST API (recommended when API key is set)

Use `RENDER_API_KEY` and the Render REST API (curl/exec): create services, list services, trigger deploys, list deploys, list logs. **Request bodies and endpoints:** `references/rest-api-deployment.md`.

### Option B: MCP via mcporter (if installed)

If the user has **mcporter** and Render configured (URL `https://mcp.render.com/mcp`, Bearer `$RENDER_API_KEY`), the agent can call Render MCP tools directly. **Tool list and example commands:** `references/mcp-integration.md`.

Example:

```bash
mcporter call render.list_services
mcporter call render.create_web_service name=my-api runtime=node buildCommand="npm ci" startCommand="npm start" repo=https://github.com/user/repo branch=main plan=free
```

Workspace must be set first (e.g. user: “Set my Render workspace to MyTeam”). Use `mcporter list render --schema` to see current tools and parameters.

---

## Checklist for New Deploys

1. Add or update `render.yaml` with `services` (and optionally `databases`, `envVarGroups`, `projects`). Use `runtime` and official Key Value form (`type: keyvalue` in services, `fromService` for references).
2. Use `sync: false` for secrets in **service** envVars only; tell user to set them in Dashboard. Never put secrets in env groups.
3. For Key Value, set `ipAllowList` (required).
4. Validate: `render blueprints validate render.yaml` or API.
5. User must commit and push, then use the **Blueprint deeplink** (`https://dashboard.render.com/blueprint/new?repo=<HTTPS_REPO_URL>`) to deploy. Optionally verify or re-deploy via API if `RENDER_API_KEY` is set.

## Rules

- Prefer Blueprint for full app definition; suggest Dashboard/API only when Blueprint cannot express something.
- Never commit real API keys or secrets; use `sync: false` and document which env vars the user must set.
- Use `runtime` (not deprecated `env`). For Python/Node set `PYTHON_VERSION`/`NODE_VERSION` in envVars when required.
- When referencing Key Value or other services, use `fromService` with correct `type` (e.g. `keyvalue`, `pserv`).
