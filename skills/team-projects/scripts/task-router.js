#!/usr/bin/env node
/**
 * Team Projects — Task Router
 *
 * Parses @-mentions from team chat messages and dispatches tasks
 * to the appropriate agent via sessions_spawn or sessions_send.
 *
 * Called by the coordinator agent or gateway hook.
 */

import { readFileSync, existsSync } from "node:fs";
import path from "node:path";

const DATA_DIR = process.env.TEAM_PROJECTS_DIR ||
  path.join(process.env.HOME || "/root", ".openclaw", "workspace", "team-projects");

// ── @-Mention Parsing ───────────────────────────────────────────────────

/**
 * Extract @mentions from a message.
 * Supports: @agentId, @agent-id, @agent_id
 * Returns: [{ agentId, start, end }]
 */
export function parseMentions(text) {
  const mentions = [];
  const re = /@([a-zA-Z][a-zA-Z0-9_-]{0,63})\b/g;
  let match;
  while ((match = re.exec(text)) !== null) {
    mentions.push({
      agentId: match[1].toLowerCase(),
      raw: match[0],
      start: match.index,
      end: match.index + match[0].length,
    });
  }
  return mentions;
}

/**
 * Extract task references from a message.
 * Supports: #task_abc123, #phase_abc123
 */
export function parseTaskRefs(text) {
  const refs = [];
  const re = /#(task_[a-f0-9]+|phase_[a-f0-9]+)/g;
  let match;
  while ((match = re.exec(text)) !== null) {
    refs.push({ ref: match[1], start: match.index, end: match.index + match[0].length });
  }
  return refs;
}

/**
 * Build a dispatch plan from a message.
 * Returns which agents to notify and with what context.
 */
export function buildDispatchPlan(message, { projectId, author, availableAgents }) {
  const mentions = parseMentions(message);
  const taskRefs = parseTaskRefs(message);

  // Deduplicate mentioned agents
  const mentionedAgents = [...new Set(mentions.map(m => m.agentId))];

  // Filter to only agents that exist
  const validAgents = mentionedAgents.filter(a =>
    availableAgents.includes(a) || a === "all" || a === "team"
  );

  // @all or @team means broadcast to all agents
  const isBroadcast = validAgents.includes("all") || validAgents.includes("team");
  const targetAgents = isBroadcast
    ? availableAgents.filter(a => a !== author)
    : validAgents.filter(a => a !== author);

  // Strip mentions from the message body for clean forwarding
  let cleanMessage = message;
  for (const m of mentions) {
    cleanMessage = cleanMessage.replace(m.raw, "").trim();
  }

  return {
    original: message,
    cleanMessage,
    author,
    projectId,
    mentions,
    taskRefs,
    targetAgents,
    isBroadcast,
    dispatchType: targetAgents.length === 0
      ? "no_target"
      : targetAgents.length === 1
        ? "direct"
        : "multi",
  };
}

/**
 * Build the system prompt context for a dispatched message.
 * Gives the receiving agent context about the project and their role.
 */
export function buildAgentContext({ projectId, taskId, agentId, allAgents }) {
  let ctx = `## Team Project Context\n`;
  ctx += `You are agent "${agentId}" working on project "${projectId}".\n`;
  ctx += `Available team members: ${allAgents.join(", ")}\n`;
  ctx += `To communicate with other agents, use @agentId in your response.\n`;
  ctx += `To reference tasks, use #taskId.\n`;

  if (taskId) {
    // Load task details
    try {
      const dbPath = path.join(DATA_DIR, "projects.json");
      if (existsSync(dbPath)) {
        const db = JSON.parse(readFileSync(dbPath, "utf-8"));
        const project = db.projects.find(p => p.id === projectId || p.slug === projectId);
        if (project) {
          for (const phase of (project.phases || [])) {
            const task = (phase.tasks || []).find(t => t.id === taskId);
            if (task) {
              ctx += `\n### Current Task: ${task.title}\n`;
              ctx += `- **ID:** ${task.id}\n`;
              ctx += `- **Phase:** ${phase.name}\n`;
              ctx += `- **Priority:** ${task.priority}\n`;
              ctx += `- **Status:** ${task.status}\n`;
              if (task.description) ctx += `- **Description:** ${task.description}\n`;
              if (task.dependsOn?.length) ctx += `- **Depends on:** ${task.dependsOn.join(", ")}\n`;
              break;
            }
          }
        }
      }
    } catch { /* ignore read errors */ }
  }

  return ctx;
}

/**
 * Format a task assignment message for an agent.
 */
export function formatTaskAssignment({ task, phase, project, fromAgent }) {
  let msg = `📋 **Task Assignment from @${fromAgent}**\n\n`;
  msg += `**Project:** ${project.name}\n`;
  msg += `**Phase:** ${phase.name}\n`;
  msg += `**Task:** ${task.title} (#${task.id})\n`;
  msg += `**Priority:** ${task.priority}\n`;
  if (task.description) msg += `\n${task.description}\n`;
  if (task.dependsOn?.length) {
    msg += `\n**Dependencies:** ${task.dependsOn.map(d => `#${d}`).join(", ")}\n`;
  }
  msg += `\nWhen you complete this task, update its status by including in your response:\n`;
  msg += `\`TASK_COMPLETE: #${task.id}\`\n`;
  msg += `\nIf you need help from another agent, tag them: \`@agentId your request\`\n`;
  return msg;
}

// ── CLI Entry Point ─────────────────────────────────────────────────────

const [,, command, ...args] = process.argv;

if (command === "parse") {
  const text = args.join(" ");
  const mentions = parseMentions(text);
  const taskRefs = parseTaskRefs(text);
  console.log(JSON.stringify({ mentions, taskRefs }, null, 2));
}

if (command === "plan") {
  const text = args.join(" ");
  const plan = buildDispatchPlan(text, {
    projectId: process.env.PROJECT_ID || "unknown",
    author: process.env.AUTHOR || "main",
    availableAgents: (process.env.AGENTS || "main").split(","),
  });
  console.log(JSON.stringify(plan, null, 2));
}
