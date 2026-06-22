#!/usr/bin/env node
/**
 * cross-agent-learning.js — BrainX V5 Phase 4.2
 *
 * Propagates high-importance learnings and gotchas from individual agents
 * to the global context so ALL agents benefit from shared discoveries.
 *
 * Usage:
 *   node scripts/cross-agent-learning.js [--hours N] [--dry-run] [--verbose] [--max-shares N]
 */

'use strict';

const path = require('path');
const crypto = require('crypto');

// ── Bootstrap ───────────────────────────────────────────────────────────
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });
const db = require(path.join(__dirname, '..', 'lib', 'db'));
const rag = require(path.join(__dirname, '..', 'lib', 'openai-rag'));

// ── Args ────────────────────────────────────────────────────────────────
const args = process.argv.slice(2);

function flag(name) {
  return args.includes(`--${name}`);
}
function option(name, fallback) {
  const idx = args.indexOf(`--${name}`);
  if (idx === -1 || idx + 1 >= args.length) return fallback;
  return args[idx + 1];
}

const HOURS = parseInt(option('hours', '24'), 10);
const DRY_RUN = flag('dry-run');
const VERBOSE = flag('verbose');
const MAX_SHARES = parseInt(option('max-shares', '10'), 10);

function log(...a) { if (VERBOSE) console.error('[cross-agent]', ...a); }

// ── Sleep helper ────────────────────────────────────────────────────────
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ── Main ────────────────────────────────────────────────────────────────
async function main() {
  const result = {
    ok: true,
    candidatesFound: 0,
    alreadyShared: 0,
    newlyShared: 0,
    skippedMaxShares: 0,
    bySourceAgent: {},
    errors: [],
  };

  try {
    // 1. Find recent high-importance learnings/gotchas from specific agents
    log(`Searching for learnings/gotchas/decisions/facts in last ${HOURS}h with importance >= 5...`);

    const candidates = await db.query(
      `SELECT id, type, content, context, tier, importance, tags, embedding, created_at
       FROM brainx_memories
       WHERE superseded_by IS NULL
         AND (
           (type IN ('learning', 'gotcha') AND importance >= 5)
           OR (type IN ('decision', 'fact') AND importance >= 6)
         )
         AND context LIKE 'agent:%'
         AND context != 'global'
         AND created_at > NOW() - make_interval(hours => $1)
       ORDER BY importance DESC, created_at DESC
       LIMIT 20`,
      [HOURS]
    );

    result.candidatesFound = candidates.rows.length;
    log(`Found ${result.candidatesFound} candidates`);

    if (result.candidatesFound === 0) {
      console.log(JSON.stringify(result));
      return;
    }

    // 2. For each candidate, check if a global copy already exists
    for (const mem of candidates.rows) {
      if (result.newlyShared >= MAX_SHARES) {
        result.skippedMaxShares++;
        log(`Max shares (${MAX_SHARES}) reached, skipping ${mem.id}`);
        continue;
      }

      // Extract agent name from context (e.g. "agent:coder" → "coder")
      const agentName = mem.context.replace(/^agent:/, '');

      // Check for existing global copy using embedding similarity
      // The embedding column is already a vector — pass it directly
      const existing = await db.query(
        `SELECT id FROM brainx_memories
         WHERE context = 'global'
           AND superseded_by IS NULL
           AND 1 - (embedding <=> $1) > 0.90
         LIMIT 1`,
        [mem.embedding]
      );

      if (existing.rows.length > 0) {
        result.alreadyShared++;
        log(`Already shared: ${mem.id} (matched global ${existing.rows[0].id})`);
        continue;
      }

      // 3. Create global copy
      const globalId = `m_global_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
      const globalContent = `[Shared from ${mem.context}] ${mem.content}`;
      const originalTags = Array.isArray(mem.tags) ? mem.tags : [];
      const globalTags = [...originalTags, 'cross-agent', `origin:${mem.context}`];
      const globalImportance = Math.max((mem.importance || 5) - 1, 5);

      log(`Sharing: ${mem.id} → ${globalId} (${mem.type}, importance ${globalImportance})`);

      if (!DRY_RUN) {
        try {
          await rag.storeMemory({
            id: globalId,
            type: mem.type,
            content: globalContent,
            context: 'global',
            tier: 'warm',
            importance: globalImportance,
            tags: globalTags,
          });
          log(`Stored global memory: ${globalId}`);
        } catch (err) {
          result.errors.push({ memoryId: mem.id, error: err.message });
          log(`Error storing ${globalId}: ${err.message}`);
          continue;
        }

        // Rate limit: 300ms between embedding API calls
        await sleep(300);
      } else {
        log(`[DRY-RUN] Would share: ${mem.id} → ${globalId}`);
      }

      result.newlyShared++;
      result.bySourceAgent[agentName] = (result.bySourceAgent[agentName] || 0) + 1;
    }

    // Report
    if (DRY_RUN) {
      log('[DRY-RUN] No memories were actually stored.');
    }

    console.log(JSON.stringify(result));
  } catch (err) {
    result.ok = false;
    result.errors.push({ error: err.message, stack: err.stack });
    console.log(JSON.stringify(result));
    process.exitCode = 1;
  } finally {
    await db.pool.end();
  }
}

main();
