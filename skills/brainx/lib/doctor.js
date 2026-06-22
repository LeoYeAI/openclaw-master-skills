/**
 * BrainX Doctor — Diagnostic Report
 * Read-only checks on BrainX health, schema, data integrity, and stats.
 * Output styled with Unicode box-drawing (clack/prompts style).
 */

const fs = require('fs');
const path = require('path');

// ─── Expected schema definitions ───

const EXPECTED_COLUMNS = [
  'id', 'type', 'content', 'context', 'tier', 'agent', 'importance',
  'embedding', 'created_at', 'last_accessed', 'access_count', 'source_session',
  'superseded_by', 'tags', 'status', 'category', 'pattern_key',
  'recurrence_count', 'first_seen', 'last_seen', 'resolved_at',
  'promoted_to', 'resolution_notes',
  'source_kind', 'source_path', 'confidence_score', 'expires_at', 'sensitivity'
];

const EXPECTED_CONSTRAINTS = [
  'brainx_memories_type_check',
  'brainx_memories_category_check',
  'brainx_memories_source_kind_check',
  'brainx_memories_sensitivity_check',
  'brainx_memories_confidence_score_check'
];

const EXPECTED_INDEXES = [
  'idx_mem_expires_at',
  'idx_mem_sensitivity',
  'idx_mem_embedding',
  'idx_mem_tier',
  'idx_mem_context',
  'idx_mem_tags',
  'idx_mem_status',
  'idx_mem_category',
  'idx_mem_pattern_key'
];

const HOOK_PATH = '/home/clawd/.openclaw/hooks/brainx-auto-inject/handler.js';

// ─── Check functions ───
// Each returns { status: 'ok'|'warn'|'fail'|'info', label, detail, verbose? }

async function checkDbConnection(db) {
  try {
    const res = await db.query("SELECT current_database() AS dbname, inet_server_addr() AS host");
    const row = res.rows[0] || {};
    const dbname = row.dbname || 'unknown';
    const host = row.host || 'localhost';
    return { status: 'ok', label: 'Connection', detail: `OK (${dbname}@${host})` };
  } catch (err) {
    return { status: 'fail', label: 'Connection', detail: err.message };
  }
}

async function checkPgvector(db) {
  try {
    const res = await db.query("SELECT extversion FROM pg_extension WHERE extname = 'vector'");
    if (res.rows.length === 0) {
      return { status: 'fail', label: 'pgvector', detail: 'not installed' };
    }
    return { status: 'ok', label: 'pgvector', detail: `v${res.rows[0].extversion}` };
  } catch (err) {
    return { status: 'fail', label: 'pgvector', detail: err.message };
  }
}

async function checkTables(db) {
  try {
    const res = await db.query(
      "SELECT count(*)::int AS n FROM information_schema.tables WHERE table_schema='public' AND table_name LIKE 'brainx_%'"
    );
    const n = res.rows[0]?.n ?? 0;
    return { status: n > 0 ? 'ok' : 'fail', label: 'Tables', detail: `${n} found` };
  } catch (err) {
    return { status: 'fail', label: 'Tables', detail: err.message };
  }
}

async function checkSchemaColumns(db) {
  try {
    const res = await db.query(
      `SELECT column_name FROM information_schema.columns
       WHERE table_schema = 'public' AND table_name = 'brainx_memories'`
    );
    const existing = new Set(res.rows.map(r => r.column_name));
    const missing = EXPECTED_COLUMNS.filter(c => !existing.has(c));
    const found = EXPECTED_COLUMNS.length - missing.length;
    if (missing.length === 0) {
      return { status: 'ok', label: 'Columns', detail: `${found}/${EXPECTED_COLUMNS.length}` };
    }
    return {
      status: 'warn', label: 'Columns',
      detail: `${found}/${EXPECTED_COLUMNS.length} (missing: ${missing.join(', ')})`,
      verbose: missing.map(c => `missing column: ${c}`)
    };
  } catch (err) {
    return { status: 'fail', label: 'Columns', detail: err.message };
  }
}

async function checkSchemaConstraints(db) {
  try {
    const res = await db.query(
      `SELECT conname FROM pg_constraint
       WHERE conrelid = 'brainx_memories'::regclass AND contype = 'c'`
    );
    const existing = new Set(res.rows.map(r => r.conname));
    const missing = EXPECTED_CONSTRAINTS.filter(c => !existing.has(c));
    const total = EXPECTED_CONSTRAINTS.length;
    const found = total - missing.length;
    if (missing.length === 0) {
      return { status: 'ok', label: 'Constraints', detail: `${found}/${total}` };
    }
    return {
      status: 'warn', label: 'Constraints',
      detail: `${found}/${total} (missing: ${missing.length})`,
      verbose: missing.map(c => `missing: ${c}`)
    };
  } catch (err) {
    return { status: 'fail', label: 'Constraints', detail: err.message };
  }
}

async function checkIndexes(db) {
  try {
    const res = await db.query(`SELECT indexname FROM pg_indexes WHERE tablename = 'brainx_memories'`);
    const existing = new Set(res.rows.map(r => r.indexname));
    const missing = EXPECTED_INDEXES.filter(i => !existing.has(i));
    const found = EXPECTED_INDEXES.length - missing.length;
    if (missing.length === 0) {
      return { status: 'ok', label: 'Indexes', detail: `${found} found` };
    }
    return {
      status: 'warn', label: 'Indexes',
      detail: `${found} found (missing ${missing.length})`,
      verbose: missing.map(i => `missing: ${i}`)
    };
  } catch (err) {
    return { status: 'fail', label: 'Indexes', detail: err.message };
  }
}

async function checkOrphanedRefs(db) {
  try {
    const res = await db.query(
      `SELECT m.id FROM brainx_memories m
       WHERE m.superseded_by IS NOT NULL
         AND m.superseded_by != 'expired'
         AND NOT EXISTS (SELECT 1 FROM brainx_memories t WHERE t.id = m.superseded_by)`
    );
    const count = res.rows.length;
    if (count === 0) return { status: 'ok', label: 'Orphaned references', detail: '0' };
    return {
      status: 'warn', label: 'Orphaned references',
      detail: `${count} orphaned superseded_by refs`,
      verbose: res.rows.map(r => `orphan: ${r.id}`)
    };
  } catch (err) {
    return { status: 'fail', label: 'Orphaned references', detail: err.message };
  }
}

async function checkNullEmbeddings(db) {
  try {
    const res = await db.query(
      `SELECT id FROM brainx_memories WHERE embedding IS NULL AND superseded_by IS NULL`
    );
    const count = res.rows.length;
    if (count === 0) return { status: 'ok', label: 'Null embeddings', detail: '0' };
    return {
      status: 'warn', label: 'Null embeddings',
      detail: `${count} memories without embeddings`,
      verbose: res.rows.slice(0, 20).map(r => `no embedding: ${r.id}`)
    };
  } catch (err) {
    return { status: 'fail', label: 'Null embeddings', detail: err.message };
  }
}

async function checkExpiredMemories(db) {
  try {
    const colCheck = await db.query(
      `SELECT 1 FROM information_schema.columns
       WHERE table_name = 'brainx_memories' AND column_name = 'expires_at'`
    );
    if (colCheck.rows.length === 0) {
      return { status: 'info', label: 'Expired memories', detail: 'skipped (no expires_at column)' };
    }
    const res = await db.query(
      `SELECT id FROM brainx_memories
       WHERE expires_at IS NOT NULL AND expires_at < NOW() AND superseded_by IS NULL`
    );
    const count = res.rows.length;
    if (count === 0) return { status: 'ok', label: 'Expired memories', detail: '0' };
    return {
      status: 'fail', label: 'Expired memories',
      detail: `${count} need cleanup`,
      verbose: res.rows.slice(0, 20).map(r => `expired: ${r.id}`)
    };
  } catch (err) {
    return { status: 'fail', label: 'Expired memories', detail: err.message };
  }
}

async function checkStaleMemories(db) {
  try {
    const res = await db.query(
      `SELECT id, tier FROM brainx_memories
       WHERE tier IN ('hot', 'warm') AND superseded_by IS NULL
         AND last_accessed < NOW() - INTERVAL '30 days'`
    );
    const count = res.rows.length;
    if (count === 0) return { status: 'ok', label: 'Stale memories', detail: '0 stale hot/warm' };
    return {
      status: 'warn', label: 'Stale memories',
      detail: `${count} hot/warm not accessed in >30d`,
      verbose: res.rows.slice(0, 20).map(r => `stale ${r.tier}: ${r.id}`)
    };
  } catch (err) {
    return { status: 'fail', label: 'Stale memories', detail: err.message };
  }
}

async function checkLegacyProvenance(db) {
  try {
    const colCheck = await db.query(
      `SELECT 1 FROM information_schema.columns
       WHERE table_name = 'brainx_memories' AND column_name = 'source_kind'`
    );
    if (colCheck.rows.length === 0) {
      return { status: 'warn', label: 'Legacy memories', detail: 'source_kind column missing (run migrations)' };
    }
    const res = await db.query(
      `SELECT COUNT(*)::int AS cnt FROM brainx_memories
       WHERE source_kind IS NULL AND superseded_by IS NULL`
    );
    const count = res.rows[0]?.cnt || 0;
    if (count === 0) return { status: 'ok', label: 'Legacy memories', detail: 'all have source_kind' };
    return { status: 'warn', label: 'Legacy memories', detail: `${count} without source_kind` };
  } catch (err) {
    return { status: 'fail', label: 'Legacy memories', detail: err.message };
  }
}

async function checkDuplicateCandidates(db) {
  try {
    const countRes = await db.query(
      `SELECT COUNT(*)::int AS cnt FROM brainx_memories
       WHERE embedding IS NOT NULL AND superseded_by IS NULL`
    );
    if ((countRes.rows[0]?.cnt || 0) < 2) {
      return { status: 'ok', label: 'Duplicates', detail: 'not enough memories to check' };
    }
    const res = await db.query(
      `WITH recent AS (
         SELECT id, embedding FROM brainx_memories
         WHERE embedding IS NOT NULL AND superseded_by IS NULL
         ORDER BY created_at DESC LIMIT 100
       )
       SELECT a.id AS id_a, b.id AS id_b,
              1 - (a.embedding <=> b.embedding) AS similarity
       FROM recent a, recent b
       WHERE a.id < b.id AND 1 - (a.embedding <=> b.embedding) > 0.95
       ORDER BY similarity DESC LIMIT 20`
    );
    const count = res.rows.length;
    if (count === 0) return { status: 'ok', label: 'Duplicates', detail: '0 pairs >0.95 in sample' };
    return {
      status: 'warn', label: 'Duplicates',
      detail: `${count} high-similarity pairs in last 100`,
      verbose: res.rows.map(r => `${r.id_a} ↔ ${r.id_b} (${Number(r.similarity).toFixed(4)})`)
    };
  } catch (err) {
    return { status: 'fail', label: 'Duplicates', detail: err.message };
  }
}

async function checkTierDistribution(db) {
  try {
    const res = await db.query(
      `SELECT COALESCE(tier, 'unknown') AS tier, COUNT(*)::int AS cnt
       FROM brainx_memories WHERE superseded_by IS NULL GROUP BY 1 ORDER BY 2 DESC`
    );
    return { status: 'info', label: 'tier_distribution', detail: res.rows };
  } catch (err) {
    return { status: 'fail', label: 'tier_distribution', detail: err.message };
  }
}

async function checkTypeDistribution(db) {
  try {
    const res = await db.query(
      `SELECT COALESCE(type, 'unknown') AS type, COUNT(*)::int AS cnt
       FROM brainx_memories WHERE superseded_by IS NULL GROUP BY 1 ORDER BY 2 DESC`
    );
    return { status: 'info', label: 'type_distribution', detail: res.rows };
  } catch (err) {
    return { status: 'fail', label: 'type_distribution', detail: err.message };
  }
}

async function checkTotalMemories(db) {
  try {
    const res = await db.query(
      `SELECT COUNT(*)::int AS cnt FROM brainx_memories WHERE superseded_by IS NULL`
    );
    return { status: 'info', label: 'total_active', detail: res.rows[0]?.cnt || 0 };
  } catch (err) {
    return { status: 'fail', label: 'total_active', detail: err.message };
  }
}

function checkHookStatus() {
  const exists = fs.existsSync(HOOK_PATH);
  return { status: exists ? 'ok' : 'warn', label: 'Hook deployed', detail: exists ? 'OK' : 'handler.js not found' };
}

function checkCliAvailable() {
  const cliPath = path.join(__dirname, 'cli.js');
  const exists = fs.existsSync(cliPath);
  return { status: exists ? 'ok' : 'warn', label: 'CLI available', detail: exists ? 'OK' : 'cli.js not found' };
}

function checkCronJobs() {
  const cronJobsPath = '/home/clawd/.openclaw/cron/jobs.json';
  try {
    const raw = fs.readFileSync(cronJobsPath, 'utf8');
    const data = JSON.parse(raw);
    const jobs = data.jobs || [];

    const normalize = (job) => ((job.name || '') + ' ' + ((job.payload && job.payload.message) || '')).toLowerCase();

    // Current production architecture: a single consolidated OpenClaw cron orchestrates
    // the BrainX V5 daily core pipeline. Legacy component jobs may remain present but
    // disabled after consolidation and should not be required for a healthy system.
    const consolidated = jobs.find(j => {
      const combined = normalize(j);
      return combined.includes('brainx daily core pipeline v5') ||
             (combined.includes('brainx') && combined.includes('daily core pipeline'));
    });

    if (consolidated) {
      const detail = consolidated.enabled
        ? 'consolidated pipeline detected: BrainX Daily Core Pipeline V5 enabled'
        : 'consolidated pipeline detected but disabled: BrainX Daily Core Pipeline V5';
      return {
        status: consolidated.enabled ? 'ok' : 'fail',
        label: 'Cron jobs',
        detail,
      };
    }

    // Backward-compatible fallback for older split-cron deployments.
    const keywords = [
      { name: 'Memory Distiller', patterns: ['distiller'] },
      { name: 'Memory Bridge', patterns: ['memory bridge'] },
      { name: 'Lifecycle Daily', patterns: ['lifecycle'] },
      { name: 'Session Harvester', patterns: ['harvester'] },
      { name: 'Cross-Agent Learning', patterns: ['cross-agent'] },
      { name: 'Contradiction Detector', patterns: ['contradiction'] }
    ];

    let found = 0;
    let enabled = 0;
    const missing = [];

    for (const expected of keywords) {
      const match = jobs.find(j => {
        const combined = normalize(j);
        return expected.patterns.some(p => combined.includes(p));
      });
      if (match) {
        found++;
        if (match.enabled) enabled++;
      } else {
        missing.push(expected.name);
      }
    }

    const detail = `${found}/6 legacy component jobs registered, ${enabled} enabled` + (missing.length > 0 ? ` (missing: ${missing.join(', ')})` : '');

    if (found >= 5 && enabled >= 5) return { status: 'ok', label: 'Cron jobs', detail };
    if (missing.length >= 3) return { status: 'fail', label: 'Cron jobs', detail };
    return { status: 'warn', label: 'Cron jobs', detail };
  } catch (err) {
    return { status: 'warn', label: 'Cron jobs', detail: 'cannot read cron config' };
  }
}

async function checkLastMemory(db) {
  try {
    const res = await db.query(
      `SELECT created_at FROM brainx_memories ORDER BY created_at DESC LIMIT 1`
    );
    if (res.rows.length === 0) {
      return { status: 'fail', label: 'Last memory', detail: 'no memories found' };
    }
    const lastAt = new Date(res.rows[0].created_at);
    const hoursAgo = (Date.now() - lastAt.getTime()) / (1000 * 60 * 60);

    let detail;
    if (hoursAgo < 48) {
      detail = `last: ${Math.round(hoursAgo)}h ago`;
    } else {
      detail = `last: ${Math.round(hoursAgo / 24)} days ago`;
    }

    if (hoursAgo < 24) return { status: 'ok', label: 'Last memory', detail };
    if (hoursAgo < 72) return { status: 'warn', label: 'Last memory', detail };
    return { status: 'fail', label: 'Last memory', detail };
  } catch (err) {
    return { status: 'fail', label: 'Last memory', detail: err.message };
  }
}

async function checkEmbeddingDimensions(db) {
  try {
    const res = await db.query(
      `SELECT DISTINCT array_length(embedding::real[], 1) AS dim
       FROM brainx_memories
       WHERE embedding IS NOT NULL
       LIMIT 10`
    );
    if (res.rows.length === 0) {
      return { status: 'ok', label: 'Embedding dims', detail: 'no embeddings to check' };
    }
    const dims = res.rows.map(r => r.dim).filter(d => d != null);
    if (dims.length === 0) {
      return { status: 'ok', label: 'Embedding dims', detail: 'no dimensions detected' };
    }
    if (dims.length === 1) {
      return { status: 'ok', label: 'Embedding dims', detail: `uniform: ${dims[0]}d` };
    }
    return { status: 'warn', label: 'Embedding dims', detail: `mixed: ${dims.map(d => d + 'd').join(', ')}` };
  } catch (err) {
    return { status: 'fail', label: 'Embedding dims', detail: err.message };
  }
}

function checkBackupFreshness() {
  const backupDirs = [
    '/home/clawd/.openclaw/skills/brainx-v5/backups/',
    '/home/clawd/backups/'
  ];
  const extensions = ['.sql', '.dump', '.pg_dump'];

  let newestMtime = null;
  let newestFile = null;

  for (const dir of backupDirs) {
    try {
      const entries = fs.readdirSync(dir, { withFileTypes: true, recursive: true });
      for (const entry of entries) {
        if (!entry.isFile()) continue;
        const ext = path.extname(entry.name);
        if (!extensions.includes(ext)) continue;
        const fullPath = path.join(entry.parentPath || entry.path || dir, entry.name);
        try {
          const stat = fs.statSync(fullPath);
          if (!newestMtime || stat.mtime > newestMtime) {
            newestMtime = stat.mtime;
            newestFile = fullPath;
          }
        } catch (_) { /* skip inaccessible files */ }
      }
    } catch (_) { /* dir doesn't exist */ }
  }

  if (!newestMtime) {
    return { status: 'warn', label: 'Backup freshness', detail: 'no backup files found' };
  }

  const daysAgo = (Date.now() - newestMtime.getTime()) / (1000 * 60 * 60 * 24);
  const detail = `${Math.round(daysAgo)}d ago (${path.basename(newestFile)})`;

  if (daysAgo < 7) return { status: 'ok', label: 'Backup freshness', detail };
  if (daysAgo < 30) return { status: 'warn', label: 'Backup freshness', detail };
  return { status: 'fail', label: 'Backup freshness', detail };
}

// ─── Run all checks ───

async function runAllChecks(db) {
  const database = [];
  database.push(await checkDbConnection(db));
  if (database[0].status === 'fail') {
    return { database, schema: [], integrity: [], provenance: [], distribution: {}, infra: [], passed: 0, warnings: 0, failures: 1 };
  }
  database.push(await checkPgvector(db));
  database.push(await checkTables(db));

  const schema = [];
  schema.push(await checkSchemaColumns(db));
  schema.push(await checkSchemaConstraints(db));
  schema.push(await checkIndexes(db));

  const integrity = [];
  integrity.push(await checkOrphanedRefs(db));
  integrity.push(await checkNullEmbeddings(db));
  integrity.push(await checkExpiredMemories(db));
  integrity.push(await checkStaleMemories(db));
  integrity.push(await checkLastMemory(db));
  integrity.push(await checkEmbeddingDimensions(db));

  const provenance = [];
  provenance.push(await checkLegacyProvenance(db));
  provenance.push(await checkDuplicateCandidates(db));

  const tierDist = await checkTierDistribution(db);
  const typeDist = await checkTypeDistribution(db);
  const totalMem = await checkTotalMemories(db);

  const infra = [];
  infra.push(checkHookStatus());
  infra.push(checkCliAvailable());
  infra.push(checkCronJobs());
  infra.push(checkBackupFreshness());

  const all = [...database, ...schema, ...integrity, ...provenance, ...infra];
  const passed = all.filter(r => r.status === 'ok').length;
  const warnings = all.filter(r => r.status === 'warn').length;
  const failures = all.filter(r => r.status === 'fail').length;

  return { database, schema, integrity, provenance, distribution: { tiers: tierDist, types: typeDist, total: totalMem }, infra, passed, warnings, failures };
}

// ─── Unicode box formatting (clack style) ───

const BANNER = `
 ██████╗ ██████╗  █████╗ ██╗███╗   ██╗██╗  ██╗
 ██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║╚██╗██╔╝
 ██████╔╝██████╔╝███████║██║██╔██╗ ██║ ╚███╔╝
 ██╔══██╗██╔══██╗██╔══██║██║██║╚██╗██║ ██╔██╗
 ██████╔╝██║  ██║██║  ██║██║██║ ╚████║██╔╝ ██╗
 ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝`;

const SYM = { ok: '✓', warn: '⚠', fail: '✗' };

function dotLine(label, detail, maxLabelLen) {
  const pad = maxLabelLen - label.length;
  const dots = ' ' + '.'.repeat(Math.max(1, pad + 2)) + ' ';
  return `${label}${dots}${detail}`;
}

function buildSection(title, checks, verbose, W) {
  const maxLabel = Math.max(...checks.map(c => c.label.length), 10);

  // Pre-compute all content lines to find actual max width
  const contentLines = [];
  for (const c of checks) {
    const sym = SYM[c.status] || ' ';
    const prefix = c.status === 'info' ? ' ' : `${sym}`;
    const text = dotLine(c.label, c.detail, maxLabel);
    contentLines.push({ line: `  ${prefix} ${text}`, check: c });
  }

  // Effective width = max of W and longest line
  const maxLine = Math.max(W, ...contentLines.map(cl => cl.line.length + 2));

  const titleBar = `◇  ${title} ` + '─'.repeat(Math.max(1, maxLine - title.length - 4)) + '╮';
  const lines = [];
  lines.push(`│`);
  lines.push(titleBar);
  lines.push(`│${' '.repeat(maxLine + 1)}│`);

  for (const cl of contentLines) {
    const pad = maxLine - cl.line.length;
    lines.push(`│${cl.line}${' '.repeat(Math.max(1, pad + 1))}│`);
    if (verbose && cl.check.verbose) {
      for (const v of cl.check.verbose) {
        const vl = `      ${v}`;
        lines.push(`│${vl}${' '.repeat(Math.max(1, maxLine - vl.length + 1))}│`);
      }
    }
  }
  lines.push(`│${' '.repeat(maxLine + 1)}│`);
  lines.push(`├${'─'.repeat(maxLine + 1)}╯`);

  return lines;
}

function buildDistributionSection(distribution, W) {
  // Pre-compute all content lines to find max width
  const contentLines = [];

  if (distribution.tiers && Array.isArray(distribution.tiers.detail)) {
    const tierStr = distribution.tiers.detail.map(r => `${r.tier}:${r.cnt}`).join('  ');
    contentLines.push(`  Tiers: ${tierStr}`);
  }

  if (distribution.types && Array.isArray(distribution.types.detail)) {
    const parts = distribution.types.detail.map(r => `${r.type}:${r.cnt}`);
    // Split into rows of 4 to keep lines short
    for (let i = 0; i < parts.length; i += 4) {
      const chunk = parts.slice(i, i + 4).join('  ');
      const prefix = i === 0 ? '  Types: ' : '         ';
      contentLines.push(`${prefix}${chunk}`);
    }
  }

  if (distribution.total) {
    contentLines.push(`  Total active: ${distribution.total.detail}`);
  }

  const maxLine = Math.max(W, ...contentLines.map(l => l.length + 2));

  const titleBar = `◇  Distribution ` + '─'.repeat(Math.max(1, maxLine - 16)) + '╮';
  const lines = [];
  lines.push(`│`);
  lines.push(titleBar);
  lines.push(`│${' '.repeat(maxLine + 1)}│`);

  for (const cl of contentLines) {
    const pad = maxLine - cl.length;
    lines.push(`│${cl}${' '.repeat(Math.max(1, pad + 1))}│`);
  }

  lines.push(`│${' '.repeat(maxLine + 1)}│`);
  lines.push(`├${'─'.repeat(maxLine + 1)}╯`);

  return lines;
}

function formatReport(report, verbose = false) {
  const W = 58; // inner content width
  const out = [];

  out.push(BANNER);
  out.push('                    🧠 DOCTOR 🧠');
  out.push('');
  out.push('┌  BrainX Doctor');

  // Database section
  out.push(...buildSection('Database', report.database, verbose, W));

  // Schema section
  if (report.schema.length) {
    out.push(...buildSection('Schema', report.schema, verbose, W));
  }

  // Data Integrity section
  if (report.integrity.length) {
    out.push(...buildSection('Data Integrity', report.integrity, verbose, W));
  }

  // Provenance section
  if (report.provenance.length) {
    out.push(...buildSection('Provenance', report.provenance, verbose, W));
  }

  // Distribution section
  if (report.distribution) {
    out.push(...buildDistributionSection(report.distribution, W));
  }

  // Infrastructure section
  if (report.infra.length) {
    out.push(...buildSection('Infrastructure', report.infra, verbose, W));
  }

  // Footer
  out.push('│');

  const parts = [];
  if (report.passed > 0) parts.push(`${report.passed} passed`);
  if (report.warnings > 0) parts.push(`${report.warnings} warnings`);
  if (report.failures > 0) parts.push(`${report.failures} failures`);
  out.push(`└  Done — ${parts.join(', ')}`);

  if (report.failures > 0 || report.warnings > 0) {
    out.push(`   Run \`brainx --fix\` to auto-repair.`);
  }

  return out.join('\n');
}

function formatReportJson(report) {
  const allChecks = [...report.database, ...report.schema, ...report.integrity, ...report.provenance, ...report.infra];

  // Include distribution data
  const dist = {};
  if (report.distribution) {
    if (report.distribution.tiers && Array.isArray(report.distribution.tiers.detail)) {
      dist.tiers = report.distribution.tiers.detail;
    }
    if (report.distribution.types && Array.isArray(report.distribution.types.detail)) {
      dist.types = report.distribution.types.detail;
    }
    if (report.distribution.total) {
      dist.total_active = report.distribution.total.detail;
    }
  }

  return JSON.stringify({
    ok: report.failures === 0,
    passed: report.passed,
    warnings: report.warnings,
    failures: report.failures,
    checks: allChecks.map(r => ({
      label: r.label,
      status: r.status,
      detail: r.detail,
      verbose: r.verbose || null
    })),
    distribution: dist
  }, null, 2);
}

// ─── Main entry point ───

async function cmdDoctor(args, deps = {}) {
  let db;
  try {
    db = deps.db || require('./db');
  } catch (err) {
    console.log(BANNER);
    console.log('                    🧠 DOCTOR 🧠');
    console.log('');
    console.log('┌  BrainX Doctor');
    console.log('│');
    console.log('└  ✗ Database connection failed: ' + err.message);
    return;
  }

  const report = await runAllChecks(db);

  if (args.json) {
    console.log(formatReportJson(report));
  } else {
    console.log(formatReport(report, args.verbose || false));
  }
}

module.exports = {
  runAllChecks,
  formatReport,
  formatReportJson,
  cmdDoctor,
  EXPECTED_COLUMNS,
  EXPECTED_CONSTRAINTS,
  EXPECTED_INDEXES
};
