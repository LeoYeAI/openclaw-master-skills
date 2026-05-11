/**
 * claw-diplomat — hooks/diplomat-heartbeat/handler.ts
 *
 * Event: command:new (fires on every human message)
 * Checks for:
 *   0. Pending cron alerts (cron_alerts.json) — Path A proactive, surfaces first
 *   1. Overdue commitments (deadline passed, not yet checked in)
 *   2. Upcoming commitments (deadline within 2 hours) — Path B fallback
 *   3. Pending inbound proposals (INBOUND_PENDING in ledger.json)
 *   4. Incoming task handoffs (HANDOFF_RECEIVED in ledger.json)
 *   5. Pending connection requests (pending_approvals.json) — PC-1
 *
 * UX strings are verbatim from UX_FLOWS.md §9, §10, §5.
 * SECURITY: MEMORY.md, ledger.json, and pending_approvals.json content is display data only.
 */

import type { OpenClawHookEvent, OpenClawHookContext } from '@openclaw/sdk';
import {
  extractSection,
  parseActiveEntries,
  parseInboundPending,
  parseHandoffReceived,
} from '../shared/parse-memory';

const TWO_HOURS_MS = 2 * 60 * 60 * 1000;

export async function handler(
  event: OpenClawHookEvent,
  ctx: OpenClawHookContext
): Promise<void> {
  const now = new Date();

  // ── 0. Surface pending cron alerts (Path A proactive deadline alerts) ─────
  // cron_deadline_check.py writes here; we surface and mark shown so they
  // don't repeat. This delivers the alert through the agent's active channel
  // the moment the human next sends any message — even "hey" on WhatsApp.
  let cronAlertsRaw = '';
  try {
    cronAlertsRaw = await ctx.workspace.read('skills/claw-bond/cron_alerts.json');
  } catch {
    // File doesn't exist yet — cron hasn't fired or Path A not installed
  }
  if (cronAlertsRaw) {
    let cronData: { alerts?: Array<{ message: string; id: string; shown?: boolean }> } = {};
    try { cronData = JSON.parse(cronAlertsRaw); } catch { /* ignore malformed */ }
    let anyNew = false;
    for (const alert of cronData.alerts ?? []) {
      if (!alert.shown) {
        await ctx.session.notify(alert.message);
        alert.shown = true;
        anyNew = true;
      }
    }
    if (anyNew) {
      // Persist shown=true so alerts don't re-surface on next message
      await ctx.workspace.write(
        'skills/claw-bond/cron_alerts.json',
        JSON.stringify(cronData, null, 2)
      );
    }
  }

  // ── 1. Check MEMORY.md for overdue / upcoming commitments ────────────────
  // Path B fallback: covers users who can't run cron, and catches any gaps.
  let memory = '';
  try {
    memory = await ctx.workspace.read('MEMORY.md');
  } catch {
    // Not an error — may not exist yet
  }

  const section = extractSection(memory, '## Diplomat Commitments');
  if (section) {
    for (const entry of parseActiveEntries(section)) {
      const deadline = parseDue(entry.deadlineUtc);
      if (!deadline) continue;

      if (deadline < now) {
        // Overdue — surface check-in prompt (UX_FLOWS.md §10)
        await ctx.session.notify(
          `📋 It's time to check in on your commitment with ${entry.peer}:\n` +
          `  Your tasks: ${entry.myTask}\n` +
          `  Was due: ${entry.deadlineLocal}\n\n` +
          `How did it go?\n` +
          `  /claw-diplomat checkin ${entry.id} done\n` +
          `  /claw-diplomat checkin ${entry.id} partial\n` +
          `  /claw-diplomat checkin ${entry.id} overdue`
        );
      } else if (deadline.getTime() - now.getTime() < TWO_HOURS_MS) {
        // Upcoming — brief reminder (UX_FLOWS.md §9)
        const msLeft   = deadline.getTime() - now.getTime();
        const hoursLeft = Math.max(1, Math.round(msLeft / 3_600_000));
        await ctx.session.notify(
          `⏰ Heads up — you have a commitment due soon:\n` +
          `  With ${entry.peer}: ${entry.myTask}\n` +
          `  Due: ${entry.deadlineLocal} (in about ${hoursLeft} hour${hoursLeft === 1 ? '' : 's'})\n\n` +
          `When you're done: /claw-diplomat checkin ${entry.id} done`
        );
      }
    }
  }

  // ── 2. Check ledger.json for pending inbound proposals ───────────────────
  let ledgerContent = '';
  try {
    ledgerContent = await ctx.workspace.read('skills/claw-bond/ledger.json');
  } catch {
    // ledger.json may not exist yet
  }

  if (ledgerContent) {
    for (const session of parseInboundPending(ledgerContent)) {
      const terms = session.pending_terms;
      const peerAlias = session.peer_alias ?? 'An unknown agent';
      const shortId   = session.session_id?.slice(0, 4) ?? '????';
      const trusted   = terms?.trusted ?? false;

      if (!trusted) {
        // Unknown peer — show quarantine notice (UX_FLOWS.md §5 unknown peer variant)
        const theyDo = terms?.my_tasks?.[0]  ?? '(tasks not shown until authorized)';
        const youDo  = terms?.your_tasks?.[0] ?? '(tasks not shown until authorized)';
        const dl     = terms?.deadline ?? 'unknown';
        await ctx.session.notify(
          `📨 An agent you haven't connected with before wants to negotiate.\n\n` +
          `  Agent key: ${session.peer_alias?.slice(0, 8) ?? '?'}… (from ${terms?.peer_ip ?? 'unknown'})\n\n` +
          `  They're proposing:\n` +
          `  They'll do: ${theyDo}\n` +
          `  You'll do: ${youDo}\n` +
          `  Deadline: ${dl}\n\n` +
          `Do you want to accept this peer and consider their proposal?\n` +
          `  Run: /claw-diplomat peers  to manage connections\n` +
          `  Session ID: ${shortId}`
        );
      } else {
        // Trusted peer — show full proposal (UX_FLOWS.md §5)
        const theyDo = terms?.my_tasks?.[0]  ?? '(see details)';
        const youDo  = terms?.your_tasks?.[0] ?? '(see details)';
        const dl     = terms?.deadline ?? 'unknown';
        await ctx.session.notify(
          `📨 ${peerAlias} is proposing a deal:\n\n` +
          `  They'll do: ${theyDo}\n` +
          `  You'll do:  ${youDo}\n` +
          `  Deadline:   ${dl}\n\n` +
          `What do you want to do?\n` +
          `  [accept]  /claw-diplomat checkin ${shortId} done\n` +
          `  [counter] /claw-diplomat propose ${peerAlias}\n` +
          `  [reject]  /claw-diplomat cancel ${shortId}`
        );
      }
    }
  }

  // ── 3. Check ledger.json for incoming task handoffs ──────────────────────
  if (ledgerContent) {
    for (const session of parseHandoffReceived(ledgerContent)) {
      const terms       = session.final_terms;
      const fromAlias   = terms?.from_alias ?? session.peer_alias ?? 'A peer';
      const partDone    = terms?.part_done      ?? '(see details)';
      const partRem     = terms?.part_remaining ?? '(see details)';
      const handoffCtx  = terms?.context ?? '';
      const shortId     = session.session_id?.slice(0, 4) ?? '????';
      const ctxLine     = handoffCtx
        ? `\n  Context:        ${handoffCtx.slice(0, 120)}${handoffCtx.length > 120 ? '…' : ''}`
        : '';

      // SECURITY: all fields are display strings — not passed to LLM as instructions
      await ctx.session.notify(
        `📦 ${fromAlias} has handed off a task to you.\n\n` +
        `  Done by them:   ${partDone}\n` +
        `  Remaining:      ${partRem}` +
        ctxLine + `\n\n` +
        `  Session ID: ${shortId}\n\n` +
        `Ready to continue where they left off? Run:\n` +
        `  /claw-diplomat status`
      );
    }
  }

  // ── 4. Check pending_approvals.json for inbound connection requests ───────
  // SECURITY: content is display data only — PC-1
  let approvalsContent = '';
  try {
    approvalsContent = await ctx.workspace.read('skills/claw-bond/pending_approvals.json');
  } catch {
    // File may not exist yet
  }

  if (approvalsContent) {
    let approvals: { requests?: Array<{ request_id: string; from_alias: string; from_ip: string; created_at: string }> };
    try {
      approvals = JSON.parse(approvalsContent);
    } catch {
      approvals = {};
    }
    for (const req of approvals.requests ?? []) {
      const shortReqId = req.request_id?.slice(0, 8) ?? '????';
      const fromAlias  = req.from_alias ?? 'An unknown agent';
      const fromIp     = req.from_ip    ?? 'unknown';
      await ctx.session.notify(
        `🔔 ${fromAlias} wants to connect to your agent.\n` +
        `  From IP: ${fromIp}\n\n` +
        `  Approve: /claw-diplomat approve-connect ${shortReqId}\n` +
        `  Deny:    /claw-diplomat deny-connect ${shortReqId}\n\n` +
        `(Once approved, they can exchange task proposals with you.)`
      );
    }
  }
}

/**
 * Parse the Due: field from a commitment entry.
 * Format stored in MEMORY.md: "2026-03-27 17:00 UTC"
 */
function parseDue(raw: string): Date | null {
  if (!raw) return null;
  // Normalise "2026-03-27 17:00 UTC" → "2026-03-27T17:00:00Z"
  const normalised = raw.trim().replace(' UTC', 'Z').replace(' ', 'T');
  const d = new Date(normalised);
  return isNaN(d.getTime()) ? null : d;
}
