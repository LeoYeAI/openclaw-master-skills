#!/usr/bin/env node
/**
 * BrainX V5 — Contradiction Detector (Phase 3.1)
 *
 * Detects semantically overlapping hot memories and marks older/shorter
 * ones as superseded by their newer/more-complete counterpart.
 *
 * Usage:
 *   node scripts/contradiction-detector.js [--top N] [--threshold N] [--dry-run] [--verbose]
 *
 * Options:
 *   --top N        Number of hot memories to analyze (default 30)
 *   --threshold N  Cosine similarity threshold (default 0.85)
 *   --dry-run      Report only, do not update the database
 *   --verbose      Print detailed pair analysis
 */

'use strict';

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });
const db = require('../lib/db');

// ── CLI args ────────────────────────────────────────────────────────────────
function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { top: 30, threshold: 0.85, dryRun: false, verbose: false };

  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--top':
        opts.top = parseInt(args[++i], 10) || 30;
        break;
      case '--threshold':
        opts.threshold = parseFloat(args[++i]) || 0.85;
        break;
      case '--dry-run':
        opts.dryRun = true;
        break;
      case '--verbose':
        opts.verbose = true;
        break;
    }
  }
  return opts;
}

// ── Main ────────────────────────────────────────────────────────────────────
async function main() {
  const opts = parseArgs();
  const startMs = Date.now();

  if (opts.verbose) {
    console.error(`[contradiction-detector] top=${opts.top} threshold=${opts.threshold} dryRun=${opts.dryRun}`);
  }

  // 1. Fetch top hot memories (not already superseded)
  const { rows: memories } = await db.query(`
    SELECT id, type, content, context, tier, importance, access_count, tags, created_at,
           length(content) AS content_len
    FROM brainx_memories
    WHERE superseded_by IS NULL
      AND tier = 'hot'
    ORDER BY access_count DESC NULLS LAST, importance DESC
    LIMIT $1
  `, [opts.top]);

  if (opts.verbose) {
    console.error(`[contradiction-detector] fetched ${memories.length} hot memories`);
  }

  if (memories.length < 2) {
    const result = { ok: true, pairsAnalyzed: 0, contradictionsFound: 0, superseded: [], complementary: 0, details: [] };
    console.log(JSON.stringify(result, null, 2));
    await db.pool.end();
    return;
  }

  // 2. Compute pairwise cosine similarity in one efficient query
  //    Build id list and fetch all similarities at once
  const ids = memories.map(m => m.id);
  const idIndex = Object.fromEntries(memories.map((m, i) => [m.id, i]));

  // Generate pairs
  const pairs = [];
  for (let i = 0; i < memories.length; i++) {
    for (let j = i + 1; j < memories.length; j++) {
      pairs.push([memories[i], memories[j]]);
    }
  }

  if (opts.verbose) {
    console.error(`[contradiction-detector] analyzing ${pairs.length} pairs`);
  }

  // Batch-fetch similarities for all pairs using a single query with unnest
  const idPairsA = pairs.map(p => p[0].id);
  const idPairsB = pairs.map(p => p[1].id);

  const { rows: simRows } = await db.query(`
    SELECT a_id, b_id, 1 - (ma.embedding <=> mb.embedding) AS similarity
    FROM unnest($1::text[], $2::text[]) AS t(a_id, b_id)
    JOIN brainx_memories ma ON ma.id = t.a_id
    JOIN brainx_memories mb ON mb.id = t.b_id
  `, [idPairsA, idPairsB]);

  // Index similarities by pair
  const simMap = new Map();
  for (const row of simRows) {
    simMap.set(`${row.a_id}|${row.b_id}`, parseFloat(row.similarity));
  }

  // 3. Analyze high-similarity pairs
  const supersededIds = [];
  let complementary = 0;
  const details = [];

  for (const [memA, memB] of pairs) {
    const sim = simMap.get(`${memA.id}|${memB.id}`);
    if (sim === undefined || sim < opts.threshold) continue;

    // Different contexts → complementary, not contradiction
    if (memA.context && memB.context && memA.context !== memB.context) {
      complementary++;
      if (opts.verbose) {
        console.error(`  [complementary] ${memA.id} <> ${memB.id} sim=${sim.toFixed(3)} contexts differ (${memA.context} vs ${memB.context})`);
      }
      details.push({
        action: 'complementary',
        ids: [memA.id, memB.id],
        similarity: parseFloat(sim.toFixed(4)),
        reason: `different contexts: "${memA.context}" vs "${memB.context}"`
      });
      continue;
    }

    // Determine which to keep: prefer newer + longer content
    const aDate = new Date(memA.created_at);
    const bDate = new Date(memB.created_at);
    const aLen = memA.content_len;
    const bLen = memB.content_len;

    // Size difference threshold: 10% — "same size" if within 10%
    const sizeDiffRatio = Math.abs(aLen - bLen) / Math.max(aLen, bLen, 1);
    const sameSize = sizeDiffRatio < 0.10;

    let keepMem, supersedeMem, reason;

    if (sameSize) {
      // Same size → keep higher importance
      if (memA.importance >= memB.importance) {
        keepMem = memA;
        supersedeMem = memB;
      } else {
        keepMem = memB;
        supersedeMem = memA;
      }
      reason = `same size (${aLen} vs ${bLen}), kept higher importance (${keepMem.importance} >= ${supersedeMem.importance})`;
    } else {
      // Different size → prefer newer AND longer
      const aIsNewer = aDate >= bDate;
      const aIsLonger = aLen > bLen;
      const bIsNewer = bDate >= aDate;
      const bIsLonger = bLen > aLen;

      if (aIsNewer && aIsLonger) {
        keepMem = memA;
        supersedeMem = memB;
        reason = `A is newer (${aDate.toISOString().slice(0, 10)}) and longer (${aLen} > ${bLen})`;
      } else if (bIsNewer && bIsLonger) {
        keepMem = memB;
        supersedeMem = memA;
        reason = `B is newer (${bDate.toISOString().slice(0, 10)}) and longer (${bLen} > ${aLen})`;
      } else {
        // Conflict: newer but shorter — keep the longer one (more complete)
        if (aIsLonger) {
          keepMem = memA;
          supersedeMem = memB;
          reason = `A is longer (${aLen} > ${bLen}) though B is newer; keeping more complete`;
        } else {
          keepMem = memB;
          supersedeMem = memA;
          reason = `B is longer (${bLen} > ${aLen}) though A is newer; keeping more complete`;
        }
      }
    }

    if (opts.verbose) {
      console.error(`  [supersede] ${supersedeMem.id} → superseded by ${keepMem.id} sim=${sim.toFixed(3)} ${reason}`);
    }

    // Skip if already superseded by a previous pair in this run
    if (supersededIds.includes(supersedeMem.id)) {
      if (opts.verbose) {
        console.error(`    [skip] ${supersedeMem.id} already superseded in this run`);
      }
      continue;
    }

    // Merge tags from superseded into keeper
    const mergedTags = [...new Set([...(keepMem.tags || []), ...(supersedeMem.tags || []), 'dedup_contradiction'])];

    if (!opts.dryRun) {
      // Mark superseded
      await db.query(
        `UPDATE brainx_memories SET superseded_by = $1 WHERE id = $2`,
        [keepMem.id, supersedeMem.id]
      );

      // Merge tags into keeper
      await db.query(
        `UPDATE brainx_memories SET tags = $1 WHERE id = $2`,
        [mergedTags, keepMem.id]
      );
    }

    supersededIds.push(supersedeMem.id);
    details.push({
      action: 'superseded',
      kept: keepMem.id,
      superseded: supersedeMem.id,
      similarity: parseFloat(sim.toFixed(4)),
      reason
    });
  }

  const durationMs = Date.now() - startMs;

  // 4. Log to brainx_query_log (if constraint allows; gracefully skip if not)
  try {
    await db.query(
      `INSERT INTO brainx_query_log (query_hash, query_kind, results_count, duration_ms)
       VALUES ($1, 'contradiction_check', $2, $3)`,
      [
        `contradiction_${new Date().toISOString().slice(0, 10)}`,
        supersededIds.length,
        durationMs
      ]
    );
  } catch (logErr) {
    // CHECK constraint may not include 'contradiction_check' — safe to skip
    if (opts.verbose) {
      console.error(`[contradiction-detector] query_log insert skipped: ${logErr.message}`);
    }
  }

  // 5. Output result
  const result = {
    ok: true,
    dryRun: opts.dryRun,
    pairsAnalyzed: pairs.length,
    contradictionsFound: supersededIds.length,
    superseded: supersededIds,
    complementary,
    durationMs,
    details
  };

  console.log(JSON.stringify(result, null, 2));
  await db.pool.end();
}

main().catch(async (err) => {
  console.error(err);
  try { await db.pool.end(); } catch (_) {}
  process.exit(1);
});
