#!/usr/bin/env node
/**
 * Team Projects — Gateway RPC Handlers
 *
 * These handlers are registered as gateway RPC methods that the
 * Control UI calls to manage projects, tasks, and team chat.
 *
 * Since OpenClaw doesn't have a native plugin RPC system yet,
 * these are called via the agent as tool calls — the agent
 * reads project state and responds to UI requests.
 *
 * For now, this serves as a reference for what RPC methods
 * would be needed if/when gateway plugin RPC is added.
 *
 * In practice, the coordinator agent uses the project-store.js
 * CLI directly, and the UI communicates via chat messages.
 */

/**
 * RPC Method Specification
 *
 * These would be registered as gateway methods:
 *
 * projects.list          → listProjects({ status?, agentId? })
 * projects.create        → createProject({ name, description, coordinator, agents })
 * projects.get           → getProject({ id })
 * projects.update        → updateProject({ id, ...fields })
 * projects.delete        → deleteProject({ id })
 *
 * projects.phases.add    → addPhase({ projectId, name, description, order })
 * projects.phases.update → updatePhase({ projectId, phaseId, ...fields })
 * projects.phases.delete → deletePhase({ projectId, phaseId })
 *
 * projects.tasks.add     → addTask({ projectId, phaseId, title, description, assignee, priority })
 * projects.tasks.update  → updateTask({ projectId, taskId, ...fields })
 * projects.tasks.get     → getTask({ projectId, taskId })
 * projects.tasks.list    → listTasks({ projectId, assignee?, status?, phaseId? })
 * projects.tasks.delete  → deleteTask({ projectId, taskId })
 *
 * projects.comments.add  → addComment({ projectId, taskId, author, text })
 *
 * projects.chat.send     → appendChatMessage({ projectId, author, text, mentions })
 * projects.chat.history  → getChatHistory({ projectId, limit?, before? })
 *
 * projects.stats         → getProjectStats({ projectId })
 * projects.wbs           → getWBS({ projectId })
 *
 * projects.dispatch.plan → getDispatchPlan({ projectId })
 * projects.dispatch.ready → findReadyTasks({ projectId })
 * projects.dispatch.advance → advancePhases({ projectId })
 */

// ── Adapter: HTTP API (optional future enhancement) ─────────────────────

import http from "node:http";
import {
  createProject, listProjects, getProject, updateProject, deleteProject,
  addPhase, updatePhase, deletePhase,
  addTask, updateTask, getTask, listTasks, deleteTask,
  addComment,
  appendChatMessage, getChatHistory,
  getProjectStats, getWBS,
} from "./project-store.js";

import {
  findReadyTasks, getDispatchPlan, advancePhases,
} from "./orchestrator.js";

const PORT = parseInt(process.env.TEAM_PROJECTS_PORT || "0", 10);

if (PORT > 0) {
  const routes = {
    "POST /api/projects":        (body) => createProject(body),
    "GET /api/projects":         (body) => listProjects(body),
    "GET /api/projects/:id":     (body) => getProject(body.id),
    "PATCH /api/projects/:id":   (body) => updateProject(body.id, body),
    "DELETE /api/projects/:id":  (body) => deleteProject(body.id),
    "POST /api/phases":          (body) => addPhase(body.projectId, body),
    "POST /api/tasks":           (body) => addTask(body.projectId, body.phaseId, body),
    "PATCH /api/tasks/:id":      (body) => updateTask(body.projectId, body.id, body),
    "GET /api/tasks":            (body) => listTasks(body.projectId, body),
    "POST /api/comments":        (body) => addComment(body.projectId, body.taskId, body),
    "POST /api/chat":            (body) => appendChatMessage(body.projectId, body),
    "GET /api/chat":             (body) => getChatHistory(body.projectId, body),
    "GET /api/stats":            (body) => getProjectStats(body.projectId),
    "GET /api/wbs":              (body) => getWBS(body.projectId),
    "GET /api/dispatch/plan":    (body) => getDispatchPlan(body.projectId),
    "GET /api/dispatch/ready":   (body) => findReadyTasks(body.projectId),
    "POST /api/dispatch/advance": (body) => advancePhases(body.projectId),
  };

  const server = http.createServer(async (req, res) => {
    res.setHeader("Content-Type", "application/json");
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

    if (req.method === "OPTIONS") {
      res.writeHead(200);
      res.end();
      return;
    }

    try {
      let body = {};
      if (req.method !== "GET") {
        const chunks = [];
        for await (const chunk of req) chunks.push(chunk);
        const raw = Buffer.concat(chunks).toString("utf-8");
        if (raw) body = JSON.parse(raw);
      }

      // Parse URL params
      const url = new URL(req.url, `http://localhost:${PORT}`);
      for (const [k, v] of url.searchParams) body[k] = v;

      // Match route
      const routeKey = `${req.method} ${url.pathname}`;
      const handler = routes[routeKey];

      if (handler) {
        const result = await handler(body);
        res.writeHead(200);
        res.end(JSON.stringify({ ok: true, data: result }));
      } else {
        res.writeHead(404);
        res.end(JSON.stringify({ ok: false, error: "Not found" }));
      }
    } catch (err) {
      res.writeHead(500);
      res.end(JSON.stringify({ ok: false, error: err.message }));
    }
  });

  server.listen(PORT, "127.0.0.1", () => {
    console.log(`Team Projects API listening on http://127.0.0.1:${PORT}`);
  });
}
