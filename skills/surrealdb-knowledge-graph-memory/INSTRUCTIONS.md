# SurrealDB Memory v2 - Instructions

Complete setup and usage guide for the SurrealDB Knowledge Graph Memory skill.

## Installation

### 1. Install SurrealDB

**Option A: Automatic (runs curl | sh)**
```bash
./scripts/install.sh
```

**Option B: Manual (recommended)**
```bash
# Linux/macOS
curl -sSf https://install.surrealdb.com | sh

# Or download from https://surrealdb.com/install
```

### 2. Set Up Python Environment

```bash
cd /path/to/surrealdb-memory

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r scripts/requirements.txt
```

### 3. Set API Key

```bash
export OPENAI_API_KEY="sk-..."
```

### 4. Start SurrealDB Server

```bash
# Create data directory
mkdir -p ~/.openclaw/memory

# Start server (keep running or use systemd)
surreal start --bind 127.0.0.1:8000 --user root --pass root file:~/.openclaw/memory/knowledge.db
```

### 5. Initialize Schema

```bash
# For new installations
./scripts/init-db.sh

# For existing v1 installations upgrading to v2
python3 scripts/migrate-v2.py
```

### 6. Configure MCP Server

Add to your mcporter config (`~/.config/mcporter/servers.json` or workspace `config/mcporter.json`):

```json
{
  "mcpServers": {
    "surrealdb-memory": {
      "command": "/path/to/.venv/bin/python3 /path/to/scripts/mcp-server-v2.py"
    }
  }
}
```

### 7. Create Working Memory Directory

```bash
mkdir -p ~/.openclaw/workspace/.working-memory
```

---

## Usage

### For Agents (AI Assistants)

#### Searching Knowledge

```bash
# Semantic search
mcporter call surrealdb-memory.knowledge_search query="user preferences" limit:5

# Search with task context (boosts relevant facts)
mcporter call surrealdb-memory.context_aware_search \
    query="API auth" \
    task_context="Building OAuth integration"
```

#### Storing Facts

```bash
# Regular storage (may be batched)
mcporter call surrealdb-memory.knowledge_store \
    content="User prefers dark mode" \
    confidence:0.9

# Important fact - immediate write
mcporter call surrealdb-memory.knowledge_store_sync \
    content="API key rotated on 2026-02-17" \
    importance:0.85
```

#### Working with Episodes

```bash
# Find similar past tasks
mcporter call surrealdb-memory.episode_search query="deploy website"

# Get learnings for current task
mcporter call surrealdb-memory.episode_learnings task_goal="Deploy REST API"

# Check current task status
mcporter call surrealdb-memory.working_memory_status
```

#### Full Statistics

```bash
mcporter call surrealdb-memory.knowledge_stats
# Returns: { facts, entities, relations, episodes, avg_confidence }
```

### For Developers

#### Working Memory API

```python
from working_memory import WorkingMemory

wm = WorkingMemory()

# Start a task
wm.start_task("Build feature X", plan=[
    {"action": "Research requirements"},
    {"action": "Implement core logic"},
    {"action": "Write tests"},
    {"action": "Deploy"}
])

# Update progress
wm.update_step(0, status="complete", result_summary="Found 5 requirements")
wm.update_step(1, status="in_progress")

# Record decisions
wm.add_decision("Using REST over GraphQL for simplicity")

# Record learnings
wm.add_learning("Always check rate limits on external APIs")

# Complete and store episode
episode = wm.complete_task(outcome="success")
```

#### Episodic Memory API

```python
from episodes import EpisodicMemory

em = EpisodicMemory()

# Search for similar episodes
similar = em.find_similar_episodes("Deploy marketing pipeline", limit=5)

# Get learnings
learnings = em.get_learnings_for_task("API integration")

# Store an episode
em.store_episode(episode_data)
```

---

## Dashboard Integration

### Installing the Memory Tab

1. **Copy gateway handler:**
   ```bash
   cp openclaw-integration/gateway/memory.ts /path/to/openclaw/src/gateway/server-methods/
   ```

2. **Add to server-methods.ts:**
   ```typescript
   import { memoryHandlers } from "./server-methods/memory.js";
   
   // Add to coreGatewayHandlers:
   ...memoryHandlers,
   ```

3. **Copy UI files:**
   ```bash
   cp openclaw-integration/ui/memory-view.ts /path/to/openclaw/src/control-ui/views/
   cp openclaw-integration/ui/memory-controller.ts /path/to/openclaw/src/control-ui/controllers/
   ```

4. **Register the tab** in nav.ts:
   ```typescript
   { id: "memory", label: "Memory", icon: "🧠", section: "System" }
   ```

5. **Rebuild:**
   ```bash
   cd /path/to/openclaw && npm run build
   ```

---

## Maintenance

### Daily Tasks (via cron or heartbeat)

```bash
# Run extraction check
python3 scripts/extract-knowledge.py check

# If needed, run extraction
python3 scripts/extract-knowledge.py extract
```

### Weekly Tasks

```bash
# Full maintenance (decay + prune)
python3 scripts/memory-cli.py maintain

# Discover new relationships
python3 scripts/extract-knowledge.py discover-relations
```

### Heartbeat Integration

Add to `HEARTBEAT.md`:
```markdown
## Memory Maintenance (rotate through, 1-2x per week)
- Check if knowledge extraction is needed
- Run relation discovery if >100 unlinked facts
- Review episode outcomes for calibration
```

---

## Systemd Service (Optional)

Create `/etc/systemd/user/surrealdb.service`:

```ini
[Unit]
Description=SurrealDB Server
After=network.target

[Service]
Type=simple
ExecStart=/home/%u/.surrealdb/surreal start --bind 127.0.0.1:8000 --user root --pass root file:/home/%u/.openclaw/memory/knowledge.db
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

Enable and start:
```bash
systemctl --user daemon-reload
systemctl --user enable surrealdb
systemctl --user start surrealdb
```

---

## Troubleshooting

### Connection Issues

```bash
# Check if server is running
curl http://localhost:8000/health

# Check port usage
lsof -i :8000
```

### Schema Issues

```bash
# Re-apply v2 schema (safe)
python3 scripts/migrate-v2.py

# Force recreate tables
python3 scripts/migrate-v2.py --force
```

### MCP Server Issues

```bash
# Test MCP server directly
python3 scripts/mcp-server-v2.py

# Check mcporter can reach it
mcporter list surrealdb-memory
```

### Embedding Issues

```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test embedding generation
python3 -c "import openai; print(openai.embeddings.create(model='text-embedding-3-small', input='test').data[0].embedding[:5])"
```

---

## Configuration

Create `~/.openclaw/surrealdb-memory.yaml` for custom settings:

```yaml
connection: "http://localhost:8000"
namespace: openclaw
database: memory
user: root
password: root

embedding:
  provider: openai
  model: text-embedding-3-small
  dimensions: 1536

confidence:
  decay_rate: 0.05       # per month
  support_threshold: 0.7
  contradict_drain: 0.20
  outcome_weight: 0.2    # v2: how much outcomes affect confidence

maintenance:
  prune_after_days: 30
  min_confidence: 0.2

working_memory:
  path: ~/.working-memory
  checkpoint_interval: 60  # seconds
```

---

## Version Upgrade

### Upgrading from v1 to v2

1. **Backup data:**
   ```bash
   cp -r ~/.openclaw/memory ~/.openclaw/memory.backup
   ```

2. **Apply v2 schema:**
   ```bash
   python3 scripts/migrate-v2.py
   ```

3. **Update MCP config** to use `mcp-server-v2.py`

4. **Create working memory directory:**
   ```bash
   mkdir -p ~/.openclaw/workspace/.working-memory
   ```

5. **Verify:**
   ```bash
   mcporter call surrealdb-memory.knowledge_stats
   # Should show "episodes" count
   ```

All existing facts are preserved. New v2 fields have safe defaults.
