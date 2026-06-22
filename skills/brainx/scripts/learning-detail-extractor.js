#!/usr/bin/env node
/**
 * BrainX V5 — Learning Detail Extractor
 *
 * Extracts extended metadata from "learning" and "gotcha" memories
 * using OpenAI (gpt-4.1-mini) and stores structured data in brainx_learning_details.
 *
 * Usage:
 *   node scripts/learning-detail-extractor.js [--limit 50] [--dry-run]
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });

const { Pool } = require('pg');
const OpenAI = require('openai');

// ── Config ──────────────────────────────────────────
const DATABASE_URL = process.env.DATABASE_URL;
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

if (!DATABASE_URL) { console.error('DATABASE_URL is required'); process.exit(1); }
if (!OPENAI_API_KEY) { console.error('OPENAI_API_KEY is required'); process.exit(1); }

const pool = new Pool({ connectionString: DATABASE_URL });
const openai = new OpenAI({ apiKey: OPENAI_API_KEY });

const BATCH_SIZE = 5;
const BATCH_DELAY_MS = 1000;
const MODEL = 'gpt-4.1-mini';

const VALID_CATEGORIES = [
  'learning', 'error', 'feature_request', 'correction',
  'knowledge_gap', 'best_practice', 'infrastructure', 'project_registry'
];

// ── Args ──────────────────────────────────────────
function parseArgs() {
  const argv = process.argv.slice(2);
  const args = { limit: 50, dryRun: false };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--limit') args.limit = parseInt(argv[++i], 10);
    else if (argv[i] === '--dry-run') args.dryRun = true;
  }
  return args;
}

// ── OpenAI extraction ──────────────────────────────
async function extractDetails(memory) {
  const systemPrompt = `You are a metadata extractor for an AI agent's memory system.
Given a memory entry (learning or gotcha), extract structured metadata.

Return a JSON object with these fields:
- category: one of [learning, error, feature_request, correction, knowledge_gap, best_practice, infrastructure, project_registry]
- what_was_wrong: what was wrong or problematic (null if not applicable)
- what_is_correct: the correct approach or solution (null if not applicable)
- source: where this learning came from (e.g. "user correction", "debugging session", "documentation")
- error_message: specific error message if any (null if none)
- command_attempted: the command that failed or was tried (null if none)
- suggested_fix: proposed solution or fix (null if none)
- environment: environment context (e.g. "Node.js", "PostgreSQL", "Railway", "Linux")
- related_files: array of file paths mentioned or relevant (empty array if none)
- complexity: one of [simple, medium, complex]
- frequency: one of [first_time, recurring]
- requested_capability: if a feature was requested, what capability (null if none)
- user_context: additional context about why this matters (null if none)

Respond ONLY with valid JSON. No markdown, no explanation.`;

  const userPrompt = `Memory ID: ${memory.id}
Type: ${memory.type}
Content: ${memory.content}
${memory.context ? `Context: ${memory.context}` : ''}
${memory.tags ? `Tags: ${memory.tags.join(', ')}` : ''}`;

  const response = await openai.chat.completions.create({
    model: MODEL,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userPrompt }
    ],
    temperature: 0.1,
    response_format: { type: 'json_object' }
  });

  const text = response.choices[0].message.content;
  return JSON.parse(text);
}

// ── Validate extracted data ──────────────────────────
function validateAndClean(data) {
  // Clamp category
  if (!VALID_CATEGORIES.includes(data.category)) {
    data.category = 'learning';
  }
  // Clamp complexity
  if (!['simple', 'medium', 'complex'].includes(data.complexity)) {
    data.complexity = 'medium';
  }
  // Clamp frequency
  if (!['first_time', 'recurring'].includes(data.frequency)) {
    data.frequency = 'first_time';
  }
  // Ensure related_files is array
  if (!Array.isArray(data.related_files)) {
    data.related_files = data.related_files ? [String(data.related_files)] : [];
  }
  return data;
}

// ── Insert into DB ──────────────────────────────────
async function insertDetail(memoryId, data) {
  const query = `
    INSERT INTO brainx_learning_details (
      memory_id, category, what_was_wrong, what_is_correct, source,
      error_message, command_attempted, suggested_fix, environment,
      related_files, requested_capability, user_context,
      complexity, frequency
    ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
    ON CONFLICT (memory_id) DO NOTHING
  `;
  const values = [
    memoryId,
    data.category,
    data.what_was_wrong || null,
    data.what_is_correct || null,
    data.source || null,
    data.error_message || null,
    data.command_attempted || null,
    data.suggested_fix || null,
    data.environment || null,
    data.related_files,
    data.requested_capability || null,
    data.user_context || null,
    data.complexity,
    data.frequency
  ];
  await pool.query(query, values);
}

// ── Sleep helper ──────────────────────────────────
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// ── Main ──────────────────────────────────────────
async function main() {
  const args = parseArgs();
  const result = { processed: 0, skipped: 0, stored: 0, errors: [] };

  try {
    // Fetch unprocessed learning/gotcha memories
    const { rows: memories } = await pool.query(`
      SELECT m.id, m.type, m.content, m.context, m.tags
      FROM brainx_memories m
      WHERE m.type IN ('learning', 'gotcha')
        AND m.id NOT IN (SELECT memory_id FROM brainx_learning_details)
      ORDER BY m.created_at DESC
      LIMIT $1
    `, [args.limit]);

    if (memories.length === 0) {
      result.skipped = 0;
      console.log(JSON.stringify(result));
      await pool.end();
      return;
    }

    // Process in batches
    for (let i = 0; i < memories.length; i += BATCH_SIZE) {
      const batch = memories.slice(i, i + BATCH_SIZE);

      for (const memory of batch) {
        try {
          // Skip very short content (likely noise)
          if (!memory.content || memory.content.trim().length < 10) {
            result.skipped++;
            continue;
          }

          const rawData = await extractDetails(memory);
          const data = validateAndClean(rawData);

          if (args.dryRun) {
            process.stderr.write(`[dry-run] ${memory.id}: ${data.category} (${data.complexity})\n`);
            result.processed++;
          } else {
            await insertDetail(memory.id, data);
            result.stored++;
            result.processed++;
          }
        } catch (err) {
          result.errors.push({ memory_id: memory.id, error: err.message });
        }
      }

      // Delay between batches (skip after last batch)
      if (i + BATCH_SIZE < memories.length) {
        await sleep(BATCH_DELAY_MS);
      }
    }
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
