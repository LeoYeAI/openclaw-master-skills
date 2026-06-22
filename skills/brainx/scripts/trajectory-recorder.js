#!/usr/bin/env node
/**
 * BrainX V5 — Trajectory Recorder
 *
 * Builds problem→solution trajectories from session logs
 * and stores them in brainx_trajectories with embeddings.
 *
 * Usage:
 *   node scripts/trajectory-recorder.js [--hours 24] [--max-sessions 10]
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { Pool } = require('pg');
const OpenAI = require('openai');

// ── Config ──────────────────────────────────────────
const DATABASE_URL = process.env.DATABASE_URL;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!DATABASE_URL) { console.error('DATABASE_URL is required'); process.exit(1); }
if (!OPENAI_API_KEY) { console.error('OPENAI_API_KEY is required'); process.exit(1); }

const pool = new Pool({ connectionString: DATABASE_URL });
const openai = new OpenAI({ apiKey: OPENAI_API_KEY });

const AGENTS_DIR = path.join(process.env.HOME || '', '.openclaw', 'agents');
const DATA_DIR = path.join(__dirname, '..', 'data');
const TRACKING_FILE = path.join(DATA_DIR, 'trajectory-sessions.json');
const MODEL = 'gpt-4.1-mini';
const EMBEDDING_MODEL = 'text-embedding-3-small';
const MAX_CONTENT_CHARS = 12000; // Max session content to send to GPT
const BATCH_DELAY_MS = 1500;

// ── Args ──────────────────────────────────────────
function parseArgs() {
  const argv = process.argv.slice(2);
  const args = { hours: 24, maxSessions: 10 };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--hours') args.hours = parseInt(argv[++i], 10);
    else if (argv[i] === '--max-sessions') args.maxSessions = parseInt(argv[++i], 10);
  }
  return args;
}

// ── Tracking ──────────────────────────────────────
function loadTracking() {
  try {
    if (fs.existsSync(TRACKING_FILE)) {
      return JSON.parse(fs.readFileSync(TRACKING_FILE, 'utf-8'));
    }
  } catch { /* ignore */ }
  return { processed: {} };
}

function saveTracking(tracking) {
  if (!fs.existsSync(DATA_DIR)) fs.mkdirSync(DATA_DIR, { recursive: true });
  fs.writeFileSync(TRACKING_FILE, JSON.stringify(tracking, null, 2));
}

// ── Find recent sessions ──────────────────────────
function findRecentSessions(hoursAgo, maxSessions) {
  const cutoff = Date.now() - (hoursAgo * 60 * 60 * 1000);
  const sessions = [];

  if (!fs.existsSync(AGENTS_DIR)) return sessions;

  const agents = fs.readdirSync(AGENTS_DIR).filter(d => {
    return !['heartbeat', 'monitor'].includes(d);
  });

  for (const agent of agents) {
    const sessDir = path.join(AGENTS_DIR, agent, 'sessions');
    if (!fs.existsSync(sessDir)) continue;

    let files;
    try {
      files = fs.readdirSync(sessDir).filter(f => f.endsWith('.jsonl'));
    } catch { continue; }

    for (const file of files) {
      const filePath = path.join(sessDir, file);
      try {
        const stat = fs.statSync(filePath);
        if (stat.mtimeMs >= cutoff && stat.size > 500) {
          sessions.push({
            agent,
            file,
            path: filePath,
            mtime: stat.mtimeMs,
            size: stat.size
          });
        }
      } catch { continue; }
    }
  }

  // Sort by most recent first, limit
  sessions.sort((a, b) => b.mtime - a.mtime);
  return sessions.slice(0, maxSessions);
}

// ── Parse session JSONL ──────────────────────────
function parseSession(filePath) {
  const lines = fs.readFileSync(filePath, 'utf-8').split('\n').filter(Boolean);
  const messages = [];

  for (const line of lines) {
    try {
      const obj = JSON.parse(line);
      if (obj.type !== 'message') continue;
      const msg = obj.message || {};
      const role = msg.role;
      if (!role || !['user', 'assistant'].includes(role)) continue;

      let content = msg.content;
      if (Array.isArray(content)) {
        content = content
          .filter(c => c && c.type === 'text')
          .map(c => c.text || '')
          .join(' ');
      }
      if (typeof content !== 'string' || content.trim().length === 0) continue;

      messages.push({ role, content: content.trim() });
    } catch { continue; }
  }

  return messages;
}

// ── Compress conversation for GPT ──────────────────
function compressConversation(messages) {
  let text = '';
  for (const msg of messages) {
    const prefix = msg.role === 'user' ? 'USER' : 'ASSISTANT';
    const content = msg.content.substring(0, 800);
    text += `${prefix}: ${content}\n\n`;
    if (text.length > MAX_CONTENT_CHARS) break;
  }
  return text.substring(0, MAX_CONTENT_CHARS);
}

// ── Extract trajectories via GPT ──────────────────
async function extractTrajectories(conversation, agent) {
  const systemPrompt = `You are a trajectory extractor for an AI agent system.
Analyze the conversation and identify PROBLEMS that were SOLVED (or attempted).
For each problem→solution trajectory found, extract:

- problem: clear description of what needed to be solved
- steps: array of {action, result} showing the resolution path (max 5 steps)
- solution: the final solution or approach that worked
- outcome: "success" if solved, "partial" if partly solved, "failed" if not solved
- context: project/topic context (e.g. "brainx-v5", "railway deployment", "email automation")

Only extract meaningful trajectories (not trivial Q&A or greetings).
Return a JSON object: { "trajectories": [...] }
If no meaningful trajectories found, return: { "trajectories": [] }
Respond ONLY with valid JSON.`;

  const response = await openai.chat.completions.create({
    model: MODEL,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: `Agent: ${agent}\n\nConversation:\n${conversation}` }
    ],
    temperature: 0.1,
    response_format: { type: 'json_object' }
  });

  const text = response.choices[0].message.content;
  const parsed = JSON.parse(text);
  return Array.isArray(parsed.trajectories) ? parsed.trajectories : [];
}

// ── Generate embedding ──────────────────────────────
async function generateEmbedding(text) {
  const response = await openai.embeddings.create({
    model: EMBEDDING_MODEL,
    input: text.substring(0, 8000)
  });
  return response.data[0].embedding;
}

// ── Generate trajectory ID ──────────────────────────
function genTrajectoryId() {
  const ts = Date.now();
  const hash = crypto.randomBytes(4).toString('hex');
  return `traj_${ts}_${hash}`;
}

// ── Insert trajectory into DB ──────────────────────
async function insertTrajectory(traj, agent, embedding) {
  const id = genTrajectoryId();
  const query = `
    INSERT INTO brainx_trajectories (id, context, problem, steps, solution, outcome, agent, embedding)
    VALUES ($1, $2, $3, $4::jsonb, $5, $6, $7, $8::vector)
  `;
  const values = [
    id,
    traj.context || null,
    traj.problem,
    JSON.stringify(Array.isArray(traj.steps) ? traj.steps : []),
    traj.solution || null,
    ['success', 'partial', 'failed'].includes(traj.outcome) ? traj.outcome : 'success',
    agent,
    `[${embedding.join(',')}]`
  ];
  await pool.query(query, values);
  return id;
}

// ── Sleep helper ──────────────────────────────────
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// ── Main ──────────────────────────────────────────
async function main() {
  const args = parseArgs();
  const tracking = loadTracking();
  const result = { sessions_processed: 0, trajectories_found: 0, stored: 0, errors: [] };

  try {
    const sessions = findRecentSessions(args.hours, args.maxSessions);

    if (sessions.length === 0) {
      console.log(JSON.stringify(result));
      await pool.end();
      return;
    }

    for (const session of sessions) {
      const sessionKey = `${session.agent}/${session.file}`;

      // Skip already processed
      if (tracking.processed[sessionKey]) {
        continue;
      }

      try {
        const messages = parseSession(session.path);

        // Skip very short sessions (< 4 messages = probably no real problem solving)
        if (messages.length < 4) {
          tracking.processed[sessionKey] = { at: new Date().toISOString(), trajectories: 0 };
          continue;
        }

        const conversation = compressConversation(messages);
        const trajectories = await extractTrajectories(conversation, session.agent);

        let sessionStored = 0;
        for (const traj of trajectories) {
          if (!traj.problem || traj.problem.trim().length < 10) continue;

          try {
            const embeddingText = `${traj.problem} ${traj.solution || ''}`;
            const embedding = await generateEmbedding(embeddingText);
            await insertTrajectory(traj, session.agent, embedding);
            sessionStored++;
            result.stored++;
          } catch (err) {
            result.errors.push({ session: sessionKey, problem: traj.problem?.substring(0, 60), error: err.message });
          }
        }

        result.trajectories_found += trajectories.length;
        result.sessions_processed++;
        tracking.processed[sessionKey] = {
          at: new Date().toISOString(),
          trajectories: sessionStored
        };

        // Delay between sessions
        await sleep(BATCH_DELAY_MS);
      } catch (err) {
        result.errors.push({ session: sessionKey, error: err.message });
      }
    }

    saveTracking(tracking);
  } catch (err) {
    result.errors.push({ phase: 'main', error: err.message });
  }

  console.log(JSON.stringify(result));
  await pool.end();
}

main().catch(err => {
  console.error(JSON.stringify({ error: err.message }));
  pool.end().catch(() => {});
  process.exit(1);
});
