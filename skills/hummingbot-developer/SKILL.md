---
name: hummingbot-developer
description: Developer skill for running Hummingbot and Gateway from source, building wheel and Docker images, and testing against Hummingbot API running from source. Use this skill when a developer wants to build, run, or test Hummingbot components locally.
metadata:
  author: hummingbot
commands:
  start:
    description: Check dev environment — repo branches, prereqs, running services
  install-deps:
    description: Auto-install missing dev dependencies (conda, node, pnpm, docker, git)
  select-branches:
    description: Interactively pick branches for hummingbot, gateway, and hummingbot-api
  install-all:
    description: Install all three repos in order (hummingbot → gateway → hummingbot-api)
  build-all:
    description: Build hummingbot wheel + all Docker images in order
  verify-build:
    description: Verify all builds are correct and in sync across repos
  run-dev-stack:
    description: Start the full dev stack from source (infra + gateway + API)
  setup-hummingbot:
    description: Install Hummingbot from source (branch, conda env, solders fix)
  run-hummingbot:
    description: Run Hummingbot CLI from source
  build-hummingbot:
    description: Build Hummingbot wheel and Docker image from source
  setup-gateway:
    description: Install and configure Gateway from source (pnpm install/build/setup)
  run-gateway:
    description: Run Gateway from source in dev mode
  build-gateway:
    description: Build Gateway Docker image from source
  setup-api-dev:
    description: Configure Hummingbot API to use local Hummingbot source (pip install -e)
  run-api-dev:
    description: Run Hummingbot API from source with hot-reload against local Hummingbot
  test-integration:
    description: Smoke test the full stack — API, Gateway, and Hummingbot connectivity
---

# hummingbot-developer

Developer workflow skill for building and running the full Hummingbot stack from source.

**Commands** (run as `/hummingbot-developer <command>`):

| Command | Description |
|---------|-------------|
| `start` | Check dev environment status |
| `select-branches` | Pick branches for all 3 repos |
| `install-all` | Install all 3 repos in order |
| `build-all` | Build wheel + all Docker images |
| `verify-build` | Verify builds are correct + in sync |
| `run-dev-stack` | Start full stack from source |
| `setup-hummingbot` | Install Hummingbot from source |
| `run-hummingbot` | Run Hummingbot CLI from source |
| `build-hummingbot` | Build wheel + Docker image |
| `setup-gateway` | Install Gateway from source |
| `run-gateway` | Run Gateway in dev mode |
| `build-gateway` | Build Gateway Docker image |
| `setup-api-dev` | Wire API to local Hummingbot source |
| `run-api-dev` | Run API from source with hot-reload |
| `test-integration` | Smoke test the full stack |

**Typical dev workflow:**
```
install-deps → select-branches → install-all → build-all → verify-build → run-dev-stack → test-integration
```

**Repo locations (all in workspace):**

| Repo | Path |
|------|------|
| hummingbot | `~/.openclaw/workspace/hummingbot` |
| gateway | `~/.openclaw/workspace/hummingbot-gateway` |
| hummingbot-api | `~/.openclaw/workspace/hummingbot-api` |

Override with env vars: `HUMMINGBOT_DIR`, `GATEWAY_DIR`, `HUMMINGBOT_API_DIR`, or `WORKSPACE`.

---

## Command: install-deps

Auto-install all missing dev dependencies. Safe to re-run — skips anything already installed.

```bash
bash scripts/install_deps.sh
```

**Installs (only if missing):**
- Homebrew (macOS)
- Xcode Command Line Tools (macOS — needed for Cython `build_ext`)
- Miniconda (conda)
- Node.js v22 (via nvm, Homebrew, or installs nvm)
- pnpm (via npm or Homebrew)
- Git
- Docker Desktop (macOS — via Homebrew cask or opens download page)

**Options:**
```bash
--check         # check only, don't install anything
--conda         # only install conda
--node          # only install node + nvm
--pnpm          # only install pnpm
```

**After installing**, restart your terminal (or `source ~/.zshrc`) to apply PATH changes, then run `check_env.sh` to confirm.

---

## Command: select-branches

Interactively pick a branch for each repo, checkout, and save to `.dev-branches`.

```bash
bash scripts/select_branches.sh
```

**Non-interactive options:**
```bash
# Use development for all
bash scripts/select_branches.sh --defaults

# Specify each branch
bash scripts/select_branches.sh \
  --hummingbot development \
  --gateway core-2.7 \
  --api development
```

Branch selections are saved to `$WORKSPACE/.dev-branches` and automatically loaded by `install_all.sh`, `build_all.sh`, and `verify_build.sh`.

---

## Command: install-all

Install all three repos in the correct order. Requires `select-branches` first (or pass `--defaults`).

```bash
bash scripts/install_all.sh
```

**What it does (in order):**
1. Removes `solders` from `environment.yml` (pip-only)
2. `make install` in hummingbot → `conda env hummingbot`
3. `pip install solders>=0.19.0` into hummingbot env
4. `pnpm install && pnpm build && pnpm run setup:with-defaults` for gateway
5. `conda env create` for hummingbot-api
6. `pip install -e <hummingbot_dir> --no-deps` → wires local source into API env

**Options:**
```bash
--skip-hbot      # skip hummingbot conda install
--skip-gateway   # skip gateway pnpm install
--skip-api       # skip hummingbot-api install
--no-local-hbot  # use PyPI hummingbot in API env instead of local source
```

---

## Command: build-all

Build hummingbot wheel and all Docker images in the correct order.

```bash
bash scripts/build_all.sh
```

**Build order:**
1. `hummingbot` wheel (`dist/*.whl`) via `python setup.py bdist_wheel`
2. `hummingbot/hummingbot:dev` Docker image
3. `hummingbot/gateway:dev` Docker image (also rebuilds dist/)
4. `hummingbot/hummingbot-api:dev` Docker image

**Each image is also tagged with the branch name** (e.g., `hummingbot/gateway:core-2.7`).

**Options:**
```bash
--wheel-only     # only build hummingbot wheel, no Docker
--no-docker      # skip all Docker builds
--no-hbot        # skip hummingbot builds
--no-gateway     # skip gateway builds
--no-api         # skip hummingbot-api builds
--tag <name>     # Docker tag (default: dev)
```

---

## Command: verify-build

Verify that all builds are correct and in sync.

```bash
bash scripts/verify_build.sh
```

**Checks:**
1. Each repo is on the expected branch (from `.dev-branches`)
2. Hummingbot wheel exists in `dist/`
3. Gateway `dist/` is built and not stale vs source
4. Local hummingbot source is active in hummingbot-api env
5. Docker images exist with correct branch labels
6. Running services (API + Gateway) are reachable
7. API → Gateway connectivity

```bash
bash scripts/verify_build.sh --no-docker   # skip Docker checks
bash scripts/verify_build.sh --no-running  # skip service checks
bash scripts/verify_build.sh --json        # JSON output
```

---

## Command: run-dev-stack

Start the full dev stack from source.

```bash
bash scripts/run_dev_stack.sh
```

**Start order:**
1. Docker infra (postgres + EMQX) via `docker compose up emqx postgres -d`
2. Gateway from source in background (`node dist/index.js --passphrase=hummingbot --dev`)
3. Hummingbot API from source in foreground (`uvicorn main:app --reload`)

**Options:**
```bash
--no-gateway           # skip gateway start
--passphrase <pass>    # gateway passphrase (default: hummingbot)
--stop                 # stop everything
--status               # show running status
```

**Logs:**
- Gateway logs: `tail -f ~/.openclaw/workspace/.gateway.log`
- API logs: printed to terminal (foreground)

---

## Command: start

Check the full dev environment and show a status summary.

### Step 1: Run environment check

```bash
bash scripts/check_env.sh --json
```

### Step 2: Check repo branches

```bash
bash scripts/check_repos.sh --json
```

### Step 3: Check running services

```bash
bash scripts/check_api.sh --json
bash scripts/check_gateway.sh --json
```

### Step 4: Show status checklist

Present a checklist like:

```
Dev Environment Status
======================
  [x] Prerequisites     — conda, node, pnpm, docker, git OK
  [x] Hummingbot repo   — branch: development, env: hummingbot (installed)
  [x] Gateway repo      — branch: development, built: yes
  [x] Hummingbot API    — running at http://localhost:8000
  [x] Gateway           — running at http://localhost:15888
  [ ] Local hummingbot  — hummingbot-api NOT using local source

Next: run /hummingbot-developer setup-api-dev to wire API to local source
```

Adapt to actual state. If all good, show the test command.

---

## Command: setup-hummingbot

Install Hummingbot from source on the `development` branch.

### Step 1: Check prereqs

```bash
bash scripts/check_env.sh
```

### Step 2: Checkout development branch

```bash
cd <HUMMINGBOT_DIR>
git fetch origin
git checkout development
git pull origin development
```

### Step 3: Remove solders from environment.yml (pip-only package)

```bash
sed -i '' '/solders/d' setup/environment.yml 2>/dev/null || sed -i '/solders/d' setup/environment.yml
```

### Step 4: Install conda environment

```bash
make install
```

This creates the `hummingbot` conda env. Takes 3-10 minutes on first run.

### Step 5: Install solders via pip (not on conda)

```bash
conda run -n hummingbot pip install "solders>=0.19.0"
```

### Interpreting output

| Output | Meaning | Next step |
|--------|---------|-----------|
| `conda develop .` succeeds | Dev install registered | Proceed |
| `PackagesNotFoundError: solders` | Forgot step 3 | Run sed + reinstall |
| `Error: Conda is not found` | conda not in PATH | `source ~/.zshrc` or install Anaconda |
| `build_ext` errors | Missing build tools | Install Xcode CLT: `xcode-select --install` |

### After setup

```
  [x] conda env "hummingbot" created
  [x] solders installed via pip
  Run hummingbot: /hummingbot-developer run-hummingbot
  Build image:    /hummingbot-developer build-hummingbot
```

---

## Command: run-hummingbot

Run the Hummingbot CLI from source.

```bash
cd <HUMMINGBOT_DIR>
conda activate hummingbot
./bin/hummingbot_quickstart.py
```

Or via make:
```bash
cd <HUMMINGBOT_DIR>
make run
```

**Note:** This opens the interactive Hummingbot CLI. Use `exit` to quit.

To run with a specific config:
```bash
make run ARGS="--config-file-name conf_pure_mm_1.yml"
```

---

## Command: build-hummingbot

Build a Hummingbot wheel and/or Docker image from source.

### Build wheel (for local pip installs)

```bash
cd <HUMMINGBOT_DIR>
conda activate hummingbot
pip install build wheel  # if not already installed
python -m build --wheel --no-isolation
```

Wheel is output to `dist/hummingbot-*.whl`.

**Important:** The wheel must be built with Python 3.12 to match hummingbot-api's environment.

**Use this wheel to install into other envs:**
```bash
pip install dist/hummingbot-*.whl --force-reinstall --no-deps
```

### Build Linux wheel for Docker

When building hummingbot-api Docker images, you need a **Linux wheel** (not macOS/Windows). Build inside Docker to ensure compatibility:

```bash
cd <HUMMINGBOT_DIR>

# Build Linux wheel using Docker (Python 3.12 to match hummingbot-api)
docker run --rm -v $(pwd):/hummingbot -w /hummingbot continuumio/miniconda3 bash -c "
  apt-get update -qq && apt-get install -y -qq gcc g++ build-essential > /dev/null 2>&1 &&
  conda create -n build python=3.12 cython numpy -y -q &&
  conda run -n build pip install -q build wheel &&
  conda run -n build python -m build --wheel
"

# Verify the Linux wheel was created
ls dist/*linux*.whl
# Example: hummingbot-20260126-cp312-cp312-linux_aarch64.whl
```

**Platform wheel suffixes:**
- `linux_x86_64` — Linux AMD/Intel 64-bit
- `linux_aarch64` — Linux ARM64 (Apple Silicon Docker, AWS Graviton)
- `macosx_11_0_arm64` — macOS Apple Silicon (native only, NOT for Docker)
- `macosx_10_9_x86_64` — macOS Intel (native only, NOT for Docker)

### Build Docker image

```bash
cd <HUMMINGBOT_DIR>
docker build -t hummingbot/hummingbot:dev -f Dockerfile .
```

Or with make (also cleans first):
```bash
make build TAG=:dev
```

**Tag for use with hummingbot-api:**
```bash
docker build -t hummingbot/hummingbot:development -f Dockerfile .
```

### Interpreting output

| Output | Meaning |
|--------|---------|
| `Successfully built` + wheel path | Wheel ready in `dist/` |
| `Successfully tagged hummingbot/hummingbot:dev` | Docker image ready |
| `build_ext` error | Cython compile issue — check conda env is active |
| OOM during Docker build | Add `--memory 4g` flag |

---

## Command: setup-gateway

Install and configure Gateway from source.

### Step 1: Check prereqs

Requires Node.js 20+, pnpm, and git.

```bash
bash scripts/check_env.sh
```

### Step 2: Checkout development branch

```bash
cd <GATEWAY_DIR>
git fetch origin
git checkout development
git pull origin development
```

### Step 3: Install dependencies

```bash
cd <GATEWAY_DIR>
pnpm install
```

If you see USB HID errors on macOS:
```bash
pnpm install --force
```

### Step 4: Build TypeScript

```bash
pnpm build
```

### Step 5: Run setup

```bash
# Non-interactive with defaults (recommended for dev)
pnpm run setup:with-defaults

# Interactive (choose which configs to update)
pnpm run setup
```

Setup creates:
- `conf/` — chain, connector, token, and RPC configs
- `certs/` — TLS certificates (self-signed for dev)

### Interpreting output

| Output | Meaning | Next step |
|--------|---------|-----------|
| `Gateway setup complete` | Ready to start | `run-gateway` |
| `tsc` errors | TypeScript compile error | Check Node version (`node --version` ≥ 20) |
| `pnpm: command not found` | pnpm not installed | `npm install -g pnpm` |
| `ENOSPC` | Disk space | Free up space |

---

## Command: run-gateway

Run Gateway from source in dev mode (HTTP, no TLS).

```bash
cd <GATEWAY_DIR>
pnpm start --passphrase=<PASSPHRASE> --dev
```

Default passphrase matches hummingbot-api setup: `hummingbot`

```bash
pnpm start --passphrase=hummingbot --dev
```

**What `--dev` does:**
- Runs in HTTP mode (no TLS) on port 15888
- Enables verbose logging
- Hummingbot API auto-connects at `http://localhost:15888`

**Verify it's running:**
```bash
curl http://localhost:15888/
```

**Watch logs for startup sequence:**
```
Gateway listening on port 15888
Solana mainnet-beta initialized
...
```

**Configure custom RPC (recommended to avoid rate limits):**
```bash
# After gateway is running, update RPC via API
curl -X POST http://localhost:15888/network/config \
  -H "Content-Type: application/json" \
  -d '{"chain": "solana", "network": "mainnet-beta", "nodeURL": "https://your-rpc.com"}'
```

---

## Command: build-gateway

Build a Gateway Docker image from source.

```bash
cd <GATEWAY_DIR>
docker build \
  --build-arg BRANCH=$(git rev-parse --abbrev-ref HEAD) \
  --build-arg COMMIT=$(git rev-parse HEAD) \
  --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
  -t hummingbot/gateway:dev \
  -f Dockerfile .
```

**Tag as development for use with hummingbot-api:**
```bash
docker tag hummingbot/gateway:dev hummingbot/gateway:development
```

**Verify image:**
```bash
docker run --rm hummingbot/gateway:dev node -e "console.log('OK')"
```

---

## Command: setup-api-dev

Configure Hummingbot API to use a **local Hummingbot source build** instead of the PyPI package.

This lets you make changes to Hummingbot and immediately test them via the API without rebuilding Docker images.

### Step 1: Install hummingbot-api conda environment

```bash
cd <HUMMINGBOT_API_DIR>
make install
```

This creates the `hummingbot-api` conda env with the PyPI version of hummingbot.

### Step 2: Install local Hummingbot into hummingbot-api env

**Option A — Editable install (recommended for active development):**
```bash
conda run -n hummingbot-api pip install -e <HUMMINGBOT_DIR> --no-deps
```

Changes to hummingbot source are reflected immediately (no reinstall needed).

**Option B — Wheel install (for testing a specific build):**
```bash
# First build the wheel
cd <HUMMINGBOT_DIR> && conda run -n hummingbot python setup.py bdist_wheel

# Install into hummingbot-api env
conda run -n hummingbot-api pip install <HUMMINGBOT_DIR>/dist/hummingbot-*.whl --force-reinstall --no-deps
```

### Step 3: Verify local version is active

```bash
conda run -n hummingbot-api python -c "import hummingbot; print(hummingbot.__file__)"
```

Should print a path inside `<HUMMINGBOT_DIR>`, not `site-packages`.

### Step 4: Install solders

```bash
conda run -n hummingbot-api pip install "solders>=0.19.0"
```

### Interpreting output

| Output | Meaning |
|--------|---------|
| Path inside your hummingbot dir | ✅ Local source active |
| Path inside `anaconda3/.../site-packages` | ❌ Still using PyPI version |
| `ImportError: No module named hummingbot` | pip install failed — retry |

---

## Command: run-api-dev

Run Hummingbot API from source with hot-reload, using local Hummingbot.

### Step 1: Start infrastructure (postgres + EMQX via Docker)

```bash
cd <HUMMINGBOT_API_DIR>
docker compose up emqx postgres -d
```

Verify they're healthy:
```bash
docker compose ps
```

### Step 2: Run the API with uvicorn hot-reload

```bash
cd <HUMMINGBOT_API_DIR>
conda run --no-capture-output -n hummingbot-api uvicorn main:app --reload
```

Or via make:
```bash
make run
```

API is available at `http://localhost:8000`
Swagger UI at `http://localhost:8000/docs`

**What hot-reload means:** Changes to `*.py` files in hummingbot-api are applied immediately. Changes to hummingbot source (editable install) are also picked up on reload.

### Step 3: Confirm local hummingbot is in use

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

Check API logs for hummingbot version on startup.

### Useful dev commands

```bash
# Watch logs
conda run -n hummingbot-api uvicorn main:app --reload --log-level debug

# Run on different port
conda run -n hummingbot-api uvicorn main:app --reload --port 8001

# Check what's running
docker compose ps
curl http://localhost:8000/health
```

---

## Command: test-integration

Smoke test the full dev stack — API, Gateway, and Hummingbot connectivity.

```bash
bash scripts/check_api.sh
bash scripts/check_gateway.sh
python scripts/test_integration.py
```

### What gets tested

| Test | Checks |
|------|--------|
| API health | `GET /health` returns 200 |
| API version | Confirms hummingbot source path (not PyPI) |
| Gateway health | `GET /` on port 15888 returns 200 |
| API→Gateway | API can reach Gateway (`/gateway/status`) |
| Connectors | At least one connector visible via API |
| Wallets | Gateway wallet list accessible |

### Interpreting results

| Output | Meaning | Fix |
|--------|---------|-----|
| `✓ API running` | API up | — |
| `✓ Gateway running` | Gateway up | — |
| `✓ API→Gateway connected` | Full stack wired | — |
| `✗ API not running` | Start with `run-api-dev` | — |
| `✗ Gateway not running` | Start with `run-gateway` | — |
| `✗ API→Gateway: connection refused` | Gateway URL mismatch | Check `.env` `GATEWAY_URL=http://localhost:15888` |
| `✗ Local hummingbot not active` | Using PyPI version | Run `setup-api-dev` |

---

## Docker-Based API Development

For testing with Docker containers (instead of source), build a custom hummingbot-api image with your hummingbot wheel.

### Step 1: Build Linux wheel for Docker

```bash
cd <HUMMINGBOT_DIR>

# Build Linux wheel using Docker (Python 3.12)
docker run --rm -v $(pwd):/hummingbot -w /hummingbot continuumio/miniconda3 bash -c "
  apt-get update -qq && apt-get install -y -qq gcc g++ build-essential > /dev/null 2>&1 &&
  conda create -n build python=3.12 cython numpy -y -q &&
  conda run -n build pip install -q build wheel &&
  conda run -n build python -m build --wheel
"

ls dist/*linux*.whl
```

### Step 2: Build hummingbot-api Docker image

```bash
cd <HUMMINGBOT_API_DIR>

# Copy wheel to API directory
cp <HUMMINGBOT_DIR>/dist/hummingbot-*-cp312-*-linux_*.whl .

# Update environment.docker.yml with wheel filename
# Then build using Dockerfile.dev
docker build -f Dockerfile.dev -t hummingbot/hummingbot-api:dev .
```

### Step 3: Deploy with docker-compose.dev.yml

```bash
cd <HUMMINGBOT_API_DIR>
docker compose -f docker-compose.dev.yml up -d
```

### Step 4: Verify development features

```bash
# Check lp_executor is available (only in development hummingbot)
curl -s -u admin:admin http://localhost:8000/executors/types/available | grep lp_executor
```

---

## Deploying Bots with Custom Images

When deploying bots via the API, specify which hummingbot Docker image to use.

### Deploy with development image

```bash
curl -X POST http://localhost:8000/bot-orchestration/deploy-v2-controllers \
  -u admin:admin \
  -H "Content-Type: application/json" \
  -d '{
    "instance_name": "my-bot",
    "credentials_profile": "master_account",
    "controllers_config": ["my_controller.yml"],
    "image": "hummingbot/hummingbot:development"
  }'
```

### Available hummingbot images

| Image | Description |
|-------|-------------|
| `hummingbot/hummingbot:latest` | Stable PyPI release (default) |
| `hummingbot/hummingbot:development` | Development branch from Docker Hub |
| `hummingbot/hummingbot:dev` | Locally built image |

### DEX connectors require Gateway

For connectors like `meteora/clmm`, Gateway must be running:

```bash
docker run -d --name gateway -p 15888:15888 \
  -e GATEWAY_PASSPHRASE=admin \
  hummingbot/gateway:development
```

---

## Quick Reference

### Full Dev Setup (first time)

```bash
# 1. Setup repos
cd ~/Documents/hummingbot && git checkout development && git pull
cd ~/.openclaw/workspace/hummingbot-gateway && git checkout development && git pull

# 2. Install hummingbot
cd ~/Documents/hummingbot
sed -i '' '/solders/d' setup/environment.yml
make install
conda run -n hummingbot pip install "solders>=0.19.0"

# 3. Install gateway
cd ~/.openclaw/workspace/hummingbot-gateway
pnpm install && pnpm build && pnpm run setup:with-defaults

# 4. Wire hummingbot-api to local source
cd ~/.openclaw/workspace/hummingbot-api
make install
conda run -n hummingbot-api pip install -e ~/Documents/hummingbot --no-deps
conda run -n hummingbot-api pip install "solders>=0.19.0"

# 5. Start everything
cd ~/.openclaw/workspace/hummingbot-gateway
pnpm start --passphrase=hummingbot --dev &

cd ~/.openclaw/workspace/hummingbot-api
docker compose up emqx postgres -d
make run
```

### Testing a Hummingbot Change

```bash
# 1. Make changes in hummingbot source
# 2. If editable install: just save the file (hot-reload picks it up)
# 3. If wheel install: rebuild and reinstall
cd ~/Documents/hummingbot
conda run -n hummingbot python setup.py bdist_wheel
conda run -n hummingbot-api pip install dist/hummingbot-*.whl --force-reinstall --no-deps
# 4. Restart API
# 5. Run tests
python scripts/test_integration.py
```

### Repo Paths (defaults)

| Component | Default path |
|-----------|-------------|
| Hummingbot | `~/Documents/hummingbot` |
| Gateway | `~/.openclaw/workspace/hummingbot-gateway` |
| Hummingbot API | `~/.openclaw/workspace/hummingbot-api` |

Override by setting env vars:
```bash
export HUMMINGBOT_DIR=~/code/hummingbot
export GATEWAY_DIR=~/code/gateway
export HUMMINGBOT_API_DIR=~/code/hummingbot-api
```

### Scripts Reference

| Script | Purpose |
|--------|---------|
| `check_env.sh` | Verify prereqs (conda, node, pnpm, docker, git) |
| `check_repos.sh` | Show branch + build status for each repo |
| `check_api.sh` | Check if Hummingbot API is running |
| `check_gateway.sh` | Check if Gateway is running |
| `test_integration.py` | End-to-end smoke tests |
