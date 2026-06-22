#!/usr/bin/env node
/**
 * BrainX Auto-Distiller
 * Processes OpenClaw session logs and auto-generates high-quality memories.
 * Uses heuristics (no LLM calls) to keep costs zero.
 */

// Load env
try {
  const dotenv = require('dotenv');
  const envPath = process.env.BRAINX_ENV || require('path').join(__dirname, '..', '.env');
  dotenv.configDotenv({ path: envPath });
} catch (_) {}

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const db = require('../lib/db');
const rag = require('../lib/openai-rag');

// ── Config ──────────────────────────────────────────
const SESSION_DIRS = [
  path.join(process.env.HOME || '/home/clawd', '.openclaw', 'agents')
];
const DEDUPE_THRESHOLD = parseFloat(process.env.BRAINX_DEDUPE_SIM_THRESHOLD || '0.92');

// ── Arg parsing ─────────────────────────────────────
function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const k = a.slice(2);
      const v = argv[i + 1];
      if (!v || v.startsWith('--')) out[k] = true;
      else { out[k] = v; i++; }
    } else {
      out._.push(a);
    }
  }
  return out;
}

// ── Session file discovery ──────────────────────────
function findSessionFiles(sinceDate) {
  const files = [];
  for (const baseDir of SESSION_DIRS) {
    if (!fs.existsSync(baseDir)) continue;
    // Walk agent dirs
    const agents = fs.readdirSync(baseDir, { withFileTypes: true });
    for (const agentDir of agents) {
      if (!agentDir.isDirectory()) continue;
      const sessionsDir = path.join(baseDir, agentDir.name, 'sessions');
      if (!fs.existsSync(sessionsDir)) continue;
      const sessionFiles = fs.readdirSync(sessionsDir).filter(f => f.endsWith('.jsonl'));
      for (const sf of sessionFiles) {
        const fullPath = path.join(sessionsDir, sf);
        const stat = fs.statSync(fullPath);
        if (sinceDate && stat.mtime < sinceDate) continue;
        files.push({ path: fullPath, agent: agentDir.name, file: sf, mtime: stat.mtime });
      }
    }
  }
  return files.sort((a, b) => b.mtime - a.mtime);
}

// ── JSONL parser ────────────────────────────────────
function parseSessionFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').filter(Boolean);
  const events = [];
  for (const line of lines) {
    try {
      events.push(JSON.parse(line));
    } catch (_) {}
  }
  return events;
}

// ── Heuristic extractors ────────────────────────────

/**
 * Find error → fix sequences: a tool error followed by a successful retry.
 */
function findErrorFixSequences(events) {
  const results = [];
  // Only consider tool results (actual runtime errors, not code reads or user messages)
  const toolResults = events.filter(e =>
    e.type === 'message' && e.message &&
    (e.role === 'tool' || (e.message && e.message.role === 'tool'))
  );
  const messages = events.filter(e => e.type === 'message' && e.message);

  for (let i = 0; i < messages.length - 1; i++) {
    const msg = messages[i];
    const role = msg.role || (msg.message && msg.message.role) || '';
    const content = typeof msg.message === 'string' ? msg.message :
      (msg.message.content && typeof msg.message.content === 'string' ? msg.message.content :
        Array.isArray(msg.message.content) ? msg.message.content.map(c => c.text || '').join(' ') : '');

    // Skip long messages (likely code dumps, file reads, or schema outputs)
    if (content.length > 2000) continue;

    // Only detect errors in tool results or short assistant messages, not in user messages or file reads
    if (role !== 'tool' && role !== 'assistant') continue;

    const lc = content.toLowerCase();

    // Use stricter error patterns that indicate actual runtime failures
    // Avoid matching code that merely contains the word "error" (e.g. console.error, error handling code)
    const isError = (
      /\berror[:\s]/i.test(content) ||
      /\bfailed\b/i.test(content) ||
      /\bexception[:\s]/i.test(content) ||
      /\bpermission denied\b/i.test(content) ||
      /\bcommand (exited|failed) with code [1-9]/i.test(content) ||
      /\bENOENT\b/.test(content) ||
      /\bEACCES\b/.test(content) ||
      /\btimeout\b/i.test(content) ||
      /\b(FATAL|PANIC|crash)\b/i.test(content)
    );

    // Exclude false positives: code snippets, schema dumps, file reads
    const isFalsePositive = (
      /^\s*(const|let|var|function|class|import|export|require|module)\b/.test(content) ||
      /^\s*(CREATE|ALTER|DROP|SELECT|INSERT|UPDATE|DELETE)\s/i.test(content) ||
      /^\s*#!/.test(content) ||
      /console\.(error|log|warn)\s*\(/i.test(content) ||
      /catch\s*\(\s*(e|err|error)\s*\)/i.test(content) ||
      /\.on\(\s*['"]error['"]/i.test(content) ||
      content.split('\n').length > 30
    );

    if (isError && !isFalsePositive && i + 1 < messages.length) {
      // Look ahead for a fix (within next 5 messages)
      for (let j = i + 1; j < Math.min(i + 6, messages.length); j++) {
        const nextMsg = messages[j];
        const nextContent = typeof nextMsg.message === 'string' ? nextMsg.message :
          (nextMsg.message.content && typeof nextMsg.message.content === 'string' ? nextMsg.message.content :
            Array.isArray(nextMsg.message.content) ? nextMsg.message.content.map(c => c.text || '').join(' ') : '');
        const nlc = nextContent.toLowerCase();

        if (nlc.includes('fixed') || nlc.includes('resolved') || nlc.includes('works now') ||
            nlc.includes('success') || nlc.includes('listo') || nlc.includes('resuelto') ||
            nlc.includes('funcionando')) {
          results.push({
            type: 'error_fix',
            error: content.slice(0, 300),
            fix: nextContent.slice(0, 300),
            importance: 7
          });
          break;
        }
      }
    }
  }
  return results;
}

/**
 * Find explicit decisions in messages.
 */
function findDecisions(events) {
  const decisionPatterns = [
    /\b(decided|going with|elegimos|vamos con|vamos a usar|the plan is|let's go with|optamos por)\b/i
  ];
  const results = [];
  const messages = events.filter(e => e.type === 'message' && e.message);

  for (const msg of messages) {
    const content = typeof msg.message === 'string' ? msg.message :
      (msg.message.content && typeof msg.message.content === 'string' ? msg.message.content :
        Array.isArray(msg.message.content) ? msg.message.content.map(c => c.text || '').join(' ') : '');

    for (const pattern of decisionPatterns) {
      if (pattern.test(content)) {
        results.push({
          type: 'decision',
          content: content.slice(0, 500),
          importance: 6
        });
        break;
      }
    }
  }
  return results;
}

/**
 * Detect long/complex sessions worth noting.
 */
function detectComplexSession(events, filePath) {
  const messages = events.filter(e => e.type === 'message');
  const turnCount = messages.length;

  // Only flag truly complex sessions
  if (turnCount < 20) return null;

  // Extract session metadata
  const sessionEvent = events.find(e => e.type === 'session');
  const cwd = sessionEvent?.cwd || '';

  // Count tool calls
  const toolCalls = events.filter(e =>
    e.type === 'custom' && e.customType === 'tool_call' ||
    e.type === 'message' && e.message?.role === 'tool'
  );

  return {
    type: 'complex_session',
    content: `Complex session (${turnCount} turns, ${toolCalls.length} tool calls) in ${cwd || 'unknown dir'}. File: ${path.basename(filePath)}`,
    importance: 5,
    turnCount,
    toolCallCount: toolCalls.length
  };
}

/**
 * Find repeated tool failures on same target.
 */
function findRepeatedFailures(events) {
  const failures = {};
  const messages = events.filter(e => e.type === 'message' && e.message);

  for (const msg of messages) {
    const role = msg.role || (msg.message && msg.message.role) || '';
    // Only count failures from tool results, not from code reads or user messages
    if (role !== 'tool') continue;

    const content = typeof msg.message === 'string' ? msg.message :
      (msg.message.content && typeof msg.message.content === 'string' ? msg.message.content :
        Array.isArray(msg.message.content) ? msg.message.content.map(c => c.text || '').join(' ') : '');

    // Skip long outputs (likely file reads, not errors)
    if (content.length > 2000) continue;

    const lc = content.toLowerCase();
    const isRealError = (
      /\berror[:\s]/i.test(content) ||
      /\bfailed\b/i.test(content) ||
      /\bcommand (exited|failed) with code [1-9]/i.test(content) ||
      /\bENOENT\b/.test(content) ||
      /\bpermission denied\b/i.test(content)
    );
    if (isRealError) {
      // Simple fingerprint: first 50 chars
      const key = lc.slice(0, 50).replace(/[^a-z0-9]/g, '_');
      failures[key] = (failures[key] || 0) + 1;
    }
  }

  const results = [];
  for (const [key, count] of Object.entries(failures)) {
    if (count >= 3) {
      results.push({
        type: 'repeated_failure',
        content: `Repeated failure (×${count}): ${key.replace(/_/g, ' ').slice(0, 100)}`,
        importance: 6
      });
    }
  }
  return results;
}

// ── Deduplication ───────────────────────────────────

async function isDuplicate(content) {
  try {
    const embedding = await rag.embed(content);
    const res = await db.query(
      `SELECT id, 1 - (embedding <=> $1::vector) AS similarity
       FROM brainx_memories
       WHERE superseded_by IS NULL
       ORDER BY similarity DESC
       LIMIT 1`,
      [JSON.stringify(embedding)]
    );
    if (res.rows.length > 0 && (res.rows[0].similarity ?? 0) >= DEDUPE_THRESHOLD) {
      return { isDup: true, existingId: res.rows[0].id, similarity: res.rows[0].similarity };
    }
    return { isDup: false };
  } catch (err) {
    // If embedding fails, skip dedupe
    return { isDup: false };
  }
}

// ── Main distillation ───────────────────────────────

async function processSession(sessionFile, opts = {}) {
  const { dryRun, verbose } = opts;

  // Check if already processed
  const existing = await db.query(
    'SELECT id FROM brainx_distillation_log WHERE session_file = $1',
    [sessionFile.file]
  );
  if (existing.rows.length > 0) {
    if (verbose) console.log(`  ⏭ Already processed: ${sessionFile.file}`);
    return { skipped: true, reason: 'already_processed' };
  }

  const events = parseSessionFile(sessionFile.path);
  if (events.length < 5) {
    if (verbose) console.log(`  ⏭ Too short (${events.length} events): ${sessionFile.file}`);
    return { skipped: true, reason: 'too_short' };
  }

  // Extract candidates via heuristics
  const candidates = [
    ...findErrorFixSequences(events),
    ...findDecisions(events),
    ...findRepeatedFailures(events)
  ];

  const complexSession = detectComplexSession(events, sessionFile.path);
  if (complexSession) candidates.push(complexSession);

  if (verbose) {
    console.log(`  📄 ${sessionFile.file}: ${events.length} events, ${candidates.length} candidates`);
  }

  let memoriesCreated = 0;
  let memoriesSkipped = 0;

  for (const candidate of candidates) {
    const memContent = candidate.type === 'error_fix'
      ? `Error: ${candidate.error}\nFix: ${candidate.fix}`
      : candidate.content;

    // Deduplicate
    const { isDup, existingId, similarity } = await isDuplicate(memContent);
    if (isDup) {
      if (verbose) console.log(`    ⏭ Duplicate (sim:${(similarity ?? 0).toFixed(2)} of ${existingId}): ${memContent.slice(0, 60)}...`);
      memoriesSkipped++;
      continue;
    }

    if (dryRun) {
      console.log(`    [DRY-RUN] Would create: [${candidate.type}|imp:${candidate.importance}] ${memContent.slice(0, 80)}...`);
      memoriesCreated++;
      continue;
    }

    // Map candidate type to brainx memory type
    const typeMap = {
      error_fix: 'gotcha',
      decision: 'decision',
      complex_session: 'note',
      repeated_failure: 'gotcha'
    };

    const categoryMap = {
      error_fix: 'error',
      decision: 'best_practice',
      complex_session: 'context',
      repeated_failure: 'error'
    };

    try {
      await rag.storeMemory({
        id: `m_distill_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
        type: typeMap[candidate.type] || 'note',
        content: memContent,
        context: null,
        tier: 'warm',
        importance: candidate.importance || 5,
        agent: sessionFile.agent,
        tags: ['auto-distilled', candidate.type],
        source_kind: 'llm_distilled',
        source_path: sessionFile.path,
        confidence: 0.6
      });
      memoriesCreated++;
      if (verbose) console.log(`    ✅ Created: [${candidate.type}|imp:${candidate.importance}] ${memContent.slice(0, 60)}...`);
    } catch (err) {
      if (verbose) console.error(`    ❌ Failed to store: ${err.message}`);
      memoriesSkipped++;
    }
  }

  // Log processing (even for dry runs, skip logging)
  if (!dryRun) {
    const logId = `dl_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
    await db.query(
      `INSERT INTO brainx_distillation_log (id, session_file, memories_created, memories_skipped)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (session_file) DO UPDATE SET
         memories_created = EXCLUDED.memories_created,
         memories_skipped = EXCLUDED.memories_skipped,
         processed_at = NOW()`,
      [logId, sessionFile.file, memoriesCreated, memoriesSkipped]
    );
  }

  return { memoriesCreated, memoriesSkipped };
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const dryRun = !!args['dry-run'] || !!args.dryRun;
  const verbose = !!args.verbose;
  const limit = args.limit ? parseInt(args.limit, 10) : 20;
  const sinceStr = args.since || null;
  const sinceDate = sinceStr ? new Date(sinceStr) : null;
  const jsonOutput = !!args.json;

  if (verbose) {
    console.log(`🧠 BrainX Auto-Distiller`);
    console.log(`  Mode: ${dryRun ? 'DRY-RUN' : 'LIVE'}`);
    console.log(`  Limit: ${limit}`);
    if (sinceDate) console.log(`  Since: ${sinceDate.toISOString()}`);
    console.log('');
  }

  const sessionFiles = findSessionFiles(sinceDate);
  const toProcess = sessionFiles.slice(0, limit);

  if (verbose) console.log(`Found ${sessionFiles.length} session files, processing ${toProcess.length}\n`);

  let totalCreated = 0;
  let totalSkipped = 0;
  let totalProcessed = 0;
  let totalAlreadyDone = 0;

  for (const sf of toProcess) {
    const result = await processSession(sf, { dryRun, verbose });
    if (result.skipped) {
      totalAlreadyDone++;
    } else {
      totalProcessed++;
      totalCreated += result.memoriesCreated || 0;
      totalSkipped += result.memoriesSkipped || 0;
    }
  }

  const summary = {
    ok: true,
    dry_run: dryRun,
    sessions_found: sessionFiles.length,
    sessions_processed: totalProcessed,
    sessions_skipped: totalAlreadyDone,
    memories_created: totalCreated,
    memories_skipped_dedup: totalSkipped
  };

  if (jsonOutput) {
    console.log(JSON.stringify(summary, null, 2));
  } else {
    console.log(`\n📊 Distillation Summary:`);
    console.log(`  Sessions found: ${summary.sessions_found}`);
    console.log(`  Sessions processed: ${summary.sessions_processed}`);
    console.log(`  Sessions skipped (already done): ${summary.sessions_skipped}`);
    console.log(`  Memories created: ${summary.memories_created}`);
    console.log(`  Memories skipped (dedup): ${summary.memories_skipped_dedup}`);
    if (dryRun) console.log(`  ⚠️  DRY-RUN mode — no changes written`);
  }
}

main().catch(err => {
  console.error(err.message || err);
  process.exit(1);
});
