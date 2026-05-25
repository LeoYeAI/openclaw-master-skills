---
name: durable-agents-setup
description: First-time setup for the Durable Agents stack (Mastra + Trigger.dev). Run once before using the main skill.
---

# Setup Guide

Runs once. After setup is verified, remove the setup reference block from `SKILL.md`.

---

## Execution Rules

These apply for the entire setup without exception.

1. **Run every step in sequence.** No skipping, no asking the user whether to continue.
2. **Never stop for user input.** Every known failure has a recovery path in this file. Go there, fix it, resume.
3. **If a fix is not in this file, find the solution independently.** Read logs, inspect the DB, check config files. Do not ask the user.
4. **Never change package versions or swap libraries to fix an error.** All versions in `package.json` are pinned intentionally. If a version mismatch appears to be the problem, the fix is in the configuration — not in bumping or changing a dependency.
5. **After any recovery, re-run only the step that failed** — not the full `./setup.sh` — unless the recovery section says otherwise.
6. **Confirm expected output before moving to the next step.** Each step specifies what success looks like. Match it before continuing.
7. **Report only at completion or on a genuinely unrecoverable failure.** Unrecoverable means: not covered in this file, and independent investigation finds no path forward.

---

## Prerequisites

- Node.js 18+
- Docker with Docker Compose
- Docker daemon running
- An AI provider API key (any OpenAI-compatible endpoint)

---

## Setup Steps

### Step 0: Check if already running

Before doing anything, verify the stack is not already up.

```bash
curl -s http://localhost:3000/health
```

If this returns `{"status":"ok",...}`, the stack is already running. Skip to the Post-Setup Checklist and confirm all checks pass. If they do, setup is complete — do not re-run anything.

If the API is not up, check whether the containers exist but are stopped:

```bash
cd trigger-infra && docker compose -p trigger ps
```

If containers exist but are stopped, bring them back up:

```bash
docker compose -p trigger up -d
cd ..
npm run dev
```

Then re-run the health check. Only proceed to Step 1 if no prior setup exists.

### Step 1: Clone and enter the repo

```bash
git clone https://github.com/ainakwalamonk/durableclaw.git
cd mastra-triggers-openclaw
```

### Step 2: Run the setup script

```bash
./setup.sh
```

Handles: deps, Docker infra, Trigger.dev bootstrap (user, org, project, secret key, project ref, CLI token), database creation, migrations, AI provider config, smoke tests.

If it fails at any stage, go to the matching recovery section below. Fix it, then resume manually from that step.

### Step 3: Verify infrastructure

Start the worker first (separate terminal), then run the test:

```bash
npm run trigger:dev   # keep running
npm run trigger:test  # in another terminal
```

`trigger:test` fires `dummy-task` via the Trigger.dev API and polls for completion. Pass = full Trigger.dev pipeline is working.

### Step 4: Start the full system

```bash
npm run dev
```

### Step 5: Health check

```bash
curl http://localhost:3000/health
```

Expected: `{"status":"ok","timestamp":"..."}`

### Step 6: Configure LLM from the openclaw gateway

Do not hardcode or guess LLM credentials. Read them from the openclaw project on this machine.

Check in this order until you find the values:

1. Look for a gateway environment file or gateway service config in the openclaw project directory (e.g. `gateway/.env`, `gateway/config.json`, `docker-compose.yml` service named `gateway`, or any `.env` at the project root that contains `AI_BASE_URL`, `AI_API_KEY`, or `MODEL_ID`).
2. Look for an openclaw config JSON (e.g. `openclaw.config.json`, `config/openclaw.json`, or any JSON referencing model/provider settings).
3. If neither exists, check running Docker containers for an AI gateway service:
   ```bash
   docker ps --format '{{.Names}}\t{{.Ports}}' | grep -i gateway
   ```
   Then inspect its environment:
   ```bash
   docker inspect <container_name> --format '{{json .Config.Env}}'
   ```

Once you have `AI_BASE_URL`, `AI_API_KEY`, and `MODEL_ID`, write them to `.env` in this project:

```bash
sed -i '' "s|^AI_BASE_URL=.*|AI_BASE_URL=<value>|" .env
sed -i '' "s|^AI_API_KEY=.*|AI_API_KEY=<value>|" .env
sed -i '' "s|^MODEL_ID=.*|MODEL_ID=<value>|" .env
```

### Step 7: Smoke test

Run the infrastructure smoke test:

```bash
npm run trigger:test
```

Expected: `dummy-task` completes with status `COMPLETED`. This test makes no LLM call — a pass here means the full Trigger.dev pipeline is operational.

If Step 6 failed to find real LLM credentials and `.env` is missing `AI_BASE_URL`, `AI_API_KEY`, or `MODEL_ID`, fill them with placeholders only for this test so the worker starts:

```bash
grep -q "^AI_API_KEY=" .env || echo "AI_API_KEY=placeholder" >> .env
grep -q "^AI_BASE_URL=" .env || echo "AI_BASE_URL=http://placeholder.local/v1" >> .env
grep -q "^MODEL_ID=" .env || echo "MODEL_ID=placeholder-model" >> .env
```

Then re-run `npm run trigger:test`. Placeholders are only acceptable here — Step 8 requires real credentials. If you used placeholders, resolve the LLM config from the openclaw gateway before continuing.

If the smoke test fails, the problem is in the infrastructure — go to the Recovery section. Do not debug LLM credentials until this passes.

### Step 8: Test the AI pipeline

Once real LLM credentials are in `.env` from Step 6:

```bash
curl -X POST http://localhost:3000/pipeline \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Build a URL shortener service"}'
```

Expected: JSON with `plan`, `review`, and run IDs.

### Step 9: Verify Trigger.dev dashboard

Open `http://localhost:3040` and confirm the run appears.

---

## Recovery

### Docker not installed or not running

```bash
docker info
```

macOS:
```bash
brew install --cask docker
# Open Docker Desktop and wait for it to start
```

Linux:
```bash
sudo apt-get update && sudo apt-get install -y docker.io docker-compose-plugin
sudo systemctl start docker
sudo usermod -aG docker $USER && newgrp docker
```

Re-run `./setup.sh` after Docker is running.

### Docker containers fail to start

```bash
cd trigger-infra && docker compose -p trigger ps
docker logs trigger-webapp-1
docker logs trigger-postgres-1
```

If containers are unhealthy:
```bash
cd trigger-infra && docker compose -p trigger down -v
cd .. && ./setup.sh
```

### Postgres not ready / connection refused

```bash
until pg_isready -h localhost -p 5433 -U postgres 2>/dev/null; do sleep 2; done
echo "Postgres ready"
```

### Trigger.dev bootstrap fails (no secret key)

```bash
bash trigger-infra/init-trigger.sh
```

If it fails to find the magic link:
```bash
docker logs trigger-webapp-1 2>&1 | grep magic
```

If that returns nothing, pull the key directly from the DB:
```bash
docker exec trigger-postgres-1 psql -U postgres -d postgres -t -A \
  -c "SELECT \"apiKey\" FROM \"RuntimeEnvironment\" WHERE type = 'DEVELOPMENT' LIMIT 1"
```

Write the result to `.env`:
```
TRIGGER_SECRET_KEY=<value>
```

### Project ref missing (CLI says "Project not found")

The CLI requires the `externalRef` — not the project name or slug.

```bash
docker exec trigger-postgres-1 psql -U postgres -d postgres -t -A \
  -c "SELECT \"externalRef\" FROM \"Project\" LIMIT 1"
```

Write the result to two places:
1. `.env` → `TRIGGER_PROJECT_REF=<value>`
2. `trigger.config.ts` → replace the `project:` field

### CLI auth fails / "not logged in"

The CLI (v3.3.17) reads `~/Library/Preferences/trigger/default.json` on macOS.

```bash
cat ~/Library/Preferences/trigger/default.json 2>/dev/null
cat ~/Library/Preferences/trigger/config.json 2>/dev/null
```

If the `self-hosted` profile is missing or has a placeholder token:
```bash
PAT=$(grep TRIGGER_ACCESS_TOKEN .env | cut -d= -f2)

node -e "
const fs = require('fs');
const p = process.env.HOME + '/Library/Preferences/trigger/default.json';
let cfg = {};
try { cfg = JSON.parse(fs.readFileSync(p, 'utf8')); } catch {}
cfg['self-hosted'] = { accessToken: '$PAT', apiUrl: 'http://localhost:3040' };
fs.writeFileSync(p, JSON.stringify(cfg, null, 2));
console.log('Updated.');
"
```

Verify:
```bash
npx trigger.dev@3.3.17 whoami --profile self-hosted
```

Expected:
```
◇  Account details [self-hosted]
│  Email: admin@trigger.local
│  URL: http://localhost:3040
```

Fallback — authenticate interactively:
```bash
npx trigger.dev@3.3.17 login -a http://localhost:3040
```

Or override via env var for CLI commands:
```bash
export TRIGGER_ACCESS_TOKEN="<your-pat>"
```

### CLI PAT returns 401 even though token looks correct

The PAT in the database was inserted with bad encryption — a known bug in `init-trigger.sh`. Regenerate it:

```bash
# Generate and encrypt a new PAT
node -e "
const crypto = require('node:crypto');
const ENCRYPTION_KEY = '400852556fef3f19b9d0dfb558eb10f5';
const token = 'tr_pat_' + crypto.randomBytes(20).toString('hex');
const nonce = crypto.randomBytes(12);
const cipher = crypto.createCipheriv('aes-256-gcm', ENCRYPTION_KEY, nonce);
let enc = cipher.update(token, 'utf8', 'hex') + cipher.final('hex');
const tag = cipher.getAuthTag().toString('hex');
const hash = crypto.createHash('sha256').update(token).digest('hex');
console.log(JSON.stringify({ token, nonce: nonce.toString('hex'), ciphertext: enc, tag, hash }));
" > /tmp/new_pat.json && cat /tmp/new_pat.json
```

```bash
# Insert into DB
TOKEN=$(node -e "console.log(require('/tmp/new_pat.json').token)")
NONCE=$(node -e "console.log(require('/tmp/new_pat.json').nonce)")
CIPHER=$(node -e "console.log(require('/tmp/new_pat.json').ciphertext)")
TAG=$(node -e "console.log(require('/tmp/new_pat.json').tag)")
HASH=$(node -e "console.log(require('/tmp/new_pat.json').hash)")
USER_ID=$(docker exec trigger-postgres-1 psql -U postgres -d postgres -t -A -c "SELECT id FROM \"User\" LIMIT 1")

docker exec trigger-postgres-1 psql -U postgres -d postgres -c "
  DELETE FROM \"PersonalAccessToken\" WHERE name = 'cli-auto';
  INSERT INTO \"PersonalAccessToken\" (id, name, \"userId\", \"obfuscatedToken\", \"encryptedToken\", \"hashedToken\", \"createdAt\", \"updatedAt\")
  VALUES ('pat_$(openssl rand -hex 12)', 'cli-auto', '$USER_ID',
    'tr_pat_****...', '{\"nonce\": \"$NONCE\", \"ciphertext\": \"$CIPHER\", \"tag\": \"$TAG\"}'::jsonb,
    '$HASH', NOW(), NOW());
"
```

```bash
# Update CLI config
node -e "
const fs = require('fs');
const p = process.env.HOME + '/Library/Preferences/trigger/default.json';
let cfg = {};
try { cfg = JSON.parse(fs.readFileSync(p, 'utf8')); } catch {}
cfg['self-hosted'] = { accessToken: '$TOKEN', apiUrl: 'http://localhost:3040' };
fs.writeFileSync(p, JSON.stringify(cfg, null, 2));
console.log('Done');
"
```

```bash
# Write to .env
sed -i '' "s|^TRIGGER_ACCESS_TOKEN=.*|TRIGGER_ACCESS_TOKEN=$TOKEN|" .env
```

### Version mismatch (404 on /engine/v1/)

The SDK and CLI are pinned to `3.3.17` to match the self-hosted v3 platform. Do not change the versions. Fix the config instead.

Verify the CLI version:
```bash
npx trigger.dev@3.3.17 --version
```

If `package.json` has `^3.3.17` (with caret), remove the caret so it reads exactly:
```json
"@trigger.dev/sdk": "3.3.17",
"trigger.dev": "3.3.17"
```

Then:
```bash
npm install
```

### Application database "mastra" does not exist

```bash
docker exec trigger-postgres-1 psql -U postgres -c "CREATE DATABASE mastra;"
npm run db:migrate
```

### AI config missing or smoke tests fail

Set in `.env`:
```
AI_BASE_URL=<provider base URL>
AI_API_KEY=<key>
MODEL_ID=<model id>
```

Common values:
- OpenAI: `AI_BASE_URL=https://api.openai.com/v1`
- OpenRouter: `AI_BASE_URL=https://openrouter.ai/api/v1`
- Ollama: `AI_BASE_URL=http://localhost:11434/v1`, `AI_API_KEY=ollama`

---

## Known Gotchas

### ESM and environment variables

This project uses ESM. `import` statements are hoisted above all code execution, including `dotenv.config()`. Any module that reads env vars at the top level will fail if loaded statically before `.env` is parsed.

Fix: all run/test commands use `--env-file=.env` (already in `package.json`). Do not remove that flag.

### AGENT.md files and the Trigger.dev worker

Trigger.dev v3 bundles code for the worker. External `.md` files are not bundled by default — `fs.readFileSync` on `AGENT.md` will throw `ENOENT` in the worker.

Fix: embed agent instructions as a string constant directly in the agent's `.ts` file. Do not use `fs.readFileSync` for agent instructions.

---

## Architecture

| Path | Purpose |
|---|---|
| `src/config/model.ts` | Model singleton. Requires `AI_BASE_URL`, `AI_API_KEY`, `MODEL_ID`. |
| `src/agents/{name}/` | Each agent: `{name}.ts` with embedded instructions. |
| `src/tools/` | Shared tools. |
| `src/pipelines/` | Pipeline orchestrators chaining Trigger.dev tasks. |
| `src/pipelines/tasks/` | Durable tasks — one agent call per task. |
| `src/mastra/index.ts` | Central agent registry. |
| `src/trigger/index.ts` | Exports all tasks for the worker. |
| `src/app/index.ts` | Express API: `/health` and `/pipeline`. |
| `trigger-infra/` | Docker Compose stack + bootstrap script. |
| `trigger.config.ts` | Trigger.dev project config (v3). |
| `scripts/test-trigger.ts` | Infrastructure verification script. |
| `db/migrations/` | SQL migrations (tracked). |

## Commands

| Command | What it does |
|---|---|
| `npm run dev` | Express API (port 3000) + Trigger.dev worker concurrently |
| `npm run app:dev` | Express server only |
| `npm run trigger:dev` | Trigger.dev worker only |
| `npm run trigger:test` | Fire dummy-task and verify completion (no AI needed) |
| `npm test` | Smoke tests |
| `npm run db:migrate` | Run database migrations |

## Environment Variables

| Variable | Source |
|---|---|
| `TRIGGER_SECRET_KEY` | Auto-extracted from DB by setup |
| `TRIGGER_PROJECT_REF` | Auto-extracted from DB by setup |
| `TRIGGER_ACCESS_TOKEN` | Auto-generated PAT by setup |
| `TRIGGER_API_URL` | Default `http://localhost:3040` |
| `DATABASE_URL` | Default `postgres://postgres:postgres@localhost:5433/mastra` |
| `AI_BASE_URL` | Set during setup |
| `AI_API_KEY` | Set during setup |
| `MODEL_ID` | Set during setup |

## Stopping Infrastructure

```bash
cd trigger-infra && docker compose -p trigger down
```

Data persists. Next `up -d` resumes from current state. Never use `-v` unless deliberately wiping everything to re-run `./setup.sh`.

---

## Post-Setup Checklist

- `npm run trigger:test` passes (infrastructure smoke test — no AI needed)
- `curl http://localhost:3000/health` returns `ok`
- LLM credentials in `.env` match the openclaw gateway config
- Example pipeline returns valid JSON with `plan`, `review`, and run IDs
- `npm test` passes

Remove the setup reference block from `SKILL.md`. Setup is complete.
