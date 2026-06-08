/**
 * events.mjs — Append-only Event Log for Stitch Design skill.
 *
 * Records every screen operation and alias change as an immutable JSONL log.
 * names.json is a rebuildable snapshot derived from this log.
 *
 * State lives in: state/projects/<projectId>/events.jsonl
 * Append-only: never edit, never delete lines.
 */

import { appendFile, readFile, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomBytes } from 'node:crypto';

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = join(__dirname, '..', 'state', 'projects');

const SCHEMA_VERSION = 1;

// --- Event ID generation ---

/** Generate a short unique event ID: evt_ + 8 hex chars */
function makeEventId() {
  return 'evt_' + randomBytes(4).toString('hex');
}

// --- File paths ---

function eventsFilePath(projectId) {
  return join(STATE_DIR, projectId, 'events.jsonl');
}

// --- Core: Append ---

/**
 * Append a single event to the project's event log.
 * @param {string} projectId
 * @param {object} event — must have `op` at minimum; id/v/ts/projectId are auto-added
 * @returns {object} the complete event as written
 */
export async function appendEvent(projectId, event) {
  const fp = eventsFilePath(projectId);
  const dir = dirname(fp);
  await mkdir(dir, { recursive: true });

  const full = {
    v: SCHEMA_VERSION,
    id: makeEventId(),
    ts: new Date().toISOString(),
    projectId,
    ...event,
  };

  await appendFile(fp, JSON.stringify(full) + '\n');
  return full;
}

// --- Core: Read ---

/**
 * Read all events for a project. Returns array of parsed event objects.
 * @param {string} projectId
 * @returns {object[]}
 */
export async function readEvents(projectId) {
  const fp = eventsFilePath(projectId);
  if (!existsSync(fp)) return [];

  const raw = await readFile(fp, 'utf8');
  const events = [];
  for (const line of raw.split('\n')) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    try {
      events.push(JSON.parse(trimmed));
    } catch {
      // skip malformed lines
    }
  }
  return events;
}

// --- Prompt preview ---

/**
 * Truncate a prompt to a preview string (max 120 chars).
 */
export function promptPreview(prompt) {
  if (!prompt) return null;
  if (prompt.length <= 120) return prompt;
  return prompt.slice(0, 117) + '...';
}

// --- Variant Group ID ---

/**
 * Generate a variant group ID from a timestamp.
 */
export function makeVariantGroupId() {
  const ts = new Date().toISOString().replace(/[-:]/g, '').replace('T', '-').slice(0, 15);
  return 'vg_' + ts;
}

// --- Query helpers ---

/**
 * Get all events for a specific alias (both screen ops with that alias and alias ops).
 * @param {string} projectId
 * @param {string} alias
 * @returns {object[]} chronological events
 */
export async function historyForAlias(projectId, alias) {
  const events = await readEvents(projectId);
  return events.filter(e =>
    e.alias === alias ||
    e.previousAlias === alias
  );
}

/**
 * Get the alias-binding history: only alias_set events for a given alias.
 * Each entry represents a "revision" of what that alias pointed to.
 * @param {string} projectId
 * @param {string} alias
 * @returns {object[]} chronological alias_set events
 */
export async function aliasRevisions(projectId, alias) {
  const events = await readEvents(projectId);
  return events.filter(e =>
    e.op === 'alias_set' && e.alias === alias
  );
}

/**
 * Walk the lineage DAG backwards from a screenId.
 * Returns array from the given screen back to root.
 * @param {string} projectId
 * @param {string} screenId
 * @returns {object[]} events from leaf to root
 */
export async function lineage(projectId, screenId) {
  const events = await readEvents(projectId);

  // Build a map: screenId → event that created it
  const screenMap = new Map();
  for (const e of events) {
    if (e.screenId && (e.op === 'generate' || e.op === 'edit')) {
      screenMap.set(e.screenId, e);
    }
    // For variants, each screenId in the array
    if (e.op === 'variants' && e.screenIds) {
      for (const sid of e.screenIds) {
        screenMap.set(sid, e);
      }
    }
  }

  const chain = [];
  let current = screenId;
  const visited = new Set();

  while (current && !visited.has(current)) {
    visited.add(current);
    const evt = screenMap.get(current);
    if (!evt) break;
    chain.push(evt);
    current = evt.parentScreenId || null;
  }

  return chain;
}

/**
 * Rebuild names.json from the event log.
 * Replays all alias_set and alias_renamed events in order.
 * @param {string} projectId
 * @returns {object} the rebuilt names data structure
 */
/**
 * Rebuild names.json from the event log.
 * Replays all alias_set and alias_renamed events in order.
 * If existingNames is provided, uses it as a base for aliases that predate event logging.
 * @param {string} projectId
 * @param {object} [existingNames] — current names.json data to preserve pre-log aliases
 * @returns {object} the rebuilt names data structure
 */
export async function rebuildNames(projectId, existingNames = null) {
  const events = await readEvents(projectId);

  // Start from existing names as base (for aliases created before event logging)
  const names = {};
  if (existingNames?.names) {
    for (const [alias, data] of Object.entries(existingNames.names)) {
      names[alias] = { ...data };
    }
  }

  // Replay events on top — events are authoritative where they exist
  for (const e of events) {
    if (e.op === 'alias_set') {
      names[e.alias] = {
        screenId: e.screenId,
        updatedAt: e.ts,
        ...(e.note ? { note: e.note } : {}),
      };
    } else if (e.op === 'alias_renamed') {
      if (names[e.previousAlias]) {
        names[e.alias] = {
          ...names[e.previousAlias],
          updatedAt: e.ts,
        };
        delete names[e.previousAlias];
      }
    } else if (e.op === 'alias_removed') {
      delete names[e.alias];
    }
  }

  return {
    version: SCHEMA_VERSION,
    project: projectId,
    rebuiltFromEvents: true,
    rebuiltAt: new Date().toISOString(),
    names,
  };
}
