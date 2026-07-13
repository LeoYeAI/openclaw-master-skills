---
name: mirofish-offline-simulation
description: Fully local multi-agent swarm intelligence simulation engine using Neo4j + Ollama for public opinion, market sentiment, and social dynamics prediction.
triggers:
  - set up mirofish offline simulation
  - run multi-agent social simulation locally
  - simulate public reaction to a document
  - configure neo4j ollama agent simulation
  - mirofish offline install and configure
  - generate swarm intelligence prediction
  - simulate market sentiment with local llm
  - add mirofish agent simulation to my project
---

# MiroFish-Offline Skill

> Skill by [ara.so](https://ara.so) — Daily 2026 Skills collection.

MiroFish-Offline is a fully local multi-agent swarm intelligence engine. Feed it any document (press release, policy draft, financial report) and it generates hundreds of AI agents with unique personalities that simulate public reaction on social media — posts, arguments, opinion shifts — hour by hour. No cloud APIs required: Neo4j CE 5.15 handles graph memory, Ollama serves the LLMs.

---

## Architecture Overview

```
Document Input
     │
     ▼
Graph Build (NER + relationship extraction via Ollama LLM)
     │
     ▼
Neo4j Knowledge Graph (entities, relations, embeddings via nomic-embed-text)
     │
     ▼
Env Setup (generate hundreds of agent personas with personalities + memory)
     │
     ▼
Simulation (agents post, reply, argue, shift opinions on simulated platforms)
     │
     ▼
Report (ReportAgent interviews focus group, queries graph, generates analysis)
     │
     ▼
Interaction (chat with any individual agent, full memory persists)
```

**Backend**: Flask + Python 3.11  
**Frontend**: Vue 3 + Node 18  
**Graph DB**: Neo4j CE 5.15 (bolt protocol)  
**LLM**: Ollama (OpenAI-compatible `/v1` endpoint)  
**Embeddings**: `nomic-embed-text` (768-dimensional, via Ollama)  
**Search**: Hybrid — 0.7 × vector similarity + 0.3 × BM25

---

## Installation

### Option A: Docker (Recommended)

```bash
git clone https://github.com/nikmcfly/MiroFish-Offline.git
cd MiroFish-Offline
cp .env.example .env

# Start Neo4j + Ollama + MiroFish backend + frontend
docker compose up -d

# Pull required models into the Ollama container
docker exec mirofish-ollama ollama pull qwen2.5:32b
docker exec mirofish-ollama ollama pull nomic-embed-text

# Check all services are healthy
docker compose ps
```

Open `http://localhost:3000`.

### Option B: Manual Setup

**1. Neo4j**
```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/mirofish \
  neo4j:5.15-community
```

**2. Ollama**
```bash
ollama serve &
ollama pull qwen2.5:32b       # Main LLM (~20GB, requires 24GB VRAM)
ollama pull qwen2.5:14b       # Lighter option (~10GB VRAM)
ollama pull nomic-embed-text  # Embeddings (small, fast)
```

**3. Backend**
```bash
cp .env.example .env
# Edit .env (see Configuration section)

cd backend
pip install -r requirements.txt
python run.py
# Backend starts on http://localhost:5000
```

**4. Frontend**
```bash
cd frontend
npm install
npm run dev
# Frontend starts on http://localhost:3000
```

---

## Configuration (`.env`)

```bash
# ── LLM (Ollama OpenAI-compatible endpoint) ──────────────────────────
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=qwen2.5:32b

# ── Neo4j ─────────────────────────────────────────────────────────────
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=mirofish

# ── Embeddings (Ollama) ───────────────────────────────────────────────
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_BASE_URL=http://localhost:11434

# ── Optional: swap Ollama for any OpenAI-compatible provider ─────────
# LLM_API_KEY=$OPENAI_API_KEY
# LLM_BASE_URL=https://api.openai.com/v1
# LLM_MODEL_NAME=gpt-4o
```

---

## Core Python API

### GraphStorage Interface

The abstraction layer between MiroFish and the graph database:

```python
from backend.storage.base import GraphStorage
from backend.storage.neo4j_storage import Neo4jStorage

# Initialize storage (typically done via Flask app.extensions)
storage = Neo4jStorage(
    uri=os.environ["NEO4J_URI"],
    user=os.environ["NEO4J_USER"],
    password=os.environ["NEO4J_PASSWORD"],
    embedding_model=os.environ["EMBEDDING_MODEL"],
    embedding_base_url=os.environ["EMBEDDING_BASE_URL"],
    llm_base_url=os.environ["LLM_BASE_URL"],
    llm_api_key=os.environ["LLM_API_KEY"],
    llm_model=os.environ["LLM_MODEL_NAME"],
)
```

### Building a Knowledge Graph from a Document

```python
from backend.services.graph_builder import GraphBuilder

builder = GraphBuilder(storage=storage)

# Feed a document string
with open("press_release.txt", "r") as f:
    document_text = f.read()

# Extract entities + relationships, store in Neo4j
graph_id = builder.build(
    content=document_text,
    title="Q4 Earnings Report",
    source_type="financial_report",
)

print(f"Graph built: {graph_id}")
# Returns a graph_id used for subsequent simulation runs
```

### Creating and Running a Simulation

```python
from backend.services.simulation import SimulationService

sim = SimulationService(storage=storage)

# Create a simulation environment from an existing graph
sim_id = sim.create_environment(
    graph_id=graph_id,
    agent_count=200,           # Number of agents to generate
    simulation_hours=24,       # Simulated time span
    platform="twitter",        # "twitter" | "reddit" | "weibo"
)

# Run the simulation (blocking — use async wrapper for production)
result = sim.run(sim_id=sim_id)

print(f"Simulation complete. Posts generated: {result['post_count']}")
print(f"Sentiment trajectory: {result['sentiment_over_time']}")
```

### Querying Simulation Results

```python
from backend.services.report import ReportAgent

report_agent = ReportAgent(storage=storage)

# Generate a structured analysis report
report = report_agent.generate(
    sim_id=sim_id,
    focus_group_size=10,    # Number of agents to interview
    include_graph_search=True,
)

print(report["summary"])
print(report["key_narratives"])
print(report["sentiment_shift"])
print(report["influential_agents"])
```

### Chatting with a Simulated Agent

```python
from backend.services.agent_chat import AgentChatService

chat = AgentChatService(storage=storage)

# List agents from a completed simulation
agents = chat.list_agents(sim_id=sim_id, limit=10)
agent_id = agents[0]["id"]

print(f"Chatting with: {agents[0]['persona']['name']}")
print(f"Personality: {agents[0]['persona']['traits']}")

# Send a message — agent responds in-character with full memory
response = chat.send(
    agent_id=agent_id,
    message="Why did you post that criticism about the earnings report?",
)

print(response["reply"])
# → Agent responds using its personality, opinion bias, and post history
```

### Hybrid Search on the Knowledge Graph

```python
from backend.services.search import SearchService

search = SearchService(storage=storage)

# Hybrid search: 0.7 * vector similarity + 0.3 * BM25
results = search.query(
    text="executive compensation controversy",
    graph_id=graph_id,
    top_k=5,
    vector_weight=0.7,
    bm25_weight=0.3,
)

for r in results:
    print(r["entity"], r["relationship"], r["score"])
```

### Implementing a Custom GraphStorage Backend

```python
from backend.storage.base import GraphStorage
from typing import List, Dict, Any

class MyCustomStorage(GraphStorage):
    """
    Swap Neo4j for any graph DB by implementing this interface.
    Register via Flask app.extensions['neo4j_storage'] = MyCustomStorage(...)
    """

    def store_entity(self, entity: Dict[str, Any]) -> str:
        # Store entity, return entity_id
        raise NotImplementedError

    def store_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Dict[str, Any],
    ) -> str:
        raise NotImplementedError

    def vector_search(
        self, embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def keyword_search(
        self, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError

    def get_agent_memory(self, agent_id: str) -> Dict[str, Any]:
        raise NotImplementedError

    def update_agent_memory(
        self, agent_id: str, memory_update: Dict[str, Any]
    ) -> None:
        raise NotImplementedError
```

### Flask App Integration Pattern

```python
# backend/app.py — how storage is wired via dependency injection
from flask import Flask
from backend.storage.neo4j_storage import Neo4jStorage
import os

def create_app():
    app = Flask(__name__)

    # Single storage instance, injected everywhere via app.extensions
    storage = Neo4jStorage(
        uri=os.environ["NEO4J_URI"],
        user=os.environ["NEO4J_USER"],
        password=os.environ["NEO4J_PASSWORD"],
        embedding_model=os.environ["EMBEDDING_MODEL"],
        embedding_base_url=os.environ["EMBEDDING_BASE_URL"],
        llm_base_url=os.environ["LLM_BASE_URL"],
        llm_api_key=os.environ["LLM_API_KEY"],
        llm_model=os.environ["LLM_MODEL_NAME"],
    )
    app.extensions["neo4j_storage"] = storage

    from backend.routes import graph_bp, simulation_bp, report_bp
    app.register_blueprint(graph_bp)
    app.register_blueprint(simulation_bp)
    app.register_blueprint(report_bp)

    return app
```

### Accessing Storage in a Flask Route

```python
from flask import Blueprint, current_app, request, jsonify

simulation_bp = Blueprint("simulation", __name__)

@simulation_bp.route("/api/simulation/run", methods=["POST"])
def run_simulation():
    storage = current_app.extensions["neo4j_storage"]
    data = request.json

    sim = SimulationService(storage=storage)
    sim_id = sim.create_environment(
        graph_id=data["graph_id"],
        agent_count=data.get("agent_count", 200),
        simulation_hours=data.get("simulation_hours", 24),
    )
    result = sim.run(sim_id=sim_id)
    return jsonify(result)
```

---

## REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/graph/build` | Upload document, build knowledge graph |
| `GET` | `/api/graph/:id` | Get graph entities and relationships |
| `POST` | `/api/simulation/create` | Create simulation environment |
| `POST` | `/api/simulation/run` | Execute simulation |
| `GET` | `/api/simulation/:id/results` | Get posts, sentiment, metrics |
| `GET` | `/api/simulation/:id/agents` | List generated agents |
| `POST` | `/api/report/generate` | Generate ReportAgent analysis |
| `POST` | `/api/agent/:id/chat` | Chat with a specific agent |
| `GET` | `/api/search` | Hybrid search the knowledge graph |

**Example: Build graph from document**
```bash
curl -X POST http://localhost:5000/api/graph/build \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Acme Corp announces record Q4 earnings, CFO resigns...",
    "title": "Q4 Press Release",
    "source_type": "press_release"
  }'
# → {"graph_id": "g_abc123", "entities": 47, "relationships": 89}
```

**Example: Run a simulation**
```bash
curl -X POST http://localhost:5000/api/simulation/run \
  -H "Content-Type: application/json" \
  -d '{
    "graph_id": "g_abc123",
    "agent_count": 150,
    "simulation_hours": 12,
    "platform": "twitter"
  }'
# → {"sim_id": "s_xyz789", "status": "running"}
```

---

## Hardware Selection Guide

| Use Case | Model | VRAM | RAM |
|----------|-------|------|-----|
| Quick test / dev | `qwen2.5:7b` | 6 GB | 16 GB |
| Balanced quality | `qwen2.5:14b` | 10 GB | 16 GB |
| Production quality | `qwen2.5:32b` | 24 GB | 32 GB |
| CPU-only (slow) | `qwen2.5:7b` | None | 16 GB |

Switch model by editing `.env`:
```bash
LLM_MODEL_NAME=qwen2.5:14b
```
Then restart the backend — no other changes needed.

---

## Common Patterns

### PR Crisis Test Pipeline

```python
import os
from backend.storage.neo4j_storage import Neo4jStorage
from backend.services.graph_builder import GraphBuilder
from backend.services.simulation import SimulationService
from backend.services.report import ReportAgent

storage = Neo4jStorage(
    uri=os.environ["NEO4J_URI"],
    user=os.environ["NEO4J_USER"],
    password=os.environ["NEO4J_PASSWORD"],
    embedding_model=os.environ["EMBEDDING_MODEL"],
    embedding_base_url=os.environ["EMBEDDING_BASE_URL"],
    llm_base_url=os.environ["LLM_BASE_URL"],
    llm_api_key=os.environ["LLM_API_KEY"],
    llm_model=os.environ["LLM_MODEL_NAME"],
)

def test_press_release(text: str) -> dict:
    # 1. Build knowledge graph
    builder = GraphBuilder(storage=storage)
    graph_id = builder.build(content=text, title="Draft PR", source_type="press_release")

    # 2. Simulate public reaction
    sim = SimulationService(storage=storage)
    sim_id = sim.create_environment(graph_id=graph_id, agent_count=300, simulation_hours=48)
    sim.run(sim_id=sim_id)

    # 3. Generate report
    report = ReportAgent(storage=storage).generate(sim_id=sim_id, focus_group_size=15)

    return {
        "sentiment_peak": report["sentiment_over_time"][0],
        "key_narratives": report["key_narratives"],
        "risk_score": report["risk_score"],
        "recommended_edits": report["recommendations"],
    }

# Usage
with open("draft_announcement.txt") as f:
    result = test_press_release(f.read())

print(f"Risk score: {result['risk_score']}/10")
print(f"Top narrative: {result['key_narratives'][0]}")
```

### Use Any OpenAI-Compatible Provider

```bash
# Claude via Anthropic (or any proxy)
LLM_API_KEY=$ANTHROPIC_API_KEY
LLM_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL_NAME=claude-3-5-sonnet-20241022

# OpenAI
LLM_API_KEY=$OPENAI_API_KEY
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4o

# Local LM Studio
LLM_API_KEY=lm-studio
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL_NAME=your-loaded-model
```

---

## Troubleshooting

### Neo4j connection refused
```bash
# Check Neo4j is running
docker ps | grep neo4j
# Check bolt port
nc -zv localhost 7687
# View Neo4j logs
docker logs neo4j --tail 50
```

### Ollama model not found
```bash
# List available models
ollama list
# Pull missing models
ollama pull qwen2.5:32b
ollama pull nomic-embed-text
# Check Ollama is serving
curl http://localhost:11434/api/tags
```

### Out of VRAM
```bash
# Switch to smaller model in .env
LLM_MODEL_NAME=qwen2.5:14b   # or qwen2.5:7b
# Restart backend
cd backend && python run.py
```

### Embeddings dimension mismatch
```bash
# nomic-embed-text produces 768-dim vectors
# If you switch embedding models, drop and recreate the Neo4j vector index:
# In Neo4j browser (http://localhost:7474):
# DROP INDEX entity_embedding IF EXISTS;
# Then restart MiroFish — it recreates the index with correct dimensions.
```

### Docker Compose: Ollama container can't access GPU
```yaml
# docker-compose.yml — add GPU reservation:
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Slow simulation on CPU
- Use `qwen2.5:7b` for faster (lower quality) inference
- Reduce `agent_count` to 50–100 for testing
- Reduce `simulation_hours` to 6–12
- CPU inference with 7b model: expect ~5–10 tokens/sec

### Frontend can't reach backend
```bash
# Check VITE_API_BASE_URL in frontend/.env
VITE_API_BASE_URL=http://localhost:5000

# Verify backend is up
curl http://localhost:5000/api/health
```

---

## Project Structure

```
MiroFish-Offline/
├── backend/
│   ├── run.py                    # Entry point
│   ├── app.py                    # Flask factory, DI wiring
│   ├── storage/
│   │   ├── base.py               # GraphStorage abstract interface
│   │   └── neo4j_storage.py      # Neo4j implementation
│   ├── services/
│   │   ├── graph_builder.py      # NER + relationship extraction
│   │   ├── simulation.py         # Agent simulation engine
│   │   ├── report.py             # ReportAgent + focus group
│   │   ├── agent_chat.py         # Per-agent chat interface
│   │   └── search.py             # Hybrid vector + BM25 search
│   └── routes/
│       ├── graph.py
│       ├── simulation.py
│       └── report.py
├── frontend/                     # Vue 3 (fully English UI)
├── docker-compose.yml
├── .env.example
└── README.md
```
