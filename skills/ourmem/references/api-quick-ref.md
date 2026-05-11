# ourmem API Quick Reference

Base URL: `https://api.ourmem.ai` (hosted) or `http://localhost:8080` (self-hosted)

Auth: `X-API-Key: YOUR_API_KEY` header on all `/v1/*` endpoints (except tenant creation and health).

Optional: `X-Agent-Id: agent-name` header for multi-agent isolation.

## Tenant

```bash
# Create tenant (returns API key)
curl -sX POST $API_URL/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{"name": "my-workspace"}'
# -> {"id": "...", "api_key": "...", "status": "active"}
```

## Memories

```bash
# Store (direct)
curl -sX POST $API_URL/v1/memories \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"content": "User prefers dark mode", "tags": ["preferences"]}'

# Store (smart ingest from conversation)
curl -sX POST $API_URL/v1/memories \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"messages": [{"role":"user","content":"I use Rust"},{"role":"assistant","content":"Got it."}], "mode": "smart"}'

# Search
curl -s "$API_URL/v1/memories/search?q=dark+mode&limit=5" -H "X-API-Key: $KEY"

# Search across all Spaces
curl -s "$API_URL/v1/memories/search?q=architecture&space=all" -H "X-API-Key: $KEY"

# List (with filters)
curl -s "$API_URL/v1/memories?category=preferences&tier=core&limit=20" -H "X-API-Key: $KEY"

# Get by ID
curl -s $API_URL/v1/memories/MEMORY_ID -H "X-API-Key: $KEY"

# Update
curl -sX PUT $API_URL/v1/memories/MEMORY_ID \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"content": "Updated content", "tags": ["updated"]}'

# Delete (soft)
curl -sX DELETE $API_URL/v1/memories/MEMORY_ID -H "X-API-Key: $KEY"
```

## User Profile

```bash
# Get profile (static facts + dynamic context)
curl -s "$API_URL/v1/profile" -H "X-API-Key: $KEY"

# Profile with related search
curl -s "$API_URL/v1/profile?q=programming+languages" -H "X-API-Key: $KEY"
```

## Spaces

```bash
# List my spaces
curl -s $API_URL/v1/spaces -H "X-API-Key: $KEY"

# Create team space
curl -sX POST $API_URL/v1/spaces \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"name": "Backend Team", "space_type": "team"}'

# Add member
curl -sX POST $API_URL/v1/spaces/SPACE_ID/members \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"user_id": "user-002", "role": "member"}'

# Share memory to space
curl -sX POST $API_URL/v1/memories/MEMORY_ID/share \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"target_space": "team/SPACE_UUID"}'

# Batch share
curl -sX POST $API_URL/v1/memories/batch-share \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"memory_ids": ["id1","id2"], "target_space": "team/SPACE_UUID"}'

# Pull memory from space
curl -sX POST $API_URL/v1/memories/MEMORY_ID/pull \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"source_space": "team/SPACE_UUID"}'

# Reshare (refresh stale shared copy)
curl -sX POST $API_URL/v1/memories/COPY_ID/reshare \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"target_space": "team/SPACE_UUID"}'

# Share to user (one-step cross-user share, auto-creates bridging space)
curl -sX POST $API_URL/v1/memories/MEMORY_ID/share-to-user \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"target_user": "TARGET_USER_TENANT_ID"}'

# Share all to user (bulk cross-user share with filters)
curl -sX POST $API_URL/v1/memories/share-all-to-user \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"target_user": "TARGET_USER_TENANT_ID", "filters": {"min_importance": 0.7}}'

# Search with stale detection
curl -s "$API_URL/v1/memories/search?q=architecture&space=all&check_stale=true" -H "X-API-Key: $KEY"

```

## File Upload

```bash
# Upload PDF/image/code for memory extraction
curl -sX POST $API_URL/v1/files \
  -H "X-API-Key: $KEY" \
  -F "file=@document.pdf"
# -> {"task_id": "...", "filename": "document.pdf", "chunks_created": 12}
```

## GitHub Connector

```bash
# Connect a repo
curl -sX POST $API_URL/v1/connectors/github/connect \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"access_token": "ghp_xxx", "repo": "org/repo", "webhook_url": "https://your-server/v1/connectors/github/webhook"}'
```

## Stats

```bash
# Overview (by type/category/tier/space/agent + timeline)
curl -s "$API_URL/v1/stats?days=30" -H "X-API-Key: $KEY"

# Space overview (per-space stats, member contributions)
curl -s $API_URL/v1/stats/spaces -H "X-API-Key: $KEY"

# Sharing flow (who shared what, where, when + flow graph)
curl -s "$API_URL/v1/stats/sharing?days=30" -H "X-API-Key: $KEY"

# Agent activity (per-agent creation counts, top categories)
curl -s $API_URL/v1/stats/agents -H "X-API-Key: $KEY"

# Tag frequency
curl -s "$API_URL/v1/stats/tags?limit=10" -H "X-API-Key: $KEY"

# Decay curve for a specific memory
curl -s "$API_URL/v1/stats/decay?memory_id=MEMORY_ID&points=90" -H "X-API-Key: $KEY"

# Relation graph (memory relationship network with cross-space edges)
curl -s "$API_URL/v1/stats/relations?limit=100" -H "X-API-Key: $KEY"

# Server config (decay params, promotion thresholds, retrieval settings)
curl -s $API_URL/v1/stats/config -H "X-API-Key: $KEY"
```

## Health

```bash
curl -s $API_URL/health
# -> {"status": "ok"}
```

## Full API Documentation

For complete endpoint details, request/response schemas, and error codes, READ `docs/API.md`.

## Imports

```bash
# Batch import a file (with adaptive strategy)
curl -sX POST $API_URL/v1/imports -H "X-API-Key: $KEY" \
  -F "file=@memory.json" -F "file_type=memory" -F "strategy=auto"
# strategy: auto (default) | atomic | section | document

# Check import progress
curl -s "$API_URL/v1/imports/IMPORT_ID" -H "X-API-Key: $KEY"

# Trigger intelligence on past import
curl -sX POST "$API_URL/v1/imports/IMPORT_ID/intelligence" -H "X-API-Key: $KEY"

# Cross-reconcile (discover relations via vector similarity)
curl -sX POST $API_URL/v1/imports/cross-reconcile -H "X-API-Key: $KEY"

# Rollback an import
curl -sX POST $API_URL/v1/imports/IMPORT_ID/rollback -H "X-API-Key: $KEY"
```

## Delete

```bash
# Batch delete by IDs
curl -sX POST $API_URL/v1/memories/batch-delete \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"memory_ids": ["id1", "id2"]}'

# Batch delete by filter (preview)
curl -sX POST $API_URL/v1/memories/batch-delete \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"filter": {"source": "import"}, "confirm": false}'

# Batch delete by filter (execute)
curl -sX POST $API_URL/v1/memories/batch-delete \
  -H "Content-Type: application/json" -H "X-API-Key: $KEY" \
  -d '{"filter": {"source": "import"}, "confirm": true}'

# Delete all memories (requires confirmation header)
curl -sX DELETE $API_URL/v1/memories/all \
  -H "X-API-Key: $KEY" -H "X-Confirm: delete-all"
```
