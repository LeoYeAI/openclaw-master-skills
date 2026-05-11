# Engram MCP Tools Reference

Complete documentation for all 13 MCP tools exposed by Engram.

## Overview

All tools are called via MCPorter:

```bash
mcporter call engram.<tool_name> [key=value ...]
```

For complex content with newlines, use single quotes:

```bash
mcporter call engram.mem_save title="..." content='Line 1
Line 2
Line 3'
```

## Parámetro Default

El parámetro `project` es opcional. Si no se especifica:
- Engram intenta detectar el directorio actual del proyecto
- Si no puede detectarlo, usa `default` como nombre de proyecto

Para mejores resultados, especifica siempre el proyecto:

```bash
mcporter call engram.mem_context project="mi-proyecto"
```

---

## Core Tools

### mem_save

Save a structured observation to persistent memory.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `title` | string | Yes | Short, searchable title |
| `content` | string | Yes | Structured content (What/Why/Where/Learn format recommended) |
| `type` | string | No | Category: `decision`, `bugfix`, `pattern`, `config`, `discovery`, `learning`, `architecture`, `manual` |
| `project` | string | No | Project name for filtering |
| `scope` | string | No | `project` (default) or `personal` |
| `topic_key` | string | No | Stable key for upserts (same key = update existing) |

**Examples:**

```bash
# Bugfix
mcporter call engram.mem_save \
  title="Fixed N+1 query in user list" \
  type="bugfix" \
  project="mi-proyecto" \
  content='**What**: Added eager loading in UserList query
**Why**: Performance degradation with 100+ users
**Where**: src/services/users.ts
**Learned**: ORM requires explicit Preload() for associations'

# Architecture decision
mcporter call engram.mem_save \
  title="Switched from sessions to JWT" \
  type="decision" \
  project="mi-proyecto" \
  content='**What**: Replaced express-session with jsonwebtoken for auth
**Why**: Session storage doesn't scale across multiple instances
**Where**: src/middleware/auth.ts, src/routes/login.ts
**Learned**: Must set httpOnly and secure flags on cookie'

# Pattern discovery
mcporter call engram.mem_save \
  title="FTS5 query sanitization pattern" \
  type="pattern" \
  project="mi-proyecto" \
  content='**What**: Wrap search terms in quotes before FTS5 MATCH
**Why**: Special chars crash FTS5 (interprets as operators)
**Where**: internal/store/store.go — sanitizeFTS() function
**Learned**: FTS5 MATCH syntax ≠ LIKE — always sanitize user input'

# With topic_key (upsert)
mcporter call engram.mem_save \
  title="Auth architecture" \
  type="architecture" \
  topic_key="architecture/auth" \
  project="mi-proyecto" \
  content='Current auth: JWT with refresh tokens...'
```

**Recommended Content Format:**

```
**What**: [concise description of what was done]
**Why**: [the reasoning, user request, or problem that drove it]
**Where**: [files/paths affected: path/to/file.ts, other.go]
**Learned**: [any gotchas, edge cases, or decisions made — optional]
```

---

### mem_search

Full-text search across all memories using SQLite FTS5.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `query` | string | Yes | Search query (natural language or keywords) |
| `project` | string | No | Filter by project name |
| `scope` | string | No | Filter by scope: `project` or `personal` |
| `type` | string | No | Filter by type: `bugfix`, `decision`, etc. |
| `limit` | number | No | Max results (default: 10, max: 20) |

**Examples:**

```bash
# Basic search
mcporter call engram.mem_search query="auth middleware"

# Project-scoped
mcporter call engram.mem_search query="JWT" project="mi-proyecto"

# Type-filtered
mcporter call engram.mem_search query="error" type="bugfix"

# Limit results
mcporter call engram.mem_search query="config" limit=5
```

**Returns:** Compact results with observation IDs, titles, and truncated content. Use `mem_get_observation` for full content.

---

### mem_context

Get recent context from previous sessions. Call at the START of a session.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `project` | string | No | Filter by project name |
| `limit` | number | No | Number of observations (default: 20) |
| `scope` | string | No | Filter by scope: `project` or `personal` |

**Examples:**

```bash
# Get recent context for project
mcporter call engram.mem_context project="mi-proyecto"

# More observations
mcporter call engram.mem_context project="mi-proyecto" limit=30

# Personal scope
mcporter call engram.mem_context scope="personal"
```

**Returns:** Recent observations and session summaries from previous sessions.

---

### mem_session_summary

Save a comprehensive end-of-session summary. Call BEFORE ending a session.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `content` | string | Yes | Structured summary (Goal/Instructions/Discoveries/Accomplished/Files format) |
| `project` | string | Yes | Project name |
| `session_id` | string | No | Session identifier |

**Examples:**

```bash
mcporter call engram.mem_session_summary \
  project="mi-proyecto" \
  content='## Goal
Implement authentication with JWT and fix performance bugs

## Instructions
User prefers Spanish for explanations

## Discoveries
- ORM requires explicit Preload() for associations
- Validation should go in boundary layer
- Refresh tokens must rotate for security

## Accomplished
- ✅ JWT implemented with refresh tokens
- ✅ N+1 query fixed (100x faster)
- ✅ Auth middleware added
- 🔲 Integration tests pending
- 🔲 API documentation pending

## Relevant Files
- src/auth/jwt.ts — Token generation and validation
- src/middleware/auth.ts — Authentication middleware
- src/services/users.ts — Optimized queries
- src/routes/*.ts — Input validation in boundary'
```

**Required Content Format:**

```markdown
## Goal
[One sentence: what were we building/working on in this session]

## Instructions
[User preferences, constraints, or context discovered during this session. Skip if nothing notable.]

## Discoveries
- [Technical finding, gotcha, or learning 1]
- [Technical finding 2]
- [Important API behavior, config quirk, etc.]

## Accomplished
- ✅ [Completed task 1 — with key implementation details]
- ✅ [Completed task 2 — mention files changed]
- 🔲 [Identified but not yet done — for next session]

## Relevant Files
- path/to/file.ts — [what it does or what changed]
- path/to/other.go — [role in the architecture]
```

---

## Drill-Down Tools

### mem_timeline

Get chronological context around a specific observation.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `observation_id` | number | Yes | The observation ID to center on |
| `before` | number | No | Observations before (default: 5) |
| `after` | number | No | Observations after (default: 5) |

**Examples:**

```bash
mcporter call engram.mem_timeline observation_id=42
mcporter call engram.mem_timeline observation_id=42 before=10 after=10
```

**Use Case:** After `mem_search`, use this to understand what happened around a specific result.

---

### mem_get_observation

Get the full, untruncated content of a specific observation.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | number | Yes | The observation ID |

**Examples:**

```bash
mcporter call engram.mem_get_observation id=42
```

**Use Case:** After `mem_search` or `mem_timeline`, use this to get complete content.

---

## Management Tools

### mem_update

Update an existing observation by ID.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | number | Yes | The observation ID to update |
| `title` | string | No | New title |
| `content` | string | No | New content |
| `type` | string | No | New type |
| `project` | string | No | New project |
| `scope` | string | No | New scope |
| `topic_key` | string | No | New topic key |

**Examples:**

```bash
# Update content
mcporter call engram.mem_update id=42 content="Updated content..."

# Update multiple fields
mcporter call engram.mem_update id=42 title="New title" type="pattern"
```

---

### mem_delete

Delete an observation by ID.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | number | Yes | The observation ID to delete |
| `hard_delete` | boolean | No | Permanently delete (default: false = soft-delete) |

**Examples:**

```bash
# Soft delete (can be recovered)
mcporter call engram.mem_delete id=42

# Hard delete (permanent)
mcporter call engram.mem_delete id=42 hard_delete=true
```

---

### mem_suggest_topic_key

Suggest a stable topic_key for evolving topics.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `type` | string | No | Observation type (architecture, bugfix, etc.) |
| `title` | string | No | Observation title |
| `content` | string | No | Content (fallback if no title) |

**Examples:**

```bash
mcporter call engram.mem_suggest_topic_key type="architecture" title="Auth architecture"
# → architecture/auth-architecture

mcporter call engram.mem_suggest_topic_key type="bugfix" title="Auth nil panic"
# → bug/auth-nil-panic
```

**Topic Key Families:**
- `architecture/*` — Architecture/design/ADR-like changes
- `bug/*` — Fixes, regressions, errors, panics
- `decision/*` — Project decisions
- `pattern/*` — Reusable patterns
- `config/*` — Configuration changes
- `discovery/*` — Discoveries
- `learning/*` — Learnings

---

## Session Lifecycle Tools

### mem_session_start

Register the start of a new coding session.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | string | Yes | Unique session identifier |
| `project` | string | Yes | Project name |
| `directory` | string | No | Working directory |

**Examples:**

```bash
mcporter call engram.mem_session_start id="session-123" project="mi-proyecto"
```

---

### mem_session_end

Mark a session as completed.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `id` | string | Yes | Session identifier |
| `summary` | string | No | Optional summary |

**Examples:**

```bash
mcporter call engram.mem_session_end id="session-123" summary="Completed auth implementation"
```

---

### mem_save_prompt

Save a user prompt for future context.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `content` | string | Yes | The user's prompt text |
| `project` | string | No | Project name |
| `session_id` | string | No | Session identifier |

**Examples:**

```bash
mcporter call engram.mem_save_prompt \
  content="Implement OAuth2 with Google provider" \
  project="mi-proyecto"
```

---

### mem_stats

Get memory system statistics.

**Parameters:** None

**Examples:**

```bash
mcporter call engram.mem_stats
```

**Returns:** Total sessions, observations, and projects tracked.

---

## Usage Patterns

### Progressive Disclosure (3-Layer Pattern)

Token-efficient memory retrieval:

```
Layer 1: mem_search "auth"         → ~100 tokens per result + IDs
Layer 2: mem_timeline id=42        → Context around observation
Layer 3: mem_get_observation id=42 → Full untruncated content
```

### Topic Key Workflow (Evolving Topics)

For architecture decisions and long-running features:

```bash
# 1. Get stable topic key
mcporter call engram.mem_suggest_topic_key type="architecture" title="Auth"
# → architecture/auth

# 2. Save with topic_key
mcporter call engram.mem_save \
  title="Auth architecture" \
  type="architecture" \
  topic_key="architecture/auth" \
  project="mi-proyecto" \
  content="Initial decision: JWT..."

# 3. Later: update same topic (upsert)
mcporter call engram.mem_save \
  title="Auth architecture" \
  type="architecture" \
  topic_key="architecture/auth" \
  project="mi-proyecto" \
  content="Updated: Added refresh tokens..."
```

### Session Workflow

```bash
# 1. Start: recover context
mcporter call engram.mem_context project="mi-proyecto"

# 2. Work: save proactively
mcporter call engram.mem_save title="Fixed X" type="bugfix" project="mi-proyecto" content='...'

# 3. End: save summary
mcporter call engram.mem_session_summary project="mi-proyecto" content='...'
```

---

## Error Handling

If a tool call fails, check:

1. **Engram binary**: `engram version` should work
2. **MCPorter config**: `mcporter list engram` should show tools
3. **MCP registration**: Run `mcporter config add engram --stdio "engram mcp"`

---

## Data Location

- **Database**: `~/.engram/engram.db` (SQLite + FTS5)
- **Override**: Set `ENGRAM_DATA_DIR` environment variable
- **Windows**: `%USERPROFILE%\.engram\engram.db`

---

## 📖 Referencia Rápida (Español)

### Flujo Básico de Sesión

```bash
# 1. Inicio: Recuperar contexto
mcporter call engram.mem_context project="mi-proyecto"

# 2. Durante trabajo: Guardar descubrimientos
mcporter call engram.mem_save \
  title="Descripción corta" \
  type="bugfix" \
  project="mi-proyecto" \
  content='**Qué**: Lo que hice
**Por qué**: La razón
**Dónde**: archivos/afectados.ts
**Aprendido**: Lessons learned'

# 3. Fin: Resumen de sesión
mcporter call engram.mem_session_summary \
  project="mi-proyecto" \
  content='## Objetivo
Qué se construyó/trabajó

## Descubrimientos
- Hallazgo 1
- Hallazgo 2

## Completado
- ✅ Tarea 1
- ✅ Tarea 2

## Archivos Relevantes
- archivo.ts — descripción'
```

### Búsquedas Rápidas

```bash
# Buscar en memoria
mcporter call engram.mem_search query="autenticación"

# Buscar por tipo
mcporter call engram.mem_search query="error" type="bugfix"

# Ver estadísticas
mcporter call engram.mem_stats
```

### Formato de Contenido (Español)

```
**Qué**: [descripción concisa de lo que se hizo]
**Por qué**: [razonamiento/contexto]
**Dónde**: [archivos afectados: ruta/al/archivo.ts]
**Aprendido**: [gotchas, edge cases - opcional]
```

### Formato de Resumen de Sesión (Español)

```markdown
## Objetivo
[Una frase: qué se construyó/trabajó]

## Instrucciones
[Preferencias del usuario descubiertas - opcional]

## Descubrimientos
- [Hallazgo técnico 1]
- [Hallazgo técnico 2]

## Completado
- ✅ [Tarea completada 1]
- ✅ [Tarea completada 2]
- 🔲 [Identificado pero no hecho]

## Archivos Relevantes
- ruta/al/archivo.ts — [qué hace]
```
