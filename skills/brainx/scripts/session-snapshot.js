#!/usr/bin/env node
/**
 * BrainX V5 — Session Snapshot
 *
 * Captures snapshots of recently modified sessions and stores them
 * in brainx_session_snapshots with embeddings for semantic search.
 *
 * Usage:
 *   node scripts/session-snapshot.js [--hours 6] [--max-sessions 10] [--verbose]
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { Pool } = require('pg');

const AGENTS_DIR = path.join(process.env.HOME || '', '.openclaw', 'agents');
const DATA_DIR = path.join(__dirname, '..', 'data');
const TRACKER_FILE = path.join(DATA_DIR, 'snapshotted-sessions.json');

const DATABASE_URL = process.env.DATABASE_URL;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!DATABASE_URL) { console.error('DATABASE_URL is required'); process.exit(1); }
if (!OPENAI_API_KEY) { console.error('OPENAI_API_KEY is required'); process.exit(1); }

const pool = new Pool({ connectionString: DATABASE_URL });

// --- CLI args ---
function parseArgs() {
  const argv = process.argv.slice(2);
  const args = { hours: 6, maxSessions: 10, verbose: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--hours') args.hours = parseInt(argv[++i], 10) || 6;
    else if (argv[i] === '--max-sessions') args.maxSessions = parseInt(argv[++i], 10) || 10;
    else if (argv[i] === '--verbose') args.verbose = true;
  }
  return args;
}

// --- Tracker (rotate files monthly) ---
function getTrackerFile() {
  const date = new Date();
  const filename = `snapshots-${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}.json`;
  return path.join(DATA_DIR, filename);
}

function loadTracker() {
  const file = getTrackerFile();
  try {
    if (fs.existsSync(file)) return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (_) {}
  return {};
}

function saveTracker(tracker) {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(getTrackerFile(), JSON.stringify(tracker, null, 2));
}

// Helper to archive old trackers (optional/manual)
function archiveOldTrackers() {
  const files = fs.readdirSync(DATA_DIR).filter(f => f.startsWith('snapshots-') && f !== path.basename(getTrackerFile()));
  // Keep last 3 months, move others to backups/
  if (files.length > 3) {
    const backupDir = path.join(DATA_DIR, '..', 'backups', 'trackers');
    if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir, { recursive: true });
    files.sort().slice(0, files.length - 3).forEach(f => {
      fs.renameSync(path.join(DATA_DIR, f), path.join(backupDir, f));
    });
  }
}

// --- Find recent JSONL session files ---
function findRecentSessions(hoursAgo, maxSessions) {
  const cutoff = Date.now() - hoursAgo * 3600 * 1000;
  const sessions = [];
  if (!fs.existsSync(AGENTS_DIR)) return sessions;

  for (const agent of fs.readdirSync(AGENTS_DIR)) {
    if (['heartbeat', 'monitor'].includes(agent)) continue;
    const sessDir = path.join(AGENTS_DIR, agent, 'sessions');
    if (!fs.existsSync(sessDir)) continue;
    for (const f of fs.readdirSync(sessDir).filter(f => f.endsWith('.jsonl'))) {
      const full = path.join(sessDir, f);
      const stat = fs.statSync(full);
      if (stat.mtimeMs >= cutoff && stat.size > 200) {
        sessions.push({ agent, sessionId: f.replace('.jsonl', ''), path: full, mtimeMs: stat.mtimeMs });
      }
    }
  }
  return sessions.sort((a, b) => b.mtimeMs - a.mtimeMs).slice(0, maxSessions);
}

// --- Parse a JSONL session file and extract structured info ---
function parseSession(filePath) {
  const lines = fs.readFileSync(filePath, 'utf8').split('\n').filter(Boolean);
  const info = {
    turnCount: 0,
    sessionStart: null,
    sessionEnd: null,
    project: 'unknown',
    files: new Set(),
    errors: [],
    urls: new Set(),
    blockers: [],
    pendingItems: [],
    assistantTexts: [],
    userTexts: [],
  };

  for (const line of lines) {
    let entry;
    try { entry = JSON.parse(line); } catch { continue; }

    // Track timestamps
    const ts = entry.timestamp || entry.message?.timestamp;
    if (ts) {
      const d = typeof ts === 'number' ? new Date(ts) : new Date(ts);
      if (!info.sessionStart || d < info.sessionStart) info.sessionStart = d;
      if (!info.sessionEnd || d > info.sessionEnd) info.sessionEnd = d;
    }

    if (entry.type === 'message' && entry.message) {
      const role = entry.message.role;
      const blocks = Array.isArray(entry.message.content) ? entry.message.content : [];
      for (const block of blocks) {
        if (block.type !== 'text' || !block.text) continue;
        const text = block.text;

        if (role === 'assistant') {
          info.turnCount++;
          info.assistantTexts.push(text);
        } else if (role === 'user') {
          info.userTexts.push(text);
        }

        // Extract file paths
        const filePaths = text.match(/\/[\w./-]+\.\w{1,10}/g) || [];
        for (const fp of filePaths) {
          if (fp.includes('node_modules') || fp.length > 120) continue;
          info.files.add(fp);
        }

        // Extract URLs
        const urlMatches = text.match(/https?:\/\/[^\s"'<>\])+]+/g) || [];
        for (const u of urlMatches) info.urls.add(u.replace(/[.,;:)]+$/, ''));

        // Extract errors
        const errMatches = text.match(/(?:error|Error|ERROR|fail|FAIL|exception|Exception)[:\s].{10,120}/g) || [];
        for (const e of errMatches.slice(0, 5)) info.errors.push(e.trim());

        // Extract blockers
        if (/block(?:ed|er|ing)|can'?t proceed|stuck|waiting for/i.test(text)) {
          const snippet = text.slice(0, 200);
          info.blockers.push(snippet);
        }
      }
    }
  }

  // Detect project from content
  const allText = [...info.userTexts, ...info.assistantTexts].join(' ').slice(0, 5000);
  info.project = detectProject(allText);

  return info;
}

// --- Project detection heuristics ---
function detectProject(text) {
  const lower = text.toLowerCase();
  const patterns = [
    { match: /brainx/i, name: 'brainx' },
    { match: /openclaw|clawd|clawma/i, name: 'openclaw' },
    { match: /mdx|closer.?academy|edzaya/i, name: 'mdx' },
    { match: /emailbot|gmail.*autom/i, name: 'emailbot' },
    { match: /notion.*crm|lead.*gen/i, name: 'lead-gen' },
    { match: /railway|deploy/i, name: 'infrastructure' },
  ];
  for (const p of patterns) {
    if (p.match.test(text)) return p.name;
  }
  // Fallback: extract from repo paths
  const repoMatch = text.match(/\/(?:home\/clawd|workspace)[/-](\w[\w-]{2,20})/);
  if (repoMatch) return repoMatch[1];
  return 'general';
}

// --- Summarize a session into a short text ---
function buildSummary(info, agent) {
  const parts = [];
  parts.push(`Agent ${agent} session with ${info.turnCount} turns.`);

  // Use last few assistant texts as summary seed
  const relevant = info.assistantTexts
    .filter(t => t.length > 80 && t.length < 2000)
    .slice(-3);

  if (relevant.length > 0) {
    const combined = relevant.map(t => t.slice(0, 300)).join(' ');
    parts.push(combined.slice(0, 600));
  }

  if (info.errors.length > 0) parts.push(`Errors: ${info.errors.slice(0, 2).join('; ')}`);
  if (info.blockers.length > 0) parts.push(`Blockers: ${info.blockers.slice(0, 2).join('; ')}`);

  return parts.join(' ').slice(0, 1200);
}

// --- Determine session status ---
function detectStatus(info) {
  if (info.blockers.length > 0) return 'blocked';
  if (info.errors.length > 3) return 'blocked';
  if (info.turnCount < 3) return 'paused';
  // Check if the last assistant message signals completion
  const lastMsg = info.assistantTexts[info.assistantTexts.length - 1] || '';
  if (/(?:listo|done|complet|terminado|finished|deployed)/i.test(lastMsg.slice(0, 300))) return 'completed';
  return 'in_progress';
}

// --- Embedding via OpenAI ---
async function embed(text) {
  const res = await fetch('https://api.openai.com/v1/embeddings', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'text-embedding-3-small',
      input: text.slice(0, 8000),
      dimensions: 1536,
    }),
  });
  if (!res.ok) {
    const msg = await res.text();
    throw new Error(`Embedding failed: ${res.status} ${msg.slice(0, 200)}`);
  }
  const data = await res.json();
  const vec = data?.data?.[0]?.embedding;
  if (!Array.isArray(vec)) throw new Error('Invalid embedding response');
  return vec;
}

// --- Insert snapshot into DB ---
async function insertSnapshot(snap) {
  const sql = `
    INSERT INTO brainx_session_snapshots
      (id, project, agent, summary, status, pending_items, blockers,
       last_file_touched, last_error, key_urls, embedding, session_start, session_end, turn_count)
    VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11::vector,$12,$13,$14)
    ON CONFLICT (id) DO UPDATE SET
      summary = EXCLUDED.summary,
      status = EXCLUDED.status,
      pending_items = EXCLUDED.pending_items,
      blockers = EXCLUDED.blockers,
      last_file_touched = EXCLUDED.last_file_touched,
      last_error = EXCLUDED.last_error,
      key_urls = EXCLUDED.key_urls,
      embedding = EXCLUDED.embedding,
      session_end = EXCLUDED.session_end,
      turn_count = EXCLUDED.turn_count
  `;
  await pool.query(sql, [
    snap.id,
    snap.project,
    snap.agent,
    snap.summary,
    snap.status,
    JSON.stringify(snap.pendingItems),
    JSON.stringify(snap.blockers),
    snap.lastFileTouched,
    snap.lastError,
    JSON.stringify(snap.keyUrls),
    JSON.stringify(snap.embedding),
    snap.sessionStart,
    snap.sessionEnd,
    snap.turnCount,
  ]);
}

// --- Main ---
async function main() {
  const args = parseArgs();
  const tracker = loadTracker();
  const sessions = findRecentSessions(args.hours, args.maxSessions);

  const result = { processed: 0, skipped: 0, stored: 0, errors: [] };

  for (const sess of sessions) {
    const trackKey = `${sess.agent}:${sess.sessionId}`;

    // Skip if already snapshotted at this mtime
    if (tracker[trackKey] && tracker[trackKey].mtimeMs >= sess.mtimeMs) {
      result.skipped++;
      continue;
    }

    try {
      const info = parseSession(sess.path);

      // Skip very short sessions
      if (info.turnCount < 2) {
        result.skipped++;
        continue;
      }

      const summary = buildSummary(info, sess.agent);
      const status = detectStatus(info);
      const snapId = `snap_${Date.now()}_${crypto.createHash('sha256').update(trackKey).digest('hex').slice(0, 8)}`;

      if (args.verbose) process.stderr.write(`[${sess.agent}] ${sess.sessionId.slice(0, 8)}... ${info.turnCount} turns → ${status}\n`);

      // Generate embedding
      const embedding = await embed(summary);

      // Rate limit
      await new Promise(r => setTimeout(r, 300));

      const snapshot = {
        id: snapId,
        project: info.project,
        agent: sess.agent,
        summary,
        status,
        pendingItems: info.pendingItems.slice(0, 10),
        blockers: info.blockers.slice(0, 5),
        lastFileTouched: [...info.files].pop() || null,
        lastError: info.errors[info.errors.length - 1] || null,
        keyUrls: [...info.urls].slice(0, 10),
        embedding,
        sessionStart: info.sessionStart,
        sessionEnd: info.sessionEnd,
        turnCount: info.turnCount,
      };

      await insertSnapshot(snapshot);

      tracker[trackKey] = { mtimeMs: sess.mtimeMs, at: Date.now(), snapId };
      result.stored++;
      result.processed++;
    } catch (err) {
      result.processed++;
      result.errors.push({ session: trackKey, error: (err.message || String(err)).slice(0, 200) });
    }
  }

  saveTracker(tracker);
  await pool.end();

  console.log(JSON.stringify(result, null, 2));
}

main().catch(err => {
  console.error(err.stack || err.message);
  process.exit(1);
});
