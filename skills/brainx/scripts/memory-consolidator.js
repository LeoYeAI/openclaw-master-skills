#!/usr/bin/env node

/**
 * memory-consolidator.js — Cluster semantically similar memories and merge them.
 *
 * Uses BFS + union-find over vector similarity to find clusters,
 * then merges via heuristic (no LLM) and supersedes originals.
 *
 * Usage:
 *   node scripts/memory-consolidator.js [options]
 *   ./brainx-v5 consolidate [options]
 *
 * Options:
 *   --dry-run          Preview without changes
 *   --verbose          Show cluster details
 *   --limit N          Max clusters to process (default: 50)
 *   --min-similarity   Similarity threshold (default: 0.85)
 *   --max-cluster      Max cluster size (default: 7)
 *   --min-cluster      Min cluster size (default: 2)
 *   --json             Machine-readable output
 */

'use strict';

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const crypto = require('crypto');
const db = require('../lib/db');
const { embed, storeMemory } = require('../lib/openai-rag');

function makeId() {
  return `m_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
}

// ── CLI args ─────────────────────────────────────────
const argv = process.argv.slice(2);

function flag(name) {
  return argv.includes(`--${name}`);
}

function opt(name, defaultVal) {
  const idx = argv.indexOf(`--${name}`);
  if (idx === -1 || idx + 1 >= argv.length) return defaultVal;
  return argv[idx + 1];
}

const DRY_RUN = flag('dry-run');
const VERBOSE = flag('verbose');
const JSON_OUT = flag('json');
const LIMIT = parseInt(opt('limit', '50'), 10);
const MIN_SIMILARITY = parseFloat(opt('min-similarity', '0.85'));
const MAX_CLUSTER = parseInt(opt('max-cluster', '7'), 10);
const MIN_CLUSTER = parseInt(opt('min-cluster', '2'), 10);

function log(...args) {
  if (!JSON_OUT) console.log(...args);
}

function vlog(...args) {
  if (VERBOSE && !JSON_OUT) console.log(...args);
}

// ── Fetch active memories ────────────────────────────
async function fetchActiveMemories() {
  const res = await db.query(`
    SELECT id, content, importance, tier, type, context, agent, tags,
           confidence_score, source_kind, created_at, last_accessed
    FROM brainx_memories
    WHERE superseded_by IS NULL
      AND tier != 'archive'
    ORDER BY created_at DESC
  `);
  return res.rows;
}

// ── Find similar memories for a given ID ─────────────
async function findSimilar(memoryId, threshold) {
  const res = await db.query(`
    SELECT id, content, importance, tier, type, context, agent, tags,
           confidence_score, source_kind, created_at, last_accessed,
           1 - (embedding <=> (SELECT embedding FROM brainx_memories WHERE id = $1)) AS similarity
    FROM brainx_memories
    WHERE id != $1
      AND superseded_by IS NULL
      AND tier != 'archive'
      AND 1 - (embedding <=> (SELECT embedding FROM brainx_memories WHERE id = $1)) > $2
    ORDER BY similarity DESC
    LIMIT 10
  `, [memoryId, threshold]);
  return res.rows;
}

// ── BFS clustering with union-find ───────────────────
async function buildClusters(memories) {
  const memMap = new Map();
  for (const m of memories) memMap.set(m.id, m);

  const processed = new Set();
  const clusters = [];

  for (const mem of memories) {
    if (processed.has(mem.id)) continue;

    // BFS from this memory
    const cluster = new Map();
    cluster.set(mem.id, mem);
    const queue = [mem.id];
    processed.add(mem.id);

    while (queue.length > 0) {
      const currentId = queue.shift();

      // Stop expanding if cluster is already at max
      if (cluster.size >= MAX_CLUSTER) break;

      const similar = await findSimilar(currentId, MIN_SIMILARITY);
      for (const s of similar) {
        if (processed.has(s.id)) continue;
        if (cluster.size >= MAX_CLUSTER) break;

        processed.add(s.id);
        cluster.set(s.id, memMap.get(s.id) || s);
        queue.push(s.id);
      }
    }

    if (cluster.size >= MIN_CLUSTER && cluster.size <= MAX_CLUSTER) {
      clusters.push([...cluster.values()]);
    }
  }

  return clusters;
}

// ── Heuristic merge (no LLM) ─────────────────────────
function mergeCluster(memories) {
  // Sort by importance DESC, then content length DESC
  const sorted = [...memories].sort((a, b) =>
    ((b.importance || 5) - (a.importance || 5)) || (b.content.length - a.content.length)
  );

  const base = sorted[0];
  const baseSentences = new Set(
    base.content.split(/[.!?\n]+/).map(s => s.trim().toLowerCase()).filter(Boolean)
  );

  // Collect unique sentences from other memories
  const additions = [];
  for (const mem of sorted.slice(1)) {
    const sentences = mem.content.split(/[.!?\n]+/).map(s => s.trim()).filter(Boolean);
    for (const s of sentences) {
      if (s.length < 10) continue;
      const lc = s.toLowerCase();
      let isDuplicate = false;
      for (const existing of baseSentences) {
        const sWords = new Set(lc.split(/\s+/));
        const eWords = new Set(existing.split(/\s+/));
        const overlap = [...sWords].filter(w => eWords.has(w)).length;
        if (overlap / Math.max(sWords.size, 1) > 0.6) {
          isDuplicate = true;
          break;
        }
      }
      if (!isDuplicate) {
        additions.push(s);
        baseSentences.add(lc);
      }
    }
  }

  let mergedContent = base.content;
  if (additions.length > 0) {
    mergedContent += '\n' + additions.join('. ') + '.';
  }

  // Pick best tier
  const tierPriority = { hot: 3, warm: 2, cold: 1 };
  const bestTier = memories.reduce((best, m) =>
    (tierPriority[m.tier] || 0) > (tierPriority[best] || 0) ? m.tier : best
  , 'cold');

  // Most recent last_accessed
  const lastAccessed = memories.reduce((latest, m) => {
    const d = m.last_accessed ? new Date(m.last_accessed) : null;
    if (!d) return latest;
    return (!latest || d > latest) ? d : latest;
  }, null);

  return {
    content: mergedContent.slice(0, 5000),
    importance: Math.max(...memories.map(m => m.importance || 5)),
    tier: bestTier,
    type: base.type,
    context: base.context,
    agent: base.agent,
    tags: [...new Set(memories.flatMap(m => m.tags || []))],
    confidence_score: Math.max(...memories.map(m => m.confidence_score || 0.7)),
    source_kind: 'consolidated',
    source_ids: memories.map(m => m.id),
    last_accessed: lastAccessed
  };
}

// ── Store consolidated memory and supersede originals ─
async function consolidateCluster(merged) {
  // Generate embedding for merged content
  const embeddingText = `${merged.type}: ${merged.content} [context: ${merged.context || ''}]`;
  const embedding = await embed(embeddingText);

  // Store as new memory
  const result = await db.withClient(async (client) => {
    await client.query('BEGIN');
    try {
      // Insert new consolidated memory with explicit ID
      const newMemId = makeId();
      const insertRes = await client.query(`
        INSERT INTO brainx_memories (
          id, type, content, context, tier, agent, importance, embedding, tags,
          source_kind, confidence_score, last_accessed
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8::vector, $9, $10, $11, $12)
        RETURNING id
      `, [
        newMemId,
        merged.type,
        merged.content,
        merged.context || null,
        merged.tier,
        merged.agent || null,
        merged.importance,
        JSON.stringify(embedding),
        merged.tags,
        'consolidated',
        merged.confidence_score,
        merged.last_accessed
      ]);

      const newId = insertRes.rows[0].id;

      // Supersede all original cluster members
      await client.query(`
        UPDATE brainx_memories
        SET superseded_by = $1,
            tags = CASE
              WHEN NOT (tags @> ARRAY['consolidated']) THEN tags || ARRAY['consolidated']
              ELSE tags
            END
        WHERE id = ANY($2::text[])
      `, [newId, merged.source_ids]);

      await client.query('COMMIT');
      return { id: newId, superseded: merged.source_ids.length };
    } catch (err) {
      await client.query('ROLLBACK');
      throw err;
    }
  });

  return result;
}

// ── Main ─────────────────────────────────────────────
async function main() {
  const startTime = Date.now();

  log('🧠 BrainX Memory Consolidator');
  log(`   Similarity threshold: ${MIN_SIMILARITY}`);
  log(`   Cluster size: ${MIN_CLUSTER}-${MAX_CLUSTER}`);
  log(`   Max clusters: ${LIMIT}`);
  log(`   Mode: ${DRY_RUN ? 'DRY RUN' : 'LIVE'}`);
  log('');

  // Count total before
  const countBefore = await db.query(
    `SELECT count(*) as total FROM brainx_memories WHERE superseded_by IS NULL AND tier != 'archive'`
  );
  const totalBefore = parseInt(countBefore.rows[0].total, 10);
  log(`📊 Active memories before: ${totalBefore}`);

  // Fetch and cluster
  log('🔍 Fetching active memories...');
  const memories = await fetchActiveMemories();
  log(`   Found ${memories.length} active memories`);

  log('🔗 Building similarity clusters...');
  const allClusters = await buildClusters(memories);
  log(`   Found ${allClusters.length} clusters total`);

  const clustersToProcess = allClusters.slice(0, LIMIT);
  log(`   Processing ${clustersToProcess.length} clusters`);
  log('');

  const stats = {
    totalMemories: memories.length,
    clustersFound: allClusters.length,
    clustersProcessed: 0,
    memoriesConsolidated: 0,
    newMemories: 0,
    errors: 0
  };

  const results = [];

  for (let i = 0; i < clustersToProcess.length; i++) {
    const cluster = clustersToProcess[i];
    const merged = mergeCluster(cluster);

    vlog(`\n── Cluster ${i + 1} (${cluster.length} memories) ──`);
    for (const m of cluster) {
      vlog(`   [${m.id.slice(0, 8)}] imp=${m.importance} tier=${m.tier} "${m.content.slice(0, 80)}..."`);
    }
    vlog(`   → Merged: "${merged.content.slice(0, 100)}..."`);
    vlog(`   → Tags: [${merged.tags.join(', ')}]`);
    vlog(`   → Importance: ${merged.importance}, Tier: ${merged.tier}`);

    if (DRY_RUN) {
      results.push({
        cluster: i + 1,
        size: cluster.length,
        memberIds: cluster.map(m => m.id),
        mergedPreview: merged.content.slice(0, 200),
        importance: merged.importance,
        tier: merged.tier,
        tags: merged.tags
      });
      stats.clustersProcessed++;
      stats.memoriesConsolidated += cluster.length;
      continue;
    }

    try {
      const result = await consolidateCluster(merged);
      log(`   ✅ Cluster ${i + 1}: created ${result.id.slice(0, 8)}, superseded ${result.superseded} memories`);
      results.push({
        cluster: i + 1,
        newId: result.id,
        superseded: result.superseded,
        memberIds: cluster.map(m => m.id)
      });
      stats.clustersProcessed++;
      stats.memoriesConsolidated += cluster.length;
      stats.newMemories++;
    } catch (err) {
      log(`   ❌ Cluster ${i + 1} failed: ${err.message}`);
      stats.errors++;
    }
  }

  // Count total after
  const countAfter = await db.query(
    `SELECT count(*) as total FROM brainx_memories WHERE superseded_by IS NULL AND tier != 'archive'`
  );
  const totalAfter = parseInt(countAfter.rows[0].total, 10);
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

  log('');
  log('═══════════════════════════════════════');
  log(`📊 Consolidation ${DRY_RUN ? '(DRY RUN) ' : ''}Summary:`);
  log(`   Active memories: ${totalBefore} → ${DRY_RUN ? '(unchanged)' : totalAfter}`);
  log(`   Clusters found: ${stats.clustersFound}`);
  log(`   Clusters processed: ${stats.clustersProcessed}`);
  log(`   Memories consolidated: ${stats.memoriesConsolidated}`);
  log(`   New merged memories: ${stats.newMemories}`);
  log(`   Errors: ${stats.errors}`);
  log(`   Elapsed: ${elapsed}s`);
  log('═══════════════════════════════════════');

  if (JSON_OUT) {
    console.log(JSON.stringify({
      ok: stats.errors === 0,
      dryRun: DRY_RUN,
      before: totalBefore,
      after: DRY_RUN ? totalBefore : totalAfter,
      stats,
      results,
      elapsed: parseFloat(elapsed)
    }, null, 2));
  }
}

main()
  .catch(err => {
    if (JSON_OUT) {
      console.log(JSON.stringify({ ok: false, error: err.message }));
    } else {
      console.error('❌ Fatal:', err.message);
    }
    process.exit(1);
  })
  .finally(() => db.pool.end());
