#!/usr/bin/env node

/**
 * Mission Control Hook for OpenClaw
 *
 * Install:
 *   cp mission-control-hook.ts ~/.openclaw/hooks/
 *   openclaw hooks enable mission-control
 *
 * Or add to openclaw.json:
 *   {
 *     "hooks": {
 *       "internal": {
 *         "enabled": true,
 *         "entries": {
 *           "mission-control": {
 *             "enabled": true,
 *             "env": {
 *               "MISSION_CONTROL_URL": "http://localhost:8000",
 *               "MISSION_CONTROL_HOOK_SECRET": "change-me-to-something-random"
 *             }
 *           }
 *         }
 *       }
 *     }
 *   }
 *
 * This hook intercepts OpenClaw lifecycle events and POSTs them to the
 * Mission Control backend. This is how the database stays in sync with
 * agent activity WITHOUT relying on session continuity.
 */

const MC_URL = process.env.MISSION_CONTROL_URL || "http://localhost:8000";
const HOOK_SECRET = process.env.MISSION_CONTROL_HOOK_SECRET || "";

async function postEvent(event, agentId, taskId, data) {
  try {
    const res = await fetch(`${MC_URL}/api/hooks/event`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Hook-Secret": HOOK_SECRET,
      },
      body: JSON.stringify({
        event,
        agentId,
        taskId,
        data,
        timestamp: new Date().toISOString(),
      }),
    });
    if (!res.ok) {
      console.error(`[mission-control-hook] POST failed: ${res.status}`);
    }
  } catch (err) {
    console.error(`[mission-control-hook] Error: ${err.message}`);
  }
}

// ─── Hook Exports ─────────────────────────────────────
// These match OpenClaw's hook lifecycle events.

export async function onSessionCreated({ agentId, sessionKey }) {
  await postEvent("session:created", agentId, null, { sessionKey });
}

export async function onSessionEnded({ agentId, sessionKey }) {
  await postEvent("session:ended", agentId, null, { sessionKey });
}

export async function onAgentIdle({ agentId }) {
  await postEvent("agent:idle", agentId, null, {});
}

export async function onAgentError({ agentId, error }) {
  await postEvent("agent:error", agentId, null, { error: error?.message || String(error) });
}

export async function onToolCall({ agentId, tool, args }) {
  // If the agent is calling a tool related to task management,
  // extract task context and report progress
  if (tool === "exec" || tool === "write" || tool === "edit") {
    // Check if there's a task ID in the current session context
    const taskId = args?.metadata?.taskId || null;
    if (taskId) {
      await postEvent("task:progress", agentId, taskId, {
        tool,
        message: `Agent using ${tool} tool`,
      });
    }
  }
}

export async function onHeartbeat({ agentId }) {
  await postEvent("agent:idle", agentId, null, { source: "heartbeat" });
}

// ─── Custom Commands ──────────────────────────────────
// Agents can send explicit task lifecycle updates via commands:
//
//   /mc task:started <taskId>
//   /mc task:completed <taskId>
//   /mc task:failed <taskId> <error message>
//   /mc task:review <taskId>

export async function onCommand({ agentId, command, args }) {
  if (!command.startsWith("/mc ")) return;

  const parts = command.slice(4).trim().split(/\s+/);
  const event = parts[0];
  const taskId = parts[1];
  const rest = parts.slice(2).join(" ");

  if (event && taskId) {
    await postEvent(event, agentId, taskId, {
      message: rest || undefined,
      error: event === "task:failed" ? (rest || "Task failed") : undefined,
    });
  }
}
