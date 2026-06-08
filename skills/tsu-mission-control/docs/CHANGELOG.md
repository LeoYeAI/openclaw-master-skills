# Changelog

## V1.1.1

### Bug Fixes

- **Fixed hook auth header mismatch**: SKILL.md, HOOK-EVENTS.md, and API-REFERENCE.md incorrectly documented `Authorization: Bearer` but the backend validates `X-Hook-Secret`. All docs now correctly show `X-Hook-Secret: YOUR_HOOK_SECRET`.
- **Fixed SQLite migration crash**: `cost_daily` table used `COALESCE(project_id, '')` in a PRIMARY KEY constraint, which is not valid SQLite syntax. Replaced with `INTEGER PRIMARY KEY AUTOINCREMENT` + `UNIQUE(date, agent_id, model, project_id)` and changed `project_id` to `NOT NULL DEFAULT ''`. Also fixed matching `ON CONFLICT` clauses in `costs.js` and `hooks.js`.
- **Fixed ClawHub slug**: Docs referenced `clawhub install mission-control` but the actual published slug is `tsu-mission-control`.
- **Fixed dispatcher not reaching agents**: `sessions.send` was never a valid gateway RPC method. Rewrote dispatcher with three delivery paths: (1) HTTP POST to gateway `/hooks/agent` endpoint with `x-openclaw-token` header, (2) WebSocket `agent` method with `idempotencyKey`, (3) persistent `pending_dispatches` SQLite queue that agents poll via `GET /api/dispatch/pending/:agentId`.
- **Fixed project kickoff never firing**: Request conversion created projects with status `approved` instead of `active`, so `onProjectActivated` never triggered and agents were never told to start. Conversion now creates projects as `active`.

### New: Dispatch Delivery System

- **Pending dispatches queue**: New `pending_dispatches` table (migration 005) stores every outbound event as a guaranteed delivery floor. Events are written here first, then pushed via HTTP/WS. If push succeeds, the pending record is cleaned up. If push fails, the agent picks it up on next poll.
- **Polling API**: New route `GET /api/dispatch/pending/:agentId` returns undelivered events and marks them delivered. Also: `?peek=true` to look without consuming, `/count` for quick checks, `POST /api/dispatch/ack` for explicit acknowledgment.
- **Natural language formatting**: Every outbound event is formatted into a plain-language message with `ACTION REQUIRED` callouts, so agents can act even without SKILL.md loaded. Each message includes the exact API calls needed.
- **Auto-cleanup**: Stall detector's periodic sweep now deletes delivered dispatches older than 24h and all dispatches older than 72h.

### Documentation

- **Added Trigger Contracts section** to SKILL.md: Four complete end-to-end workflow chains (Request Approved → Project Kickoff, Project Activated → Start Working, Review Approved → Next Task, Changes Requested → Revise and Resubmit) with exact agent response requirements and failure consequences.
- **Added LAN/systemd runbook** to GETTING-STARTED.md: How to bind frontend to `0.0.0.0`, set CORS for LAN access, and full systemd user service unit files for running as persistent services.

### Upgrading from V1.1.0

If you already have a database from V1.1.0, the `cost_daily` table schema changed. Delete the old database and let it recreate:

```bash
rm ~/.openclaw/mission-control/backend/data/mission-control.db
cd ~/.openclaw/mission-control && npm run dev
```

Or manually fix the existing database:

```sql
ALTER TABLE cost_daily RENAME TO cost_daily_old;
CREATE TABLE cost_daily (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT NOT NULL, agent_id TEXT NOT NULL,
  model TEXT NOT NULL DEFAULT '', project_id TEXT NOT NULL DEFAULT '',
  total_input INTEGER DEFAULT 0, total_output INTEGER DEFAULT 0,
  total_cache INTEGER DEFAULT 0, total_cost_usd REAL DEFAULT 0,
  run_count INTEGER DEFAULT 0,
  UNIQUE (date, agent_id, model, project_id)
);
INSERT INTO cost_daily (date, agent_id, model, project_id, total_input, total_output, total_cache, total_cost_usd, run_count)
  SELECT date, agent_id, model, COALESCE(project_id, ''), total_input, total_output, total_cache, total_cost_usd, run_count FROM cost_daily_old;
DROP TABLE cost_daily_old;
```

---

## V1.1.0

### Markdown Renderer

- Replaced regex-based Markdown renderer with the `marked` library
- Full GFM support: tables, nested lists, strikethrough, code blocks with language hints
- XSS protection: `stripDangerousHtml` pass after rendering removes script tags, event handlers, iframes
- Renders six formats: Markdown, HTML, JSON (pretty-printed), CSV (styled tables), code (monospace), plain text

### Pagination

- New `usePagination` hook for offset-based "Load More" pagination
- Library document list loads 25 at a time instead of all at once
- Activity feed loads 50 at a time with "Load More" button
- Both reset automatically when filters change
- Backend activity endpoint now supports `offset` parameter

### Browser Notifications

- Desktop notifications fire when the tab is not focused (requests permission on first load)
- In-app toasts fire always — color-coded by type, auto-dismiss after 5 seconds
- Notifies on: review submitted, approval needed, request submitted, task stalled, task failed, document published, agent error
- SSE listener expanded to cover all 30+ event types

### Error Handling (from V1.0.1)

- Global `wrapRouter` wraps every route handler in try/catch — thrown errors go to error middleware instead of crashing
- Global `errorMiddleware` logs full stack trace server-side, sends safe JSON to client
- Dispatcher is completely fire-and-forget — gateway disconnect never breaks route handlers
- Three levels of try/catch in dispatch: outer, DB write, WebSocket send

### Input Sanitization (from V1.0.1)

- `sanitizeBody` middleware strips dangerous HTML from all incoming request bodies
- Removes `<script>`, event handlers (`onerror=`), `javascript:` URLs, `<iframe>/<embed>/<object>/<form>` tags
- `validate()` function checks required fields, types, string lengths, enum whitelists
- Applied to hooks, library, projects, tasks, and requests endpoints

### Outbound Dispatcher (from V1.0.1)

- 13 outbound events dispatched back to agents when humans make decisions
- Review approved/changes/rejected → agent knows to continue, revise, or move on
- Approval granted/denied → agent resumes or handles denial
- Project kickoff → agent starts planning tasks
- Task assigned/resume/queued → agent picks up or continues work
- Project activated/paused/completed → agent starts, stops, or acknowledges
- Stall nudge → agent reports status immediately

---

## V1.0.0

Initial release.

- 8 dashboard views: Dashboard, Inbox, Pipeline, Projects, Library, Agents, Costs, Activity
- Unified Inbox merging requests, reviews, and approvals
- Pipeline kanban with enforced state machine transitions
- Library with collections, tags, multi-format reader, full-text search (FTS5), versioning
- 12 inbound hook events for agent → Mission Control communication
- OpenClaw Gateway WebSocket integration for agent presence and health
- Background stall detector (flags tasks stuck 120+ min, stale agents)
- Cost tracking per session, agent, model, and project
- SQLite database with 4 migration files
- Docker Compose support
- Lifecycle hook for OpenClaw integration
- SKILL.md for agent system prompt injection
