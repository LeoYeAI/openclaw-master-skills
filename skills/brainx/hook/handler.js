/**
 * BrainX V5 Auto-Inject Hook Handler
 *
 * Runs on agent:bootstrap — queries PostgreSQL for hot/warm memories
 * and injects them into the agent's MEMORY.md + BRAINX_CONTEXT.md.
 */

import { createRequire } from "module";
import fs from "node:fs/promises";
import path from "node:path";
import { execFile } from "node:child_process";

const BRAINX_DIR = "/home/clawd/.openclaw/skills/brainx-v5";
const brainxRequire = createRequire(path.join(BRAINX_DIR, "index.js"));

// ─── Agent profiles for context-aware injection ────────────────

import { readFileSync } from "node:fs";

let agentProfiles = {};
try {
  const raw = readFileSync(path.join(BRAINX_DIR, 'hook', 'agent-profiles.json'), 'utf-8');
  agentProfiles = JSON.parse(raw);
} catch {
  // No profiles file — all agents get default (unfiltered) injection
}

// Section markers for MEMORY.md — content between these is replaced each run
const BRAINX_START = "<!-- BRAINX:START -->";
const BRAINX_END = "<!-- BRAINX:END -->";

// ─── Env loading ───────────────────────────────────────────────

function loadEnv() {
  try {
    const dotenv = brainxRequire("dotenv");
    dotenv.config({ path: path.join(BRAINX_DIR, ".env"), quiet: true });
  } catch {}
}

// ─── Singleton pool ────────────────────────────────────────────

let _pool = null;
let _poolUrl = null;

function getPool(dbUrl) {
  if (_pool && _poolUrl === dbUrl) return _pool;
  if (_pool) { _pool.end().catch(() => {}); }
  try {
    const { Pool } = brainxRequire("pg");
    _pool = new Pool({ connectionString: dbUrl, max: 3, idleTimeoutMillis: 30000 });
    _poolUrl = dbUrl;
    _pool.on("error", (err) => {
      console.error("[brainx-inject] Pool background error:", err.message);
      _pool = null;
      _poolUrl = null;
    });
    return _pool;
  } catch (err) {
    console.error("[brainx-inject] Failed to create pool:", err.message);
    _pool = null;
    _poolUrl = null;
    throw err;
  }
}

// ─── Helpers ───────────────────────────────────────────────────

function extractAgentId(sessionKey) {
  if (!sessionKey) return "unknown";
  const parts = sessionKey.split(":");
  return parts.length >= 2 ? parts[1] : "unknown";
}

function ts() {
  return new Date().toISOString().replace("T", " ").replace(/\.\d+Z$/, " UTC");
}

function truncate(str, max = 150) {
  if (!str || str.length <= max) return str || "";
  return str.slice(0, max - 3) + "...";
}

// ─── Retry helpers ─────────────────────────────────────────────

const MAX_RETRIES = 3;
const BASE_DELAY_MS = 500;
const MAX_DELAY_MS = 5000;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function calculateDelay(attempt) {
  const exponential = BASE_DELAY_MS * Math.pow(2, attempt);
  const jitter = Math.random() * 500;
  return Math.min(exponential + jitter, MAX_DELAY_MS);
}

async function withRetry(operation, context = "operation") {
  let lastError;
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      return await operation();
    } catch (err) {
      lastError = err;
      const isRetryable = err.code === 'ECONNREFUSED' || 
                          err.code === 'ETIMEDOUT' ||
                          err.code === 'ECONNRESET' ||
                          err.message?.includes('connection') ||
                          err.message?.includes('timeout');
      
      if (!isRetryable || attempt >= MAX_RETRIES - 1) {
        throw err;
      }
      
      const delay = calculateDelay(attempt);
      console.log(`[brainx-inject] ${context} failed (attempt ${attempt + 1}/${MAX_RETRIES}), retrying in ${Math.round(delay)}ms...`);
      await sleep(delay);
    }
  }
  throw lastError;
}

// ─── DB queries (with retry wrapper) ───────────────────────────

async function queryTopMemories(pool, { limit = 8, minImportance = 5, agentName = null }) {
  // Split into own-agent + cross-agent slots to ensure visibility across agents
  const crossSlots = Math.max(2, Math.floor(limit * 0.3));  // ~30% for other agents
  const ownSlots = limit - crossSlots;

  return withRetry(async () => {
    // 1. Own agent memories (or global if no agent)
    const ownFilter = agentName
      ? `AND (agent = $3 OR agent IS NULL)`
      : '';
    const ownParams = agentName
      ? [minImportance, ownSlots, agentName]
      : [minImportance, ownSlots];
    const { rows: ownRows } = await pool.query(
      `SELECT content, tier, importance, type, agent, context
       FROM brainx_memories
       WHERE tier IN ('hot', 'warm')
         AND importance >= $1
         AND superseded_by IS NULL
         ${ownFilter}
       ORDER BY importance DESC, last_seen DESC NULLS LAST, created_at DESC
       LIMIT $2`,
      ownParams
    );

    // 2. Cross-agent memories (from OTHER agents, prioritizing cross-agent tagged)
    const crossFilter = agentName
      ? `AND agent IS DISTINCT FROM $3 AND agent IS NOT NULL`
      : '';
    const crossParams = agentName
      ? [minImportance, crossSlots, agentName]
      : [minImportance, crossSlots];
    const { rows: crossRows } = await pool.query(
      `SELECT content, tier, importance, type, agent, context
       FROM brainx_memories
       WHERE tier IN ('hot', 'warm')
         AND importance >= $1
         AND superseded_by IS NULL
         ${crossFilter}
       ORDER BY
         CASE WHEN 'cross-agent' = ANY(tags) THEN 1 ELSE 0 END DESC,
         importance DESC, last_seen DESC NULLS LAST, created_at DESC
       LIMIT $2`,
      crossParams
    );

    return [...ownRows, ...crossRows];
  }, "queryTopMemories");
}

async function queryAgentMemories(
  pool,
  agentName,
  { limit = 5, minImportance = 5 }
) {
  return withRetry(async () => {
    const { rows } = await pool.query(
      `SELECT content, tier, importance, type, context
       FROM brainx_memories
       WHERE agent = $1
         AND importance >= $2
         AND superseded_by IS NULL
       ORDER BY importance DESC, last_seen DESC NULLS LAST
       LIMIT $3`,
      [agentName, minImportance, limit]
    );
    return rows;
  }, "queryAgentMemories");
}

async function queryByType(pool, type, { limit = 10, minImportance = 5 }) {
  return withRetry(async () => {
    const { rows } = await pool.query(
      `SELECT content, tier, importance, type, agent, context
       FROM brainx_memories
       WHERE type = $1
         AND tier IN ('hot', 'warm')
         AND importance >= $2
         AND superseded_by IS NULL
       ORDER BY importance DESC, last_seen DESC NULLS LAST
       LIMIT $3`,
      [type, minImportance, limit]
    );
    return rows;
  }, "queryByType");
}

async function queryFacts(pool, { limit = 25 }) {
  return withRetry(async () => {
    const { rows } = await pool.query(
      `SELECT content, tier, importance, context, tags::text AS tags
       FROM brainx_memories
       WHERE type = 'fact'
         AND superseded_by IS NULL
         AND tier IN ('hot', 'warm')
       ORDER BY importance DESC, last_seen DESC NULLS LAST
       LIMIT $1`,
      [limit]
    );
    return rows;
  }, "queryFacts");
}

// ─── Agent-aware query (uses agent-profiles.json) ──────────────

function getAgentProfile(agentName) {
  return agentProfiles[agentName] || null;
}

async function queryAgentAwareMemories(pool, agentName, { limit = 8, minImportance = 5 }) {
  const profile = getAgentProfile(agentName);

  // No profile → fall back to default top memories with cross-agent slots
  if (!profile || (profile.contexts.length === 0 && profile.excludeTypes.length === 0 && profile.boostTypes.length === 0)) {
    return queryTopMemories(pool, { limit, minImportance, agentName });
  }

  // Split into own-agent + cross-agent slots (same strategy as queryTopMemories)
  const crossSlots = Math.max(2, Math.floor(limit * 0.3));
  const ownSlots = limit - crossSlots;

  return withRetry(async () => {
    // Build shared clauses from profile
    let excludeClause = '';
    const sharedParams = [];
    let paramIdx = 3; // $1=minImportance, $2=limit

    if (profile.excludeTypes.length > 0) {
      excludeClause = ` AND type NOT IN (${profile.excludeTypes.map(() => `$${paramIdx++}`).join(',')})`;
      sharedParams.push(...profile.excludeTypes);
    }

    let contextBoostExpr = '0';
    if (profile.contexts.length > 0) {
      const contextPlaceholders = profile.contexts.map(() => `$${paramIdx++}`).join(',');
      sharedParams.push(...profile.contexts);
      contextBoostExpr = `CASE WHEN context IN (${contextPlaceholders}) THEN 2 ELSE 0 END`;
    }

    let boostTypeExpr = '0';
    if (profile.boostTypes.length > 0) {
      const boostPlaceholders = profile.boostTypes.map(() => `$${paramIdx++}`).join(',');
      sharedParams.push(...profile.boostTypes);
      boostTypeExpr = `CASE WHEN type IN (${boostPlaceholders}) THEN 1 ELSE 0 END`;
    }

    // 1. Own-agent memories (agent = agentName OR agent IS NULL)
    const ownAgentParam = paramIdx++;
    const ownParams = [minImportance, ownSlots, ...sharedParams, agentName];
    const ownSql = `SELECT content, tier, importance, type, agent, context
       FROM brainx_memories
       WHERE tier IN ('hot', 'warm')
         AND importance >= $1
         AND superseded_by IS NULL
         AND (agent = $${ownAgentParam} OR agent IS NULL)
         ${excludeClause}
       ORDER BY (${contextBoostExpr} + ${boostTypeExpr}) DESC,
                importance DESC,
                last_seen DESC NULLS LAST,
                created_at DESC
       LIMIT $2`;
    const { rows: ownRows } = await pool.query(ownSql, ownParams);

    // 2. Cross-agent memories (from other agents)
    // Reset paramIdx for cross query
    let crossParamIdx = 3;
    const crossSharedParams = [];
    let crossExcludeClause = '';
    if (profile.excludeTypes.length > 0) {
      crossExcludeClause = ` AND type NOT IN (${profile.excludeTypes.map(() => `$${crossParamIdx++}`).join(',')})`;
      crossSharedParams.push(...profile.excludeTypes);
    }
    let crossContextBoost = '0';
    if (profile.contexts.length > 0) {
      const cp = profile.contexts.map(() => `$${crossParamIdx++}`).join(',');
      crossSharedParams.push(...profile.contexts);
      crossContextBoost = `CASE WHEN context IN (${cp}) THEN 2 ELSE 0 END`;
    }
    let crossBoostType = '0';
    if (profile.boostTypes.length > 0) {
      const bp = profile.boostTypes.map(() => `$${crossParamIdx++}`).join(',');
      crossSharedParams.push(...profile.boostTypes);
      crossBoostType = `CASE WHEN type IN (${bp}) THEN 1 ELSE 0 END`;
    }
    const crossAgentParam = crossParamIdx++;
    const crossParams = [minImportance, crossSlots, ...crossSharedParams, agentName];
    const crossSql = `SELECT content, tier, importance, type, agent, context
       FROM brainx_memories
       WHERE tier IN ('hot', 'warm')
         AND importance >= $1
         AND superseded_by IS NULL
         AND agent IS DISTINCT FROM $${crossAgentParam} AND agent IS NOT NULL
         ${crossExcludeClause}
       ORDER BY
         CASE WHEN 'cross-agent' = ANY(tags) THEN 1 ELSE 0 END DESC,
         (${crossContextBoost} + ${crossBoostType}) DESC,
         importance DESC,
         last_seen DESC NULLS LAST,
         created_at DESC
       LIMIT $2`;
    const { rows: crossRows } = await pool.query(crossSql, crossParams);

    return [...ownRows, ...crossRows];
  }, "queryAgentAwareMemories");
}

// ─── Formatting ────────────────────────────────────────────────

function formatMemoryLine(m, maxLen = 150) {
  const meta = `[${m.tier}/imp:${m.importance}]`;
  return `- **${meta}** ${truncate(m.content, maxLen)}`;
}

function formatMemoryBlock(m) {
  const parts = [`[tier:${m.tier} imp:${m.importance} type:${m.type}`];
  if (m.agent) parts[0] += ` agent:${m.agent}`;
  if (m.context) parts[0] += ` ctx:${m.context}`;
  parts[0] += "]";
  parts.push(truncate(m.content, 2000));
  return parts.join("\n");
}

// ─── MEMORY.md injection ──────────────────────────────────────

function buildMemorySection(agentName, timestamp, teamMems, ownMems) {
  const lines = [BRAINX_START, "", "## BrainX Context (Auto-Injected)", ""];
  lines.push(`**Agent:** ${agentName} | **Updated:** ${timestamp}`);
  lines.push("");

  if (teamMems.length > 0) {
    // Split team memories: own-agent vs cross-agent for balanced display
    const ownTeam = teamMems.filter(m => m.agent === agentName || !m.agent);
    const crossTeam = teamMems.filter(m => m.agent && m.agent !== agentName);

    lines.push("### Top Memories");
    for (const m of ownTeam.slice(0, 5)) {
      lines.push(formatMemoryLine(m));
    }
    lines.push("");

    if (crossTeam.length > 0) {
      lines.push("### Cross-Agent Intel");
      for (const m of crossTeam.slice(0, 3)) {
        lines.push(`- **[${m.agent}/${m.tier}/imp:${m.importance}]** ${(m.content || '').slice(0, 120)}...`);
      }
      lines.push("");
    }
  }

  if (ownMems.length > 0) {
    lines.push(`### My Memories (${agentName})`);
    for (const m of ownMems.slice(0, 4)) {
      lines.push(formatMemoryLine(m));
    }
    lines.push("");
  }

  if (teamMems.length === 0 && ownMems.length === 0) {
    lines.push("*No hot/warm memories with importance >= 5.*");
    lines.push("");
  }

  lines.push(
    `> Full context: \`cat BRAINX_CONTEXT.md\` | Topics: \`cat brainx-topics/<topic>.md\``
  );
  lines.push("", BRAINX_END);
  return lines.join("\n");
}

async function updateMemoryMd(workspaceDir, section) {
  const memPath = path.join(workspaceDir, "MEMORY.md");
  let content = "";
  try {
    content = await fs.readFile(memPath, "utf-8");
  } catch {
    // File doesn't exist — will create with just the section
  }

  // Use lastIndexOf: MEMORY.md templates may reference the markers in
  // instructional text — the real injection block is always the last occurrence.
  const startIdx = content.lastIndexOf(BRAINX_START);
  const endIdx = content.lastIndexOf(BRAINX_END);

  if (startIdx !== -1 && endIdx !== -1) {
    // Replace existing section
    content =
      content.slice(0, startIdx) +
      section +
      content.slice(endIdx + BRAINX_END.length);
  } else {
    // Append
    content = content.trimEnd() + "\n\n" + section + "\n";
  }

  await fs.writeFile(memPath, content, "utf-8");
}

// ─── BRAINX_CONTEXT.md + topic files (backward compat) ───────

async function writeTopicFile(dir, filename, title, memories, timestamp) {
  const filePath = path.join(dir, filename);
  if (memories.length === 0) {
    await fs.writeFile(filePath, `# ${title} — None found\n`, "utf-8");
    return 0;
  }
  const lines = [`# ${title}`, "", `**Updated:** ${timestamp}`, ""];
  for (const m of memories) {
    lines.push(formatMemoryBlock(m));
    lines.push("");
    lines.push("---");
    lines.push("");
  }
  await fs.writeFile(filePath, lines.join("\n"), "utf-8");
  return memories.length;
}

async function writeBrainxContext(
  workspaceDir,
  agentName,
  timestamp,
  counts,
  facts,
  ownMems
) {
  const topicsDir = path.join(workspaceDir, "brainx-topics");
  const contextPath = path.join(workspaceDir, "BRAINX_CONTEXT.md");

  // Compact index — always loaded
  const lines = [
    "# BrainX V5 Context (Auto-Injected)",
    "",
    `**Agent:** ${agentName} | **Updated:** ${timestamp}`,
    "**Mode:** Compact index — read topic files with `cat brainx-topics/<file>.md` when you need detail",
    "",
  ];

  // Facts summary
  lines.push(
    `## Facts (${counts.facts}) -> \`brainx-topics/facts.md\``
  );
  if (facts.length > 0) {
    for (const f of facts.slice(0, 5)) {
      lines.push(`  - [${f.tier}] ${truncate(f.content, 100)}`);
    }
  } else {
    lines.push("  *Empty*");
  }
  lines.push("");

  // Own memories summary
  lines.push(
    `## My memories (${counts.own}) -> \`brainx-topics/own.md\``
  );
  if (ownMems.length > 0) {
    for (const m of ownMems.slice(0, 3)) {
      lines.push(`  - ${truncate(m.content, 100)}`);
    }
  } else {
    lines.push("  *No own memories*");
  }
  lines.push("");

  // Topics directory table
  lines.push("## Topics");
  lines.push("");
  lines.push("| Topic | Items | File |");
  lines.push("|-------|-------|------|");
  lines.push(
    `| Decisions | ${counts.decisions} | \`brainx-topics/decisions.md\` |`
  );
  lines.push(
    `| Gotchas | ${counts.gotchas} | \`brainx-topics/gotchas.md\` |`
  );
  lines.push(
    `| Learnings | ${counts.learnings} | \`brainx-topics/learnings.md\` |`
  );
  lines.push(`| Team | ${counts.team} | \`brainx-topics/team.md\` |`);
  lines.push(`| Facts | ${counts.facts} | \`brainx-topics/facts.md\` |`);
  lines.push(`| Own | ${counts.own} | \`brainx-topics/own.md\` |`);
  lines.push("");

  lines.push("---");
  lines.push(
    '**Save fact:** `brainx add --type fact --tier hot --importance 8 --context "project:NAME" --content "..."`'
  );

  await fs.writeFile(contextPath, lines.join("\n") + "\n", "utf-8");
  return lines.join("\n").length;
}

// ─── Telemetry ─────────────────────────────────────────────────

async function logInjection(pool, agentName, ownCount, teamCount, totalChars) {
  try {
    await pool.query(
      `INSERT INTO brainx_pilot_log (agent, own_memories, team_memories, total_chars, injected_at)
       VALUES ($1, $2, $3, $4, NOW())`,
      [agentName, ownCount, teamCount, totalChars]
    );
  } catch {}
}

// ─── Main handler ──────────────────────────────────────────────

const handler = async (event) => {
  if (event.type !== "agent" || event.action !== "bootstrap") return;

  const t0 = Date.now();

  try {
    loadEnv();

    const dbUrl = process.env.DATABASE_URL;
    if (!dbUrl) {
      console.error("[brainx-inject] DATABASE_URL not set, skipping");
      return;
    }

    const workspaceDir = event.context?.workspaceDir;
    if (!workspaceDir) {
      console.error("[brainx-inject] No workspaceDir in event context, skipping");
      return;
    }

    // Extract agent ID from multiple sources (event context, session key, env)
    const agentName = event.agentId || event.agent || extractAgentId(event.sessionKey) || process.env.OPENCLAW_AGENT_ID || 'unknown';
    const timestamp = ts();

    const pool = getPool(dbUrl);

    {
      // Run all queries in parallel (team memories are now agent-aware)
      const [teamMems, ownMems, facts, decisions, learnings, gotchas] =
        await Promise.all([
          queryAgentAwareMemories(pool, agentName, { limit: 12, minImportance: 5 }),
          queryAgentMemories(pool, agentName, { limit: 5, minImportance: 5 }),
          queryFacts(pool, { limit: 25 }),
          queryByType(pool, "decision", { limit: 8, minImportance: 5 }),
          queryByType(pool, "learning", { limit: 8, minImportance: 5 }),
          queryByType(pool, "gotcha", { limit: 10, minImportance: 3 }),
        ]);

      // 1. Update MEMORY.md (primary injection path)
      const memSection = buildMemorySection(
        agentName,
        timestamp,
        teamMems,
        ownMems
      );
      await updateMemoryMd(workspaceDir, memSection);

      // 2. Write topic files (backward compat)
      const topicsDir = path.join(workspaceDir, "brainx-topics");
      await fs.mkdir(topicsDir, { recursive: true });

      const [, , , , ,] = await Promise.all([
        writeTopicFile(
          topicsDir,
          "facts.md",
          "Project Facts",
          facts,
          timestamp
        ),
        writeTopicFile(
          topicsDir,
          "decisions.md",
          "Decisions",
          decisions,
          timestamp
        ),
        writeTopicFile(
          topicsDir,
          "learnings.md",
          "Learnings & Insights",
          learnings,
          timestamp
        ),
        writeTopicFile(
          topicsDir,
          "team.md",
          "Team Knowledge (High Importance)",
          teamMems,
          timestamp
        ),
        writeTopicFile(
          topicsDir,
          "own.md",
          `Agent: ${agentName} — My Memories`,
          ownMems,
          timestamp
        ),
      ]);

      const counts = {
        facts: facts.length,
        decisions: decisions.length,
        learnings: learnings.length,
        team: teamMems.length,
        own: ownMems.length,
        gotchas: gotchas.length,
      };

      // 3. Write BRAINX_CONTEXT.md (compact index)
      const indexChars = await writeBrainxContext(
        workspaceDir,
        agentName,
        timestamp,
        counts,
        facts,
        ownMems
      );

      // Write gotchas topic with real data from DB
      await writeTopicFile(topicsDir, "gotchas.md", "Gotchas & Traps", gotchas, timestamp);

      // 4. Telemetry
      await logInjection(
        pool,
        agentName,
        ownMems.length,
        teamMems.length,
        memSection.length + indexChars
      );

      const elapsed = Date.now() - t0;
      console.log(
        `[brainx-inject] agent=${agentName} team=${teamMems.length} own=${ownMems.length} facts=${facts.length} decisions=${decisions.length} ${elapsed}ms`
      );
    }
  } catch (err) {
    const elapsed = Date.now() - t0;
    const errorMsg = err instanceof Error ? err.message : String(err);
    
    // Log error but don't crash the agent bootstrap
    console.error(`[brainx-inject] Failed after ${elapsed}ms: ${errorMsg}`);
    
    // Write a minimal fallback to MEMORY.md so the agent knows BrainX had issues
    try {
      const workspaceDir = event.context?.workspaceDir;
      if (workspaceDir) {
        const fallbackSection = `${BRAINX_START}\n\n## BrainX Context (Auto-Injected)\n\n**⚠️ BrainX injection failed:** ${errorMsg}\n\n> Run \`brainx health\` to check status\n\n${BRAINX_END}`;
        await updateMemoryMd(workspaceDir, fallbackSection);
      }
    } catch (fallbackErr) {
      // If even fallback fails, just log it
      console.error("[brainx-inject] Fallback write also failed:", fallbackErr);
    }
  }
};

export default handler;
