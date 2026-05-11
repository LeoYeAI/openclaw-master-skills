# SurrealDB Memory v2.0 Upgrade Guide

This upgrade adds **Working Memory**, **Episodic Memory**, **Synchronous Writes**, **Context-Aware Retrieval**, and **Outcome Calibration** to the knowledge graph.

## Quick Start

```bash
# 1. Ensure SurrealDB is running
pgrep surreal || ~/.surrealdb/surreal start --user root --pass root file:~/.openclaw/memory/knowledge.db &

# 2. Apply v2 schema
./scripts/migrate-v2.sh

# 3. Update MCP config to use v2 server
# In your mcp config, change:
#   "command": "python3 scripts/mcp-server.py"
# To:
#   "command": "python3 scripts/mcp-server-v2.py"

# 4. Create working memory directory
mkdir -p ~/.openclaw/workspace/.working-memory
```

## Architecture Overview

```
Tier 1: Context Window (conversation)
    ↕ (continuous read/write during loop iterations)
Tier 1.5: Working Memory (.working-memory/current-task.yaml)  ← NEW
    ↕ (persisted every N iterations)
Tier 2: File-Based Memory (daily logs, MEMORY.md)
    ↕ (cron extraction + sync writes for important facts)
Tier 3: Knowledge Graph (facts, entities, relations, episodes)  ← ENHANCED
```

## New Capabilities

### 1. Working Memory (Tier 1.5)

Track current task state that survives crashes:

```python
from working_memory import WorkingMemory

wm = WorkingMemory()

# Start a task
wm.start_task("Deploy marketing pipeline", plan=[
    {"action": "Audit existing templates"},
    {"action": "Fix broken templates"},
    {"action": "Configure Mailchimp API"},
    {"action": "Test end-to-end"}
])

# Update progress
wm.update_step(1, status="complete", result_summary="Found 12 templates, 3 broken")
wm.update_step(2, status="in_progress")

# Record decisions and learnings
wm.add_decision("Using Mailchimp over SendGrid - client already has account")
wm.add_learning("Always check for OAuth token expiry before deployments")

# Complete and create episode
episode = wm.complete_task(outcome="success")
```

### 2. Episodic Memory

Learn from past task attempts:

```python
from episodes import EpisodicMemory

em = EpisodicMemory()

# Find similar past tasks
similar = em.find_similar_episodes("Deploy marketing pipeline", limit=5)

# Get actionable learnings
learnings = em.get_learnings_for_task("Deploy API integration")
# Returns: ["Always validate OAuth tokens first", "⚠️ Past failure: Token expired mid-deploy"]
```

### 3. Synchronous Fact Writes

Important discoveries get stored immediately:

```python
# Via MCP tool
mcporter call surrealdb-memory.knowledge_store_sync \
    content="Client X API uses OAuth2 not API keys" \
    importance:0.85 \
    source="explicit"

# Result: {"sync_written": true, "fact_id": "fact:abc123"}
```

### 4. Context-Aware Retrieval

Search with awareness of current task:

```python
# Via MCP tool
mcporter call surrealdb-memory.context_aware_search \
    query="API authentication" \
    task_context="Deploy marketing automation for ClientX"

# Returns facts relevant to BOTH query AND task, plus related episodes
```

### 5. Outcome Calibration

Facts that lead to success gain confidence; facts that correlate with failure lose confidence:

```sql
-- In SurrealDB, facts now have:
success_count: 3,
failure_count: 0,
last_outcome: "success"

-- Effective confidence includes outcome adjustment:
fn::effective_confidence_v2(fact_id)
```

## New MCP Tools

| Tool | Description |
|------|-------------|
| `knowledge_store_sync` | Sync write for important facts (>0.7 importance) |
| `episode_search` | Find similar past tasks |
| `episode_learnings` | Get actionable insights from history |
| `episode_store` | Store completed task episode |
| `working_memory_status` | Get current task progress |
| `context_aware_search` | Task-aware memory retrieval |

## Schema Changes

New tables:
- `episode` - Task histories with semantic search
- `working_memory` - Snapshots for crash recovery

New fields on `fact`:
- `scope` - global, client, agent
- `client_id`, `agent_id` - Multi-tenant support
- `success_count`, `failure_count` - Outcome tracking
- `last_outcome` - Most recent outcome

New functions:
- `fn::effective_confidence_v2()` - Includes outcome adjustment
- `fn::outcome_adjustment()` - Calculate confidence delta from outcomes
- `fn::scoped_search()` - Multi-tenant aware search
- `fn::context_aware_search()` - Task context boosting

## Integration Points

### Agent Loop Integration

```python
# At task start
wm = WorkingMemory()
if wm.has_active_task():
    # Resume from crash
    state = wm.get_state()
    current_step = wm.get_current_step()
else:
    # Start fresh
    wm.start_task(goal, plan)

# During iterations
wm.update_step(step_id, status="complete", result_summary="...")
wm.record_fact_used("fact:123")  # Track what knowledge we used

# On completion
episode = wm.complete_task(outcome="success")
em = EpisodicMemory()
em.store_episode(episode)  # Saves to graph with embedding
```

### Heartbeat/Cron Integration

Add to `HEARTBEAT.md`:
```markdown
## Memory Maintenance
- Check working memory for abandoned tasks (>24h no update)
- Run outcome calibration for recently completed episodes
```

## Backward Compatibility

- Original 4 tools (`knowledge_search`, `knowledge_recall`, `knowledge_store`, `knowledge_stats`) work unchanged
- Existing facts remain valid; new fields have defaults
- Can run v1 and v2 servers simultaneously (different ports)

## Troubleshooting

**"Episode table not found"**
```bash
./scripts/migrate-v2.sh
```

**"Working memory module not available"**
```bash
pip install pyyaml  # Required for working_memory.py
```

**"context_aware_search returns empty"**
- Ensure `OPENAI_API_KEY` is set for embeddings
- Check that task_context is meaningful text
