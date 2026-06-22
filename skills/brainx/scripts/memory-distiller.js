#!/usr/bin/env node
/**
 * BrainX V5 — Memory Distiller (LLM-powered)
 * 
 * Reads session transcripts and uses a cheap/fast LLM to extract
 * ALL types of memories: personal facts, financial data, preferences,
 * project details, relationships, deadlines, goals, etc.
 * 
 * Unlike the regex-based extractors, this UNDERSTANDS context.
 * 
 * Usage:
 *   node memory-distiller.js [--hours 8] [--agent coder] [--dry-run] [--verbose] [--model openai/gpt-4.1-mini]
 * 
 * Designed to run as cron every 4-8h.
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const AGENTS_DIR = path.join(process.env.HOME || '', '.openclaw', 'agents');
const BRAINX_DIR = path.join(__dirname, '..');

// ── Config ────────────────────────────────────────────
const DEFAULT_MODEL = process.env.BRAINX_DISTILLER_MODEL || 'gpt-4.1-mini';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const MAX_TRANSCRIPT_CHARS = 12000; // Per session chunk sent to LLM
const MAX_MEMORIES_PER_SESSION = 15;

// ── Args ──────────────────────────────────────────────
function parseArgs() {
  const args = {};
  const argv = process.argv.slice(2);
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--hours') args.hours = parseInt(argv[++i], 10);
    else if (argv[i] === '--dry-run') args.dryRun = true;
    else if (argv[i] === '--agent') args.agentFilter = argv[++i];
    else if (argv[i] === '--verbose') args.verbose = true;
    else if (argv[i] === '--model') args.model = argv[++i];
    else if (argv[i] === '--max-sessions') args.maxSessions = parseInt(argv[++i], 10);
  }
  return {
    hours: args.hours || 8,
    dryRun: args.dryRun || false,
    agentFilter: args.agentFilter || null,
    verbose: args.verbose || false,
    model: args.model || DEFAULT_MODEL,
    maxSessions: args.maxSessions || 20,
  };
}

// ── Session Discovery ─────────────────────────────────
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
      if (stat.mtimeMs >= cutoff && stat.size > 500) {
        sessions.push({ agent, path: fullPath, sessionId: file.replace('.jsonl', ''), modified: stat.mtimeMs, size: stat.size });
      }
    }
  }
  return sessions.sort((a, b) => b.modified - a.modified);
}

// ── Transcript Builder ────────────────────────────────
function buildTranscript(filePath, maxChars) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n').filter(Boolean);
  const messages = [];
  let totalChars = 0;

  for (const line of lines) {
    try {
      const entry = JSON.parse(line);
      if (entry.type !== 'message' || !entry.message) continue;
      const role = entry.message.role;
      if (!['assistant', 'user'].includes(role)) continue;

      let text = '';
      if (Array.isArray(entry.message.content)) {
        text = entry.message.content
          .filter(b => b.type === 'text' && b.text)
          .map(b => b.text)
          .join('\n');
      } else if (typeof entry.message.content === 'string') {
        text = entry.message.content;
      }

      if (!text || text === 'NO_REPLY' || text === 'HEARTBEAT_OK') continue;
      if (/^💓|^🦞\s*✅/.test(text) && text.length < 100) continue;

      // Truncate individual messages
      if (text.length > 1500) text = text.slice(0, 1500) + '…';

      if (totalChars + text.length > maxChars) break;
      messages.push(`[${role}]: ${text}`);
      totalChars += text.length;
    } catch { /* skip */ }
  }

  return messages.join('\n\n');
}

// ── LLM Call ──────────────────────────────────────────
const EXTRACTION_PROMPT = `You are a memory extraction system. Read the conversation transcript below and extract ALL important facts, data points, and memories that would be valuable to remember across sessions.

Extract these types of memories:

1. **FACTS** (type=fact): Concrete data points
   - URLs, endpoints, service names, configs
   - Personal info mentioned (birthdays, locations, preferences)
   - Financial figures (budgets, costs, prices, accounts)
   - Contact info (names, roles, companies, relationships)
   - Deadlines, dates, schedules
   - Account/subscription details

2. **DECISIONS** (type=decision): Choices made
   - Technical decisions (which tool/approach to use)
   - Business decisions (pricing, strategy)
   - Any "we decided to..." or "vamos a..."

3. **LEARNINGS** (type=learning): Things discovered
   - Bugs found and how they were fixed
   - How something works (that wasn't obvious)
   - Workarounds discovered

4. **GOTCHAS** (type=gotcha): Traps to avoid
   - Things that break easily
   - Common mistakes
   - "Don't do X because Y"

5. **PREFERENCES** (type=fact, category=preference): How the user likes things
   - Communication style preferences
   - Tool preferences
   - Workflow preferences

For each memory, output a JSON object with:
- type: fact|decision|learning|gotcha
- content: The distilled fact (concise but complete, 1-3 sentences max)
- category: personal|financial|contact|preference|goal|relationship|business|client|deadline|infrastructure|project_registry|error|correction|best_practice|routine|context
- importance: 1-10 (10=critical, 7+=significant, 5=useful, <5=minor)
- context: "project:NAME" or "personal:TOPIC" or "business:TOPIC"
- tier: hot (critical/frequent) | warm (useful) | cold (archival)

RULES:
- Extract FACTS, not conversation. "User asked about X" is NOT a memory. "X costs $500/month" IS.
- Be concise. Each memory should be 1-3 sentences of distilled information.
- Skip greetings, small talk, status confirmations, code dumps, tool outputs.
- Prefer Spanish if the conversation is in Spanish.
- If nothing worth remembering, return {"memories": []}.
- Output a JSON object with a "memories" array. No markdown, no explanation.
- Focus on WHAT WAS DECIDED/DISCOVERED/CONFIGURED, not the conversation flow.

Conversation transcript:
`;

async function probeOpenAIAuth(model = DEFAULT_MODEL) {
  if (!OPENAI_API_KEY) {
    return { tested: false, ok: false, reason: 'missing_key' };
  }

  try {
    const res = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        messages: [{ role: 'user', content: 'Reply only with OK' }],
        temperature: 0,
        max_tokens: 5,
      }),
    });

    if (!res.ok) {
      const err = await res.text();
      return {
        tested: true,
        ok: false,
        status: res.status,
        error: err.slice(0, 300),
      };
    }

    return { tested: true, ok: true, status: res.status };
  } catch (e) {
    return {
      tested: true,
      ok: false,
      reason: 'probe_failed',
      error: (e.message || String(e)).slice(0, 300),
    };
  }
}

async function callLLM(transcript, model) {
  if (!OPENAI_API_KEY) throw new Error('OPENAI_API_KEY required');

  const res = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${OPENAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      messages: [
        { role: 'system', content: EXTRACTION_PROMPT },
        { role: 'user', content: transcript },
      ],
      temperature: 0.1,
      max_tokens: 4000,
      response_format: { type: 'json_object' },
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    const code = res.status === 401 ? 'OPENAI_AUTH_401' : `OPENAI_HTTP_${res.status}`;
    throw new Error(`${code}: ${err.slice(0, 300)}`);
  }

  const data = await res.json();
  const content = data.choices?.[0]?.message?.content || '[]';

  try {
    const parsed = JSON.parse(content);
    // Handle both {memories: [...]} and [...] formats
    const memories = Array.isArray(parsed) ? parsed : (parsed.memories || parsed.facts || parsed.items || []);
    return {
      memories: memories.slice(0, MAX_MEMORIES_PER_SESSION),
      usage: data.usage || {},
    };
  } catch {
    return { memories: [], usage: data.usage || {}, parseError: true };
  }
}

// ── Store ─────────────────────────────────────────────
let _rag = null;
function getRag() {
  if (!_rag) _rag = require(path.join(BRAINX_DIR, 'lib', 'openai-rag'));
  return _rag;
}

async function storeMemory(mem, agent, sessionId, dryRun) {
  if (dryRun) return { ok: true, dryRun: true };
  try {
    const rag = getRag();
    const validTypes = ['fact', 'decision', 'learning', 'gotcha', 'note'];
    const validCategories = [
      'learning', 'error', 'feature_request', 'correction', 'knowledge_gap', 'best_practice',
      'infrastructure', 'project_registry',
      'personal', 'financial', 'contact', 'preference', 'goal', 'relationship', 'health',
      'business', 'client', 'deadline', 'routine', 'context',
    ];

    const type = validTypes.includes(mem.type) ? mem.type : 'note';
    const category = validCategories.includes(mem.category) ? mem.category : null;
    const tier = ['hot', 'warm', 'cold', 'archive'].includes(mem.tier) ? mem.tier : 'warm';
    const importance = Math.max(1, Math.min(10, parseInt(mem.importance, 10) || 5));

    const result = await rag.storeMemory({
      id: `dist_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`,
      type,
      content: String(mem.content || '').slice(0, 2000),
      context: String(mem.context || `agent:${agent}`).slice(0, 200),
      tier,
      importance,
      agent,
      tags: ['distilled', `agent:${agent}`, `session:${sessionId.slice(0, 8)}`],
      status: 'pending',
      category,
    });
    return { ok: true, id: result?.id, merged: result?.dedupe_merged };
  } catch (e) {
    return { ok: false, error: (e.message || String(e)).slice(0, 200) };
  }
}

// ── Tracking: skip already-distilled sessions ─────────
function getDistilledLog() {
  const logPath = path.join(BRAINX_DIR, 'data', 'distilled-sessions.json');
  try {
    return JSON.parse(fs.readFileSync(logPath, 'utf8'));
  } catch {
    return {};
  }
}

function saveDistilledLog(log) {
  const logPath = path.join(BRAINX_DIR, 'data', 'distilled-sessions.json');
  fs.mkdirSync(path.dirname(logPath), { recursive: true });
  fs.writeFileSync(logPath, JSON.stringify(log, null, 2));
}

// ── Main ──────────────────────────────────────────────
async function main() {
  const args = parseArgs();
  const sessions = findRecentSessions(args.hours, args.agentFilter);
  const distilledLog = getDistilledLog();

  const summary = {
    sessions: sessions.length,
    processed: 0,
    skipped: 0,
    memoriesExtracted: 0,
    memoriesStored: 0,
    memoriesFailed: 0,
    memoriesMerged: 0,
    tokensUsed: { prompt: 0, completion: 0 },
    errors: [],
    authProbe: null,
    verifiedRootCause: null,
  };

  const toProcess = sessions
    .filter(s => {
      const key = `${s.agent}:${s.sessionId}`;
      const prev = distilledLog[key];
      // Re-process if file was modified since last distill
      if (prev && prev.modified >= s.modified) {
        summary.skipped++;
        return false;
      }
      return true;
    })
    .slice(0, args.maxSessions);

  for (const session of toProcess) {
    const transcript = buildTranscript(session.path, MAX_TRANSCRIPT_CHARS);
    if (transcript.length < 200) {
      summary.skipped++;
      continue;
    }

    try {
      if (args.verbose) process.stderr.write(`[distiller] Processing ${session.agent}/${session.sessionId} (${transcript.length} chars)...\n`);

      const { memories, usage, parseError } = await callLLM(transcript, args.model);

      summary.tokensUsed.prompt += usage.prompt_tokens || 0;
      summary.tokensUsed.completion += usage.completion_tokens || 0;

      if (parseError) {
        summary.errors.push(`Parse error for ${session.agent}/${session.sessionId}`);
        continue;
      }

      summary.memoriesExtracted += memories.length;

      for (const mem of memories) {
        if (!mem.content || String(mem.content).length < 10) continue;

        const result = await storeMemory(mem, session.agent, session.sessionId, args.dryRun);
        if (result.ok) {
          summary.memoriesStored++;
          if (result.merged) summary.memoriesMerged++;
        } else {
          summary.memoriesFailed++;
          if (summary.errors.length < 10) summary.errors.push(result.error);
        }
        // Rate limit: 150ms between embedding calls
        await new Promise(r => setTimeout(r, 150));
      }

      summary.processed++;

      // Track this session as distilled
      if (!args.dryRun) {
        const key = `${session.agent}:${session.sessionId}`;
        distilledLog[key] = { modified: session.modified, at: Date.now(), memories: memories.length };
      }

      // Rate limit between LLM calls: 500ms
      await new Promise(r => setTimeout(r, 500));

    } catch (e) {
      summary.errors.push(`${session.agent}/${session.sessionId}: ${(e.message || '').slice(0, 150)}`);
    }
  }

  if (summary.errors.some(e => String(e).includes('OPENAI_AUTH_401'))) {
    summary.authProbe = await probeOpenAIAuth(args.model);
    summary.verifiedRootCause = summary.authProbe?.ok === false && summary.authProbe?.status === 401
      ? 'verified_openai_auth_401'
      : null;
  }

  if (!args.dryRun) saveDistilledLog(distilledLog);

  console.log(JSON.stringify(summary, null, 2));
}

main().catch(e => {
  console.error(e.message || e);
  process.exit(1);
});
