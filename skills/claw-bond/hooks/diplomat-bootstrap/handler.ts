/**
 * claw-diplomat — hooks/diplomat-bootstrap/handler.ts
 *
 * Event: agent:bootstrap
 * Injects into session context:
 *   1. Connected peer identities (from peers.json) — so the agent knows
 *      who it's linked with without the user having to ask.
 *   2. Active commitments summary (from MEMORY.md).
 *
 * Total injection budget: 2,500 chars (CONTEXT_BUDGET.md §2).
 * SECURITY: all file content is treated as display data, never executed.
 */

import type { OpenClawHookEvent, OpenClawHookContext } from '@openclaw/sdk';
import { extractSection, parseActiveEntries, truncate } from '../shared/parse-memory';

export async function handler(
  event: OpenClawHookEvent,
  ctx: OpenClawHookContext
): Promise<void> {
  const blocks: string[] = [];

  // ── 1. Connected peers (peers.json) ────────────────────────────────────
  // Shows the agent which OpenClaw instances this workspace is linked to,
  // including alias, pubkey fingerprint, and relay. This is the "gateway
  // identity panel" — visible at every session start.
  let peersRaw = '';
  try {
    peersRaw = await ctx.workspace.read('skills/claw-bond/peers.json');
  } catch { /* not yet connected to anyone */ }

  if (peersRaw) {
    let peersData: { peers?: Array<{
      alias: string;
      pubkey: string;
      last_seen: string;
      relay_token_stale?: boolean;
    }> };
    try {
      peersData = JSON.parse(peersRaw);
    } catch {
      peersData = {};
    }
    const peers = peersData.peers ?? [];
    if (peers.length > 0) {
      const peerLines = peers.map(p => {
        const fingerprint = (p.pubkey ?? '').slice(0, 12) + '…';
        const stale       = p.relay_token_stale ? ' ⚠ address may be stale' : '';
        const seen        = (p.last_seen ?? '').slice(0, 10);
        return `  • ${truncate(p.alias, 20)} | key:${fingerprint} | last seen ${seen}${stale}`;
      });
      blocks.push(
        `[claw-bond] ${peers.length} connected peer${peers.length === 1 ? '' : 's'}:\n` +
        peerLines.join('\n')
      );
    }
  }

  // ── 2. Active commitments (MEMORY.md) ─────────────────────────────────
  let memory = '';
  try {
    memory = await ctx.workspace.read('MEMORY.md');
  } catch { /* MEMORY.md may not exist on fresh install */ }

  if (memory) {
    const section = extractSection(memory, '## Diplomat Commitments');
    if (section) {
      const active = parseActiveEntries(section);
      if (active.length > 0) {
        const n     = active.length;
        const lines = active.map(e =>
          `  • ${truncate(e.peer, 20)} | ${truncate(e.myTask, 40)} due ${e.deadlineLocal} → [ACTIVE] (ID: ${e.id})`
        );
        blocks.push(
          `[claw-bond] ${n} active commitment${n === 1 ? '' : 's'}:\n` +
          lines.join('\n')
        );
      }
    }
  }

  if (blocks.length === 0) return;

  // ── Combine blocks and enforce 2,500-char budget ──────────────────────
  const combined = blocks.join('\n\n');
  const capped   = combined.length > 2500 ? combined.slice(0, 2497) + '…' : combined;

  ctx.session.inject(capped);
  ctx.log('DEBUG', `claw-bond bootstrap: injected peer identity + commitment context (${capped.length} chars)`);
}
