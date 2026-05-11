# ourmem Self-Hosted Setup Guide

API Base: `http://localhost:8080` (or your custom host)

Self-hosting gives you full control over your data. Everything stays on your infrastructure. You need Docker (or the binary) and optionally an object storage backend.

## Prerequisites

- Docker Engine 20+ with Docker Compose v2
- OR: the `omem-server` binary (Rust, single file)

## Option A: Docker (recommended)

### Quick one-liner

```bash
# Minimal (BM25 search only, no embedding API needed)
docker run -d --name omem -p 8080:8080 ghcr.io/ourmem/omem-server:latest

# With Bedrock embedding (recommended, needs AWS credentials)
docker run -d --name omem -p 8080:8080 \
  -e OMEM_EMBED_PROVIDER=bedrock \
  -e AWS_REGION=us-east-1 \
  ghcr.io/ourmem/omem-server:latest

# With OpenAI-compatible embedding
docker run -d --name omem -p 8080:8080 \
  -e OMEM_EMBED_PROVIDER=openai-compatible \
  -e OMEM_EMBED_API_KEY=sk-xxx \
  ghcr.io/ourmem/omem-server:latest
```

### From source repo

```bash
git clone https://github.com/ourmem/omem.git
cd omem
cp .env.example .env
docker-compose up -d
```

This starts two services:

| Service | Port | Description |
|---------|------|-------------|
| omem-server | 8080 | REST API |
| MinIO | 9000/9001 | S3-compatible storage (dev mode) |

### Verify the server

```bash
curl http://localhost:8080/health
# -> {"status":"ok"}
```

## Option B: Pre-built Binary

Two release artifacts are available:

| File | Build | LLM Support |
|------|-------|-------------|
| `omem-server-vX.Y.Z-linux-amd64.tar.gz` | musl static | OpenAI-compatible (DashScope, Ollama, etc) |
| `omem-server-vX.Y.Z-linux-amd64-bedrock.tar.gz` | glibc dynamic | All above + AWS Bedrock |

Download from the [GitHub releases page](https://github.com/ourmem/omem/releases):

```bash
# musl static binary (runs on any Linux x86_64, zero dependencies)
curl -LO https://github.com/ourmem/omem/releases/latest/download/omem-server-vX.Y.Z-linux-amd64.tar.gz
tar xzf omem-server-vX.Y.Z-linux-amd64.tar.gz
chmod +x omem-server

# Run
OMEM_PORT=8080 \
OMEM_EMBED_PROVIDER=noop \
./omem-server
```

Replace `vX.Y.Z` with the actual version number from the releases page.

## Option C: Build from source (musl static binary)

Build a single static binary that runs on **any Linux x86_64** with zero dependencies:

```bash
rustup target add x86_64-unknown-linux-musl

RUSTFLAGS="-C target-feature=+crt-static -C relocation-model=static" \
  cargo build --release --target x86_64-unknown-linux-musl \
  -p omem-server --no-default-features

# Binary: target/x86_64-unknown-linux-musl/release/omem-server (~182MB, statically linked)
```

Note: `--no-default-features` disables AWS Bedrock support. Use `OMEM_EMBED_PROVIDER=openai-compatible` instead (e.g. DashScope, OpenAI).

Transfer to any server:

```bash
gzip -c target/x86_64-unknown-linux-musl/release/omem-server > omem-server.gz
scp omem-server.gz user@server:/opt/
ssh user@server "gunzip /opt/omem-server.gz && chmod +x /opt/omem-server && /opt/omem-server"
```

## Object Storage (Optional)

By default ourmem stores data on local disk. For durability and scalability, configure object storage:

### Alibaba Cloud OSS (native oss:// scheme)

```bash
OMEM_OSS_BUCKET=your-bucket
OSS_ENDPOINT=https://oss-xx-internal.aliyuncs.com
OSS_ACCESS_KEY_ID=your-ak
OSS_ACCESS_KEY_SECRET=your-sk
```

On Alibaba Cloud ECS, credentials can be auto-discovered from the ECS RAM role (no AK/SK needed).

### S3-compatible storage

```bash
OMEM_S3_BUCKET=your-bucket
AWS_ENDPOINT_URL=https://s3.amazonaws.com
AWS_REGION=us-east-1
```

> OSS takes priority over S3. If both `OMEM_OSS_BUCKET` and `OMEM_S3_BUCKET` are set, OSS is used.

## Step 1: Create API Key

```bash
curl -sX POST http://localhost:8080/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"name": "my-workspace"}' | jq .
```

Response:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "api_key": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active"
}
```

Save the `api_key`. A personal Space is created automatically.

## Step 2: Install Plugin

Pick the user's platform. All configs below use `http://localhost:8080` as the server URL. Adjust if your server runs elsewhere.

### Claude Code

`[AGENT]` Set environment variables. Add to `~/.bashrc` or `~/.zshrc` for persistence:

```bash
export OMEM_API_URL="http://localhost:8080"
export OMEM_API_KEY="YOUR_API_KEY"
```

Then install the plugin inside Claude Code:

```
/plugin marketplace add ourmem/omem
/plugin install ourmem@ourmem
```

### OpenCode

`[AGENT]` Add the plugin to `opencode.json`:

```bash
# If opencode.json exists, merge the plugin entry
jq '.plugin = ((.plugin // []) + ["@ourmem/opencode"] | unique)' opencode.json > tmp.json && mv tmp.json opencode.json
```

If no `opencode.json` exists, create one:

```json
{
  "plugin": ["@ourmem/opencode"]
}
```

Set environment variables (add to `~/.bashrc` or `~/.zshrc` for persistence):

```bash
export OMEM_API_URL="http://localhost:8080"
export OMEM_API_KEY="YOUR_API_KEY"
```

### OpenClaw

`[AGENT]` Detect npm registry reachability first (same as hosted setup). Then install:

```bash
openclaw plugins install @ourmem/openclaw

# For China/Alibaba Cloud networks:
NPM_CONFIG_REGISTRY=https://registry.npmmirror.com openclaw plugins install @ourmem/openclaw
```

Configure `openclaw.json`:

```bash
jq --arg api_key "$API_KEY" '
  .plugins.slots.memory = "ourmem" |
  if (.plugins.entries.ourmem.config // {}) == {}
  then
    .plugins.entries.ourmem = {
      enabled: true,
      config: { apiUrl: "http://localhost:8080", apiKey: $api_key }
    }
  else
    .plugins.entries.ourmem.config.apiKey = $api_key |
    .plugins.entries.ourmem.enabled = true
  end |
  .plugins.allow = ((.plugins.allow // []) + ["ourmem"] | unique)
' openclaw.json > tmp.json && mv tmp.json openclaw.json
```

If no `openclaw.json` exists, create:

```json
{
  "plugins": {
    "slots": { "memory": "ourmem" },
    "entries": {
      "ourmem": {
        "enabled": true,
        "config": {
          "apiUrl": "http://localhost:8080",
          "apiKey": "YOUR_API_KEY"
        }
      }
    },
    "allow": ["ourmem"]
  }
}
```

### MCP Server (Cursor / VS Code / Claude Desktop)

Add to your MCP config:

```json
{
  "mcpServers": {
    "ourmem": {
      "command": "npx",
      "args": ["-y", "@ourmem/mcp"],
      "env": {
        "OMEM_API_URL": "http://localhost:8080",
        "OMEM_API_KEY": "YOUR_API_KEY"
      }
    }
  }
}
```

## Step 3: Configure

Replace `YOUR_API_KEY` with the actual key from Step 1.

If the server runs on a different host or port, update `OMEM_API_URL` / `apiUrl` accordingly.

## Step 4: Restart

- **Claude Code**: restart the `claude` process
- **OpenCode**: restart the `opencode` process
- **OpenClaw**: restart the gateway
- **MCP clients**: restart the app

## Step 5: Verify

```bash
# Health
curl -sf http://localhost:8080/health && echo "OK"

# Auth
curl -sf -H "X-API-Key: YOUR_API_KEY" \
  "http://localhost:8080/v1/memories?limit=1" && echo "Auth OK"

# Store a test memory
curl -sX POST http://localhost:8080/v1/memories \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"content": "ourmem self-hosted setup complete", "tags": ["test"]}'

# Search it back
curl -s "http://localhost:8080/v1/memories/search?q=self-hosted+setup&limit=1" \
  -H "X-API-Key: YOUR_API_KEY" | jq '.results[0].memory.content'
```

If all checks pass, return to the main SKILL.md and continue with Step 5 (handoff).

## Environment Variables

Key server-side variables (set in `.env` or Docker environment):

| Variable | Default | Description |
|----------|---------|-------------|
| `OMEM_PORT` | `8080` | Server port |
| `OMEM_LOG_LEVEL` | `info` | Log level |
| `OMEM_OSS_BUCKET` | _(empty)_ | Alibaba Cloud OSS bucket (enables oss:// scheme) |
| `OMEM_S3_BUCKET` | `omem-data` | S3 bucket for LanceDB |
| `OMEM_EMBED_PROVIDER` | `noop` | Embedding: `noop`, `bedrock`, `openai-compatible` |
| `OMEM_LLM_PROVIDER` | _(empty)_ | LLM: `openai-compatible`, `bedrock` |

For production with real embeddings, set `OMEM_EMBED_PROVIDER=bedrock` (or `openai-compatible` with your endpoint).

### Example: DashScope (Alibaba Cloud)

```bash
OMEM_EMBED_PROVIDER=openai-compatible
OMEM_EMBED_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode
OMEM_EMBED_MODEL=text-embedding-v3
OMEM_EMBED_API_KEY=sk-your-dashscope-key
OMEM_LLM_PROVIDER=openai-compatible
OMEM_LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode
OMEM_LLM_MODEL=qwen-turbo
OMEM_LLM_API_KEY=sk-your-dashscope-key
```

### Example: OpenAI

```bash
OMEM_EMBED_PROVIDER=openai-compatible
OMEM_EMBED_BASE_URL=https://api.openai.com
OMEM_EMBED_MODEL=text-embedding-3-small
OMEM_EMBED_API_KEY=sk-your-openai-key
OMEM_LLM_PROVIDER=openai-compatible
OMEM_LLM_BASE_URL=https://api.openai.com
OMEM_LLM_MODEL=gpt-4o-mini
OMEM_LLM_API_KEY=sk-your-openai-key
```

### Example: AWS Bedrock (glibc build only)

```bash
OMEM_EMBED_PROVIDER=bedrock
OMEM_LLM_PROVIDER=bedrock
OMEM_LLM_MODEL=anthropic.claude-3-haiku-20240307-v1:0
AWS_REGION=us-east-1
```

See `docs/DEPLOY.md` for the full environment variable reference and deployment guide.
