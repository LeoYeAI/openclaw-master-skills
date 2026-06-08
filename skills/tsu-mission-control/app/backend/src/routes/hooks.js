import { Router } from "express";
import { getDb } from "../db.js";
import { broadcast } from "../services/events.js";
import { wrapRouter, validate } from "../middleware.js";

const router = Router();

// Valid hook event names
const VALID_EVENTS = [
  "task:started", "task:completed", "task:failed", "task:progress", "task:review",
  "agent:idle", "agent:error", "session:created", "session:ended",
  "approval:needed", "request:submit", "library:publish", "library:update",
];

// ── HOOK RECEIVER ─────────────────────────────────────
router.post("/event", (req, res) => {
  const db = getDb();
  const { event, agentId, taskId, data, timestamp } = req.body;

  // Validate the event payload
  const err = validate(req.body, {
    event: { required: true, type: "string", maxLength: 100 },
    agentId: { type: "string", maxLength: 100 },
    taskId: { type: "string", maxLength: 100 },
  });
  if (err) return res.status(400).json({ error: err });

  if (!VALID_EVENTS.includes(event)) {
    // Log unknown events but don't reject — forward compatibility
    console.warn(`[hook] Unknown event type: ${event}`);
  }

  console.log(`[hook] ${event} from agent=${agentId || "?"} task=${taskId || "?"}`);

  switch (event) {
    case "task:started": {
      if (taskId) {
        db.prepare(`
          UPDATE tasks SET
            pipeline_stage = 'doing', status = 'in_progress',
            assigned_agent = COALESCE(?, assigned_agent),
            started_at = COALESCE(started_at, datetime('now')),
            updated_at = datetime('now')
          WHERE id = ?
        `).run(agentId || null, taskId);

        db.prepare(`
          INSERT INTO activity_log (entity_type, entity_id, action, new_value, actor, message)
          VALUES ('task', ?, 'stage_changed', 'doing', ?, ?)
        `).run(taskId, agentId || "system", `Agent ${agentId} started working on task`);
      }

      if (agentId) {
        db.prepare(`
          UPDATE agents SET status = 'busy', current_task_id = ?, last_heartbeat = datetime('now')
          WHERE id = ?
        `).run(taskId || null, agentId);
      }

      broadcast("task:started", { taskId, agentId, data });
      break;
    }

    case "task:completed": {
      if (taskId) {
        db.prepare(`
          UPDATE tasks SET
            pipeline_stage = 'done', status = 'done',
            completed_at = datetime('now'), updated_at = datetime('now'),
            actual_mins = ?
          WHERE id = ?
        `).run(data?.actualMins || null, taskId);

        db.prepare(`
          INSERT INTO activity_log (entity_type, entity_id, action, new_value, actor, message)
          VALUES ('task', ?, 'stage_changed', 'done', ?, ?)
        `).run(taskId, agentId || "system", `Task completed by ${agentId || "agent"}`);

        // Check if all tasks in the project are done
        const task = db.prepare("SELECT project_id FROM tasks WHERE id = ?").get(taskId);
        if (task?.project_id) {
          const remaining = db.prepare(`
            SELECT COUNT(*) as count FROM tasks
            WHERE project_id = ? AND pipeline_stage != 'done' AND status != 'cancelled'
          `).get(task.project_id);

          if (remaining.count === 0) {
            db.prepare(`
              UPDATE projects SET status = 'completed', completed_at = datetime('now'), updated_at = datetime('now')
              WHERE id = ?
            `).run(task.project_id);
            broadcast("project:completed", { id: task.project_id });
          }
        }
      }

      if (agentId) {
        db.prepare(`
          UPDATE agents SET status = 'idle', current_task_id = NULL, last_heartbeat = datetime('now')
          WHERE id = ?
        `).run(agentId);
      }

      broadcast("task:completed", { taskId, agentId, data });
      break;
    }

    case "task:failed": {
      if (taskId) {
        db.prepare(`
          UPDATE tasks SET
            pipeline_stage = 'blocked', status = 'blocked',
            updated_at = datetime('now'),
            metadata = json_set(COALESCE(metadata, '{}'), '$.error', ?)
          WHERE id = ?
        `).run(data?.error || "Unknown error", taskId);

        db.prepare(`
          INSERT INTO activity_log (entity_type, entity_id, action, new_value, actor, message)
          VALUES ('task', ?, 'failed', 'blocked', ?, ?)
        `).run(taskId, agentId || "system", `Task failed: ${data?.error || "unknown"}`);
      }

      if (agentId) {
        db.prepare(`
          UPDATE agents SET status = 'error', current_task_id = NULL, last_heartbeat = datetime('now')
          WHERE id = ?
        `).run(agentId);
      }

      broadcast("task:failed", { taskId, agentId, data });
      break;
    }

    case "task:progress": {
      if (taskId && data?.progress !== undefined) {
        db.prepare(`
          UPDATE tasks SET
            metadata = json_set(COALESCE(metadata, '{}'), '$.progress', ?),
            updated_at = datetime('now')
          WHERE id = ?
        `).run(data.progress, taskId);
      }
      broadcast("task:progress", { taskId, agentId, progress: data?.progress, message: data?.message });
      break;
    }

    case "task:review": {
      if (taskId) {
        db.prepare(`
          UPDATE tasks SET
            pipeline_stage = 'review', status = 'review', updated_at = datetime('now')
          WHERE id = ?
        `).run(taskId);

        db.prepare(`
          INSERT INTO activity_log (entity_type, entity_id, action, new_value, actor, message)
          VALUES ('task', ?, 'stage_changed', 'review', ?, ?)
        `).run(taskId, agentId || "system", `Task submitted for review by ${agentId || "agent"}`);

        // Auto-create a review record
        const task = db.prepare("SELECT * FROM tasks WHERE id = ?").get(taskId);
        const lastRound = db.prepare("SELECT MAX(round) as r FROM reviews WHERE task_id = ?").get(taskId);
        const round = (lastRound?.r || 0) + 1;

        db.prepare(`
          INSERT INTO reviews (task_id, project_id, round, submitted_by, deliverables, work_summary, checklist)
          VALUES (?, ?, ?, ?, ?, ?, ?)
        `).run(
          taskId,
          task?.project_id || null,
          round,
          agentId || "agent",
          JSON.stringify(data?.deliverables || []),
          data?.summary || data?.message || "",
          JSON.stringify(data?.checklist || [])
        );

        broadcast("review:submitted", { taskId, agentId, round });
      }
      broadcast("task:review", { taskId, agentId });
      break;
    }

    case "agent:idle": {
      if (agentId) {
        db.prepare(`
          UPDATE agents SET status = 'idle', current_task_id = NULL, last_heartbeat = datetime('now')
          WHERE id = ?
        `).run(agentId);
      }
      broadcast("agent:idle", { agentId });
      break;
    }

    case "agent:error": {
      if (agentId) {
        db.prepare(`
          UPDATE agents SET status = 'error', last_heartbeat = datetime('now'),
            metadata = json_set(COALESCE(metadata, '{}'), '$.lastError', ?)
          WHERE id = ?
        `).run(data?.error || "Unknown", agentId);
      }
      broadcast("agent:error", { agentId, error: data?.error });
      break;
    }

    case "session:created":
    case "session:ended": {
      if (agentId) {
        const delta = event === "session:created" ? 1 : -1;
        db.prepare(`
          UPDATE agents SET session_count = MAX(0, session_count + ?), last_heartbeat = datetime('now')
          WHERE id = ?
        `).run(delta, agentId);
      }

      // Record cost on session end if token data is provided
      if (event === "session:ended" && data?.tokens) {
        const t = data.tokens;
        db.prepare(`
          INSERT INTO cost_entries (agent_id, task_id, project_id, session_key, model, provider,
            input_tokens, output_tokens, cache_read_tokens, cache_write_tokens,
            input_cost_usd, output_cost_usd, cache_cost_usd, total_cost_usd, duration_ms)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).run(
          agentId || "unknown", taskId || null, data?.projectId || null,
          data?.sessionKey || null, t.model || "", t.provider || "",
          t.input || 0, t.output || 0, t.cacheRead || 0, t.cacheWrite || 0,
          t.inputCost || 0, t.outputCost || 0, t.cacheCost || 0, t.totalCost || 0,
          data?.durationMs || null
        );

        // Update daily aggregate
        const date = new Date().toISOString().slice(0, 10);
        db.prepare(`
          INSERT INTO cost_daily (date, agent_id, model, project_id, total_input, total_output, total_cache, total_cost_usd, run_count)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
          ON CONFLICT(date, agent_id, model, project_id)
          DO UPDATE SET
            total_input = total_input + excluded.total_input,
            total_output = total_output + excluded.total_output,
            total_cache = total_cache + excluded.total_cache,
            total_cost_usd = total_cost_usd + excluded.total_cost_usd,
            run_count = run_count + 1
        `).run(date, agentId || "unknown", t.model || "unknown", data?.projectId || "",
          t.input || 0, t.output || 0, (t.cacheRead || 0) + (t.cacheWrite || 0), t.totalCost || 0);

        broadcast("cost:recorded", { agent_id: agentId, model: t.model, total_cost_usd: t.totalCost });
      }

      broadcast(event.replace(":", "."), { agentId, sessionKey: data?.sessionKey });
      break;
    }

    case "approval:needed": {
      // Agent requests human approval (e.g. Lobster workflow gate)
      db.prepare(`
        INSERT INTO approvals (type, entity_type, entity_id, title, description, urgency, requested_by, resume_token, context)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
      `).run(
        data?.type || "workflow_gate",
        data?.entityType || "task",
        taskId || data?.entityId || null,
        data?.title || `Approval needed from ${agentId || "agent"}`,
        data?.description || "",
        data?.urgency || "normal",
        agentId || "system",
        data?.resumeToken || null,
        JSON.stringify(data?.context || {})
      );
      broadcast("approval:created", { agentId, taskId, type: data?.type });
      break;
    }

    case "request:submit": {
      // Agent submits a new project request
      const reqInfo = db.prepare(`
        INSERT INTO project_requests (title, description, requester, category, urgency, source_channel, source_ref)
        VALUES (?, ?, ?, ?, ?, ?, ?)
      `).run(
        data?.title || "Untitled request",
        data?.description || "",
        agentId || "agent",
        data?.category || "general",
        data?.urgency || "normal",
        data?.channel || "agent",
        data?.ref || null
      );
      const newReq = db.prepare("SELECT * FROM project_requests WHERE rowid = ?").get(reqInfo.lastInsertRowid);
      broadcast("request:submitted", newReq);
      break;
    }

    case "library:publish": {
      // Agent publishes a document to the Library
      const slugify = (t) => t.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 80);
      const content = data?.content || "";
      const title = data?.title || "Untitled";

      const docInfo = db.prepare(`
        INSERT INTO documents (title, slug, content, doc_type, format, collection_id,
          excerpt, word_count, author_agent, project_id, task_id, source_path, status, published_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'published', datetime('now'))
      `).run(
        title, slugify(title), content,
        data?.doc_type || "document", data?.format || "markdown",
        data?.collection_id || null,
        content.replace(/[#*_`>\[\]()!]/g, "").replace(/\n+/g, " ").trim().slice(0, 200),
        content.split(/\s+/).filter(Boolean).length,
        agentId || "agent",
        data?.projectId || null, taskId || null,
        data?.source_path || null
      );

      const doc = db.prepare("SELECT * FROM documents WHERE rowid = ?").get(docInfo.lastInsertRowid);

      // Save initial version
      db.prepare(`
        INSERT INTO document_versions (doc_id, version, content, change_note, changed_by)
        VALUES (?, 1, ?, 'Published by agent', ?)
      `).run(doc.id, content, agentId || "agent");

      db.prepare(`
        INSERT INTO activity_log_v2 (entity_type, entity_id, action, new_value, actor, message)
        VALUES ('document', ?, 'published', 'published', ?, ?)
      `).run(doc.id, agentId || "agent", `Document published: "${title}"`);

      broadcast("library:published", doc);
      break;
    }

    case "library:update": {
      // Agent updates an existing document
      if (!data?.doc_id) break;
      const existing = db.prepare("SELECT * FROM documents WHERE id = ?").get(data.doc_id);
      if (!existing) break;

      const newContent = data.content || existing.content;
      const newVersion = existing.version + 1;

      db.prepare(`
        UPDATE documents SET content = ?, excerpt = ?, word_count = ?,
          version = ?, updated_at = datetime('now')
        WHERE id = ?
      `).run(
        newContent,
        newContent.replace(/[#*_`>\[\]()!]/g, "").replace(/\n+/g, " ").trim().slice(0, 200),
        newContent.split(/\s+/).filter(Boolean).length,
        newVersion, data.doc_id
      );

      db.prepare(`
        INSERT INTO document_versions (doc_id, version, content, change_note, changed_by)
        VALUES (?, ?, ?, ?, ?)
      `).run(data.doc_id, newVersion, newContent, data.change_note || "", agentId || "agent");

      broadcast("library:updated", { id: data.doc_id, version: newVersion });
      break;
    }

    default:
      // Unknown events get logged but still accepted
      db.prepare(`
        INSERT INTO activity_log (entity_type, entity_id, action, new_value, actor, message)
        VALUES ('system', ?, ?, ?, ?, ?)
      `).run(
        agentId || "unknown", event, JSON.stringify(data || {}),
        agentId || "system", `Hook event: ${event}`
      );
  }

  res.json({ ok: true, event });
});

wrapRouter(router);
export default router;
