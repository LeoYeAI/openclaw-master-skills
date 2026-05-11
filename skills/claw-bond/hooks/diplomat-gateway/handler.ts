/**
 * claw-diplomat — hooks/diplomat-gateway/handler.ts
 *
 * Event: gateway:startup
 *
 * Checks whether the inbound relay listener is already running (via PID file).
 * If it is running  → logs and returns silently.
 * If it is not running → writes a flag file and injects a one-line startup
 *   instruction into the agent session so the agent can start listener.py
 *   as a background process on the next /claw-diplomat command.
 *
 * The process launch itself is delegated to the agent (via SKILL.md instructions)
 * rather than being executed here. This keeps the hook layer free of shell
 * execution and uses only the declared workspace filesystem APIs.
 *
 * fail_open: true — if the listener isn't running the user gets a nudge;
 * this is not a hard failure that should block the gateway.
 */

import type { OpenClawHookEvent, OpenClawHookContext } from '@openclaw/sdk';
import * as path from 'path';
import * as fs from 'fs';

export async function handler(
  event: OpenClawHookEvent,
  ctx: OpenClawHookContext
): Promise<void> {
  const workspaceRoot = process.env.DIPLOMAT_WORKSPACE ?? process.cwd();
  const skillDir      = path.join(workspaceRoot, 'skills', 'claw-bond');
  const listenerPath  = path.join(skillDir, 'listener.py');
  const pidPath       = path.join(skillDir, 'listener.pid');
  const flagPath      = path.join(skillDir, 'listener.start_requested');

  // ── Verify the skill is installed ──────────────────────────────────────
  if (!fs.existsSync(listenerPath)) {
    ctx.session.notify(
      '⚠️ claw-bond: listener.py not found — skill may not be installed correctly.\n' +
      'Run: clawhub install claw-bond'
    );
    return;
  }

  // ── Check if listener is already running via PID file ──────────────────
  if (fs.existsSync(pidPath)) {
    const rawPid      = fs.readFileSync(pidPath, 'utf-8').trim();
    const existingPid = parseInt(rawPid, 10);
    if (!isNaN(existingPid)) {
      try {
        // Signal 0 = existence check only — does NOT kill or interact with the process.
        process.kill(existingPid, 0);
        ctx.log('INFO', `claw-bond listener is running (PID ${existingPid})`);
        return; // Already running — nothing to do
      } catch {
        // Process is gone — PID file is stale; clean it up and fall through
        ctx.log('DEBUG', `claw-bond stale PID ${existingPid} — will request restart`);
        try { fs.unlinkSync(pidPath); } catch { /* ignore */ }
      }
    }
  }

  // ── Listener is not running ─────────────────────────────────────────────
  // Write a flag file so the agent (and any tooling) can detect this state.
  // The agent reads SKILL.md which instructs it to run listener.py in the
  // background when it sees this flag or the next /claw-diplomat command.
  try {
    fs.writeFileSync(flagPath, new Date().toISOString(), 'utf-8');
  } catch {
    // Non-fatal — the inject below still provides the nudge
  }

  ctx.session.inject(
    '[claw-bond] Listener not running — inbound proposals will not be received.\n' +
    'To start it, run in terminal:\n' +
    `  python3 "${listenerPath}" &\n` +
    'Or tell your agent: "start the claw-bond listener"'
  );

  ctx.log('INFO', 'claw-bond: listener not running — agent notified to start listener.py');
}
