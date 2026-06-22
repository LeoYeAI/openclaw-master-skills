/**
 * BrainX EIDOS Loop
 * Prediction → Outcome → Evaluation cycle for agent self-improvement.
 */

const crypto = require('crypto');
const db = require('./db');
const rag = require('./openai-rag');

function makeEidosId() {
  return `eidos_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
}

/**
 * Record a prediction before an action.
 */
async function predict({ agent, tool, project, prediction, predictedOutcome, context }) {
  if (!prediction) throw new Error('prediction text is required');

  const id = makeEidosId();
  const contextJson = context ? (typeof context === 'string' ? context : JSON.stringify(context)) : null;

  await db.query(
    `INSERT INTO brainx_eidos_cycles (id, agent, tool, project, context, prediction, predicted_outcome, status)
     VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7, 'predicted')`,
    [id, agent || 'unknown', tool || null, project || null, contextJson, prediction, predictedOutcome || null]
  );

  return { id, status: 'predicted' };
}

/**
 * Evaluate a prediction against actual outcome.
 */
async function evaluate({ id, actualOutcome, accuracy, notes }) {
  if (!id) throw new Error('prediction id is required');
  if (!actualOutcome) throw new Error('outcome text is required');

  const accuracyVal = accuracy !== undefined && accuracy !== null ? parseFloat(accuracy) : null;
  if (accuracyVal !== null && (accuracyVal < 0 || accuracyVal > 1)) {
    throw new Error('accuracy must be between 0 and 1');
  }

  const res = await db.query(
    `UPDATE brainx_eidos_cycles
     SET actual_outcome = $2,
         accuracy = $3,
         evaluation_notes = $4,
         status = 'evaluated',
         evaluated_at = NOW()
     WHERE id = $1 AND status = 'predicted'
     RETURNING id, agent, tool, prediction, actual_outcome, accuracy, status`,
    [id, actualOutcome, accuracyVal, notes || null]
  );

  if (res.rowCount === 0) {
    throw new Error(`Prediction not found or already evaluated: ${id}`);
  }

  return res.rows[0];
}

/**
 * Distill a learning from an evaluated prediction (especially wrong ones).
 */
async function distillLearning({ id }) {
  if (!id) throw new Error('evaluation id is required');

  // Fetch the evaluated cycle
  const cycleRes = await db.query(
    `SELECT * FROM brainx_eidos_cycles WHERE id = $1 AND status = 'evaluated'`,
    [id]
  );

  if (cycleRes.rows.length === 0) {
    throw new Error(`Evaluated cycle not found: ${id}`);
  }

  const cycle = cycleRes.rows[0];
  const accuracy = cycle.accuracy !== null ? parseFloat(cycle.accuracy) : null;

  // Generate a learning memory from the mismatch
  let learningContent;
  if (accuracy !== null && accuracy < 0.5) {
    learningContent = `EIDOS Learning: Predicted "${cycle.prediction}" for tool:${cycle.tool || 'unknown'}, but actual outcome was "${cycle.actual_outcome}". ${cycle.evaluation_notes ? `Notes: ${cycle.evaluation_notes}` : ''}`;
  } else if (accuracy !== null && accuracy >= 0.5 && accuracy < 0.8) {
    learningContent = `EIDOS Partial: Prediction "${cycle.prediction}" for tool:${cycle.tool || 'unknown'} was partially correct. Actual: "${cycle.actual_outcome}". ${cycle.evaluation_notes || ''}`;
  } else {
    learningContent = `EIDOS Confirmation: Prediction "${cycle.prediction}" for tool:${cycle.tool || 'unknown'} was accurate. Outcome: "${cycle.actual_outcome}".`;
  }

  // Store as a learning memory
  const memoryId = `m_eidos_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
  const importance = accuracy !== null && accuracy < 0.5 ? 7 : 4; // Wrong predictions are more valuable
  const memory = {
    id: memoryId,
    type: 'learning',
    content: learningContent,
    context: cycle.project ? `project:${cycle.project}` : null,
    tier: 'warm',
    importance,
    agent: cycle.agent,
    tags: ['eidos', 'auto-distilled'],
    source_kind: 'llm_distilled',
    confidence: accuracy !== null ? (1 - Math.abs(0.5 - accuracy)) : 0.5
  };

  const stored = await rag.storeMemory(memory);

  // Update the cycle
  await db.query(
    `UPDATE brainx_eidos_cycles
     SET learning_memory_id = $2, status = 'distilled', distilled_at = NOW()
     WHERE id = $1`,
    [id, stored?.id || memoryId]
  );

  return {
    id,
    learning_memory_id: stored?.id || memoryId,
    learning_content: learningContent,
    status: 'distilled'
  };
}

/**
 * Get prediction accuracy stats.
 */
async function stats({ agent, days }) {
  const daysVal = days ? parseInt(days, 10) : 30;
  const params = [daysVal];
  let agentFilter = '';
  if (agent) {
    agentFilter = ' AND agent = $2';
    params.push(agent);
  }

  const [totalRes, byToolRes, accuracyRes, recentRes] = await Promise.all([
    db.query(
      `SELECT
         COUNT(*)::int AS total,
         COUNT(*) FILTER (WHERE status = 'predicted')::int AS pending,
         COUNT(*) FILTER (WHERE status = 'evaluated')::int AS evaluated,
         COUNT(*) FILTER (WHERE status = 'distilled')::int AS distilled
       FROM brainx_eidos_cycles
       WHERE created_at >= NOW() - make_interval(days => $1)${agentFilter}`,
      params
    ),
    db.query(
      `SELECT tool,
              COUNT(*)::int AS total,
              ROUND(AVG(accuracy)::numeric, 3) AS avg_accuracy,
              COUNT(*) FILTER (WHERE accuracy IS NOT NULL AND accuracy >= 0.8)::int AS accurate,
              COUNT(*) FILTER (WHERE accuracy IS NOT NULL AND accuracy < 0.5)::int AS wrong
       FROM brainx_eidos_cycles
       WHERE created_at >= NOW() - make_interval(days => $1)${agentFilter}
       GROUP BY tool
       ORDER BY total DESC`,
      params
    ),
    db.query(
      `SELECT
         ROUND(AVG(accuracy)::numeric, 3) AS overall_accuracy,
         ROUND(STDDEV(accuracy)::numeric, 3) AS accuracy_stddev,
         MIN(accuracy) AS min_accuracy,
         MAX(accuracy) AS max_accuracy
       FROM brainx_eidos_cycles
       WHERE accuracy IS NOT NULL
         AND created_at >= NOW() - make_interval(days => $1)${agentFilter}`,
      params
    ),
    db.query(
      `SELECT id, agent, tool, prediction, actual_outcome, accuracy, status, created_at
       FROM brainx_eidos_cycles
       WHERE created_at >= NOW() - make_interval(days => $1)${agentFilter}
       ORDER BY created_at DESC
       LIMIT 10`,
      params
    )
  ]);

  return {
    window_days: daysVal,
    agent: agent || 'all',
    counts: totalRes.rows[0],
    by_tool: byToolRes.rows,
    accuracy: accuracyRes.rows[0],
    recent: recentRes.rows
  };
}

module.exports = { predict, evaluate, distillLearning, stats };
