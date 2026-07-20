# n8n-claw Architecture Reference

The advanced paradigm of rebuilding the OpenClaw agent entirely within the n8n ecosystem using Supabase for state persistence and Claude as the cognitive engine.

---

## Table of Contents

1. [Architecture Overview](#overview)
2. [The Core Triad](#core-triad)
3. [Supabase Database Schema](#database-schema)
4. [Workflow Catalog](#workflow-catalog)
5. [Semantic Memory and RAG Pipeline](#rag-pipeline)
6. [MCP Builder: Self-Expanding Agent](#mcp-builder)
7. [Telegram Interface](#telegram-interface)
8. [Deployment Guide](#deployment)

---

## Architecture Overview

The n8n-claw project abandons OpenClaw's original Node.js/TypeScript runtime. Instead, it recreates the agent's entire cognitive infrastructure as n8n workflows, making the underlying logic fully transparent and modifiable without traditional coding.

```
┌─────────────────────────────────────────────────────┐
│                    n8n-claw Stack                     │
│                                                       │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │  Telegram    │  │   n8n        │  │  Supabase   │ │
│  │  Bot API     │──│  Workflows   │──│  PostgreSQL │ │
│  │  (Interface) │  │  (Brain)     │  │  (Memory)   │ │
│  └─────────────┘  └──────┬───────┘  └─────────────┘ │
│                          │                            │
│                   ┌──────┴───────┐                    │
│                   │    Claude    │                    │
│                   │  (Cognition) │                    │
│                   └──────────────┘                    │
└─────────────────────────────────────────────────────┘
```

### Why Rebuild Inside n8n?

| Concern | Standalone OpenClaw | n8n-claw |
|---------|--------------------|---------| 
| Memory persistence | Fragile local Markdown files | PostgreSQL with vector embeddings |
| Workflow transparency | Opaque TypeScript runtime | Visual node graphs, fully inspectable |
| Self-expansion | ClawHub skills (supply chain risk) | MCP Builder generates workflows autonomously |
| Interface | CLI + multiple bridge services | Single Telegram bot (or any webhook) |
| State management | Files that degrade with context window | Structured database tables with defined schemas |
| Debugging | Log archaeology | Click-through execution inspector |

---

## The Core Triad

### n8n (The Orchestration Brain)

Serves as the central execution engine:
- Manages the Telegram bot interface (receiving and sending messages)
- Schedules background cron tasks (Heartbeat workflow runs every 15 minutes)
- Executes all tool calls deterministically
- Chains multi-step reasoning into visual pipelines

### Supabase (The State and Memory Layer)

Replaces OpenClaw's local Markdown memory files with a robust PostgreSQL database:
- PostgREST auto-generated REST API for database access from n8n
- Row Level Security (RLS) for multi-user isolation
- pgvector extension for semantic search over long-term memory
- Supabase Studio for visual database administration

### Claude (The Cognitive Engine)

Anthropic's LLM processes natural language, maintains conversational context, and drives decision-making:
- Receives structured prompts assembled by n8n from database state
- Returns structured responses that n8n parses and routes
- Has no direct access to tools or APIs — n8n mediates everything

---

## Supabase Database Schema

### Core Tables

**`soul`** — Agent personality and behavioral boundaries
```sql
CREATE TABLE soul (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  personality TEXT NOT NULL,      -- Core character description
  boundaries TEXT,                -- Hard limits on behavior
  linguistic_vibe TEXT,           -- Tone, vocabulary preferences
  active BOOLEAN DEFAULT true,
  updated_at TIMESTAMPTZ DEFAULT now()
);
```
Administrators can hot-swap the agent's persona by toggling the `active` flag — no service restart required.

**`conversations`** — Historical dialogue tracking
```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_conversations_user ON conversations(user_id, created_at DESC);
```

**`user_profiles`** — User-specific metadata
```sql
CREATE TABLE user_profiles (
  user_id TEXT PRIMARY KEY,
  display_name TEXT,
  timezone TEXT DEFAULT 'UTC',
  preferences JSONB DEFAULT '{}',
  first_seen TIMESTAMPTZ DEFAULT now(),
  last_active TIMESTAMPTZ DEFAULT now()
);
```

**`mcp_registry`** — Available server capabilities
```sql
CREATE TABLE mcp_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  server_name TEXT NOT NULL,
  server_url TEXT NOT NULL,
  capabilities JSONB NOT NULL,   -- Tool definitions
  status TEXT DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**`agents`** — Specific tool instructions and context
```sql
CREATE TABLE agents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  instructions TEXT NOT NULL,    -- Detailed tool-use instructions
  tools JSONB DEFAULT '[]',      -- Available tool definitions
  active BOOLEAN DEFAULT true
);
```

### Memory Tables

**`memory_daily`** — Raw interaction logs for consolidation
```sql
CREATE TABLE memory_daily (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  content TEXT NOT NULL,
  interaction_type TEXT,          -- 'conversation', 'task', 'correction'
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**`memory_long`** — Consolidated long-term memory with vector embeddings
```sql
CREATE TABLE memory_long (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL,
  summary TEXT NOT NULL,          -- Human-readable summary
  embedding VECTOR(1536),         -- Vector embedding for semantic search
  source_date DATE NOT NULL,      -- Date of original interactions
  importance FLOAT DEFAULT 0.5,   -- Relevance weighting
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_memory_long_embedding ON memory_long
  USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## Workflow Catalog

The n8n-claw system consists of several interconnected workflows:

### 1. Main Chat Handler
**Trigger**: Telegram webhook (incoming message)
**Flow**:
```
Telegram Trigger
  → Fetch user profile from Supabase
  → Fetch relevant long-term memories (semantic search)
  → Fetch recent conversation history (last N messages)
  → Assemble system prompt (soul + memories + history)
  → Claude API call (with assembled context)
  → Parse response
  → Store conversation in Supabase
  → Send response via Telegram
```

### 2. Heartbeat (Proactive Agent)
**Trigger**: Cron schedule (every 15 minutes)
**Flow**:
```
Schedule Trigger
  → Check for pending reminders in Supabase
  → Check for scheduled tasks
  → If pending items exist:
    → Assemble context for each item
    → Claude decides on proactive action
    → Execute action (send message, trigger workflow, etc.)
  → Log heartbeat execution
```

This transforms the agent from reactive (waits for user) to proactive (checks and acts on schedule).

### 3. Memory Consolidation (Daily RAG Pipeline)
**Trigger**: Cron schedule (3:00 AM daily)
**Flow**: See [RAG Pipeline section](#rag-pipeline) below

### 4. MCP Builder (Self-Expansion)
**Trigger**: Agent tool call requesting new integration
**Flow**: See [MCP Builder section](#mcp-builder) below

### 5. Calendar Manager
**Trigger**: Telegram message containing calendar-related intent
**Flow**:
```
Intent Detection
  → Google Calendar API (via n8n node)
  → Format events for user
  → Return to main chat handler
```

### 6. Reminder System
**Trigger**: Telegram message containing reminder intent
**Flow**:
```
Parse reminder details (time, message)
  → Store in Supabase reminders table
  → Heartbeat workflow picks up when due
  → Send reminder via Telegram
```

---

## Semantic Memory and RAG Pipeline

### The Problem with Flat Context

Standard agents degrade as conversations lengthen. When the context window approaches 64k tokens, the agent begins "forgetting" earlier instructions, preferences, and critical constraints. OpenClaw's approach — writing flat-text summaries to local Markdown files — creates brittle, keyword-dependent recall.

### The n8n-claw Solution: Vector-Based Consolidation

Every night at 3:00 AM, an automated pipeline converts raw interaction logs into semantically searchable long-term memory.

### Pipeline Stages

```
Stage 1: EXTRACT
├── Query memory_daily table for previous day's interactions
├── Filter by user_id
└── Aggregate into chronological log

Stage 2: SUMMARIZE
├── Send interaction log to Claude
├── Prompt: "Generate compact summaries focusing on:
│   - User preferences and habits
│   - Factual corrections issued by user
│   - Operational patterns and workflows
│   - Emotional context and relationship dynamics"
└── Receive structured summaries

Stage 3: EMBED
├── Send each summary to embedding model
│   Options: OpenAI text-embedding-3-small
│            Voyage AI voyage-3
│            Local Ollama (nomic-embed-text)
└── Receive 1536-dimensional vectors

Stage 4: STORE
├── Insert summaries + vectors into memory_long table
├── Associate with source_date and user_id
└── Calculate importance score based on interaction density

Stage 5: CLEANUP
├── Delete processed rows from memory_daily
└── Log consolidation metrics
```

### Retrieval at Query Time

When a user sends a message, the Main Chat Handler:

1. Converts the user's current message to a vector embedding
2. Performs cosine similarity search against `memory_long` table
3. Returns top-K most semantically relevant memories
4. Injects these memories into the system prompt as context

This allows the agent to match the **meaning and intent** of the current query against historical context, rather than relying on brittle exact-keyword matching.

### Embedding Model Options

| Model | Dimensions | Speed | Privacy | Cost |
|-------|-----------|-------|---------|------|
| OpenAI text-embedding-3-small | 1536 | Fast | Cloud | ~$0.02/1M tokens |
| Voyage AI voyage-3 | 1024 | Fast | Cloud | ~$0.06/1M tokens |
| Ollama nomic-embed-text | 768 | Medium | Local | Free (compute only) |
| Ollama mxbai-embed-large | 1024 | Medium | Local | Free (compute only) |

For maximum data sovereignty, use local Ollama embeddings. Adjust the `VECTOR()` dimension in the schema to match your chosen model.

---

## MCP Builder: Self-Expanding Agent

The most advanced capability: the agent can autonomously build new API integrations.

### Trigger Condition

User requests an integration the agent doesn't currently have. Example: "Connect to my Notion workspace and pull today's tasks."

### Build Pipeline

```
Stage 1: RESEARCH
├── Agent recognizes it lacks Notion integration
├── Triggers MCP Builder workflow
├── n8n uses local SearXNG instance to search for Notion API documentation
│   (SearXNG avoids dependency on paid search APIs like Brave)
└── Fetches and ingests relevant developer docs

Stage 2: GENERATE
├── n8n invokes Claude Code CLI (@anthropic-ai/claude-code)
│   installed globally via npm
│   integrated via n8n-nodes-claude-code-cli community node
├── Claude Code generates:
│   - MCP server integration code
│   - Trigger workflow (webhook or schedule)
│   - Functional sub-workflow (API operations)
└── Output: two new n8n workflow JSON definitions

Stage 3: DEPLOY
├── n8n programmatically creates both workflows
├── Registers new capability in mcp_registry table
├── Agent's tool catalog is updated for future queries
└── User is notified of new capability

Stage 4: CREDENTIAL BINDING (Human Step)
├── Human logs into n8n UI
├── Provisions API credentials for new integration
├── Tests the generated workflow
└── Activates and locks the workflow
```

### Prerequisites

**Claude Code CLI Installation**:
```bash
npm install -g @anthropic-ai/claude-code
```

**n8n Docker Compose** must include:
```yaml
environment:
  - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

**Community Node**: Install `n8n-nodes-claude-code-cli` from n8n's community node marketplace.

### Security Consideration

The MCP Builder is powerful but requires the same air-gap procedure as any other workflow. The generated integration code must be reviewed by a human before credentials are provisioned. Never auto-bind credentials to agent-generated workflows.

---

## Telegram Interface

### Bot Setup

1. Create a bot via @BotFather on Telegram
2. Receive the bot token
3. Configure the token in n8n's Telegram node credentials
4. Set the webhook URL to your n8n instance's Telegram trigger endpoint

### Message Flow

```
User → Telegram → n8n Telegram Trigger
  → Main Chat Handler workflow
    → Claude reasoning
  → n8n Telegram Send node
User ← Telegram ← Response
```

### Supported Interactions

- Text messages → conversational AI
- `/remind` command → reminder system
- `/calendar` command → calendar manager
- `/status` command → system health check
- File uploads → document processing pipeline
- Voice messages → transcription + processing (if Whisper integration configured)

---

## Deployment

### Docker Compose Template

```yaml
version: "3.8"

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:5678:5678"
    volumes:
      - n8n-data:/home/node/.n8n
    environment:
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}
      - WEBHOOK_URL=https://n8n.yourdomain.com
      - N8N_DEFAULT_BINARY_DATA_MODE=filesystem
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - GENERIC_TIMEZONE=${TIMEZONE}
    depends_on:
      - supabase-db

  supabase-db:
    image: supabase/postgres:15.1.0.147
    restart: unless-stopped
    ports:
      - "127.0.0.1:5432:5432"
    volumes:
      - supabase-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=n8n_claw

  supabase-studio:
    image: supabase/studio:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:3001:3000"  # Localhost only! Access via SSH tunnel
    environment:
      - SUPABASE_URL=http://supabase-db:5432
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

  searxng:
    image: searxng/searxng:latest
    restart: unless-stopped
    ports:
      - "127.0.0.1:8080:8080"
    volumes:
      - searxng-data:/etc/searxng

volumes:
  n8n-data:
  supabase-data:
  searxng-data:
```

### Supabase Studio Access

Supabase Studio is bound to localhost for security. Access requires an SSH tunnel:

```bash
ssh -L 3001:localhost:3001 user@YOUR-VPS-IP
# Then open http://localhost:3001 in browser
```

### Database Initialization

Create an `init.sql` file with the schema from the [Database Schema section](#database-schema). Include the pgvector extension:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
-- Then create all tables as defined above
```

### Environment Variables

```env
N8N_ENCRYPTION_KEY=<openssl rand -hex 32>
ANTHROPIC_API_KEY=sk-ant-...
POSTGRES_PASSWORD=<strong-password>
TIMEZONE=America/New_York
TELEGRAM_BOT_TOKEN=<from-botfather>
```

### Post-Deployment Checklist

- [ ] All containers running (`docker compose ps`)
- [ ] Supabase database initialized with schema
- [ ] pgvector extension enabled
- [ ] n8n accessible via reverse proxy with SSL
- [ ] Telegram bot webhook configured
- [ ] Anthropic API key tested
- [ ] SearXNG accessible from n8n container
- [ ] Memory consolidation cron workflow created (3:00 AM)
- [ ] Heartbeat workflow created (every 15 minutes)
- [ ] Main chat handler workflow tested with sample message
- [ ] Supabase Studio accessible via SSH tunnel
- [ ] Soul table populated with agent personality
