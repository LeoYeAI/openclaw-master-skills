#!/usr/bin/env node
/**
 * BrainX V5 — Pattern Detector
 *
 * Detects recurring patterns in memories by clustering similar embeddings
 * and registers them in brainx_patterns.
 *
 * Usage:
 *   node scripts/pattern-detector.js [--days 7] [--min-similarity 0.85] [--verbose]
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const { Pool } = require('pg');

const DATABASE_URL = process.env.DATABASE_URL;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!DATABASE_URL) { console.error('DATABASE_URL is required'); process.exit(1); }
if (!OPENAI_API_KEY) { console.error('OPENAI_API_KEY is required'); process.exit(1); }

const pool = new Pool({ connectionString: DATABASE_URL });

// --- CLI args ---
function parseArgs() {
  const argv = process.argv.slice(2);
  const args = { days: 7, minSimilarity: 0.85, verbose: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--days') args.days = parseInt(argv[++i], 10) || 7;
    else if (argv[i] === '--min-similarity') args.minSimilarity = parseFloat(argv[++i]) || 0.85;
    else if (argv[i] === '--verbose') args.verbose = true;
  }
  return args;
}

// --- Fetch recent memories with embeddings ---
async function fetchRecentMemories(days) {
  const cutoff = new Date(Date.now() - days * 86400 * 1000).toISOString();
  const res = await pool.query(
    `SELECT id, type, content, context, tier, agent, importance, embedding,
            category, status, created_at
     FROM brainx_memories
     WHERE created_at >= $1
       AND embedding IS NOT NULL
       AND superseded_by IS NULL
     ORDER BY created_at DESC
     LIMIT 500`,
    [cutoff]
  );
  return res.rows;
}

// --- Cosine similarity between two vectors ---
function cosineSimilarity(a, b) {
  if (!a || !b || a.length !== b.length) return 0;
  let dot = 0, magA = 0, magB = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    magA += a[i] * a[i];
    magB += b[i] * b[i];
  }
  const denom = Math.sqrt(magA) * Math.sqrt(magB);
  return denom === 0 ? 0 : dot / denom;
}

// --- Parse embedding from pg (comes as string "[0.1,0.2,...]") ---
function parseEmbedding(raw) {
  if (Array.isArray(raw)) return raw;
  if (typeof raw === 'string') {
    try {
      // pgvector returns "[0.1,0.2,...]"
      const cleaned = raw.replace(/^\[/, '').replace(/\]$/, '');
      return cleaned.split(',').map(Number);
    } catch { return null; }
  }
  return null;
}

// --- Group memories by semantic similarity (greedy clustering) ---
function clusterMemories(memories, minSimilarity) {
  const embeddings = memories.map(m => ({
    ...m,
    vec: parseEmbedding(m.embedding),
  })).filter(m => m.vec && m.vec.length > 0);

  const assigned = new Set();
  const clusters = [];

  for (let i = 0; i < embeddings.length; i++) {
    if (assigned.has(i)) continue;

    const cluster = [embeddings[i]];
    assigned.add(i);

    for (let j = i + 1; j < embeddings.length; j++) {
      if (assigned.has(j)) continue;
      const sim = cosineSimilarity(embeddings[i].vec, embeddings[j].vec);
      if (sim >= minSimilarity) {
        cluster.push(embeddings[j]);
        assigned.add(j);
      }
    }

    if (cluster.length >= 2) {
      clusters.push(cluster);
    }
  }

  return clusters;
}

// --- Generate a descriptive slug for a cluster ---
function generatePatternKey(cluster) {
  // Use the first memory's content to derive a slug
  const texts = cluster.map(m => m.content.slice(0, 200)).join(' ');
  const lower = texts.toLowerCase();

  // Try to find a dominant theme via keywords
  const themes = [
    { match: /error|fail|crash|bug|exception/i, key: 'error' },
    { match: /deploy|railway|release|production/i, key: 'deploy' },
    { match: /api.?key|token|auth|credential/i, key: 'auth' },
    { match: /config|setup|install|migration/i, key: 'config' },
    { match: /test|spec|coverage|assert/i, key: 'testing' },
    { match: /performance|slow|timeout|latency/i, key: 'perf' },
    { match: /memory|brainx|embedding|vector/i, key: 'memory' },
    { match: /session|agent|spawn|subagent/i, key: 'agent' },
    { match: /git|commit|branch|merge|pr/i, key: 'git' },
    { match: /cron|schedule|heartbeat|periodic/i, key: 'cron' },
    { match: /slack|telegram|discord|message/i, key: 'messaging' },
    { match: /notion|database|postgres|sql/i, key: 'data' },
    { match: /frontend|html|css|react|ui/i, key: 'frontend' },
    { match: /email|smtp|gmail|sendgrid/i, key: 'email' },
    { match: /lead|pipeline|crm|prospect/i, key: 'leads' },
  ];

  let themeKey = 'general';
  for (const t of themes) {
    if (t.match.test(texts)) { themeKey = t.key; break; }
  }

  // Extract a few prominent words for specificity
  const words = lower
    .replace(/[^a-záéíóúñ\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 3 && !STOP_WORDS.has(w));

  // Count frequency
  const freq = {};
  for (const w of words) freq[w] = (freq[w] || 0) + 1;
  const topWords = Object.entries(freq)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 2)
    .map(([w]) => w);

  const suffix = topWords.length > 0 ? `-${topWords.join('-')}` : '';
  return `${themeKey}${suffix}`.slice(0, 60);
}

const STOP_WORDS = new Set([
  'the', 'and', 'for', 'with', 'this', 'that', 'from', 'have', 'been', 'were',
  'are', 'was', 'will', 'can', 'not', 'but', 'all', 'she', 'her', 'his', 'its',
  'they', 'them', 'what', 'when', 'which', 'who', 'how', 'each', 'other',
  'como', 'para', 'que', 'del', 'los', 'las', 'una', 'con', 'por', 'más',
  'pero', 'este', 'esta', 'estos', 'estas', 'todo', 'toda', 'todos',
]);

// --- Calculate impact score ---
function calcImpactScore(cluster) {
  const avgImportance = cluster.reduce((s, m) => s + (m.importance || 5), 0) / cluster.length;
  const recurrence = cluster.length;
  // Scale: importance (1-10) * log2(recurrence+1) for diminishing returns
  return parseFloat((avgImportance * Math.log2(recurrence + 1)).toFixed(2));
}

// --- UPSERT pattern into DB ---
async function upsertPattern(patternKey, cluster, impactScore) {
  // Pick representative: highest importance
  const sorted = [...cluster].sort((a, b) => (b.importance || 5) - (a.importance || 5));
  const representative = sorted[0];
  const latest = cluster.reduce((a, b) =>
    new Date(a.created_at) > new Date(b.created_at) ? a : b
  );

  const now = new Date();

  const res = await pool.query(
    `INSERT INTO brainx_patterns
       (pattern_key, recurrence_count, first_seen, last_seen, impact_score,
        representative_memory_id, last_memory_id, last_category, last_status,
        created_at, updated_at)
     VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $10)
     ON CONFLICT (pattern_key) DO UPDATE SET
       recurrence_count = brainx_patterns.recurrence_count + $2,
       last_seen = $4,
       impact_score = GREATEST(brainx_patterns.impact_score, $5),
       last_memory_id = $7,
       last_category = COALESCE($8, brainx_patterns.last_category),
       last_status = COALESCE($9, brainx_patterns.last_status),
       updated_at = $10
     RETURNING (xmax = 0) AS is_insert`,
    [
      patternKey,
      cluster.length,
      representative.created_at || now,
      latest.created_at || now,
      impactScore,
      representative.id,
      latest.id,
      latest.category || null,
      latest.status || null,
      now,
    ]
  );

  return res.rows[0]?.is_insert;
}

// --- Main ---
async function main() {
  const args = parseArgs();
  const result = { patterns_found: 0, new_patterns: 0, updated_patterns: 0, errors: [] };

  try {
    const memories = await fetchRecentMemories(args.days);

    if (args.verbose) process.stderr.write(`Fetched ${memories.length} memories from last ${args.days} days\n`);

    if (memories.length < 2) {
      console.log(JSON.stringify(result, null, 2));
      await pool.end();
      return;
    }

    const clusters = clusterMemories(memories, args.minSimilarity);
    result.patterns_found = clusters.length;

    if (args.verbose) process.stderr.write(`Found ${clusters.length} clusters (min similarity ${args.minSimilarity})\n`);

    for (const cluster of clusters) {
      try {
        const patternKey = generatePatternKey(cluster);
        const impactScore = calcImpactScore(cluster);

        if (args.verbose) {
          process.stderr.write(`  Pattern: ${patternKey} (${cluster.length} memories, impact ${impactScore})\n`);
        }

        const isNew = await upsertPattern(patternKey, cluster, impactScore);

        if (isNew) result.new_patterns++;
        else result.updated_patterns++;
      } catch (err) {
        result.errors.push((err.message || String(err)).slice(0, 200));
      }
    }
  } catch (err) {
    result.errors.push((err.message || String(err)).slice(0, 200));
  }

  await pool.end();
  console.log(JSON.stringify(result, null, 2));
}

main().catch(err => {
  console.error(err.stack || err.message);
  process.exit(1);
});
