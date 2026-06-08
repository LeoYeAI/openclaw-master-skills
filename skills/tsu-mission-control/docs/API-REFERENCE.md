# API Reference

Mission Control backend runs at `http://localhost:8000` by default. All endpoints return JSON.

---

## Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/projects` | List all projects. Filter: `?status=active&owner=main` |
| GET | `/api/projects/:id` | Get project with task counts |
| POST | `/api/projects` | Create project |
| PATCH | `/api/projects/:id` | Update project fields |
| DELETE | `/api/projects/:id` | Delete project (cascades tasks) |

**Create project body:**
```json
{ "name": "My Project", "description": "...", "priority": "high", "owner_agent": "main" }
```

---

## Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tasks` | List tasks. Filter: `?project_id=X&pipeline_stage=doing` |
| GET | `/api/tasks/:id` | Get task with activity and tags |
| POST | `/api/tasks` | Create task |
| PATCH | `/api/tasks/:id` | Update task fields |
| POST | `/api/tasks/:id/move` | Move task to new pipeline stage |
| DELETE | `/api/tasks/:id` | Delete task |
| GET | `/api/tasks/pipeline/overview` | All tasks grouped by stage |

**Move task body:**
```json
{ "to_stage": "doing", "actor": "main" }
```

**Pipeline stages and valid transitions:**
```
backlog → todo
todo    → doing, backlog
doing   → review, todo
review  → done, doing
done    → (terminal)
```

---

## Unified Inbox

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/inbox` | Merged queue of requests, reviews, approvals. Filter: `?type=review&status=pending` |
| GET | `/api/inbox/counts` | Badge counts: `{ requests, reviews, approvals, total }` |

Items are sorted: pending first, then by urgency, then newest.

---

## Requests

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/requests` | List project requests |
| POST | `/api/requests` | Submit a request |
| POST | `/api/requests/:id/triage` | Triage: approve, reject, defer |
| POST | `/api/requests/:id/convert` | Convert approved request to project |

---

## Reviews

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reviews` | List reviews. Filter: `?status=pending` |
| GET | `/api/reviews/:id` | Full review with comments and versions |
| POST | `/api/reviews` | Create a review (usually done by hook) |
| POST | `/api/reviews/:id/comment` | Add a comment |
| POST | `/api/reviews/:id/decide` | Approve, request changes, or reject |
| GET | `/api/reviews/stats/summary` | Aggregate metrics |

**Decide body:**
```json
{ "decision": "approved", "notes": "Looks good", "quality_score": 5, "reviewer": "user" }
```

---

## Approvals

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/approvals` | List approvals |
| POST | `/api/approvals` | Create an approval gate |
| POST | `/api/approvals/:id/decide` | Approve or reject |

---

## Library

### Collections

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/library/collections` | List all collections (returns tree + flat) |
| POST | `/api/library/collections` | Create a collection |
| PATCH | `/api/library/collections/:id` | Update collection |
| DELETE | `/api/library/collections/:id` | Delete (moves docs to uncategorized) |

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/library/documents` | Browse documents. Filter: `?collection_id=X&doc_type=research&status=published` |
| GET | `/api/library/documents/:id` | Full document with content, tags, version history |
| POST | `/api/library/documents` | Create/publish a document |
| PATCH | `/api/library/documents/:id` | Update (creates new version if content changes) |
| DELETE | `/api/library/documents/:id` | Delete document |
| GET | `/api/library/documents/:id/versions/:v` | Get specific version content |

### Search & Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/library/search?q=term` | Full-text search across titles and content |
| GET | `/api/library/tags` | List all tags with doc counts |
| POST | `/api/library/tags` | Create a tag |
| GET | `/api/library/stats` | Library statistics |

---

## Agents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/agents` | List all agents with task counts |
| PUT | `/api/agents/:id` | Upsert agent (used by gateway sync) |
| POST | `/api/agents/:id/heartbeat` | Record heartbeat |

---

## Costs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/costs/summary?days=30` | Cost dashboard: totals, daily, by agent, by model, by project |
| POST | `/api/costs` | Record a cost entry |

---

## Events & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/events/stream` | SSE stream for real-time push |
| GET | `/api/events/stats` | Dashboard statistics |
| GET | `/api/events/activity?limit=50` | Activity log |
| GET | `/api/health` | Health check with pending counts |

---

## Hooks

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/hooks/event` | Receive lifecycle events from OpenClaw |

**Headers:**
```
Content-Type: application/json
X-Hook-Secret: YOUR_HOOK_SECRET
```

See `HOOK-EVENTS.md` for all supported events and payloads.

---

## Dispatch (Outbound Events)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dispatch/pending/:agentId` | Poll for undelivered events. Marks as delivered. |
| GET | `/api/dispatch/pending/:agentId?peek=true` | Peek at events without consuming them |
| GET | `/api/dispatch/pending/:agentId/count` | Quick count of pending events |
| POST | `/api/dispatch/ack` | Acknowledge events by ID: `{ "ids": [1, 2] }` |

Events are queued in `pending_dispatches` whenever a human makes a decision (approves, rejects, converts, etc.). Mission Control also tries to push them via the gateway's `/hooks/agent` HTTP endpoint and WebSocket `agent` method. The polling path is the guaranteed fallback.
