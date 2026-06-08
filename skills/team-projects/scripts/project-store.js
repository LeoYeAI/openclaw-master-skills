#!/usr/bin/env node
/**
 * Team Projects — Project Store
 *
 * JSON-file-backed CRUD for projects, phases, tasks, and comments.
 * Designed to be called from Gateway RPC handlers or CLI.
 *
 * Storage: ~/.openclaw/workspace/team-projects/projects.json
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync, appendFileSync } from "node:fs";
import { randomUUID } from "node:crypto";
import path from "node:path";

const DATA_DIR = process.env.TEAM_PROJECTS_DIR ||
  path.join(process.env.HOME || "/root", ".openclaw", "workspace", "team-projects");
const DB_PATH = path.join(DATA_DIR, "projects.json");

// ── Helpers ─────────────────────────────────────────────────────────────

function ensureDir() {
  if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });
}

function loadDB() {
  ensureDir();
  if (!existsSync(DB_PATH)) return { projects: [], version: 1 };
  try {
    return JSON.parse(readFileSync(DB_PATH, "utf-8"));
  } catch {
    return { projects: [], version: 1 };
  }
}

function saveDB(db) {
  ensureDir();
  writeFileSync(DB_PATH, JSON.stringify(db, null, 2), "utf-8");
}

function now() {
  return new Date().toISOString();
}

function slug(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 48);
}

// ── Project CRUD ────────────────────────────────────────────────────────

export function createProject({ name, description, coordinator, agents }) {
  const db = loadDB();
  const project = {
    id: `proj_${randomUUID().slice(0, 8)}`,
    slug: slug(name),
    name,
    description: description || "",
    coordinator: coordinator || "main",
    agents: agents || [],
    status: "planning",  // planning | active | paused | completed | archived
    phases: [],
    createdAt: now(),
    updatedAt: now(),
  };
  db.projects.push(project);
  saveDB(db);
  return project;
}

export function listProjects({ status, agentId } = {}) {
  const db = loadDB();
  let projects = db.projects;
  if (status) projects = projects.filter(p => p.status === status);
  if (agentId) projects = projects.filter(p =>
    p.coordinator === agentId ||
    p.agents.includes(agentId) ||
    p.phases?.some(ph => ph.tasks?.some(t => t.assignee === agentId))
  );
  return projects.map(p => ({
    ...p,
    taskCount: (p.phases || []).reduce((sum, ph) => sum + (ph.tasks || []).length, 0),
    completedCount: (p.phases || []).reduce((sum, ph) =>
      sum + (ph.tasks || []).filter(t => t.status === "done").length, 0),
  }));
}

export function getProject(projectId) {
  const db = loadDB();
  return db.projects.find(p => p.id === projectId || p.slug === projectId) || null;
}

export function updateProject(projectId, updates) {
  const db = loadDB();
  const idx = db.projects.findIndex(p => p.id === projectId || p.slug === projectId);
  if (idx === -1) return null;
  const allowed = ["name", "description", "status", "coordinator", "agents"];
  for (const key of allowed) {
    if (updates[key] !== undefined) db.projects[idx][key] = updates[key];
  }
  db.projects[idx].updatedAt = now();
  saveDB(db);
  return db.projects[idx];
}

export function deleteProject(projectId) {
  const db = loadDB();
  const idx = db.projects.findIndex(p => p.id === projectId || p.slug === projectId);
  if (idx === -1) return false;
  db.projects.splice(idx, 1);
  saveDB(db);
  return true;
}

// ── Phase CRUD ──────────────────────────────────────────────────────────

export function addPhase(projectId, { name, description, order }) {
  const db = loadDB();
  const project = db.projects.find(p => p.id === projectId || p.slug === projectId);
  if (!project) return null;
  if (!project.phases) project.phases = [];
  const phase = {
    id: `phase_${randomUUID().slice(0, 8)}`,
    name,
    description: description || "",
    order: order ?? project.phases.length,
    status: "pending",  // pending | active | completed
    tasks: [],
    createdAt: now(),
  };
  project.phases.push(phase);
  project.phases.sort((a, b) => a.order - b.order);
  project.updatedAt = now();
  saveDB(db);
  return phase;
}

export function updatePhase(projectId, phaseId, updates) {
  const db = loadDB();
  const project = db.projects.find(p => p.id === projectId || p.slug === projectId);
  if (!project) return null;
  const phase = (project.phases || []).find(ph => ph.id === phaseId);
  if (!phase) return null;
  const allowed = ["name", "description", "status", "order"];
  for (const key of allowed) {
    if (updates[key] !== undefined) phase[key] = updates[key];
  }
  project.updatedAt = now();
  saveDB(db);
  return phase;
}

export function deletePhase(projectId, phaseId) {
  const db = loadDB();
  const project = db.projects.find(p => p.id === projectId || p.slug === projectId);
  if (!project) return false;
  const idx = (project.phases || []).findIndex(ph => ph.id === phaseId);
  if (idx === -1) return false;
  project.phases.splice(idx, 1);
  project.updatedAt = now();
  saveDB(db);
  return true;
}

// ── Task CRUD ───────────────────────────────────────────────────────────

export function addTask(projectId, phaseId, { title, description, assignee, priority, tags, dependsOn }) {
  const db = loadDB();
  const project = db.projects.find(p => p.id === projectId || p.slug === projectId);
  if (!project) return null;
  const phase = (project.phases || []).find(ph => ph.id === phaseId);
  if (!phase) return null;
  if (!phase.tasks) phase.tasks = [];
  const task = {
    id: `task_${randomUUID().slice(0, 8)}`,
    title,
    description: description || "",
    assignee: assignee || null,
    priority: priority || "medium",  // critical | high | medium | low
    status: "todo",  // todo | in_progress | blocked | review | done
    tags: tags || [],
    dependsOn: Array.isArray(dependsOn) ? dependsOn : (dependsOn ? [dependsOn] : []),
    sessionKey: null,     // filled when agent picks up the task
    comments: [],
    artifacts: [],        // file paths, URLs, etc.
    createdAt: now(),
    updatedAt: now(),
    startedAt: null,
    completedAt: null,
  };
  phase.tasks.push(task);
  project.updatedAt = now();
  saveDB(db);
  return task;
}

export function updateTask(projectId, taskId, updates) {
  const db = loadDB();
  const project = db.projects.find(p => p.id === projectId || p.slug === projectId);
  if (!project) return null;
  for (const phase of (project.phases || [])) {
    const task = (phase.tasks || []).find(t => t.id === taskId);
    if (!task) continue;
    const allowed = [
      "title", "description", "assignee", "priority", "status",
      "tags", "dependsOn", "sessionKey", "artifacts",
    ];
    for (const key of allowed) {
      if (updates[key] !== undefined) task[key] = updates[key];
    }
    if (updates.status === "in_progress" && !task.startedAt) {
      task.startedAt = now();
    }
    if (updates.status === "done" && !task.completedAt) {
      task.completedAt = now();
    }
    task.updatedAt = now();
    project.updatedAt = now();
    saveDB(db);
    return task;
  }
  return null;
}

export function getTask(projectId, taskId) {
  const project = getProject(projectId);
  if (!project) return null;
  for (const phase of (project.phases || [])) {
    const task = (phase.tasks || []).find(t => t.id === taskId);
    if (task) return { ...task, phaseId: phase.id, phaseName: phase.name };
  }
  return null;
}

export function listTasks(projectId, { assignee, status, phaseId, priority } = {}) {
  const project = getProject(projectId);
  if (!project) return [];
  const tasks = [];
  for (const phase of (project.phases || [])) {
    if (phaseId && phase.id !== phaseId) continue;
    for (const task of (phase.tasks || [])) {
      if (assignee && task.assignee !== assignee) continue;
      if (status && task.status !== status) continue;
      if (priority && task.priority !== priority) continue;
      tasks.push({ ...task, phaseId: phase.id, phaseName: phase.name });
    }
  }
  return tasks;
}

export function deleteTask(projectId, taskId) {
  const db = loadDB();
  const project = db.projects.find(p => p.id === projectId || p.slug === projectId);
  if (!project) return false;
  for (const phase of (project.phases || [])) {
    const idx = (phase.tasks || []).findIndex(t => t.id === taskId);
    if (idx === -1) continue;
    phase.tasks.splice(idx, 1);
    project.updatedAt = now();
    saveDB(db);
    return true;
  }
  return false;
}

// ── Task Comments ───────────────────────────────────────────────────────

export function addComment(projectId, taskId, { author, text }) {
  const db = loadDB();
  const project = db.projects.find(p => p.id === projectId || p.slug === projectId);
  if (!project) return null;
  for (const phase of (project.phases || [])) {
    const task = (phase.tasks || []).find(t => t.id === taskId);
    if (!task) continue;
    if (!task.comments) task.comments = [];
    const comment = {
      id: `cmt_${randomUUID().slice(0, 8)}`,
      author,
      text,
      createdAt: now(),
    };
    task.comments.push(comment);
    task.updatedAt = now();
    project.updatedAt = now();
    saveDB(db);
    return comment;
  }
  return null;
}

// ── Team Chat Log ───────────────────────────────────────────────────────

export function appendChatMessage(projectId, { author, text, mentions, taskRef }) {
  const chatPath = path.join(DATA_DIR, `chat_${projectId}.jsonl`);
  ensureDir();
  const entry = {
    id: `msg_${randomUUID().slice(0, 8)}`,
    author,
    text,
    mentions: mentions || [],
    taskRef: taskRef || null,
    timestamp: now(),
  };
  const line = JSON.stringify(entry) + "\n";
  appendFileSync(chatPath, line, "utf-8");
  return entry;
}

export function getChatHistory(projectId, { limit, before } = {}) {
  const chatPath = path.join(DATA_DIR, `chat_${projectId}.jsonl`);
  if (!existsSync(chatPath)) return [];
  const lines = readFileSync(chatPath, "utf-8").trim().split("\n").filter(Boolean);
  let messages = lines.map(l => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean);
  if (before) messages = messages.filter(m => m.timestamp < before);
  if (limit) messages = messages.slice(-limit);
  return messages;
}

// ── Project Summary / Stats ─────────────────────────────────────────────

export function getProjectStats(projectId) {
  const project = getProject(projectId);
  if (!project) return null;
  const allTasks = [];
  for (const phase of (project.phases || [])) {
    for (const task of (phase.tasks || [])) {
      allTasks.push(task);
    }
  }
  const byStatus = {};
  const byAssignee = {};
  const byPriority = {};
  for (const t of allTasks) {
    byStatus[t.status] = (byStatus[t.status] || 0) + 1;
    if (t.assignee) byAssignee[t.assignee] = (byAssignee[t.assignee] || 0) + 1;
    byPriority[t.priority] = (byPriority[t.priority] || 0) + 1;
  }
  const total = allTasks.length;
  const done = byStatus.done || 0;
  return {
    projectId: project.id,
    name: project.name,
    status: project.status,
    phases: (project.phases || []).length,
    totalTasks: total,
    completedTasks: done,
    progress: total > 0 ? Math.round((done / total) * 100) : 0,
    byStatus,
    byAssignee,
    byPriority,
  };
}

// ── WBS (Work Breakdown Structure) ──────────────────────────────────────

export function getWBS(projectId) {
  const project = getProject(projectId);
  if (!project) return null;
  return {
    project: { id: project.id, name: project.name, status: project.status },
    phases: (project.phases || []).map(ph => ({
      id: ph.id,
      name: ph.name,
      status: ph.status,
      order: ph.order,
      tasks: (ph.tasks || []).map(t => ({
        id: t.id,
        title: t.title,
        assignee: t.assignee,
        status: t.status,
        priority: t.priority,
        dependsOn: t.dependsOn,
      })),
    })),
  };
}

// ── CLI Entry Point ─────────────────────────────────────────────────────

const [,, command, ...args] = process.argv;

function parseArgs(args) {
  const result = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i].startsWith("--")) {
      const key = args[i].slice(2);
      const val = args[i + 1] && !args[i + 1].startsWith("--") ? args[++i] : true;
      // Handle arrays (comma-separated)
      if (typeof val === "string" && val.includes(",")) {
        result[key] = val.split(",").map(s => s.trim());
      } else {
        result[key] = val;
      }
    }
  }
  return result;
}

if (command) {
  const opts = parseArgs(args);
  let result;
  switch (command) {
    case "create-project":
      result = createProject(opts);
      break;
    case "list-projects":
      result = listProjects(opts);
      break;
    case "get-project":
      result = getProject(opts.id);
      break;
    case "update-project":
      result = updateProject(opts.id, opts);
      break;
    case "delete-project":
      result = deleteProject(opts.id);
      break;
    case "add-phase":
      result = addPhase(opts.project, opts);
      break;
    case "update-phase":
      result = updatePhase(opts.project, opts.id, opts);
      break;
    case "add-task":
      result = addTask(opts.project, opts.phase, opts);
      break;
    case "update-task":
      result = updateTask(opts.project, opts.id, opts);
      break;
    case "get-task":
      result = getTask(opts.project, opts.id);
      break;
    case "list-tasks":
      result = listTasks(opts.project, opts);
      break;
    case "add-comment":
      result = addComment(opts.project, opts.task, opts);
      break;
    case "stats":
      result = getProjectStats(opts.id || opts.project);
      break;
    case "wbs":
      result = getWBS(opts.id || opts.project);
      break;
    default:
      console.error(`Unknown command: ${command}`);
      process.exit(1);
  }
  console.log(JSON.stringify(result, null, 2));
}
