#!/usr/bin/env node
/**
 * BrainX V5 — Context-Pack Builder (Phase 2.2)
 *
 * Generates weekly "context packs" that summarise hot/warm memories
 * grouped by context (agent:*, project:*).  Packs are compact markdown
 * blocks designed for efficient LLM injection (fewer tokens, more signal).
 *
 * Usage:
 *   node scripts/context-pack-builder.js [--days N] [--dry-run] [--verbose]
 */

'use strict';

const path = require('path');
const fs   = require('fs');

// ── Bootstrap env + DB ────────────────────────────────────────────────
require('dotenv').config({ path: path.join(__dirname, '..', '.env') });
const db = require('../lib/db');

// ── CLI args ──────────────────────────────────────────────────────────
const args   = process.argv.slice(2);
const DAYS   = (() => { const i = args.indexOf('--days'); return i !== -1 && args[i + 1] ? parseInt(args[i + 1], 10) : 7; })();
const DRY    = args.includes('--dry-run');
const VERB   = args.includes('--verbose');

const MAX_CONTENT_LEN = 200;   // per-memory content truncation
const MAX_PACK_LEN    = 800;   // per-context pack max chars

const DATA_DIR  = path.join(__dirname, '..', 'data');
const JSON_PATH = path.join(DATA_DIR, 'context-packs.json');

// ── Helpers ───────────────────────────────────────────────────────────
function truncate(str, max) {
  if (!str) return '';
  const clean = str.replace(/\n/g, ' ').trim();
  return clean.length <= max ? clean : clean.slice(0, max - 1) + '…';
}

function log(...a) { if (VERB) console.error('[context-pack-builder]', ...a); }

// ── Main ──────────────────────────────────────────────────────────────
async function main() {
  // 1. Fetch hot + warm memories from the last N days
  const { rows: memories } = await db.query(`
    SELECT id, type, content, context, tier, importance, tags, created_at
    FROM brainx_memories
    WHERE superseded_by IS NULL
      AND tier IN ('hot', 'warm')
      AND created_at > NOW() - $1::interval
    ORDER BY importance DESC, created_at DESC
  `, [`${DAYS} days`]);

  log(`Fetched ${memories.length} memories from last ${DAYS} days`);

  if (memories.length === 0) {
    console.log(JSON.stringify({ packs: [], count: 0, days: DAYS, message: 'No memories found' }));
    process.exit(0);
  }

  // 2. Group by context
  const groups = {};
  for (const m of memories) {
    const ctx = m.context || 'unknown';
    if (!groups[ctx]) groups[ctx] = [];
    groups[ctx].push(m);
  }

  log(`Grouped into ${Object.keys(groups).length} contexts: ${Object.keys(groups).join(', ')}`);

  // 3. Build packs
  const packs = [];

  for (const [ctx, mems] of Object.entries(groups)) {
    const avgImp = (mems.reduce((s, m) => s + (m.importance || 0), 0) / mems.length).toFixed(1);
    let header = `### ${ctx} (${mems.length} memories, avg importance ${avgImp})`;
    let lines  = [];

    for (const m of mems) {
      const line = `- [${m.type || 'note'}] ${truncate(m.content, MAX_CONTENT_LEN)}`;
      lines.push(line);
    }

    // Assemble and enforce MAX_PACK_LEN
    let pack = header + '\n' + lines.join('\n');
    if (pack.length > MAX_PACK_LEN) {
      // Keep header, trim lines until within budget
      let trimmed = header + '\n';
      for (const line of lines) {
        if ((trimmed + line + '\n').length > MAX_PACK_LEN - 20) {
          trimmed += `- ... (+${mems.length - lines.indexOf(line)} more)\n`;
          break;
        }
        trimmed += line + '\n';
      }
      pack = trimmed.trimEnd();
    }

    packs.push({
      context:     ctx,
      memoryCount: mems.length,
      avgImportance: parseFloat(avgImp),
      pack,
      generatedAt: new Date().toISOString(),
    });
  }

  // 4. Output
  const output = {
    packs,
    count:  packs.length,
    days:   DAYS,
    dryRun: DRY,
    generatedAt: new Date().toISOString(),
  };

  console.log(JSON.stringify(output, null, 2));

  if (DRY) {
    log('Dry run — skipping persistence');
    process.exit(0);
  }

  // 5. Persist — try table first, fall back to JSON file
  let usedTable = false;
  try {
    const { rows } = await db.query(
      "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'brainx_context_packs')"
    );
    if (rows[0].exists) {
      await persistToTable(packs);
      usedTable = true;
      log('Saved packs to brainx_context_packs table');
    }
  } catch (err) {
    log('Table persistence failed, falling back to JSON:', err.message);
  }

  if (!usedTable) {
    await persistToJson(output);
    log(`Saved packs to ${JSON_PATH}`);
  }

  process.exit(0);
}

// ── Persistence: DB table ─────────────────────────────────────────────
async function persistToTable(packs) {
  for (const p of packs) {
    const id = `cp_${p.context.replace(/[^a-z0-9]/gi, '_')}_${Date.now()}`;
    await db.query(`
      INSERT INTO brainx_context_packs (id, data, created_at, updated_at)
      VALUES ($1, $2, NOW(), NOW())
    `, [id, JSON.stringify(p)]);
  }
}

// ── Persistence: JSON file fallback ───────────────────────────────────
async function persistToJson(output) {
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }
  fs.writeFileSync(JSON_PATH, JSON.stringify(output, null, 2), 'utf-8');
}

// ── Run ───────────────────────────────────────────────────────────────
main().catch(err => {
  console.error('FATAL:', err);
  process.exit(1);
});
