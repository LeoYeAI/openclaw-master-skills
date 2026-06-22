/**
 * BrainX Advisory System
 * Pre-action advisory that queries relevant memories before an agent executes a tool.
 */

const crypto = require('crypto');
const db = require('./db');
const rag = require('./openai-rag');

// ─── High-risk tool registry ──────────────────────────────────

const HIGH_RISK_TOOLS = new Set([
  'exec', 'deploy', 'railway', 'delete', 'rm', 'drop',
  'git push', 'git force-push', 'migration', 'cron',
  'message send', 'email send'
]);

/**
 * Check if a tool name is considered high-risk.
 * Matches exact tool names and also checks the first word (e.g. "git push" matches "git").
 * @param {string} tool
 * @returns {boolean}
 */
function isHighRisk(tool) {
  if (!tool) return false;
  return HIGH_RISK_TOOLS.has(tool) ||
    HIGH_RISK_TOOLS.has(tool.split(' ')[0]);
}

// Cooldown: don't spam same advice within this window (ms)
const ADVISORY_COOLDOWN_MS = parseInt(process.env.BRAINX_ADVISORY_COOLDOWN_MS || '300000', 10); // 5 min default

function makeAdvisoryId() {
  return `adv_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
}

/**
 * Build a search query string from action context for embedding similarity.
 */
function buildSearchQuery(actionContext) {
  const parts = [];
  if (actionContext.tool) parts.push(`tool:${actionContext.tool}`);
  if (actionContext.args) {
    try {
      const argsObj = typeof actionContext.args === 'string' ? JSON.parse(actionContext.args) : actionContext.args;
      // Include key arg values for better semantic match
      for (const [k, v] of Object.entries(argsObj)) {
        if (typeof v === 'string' && v.length < 200) parts.push(`${k}:${v}`);
      }
    } catch (_) {
      parts.push(String(actionContext.args));
    }
  }
  if (actionContext.project) parts.push(`project:${actionContext.project}`);
  if (actionContext.agent) parts.push(`agent:${actionContext.agent}`);
  return parts.join(' ');
}

/**
 * Check cooldown: was there a recent advisory for this agent+tool?
 */
async function isOnCooldown(agent, tool) {
  const cutoff = new Date(Date.now() - ADVISORY_COOLDOWN_MS);
  const res = await db.query(
    `SELECT id FROM brainx_advisories
     WHERE agent = $1 AND tool = $2 AND created_at > $3
     ORDER BY created_at DESC LIMIT 1`,
    [agent || 'unknown', tool, cutoff]
  );
  return res.rows.length > 0;
}

/**
 * Query memories relevant to the action context.
 */
async function queryRelevantMemories(searchQuery, limit = 5) {
  const rows = await rag.search(searchQuery, {
    limit,
    minSimilarity: 0.25,
    minImportance: 5,
    tierFilter: null, // we'll filter hot/warm in SQL
    contextFilter: null
  });

  // Filter to hot/warm and not superseded (search already excludes superseded)
  return rows.filter(r => r.tier === 'hot' || r.tier === 'warm');
}

/**
 * Query trajectories for similar problem→solution paths.
 */
async function queryTrajectories(searchQuery, limit = 3) {
  try {
    const embedding = await rag.embed(searchQuery);
    const res = await db.query(
      `SELECT id, context, problem, solution, outcome,
              1 - (embedding <=> $1::vector) AS similarity
       FROM brainx_trajectories
       WHERE outcome IN ('success', 'partial')
       ORDER BY similarity DESC
       LIMIT $2`,
      [JSON.stringify(embedding), limit]
    );
    return res.rows.filter(r => (r.similarity ?? 0) >= 0.25);
  } catch (_) {
    return [];
  }
}

/**
 * Query patterns for recurring issues related to the action.
 */
async function queryPatterns(tool, limit = 3) {
  try {
    const res = await db.query(
      `SELECT p.pattern_key, p.recurrence_count, p.impact_score, p.last_status,
              m.content AS representative_content, m.type AS memory_type
       FROM brainx_patterns p
       LEFT JOIN brainx_memories m ON m.id = p.representative_memory_id
       WHERE p.recurrence_count >= 2
         AND COALESCE(p.last_status, 'pending') NOT IN ('wont_fix')
       ORDER BY p.recurrence_count DESC, p.impact_score DESC
       LIMIT $1`,
      [limit]
    );
    return res.rows;
  } catch (_) {
    return [];
  }
}

/**
 * Format advisory results into readable text.
 */
function formatAdvisory(memories, trajectories, patterns) {
  const sections = [];
  let totalConfidence = 0;
  let count = 0;

  if (memories.length > 0) {
    const lines = memories.map(m => {
      const sim = (m.similarity ?? 0).toFixed(2);
      return `  • [${m.type}|sim:${sim}|imp:${m.importance}] ${m.content.slice(0, 200)}`;
    });
    sections.push(`📝 Relevant Memories (${memories.length}):\n${lines.join('\n')}`);
    totalConfidence += memories.reduce((s, m) => s + (m.similarity ?? 0), 0);
    count += memories.length;
  }

  if (trajectories.length > 0) {
    const lines = trajectories.map(t => {
      const sim = (t.similarity ?? 0).toFixed(2);
      return `  • [${t.outcome}|sim:${sim}] ${t.problem?.slice(0, 100) || 'N/A'} → ${t.solution?.slice(0, 100) || 'N/A'}`;
    });
    sections.push(`🔄 Similar Past Paths (${trajectories.length}):\n${lines.join('\n')}`);
    totalConfidence += trajectories.reduce((s, t) => s + (t.similarity ?? 0), 0);
    count += trajectories.length;
  }

  if (patterns.length > 0) {
    const lines = patterns.map(p =>
      `  • [×${p.recurrence_count}|impact:${(p.impact_score ?? 0).toFixed(1)}] ${p.representative_content?.slice(0, 150) || p.pattern_key}`
    );
    sections.push(`🔁 Recurring Patterns (${patterns.length}):\n${lines.join('\n')}`);
    // Patterns add a fixed confidence boost
    totalConfidence += patterns.length * 0.3;
    count += patterns.length;
  }

  const avgConfidence = count > 0 ? Math.min(totalConfidence / count, 1.0) : 0;
  const sourceIds = memories.map(m => m.id);

  return {
    text: sections.length > 0 ? sections.join('\n\n') : null,
    confidence: Number(avgConfidence.toFixed(3)),
    sourceIds,
    totalSources: count
  };
}

/**
 * Main advisory function.
 * @param {Object} actionContext - { tool, args, agent, project }
 * @returns {Object} { advisory_text, confidence, source_memory_ids, id, on_cooldown }
 */
async function getAdvisory(actionContext) {
  const { tool, args, agent, project } = actionContext;

  // Check cooldown
  if (await isOnCooldown(agent, tool)) {
    return {
      id: null,
      advisory_text: null,
      confidence: 0,
      source_memory_ids: [],
      on_cooldown: true
    };
  }

  const searchQuery = buildSearchQuery(actionContext);

  // Query all sources in parallel
  const [memories, trajectories, patterns] = await Promise.all([
    queryRelevantMemories(searchQuery),
    queryTrajectories(searchQuery),
    queryPatterns(tool)
  ]);

  const { text, confidence, sourceIds, totalSources } = formatAdvisory(memories, trajectories, patterns);

  if (!text) {
    return {
      id: null,
      advisory_text: null,
      confidence: 0,
      source_memory_ids: [],
      on_cooldown: false
    };
  }

  // Store the advisory
  const id = makeAdvisoryId();
  const actionContextJson = {
    tool,
    args: typeof args === 'string' ? (() => { try { return JSON.parse(args); } catch (_) { return args; } })() : args,
    agent,
    project
  };

  await db.query(
    `INSERT INTO brainx_advisories (id, agent, tool, action_context, advisory_text, source_memory_ids, confidence)
     VALUES ($1, $2, $3, $4, $5, $6, $7)`,
    [id, agent || 'unknown', tool, JSON.stringify(actionContextJson), text, sourceIds, confidence]
  );

  return {
    id,
    advisory_text: text,
    confidence,
    source_memory_ids: sourceIds,
    on_cooldown: false
  };
}

/**
 * Record feedback on an advisory.
 */
async function advisoryFeedback(advisoryId, wasFollowed, outcome) {
  const res = await db.query(
    `UPDATE brainx_advisories
     SET was_followed = $2, outcome = $3
     WHERE id = $1
     RETURNING id, agent, tool, was_followed, outcome`,
    [advisoryId, wasFollowed, outcome || null]
  );
  if (res.rowCount === 0) throw new Error(`Advisory not found: ${advisoryId}`);
  return res.rows[0];
}

module.exports = { getAdvisory, advisoryFeedback, buildSearchQuery, formatAdvisory, isHighRisk, HIGH_RISK_TOOLS };
