/**
 * BrainX Fix — Auto-Repair
 * Fixes issues detected by `brainx doctor`.
 * Output styled with Unicode box-drawing (clack/prompts style).
 */

const fs = require('fs');
const path = require('path');

const MIGRATIONS_DIR = path.join(__dirname, '..', 'sql', 'migrations');

// ─── Step 1: Apply missing migrations ───

async function applyMigrations(db, opts = {}) {
  const { dryRun = false } = opts;

  let files;
  try {
    files = fs.readdirSync(MIGRATIONS_DIR).filter(f => f.endsWith('.sql')).sort();
  } catch (err) {
    return { label: 'Migrations', status: 'warn', detail: err.message };
  }

  if (files.length === 0) {
    return { label: 'Migrations', status: 'ok', detail: 'no migration files found' };
  }

  const [colRes, conRes] = await Promise.all([
    db.query(`SELECT column_name FROM information_schema.columns
              WHERE table_schema = 'public' AND table_name = 'brainx_memories'`),
    db.query(`SELECT conname FROM pg_constraint
              WHERE conrelid = 'brainx_memories'::regclass`)
  ]);
  const existingCols = new Set(colRes.rows.map(r => r.column_name));
  const existingCons = new Set(conRes.rows.map(r => r.conname));

  const migrationChecks = {
    '005-sync-schema-production.sql': () =>
      existingCons.has('brainx_memories_type_check') && existingCons.has('brainx_memories_category_check'),
    '006-provenance.sql': () =>
      existingCols.has('source_kind') && existingCols.has('sensitivity') && existingCols.has('expires_at')
  };

  const applied = [];
  for (const file of files) {
    const checkFn = migrationChecks[file];
    if (checkFn && checkFn()) continue;

    if (dryRun) { applied.push(file); continue; }

    const sql = fs.readFileSync(path.join(MIGRATIONS_DIR, file), 'utf8');
    try {
      await db.query(sql);
      applied.push(file);
    } catch (err) {
      return { label: 'Migrations', status: 'fail', detail: `${file} — ${err.message}` };
    }
  }

  if (applied.length === 0) {
    return { label: 'Migrations', status: 'ok', detail: 'nothing to apply' };
  }
  const prefix = dryRun ? 'would apply' : 'applied';
  return {
    label: 'Migrations', status: 'fixed',
    detail: `${prefix} ${applied.length}: ${applied.join(', ')}`,
    verbose: applied.map(f => `${dryRun ? 'would apply' : 'applied'}: ${f}`)
  };
}

// ─── Step 2: Clean expired memories ───

async function cleanExpired(db, opts = {}) {
  const { dryRun = false } = opts;

  const colCheck = await db.query(
    `SELECT 1 FROM information_schema.columns
     WHERE table_name = 'brainx_memories' AND column_name = 'expires_at'`
  );
  if (colCheck.rows.length === 0) {
    return { label: 'Expired cleanup', status: 'ok', detail: 'no expires_at column' };
  }

  const countRes = await db.query(
    `SELECT COUNT(*)::int AS cnt FROM brainx_memories
     WHERE expires_at IS NOT NULL AND expires_at < NOW() AND superseded_by IS NULL`
  );
  const count = countRes.rows[0]?.cnt || 0;

  if (count === 0) return { label: 'Expired cleanup', status: 'ok', detail: 'no expired memories' };
  if (dryRun) return { label: 'Expired cleanup', status: 'fixed', detail: `would archive ${count} memories` };

  await db.query(
    `UPDATE brainx_memories SET tier = 'archive', superseded_by = 'expired'
     WHERE expires_at IS NOT NULL AND expires_at < NOW() AND superseded_by IS NULL`
  );
  return { label: 'Expired cleanup', status: 'fixed', detail: `archived ${count} memories` };
}

// ─── Step 3: Fix orphaned superseded_by ───

async function fixOrphans(db, opts = {}) {
  const { dryRun = false } = opts;

  const res = await db.query(
    `SELECT m.id FROM brainx_memories m
     WHERE m.superseded_by IS NOT NULL AND m.superseded_by != 'expired'
       AND NOT EXISTS (SELECT 1 FROM brainx_memories t WHERE t.id = m.superseded_by)`
  );
  const count = res.rows.length;

  if (count === 0) return { label: 'Orphaned refs', status: 'ok', detail: 'no orphans found' };
  if (dryRun) {
    return { label: 'Orphaned refs', status: 'fixed', detail: `would fix ${count} refs`,
      verbose: res.rows.map(r => `would fix: ${r.id}`) };
  }

  await db.query(`UPDATE brainx_memories SET superseded_by = NULL WHERE id = ANY($1)`,
    [res.rows.map(r => r.id)]);
  return { label: 'Orphaned refs', status: 'fixed', detail: `cleared ${count} refs` };
}

// ─── Step 4: Backfill legacy provenance ───

async function backfillProvenance(db, opts = {}) {
  const { dryRun = false } = opts;

  const colCheck = await db.query(
    `SELECT 1 FROM information_schema.columns
     WHERE table_name = 'brainx_memories' AND column_name = 'source_kind'`
  );
  if (colCheck.rows.length === 0) {
    return { label: 'Legacy provenance', status: 'ok', detail: 'source_kind column not present' };
  }

  const countRes = await db.query(
    `SELECT COUNT(*)::int AS cnt FROM brainx_memories
     WHERE source_kind IS NULL AND superseded_by IS NULL`
  );
  const count = countRes.rows[0]?.cnt || 0;

  if (count === 0) return { label: 'Legacy provenance', status: 'ok', detail: 'all have source_kind' };
  if (dryRun) return { label: 'Legacy provenance', status: 'fixed', detail: `would backfill ${count} memories` };

  await db.query(
    `UPDATE brainx_memories SET source_kind = 'markdown_import'
     WHERE source_kind IS NULL AND superseded_by IS NULL`
  );
  return { label: 'Legacy provenance', status: 'fixed', detail: `backfilled ${count} memories` };
}

// ─── Step 5: Demote stale tiers ───

async function demoteStaleTiers(db, opts = {}) {
  const { dryRun = false } = opts;

  const hotRes = await db.query(
    `SELECT COUNT(*)::int AS cnt FROM brainx_memories
     WHERE tier = 'hot' AND superseded_by IS NULL AND last_accessed < NOW() - INTERVAL '60 days'`
  );
  const hotCount = hotRes.rows[0]?.cnt || 0;

  const warmRes = await db.query(
    `SELECT COUNT(*)::int AS cnt FROM brainx_memories
     WHERE tier = 'warm' AND superseded_by IS NULL AND last_accessed < NOW() - INTERVAL '90 days'`
  );
  const warmCount = warmRes.rows[0]?.cnt || 0;

  if (hotCount === 0 && warmCount === 0) {
    return { label: 'Stale demotion', status: 'ok', detail: 'no stale tiers' };
  }

  const parts = [];
  if (hotCount > 0) parts.push(`${hotCount} hot→warm`);
  if (warmCount > 0) parts.push(`${warmCount} warm→cold`);

  if (dryRun) return { label: 'Stale demotion', status: 'fixed', detail: `would demote ${parts.join(', ')}` };

  if (hotCount > 0) {
    await db.query(`UPDATE brainx_memories SET tier = 'warm'
      WHERE tier = 'hot' AND superseded_by IS NULL AND last_accessed < NOW() - INTERVAL '60 days'`);
  }
  if (warmCount > 0) {
    await db.query(`UPDATE brainx_memories SET tier = 'cold'
      WHERE tier = 'warm' AND superseded_by IS NULL AND last_accessed < NOW() - INTERVAL '90 days'`);
  }
  return { label: 'Stale demotion', status: 'fixed', detail: parts.join(', ') };
}

// ─── Step 6: Regenerate null embeddings ───

async function regenerateEmbeddings(db, opts = {}) {
  const { dryRun = false, skipEmbeddings = false } = opts;

  if (skipEmbeddings) {
    return { label: 'Null embeddings', status: 'ok', detail: 'skipped (--skip-embeddings)' };
  }

  const res = await db.query(
    `SELECT id, type, content, context FROM brainx_memories
     WHERE embedding IS NULL AND superseded_by IS NULL
     ORDER BY created_at DESC LIMIT 20`
  );

  if (res.rows.length === 0) return { label: 'Null embeddings', status: 'ok', detail: 'all have embeddings' };
  if (dryRun) {
    return { label: 'Null embeddings', status: 'fixed', detail: `would regenerate ${res.rows.length}`,
      verbose: res.rows.map(r => `would embed: ${r.id}`) };
  }

  let embed;
  try { embed = require('./openai-rag').embed; }
  catch (err) { return { label: 'Null embeddings', status: 'fail', detail: `cannot load embed: ${err.message}` }; }

  let success = 0, failures = 0;
  const errors = [];
  for (const row of res.rows) {
    try {
      const text = `${row.type}: ${row.content} [context: ${row.context || ''}]`;
      const embedding = await embed(text);
      await db.query(`UPDATE brainx_memories SET embedding = $1::vector WHERE id = $2`,
        [JSON.stringify(embedding), row.id]);
      success++;
    } catch (err) {
      failures++;
      errors.push(`failed ${row.id}: ${err.message}`);
    }
  }

  const total = res.rows.length;
  if (failures === 0) return { label: 'Null embeddings', status: 'fixed', detail: `regenerated ${success}/${total}` };
  return { label: 'Null embeddings', status: 'warn', detail: `${success}/${total} (${failures} failed)`, verbose: errors };
}

// ─── Step 7: Auto-dedup high-similarity pairs ───

async function autoDedup(db, opts = {}) {
  const { dryRun = false } = opts;

  try {
    const countRes = await db.query(
      `SELECT COUNT(*)::int AS cnt FROM brainx_memories
       WHERE embedding IS NOT NULL AND superseded_by IS NULL`
    );
    if ((countRes.rows[0]?.cnt || 0) < 2) {
      return { label: 'Auto-dedup', status: 'ok', detail: 'not enough memories' };
    }

    const res = await db.query(
      `WITH recent AS (
         SELECT id, embedding, created_at FROM brainx_memories
         WHERE embedding IS NOT NULL AND superseded_by IS NULL
         ORDER BY created_at DESC LIMIT 200
       )
       SELECT a.id AS old_id, b.id AS new_id,
              1 - (a.embedding <=> b.embedding) AS similarity
       FROM recent a, recent b
       WHERE a.id < b.id AND a.created_at < b.created_at
         AND 1 - (a.embedding <=> b.embedding) > 0.95
       ORDER BY similarity DESC LIMIT 50`
    );

    const count = res.rows.length;
    if (count === 0) return { label: 'Auto-dedup', status: 'ok', detail: 'no duplicates found' };

    if (dryRun) {
      return {
        label: 'Auto-dedup', status: 'fixed',
        detail: `would dedup ${count} pairs`,
        verbose: res.rows.slice(0, 10).map(r => `${r.old_id} → ${r.new_id} (${Number(r.similarity).toFixed(4)})`)
      };
    }

    for (const row of res.rows) {
      await db.query(
        `UPDATE brainx_memories SET superseded_by = $1 WHERE id = $2 AND superseded_by IS NULL`,
        [row.new_id, row.old_id]
      );
    }
    return { label: 'Auto-dedup', status: 'fixed', detail: `deduped ${count} pairs` };
  } catch (err) {
    return { label: 'Auto-dedup', status: 'fail', detail: err.message };
  }
}

// ─── Step 8: Cron re-registration check ───

async function checkCronRegistration(db, opts = {}) {
  const cronJobsPath = path.join(process.env.HOME || '', '.openclaw', 'cron', 'jobs.json');
  try {
    const raw = fs.readFileSync(cronJobsPath, 'utf8');
    const data = JSON.parse(raw);
    const jobs = data.jobs || [];

    const keywords = [
      { name: 'Memory Distiller', patterns: ['distiller'] },
      { name: 'Memory Bridge', patterns: ['memory bridge'] },
      { name: 'Lifecycle Daily', patterns: ['lifecycle'] },
      { name: 'Session Harvester', patterns: ['harvester'] },
      { name: 'Cross-Agent Learning', patterns: ['cross-agent'] },
      { name: 'Contradiction Detector', patterns: ['contradiction'] }
    ];

    let found = 0;
    const missing = [];

    for (const expected of keywords) {
      const match = jobs.find(j => {
        const combined = ((j.name || '') + ' ' + ((j.payload && j.payload.message) || '')).toLowerCase();
        return expected.patterns.some(p => combined.includes(p));
      });
      if (match) {
        found++;
      } else {
        missing.push(expected.name);
      }
    }

    if (missing.length === 0) {
      return { label: 'Cron registration', status: 'ok', detail: `all 6 BrainX crons present` };
    }
    return {
      label: 'Cron registration', status: 'warn',
      detail: `${missing.length} BrainX crons missing — register manually via \`openclaw cron\``,
      verbose: missing.map(m => `missing: ${m}`)
    };
  } catch (err) {
    return { label: 'Cron registration', status: 'warn', detail: 'cannot read cron config' };
  }
}

// ─── Run all fixes ───

async function runAllFixes(db, opts = {}) {
  const results = [];
  results.push(await applyMigrations(db, opts));
  results.push(await cleanExpired(db, opts));
  results.push(await fixOrphans(db, opts));
  results.push(await backfillProvenance(db, opts));
  results.push(await demoteStaleTiers(db, opts));
  results.push(await regenerateEmbeddings(db, opts));
  results.push(await autoDedup(db, opts));
  results.push(await checkCronRegistration(db, opts));
  return results;
}

// ─── Unicode box formatting (clack style) ───

const SYM_STATUS = { ok: '✓', fixed: '✓', warn: '⚠', fail: '✗' };

function formatFixReport(results, verbose = false, dryRun = false) {
  const W = 58; // minimum inner content width
  const total = results.length;

  // Pre-compute all lines to find actual max width
  const maxLabel = 22;
  const computedLines = [];
  for (let i = 0; i < results.length; i++) {
    const r = results[i];
    const step = `[${i + 1}/${total}]`;
    const sym = SYM_STATUS[r.status] || ' ';
    const pad = Math.max(1, maxLabel - r.label.length);
    const dots = ' ' + '.'.repeat(pad) + ' ';
    const line = `  ${sym} ${step} ${r.label}${dots}${r.detail}`;
    const verboseLines = (verbose && r.verbose) ? r.verbose.map(v => `            ${v}`) : [];
    computedLines.push({ line, verboseLines });
  }

  const allLines = computedLines.flatMap(cl => [cl.line, ...cl.verboseLines]);
  const maxLine = Math.max(W, ...allLines.map(l => l.length + 2));

  const out = [];
  const heading = dryRun ? '┌  BrainX Fix (dry-run)' : '┌  BrainX Fix';
  out.push('');
  out.push(heading);
  out.push('│');

  const titleBar = `◇  Repairs ` + '─'.repeat(Math.max(1, maxLine - 11)) + '╮';
  out.push(titleBar);
  out.push(`│${' '.repeat(maxLine + 1)}│`);

  for (const cl of computedLines) {
    const pad = maxLine - cl.line.length;
    out.push(`│${cl.line}${' '.repeat(Math.max(1, pad + 1))}│`);
    for (const vl of cl.verboseLines) {
      const vpad = maxLine - vl.length;
      out.push(`│${vl}${' '.repeat(Math.max(1, vpad + 1))}│`);
    }
  }

  out.push(`│${' '.repeat(maxLine + 1)}│`);
  out.push(`├${'─'.repeat(maxLine + 1)}╯`);
  out.push('│');

  const hasFailure = results.some(r => r.status === 'fail');
  if (hasFailure) {
    out.push('└  Some repairs failed. Check errors above.');
  } else {
    out.push('└  All repairs complete. Run `brainx doctor` to verify.');
  }

  return out.join('\n');
}

function formatFixReportJson(results) {
  return JSON.stringify({
    ok: !results.some(r => r.status === 'fail'),
    steps: results.map(r => ({
      label: r.label,
      status: r.status,
      detail: r.detail,
      verbose: r.verbose || null
    }))
  }, null, 2);
}

// ─── Main entry point ───

async function cmdFix(args, deps = {}) {
  let db;
  try {
    db = deps.db || require('./db');
  } catch (err) {
    console.log('');
    console.log('┌  BrainX Fix');
    console.log('│');
    console.log('└  ✗ Database connection failed: ' + err.message);
    return;
  }

  const opts = {
    dryRun: args['dry-run'] || args.dryRun || false,
    verbose: args.verbose || false,
    skipEmbeddings: args['skip-embeddings'] || args.skipEmbeddings || false
  };

  const results = await runAllFixes(db, opts);

  if (args.json) {
    console.log(formatFixReportJson(results));
  } else {
    console.log(formatFixReport(results, opts.verbose, opts.dryRun));
  }
}

module.exports = {
  runAllFixes,
  formatFixReport,
  formatFixReportJson,
  cmdFix
};
