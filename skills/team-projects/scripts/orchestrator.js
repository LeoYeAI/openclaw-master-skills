#!/usr/bin/env node
/**
 * Team Projects — Orchestrator
 *
 * The coordinator agent logic that:
 * 1. Reads the project plan
 * 2. Identifies next actionable tasks
 * 3. Dispatches them to appropriate agents via sessions_spawn
 * 4. Tracks completions and advances the project
 *
 * This is designed to be called as a tool by the coordinator agent,
 * or triggered via cron for autonomous project advancement.
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from "node:fs";
import path from "node:path";

const DATA_DIR = process.env.TEAM_PROJECTS_DIR ||
  path.join(process.env.HOME || "/root", ".openclaw", "workspace", "team-projects");
const DB_PATH = path.join(DATA_DIR, "projects.json");
const STATE_PATH = path.join(DATA_DIR, "orchestrator-state.json");

// ── State Management ────────────────────────────────────────────────────

function loadState() {
  if (!existsSync(STATE_PATH)) return { dispatched: {}, completions: [] };
  try {
    return JSON.parse(readFileSync(STATE_PATH, "utf-8"));
  } catch {
    return { dispatched: {}, completions: [] };
  }
}

function saveState(state) {
  if (!existsSync(DATA_DIR)) mkdirSync(DATA_DIR, { recursive: true });
  writeFileSync(STATE_PATH, JSON.stringify(state, null, 2), "utf-8");
}

function loadDB() {
  if (!existsSync(DB_PATH)) return { projects: [] };
  try {
    return JSON.parse(readFileSync(DB_PATH, "utf-8"));
  } catch {
    return { projects: [] };
  }
}

// ── Task Readiness Analysis ─────────────────────────────────────────────

/**
 * Determine which tasks are ready to be dispatched.
 * A task is ready when:
 * - status is "todo"
 * - all dependencies are "done"
 * - it has an assignee
 * - it hasn't already been dispatched (in current cycle)
 */
export function findReadyTasks(projectId) {
  const db = loadDB();
  const project = db.projects.find(p => p.id === projectId || p.slug === projectId);
  if (!project) return [];

  const state = loadState();

  // Build a set of completed task IDs
  const completedIds = new Set();
  for (const phase of (project.phases || [])) {
    for (const task of (phase.tasks || [])) {
      if (task.status === "done") completedIds.add(task.id);
    }
  }

  const ready = [];
  for (const phase of (project.phases || [])) {
    if (phase.status === "completed") continue;
    for (const task of (phase.tasks || [])) {
      if (task.status !== "todo") continue;
      if (!task.assignee) continue;

      // Check if already dispatched
      if (state.dispatched[task.id]) continue;

      // Check dependencies
      const deps = Array.isArray(task.dependsOn) ? task.dependsOn : (task.dependsOn ? [task.dependsOn] : []);
      const depsReady = deps.every(dep => completedIds.has(dep));
      if (!depsReady) continue;

      ready.push({
        taskId: task.id,
        title: task.title,
        description: task.description,
        assignee: task.assignee,
        priority: task.priority,
        phaseId: phase.id,
        phaseName: phase.name,
        dependsOn: task.dependsOn,
      });
    }
  }

  // Sort by priority: critical > high > medium > low
  const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
  ready.sort((a, b) => (priorityOrder[a.priority] || 99) - (priorityOrder[b.priority] || 99));

  return ready;
}

/**
 * Mark a task as dispatched (prevents double-dispatch).
 */
export function markDispatched(taskId, { sessionKey, agentId }) {
  const state = loadState();
  state.dispatched[taskId] = {
    sessionKey,
    agentId,
    dispatchedAt: new Date().toISOString(),
  };
  saveState(state);
}

/**
 * Record a task completion event.
 */
export function recordCompletion(taskId, { agentId, summary, artifacts }) {
  const state = loadState();
  delete state.dispatched[taskId];
  state.completions.push({
    taskId,
    agentId,
    summary,
    artifacts: artifacts || [],
    completedAt: new Date().toISOString(),
  });
  saveState(state);
}

/**
 * Get a dispatch plan for the coordinator agent.
 * Returns a structured plan that the agent can execute via sessions_spawn.
 */
export function getDispatchPlan(projectId) {
  const readyTasks = findReadyTasks(projectId);
  const db = loadDB();
  const project = db.projects.find(p => p.id === projectId || p.slug === projectId);

  if (!project) return { error: "Project not found" };

  // Group by assignee
  const byAgent = {};
  for (const task of readyTasks) {
    if (!byAgent[task.assignee]) byAgent[task.assignee] = [];
    byAgent[task.assignee].push(task);
  }

  // Build dispatch instructions
  const dispatches = [];
  for (const [agentId, tasks] of Object.entries(byAgent)) {
    for (const task of tasks) {
      dispatches.push({
        action: "sessions_spawn",
        agentId,
        task: buildTaskPrompt(task, project),
        taskId: task.id,
        priority: task.priority,
      });
    }
  }

  // Project progress
  let totalTasks = 0, doneTasks = 0;
  for (const phase of (project.phases || [])) {
    for (const task of (phase.tasks || [])) {
      totalTasks++;
      if (task.status === "done") doneTasks++;
    }
  }

  return {
    projectId: project.id,
    projectName: project.name,
    progress: totalTasks > 0 ? Math.round((doneTasks / totalTasks) * 100) : 0,
    totalTasks,
    completedTasks: doneTasks,
    readyToDispatch: dispatches.length,
    dispatches,
    blockedTasks: countBlockedTasks(project),
  };
}

function buildTaskPrompt(task, project) {
  let prompt = `# Task: ${task.title}\n\n`;
  prompt += `**Project:** ${project.name}\n`;
  prompt += `**Phase:** ${task.phaseName}\n`;
  prompt += `**Priority:** ${task.priority}\n`;
  prompt += `**Task ID:** ${task.taskId}\n\n`;
  if (task.description) prompt += `## Description\n\n${task.description}\n\n`;
  prompt += `## Instructions\n\n`;
  prompt += `Complete this task thoroughly. When finished:\n`;
  prompt += `1. Summarize what you did\n`;
  prompt += `2. List any artifacts (files created, URLs, etc.)\n`;
  prompt += `3. Note any issues or follow-up needed\n`;
  return prompt;
}

function countBlockedTasks(project) {
  const completedIds = new Set();
  let blocked = 0;
  for (const phase of (project.phases || [])) {
    for (const task of (phase.tasks || [])) {
      if (task.status === "done") completedIds.add(task.id);
    }
  }
  for (const phase of (project.phases || [])) {
    for (const task of (phase.tasks || [])) {
      if (task.status !== "todo") continue;
      const deps = Array.isArray(task.dependsOn) ? task.dependsOn : (task.dependsOn ? [task.dependsOn] : []);
      if (deps.length > 0 && !deps.every(d => completedIds.has(d))) {
        blocked++;
      }
    }
  }
  return blocked;
}

/**
 * Check if a project's current phase is complete and advance to next.
 */
export function advancePhases(projectId) {
  const db = loadDB();
  const project = db.projects.find(p => p.id === projectId || p.slug === projectId);
  if (!project) return null;

  const advanced = [];
  for (const phase of (project.phases || [])) {
    if (phase.status === "completed") continue;
    const tasks = phase.tasks || [];
    if (tasks.length === 0) continue;
    const allDone = tasks.every(t => t.status === "done");
    if (allDone) {
      phase.status = "completed";
      advanced.push(phase.id);
    } else if (tasks.some(t => t.status === "in_progress" || t.status === "review")) {
      if (phase.status !== "active") phase.status = "active";
    }
  }

  // Check if all phases are complete
  const allPhasesComplete = (project.phases || []).every(p => p.status === "completed");
  if (allPhasesComplete && project.status === "active") {
    project.status = "completed";
  }

  if (advanced.length > 0 || allPhasesComplete) {
    project.updatedAt = new Date().toISOString();
    const dbFull = loadDB();
    const idx = dbFull.projects.findIndex(p => p.id === project.id);
    if (idx !== -1) dbFull.projects[idx] = project;
    writeFileSync(DB_PATH, JSON.stringify(dbFull, null, 2), "utf-8");
  }

  return {
    advancedPhases: advanced,
    projectComplete: allPhasesComplete,
  };
}

// ── CLI Entry Point ─────────────────────────────────────────────────────

const [,, command, ...args] = process.argv;

if (command) {
  const projectId = args[0] || process.env.PROJECT_ID;
  let result;
  switch (command) {
    case "ready":
      result = findReadyTasks(projectId);
      break;
    case "plan":
      result = getDispatchPlan(projectId);
      break;
    case "advance":
      result = advancePhases(projectId);
      break;
    case "dispatched":
      result = loadState().dispatched;
      break;
    default:
      console.error(`Unknown command: ${command}`);
      process.exit(1);
  }
  console.log(JSON.stringify(result, null, 2));
}
