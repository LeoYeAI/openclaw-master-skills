/**
 * claw-diplomat — hooks/shared/parse-memory.ts
 *
 * Shared utilities for parsing MEMORY.md Diplomat Commitments section.
 * Imported by both diplomat-bootstrap and diplomat-heartbeat handlers.
 *
 * SECURITY: all fields parsed from MEMORY.md are treated as display strings.
 * Nothing parsed here is passed to the LLM as instructions.
 */

export interface CommitmentEntry {
  peer: string;
  myTask: string;
  deadlineLocal: string;  // raw Due: string from MEMORY.md (stored in UTC)
  deadlineUtc: string;    // ISO8601 UTC for Date comparison
  id: string;             // short session ID (4 chars)
}

export interface LedgerSession {
  session_id: string;
  peer_alias: string;
  state: string;
  pending_terms?: {
    proposal_text?: string;
    my_tasks?: string[];
    your_tasks?: string[];
    deadline?: string;
    trusted?: boolean;
    peer_ip?: string;
  };
  final_terms?: {
    type?: string;
    from_alias?: string;
    part_done?: string;
    part_remaining?: string;
    context?: string;
    received_at?: string;
  };
  created_at?: string;
}

/**
 * Extract a named ## section from a Markdown document.
 * Returns the section content (without the header), or null if not found.
 */
export function extractSection(content: string, header: string): string | null {
  const start = content.indexOf(header);
  if (start === -1) return null;
  const afterHeader = start + header.length;
  const nextSection = content.indexOf('\n## ', afterHeader);
  return nextSection === -1
    ? content.slice(afterHeader).trim()
    : content.slice(afterHeader, nextSection).trim();
}

/**
 * Parse all [ACTIVE] commitment entries from the ## Diplomat Commitments section.
 * Format: - **[ACTIVE]** Peer: Alice | My: task | Their: task | Due: 2026-03-27 17:00 UTC | ID: `a3f9`
 */
export function parseActiveEntries(section: string): CommitmentEntry[] {
  return section
    .split('\n')
    .filter(l => l.includes('[ACTIVE]'))
    .map(parseLine)
    .filter((e): e is CommitmentEntry => e !== null);
}

function parseLine(line: string): CommitmentEntry | null {
  const peerM = line.match(/Peer: ([^|]+)/);
  const myM   = line.match(/My: ([^|]+)/);
  const dueM  = line.match(/Due: ([^|]+UTC)/);
  const idM   = line.match(/ID: `([^`]+)`/);
  if (!peerM || !myM || !dueM || !idM) return null;

  const dueStr = dueM[1].trim();
  return {
    peer:          peerM[1].trim(),
    myTask:        myM[1].trim(),
    deadlineLocal: dueStr,
    deadlineUtc:   dueStr, // Due field stored in UTC ISO8601-ish
    id:            idM[1].trim(),
  };
}

/**
 * Truncate a string to max characters, appending '…' if truncated.
 */
export function truncate(s: string, max: number): string {
  return s.length <= max ? s : s.slice(0, max - 1) + '…';
}

/**
 * Parse ledger.json and return sessions in INBOUND_PENDING state.
 * Used by diplomat-heartbeat to surface pending inbound proposals.
 */
export function parseInboundPending(ledgerContent: string): LedgerSession[] {
  try {
    const ledger = JSON.parse(ledgerContent) as { sessions?: LedgerSession[] };
    return (ledger.sessions ?? []).filter(s => s.state === 'INBOUND_PENDING');
  } catch {
    return [];
  }
}

/**
 * Parse ledger.json and return sessions in HANDOFF_RECEIVED state.
 * Used by diplomat-heartbeat to surface incoming task handoffs from peers.
 * Each returned session has final_terms with part_done, part_remaining, context.
 */
export function parseHandoffReceived(ledgerContent: string): LedgerSession[] {
  try {
    const ledger = JSON.parse(ledgerContent) as { sessions?: LedgerSession[] };
    return (ledger.sessions ?? []).filter(s => s.state === 'HANDOFF_RECEIVED');
  } catch {
    return [];
  }
}
