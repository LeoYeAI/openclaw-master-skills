#!/usr/bin/env node
/**
 * BrainX V5 — Fact Extractor
 * 
 * Extracts operational FACTS from session logs:
 * - URLs (production, staging, API endpoints)
 * - Service mappings (Railway service → repo → URL)
 * - Config values (env vars, API keys names, ports)
 * - Project structure (directories, branches, deploy targets)
 * 
 * Unlike the session-harvester (which stores conversation fragments),
 * this extracts STRUCTURED FACTS that prevent agent amnesia.
 * 
 * Usage:
 *   node fact-extractor.js [--hours 24] [--dry-run] [--agent coder] [--verbose]
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const AGENTS_DIR = path.join(process.env.HOME || '', '.openclaw', 'agents');
const BRAINX_DIR = path.join(__dirname, '..');

// ── Args ──────────────────────────────────────────────
function parseArgs() {
  const args = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--hours') args.hours = parseInt(argv[++i], 10);
    else if (argv[i] === '--dry-run') args.dryRun = true;
    else if (argv[i] === '--agent') args.agentFilter = argv[++i];
    else if (argv[i] === '--verbose') args.verbose = true;
  }
  return {
    hours: args.hours || 24,
    dryRun: args.dryRun || false,
    agentFilter: args.agentFilter || null,
    verbose: args.verbose || false,
  };
}

// ── Session Discovery ──────────────────────────────────
function findRecentSessions(hoursAgo, agentFilter) {
  const cutoff = Date.now() - (hoursAgo * 60 * 60 * 1000);
  const sessions = [];
  if (!fs.existsSync(AGENTS_DIR)) return sessions;

  const agents = fs.readdirSync(AGENTS_DIR).filter(d => {
    if (agentFilter) return d === agentFilter;
    return !['heartbeat', 'monitor'].includes(d);
  });

  for (const agent of agents) {
    const sessDir = path.join(AGENTS_DIR, agent, 'sessions');
    if (!fs.existsSync(sessDir)) continue;
    for (const file of fs.readdirSync(sessDir).filter(f => f.endsWith('.jsonl'))) {
      const fullPath = path.join(sessDir, file);
      const stat = fs.statSync(fullPath);
      if (stat.mtimeMs >= cutoff) {
        sessions.push({ agent, path: fullPath, sessionId: file.replace('.jsonl', '') });
      }
    }
  }
  return sessions;
}

// ── Message Extraction ─────────────────────────────────
function extractAllMessages(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  return content.split('\n').filter(Boolean).map(line => {
    try {
      const entry = JSON.parse(line);
      if (entry.type !== 'message' || !entry.message) return null;
      const role = entry.message.role;
      if (!['assistant', 'user'].includes(role)) return null;
      const texts = [];
      if (Array.isArray(entry.message.content)) {
        for (const block of entry.message.content) {
          if (block.type === 'text' && block.text) texts.push(block.text);
        }
      } else if (typeof entry.message.content === 'string') {
        texts.push(entry.message.content);
      }
      return texts.length ? { role, text: texts.join('\n'), ts: entry.timestamp } : null;
    } catch { return null; }
  }).filter(Boolean);
}

// ── Fact Patterns ──────────────────────────────────────
const FACT_EXTRACTORS = [
  // Railway URLs
  {
    name: 'railway_url',
    pattern: /https?:\/\/[\w-]+(?:\.up)?\.railway\.app\b[^\s)>\]"']*/gi,
    build: (match, ctx) => ({
      type: 'fact',
      category: 'infrastructure',
      content: `Railway URL: ${match[0]}`,
      importance: 8,
      tier: 'hot',
      tags: ['railway', 'url', 'auto-extracted'],
    }),
  },
  // Railway service mappings: "service X" or "servicio X"  
  {
    name: 'railway_service',
    pattern: /(?:railway\s+)?(?:servicio?|service)\s+[`"']?([\w-]{3,})[`"']?\s*(?:→|->|=|:|\()\s*(?:frontend|backend|api|worker|web|app)/gi,
    build: (match, ctx) => ({
      type: 'fact',
      category: 'infrastructure',
      content: `Railway service mapping: ${match[0].trim()}`,
      importance: 8,
      tier: 'hot',
      tags: ['railway', 'service', 'mapping', 'auto-extracted'],
    }),
  },
  // Vercel/Netlify URLs
  {
    name: 'vercel_url',
    pattern: /https?:\/\/[\w-]+\.(?:vercel|netlify)\.app\b[^\s)>\]"']*/gi,
    build: (match) => ({
      type: 'fact',
      category: 'infrastructure',
      content: `Deploy URL: ${match[0]}`,
      importance: 8,
      tier: 'hot',
      tags: ['deploy', 'url', 'auto-extracted'],
    }),
  },
  // GitHub repos
  {
    name: 'github_repo',
    pattern: /(?:repo(?:sitorio?)?|repositorio?)\s*(?::|→|->|=)?\s*(?:https?:\/\/github\.com\/)?([\w-]+\/[\w.-]+)/gi,
    build: (match) => ({
      type: 'fact',
      category: 'project_registry',
      content: `GitHub repo: ${match[1] || match[0]}`,
      importance: 7,
      tier: 'hot',
      tags: ['github', 'repo', 'auto-extracted'],
    }),
  },
  // Frontend/Backend URL declarations
  {
    name: 'service_url_declaration',
    pattern: /(?:frontend|backend|api|dashboard)\s*(?:URL|endpoint|link|dirección|url)\s*(?::|→|->|=|es)\s*(https?:\/\/[^\s)>\]"']+)/gi,
    build: (match) => ({
      type: 'fact',
      category: 'infrastructure',
      content: `Service URL: ${match[0].trim()}`,
      importance: 9,
      tier: 'hot',
      tags: ['url', 'service', 'auto-extracted'],
    }),
  },
  // Root directory / project structure
  {
    name: 'root_directory',
    pattern: /(?:root\s+dir(?:ectory)?|directorio\s+raíz?|carpeta\s+(?:principal|raíz?))\s*(?::|→|->|=|`)\s*[`"']?([\w./-]{2,})[`"']?/gi,
    build: (match) => ({
      type: 'fact',
      category: 'project_registry',
      content: `Project root directory: ${match[0].trim()}`,
      importance: 7,
      tier: 'warm',
      tags: ['project', 'directory', 'auto-extracted'],
    }),
  },
  // Port declarations
  {
    name: 'port_config',
    pattern: /(?:PORT|puerto)\s*(?:=|:)\s*(\d{2,5})\b/gi,
    build: (match) => ({
      type: 'fact',
      category: 'infrastructure',
      content: `Port config: ${match[0].trim()}`,
      importance: 6,
      tier: 'warm',
      tags: ['config', 'port', 'auto-extracted'],
    }),
  },
  // Database URLs (sanitized)
  {
    name: 'database_url',
    pattern: /(?:DATABASE_URL|database|db)\s*(?:=|:)\s*(postgres(?:ql)?:\/\/[^\s"']+)/gi,
    build: (match) => {
      // Sanitize: keep host/db name, remove credentials
      const url = match[1] || match[0];
      const sanitized = url.replace(/\/\/[^@]+@/, '//***@');
      return {
        type: 'fact',
        category: 'infrastructure',
        content: `Database: ${sanitized}`,
        importance: 7,
        tier: 'warm',
        tags: ['database', 'config', 'auto-extracted'],
      };
    },
  },
  // Explicit project-to-service mappings in conversation
  {
    name: 'project_service_map',
    pattern: /[`"*]*([a-z][\w-]{2,})[`"*]*\s*(?:→|->|=|es el?|is the?)\s*(?:el\s+)?(?:frontend|backend|api|web|dashboard|worker|service)\b/gi,
    build: (match) => ({
      type: 'fact',
      category: 'project_registry',
      content: `Project mapping: ${match[0].trim()}`,
      importance: 8,
      tier: 'hot',
      tags: ['project', 'mapping', 'auto-extracted'],
    }),
  },
  // Branch info
  {
    name: 'branch_info',
    pattern: /(?:branch|rama)\s*(?::|=|→|->)\s*[`"']?([\w./-]{2,60})[`"']?/gi,
    build: (match) => ({
      type: 'fact',
      category: 'project_registry',
      content: `Branch: ${match[0].trim()}`,
      importance: 6,
      tier: 'warm',
      tags: ['git', 'branch', 'auto-extracted'],
    }),
  },
];

// ── Dedup ──────────────────────────────────────────────
function factKey(content) {
  // Normalize for dedup: lowercase, strip whitespace variations
  return crypto.createHash('sha256')
    .update(content.toLowerCase().replace(/\s+/g, ' ').trim())
    .digest('hex')
    .slice(0, 20);
}

// ── Store ──────────────────────────────────────────────
let _rag = null;
function getRag() {
  if (!_rag) _rag = require(path.join(BRAINX_DIR, 'lib', 'openai-rag'));
  return _rag;
}

async function storeFact(fact, agent, sessionId, dryRun) {
  if (dryRun) return { ok: true, dryRun: true };
  try {
    const rag = getRag();
    const result = await rag.storeMemory({
      id: `fact_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
      type: fact.type,
      content: fact.content,
      context: fact.context || `project:global`,
      tier: fact.tier || 'hot',
      importance: fact.importance || 8,
      agent: agent,
      tags: [...(fact.tags || []), `session:${sessionId.slice(0, 8)}`],
      status: 'pending',
      category: fact.category || 'infrastructure',
    });
    return { ok: true, id: result?.id, merged: result?.dedupe_merged };
  } catch (e) {
    return { ok: false, error: (e.message || String(e)).slice(0, 200) };
  }
}

// ── Main ───────────────────────────────────────────────
async function main() {
  const args = parseArgs();
  const sessions = findRecentSessions(args.hours, args.agentFilter);
  
  const seen = new Set();
  const facts = [];
  const summary = { sessions: sessions.length, facts: 0, stored: 0, failed: 0, deduped: 0, dryRun: args.dryRun };

  // Also check existing facts in DB to avoid re-extracting
  try {
    const db = require(path.join(BRAINX_DIR, 'lib', 'db'));
    const existing = await db.query(
      `SELECT LEFT(content, 300) as content FROM brainx_memories WHERE type = 'fact' AND superseded_by IS NULL`
    );
    for (const row of existing.rows) {
      seen.add(factKey(row.content));
    }
    if (args.verbose) console.error(`[fact-extractor] ${seen.size} existing facts in DB`);
  } catch (e) {
    if (args.verbose) console.error(`[fact-extractor] Could not check existing: ${e.message}`);
  }

  for (const session of sessions) {
    const messages = extractAllMessages(session.path);
    
    for (const msg of messages) {
      for (const extractor of FACT_EXTRACTORS) {
        // Reset regex lastIndex
        extractor.pattern.lastIndex = 0;
        let match;
        while ((match = extractor.pattern.exec(msg.text)) !== null) {
          const fact = extractor.build(match, { agent: session.agent, role: msg.role });
          if (!fact) continue;
          
          const key = factKey(fact.content);
          if (seen.has(key)) {
            summary.deduped++;
            continue;
          }
          seen.add(key);
          
          facts.push({ ...fact, agent: session.agent, sessionId: session.sessionId });
        }
      }
    }
  }

  summary.facts = facts.length;

  // Store facts
  for (const fact of facts) {
    const result = await storeFact(fact, fact.agent, fact.sessionId, args.dryRun);
    if (result.ok) summary.stored++;
    else {
      summary.failed++;
      if (args.verbose) console.error(`[fact-extractor] Failed: ${result.error}`);
    }
    // Rate limit: 100ms between API calls
    await new Promise(r => setTimeout(r, 100));
  }

  console.log(JSON.stringify(summary, null, 2));
}

main().catch(e => {
  console.error(e.message || e);
  process.exit(1);
});
