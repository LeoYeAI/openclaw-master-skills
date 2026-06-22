#!/usr/bin/env node
/**
 * BrainX V5 — Session Harvester
 * 
 * Reads recent OpenClaw session JSONLs and extracts high-signal memories.
 * Designed to run as a cron agentTurn every 4h.
 * 
 * Usage:
 *   node session-harvester.js [--hours 4] [--dry-run] [--agent main] [--verbose]
 * 
 * Output: JSON summary of extracted memories
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const AGENTS_DIR = path.join(process.env.HOME || '', '.openclaw', 'agents');
const BRAINX_DIR = path.join(__dirname, '..');

// Parse args
function parseArgs() {
  const args = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--hours') args.hours = parseInt(argv[++i], 10);
    else if (argv[i] === '--dry-run') args.dryRun = true;
    else if (argv[i] === '--agent') args.agentFilter = argv[++i];
    else if (argv[i] === '--verbose') args.verbose = true;
    else if (argv[i] === '--min-chars') args.minChars = parseInt(argv[++i], 10);
    else if (argv[i] === '--max-memories') args.maxMemories = parseInt(argv[++i], 10);
  }
  return {
    hours: args.hours || 4,
    dryRun: args.dryRun || false,
    agentFilter: args.agentFilter || null,
    verbose: args.verbose || false,
    minChars: args.minChars || 120,
    maxMemories: args.maxMemories || 40,
  };
}

// Find recently modified JSONL files
function findRecentSessions(hoursAgo, agentFilter) {
  const cutoff = Date.now() - (hoursAgo * 60 * 60 * 1000);
  const sessions = [];

  if (!fs.existsSync(AGENTS_DIR)) return sessions;

  const agents = fs.readdirSync(AGENTS_DIR).filter(d => {
    if (agentFilter) return d === agentFilter;
    // Skip heartbeat/monitor — they're operational noise
    return !['heartbeat', 'monitor'].includes(d);
  });

  for (const agent of agents) {
    const sessDir = path.join(AGENTS_DIR, agent, 'sessions');
    if (!fs.existsSync(sessDir)) continue;

    const files = fs.readdirSync(sessDir).filter(f => f.endsWith('.jsonl'));
    for (const file of files) {
      const fullPath = path.join(sessDir, file);
      const stat = fs.statSync(fullPath);
      if (stat.mtimeMs >= cutoff) {
        sessions.push({
          agent,
          sessionId: file.replace('.jsonl', ''),
          path: fullPath,
          modified: stat.mtimeMs,
          size: stat.size,
        });
      }
    }
  }

  return sessions.sort((a, b) => b.modified - a.modified);
}

// Extract assistant text messages from a JSONL file
function extractMessages(filePath, minChars) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n').filter(Boolean);
  const messages = [];

  for (const line of lines) {
    try {
      const entry = JSON.parse(line);
      if (entry.type !== 'message') continue;
      if (!entry.message || entry.message.role !== 'assistant') continue;
      if (!Array.isArray(entry.message.content)) continue;

      for (const block of entry.message.content) {
        if (block.type !== 'text') continue;
        const text = (block.text || '').trim();

        // Skip noise
        if (!text || text.length < minChars) continue;
        if (text === 'NO_REPLY' || text === 'HEARTBEAT_OK') continue;
        if (/^💓\s*✅/.test(text)) continue; // Session start markers
        if (/^🦞\s*(Hey|Hola|Buenos)/.test(text) && text.length < 150) continue; // Greetings

        messages.push({
          text,
          timestamp: entry.timestamp || entry.message?.timestamp,
          charLen: text.length,
        });
      }
    } catch {
      // Skip malformed lines
    }
  }

  return messages;
}

// Classify a message using heuristic rules
// Returns null if the message is operational/mundane
function classifyMessage(text) {
  const lower = text.toLowerCase();

  // Skip patterns: operational chatter, status reports, code dumps, greetings
  const SKIP_PATTERNS = [
    /^(sí|si|ok|listo|hecho|done|entendido|perfecto|claro)/i,
    /heartbeat|cron.*complet|session cleanup|health check/i,
    /^no_reply$/i,
    /sin cambios|no changes|nothing to report/i,
    /^\[.*\]\s*✅/,  // Status confirmations
    /^```[\s\S]{200,}```/,  // Code blocks that dominate the message
    /^\s*(import|const|function|class|export|interface|type )\s/m,  // Code-first messages
    /^(Here'?s|Aquí (está|va)|Te muestro|I'll create)/i,  // Preambles to code dumps
    /node_modules|package\.json|tsconfig|\.gitignore/,  // Config file contents
    /Successfully wrote \d+ bytes/,  // Tool output
    /Process exited with code/,  // Tool output
  ];

  for (const pat of SKIP_PATTERNS) {
    if (pat.test(text)) return null;
  }

  // Classification rules (order matters — first match wins)
  const RULES = [
    // Decisions
    { match: /(?:decid|decisión|decidimos|elegimos|vamos a usar|switched to|migrat|adoptamos|en vez de|reemplaz)/i, type: 'decision', importance: 7 },
    { match: /(?:la solución|the fix|se resolvió|fix(?:ed|eado)|corregido|arreglado|el problema era)/i, type: 'learning', importance: 7, category: 'error' },
    
    // Errors / debugging
    { match: /(?:error|fail|crash|bug|broke|fallo|falló|roto|no funciona|se cayó|exception|stack trace)/i, type: 'learning', importance: 6, category: 'error' },
    
    // Gotchas / warnings
    { match: /(?:gotcha|cuidado|watch out|careful|trap|caveat|ojo con|no usar|avoid|nunca|prohibido)/i, type: 'gotcha', importance: 7, category: 'correction' },
    
    // Learnings / discoveries
    { match: /(?:aprendí|descubrí|resulta que|turns out|actually|en realidad|lo que pasa|the issue was|root cause)/i, type: 'learning', importance: 6, category: 'learning' },
    
    // Best practices
    { match: /(?:best practice|patrón|convention|siempre|always|nunca|never|regla|rule|estándar)/i, type: 'note', importance: 6, category: 'best_practice' },
    
    // Architecture / design
    { match: /(?:arquitectura|architecture|diseño|schema|structure|pipeline|workflow|integración)/i, type: 'decision', importance: 6 },
    
    // Config / setup
    { match: /(?:config|configuración|setup|instalé|installed|deploy|variable|env|api.?key|token)/i, type: 'note', importance: 5, category: 'correction' },
  ];

  for (const rule of RULES) {
    if (rule.match.test(text)) {
      return {
        type: rule.type,
        importance: rule.importance,
        category: rule.category || null,
      };
    }
  }

  // Only keep unclassified messages if they're VERY substantive (>800 chars)
  // and contain signal words indicating something worth remembering
  if (text.length > 800) {
    const hasSignal = /(?:importante|critical|key|clave|nota:|note:|resumen|summary|conclusion|resultado|result)/i.test(text);
    if (hasSignal) {
      return { type: 'note', importance: 5, category: null };
    }
  }

  // Skip everything else — better to miss some than to store noise
  return null;
}

// Create a content hash for dedup
function contentHash(text) {
  return crypto.createHash('sha256').update(text.slice(0, 500)).digest('hex').slice(0, 16);
}

// Store a memory directly via the RAG library (no subprocess)
let _rag = null;
function getRag() {
  if (!_rag) _rag = require(path.join(BRAINX_DIR, 'lib', 'openai-rag'));
  return _rag;
}

async function storeToBrainx(memory, dryRun) {
  if (dryRun) return { ok: true, dryRun: true };

  try {
    const rag = getRag();
    const result = await rag.storeMemory({
      id: `m_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
      type: memory.type,
      content: memory.content,
      context: memory.context || null,
      tier: memory.tier || 'warm',
      importance: memory.importance ?? 5,
      agent: memory.tags?.find(t => t.startsWith('agent:'))?.slice(6) || null,
      tags: memory.tags || [],
    });
    return { ok: true, id: result?.id, dedupe_merged: result?.dedupe_merged };
  } catch (e) {
    return { ok: false, error: (e.message || String(e)).slice(0, 200) };
  }
}

// Truncate content to reasonable size for memory storage
function truncateContent(text, maxChars = 1500) {
  if (text.length <= maxChars) return text;
  return text.slice(0, maxChars - 1) + '…';
}

async function main() {
  const args = parseArgs();
  const sessions = findRecentSessions(args.hours, args.agentFilter);

  const summary = {
    sessionsScanned: sessions.length,
    messagesExtracted: 0,
    messagesClassified: 0,
    messagesSkipped: 0,
    memoriesStored: 0,
    memoriesFailed: 0,
    candidatesTotal: 0,
    candidatesCapped: false,
    byAgent: {},
    byType: {},
    errors: [],
  };

  const seenHashes = new Set();
  const candidates = [];

  // Phase 1: Collect and classify all messages
  for (const session of sessions) {
    const messages = extractMessages(session.path, args.minChars);
    summary.messagesExtracted += messages.length;

    if (!summary.byAgent[session.agent]) {
      summary.byAgent[session.agent] = { scanned: 0, stored: 0 };
    }
    summary.byAgent[session.agent].scanned += messages.length;

    for (const msg of messages) {
      const classification = classifyMessage(msg.text);
      if (!classification) {
        summary.messagesSkipped++;
        continue;
      }
      summary.messagesClassified++;

      const hash = contentHash(msg.text);
      if (seenHashes.has(hash)) continue;
      seenHashes.add(hash);

      candidates.push({
        agent: session.agent,
        sessionId: session.sessionId,
        classification,
        text: msg.text,
      });
    }
  }

  // Phase 2: Sort by importance, then take top N
  const TYPE_PRIORITY = { decision: 0, gotcha: 1, learning: 2, note: 3, feature_request: 4, action: 5 };
  candidates.sort((a, b) => {
    const impDiff = b.classification.importance - a.classification.importance;
    if (impDiff !== 0) return impDiff;
    return (TYPE_PRIORITY[a.classification.type] || 9) - (TYPE_PRIORITY[b.classification.type] || 9);
  });

  summary.candidatesTotal = candidates.length;
  summary.candidatesCapped = candidates.length > args.maxMemories;
  const toStore = candidates.slice(0, args.maxMemories);

  // Phase 3: Store to BrainX (with rate limiting)
  for (const cand of toStore) {
    const memory = {
      type: cand.classification.type,
      content: truncateContent(cand.text),
      context: `agent:${cand.agent}`,
      tier: cand.classification.importance >= 7 ? 'hot' : 'warm',
      importance: cand.classification.importance,
      category: cand.classification.category,
      tags: ['auto-harvested', `agent:${cand.agent}`, `session:${cand.sessionId.slice(0, 8)}`],
    };

    if (!args.dryRun) {
      await new Promise(r => setTimeout(r, 250));
    }

    const result = await storeToBrainx(memory, args.dryRun);

    if (result.ok) {
      summary.memoriesStored++;
      summary.byAgent[cand.agent].stored = (summary.byAgent[cand.agent].stored || 0) + 1;
      summary.byType[cand.classification.type] = (summary.byType[cand.classification.type] || 0) + 1;
    } else {
      summary.memoriesFailed++;
      if (summary.errors.length < 5) {
        summary.errors.push(result.error?.slice(0, 100));
      }
    }

    if (args.verbose && result.ok) {
      console.error(`[${cand.agent}] ${cand.classification.type}: ${cand.text.slice(0, 80)}...`);
    }
  }

  console.log(JSON.stringify({
    ok: true,
    dryRun: args.dryRun,
    hours: args.hours,
    maxMemories: args.maxMemories,
    ...summary,
  }, null, 2));
}

main().catch(e => {
  console.error(e.stack || e.message);
  process.exit(1);
});
